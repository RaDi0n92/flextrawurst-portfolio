import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  buildDanielRootAdmin,
  buildObserverAdmin,
  buildSystemProcessActor,
  hasPermission,
} from "../kernel/admin/admin_permissions.ts";
import {
  createCommandIntent,
} from "../kernel/admin/command_intent.ts";
import {
  createEmptyCommandLedger,
  recordCommandIntent,
} from "../kernel/admin/command_ledger.ts";
import {
  buildFeatureRegistry,
  findFeatureFlag,
  listDisabledFeatures,
  listBlockedFeatures,
  listEnabledFeatures,
} from "../kernel/features/feature_registry.ts";
import { evaluateFeatureActivationGate } from "../kernel/features/feature_activation_gate.ts";
import { evaluateFeatureDeactivationGate } from "../kernel/features/feature_deactivation_gate.ts";
import { buildAdminControlSnapshot } from "../kernel/admin/admin_control_snapshot.ts";
import { buildAdminControlInspection } from "../kernel/admin/admin_control_inspection.ts";
import {
  buildAdminControlExport,
  serializeAdminControlExport,
} from "../kernel/admin/admin_control_export.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

// ---------------------------------------------------------------------------
// 1. Admin Roles und Permissions
// ---------------------------------------------------------------------------

describe("Ring 17 — AdminPermissions: Roles", () => {
  it("1. buildDanielRootAdmin erzeugt role daniel_root", () => {
    const actor = buildDanielRootAdmin();
    assert.equal(actor.role, "daniel_root");
  });

  it("2. DanielRoot hat feature.approve_activation", () => {
    const actor = buildDanielRootAdmin();
    assert.ok(hasPermission(actor, "feature.approve_activation"));
  });

  it("3. DanielRoot hat worldrun.freeze", () => {
    const actor = buildDanielRootAdmin();
    assert.ok(hasPermission(actor, "worldrun.freeze"));
  });

  it("4. Observer hat feature.view", () => {
    const actor = buildObserverAdmin("obs_1");
    assert.ok(hasPermission(actor, "feature.view"));
  });

  it("5. Observer hat keine feature.approve_activation", () => {
    const actor = buildObserverAdmin("obs_1");
    assert.ok(!hasPermission(actor, "feature.approve_activation"));
  });

  it("6. system_process darf keine Aktivierung freigeben", () => {
    const actor = buildSystemProcessActor("sys_1");
    assert.ok(!hasPermission(actor, "feature.approve_activation"));
    assert.ok(!hasPermission(actor, "import.approve"));
    assert.ok(!hasPermission(actor, "slot.approve_activation"));
  });

  it("DanielRoot hat worldrun.stop", () => {
    const actor = buildDanielRootAdmin();
    assert.ok(hasPermission(actor, "worldrun.stop"));
  });

  it("DanielRoot hat import.approve", () => {
    const actor = buildDanielRootAdmin();
    assert.ok(hasPermission(actor, "import.approve"));
  });

  it("Observer hat export.view", () => {
    const actor = buildObserverAdmin("obs_2");
    assert.ok(hasPermission(actor, "export.view"));
  });

  it("Observer hat keine feature.deactivate", () => {
    const actor = buildObserverAdmin("obs_3");
    assert.ok(!hasPermission(actor, "feature.deactivate"));
  });
});

// ---------------------------------------------------------------------------
// 2. CommandIntent
// ---------------------------------------------------------------------------

