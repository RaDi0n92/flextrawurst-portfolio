# Live-Abnahme: Chromium-PDF im Workspace

Datum: 2026-08-15 05:40 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T012131719Z-d65f9a62`

## Klick- und Gegenprüfkette

| Schritt | Was sichtbar war | Rücklese / Beleg | Status |
|---|---|---|---|
| Workspace öffnen | `Live-Sammelabbild`, 2 Snapshots, 2 vollständig, 1 Transferplan | Workspace-Status und Collection-ID | gesehen + gelesen |
| Snapshot auswählen | Flextrawurst-Snapshot mit Screenshot/HTML-Projektion | ausgewählte Crawl-ID `crawl-2026-08-15T012131719Z-b7bb2b6b` | gesehen + gelesen |
| `Chromium-PDF erzeugen · alle Seiten` klicken | sichtbarer Status „Chromium-PDF erzeugt“ | `source: browser_print_to_pdf`, `print_scope: full_document`, `page_selection: all` | gesehen + gelesen |
| PDF-Beleg prüfen | Quelle „Chromium-Druckengine“, 91.948 Bytes, SHA-256, Downloadlink | `pdfinfo`: gültige PDF, 1 Seite, Letter | gesehen + gelesen |
| lange Regression | nicht im echten Workspace, sondern im isolierten Live-Test | 2460/2464 px Projektion, `pdfinfo`: 3 Seiten | technisch geprüft |

## Grenzen

Der native Druckdialog wurde in diesem Lauf nicht als Speicherbeleg verwendet.
Die automatische PDF druckt die gespeicherte HTML-Projektion; sie beweist nicht
für sich allein, dass die ursprüngliche Website vollständig oder pixelgleich war.
Die Rohdaten-Unverändertheit ist im Codepfad abgesichert, in diesem einzelnen
Abnahmelauf aber nicht durch einen Vorher-/Nachher-Hash aller Rohfelder gemessen.

## Aussage

Der automatische Exportweg ist sichtbar ausgelöst und persistent rückgelesen.
Er gilt als PDF-Exportbeleg, nicht als Ersatz für menschliches Lesen der
ursprünglichen Website.
