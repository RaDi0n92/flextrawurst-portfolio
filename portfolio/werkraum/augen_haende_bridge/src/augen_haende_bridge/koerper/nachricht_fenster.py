"""Banner und Ticker einer Raute (R026, R027): dieselbe Nachricht in zwei gleichzeitigen Darstellungen.

Stand nach Daniels Beschluss vom 2026-10-01 (vorher: Banner 3,3 s, Ticker 6,6 s klein):

* **Raum-Banner, 6,6 s.** Groß und präsent, breit und fast mittig im Zielbereich (das gebundene Programm, sonst der
  Desktop), mit einem Zug zu der Ecke oder Kante, an der die Raute steht; es bleibt innerhalb des Zielbereichs. Es ist schmal und hoch (höchstens
  35 % der Zielbreite): lange Texte werden mit vielen Zeilen von oben nach unten gelesen. Es überlappt nie die Box neben der Raute. Es erscheint mit vollem Kontrast und wird über 6,6 s kontinuierlich durchsichtiger, bis es sich auflöst.
* **Rauten-Box („Ticker“), 9,9 s.** Direkt an der Raute, größer als früher und hoch statt lang: der Text wird in einer
  schmalen Spalte umgebrochen. Sie bleibt 9,9 s stehen und passt in den Bildschirm (steht sie am rechten Rand, geht sie links der Raute auf).

Beide sind eigene kleine, klickdurchlässige Fenster (R118) und nehmen nie den Fokus. Die dauerhafte dritte
Darstellung ist der Chat (`chat_fenster.py`). Daniels eigene Worte erscheinen nur im Chat und als Raum-Banner, nicht als Box.
"""

from __future__ import annotations

from collections.abc import Callable

from . import stil
from . import win32 as w
from .chat_fenster import umbrechen
from .fenster import Fenster, Leinwand, Schrift

BANNER_DAUER_MS = 6600
TICKER_DAUER_MS = 9900  # Daniel 2026-10-01: „9,9 Sekunden neben der Raute“
FADE_TAKT_MS = 33
ZUG_ZUR_RAUTE = 0.35  # Anteil des Wegs von der Zielmitte zur Raute, den das Banner mitgeht
BANNER_MAX_ANTEIL = 0.35  # höchstens dieser Anteil der Zielbreite: schmal und hoch, damit man von oben nach unten liest (Daniel 2026-10-01)
BANNER_MAX_ZEILEN = 12  # längere Texte werden gekürzt („ …“); der ganze Text steht im Chat
TICKER_MAX_ZEILEN = 10
TICKER_ABSTAND = 6
LUECKE = 12  # Mindestabstand zwischen Banner, Box und Raute
TICKER_SPALTE_PX = 300  # Breite der Textspalte der Box neben der Raute (bei Faktor 1)
PAD = 10
TIMER_TAKT, TIMER_ENDE = 1, 2

Rechteck = tuple[int, int, int, int]


def _mitte(rechteck: Rechteck) -> tuple[int, int]:
    links, oben, rechts, unten = rechteck
    return (links + rechts) // 2, (oben + unten) // 2


def banner_breite(text_breite: int, ziel: Rechteck) -> int:
    ziel_breite = ziel[2] - ziel[0]
    return max(1, min(text_breite + 2 * PAD, int(ziel_breite * BANNER_MAX_ANTEIL)))


def schneidet(a: Rechteck, b: Rechteck, luecke: int = 0) -> bool:
    """Überlappen sich zwei Rechtecke (mit `luecke` Sicherheitsabstand)?"""
    return a[0] < b[2] + luecke and b[0] < a[2] + luecke and a[1] < b[3] + luecke and b[1] < a[3] + luecke


def _frei(kandidaten: list[tuple[int, int]], breite: int, hoehe: int, grenzen: Rechteck,
          meiden: list[tuple[Rechteck, int]]) -> tuple[int, int] | None:
    """Der erste Kandidat (in die Grenzen geklemmt), der keinem der `meiden` (Rechteck, Mindestabstand) in die Quere kommt."""
    for x, y in kandidaten:
        x = max(grenzen[0], min(x, grenzen[2] - breite))
        y = max(grenzen[1], min(y, grenzen[3] - hoehe))
        if not any(schneidet((x, y, x + breite, y + hoehe), m, luecke) for m, luecke in meiden):
            return x, y
    return None


