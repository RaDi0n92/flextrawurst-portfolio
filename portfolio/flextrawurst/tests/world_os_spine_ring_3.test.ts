import { describe, it, before } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  createInitialSixSlotsThreeTickScenario,
} from "../kernel/scenario/world_scenario.ts";
import { runWorldScenario } from "../kernel/scenario/run_world_scenario.ts";
import type { WorldInspectionPack } from "../kernel/inspection/world_inspection_pack.ts";
import {
  buildCanonicalEntitySlots,
  buildSlotsFromScenarioPack,
} from "../kernel/slots/entity_slot.ts";
import {
  buildProvenanceForInspectionPack,
  buildProvenanceForSlots,
} from "../kernel/provenance/provenance_record.ts";
import {
  assessActivationReadiness,
  assessAllSlotsActivationReadiness,
} from "../kernel/activation/activation_readiness.ts";
import {
  assessCameraReadiness,
} from "../kernel/world_camera/camera_readiness.ts";
import { buildWorldCameraNavigation } from "../kernel/world_camera/world_camera_navigation.ts";
import { assessRuntimeReadiness } from "../kernel/runtime/runtime_readiness.ts";
import {
  buildWorldOSSpine,
} from "../kernel/os_spine/world_os_spine.ts";
import {
  buildWorldOSSpineExport,
  serializeWorldOSSpineExport,
} from "../kernel/os_spine/world_os_spine_export.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";
import {
  buildWorldStateExport,
  serializeWorldStateExport,
} from "../kernel/export/world_state_export.ts";

let store: InMemoryEventStore;
let pack: WorldInspectionPack;

before(() => {
  store = new InMemoryEventStore();
  const scenario = createInitialSixSlotsThreeTickScenario();
  pack = runWorldScenario(store, scenario);
});

