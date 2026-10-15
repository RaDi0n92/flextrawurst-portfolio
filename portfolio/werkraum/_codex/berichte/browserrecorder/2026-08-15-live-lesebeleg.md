# Live-Abnahme: lesbare Markdown- und PDF-Ausgaben

Datum: 2026-08-15 12:24 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T100824006Z-8c1ae203`  
Snapshot: `crawl-2026-08-15T100949025Z-e24f0e29`

## Klick- und Gegenprüfkette

| Schritt | Sichtbarer Befund | Rücklese / Gegenbeleg | Status |
|---|---|---|---|
| Flextrawurst sichtbar aktivieren | echter Browser-Tab zeigte `Was ist das? — flextrawurst` | `chrome.tabs.query(active:true,currentWindow:true)` meldete exakt `https://flextrawurst.de/` | gesehen + gelesen |
| Aufnahme klicken | genau ein sichtbarer Start im Universalmodus | `source_mode: active_visible_tab`, `trigger: explicit_user_start`, `status: complete`, `top: 0`, `max_top: 5875`, `scroll_height: 6312`, `text_length: 16844` | gesehen + gelesen |
| Workspace öffnen | Screenshot oben lesbar; Ausgaben kompakt darunter; HTML standardmäßig optional | Collection blieb bei zwei Snapshots; Rohstatus blieb `Rohdaten unverändert` | gesehen + gelesen |
| Markdown herunterladen | sichtbarer Button `Markdown herunterladen` | 20.389 Bytes; Titel, `KI-Wesen und echte Menschen.`, `Welt-API aktiv`, `LEITSTAND ÖFFNEN` und Grenze gegen automatische Ergänzung enthalten | gesehen + gelesen |
| HTML-Projektion öffnen | optionale Rohspur blieb nach 1,4 s Polling offen | statischer Stil vorhanden, `animationName: none`, `opacity: 1`, `textLength: 16830` | gesehen + gelesen |
| Chromium-PDF erzeugen | sichtbarer Status `Chromium-PDF erzeugt · 12 Seiten erkannt` | 771.351 Bytes, `source: browser_print_to_pdf`, `print_scope: full_document`, `page_selection: all`, SHA-256 `932cbe444a306ce3dd95f05e3f055c0c6292dc7e51104d79e53f3374b6c7661d` | gesehen + gelesen |
| PDF prüfen | gerenderte erste PDF-Seite zeigte Screenshot plus vollständigen Lesebeleg | `pdfinfo`: 12 Seiten; `pdftotext`: Flextrawurst, Welt-API, Leitstand, Weltkarte und Herkunft gefunden | gesehen + gelesen |
| Rohdaten nach PDF | kein sichtbares Rohfeld verändert | HTML-, Text- und Screenshot-SHA-256 vor/nach PDF identisch | geprüft |

## Ehrlicher Fehlversuch

Ein früherer Klick wurde trotz alter Flex-Anzeige im echten Browser auf dem aktiven
RFC-Tab ausgeführt. Er speicherte deshalb korrekt `RFC Editor` in der getrennten
Collection `collection-2026-08-15T092846413Z-d6521307`. Der Snapshot wurde nicht
gelöscht oder umetikettiert. Erst die echte Desktop-Aktivierung von Flextrawurst
und die erneute Prüfung des aktiven Tabs führten zum Flextrawurst-Beleg.

## Was jetzt verbessert ist

- Lesetext wird bei neuen Aufnahmen tatsächlich gespeichert; zuvor wurde nur seine
  Länge gezählt.
- Markdown ist eine direkte, lesbare Ausgabe mit Herkunft, Position, Text, Links
  und klarer Grenze.
- Screenshot bleibt der sichtbare Originalausschnitt.
- Die optionale HTML-Projektion friert Animationen ein und lässt innere
  Scrollflächen sichtbar werden, ohne den Roh-Snapshot zu ändern.
- Der PDF-Weg erzeugt einen ruhigen Lesebeleg aus Screenshot, gespeichertem Text
  und Linkzielen. Die Layout-Rohspur ist im Druckfenster optional.

## Grenzen

Der Universalmodus nimmt weiterhin nur den ausdrücklich geklickten sichtbaren
Zustand auf. Es gibt keinen Auto-Scroll und kein automatisches Folgen von Links.
Der PDF-Beleg enthält deshalb alles, was in diesem Snapshot als DOM/Text gespeichert
wurde; er beweist nicht, dass jede dynamische Website-Schicht oder jede externe
Ressource vollständig und pixelgleich vorlag. `full_document/all` beschreibt hier
den gespeicherten Lesebeleg, nicht eine heimliche Vollbesichtigung der Website.

## Aussage

Der Flextrawurst-Fall ist jetzt als lesbarer Beleg brauchbar: Screenshot, Markdown,
PDF und Rohdaten widersprechen sich nicht; die Provenienz bleibt sichtbar, und der
ehrliche Fehlversuch bleibt als Fehlversuch erhalten.
