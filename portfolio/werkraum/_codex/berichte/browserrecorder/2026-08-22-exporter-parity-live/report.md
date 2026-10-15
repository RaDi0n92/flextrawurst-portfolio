# Exporter-Parity Live-Formate

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SCOPE: Sichtbarer Recorder-Workspace, gemeinsame Exporter-Parity-Ebene

## Aktion

Die bestehende Wikipedia-Manuelle-Seitensammlung wurde im sichtbaren Workspace mit den sechs verfügbaren Projektionen ausgegeben: CSV, JSON, TXT, Markdown, DOCX und PDF. Jede Aktion erfolgte über die sichtbaren Format- und Export-Steuerelemente in Playwright; pro Datei wurde der Browser-Download abgewartet und die lokale Datei gelesen.

## Sichtbar

- Screenshot: `parity-all-formats-after.png`
- Vor jeder Ausgabe war die sichtbare Format-Auswahl auf das jeweilige Format gesetzt.
- Der Workspace zeigte nach jeder Ausgabe einen expliziten Status mit Bytes, SHA-256, Servermanifest und Browser-Download.

## Rücklese

| Format | Datei | Bytes | SHA-256 |
|---|---|---:|---|
| CSV | `parity-live-csv.csv` | 10952 | `8078696a97e1d9e1a2d5c51b331c4c779cd15c94b339b2d54680c1413ad34eb7` |
| JSON | `parity-live-json.json` | 13093 | `b24f8d885bb10450d22884d4ab61d92d5c960aad2de65ec35e8956d5a946f4a8` |
| TXT | `parity-live-txt.txt` | 11001 | `cdb79a33b242abed9fa87c18312713e5e430e47c00526164687b3135c87fbd65` |
| MD | `parity-live-md.md` | 10922 | `1597ebb7062961f39cc093e42749476c0be33b0367ebc04742009f97ac996688` |
| DOCX | `parity-live-docx.docx` | 21174 | `4287282b13199a189fd6e7dd9f4ea11dd1c266ea5aee7d681bfeb093c4c493e8` |
| PDF | `parity-live-pdf.pdf` | 338387 | `2701cec9f2a9b161f481feff5667b14859479dea182f210d5b8e1282f8ae3afc` |

DOCX-Rücklese: ZIP/OOXML-Magic `504b`; `word/document.xml` und Styles vorhanden; die deaktivierte Reasoning-Option wurde nicht als Reasoning-Abschnitt ausgegeben. PDF-Rücklese: lokaler SHA-256 entspricht dem sichtbaren Workspace-Status.

## Grenzen

Die PDF-Projektion bleibt eine Druck-Projektion der sichtbaren Quellen, keine pixelidentische Medienarchivierung. Provider-spezifische Optionen werden als Projektionseinstellungen im Manifest mitgeführt; die Format- und Downloadkette ist nachweisbar.

- REC-GATE-001: PASS — Recorder-Verträge vor der Änderung geprüft.
- REC-EYE-001: PASS — sichtbare Workspace-Formatwahl, Status und Screenshot belegt.
- REC-DOWNLOAD-001: PASS — sechs Browser-Downloads abgewartet, Dateien lokal gelesen, Bytes und SHA-256 rückgelesen.
- REC-FETCH-001: PASS — Artefakte und Manifeststatus aus sichtbarer Exportkette rückgelesen.
- REC-SEC-001: PASS — keine Tokens oder Secrets in Exportdateien bzw. Bericht aufgenommen.
- REC-DOC-001: PASS — Evidence-Version, Aktion, Sichtbarkeit, Rücklese und Grenzen dokumentiert.

OUTCOME: PASS