describe("Ring 17 — CommandIntent: dry_run und keine Ausführung", () => {
  it("7. createCommandIntent erzeugt dry_run Command", () => {
    const cmd = createCommandIntent({
      command_id: "cmd_001",
      command_type: "request_feature_activation",
      requested_by: "daniel_root",
      target_type: "feature",
      target_id: "tamagotchi_care_feature",
      reason: "Test-Anfrage",
      created_at: "2026-05-09T00:00:00Z",
    });
    assert.equal(cmd.dry_run, true);
  });

  it("8. CommandIntent führt nichts aus (dry_run true)", () => {
    const cmd = createCommandIntent({
      command_id: "cmd_002",
      command_type: "approve_feature_activation",
      requested_by: "daniel_root",
      target_type: "organ",
      target_id: "kompoase_space_feature",
      reason: "Test",
      created_at: "2026-05-09T00:00:00Z",
    });
    assert.equal(cmd.dry_run, true);
    assert.equal(cmd.command_type, "approve_feature_activation");
  });

  it("CommandIntent für import approval bleibt dry_run", () => {
    const cmd = createCommandIntent({
      command_id: "cmd_003",
      command_type: "approve_import",
      requested_by: "daniel_root",
      target_type: "import_bundle",
      target_id: "import_bundle_001",
      reason: "Import prüfen",
      created_at: "2026-05-09T00:00:00Z",
    });
    assert.equal(cmd.dry_run, true);
  });

  it("76. CommandIntent für import approval bleibt dry_run (nochmals explizit)", () => {
    const cmd = createCommandIntent({
      command_id: "cmd_004",
      command_type: "approve_import",
      requested_by: "daniel_root",
      target_type: "import_bundle",
      target_id: "bundle_flarum_01",
      reason: "Flarum-Import prüfen",
      created_at: "2026-05-09T00:00:00Z",
    });
    assert.equal(cmd.dry_run, true);
  });

  it("77. CommandIntent für readonly export bleibt dry_run", () => {
    const cmd = createCommandIntent({
      command_id: "cmd_005",
      command_type: "create_readonly_export",
      requested_by: "daniel_root",
      target_type: "export",
      target_id: "worldblick_export_01",
      reason: "Export erstellen",
      created_at: "2026-05-09T00:00:00Z",
    });
    assert.equal(cmd.dry_run, true);
  });
});

// ---------------------------------------------------------------------------
// 3. CommandLedger
// ---------------------------------------------------------------------------

describe("Ring 17 — CommandLedger: append-only", () => {
  const actor = buildDanielRootAdmin();

  it("9. createEmptyCommandLedger erzeugt leeres Ledger", () => {
    const ledger = createEmptyCommandLedger();
    assert.equal(ledger.entries.length, 0);
    assert.equal(ledger.ledger_version, 1);
  });

  it("10. recordCommandIntent gibt neues Ledger zurück", () => {
    const ledger = createEmptyCommandLedger();
    const cmd = createCommandIntent({
      command_id: "cmd_l01",
      command_type: "request_feature_activation",
      requested_by: "daniel_root",
      target_type: "feature",
      target_id: "tamagotchi_care_feature",
      reason: "Test",
      created_at: "2026-05-09T00:00:00Z",
    });
    const newLedger = recordCommandIntent(ledger, cmd, actor, "recorded", ["Notiz"]);
    assert.equal(newLedger.entries.length, 1);
  });

  it("11. altes Ledger bleibt unverändert", () => {
    const ledger = createEmptyCommandLedger();
    const cmd = createCommandIntent({
      command_id: "cmd_l02",
      command_type: "deactivate_feature",
      requested_by: "daniel_root",
      target_type: "feature",
      target_id: "worldblick_readonly_export",
      reason: "Test",
      created_at: "2026-05-09T00:00:00Z",
    });
    const _newLedger = recordCommandIntent(ledger, cmd, actor, "recorded", []);
    assert.equal(ledger.entries.length, 0);
  });

  it("73. CommandLedger append-only Verhalten: zwei Commands", () => {
    let ledger = createEmptyCommandLedger();
    const cmd1 = createCommandIntent({
      command_id: "cmd_app1",
      command_type: "request_feature_activation",
      requested_by: "daniel_root",
      target_type: "feature",
      target_id: "f1",
      reason: "Test 1",
      created_at: "2026-05-09T00:00:00Z",
    });
    const cmd2 = createCommandIntent({
      command_id: "cmd_app2",
      command_type: "pause_worldrun",
      requested_by: "daniel_root",
      target_type: "worldrun",
      target_id: "run_01",
      reason: "Test 2",
      created_at: "2026-05-09T00:00:01Z",
    });
    ledger = recordCommandIntent(ledger, cmd1, actor, "recorded", []);
    ledger = recordCommandIntent(ledger, cmd2, actor, "blocked", ["blockiert"]);
    assert.equal(ledger.entries.length, 2);
    assert.equal(ledger.entries[0].command.command_id, "cmd_app1");
    assert.equal(ledger.entries[1].command.command_id, "cmd_app2");
  });

  it("74. CommandLedger kann blocked Command speichern", () => {
    const ledger = createEmptyCommandLedger();
    const cmd = createCommandIntent({
      command_id: "cmd_blocked",
      command_type: "approve_feature_activation",
      requested_by: "obs_1",
      target_type: "organ",
      target_id: "tamagotchi_care_feature",
      reason: "Versuch",
      created_at: "2026-05-09T00:00:00Z",
    });
    const obs = buildObserverAdmin("obs_1");
    const newLedger = recordCommandIntent(ledger, cmd, obs, "blocked", ["Fehlende Permission"]);
    assert.equal(newLedger.entries[0].status, "blocked");
  });

  it("75. CommandLedger kann approved Command speichern ohne Ausführung", () => {
    const ledger = createEmptyCommandLedger();
    const cmd = createCommandIntent({
      command_id: "cmd_approved",
      command_type: "create_readonly_export",
      requested_by: "daniel_root",
      target_type: "export",
      target_id: "worldblick_export_01",
      reason: "Export freigegeben",
      created_at: "2026-05-09T00:00:00Z",
    });
    const newLedger = recordCommandIntent(ledger, cmd, actor, "approved", ["Readonly export OK"]);
    assert.equal(newLedger.entries[0].status, "approved");
    assert.equal(newLedger.entries[0].command.dry_run, true);
  });
});

