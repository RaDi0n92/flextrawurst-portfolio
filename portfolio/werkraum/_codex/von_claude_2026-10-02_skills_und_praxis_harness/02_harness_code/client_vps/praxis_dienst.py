"""Starter-Dienst für den Praxistest als Graph (`praxis/lauf.py`): hält die Läufe, liest die **echten Spuren** aus dem Ereignisprotokoll, schreibt Ansagen in die Raute und führt das Protokoll.

Dieser Dienst vermittelt nur: Er handelt nie selbst auf dem Bildschirm, startet keinen Agenten und ändert nichts außer den Dateien seines Protokolls (`bridge_docs/praxistest/lauf-<id>.md` und `.jsonl`). Ein Schritt zählt erst, wenn Spuren da sind — eine bloße Behauptung öffnet keinen Knoten.
"""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from pathlib import Path

from augen_haende_bridge.praxis.lauf import PraxisFehler, PraxisLauf, lade_szenario, szenario_pfad, szenarien

DOKU_ORDNER = Path(__file__).resolve().parent.parent / "bridge_docs" / "praxistest"
MAX_LAEUFE = 5


class PraxisDienst:
    def __init__(self, launcher, ordner: Path, doku_ordner: Path | None = None):
        self.l = launcher
        self.ordner = Path(ordner)
        self.doku = Path(doku_ordner) if doku_ordner is not None else DOKU_ORDNER
        self.laeufe: dict[str, PraxisLauf] = {}
        self._sperre = threading.RLock()
        self.menue_freigabe = False  # erst wahr, wenn die Menü-Fenster der Bridge für die Hände freigegeben sind (Käfig-Erweiterung)

    # ---- Spuren aus dem Protokoll ---------------------------------------------------------------------------------------------------------------------
    def _name(self, tid: str) -> str:
        a = self.l.register.agenten.get(tid)
        return a.name if a else tid

    def _ereignisse(self, tid: str, art: str, seit_ms: int) -> list:
        k = getattr(self.l, "kapseln", None)
        if k is None:
            return []
        return [e for e in k.protokoll.zeitraum(seit_ms, None, [tid], [art])]

    def evidenz(self, tid: str, art: str, seit_ms: int) -> int:
        if art in ("sehen", "raute", "nachricht", "weltdom"):
            ev = self._ereignisse(tid, art, seit_ms)
            return len([e for e in ev if e.daten.get("ok", True)]) if art in ("weltdom", "nachricht") else len(ev)
        if art == "haende":
            return len([e for e in self._ereignisse(tid, "haende", seit_ms) if e.daten.get("ok")])
        if art == "haende_abgelehnt":
            return len([e for e in self._ereignisse(tid, "haende", seit_ms) if not e.daten.get("ok") and e.daten.get("reason") == "ausserhalb"])
        if art == "kapsel":
            k = getattr(self.l, "kapseln", None)
            return len([c for c in (k.store.liste() if k else []) if c["von"] == self._name(tid) and c["erzeugt_ms"] >= seit_ms])
        if art == "seed":
            s = getattr(self.l, "seeds", None)
            if s is None:
                return 0
            n = 0
            for x in s.store.liste():
                v = s.store.hole(x["id"])
                if v and v["von"] == self._name(tid) and v["erzeugt_ms"] >= seit_ms:
                    n += 1
            return n
        if art == "loop":
            s = getattr(self.l, "seeds", None)
            return len([x for x in (s.loops.liste() if s else []) if s._eigner.get(x["id"]) == tid and x["gestartet_ms"] >= seit_ms]) if s else 0
        return 0

    # ---- Raute und Protokoll ------------------------------------------------------------------------------------------------------------------------------
    def _raute(self, tid: str, text: str) -> bool:
        if tid not in self.l.sessions:
            return False
        self.l._publish("raute_tippen", {"terminal_id": tid, "text": text[:500]}, message_id=f"tippen-{tid}-{uuid.uuid4().hex[:8]}")
        k = getattr(self.l, "kapseln", None)
        if k is not None:
            k.erfassen("raute", tid, f"test: {text[:200]}", {"weg": "praxis"})
        return True

    def _ledger(self, lauf_id: str):
        def schreiben(z: dict) -> None:
            self.ordner.mkdir(parents=True, exist_ok=True)
            with open(self.ordner / f"{lauf_id}.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(z, ensure_ascii=False) + "\n")
            try:
                self.doku.mkdir(parents=True, exist_ok=True)
                datei = self.doku / f"lauf-{lauf_id}.md"
                neu = not datei.exists()
                with open(datei, "a", encoding="utf-8") as f:
                    if neu:
                        f.write(f"# Praxistest-Lauf {lauf_id}\n\nJede Zeile ist ein abgeschlossener Schritt, mit Ansage (so stand sie in der Raute), Handlung, Blick und dem Urteil des Zuschauers.\n\n"
                                "| Schritt | Status | Handelnder → Zuschauer | Ansage | Getan | Gesehen | Zuschauer sagt | Klärrunden |\n|---|---|---|---|---|---|---|---|\n")
                    c = lambda t: str(t or "").replace("|", "/").replace("\n", " ")[:300]
                    if z.get("status") == "entdeckung":
                        f.write(f"| {z['nr']} | Entdeckung | {c(z.get('von'))} | {c(z.get('text'))} | | | | |\n")
                    elif z.get("status") == "zurueckgestellt":
                        f.write(f"| {z['nr']} | zurückgestellt | | {c(z.get('titel'))} | | | {c(z.get('grund'))} | |\n")
                    else:
                        f.write(f"| {z['nr']} {c(z.get('titel'))} | {z.get('status')} | {c(z.get('handelnder'))} → {c(z.get('zuschauer'))} | {c(z.get('ansage'))} | {c(z.get('getan'))} | {c(z.get('gesehen'))} | "
                                f"{c(z.get('zuschauer_urteil'))}: {c(z.get('zuschauer_text'))} | {z.get('klaerrunden', 0)} |\n")
            except OSError:
                pass
        return schreiben

    # ---- Läufe ------------------------------------------------------------------------------------------------------------------------------------------------------
    def _lauf_von(self, tid: str) -> PraxisLauf | None:
        with self._sperre:
            for l in reversed(list(self.laeufe.values())):
                if tid in (l.a, l.b):
                    return l
        return None

    def starten(self, tid: str, partner: str, ab: int = 1, szenario: str = "menschlich") -> dict:
        p = self.l.register.finde(partner) if isinstance(partner, str) else None
        if p is None or p.terminal_id == tid:
            return {"ok": False, "reason": "partner_unbekannt", "sage": "Wen soll ich dazuholen? Nenne den Namen des anderen Agenten genau wie in `bridge_cli.py agenten`."}
        if p.terminal_id not in self.l.sessions:
            return {"ok": False, "reason": "partner_nicht_aktiv"}
        if type(ab) is not int or ab < 1:
            return {"ok": False, "reason": "ab_ungueltig"}
        with self._sperre:
            if len(self.laeufe) >= MAX_LAEUFE:
                return {"ok": False, "reason": "zu_viele_laeufe"}
            lauf_id = f"p-{uuid.uuid4().hex[:6]}"
            try:
                lauf = PraxisLauf(lade_szenario(szenario_pfad(szenario)), tid, p.terminal_id, namen={tid: self._name(tid), p.terminal_id: p.name}, evidenz=self.evidenz, raute=self._raute, ledger=self._ledger(lauf_id),
                                  menue_freigabe=self.menue_freigabe, ab=ab, lauf_id=lauf_id)
            except PraxisFehler as f:
                return {"ok": False, "reason": str(f)}
            self.laeufe[lauf_id] = lauf
        return {"ok": True, "lauf": lauf_id, "sage": f"Los geht's, {self._name(tid)} und {p.name}. Mit `bridge_cli.py test karte` seht ihr jederzeit, was als Nächstes dran ist. Das Protokoll entsteht live in bridge_docs/praxistest/lauf-{lauf_id}.md.",
                "karte": lauf.karte(tid)}

    def befehl(self, tid: str, r: dict) -> dict:
        b = r.get("befehl")
        if b == "start":
            return self.starten(tid, r.get("partner"), r.get("ab", 1), r.get("szenario", "menschlich"))
        if b == "szenarien":
            return {"ok": True, "szenarien": szenarien()}
        lauf = self._lauf_von(tid)
        if lauf is None:
            return {"ok": False, "reason": "kein_lauf", "sage": "Es läuft noch kein Praxistest. Starte einen mit `bridge_cli.py test start <Partner>`."}
        with self._sperre:
            if b == "karte":
                return lauf.karte(tid)
            if b == "status":
                return {"ok": True, **lauf.status()}
            if b == "ansage":
                return lauf.ansage(tid, str(r.get("text") or ""))
            if b == "getan":
                return lauf.getan(tid, str(r.get("text") or ""))
            if b == "gesehen":
                return lauf.gesehen(tid, str(r.get("text") or ""), str(r.get("urteil") or ""))
            if b == "zuschauer":
                return lauf.zuschauer(tid, str(r.get("text") or ""), str(r.get("urteil") or ""))
            if b == "planaenderung":
                return lauf.planaenderung(tid, str(r.get("text") or ""))
            if b == "nochmal":
                return lauf.nochmal(tid)
            if b == "kuer":
                return lauf.kuer(tid, str(r.get("text") or ""))
            if b == "stopp":
                with_id = lauf.id
                self.laeufe.pop(with_id, None)
                return {"ok": True, "sage": f"Lauf {with_id} beendet. Das Protokoll bleibt stehen."}
        return {"ok": False, "reason": "befehl_unbekannt"}
