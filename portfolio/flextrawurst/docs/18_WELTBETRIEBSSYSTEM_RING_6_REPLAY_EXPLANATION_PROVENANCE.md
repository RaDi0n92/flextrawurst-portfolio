# Weltbetriebssystem Ring 6 — Replay / Zeitspur / Erklärbarkeit

## Was Ring 6 ist

Ring 6 erklärt, warum ein sichtbarer Bedeutungs-Hinweis (VisualMeaning) existiert. Dazu bauen wir:
- ReplayTimeWindow: Zeitfenster über Events und Frames
- WorldReplayTrace: Spur eines Slots durch die Ereignisgeschichte
- VisualReplayExplanation: Vollständige Erklärung eines VisualMeaning

## Verbindliche Invarianten

- Replay erzeugt niemals neue Events
- Replay aktiviert niemals Slots
- Replay verwandelt niemals Import-Kandidaten in Live-Zustände
- can_trigger_activation ist immer false

## Erklärungsfelder

- visual_id
- why_visible: Warum ist dieser Bedeutungs-Hinweis sichtbar?
- source_summary: Zusammenfassung der Herkunft
- world_ground: Weltgrund — strukturelle Begründung
- provenance_markers: Liste der Herkunfts-IDs
- activation_status: blocked oder not_ready
- is_live_state: Ist dies ein aktueller Live-Zustand?
- is_import_origin: Kommt dies aus einem Import?
- can_trigger_activation: immer false

## Was Ring 6 nicht baut

- Keine neuen Events
- Keine Aktivierung
- Keine Mutation des EventStore
- Keine UI
