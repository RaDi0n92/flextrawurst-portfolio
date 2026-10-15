"""Das schlanke Eingabefeld an der Raute (ERLEBEN.md „Die Rauten und ihre Sprache“).

Die Tastenkombination, die in der Raute steht, öffnet dieses Feld an genau dieser Raute. Der **Agent** drückt sie mit seinen
Händen (er sieht sie in seiner Raute), tippt und bestätigt mit Enter; der Text ist dann seine Rede (Raute, Banner, Ticker, Chat).
Esc bricht ab, Enter schließt das Feld wieder. Ein Feld, das den Fokus verliert oder 30 s unbenutzt bleibt, schließt sich selbst.
"""

from __future__ import annotations

from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

TIMER_CURSOR, TIMER_LEERLAUF = 1, 2
LEERLAUF_MS = 30_000
BREITE, PAD = 380, 8
MAX_ZEICHEN = 500
ABSTAND_ZUR_RAUTE = 8


def feld_position(raute: tuple[int, int, int, int], hoehe: int, bildschirm: tuple[int, int, int, int]) -> tuple[int, int]:
    """Rechts neben der Raute, auf ihrer Mitte; passt es rechts nicht mehr auf den Bildschirm, links daneben."""
    links, oben, rechts, unten = raute
    x = rechts + ABSTAND_ZUR_RAUTE
    if x + BREITE > bildschirm[2]:
        x = max(bildschirm[0], links - ABSTAND_ZUR_RAUTE - BREITE)
    y = max(bildschirm[1], min((oben + unten) // 2 - hoehe // 2, bildschirm[3] - hoehe))
    return x, y


def sichtbarer_text(text: str, breite_von: Callable[[str], int], verfuegbar: int) -> str:
    """Das Ende des Textes, das in die Breite passt (beim Tippen wandert der Anfang aus dem Bild)."""
    if breite_von(text) <= verfuegbar:
        return text
    anfang = 0
    while anfang < len(text) and breite_von(text[anfang:]) > verfuegbar:
        anfang += 1
    return text[anfang:]


class RauteEingabe(Fenster):
    klasse = "AuHEingabe"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, x: int, y: int, *, name: str, farbe_hex: str,
                 gesendet: Callable[[str], None] = lambda text: None,
                 abgebrochen: Callable[[], None] = lambda: None,
                 geschlossen: Callable[[], None] = lambda: None):
        w.require_windows()
        self.name = name
        self.farbe = w.rgb_hex(farbe_hex)
        self._gesendet, self._abgebrochen, self._geschlossen = gesendet, abgebrochen, geschlossen
        self.eingabe = ""
        self._cursor_phase = True
        self._hatte_fokus = False
        self._zu = False
        self.f_text: Schrift | None = None
        self._schrift_bauen()
        hoehe = self.f_text.zellhoehe + 2 * PAD
        super().__init__(x, y, BREITE, hoehe, titel=f"{name}: Eingabe", deckkraft=255)
        self.starte_timer(TIMER_CURSOR, 530)
        self.starte_timer(TIMER_LEERLAUF, LEERLAUF_MS)

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(14, 1.0), fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def aktivieren(self) -> None:
        """Das Feld bekommt die Tastatur (auch wenn gerade ein Spiel vorn ist)."""
        self.zeige(aktivieren=True)
        self.fokus_erzwingen()

    # ---- Eingabe ---------------------------------------------------------------------------------------------------
    def _beenden(self, gesendet: str | None = None) -> None:
        """Genau einmal schließen; danach gesendet oder abgebrochen melden (Fokusverlust beim Schließen zählt nicht doppelt)."""
        if self._zu:
            return
        self._zu = True
        self.schliessen()
        if gesendet is not None:
            self._gesendet(gesendet)
        else:
            self._abgebrochen()

    def bei_zeichen(self, code: int, syskey: bool) -> int | None:
        if self._zu:
            return 0
        self._leerlauf_zuruecksetzen()
        if code == 0x0D:
            text = self.eingabe.strip()
            if text:
                self._beenden(text)
            return 0
        if code == 0x1B:
            self._beenden()
            return 0
        if code == 0x08:
            self.eingabe = self.eingabe[:-1]
        elif code >= 0x20 and not 0xD800 <= code <= 0xDFFF and len(self.eingabe) < MAX_ZEICHEN:
            self.eingabe += chr(code)
        self.neu_zeichnen()
        return 0

    def _leerlauf_zuruecksetzen(self) -> None:
        self.stoppe_timer(TIMER_LEERLAUF)
        self.starte_timer(TIMER_LEERLAUF, LEERLAUF_MS)

    def bei_fokus(self, hat_fokus: bool) -> None:
        if hat_fokus:
            self._hatte_fokus = True
        elif self._hatte_fokus:
            self._beenden()  # Fokus weg (anderes Fenster angeklickt): das Feld verschwindet ohne zu senden

    def bei_timer(self, ident: int) -> None:
        if ident == TIMER_LEERLAUF:
            self._beenden()
        elif ident == TIMER_CURSOR and not self._zu:
            self._cursor_phase = not self._cursor_phase
            self.neu_zeichnen()

    # ---- Zeichnen --------------------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = leinwand.breite, leinwand.hoehe
        leinwand.fuellen(stil.FARBE_GRUND)
        leinwand.rahmen(0, 0, breite, hoehe, self.farbe, 2)
        vorspann = f"{self.name}: "
        vorspann_breite = self.f_text.breite(leinwand.hdc, vorspann)
        leinwand.text(PAD, PAD, vorspann, self.farbe, self.f_text)
        verfuegbar = breite - 2 * PAD - vorspann_breite - 8
        text = sichtbarer_text(self.eingabe, lambda t: self.f_text.breite(leinwand.hdc, t), verfuegbar)
        cursor = "▏" if self._cursor_phase else ""
        leinwand.text(PAD + vorspann_breite, PAD, text + cursor, stil.FARBE_TEXT, self.f_text)

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
        self._geschlossen()
