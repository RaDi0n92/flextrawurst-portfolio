"""Der Ablauf-Dienst des Starters (G12): führt Abläufe der Agenten aus, steuert sie für Daniel und lässt Regiesprüche wirken.

Die Ausführung liegt beim Starter, weil er alles hat, was ein Ablauf anfasst: das Register der Agenten (Delegation, Nachrichten), die Leases (Hände), den Weg zum WorldDOM des Körpers und den Draht zu Daniel (Freigaben).
Jeder Lauf gehört einem Agenten und handelt in dessen Namen — mit **seiner** Lease, **seinem** Ziel, **seinen** Rechten; ein Ablauf kann nichts, was der Agent nicht selbst könnte.
Daniel steuert alle Läufe (starten, pausieren, fortsetzen, abbrechen, Zweig, Freigaben, Lernen an/aus); ein Agent steuert nur seine eigenen und kann das Lernen nie einschalten.
"""

from __future__ import annotations

import json
import threading
import time
from collections import deque
from pathlib import Path

from augen_haende_bridge import ablauf as ab
from augen_haende_bridge import ablauf_modi as am
from augen_haende_bridge.koerper import regiespruch_wirkung as rw

MAX_LAEUFE_STAND = 20
MAX_OFFEN_STAND = 10
AUFTRAG_POLL_S = 0.5


