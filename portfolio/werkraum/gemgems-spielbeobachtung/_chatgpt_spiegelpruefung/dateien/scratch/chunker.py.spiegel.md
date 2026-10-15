# Spiegelprüfung — `scratch/chunker.py`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/scratch/chunker.py`
- Snapshot-SHA256: `767773dd2c6a92d550f3653e5bb8a624f92e1e78698442d443bd9efc40b51af9`
- Bytes: 1428
- Zeilen: 41
- Snapshot-mtime: `2026-08-13T00:51:41.714615+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–41: `6e81b0e448d8cfeb3f8ac1a2a7e65f23e094e8bb9ef53765e52fe82683f9d4fa` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Hilfsskript, das `/root/werkraum/flarum_vollexport.html` vollständig als Zeilen einliest.
- Teilt den Export in 400-Zeilen-Chunks unter `scratch/flarum_chunks/`.
- Erzeugt `flarum_ledger.md` mit einer Checkbox und Original-Zeilenbereich für jeden Chunk.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- `chunk_size_lines = 400`.
- Chunknamen: `chunk_0001.html`, ...
- Anzahl wird als `ceil(total_lines / 400)` berechnet.

## Provenienzklasse

Technisches Hilfsskript der Gemini-Ausgrabung.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

Das Skript erzeugt Chunks und ein Ledger. Es beweist nicht, dass die Chunks anschließend semantisch gelesen wurden.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