// ---------------------------------------------------------------------------
// 4. FeatureRegistry
// ---------------------------------------------------------------------------

describe("Ring 17 — FeatureRegistry: Organ-Features registriert", () => {
  const registry = buildFeatureRegistry();

  it("12. buildFeatureRegistry enthält tamagotchi_care_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "tamagotchi_care_feature"));
  });

  it("13. buildFeatureRegistry enthält kompoase_space_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "kompoase_space_feature"));
  });

  it("14. buildFeatureRegistry enthält sleep_cycle_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "sleep_cycle_feature"));
  });

  it("15. buildFeatureRegistry enthält substance_modifiers_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "substance_modifiers_feature"));
  });

  it("16. buildFeatureRegistry enthält dream_residue_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "dream_residue_feature"));
  });

  it("17. buildFeatureRegistry enthält resonance_vacation_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "resonance_vacation_feature"));
  });

  it("18. buildFeatureRegistry enthält metawar_space_feature", () => {
    assert.ok(registry.some((f) => f.feature_id === "metawar_space_feature"));
  });
});

describe("Ring 17 — FeatureRegistry: Organ-Features deaktiviert", () => {
  const registry = buildFeatureRegistry();
  const organs = registry.filter((f) => f.kind === "organ");

  it("19. alle Organ-Features enabled false", () => {
    for (const f of organs) {
      assert.equal(f.enabled, false, `${f.feature_id} hat enabled true`);
    }
  });

  it("20. alle Organ-Features default_enabled false", () => {
    for (const f of organs) {
      assert.equal(f.default_enabled, false, `${f.feature_id} hat default_enabled true`);
    }
  });

  it("21. alle Organ-Features can_enable_now false", () => {
    for (const f of organs) {
      assert.equal(f.can_enable_now, false, `${f.feature_id} hat can_enable_now true`);
    }
  });

  it("22. alle Organ-Features haben concept_not_planned_by_daniel Blocker", () => {
    for (const f of organs) {
      assert.ok(
        f.blockers.includes("concept_not_planned_by_daniel"),
        `${f.feature_id} fehlt Blocker concept_not_planned_by_daniel`
      );
    }
  });
});

describe("Ring 17 — FeatureRegistry: System-Features", () => {
  it("23. worldblick_readonly_export enabled true", () => {
    const f = findFeatureFlag("worldblick_readonly_export");
    assert.ok(f);
    assert.equal(f!.enabled, true);
  });

  it("24. admin_control_plane enabled true", () => {
    const f = findFeatureFlag("admin_control_plane");
    assert.ok(f);
    assert.equal(f!.enabled, true);
  });

  it("25. deep_search_foundation registered aber disabled", () => {
    const f = findFeatureFlag("deep_search_foundation");
    assert.ok(f);
    assert.equal(f!.enabled, false);
    assert.equal(f!.status, "registered");
  });

  it("26. import_gate nicht live aktiv", () => {
    const f = findFeatureFlag("import_gate");
    assert.ok(f);
    assert.equal(f!.enabled, false);
  });
});

