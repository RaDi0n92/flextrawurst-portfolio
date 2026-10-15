"""Die Regie- und Medienleiste unten links (Skizze, R028, R040, R041, UQ05): Mikrofon, Kamera, Regie und der große
Not-Aus-Knopf, alles für den gewählten Agenten.

Ein kleines schwebendes Fenster (R118), kein Overlay. Ganz oben ein Griff zum Verschieben, darunter der Name des
gewählten Agenten (ein Klick wechselt zum nächsten); unten ein Prozent-Knopf, der die Deckkraft weiterschaltet (R031). Die Knöpfe zeigen echten Zustand (an/aus/Fehler), keinen bloßen Schalter (V04): dahinter
hängen `kamera.py`/`mikrofon.py`. Die Regiesprüche (R029) sind Gesprächswünsche an die Sitzung — nicht mit
Laufpause, Bildpause oder Not-Aus zu verwechseln (R030).
"""

from __future__ import annotations

import math
from collections.abc import Callable

from . import stil
from . import win32 as w
from .fenster import Fenster, Leinwand, Schrift

BREITE = 76
GRIFF_H = 12
KOPF_H = 26
KNOPF_D = 44
LUECKE = 8
RAND = 16
DECK_H = 22
_KNOEPFE_ENDE = GRIFF_H + KOPF_H + LUECKE + 4 * (KNOPF_D + LUECKE)
HOEHE = _KNOEPFE_ENDE + DECK_H + 4
ABSTAND_ZUM_RAND = 12

KNOEPFE = ("mikrofon", "kamera", "regie", "notaus")
KNOPF_TEXT = {"mikrofon": "Mik", "kamera": "Cam", "regie": "Regie", "notaus": "STOP"}
ZUSTAENDE = ("aus", "startet", "ein", "fehler")

# R029: alle dokumentierten Regiesprüche, als Gesprächswunsch in die Sitzung getippt.
REGIESPRUECHE = (
    "Weiter so", "Mach mal", "Go!", "Warte kurz", "Pause", "Weiter", "Ja", "Nein", "Denk nach", "Denk neu",
    "Konzentrier dich", "Hast du eine andere Idee?", "Schritt zurück / Undo", "Neu scannen",
)

Rechteck = tuple[int, int, int, int]


def leiste_position(flaeche: Rechteck) -> tuple[int, int]:
    """Unten links auf der Arbeitsfläche."""
    return flaeche[0] + ABSTAND_ZUM_RAND, flaeche[3] - HOEHE - ABSTAND_ZUM_RAND


def knopf_rechtecke() -> dict[str, Rechteck]:
    """Kopfzeile plus vier Kreis-Knöpfe untereinander, in Fensterkoordinaten."""
    ergebnis: dict[str, Rechteck] = {"griff": (0, 0, BREITE, GRIFF_H),
                                     "agent": (0, GRIFF_H, BREITE, GRIFF_H + KOPF_H)}
    oben = GRIFF_H + KOPF_H + LUECKE
    for name in KNOEPFE:
        ergebnis[name] = (RAND, oben, RAND + KNOPF_D, oben + KNOPF_D)
        oben += KNOPF_D + LUECKE
    ergebnis["deckkraft"] = (8, _KNOEPFE_ENDE, BREITE - 8, _KNOEPFE_ENDE + DECK_H)
    return ergebnis


def knopf_bei(x: int, y: int) -> str | None:
    for name, (links, oben, rechts, unten) in knopf_rechtecke().items():
        if links <= x < rechts and oben <= y < unten:
            return name
    return None


def kreis(mitte_x: int, mitte_y: int, radius: int, ecken: int = 28) -> list[tuple[int, int]]:
    return [(round(mitte_x + radius * math.cos(2 * math.pi * i / ecken)),
             round(mitte_y + radius * math.sin(2 * math.pi * i / ecken))) for i in range(ecken)]


