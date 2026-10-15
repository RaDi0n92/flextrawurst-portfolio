import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  CANONICAL_ENTITY_IDS,
  seedCanonicalEntities,
} from "../kernel/entities/seed_entities.ts";
import { runWorldTickOnce } from "../kernel/world_engine/run_tick_once.ts";
import { runPresencePulseForExistingEntities } from "../kernel/world_engine/run_presence_pulse_for_entities.ts";
import { buildWorldProjection } from "../kernel/projections/world_projection.ts";
import { buildEntityProjection } from "../kernel/projections/entity_projection.ts";
import { buildWorldRenderHints } from "../vme/world_meaning_projection.ts";
import { replayWorld } from "../kernel/replay/historical_replay.ts";

const TS = "2026-05-09T10:00:00.000Z";
const TS2 = "2026-05-09T10:01:00.000Z";

describe("Deterministische Weltbewegung 2 — Multi-Entity", () => {
  it("1. seedCanonicalEntities erzeugt entity_count 6 in der WorldProjection", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const wp = buildWorldProjection(store.getAll());
    assert.equal(wp.entity_count, 6);
  });

  it("2. alle 6 kanonischen IDs sind in worldProjection.entities vorhanden", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const wp = buildWorldProjection(store.getAll());
    for (const id of CANONICAL_ENTITY_IDS) {
      assert.ok(id in wp.entities, `Entität ${id} fehlt`);
    }
  });

  it("3. runWorldTickOnce erzeugt ein event_type system.tick", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(tick.event_type, "system.tick");
  });

  it("4. runPresencePulseForExistingEntities gibt genau 6 Events zurück", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const stored = runPresencePulseForExistingEntities(store, tick, {
      timestamp: TS,
    });
    assert.equal(stored.length, 6);
  });

  it("5. jedes zurückgegebene Pulse-Event hat event_type entity.state_changed", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const stored = runPresencePulseForExistingEntities(store, tick, {
      timestamp: TS,
    });
    for (const event of stored) {
      assert.equal(event.event_type, "entity.state_changed");
    }
  });

  it("6. nach dem ersten Puls hat jede Entität presence_pulse_count === 1", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const events = store.getAll();
    for (const id of CANONICAL_ENTITY_IDS) {
      const proj = buildEntityProjection(id, events);
      assert.equal(proj.current_state.presence_pulse_count, 1);
    }
  });

  it("7. Pulse-Event-IDs folgen dem Muster evt-pulse-tick1-{entityId}", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const stored = runPresencePulseForExistingEntities(store, tick, {
      timestamp: TS,
    });
    const storedIds = stored.map((e) => e.event_id).sort();
    const expectedIds = CANONICAL_ENTITY_IDS.map(
      (id) => `evt-pulse-tick1-${id}`
    ).sort();
    assert.deepEqual(storedIds, expectedIds);
  });

  it("8. jedes Pulse-Event hat causal_links auf den auslösenden Tick", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const stored = runPresencePulseForExistingEntities(store, tick, {
      timestamp: TS,
    });
    for (const event of stored) {
      assert.deepEqual(event.causal_links, ["evt-tick-1"]);
    }
  });

  it("9. nach zwei Ticks und zwei Pulsen hat jede Entität presence_pulse_count === 2", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick1 = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick1, { timestamp: TS });
    const tick2 = runWorldTickOnce(store, {
      event_id: "evt-tick-2",
      tick_number: 2,
      timestamp: TS2,
      world_time: TS2,
    });
    runPresencePulseForExistingEntities(store, tick2, { timestamp: TS2 });
    const events = store.getAll();
    for (const id of CANONICAL_ENTITY_IDS) {
      const proj = buildEntityProjection(id, events);
      assert.equal(proj.current_state.presence_pulse_count, 2);
    }
  });

  it("10. entity_count bleibt 6 nach zwei Ticks und zwei Pulsen", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick1 = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick1, { timestamp: TS });
    const tick2 = runWorldTickOnce(store, {
      event_id: "evt-tick-2",
      tick_number: 2,
      timestamp: TS2,
      world_time: TS2,
    });
    runPresencePulseForExistingEntities(store, tick2, { timestamp: TS2 });
    const wp = buildWorldProjection(store.getAll());
    assert.equal(wp.entity_count, 6);
  });

  it("11. kein Phantom-Puls: genau 6 entity.state_changed nach einem Puls-Zyklus", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const stateChangedCount = store
      .getAll()
      .filter((e) => e.event_type === "entity.state_changed").length;
    assert.equal(stateChangedCount, 6);
  });

  it("12. buildWorldRenderHints gibt ein Array mit 6 RenderHints zurück", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const events = store.getAll();
    const wp = buildWorldProjection(events);
    const hints = buildWorldRenderHints(wp, events);
    assert.equal(hints.length, 6);
  });

  it("13. jedes RenderHint nach dem Puls enthält 'Weltpuls' in der Erklärung", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const events = store.getAll();
    const wp = buildWorldProjection(events);
    const hints = buildWorldRenderHints(wp, events);
    for (const hint of hints) {
      assert.ok(
        hint.explanation.includes("Weltpuls"),
        `Fehlende Weltpuls-Referenz: "${hint.explanation}"`
      );
    }
  });

  it("14. replayWorld ohne upToIndex liefert dieselbe entity_count wie die Live-Projektion", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const events = store.getAll();
    const live = buildWorldProjection(events);
    const { worldProjection } = replayWorld(events);
    assert.equal(worldProjection.entity_count, live.entity_count);
  });

  it("15. replayWorld bis vor dem ersten Puls zeigt presence_pulse_count 0 für alle Entitäten", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const events = store.getAll();
    // 6 seed events (0-5) + 1 tick (index 6) → replay up to index 6 = before any pulses
    const tickIndex = events.findIndex((e) => e.event_type === "system.tick");
    const { worldProjection } = replayWorld(events, tickIndex);
    assert.equal(worldProjection.entity_count, 6);
    for (const proj of Object.values(worldProjection.entities)) {
      const count = proj.current_state.presence_pulse_count;
      assert.ok(
        count === undefined || count === 0,
        `Erwartete 0 oder undefined, bekam ${count} für ${proj.entity_id}`
      );
    }
  });

  it("16. replayWorld hängt keine neuen Events an den Store an (rein lesend)", () => {
    const store = new InMemoryEventStore();
    seedCanonicalEntities(store, TS);
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-1",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runPresencePulseForExistingEntities(store, tick, { timestamp: TS });
    const countBefore = store.getAll().length;
    replayWorld(store.getAll());
    const countAfter = store.getAll().length;
    assert.equal(countAfter, countBefore);
  });
});