class AblaufDienst:
    def __init__(self, launcher, ordner: Path | None, *, frist_s: float = 120.0, schlafen=time.sleep):
        self.l = launcher
        self.speicher = ab.AblaufSpeicher(ordner)
        self.genehmigungen = am.Genehmigungen()
        self.modi = am.Modi(self.genehmigungen, aufgabenbereich=self._bereich, ereignis=self._witness, lernen=self._lernen, frist_s=frist_s)
        self.ausf = ab.Ausfuehrer(self._handler(), modi=self.modi, speicher=self.speicher, schlafen=schlafen)
        self._schlafen = schlafen
        self.laeufe: dict[str, ab.Lauf] = {}
        self.bereich_aus: set[str] = set()
        self.witness_log: deque = deque(maxlen=200)
        self.lernen_pfad = (Path(ordner) / "lernen.jsonl") if ordner else None
        self._sperre = threading.RLock()

    # ---- Handler: die Fähigkeiten, die ein Knoten rufen darf (immer im Namen des Agenten) ----------------------------------------------------------
    def _handler(self) -> dict:
        def weltdom(spec, ctx):
            a = spec["args"]
            return self.l.weltdom_befehl(spec["agent"], {"befehl": a.get("befehl"), "args": a.get("args", {}), **({"seq": a["seq"]} if "seq" in a else {})})

        def haende(spec, ctx):
            a = spec["args"]
            return self.l.haende_befehl(spec["agent"], {"aktion": a.get("aktion"), **({"seq": a["seq"]} if "seq" in a else {})})

        def lease(spec, ctx):
            return self.l.lease_befehl(spec["agent"], spec["args"])

        def nachricht(spec, ctx):
            return self.l._agent_befehl(spec["agent"], "nachricht", spec["args"]) or {"ok": False, "reason": "unbekannt"}

        def auftrag(spec, ctx):
            a = spec["args"]
            r = self.l._agent_befehl(spec["agent"], "auftrag", {"an": a.get("an"), "text": a.get("text")}) or {"ok": False, "reason": "unbekannt"}
            if not r.get("ok"):
                return r
            aid = r["auftrag"]["id"]
            ende = time.monotonic() + float(a.get("warte_s", 60))
            while time.monotonic() < ende:
                x = self.l.register.auftraege.get(aid)
                if x is not None and x.status in ("fertig", "fehler", "abgebrochen"):
                    return {"ok": x.status == "fertig", "auftrag": x.zu_dict(), **({"unsicherheit": x.unsicherheit} if x.unsicherheit else {})}
                self._schlafen(AUFTRAG_POLL_S)
            x = self.l.register.auftraege.get(aid)
            return {"ok": False, "reason": "keine_rueckmeldung", "auftrag": x.zu_dict() if x else r["auftrag"], "hinweis": "der Empfänger hat in der Frist nichts gemeldet; der Auftrag bleibt offen"}

        return {"weltdom": weltdom, "haende": haende, "lease": lease, "nachricht": nachricht, "auftrag": auftrag}

    # ---- Modi-Anschlüsse ------------------------------------------------------------------------------------------------------------------------
    def _bereich(self, lauf) -> bool:
        a = self.l.register.agenten.get(lauf.agent)
        return a is not None and a.zustand == "running" and lauf.agent not in self.bereich_aus

    def _witness(self, e: dict) -> None:
        self.witness_log.append(e)
        self.stand_melden()

    def _lernen(self, rec: dict) -> None:
        if self.lernen_pfad is None:
            return
        self.lernen_pfad.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lernen_pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps({**rec, "zeit_ms": int(time.time() * 1000)}, ensure_ascii=False, default=str) + "\n")

    # ---- Läufe ------------------------------------------------------------------------------------------------------------------------------------
    def starten(self, agent: str, ablauf_id: str, modi=None, version: int | None = None, *, warten: bool = False, trotzdem: bool = False) -> dict:
        a = self.speicher.ablauf(ablauf_id, version)
        if a is None:
            return {"ok": False, "reason": "ablauf_unbekannt"}
        if agent not in self.l.register.agenten:
            return {"ok": False, "reason": "agent_unbekannt"}
        try:
            m = self.modi.normalisieren(modi)
        except am.ModiFehler as f:
            return {"ok": False, "reason": str(f)}
        if a.erwartet and not trotzdem and "shadow" not in m:
            fehlend = self._gealtert(agent, a)
            if fehlend is not None:
                return fehlend
        lauf = ab.neuer_lauf(a, agent, frozenset(self.ausf.handler), m, int(time.time() * 1000))
        with self._sperre:
            self.laeufe[lauf.id] = lauf
        self.ausf.starten(lauf)
        t = threading.Thread(target=self._laufen, args=(lauf,), daemon=True, name=f"ablauf-{lauf.id}")
        t.start()
        if warten:
            t.join(30)
        return {"ok": True, "lauf": lauf.id, "ablauf": a.id, "version": a.version, "modi": list(m)}

    def _gealtert(self, agent: str, a) -> dict | None:
        """Vor dem Start frisch messen und mit dem vergleichen, worauf sich der Ablauf stützt. Warnung statt Handlung: fehlt etwas oder lässt sich nicht messen, startet der Lauf nicht von selbst."""
        m = self.l.weltdom_befehl(agent, {"befehl": "liste", "args": {"neu_messen": True}})
        if not m.get("ok"):
            return {"ok": False, "reason": "ablauf_nicht_pruefbar", "hinweis": f"Der Ablauf nennt erwartete Knoten, aber die frische Messung ging nicht ({m.get('reason') or m.get('status')}). Mit „trotzdem“ starten, wenn du das willst."}
        fehlend = ab.fehlende_erwartungen(a.erwartet, m.get("knoten", []))
        if fehlend:
            return {"ok": False, "reason": "ablauf_gealtert", "fehlend": fehlend, "hinweis": "Die Oberfläche zeigt nicht mehr, worauf sich der Ablauf stützt. Neu entwerfen oder mit „trotzdem“ starten."}
        return None

    def _laufen(self, lauf) -> None:
        try:
            self.ausf.laufen(lauf)
        except Exception as f:
            lauf.run.status = ab.RunStatus.BLOCKED
            lauf.grund = f"ausnahme: {f!r}"[:200]
        self.stand_melden()

    def _lauf(self, lauf_id: str, agent: str | None):
        lauf = self.laeufe.get(lauf_id)
        if lauf is None:
            return None, {"ok": False, "reason": "lauf_unbekannt"}
        if agent is not None and lauf.agent != agent:
            return None, {"ok": False, "reason": "nicht_dein_lauf"}
        return lauf, None

    def zusammenfassung(self, lauf) -> dict:
        a = self.l.register.agenten.get(lauf.agent)
        return {"id": lauf.id, "ablauf": lauf.ablauf.id, "version": lauf.ablauf.version, "agent": a.name if a else lauf.agent, "status": lauf.status, "knoten": lauf.run.current_node_id,
                "grund": lauf.grund[:120], "modi": list(lauf.modi), "schritte": lauf.schritte, "eltern": lauf.eltern}

    # ---- Befehle der Agenten ---------------------------------------------------------------------------------------------------------------------
    def befehl(self, agent: str, request: dict) -> dict:
        b = request.get("befehl")
        if b == "liste":
            return {"ok": True, "ablaeufe": self.speicher.liste(), "laeufe": [self.zusammenfassung(l) for l in self.laeufe.values() if l.agent == agent]}
        if b == "neu":
            try:
                a = self.speicher.speichere(request.get("ablauf"), self.l.register.agenten[agent].name if agent in self.l.register.agenten else agent)
            except ab.AblaufFehler as f:
                return {"ok": False, "reason": str(f)}
            return {"ok": True, "ablauf": a.id, "version": a.version, "versionen": self.speicher.versionen(a.id)}
        if b == "zeige":
            a = self.speicher.ablauf(str(request.get("ablauf")), request.get("version"))
            return {"ok": True, "ablauf": a.zu_dict(), "versionen": self.speicher.versionen(a.id)} if a else {"ok": False, "reason": "ablauf_unbekannt"}
        if b == "start":
            return self.starten(agent, str(request.get("ablauf")), request.get("modi"), request.get("version"), warten=bool(request.get("warten")), trotzdem=bool(request.get("trotzdem")))
        if b == "replay":
            d = self.speicher.lauf(str(request.get("lauf")))
            if d is None or d.get("agent") != agent:
                return {"ok": False, "reason": "lauf_unbekannt"}
            return {"ok": True, "spur": ab.wiedergeben(self.speicher, d["id"]), "hinweis": "gespeicherte Spur; es wurde nichts ausgeführt"}
        lauf, fehler = self._lauf(str(request.get("lauf")), agent)
        if fehler:
            return fehler
        if b == "status":
            return {"ok": True, "lauf": lauf.zu_dict()}
        return self._steuern_lauf(lauf, b, request)

    def _steuern_lauf(self, lauf, b: str, request: dict) -> dict:
        if b == "pause":
            return {"ok": self.ausf.pausieren(lauf), "status": lauf.status}
        if b == "weiter":
            kd = getattr(self.l, "kapseln", None)
            if kd is not None and not kd.zweig_darf_starten(lauf.id):
                return {"ok": False, "reason": "frische_messung_fehlt", "hinweis": "Zweig aus Kapsel: erst frisch messen (kapsel zweig-messen)", "status": lauf.status}
            ok = self.ausf.fortsetzen(lauf)
            if ok:
                threading.Thread(target=self._laufen, args=(lauf,), daemon=True).start()
            return {"ok": ok, "status": lauf.status}
        if b == "stopp":
            self.ausf.abbrechen(lauf, str(request.get("grund") or "abgebrochen")[:60])
            return {"ok": True, "status": lauf.status}
        if b == "checkpoint":
            name = request.get("name")
            if not isinstance(name, str) or not ab.ID.fullmatch(name):
                return {"ok": False, "reason": "name_ungueltig"}
            self.ausf.checkpoint(lauf, name)
            return {"ok": True, "checkpoints": list(lauf.run.checkpoints)}
        if b == "zweig":
            name = request.get("checkpoint")
            if name not in lauf.snapshots:
                return {"ok": False, "reason": "checkpoint_unbekannt"}
            z = self.ausf.zweig(lauf, name)
            with self._sperre:
                self.laeufe[z.id] = z
            return {"ok": True, "lauf": z.id, "hinweis": "neuer Lauf, noch nicht gestartet; der alte bleibt unverändert"}
        if b == "zweig_start":
            return {"ok": False, "reason": "befehl_unbekannt"}
        return {"ok": False, "reason": "befehl_unbekannt"}

    # ---- Daniels Steuerung (vom Desktop) ----------------------------------------------------------------------------------------------------------
    def steuern(self, p: dict) -> dict:
        a = p["aktion"]
        if a == "freigeben" or a == "verweigern":
            return {"ok": self.genehmigungen.entscheiden(p.get("frage_id") or "", a == "freigeben")}
        if a == "lernen":
            self.modi.lernen_aktiv = bool(p.get("an"))
            self.stand_melden()
            return {"ok": True, "lernen": self.modi.lernen_aktiv}
        if a == "bereich":
            (self.bereich_aus.discard if p.get("an") else self.bereich_aus.add)(p.get("terminal_id") or "")
            return {"ok": True}
        if a == "start":
            return self.starten(p.get("terminal_id") or "", p.get("ablauf_id") or "", p.get("modi"))
        if a == "seed_zurueckziehen":  # G15: Daniel nimmt einen Seed zurück (Datei-Block, Loop, Zustand); ein anderer Weg als der Eigentümer-Weg der Agenten
            r = self.l.seeds.zurueckziehen(None, {"seed": p.get("seed_id")}, daniel=True)
            self.stand_melden()
            return r
        if a == "loop_stoppen":
            loop = self.l.seeds.loops.hole(str(p.get("loop_id")))
            if loop is None:
                return {"ok": False, "reason": "loop_unbekannt"}
            loop.stoppen("gestoppt")
            self.stand_melden()
            return {"ok": True, "loop": loop.stand()}
        lauf, fehler = self._lauf(p.get("lauf_id") or "", None)
        if fehler:
            return fehler
        mapping = {"pausieren": "pause", "fortsetzen": "weiter", "abbrechen": "stopp"}
        if a == "zweig":
            r = self._steuern_lauf(lauf, "zweig", {"checkpoint": p.get("checkpoint")})
            if r.get("ok"):
                z = self.laeufe[r["lauf"]]
                self.ausf.starten(z)
                threading.Thread(target=self._laufen, args=(z,), daemon=True).start()
            return r
        if a in mapping:
            return self._steuern_lauf(lauf, mapping[a], {"grund": "daniel"})
        return {"ok": False, "reason": "aktion_unbekannt"}

    # ---- Stand für die Oberfläche ---------------------------------------------------------------------------------------------------------------------
    def stand(self) -> dict:
        with self._sperre:
            laeufe = sorted(self.laeufe.values(), key=lambda l: l.gestartet_ms, reverse=True)[:MAX_LAEUFE_STAND]
        seeds = self._seed_stand()
        stand = {"laeufe": [self.zusammenfassung(l) for l in laeufe], "offen": [{"id": f["id"], "lauf": f["lauf"], "knoten": f["knoten"], "beschreibung": f["beschreibung"]} for f in self.genehmigungen.offen()[:MAX_OFFEN_STAND]],
                "lernen": self.modi.lernen_aktiv, "ablaeufe": [{"id": x["id"], "name": x["name"], "version": x["version"]} for x in self.speicher.liste()[:20]]}
        if seeds:
            stand["seeds"] = seeds
        return stand

    def _seed_stand(self) -> list[dict]:
        """Aktive Seeds und laufende Loops, kurz — damit Daniel sie in seiner Oberfläche sieht und zurücknehmen kann."""
        s = getattr(self.l, "seeds", None)
        if s is None:
            return []
        aus = [{"art": "seed", "id": x["id"], "titel": x["titel"][:60], "zieltyp": x["zieltyp"]} for x in s.store.liste("aktiv")[:10]]
        aus += [{"art": "loop", "id": l["id"], "titel": l["titel"][:60], "zieltyp": l["art"]} for l in s.loops.liste() if l["zustand"] in ("laeuft", "pausiert")][:10]
        return aus

    def stand_melden(self) -> None:
        try:
            self.l.ablauf_stand_senden()
        except Exception:
            self.l.dropped += 1

    # ---- Regiesprüche --------------------------------------------------------------------------------------------------------------------------------
    def regie(self, terminal_id: str, spruch: str) -> dict:
        sess = self.l.sessions.get(terminal_id)

        def eigene():
            return [l for l in self.laeufe.values() if l.agent == terminal_id]

        def zweig(lauf, name):
            r = self._steuern_lauf(lauf, "zweig", {"checkpoint": name})
            if not r.get("ok"):
                return None
            return self.laeufe[r["lauf"]]

        def neu_messen():
            ziel, grund = self.l._haende_ziel(terminal_id, None)
            if ziel is None:
                return None
            r = self.l.weltdom_befehl(terminal_id, {"befehl": "liste", "args": {}})
            return r if r.get("ok") else None

        def tippen(text):
            """Ein Gesprächswunsch geht nie ins Terminal (bewusst, wie bisher): der Körper zeigt ihn als Banner im Bild des Agenten. Zustellbar heißt: der Agent läuft noch."""
            return sess is not None and sess.state == "running"

        def spaeter(lauf, s):
            def lauf_():
                self._schlafen(s)
                if lauf.status == "paused" and self.ausf.fortsetzen(lauf):
                    self._laufen(lauf)

            threading.Thread(target=lauf_, daemon=True).start()

        u = rw.Umfeld(eigene, self.ausf.pausieren, lambda l: self._fortsetzen(l), zweig, lambda: [f for f in self.genehmigungen.offen() if (self.laeufe.get(f["lauf"]) and self.laeufe[f["lauf"]].agent == terminal_id)],
                      lambda fid, ja: self.genehmigungen.entscheiden(fid, ja), neu_messen, tippen, spaeter)
        return rw.wirke(spruch, u)

    def _fortsetzen(self, lauf) -> bool:
        ok = self.ausf.fortsetzen(lauf)
        if ok:
            threading.Thread(target=self._laufen, args=(lauf,), daemon=True).start()
        return ok
