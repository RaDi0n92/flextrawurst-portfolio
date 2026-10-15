"""Zeichnet Objekte (siehe `objekte.py`) in ein RGBA-Bild: ein einziger Zeichner für alles, was jemand sieht — die Komposition in den Bildern der Agenten,
die Anzeige auf Daniels Bildschirm und die Vorschau im Editor. So sieht jeder dasselbe Objekt.

Plattformneutral (Pillow). Koordinaten der Objekte sind relativ zum Gate und werden auf die Bildgröße umgerechnet.
"""

from __future__ import annotations

import io
import math

from PIL import Image, ImageDraw, ImageFont

from .objekte import Objekt

SCHRIFTEN = {
    (False, False): ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"),
    (True, False): ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"),
    (False, True): ("segoeuii.ttf", "ariali.ttf", "DejaVuSans-Oblique.ttf", "LiberationSans-Italic.ttf"),
    (True, True): ("segoeuiz.ttf", "arialbi.ttf", "DejaVuSans-BoldOblique.ttf", "LiberationSans-BoldItalic.ttf"),
}
ZEILEN_ABSTAND = 4
_schrift_cache: dict[tuple, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def schrift(groesse: int, fett: bool = False, kursiv: bool = False):
    schluessel = (groesse, fett, kursiv)
    if schluessel not in _schrift_cache:
        gefunden = None
        for name in SCHRIFTEN[(fett, kursiv)] + (SCHRIFTEN[(False, False)] if (fett or kursiv) else ()):
            try:
                gefunden = ImageFont.truetype(name, groesse)
                break
            except OSError:
                continue
        _schrift_cache[schluessel] = gefunden if gefunden is not None else ImageFont.load_default(size=groesse)
    return _schrift_cache[schluessel]


def _zeilenhoehe(font) -> int:
    try:
        a, d = font.getmetrics()
        return a + d + ZEILEN_ABSTAND
    except AttributeError:
        return font.size + ZEILEN_ABSTAND


def _zeilen_breite(font, zeile: str) -> float:
    try:
        return font.getlength(zeile)
    except AttributeError:
        return len(zeile) * font.size * 0.6


def text_masse_px(text: str, groesse: int, fett: bool = False, kursiv: bool = False) -> tuple[float, float]:
    """Breite und Höhe eines (mehrzeiligen) Textes in Pixeln: derselbe Zeilenaufbau wie beim Zeichnen."""
    font = schrift(groesse, fett, kursiv)
    zeilen = (text or " ").split("\n")
    return max(_zeilen_breite(font, z) for z in zeilen), len(zeilen) * _zeilenhoehe(font) - ZEILEN_ABSTAND


def hex_zu_rgba(farbe: str, alpha: int = 255) -> tuple[int, int, int, int]:
    try:
        return int(farbe[1:3], 16), int(farbe[3:5], 16), int(farbe[5:7], 16), alpha
    except (ValueError, IndexError):
        return 255, 0, 85, alpha


def _px(o: Objekt, breite: int, hoehe: int) -> list[tuple[float, float]]:
    return [(x * breite, y * hoehe) for x, y in o.punkte]


def _linie(zeichner: ImageDraw.ImageDraw, pts, farbe, breite: int) -> None:
    if len(pts) == 1:
        x, y = pts[0]
        r = breite / 2
        zeichner.ellipse((x - r, y - r, x + r, y + r), fill=farbe)
        return
    zeichner.line(pts, fill=farbe, width=breite, joint="curve")
    r = breite / 2
    for x, y in (pts[0], pts[-1]):  # runde Enden
        zeichner.ellipse((x - r, y - r, x + r, y + r), fill=farbe)


def _pfeilspitze(zeichner, a, b, farbe, staerke: int) -> None:
    laenge = max(12.0, staerke * 4.0)
    winkel = math.atan2(b[1] - a[1], b[0] - a[0])
    links = (b[0] - laenge * math.cos(winkel - math.pi / 7), b[1] - laenge * math.sin(winkel - math.pi / 7))
    rechts = (b[0] - laenge * math.cos(winkel + math.pi / 7), b[1] - laenge * math.sin(winkel + math.pi / 7))
    zeichner.polygon([b, links, rechts], fill=farbe)


def zeichne_objekt(bild: Image.Image, o: Objekt, breite: int, hoehe: int) -> None:
    """Ein Objekt auf das RGBA-Bild (mit Alpha-Mischung)."""
    ebene = Image.new("RGBA", bild.size, (0, 0, 0, 0))
    z = ImageDraw.Draw(ebene)
    faktor_marker = 1.0
    farbe = hex_zu_rgba(o.farbe, 255)
    pts = _px(o, breite, hoehe)
    if not pts:
        return
    if o.art == "freihand":
        _linie(z, pts, farbe, o.staerke)
    elif o.art == "marker":
        _linie(z, pts, hex_zu_rgba(o.farbe, 255), max(8, o.staerke * 4))
        faktor_marker = 0.4  # halbdurchsichtig wie ein Textmarker
    elif o.art in ("linie", "pfeil") and len(pts) >= 2:
        a, b = pts[0], pts[-1]
        _linie(z, [a, b], farbe, o.staerke)
        if o.art == "pfeil":
            _pfeilspitze(z, a, b, farbe, o.staerke)
    elif o.art in ("rechteck", "kreis") and len(pts) >= 2:
        l, t = min(pts[0][0], pts[-1][0]), min(pts[0][1], pts[-1][1])
        r, u = max(pts[0][0], pts[-1][0]), max(pts[0][1], pts[-1][1])
        if o.art == "rechteck":
            z.rectangle((l, t, r, u), outline=farbe, width=o.staerke)
        else:
            z.ellipse((l, t, r, u), outline=farbe, width=o.staerke)
    elif o.art == "text":
        x, y = pts[0]
        font = schrift(o.schriftgroesse, o.fett, o.kursiv)
        schritt = _zeilenhoehe(font)
        for nr, zeile in enumerate((o.text or " ").split("\n")):
            z.text((x, y + nr * schritt), zeile, fill=farbe, font=font)
            if o.unterstrichen and zeile.strip():
                try:
                    ascent = font.getmetrics()[0]
                except AttributeError:
                    ascent = font.size
                unten = y + nr * schritt + ascent + max(1, o.schriftgroesse // 14) + 1
                z.line((x, unten, x + _zeilen_breite(font, zeile), unten), fill=farbe, width=max(1, o.schriftgroesse // 14))
    elif o.art == "bild" and o.bild and len(pts) >= 2:
        try:
            with Image.open(io.BytesIO(o.bild)) as roh:
                roh = roh.convert("RGBA")
            l, t = int(min(pts[0][0], pts[-1][0])), int(min(pts[0][1], pts[-1][1]))
            b_, h_ = max(1, int(abs(pts[-1][0] - pts[0][0]))), max(1, int(abs(pts[-1][1] - pts[0][1])))
            ebene.paste(roh.resize((b_, h_), Image.LANCZOS), (l, t))
        except Exception:
            return  # ein kaputtes Bild darf den Rest nicht verhindern
    faktor = faktor_marker * max(5, min(100, o.deckkraft)) / 100
    if faktor < 0.999:
        ebene.putalpha(ebene.getchannel("A").point(lambda a: int(a * faktor)))
    bild.alpha_composite(ebene)


def rendern(objekte: list[Objekt], breite: int, hoehe: int, hintergrund=(0, 0, 0, 0)) -> Image.Image:
    """Alle Objekte (in der übergebenen Reihenfolge, unten zuerst) auf ein RGBA-Bild dieser Größe."""
    bild = Image.new("RGBA", (max(1, breite), max(1, hoehe)), hintergrund)
    for o in objekte:
        zeichne_objekt(bild, o, breite, hoehe)
    return bild


def text_grenzen(text: str, groesse: int, breite: int, hoehe: int, fett: bool = False, kursiv: bool = False) -> tuple[float, float]:
    """Breite und Höhe eines Textes in Gate-Koordinaten (für den Rahmen und das Treffen)."""
    b, h = text_masse_px(text, groesse, fett, kursiv)
    return b / max(1, breite), h / max(1, hoehe)
