"""Das Bild genau eines Fensters (G06.7, R014, R120, R124): vollständig, auch wenn ein anderes Fenster davorliegt, und ehrlich, wenn das nicht gelingt.

Bisher schnitt der Bilderstrom das Zielfenster aus dem Bild des ganzen Bildschirms: lag ein anderes Fenster davor, standen dessen Pixel im Bild des Agenten. Jetzt
fragt er zuerst die Fensteraufnahme der Plattform (Windows: PrintWindow mit PW_RENDERFULLCONTENT; Linux: XComposite) und nimmt deren Bild, wenn es echten Inhalt hat.
Eine leere oder schwarze Aufnahme ist ein bekannter Fehlerfall (Spiele und Browser mit Hardwarebeschleunigung liefern über PrintWindow oft Schwarz): sie wird erkannt, und
das Bild fällt **sichtbar** auf den Bildschirmausschnitt zurück (`aufnahme: "ausschnitt"` mit Grund), nie still mit einem falschen Bild.

Plattformneutral: die Aufnahme selbst kommt als Funktion herein, hier stehen nur die Prüfung und die Entscheidung.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

AUFNAHME_FENSTER, AUFNAHME_AUSSCHNITT = "fenster", "ausschnitt"
GRUND_LEER, GRUND_FEHLT, GRUND_NICHT_UNTERSTUETZT, GRUND_FEHLER = "leer", "fehlt", "nicht_unterstuetzt", "fehler"
SCHWARZ_SCHWELLE = 2  # kein Farbkanal über diesem Wert = schwarz (Rauschen der Kodierung zählt noch als schwarz)


@dataclass(frozen=True)
class FensterBild:
    bgra: bytes
    breite: int
    hoehe: int
    aufnahme: str  # fenster | ausschnitt
    grund: str = ""  # nur beim Rückfall: warum das Fensterbild nicht genommen wurde


def ist_leer(bgra: bytes, breite: int, hoehe: int) -> bool:
    """Leer heißt: keine Bytes, falsche Größe, ganz durchsichtig oder ganz schwarz. Ein einfarbig helles Fenster (leeres weißes Blatt) ist echter Inhalt."""
    if breite < 1 or hoehe < 1 or len(bgra) < breite * hoehe * 4:
        return True
    n = breite * hoehe * 4
    if max(bgra[3:n:4]) == 0:  # alles durchsichtig (manche Aufnahmen setzen Alpha nicht: dann zählt nur Schwarz)
        return True
    return max(max(bgra[0:n:4]), max(bgra[1:n:4]), max(bgra[2:n:4])) <= SCHWARZ_SCHWELLE  # ohne numpy: die Windows-Fassung bringt es nicht mit


class FensterAufnahme:
    """Entscheidet je Fenster: Fensterbild oder Rückfall. Zählt, wie oft was vorkam, damit Daniel es sieht."""

    def __init__(self, fenster_bild: Callable[[int], tuple[bytes, int, int] | None] | None, leer: Callable[[bytes, int, int], bool] = ist_leer):
        self._fenster_bild, self._leer = fenster_bild, leer
        self.zaehler = {AUFNAHME_FENSTER: 0, AUFNAHME_AUSSCHNITT: 0}
        self.gruende: dict[str, int] = {}

    @property
    def verfuegbar(self) -> bool:
        return self._fenster_bild is not None

    def holen(self, kennung: int) -> FensterBild | None:
        """Das Fensterbild, oder None mit gemerktem Grund (der Aufrufer nimmt dann den Bildschirmausschnitt und nennt den Grund im Bild-Eintrag)."""
        self.letzter_grund = GRUND_NICHT_UNTERSTUETZT
        if self._fenster_bild is None:
            return self._rueckfall(GRUND_NICHT_UNTERSTUETZT)
        try:
            ergebnis = self._fenster_bild(int(kennung))
        except Exception:
            return self._rueckfall(GRUND_FEHLER)
        if ergebnis is None:
            return self._rueckfall(GRUND_FEHLT)
        bgra, breite, hoehe = ergebnis
        if self._leer(bgra, breite, hoehe):
            return self._rueckfall(GRUND_LEER)
        self.zaehler[AUFNAHME_FENSTER] += 1
        self.letzter_grund = ""
        return FensterBild(bgra, breite, hoehe, AUFNAHME_FENSTER)

    def _rueckfall(self, grund: str) -> None:
        self.letzter_grund = grund
        self.zaehler[AUFNAHME_AUSSCHNITT] += 1
        self.gruende[grund] = self.gruende.get(grund, 0) + 1
        return None

    letzter_grund = ""


# ---- Was bei welchem Zustand des Ziels ankommt ------------------------------------------------------------------------------
def aussage(zustand: str, fensteraufnahme: bool) -> dict:
    """Die feste Aussage je Zielzustand (Statustext und Fähigkeit): kleine Fenster kommen wie sie sind, verdeckte vollständig nur mit Fensteraufnahme, minimierte und
    geschlossene gar nicht. Minimierte Ziele sind nicht gefordert (Daniel, R123), sie werden nur ehrlich gemeldet."""
    tabelle = {
        "ok": ("Bild des Fensters", "frisch"),
        "verdeckt": (("Bild des ganzen Fensters trotz davorliegender Fenster", "frisch") if fensteraufnahme
                     else ("Bild enthält die Fenster davor, die Fensteraufnahme fehlt", "fremde_pixel")),
        "minimiert": ("minimiert: keine Aufnahme, das letzte Bild bleibt stehen", "keine_aufnahme"),
        "inaktiv": ("im Hintergrund, Bild frisch", "frisch"),
        "weg": ("Fenster geschlossen: keine Bilder, bis ein Ziel neu gebunden wird", "keine_aufnahme"),
    }
    text, faehigkeit = tabelle.get(zustand, ("Zustand unbekannt", "unbekannt"))
    return {"zustand": zustand, "statustext": text, "faehigkeit": faehigkeit}
