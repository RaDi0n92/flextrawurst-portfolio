import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import { createWorldTick } from "../kernel/world_engine/create_tick.ts";
import { runWorldTickOnce } from "../kernel/world_engine/run_tick_once.ts";
import { replay } from "../kernel/replay/historical_replay.ts";
import { validateEvent } from "../kernel/events/validate.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";

const TS = "2026-05-09T10:00:00.000Z";

function seedEvent(): FlextrawurstEvent {
  return {
    event_id: "evt-seed-001",
    event_type: "system.seed_entity",
    actor_type: "world_engine",
    actor_id: "world_engine",
    target_type: null,
    target_id: null,
    timestamp: TS,
    payload: { entity_id: "Schorschel", initial_state: { awake: true } },
    kontext: null,
    causal_links: [],
    origin_type: "manual_seed",
    created_by_process: "seed_script",
    visibility_layer: "system",
    projection_policy: null,
  };
}

describe("World-Engine-Tick — erster kontrollierter Weltpuls", () => {
  it("1. createWorldTick erzeugt ein gültiges system.tick Event", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const store = new InMemoryEventStore();
    assert.doesNotThrow(() => validateEvent(event, new Set()));
    assert.equal(event.event_type, "system.tick");
    assert.equal(event.event_id, "evt-tick-001");
  });

  it("2. runWorldTickOnce schreibt genau ein system.tick Event in den InMemoryEventStore", () => {
    const store = new InMemoryEventStore();
    runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(store.length, 1);
    assert.ok(store.has("evt-tick-001"));
  });

  it("3. Tick hat actor_type world_engine", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(event.actor_type, "world_engine");
  });

  it("4. Tick hat actor_id world_engine", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(event.actor_id, "world_engine");
  });

  it("5. Tick hat origin_type live_world", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(event.origin_type, "live_world");
  });

  it("6. tick_number landet im payload", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 42,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(event.payload.tick_number, 42);
  });

  it("7. world_time landet im payload", () => {
    const event = createWorldTick({
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    assert.equal(event.payload.world_time, TS);
  });

  it("8. Ungültiger Tick mit actor_type human wird abgelehnt", () => {
    const store = new InMemoryEventStore();
    assert.throws(
      () => {
        store.append({
          event_id: "evt-tick-bad",
          event_type: "system.tick",
          actor_type: "human",
          actor_id: "daniel",
          target_type: null,
          target_id: null,
          timestamp: TS,
          payload: { tick_number: 1, tick_reason: "manual_test", world_time: TS },
          kontext: null,
          causal_links: [],
          origin_type: "live_world",
          created_by_process: "world_engine_tick",
          visibility_layer: "system",
          projection_policy: null,
        });
      },
      /actor_type/
    );
    assert.equal(store.length, 0);
  });

  it("9. Replay erzeugt nach Tick keinen neuen Tick und verändert den Store nicht", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });

    const lengthBefore = store.length;
    const events = store.getAll();
    replay(events, "Schorschel", events.length - 1);

    assert.equal(store.length, lengthBefore);

    const ticks = store.getAll().filter((e) => e.event_type === "system.tick");
    assert.equal(ticks.length, 1);
  });

  it("10. Mehrere manuelle Ticks bleiben append-only und geordnet", () => {
    const store = new InMemoryEventStore();
    runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runWorldTickOnce(store, {
      event_id: "evt-tick-002",
      tick_number: 2,
      timestamp: TS,
      world_time: TS,
    });
    runWorldTickOnce(store, {
      event_id: "evt-tick-003",
      tick_number: 3,
      timestamp: TS,
      world_time: TS,
    });

    assert.equal(store.length, 3);

    const events = store.getAll();
    assert.equal(events[0].payload.tick_number, 1);
    assert.equal(events[1].payload.tick_number, 2);
    assert.equal(events[2].payload.tick_number, 3);

    // Append-only: zurückgegebenes Array ist eingefroren
    assert.throws(() => {
      (events as any[]).push({});
    });
  });
});
