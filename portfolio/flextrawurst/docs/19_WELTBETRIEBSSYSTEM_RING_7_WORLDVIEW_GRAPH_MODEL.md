# Weltbetriebssystem Ring 7 — Worldview Read-only Graph Model

## Was Ring 7 ist

Ring 7 baut den ersten read-only Graphkörper als Datenmodell. Kein Renderer, keine UI, kein Three.js, kein Cytoscape. Nur ein strukturiertes Datenmodell, das einen späteren Renderer anschließbar macht.

## Graph-Knoten-Typen

- entity_slot_node: Kanonischer Entitätsslot
- room_node: Raum/Weltraum
- event_node: Event aus dem EventStore
- import_origin_node: Herkunft aus Flarum/Forum (Vorphase)
- visual_meaning_node: Bedeutungs-Hinweis aus Ring 5
- replay_trace_node: Replay-Spur aus Ring 6

## Graph-Kanten-Typen

- slot_has_origin: Slot → Herkunft
- event_affects_slot: Event → Slot
- visual_explains_event: VisualMeaning → Event
- room_contains_slot: Raum → Slot
- replay_references_event: ReplayTrace → Event
- origin_candidate_maps_to_slot: ImportOrigin → Slot

## Zoom-Ebenen

cosmos → room → entity → post_or_event → raw_event → provenance

## Raumwetter (RoomWeather)

Raumwetter beschreibt den atmosphärischen Zustand eines Raums als Daten:
- density, activity, silence, tension
- origin_pressure, import_presence, live_presence

## Invarianten

- is_read_only: true — kein Schreiben
- uses_renderer: false — kein Renderer
- uses_ui: false — keine UI
- Keine Renderer-Felder im Graph
- Flarum-Knoten haben is_live_flextrawurst_state: false
- Import-Ursprünge haben requires_start_decision: true
