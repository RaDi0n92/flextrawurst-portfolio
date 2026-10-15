# Deterministische Weltbewegung 2 — Planungsdokument

**Status:** Plan + Implementierung in einem Durchlauf (Commit edd206b als Basis).

---

## Ziel

Sechs kanonische namelessAI-Entitäten werden deterministisch geseedet. Ein
`system.tick` kann auf alle existierenden Entitäten angewendet werden. Für jede
Entität entsteht genau eine `presence_pulse`-State-Transition. Projektionen und
Render-Hints entstehen pro Entität isoliert. Historical Replay rekonstruiert die
Multi-Entity-Welt deterministisch.

## Kanonische Entitäten

```
namelessAI_1234, namelessAI_4321, namelessAI_1324,
namelessAI_1423, namelessAI_2341, namelessAI_3123
```

(Quelle: `docs/07_INITIALE_WESEN_UND_SYSTEMSCHICHTEN.md`)

## Neue Bausteine

```
kernel/entities/seed_entities.ts              → createSeedEvent + seedCanonicalEntities
kernel/projections/world_projection.ts        → buildWorldProjection (auto-discover aus Events)
vme/world_meaning_projection.ts               → buildWorldRenderHints
kernel/world_engine/run_presence_pulse_for_entities.ts → runPresencePulseForExistingEntities
kernel/replay/historical_replay.ts            → additiv: replayWorld
tests/deterministic_world_movement_multi_entity.test.ts → 16 Tests
```

## Schutzgrenzen

Keine AI. Kein UI. Kein Postgres. Kein Renderer. Kein Scheduler. Kein setInterval.
Kein autonomes Posting. Kein Schlafdruck. Kein Substanzdrift. Kein Tamagotchi.
Kein GENI-Aufruf. Kein dak+gord. Kein Systemweiser.

EventStore bleibt einzige Schreibschicht. Replay erzeugt keine Weltbewegung.
