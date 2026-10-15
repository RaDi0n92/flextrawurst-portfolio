EVIDENCE_VERSION: 1

# Replica-Abnahme: Rohquelle, Markdown, PDF und heruntergeladene Datei

Datum: 2026-08-15 15:32 +0200  
Ort: sichtbarer Chromium-Lauf mit isolierter Fixture und Live-Sammelabbild
Test: `_codex/tools/test_crawl_universal_collection_live.js`

## Eine sichtbare Aktion

Nach zwei ausdrücklich geklickten sichtbaren Snapshots wurde im Workspace genau
einmal `🧬 Replica-Bundle prüfen/exportieren` geklickt. Der Button arbeitet nur
auf der bereits gespeicherten Collection; er öffnet keine Quellseite und startet
keinen zusätzlichen Fetch.

## Was mein Auge sah

Das Workspace-Bild `/tmp/dak-crawler-after-visible-capture.png` wurde angesehen.
Es zeigt `Live · 1 Snapshot · 1 vollständig`, die sichtbare Position `300/1638`,
die drei Fixture-Leselinien und den neuen Replica-Button. Der Lauf selbst
enthielt anschließend zwei Snapshots; der erste Screenshot ist der sichtbare
Vorher-/Nachher-Beleg der Collection-Abnahme.

## Rücklese der erzeugten Datei

Die tatsächlich von Chromium heruntergeladene JSON-Datei wurde vom Datenträger
gelesen und geparst:

- Datei: `/tmp/dak-collection-audit-1786800669644/replica-bundle.json`
- 97.124 Bytes
- SHA-256: `7ccb0927ae71e750d6cfd118140ff5266e1a1590b3ed9c0dc58a7627093baddf`
- `schema: dak-replica/v1`
- 2 Snapshots; beide gespeicherten Quelltexte sind im Bundle und in der
  Markdown-Projektion enthalten.
- `navigation_performed: false`, `additional_fetch_performed: false`

Der bestehende harte Dateiabgleich bleibt zusätzlich bestehen: Die
Quellabschrift und die erzeugte Markdown-Datei wurden Abschnitt für Abschnitt
exakt verglichen. Die erzeugte Sammlungs-PDF wurde als Datei gespeichert,
mit `pdftotext` zurückgelesen und beide extrahierten Texte wurden gegen die
gespeicherten Originaltexte verglichen. Das Ergebnis war für beide Snapshots
gleich.

## Was das Replica ist und was es nicht ist

Das Bundle ist ein gespeichertes Snapshot-Replica mit Roh-HTML, Lesetext,
Screenshot-Daten-URL, sichtbaren Links/Assets, Quellhashes und den erzeugten
Projektionen. Es ist kein Behauptungsautomat für eine pixelgleiche Originalseite:
HTML, Markdown und PDF sind verschiedene Repräsentationen; binäre Gleichheit
zwischen diesen Formaten wird ausdrücklich nicht behauptet. Replay bleibt
`projection_only_scripts_disabled`; die echte Website wird nicht nachgeladen.

## Marker

- REC-GATE-001: PASS — Contracts-Gate und Replica-Evidence-Gate liefen ohne Fehler.
- REC-REPLICA-001: PASS — Bundle enthält gespeicherte Rohquellen, Projektionen,
  Hashes, Scope und explizite Negativaktionen; kein neuer Tab/Fetch im
  Replica-Schritt.
- REC-DOWNLOAD-001: PASS — die heruntergeladene JSON-Datei wurde real gelesen,
  geparst und mit Bytezahl/SHA-256 rückgelesen.
- REC-FETCH-001: PASS — Replica selbst führt keinen Fetch aus; die getrennte
  Fetch-Abnahme bleibt für Ressourcenlimits und Provenienz maßgeblich.
- REC-DOC-001: PASS — Aktion, Augenbefund, Datei-Rücklese und Grenzen stehen
  getrennt in diesem Markdown-Bericht.

OUTCOME: PASS
