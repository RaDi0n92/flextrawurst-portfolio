"""Die Hände an den Körper anschließen (G10): Engine, Plattform-Backend, Zielzustand, Protokoll und die Beobachtung von Daniels Eingabe aus einer Hand.

`baue_haende(plattform, ort, not_aus, …)` liefert ein `Haende`-Bündel: die Engine, den Beobachter der Übernahme und `starten()`/`stoppen()` für die Aufzeichnung. Ohne Backend (kein XTEST,
Wine ohne Anzeige) ist `engine` None und der Grund steht in `fehler`: die Hände sind dann ehrlich nicht verfügbar, nicht heimlich leer.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path

from . import ziele
from .eingabe_adapter import HaendeEngine, ZielStand
from .uebernahme import Uebernahme

PROTOKOLL_MAX_BYTES = 5 * 1024 * 1024


@dataclass
class Haende:
    engine: HaendeEngine | None = None
    uebernahme: Uebernahme | None = None
    fehler: str = ""
    quellen: list = field(default_factory=list)

    def starten(self) -> None:
        for q in self.quellen:
            try:
                q.start()
            except Exception as f:  # die Beobachtung ist ein Zusatz: scheitert sie, melden wir es und die Hände laufen weiter
                self.fehler = f"Beobachtung von Daniels Eingabe nicht gestartet: {f!r}"[:200]

    def stoppen(self) -> None:
        for q in self.quellen:
            try:
                q.stop()
            except Exception:
                pass


class Protokoll:
    """Eine Zeile je ausgeführter oder abgelehnter Aktion (JSON). Wird bei 5 MB einmal umbenannt (`.1`), nie gelöscht."""

    def __init__(self, pfad: Path | None):
        self.pfad = Path(pfad) if pfad else None
        self._sperre = threading.Lock()

    def __call__(self, eintrag: dict) -> None:
        if self.pfad is None:
            raise OSError("kein Protokollpfad")
        with self._sperre:
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            if self.pfad.exists() and self.pfad.stat().st_size > PROTOKOLL_MAX_BYTES:
                self.pfad.replace(self.pfad.with_suffix(self.pfad.suffix + ".1"))
            with open(self.pfad, "a", encoding="utf-8") as f:
                f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def baue_haende(plattform: str, ort: str, not_aus, *, protokoll_pfad: Path | None = None, ausnahme=lambda: False, backend=None, fenster_zustand=None) -> Haende:
    """`plattform` ist `windows` oder `linux`. `backend` und `fenster_zustand` sind für Tests einspeisbar."""
    if fenster_zustand is None:
        from .ziel_halter import fenster_zustand as fz
        fenster_zustand = fz
    try:
        if backend is None:
            if plattform == "windows":
                from .eingabe_adapter import WindowsBackend
                backend = WindowsBackend()
            else:
                from .eingabe_adapter import X11Backend
                backend = X11Backend()
    except Exception as fehler:
        return Haende(None, None, f"Hände nicht verfügbar: {fehler!r}"[:200])

    def stand(ziel: str) -> ZielStand | None:
        kennung = ziele.fenster_kennung(ziel)
        if kennung is None or ziele.ort_von(ziel) != ort:
            return None
        vorhanden, minimiert, rect = fenster_zustand(kennung)
        return ZielStand(vorhanden, rect, minimiert, kennung, None)

    def kennung(ziel: str) -> int | None:
        return ziele.fenster_kennung(ziel) if ziele.ort_von(ziel) == ort else None

    engine = HaendeEngine(backend, not_aus=not_aus, ziel_stand=stand, ziel_kennung=kennung, protokoll=Protokoll(protokoll_pfad))
    ueb = Uebernahme(engine, ausnahme=ausnahme)
    quellen: list = []
    try:
        if plattform == "windows":
            from .uebernahme import WindowsHooks
            quellen.append(WindowsHooks(ueb))
        elif os.environ.get("DISPLAY"):
            from .uebernahme import X11Aufzeichnung
            quellen.append(X11Aufzeichnung(ueb.ereignis_x11))
    except Exception as fehler:
        return Haende(engine, ueb, f"Beobachtung von Daniels Eingabe nicht verfügbar: {fehler!r}"[:200])
    return Haende(engine, ueb, "", quellen)
