# KONSOLIDIERUNG SPIEL / WERKSTATT · 2026-09-02

Status: **aktive Konsolidierungs- und Bauphase**

Dieser Ordner ist der heutige Einstieg in den seit Juli/August gewachsenen Spiel-Wildwuchs. Er ersetzt weder GemGems-Archäologie noch bestehende Spielquellen. Er trennt sie erstmals ausdrücklich in drei operative Schichten:

1. **HISTORISCH** – Archäologie, alte Prototypen, frühere Varianten und Beweisquellen. Darf relevant sein, baut aber nicht automatisch die heutige Welt.
2. **AKTUELL** – heute real laufende/benutzte Implementierungen und ausdrücklich weiterhin gültige Spielkörper bzw. Verträge.
3. **ARBEIT** – Entwürfe, noch nicht ausführbare Architektur, neue Spielideen und noch nicht in den aktuellen Spielkörper integrierte Entscheidungen.

## Heutiger technischer Befund

- `flextrawurst-spiel-werkstatt.service` läuft real auf `127.0.0.1:18119`.
- Godot-World-Bridge antwortet real auf `127.0.0.1:18092/health`.
- 3D-MCP `8090` und produktiver VPS-MCP `8091` lauschen weiterhin; `/health` ist dort kein definierter Endpoint und liefert 404.
- Der alte `truth_engine` ist **nicht** die heutige Wahrheit: Status `degraded_last_good_preserved`, letzte erfolgreiche Generation 2026-07-26, aktuelle Obsidian-Validierung scheitert an alten Wikilinks.
- Ein ausführbarer Spiel-Kontextinjektor wurde im Bestand nicht gefunden; vorhanden ist das Konzept vom 2026-08-17.
- Das Mandat `LEBENDES_SPIELGEDAECHTNIS` existiert, aber der spezialisierte Spielgedächtnis-Körper ist nicht als fertig implementiertes Gesamtsystem vorgefunden worden.

## Bauentscheidung 2026-09-02

Nicht noch einen konkurrierenden Wahrheitsapparat danebenstellen.

Die bereits laufende Spiel-Werkstatt wird erweitert um:

- eine **live berechnete Aktuelle-Wahrheit-Ansicht**, die HISTORISCH / AKTUELL / ARBEIT sichtbar trennt;
- sichtbaren Gesundheitsstatus realer Laufzeitkörper;
- einen kleinen **ausführbaren Kontext-Endpunkt**, der aus einem kuratierten Quellenregister relevante Quellen mit Herkunft und Schicht zurückliefert;
- keine automatische Kanonisierung von Treffern;
- keine stille Nutzung des degradierten alten Truth-Engine als aktuelle Wahrheit.

Das Quellenregister liegt in `CURRENT_CONTEXT_SOURCES.json`.

Die Werkstatt bleibt menschlicher Zugang und Arbeitsoberfläche. Godot bleibt spielbare Verkörperung. GemGems bleibt Archäologie/Beweiskörper. Der neue Kontext-Endpunkt ist eine erste ausführbare Naht für AI-Ströme, nicht die Behauptung eines schon vollständig automatisierten Multi-AI-Gedächtnisses.
