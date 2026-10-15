# Live-1:1-Vergleich: Quellabschrift gegen Markdown und PDF

Datum: 2026-08-15 13:44 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T100824006Z-8c1ae203`

## Prüfregel

Bytezahl und Seitenzahl gelten nicht als Qualitätsbeweis. Für jeden gespeicherten
Snapshot wurde die beim sichtbaren Aufnahme-Klick vorhandene Lesetext-Repräsentation
als Quellabschrift in eine eigene Datei geschrieben. Danach wurden Markdown und PDF
ebenfalls als Dateien geschrieben und zurückgelesen.

## Dateien des echten Vergleichs

Die Live-Dateien lagen unter `/tmp/codex-tabwise-audit-live-final/`:

- `source-01.txt` — 16.821 Zeichen
- `source-02.txt` — 16.844 Zeichen
- `generated-collection.md` — 41.484 Bytes
- `generated-collection.pdf` — 1.458.939 Bytes
- `generated-collection-pdftotext.txt` — PDF-Text nach `pdftotext -layout`

Die Dateien sind bewusst getrennt: Quelle, erzeugte Markdown-Datei, erzeugte
PDF-Datei und aus der PDF zurückgelesener Text werden nicht zu einem einzigen
grünen Status vermischt.

## Ergebnis pro Snapshot

| Beleg | Quelle | Ergebnis | Fehlerklasse |
|---|---:|---|---|
| Markdown 1 | 16.821 Zeichen | Inhalt exakt; nur ein struktureller Abschluss-Zeilenumbruch | Format, kein Inhaltsverlust |
| Markdown 2 | 16.844 Zeichen | Inhalt exakt; nur ein struktureller Abschluss-Zeilenumbruch | Format, kein Inhaltsverlust |
| PDF-Text 1 | 16.821 Zeichen | Rohvergleich wegen Formfeed bei Offset 150 verschieden; Whitespace-normalisiert exakt gleich | echter PDF-Seitenumbruch |
| PDF-Text 2 | 16.844 Zeichen | Rohvergleich wegen Formfeed bei Offset 249 verschieden; Whitespace-normalisiert exakt gleich | echter PDF-Seitenumbruch |

Der Markdown-Vergleich entfernte ausschließlich den einen vom nächsten
Markdown-Heading benötigten Struktur-Zeilenumbruch. Danach war der Inhalt
zeichengetreu gleich. Beim PDF wurde `pdftotext -layout` verwendet; die beiden
Formfeeds markieren Seitenwechsel und keinen verlorenen oder veränderten Text.

## Hash-Gegenbeleg

Der erneuerte echte PDF-Beleg trägt:

- Quelle: `browser_print_to_pdf`
- Umfang: `collection_snapshots`
- Auswahl: `all`
- Snapshots: `2`
- PDF: 24 Seiten, 1.458.939 Bytes
- PDF-SHA-256: `f8e2cddcd0c96c27440f440239d8f227fd599233bec7610bfed88014691a7292`
- Quellhash 1: `1acae418cb629e6528911ad40de9be10fbae792a64842e9e8c9c3b79c647a295`
- Quellhash 2: `ed2df453fabb73c62f87db6a39d7801d4ad6be30d8709678cd8479065dbc8f32`

Der Workspace zeigte danach sichtbar `Quellhashes 2/2`. Die alte PDF wurde
vorher ehrlich als `Quellhashes 0/2` angezeigt und erst durch den erneuten
bewussten PDF-Klick ersetzt.

## Fehleranalyse

Es wurde kein Inhaltsverlust gefunden. Der einzige Markdown-Unterschied ist
eine notwendige Ausgabegrenze; die einzigen PDF-Unterschiede sind zwei
Formfeeds an Seitenumbrüchen. Ein byteweiser Vergleich der PDF mit einer
Textdatei wäre fachlich falsch, weil PDF Seitenlayout und Binärstruktur enthält.
Der belastbare Vergleich ist deshalb: Quelltextdatei gegen extrahierten
PDF-Lesetext, mit Rohdiff und separat ausgewiesener Layout-Normalisierung.

Die Quellabschrift ist der beim sichtbaren Klick gespeicherte Lesetext, nicht
ein späterer erneuter Abruf der Website. Damit wird genau der aufgezeichnete
Zustand geprüft und nicht unbemerkt ein aktueller Webseitenzustand untergeschoben.

## Konsequenz

Der Workspace stellt jetzt drei getrennte Ausgänge bereit: `Quellabschrift
exportieren`, `Sammlung als Markdown` und `Sammlung als PDF · alle Snapshots`.
Der Live-Test schreibt und vergleicht alle drei Materialschichten; ein bloßes
„grün“ ohne Rücklese der erzeugten Datei reicht dort nicht mehr.

Nach dem Vergleich wurde noch ein echter Randfall geschlossen: Die Markdown-
Erzeugung verwendet den gespeicherten Lesetext nicht mehr mit `.trim()`. Auch
führende und abschließende Zeichen bleiben damit in der Quellabschrift und in
der Ausgabe erhalten.