def knopf_farbe(name: str, zustand: str, notaus: bool) -> int:
    if name == "notaus":
        return stil.FARBE_FEHLER if not notaus else stil.FARBE_WARNUNG
    if name == "regie":
        return stil.FARBE_KNOPF_AKTIV
    return {"ein": stil.FARBE_OK, "fehler": stil.FARBE_FEHLER, "startet": stil.FARBE_WARNUNG}.get(zustand, stil.FARBE_KNOPF)


ZUSTANDSWORT = {"aus": "aus", "startet": "…", "ein": "an", "fehler": "Fehler"}


def zustandswort(name: str, zustand: str) -> str:
    """Das Wort unter „Mik“ und „Cam“: der Zustand darf nicht nur durch eine Farbe erkennbar sein. Für die anderen Knöpfe leer."""
    return ZUSTANDSWORT.get(zustand, "") if name in ("mikrofon", "kamera") else ""


def knopf_beschriftung(name: str, notaus: bool) -> str:
    return "frei" if name == "notaus" and notaus else KNOPF_TEXT[name]


class RegieFenster(Fenster):
    klasse = "AuHRegie"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, x: int, y: int, *,
                 agent_wechseln: Callable[[], None] = lambda: None,
                 mikrofon_umschalten: Callable[[], None] = lambda: None,
                 kamera_umschalten: Callable[[], None] = lambda: None,
                 regie_menue: Callable[[int, int], None] = lambda x, y: None,
                 notaus_umschalten: Callable[[], None] = lambda: None):
        w.require_windows()
        self.agent_name = "kein Agent"
        self.agent_farbe = stil.FARBE_TEXT_GEDAEMPFT
        self.mikrofon, self.kamera, self.notaus = "aus", "aus", False
        self.hinweis = ""
        self._knopf_unten: str | None = None
        self._aufrufe = {"agent": agent_wechseln, "mikrofon": mikrofon_umschalten, "kamera": kamera_umschalten,
                         "notaus": notaus_umschalten}
        self._regie_menue = regie_menue
        self.f_text: Schrift | None = None
        super().__init__(x, y, BREITE, HOEHE, titel="Regie und Medien", deckkraft=stil.deckkraft_alpha(90),
                         nicht_aktivieren=True)
        self._schrift_bauen()

    def _schrift_bauen(self) -> None:
        screen = w.user32.GetDC(None)
        hdc = w.gdi32.CreateCompatibleDC(screen)
        try:
            self.f_text = Schrift(hdc, stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(11, 1.0), fest=False)
        finally:
            w.gdi32.DeleteDC(hdc)
            w.user32.ReleaseDC(None, screen)

    def setze(self, *, agent_name: str | None = None, agent_farbe: int | None = None, mikrofon: str | None = None,
              kamera: str | None = None, notaus: bool | None = None, hinweis: str | None = None) -> None:
        if agent_name is not None:
            self.agent_name = agent_name
        if agent_farbe is not None:
            self.agent_farbe = agent_farbe
        if mikrofon is not None:
            self.mikrofon = mikrofon
        if kamera is not None:
            self.kamera = kamera
        if notaus is not None:
            self.notaus = notaus
        if hinweis is not None:
            self.hinweis = hinweis
        self.neu_zeichnen()

    def deckkraft_prozent(self) -> int:
        return stil.alpha_prozent(self.deckkraft or 255)

    def treffer(self, x: int, y: int) -> int | None:
        """Der Griff oben verschiebt das Fenster (Bildschirmkoordinaten wie bei allen Fenstern)."""
        _links, oben, _r, _u = self.rechteck()
        return w.HTCAPTION if y - oben < GRIFF_H else w.HTCLIENT

    def zustand_von(self, name: str) -> str:
        return {"mikrofon": self.mikrofon, "kamera": self.kamera}.get(name, "aus")

    # ---- Zeichnen --------------------------------------------------------------------------------------------------
    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(stil.FARBE_LEISTE)
        leinwand.rahmen(0, 0, BREITE, HOEHE, self.agent_farbe, 2)
        leinwand.fuellen(stil.farbe_hell(stil.FARBE_LEISTE, 1.8), 2, 2, BREITE - 2, GRIFF_H)
        for punkt in range(3):  # drei Punkte als Griff
            leinwand.fuellen(stil.FARBE_TEXT_GEDAEMPFT, BREITE // 2 - 10 + punkt * 10, GRIFF_H // 2 - 1,
                             BREITE // 2 - 6 + punkt * 10, GRIFF_H // 2 + 3)
        name = self.agent_name[:9]
        breite = self.f_text.breite(leinwand.hdc, name)
        leinwand.text(max(2, (BREITE - breite) // 2), GRIFF_H + (KOPF_H - self.f_text.zellhoehe) // 2, name,
                      self.agent_farbe, self.f_text)
        d_links, d_oben, d_rechts, d_unten = knopf_rechtecke()["deckkraft"]
        leinwand.rahmen(d_links, d_oben, d_rechts, d_unten, stil.FARBE_TEXT_GEDAEMPFT, 1)
        prozent = f"{self.deckkraft_prozent()}%"
        leinwand.text(d_links + (d_rechts - d_links - self.f_text.breite(leinwand.hdc, prozent)) // 2,
                      d_oben + (DECK_H - self.f_text.zellhoehe) // 2, prozent, stil.FARBE_TEXT, self.f_text)
        for knopf in KNOEPFE:
            links, oben, rechts, unten = knopf_rechtecke()[knopf]
            farbe = knopf_farbe(knopf, self.zustand_von(knopf), self.notaus)
            if self._knopf_unten == knopf:
                farbe = stil.farbe_hell(farbe, 1.3)
            leinwand.polygon(kreis((links + rechts) // 2, (oben + unten) // 2, KNOPF_D // 2), fuellfarbe=farbe,
                             randfarbe=stil.FARBE_TEXT, randbreite=1)
            text = knopf_beschriftung(knopf, self.notaus)
            tb = self.f_text.breite(leinwand.hdc, text)
            textfarbe = (stil.FARBE_GRUND if knopf in ("mikrofon", "kamera") and self.zustand_von(knopf) == "ein"
                         else stil.FARBE_TEXT)
            wort = zustandswort(knopf, self.zustand_von(knopf))
            if wort:  # der Zustand steht auch als Wort da, nicht nur als Farbe (UQ08)
                zeilen_h = self.f_text.zellhoehe
                y0 = (oben + unten - 2 * zeilen_h) // 2
                leinwand.text((links + rechts - tb) // 2, y0, text, textfarbe, self.f_text)
                wb = self.f_text.breite(leinwand.hdc, wort)
                leinwand.text((links + rechts - wb) // 2, y0 + zeilen_h - 1, wort, textfarbe, self.f_text)
            else:
                leinwand.text((links + rechts - tb) // 2, (oben + unten - self.f_text.zellhoehe) // 2, text, textfarbe, self.f_text)

    # ---- Bedienen --------------------------------------------------------------------------------------------------
    def bei_maus_runter(self, x: int, y: int, flags: int) -> int | None:
        self._knopf_unten = knopf_bei(x, y)
        if self._knopf_unten == "griff":
            self._knopf_unten = None
        if self._knopf_unten is not None:
            self.erfasse_maus()
            self.neu_zeichnen()
        return 0

    def bei_maus_hoch(self, x: int, y: int, flags: int) -> int | None:
        gedrueckt, self._knopf_unten = self._knopf_unten, None
        if gedrueckt is None:
            return 0
        self.gib_maus_frei()
        if knopf_bei(x, y) == gedrueckt:
            if gedrueckt == "deckkraft":
                self.setze_deckkraft(stil.deckkraft_alpha(stil.naechste_stufe(self.deckkraft_prozent())))
            elif gedrueckt == "regie":
                links, oben, _r, _u = self.rechteck()
                rechteck = knopf_rechtecke()["regie"]
                self._regie_menue(links + rechteck[2], oben + rechteck[1])
            else:
                self._aufrufe[gedrueckt]()
        self.neu_zeichnen()
        return 0

    def bei_maus_verloren(self) -> None:
        self._knopf_unten = None

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
