"""Set-of-Mark für den WorldDOM: ein Bild des Ziels, in dem jeder bedienbare Knoten einen Rahmen und eine Nummer trägt — und die Tabelle Nummer → Knoten-Kennung.

Das Modell muss dann nicht Pixel raten („klick bei 412, 98“), sondern sagt „Nummer 7“; gehandelt wird über die Kennung (`knoten ID klick`), die auch bei verschobenem Fenster gilt. Quelle sind nur die **gemessenen** Knoten (echt und erschlossen), nie Projiziertes; jeder Eintrag nennt Herkunft und Alter.
Die Rahmenfarbe trägt die Herkunft (echt blau, erschlossen orange, eigene Anker grün). Zu viele Knoten werden begrenzt (`MAX_MARKEN`); was weggelassen wurde, steht in `weggelassen`.
"""

from __future__ import annotations

MAX_MARKEN = 60
FARBEN = {"real": (0, 120, 255), "inferred": (255, 150, 0), "authored": (0, 170, 80)}
BEDIENBAR = ("klick", "text_setzen", "zeigen", "klick_koordinate")


def _bedienbar(k: dict) -> bool:
    return bool(k.get("rect")) and any(f in BEDIENBAR for f in k.get("faehigkeiten", ())) and k.get("herkunft") in FARBEN and not k.get("veraltet")


def auswaehlen(knoten: list[dict]) -> tuple[list[dict], int]:
    """Die zu markierenden Knoten (bedienbar, mit Ort, nicht veraltet): echte vor erschlossenen, kleine vor großen (große Flächen verdecken sonst alles); höchstens `MAX_MARKEN`."""
    kandidaten = [k for k in knoten if _bedienbar(k)]
    rang = {"real": 0, "authored": 1, "inferred": 2}
    kandidaten.sort(key=lambda k: (rang[k["herkunft"]], (k["rect"][2] - k["rect"][0]) * (k["rect"][3] - k["rect"][1])))
    return kandidaten[:MAX_MARKEN], max(0, len(kandidaten) - MAX_MARKEN)


def markieren(bgra: bytes, breite: int, hoehe: int, bereich: tuple[int, int, int, int], knoten: list[dict]) -> dict:
    """{"jpeg", "breite", "hoehe", "tabelle", "weggelassen"} — `bereich` ist das Bildschirmrechteck, das das Bild zeigt."""
    from PIL import Image, ImageDraw

    from . import bild as bildmodul

    gewaehlt, weggelassen = auswaehlen(knoten)
    bw, bh = max(1, bereich[2] - bereich[0]), max(1, bereich[3] - bereich[1])
    fx, fy = breite / bw, hoehe / bh
    bild = Image.frombuffer("RGBA", (breite, hoehe), bgra, "raw", "BGRA", 0, 1).convert("RGB")
    zeichner = ImageDraw.Draw(bild)
    tabelle = []
    for nr, k in enumerate(gewaehlt, 1):
        l, o, r, u = k["rect"]
        box = (round((l - bereich[0]) * fx), round((o - bereich[1]) * fy), round((r - bereich[0]) * fx), round((u - bereich[1]) * fy))
        box = (max(0, box[0]), max(0, box[1]), min(breite - 1, box[2]), min(hoehe - 1, box[3]))
        if box[2] <= box[0] or box[3] <= box[1]:
            weggelassen += 1  # liegt außerhalb dessen, was das Bild zeigt
            continue
        farbe = FARBEN[k["herkunft"]]
        zeichner.rectangle(box, outline=farbe, width=2)
        text = str(len(tabelle) + 1)
        tw = 8 * len(text) + 6
        zeichner.rectangle((box[0], box[1], box[0] + tw, box[1] + 14), fill=farbe)
        zeichner.text((box[0] + 3, box[1] + 1), text, fill=(255, 255, 255))
        tabelle.append({"nr": len(tabelle) + 1, "knoten": k["id"], "rolle": k.get("rolle", ""), "name": (k.get("name") or "")[:60], "herkunft": k["herkunft"], "alter_ms": k.get("alter_ms"),
                        "faehigkeiten": list(k.get("faehigkeiten", ()))})
    ziel = bildmodul.skaliert_auf(*bild.size)
    if ziel != bild.size:
        bild = bild.resize(ziel, Image.LANCZOS)
    import io

    qualitaet = bildmodul.QUALITAET
    while True:
        puffer = io.BytesIO()
        bild.save(puffer, format="JPEG", quality=qualitaet)
        daten = puffer.getvalue()
        if len(daten) <= bildmodul.MAX_JPEG_BYTES or qualitaet <= 30:
            break
        qualitaet -= 15
    return {"jpeg": daten, "breite": bild.size[0], "hoehe": bild.size[1], "tabelle": tabelle, "weggelassen": weggelassen}
