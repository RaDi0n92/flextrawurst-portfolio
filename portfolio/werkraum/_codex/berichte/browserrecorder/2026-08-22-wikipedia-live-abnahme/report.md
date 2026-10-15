# Wikipedia-Live-Abnahme · sichtbarer Playwright-Lauf

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SOURCE: `https://de.wikipedia.org/wiki/Wikipedia:Hauptseite`
COLLECTION: `collection-2026-08-22T154635287Z-1d97f70f`

## Aktion

Desktop 1 / Chromium wurde headful über CDP `9235` geprüft. Wikipedia blieb die sichtbare Quelle. Playwright führte den Lauf in einzelnen menschlichen Schritten aus: Startposition, Wheel 720, Wheel 900, Wheel 1100 bis zum Seitenende und ein weiterer sichtbarer Kontrollschritt. Nach jedem Schritt wurden Originalseite und Recorder-Seitenleiste fotografiert; danach wurde genau ein sichtbarer Snapshot gestartet und die Collection-/Crawl-Anzeige erneut gelesen.

## Sichtbar

Die Originalseite meldete im DOM `scrollHeight: 2550`, `innerHeight: 450`. Die Recorder-Collection schrieb nach den fünf ausdrücklich ausgelösten Snapshots:

| Snapshot | sichtbare Originalposition | gespeicherte Collection-Position |
|---:|---:|---:|
| 1 | `0` | `0/2099` |
| 2 | `720` | `720/2099` |
| 3 | `1620` | `1620/2099` |
| 4 | `2099` | `2099/2099` |
| 5 | `2099` | `2099/2099` |

Belege liegen als `wiki-live-01..05-*-original.png`, `*-before-snapshot.png` und `*-after-snapshot.png` vor. Der Workspace-Screenshot vor und nach dem Export ist ebenfalls enthalten.

## Rücklese

Die Collection zeigte `5 sichtbare Snapshots`, `26040 Lesetextzeichen` und fünf vollständige Einträge. Aus genau dieser Collection wurden über die sichtbare Parity-Ebene alle Quellen markiert und anschließend DOCX und PDF erzeugt.

| Format | Bytes | SHA-256 |
|---|---:|---|
| DOCX | 50622 | `817d58b06d2f142558ae8f5217b32c92195e7e35bfcdcec9f0f76305a758fe08` |
| PDF | 1140380 | `b3aeeeb2debcc59d74d48821e28424f2635e3ecc4324e5380ccfb45262b9d0b6` |

Der sichtbare Workspace meldete für beide Artefakte `Server: persisted`. DOCX ist als Office-ZIP/OOXML geschrieben; PDF bleibt eine Druck-Projektion der sichtbaren Sammlung.

## Gefundener Fehler und Fix

Der erste Lauf meldete für Wikipedia bei jeder Position `0/394`, obwohl die sichtbare Seite weitergescrollt war. Ursache war die Auswahl eines verschachtelten Overflow-Containers als Scrolloberfläche. `core/crawl_recorder.js` priorisiert jetzt das scrollbare Dokument, wenn das Dokument selbst höher als der Viewport ist. Der Wiederholungslauf belegt die korrekten Positionen oben.

## Grenzen

Die fünfte Aktion war absichtlich ein Kontrollsnapshot am bereits erreichten Seitenende; sie beweist, dass der Endzustand stabil bleibt. Die PDF/DOCX-Dateien sind Projektionen der gespeicherten sichtbaren Snapshots, keine pixelidentische Medienarchivierung.

- REC-GATE-001: PASS — Recorder-Verträge vor Änderung und Live-Lauf geprüft.
- REC-BACKUP-001: PASS — Backup-Commits vor Scroll-Fix, Status-Fix und Evidence-Schreiben vorhanden.
- REC-EYE-001: PASS — Originalseite, Vorher-/Nachher-Seitenleiste, Workspace und sichtbare Positionen fotografiert.
- REC-CRAWL-001: PASS — jede Seite ausschließlich durch ausdrücklichen sichtbaren Snapshot-Klick; kein Auto-Scroll, keine Folgeseiten.
- REC-DOWNLOAD-001: PASS — DOCX/PDF-Downloads abgewartet, lokal gelesen, Bytegrößen und SHA-256 rückgelesen.
- REC-FETCH-001: PASS — Collection-/Snapshot-/Manifest-Rücklese aus Recorder und Workspace.
- REC-SEC-001: PASS — keine Tokens, Secrets oder Zugangsdaten in Belegen.
- REC-DOC-001: PASS — Aktion, sichtbare Belegkette, Rücklese, Fix und Grenzen dokumentiert.

OUTCOME: PASS
