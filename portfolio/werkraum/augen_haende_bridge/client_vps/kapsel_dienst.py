"""Starter-Dienst für G13/G14: Ereignisprotokoll, Momentkapseln, Zeit-Scrubber, Kontext-Mischpult und Hauhaucs-Beobachtung.

Alles hier ist Aufzeichnen und Lesen. Das Protokoll hört nur zu (Skript, kein Modell); der Scrubber führt nichts aus; der einzige Weg zu einem Modellaufruf ist `beobachtung jetzt` — und der geht nur an den
Chat-Server (11435), nie an die Hintergrundinstanz der Codewesen. Ein Zweig aus einer Kapsel startet pausiert und verlangt vor der ersten Live-Handlung eine frische WorldDOM-Messung.
"""

from __future__ import annotations

import base64
import json
import os
import threading
import time
from pathlib import Path

from augen_haende_bridge import kapseln as kp
from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
from augen_haende_bridge.hauhaucs import CHAT_URL, Beobachtung, BeobachterFehler, Budget, ModellClient
from augen_haende_bridge.kontextmischpult import Mischpult, PultFehler
from augen_haende_bridge.scrubber import Zeitlinie

MAX_BILDER_AN_MODELL = 3


class KapselDienst:
    def __init__(self, launcher, ordner: Path, client: ModellClient | None = None):
        self.l = launcher
        self.ordner = Path(ordner)
        self.protokoll = Ereignisprotokoll(self.ordner / "protokoll")
        self.spiegel = None
        from augen_haende_bridge.speicher.ereignisspeicher import adresse
        echt = (Path(__file__).resolve().parents[1] / "runtime") in self.ordner.resolve().parents  # Tests mit Temp-Ordnern schreiben nie in die echte Datenbank
        if adresse() and (os.environ.get("BRIDGE_DB_URL") or echt):  # Ereignisspeicher (PostgreSQL): jedes Ereignis zusätzlich dorthin, in eigenem Faden
            from augen_haende_bridge.speicher.spiegel import Spiegel
            self.spiegel = Spiegel(self.protokoll)
        self.store = kp.KapselStore(self.ordner / "kapseln")
        self.pult = Mischpult("Hauhaucs")
        self.beobachtung = Beobachtung(self.protokoll, self.pult, client or ModellClient(os.environ.get("BRIDGE_CHAT_URL") or CHAT_URL), Budget(), kapsel_existiert=self._kapsel_da, namen=self._name)
        self._frische: dict[str, bool] = {}  # Zweig-Lauf -> es fehlt noch die frische Messung
        self._sperre = threading.Lock()

    # ---- Einspeisen (vom Starter aufgerufen, nie mit Wirkung) ------------------------------------------------------------------------------------------------
    def _name(self, tid: str) -> str:
        a = self.l.register.agenten.get(tid)
        return a.name if a else tid

    def _kapsel_da(self, kid: str) -> bool:
        try:
            self.store.laden(kid)
            return True
        except kp.KapselFehler:
            return False

    def erfassen(self, art: str, agent: str = "", text: str = "", daten: dict | None = None, ziel: str = "") -> None:
        try:
            self.protokoll.erfassen(art, agent, text, daten, ziel)
        except Exception:
            pass  # Aufzeichnen darf nie etwas anhalten

    def ausgabe(self, agent: str, daten: bytes) -> None:
        try:
            self.protokoll.ausgabe(agent, daten)
        except Exception:
            pass

    # ---- Kapselquellen ---------------------------------------------------------------------------------------------------------------------------------------------
    def quellen(self) -> kp.Quellen:
        l = self.l

        def ereignisse(von, bis, agenten):
            return [e.zu_dict() for e in self.protokoll.zeitraum(von, bis, agenten)]

        def frames(tid):
            ordner = l.frames_dir / tid
            ergebnis = []
            for p in sorted(ordner.glob("frame-*")) if ordner.is_dir() else []:
                try:
                    zeit = int(p.stem.split("-")[1])
                except (IndexError, ValueError):
                    continue
                ergebnis.append((p, {"captured_at_ms": zeit, "source": "frames-ordner"}))
            return ergebnis

        def agenten():
            liste = l.agenten_liste()
            for d in liste:
                d["ziel_info"] = dict(l.ziel_info.get(d["terminal_id"], {}))
                d["anzeigeort"] = l.anzeige.get(d["terminal_id"])
                d["ziel"] = l.ziel.get(d["terminal_id"])
            return liste

        def agenten_von(ziel):
            return [tid for tid, info in l.ziel_info.items() if info.get("target_id") == ziel and tid in l.register.agenten]

        def liste(tid, **args):
            r = l.weltdom_befehl(tid, {"befehl": "liste", "args": {"neu_messen": False, **args}})
            if not r.get("ok"):
                raise LookupError(f"Körper hat nicht geantwortet: {r.get('reason') or r.get('status') or 'unbekannt'}")
            return r

        def weltdom(ziel):
            wer = agenten_von(ziel)
            if not wer:
                raise LookupError("kein Agent mit diesem Ziel gefunden")
            return liste(wer[0])["knoten"]  # der zuletzt gemessene Stand im Körper, nicht frisch gemessen

        def koerper(tid):
            """Was der Körper über Zeichnungen und Bindung weiß: erfundene und projizierte Knoten (Anker, Zeigezeichen) und die Bindung des Ziels."""
            return {"bindung": dict(l.ziel_info.get(tid, {})), "anzeigeort": l.anzeige.get(tid), "ziel_ort": l.ziel.get(tid),
                    "anker": liste(tid, herkunft="authored")["knoten"], "projiziert": liste(tid, herkunft="projected")["knoten"]}

        def laeufe(tid):
            return [x.zu_dict() for x in l.ablauf.laeufe.values() if x.agent == tid]

        return kp.Quellen(agenten=agenten, ereignisse=ereignisse, modell=lambda: self.pult.export() if self.pult.nachrichten else None, terminal=lambda tid, bis: self.protokoll.ausgabe_bis(tid, bis, kp.MAX_TERMINAL_ZEICHEN), frames=frames, koerper=koerper, weltdom=weltdom, laeufe=laeufe)

    def moment(self, von: str, art: str, grund: str = "", agenten=None, ziele=None, zeitraum=None, eltern: str | None = None) -> dict:
        try:
            k = self.store.erzeugen(self.quellen(), art, von=von, grund=grund, agenten=agenten, ziele=ziele, zeitraum=tuple(zeitraum) if zeitraum else None, eltern=eltern)
        except kp.KapselFehler as f:
            return {"ok": False, "reason": str(f)}
        self.erfassen("kapsel", "", f"Kapsel {k['id']} ({art})", {"kapsel": k["id"], "luecken": len(k["luecken"])})
        return {"ok": True, "kapsel": k["id"], "luecken": k["luecken"], "agenten": [self._name(t) for t in k["auswahl"]["agenten"]], "hinweis": "unveränderlich gespeichert; Gedanken dazu kommen als eigene Ebenen"}

    # ---- Zeitlinie (nur lesen) ----------------------------------------------------------------------------------------------------------------------------------
    def zeitlinie(self, agenten=None) -> Zeitlinie:
        ereignisse = [e.zu_dict() for e in self.protokoll.zeitraum(0, None, agenten)]
        stuecke: dict[str, list[tuple[int, str]]] = {}
        frames: dict[str, list[tuple[int, dict]]] = {}
        for tid in agenten or list(self.l.register.agenten):
            with self.protokoll._sperre:
                stuecke[tid] = list(self.protokoll._ausgabe.get(tid, []))
            frames[tid] = [(m["captured_at_ms"], m) for _p, m in self.quellen().frames(tid)]
        return Zeitlinie(ereignisse, stuecke, frames)

    # ---- Zweig aus einer Kapsel ---------------------------------------------------------------------------------------------------------------------------------
    def zweig_aus_kapsel(self, agent: str, kid: str, lauf_id: str, checkpoint: str) -> dict:
        try:
            self.store.laden(kid)
        except kp.KapselFehler as f:
            return {"ok": False, "reason": str(f)}
        lauf = self.l.ablauf.laeufe.get(lauf_id)
        if lauf is None or lauf.agent != agent:
            return {"ok": False, "reason": "lauf_nicht_mehr_vorhanden", "hinweis": "die Kapsel zeigt den Lauf, aber nur ein noch geladener eigener Lauf kann verzweigt werden"}
        r = self.l.ablauf.befehl(agent, {"befehl": "zweig", "lauf": lauf_id, "checkpoint": checkpoint})
        if r.get("ok"):
            with self._sperre:
                self._frische[r["lauf"]] = True
            self.erfassen("ablauf", agent, f"Zweig {r['lauf']} aus Kapsel {kid}", {"kapsel": kid, "lauf": r["lauf"]})
            r["hinweis"] = "pausiert: vor der ersten Live-Handlung muss frisch gemessen werden (kapsel zweig-messen)"
        return r

    def zweig_messen(self, agent: str, lauf_id: str) -> dict:
        with self._sperre:
            if lauf_id not in self._frische:
                return {"ok": False, "reason": "kein_kapselzweig"}
        m = self.l.weltdom_befehl(agent, {"befehl": "liste", "args": {}})
        if m.get("ok"):
            with self._sperre:
                self._frische.pop(lauf_id, None)
        return {"ok": bool(m.get("ok")), "reason": m.get("reason", ""), "frisch": bool(m.get("ok"))}

    def zweig_darf_starten(self, lauf_id: str) -> bool:
        with self._sperre:
            return lauf_id not in self._frische

    # ---- Befehle der Agenten ----------------------------------------------------------------------------------------------------------------------------------------
    def befehl(self, agent: str, request: dict) -> dict:
        b = request.get("befehl")
        try:
            if b == "moment":
                return self.moment(self._name(agent), request.get("art") or kp.ART_AGENT, str(request.get("grund") or ""), request.get("agenten") or ([agent] if (request.get("art") or kp.ART_AGENT) == kp.ART_AGENT else None),
                                   request.get("ziele"), request.get("zeitraum"))
            if b == "liste":
                return {"ok": True, "kapseln": self.store.liste()}
            if b == "zeige":
                k = self.store.laden(str(request.get("kapsel")))
                return {"ok": True, "kapsel": {x: k[x] for x in ("id", "erzeugt_ms", "ausloeser", "auswahl", "luecken", "unveraendert", "eltern") if x in k}, "ebenen": self.store.ebenen(k["id"])}
            if b == "ebene":
                return {"ok": True, "ebene": self.store.ebene_hinzufuegen(str(request.get("kapsel")), str(request.get("art")), self._name(agent), str(request.get("text") or ""), request.get("tags"))}
            if b == "suche":
                return {"ok": True, "treffer": self.store.suche(request.get("tags"), request.get("text"))}
            if b == "folge":
                return {"ok": True, "kapsel": self.store.folge_kapsel(str(request.get("kapsel")), self.quellen(), self._name(agent), str(request.get("grund") or ""))["id"]}
            if b == "vergleiche":
                return {"ok": True, "vergleich": self.store.vergleiche(str(request.get("a")), str(request.get("b")))}
            if b == "wiedergabe":
                g = self.store.gespraech(str(request.get("kapsel")))
                if g is None:
                    return {"ok": True, "gespraech": None, "hinweis": "diese Kapsel enthält kein Modellgespräch"}
                return {"ok": True, "nachrichten": [{"id": n["id"], "rolle": n["rolle"], "text": n["text"], "quelle": n.get("quelle", "")} for n in g["nachrichten"]],
                        "hinweis": "aufgezeichnet; es wurde kein Modell gerufen"}
            if b == "gespraech_laden":
                g = self.store.gespraech(str(request.get("kapsel")))
                if g is None:
                    return {"ok": False, "reason": "kein_gespraech_in_kapsel"}
                return {"ok": True, "nachrichten": self.pult.ersetzen_durch(g), "hinweis": "das Mischpult enthält jetzt das Gespräch aus der Kapsel; mit „pult zurueck“ rückgängig, mit „chat“ geht es weiter"}
            if b == "zeitlinie":
                z = self.zeitlinie(request.get("agenten"))
                t = request.get("zeit_ms")
                if t is None:
                    return {"ok": True, "marken": z.marken[-200:], "anzahl": len(z.marken), "wirkung_auf_anwendung": False}
                if request.get("richtung") in (-1, 1):
                    t = z.schritt(int(t), int(request["richtung"]))
                    if t is None:
                        return {"ok": True, "zeit_ms": None, "ende": True, "wirkung_auf_anwendung": False}
                return {"ok": True, "zeit_ms": t, **z.zustand_bei(int(t), request.get("agenten"))}
            if b == "zweig":
                return self.zweig_aus_kapsel(agent, str(request.get("kapsel")), str(request.get("lauf")), str(request.get("checkpoint")))
            if b == "zweig_messen":
                return self.zweig_messen(agent, str(request.get("lauf")))
            if b == "chat":
                text = request.get("text")
                return self.beobachtung.chatten(text if isinstance(text, str) else "")
            if b == "beobachtung":
                return self._beobachtung(request)
            if b == "mischpult":
                return self._mischpult(request)
        except (kp.KapselFehler, PultFehler, BeobachterFehler) as f:
            return {"ok": False, "reason": str(f)}
        return {"ok": False, "reason": "befehl_unbekannt"}

    def _ids(self, namen) -> list[str]:
        ids = []
        for n in namen or []:
            a = self.l.register.finde(n)
            if a is None:
                raise BeobachterFehler(f"agent_unbekannt:{n}")
            ids.append(a.terminal_id)
        return ids

    def _beobachtung(self, r: dict) -> dict:
        a, o = r.get("aktion"), self.beobachtung
        if a == "start":
            return {"ok": True, **o.starten(self._ids(r.get("agenten")), bool(r.get("bilder")))}
        if a == "stop":
            return {"ok": True, **o.stop()}
        if a == "status":
            return {"ok": True, **o.status()}
        if a == "bilder":
            o.bilder_schalten(bool(r.get("an")))
            return {"ok": True, "bilder": o.mit_bildern}
        if a == "zustellen":
            return {"ok": True, "zugestellt": o.zustellen()}
        if a == "lesen":
            ids = self._ids([r.get("agent")])
            return {"ok": True, "text": o.lesbar(ids[0], int(r.get("n") or 40))}
        if a == "budget":
            for k in ("max_aufrufe", "max_tokens"):
                if isinstance(r.get(k), int) and not isinstance(r.get(k), bool) and r[k] >= 0:
                    setattr(o.budget, k, r[k])
            return {"ok": True, "budget": o.budget.zu_dict()}
        if a == "jetzt":
            bilder = None
            if r.get("bilder") and not o.mit_bildern:
                return {"ok": False, "reason": "bilder_nicht_zugeschaltet", "hinweis": "Bilder erst mit „beobachtung bilder an“ zuschalten; es wurde kein Modell gerufen"}
            if r.get("bilder"):
                bilder = []
                for tid in o.agenten:
                    m = self.l.latest_frame(tid)
                    if m:
                        try:
                            bilder.append(base64.b64encode((self.l.frames_dir / tid / m["file"]).read_bytes()).decode())
                        except OSError:
                            pass
                bilder = bilder[:MAX_BILDER_AN_MODELL]
            return o.jetzt_dokumentieren(str(r.get("auftrag") or ""), r.get("kapseln"), bilder)
        return {"ok": False, "reason": "aktion_unbekannt"}

    def _mischpult(self, r: dict) -> dict:
        a, p = r.get("aktion"), self.pult
        if a == "zeige":
            return {"ok": True, "anzeige": p.anzeige(), "vorschau": p.vorschau(), "nachrichten": [n.zu_dict() for n in p.nachrichten]}
        if a == "leeren":
            return {"ok": True, "entfernt": p.leeren()}
        if a == "halbieren":
            return {"ok": True, "entfernt": p.halbieren()}
        if a == "zurueck":
            return {"ok": True, "schritte": p.zurueckspringen(int(r.get("n") or 1))}
        if a == "auswahl":
            return {"ok": True, "ausgewaehlt": p.nur_auswaehlen(r.get("ids") or [])}
        if a == "entfernen":
            return {"ok": True, "entfernt": p.entfernen(r.get("ids") or [])}
        if a == "text":
            return {"ok": True, "id": p.einspeisen_text(str(r.get("text") or ""), quelle="daniel")}
        if a == "datei":
            return {"ok": True, "ids": p.einspeisen_dateien([(str(n), str(t)) for n, t in (r.get("dateien") or [])])}
        if a == "feld":
            p.feld_setzen(str(r.get("name") or ""), str(r.get("text") or ""), bool(r.get("aktiv", True)))
            return {"ok": True, "felder": len(p.felder)}
        if a == "feedback":
            p.einmalfeedback_setzen(r.get("text"))
            return {"ok": True}
        if a == "grenzen":
            p.grenzen_setzen(r.get("max_zeichen"), r.get("max_tokens"))
            return {"ok": True}
        if a == "export":
            return {"ok": True, "pult": p.export()}
        if a == "speichern":
            return {"ok": True, "pfad": str(p.speichern(self.ordner / "pulte"))}
        return {"ok": False, "reason": "aktion_unbekannt"}
