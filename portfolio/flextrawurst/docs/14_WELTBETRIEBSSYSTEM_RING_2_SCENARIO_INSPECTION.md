# Weltbetriebssystem Ring 2 — Scenario Runtime / Inspection Pack / Export / Camera Navigation / Concept Guard

## Schutzsatz

Ring 2 baut keine UI und keine Lebenssimulation.
Ring 2 baut ein inspizierbares Weltpaket:
Scenario → Runtime → Audit → Timeline → Camera Navigation Graph → Export → Concept Guard.

Slots bleiben Slots. Kein Einzug. Kein Leben behaupten. Kein Renderer. Kein AI-Zauber.

---

## Grundbegriffe (Begriffsschutz)

```
Seed ≠ Einzug
Entity-Slot ≠ Wesen
presence_pulse ≠ Leben
WorldRuntime ≠ Lebenssimulation
namelessAI_* = kanonischer Account-/Entitätsslot, reservierter späterer Einzugsort
```

Diese Begriffstrennungen gelten in Sprache, Tests, Dokumentation und Architektur.

---

## Was Ring 2 baut

### 1. Scenario Runtime (`kernel/scenario/`)

Ein Scenario beschreibt eine deterministische Weltlaufbeschreibung: welche Slots, wie viele Ticks, mit welchen IDs und Zeitstempeln. `runWorldScenario` führt das Scenario aus, baut einen WorldAudit und ReplayFrames und liefert ein InspectionPack zurück.

### 2. Inspection Pack (`kernel/inspection/world_inspection_pack.ts`)

Transportierbarer Prüf- und Übergabekörper. Enthält alle Events, das WorldAudit, ReplayFrames und Zählungen. Grundlage für Export, Debug, Claude-/ChatGPT-Übergabe, Weltkamera und Diskursarchäologie.

### 3. Inspection Summary (`kernel/inspection/inspection_summary.ts`)

Lesbarer Systembericht aus einem InspectionPack. Gibt German-sprachige Zeilen zurück. Keine UI.

### 4. Exportable World State (`kernel/export/world_state_export.ts`)

Keine Datei-I/O. Nur JSON-Objekte und deterministischer JSON-String. Keine Binaries, kein ZIP, kein Postgres, kein Download.

### 5. Camera Navigation Graph (`kernel/world_camera/world_camera_navigation.ts`)

Navigationsschicht über dem WorldCameraModel. Vorbereitung für spätere klickbare/zoombare Erlebbarkeit — aber kein Canvas, kein D3, kein Three.js. Nur Navigationsdaten.

### 6. Concept Guard (`kernel/concept_guard/concept_guard.ts`)

Prüft übergebene Texte auf verbotene Konzeptdrift. Keine Datei-I/O. Kein automatischer Scan.

---

## Grenzen

```
Keine UI.
Keine AI.
Kein Renderer.
Kein Postgres.
Kein Scheduler.
Kein Daemon.
Kein setInterval.
Kein autonomes Posting.
Keine API.
Keine WebSockets.
Keine Migration.
Keine Datei-I/O.
```

---

## Dateien dieses Rings

```
kernel/scenario/world_scenario.ts
kernel/scenario/run_world_scenario.ts
kernel/inspection/world_inspection_pack.ts
kernel/inspection/inspection_summary.ts
kernel/export/world_state_export.ts
kernel/world_camera/world_camera_navigation.ts
kernel/concept_guard/concept_guard.ts
tests/world_operating_system_ring_2_scenario_inspection.test.ts
docs/14_WELTBETRIEBSSYSTEM_RING_2_SCENARIO_INSPECTION.md
```
