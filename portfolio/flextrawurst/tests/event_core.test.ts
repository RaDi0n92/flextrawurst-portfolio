import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import { buildEntityProjection } from "../kernel/projections/entity_projection.ts";
import { replay } from "../kernel/replay/historical_replay.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";

const TS = new Date().toISOString();

function seedEvent(overrides: Partial<FlextrawurstEvent> = {}): FlextrawurstEvent {
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
    ...overrides,
  };
}

describe("Event Core — erster Weltbeweis", () => {
  it("1. Seed-Event für Schorschel wird akzeptiert", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    assert.equal(store.length, 1);
    assert.ok(store.has("evt-seed-001"));
  });

  it("2. system.tick wird akzeptiert", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    store.append({
      event_id: "evt-tick-001",
      event_type: "system.tick",
      actor_type: "world_engine",
      actor_id: "world_engine",
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
    assert.equal(store.length, 2);
  });

  it("3. entity.state_changed wird akzeptiert", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    store.append({
      event_id: "evt-state-001",
      event_type: "entity.state_changed",
      actor_type: "nameless_ai",
      actor_id: "Schorschel",
      target_type: null,
      target_id: null,
      timestamp: TS,
      payload: { state: { awake: true, state_level: 0.5 } },
      kontext: null,
      causal_links: ["evt-seed-001"],
      origin_type: "live_world",
      created_by_process: "entity_runner",
      visibility_layer: "public",
      projection_policy: null,
    });
    assert.equal(store.length, 2);
  });

  it("4. entity.post_stub wird akzeptiert", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    store.append({
      event_id: "evt-post-001",
      event_type: "entity.post_stub",
      actor_type: "nameless_ai",
      actor_id: "Schorschel",
      target_type: null,
      target_id: null,
      timestamp: TS,
      payload: { origin: "entity_runner", state_at_creation: { awake: true } },
      kontext: null,
      causal_links: ["evt-seed-001"],
      origin_type: "live_world",
      created_by_process: "entity_runner",
      visibility_layer: "public",
      projection_policy: null,
    });
    assert.equal(store.length, 2);
  });

  it("5. Unbekannter Eventtyp wird abgelehnt", () => {
    const store = new InMemoryEventStore();
    assert.throws(
      () => {
        store.append({
          event_id: "evt-bad-001",
          event_type: "wesen.post" as any,
          actor_type: "nameless_ai",
          actor_id: "Schorschel",
          target_type: null,
          target_id: null,
          timestamp: TS,
          payload: {},
          kontext: null,
          causal_links: [],
          origin_type: "live_world",
          created_by_process: null,
          visibility_layer: "public",
          projection_policy: null,
        });
      },
      /nicht erlaubt/
    );
    assert.equal(store.length, 0);
  });

  it('6. source-Feld wird abgelehnt', () => {
    const store = new InMemoryEventStore();
    assert.throws(
      () => store.append({ ...seedEvent(), source: "some_source" } as any),
      /source/
    );
    assert.equal(store.length, 0);
  });

  it('7. redaction_state-Feld wird abgelehnt', () => {
    const store = new InMemoryEventStore();
    assert.throws(
      () =>
        store.append({ ...seedEvent(), redaction_state: "tombstoned" } as any),
      /redaction_state/
    );
    assert.equal(store.length, 0);
  });

  it("8. EventStore bleibt append-only", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());

    // Zurückgegebenes Array ist eingefroren — push wirft
    const all = store.getAll();
    assert.throws(() => {
      (all as any[]).push({});
    });

    // Gespeichertes Event ist eingefroren — Mutation wirft
    const stored = store.getById("evt-seed-001")!;
    assert.throws(() => {
      (stored as any).event_type = "system.tick";
    });

    // Kein delete, kein update
    assert.equal(typeof (store as any).delete, "undefined");
    assert.equal(typeof (store as any).update, "undefined");

    assert.equal(store.length, 1);
  });

  it("9. EntityProjection baut Schorschel korrekt auf", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    store.append({
      event_id: "evt-state-001",
      event_type: "entity.state_changed",
      actor_type: "nameless_ai",
      actor_id: "Schorschel",
      target_type: null,
      target_id: null,
      timestamp: TS,
      payload: { state: { awake: true, state_level: 0.7 } },
      kontext: null,
      causal_links: ["evt-seed-001"],
      origin_type: "live_world",
      created_by_process: "entity_runner",
      visibility_layer: "public",
      projection_policy: null,
    });

    const proj = buildEntityProjection("Schorschel", store.getAll());
    assert.equal(proj.exists, true);
    assert.equal(proj.entity_id, "Schorschel");
    assert.equal(proj.current_state.awake, true);
    assert.equal(proj.current_state.state_level, 0.7);
    assert.equal(proj.last_event_id, "evt-state-001");
  });

  it("10. Historical Replay reproduziert Projektion und Render-Hints deterministisch", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    store.append({
      event_id: "evt-tick-001",
      event_type: "system.tick",
      actor_type: "world_engine",
      actor_id: "world_engine",
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
    store.append({
      event_id: "evt-state-001",
      event_type: "entity.state_changed",
      actor_type: "nameless_ai",
      actor_id: "Schorschel",
      target_type: null,
      target_id: null,
      timestamp: TS,
      payload: { state: { awake: true, state_level: 0.5 } },
      kontext: null,
      causal_links: ["evt-seed-001"],
      origin_type: "live_world",
      created_by_process: "entity_runner",
      visibility_layer: "public",
      projection_policy: null,
    });

    const events = store.getAll();
    const upTo = events.length - 1;

    const result1 = replay(events, "Schorschel", upTo);
    const result2 = replay(events, "Schorschel", upTo);

    // Deterministisch identisch
    assert.deepEqual(result1.projection, result2.projection);
    assert.deepEqual(result1.renderHints, result2.renderHints);

    // Korrekte Werte
    assert.equal(result1.projection.exists, true);
    assert.equal(result1.renderHints.node_opacity, 1.0);
    assert.equal(result1.renderHints.node_pulse_speed, "normal");
    assert.ok(result1.renderHints.source_event_ids.length > 0);

    // Replay mit upToIndex=0 → nur seed, keine state_changed
    const partial = replay(events, "Schorschel", 0);
    assert.equal(partial.projection.exists, true);
    assert.equal(partial.projection.current_state.state_level, undefined);
  });
});
