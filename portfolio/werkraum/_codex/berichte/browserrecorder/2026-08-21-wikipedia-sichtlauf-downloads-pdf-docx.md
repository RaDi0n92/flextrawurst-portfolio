EVIDENCE_VERSION: 1

# Wikipedia-Sichtlauf, Download-Abnahme und Office-Projektionen

Datum: 2026-08-21  
Arbeitsfläche: Desktop 1 (`DISPLAY=:1`), sichtbares Chromium mit persistentem Playwright-Profil  
Original: `https://de.wikipedia.org/wiki/Browser` → sichtbare Weiterleitung auf `https://de.wikipedia.org/wiki/Webbrowser`  
Belegwurzel: `/tmp/dak-wikipedia-live/`

## Sichtbare Laufkette

- Die Originalseite wurde im sichtbaren Browser geöffnet; der Seitentitel war `Webbrowser – Wikipedia`.
- Pro Format wurde die Seite mit endlichen Maus-Wheel-Schritten (`84 %` der Viewport-Höhe) vollständig durchlaufen. Endzustand: `scrollY=10157`, `scrollHeight=10977`, `viewportHeight=820`; die letzte Stufe erreicht das Seitenende.
- Der erste Lauf hatte 16 Stufen (`step-000.png` bis `step-015.png`); der Markdown-Vergleich hatte wegen eines zusätzlichen Rand-Schritts 17 Stufen (`step-000.png` bis `step-016.png`).
- Sichtbare Screenshots liegen unter `/tmp/dak-wikipedia-live/screens/` sowie je Format unter `download-<format>-before.png`, `download-<format>-after.png` und `compare-<format>-step-*.png`.
- Der Download wurde jeweils als Playwright-Download-Ereignis abgewartet und mit `download.saveAs(...)` abgeschlossen; fünf textuelle Formate plus PDF und DOCX sind vorhanden.

## Finales Hash-Paar (Originalartefakt = Browser-Download)

| Format | Bytes | SHA-256 |
|---|---:|---|
| PAGE.md | 19172 | `642620bf913c164fd4aa5efeecee20f24101e997866cf594b273b18cc625eaf5` |
| PAGE.html | 26123 | `dfa7072a699a8808a69c3a636199587ca31dc06c47d201fd0f54b55c05f0b281` |
| PAGE.txt | 18764 | `239aed0312843fa44ab7e6aa32020bc1b47f71003732aa37d5b6e791b9ae5a30` |
| PAGE.csv | 26511 | `093b3b449e350e789e673c24fd08f9e3b63a372b2bd57105e48282da232c61c2` |
| PAGE.json | 28093 | `1c6ed34b0d20ec86ec0d69542920c06f575b962e14bc9af6f2efb2d0683b3868` |
| PDF | 63579 | `88270a659e8a3479b5776385cfb336bb764abd11452b83251ba2c67a86cffd9e` |
| DOCX | 45027 | `1a402c624d46c37b0d43a7c4fe42e483a72e9dae52cedd6650a0d0e2413ebbca` |

Die Hashes wurden jeweils zweimal gelesen: aus dem erzeugten Originalartefakt und aus der final gespeicherten Datei in `/tmp/dak-wikipedia-live/downloads/`. Alle Paare sind bytegleich. Die maschinenlesbare Vergleichsdatei ist `/tmp/dak-wikipedia-live/playwright-download-compare.json`; sie enthält je Format `download_complete: true` und `token_recall: 1` gegen den vollständig durchlaufenen Original-DOM bzw. die extrahierte PDF-/DOCX-Schicht.

## PDF und DOCX

PDF und DOCX sind aus derselben vollständigen Wikipedia-DOM-Projektion erzeugt, anschließend über den sichtbaren Browser heruntergeladen und aus der finalen Datei rückgelesen. Die Office-Rücklese liegt in `/tmp/dak-wikipedia-live/wikipedia-browser-live/office-extracted-text.json` (PDF: 18052 Zeichen, DOCX: 22257 Zeichen).

## Grenzen der Aussage

Das ist ein echter sichtbarer Browser-/Playwright-Lauf gegen die Originalseite und eine abgeschlossene Download- und Hash-Kette. Die PDF/DOCX-Dateien sind Projektionen der erfassten Seite, keine byteidentischen Wikipedia-Originaldateien. Externe Bild-/Medien-Assets wurden nicht separat archiviert. Die neue Sidepanel-Route ist syntax- und Fixture-getestet; ein erneuter Produktionsservice-Neustart oder ein authentifizierter Recorder-Backend-Lauf war für diesen Beleg nicht nötig und wurde nicht vorgetäuscht.

## Gate-Marker

- REC-GATE-001: PASS — Vertragsprüfung mit `check_recorder_skill_gates.py contracts` grün.
- REC-BACKUP-001: PASS — Backup-Sicherheitspunkt `2904e4e18` vor Abnahme-/Berichtsschritt.
- REC-CRAWL-001: PASS — endlicher, sichtbarer Wikipedia-Lauf mit dokumentiertem Seitenende und Schritt-Screenshots.
- REC-EYE-001: PASS — sichtbare Desktop-1-Screenshots vor/nach Download und am finalen Originalzustand liegen vor und wurden geprüft.
- REC-FETCH-001: PASS — Quelle, Weiterleitung, Captures und bekannte Lücken sind im Laufbericht festgehalten.
- REC-DOWNLOAD-001: PASS — alle sieben Artefakte haben `download_complete: true`, Bytezahl und finale SHA-256-Rücklese.
- REC-REPLICA-001: PASS — PDF/DOCX-Provenienz verweist auf dieselbe vollständige Wikipedia-DOM-Projektion und die extrahierte Rücklese.
- REC-SEC-001: PASS — Downloadfläche ist eine lokale, kontrollierte Testfläche; keine fremden Uploads oder unmarkierten Fetches.
- REC-DOC-001: PASS — dieser Bericht, die maschinenlesbare Vergleichsdatei und die Screenshotpfade sind vorhanden.

OUTCOME: PASS