describe("Ring 17 — FeatureRegistry: Listen-Funktionen", () => {
  it("27. listDisabledFeatures enthält Organ-Features", () => {
    const disabled = listDisabledFeatures();
    assert.ok(disabled.some((f) => f.feature_id === "tamagotchi_care_feature"));
    assert.ok(disabled.some((f) => f.feature_id === "metawar_space_feature"));
  });

  it("28. listBlockedFeatures enthält Organ-Features", () => {
    const blocked = listBlockedFeatures();
    assert.ok(blocked.some((f) => f.feature_id === "kompoase_space_feature"));
    assert.ok(blocked.some((f) => f.feature_id === "sleep_cycle_feature"));
  });

  it("29. listEnabledFeatures enthält worldblick/admin", () => {
    const enabled = listEnabledFeatures();
    assert.ok(enabled.some((f) => f.feature_id === "worldblick_readonly_export"));
    assert.ok(enabled.some((f) => f.feature_id === "admin_control_plane"));
  });

  it("71. FeatureRegistry ist deterministisch", () => {
    const r1 = buildFeatureRegistry();
    const r2 = buildFeatureRegistry();
    assert.deepEqual(
      r1.map((f) => f.feature_id).sort(),
      r2.map((f) => f.feature_id).sort()
    );
  });
});

// ---------------------------------------------------------------------------
// 5. ActivationGate
// ---------------------------------------------------------------------------

describe("Ring 17 — FeatureActivationGate: Organ-Features blockiert", () => {
  const daniel = buildDanielRootAdmin();
  const observer = buildObserverAdmin("obs_4");

  it("30. ActivationGate blockiert Tamagotchi für observer", () => {
    const f = findFeatureFlag("tamagotchi_care_feature")!;
    const report = evaluateFeatureActivationGate(f, observer);
    assert.equal(report.blocked, true);
    assert.equal(report.allowed, false);
  });

  it("31. ActivationGate blockiert Tamagotchi für daniel_root wegen can_enable_now false", () => {
    const f = findFeatureFlag("tamagotchi_care_feature")!;
    const report = evaluateFeatureActivationGate(f, daniel);
    assert.equal(report.blocked, true);
    assert.equal(report.allowed, false);
    assert.ok(report.blockers.includes("can_enable_now_is_false"));
  });

  it("32. ActivationGate nennt required approval Daniel", () => {
    const f = findFeatureFlag("tamagotchi_care_feature")!;
    const report = evaluateFeatureActivationGate(f, observer);
    assert.ok(
      report.required_approvals.some((a) =>
        a.includes("daniel") || a.includes("daniel_explicit_approval")
      )
    );
  });

  it("33. ActivationGate blockiert KompOase", () => {
    const f = findFeatureFlag("kompoase_space_feature")!;
    const report = evaluateFeatureActivationGate(f, daniel);
    assert.equal(report.blocked, true);
  });

  it("34. ActivationGate blockiert Resonanzurlaub", () => {
    const f = findFeatureFlag("resonance_vacation_feature")!;
    const report = evaluateFeatureActivationGate(f, daniel);
    assert.equal(report.blocked, true);
  });

  it("78. FeatureActivationGate für enabled ungefährliches Feature: worldblick mit DanielRoot", () => {
    const f = findFeatureFlag("worldblick_readonly_export")!;
    const report = evaluateFeatureActivationGate(f, daniel);
    assert.equal(report.allowed, true);
    assert.equal(report.blocked, false);
  });

  it("79. FeatureActivationGate für Organ bleibt trotzdem blockiert", () => {
    const f = findFeatureFlag("substance_modifiers_feature")!;
    const report = evaluateFeatureActivationGate(f, daniel);
    assert.equal(report.blocked, true);
    assert.equal(report.allowed, false);
  });
});

// ---------------------------------------------------------------------------
// 6. DeactivationGate
// ---------------------------------------------------------------------------