describe("Weltbetriebssystem Ring 3 — World OS Spine", () => {

  // --- Ring-2-Baseline ---

  it("1. Ring-2 ScenarioPack kann erzeugt werden", () => {
    assert.ok(pack);
    assert.equal(pack.pack_version, 1);
  });

  it("2. Ring-2 pack enthält 27 Events", () => {
    assert.equal(pack.event_count, 27);
  });

  it("3. Ring-2 audit_ok ist true", () => {
    assert.equal(pack.audit_ok, true);
  });

  // --- Slot-Layer ---

  it("4. buildCanonicalEntitySlots erzeugt 6 Slots", () => {
    const slots = buildCanonicalEntitySlots();
    assert.equal(slots.length, 6);
  });

  it("5. buildCanonicalEntitySlots — alle Slots haben Status reserved", () => {
    const slots = buildCanonicalEntitySlots();
    for (const slot of slots) {
      assert.equal(slot.status, "reserved");
    }
  });

  it("6. buildCanonicalEntitySlots — kein Slot hat Status occupied", () => {
    const slots = buildCanonicalEntitySlots();
    const occupiedCount = slots.filter((s) => s.status === "occupied").length;
    assert.equal(occupiedCount, 0);
  });

  it("7. buildCanonicalEntitySlots — alle Slots sind canonical true", () => {
    const slots = buildCanonicalEntitySlots();
    for (const slot of slots) {
      assert.equal(slot.canonical, true);
    }
  });

  it("8. buildCanonicalEntitySlots — kein Slot hat occupant_id", () => {
    const slots = buildCanonicalEntitySlots();
    for (const slot of slots) {
      assert.equal(slot.occupant_id, null);
    }
  });

  it("9. buildSlotsFromScenarioPack erkennt 6 seeded Slots", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    assert.equal(slots.length, 6);
  });

  it("10. buildSlotsFromScenarioPack — alle Slots haben Status seeded", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    for (const slot of slots) {
      assert.equal(slot.status, "seeded", `Slot ${slot.slot_id} hat Status ${slot.status}`);
    }
  });

  it("11. buildSlotsFromScenarioPack — kein Slot hat Status occupied", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const occupiedCount = slots.filter((s) => s.status === "occupied").length;
    assert.equal(occupiedCount, 0);
  });

  it("12. buildSlotsFromScenarioPack — kein Slot hat occupant_id", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    for (const slot of slots) {
      assert.equal(slot.occupant_id, null);
    }
  });

  it("13. buildSlotsFromScenarioPack — alle Slots haben source canonical_seed", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    for (const slot of slots) {
      assert.equal(slot.source, "canonical_seed");
    }
  });

  // --- Provenienz-Layer ---

  it("14. buildProvenanceForInspectionPack erzeugt Records", () => {
    const records = buildProvenanceForInspectionPack(pack);
    assert.ok(records.length > 0);
  });

  it("15. Provenance enthält canonical_seed Records", () => {
    const records = buildProvenanceForInspectionPack(pack);
    const hasCanonicalSeed = records.some(
      (r) => r.provenance_type === "canonical_seed"
    );
    assert.equal(hasCanonicalSeed, true);
  });

  it("16. Provenance enthält runtime_generated Records", () => {
    const records = buildProvenanceForInspectionPack(pack);
    const hasRuntime = records.some(
      (r) => r.provenance_type === "runtime_generated"
    );
    assert.equal(hasRuntime, true);
  });

  it("17. Provenance enthält Record für InspectionPack selbst", () => {
    const records = buildProvenanceForInspectionPack(pack);
    const packRecord = records.find((r) => r.subject_type === "inspection_pack");
    assert.ok(packRecord, "Kein ProvenanceRecord für InspectionPack");
  });

  it("18. buildProvenanceForSlots erzeugt einen Record pro Slot", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const records = buildProvenanceForSlots(slots, pack);
    assert.equal(records.length, slots.length);
  });

  it("19. Slot-Provenance-Records sind alle canonical_seed", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const records = buildProvenanceForSlots(slots, pack);
    for (const r of records) {
      assert.equal(r.provenance_type, "canonical_seed");
    }
  });

  it("20. Slot-Provenance-Records haben confidence structural", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const records = buildProvenanceForSlots(slots, pack);
    for (const r of records) {
      assert.equal(r.confidence, "structural");
    }
  });

  it("21. Slot-Provenance-Records haben subject_type entity_slot", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const records = buildProvenanceForSlots(slots, pack);
    for (const r of records) {
      assert.equal(r.subject_type, "entity_slot");
    }
  });

  // --- Activation-Readiness-Layer ---

  it("22. assessAllSlotsActivationReadiness erzeugt Report für alle 6 Slots", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    assert.equal(reports.length, 6);
  });

  it("23. ActivationReadiness may_activate_now ist für alle Slots false", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.equal(
        r.may_activate_now,
        false,
        `Slot ${r.slot_id} hat may_activate_now true`
      );
    }
  });

  it("24. ActivationReadiness status ist not_ready für alle Slots", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.equal(r.status, "not_ready");
    }
  });

  it("25. ActivationReadiness nennt explicit_daniel_activation_approval als missing", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.ok(
        r.missing.includes("explicit_daniel_activation_approval"),
        `Slot ${r.slot_id} fehlt explicit_daniel_activation_approval in missing`
      );
    }
  });

  it("26. ActivationReadiness nennt memory_import als missing", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.ok(
        r.missing.includes("memory_import"),
        `Slot ${r.slot_id} fehlt memory_import in missing`
      );
    }
  });

  it("27. ActivationReadiness nennt resident_profile als missing", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.ok(r.missing.includes("resident_profile"));
    }
  });

  it("28. ActivationReadiness nennt no_occupancy_without_explicit_activation als Blocker", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const reports = assessAllSlotsActivationReadiness(slots, prov, pack);
    for (const r of reports) {
      assert.ok(
        r.blockers.includes("no_occupancy_without_explicit_activation"),
        `Slot ${r.slot_id} fehlt Blocker`
      );
    }
  });

  // --- Camera-Readiness-Layer ---

  it("29. CameraReadiness clickable ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.clickable, true);
  });

  it("30. CameraReadiness zoomable ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.zoomable, true);
  });

  it("31. CameraReadiness traceable ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.traceable, true);
  });

  it("32. CameraReadiness has_timeline ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.has_timeline, true);
  });

  it("33. CameraReadiness has_navigation_paths ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.has_navigation_paths, true);
  });

  it("34. CameraReadiness ok ist true", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.ok, true);
  });

  it("35. CameraReadiness missing ist leer für gültige Welt", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    assert.equal(report.missing.length, 0);
  });

  it("36. CameraReadiness notes enthalten 'Kein Renderer'", () => {
    const nav = buildWorldCameraNavigation(pack.audit.camera_model);
    const report = assessCameraReadiness(
      pack.audit.camera_model,
      nav,
      pack.audit.timeline
    );
    const hasRendererNote = report.notes.some((n) =>
      n.includes("Kein Renderer")
    );
    assert.equal(hasRendererNote, true);
  });

  // --- Runtime-Readiness-Layer ---

  it("37. RuntimeReadiness ok ist true", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.ok, true);
  });

  it("38. RuntimeReadiness deterministic ist true", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.deterministic, true);
  });

  it("39. RuntimeReadiness uses_ai ist false", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.uses_ai, false);
  });

  it("40. RuntimeReadiness uses_ui ist false", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.uses_ui, false);
  });

  it("41. RuntimeReadiness uses_postgres ist false", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.uses_postgres, false);
  });

  it("42. RuntimeReadiness uses_scheduler ist false", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.uses_scheduler, false);
  });

  it("43. RuntimeReadiness event_count ist 27", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.event_count, 27);
  });

  it("44. RuntimeReadiness tick_count ist 3", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.tick_count, 3);
  });

  it("45. RuntimeReadiness trace_count ist 18", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.trace_count, 18);
  });

  it("46. RuntimeReadiness replay_frame_count ist 3", () => {
    const report = assessRuntimeReadiness(pack);
    assert.equal(report.replay_frame_count, 3);
  });

  // --- World OS Spine ---

  it("47. buildWorldOSSpine erzeugt spine_version 1", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.spine_version, 1);
  });

  it("48. WorldOSSpine hat scenario_id", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.scenario_id, pack.scenario_id);
  });

  it("49. WorldOSSpine enthält 6 Slots", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.slots.length, 6);
  });

  it("50. WorldOSSpine enthält 0 occupied Slots", () => {
    const spine = buildWorldOSSpine(pack);
    const occupiedCount = spine.slots.filter((s) => s.status === "occupied").length;
    assert.equal(occupiedCount, 0);
  });

  it("51. WorldOSSpine enthält 6 ActivationReadiness-Reports", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.activation_readiness.length, 6);
  });

  it("52. WorldOSSpine — alle ActivationReadiness may_activate_now false", () => {
    const spine = buildWorldOSSpine(pack);
    for (const r of spine.activation_readiness) {
      assert.equal(r.may_activate_now, false);
    }
  });

  it("53. WorldOSSpine audit_ok ist true", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.audit_ok, true);
  });

  it("54. WorldOSSpine camera_readiness.ok ist true", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.camera_readiness.ok, true);
  });

  it("55. WorldOSSpine runtime_readiness.ok ist true", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.runtime_readiness.ok, true);
  });

  it("56. WorldOSSpine runtime_readiness.deterministic ist true", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(spine.runtime_readiness.deterministic, true);
  });

  it("57. WorldOSSpine summary enthält '0 Wesen eingezogen'", () => {
    const spine = buildWorldOSSpine(pack);
    const found = spine.summary.some((l) => l.includes("0 Wesen eingezogen"));
    assert.equal(
      found,
      true,
      `Summary enthält nicht '0 Wesen eingezogen': ${JSON.stringify(spine.summary)}`
    );
  });

  it("58. WorldOSSpine summary enthält 'Kein Einzug'", () => {
    const spine = buildWorldOSSpine(pack);
    const found = spine.summary.some((l) =>
      l.toLowerCase().includes("kein einzug")
    );
    assert.equal(
      found,
      true,
      `Summary enthält nicht 'Kein Einzug': ${JSON.stringify(spine.summary)}`
    );
  });

  it("59. WorldOSSpine summary enthält '6 kanonische Entitätsslots'", () => {
    const spine = buildWorldOSSpine(pack);
    const found = spine.summary.some((l) =>
      l.includes("6 kanonische Entitätsslots")
    );
    assert.equal(found, true);
  });

  it("60. WorldOSSpine summary enthält 'Runtime deterministisch'", () => {
    const spine = buildWorldOSSpine(pack);
    const found = spine.summary.some((l) =>
      l.includes("Runtime deterministisch")
    );
    assert.equal(found, true);
  });

  it("61. WorldOSSpine summary enthält 'klick-/zoom-/tracebar'", () => {
    const spine = buildWorldOSSpine(pack);
    const found = spine.summary.some((l) =>
      l.includes("klick-") && l.includes("zoom-") && l.includes("tracebar")
    );
    assert.equal(found, true);
  });

  it("62. WorldOSSpine concept_guard.ok ist true für eigene Sprache", () => {
    const spine = buildWorldOSSpine(pack);
    assert.equal(
      spine.concept_guard.ok,
      true,
      `ConceptGuard-Verletzungen: ${JSON.stringify(spine.concept_guard.violations)}`
    );
  });

  it("63. WorldOSSpine enthält Provenienz-Records", () => {
    const spine = buildWorldOSSpine(pack);
    assert.ok(spine.provenance.length > 0);
  });

  it("64. WorldOSSpine Provenienz enthält canonical_seed Records", () => {
    const spine = buildWorldOSSpine(pack);
    const hasCanonical = spine.provenance.some(
      (r) => r.provenance_type === "canonical_seed"
    );
    assert.equal(hasCanonical, true);
  });

  it("65. WorldOSSpine Provenienz enthält runtime_generated Records", () => {
    const spine = buildWorldOSSpine(pack);
    const hasRuntime = spine.provenance.some(
      (r) => r.provenance_type === "runtime_generated"
    );
    assert.equal(hasRuntime, true);
  });

  // --- Spine Export ---

  it("66. buildWorldOSSpineExport erzeugt export_version 1", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.export_version, 1);
  });

  it("67. SpineExport created_from ist in_memory_os_spine", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.created_from, "in_memory_os_spine");
  });

  it("68. SpineExport slot_count ist 6", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.slot_count, 6);
  });

  it("69. SpineExport occupied_count ist 0", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.occupied_count, 0);
  });

  it("70. SpineExport all_activation_readiness_false ist true", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.all_activation_readiness_false, true);
  });

  it("71. SpineExport uses_ai ist false", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.uses_ai, false);
  });

  it("72. SpineExport uses_ui ist false", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.uses_ui, false);
  });

  it("73. SpineExport uses_postgres ist false", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.uses_postgres, false);
  });

  it("74. SpineExport uses_scheduler ist false", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.uses_scheduler, false);
  });

  it("75. SpineExport runtime_deterministic ist true", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.runtime_deterministic, true);
  });

  it("76. SpineExport audit_ok ist true", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.audit_ok, true);
  });

  it("77. SpineExport concept_guard_ok ist true", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    assert.equal(exp.concept_guard_ok, true);
  });

  it("78. serializeWorldOSSpineExport ist deterministisch", () => {
    const spine = buildWorldOSSpine(pack);
    const s1 = serializeWorldOSSpineExport(spine);
    const s2 = serializeWorldOSSpineExport(spine);
    assert.equal(s1, s2);
  });

  it("79. serializeWorldOSSpineExport gibt gültiges JSON zurück", () => {
    const spine = buildWorldOSSpine(pack);
    const s = serializeWorldOSSpineExport(spine);
    assert.doesNotThrow(() => JSON.parse(s));
  });

  it("80. serialisierter Spine enthält export_version 1", () => {
    const spine = buildWorldOSSpine(pack);
    const parsed = JSON.parse(serializeWorldOSSpineExport(spine));
    assert.equal(parsed.export_version, 1);
  });

  // --- EventStore-Unveränderlichkeit ---

  it("81. buildWorldOSSpine verändert EventStore nicht", () => {
    const before = store.length;
    buildWorldOSSpine(pack);
    assert.equal(store.length, before);
  });

  it("82. buildWorldOSSpineExport verändert EventStore nicht", () => {
    const before = store.length;
    const spine = buildWorldOSSpine(pack);
    buildWorldOSSpineExport(spine);
    assert.equal(store.length, before);
  });

  it("83. assessRuntimeReadiness verändert EventStore nicht", () => {
    const before = store.length;
    assessRuntimeReadiness(pack);
    assert.equal(store.length, before);
  });

  it("84. buildSlotsFromScenarioPack verändert EventStore nicht", () => {
    const before = store.length;
    buildSlotsFromScenarioPack(pack);
    assert.equal(store.length, before);
  });

  it("85. buildProvenanceForInspectionPack verändert EventStore nicht", () => {
    const before = store.length;
    buildProvenanceForInspectionPack(pack);
    assert.equal(store.length, before);
  });

  // --- InspectionPack-Unveränderlichkeit ---

  it("86. InspectionPack bleibt nach Spine-Build unverändert — event_count", () => {
    const countBefore = pack.event_count;
    buildWorldOSSpine(pack);
    assert.equal(pack.event_count, countBefore);
  });

  it("87. InspectionPack bleibt nach Spine-Build unverändert — tick_count", () => {
    const ticksBefore = pack.tick_count;
    buildWorldOSSpine(pack);
    assert.equal(pack.tick_count, ticksBefore);
  });

  it("88. InspectionPack bleibt nach Spine-Build unverändert — audit_ok", () => {
    const auditBefore = pack.audit_ok;
    buildWorldOSSpine(pack);
    assert.equal(pack.audit_ok, auditBefore);
  });

  // --- Ring-2-Export-Kompatibilität ---

  it("89. Ring-2 buildWorldStateExport bleibt nach Ring-3-Operationen kompatibel", () => {
    buildWorldOSSpine(pack);
    const exp = buildWorldStateExport(pack);
    assert.equal(exp.export_version, 1);
    assert.equal(exp.counts.entity_slots, 6);
    assert.equal(exp.counts.ticks, 3);
    assert.equal(exp.counts.traces, 18);
  });

  it("90. Ring-2 serializeWorldStateExport ist nach Ring-3-Operationen deterministisch", () => {
    buildWorldOSSpine(pack);
    const s1 = serializeWorldStateExport(pack);
    const s2 = serializeWorldStateExport(pack);
    assert.equal(s1, s2);
  });

  // --- ConceptGuard-Integration ---

  it("91. ConceptGuard akzeptiert Spine-eigene Sprache", () => {
    const spine = buildWorldOSSpine(pack);
    const texts = spine.summary.map((line, i) => ({ id: `summary-${i}`, text: line }));
    const report = checkConceptLanguage(texts);
    assert.equal(
      report.ok,
      true,
      `Spine-Summary enthält verbotene Begriffe: ${JSON.stringify(report.violations)}`
    );
  });

  it("92. ConceptGuard erkennt 'Seed bedeutet Einzug' weiterhin", () => {
    const report = checkConceptLanguage([
      { id: "r3-test", text: "Seed bedeutet Einzug und presence_pulse bedeutet Leben" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.length >= 2);
  });

  it("93. SpineExport summary enthält '0 Wesen eingezogen'", () => {
    const spine = buildWorldOSSpine(pack);
    const exp = buildWorldOSSpineExport(spine);
    const found = exp.summary.some((l) => l.includes("0 Wesen eingezogen"));
    assert.equal(found, true);
  });

  // --- Slot-Status-Korrektheit ---

  it("94. kein Slot bekommt occupied durch presence_pulse", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const presencePulseEvents = [...pack.events].filter(
      (e) =>
        e.event_type === "entity.state_changed" &&
        (e.payload as Record<string, unknown>).transition_rule === "presence_pulse"
    );
    assert.ok(presencePulseEvents.length > 0, "Es sollten presence_pulse Events existieren");
    const occupiedSlots = slots.filter((s) => s.status === "occupied");
    assert.equal(
      occupiedSlots.length,
      0,
      "presence_pulse darf keinen occupied-Status erzeugen"
    );
  });

  it("95. kein Slot bekommt occupied durch Scenario-Run", () => {
    const freshStore = new InMemoryEventStore();
    const freshPack = runWorldScenario(freshStore, createInitialSixSlotsThreeTickScenario());
    const slots = buildSlotsFromScenarioPack(freshPack);
    const occupiedSlots = slots.filter((s) => s.status === "occupied");
    assert.equal(occupiedSlots.length, 0);
  });

  it("96. Spine zeigt 0 Slots belegt", () => {
    const spine = buildWorldOSSpine(pack);
    const occupied = spine.slots.filter((s) => s.status === "occupied");
    assert.equal(occupied.length, 0);
  });

  // --- Aktivierungs-Schranke ---

  it("97. assessActivationReadiness eines einzelnen Slots — may_activate_now false", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const report = assessActivationReadiness(slots[0], prov, pack);
    assert.equal(report.may_activate_now, false);
  });

  it("98. assessActivationReadiness enthält ai_runtime_binding in missing", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const report = assessActivationReadiness(slots[0], prov, pack);
    assert.ok(report.missing.includes("ai_runtime_binding"));
  });

  it("99. assessActivationReadiness enthält activation_event_type in missing", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const report = assessActivationReadiness(slots[0], prov, pack);
    assert.ok(report.missing.includes("activation_event_type"));
  });

  it("100. assessActivationReadiness enthält Warnungen", () => {
    const slots = buildSlotsFromScenarioPack(pack);
    const prov = buildProvenanceForSlots(slots, pack);
    const report = assessActivationReadiness(slots[0], prov, pack);
    assert.ok(report.warnings.length > 0);
  });
});
