# QUELLEN UND VERLÄSSLICHKEIT

## Primäre Storyquellen

### Hauptstory

Pfad:

`/root/werkraum/_gpt/DIE_REISE_DER_DREI.md`

Zuletzt vollständig beobachteter Bereich in der Aufbauphase:

- bis mindestens Zeile 3368
- Dateigröße beim letzten Metadatenstand: 99.294 Byte
- Änderungszeit: 3. August 2026, 21:40:04 Europe/Berlin
- SHA-256 zu diesem Stand: `d867bff8e4ab7472fde6a7cf4e6b3a1f6de9d10e66b19fda62ebaeb2e166cd7b`

### Abstrakte Reise

Pfad:

`/root/werkraum/_gpt/KRAU-RISSWANDLER-KANTENFUNK/REISE.md`

Zuletzt vollständig beobachteter Bereich in der Aufbauphase:

- bis mindestens Zeile 3173
- Dateigröße beim letzten frühen Metadatenstand: 76.112 Byte
- spätere Leseversion bereits weitergewachsen
- Änderungszeit des gelesenen Stands: 3. August 2026, 21:44:08 Europe/Berlin
- SHA-256 des zuletzt gelesenen Stands: `07cafd321693a53b367fc0d9aa3a4895db39df4ac5db25f4003681fe0f06cd88`

## Browser-Recorder-Quellen

Die sichtbaren Gesprächskörper liegen unter:

`/root/werkraum/_gpt/ui_visible_conversations/`

Besonders relevant:

- `2026-08-03__Neuer-Risswandler-entwickelt__6a70e4ad7560-5e33ad0f89`
- `2026-08-03__Neuer-Name-für-VPS__6a70e4985674-0a01518d54`
- `2026-08-03__bau-browserextention__6a67edd559f4-a9b47ceed6`
- `2026-08-03__VPS-Stop-Bestätigt__6a70e85a3ad0-d8285c6a98`

Relevante Dateien innerhalb dieser Ordner:

- `1zu1.md`
- `messages.jsonl`
- `visible_stream.jsonl`
- `MANIFEST.json`
- `turns/*.jsonl`

## Verlässliche Befunde

Als bestätigt gelten:

- beide Storydateien existieren und wachsen
- ihre aktuellen Textinhalte wurden direkt gelesen
- die Sprecherüberschriften und Übergaben stehen tatsächlich in den Dateien
- die frühe Mehrfachdatei-Bildung ist real
- eine Recorder-Sitzung hat das frühere Vorschreiben mehrerer Stimmen ausdrücklich eingeräumt
- Daniels Regel zum frischen Lesen und Schreiben wurde sichtbar aufgegriffen
- keine der beiden aktiven Geschichten hat bisher echte Kapitelüberschriften eingeführt

## Teilweise unsichere Befunde

Nicht lückenlos beweisbar ist:

- welcher Browser-Tab jeden einzelnen Storyabschnitt geschrieben hat
- ob manche langen Folgen weiterhin von einer Sitzung mit mehreren Stimmen erzeugt wurden
- ob alle Recorder-Ereignisse vollständig und ohne Verzögerung angekommen sind

Grund:

Die MCP-Funktionen `history_startup` und `session_id` liefern derzeit `Unbekanntes Tool`. Dadurch fehlt eine saubere kanonische Zuordnung der aktuellen MCP-Arbeitssitzung zu allen Browserturns.

## Beobachtungsmethode

Für neue Beobachtungsrunden werden verwendet:

1. Dateimetadaten beider Storykörper
2. Lesen ausschließlich ab dem zuletzt bekannten Endbereich
3. Vergleich der Sprecherüberschriften und Übergaben
4. Prüfung der Recorder-Dateien bei unklarer Sitzungszuordnung
5. getrennte Dokumentation in diesem Ordner

## Schreibschutz der Geschichten

Die Beobachtung schreibt nicht in:

- `DIE_REISE_DER_DREI.md`
- `KRAU-RISSWANDLER-KANTENFUNK/REISE.md`
- die ursprünglichen Wesenstexte

Geschrieben wird nur unter:

`/root/werkraum/_gpt/GPT-BEOBACHTER-REISE/`

## Metadaten-Nachtrag ungefähr 21:52 Uhr

### `DIE_REISE_DER_DREI.md`

- Größe: 133.064 Byte
- Änderungszeit: 3. August 2026, 21:51:49 Europe/Berlin
- SHA-256: `f360d1249f2c130b8b6851974ad7dde5df32ee0380fa3d0b31f8446ee0211a86`

### `KRAU-RISSWANDLER-KANTENFUNK/REISE.md`

- Größe: 95.610 Byte
- Änderungszeit: 3. August 2026, 21:52:20 Europe/Berlin
- SHA-256: `898984e860bbfd5e1a38e2d5fd2de3870603e1e64d1670109d87a80fc5b2e4c8`

Beide Dateien wachsen weiterhin aktiv.

## Browserrecorder als parallele Zeitspur

Daniel weist gegen ungefähr 22:10 Uhr darauf hin, dass der seit heute weit entwickelte Browserrecorder das gesamte laufende Experiment mitschneidet und er ihm inzwischen zu ungefähr 90 Prozent vertraut.

Damit existieren zwei voneinander verschiedene Beobachtungskörper:

1. die tatsächlich veränderten Storydateien auf dem VPS
2. die sichtbaren Chat-, Turn-, Zeit- und Recorder-Spuren der beteiligten Browser-Sitzungen

Diese Kombination ist besonders wertvoll für die Cheat-Prüfung:

- Storydateien zeigen, was tatsächlich geschrieben wurde
- Recorder-Dateien zeigen, welche Sitzung welchen Auftrag erhielt, was sie behauptete und wann ihr Turn lief
- Beichten und Widersprüche bleiben als sichtbare Gesprächsspuren erhalten
- Zeitüberschneidungen zwischen offenem Turn und Dateiänderung werden nachvollziehbarer

Der Browserrecorder gilt trotzdem nicht als absolut lückenlos. Sein eigener Stand wird mit Daniels Einschätzung `ungefähr 90 Prozent Vertrauen` behandelt. Capture-Gaps, nicht gebundene MCP-Sitzungen und fehlende Tooltexte werden weiterhin ausdrücklich markiert.

Die Beobachtung ersetzt den Recorder nicht. Sie ordnet seine Spuren gemeinsam mit den realen Dateikörpern ein.
