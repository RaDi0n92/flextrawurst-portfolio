import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  CANONICAL_ENTITY_IDS,
  seedCanonicalEntities,
} from "../kernel/entities/seed_entities.ts";
import { runWorldCycles } from "../kernel/world_engine/run_world_cycles.ts";
import { buildWorldSnapshot } from "../kernel/snapshots/world_snapshot.ts";
import { checkWorldIntegrity } from "../kernel/integrity/world_integrity.ts";
import { buildWorldTimeline } from "../kernel/timeline/world_timeline.ts";
import {
  findEventsByType,
  findEventsByTarget,
  findCausalChildren,
  findEntityTrace,
  findCausalParents,
} from "../kernel/queries/event_queries.ts";
import { buildWorldCameraModel } from "../kernel/world_camera/world_camera_model.ts";
import { buildWorldAudit } from "../kernel/audit/world_audit.ts";
import { buildWorldReplayFrames } from "../kernel/replay/world_replay_frames.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";

const SEED_TS = "2026-05-09T10:00:00.000Z";
const TS1 = "2026-05-09T10:01:00.000Z";
const TS2 = "2026-05-09T10:02:00.000Z";
const TS3 = "2026-05-09T10:03:00.000Z";

const THREE_CYCLES = [
  {
    tick_event_id: "evt-os-tick-1",
    tick_number: 1,
    timestamp: TS1,
    world_time: TS1,
    transition_event_id_prefix: "evt-os-pulse-tick1",
  },
  {
    tick_event_id: "evt-os-tick-2",
    tick_number: 2,
    timestamp: TS2,
    world_time: TS2,
    transition_event_id_prefix: "evt-os-pulse-tick2",
  },
  {
    tick_event_id: "evt-os-tick-3",
    tick_number: 3,
    timestamp: TS3,
    world_time: TS3,
    transition_event_id_prefix: "evt-os-pulse-tick3",
  },
];

function buildThreeCycleWorld(): { store: InMemoryEventStore; events: readonly FlextrawurstEvent[] } {
  const store = new InMemoryEventStore();
  seedCanonicalEntities(store, SEED_TS);
  runWorldCycles(store, THREE_CYCLES);
  return { store, events: store.getAll() };
}

