"""Die Objekte auf Daniels Bildschirm (G08): je Gate ein durchklickbares Pixel-Alpha-Fenster, das nur die Objekte mit `bildschirm=True` zeigt.

Das Fenster steht genau auf dem Gate (dem gebundenen Fenster oder dem Desktop), folgt ihm beim Verschieben und Skalieren, verschwindet mit ihm beim
Minimieren oder Schließen und kommt beim Wiederherstellen zurück. Objekte nur für Agenten (`bildschirm=False`) erscheinen hier nie: sie leben nur im Bild
des Empfängers (Komposition).
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from . import ziele
from .komposition import Arbeitsflaechen
from .zeichnen_render import rendern

Rechteck = tuple[int, int, int, int]
TAKT_S = 0.2


class ArbeitsflaechenAnzeige:
    def __init__(self, arbeit: Arbeitsflaechen, fenster_bauen: Callable[[Rechteck], object],
                 gate_zustand: Callable[[str], tuple[bool, bool, Rechteck | None]],
                 desktop: Callable[[], Rechteck], editor_offen: Callable[[], str | None] = lambda: None, takt_s: float = TAKT_S, bild_elemente=None):
        self._arbeit, self._bauen, self._zustand, self._desktop = arbeit, fenster_bauen, gate_zustand, desktop
        self._editor_offen = editor_offen  # Schlüssel des Gates, dessen Editor offen ist (dort zeigt der Editor die Objekte selbst)
        self._takt_s = takt_s
        self._bild_elemente = bild_elemente  # die schwebenden Bild-Elemente (eigene Fenster), gleicher Takt
        self.fenster: dict[str, object] = {}
        self._stand: dict[str, tuple] = {}
        self._stop = threading.Event()

    def _rect(self, schluessel: str) -> tuple[bool, Rechteck | None]:
        """(Gate da und sichtbar, Rechteck)."""
        if schluessel == "desktop":
            return True, self._desktop()
        if ziele.ist_fenster(schluessel):
            existiert, minimiert, rect = self._zustand(schluessel)
            return existiert and not minimiert and rect is not None, rect
        return False, None

    def tick(self) -> None:
        offen = self._editor_offen()
        for schluessel, dok in list(self._arbeit.dokumente.items()):
            objekte = dok.auf_dem_bildschirm()
            da, rect = self._rect(schluessel)
            if self._bild_elemente is not None:
                self._bild_elemente.tick(schluessel, dok, da, rect, schluessel == offen)
            soll = bool(objekte) and da and rect is not None and schluessel != offen
            fenster = self.fenster.get(schluessel)
            if not soll:
                if fenster is not None and self._stand.get(schluessel) != "weg":
                    fenster.verberge()
                    self._stand[schluessel] = "weg"
                continue
            breite, hoehe = rect[2] - rect[0], rect[3] - rect[1]
            if breite < 8 or hoehe < 8:
                continue
            stand = (dok.version, rect)
            if fenster is None:
                fenster = self.fenster[schluessel] = self._bauen(rect)
            if self._stand.get(schluessel) == stand:
                continue
            if self._stand.get(schluessel) in (None, "weg") or self._stand[schluessel][1] != rect:
                fenster.verschiebe(rect[0], rect[1], breite, hoehe)
            fenster.setze_rgba(rendern(objekte, breite, hoehe))
            fenster.zeige(aktivieren=False)
            self._stand[schluessel] = stand

    def starten(self, gui_post: Callable[[Callable[[], None]], None]) -> None:
        def lauf() -> None:
            while not self._stop.wait(self._takt_s):
                gui_post(self.tick)

        threading.Thread(target=lauf, name="arbeitsflaechen-anzeige", daemon=True).start()

    def stoppen(self) -> None:
        self._stop.set()

    def schliessen(self) -> None:
        if self._bild_elemente is not None:
            self._bild_elemente.schliessen()
        for fenster in self.fenster.values():
            fenster.schliessen()
        self.fenster.clear()
        self._stand.clear()
