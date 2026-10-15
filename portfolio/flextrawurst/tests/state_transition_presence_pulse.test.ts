import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import { runWorldTickOnce } from "../kernel/world_engine/run_tick_once.ts";
import { applyPresencePulse } from "../kernel/world_engine/state_transitions/presence_pulse.ts";
import { runStateTransitionOnce } from "../kernel/world_engine/run_state_transition_once.ts";
import { buildEntityProjection } from "../kernel/projections/entity_projection.ts";
import { buildRenderHints } from "../vme/meaning_projection.ts";
import { replay } from "../kernel/replay/historical_replay.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";

const TS = "2026-05-09T10:00:00.000Z";
const TS2 = "2026-05-09T10:01:00.000Z";
const ENTITY = "Schorschel";

function seedEvent(): FlextrawurstEvent {
  return {
    event_id: "evt-seed-001",
    event_type: "system.seed_entity",
    actor_type: "world_engine",
    actor_id: "world_engine",
    target_type: null,
    target_id: null,
    timestamp: TS,
    payload: { entity_id: ENTITY, initial_state: { awake: true } },
    kontext: null,
    causal_links: [],
    origin_type: "manual_seed",
    created_by_process: "seed_script",
    visibility_layer: "system",
    projection_policy: null,
  };
}

function storeWithSeedAndTick() {
  const store = new InMemoryEventStore();
  store.append(seedEvent());
  const tick = runWorldTickOnce(store, {
    event_id: "evt-tick-001",
    tick_number: 1,
    timestamp: TS,
    world_time: TS,
  });
  return { store, tick };
}