def banner_position(ziel: Rechteck, raute: Rechteck, breite: int, hoehe: int, meiden: list[Rechteck] | tuple = ()) -> tuple[int, int]:
    """Fast mittig im Zielbereich, ein Stück zur Raute hingezogen, danach in den Zielbereich geklemmt. Überlappt das mit einem der
    `meiden` (die Box neben der Raute, die Raute), wird zur Seite, nach oben oder nach unten ausgewichen (nahe Plätze zuerst)."""
    ziel_x, ziel_y = _mitte(ziel)
    raute_x, raute_y = _mitte(raute)
    x = ziel_x + int((raute_x - ziel_x) * ZUG_ZUR_RAUTE) - breite // 2
    y = ziel_y + int((raute_y - ziel_y) * ZUG_ZUR_RAUTE) - hoehe // 2
    x = max(ziel[0], min(x, ziel[2] - breite))
    y = max(ziel[1], min(y, ziel[3] - hoehe))
    alle = [*meiden, raute]
    gemieden = [(m, LUECKE) for m in alle]
    if not any(schneidet((x, y, x + breite, y + hoehe), m, luecke) for m, luecke in gemieden):
        return x, y
    kandidaten: list[tuple[int, int]] = []
    for m in alle:
        kandidaten += [(m[0] - LUECKE - breite, y), (m[2] + LUECKE, y), (x, m[1] - LUECKE - hoehe), (x, m[3] + LUECKE)]
    kandidaten.sort(key=lambda k: abs(k[0] - x) + abs(k[1] - y))
    frei = _frei(kandidaten, breite, hoehe, ziel, gemieden)
    return frei if frei is not None else (x, y)


def banner_alpha(vergangen_ms: int) -> int:
    """Voller Kontrast am Anfang, linear bis unsichtbar nach `BANNER_DAUER_MS` (6,6 s)."""
    rest = max(0.0, 1.0 - vergangen_ms / BANNER_DAUER_MS)
    return max(0, min(255, round(255 * rest)))


def ticker_position(raute: Rechteck, hoehe: int, breite: int = 0, grenzen: Rechteck | None = None,
                    meiden: list[Rechteck] | tuple = ()) -> tuple[int, int]:
    """Direkt rechts neben der Raute, vertikal auf ihrer Mitte. Mit `grenzen` bleibt die Box im Bildschirm: reicht rechts der Platz
    nicht, geht sie links der Raute auf; oben und unten wird geklemmt. Mit `meiden` (das Banner) weicht sie dem aus:
    erst links, dann über, dann unter der Raute."""
    _x, mitte_y = _mitte(raute)
    x, y = raute[2] + TICKER_ABSTAND, mitte_y - hoehe // 2
    if grenzen is None:
        return x, y
    kandidaten = [(x, y), (raute[0] - TICKER_ABSTAND - breite, y), (raute[0], raute[1] - TICKER_ABSTAND - hoehe),
                  (raute[0], raute[3] + TICKER_ABSTAND)]
    frei = _frei(kandidaten, breite, hoehe, grenzen, [(raute, 0), *[(m, LUECKE) for m in meiden]])
    if frei is not None:
        return frei
    if x + breite > grenzen[2]:
        x = raute[0] - TICKER_ABSTAND - breite
    return max(grenzen[0], min(x, grenzen[2] - breite)), max(grenzen[1], min(y, grenzen[3] - hoehe))


def _textmass(name: str, hoehe_px: int, fett: bool, text: str) -> tuple[Schrift, int]:
    screen = w.user32.GetDC(None)
    hdc = w.gdi32.CreateCompatibleDC(screen)
    try:
        schrift = Schrift(hdc, name, hoehe_px, fett=fett, fest=False)
        return schrift, schrift.breite(hdc, text)
    finally:
        w.gdi32.DeleteDC(hdc)
        w.user32.ReleaseDC(None, screen)


def kuerzen(zeilen: list[str], maximal: int, max_breite: int, messen: Callable[[str], int]) -> list[str]:
    """Höchstens `maximal` Zeilen; die letzte endet dann auf „ …“ und bleibt innerhalb von `max_breite`."""
    if len(zeilen) <= maximal:
        return zeilen
    kept = zeilen[:maximal]
    letzte = kept[-1].rstrip()
    while letzte and messen(letzte + " …") > max_breite:
        letzte = letzte[:-1].rstrip()
    kept[-1] = letzte + " …"
    return kept


def _textzeilen(name: str, hoehe_px: int, fett: bool, text: str, max_breite: int,
                max_zeilen: int = 1000) -> tuple[Schrift, list[str], int]:
    """Schrift, die umgebrochenen (und bei `max_zeilen` gekürzten) Zeilen (höchstens `max_breite` breit) und die Breite der breitesten."""
    screen = w.user32.GetDC(None)
    hdc = w.gdi32.CreateCompatibleDC(screen)
    try:
        schrift = Schrift(hdc, name, hoehe_px, fett=fett, fest=False)
        messen = lambda t: schrift.breite(hdc, t)  # noqa: E731
        zeilen = kuerzen(umbrechen(text, max(20, max_breite), messen), max_zeilen, max(20, max_breite), messen)
        return schrift, zeilen, max(schrift.breite(hdc, z) for z in zeilen)
    finally:
        w.gdi32.DeleteDC(hdc)
        w.user32.ReleaseDC(None, screen)


