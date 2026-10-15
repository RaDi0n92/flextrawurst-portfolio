import { describe, it, before } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  createInitialSixSlotsThreeTickScenario,
} from "../kernel/scenario/world_scenario.ts";
import { runWorldScenario } from "../kernel/scenario/run_world_scenario.ts";
import type { WorldInspectionPack } from "../kernel/inspection/world_inspection_pack.ts";
import { buildInspectionSummary } from "../kernel/inspection/inspection_summary.ts";
import {
  buildWorldStateExport,
  serializeWorldStateExport,
} from "../kernel/export/world_state_export.ts";
import { buildWorldCameraNavigation } from "../kernel/world_camera/world_camera_navigation.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

let store: InMemoryEventStore;
let pack: WorldInspectionPack;

before(() => {
  store = new InMemoryEventStore();
  const scenario = createInitialSixSlotsThreeTickScenario();
  pack = runWorldScenario(store, scenario);
});

describe("Weltbetriebssystem Ring 2 — Scenario Inspection", () => {

  // --- Scenario ---

  it("1. createInitialSixSlotsThreeTickScenario erzeugt 6 Entitätsslots", () => {
    const scenario = createInitialSixSlotsThreeTickScenario();
    assert.equal(scenario.entity_ids.length, 6);
  });

  it("2. createInitialSixSlotsThreeTickScenario erzeugt 3 Cycles", () => {
    const scenario = createInitialSixSlotsThreeTickScenario();
    assert.equal(scenario.cycles.length, 3);
  });

  it("3. Scenario hat scenario_id initial_six_slots_three_ticks", () => {
    const scenario = createInitialSixSlotsThreeTickScenario();
    assert.equal(scenario.scenario_id, "initial_six_slots_three_ticks");
  });

  it("4. Scenario description enthält keine verbotene Sprache", () => {
    const scenario = createInitialSixSlotsThreeTickScenario();
    const report = checkConceptLanguage([
      { id: "label", text: scenario.label },
      { id: "description", text: scenario.description },
    ]);
    assert.equal(
      report.ok,
      true,
      `Verbotene Begriffe gefunden: ${report.violations.map((v) => v.term).join(", ")}`
    );
  });

  // --- InspectionPack Grundstruktur ---

  it("5. runWorldScenario erzeugt ein InspectionPack", () => {
    assert.ok(pack, "InspectionPack ist null oder undefined");
  });

  it("6. InspectionPack hat pack_version 1", () => {
    assert.equal(pack.pack_version, 1);
  });

  it("7. InspectionPack hat scenario_id initial_six_slots_three_ticks", () => {
    assert.equal(pack.scenario_id, "initial_six_slots_three_ticks");
  });

  it("8. InspectionPack hat ein label", () => {
    assert.ok(pack.label.length > 0);
  });

  // --- InspectionPack Zählungen ---

  it("9. InspectionPack enthält 27 Events", () => {
    assert.equal(pack.event_count, 27);
  });

  it("10. InspectionPack zählt 6 Entitätsslots", () => {
    assert.equal(pack.entity_slot_count, 6);
  });

  it("11. InspectionPack zählt 3 Ticks", () => {
    assert.equal(pack.tick_count, 3);
  });

  it("12. InspectionPack zählt 18 Spuren", () => {
    assert.equal(pack.trace_count, 18);
  });

  it("13. InspectionPack events-Array hat 27 Einträge", () => {
    assert.equal(pack.events.length, 27);
  });

  // --- Audit ---

  it("14. InspectionPack audit_ok ist true", () => {
    assert.equal(pack.audit_ok, true);
  });

  it("15. InspectionPack enthält WorldAudit", () => {
    assert.ok(pack.audit);
    assert.ok(pack.audit.integrity);
    assert.ok(pack.audit.timeline);
    assert.ok(pack.audit.snapshot);
    assert.ok(pack.audit.camera_model);
  });

  it("16. WorldAudit integrity.ok ist true", () => {
    assert.equal(pack.audit.integrity.ok, true);
  });

  it("17. WorldAudit snapshot zählt 27 Events", () => {
    assert.equal(pack.audit.snapshot.event_count, 27);
  });

  it("18. WorldAudit snapshot zählt 6 Entitäten", () => {
    assert.equal(pack.audit.snapshot.entity_count, 6);
  });

  // --- ReplayFrames ---

  it("19. InspectionPack enthält 3 ReplayFrames", () => {
    assert.equal(pack.replay_frames.length, 3);
  });

  it("20. ReplayFrame 0 hat frame_index 0", () => {
    assert.equal(pack.replay_frames[0].frame_index, 0);
  });

  it("21. ReplayFrame 2 hat frame_index 2", () => {
    assert.equal(pack.replay_frames[2].frame_index, 2);
  });

  it("22. Letzter ReplayFrame Snapshot last_event_id entspricht Audit-Snapshot last_event_id", () => {
    const lastFrame = pack.replay_frames[pack.replay_frames.length - 1];
    assert.equal(
      lastFrame.snapshot.last_event_id,
      pack.audit.snapshot.last_event_id
    );
  });

  it("23. Letzter ReplayFrame Snapshot event_count entspricht Audit-Snapshot event_count", () => {
    const lastFrame = pack.replay_frames[pack.replay_frames.length - 1];
    assert.equal(
      lastFrame.snapshot.event_count,
      pack.audit.snapshot.event_count
    );
  });

  // --- Notes ---

  it("24. InspectionPack notes enthält Slot-Schutzsatz", () => {
    const hasSlotNote = pack.notes.some((n) => n.includes("Slots bleiben Slots"));
    assert.equal(hasSlotNote, true);
  });

  it("25. InspectionPack notes enthält Keine-Beteiligung-Satz", () => {
    const hasNoInvolvementNote = pack.notes.some(
      (n) => n.includes("Keine UI") && n.includes("keine AI")
    );
    assert.equal(hasNoInvolvementNote, true);
  });

  // --- WorldStateExport ---

  it("26. buildWorldStateExport erzeugt export_version 1", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.export_version, 1);
  });

  it("27. WorldStateExport created_from ist in_memory_runtime", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.created_from, "in_memory_runtime");
  });

  it("28. WorldStateExport scenario_id stimmt überein", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.scenario_id, pack.scenario_id);
  });

  it("29. WorldStateExport enthält Integrity-Zusammenfassung", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.integrity.ok, true);
    assert.equal(exp.integrity.error_count, 0);
    assert.equal(typeof exp.integrity.warning_count, "number");
  });

  it("30. WorldStateExport enthält Timeline-Zusammenfassung", () => {
    const exp = buildWorldStateExport(pack);
    assert.ok(exp.timeline.last_event_id);
    assert.ok(exp.timeline.first_event_id);
    assert.equal(exp.timeline.tick_count, 3);
  });

  it("31. WorldStateExport counts.entity_slots ist 6", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.counts.entity_slots, 6);
  });

  it("32. WorldStateExport counts.ticks ist 3", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.counts.ticks, 3);
  });

  it("33. WorldStateExport counts.traces ist 18", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.counts.traces, 18);
  });

  it("34. WorldStateExport replay_frame_count ist 3", () => {
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.replay_frame_count, 3);
  });

  it("35. WorldStateExport camera_model enthält node_count > 0", () => {
    const exp = buildWorldStateExport(pack);
    assert.ok(exp.camera_model.node_count > 0);
  });

  it("36. serializeWorldStateExport ist deterministisch", () => {
    const s1 = serializeWorldStateExport(pack);
    const s2 = serializeWorldStateExport(pack);
    assert.equal(s1, s2);
  });

  it("37. serializeWorldStateExport gibt gültiges JSON zurück", () => {
    const s = serializeWorldStateExport(pack);
    assert.doesNotThrow(() => JSON.parse(s));
  });

  it("38. serialisiertes Export enthält export_version 1", () => {
    const parsed = JSON.parse(serializeWorldStateExport(pack));
    assert.equal(parsed.export_version, 1);
  });

  // --- Camera Navigation ---

  it("39. WorldCameraNavigation enthält entry_node_ids", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    assert.ok(Array.isArray(nav.entry_node_ids));
    assert.ok(nav.entry_node_ids.length > 0);
  });

  it("40. WorldCameraNavigation entry_node_ids zeigen auf entity_slot-Knoten", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const entityGroup = nav.focus_groups.find((g) => g.id === "entity_slots");
    assert.ok(entityGroup);
    for (const id of nav.entry_node_ids) {
      assert.ok(entityGroup.node_ids.includes(id));
    }
  });

  it("41. WorldCameraNavigation enthält FocusGroup entity_slots", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "entity_slots");
    assert.ok(group, "FocusGroup entity_slots fehlt");
    assert.equal(group.layer, 0);
  });

  it("42. FocusGroup entity_slots hat 6 Knoten", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "entity_slots");
    assert.ok(group);
    assert.equal(group.node_ids.length, 6);
  });

  it("43. WorldCameraNavigation enthält FocusGroup world_ticks", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "world_ticks");
    assert.ok(group, "FocusGroup world_ticks fehlt");
    assert.equal(group.layer, 1);
  });

  it("44. FocusGroup world_ticks hat 3 Knoten", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "world_ticks");
    assert.ok(group);
    assert.equal(group.node_ids.length, 3);
  });

  it("45. WorldCameraNavigation enthält FocusGroup presence_traces", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "presence_traces");
    assert.ok(group, "FocusGroup presence_traces fehlt");
    assert.equal(group.layer, 2);
  });

  it("46. FocusGroup presence_traces hat 18 Knoten", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "presence_traces");
    assert.ok(group);
    assert.equal(group.node_ids.length, 18);
  });

  it("47. WorldCameraNavigation enthält FocusGroup audit_layer", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const group = nav.focus_groups.find((g) => g.id === "audit_layer");
    assert.ok(group, "FocusGroup audit_layer fehlt");
    assert.equal(group.layer, 3);
  });

  it("48. WorldCameraNavigation enthält ZoomPath overview_to_entities", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const path = nav.zoom_paths.find((p) => p.id === "overview_to_entities");
    assert.ok(path, "ZoomPath overview_to_entities fehlt");
    assert.ok(path.node_ids.length > 0);
  });

  it("49. WorldCameraNavigation enthält ZoomPath overview_to_ticks", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const path = nav.zoom_paths.find((p) => p.id === "overview_to_ticks");
    assert.ok(path, "ZoomPath overview_to_ticks fehlt");
  });

  it("50. WorldCameraNavigation enthält ZoomPath tick_to_traces", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const path = nav.zoom_paths.find((p) => p.id === "tick_to_traces");
    assert.ok(path, "ZoomPath tick_to_traces fehlt");
    assert.ok(path.node_ids.length > 0);
  });

  it("51. WorldCameraNavigation enthält ZoomPath entity_to_trace_history", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const path = nav.zoom_paths.find((p) => p.id === "entity_to_trace_history");
    assert.ok(path, "ZoomPath entity_to_trace_history fehlt");
  });

  it("52. Alle ZoomPaths haben ein explanation-Feld", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    for (const path of nav.zoom_paths) {
      assert.ok(
        path.explanation.length > 0,
        `ZoomPath ${path.id} hat leere explanation`
      );
    }
  });

  // --- Concept Guard ---

  it("53. ConceptGuard akzeptiert erlaubte Slot-Sprache", () => {
    const report = checkConceptLanguage([
      { id: "t1", text: "kanonischer Entitätsslot" },
      { id: "t2", text: "Account-Entität registriert" },
      { id: "t3", text: "späterer möglicher Einzug" },
      { id: "t4", text: "Tragstruktur des Weltkerns" },
      { id: "t5", text: "Slot durchläuft Weltpuls" },
    ]);
    assert.equal(report.ok, true, `Unerwartete Verletzungen: ${JSON.stringify(report.violations)}`);
    assert.equal(report.violations.length, 0);
  });

  it("54. ConceptGuard erkennt 'Seed bedeutet Einzug'", () => {
    const report = checkConceptLanguage([
      { id: "bad1", text: "Seed bedeutet Einzug in die Welt" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some((v) => v.term === "Seed bedeutet Einzug");
    assert.equal(found, true);
  });

  it("55. ConceptGuard erkennt 'presence_pulse bedeutet Leben'", () => {
    const report = checkConceptLanguage([
      { id: "bad2", text: "presence_pulse bedeutet Leben im Weltkern" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some(
      (v) => v.term === "presence_pulse bedeutet Leben"
    );
    assert.equal(found, true);
  });

  it("56. ConceptGuard erkennt 'eingezogene Wesen'", () => {
    const report = checkConceptLanguage([
      { id: "bad3", text: "Die eingezogenen Wesen leben im System" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some((v) => v.term === "eingezogene Wesen");
    assert.equal(found, true);
  });

  it("57. ConceptGuard erkennt 'lebende Wesen'", () => {
    const report = checkConceptLanguage([
      { id: "bad4", text: "lebende Wesen im Ring" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some((v) => v.term === "lebende Wesen");
    assert.equal(found, true);
  });

  it("58. ConceptGuard erkennt 'Wesen leben'", () => {
    const report = checkConceptLanguage([
      { id: "bad5", text: "Wesen leben in Räumen" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some((v) => v.term === "Wesen leben");
    assert.equal(found, true);
  });

  it("59. ConceptGuard erkennt 'Bewohner eingezogen'", () => {
    const report = checkConceptLanguage([
      { id: "bad6", text: "Bewohner eingezogen nach Seed" },
    ]);
    assert.equal(report.ok, false);
    const found = report.violations.some((v) => v.term === "Bewohner eingezogen");
    assert.equal(found, true);
  });

  it("60. ConceptGuard meldet Verletzungs-ID korrekt", () => {
    const report = checkConceptLanguage([
      { id: "mein-doc", text: "Seed bedeutet Einzug" },
    ]);
    assert.equal(report.violations[0].id, "mein-doc");
  });

  it("61. ConceptGuard meldet message bei Verletzung", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Seed bedeutet Einzug" },
    ]);
    assert.ok(report.violations[0].message.length > 0);
  });

  it("62. ConceptGuard meldet ok true für leere Texte", () => {
    const report = checkConceptLanguage([]);
    assert.equal(report.ok, true);
    assert.equal(report.violations.length, 0);
  });

  // --- Inspection Summary ---

  it("63. InspectionSummary enthält '6 Entitätsslots'", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes("6 Entitätsslots"));
    assert.equal(found, true, `Summary-Zeilen: ${JSON.stringify(lines)}`);
  });

  it("64. InspectionSummary enthält '3 Ticks'", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes("3 Ticks"));
    assert.equal(found, true);
  });

  it("65. InspectionSummary enthält '18 Spuren'", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes("18 Spuren"));
    assert.equal(found, true);
  });

  it("66. InspectionSummary enthält scenario_id", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes(pack.scenario_id));
    assert.equal(found, true);
  });

  it("67. InspectionSummary erwähnt 'Integrity ok'", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes("Integrity ok"));
    assert.equal(found, true);
  });

  it("68. InspectionSummary erwähnt ReplayFrames", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some((l) => l.includes("ReplayFrames: 3"));
    assert.equal(found, true);
  });

  it("69. InspectionSummary bestätigt keine AI/UI/Postgres/Renderer-Beteiligung", () => {
    const lines = buildInspectionSummary(pack);
    const found = lines.some(
      (l) =>
        l.includes("Keine UI") &&
        l.includes("keine AI") &&
        l.includes("kein Renderer") &&
        l.includes("kein Postgres")
    );
    assert.equal(
      found,
      true,
      "Summary enthält keinen Satz über fehlende Beteiligung von UI/AI/Renderer/Postgres"
    );
  });

  it("70. InspectionSummary enthält mindestens 5 Zeilen", () => {
    const lines = buildInspectionSummary(pack);
    assert.ok(lines.length >= 5);
  });

  // --- EventStore-Unveränderlichkeit ---

  it("71. EventStore bleibt bei 27 Events nach buildWorldStateExport", () => {
    buildWorldStateExport(pack);
    assert.equal(store.length, 27);
  });

  it("72. EventStore bleibt bei 27 Events nach serializeWorldStateExport", () => {
    serializeWorldStateExport(pack);
    assert.equal(store.length, 27);
  });

  it("73. EventStore bleibt bei 27 Events nach buildWorldCameraNavigation", () => {
    buildWorldCameraNavigation(pack.audit.camera_model);
    assert.equal(store.length, 27);
  });

  it("74. EventStore bleibt bei 27 Events nach buildInspectionSummary", () => {
    buildInspectionSummary(pack);
    assert.equal(store.length, 27);
  });

  it("75. EventStore bleibt bei 27 Events nach checkConceptLanguage", () => {
    checkConceptLanguage([{ id: "test", text: "kanonischer Entitätsslot" }]);
    assert.equal(store.length, 27);
  });

  // --- Ring-Grenzen: keine verbotene Beteiligung ---

  it("76. InspectionPack events sind read-only (frozen)", () => {
    assert.throws(() => {
      (pack.events as FlextrawurstEvent[]).push(pack.events[0] as unknown as never);
    });
  });

  it("77. WorldStateExport enthält kein UI/Renderer/AI-Feld", () => {
    const exp = buildWorldStateExport(pack);
    const keys = Object.keys(exp);
    const forbidden = keys.filter((k) =>
      ["ui", "renderer", "ai", "postgres", "scheduler"].includes(k.toLowerCase())
    );
    assert.equal(forbidden.length, 0);
  });

  it("78. Scenario cycles sind deterministisch — zwei Aufrufe ergeben gleiche tick_event_ids", () => {
    const s1 = createInitialSixSlotsThreeTickScenario();
    const s2 = createInitialSixSlotsThreeTickScenario();
    for (let i = 0; i < s1.cycles.length; i++) {
      assert.equal(s1.cycles[i].tick_event_id, s2.cycles[i].tick_event_id);
    }
  });

  it("79. Scenario seed_timestamp ist deterministisch", () => {
    const s1 = createInitialSixSlotsThreeTickScenario();
    const s2 = createInitialSixSlotsThreeTickScenario();
    assert.equal(s1.seed_timestamp, s2.seed_timestamp);
  });

  it("80. WorldCameraNavigation tick_to_traces-ZoomPath enthält sowohl tick- als auch trace-IDs", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const tickGroup = nav.focus_groups.find((g) => g.id === "world_ticks")!;
    const traceGroup = nav.focus_groups.find((g) => g.id === "presence_traces")!;
    const tickToTraces = nav.zoom_paths.find((p) => p.id === "tick_to_traces")!;
    const containsTick = tickGroup.node_ids.some((id) =>
      tickToTraces.node_ids.includes(id)
    );
    const containsTrace = traceGroup.node_ids.some((id) =>
      tickToTraces.node_ids.includes(id)
    );
    assert.equal(containsTick, true, "tick_to_traces enthält keine Tick-IDs");
    assert.equal(containsTrace, true, "tick_to_traces enthält keine Trace-IDs");
  });
});

// Type-only import needed for test 76
import type { FlextrawurstEvent } from "../kernel/events/types.ts";