describe("Weltbetriebssystem Ring 1", () => {
  it("1. Drei-Cycle-Welt mit sechs kanonischen Slots erzeugt 27 Events", () => {
    const { events } = buildThreeCycleWorld();
    assert.equal(events.length, 27);
  });

  it("2. checkWorldIntegrity meldet ok true für saubere Welt", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.ok, true, `Fehler: ${report.errors.join(", ")}`);
  });

  it("3. Integrity zählt 6 seed events", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.counts.seed_events, 6);
  });

  it("4. Integrity zählt 3 tick events", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.counts.tick_events, 3);
  });

  it("5. Integrity zählt 18 state_changed events", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.counts.state_changed_events, 18);
  });

  it("6. Integrity findet keine forbidden_fields in sauberer Welt", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.forbidden_fields_found.length, 0);
  });

  it("7. Integrity erkennt absichtlich eingefügtes source-Feld als Fehler", () => {
    const { events } = buildThreeCycleWorld();
    const fakeEvent = {
      ...events[0],
      event_id: "fake-with-source",
      source: "verboten",
    } as unknown as FlextrawurstEvent;
    const report = checkWorldIntegrity([...events, fakeEvent]);
    assert.ok(
      report.forbidden_fields_found.some((f) => f.startsWith("source")),
      "source-Feld nicht erkannt"
    );
    assert.equal(report.ok, false);
  });

  it("8. Integrity erkennt duplicate event_id als Fehler", () => {
    const { events } = buildThreeCycleWorld();
    const withDup = [...events, events[0]];
    const report = checkWorldIntegrity(withDup as readonly FlextrawurstEvent[]);
    assert.ok(report.duplicate_event_ids.length > 0, "Duplikat nicht erkannt");
    assert.equal(report.ok, false);
  });

  it("9. buildWorldTimeline erzeugt 27 TimelineFrames", () => {
    const { events } = buildThreeCycleWorld();
    const timeline = buildWorldTimeline(events);
    assert.equal(timeline.frames.length, 27);
  });

  it("10. Timeline enthält deutsche Summary für Seed", () => {
    const { events } = buildThreeCycleWorld();
    const timeline = buildWorldTimeline(events);
    const seedFrames = timeline.frames.filter((f) =>
      f.event_type === "system.seed_entity"
    );
    assert.equal(seedFrames.length, 6);
    for (const frame of seedFrames) {
      assert.ok(
        frame.summary.startsWith("Seed:") && frame.summary.includes("kanonischer"),
        `Unerwartete Summary: "${frame.summary}"`
      );
    }
  });

  it("11. Timeline enthält deutsche Summary für Tick", () => {
    const { events } = buildThreeCycleWorld();
    const timeline = buildWorldTimeline(events);
    const tickFrames = timeline.frames.filter((f) =>
      f.event_type === "system.tick"
    );
    assert.equal(tickFrames.length, 3);
    for (const frame of tickFrames) {
      assert.ok(
        frame.summary.includes("Tick") && frame.summary.includes("Weltpuls"),
        `Unerwartete Tick-Summary: "${frame.summary}"`
      );
    }
  });

  it("12. Timeline enthält deutsche Summary für presence_pulse-Spur", () => {
    const { events } = buildThreeCycleWorld();
    const timeline = buildWorldTimeline(events);
    const traceFrames = timeline.frames.filter((f) =>
      f.event_type === "entity.state_changed"
    );
    assert.equal(traceFrames.length, 18);
    for (const frame of traceFrames) {
      assert.ok(
        frame.summary.startsWith("Spur:") && frame.summary.includes("Weltpuls"),
        `Unerwartete Spur-Summary: "${frame.summary}"`
      );
    }
  });

  it("13. findEventsByType findet 3 system.tick", () => {
    const { events } = buildThreeCycleWorld();
    const ticks = findEventsByType(events, "system.tick");
    assert.equal(ticks.length, 3);
  });

  it("14. findEventsByTarget findet Seed und Spuren für Schorschel", () => {
    const { events } = buildThreeCycleWorld();
    const targeted = findEventsByTarget(events, "nameless_ai", "Schorschel");
    // 1 seed + 3 presence_pulses
    assert.equal(targeted.length, 4);
  });

  it("15. findCausalChildren findet sechs presence_pulse-Transitions für Tick #1", () => {
    const { events } = buildThreeCycleWorld();
    const children = findCausalChildren(events, "evt-os-tick-1");
    assert.equal(children.length, 6);
    for (const child of children) {
      assert.equal(child.event_type, "entity.state_changed");
    }
  });

  it("16. findEntityTrace enthält Seed und drei presence_pulse-Spuren für Schorschel", () => {
    const { events } = buildThreeCycleWorld();
    const trace = findEntityTrace(events, "Schorschel");
    // 1 seed (payload.entity_id) + 3 presence_pulses (target_id)
    assert.equal(trace.length, 4);
    const types = trace.map((e) => e.event_type);
    assert.ok(types.includes("system.seed_entity"), "Kein Seed in Trace");
    assert.equal(
      types.filter((t) => t === "entity.state_changed").length,
      3
    );
  });

  it("17. buildWorldCameraModel erzeugt 6 entity_slot nodes", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const entityNodes = model.nodes.filter((n) => n.type === "entity_slot");
    assert.equal(entityNodes.length, 6);
  });

  it("18. buildWorldCameraModel erzeugt 3 tick nodes", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const tickNodes = model.nodes.filter((n) => n.type === "tick");
    assert.equal(tickNodes.length, 3);
  });

  it("19. buildWorldCameraModel erzeugt 18 trace nodes", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const traceNodes = model.nodes.filter((n) => n.type === "trace");
    assert.equal(traceNodes.length, 18);
  });

  it("20. CameraModel erzeugt causal und runtime_trace edges", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const causalEdges = model.edges.filter((e) => e.type === "causal");
    const traceEdges = model.edges.filter((e) => e.type === "runtime_trace");
    assert.equal(causalEdges.length, 18, "Falsche Anzahl causal edges");
    assert.equal(traceEdges.length, 18, "Falsche Anzahl runtime_trace edges");
  });

  it("21. CameraModel enthält Layer 0–3", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const layerNumbers = model.layers.map((l) => l.layer).sort();
    assert.deepEqual(layerNumbers, [0, 1, 2, 3]);
  });

  it("22. CameraModel world_health ist ok für saubere Welt", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    assert.equal(model.world_health, "ok");
  });

  it("23. buildWorldAudit kombiniert integrity, timeline, snapshot und camera_model", () => {
    const { events } = buildThreeCycleWorld();
    const audit = buildWorldAudit(events);
    assert.ok(audit.integrity !== undefined, "integrity fehlt");
    assert.ok(audit.timeline !== undefined, "timeline fehlt");
    assert.ok(audit.snapshot !== undefined, "snapshot fehlt");
    assert.ok(audit.camera_model !== undefined, "camera_model fehlt");
  });

  it("24. WorldAudit snapshot entspricht live WorldSnapshot nach drei Cycles", () => {
    const { events } = buildThreeCycleWorld();
    const audit = buildWorldAudit(events);
    const live = buildWorldSnapshot(events);
    assert.equal(audit.snapshot.event_count, live.event_count);
    assert.equal(audit.snapshot.tick_count, live.tick_count);
    assert.equal(audit.snapshot.transition_count, live.transition_count);
    assert.equal(audit.snapshot.entity_count, live.entity_count);
    assert.equal(audit.snapshot.latest_tick_number, live.latest_tick_number);
  });

  it("25. WorldAudit verändert EventStore nicht", () => {
    const { store, events } = buildThreeCycleWorld();
    const countBefore = store.getAll().length;
    buildWorldAudit(events);
    const countAfter = store.getAll().length;
    assert.equal(countAfter, countBefore);
  });

  it("26. Historical Replay und ReplayFrames bleiben kompatibel nach Ring 1", () => {
    const { events } = buildThreeCycleWorld();
    const frames = buildWorldReplayFrames(events);
    assert.equal(frames.length, 3);
    assert.equal(frames[2].snapshot.tick_count, 3);
    assert.equal(frames[2].snapshot.transition_count, 18);
    assert.equal(frames[2].snapshot.entity_count, 6);
  });

  it("27. findCausalParents findet Tick für eine presence_pulse Transition", () => {
    const { events } = buildThreeCycleWorld();
    const firstTrace = events.find(
      (e) =>
        e.event_type === "entity.state_changed" &&
        e.actor_type === "world_engine"
    );
    assert.ok(firstTrace, "Keine Transition gefunden");
    const parents = findCausalParents(events, firstTrace!.event_id);
    assert.equal(parents.length, 1);
    assert.equal(parents[0].event_type, "system.tick");
  });

  it("28. Timeline frame_index ist konsekutiv 0..26", () => {
    const { events } = buildThreeCycleWorld();
    const timeline = buildWorldTimeline(events);
    for (let i = 0; i < timeline.frames.length; i++) {
      assert.equal(timeline.frames[i].index, i);
    }
  });

  it("29. CameraModel timeline_markers enthält 3 Einträge (einen pro Tick)", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    assert.equal(model.timeline_markers.length, 3);
  });

  it("30. Integrity meldet total_events 27 für Drei-Cycle-Welt", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.counts.total_events, 27);
  });

  it("31. Integrity meldet 0 unknown_events für Drei-Cycle-Welt", () => {
    const { events } = buildThreeCycleWorld();
    const report = checkWorldIntegrity(events);
    assert.equal(report.counts.unknown_events, 0);
  });

  it("32. CameraModel entity_slot nodes haben korrekte IDs für alle 6 kanonischen Entitäten", () => {
    const { events } = buildThreeCycleWorld();
    const snapshot = buildWorldSnapshot(events);
    const timeline = buildWorldTimeline(events);
    const integrity = checkWorldIntegrity(events);
    const model = buildWorldCameraModel(snapshot, timeline, integrity);
    const entityNodeIds = model.nodes
      .filter((n) => n.type === "entity_slot")
      .map((n) => n.id);
    for (const id of CANONICAL_ENTITY_IDS) {
      assert.ok(
        entityNodeIds.includes(`node-entity-${id}`),
        `Kein entity_slot node für ${id}`
      );
    }
  });

  it("33. WorldAudit camera_model world_health ist ok", () => {
    const { events } = buildThreeCycleWorld();
    const audit = buildWorldAudit(events);
    assert.equal(audit.camera_model.world_health, "ok");
  });
});
