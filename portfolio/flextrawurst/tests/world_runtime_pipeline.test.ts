import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  CANONICAL_ENTITY_IDS,
  seedCanonicalEntities,
} from "../kernel/entities/seed_entities.ts";
import { buildEntityProjection } from "../kernel/projections/entity_projection.ts";
import { buildWorldSnapshot } from "../kernel/snapshots/world_snapshot.ts";
import { runWorldCycle } from "../kernel/world_engine/run_world_cycle.ts";
import { runWorldCycles } from "../kernel/world_engine/run_world_cycles.ts";
import { buildWorldReplayFrames } from "../kernel/replay/world_replay_frames.ts";

const SEED_TS = "2026-05-09T10:00:00.000Z";
const TS1 = "2026-05-09T10:01:00.000Z";
const TS2 = "2026-05-09T10:02:00.000Z";
const TS3 = "2026-05-09T10:03:00.000Z";

const THREE_CYCLES = [
  {
    tick_event_id: "evt-cycle-tick-1",
    tick_number: 1,
    timestamp: TS1,
    world_time: TS1,
    transition_event_id_prefix: "evt-cycle-pulse-tick1",
  },
  {
    tick_event_id: "evt-cycle-tick-2",
    tick_number: 2,
    timestamp: TS2,
    world_time: TS2,
    transition_event_id_prefix: "evt-cycle-pulse-tick2",
  },
  {
    tick_event_id: "evt-cycle-tick-3",
    tick_number: 3,
    timestamp: TS3,
    world_time: TS3,
    transition_event_id_prefix: "evt-cycle-pulse-tick3",
  },
];

function makeSeededStore(): InMemoryEventStore {
  const store = new InMemoryEventStore();
  seedCanonicalEntities(store, SEED_TS);
  return store;
}

