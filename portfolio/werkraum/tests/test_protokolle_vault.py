#!/usr/bin/env python3
"""Playwright-Test fuer den Protokolle-Vault -- 2026-08-04.

Prueft das, was am 03./04.08. gebaut wurde, im echten Browser statt per curl:
  - Zugang ist geschuetzt (ohne Kennung kein Zugriff)
  - mit Kennung laedt die Obsidian-Oberflaeche wirklich (nicht nur HTTP 200)
  - dasselbe ueber den eigenen Port 8457
  - die geschriebenen Protokolldateien liegen im Vault und sind lesbar

Aufruf: python3 /root/werkraum/tests/test_protokolle_vault.py
Schreibt Belegbilder nach /root/werkraum/tests/belege/.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ADRESSE_DOMAIN = "https://flextrawurst.de/protokolle/"
ADRESSE_PORT = "https://[SERVER-IP]:8457/"
KENNUNG = {"username": "daniel", "password": "[GESCHWAERZT]"}
VAULT = Path("/root/werkraum/protokolle")
BELEGE = Path("/root/werkraum/tests/belege")

ergebnisse = []


def pruefe(name: str, bedingung: bool, hinweis: str = ""):
    ergebnisse.append((name, bedingung, hinweis))
    print(f"  {'OK  ' if bedingung else 'FEHL'}  {name}{'  -- ' + hinweis if hinweis else ''}",
          flush=True)


def main() -> int:
    BELEGE.mkdir(parents=True, exist_ok=True)
    print("Protokolle-Vault, Browsertest\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])

        # 1. ohne Kennung -- der Vault darf nicht offen stehen
        seite = browser.new_context(ignore_https_errors=True).new_page()
        antwort = seite.goto(ADRESSE_DOMAIN, wait_until="domcontentloaded")
        pruefe("ohne Kennung abgewiesen", antwort.status == 401, f"Status {antwort.status}")
        seite.close()

        # 2. mit Kennung ueber die Domain
        ktx = browser.new_context(http_credentials=KENNUNG, ignore_https_errors=True,
                                  viewport={"width": 1400, "height": 900})
        seite = ktx.new_page()
        antwort = seite.goto(ADRESSE_DOMAIN, wait_until="domcontentloaded", timeout=60000)
        pruefe("mit Kennung eingelassen", antwort.status == 200, f"Status {antwort.status}")

        # Die Oberflaeche kommt ueber eine Leinwand/Weboberflaeche -- warten, bis wirklich
        # etwas gezeichnet ist, statt nur auf den HTTP-Code zu vertrauen.
        seite.wait_for_timeout(12000)
        seite.screenshot(path=str(BELEGE / "protokolle_domain.png"), full_page=False)
        inhalt = seite.content()
        pruefe("Oberflaeche geladen (Leinwand/Selkies vorhanden)",
               ("canvas" in inhalt.lower() or "selkies" in inhalt.lower()
                or "video" in inhalt.lower()),
               f"{len(inhalt)} Zeichen HTML")

        # 2026-08-04: Der HTTP-Code hat hier zuerst getrogen -- Obsidian lief, zeigte aber
        # den Startbildschirm ("Create new vault"), weil der Vault im Container nie
        # registriert war. Erst das Belegbild hat es gezeigt.
        #
        # Der erste Versuch, das zu pruefen, ging ueber die Helligkeit und war falsch: er
        # nahm an, die geoeffnete Oberflaeche sei dunkel. Sie laeuft im hellen Design, der
        # Test schlug bei einem gesunden Zustand fehl. Was tatsaechlich unterscheidet:
        # der Startbildschirm ist ein kleines Fenster auf schwarzem Grund, die geoeffnete
        # Oberflaeche fuellt den Bildschirm bis in die Ecken.
        from PIL import Image
        bild = Image.open(BELEGE / "protokolle_domain.png").convert("L")
        ecken = [bild.getpixel(xy) for xy in
                 ((5, bild.height - 5), (bild.width - 5, bild.height - 5), (5, 60))]
        pruefe("Fenster fuellt den Bildschirm (kein Startbildschirm)",
               all(w > 40 for w in ecken), f"Ecken {ecken}")

        import json as _json, subprocess
        roh = subprocess.run(["docker", "exec", "obsidian-protokolle", "cat",
                              "/config/.config/obsidian/obsidian.json"],
                             capture_output=True, text=True).stdout or "{}"
        vaults = _json.loads(roh).get("vaults", {})
        pruefe("Vault im Container registriert und offen",
               any(v.get("path") == "/vault" and v.get("open") for v in vaults.values()),
               str(list(vaults.values()))[:80])
        pruefe("kein Serverfehler im Text",
               "502 Bad Gateway" not in inhalt and "504 Gateway" not in inhalt)
        seite.close()

        # 3. derselbe Vault ueber den eigenen Port
        seite = ktx.new_page()
        antwort = seite.goto(ADRESSE_PORT, wait_until="domcontentloaded", timeout=60000)
        pruefe("eigener Port 8457 erreichbar", antwort.status == 200, f"Status {antwort.status}")
        seite.wait_for_timeout(8000)
        seite.screenshot(path=str(BELEGE / "protokolle_port8457.png"))
        seite.close()

        browser.close()

    # 4. der Inhalt, der dort zu sehen sein soll
    dateien = sorted(VAULT.rglob("*.md"))
    pruefe("Protokolldateien im Vault", len(dateien) > 0, f"{len(dateien)} Dateien")

    if dateien:
        text = dateien[-1].read_text(encoding="utf-8")
        pruefe("Frontmatter vorhanden", text.startswith("---\ndatum:"))
        pruefe("deutsches Datumsformat im Namen",
               len(dateien[-1].stem.split("_")[0].split("-")[-1]) == 4,
               dateien[-1].name)
        pruefe("Ereignisse mit Uhrzeit", "## " in text and ":" in text)

    fehler = [n for n, ok, _ in ergebnisse if not ok]
    print(f"\n{len(ergebnisse) - len(fehler)}/{len(ergebnisse)} bestanden")
    if fehler:
        print("nicht bestanden: " + ", ".join(fehler))
    print(f"Belegbilder: {BELEGE}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
