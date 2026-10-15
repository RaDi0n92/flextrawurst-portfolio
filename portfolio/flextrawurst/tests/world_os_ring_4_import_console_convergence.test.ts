import { describe, it, before } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  createInitialSixSlotsThreeTickScenario,
} from "../kernel/scenario/world_scenario.ts";
import { runWorldScenario } from "../kernel/scenario/run_world_scenario.ts";
import type { WorldInspectionPack } from "../kernel/inspection/world_inspection_pack.ts";
import {
  buildWorldOSSpine,
} from "../kernel/os_spine/world_os_spine.ts";
import type { WorldOSSpine } from "../kernel/os_spine/world_os_spine.ts";
import {
  createForumImportFixtureForCanonicalSlots,
} from "../kernel/import_gate/forum_import_candidate.ts";
import type { ForumImportBundle } from "../kernel/import_gate/forum_import_candidate.ts";
import { mapForumAccountsToSlots } from "../kernel/import_gate/account_slot_mapping.ts";
import { runImportDryRun } from "../kernel/import_gate/import_dry_run.ts";
import { buildImportProvenancePreview } from "../kernel/import_gate/import_provenance_preview.ts";
import { runActivationFirewall } from "../kernel/activation/activation_firewall.ts";
import {
  extendSpineWithImportGate,
} from "../kernel/os_spine/world_os_spine_import_extension.ts";
import type { WorldOSSpineImportExtension } from "../kernel/os_spine/world_os_spine_import_extension.ts";
import {
  buildReadOnlyConsoleModel,
} from "../kernel/console/read_only_console_model.ts";
import type { ReadOnlyConsoleModel } from "../kernel/console/read_only_console_model.ts";
import {
  buildConsoleExport,
  serializeConsoleExport,
} from "../kernel/console/console_export.ts";
import { buildOSConvergenceReport } from "../kernel/os_spine/os_convergence_report.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

let store: InMemoryEventStore;
let pack: WorldInspectionPack;
let spine: WorldOSSpine;
let bundle: ForumImportBundle;
let importExtension: WorldOSSpineImportExtension;
let consoleModel: ReadOnlyConsoleModel;

before(() => {
  store = new InMemoryEventStore();
  const scenario = createInitialSixSlotsThreeTickScenario();
  pack = runWorldScenario(store, scenario);
  spine = buildWorldOSSpine(pack);
  bundle = createForumImportFixtureForCanonicalSlots();
  importExtension = extendSpineWithImportGate(spine, bundle);
  consoleModel = buildReadOnlyConsoleModel(spine, importExtension);
});

