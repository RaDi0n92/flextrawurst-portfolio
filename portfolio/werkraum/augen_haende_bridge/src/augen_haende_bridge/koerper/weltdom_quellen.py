"""Die Quellen des WorldDOM (G11): echte Struktur aus dem Browser (CDP) und aus dem Bild erschlossene Struktur (Flächen und Beschriftungen).

Echte Struktur kommt aus `uia.py` (siehe `weltdom.aus_ui_baum`) und hier aus `cdp.py`. Erschlossene Struktur ist eine Vermutung und sagt das: Konfidenz unter 1, Rolle „…_aehnlich“, Grenzen im Knoten.
Die Bildverarbeitung braucht OpenCV (Flächen) und `tesseract` (Beschriftungen); fehlt eines, entsteht nur die jeweils andere Art Knoten und der Grund steht im Ergebnis, nie ein erfundener Treffer.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .weltdom import STANDARD_TTL, Knoten, knoten_id

Rechteck = tuple[int, int, int, int]
MIN_BREITE, MIN_HOEHE = 24, 12
MAX_FLAECHEN = 80
CDP_ROLLEN = {"button": ("klick", "lesen"), "link": ("klick", "lesen"), "textbox": ("text_setzen", "lesen"), "searchbox": ("text_setzen", "lesen"), "checkbox": ("klick", "lesen"),
              "radio": ("klick", "lesen"), "combobox": ("klick", "lesen"), "menuitem": ("klick", "lesen"), "tab": ("klick", "lesen"), "heading": ("lesen",), "StaticText": ("lesen",),
              "paragraph": ("lesen",), "image": ("lesen",), "listitem": ("lesen",)}


# ---- Browser ---------------------------------------------------------------------------------------------------------------------------
def aus_cdp(ziel: str, seite, jetzt_ms: int, *, inhalt_ursprung: tuple[int, int] | None = None) -> list[Knoten]:
    """Der Baum der Bedienungshilfen einer Seite plus die Lage jedes Elements. `inhalt_ursprung` ist der Bildschirmpunkt der linken oberen Ecke der Seite (aus `window.screenX` und dem Rahmen
    abgeleitet); ohne ihn bleibt die Lage in Seitenkoordinaten und die Geometrie ist als „abgeleitet“ gekennzeichnet — die Auflösung selbst läuft über das DOM und braucht sie nicht."""
    ox, oy = inhalt_ursprung or (0, 0)
    knoten: list[Knoten] = []
    for ax in seite.ax_baum():
        if ax.rolle not in CDP_ROLLEN or (ax.rolle == "StaticText" and not ax.name.strip()):
            continue
        if ax.rolle in ("StaticText", "paragraph", "listitem") and len(ax.name) > 120:
            continue
        rect = None
        if ax.knoten_id is not None:
            try:
                box = seite.befehl("DOM.getBoxModel", backendNodeId=ax.knoten_id)["model"]["border"]
                rect = (int(min(box[0::2])) + ox, int(min(box[1::2])) + oy, int(max(box[0::2])) + ox, int(max(box[1::2])) + oy)
            except Exception:
                rect = None
        knoten.append(Knoten(knoten_id(ziel, "real", "cdp", ax.rolle, ax.name, ax.knoten_id), ziel, "real", "cdp", ax.rolle, ax.name[:200], str(ax.wert)[:300], rect, 1.0, jetzt_ms, STANDARD_TTL["real"], None,
                             CDP_ROLLEN[ax.rolle], "cdp", {"backend_id": ax.knoten_id, "rolle": ax.rolle, "name": ax.name[:200], "seite": seite.ziel.id}, "", "",
                             "gemessen" if inhalt_ursprung else "abgeleitet"))
    return knoten


def seiten_ursprung(seite) -> tuple[int, int] | None:
    """Die Bildschirmlage der Seiteninhalte: Fensterposition plus Rahmen (aus Außen- und Innenmaß abgeleitet). None, wenn die Seite es nicht hergibt."""
    try:
        sx, sy = int(seite.auswerten("window.screenX")), int(seite.auswerten("window.screenY"))
        ow, oh = int(seite.auswerten("window.outerWidth")), int(seite.auswerten("window.outerHeight"))
        iw, ih = int(seite.auswerten("window.innerWidth")), int(seite.auswerten("window.innerHeight"))
        return sx + max(0, (ow - iw) // 2), sy + max(0, oh - ih - max(0, (ow - iw) // 2))
    except Exception:
        return None


# ---- Bild -------------------------------------------------------------------------------------------------------------------------------
def flaechen_erschliessen(ziel: str, bgra: bytes, breite: int, hoehe: int, bildbereich: Rechteck, bild_seq: int | None, jetzt_ms: int) -> tuple[list[Knoten], str]:
    """Rechteckige Flächen im Bild: Schaltflächen-, Feld- und Kartenähnliches. (Knoten, Hinweis). Der Hinweis ist leer, wenn alles lief, sonst der Grund für fehlende Ergebnisse."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return [], "OpenCV fehlt: keine Flächen erschlossen"
    if breite < 40 or hoehe < 30 or len(bgra) < breite * hoehe * 4:
        return [], "Bild zu klein oder unvollständig"
    bild = np.frombuffer(bgra, dtype=np.uint8, count=breite * hoehe * 4).reshape(hoehe, breite, 4)[..., :3]
    grau = cv2.cvtColor(np.ascontiguousarray(bild), cv2.COLOR_BGR2GRAY)
    kanten = cv2.Canny(cv2.GaussianBlur(grau, (3, 3), 0), 40, 120)
    kanten = cv2.dilate(kanten, np.ones((3, 3), np.uint8))
    konturen, _ = cv2.findContours(kanten, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    bx, by = bildbereich[0], bildbereich[1]
    sx, sy = (bildbereich[2] - bildbereich[0]) / breite, (bildbereich[3] - bildbereich[1]) / hoehe
    kandidaten = []
    for c in konturen:
        x, y, b, h = cv2.boundingRect(c)
        if b < MIN_BREITE or h < MIN_HOEHE or b * h > 0.9 * breite * hoehe:
            continue
        flaeche = cv2.contourArea(c)
        fuell = flaeche / float(b * h) if b * h else 0.0
        peri = cv2.arcLength(c, True)
        ecken = len(cv2.approxPolyDP(c, 0.03 * peri, True)) if peri else 0
        if ecken < 4 or ecken > 8 or fuell < 0.55:
            continue
        kandidaten.append((x, y, b, h, fuell))
    # Doppelte (innere und äußere Kante derselben Fläche) zusammenfassen
    kandidaten.sort(key=lambda k: -k[2] * k[3])
    behalten: list[tuple[int, int, int, int, float]] = []
    for k in kandidaten:
        if any(abs(k[0] - o[0]) < 6 and abs(k[1] - o[1]) < 6 and abs(k[2] - o[2]) < 10 and abs(k[3] - o[3]) < 10 for o in behalten):
            continue
        behalten.append(k)
        if len(behalten) >= MAX_FLAECHEN:
            break
    knoten = []
    for x, y, b, h, fuell in behalten:
        ausschnitt = grau[y:y + h, x:x + b]
        streuung = float(ausschnitt.std())
        if b >= 4 * h and streuung < 25 and float(ausschnitt.mean()) > 150:
            rolle = "feld_aehnlich"  # breit, hell und ruhig: ein Eingabefeld
        elif h <= 80 and b <= 400 and streuung < 60:
            rolle = "schaltflaeche_aehnlich"
        else:
            rolle = "flaeche"
        conf = round(min(0.8, 0.3 + 0.5 * fuell), 3)
        rect = (int(bx + x * sx), int(by + y * sy), int(bx + (x + b) * sx), int(by + (y + h) * sy))
        knoten.append(Knoten(knoten_id(ziel, "inferred", "flaeche", rolle, x // 4, y // 4, b // 4, h // 4), ziel, "inferred", "flaeche", rolle, "", "", rect, conf, jetzt_ms, STANDARD_TTL["inferred"], bild_seq,
                             ("zeigen", "klick_koordinate"), "koordinate", {"bild": [x, y, b, h]}, "", "aus dem Bild vermutet: Rolle und Grenzen sind geschätzt, es gibt keine Anwendungsstruktur dahinter"))
    return knoten, ""




def beschriftungen_erschliessen(ziel: str, bgra: bytes, breite: int, hoehe: int, bildbereich: Rechteck, bild_seq: int | None, jetzt_ms: int, *, sprache: str = "eng", timeout_s: float = 30.0,
                                tesseract: str | None = None) -> tuple[list[Knoten], str]:
    """Textstellen im Bild per OCR (tesseract). Konfidenz aus der Erkennungssicherheit, gedeckelt auf 0,9."""
    exe = tesseract or shutil.which("tesseract")
    if exe is None:
        return [], "tesseract fehlt: keine Beschriftungen erschlossen"
    try:
        from PIL import Image
    except ImportError:
        return [], "Pillow fehlt"
    if breite < 20 or hoehe < 10 or len(bgra) < breite * hoehe * 4:
        return [], "Bild zu klein oder unvollständig"
    from PIL import ImageOps

    bild = Image.frombuffer("RGBA", (breite, hoehe), bgra, "raw", "BGRA", 0, 1).convert("RGB")
    skala = 2 if max(breite, hoehe) < 1400 else 1
    if skala != 1:
        bild = bild.resize((breite * skala, hoehe * skala))
    ausgaben = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, b in (("normal", bild), ("invertiert", ImageOps.invert(bild))):  # helle Schrift auf dunklem Grund liest tesseract nur invertiert
            pfad = Path(tmp) / f"{name}.png"
            b.save(pfad)
            try:
                lauf = subprocess.run([exe, str(pfad), "stdout", "-l", sprache, "--psm", "11", "tsv"], capture_output=True, text=True, timeout=timeout_s)
            except (subprocess.SubprocessError, OSError) as fehler:
                return [], f"tesseract nicht ausgeführt: {fehler.__class__.__name__}"
            if lauf.returncode != 0:
                return [], "tesseract meldet einen Fehler"
            ausgaben.append(lauf.stdout)
    zeilen: dict[tuple, list] = {}
    for nr, ausgabe in enumerate(ausgaben):
        for z in ausgabe.splitlines()[1:]:
            t = z.split("\t")
            if len(t) < 12 or not t[11].strip():
                continue
            try:
                conf = float(t[10])
            except ValueError:
                continue
            if conf < 40:
                continue
            zeilen.setdefault((nr, t[2], t[3], t[4]), []).append((int(t[6]), int(t[7]), int(t[8]), int(t[9]), t[11].strip(), conf))
    bx, by = bildbereich[0], bildbereich[1]
    sx, sy = (bildbereich[2] - bildbereich[0]) / breite, (bildbereich[3] - bildbereich[1]) / hoehe
    knoten = []
    gesehen: list[tuple[int, int, int, int]] = []
    for woerter in sorted(zeilen.values(), key=lambda ws: -sum(w[5] for w in ws) / len(ws)):
        text = " ".join(w[4] for w in woerter)[:200]
        kasten = (min(w[0] for w in woerter), min(w[1] for w in woerter), max(w[0] + w[2] for w in woerter), max(w[1] + w[3] for w in woerter))
        if any(min(kasten[2], g[2]) - max(kasten[0], g[0]) > 0.5 * (kasten[2] - kasten[0]) and min(kasten[3], g[3]) - max(kasten[1], g[1]) > 0.5 * (kasten[3] - kasten[1]) for g in gesehen):
            continue  # dieselbe Textstelle, vom anderen Durchgang schon besser gelesen
        gesehen.append(kasten)
        x0, y0 = min(w[0] for w in woerter) // skala, min(w[1] for w in woerter) // skala
        x1, y1 = max(w[0] + w[2] for w in woerter) // skala, max(w[1] + w[3] for w in woerter) // skala
        conf = round(min(0.9, sum(w[5] for w in woerter) / len(woerter) / 100.0), 3)
        rect = (int(bx + x0 * sx), int(by + y0 * sy), int(bx + x1 * sx), int(by + y1 * sy))
        knoten.append(Knoten(knoten_id(ziel, "inferred", "ocr", text, x0 // 4, y0 // 4), ziel, "inferred", "ocr", "text_ocr", text, text, rect, conf, jetzt_ms, STANDARD_TTL["inferred"], bild_seq,
                             ("zeigen", "lesen", "klick_koordinate"), "koordinate", {"bild": [x0, y0, x1 - x0, y1 - y0]}, "", "Text aus dem Bild gelesen: kann Lesefehler enthalten, kein Programmelement"))
    return knoten, ""


def flaechen_benennen(flaechen: list[Knoten], bgra: bytes, breite: int, hoehe: int, *, sprache: str = "eng", timeout_s: float = 15.0, tesseract: str | None = None) -> str:
    """Liest den Text in jeder erschlossenen Fläche einzeln (Ausschnitt, Graustufen, hell auf dunkel invertiert, vergrößert). Das findet Beschriftungen, die die Seitenerkennung über das ganze Bild
    übersieht. Gibt einen Hinweis zurück, wenn etwas fehlt; benannte Flächen behalten ihre niedrigere Konfidenz."""
    exe = tesseract or shutil.which("tesseract")
    if exe is None:
        return "tesseract fehlt: keine Flächen benannt"
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return "Pillow fehlt"
    ganz = Image.frombuffer("RGBA", (breite, hoehe), bgra, "raw", "BGRA", 0, 1).convert("RGB")
    with tempfile.TemporaryDirectory() as tmp:
        for f in flaechen:
            x, y, b, h = f.anker.get("bild", (0, 0, 0, 0))
            if f.name or b < 20 or h < 10 or f.rolle == "feld_aehnlich":
                continue
            aus = ImageOps.grayscale(ganz.crop((x, y, x + b, y + h)))
            if aus.getextrema()[1] - aus.getextrema()[0] < 40:
                continue
            for bild in (ImageOps.invert(aus), aus):
                pfad = Path(tmp) / "f.png"
                ImageOps.autocontrast(bild).resize((b * 3, h * 3)).save(pfad)
                try:
                    lauf = subprocess.run([exe, str(pfad), "stdout", "-l", sprache, "--psm", "7", "tsv"], capture_output=True, text=True, timeout=timeout_s)
                except (subprocess.SubprocessError, OSError):
                    return "tesseract nicht ausgeführt"
                woerter = [z.split("\t") for z in lauf.stdout.splitlines()[1:]]
                gut = [(t[11].strip(), float(t[10])) for t in woerter if len(t) >= 12 and t[11].strip() and float(t[10]) >= 50]
                if gut:
                    f.name = " ".join(w for w, _ in gut)[:200]
                    f.confidence = round(min(f.confidence, 0.9, sum(c for _, c in gut) / len(gut) / 100.0), 3)
                    break
    return ""


def benennen(flaechen: list[Knoten], texte: list[Knoten]) -> list[Knoten]:
    """Eine Fläche, in der genau eine Textstelle liegt, bekommt deren Text als Namen (die Konfidenz bleibt die niedrigere der beiden)."""
    ergebnis = []
    for f in flaechen:
        drin = [t for t in texte if f.rect and t.rect and t.rect[0] >= f.rect[0] - 2 and t.rect[2] <= f.rect[2] + 2 and t.rect[1] >= f.rect[1] - 2 and t.rect[3] <= f.rect[3] + 2]
        if len(drin) == 1:
            f.name = drin[0].name
            f.confidence = round(min(f.confidence, drin[0].confidence), 3)
        ergebnis.append(f)
    return ergebnis
