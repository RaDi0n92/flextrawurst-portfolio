# Mein Gesamtkonstrukt · Planer

Dieser Ordner ist der reale, servergespeicherte Körper des Planers.

## Eine aktuelle Wahrheit

`data/current.json` ist der einzige autoritative Arbeitsstand. Browser-Speicher ist nur ein kurzlebiger Cache und darf den Serverstand beim Laden niemals überstimmen.

## Ordner

- `app/index.html` – ausgelieferte Planeroberfläche
- `server/planner_api.py` – Seite und Server-API
- `server/sync.js` – automatische Synchronisierung der Oberfläche
- `data/current.json` – aktuelle vollständige Wahrheit, eingerückt und menschenlesbar
- `data/history/` – vollständige Schnappschüsse bei bewusst gespeicherten Arbeitsrevisionen
- `data/events/YYYY-MM-DD.ndjson` – chronologische, zeilenweise lesbare Speicherereignisse

## Schreibverhalten

Jede fachliche Änderung wird nach kurzer Tipp-Pause automatisch an den Server übertragen. Gleichzeitige veraltete Browserstände überschreiben neuere Serverstände nicht still: Die API antwortet mit einem Revisionskonflikt und die Oberfläche fordert zum Neuladen auf.

Die Schaltfläche für eine bewusste Revision bleibt zusätzlich erhalten. Sie erzeugt eine fachliche Arbeitsrevision und dadurch einen vollständigen Schnappschuss in `data/history/`.

## API

- `GET /Mein-Gesamtkonstrukt-planer/api/state/` – aktuellen Stand lesen
- `PUT /Mein-Gesamtkonstrukt-planer/api/state/` – aktuellen Stand mit `baseRevision` konfliktgeprüft schreiben

Alle Antworten und die Planerseite selbst werden mit `no-store` ausgeliefert.
