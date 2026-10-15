EVIDENCE_VERSION: 1

# Live-Abnahme: Replica-Bundle im echten virtuellerdesktop2

Datum: 2026-08-15 15:38 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T100824006Z-8c1ae203`

## Vorher

Nach dem Neuladen der Erweiterung zeigte der Workspace sichtbar zwei vollständige
Flextrawurst-Snapshots, die Position `0/5875`, eine vorhandene
Sammlungs-PDF mit 24 Seiten und den Button `🧬 Replica-Bundle
prüfen/exportieren`. Vorherbild: `/tmp/dak-real-replica-final-before.png`.

## Eine Aktion

Genau ein sichtbarer Klick auf `Replica-Bundle prüfen/exportieren` erzeugte den
Download. Der Button arbeitet auf der Collection; keine Quellseite wurde
geöffnet, kein Tab gewechselt und kein zusätzlicher Fetch ausgelöst.

## Nachher mit eigenen Augen

Nachherbild: `/tmp/dak-real-replica-final-after.png`. Sichtbar blieb der
Workspacezustand mit denselben zwei Snapshots; oben stand `Replica zuletzt
rückgelesen`. Darunter stand:

`Replica-Bundle vorhanden · 2 Quellen · Markdown-Rückhalt 2/2 · 3075510 Bytes · SHA-256 f3e755603da7bfa39f90d242dbe8e8189b2aa010b2d47e85381d6919205d6aca · keine Navigation oder neuen Fetches.`

## Persistenz-Rücklese

Der Browser-Download wurde über `chrome.downloads` als `complete`,
`fileSize: 3075510` und `exists: true` rückgelesen. Die Datei lag im Container
unter `/tmp/playwright-artifacts-Lx58Tv/0929fb8f-97af-47f6-a16a-89b4d655dba7`.
Python las sie dort real und parste sie:

- `schema: dak-replica/v1`
- 3.075.510 Bytes
- SHA-256 `f3e755603da7bfa39f90d242dbe8e8189b2aa010b2d47e85381d6919205d6aca`
- 2 Snapshots
- `source_text_embedded_snapshots: 2`
- `navigation_performed: false`
- `additional_fetch_performed: false`

## Ehrlicher Fehlerversuch

Ein früherer echter Klick lieferte zunächst nur einen temporären
Playwright-Artefaktpfad, der aus dem Codex-Prozess nicht geöffnet werden konnte.
Das wurde als Rücklesefehler behandelt. Erst der anschließende Lauf mit
Container-Rücklese gilt als Beleg. Erfolg wurde nicht aus `download`-Event oder
`exists` allein behauptet.

Die PDF-Text-gegen-Original-Prüfung gehört zum separaten isolierten
Collection-Lauf: Dort wurde die erzeugte PDF mit `pdftotext` gelesen und beide
Quelltexte wurden exakt verglichen. Dieser echte Desktop-Lauf beweist für das
Replica-Bundle die JSON-Rücklese, nicht erneut die PDF-Text-Extraktion.

## Marker

- REC-GATE-001: PASS — Vertrags- und Evidence-Gates wurden ausgeführt.
- REC-REPLICA-001: PASS — echter sichtbarer Klick, persistente Container-Datei,
  zwei Quellen, Hash und Negativaktionen stimmen zusammen.
- REC-DOWNLOAD-001: PASS — Chrome meldete `complete`; Größe und SHA wurden aus
  der realen Containerdatei gelesen.
- REC-FETCH-001: PASS — der Replica-Klick meldete und speicherte keinen neuen
  Fetch; Ressourcen-Fetch bleibt separat abgenommen.
- REC-DOC-001: PASS — Vorher, eine Aktion, Nachher, Rücklese und Fehlerversuch
  sind getrennt dokumentiert.

OUTCOME: PASS
