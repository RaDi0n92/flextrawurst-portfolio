"""Bilder für den Agenten: den gebundenen Ausschnitt aus einem echten Frame schneiden und als JPEG kodieren.

R120: gesehen und gesendet wird erst, wenn im Fensterscanner etwas gebunden ist — dieses Modul bekommt deshalb
immer einen Frame plus das gebundene Rechteck. Größenlimit nach dem Bridge-Skill (Tor R6): höchstens 1920×1080,
JPEG-Qualität 80, und unter der Frame-Grenze des Relays (`transport.py`: 1 400 000 Zeichen Base64).
Pillow wird erst beim Kodieren importiert.
"""

from __future__ import annotations

import io

MAX_BREITE, MAX_HOEHE = 1920, 1080
QUALITAET = 80
MAX_JPEG_BYTES = 1_000_000  # Base64 macht daraus etwa 1,33 MB, unter der Relay-Grenze

Rechteck = tuple[int, int, int, int]


def ausschnitt_im_frame(ziel: Rechteck, ursprung: tuple[int, int], breite: int, hoehe: int) -> Rechteck | None:
    """Ziel (Bildschirmkoordinaten) in Framekoordinaten, auf den Frame geklemmt; None, wenn nichts übrig bleibt."""
    links = max(0, ziel[0] - ursprung[0])
    oben = max(0, ziel[1] - ursprung[1])
    rechts = min(breite, ziel[2] - ursprung[0])
    unten = min(hoehe, ziel[3] - ursprung[1])
    if rechts <= links or unten <= oben:
        return None
    return links, oben, rechts, unten


def skaliert_auf(breite: int, hoehe: int) -> tuple[int, int]:
    faktor = min(1.0, MAX_BREITE / breite, MAX_HOEHE / hoehe)
    return max(1, round(breite * faktor)), max(1, round(hoehe * faktor))


def bgra_zu_jpeg(bgra: bytes, breite: int, hoehe: int, ausschnitt: Rechteck, nachbearbeiten=None) -> tuple[bytes, int, int]:
    """(JPEG-Bytes, Breite, Höhe) des Ausschnitts. `nachbearbeiten` bekommt den RGB-Ausschnitt und liefert das fertige Bild (z. B. mit den
    Objekten, die nur dieser Empfänger sehen soll)."""
    from PIL import Image

    bild = Image.frombuffer("RGBA", (breite, hoehe), bgra, "raw", "BGRA", 0, 1).crop(ausschnitt).convert("RGB")
    if nachbearbeiten is not None:
        bild = nachbearbeiten(bild)
    ziel = skaliert_auf(*bild.size)
    if ziel != bild.size:
        bild = bild.resize(ziel, Image.LANCZOS)
    qualitaet = QUALITAET
    while True:
        puffer = io.BytesIO()
        bild.save(puffer, format="JPEG", quality=qualitaet)
        daten = puffer.getvalue()
        if len(daten) <= MAX_JPEG_BYTES or qualitaet <= 30:
            return daten, bild.size[0], bild.size[1]
        qualitaet -= 15


def datei_zu_jpeg(pfad: str) -> tuple[bytes, int, int]:
    """Eine Bilddatei als JPEG für den Agenten, auf höchstens 1920×1080 und unter die Frame-Grenze gebracht (Quelle „file“)."""
    from PIL import Image

    with Image.open(pfad) as roh:
        bild_ = roh.convert("RGB")
    ziel = skaliert_auf(*bild_.size)
    if ziel != bild_.size:
        bild_ = bild_.resize(ziel, Image.LANCZOS)
    qualitaet = QUALITAET
    while True:
        puffer = io.BytesIO()
        bild_.save(puffer, format="JPEG", quality=qualitaet)
        daten = puffer.getvalue()
        if len(daten) <= MAX_JPEG_BYTES or qualitaet <= 30:
            return daten, bild_.size[0], bild_.size[1]
        qualitaet -= 15


def bgr_zu_jpeg(bgr: bytes, breite: int, hoehe: int) -> tuple[bytes, int, int]:
    """Ein Kameraframe (BGR, wie `cv2` ihn liefert) als JPEG, auf höchstens 1920×1080 begrenzt."""
    from PIL import Image

    bild_ = Image.frombuffer("RGB", (breite, hoehe), bgr, "raw", "BGR", 0, 1)
    ziel = skaliert_auf(breite, hoehe)
    if ziel != (breite, hoehe):
        bild_ = bild_.resize(ziel, Image.LANCZOS)
    qualitaet = QUALITAET
    while True:
        puffer = io.BytesIO()
        bild_.save(puffer, format="JPEG", quality=qualitaet)
        daten = puffer.getvalue()
        if len(daten) <= MAX_JPEG_BYTES or qualitaet <= 30:
            return daten, bild_.size[0], bild_.size[1]
        qualitaet -= 15