describe("Ring 17 — FeatureDeactivationGate", () => {
  const daniel = buildDanielRootAdmin();
  const observer = buildObserverAdmin("obs_5");

  it("35. DeactivationGate erlaubt worldblick bei passender Permission", () => {
    const f = findFeatureFlag("worldblick_readonly_export")!;
    const report = evaluateFeatureDeactivationGate(f, daniel);
    assert.equal(report.allowed, true);
    assert.equal(report.blocked, false);
  });

  it("36. DeactivationGate blockiert ohne Permission", () => {
    const f = findFeatureFlag("worldblick_readonly_export")!;
    const report = evaluateFeatureDeactivationGate(f, observer);
    assert.equal(report.allowed, false);
    assert.equal(report.blocked, true);
  });

  it("DeactivationGate: disabled Feature braucht keine Deactivation", () => {
    const f = findFeatureFlag("tamagotchi_care_feature")!;
    const report = evaluateFeatureDeactivationGate(f, daniel);
    assert.equal(report.blocked, false);
    assert.ok(report.notes.some((n) => n.includes("bereits deaktiviert")));
  });
});

// ---------------------------------------------------------------------------
// 7. AdminControlSnapshot
// ---------------------------------------------------------------------------

describe("Ring 17 — AdminControlSnapshot", () => {
  const daniel = buildDanielRootAdmin();
  const registry = buildFeatureRegistry();
  const snapshot = buildAdminControlSnapshot(daniel, registry);

  it("37. AdminControlSnapshot zählt alle Features", () => {
    assert.equal(snapshot.feature_count, registry.length);
  });

  it("38. Snapshot enabled_feature_count mindestens 2", () => {
    assert.ok(snapshot.enabled_feature_count >= 2);
  });

  it("39. Snapshot blocked_feature_count mindestens 7", () => {
    assert.ok(snapshot.blocked_feature_count >= 7);
  });

  it("40. Snapshot critical_controls can_freeze_worldrun true für Daniel", () => {
    assert.equal(snapshot.critical_controls.can_freeze_worldrun, true);
  });

  it("41. Snapshot critical_controls can_stop_worldrun true für Daniel", () => {
    assert.equal(snapshot.critical_controls.can_stop_worldrun, true);
  });

  it("42. Snapshot critical_controls can_approve_import true für Daniel", () => {
    assert.equal(snapshot.critical_controls.can_approve_import, true);
  });

  it("43. Snapshot critical_controls can_approve_feature_activation true für Daniel", () => {
    assert.equal(snapshot.critical_controls.can_approve_feature_activation, true);
  });

  it("Snapshot snapshot_version ist 1", () => {
    assert.equal(snapshot.snapshot_version, 1);
  });

  it("Observer Snapshot: can_approve_feature_activation false", () => {
    const obs = buildObserverAdmin("obs_6");
    const obsSnapshot = buildAdminControlSnapshot(obs, registry);
    assert.equal(obsSnapshot.critical_controls.can_approve_feature_activation, false);
  });
});

// ---------------------------------------------------------------------------
// 8. AdminControlInspection
// ---------------------------------------------------------------------------

describe("Ring 17 — AdminControlInspection", () => {
  const daniel = buildDanielRootAdmin();
  const inspection = buildAdminControlInspection(daniel);

  it("44. buildAdminControlInspection erzeugt ActivationGates für alle Features", () => {
    assert.equal(inspection.activation_gates.length, inspection.features.length);
  });

  it("45. Inspection summary enthält Alle Organ-Features deaktiviert", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Alle Organ-Features deaktiviert")));
  });

  it("46. Inspection summary enthält Aktivierung blockiert", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Aktivierung blockiert")));
  });

  it("47. Inspection summary enthält Tiefensuche-Grundlage registriert", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Tiefensuche-Grundlage")));
  });

  it("Inspection summary enthält Verwaltungs-Steuerungsebene aktiv", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Verwaltungs-Steuerungsebene aktiv")));
  });

  it("Inspection summary enthält Weltblick nur-lesen erlaubt", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Weltblick nur-lesen erlaubt")));
  });

  it("72. AdminControlInspection ist deterministisch", () => {
    const i1 = buildAdminControlInspection(daniel);
    const i2 = buildAdminControlInspection(daniel);
    assert.equal(i1.features.length, i2.features.length);
    assert.equal(i1.snapshot.feature_count, i2.snapshot.feature_count);
    assert.equal(i1.safe_to_activate_organs ?? false, i2.safe_to_activate_organs ?? false);
  });
});