describe("Weltbetriebssystem Ring 4 — Import Gate + Console + OS Convergence", () => {

  // --- Ring-3-Baseline ---

  it("1. Ring-3 Spine kann aus InspectionPack gebaut werden", () => {
    assert.ok(spine);
    assert.equal(spine.spine_version, 1);
    assert.ok(spine.scenario_id);
    assert.ok(spine.slots.length > 0);
  });

  // --- ForumImportFixture ---

  it("2. ForumImportFixture enthält 6 Accounts", () => {
    assert.equal(bundle.accounts.length, 6);
  });

  it("3. ForumImportFixture enthält mindestens 2 Diskussionen", () => {
    assert.ok(bundle.discussions.length >= 2);
  });

  it("4. ForumImportFixture enthält mindestens 6 Posts", () => {
    assert.ok(bundle.posts.length >= 6);
  });

  // --- Account-to-Slot Mapping ---

  it("5. mapForumAccountsToSlots mappt alle 6 kanonischen Accounts", () => {
    const mappings = mapForumAccountsToSlots(bundle, spine.slots);
    const matched = mappings.filter(
      (m) => m.mapping_status === "matched_canonical_slot"
    );
    assert.equal(matched.length, 6);
  });

  it("6. unbekannter Account bleibt unmatched", () => {
    const extendedBundle: ForumImportBundle = {
      ...bundle,
      accounts: [
        ...bundle.accounts,
        {
          account_id: "totally_unknown_xyz_99",
          display_name: "Unbekannt",
          canonical_match: false,
          matched_slot_id: null,
        },
      ],
    };
    const mappings = mapForumAccountsToSlots(extendedBundle, spine.slots);
    const unknownMapping = mappings.find(
      (m) => m.account_id === "totally_unknown_xyz_99"
    );
    assert.ok(unknownMapping);
    assert.equal(unknownMapping.mapping_status, "unmatched_account");
    assert.equal(unknownMapping.slot_id, null);
  });

  // --- Import Dry Run ---

  it("7. ImportDryRun mapped_count 6", () => {
    assert.equal(importExtension.dry_run.mapped_count, 6);
  });

  it("8. ImportDryRun would_create_events false", () => {
    assert.equal(importExtension.dry_run.would_create_events, false);
  });

  it("9. ImportDryRun would_activate_slots false", () => {
    assert.equal(importExtension.dry_run.would_activate_slots, false);
  });

  // --- Import Provenance Preview ---

  it("10. ImportProvenancePreview erzeugt flarum_import_candidate Records", () => {
    const records = importExtension.provenance_preview.provenance_records;
    assert.ok(records.length > 0);
    const candidateRecords = records.filter(
      (r) => r.provenance_type === "flarum_import_candidate"
    );
    assert.ok(candidateRecords.length > 0);
  });

  it("11. ImportProvenancePreview schreibt keine Events", () => {
    assert.equal(store.length, 27);
  });

  // --- Activation Firewall ---

  it("12. ActivationFirewall blocked true", () => {
    assert.equal(importExtension.activation_firewall.blocked, true);
  });

  it("13. ActivationFirewall allowed_slot_ids leer", () => {
    assert.equal(
      importExtension.activation_firewall.allowed_slot_ids.length,
      0
    );
  });

  it("14. ActivationFirewall blocked_slot_ids 6", () => {
    assert.equal(
      importExtension.activation_firewall.blocked_slot_ids.length,
      6
    );
  });

  it("15. ActivationFirewall reason enthält 'Kein Einzug'", () => {
    assert.ok(
      importExtension.activation_firewall.reason.includes("Kein Einzug")
    );
  });

  it("16. ActivationFirewall check import_is_not_activation passed true", () => {
    const check = importExtension.activation_firewall.checks.find(
      (c) => c.check_id === "import_is_not_activation"
    );
    assert.ok(check);
    assert.equal(check.passed, true);
  });

  it("17. ActivationFirewall check presence_pulse_is_not_life passed true", () => {
    const check = importExtension.activation_firewall.checks.find(
      (c) => c.check_id === "presence_pulse_is_not_life"
    );
    assert.ok(check);
    assert.equal(check.passed, true);
  });

  // --- Spine bleibt unverändert ---

  it("18. extendSpineWithImportGate mutiert Spine nicht", () => {
    assert.equal(spine.spine_version, 1);
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
    assert.ok(spine.slots.every((s) => s.status !== "occupied"));
    const newExtension = extendSpineWithImportGate(spine, bundle);
    assert.ok(newExtension);
    assert.equal(spine.spine_version, 1);
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
  });

  it("19. Slots bleiben occupant_id null", () => {
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
  });

  it("20. Slots bleiben nicht occupied", () => {
    assert.ok(spine.slots.every((s) => s.status !== "occupied"));
  });

  // --- ReadOnlyConsoleModel ---

  it("21. ReadOnlyConsoleModel hat console_version 1", () => {
    assert.equal(consoleModel.console_version, 1);
  });

  it("22. ConsoleModel hat overview Section", () => {
    const section = consoleModel.sections.find((s) => s.kind === "overview");
    assert.ok(section);
    assert.equal(section.id, "overview");
  });

  it("23. ConsoleModel hat slots Section", () => {
    const section = consoleModel.sections.find((s) => s.kind === "slots");
    assert.ok(section);
    assert.equal(section.id, "slots");
  });

  it("24. ConsoleModel hat import_gate Section", () => {
    const section = consoleModel.sections.find(
      (s) => s.kind === "import_gate"
    );
    assert.ok(section);
    assert.equal(section.id, "import_gate");
  });

  it("25. ConsoleModel hat activation_firewall Section", () => {
    const section = consoleModel.sections.find(
      (s) => s.kind === "activation_firewall"
    );
    assert.ok(section);
    assert.equal(section.id, "activation_firewall");
  });

  it("26. ConsoleModel hat camera_readiness Section", () => {
    const section = consoleModel.sections.find(
      (s) => s.kind === "camera_readiness"
    );
    assert.ok(section);
    assert.equal(section.id, "camera_readiness");
  });

  it("27. ConsoleModel zeigt 6 Slots", () => {
    const overview = consoleModel.sections.find((s) => s.id === "overview");
    assert.ok(overview);
    const row = overview.rows.find((r) => r["label"] === "slot_count");
    assert.ok(row);
    assert.equal(row["value"], 6);
  });

  it("28. ConsoleModel zeigt 0 occupied", () => {
    const overview = consoleModel.sections.find((s) => s.id === "overview");
    assert.ok(overview);
    const row = overview.rows.find((r) => r["label"] === "occupied_count");
    assert.ok(row);
    assert.equal(row["value"], 0);
  });

  it("29. ConsoleModel zeigt 0 eingezogene Wesen", () => {
    const overview = consoleModel.sections.find((s) => s.id === "overview");
    assert.ok(overview);
    const row = overview.rows.find(
      (r) => r["label"] === "eingezogene_wesen_count"
    );
    assert.ok(row);
    assert.equal(row["value"], 0);
  });

  it("30. ConsoleModel warnt vor Import ≠ Einzug", () => {
    const warningMatch = consoleModel.warnings.some(
      (w) => w.includes("Import") && w.includes("Einzug")
    );
    assert.ok(warningMatch);
  });

  it("31. ConsoleNavigation enthält Einträge für alle Sections", () => {
    assert.equal(
      consoleModel.navigation.length,
      consoleModel.sections.length
    );
    for (const section of consoleModel.sections) {
      const navItem = consoleModel.navigation.find(
        (n) => n.target_section_id === section.id
      );
      assert.ok(navItem, `Navigation-Eintrag für Section '${section.id}' fehlt`);
    }
  });

  // --- Console Export ---

  it("32. ConsoleExport ist deterministisch", () => {
    const s1 = serializeConsoleExport(consoleModel);
    const s2 = serializeConsoleExport(consoleModel);
    assert.equal(s1, s2);
  });

  it("33. ConsoleExport schreibt keine Datei und gibt String zurück", () => {
    const result = serializeConsoleExport(consoleModel);
    assert.equal(typeof result, "string");
    assert.ok(result.length > 0);
    const parsed = JSON.parse(result);
    assert.equal(parsed.export_version, 1);
    assert.equal(parsed.created_from, "in_memory_console_model");
  });

  // --- OS Convergence Report ---

  it("34. OSConvergenceReport has_runtime true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.has_runtime, true);
  });

  it("35. OSConvergenceReport has_spine true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.has_spine, true);
  });

  it("36. OSConvergenceReport has_import_gate true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.has_import_gate, true);
  });

  it("37. OSConvergenceReport has_activation_firewall true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.has_activation_firewall, true);
  });

  it("38. OSConvergenceReport has_console_model true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.has_console_model, true);
  });

  it("39. OSConvergenceReport ready_for_real_import_files true", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_real_import_files, true);
  });

  it("40. OSConvergenceReport ready_for_ui false", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_ui, false);
  });

  it("41. OSConvergenceReport ready_for_activation false", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_activation, false);
  });

  it("42. OSConvergenceReport blocker resident_profile_missing", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.ok(report.blockers.includes("resident_profile_missing"));
  });

  it("43. OSConvergenceReport blocker explicit_activation_protocol_missing", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.ok(
      report.blockers.includes("explicit_activation_protocol_missing")
    );
  });

  // --- Concept Guard — neue Muster ---

  it("44. ConceptGuard erkennt 'Import bedeutet Einzug'", () => {
    const result = checkConceptLanguage([
      { id: "test-44", text: "Import bedeutet Einzug in die Welt." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(result.violations.some((v) => v.term === "Import bedeutet Einzug"));
  });

  it("45. ConceptGuard erkennt 'Flarum-Post ist Live-Handlung'", () => {
    const result = checkConceptLanguage([
      { id: "test-45", text: "Flarum-Post ist Live-Handlung des Wesens." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(
      result.violations.some((v) => v.term === "Flarum-Post ist Live-Handlung")
    );
  });

  it("46. ConceptGuard erkennt 'Account ist Bewohner'", () => {
    const result = checkConceptLanguage([
      { id: "test-46", text: "Account ist Bewohner des Slots." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(result.violations.some((v) => v.term === "Account ist Bewohner"));
  });

  it("47. ConceptGuard erkennt 'Slot ist Wesen'", () => {
    const result = checkConceptLanguage([
      { id: "test-47", text: "Slot ist Wesen mit eigenem Leben." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(result.violations.some((v) => v.term === "Slot ist Wesen"));
  });

  it("48. ConceptGuard erkennt 'Console ist UI'", () => {
    const result = checkConceptLanguage([
      { id: "test-48", text: "Console ist UI für den Nutzer." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(result.violations.some((v) => v.term === "Console ist UI"));
  });

  it("49. ConceptGuard erkennt 'CameraModel ist Renderer'", () => {
    const result = checkConceptLanguage([
      { id: "test-49", text: "CameraModel ist Renderer für die Welt." },
    ]);
    assert.equal(result.ok, false);
    assert.ok(
      result.violations.some((v) => v.term === "CameraModel ist Renderer")
    );
  });

  it("50. ConceptGuard akzeptiert 'Import-Kandidat'", () => {
    const result = checkConceptLanguage([
      {
        id: "test-50",
        text: "Import-Kandidat, Herkunft, Provenienz, Slot-Mapping, Read-only Console Model, Renderer-offenes Datenmodell.",
      },
    ]);
    assert.equal(result.ok, true);
    assert.equal(result.violations.length, 0);
  });

  // --- EventStore bleibt unverändert ---

  it("51. EventStore bleibt nach ImportDryRun unverändert", () => {
    const dryRun = runImportDryRun(bundle, spine.slots);
    assert.equal(dryRun.would_create_events, false);
    assert.equal(store.length, 27);
  });

  it("52. EventStore bleibt nach ConsoleExport unverändert", () => {
    serializeConsoleExport(consoleModel);
    assert.equal(store.length, 27);
  });

  it("53. EventStore bleibt nach ConvergenceReport unverändert", () => {
    buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(store.length, 27);
  });

  // --- Strukturelle Garantien ---

  it("54. Exportfunktionen geben Strings/Objekte zurück und schreiben keine Dateien", () => {
    const exported = buildConsoleExport(consoleModel);
    assert.equal(typeof exported, "object");
    assert.equal(exported.export_version, 1);
    const serialized = serializeConsoleExport(consoleModel);
    assert.equal(typeof serialized, "string");
    assert.equal(store.length, 27);
  });

  it("55. Keine UI/HTML/CSS/DOM-Strukturen im ConsoleModel", () => {
    const serialized = JSON.stringify(consoleModel);
    assert.ok(!serialized.includes("<html"));
    assert.ok(!serialized.includes("<div"));
    assert.ok(!serialized.includes("<style"));
    assert.ok(!serialized.includes("document."));
    assert.ok(!serialized.includes("window."));
    assert.ok(!serialized.includes("innerHTML"));
    assert.ok(!serialized.includes("createElement"));
  });

  it("56. Keine AI-Aufrufe im ConsoleModel oder Import-Gate", () => {
    assert.equal(spine.runtime_readiness.uses_ai, false);
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_activation, false);
  });

  it("57. Keine Postgres-Nutzung", () => {
    assert.equal(spine.runtime_readiness.uses_postgres, false);
  });

  it("58. Keine Scheduler-Nutzung", () => {
    assert.equal(spine.runtime_readiness.uses_scheduler, false);
  });

  it("59. Alle bisherigen Spine-Tests bleiben gültig", () => {
    assert.equal(spine.slots.length, 6);
    assert.ok(spine.activation_readiness.every((r) => r.may_activate_now === false));
    assert.equal(spine.runtime_readiness.deterministic, true);
    assert.equal(spine.runtime_readiness.uses_ai, false);
    assert.equal(spine.runtime_readiness.uses_ui, false);
    assert.ok(spine.camera_readiness.ok);
    assert.ok(spine.audit_ok);
  });

  it("60. Gesamtmodell beweist: Realitätsanschluss vorbereitet, Aktivierung blockiert", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);

    assert.equal(report.has_runtime, true);
    assert.equal(report.has_spine, true);
    assert.equal(report.has_import_gate, true);
    assert.equal(report.has_activation_firewall, true);
    assert.equal(report.has_console_model, true);
    assert.equal(report.has_camera_navigation, true);

    assert.equal(report.ready_for_real_import_files, true);
    assert.equal(report.ready_for_ui, false);
    assert.equal(report.ready_for_activation, false);

    assert.equal(importExtension.activation_firewall.blocked, true);
    assert.equal(importExtension.activation_firewall.allowed_slot_ids.length, 0);

    assert.equal(importExtension.dry_run.would_create_events, false);
    assert.equal(importExtension.dry_run.would_activate_slots, false);

    assert.ok(spine.slots.every((s) => s.occupant_id === null));
    assert.ok(spine.slots.every((s) => s.status !== "occupied"));

    assert.equal(store.length, 27);
  });

  // --- Zusätzliche Ring-4-Garantien ---

  it("61. ForumImportBundle hat bundle_id", () => {
    assert.ok(bundle.bundle_id.length > 0);
    assert.equal(bundle.source_type, "manual_fixture");
  });

  it("62. ImportProvenancePreview hat preview_id und bundle_id", () => {
    assert.ok(
      importExtension.provenance_preview.preview_id.length > 0
    );
    assert.equal(
      importExtension.provenance_preview.bundle_id,
      bundle.bundle_id
    );
  });

  it("63. ImportProvenancePreview post_to_slot_links zeigen flarum_import_candidate", () => {
    const links = importExtension.provenance_preview.post_to_slot_links;
    assert.ok(links.length >= 6);
    assert.ok(
      links.every((l) => l.provenance_type === "flarum_import_candidate")
    );
  });

  it("64. Alle kanonischen Account-IDs in Mappings vorhanden", () => {
    const mappings = importExtension.dry_run.mappings;
    const canonicalIds = [
      "Schorschel",
      "Resonanzknoten",
      "F3INSCHM3CK3R",
      "träumerlie",
      "R1ZZ1",
      "jumpa",
    ];
    for (const id of canonicalIds) {
      const mapping = mappings.find((m) => m.account_id === id);
      assert.ok(mapping, `Mapping für ${id} fehlt`);
      assert.equal(mapping.mapping_status, "matched_canonical_slot");
      assert.equal(mapping.slot_id, id);
    }
  });

  it("65. buildImportProvenancePreview direkt aufgerufen schreibt keine Events", () => {
    const mappings = mapForumAccountsToSlots(bundle, spine.slots);
    const preview = buildImportProvenancePreview(bundle, mappings);
    assert.ok(preview.provenance_records.length > 0);
    assert.equal(store.length, 27);
  });

  it("66. runActivationFirewall direkt aufgerufen blockiert alle Slots", () => {
    const dryRun = runImportDryRun(bundle, spine.slots);
    const firewall = runActivationFirewall(
      spine.slots,
      dryRun,
      spine.activation_readiness
    );
    assert.equal(firewall.blocked, true);
    assert.equal(firewall.allowed_slot_ids.length, 0);
    assert.equal(firewall.blocked_slot_ids.length, 6);
  });

  it("67. ConsoleModel runtime-Section zeigt uses_ai false und uses_ui false", () => {
    const runtimeSection = consoleModel.sections.find(
      (s) => s.id === "runtime"
    );
    assert.ok(runtimeSection);
    const aiRow = runtimeSection.rows.find((r) => r["label"] === "uses_ai");
    const uiRow = runtimeSection.rows.find((r) => r["label"] === "uses_ui");
    assert.ok(aiRow);
    assert.ok(uiRow);
    assert.equal(aiRow["value"], false);
    assert.equal(uiRow["value"], false);
  });

  it("68. OSConvergenceReport convergence_version ist 1", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.convergence_version, 1);
  });

  it("69. OSConvergenceReport blockers enthält real_import_parser_missing und ui_renderer_missing", () => {
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.ok(report.blockers.includes("real_import_parser_missing"));
    assert.ok(report.blockers.includes("ui_renderer_missing"));
    assert.ok(report.blockers.includes("memory_import_missing"));
  });

  it("70. Importierter Ursprung bleibt Ursprung — kein Post wird als Live-Handlung behandelt", () => {
    const links = importExtension.provenance_preview.post_to_slot_links;
    for (const link of links) {
      assert.equal(
        link.provenance_type,
        "flarum_import_candidate",
        `Post ${link.post_id} hat falschen Provenance-Typ`
      );
    }
    assert.equal(store.length, 27);
  });
});
