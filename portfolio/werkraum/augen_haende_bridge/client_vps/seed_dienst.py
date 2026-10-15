"""Starter-Dienst für G15: Seeds ausliefern und zurücknehmen, Loops und Goals führen.

Agenten **schlagen vor**; ausgeliefert wird nach dem Freiheitsprofil, das Daniel in `freigaben.json` setzt (Vorgabe: jede Auslieferung braucht sein Ja). Daniels Ja geht über denselben Weg wie die Freigaben der Abläufe (offene Fragen, die seine Oberfläche schon zeigt).
Dateien (Memory, Dokument, Skill) werden nur im von Daniel genannten Zielumfang angefasst und brauchen **immer** sein Ja im Einzelfall — auch im Profil „selbststaendig“.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

from augen_haende_bridge import ablauf as ab
from augen_haende_bridge import loops as lp
from augen_haende_bridge.koerper.agentenregister import Zustellung
from augen_haende_bridge.seeds import DATEI_ZIELE, SeedFehler, SeedStore

FRIST_S = 120.0


class SeedDienst:
    def __init__(self, launcher, ordner: Path, *, frist_s: float = FRIST_S):
        self.l = launcher
        self.store = SeedStore(Path(ordner))
        self.loops = lp.LoopVerwaltung()
        self.frist_s = frist_s
        self._loop_seed: dict[str, str] = {}  # loop-id -> seed-id
        self._eigner: dict[str, str] = {}  # loop-id -> terminal_id

    def _name(self, tid: str) -> str:
        a = self.l.register.agenten.get(tid)
        return a.name if a else tid

    def _melden(self) -> None:
        """Daniels Oberfläche bekommt den neuen Stand (aktive Seeds, laufende Loops)."""
        try:
            self.l.ablauf.stand_melden()
        except Exception:
            pass

    def _erfassen(self, text: str, **daten) -> None:
        k = getattr(self.l, "kapseln", None)
        if k is not None:
            k.erfassen("sonstiges", "", text, daten)

    def stoppen(self) -> None:
        self.loops.alle_stoppen("gestoppt")

    # ---- Vorschlagen ----------------------------------------------------------------------------------------------------------------------------------
    def vorschlagen(self, agent: str, r: dict) -> dict:
        zieltyp, inhalt, budget = r.get("zieltyp"), r.get("inhalt"), r.get("budget")
        if zieltyp == "ablauf":
            try:
                ab.Ablauf.aus_dict(inhalt)
            except ab.AblaufFehler as f:
                return {"ok": False, "reason": f"ablauf_ungueltig:{f}"}
        if zieltyp in ("loop", "goal"):
            fehler = self._loop_pruefen(inhalt, budget, zieltyp)
            if fehler:
                return {"ok": False, "reason": fehler}
        k = getattr(self.l, "kapseln", None)
        for kid in r.get("kapseln") or []:  # die Herkunft muss belastbar sein (G13): eine genannte Kapsel muss es geben
            if k is not None and isinstance(kid, str) and not k._kapsel_da(kid):
                return {"ok": False, "reason": "kapsel_unbekannt", "kapsel": kid}
        for n in r.get("empfaenger") or []:
            if not isinstance(n, str) or self.l.register.finde(n) is None:
                return {"ok": False, "reason": "empfaenger_unbekannt", "empfaenger": n}
        v = self.store.vorschlagen(von=self._name(agent), zieltyp=zieltyp, titel=r.get("titel"), inhalt=inhalt, empfaenger=r.get("empfaenger"), ziel_pfad=r.get("ziel_pfad"),
                                   kapseln=r.get("kapseln"), budget=budget, seed_id=r.get("seed"))
        self._erfassen(f"Seed {v['id']} v{v['version']} vorgeschlagen ({zieltyp})", seed=v["id"])
        return {"ok": True, "seed": v["id"], "version": v["version"], "status": v["status"], "pruefung": self.store.pruefen(v["id"], v["version"]),
                "hinweis": "nur vorgeschlagen; ausgeliefert wird nach Daniels Freigabe („seed ausliefern“)"}

    def _loop_pruefen(self, ablauf_id, budget, zieltyp) -> str:
        if not isinstance(ablauf_id, str) or self.l.ablauf.speicher.ablauf(ablauf_id) is None:
            return "ablauf_unbekannt"
        if not isinstance(budget, dict):
            return "budget_ungueltig"
        rest = {k: v for k, v in budget.items() if k not in ("intervall_s", "abschluss")}
        try:
            lp.budget_pruefen(rest)
        except lp.LoopFehler as f:
            return str(f)
        if not isinstance(budget.get("intervall_s", 1), (int, float)) or isinstance(budget.get("intervall_s", 1), bool) or not 0 <= budget.get("intervall_s", 1) <= 3600:
            return "intervall_ungueltig"
        if zieltyp == "goal" and not isinstance(budget.get("abschluss"), dict):
            return "abschluss_fehlt"
        if zieltyp == "loop" and "abschluss" in budget:
            return "abschluss_nur_bei_goal"
        return ""

    # ---- Ausliefern ----------------------------------------------------------------------------------------------------------------------------------------
    def ausliefern(self, agent: str, r: dict) -> dict:
        sid, ver = r.get("seed"), r.get("version")
        v = self.store.hole(sid, ver)
        if v is None:
            return {"ok": False, "reason": "seed_unbekannt"}
        p = self.store.pruefen(sid, v["version"])
        if p["hindernisse"]:
            return {"ok": False, "reason": p["hindernisse"][0], "pruefung": p}
        if v["status"] == "vorschlag":
            if p["freiheit"] == "vorschlag":
                return {"ok": False, "reason": "freiheit_nur_vorschlag", "hinweis": "Daniels Freiheitsprofil erlaubt nur Vorschläge."}
            if p["braucht_daniel"]:
                gid = self.l.ablauf.genehmigungen.anfordern(f"seed-{sid}", f"v{v['version']}", f"Seed {sid} v{v['version']} ({v['zieltyp']}) von {v['von']}: {v['titel']} — {p['wirkung']}")
                self.l.ablauf.stand_melden()
                entscheidung = self.l.ablauf.genehmigungen.warte(gid, self.frist_s)
                self.l.ablauf.stand_melden()
                if entscheidung != "ja":
                    return {"ok": False, "reason": "nicht_freigegeben" if entscheidung == "nein" else "keine_antwort", "entscheidung": entscheidung}
                self.store.freigeben(sid, "Daniel", v["version"])
            else:
                self.store.freigeben(sid, "Freiheitsprofil", v["version"])
        elif v["status"] != "freigegeben":
            return {"ok": False, "reason": f"status_{v['status']}"}
        try:
            return self._liefern(self.store.hole(sid, v["version"]), agent)
        except (SeedFehler, ab.AblaufFehler, lp.LoopFehler) as f:
            return {"ok": False, "reason": str(f)}

    def _liefern(self, v: dict, agent: str) -> dict:
        z, sid, nr = v["zieltyp"], v["id"], v["version"]
        if z in DATEI_ZIELE:
            self.store.datei_einfuegen(sid, nr, "Starter")
            return self._fertig(v, {"datei": v["ziel_pfad"], "hinweis": "als markierter Block eingefügt, Original gesichert; „seed zurueckziehen“ nimmt genau diesen Block wieder heraus"})
        if z == "ablauf":
            a = self.l.ablauf.speicher.speichere(v["inhalt"], f"Seed {sid}")
            self.store.aktiv_setzen(sid, nr, "Starter", ablauf=a.id, ablauf_version=a.version)
            return self._fertig(v, {"ablauf": a.id, "ablauf_version": a.version, "hinweis": "als neue Version gespeichert; gespeicherte Versionen werden nie gelöscht"})
        if z == "kontext":
            gesehen, fehlen = [], []
            for n in v["empfaenger"]:
                a = self.l.register.finde(n)
                if a is None or a.terminal_id not in self.l.sessions:
                    fehlen.append(n)
                    continue
                self.l._zustellen([Zustellung(a.terminal_id, a.name, f"[Bridge · Seed {sid} v{nr} von {v['von']}] {v['inhalt']}")])
                gesehen.append(a.name)
            if not gesehen:
                return {"ok": False, "reason": "niemand_erreicht", "fehlend": fehlen}
            self.store.aktiv_setzen(sid, nr, "Starter", zugestellt=gesehen)
            return self._fertig(v, {"zugestellt": gesehen, "nicht_erreicht": fehlen, "hinweis": "zugestellt, nicht „verstanden“: ob der Agent es aufnimmt, entscheidet er selbst"})
        return self._loop_starten(v, agent)

    def _fertig(self, v: dict, extra: dict) -> dict:
        self._melden()
        self._erfassen(f"Seed {v['id']} v{v['version']} ausgeliefert ({v['zieltyp']})", seed=v["id"])
        return {"ok": True, "seed": v["id"], "version": v["version"], "status": "aktiv", **extra}

    def _loop_starten(self, v: dict, agent: str) -> dict:
        b = dict(v["budget"])
        intervall, abschluss = b.pop("intervall_s", 1.0), b.pop("abschluss", None)
        wer = self.l.register.finde(v["empfaenger"][0]) if v["empfaenger"] else self.l.register.agenten.get(agent)
        if wer is None:
            return {"ok": False, "reason": "agent_unbekannt"}
        ablauf_id, tid = v["inhalt"], wer.terminal_id

        def durchlauf(nr: int) -> dict:
            r = self.l.ablauf.starten(tid, ablauf_id, None, None, warten=True)
            if not r.get("ok"):
                return {"ok": False, "status": r.get("reason", "start_fehlgeschlagen")}
            lauf = self.l.ablauf.laeufe.get(r["lauf"])
            status = lauf.status if lauf else "unbekannt"
            return {"ok": status == "completed", "status": status, "kurz": f"Lauf {r['lauf']}", "ctx": ({**lauf.ctx, "zustand": dict(lauf.zustand)} if lauf else {})}  # Pfade der Abschlussbedingung: Ergebnisse der Knoten (a.b.c) und „zustand.<name>“

        loop = self.loops.neu(v["titel"], durchlauf, budget=b, intervall_s=intervall, abschluss=abschluss)
        self.store.aktiv_setzen(v["id"], v["version"], "Starter", loop=loop.id)
        self._loop_seed[loop.id], self._eigner[loop.id] = v["id"], tid
        loop.starten()
        threading.Thread(target=self._nach_ende, args=(loop, v["id"], v["version"]), daemon=True, name=f"seed-ende-{loop.id}").start()
        return self._fertig(v, {"loop": loop.id, "art": loop.art, "budget": loop.budget, "hinweis": "läuft mit Budget; „loop stopp“ beendet ihn, danach beginnt nichts Neues"})

    def _nach_ende(self, loop, sid: str, nr: int) -> None:
        if loop._faden is not None:
            loop._faden.join()
        try:
            self.store.zurueckziehen(sid, nr, "Starter", grund=f"loop beendet: {loop.grund}")
        except SeedFehler:
            pass
        self._melden()

    # ---- Zurückziehen ---------------------------------------------------------------------------------------------------------------------------------------
    def zurueckziehen(self, agent: str | None, r: dict, *, daniel: bool = False) -> dict:
        antwort = self._zurueckziehen(agent, r, daniel=daniel)
        if antwort.get("ok"):
            self._melden()
        return antwort

    def _zurueckziehen(self, agent: str | None, r: dict, *, daniel: bool = False) -> dict:
        sid, ver = r.get("seed"), r.get("version")
        v = self.store.hole(sid, ver)
        if v is None:
            return {"ok": False, "reason": "seed_unbekannt"}
        if not daniel and v["von"] != self._name(agent or ""):
            return {"ok": False, "reason": "nicht_dein_seed", "hinweis": "nur wer einen Seed vorgeschlagen hat (oder Daniel) kann ihn zurückziehen"}
        von = "Daniel" if daniel else v["von"]
        try:
            if v["status"] == "aktiv" and v["zieltyp"] in DATEI_ZIELE:
                s = self.store.datei_entfernen(sid, v["version"], von)
                return {"ok": True, "status": s["status"], "hinweis": "der Block wurde entfernt; das Original ist unverändert"}
            if v["status"] == "aktiv" and v["zieltyp"] in ("loop", "goal"):
                for lid, s in self._loop_seed.items():
                    if s == sid and (l := self.loops.hole(lid)) is not None:
                        l.stoppen("gestoppt")
                v = self.store.hole(sid, v["version"])
                if v["status"] == "aktiv":
                    self.store.zurueckziehen(sid, v["version"], von, grund="gestoppt")
                return {"ok": True, "status": "zurueckgezogen", "hinweis": "Loop gestoppt; es beginnt nichts Neues"}
            hinweis = {"ablauf": "als aktiver Seed zurückgezogen; die gespeicherte Ablauf-Version bleibt (nichts wird gelöscht)",
                       "kontext": "als aktiver Seed zurückgezogen; was bereits zugestellt wurde, ist gesagt"}.get(v["zieltyp"], "")
            s = self.store.zurueckziehen(sid, v["version"], von)
            return {"ok": True, "status": s["status"], "hinweis": hinweis}
        except SeedFehler as f:
            return {"ok": False, "reason": str(f)}

    # ---- Befehle der Agenten --------------------------------------------------------------------------------------------------------------------------------------
    def befehl(self, agent: str, r: dict) -> dict:
        b = r.get("befehl")
        try:
            if b == "vorschlagen":
                return self.vorschlagen(agent, r)
            if b == "liste":
                return {"ok": True, "seeds": self.store.liste(r.get("status")), "freiheit": self.store.freigaben.freiheit()}
            if b == "zeige":
                v = self.store.hole(r.get("seed"), r.get("version"))
                return {"ok": True, "seed": v} if v else {"ok": False, "reason": "seed_unbekannt"}
            if b == "pruefen":
                return {"ok": True, "pruefung": self.store.pruefen(r.get("seed"), r.get("version"))}
            if b == "exportieren":
                return {"ok": True, "export": self.store.exportieren(r.get("seed"))}
            if b == "ausliefern":
                return self.ausliefern(agent, r)
            if b == "zurueckziehen":
                return self.zurueckziehen(agent, r)
            if b == "loop":
                return self._loop_befehl(agent, r)
        except (SeedFehler, lp.LoopFehler) as f:
            return {"ok": False, "reason": str(f)}
        return {"ok": False, "reason": "befehl_unbekannt"}

    def _loop_befehl(self, agent: str, r: dict) -> dict:
        a = r.get("aktion")
        if a == "liste":
            return {"ok": True, "loops": [s for s in self.loops.liste() if self._eigner.get(s["id"]) == agent]}
        loop = self.loops.hole(str(r.get("loop")))
        if loop is None:
            return {"ok": False, "reason": "loop_unbekannt"}
        if self._eigner.get(loop.id) != agent:
            return {"ok": False, "reason": "nicht_dein_loop"}
        if a == "status":
            return {"ok": True, "loop": loop.stand()}
        if a == "pause":
            return {"ok": loop.pausieren(), "loop": loop.stand()}
        if a == "weiter":
            return {"ok": loop.fortsetzen(), "loop": loop.stand()}
        if a == "stopp":
            loop.stoppen("gestoppt")
            return {"ok": True, "loop": loop.stand()}
        return {"ok": False, "reason": "aktion_unbekannt"}