// ---------------------------------------------------------------------------
// 9. AdminControlExport — Determinismus
// ---------------------------------------------------------------------------

describe("Ring 17 — AdminControlExport: Determinismus", () => {
  const daniel = buildDanielRootAdmin();

  it("48. AdminControlExport deterministisch", () => {
    const i1 = buildAdminControlInspection(daniel);
    const i2 = buildAdminControlInspection(daniel);
    const e1 = buildAdminControlExport(i1);
    const e2 = buildAdminControlExport(i2);
    assert.deepEqual(e1, e2);
  });

  it("49. serializeAdminControlExport stabil", () => {
    const i1 = buildAdminControlInspection(daniel);
    const i2 = buildAdminControlInspection(daniel);
    const j1 = serializeAdminControlExport(i1);
    const j2 = serializeAdminControlExport(i2);
    assert.equal(j1, j2);
  });

  it("Export organ_features_enabled ist false", () => {
    const inspection = buildAdminControlInspection(daniel);
    const exp = buildAdminControlExport(inspection);
    assert.equal(exp.organ_features_enabled, false);
  });

  it("Export safe_to_activate_organs ist false", () => {
    const inspection = buildAdminControlInspection(daniel);
    const exp = buildAdminControlExport(inspection);
    assert.equal(exp.safe_to_activate_organs, false);
  });

  it("Export feature_ids sind sortiert", () => {
    const inspection = buildAdminControlInspection(daniel);
    const exp = buildAdminControlExport(inspection);
    const sorted = [...exp.feature_ids].sort();
    assert.deepEqual(exp.feature_ids, sorted);
  });
});

// ---------------------------------------------------------------------------
// 10. ConceptGuard — neue verbotene Muster
// ---------------------------------------------------------------------------

describe("Ring 17 — ConceptGuard: neue verbotene Muster", () => {
  it("50. ConceptGuard erkennt 'Feature registriert heißt aktiv'", () => {
    const r = checkConceptLanguage([{ id: "g1", text: "Feature registriert heißt aktiv." }]);
    assert.equal(r.ok, false);
  });

  it("51. ConceptGuard erkennt 'Blueprint ist aktivierbar'", () => {
    const r = checkConceptLanguage([{ id: "g2", text: "Blueprint ist aktivierbar jetzt." }]);
    assert.equal(r.ok, false);
  });

  it("52. ConceptGuard erkennt 'AdminControl aktiviert Organe automatisch'", () => {
    const r = checkConceptLanguage([{ id: "g3", text: "AdminControl aktiviert Organe automatisch." }]);
    assert.equal(r.ok, false);
  });

  it("53. ConceptGuard erkennt 'Worldblick darf Welt verändern'", () => {
    const r = checkConceptLanguage([{ id: "g4", text: "Worldblick darf Welt verändern." }]);
    assert.equal(r.ok, false);
  });

  it("54. ConceptGuard erkennt 'ImportGate darf live importieren'", () => {
    const r = checkConceptLanguage([{ id: "g5", text: "ImportGate darf live importieren jetzt." }]);
    assert.equal(r.ok, false);
  });

  it("55. ConceptGuard erkennt 'DeepSearch ist schon implementiert'", () => {
    const r = checkConceptLanguage([{ id: "g6", text: "DeepSearch ist schon implementiert." }]);
    assert.equal(r.ok, false);
  });

  it("56. ConceptGuard erkennt 'Operator darf ohne Daniel aktivieren'", () => {
    const r = checkConceptLanguage([{ id: "g7", text: "Operator darf ohne Daniel aktivieren." }]);
    assert.equal(r.ok, false);
  });
});

