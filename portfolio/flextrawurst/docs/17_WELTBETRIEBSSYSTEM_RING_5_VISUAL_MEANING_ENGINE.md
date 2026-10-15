# Weltbetriebssystem Ring 5 — Visual Meaning Engine ohne Renderer

## Was Ring 5 ist

Ring 5 übersetzt Weltzustände und Events in sichtbare Bedeutungs-Hinweise (VisualMeaning). Es gibt keinen Renderer, kein Canvas, kein DOM. Nur Datenmodelle, die später von einem Renderer genutzt werden können.

## Kernprinzip

Keine visuelle Bewegung ohne Weltgrund.
Kein Effekt ohne erklärbare Provenienz.
Kein Graph als Deko-Netzwerk.

## Pflichtfelder jedes VisualMeaning

- visual_id, visual_kind, meaning, intensity, confidence
- source_event_ids / source_state_ids / source_slot_ids / source_room_ids
- is_decorative: immer false — dekorative Visuals sind verboten
- created_from, created_at

## Visual Kinds

- node_pulse: Weltpuls eines Entitätsslots
- edge_pressure: Kantenspannung zwischen Knoten
- silence_shell: Schweige-Hülle um inaktive Slots
- memory_echo: Echo eines vergangenen Ereignisses
- dream_residue_hint: Hinweis auf Traumrückstand
- room_density: Raumdichte-Marker
- activation_block: Blockierung durch Activation Firewall
- origin_marker: Herkunftsmarker (z. B. Flarum-Vorphase)
- replay_trace: Replay-Spur eines Ereignisses

## Flarum-Herkunft als origin_marker

Flarum-Accounts können als origin_marker dargestellt werden:
- origin_layer: "flarum_vorphase"
- is_live_flextrawurst_state: false
- requires_start_decision: true

## Was Ring 5 nicht baut

- Kein Renderer
- Kein Canvas, kein DOM, kein Three.js, kein Cytoscape
- Keine UI
- Keine Animation
- Keine AI-Ausführung
