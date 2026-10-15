# Live-Abnahme: tabweise Sammlung als Markdown und PDF

Datum: 2026-08-15 12:51 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T100824006Z-8c1ae203`

## Verständnis

Ein Tabwechsel allein nimmt nichts auf. Jeder sichtbare Aufnahme-Klick bleibt
ein eigener Snapshot mit eigener URL und Position. Die Sammelausgaben dürfen
danach ausschließlich diese bereits gespeicherten Snapshots zusammenführen;
keine weitere Seite darf dafür automatisch geöffnet, geladen, gescrollt oder
aufgenommen werden.

## Klick- und Gegenprüfkette

| Schritt | Was mein Auge sah | Rücklese / Beleg | Status |
|---|---|---|---|
| Bestehende Sammlung nach Extension-Reload öffnen | Zwei Flextrawurst-Snapshots, neue Buttons `Sammlung als Markdown`, `Sammlung als PDF · alle Snapshots` und zunächst deaktivierter PDF-Download | Workspace-DOM: 2 Snapshot-Karten, 4 Browserseiten unverändert | gesehen + gelesen |
| `Sammlung als Markdown` klicken | Status: `2 ausdrücklich gespeicherte Snapshots · keine weiteren Seiten ergänzt` | 41.314 Bytes; nummerierte Abschnitte 1 und 2; Flextrawurst-Lesetext und explizite Sammlungsgrenze enthalten; Snapshotzahl blieb 2 | gesehen + gelesen |
| Markdown-Download rücklesen | Erster CDP-Downloadpfad war bereits verschwunden; dieser technische Fehlversuch wurde nicht als Erfolg gezählt | Zweiter sichtbarer Klick mit Blob-Rücklese bestätigte den Inhalt direkt im Workspace | korrigiert + belegt |
| `Sammlung als PDF · alle Snapshots` klicken | Status und danach sichtbarer Beleg `Sammlungs-PDF vorhanden · 24 Seiten · 1458550 Bytes · Quelle browser_print_to_pdf` | Persistenz-Rücklese: `source: browser_print_to_pdf`, `print_scope: collection_snapshots`, `page_selection: all`, `snapshot_count: 2`, SHA-256 `43ba48f2c5b42307c2bc3e5ddae6038bd7489c2a3e8fc18be536ac9bc4e4b3db` | gesehen + gelesen |
| PDF-Datei prüfen | Gerenderte erste PDF-Seite zeigt Sammlung, Snapshot 1, Screenshot und Lesetext sauber lesbar | `pdfinfo`: gültige PDF, 24 Seiten, 1.458.550 Bytes; `pdftotext` findet Snapshot 1 und Snapshot 2 | gesehen + gelesen |
| `Sammlungs-PDF herunterladen` klicken | Status: `Sammlungs-PDF heruntergeladen · 2 Snapshots · gespeicherter Beleg` | Download-Ziel `data:application/pdf;base64`, Dateiname `seitensammlung-06Z-8c1ae203.pdf`; Snapshotzahl weiter 2 | gesehen + gelesen |

## Grenzen und ehrlicher Befund

Die Sammlung setzt nur die vorhandenen Snapshots zusammen. Sie beweist nicht,
dass die ursprüngliche Website vollständig oder pixelgleich gespeichert wurde.
Der Screenshot bleibt der sichtbare Ausschnitt; der Lesetext stammt aus dem
gespeicherten Snapshot. Beide echten Flextrawurst-Snapshots dieser Abnahme
zeigen dieselbe URL, weil genau diese bestehende Collection geprüft wurde.

Der PDF-Druck öffnet intern nur eine Erweiterungs-Druckansicht aus den bereits
gespeicherten Daten. Die Zielseiten-URLs blieben vor und nach dem PDF-Lauf
identisch; es entstand kein neuer Snapshot. Der normale Workspace-Status trägt
nicht die PDF-Base64-Daten, sondern nur Metadaten; die Datei wird erst beim
ausdrücklichen Download-Klick gelesen.

## Aussage

Tab für Tab aufnehmen funktioniert als getrennte Rohspur. Markdown und PDF
können anschließend bewusst als Sammlung „auftanken“, ohne den Recorder in
einen versteckten Crawler zu verwandeln.
