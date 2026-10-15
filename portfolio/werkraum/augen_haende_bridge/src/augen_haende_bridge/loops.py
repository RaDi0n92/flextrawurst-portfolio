"""Loops und Goals (G15): eine Wiederholung mit Budget, nachvollziehbarem Fortschritt, Start, Pause, Stop und einem **echten Abschlussgrund**.

* **Loop**: ein Ablauf (G12) wird wiederholt, bis das Budget aufgebraucht ist oder jemand stoppt.
* **Goal**: wie ein Loop, aber mit einer Abschlussbedingung (`ablauf.bedingung` auf dem Ergebnis des letzten Durchlaufs); ist sie erfüllt, ist das Ziel erreicht („abgeschlossen“).

Grenzen, die immer gelten: höchstens `MAX_LAEUFE` Durchläufe und `MAX_SEKUNDEN` Gesamtzeit, nie mehr als `MAX_GLEICHZEITIG` Loops zugleich, drei Fehlschläge in Folge beenden den Loop mit Grund `fehler`.
**Nach einem Stop beginnt nie ein neuer Durchlauf** — das Ende wird mit dem laufenden Durchlauf abgeglichen (`stoppen` wartet darauf), und der Abschlussgrund steht im Zustand. Fortschritt ist die Liste der Durchläufe mit Zeit, Ergebnis und Grund.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable

from . import ablauf as ab

MAX_LAEUFE = 1000
MAX_SEKUNDEN = 86_400
MAX_GLEICHZEITIG = 5
MAX_FEHLER_IN_FOLGE = 3
MAX_FORTSCHRITT = 200
ENDGRUENDE = ("abgeschlossen", "budget_laeufe_erschoepft", "budget_zeit_erschoepft", "gestoppt", "fehler")


class LoopFehler(ValueError):
    pass


def budget_pruefen(budget: object) -> dict:
    if not isinstance(budget, dict) or not set(budget) <= {"max_laeufe", "max_s"}:
        raise LoopFehler("budget_ungueltig")
    n, s = budget.get("max_laeufe", 10), budget.get("max_s", 3600)
    if type(n) is not int or not 1 <= n <= MAX_LAEUFE or type(s) is not int or not 1 <= s <= MAX_SEKUNDEN:
        raise LoopFehler("budget_ungueltig")
    return {"max_laeufe": n, "max_s": s}


class Loop:
    def __init__(self, loop_id: str, titel: str, durchlauf: Callable[[int], dict], *, budget: dict, intervall_s: float = 1.0, abschluss: dict | None = None, uhr=time.monotonic,
                 jetzt_ms=lambda: int(time.time() * 1000)):
        self.id, self.titel = loop_id, titel
        self._durchlauf, self.budget, self.intervall_s, self.abschluss = durchlauf, budget_pruefen(budget), max(0.0, float(intervall_s)), abschluss
        if abschluss is not None:
            try:
                ab.bedingung(abschluss, {})
            except Exception:
                raise LoopFehler("abschluss_ungueltig") from None
        self._uhr, self._jetzt = uhr, jetzt_ms
        self.art = "goal" if abschluss is not None else "loop"
        self.zustand = "bereit"  # bereit | laeuft | pausiert | beendet
        self.grund = ""
        self.fortschritt: list[dict] = []
        self.laeufe = 0
        self._fehler_in_folge = 0
        self._start = 0.0
        self._stop = threading.Event()
        self._weiter = threading.Event()
        self._weiter.set()
        self._faden: threading.Thread | None = None
        self._sperre = threading.Lock()
        self.gestartet_ms = 0
        self.beendet_ms = 0

    def starten(self) -> None:
        with self._sperre:
            if self.zustand != "bereit":
                raise LoopFehler("schon_gestartet")
            self.zustand, self._start, self.gestartet_ms = "laeuft", self._uhr(), self._jetzt()
        self._faden = threading.Thread(target=self._lauf, daemon=True, name=f"loop-{self.id}")
        self._faden.start()

    def pausieren(self) -> bool:
        with self._sperre:
            if self.zustand != "laeuft":
                return False
            self.zustand = "pausiert"
            self._weiter.clear()
            return True

    def fortsetzen(self) -> bool:
        with self._sperre:
            if self.zustand != "pausiert":
                return False
            self.zustand = "laeuft"
            self._weiter.set()
            return True

    def stoppen(self, grund: str = "gestoppt", warten_s: float = 5.0) -> bool:
        """Beendet den Loop; es beginnt kein weiterer Durchlauf. Wartet, bis der laufende Durchlauf (falls einer läuft) zu Ende ist."""
        with self._sperre:
            if self.zustand == "beendet":
                return False
            self._stop.set()
            self._weiter.set()
            if self.grund == "":
                self.grund = grund
        if self._faden is not None and self._faden is not threading.current_thread():
            self._faden.join(warten_s)
        if self._faden is None:  # nie gestartet
            with self._sperre:
                self.zustand, self.beendet_ms = "beendet", self._jetzt()
        return True

    def _beenden(self, grund: str) -> None:
        with self._sperre:
            self.grund = self.grund or grund
            self.zustand, self.beendet_ms = "beendet", self._jetzt()

    def _lauf(self) -> None:
        try:
            while True:
                self._weiter.wait()
                if self._stop.is_set():
                    return self._beenden("gestoppt")
                if self.laeufe >= self.budget["max_laeufe"]:
                    return self._beenden("budget_laeufe_erschoepft")
                if self._uhr() - self._start >= self.budget["max_s"]:
                    return self._beenden("budget_zeit_erschoepft")
                nr = self.laeufe + 1
                try:
                    r = self._durchlauf(nr)
                    ok = bool(r.get("ok"))
                    ergebnis = {"nr": nr, "zeit_ms": self._jetzt(), "ok": ok, "status": str(r.get("status", ""))[:40], "kurz": str(r.get("kurz", ""))[:200]}
                except Exception as f:
                    r, ok = {}, False
                    ergebnis = {"nr": nr, "zeit_ms": self._jetzt(), "ok": False, "status": "ausnahme", "kurz": f.__class__.__name__}
                self.laeufe = nr
                self.fortschritt.append(ergebnis)
                del self.fortschritt[:-MAX_FORTSCHRITT]
                self._fehler_in_folge = 0 if ok else self._fehler_in_folge + 1
                if self._stop.is_set():
                    return self._beenden("gestoppt")
                if self.abschluss is not None and ok and ab.bedingung(self.abschluss, r.get("ctx", {})):
                    return self._beenden("abgeschlossen")
                if self._fehler_in_folge >= MAX_FEHLER_IN_FOLGE:
                    return self._beenden("fehler")
                if self._stop.wait(self.intervall_s):
                    return self._beenden("gestoppt")
        except Exception:
            self._beenden("fehler")

    def stand(self) -> dict:
        with self._sperre:
            return {"id": self.id, "titel": self.titel, "art": self.art, "zustand": self.zustand, "grund": self.grund, "laeufe": self.laeufe, "budget": dict(self.budget), "intervall_s": self.intervall_s,
                    "fortschritt": list(self.fortschritt[-10:]), "abschluss": self.abschluss, "gestartet_ms": self.gestartet_ms, "beendet_ms": self.beendet_ms}


class LoopVerwaltung:
    def __init__(self):
        self._loops: dict[str, Loop] = {}
        self._sperre = threading.Lock()

    def neu(self, titel: str, durchlauf, **kw) -> Loop:
        with self._sperre:
            aktiv = sum(1 for l in self._loops.values() if l.zustand in ("laeuft", "pausiert"))
            if aktiv >= MAX_GLEICHZEITIG:
                raise LoopFehler("zu_viele_loops")
            l = Loop(f"l-{uuid.uuid4().hex[:8]}", titel, durchlauf, **kw)
            self._loops[l.id] = l
            return l

    def hole(self, loop_id: str) -> Loop | None:
        return self._loops.get(loop_id)

    def liste(self) -> list[dict]:
        with self._sperre:
            return [l.stand() for l in self._loops.values()]

    def alle_stoppen(self, grund: str = "gestoppt") -> int:
        n = 0
        for l in list(self._loops.values()):
            n += bool(l.stoppen(grund))
        return n
