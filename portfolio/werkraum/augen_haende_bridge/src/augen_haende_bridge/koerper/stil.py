"""Farben, Schriften und Deckkraft des Körpers an einer Stelle."""

from __future__ import annotations

from . import win32 as w

# R031: »66 % transparent« heißt 34 % Deckkraft. Beide Begriffe stehen in der Anzeige.
DECKKRAFT_START_PROZENT = 34
DECKKRAFT_STUFEN_PROZENT = (34, 50, 75, 100)

SCHRIFT_TERMINAL = ("Cascadia Mono", "Consolas", "Courier New")
SCHRIFT_OBERFLAECHE = ("Segoe UI", "Tahoma", "Arial")
SCHRIFT_ERSATZ = ("Segoe UI Symbol", "MS Gothic", "Segoe UI Emoji", "Arial Unicode MS")

FARBE_GRUND = w.rgb(12, 12, 12)
FARBE_TITEL = w.rgb(30, 32, 42)
FARBE_LEISTE = w.rgb(24, 26, 34)
FARBE_TEXT = w.rgb(226, 228, 235)
FARBE_TEXT_GEDAEMPFT = w.rgb(140, 146, 160)
FARBE_KNOPF = w.rgb(52, 56, 70)
FARBE_KNOPF_AKTIV = w.rgb(84, 92, 120)
FARBE_AUSWAHL = w.rgb(38, 79, 120)
FARBE_FEHLER = w.rgb(231, 72, 86)
FARBE_OK = w.rgb(22, 198, 12)
FARBE_WARNUNG = w.rgb(249, 241, 165)

# Rautenfarben für Agenten ohne eigene Wahl (Cyan, Gelb, Magenta, Grün, Blau, Orange, Violett, Rosa)
AGENTENFARBEN = ("#00E5FF", "#FFD600", "#FF0055", "#00E676", "#2979FF", "#FF9100", "#B388FF", "#FF80AB")


def agentenfarbe(name: str) -> str:
    """Stabile Farbe je Agentenname: dieselbe bei jedem Start (das eingebaute hash() wechselt mit jedem Prozess)."""
    import zlib

    return AGENTENFARBEN[zlib.crc32(name.encode("utf-8")) % len(AGENTENFARBEN)]


def deckkraft_alpha(prozent: int) -> int:
    return max(0, min(255, round(prozent * 255 / 100)))


def alpha_prozent(alpha: int) -> int:
    return round(alpha * 100 / 255)


def naechste_stufe(prozent: int) -> int:
    for stufe in DECKKRAFT_STUFEN_PROZENT:
        if stufe > prozent + 1:
            return stufe
    return DECKKRAFT_STUFEN_PROZENT[0]


def kuerzel_aus_name(name: str) -> str:
    buchstaben = [c for c in name if c.isalnum()]
    return "".join(buchstaben[:2]).upper() or "?"


def farbe_hell(farbe: int, faktor: float) -> int:
    r, g, b = farbe & 0xFF, (farbe >> 8) & 0xFF, (farbe >> 16) & 0xFF
    return w.rgb(min(255, int(r * faktor)), min(255, int(g * faktor)), min(255, int(b * faktor)))


def mischen(farbe: int, ziel: int, anteil: float) -> int:
    """`farbe` um `anteil` (0 bis 1) zur Farbe `ziel` hin gemischt: die gleiche Farbe als Nuance."""
    kanaele = [((farbe >> s) & 0xFF, (ziel >> s) & 0xFF) for s in (0, 8, 16)]
    return w.rgb(*[round(a + (b - a) * anteil) for a, b in kanaele])


def skaliert(wert: int, faktor: float) -> int:
    return max(1, round(wert * faktor))