describe("State-Transition — presence_pulse — erster Weltpuls-Abdruck", () => {
  it("1. applyPresencePulse erzeugt entity.state_changed aus gültigem system.tick", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    assert.ok(event !== null);
    assert.equal(event!.event_type, "entity.state_changed");
  });

  it("2. erzeugtes Event hat causal_links auf tick.event_id", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    assert.ok(event !== null);
    assert.deepEqual(event!.causal_links, ["evt-tick-001"]);
  });

  it("3. erzeugtes Event hat actor_type world_engine", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    assert.equal(event!.actor_type, "world_engine");
  });

  it("4. erzeugtes Event hat target_type nameless_ai", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    assert.equal(event!.target_type, "nameless_ai");
    assert.equal(event!.target_id, ENTITY);
  });

  it("5. state_patch enthält last_tick_number aus Tick-Payload", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    const patch = (event!.payload as any).state_patch;
    assert.equal(patch.last_tick_number, 1);
  });

  it("6. state_patch enthält last_world_time aus Tick-Payload", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    const patch = (event!.payload as any).state_patch;
    assert.equal(patch.last_world_time, TS);
  });

  it("7. presence_pulse_count startet bei 1", () => {
    const { store, tick } = storeWithSeedAndTick();
    const proj = buildEntityProjection(ENTITY, store.getAll());
    const event = applyPresencePulse(tick, proj, {
      event_id: "evt-pulse-001",
      timestamp: TS,
    });
    const patch = (event!.payload as any).state_patch;
    assert.equal(patch.presence_pulse_count, 1);
  });

  it("8. zweiter Tick erhöht presence_pulse_count deterministisch auf 2", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());

    const tick1 = runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runStateTransitionOnce(store, tick1, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    const tick2 = runWorldTickOnce(store, {
      event_id: "evt-tick-002",
      tick_number: 2,
      timestamp: TS2,
      world_time: TS2,
    });
    const pulse2 = runStateTransitionOnce(store, tick2, {
      event_id: "evt-pulse-002",
      entityId: ENTITY,
      timestamp: TS2,
    });

    assert.ok(pulse2 !== null);
    const patch = (pulse2!.payload as any).state_patch;
    assert.equal(patch.presence_pulse_count, 2);
    assert.equal(patch.last_tick_number, 2);
  });

  it("9. Rule gibt null zurück, wenn Ziel-Entität nicht existiert", () => {
    const store = new InMemoryEventStore();
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    const result = runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });
    assert.equal(result, null);
    // Kein Event geschrieben außer dem Tick
    assert.equal(store.length, 1);
  });

  it("10. runStateTransitionOnce speichert nur über store.append", () => {
    const { store, tick } = storeWithSeedAndTick();
    const lenBefore = store.length;

    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    assert.equal(store.length, lenBefore + 1);
    assert.ok(store.has("evt-pulse-001"));

    // Kein delete, kein update
    assert.equal(typeof (store as any).delete, "undefined");
    assert.equal(typeof (store as any).update, "undefined");
  });

  it("11. Projection enthält nach Transition den neuen State", () => {
    const { store, tick } = storeWithSeedAndTick();
    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    const proj = buildEntityProjection(ENTITY, store.getAll());
    assert.equal(proj.exists, true);
    assert.equal(proj.current_state.last_tick_number, 1);
    assert.equal(proj.current_state.last_world_time, TS);
    assert.equal(proj.current_state.presence_pulse_count, 1);
    assert.equal(proj.last_event_id, "evt-pulse-001");
  });

  it("12. Meaning Projection nutzt den neuen State für explanation und source_event_ids", () => {
    const { store, tick } = storeWithSeedAndTick();
    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    const proj = buildEntityProjection(ENTITY, store.getAll());
    const hints = buildRenderHints(proj, store.getAll());

    assert.ok(
      hints.explanation.includes("Weltpuls") || hints.explanation.includes("Puls"),
      `explanation sollte Weltpuls enthalten, war: "${hints.explanation}"`
    );
    assert.ok(hints.source_event_ids.includes("evt-pulse-001"));
    assert.ok(hints.source_event_ids.length > 0);
  });

  it("13. Historical Replay reproduziert dieselbe Projection und dieselben RenderHints", () => {
    const { store, tick } = storeWithSeedAndTick();
    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    const events = store.getAll();
    const upTo = events.length - 1;

    const r1 = replay(events, ENTITY, upTo);
    const r2 = replay(events, ENTITY, upTo);

    assert.deepEqual(r1.projection, r2.projection);
    assert.deepEqual(r1.renderHints, r2.renderHints);
    assert.equal(r1.projection.current_state.presence_pulse_count, 1);
  });

  it("14. Replay erzeugt keine zusätzliche Transition", () => {
    const { store, tick } = storeWithSeedAndTick();
    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    const lenBefore = store.length;
    const events = store.getAll();
    replay(events, ENTITY, events.length - 1);

    assert.equal(store.length, lenBefore);

    const pulseEvents = store
      .getAll()
      .filter((e) => e.event_type === "entity.state_changed");
    assert.equal(pulseEvents.length, 1);
  });

  it("15. Vollständige Kette: Seed → Tick → Presence Pulse → Projection → Replay deterministisch", () => {
    const store = new InMemoryEventStore();
    store.append(seedEvent());
    const tick = runWorldTickOnce(store, {
      event_id: "evt-tick-001",
      tick_number: 1,
      timestamp: TS,
      world_time: TS,
    });
    runStateTransitionOnce(store, tick, {
      event_id: "evt-pulse-001",
      entityId: ENTITY,
      timestamp: TS,
    });

    assert.equal(store.length, 3);

    const events = store.getAll();
    const r1 = replay(events, ENTITY, events.length - 1);
    const r2 = replay(events, ENTITY, events.length - 1);

    assert.deepEqual(r1.projection, r2.projection);
    assert.deepEqual(r1.renderHints, r2.renderHints);
    assert.equal(r1.projection.exists, true);
    assert.equal(r1.projection.current_state.presence_pulse_count, 1);
    assert.equal(r1.renderHints.node_opacity, 1.0);
    assert.ok(r1.renderHints.source_event_ids.includes("evt-pulse-001"));
    assert.ok(r1.renderHints.explanation.includes("Weltpuls"));
  });
});