class BannerFenster(Fenster):
    klasse = "AuHBanner"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, *, text: str, farbe_hex: str, ziel_rechteck: Rechteck, raute_rechteck: Rechteck,
                 jetzt_ms: Callable[[], int], geschlossen: Callable[[], None] = lambda: None,
                 meiden: Callable[[], list[Rechteck]] | None = None):
        w.require_windows()
        self.text = text
        self.farbe = w.rgb_hex(farbe_hex)
        self._jetzt_ms = jetzt_ms
        self._geschlossen = geschlossen
        max_breite = int((ziel_rechteck[2] - ziel_rechteck[0]) * BANNER_MAX_ANTEIL) - 2 * PAD
        self.f_text, self.zeilen, text_breite = _textzeilen(stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(22, 1.0), True, text, max_breite,
                                                           BANNER_MAX_ZEILEN)
        breite = banner_breite(text_breite, ziel_rechteck)
        hoehe = len(self.zeilen) * self.f_text.zellhoehe + 2 * PAD
        x, y = banner_position(ziel_rechteck, raute_rechteck, breite, hoehe, meiden() if meiden is not None else ())
        super().__init__(x, y, breite, hoehe, titel=f"Banner: {text[:32]}", deckkraft=255, durchklickbar=True,
                         nicht_aktivieren=True)
        self.start_ms = jetzt_ms()
        self.starte_timer(TIMER_TAKT, FADE_TAKT_MS)

    def bei_timer(self, ident: int) -> None:
        if ident != TIMER_TAKT:
            return
        vergangen = self._jetzt_ms() - self.start_ms
        if vergangen >= BANNER_DAUER_MS:
            self.stoppe_timer(TIMER_TAKT)
            self._geschlossen()
            self.schliessen()
            return
        self.setze_deckkraft(banner_alpha(vergangen))

    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(self.farbe)
        for i, zeile in enumerate(self.zeilen):
            leinwand.text(PAD, PAD + i * self.f_text.zellhoehe, zeile, stil.FARBE_GRUND, self.f_text)

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None


class TickerFenster(Fenster):
    klasse = "AuHTicker"
    fensterstil = w.WS_POPUP
    exstil = w.WS_EX_TOPMOST | w.WS_EX_TOOLWINDOW

    def __init__(self, *, text: str, farbe_hex: str, raute_rechteck: Rechteck,
                 geschlossen: Callable[[], None] = lambda: None, grenzen: Callable[[], Rechteck] | None = None,
                 meiden: Callable[[], list[Rechteck]] | None = None):
        w.require_windows()
        self.text = text
        self.farbe = w.rgb_hex(farbe_hex)
        self._geschlossen = geschlossen
        self._grenzen = grenzen
        self._meiden = meiden
        self.f_text, self.zeilen, text_breite = _textzeilen(stil.SCHRIFT_OBERFLAECHE[0], stil.skaliert(16, 1.0), False, text,
                                                           stil.skaliert(TICKER_SPALTE_PX, 1.0), TICKER_MAX_ZEILEN)
        breite, hoehe = text_breite + 2 * PAD, len(self.zeilen) * self.f_text.zellhoehe + 2 * PAD
        x, y = ticker_position(raute_rechteck, hoehe, breite, grenzen() if grenzen is not None else None,
                               meiden() if meiden is not None else ())
        super().__init__(x, y, breite, hoehe, titel=f"Ticker: {text[:32]}",
                         deckkraft=stil.deckkraft_alpha(90), durchklickbar=True, nicht_aktivieren=True)
        self.starte_timer(TIMER_ENDE, TICKER_DAUER_MS)

    def an_raute(self, raute_rechteck: Rechteck) -> None:
        """Folgt der Raute, wenn sie währenddessen verschoben wird."""
        x, y = ticker_position(raute_rechteck, self.hoehe, self.breite, self._grenzen() if self._grenzen is not None else None,
                               self._meiden() if self._meiden is not None else ())
        self.verschiebe(x, y)

    def bei_timer(self, ident: int) -> None:
        if ident != TIMER_ENDE:
            return
        self.stoppe_timer(TIMER_ENDE)
        self._geschlossen()
        self.schliessen()

    def zeichnen(self, leinwand: Leinwand) -> None:
        leinwand.fuellen(stil.FARBE_LEISTE)
        for i, zeile in enumerate(self.zeilen):
            leinwand.text(PAD, PAD + i * self.f_text.zellhoehe, zeile, self.farbe, self.f_text)
        leinwand.rahmen(0, 0, leinwand.breite, leinwand.hoehe, self.farbe, 1)

    def bei_zerstoert(self) -> None:
        if self.f_text is not None:
            self.f_text.freigeben()
            self.f_text = None
