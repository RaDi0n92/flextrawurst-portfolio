# Spiegelprüfung — `kritik/test_kosmos_01.py`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/kritik/test_kosmos_01.py`
- Snapshot-SHA256: `f9db07c6656f80deff795b396e26ba1d01af353fc7c8c53bcdb5dbc98c19ff83`
- Bytes: 1231
- Zeilen: 38
- Snapshot-mtime: `2026-08-13T00:02:58.174690+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–38: `9722f2f88abadf47921340154ba2d813c1f80f24d497056d20d47f5f3bf51f8e` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Python/Playwright-Testskript. Öffnet Chromium, ruft `http://localhost:8787` auf, liest `page.content()` und sucht case-insensitiv zehn feste Keywords.
- Druckt bei Verbindung `SUCCESS`, die gefundenen Keywords und bei leerer Trefferliste `FAILED - No evidence ... on the surface`.
- Fängt alle Exceptions ab und schließt den Browser im `finally`.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Keywords: `Wupper-Ennepe`, `300`, `Lockpicking`, `Procedural`, `Schwelm`, `km²`, `LoD2`, `Dietrich`, `Stealth`, `Loot`.
- Timeout: 5000 ms.

## Provenienzklasse

Test-Harness-Code. Die Datei belegt die Prüflogik, nicht allein deren historische Ausführung.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Prüft nur HTML/DOM-Text der einen URL, nicht Canvas-Inhalte, WebGL, Netzwerk-APIs, Serverdateien oder andere Ports.
- Ein `FAILED` wird nur gedruckt; das Skript setzt keinen non-zero Exitcode für fehlende Keywords.
- Der Code allein beweist nicht, wann oder mit welchem Ergebnis er ausgeführt wurde.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