describe("Ring 17 — ConceptGuard: erlaubte Sprache akzeptiert", () => {
  it("57. ConceptGuard akzeptiert 'Feature registriert aber deaktiviert'", () => {
    const r = checkConceptLanguage([{ id: "a1", text: "Feature registriert aber deaktiviert." }]);
    assert.equal(r.ok, true);
  });

  it("58. ConceptGuard akzeptiert 'ActivationGate blockiert'", () => {
    const r = checkConceptLanguage([{ id: "a2", text: "ActivationGate blockiert das Feature." }]);
    assert.equal(r.ok, true);
  });

  it("59. ConceptGuard akzeptiert 'Admin Control Plane'", () => {
    const r = checkConceptLanguage([{ id: "a3", text: "Admin Control Plane ist aktiv." }]);
    assert.equal(r.ok, true);
  });

  it("60. ConceptGuard akzeptiert 'CommandIntent'", () => {
    const r = checkConceptLanguage([{ id: "a4", text: "CommandIntent wurde erstellt." }]);
    assert.equal(r.ok, true);
  });

  it("61. ConceptGuard akzeptiert 'CommandLedger'", () => {
    const r = checkConceptLanguage([{ id: "a5", text: "CommandLedger wurde aktualisiert." }]);
    assert.equal(r.ok, true);
  });

  it("ConceptGuard akzeptiert 'Deep Search Foundation placeholder'", () => {
    const r = checkConceptLanguage([{ id: "a6", text: "Deep Search Foundation placeholder registriert." }]);
    assert.equal(r.ok, true);
  });

  it("ConceptGuard akzeptiert 'Read-only Worldblick'", () => {
    const r = checkConceptLanguage([{ id: "a7", text: "Read-only Worldblick ist erlaubt." }]);
    assert.equal(r.ok, true);
  });
});

// ---------------------------------------------------------------------------
// 11. Keine Runtime-Aktivitäten
// ---------------------------------------------------------------------------

describe("Ring 17 — Keine Runtime-Aktivitäten", () => {
  const registry = buildFeatureRegistry();

  it("62. Kein Feature wird durch Tests aktiviert", () => {
    for (const f of registry) {
      if (f.kind === "organ") assert.equal(f.enabled, false);
    }
  });

  it("63. Kein Organ wird implementiert", () => {
    const organs = registry.filter((f) => f.kind === "organ");
    for (const f of organs) {
      assert.equal(f.enabled, false);
      assert.equal(f.can_enable_now, false);
    }
  });

  it("64. Kein Event wird erzeugt", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"event_type"'));
  });

  it("65. Kein EventStore wird benötigt", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes("EventStore"));
  });

  it("66. Keine AI", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"ai"'));
  });

  it("67. Kein Postgres", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"db"'));
  });

  it("68. Kein Renderer", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"renderer"'));
  });

  it("69. Kein Scheduler", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"scheduler"'));
  });

  it("70. Keine UI", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = JSON.stringify(inspection);
    assert.ok(!json.includes('"ui"'));
  });
});

// ---------------------------------------------------------------------------
// 12. Regressions-Smoke-Test
// ---------------------------------------------------------------------------

describe("Ring 17 — Regression: bisherige Importe weiter funktionsfähig", () => {
  it("80. Alle bisherigen Tests bleiben grün — FeatureRegistry importierbar", () => {
    const registry = buildFeatureRegistry();
    assert.ok(registry.length >= 11);
  });

  it("AdminControlInspection liefert nicht-leer summary", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    assert.ok(inspection.summary.length > 0);
  });

  it("Kein Organ-Feature hat enabled true nach buildFeatureRegistry", () => {
    const organs = buildFeatureRegistry().filter((f) => f.kind === "organ");
    assert.ok(organs.every((f) => !f.enabled));
  });

  it("serializeAdminControlExport gibt gültiges JSON", () => {
    const inspection = buildAdminControlInspection(buildDanielRootAdmin());
    const json = serializeAdminControlExport(inspection);
    assert.doesNotThrow(() => JSON.parse(json));
  });

  it("DanielRoot Inspection: Organ-ActivationGates alle blocked", () => {
    const daniel = buildDanielRootAdmin();
    const inspection = buildAdminControlInspection(daniel);
    const organGates = inspection.activation_gates.filter((g) =>
      g.feature_id.endsWith("_feature")
    );
    for (const gate of organGates) {
      assert.equal(gate.blocked, true, `${gate.feature_id} sollte blocked sein`);
    }
  });
});
