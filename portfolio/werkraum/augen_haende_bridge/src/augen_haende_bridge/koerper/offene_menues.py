"""Das Register der gerade offenen Menüs des Körpers (Voraussetzung der Menü-Freigabe im Käfig).

Das Menü, das der Körper selbst geöffnet hat, kennt seine Einträge samt Befehls-Id, Text und Schirmrechteck. Der Agent nennt einen Eintrag beim Namen;
Koordinaten vom Agenten nimmt der Körper für Menüs nie an. Wer ein Menü zeigt, trägt es hier ein und nimmt es wieder heraus; ohne Eintrag (zum Beispiel unter Windows,
wo das Menü ein natives Popup ohne bekannte Rechtecke ist) bleibt jede Menü-Aktion abgelehnt.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MenueEintrag:
    befehl: int
    text: str
    rect: tuple[int, int, int, int]  # Bildschirmkoordinaten (links, oben, rechts, unten)
    aktiv: bool = True

    @property
    def mitte(self) -> tuple[int, int]:
        return ((self.rect[0] + self.rect[2]) // 2, (self.rect[1] + self.rect[3]) // 2)


@dataclass(frozen=True)
class OffenesMenue:
    kennung: int  # Fenster-ID des Menüs auf oberster Ebene: das, was `fenster_am_punkt` an einem Menüpunkt liefert
    art: str  # welches Menü es ist („raute“, …); leer = unbekannt, dann gibt es keine Freigabe
    eintraege: tuple[MenueEintrag, ...]
    schliessen: Callable[[], None] | None = field(default=None, compare=False)  # schließt das Menü (wie Esc); der Körper führt es selbst aus, es wird keine Taste simuliert


class OffeneMenues:
    def __init__(self) -> None:
        self._sperre = threading.Lock()
        self._offen: OffenesMenue | None = None

    def oeffnen(self, kennung: int, art: str, eintraege: list[MenueEintrag], schliessen: Callable[[], None] | None = None) -> None:
        with self._sperre:
            self._offen = OffenesMenue(int(kennung), art, tuple(eintraege), schliessen)

    def schliessen(self, kennung: int | None = None) -> None:
        with self._sperre:
            if kennung is None or (self._offen is not None and self._offen.kennung == int(kennung)):
                self._offen = None

    def aktuell(self) -> OffenesMenue | None:
        with self._sperre:
            return self._offen


REGISTER = OffeneMenues()

_art = threading.local()


@contextmanager
def menue_art(art: str):
    """`with menue_art("raute"): zeige_menue(...)`: das Menü, das in diesem Block aufgeht, bekommt diese Art. Ohne Block ist die Art leer."""
    vorher = getattr(_art, "wert", "")
    _art.wert = art
    try:
        yield
    finally:
        _art.wert = vorher


def aktuelle_art() -> str:
    return getattr(_art, "wert", "")
