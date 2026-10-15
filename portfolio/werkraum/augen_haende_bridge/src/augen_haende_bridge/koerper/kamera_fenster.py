"""Das Kamerabild von Daniel bei einem Agenten: ein kleines Fenster, das dort steht, wo der Agent gerade ist.

Der Agent bekommt dasselbe Bild über den Bilderstrom (und sieht dieses Fenster außerdem in seinem Bildschirmausschnitt). Hier sieht
Daniel, was der Agent von ihm sieht — seitenverkehrt wie ein Spiegel, weil das so vertraut aussieht; der Agent bekommt das Bild
unverändert. Das Fenster lässt sich am Kopf verschieben, an den Kanten vergrößern und über den Prozent-Knopf transparenter machen.
"""

from __future__ import annotations

from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

KOPF_H = 20
RAND = 5
KNOPF_B = 20
PROZENT_B = 40
MIN_B, MIN_H = 96, 72

Rechteck = tuple[int, int, int, int]


def kopf_rechtecke(breite: int) -> dict[str, Rechteck]:
    schliessen = (breite - RAND - KNOPF_B, 1, breite - RAND, KOPF_H - 1)
    deckkraft = (schliessen[0] - 4 - PROZENT_B, 1, schliessen[0] - 4, KOPF_H - 1)
    return {"schliessen": schliessen, "deckkraft": deckkraft}


def bild_flaeche(breite: int, hoehe: int, bild_b: int, bild_h: int) -> Rechteck:
    """Das Bild passt (ohne Verzerrung) mittig in die Fläche unter dem Kopf: (links, oben, breite, hoehe)."""
    frei_b, frei_h = max(1, breite - 2), max(1, hoehe - KOPF_H - 1)
    faktor = min(frei_b / max(1, bild_b), frei_h / max(1, bild_h))
    b, h = max(1, int(bild_b * faktor)), max(1, int(bild_h * faktor))
    return 1 + (frei_b - b) // 2, KOPF_H + (frei_h - h) // 2, b, h


def kante_bei(x: int, y: int, breite: int, hoehe: int, rand: int = RAND) -> int | None:
    links, rechts, oben, unten = x < rand, x >= breite - rand, y < rand, y >= hoehe - rand
    if oben and links:
        return w.HTTOPLEFT
    if oben and rechts:
        return w.HTTOPRIGHT
    if unten and links:
        return w.HTBOTTOMLEFT
    if unten and rechts:
        return w.HTBOTTOMRIGHT
    if oben:
        return w.HTTOP
    if unten:
        return w.HTBOTTOM
    if links:
        return w.HTLEFT
    if rechts:
        return w.HTRIGHT
    return None


def _in(rechteck: Rechteck, x: int, y: int) -> bool:
    return rechteck[0] <= x < rechteck[2] and rechteck[1] <= y < rechteck[3]


class KameraFenster(Fenster):
    klasse = "AuHKamera"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, x: int, y: int, *, breite: int = 240, hoehe: int = 190, name: str = "", farbe_hex: str = "#FFFFFF",
                 verbergen_gewuenscht: Callable[[], None] = lambda: None):
        w.require_windows()
        self.name, self.farbe = name, w.rgb_hex(farbe_hex)
        self._verbergen = verbergen_gewuenscht
        self.bild = None  # (bgr, breite, hoehe) des letzten Frames
        self.f_text: Schrift | None = None
        super().__init__(x, y, breite, hoehe, titel=f"Kamera · {name}", deckkraft=stil.deckkraft_alpha(85), nicht_aktivieren=True)
        self._schrift_bauen()

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(12, 1.0), fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def setze_identitaet(self, name: str | None = None, farbe_hex: str | None = None) -> None:
        if name:
            self.name = name
            w.user32.SetWindowTextW(self.hwnd, f"Kamera · {name}")
        if farbe_hex:
            self.farbe = w.rgb_hex(farbe_hex)
        self.neu_zeichnen()

    def bild_setzen(self, bgr: bytes, breite: int, hoehe: int) -> None:
        self.bild = (bgr, breite, hoehe)
        self.neu_zeichnen()

    def bild_loeschen(self) -> None:
        self.bild = None
        self.neu_zeichnen()

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

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
            self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(self.deckkraft_prozent())))
            self.neu_zeichnen()
        elif _in(rechtecke["schliessen"], x, y):
            self._verbergen()
        return 0

    def bei_rad(self, delta: int, x: int, y: int, flags: int) -> int | None:
        """Mausrad über dem Bild: Deckkraft in 5-%-Schritten."""
        prozent = max(10, min(100, self.deckkraft_prozent() + (5 if delta > 0 else -5)))
        self.setze_deckkraft(stil.deckkraft_alpha(prozent))
        self.neu_zeichnen()
        return 0

    def bei_groesse(self, breite: int, hoehe: int) -> None:
        self.neu_zeichnen()

    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = leinwand.breite, leinwand.hoehe
        leinwand.fuellen(stil.FARBE_GRUND)
        leinwand.fuellen(stil.FARBE_LEISTE, 0, 0, breite, KOPF_H)
        kopf_y = (KOPF_H - self.f_text.zellhoehe) // 2
        leinwand.text(RAND + 2, kopf_y, f"{self.name[:16]} · ich"[:24], self.farbe, self.f_text)
        rechtecke = kopf_rechtecke(breite)
        d = rechtecke["deckkraft"]
        leinwand.rahmen(*d, stil.FARBE_TEXT_GEDAEMPFT, 1)
        prozent = f"{self.deckkraft_prozent()}%"
        leinwand.text(d[0] + (d[2] - d[0] - self.f_text.breite(leinwand.hdc, prozent)) // 2, kopf_y, prozent, stil.FARBE_TEXT, self.f_text)
        s = rechtecke["schliessen"]
        leinwand.fuellen(stil.FARBE_KNOPF, *s)
        mx, my, r = (s[0] + s[2]) // 2, (s[1] + s[3]) // 2, 4
        leinwand.linie(mx - r, my - r, mx + r + 1, my + r + 1, stil.FARBE_TEXT, 2)
        leinwand.linie(mx - r, my + r, mx + r + 1, my - r - 1, stil.FARBE_TEXT, 2)
        if self.bild is None:
            text = "Kamera startet …"
            leinwand.text((breite - self.f_text.breite(leinwand.hdc, text)) // 2, KOPF_H + (hoehe - KOPF_H - self.f_text.zellhoehe) // 2,
                          text, stil.FARBE_TEXT_GEDAEMPFT, self.f_text)
        else:
            bgr, bild_b, bild_h = self.bild
            links, oben, b, h = bild_flaeche(breite, hoehe, bild_b, bild_h)
            leinwand.bgr_zeichnen(bgr, bild_b, bild_h, links, oben, b, h, spiegeln=True)
        leinwand.rahmen(0, 0, breite, hoehe, self.farbe, 1)

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
