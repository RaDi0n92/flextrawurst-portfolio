"""Kamera-Anbindung des Körpers (G07, erste Fassung für G02/BE03): echte Frames, kein Zustandsschalter.

`pruefe_koerper.py` (V04-MEDIEN-ATTRAPPE) verbietet ausdrücklich, Kamera/Mikrofon als bloße Ein/Aus-Booleans
nachzubauen. Diese erste Fassung liefert deshalb tatsächliche Frames mit Alter, Herkunft und Sequenznummer
(Vorgriff auf G07s "Fertig, wenn"), aber noch kein Pro-Agent-Routing, kein PiP-Layout und kein Aufnahme-Replay —
das bleibt der vollen G07-Fassung. `cv2` wird lazy importiert (erst beim tatsächlichen Einschalten), damit das
Modul unter Linux ohne installiertes `cv2` und ohne Kamera-Hardware weiterhin importierbar bleibt.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class KameraFehler(RuntimeError):
    """Ein erwarteter, benannter Fehlschlag (fehlendes cv2, kein Gerät) — kein Programmierfehler."""


@dataclass(frozen=True)
class KameraFrame:
    sequenz: int
    aufgenommen_ms: int
    breite: int
    hoehe: int
    bgr: bytes
    quelle: str


class KameraQuelle(Protocol):
    """Das injizierbare Backend. `Cv2KameraQuelle` ist die echte Implementierung; Tests setzen eine Fake-Quelle ein."""

    def oeffnen(self, index: int) -> bool: ...
    def lesen(self) -> tuple[int, int, bytes] | None: ...
    def schliessen(self) -> None: ...


class Cv2KameraQuelle:
    """Echtes Backend über `cv2.VideoCapture`. `cv2` wird erst bei `oeffnen()` importiert, nicht beim Modulimport."""

    def __init__(self) -> None:
        self._erfassung = None

    def oeffnen(self, index: int) -> bool:
        try:
            import cv2
        except ImportError as fehler:
            raise KameraFehler("cv2_nicht_installiert") from fehler
        self._erfassung = cv2.VideoCapture(index)
        return bool(self._erfassung.isOpened())

    def lesen(self) -> tuple[int, int, bytes] | None:
        if self._erfassung is None:
            return None
        ok, frame = self._erfassung.read()
        if not ok or frame is None:
            return None
        hoehe, breite = frame.shape[0], frame.shape[1]
        return breite, hoehe, frame.tobytes()

    def schliessen(self) -> None:
        if self._erfassung is not None:
            self._erfassung.release()
            self._erfassung = None


class Kamera:
    """Zustand, Sequenzierung und Fehlerbericht einer Kamera. Eine Instanz entspricht einer zuschaltbaren Kamera (R040)."""

    def __init__(self, *, quelle: KameraQuelle | None = None, jetzt_ms: Callable[[], int] | None = None) -> None:
        self._quelle = quelle if quelle is not None else Cv2KameraQuelle()
        self._jetzt_ms = jetzt_ms or (lambda: int(time.monotonic() * 1000))
        self.aktiv = False
        self.letzter_fehler: str | None = None
        self._index: int | None = None
        self._sequenz = 0

    SUCHE = range(4)

    def einschalten(self, index: int | None = None) -> bool:
        """Öffnet das Gerät wirklich; liefert False mit gesetztem `letzter_fehler`, wenn es fehlt — täuscht nichts vor.

        Ohne Index wird der erste Index von 0 bis 3 genommen, der nicht nur aufgeht, sondern auch ein Bild liefert (Rechner mit
        mehreren Kameras oder virtuellen Kameras beginnen oft nicht bei 0)."""
        if self.aktiv:
            return True
        self.letzter_fehler = None
        kandidaten = list(self.SUCHE) if index is None else [index]
        for kandidat in kandidaten:
            try:
                geoeffnet = self._quelle.oeffnen(kandidat)
            except KameraFehler as fehler:
                self.letzter_fehler = str(fehler)
                if index is not None:
                    return False
                continue
            if not geoeffnet:
                continue
            if index is None and self._quelle.lesen() is None:
                self._quelle.schliessen()  # geht auf, liefert aber kein Bild: nächster Index
                continue
            self.aktiv = True
            self.letzter_fehler = None
            self._index = kandidat
            self._sequenz = 0
            return True
        if self.letzter_fehler is None:
            self.letzter_fehler = "kamera_nicht_gefunden"
        return False

    def ausschalten(self) -> None:
        if self.aktiv:
            self._quelle.schliessen()
        self.aktiv = False
        self._index = None

    def frame_lesen(self) -> KameraFrame | None:
        """Ein Frame pro Aufruf, mit fortlaufender Sequenz und Aufnahmezeit; None bei Fehler oder wenn ausgeschaltet."""
        if not self.aktiv:
            return None
        ergebnis = self._quelle.lesen()
        if ergebnis is None:
            self.letzter_fehler = "kein_frame"
            return None
        breite, hoehe, daten = ergebnis
        self._sequenz += 1
        self.letzter_fehler = None
        return KameraFrame(sequenz=self._sequenz, aufgenommen_ms=self._jetzt_ms(), breite=breite, hoehe=hoehe,
                            bgr=daten, quelle=f"cv2:{self._index}")
