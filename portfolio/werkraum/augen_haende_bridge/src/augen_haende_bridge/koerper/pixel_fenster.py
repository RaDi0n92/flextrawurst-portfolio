"""Ein Fenster mit Pixel-Alpha (UpdateLayeredWindow): beliebig geformte, weich auslaufende Inhalte ohne Hintergrund (G08).

Dient als Anzeige der Objekte auf Daniels Bildschirm (durchklickbar bis auf die Pixel, die man schaut) und als Editorfläche. Der Inhalt kommt als RGBA-Bild
(Pillow) vom gemeinsamen Zeichner; hier wird er nur auf den Bildschirm gebracht.
"""

from __future__ import annotations

import ctypes

from PIL import Image, ImageChops

from . import win32 as w
from .fenster import Fenster, Leinwand


def vormultipliziert_bgra(bild: Image.Image) -> bytes:
    """RGBA → BGRA mit vormultiplizierten Farbkanälen (so verlangt es UpdateLayeredWindow mit AC_SRC_ALPHA)."""
    r, g, b, a = bild.convert("RGBA").split()
    r, g, b = ImageChops.multiply(r, a), ImageChops.multiply(g, a), ImageChops.multiply(b, a)
    return Image.merge("RGBA", (b, g, r, a)).tobytes()


class PixelFenster(Fenster):
    klasse = "AuHPixel"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW | w.WS_EX_LAYERED

    def __init__(self, x: int, y: int, breite: int, hoehe: int, *, titel: str = "", durchklickbar: bool = True, nicht_aktivieren: bool = True):
        w.require_windows()
        self._pixel: Leinwand | None = None
        self.letztes_bild: Image.Image | None = None
        self.angenommen = False  # hat Windows das letzte Bild angenommen (UpdateLayeredWindow)
        # Durchklicken über den Fensterstil, nicht über `durchklickbar`: das ruft SetLayeredWindowAttributes auf, und danach lehnt manches
        # Windows (und Wine) UpdateLayeredWindow ab.
        self.exstil = type(self).exstil | (w.WS_EX_TRANSPARENT if durchklickbar else 0)
        super().__init__(x, y, breite, hoehe, titel=titel, deckkraft=None, durchklickbar=False, nicht_aktivieren=nicht_aktivieren)

    def setze_rgba(self, bild: Image.Image) -> bool:
        """Das Bild auf die Fenstergröße gebracht anzeigen. Liefert, ob Windows es angenommen hat."""
        breite, hoehe = self.clientgroesse()
        if breite <= 0 or hoehe <= 0:
            return False
        if bild.size != (breite, hoehe):
            bild = bild.resize((breite, hoehe))
        self.letztes_bild = bild
        if self._pixel is None or (self._pixel.breite, self._pixel.hoehe) != (breite, hoehe):
            if self._pixel is not None:
                self._pixel.freigeben()
            self._pixel = Leinwand(breite, hoehe)
        daten = vormultipliziert_bgra(bild)
        ctypes.memmove(self._pixel._bits.value, daten, len(daten))
        links, oben, _r, _u = self.rechteck()
        ziel, groesse, quelle = w.POINT(links, oben), w.SIZE(breite, hoehe), w.POINT(0, 0)
        mischen = w.BLENDFUNCTION(w.AC_SRC_OVER, 0, 255, w.AC_SRC_ALPHA)
        self.angenommen = bool(w.user32.UpdateLayeredWindow(self.hwnd, None, ctypes.byref(ziel), ctypes.byref(groesse), self._pixel.hdc,
                                                            ctypes.byref(quelle), 0, ctypes.byref(mischen), w.ULW_ALPHA))
        return self.angenommen

    def verschiebe(self, x: int, y: int, breite: int | None = None, hoehe: int | None = None) -> None:
        super().verschiebe(x, y, breite, hoehe)
        if self.letztes_bild is not None:
            self.setze_rgba(self.letztes_bild)  # UpdateLayeredWindow legt auch den Ort fest: nach dem Verschieben neu anzeigen

    def _paint(self) -> None:
        paint = w.PAINTSTRUCT()
        w.user32.BeginPaint(self.hwnd, ctypes.byref(paint))
        w.user32.EndPaint(self.hwnd, ctypes.byref(paint))  # Inhalt kommt nur über setze_rgba

    def bei_zerstoert(self) -> None:
        if self._pixel is not None:
            self._pixel.freigeben()
            self._pixel = None


def _linux_einhaengen() -> None:
    from .plattform import ist_linux

    if ist_linux():
        from . import fenster_linux as fl

        globals()["PixelFenster"] = fl.PixelFenster


_linux_einhaengen()
