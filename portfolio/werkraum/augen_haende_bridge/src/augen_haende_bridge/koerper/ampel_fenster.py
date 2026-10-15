"""Das Ampel-Fenster eines Agenten: drei Lampen (Augen, Hände, Ziel), jede zeigt das Schlimmste ihrer Gruppe.

Zustände (Berechnung in `ampel.py`):

* Blau = läuft, Orange = Achtung, Rot = kaputt (blinkt, piept beim Wechsel auf Rot), Grau = ausdrücklich aus.
* Klick auf eine rote Lampe behebt, wenn es eine Behebung gibt; sonst erklärt der Chat die Lampe.
* Strg+Alt + Rechtsklick: Menü mit allen Funktionen (auch 40), jede ausgeschrieben mit Erklärung, dahinter in Klammern ihr Zustand; dazu
  Deckkraft, größer, kleiner, Sichtbarkeitsregel (immer oder nur bei einem Programm) und Ein-/Ausblenden, wie bei der Raute.

Bedienung wie bei der Raute: durchklickbar; mit gehaltener Bedientaste (Strg+Alt) überall im Fenster ziehen, ein Klick ohne Zug wirkt auf die
Lampe; Größe, Deckkraft, Regel und Ausblenden über das Menü. Rahmen und Name tragen die Farbe des Agenten.
"""

from __future__ import annotations

from collections.abc import Callable

from . import ampel, stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

BASIS_BREITE = 150  # bei Faktor 1: drei Lampen nebeneinander
HOEHE = 26
LAMPE_D = 14
FAKTOR_MIN, FAKTOR_MAX, FAKTOR_SCHRITT = 0.7, 3.0, 0.3
ZIEH_SCHWELLE = 4  # Pixel Mausbewegung, bevor ein Runterdrücken als Ziehen statt als Klick zählt (wie bei der Raute)
TIMER_DATEN, TIMER_BLINK = 1, 2
DATEN_MS, BLINK_MS = 700, 450

Rechteck = tuple[int, int, int, int]

BLAU, ORANGE, ROT, GRAU = w.rgb(45, 125, 255), w.rgb(255, 152, 0), stil.FARBE_FEHLER, stil.FARBE_KNOPF
FARBEN = {ampel.GRUEN: BLAU, ampel.GELB: ORANGE, ampel.ROT: ROT, ampel.GRAU: GRAU}


def klemmen(faktor: float) -> float:
    return max(FAKTOR_MIN, min(FAKTOR_MAX, round(faktor, 2)))


def _s(wert: float, faktor: float) -> int:
    return max(1, round(wert * faktor))


def masse(faktor: float, zeilen: int = 0) -> tuple[int, int]:
    return _s(BASIS_BREITE, faktor), _s(HOEHE, faktor)


def lampen_mitte(index: int, faktor: float) -> tuple[int, int]:
    """Mittelpunkt der Lampe `index` (0 bis 2) in Fensterkoordinaten."""
    b, h = masse(faktor)
    return (2 * index + 1) * b // 6, h // 2


LAMPEN_NAMEN = ("Augen", "Hände", "Ziel")
LAMPEN_BUCHSTABEN = ("A", "H", "Z")  # Daniel 2026-10-03: neben jeder Lampe der Anfangsbuchstabe ihrer Funktion; ohne Farbe lesbar


def buchstabe_links(index: int, faktor: float) -> int:
    """Linke Kante des Buchstabens neben Lampe `index`: rechts vom Lampenrand, innerhalb des eigenen Drittels."""
    b, _h = masse(faktor)
    mx, _my = lampen_mitte(index, faktor)
    return mx + _s(LAMPE_D, faktor) // 2 + _s(5, faktor)


