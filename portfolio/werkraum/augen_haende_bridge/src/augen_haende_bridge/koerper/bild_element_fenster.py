"""Ein Bild-Element (G08): ein Bild als eigenes schwebendes Fenster der Bridge-Oberfläche.

Es steht dauerhaft in einem Gate (dem gebundenen Fenster oder dem Desktop) und ist immer direkt anfassbar: am Kopf verschieben, an den Kanten die Größe ändern,
Prozent-Knopf oder Mausrad machen es transparenter (kein X: Ausblenden nur über das Menü), Rechtsklick (mit gehaltener Bedientaste, wie bei allen Bridge-Elementen) öffnet das Menü
(Sichtbar für …, Deckkraft, Entfernen). Der Kopf liegt über dem Bild, das Fenster ist genau so groß wie das Objekt im Dokument.
"""

from __future__ import annotations

from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift
from .kamera_fenster import PROZENT_B, RAND, kante_bei

KOPF_H = 20
MIN_B, MIN_H = 64, 48

Rechteck = tuple[int, int, int, int]


def kopf_rechtecke(breite: int) -> dict[str, Rechteck]:
    """Nur der Prozent-Knopf: ein X zum Ausblenden gibt es bewusst nicht (zu leicht versehentlich gedrückt); Ausblenden und Entfernen stehen im Menü (Rechtsklick mit Bedientaste)."""
    return {"deckkraft": (breite - RAND - PROZENT_B, 1, breite - RAND, KOPF_H - 1)}


def _in(rechteck: Rechteck, x: int, y: int) -> bool:
    return rechteck[0] <= x < rechteck[2] and rechteck[1] <= y < rechteck[3]


class BildElementFenster(Fenster):
    klasse = "AuHBildElement"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, x: int, y: int, breite: int, hoehe: int, *, bild: tuple[bytes, int, int], name: str = "Bild",
                 bei_deckkraft: Callable[[int], None] = lambda p: None, bei_ausblenden: Callable[[], None] = lambda: None,
                 bei_menue: Callable[[int, int], None] = lambda x, y: None, modifikator: Callable[[], bool] | None = None):
        w.require_windows()
        self.bild = bild  # (bgr, breite, hoehe)
        self.name = name
        self._deckkraft_melden, self._ausblenden, self._menue, self._modifikator = bei_deckkraft, bei_ausblenden, bei_menue, modifikator
        self.f_text: Schrift | None = None
        super().__init__(x, y, breite, hoehe, titel=f"Bild · {name}", deckkraft=255, nicht_aktivieren=True)
        self._schrift_bauen()

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(12, 1.0), fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

    def prozent_setzen(self, prozent: int) -> None:
        self.setze_deckkraft(stil.deckkraft_alpha(max(5, min(100, prozent))))
        self.neu_zeichnen()

    def treffer(self, x: int, y: int) -> int | None:
        links, oben, rechts, unten = self.rechteck()
        cx, cy = x - links, y - oben
        breite, hoehe = rechts - links, unten - oben
        kante = kante_bei(cx, cy, breite, hoehe)
        if kante is not None:
            return kante
        if cy < KOPF_H and not any(_in(r, cx, cy) for r in kopf_rechtecke(breite).values()):
            return w.HTCAPTION
        return w.HTCLIENT

    def bei_nachricht(self, msg: int, wparam: int, lparam: int) -> int | None:
        if msg == w.WM_GETMINMAXINFO:
            import ctypes
            info = ctypes.cast(lparam, ctypes.POINTER(w.MINMAXINFO)).contents
            info.ptMinTrackSize.x, info.ptMinTrackSize.y = MIN_B, MIN_H
            return 0
        return None

    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        breite, _ = self.clientgroesse()
        rechtecke = kopf_rechtecke(breite)
        if _in(rechtecke["deckkraft"], x, y):
            self._prozent_melden(stil.naechste_stufe(self.deckkraft_prozent()))
        return 0

    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None:
        if self._modifikator is None or self._modifikator():
            links, oben, _r, _u = self.rechteck()
            self._menue(links + x, oben + y)
        return 0

    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None:
        self._prozent_melden(self.deckkraft_prozent() + (5 if delta > 0 else -5))
        return 0

    def _prozent_melden(self, prozent: int) -> None:
        prozent = max(10, min(100, prozent))
        self.prozent_setzen(prozent)
        self._deckkraft_melden(prozent)

    def bei_groesse(self, breite: int, hoehe: int) -> None:
        self.neu_zeichnen()

    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = leinwand.breite, leinwand.hoehe
        bgr, bild_b, bild_h = self.bild
        leinwand.fuellen(stil.FARBE_GRUND)
        leinwand.bgr_zeichnen(bgr, bild_b, bild_h, 0, 0, breite, hoehe)
        leinwand.fuellen(stil.FARBE_LEISTE, 0, 0, breite, KOPF_H)
        kopf_y = (KOPF_H - self.f_text.zellhoehe) // 2
        leinwand.text(RAND + 2, kopf_y, self.name[:24], stil.FARBE_TEXT, self.f_text)
        rechtecke = kopf_rechtecke(breite)
        d = rechtecke["deckkraft"]
        leinwand.rahmen(*d, stil.FARBE_TEXT_GEDAEMPFT, 1)
        prozent = f"{self.deckkraft_prozent()}%"
        leinwand.text(d[0] + (d[2] - d[0] - self.f_text.breite(leinwand.hdc, prozent)) // 2, kopf_y, prozent, stil.FARBE_TEXT, self.f_text)
        leinwand.rahmen(0, 0, breite, hoehe, stil.FARBE_TEXT_GEDAEMPFT, 1)

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
