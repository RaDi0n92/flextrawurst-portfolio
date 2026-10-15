
# History und Zeitstrom

Die ANTIBIBEL besitzt mehrere getrennte Zeitebenen:

## 1. Global technische Primärquelle

`/root/werkraum/_gpt/session_history.jsonl`

Sie enthält hashverkettete Werkzeug- und Sessionereignisse. Diese Datei wird hier nur gelesen.

## 2. UI-sichtbarer Gesprächskörper

Der globale MCP-Vertrag speichert sichtbare Nachrichten getrennt von technischer History. Der lokale Spiegel liegt unter `ui_exports/`, sobald die Nachrichten erfolgreich über den MCP gebunden wurden.

## 3. Lokale Gründungschronik

`07_HISTORY/GRUENDUNGSEVENTS.jsonl` hält bedeutende inhaltliche Schritte fest, deren Bedeutung aus reinen Werkzeugaktionen nicht vollständig hervorgeht.

## 4. Generierter Projektzeitstrom

`ZEITSTROM.md` und `Zeitstrom/` werden aus globalen History-Ereignissen mit Bezug zur ANTIBIBEL sowie der lokalen Gründungschronik erzeugt.

Parallele Ereignisse bleiben getrennt. Modellierte Ursachen werden als modelliert markiert.
