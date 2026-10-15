#!/usr/bin/env python3
"""Prueft im Browser, dass alle Obsidian-Vaults dunkel laufen -- 2026-08-04.

Daniel: "bitte mach es dunkel und auh für alle obsidians die ih mitlerweile hb egalobb auf
den ports oder flextrawur.de/xxx"

Nicht nur die Einstellungsdatei wird geprueft, sondern das gezeichnete Bild -- beim
Protokolle-Vault hat sich gezeigt, dass eine erreichbare Seite noch lange nicht die richtige
Seite ist. Gemessen wird die Helligkeit der Flaeche: dunkel liegt weit unter 100, das helle
Design lag bei 246.

Aufruf: python3 /root/werkraum/tests/test_obsidian_dunkel.py
"""

import re
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

KENNUNG_ALLGEMEIN = {"username": "daniel", "password": "[GESCHWAERZT]"}
BELEGE = Path("/root/werkraum/tests/belege/dunkel")
HELL_GRENZE = 100     # darueber ist es das helle Design

ergebnisse = []


def adressen() -> list:
    """Aus nginx lesen, welcher Port zu welchem Container gehoert -- nicht raten.

    Der erste Versuch war zu grob und fand nur zwei von zwoelf. Jetzt: jede Datei unter
    sites-enabled, erster listen-Port, erster proxy_pass auf 127.0.0.1:3xxx. Port 443/80
    faellt weg (das ist die Domain, dort zaehlen die Pfade darunter).
    """
    gefunden = []
    for datei in sorted(Path("/etc/nginx/sites-enabled").iterdir()):
        try:
            text = datei.read_text(errors="replace")
        except Exception:
            continue
        port = next((m.group(1) for m in
                     re.finditer(r"^\s*listen\s+(\d+)", text, re.M)), None)
        ziel = next((m.group(1) for m in
                     re.finditer(r"127\.0\.0\.1:(3\d{3})", text)), None)
        if port and ziel and port not in ("80", "443"):
            gefunden.append((datei.name, f"https://[SERVER-IP]:{port}/"))
    gefunden.append(("flextrawurst.de/protokolle", "https://flextrawurst.de/protokolle/"))
    gefunden.append(("flextrawurst.de/inboxvault", "https://flextrawurst.de/inboxvault/"))
    return sorted(set(gefunden))


def main() -> int:
    BELEGE.mkdir(parents=True, exist_ok=True)
    ziele = adressen()
    print(f"Dunkles Design, {len(ziele)} Adressen\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        ktx = browser.new_context(http_credentials=KENNUNG_ALLGEMEIN, ignore_https_errors=True,
                                  viewport={"width": 1200, "height": 800})
        for name, adresse in ziele:
            seite = ktx.new_page()
            try:
                antwort = seite.goto(adresse, wait_until="domcontentloaded", timeout=45000)
                if antwort.status != 200:
                    ergebnisse.append((name, False))
                    print(f"  FEHL  {name:34s} Status {antwort.status}")
                    seite.close()
                    continue
                seite.wait_for_timeout(11000)
                bild_pfad = BELEGE / f"{name.replace('/', '_')}.png"
                seite.screenshot(path=str(bild_pfad))
                grau = Image.open(bild_pfad).convert("L")
                hell = sum(grau.getdata()) / (grau.width * grau.height)
                ok = hell < HELL_GRENZE
                ergebnisse.append((name, ok))
                print(f"  {'OK  ' if ok else 'FEHL'}  {name:34s} Helligkeit {hell:5.0f}")
            except Exception as exc:
                ergebnisse.append((name, False))
                print(f"  FEHL  {name:34s} {str(exc)[:60]}")
            finally:
                seite.close()
        browser.close()

    fehler = [n for n, ok in ergebnisse if not ok]
    print(f"\n{len(ergebnisse) - len(fehler)}/{len(ergebnisse)} dunkel")
    if fehler:
        print("nicht dunkel: " + ", ".join(fehler))
    print(f"Belegbilder: {BELEGE}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
