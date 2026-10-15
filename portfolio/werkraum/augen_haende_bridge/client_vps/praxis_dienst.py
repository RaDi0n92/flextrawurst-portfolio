"""Starter-Dienst für den Praxistest als Graph (`praxis/lauf.py`): hält die Läufe, liest die **echten Spuren** aus dem Ereignisprotokoll, schreibt Ansagen in die Raute und führt das Protokoll.

Dieser Dienst vermittelt nur: Er handelt nie selbst auf dem Bildschirm, startet keinen Agenten und ändert nichts außer den Dateien seines Protokolls (`bridge_docs/praxistest/lauf-<id>.md` und `.jsonl`). Ein Schritt zählt erst, wenn Spuren da sind — eine bloße Behauptung öffnet keinen Knoten.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from pathlib import Path

from augen_haende_bridge.praxis.lauf import PraxisFehler, PraxisLauf, lade_szenario, szenario_pfad, szenarien
from augen_haende_bridge.praxis.belege import pruefe as pruefe_schrittbelege
from augen_haende_bridge.praxis import erinnerung

DOKU_ORDNER = Path(__file__).resolve().parent.parent / "bridge_docs" / "praxistest"
MAX_LAEUFE = 5
RAUTE_FRIST_S = 15.0


class PraxisDienst:
    def __init__(self, launcher, ordner: Path, doku_ordner: Path | None = None):
        self.l = launcher
        self.ordner = Path(ordner)
        self.doku = Path(doku_ordner) if doku_ordner is not None else DOKU_ORDNER
        self.laeufe: dict[str, PraxisLauf] = {}
        self._sperre = threading.RLock()
        self._raute_sperre = threading.Lock()
        self._raute_wartend: dict[str, dict] = {}
        self.projektionsfehler = ""
        self._checkpoint_offen: set[str] = set()
        self.unterbrochen = []
        for pfad in sorted(self.ordner.glob("*.checkpoint.json")):
            try:
                d = json.loads(pfad.read_text(encoding="utf-8"))
                if d.get("ergebnis", {}).get("status") == "RUNNING":
                    self.unterbrochen.append({"id": d["id"], "knoten": d.get("knoten"), "status": "INTERRUPTED",
                                             "recovery": "NEW_ATTEMPT_REQUIRED_AFTER_RESTART"})
            except (OSError, ValueError, KeyError):
                self.unterbrochen.append({"file": pfad.name, "status": "UNREADABLE_CHECKPOINT"})
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

    def kontext(self, tid: str) -> dict:
        """Stamped by the starter before dispatch; agent-supplied evidence IDs are ignored."""
        with self._sperre:
            l = self._lauf_von(tid)
            if l is None or l.knoten == "ende":
                return {}
            l._vor()
            return {"run_id": l.id, "step": l.nr, "attempt_id": l.z["versuch_id"], "phase": l.art,
                    "started_ms": int(time.time() * 1000), "since_ms": l.z["t_lesen_ms"],
                    "target_id": getattr(self.l, "ziel_info", {}).get(tid, {}).get("target_id")}

    def pruefe_belege(self, lauf: PraxisLauf) -> dict:
        k = getattr(self.l, "kapseln", None)
        ev = k.protokoll.zeitraum(lauf.z["t_lesen_ms"], None, [lauf.a, lauf.b]) if k else []
        return pruefe_schrittbelege(lauf.schritt()["belege"], [e.zu_dict() for e in ev], run_id=lauf.id,
                                   attempt_id=lauf.z["versuch_id"], step=lauf.nr,
                                   actors={"handelnder": lauf.handelnder(), "zuschauer": lauf.zuschauer_von()},
                                   targets=lauf.z.get("targets", {}), since_ms=lauf.z["t_lesen_ms"])

    def befehlspur(self, tid: str, command: str, request: dict, antwort: dict, kontext: dict) -> None:
        """Small typed projection for the active exercise; no raw command text or secrets."""
        if not kontext or command == "test":
            return
        a = request.get("aktion") if isinstance(request.get("aktion"), dict) else {}
        d = {"praxis": kontext, "command": command, "befehl": request.get("befehl", ""),
             "ok": antwort.get("ok") is True, "reason": antwort.get("reason") or antwort.get("grund", ""),
             "status": antwort.get("status", ""), "action_kind": a.get("art", ""), "taste": a.get("taste", "links"),
             "kombi": str(a.get("kombi", "")).lower().replace("ctrl", "strg"), "empfaenger": request.get("an", "")}
        if command == "lease":
            d["lease_id"] = antwort.get("lease", "")
            d["befehl"] = request.get("aktion", "nehmen")
        if command == "kapsel":
            c = antwort.get("kapsel")
            d["resource_id"] = c.get("id") if isinstance(c, dict) else c
            d["unveraendert"] = c.get("unveraendert") is True if isinstance(c, dict) else False
        if command == "seed":
            sid = antwort.get("seed")
            d["resource_id"] = sid if isinstance(sid, str) else request.get("seed")
            if d["resource_id"]:
                v = self.l.seeds.store.hole(d["resource_id"], antwort.get("version"))
                d["daniel_freigabe"] = bool(v and any(e.get("was") == "freigegeben" and e.get("von") == "Daniel" for e in v.get("ereignisse", [])))
                l = self._lauf_von(tid)
                partner = l.b if l and l.a == tid else (l.a if l else "")
                d["partner_in_queue"] = self._name(partner) in (antwort.get("zugestellt") or [])
            lp = antwort.get("loop")
            d["loop_id"] = lp.get("id") if isinstance(lp, dict) else lp
            if isinstance(lp, dict):
                d.update(resource_id=lp.get("id"), loop_grund=lp.get("grund"), loop_laeufe=lp.get("laeufe"),
                         loop_budget=lp.get("budget", {}).get("max_laeufe"))
            elif isinstance(lp, str):
                d["resource_id"] = lp
        self.l.kapseln.erfassen("sonstiges", tid, "Praxistest-Aktionsbeleg", d)

    def evidenz(self, tid: str, art: str, seit_ms: int) -> int:
        if art == "sehen":
            # Legacy callers may ask for a raw observation count outside a
            # contract-v2 run.  The stricter target/freshness proof is applied
            # by ``belege.py`` for v2, while the old diagnostic remains useful
            # for the standalone bridge command.
            lauf = self._lauf_von(tid)
            if not lauf or lauf.szenario.get("contract_version", 1) != 2:
                return len(self._ereignisse(tid, art, seit_ms))
            ziel = getattr(self.l, "ziel_info", {}).get(tid, {}).get("target_id")
            return len([e for e in self._ereignisse(tid, art, seit_ms)
                        if ziel and ziel == lauf.z.get("targets", {}).get(tid)
                        and e.daten.get("target_id") == ziel
                        and type(e.daten.get("captured_at_ms")) is int
                        and e.daten["captured_at_ms"] >= seit_ms
                        and type(e.daten.get("received_at_ms")) is int
                        and e.daten["received_at_ms"] >= seit_ms
                        and e.daten.get("source") not in (None, "file", "synthetic")])
        if art in ("sehen", "raute", "nachricht", "weltdom"):
            ev = self._ereignisse(tid, art, seit_ms)
            return len([e for e in ev if e.daten.get("ok") is True]) if art in ("weltdom", "nachricht") else len(ev)
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
    def _raute(self, tid: str, text: str) -> dict:
        if tid not in self.l.sessions:
            return {"ok": False, "grund": "terminal_unbekannt"}
        rid = f"praxis-{uuid.uuid4().hex}"
        w = {"tid": tid, "ort": getattr(self.l, "anzeige", {}).get(tid),
             "event": threading.Event(), "ergebnis": None}
        with self._raute_sperre:
            self._raute_wartend[rid] = w
        try:
            self.l._publish("raute_tippen", {"terminal_id": tid, "text": text[:500], "request_id": rid}, message_id=rid)
            if not w["event"].wait(RAUTE_FRIST_S):
                return {"ok": False, "grund": "raute_quittung_fehlt", "request_id": rid}
            r = dict(w["ergebnis"])
            k = getattr(self.l, "kapseln", None)
            if k is not None:
                k.erfassen("raute", tid, f"Körperquittung: {text[:200]}", {"weg": "praxis", **r})
            return r
        finally:
            with self._raute_sperre:
                self._raute_wartend.pop(rid, None)

    def raute_ergebnis(self, payload: dict, ort: str | None) -> None:
        # Eigene Sperre: der CLI-Thread wartet mit gehaltener Lauf-Sperre auf die Antwort.
        with self._raute_sperre:
            w = self._raute_wartend.get(payload.get("request_id"))
            if w is None or w["tid"] != payload.get("terminal_id") or w["ergebnis"] is not None:
                return
            if getattr(self.l, "verteiler", None) is not None and (ort != w["ort"] or getattr(self.l, "anzeige", {}).get(w["tid"]) != ort):
                return
            if type(payload.get("ok")) is not bool:
                return
            w["ergebnis"] = dict(payload)
            w["event"].set()

    def _ledger(self, lauf_id: str):
        def schreiben(z: dict) -> None:
            spiegel = getattr(getattr(self.l, "kapseln", None), "spiegel", None)
            if spiegel is not None:
                spiegel.ledger(z)  # Ereignisspeicher: nur anreihen, nie warten
            self.ordner.mkdir(parents=True, exist_ok=True)
            with open(self.ordner / f"{lauf_id}.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(z, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            try:
                self.doku.mkdir(parents=True, exist_ok=True)
                datei = self.doku / f"lauf-{lauf_id}.md"
                neu = not datei.exists()
                with open(datei, "a", encoding="utf-8") as f:
                    if neu:
                        f.write(f"# Praxistest-Lauf {lauf_id}\n\nAnsagen haben eine Körperquittung. Urteile sind Beobachtungen der Agenten; zurückgestellt bedeutet nicht getestet. Die vollständige Quelle ist das JSONL-Ledger.\n\n"
                                "| Schritt | Status | Handelnder → Zuschauer | Ansage | Getan | Gesehen | Zuschauer sagt | Klärrunden |\n|---|---|---|---|---|---|---|---|\n")
                    c = lambda t: str(t or "").replace("|", "/").replace("\n", " ")[:300]
                    if z.get("status") == "entdeckung":
                        f.write(f"| {z['nr']} | Entdeckung | {c(z.get('von'))} | {c(z.get('text'))} | | | | |\n")
                    elif z.get("status") == "zurueckgestellt":
                        f.write(f"| {z['nr']} | zurückgestellt | | {c(z.get('titel'))} | | | {c(z.get('grund'))} | |\n")
                    elif z.get("status") not in ("ok", "anders", "fehler", "offen_streit"):
                        f.write(f"| {z.get('nr', '')} | {c(z.get('status'))} | | {c(z.get('text'))} | | | | |\n")
                    else:
                        f.write(f"| {z['nr']} {c(z.get('titel'))} | {z.get('status')} | {c(z.get('handelnder'))} → {c(z.get('zuschauer'))} | {c(z.get('ansage'))} | {c(z.get('getan'))} | {c(z.get('gesehen'))} | "
                                f"{c(z.get('zuschauer_urteil'))}: {c(z.get('zuschauer_text'))} | {z.get('klaerrunden', 0)} |\n")
            except OSError as exc:
                self.projektionsfehler = f"markdown_projektion: {type(exc).__name__}"
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
            if any(tid in (l.a, l.b) or p.terminal_id in (l.a, l.b) for l in self.laeufe.values() if l.knoten != "ende"):
                return {"ok": False, "reason": "agent_hat_aktiven_lauf"}
            if len(self.laeufe) >= MAX_LAEUFE:
                return {"ok": False, "reason": "zu_viele_laeufe"}
            lauf_id = f"p-{uuid.uuid4().hex[:6]}"
            try:
                lauf = PraxisLauf(lade_szenario(szenario_pfad(szenario)), tid, p.terminal_id, namen={tid: self._name(tid), p.terminal_id: p.name}, evidenz=self.evidenz, raute=self._raute, ledger=self._ledger(lauf_id),
                                  menue_freigabe=self.menue_freigabe, ab=ab, lauf_id=lauf_id, pruefe_belege=self.pruefe_belege)
            except PraxisFehler as f:
                return {"ok": False, "reason": str(f)}
            self.laeufe[lauf_id] = lauf
        return {"ok": True, "lauf": lauf_id, "sage": f"Los geht's, {self._name(tid)} und {p.name}. Mit `bridge_cli.py test karte` seht ihr jederzeit, was als Nächstes dran ist. Das Protokoll entsteht live in bridge_docs/praxistest/lauf-{lauf_id}.md.",
                "karte": lauf.karte(tid)}

    def befehl(self, tid: str, r: dict) -> dict:
        try:
            with self._sperre:
                lauf = self._lauf_von(tid)
                if lauf and lauf.id in self._checkpoint_offen:
                    self._checkpoint(lauf)
                antwort = self._befehl(tid, r)
                lauf = self._lauf_von(tid)
                if lauf:
                    self._checkpoint(lauf)
        except (PraxisFehler, OSError) as exc:
            return {"ok": False, "reason": str(exc), "sage": "Der Schritt wurde nicht abgeschlossen. Prüfe das Protokoll und wiederhole erst nach Behebung des Fehlers."}
        if self.projektionsfehler:
            antwort["protokoll_hinweis"] = self.projektionsfehler
        if antwort.get("fehlversuche") and lauf is not None:
            self._erinnere_im_hintergrund(lauf, antwort)
        return antwort

    def _erinnere_im_hintergrund(self, lauf: PraxisLauf, antwort: dict) -> None:
        """Nach einem Fehlversuch ähnliche frühere Fälle aus dem Ereignisspeicher holen; sie stehen danach in `test karte` (`erinnerung`). Blockiert nie."""
        nr, titel, grund, klasse = lauf.nr, lauf.schritt()["titel"], antwort.get("reason", ""), antwort.get("klasse", "")

        def suche() -> None:
            faelle = self._aehnliche(grund, titel, klasse=klasse)
            with self._sperre:
                lauf.erinnerung = {"nr": nr, "grund": grund, "faelle": faelle,
                                   "hinweis": "Frühere Fälle aus dem Ereignisspeicher (Bedeutung und Wort). Lies sie, bevor du wieder versuchst; sie stammen von Agenten, die dasselbe Hindernis hatten."}

        threading.Thread(target=suche, daemon=True, name="praxis-erinnerung").start()

    _aehnliche = staticmethod(erinnerung.aehnliche)

    def _checkpoint(self, lauf: PraxisLauf) -> None:
        self._checkpoint_offen.add(lauf.id)
        self.ordner.mkdir(parents=True, exist_ok=True)
        pfad = self.ordner / f"{lauf.id}.checkpoint.json"
        temp = pfad.with_suffix(f".{uuid.uuid4().hex}.tmp")
        try:
            with open(temp, "x", encoding="utf-8") as f:
                os.chmod(temp, 0o600)
                json.dump(lauf.checkpoint(), f, ensure_ascii=False, sort_keys=True)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, pfad)
            self._checkpoint_offen.discard(lauf.id)
        finally:
            temp.unlink(missing_ok=True)

    def _befehl(self, tid: str, r: dict) -> dict:
        b = r.get("befehl")
        if b == "vorflug":
            p = self.l.register.finde(r.get("partner")) if isinstance(r.get("partner"), str) else None
            ids = [tid] + ([p.terminal_id] if p and p.terminal_id != tid else [])
            checks = []
            for t in ids:
                meta = self.l.latest_frame(t)
                ziel = getattr(self.l, "ziel_info", {}).get(t, {}).get("target_id")
                checks.append({"agent": self._name(t), "session_running": getattr(self.l.sessions.get(t), "state", None) == "running",
                               "target_bound": bool(ziel), "fresh_target_frame": bool(meta and ziel and meta.get("target_id") == ziel
                               and 0 <= meta.get("age_ms", 10**9) <= 15000 and meta.get("source") not in (None, "file", "synthetic"))})
            return {"ok": len(ids) == 2 and all(c["session_running"] and c["target_bound"] and c["fresh_target_frame"] for c in checks),
                    "checks": checks, "raute": "Wird erst durch die Körperquittung der Ansage geprüft.",
                    "menue": "Nicht freigegeben; Menüschritte bleiben NOT_TESTED.", "partner_found": len(ids) == 2}
        if b == "start":
            return self.starten(tid, r.get("partner"), r.get("ab", 1), r.get("szenario", "menschlich"))
        if b == "szenarien":
            return {"ok": True, "szenarien": szenarien()}
        lauf = self._lauf_von(tid)
        if lauf is None:
            return {"ok": False, "reason": "kein_lauf", "unterbrochene_laeufe": self.unterbrochen,
                    "sage": "Es läuft kein Praxistest. Alte Checkpoints bleiben Evidence; nach Neustart beginnt ein neuer Versuch (`test start <Partner>`)."}
        with self._sperre:
            if b == "karte":
                return lauf.karte(tid)
            if b == "status":
                return {"ok": True, **lauf.status()}
            if b == "ansage":
                if lauf.art == "ansage" and tid == lauf.handelnder():
                    lauf.z["targets"] = {t: getattr(self.l, "ziel_info", {}).get(t, {}).get("target_id") for t in (lauf.a, lauf.b)}
                return lauf.ansage(tid, str(r.get("text") or ""))
            if b == "ursache":
                return lauf.ursache(tid, str(r.get("text") or ""))
            if b == "nicht_getestet":
                return lauf.nicht_getestet(tid, str(r.get("text") or ""))
            if b in ("getan", "gesehen", "zuschauer"):
                gewechselt = lauf.ziel_gewechselt({t: getattr(self.l, "ziel_info", {}).get(t, {}).get("target_id") for t in (lauf.a, lauf.b)})
                if gewechselt:
                    return gewechselt
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
                lauf._zeile({"nr": min(lauf.nr, lauf.n), "status": "abgebrochen", "von": self._name(tid)})
                lauf.run.abort("praxis_stopp")
                self._checkpoint(lauf)
                self.laeufe.pop(with_id, None)
                return {"ok": True, "sage": f"Lauf {with_id} beendet. Das Protokoll bleibt stehen."}
        return {"ok": False, "reason": "befehl_unbekannt"}