def lampe_bei(x: int, y: int, faktor: float, anzahl: int = 3) -> int | None:
    b, h = masse(faktor)
    if not (0 <= y < h and 0 <= x < b):
        return None
    i = min(anzahl - 1, x * 3 // b)
    return i if i < anzahl else None


def kuerzen(text: str, max_zeichen: int) -> str:
    return text if len(text) <= max_zeichen else text[:max(1, max_zeichen - 1)] + "…"


def kreis(mitte_x: int, mitte_y: int, radius: int, ecken: int = 20) -> list[tuple[int, int]]:
    import math

    return [(round(mitte_x + radius * math.cos(2 * math.pi * i / ecken)),
             round(mitte_y + radius * math.sin(2 * math.pi * i / ecken))) for i in range(ecken)]


def hex_zu_rgb(farbe_hex: str, ersatz: int | None = None) -> int:
    try:
        h = farbe_hex.lstrip("#")
        return w.rgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except (ValueError, IndexError, AttributeError):
        return stil.FARBE_KNOPF_AKTIV if ersatz is None else ersatz


class AmpelFenster(Fenster):
    klasse = "AuHAmpel"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, x: int, y: int, *, name: str = "Agent",
                 daten: Callable[[str], list] = lambda name: [],
                 aktion: Callable[[str, str], None] = lambda agent, name: None,
                 menue: Callable[[str, int, int], None] = lambda agent, x, y: None,
                 farbe: Callable[[], str] = lambda: "",
                 faktor: float = 1.0):
        w.require_windows()
        self.agent_name = name
        self._ampel_daten, self._ampel_aktion, self._ampel_menue, self._ampel_farbe = daten, aktion, menue, farbe
        self.faktor = klemmen(faktor)
        self.lampen: list[ampel.Lampe] = []
        self._phase = True
        self._unten: int | None = None
        self._ziehanker = None
        self._fenster_anker = None
        self._ziehen = False
        self.f_name = self.f_zeile = None
        b, h = masse(self.faktor, 0)
        super().__init__(x, y, b, h, titel=f"Ampel {name}", deckkraft=stil.deckkraft_alpha(96), nicht_aktivieren=True)
        self._schrift_bauen()
        self.starte_timer(TIMER_DATEN, DATEN_MS, self.aktualisieren)
        self.starte_timer(TIMER_BLINK, BLINK_MS, self._blinken)

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            name = stil.SCHRIFT_OBERFLAECHE[0]
            self.f_name = Schrift(hdc, name, _s(14, self.faktor), fett=True, fest=False)
            self.f_zeile = Schrift(hdc, name, _s(12, self.faktor), fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def faktor_setzen(self, faktor: float) -> None:
        faktor = klemmen(faktor)
        if faktor == self.faktor:
            return
        self.faktor = faktor
        self._schrift_bauen()
        self._an_inhalt_anpassen()
        self.neu_zeichnen()

    def _an_inhalt_anpassen(self) -> None:
        links, oben, _r, _u = self.rechteck()
        b, h = masse(self.faktor)
        self.verschiebe(links, oben, b, h)

    # ---- Daten und Takt --------------------------------------------------------------------------------------------
    def aktualisieren(self) -> None:
        try:
            self.lampen = ampel.drei_lampen(list(self._ampel_daten(self.agent_name)))
        except Exception:
            return
        self.neu_zeichnen()

    def _blinken(self) -> None:
        self._phase = not self._phase
        if any(l.blinkt for l in self.lampen):
            self.neu_zeichnen()

    def treffer(self, x: int, y: int) -> int | None:
        # Klick und Zug werden selbst unterschieden (siehe bei_maus_*), kein System-Fensterzug über HTCAPTION.
        return w.HTCLIENT

    def groesser(self, schritt: float = FAKTOR_SCHRITT) -> None:
        self.faktor_setzen(self.faktor + schritt)

    def deckkraft_weiter(self) -> None:
        self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(stil.alpha_prozent(self.deckkraft or 255))))

    # ---- Zeichnen --------------------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        breite, hoehe = masse(self.faktor)
        agentenfarbe = hex_zu_rgb(self._ampel_farbe())
        leinwand.fuellen(stil.FARBE_LEISTE)
        d = _s(LAMPE_D, self.faktor)
        for i, name in enumerate(LAMPEN_NAMEN):
            lampe = self.lampen[i] if i < len(self.lampen) else None
            mx, my = lampen_mitte(i, self.faktor)
            farbe = FARBEN.get(lampe.farbe, GRAU) if lampe else GRAU
            hell = lampe is None or (not lampe.blinkt) or self._phase
            if hell and lampe is not None and lampe.farbe != ampel.GRAU:
                leinwand.polygon(kreis(mx, my, d // 2 + max(2, d // 4)), fuellfarbe=stil.mischen(farbe, stil.FARBE_LEISTE, 0.7))
            if self._unten == i:
                farbe = stil.farbe_hell(farbe, 1.3)
            leinwand.polygon(kreis(mx, my, d // 2), fuellfarbe=farbe if hell else stil.mischen(farbe, stil.FARBE_LEISTE, 0.75),
                             randfarbe=stil.mischen(farbe, w.rgb(255, 255, 255), 0.35), randbreite=1)
            leinwand.text(buchstabe_links(i, self.faktor), my - self.f_zeile.zellhoehe // 2, LAMPEN_BUCHSTABEN[i], stil.FARBE_TEXT, self.f_zeile)
        leinwand.rahmen(0, 0, breite, hoehe, agentenfarbe, 2)

    # ---- Bedienen (wie die Raute) -----------------------------------------------------------------------------------
    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        self.erfasse_maus()
        self._ziehanker = self.maus_position()
        links, oben, _r, _u = self.rechteck()
        self._fenster_anker = (links, oben)
        self._ziehen = False
        self._unten = lampe_bei(x, y, self.faktor, len(self.lampen))
        self.neu_zeichnen()
        return 0

    def bei_maus_bewegt(self, x: int, y: int, flags: int) -> int | None:
        if self._ziehanker is None or not flags & 0x0001:
            return 0
        schirm_x, schirm_y = self.maus_position()
        dx, dy = schirm_x - self._ziehanker[0], schirm_y - self._ziehanker[1]
        if not self._ziehen and (abs(dx) > ZIEH_SCHWELLE or abs(dy) > ZIEH_SCHWELLE):
            self._ziehen = True
            self._unten = None
        if self._ziehen and self._fenster_anker is not None:
            self.verschiebe(self._fenster_anker[0] + dx, self._fenster_anker[1] + dy)
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        if self._ziehanker is None:
            return 0
        war_ziehen, gedrueckt = self._ziehen, self._unten  # vor gib_maus_frei lesen: es ruft bei_maus_verloren auf und löscht beides
        self.gib_maus_frei()
        self._ziehanker = self._fenster_anker = self._unten = None
        self._ziehen = False
        if not war_ziehen and gedrueckt is not None and gedrueckt < len(self.lampen):
            lampe = self.lampen[gedrueckt]
            self._ampel_aktion(self.agent_name, lampe.behebe if lampe.behebe else f"gruppe:{lampe.kennung}")
        self.neu_zeichnen()
        return 0

    def bei_rechtsklick(self, x: int, y: int, flags: int) -> int | None:
        links, oben, _r, _u = self.rechteck()
        self._ampel_menue(self.agent_name, links + x, oben + y)
        return 0

    def bei_maus_verloren(self) -> None:
        self._ziehanker = self._fenster_anker = self._unten = None
        self._ziehen = False