describe("World Runtime Pipeline", () => {
  it("1. seedCanonicalEntities erzeugt sechs Entitäten im Store", () => {
    const store = makeSeededStore();
    assert.equal(store.getAll().length, 6);
    const seedEvents = store
      .getAll()
      .filter((e) => e.event_type === "system.seed_entity");
    assert.equal(seedEvents.length, 6);
  });

  it("2. runWorldCycle erzeugt einen Tick und sechs Transitions im Store", () => {
    const store = makeSeededStore();
    runWorldCycle(store, THREE_CYCLES[0]);
    const events = store.getAll();
    const tickCount = events.filter((e) => e.event_type === "system.tick").length;
    const transitionCount = events.filter(
      (e) => e.event_type === "entity.state_changed"
    ).length;
    assert.equal(tickCount, 1);
    assert.equal(transitionCount, 6);
  });

  it("3. runWorldCycle gibt Snapshot mit tick_count 1 und transition_count 6 zurück", () => {
    const store = makeSeededStore();
    const snapshot = runWorldCycle(store, THREE_CYCLES[0]);
    assert.equal(snapshot.tick_count, 1);
    assert.equal(snapshot.transition_count, 6);
  });

  it("4. runWorldCycles führt drei deterministische Cycles aus", () => {
    const store = makeSeededStore();
    const snapshots = runWorldCycles(store, THREE_CYCLES);
    assert.equal(snapshots.length, 3);
  });

  it("5. EventStore enthält nach 3 Cycles exakt 27 Events", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    assert.equal(store.getAll().length, 27);
  });

  it("6. exakt 3 system.tick Events existieren nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const tickCount = store
      .getAll()
      .filter((e) => e.event_type === "system.tick").length;
    assert.equal(tickCount, 3);
  });

  it("7. exakt 18 entity.state_changed Events existieren nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const transitionCount = store
      .getAll()
      .filter((e) => e.event_type === "entity.state_changed").length;
    assert.equal(transitionCount, 18);
  });

  it("8. jede Entität hat presence_pulse_count 3 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const events = store.getAll();
    for (const id of CANONICAL_ENTITY_IDS) {
      const proj = buildEntityProjection(id, events);
      assert.equal(
        proj.current_state.presence_pulse_count,
        3,
        `presence_pulse_count falsch für ${id}`
      );
    }
  });

  it("9. jede Entität hat last_tick_number 3 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const events = store.getAll();
    for (const id of CANONICAL_ENTITY_IDS) {
      const proj = buildEntityProjection(id, events);
      assert.equal(
        proj.current_state.last_tick_number,
        3,
        `last_tick_number falsch für ${id}`
      );
    }
  });

  it("10. jede Entität hat isolierten last_event_id nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const events = store.getAll();
    const lastEventIds = new Set<string>();
    for (const id of CANONICAL_ENTITY_IDS) {
      const proj = buildEntityProjection(id, events);
      assert.ok(
        proj.last_event_id !== null,
        `last_event_id ist null für ${id}`
      );
      assert.ok(
        !lastEventIds.has(proj.last_event_id!),
        `last_event_id nicht eindeutig: ${proj.last_event_id}`
      );
      lastEventIds.add(proj.last_event_id!);
      assert.equal(
        proj.last_event_id,
        `evt-cycle-pulse-tick3-${id}`,
        `last_event_id hat falsches Muster für ${id}`
      );
    }
  });

  it("11. WorldSnapshot meldet entity_count 6 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.entity_count, 6);
  });

  it("12. WorldSnapshot meldet tick_count 3 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.tick_count, 3);
  });

  it("13. WorldSnapshot meldet transition_count 18 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.transition_count, 18);
  });

  it("14. WorldSnapshot enthält 6 RenderHints", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.render_hints.length, 6);
  });

  it("15. WorldRenderHints erklären Weltpuls #3 für alle Entitäten", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    for (const hint of snapshot.render_hints) {
      assert.ok(
        hint.explanation.includes("Weltpuls #3"),
        `Fehlende Weltpuls-#3-Referenz in: "${hint.explanation}"`
      );
    }
  });

  it("16. buildWorldReplayFrames erzeugt exakt 3 deterministische Frames", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const frames = buildWorldReplayFrames(store.getAll());
    assert.equal(frames.length, 3);
    for (let i = 0; i < 3; i++) {
      assert.equal(frames[i].frame_index, i);
    }
  });

  it("17. ReplayFrame 0 zeigt presence_pulse_count 1, Frame 2 zeigt 3", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const frames = buildWorldReplayFrames(store.getAll());
    for (const id of CANONICAL_ENTITY_IDS) {
      const frame0Proj = frames[0].snapshot.entities[id];
      assert.equal(
        frame0Proj.current_state.presence_pulse_count,
        1,
        `Frame 0: presence_pulse_count falsch für ${id}`
      );
      const frame2Proj = frames[2].snapshot.entities[id];
      assert.equal(
        frame2Proj.current_state.presence_pulse_count,
        3,
        `Frame 2: presence_pulse_count falsch für ${id}`
      );
    }
  });

  it("18. letzter ReplayFrame ergibt denselben Snapshot wie Live-Run", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const events = store.getAll();
    const liveSnapshot = buildWorldSnapshot(events);
    const frames = buildWorldReplayFrames(events);
    const lastFrame = frames[frames.length - 1];

    assert.equal(lastFrame.snapshot.event_count, liveSnapshot.event_count);
    assert.equal(lastFrame.snapshot.tick_count, liveSnapshot.tick_count);
    assert.equal(lastFrame.snapshot.transition_count, liveSnapshot.transition_count);
    assert.equal(lastFrame.snapshot.entity_count, liveSnapshot.entity_count);
    assert.equal(lastFrame.snapshot.latest_tick_number, liveSnapshot.latest_tick_number);
    assert.equal(lastFrame.snapshot.last_event_id, liveSnapshot.last_event_id);
  });

  it("19. buildWorldReplayFrames erzeugt keine neuen Events im Store", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const countBefore = store.getAll().length;
    buildWorldReplayFrames(store.getAll());
    const countAfter = store.getAll().length;
    assert.equal(countAfter, countBefore);
  });

  it("20. runWorldCycle erzeugt keine Transitions wenn keine Entitäten existieren", () => {
    const store = new InMemoryEventStore();
    const snapshot = runWorldCycle(store, THREE_CYCLES[0]);
    const events = store.getAll();
    const tickCount = events.filter((e) => e.event_type === "system.tick").length;
    const transitionCount = events.filter(
      (e) => e.event_type === "entity.state_changed"
    ).length;
    assert.equal(tickCount, 1);
    assert.equal(transitionCount, 0);
    assert.equal(snapshot.transition_count, 0);
    assert.equal(snapshot.entity_count, 0);
  });

  it("21. WorldSnapshot.latest_tick_number ist 3 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.latest_tick_number, 3);
  });

  it("22. WorldSnapshot.event_count ist 27 nach 3 Cycles", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const snapshot = buildWorldSnapshot(store.getAll());
    assert.equal(snapshot.event_count, 27);
  });

  it("23. source und redaction_state bleiben verboten im EventStore", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const events = store.getAll();
    for (const event of events) {
      assert.ok(!("source" in event), `Verbotenes Feld 'source' in ${event.event_id}`);
      assert.ok(
        !("redaction_state" in event),
        `Verbotenes Feld 'redaction_state' in ${event.event_id}`
      );
    }
  });

  it("24. ReplayFrame-Snapshots haben korrekte tick_count-Progression 1 → 2 → 3", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const frames = buildWorldReplayFrames(store.getAll());
    assert.equal(frames[0].snapshot.tick_count, 1);
    assert.equal(frames[1].snapshot.tick_count, 2);
    assert.equal(frames[2].snapshot.tick_count, 3);
  });

  it("25. ReplayFrame-Snapshots haben korrekte transition_count-Progression 6 → 12 → 18", () => {
    const store = makeSeededStore();
    runWorldCycles(store, THREE_CYCLES);
    const frames = buildWorldReplayFrames(store.getAll());
    assert.equal(frames[0].snapshot.transition_count, 6);
    assert.equal(frames[1].snapshot.transition_count, 12);
    assert.equal(frames[2].snapshot.transition_count, 18);
  });
});
