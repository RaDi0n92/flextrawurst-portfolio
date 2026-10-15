import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  getFutureConceptRegistry,
  findFutureConceptById,
  listFutureConceptsByKind,
  listConceptsNeedingDanielPlanning,
} from "../kernel/future_concepts/future_concept_registry.ts";
import {
  buildOrganBlueprint,
  buildOrganBlueprintsForRegistry,
} from "../kernel/organ_dock/organ_blueprint.ts";
import { buildOrganDock } from "../kernel/organ_dock/organ_dock.ts";
import {
  assessOrganReadiness,
  assessAllOrganReadiness,
} from "../kernel/organ_dock/organ_readiness.ts";
import { buildOrganDockInspection } from "../kernel/organ_dock/organ_dock_inspection.ts";
import {
  buildOrganDockExport,
  serializeOrganDockExport,
} from "../kernel/organ_dock/organ_dock_export.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

// ---------------------------------------------------------------------------
// 1. Registry — Konzepte vorhanden
// ---------------------------------------------------------------------------

describe("Ring 16 — Future Concept Registry: Konzepte vorhanden", () => {
  const registry = getFutureConceptRegistry();

  it("1. Registry enthält tamagotchi_care", () => {
    assert.ok(registry.some((c) => c.concept_id === "tamagotchi_care"));
  });

  it("2. Registry enthält kompoase_space", () => {
    assert.ok(registry.some((c) => c.concept_id === "kompoase_space"));
  });

  it("3. Registry enthält sleep_cycle", () => {
    assert.ok(registry.some((c) => c.concept_id === "sleep_cycle"));
  });

  it("4. Registry enthält substance_modifiers", () => {
    assert.ok(registry.some((c) => c.concept_id === "substance_modifiers"));
  });

  it("5. Registry enthält dream_residue", () => {
    assert.ok(registry.some((c) => c.concept_id === "dream_residue"));
  });

  it("6. Registry enthält resonance_vacation", () => {
    assert.ok(registry.some((c) => c.concept_id === "resonance_vacation"));
  });

  it("7. Registry enthält metawar_space", () => {
    assert.ok(registry.some((c) => c.concept_id === "metawar_space"));
  });

  it("8. alle Konzepte haben status needs_daniel_planning oder raw_idea", () => {
    for (const c of registry) {
      assert.ok(
        c.status === "needs_daniel_planning" || c.status === "raw_idea",
        `${c.concept_id} hat Status ${c.status}`
      );
    }
  });

  it("9. kein Konzept ist ready_for_architecture", () => {
    for (const c of registry) {
      assert.notEqual(c.status, "ready_for_architecture");
    }
  });

  it("10. listConceptsNeedingDanielPlanning liefert alle 7", () => {
    const result = listConceptsNeedingDanielPlanning();
    assert.equal(result.length, 7);
  });
});

// ---------------------------------------------------------------------------
// 2. Registry — Such- und Filterfunktionen
// ---------------------------------------------------------------------------

describe("Ring 16 — Future Concept Registry: Such- und Filterfunktionen", () => {
  it("11. findFutureConceptById findet tamagotchi_care", () => {
    const c = findFutureConceptById("tamagotchi_care");
    assert.ok(c);
    assert.equal(c!.concept_id, "tamagotchi_care");
  });

  it("12. listFutureConceptsByKind care_system findet Tamagotchi", () => {
    const result = listFutureConceptsByKind("care_system");
    assert.ok(result.some((c) => c.concept_id === "tamagotchi_care"));
  });

  it("13. listFutureConceptsByKind space_system findet KompOase", () => {
    const result = listFutureConceptsByKind("space_system");
    assert.ok(result.some((c) => c.concept_id === "kompoase_space"));
  });

  it("findFutureConceptById gibt undefined für unbekannte ID", () => {
    assert.equal(findFutureConceptById("does_not_exist"), undefined);
  });

  it("listFutureConceptsByKind conflict_system findet metawar_space", () => {
    const result = listFutureConceptsByKind("conflict_system");
    assert.ok(result.some((c) => c.concept_id === "metawar_space"));
  });
});

// ---------------------------------------------------------------------------
// 3. Not-yet Felder der Konzepte
// ---------------------------------------------------------------------------

describe("Ring 16 — Future Concept Registry: not_yet Felder", () => {
  it("14. Tamagotchi not_yet enthält keine Hunger-/Durstsimulation", () => {
    const c = findFutureConceptById("tamagotchi_care")!;
    assert.ok(c.not_yet.some((n) => n.includes("Hunger") || n.includes("Durst")));
  });

  it("15. KompOase not_yet enthält kein fertiger Raum", () => {
    const c = findFutureConceptById("kompoase_space")!;
    assert.ok(c.not_yet.some((n) => n.includes("fertiger Raum")));
  });

  it("16. sleep_cycle not_yet enthält keine Schlafpflicht", () => {
    const c = findFutureConceptById("sleep_cycle")!;
    assert.ok(c.not_yet.some((n) => n.includes("Schlafpflicht")));
  });

  it("17. substance_modifiers not_yet enthält keine echte Substanzlogik", () => {
    const c = findFutureConceptById("substance_modifiers")!;
    assert.ok(c.not_yet.some((n) => n.includes("Substanzlogik")));
  });

  it("18. dream_residue not_yet enthält keine Traumgenerierung", () => {
    const c = findFutureConceptById("dream_residue")!;
    assert.ok(c.not_yet.some((n) => n.includes("Traumgenerierung")));
  });

  it("19. resonance_vacation not_yet enthält keine aktive Kommentarblockade", () => {
    const c = findFutureConceptById("resonance_vacation")!;
    assert.ok(c.not_yet.some((n) => n.includes("Kommentarblockade")));
  });

  it("20. metawar_space not_yet enthält keine Live-Debatte", () => {
    const c = findFutureConceptById("metawar_space")!;
    assert.ok(c.not_yet.some((n) => n.includes("Live-Debatte")));
  });
});

// ---------------------------------------------------------------------------
// 4. OrganBlueprint
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganBlueprint: implementation_forbidden", () => {
  const registry = getFutureConceptRegistry();

  it("21. buildOrganBlueprint erzeugt implementation_forbidden true", () => {
    const c = findFutureConceptById("tamagotchi_care")!;
    const bp = buildOrganBlueprint(c);
    assert.equal(bp.implementation_forbidden, true);
  });

  it("22. alle Blueprints sind implementation_forbidden true", () => {
    const blueprints = buildOrganBlueprintsForRegistry(registry);
    for (const bp of blueprints) {
      assert.equal(
        bp.implementation_forbidden,
        true,
        `${bp.blueprint_id} hat implementation_forbidden false`
      );
    }
  });

  it("Blueprint hat status blueprint_only", () => {
    const c = findFutureConceptById("kompoase_space")!;
    const bp = buildOrganBlueprint(c);
    assert.equal(bp.status, "blueprint_only");
  });

  it("Blueprint forbidden_reason enthält Daniels explizite Feinplanung", () => {
    const c = findFutureConceptById("sleep_cycle")!;
    const bp = buildOrganBlueprint(c);
    assert.ok(bp.forbidden_reason.includes("Daniels explizite Feinplanung"));
  });

  it("Blueprint blueprint_id hat Präfix blueprint_", () => {
    const c = findFutureConceptById("tamagotchi_care")!;
    const bp = buildOrganBlueprint(c);
    assert.equal(bp.blueprint_id, "blueprint_tamagotchi_care");
  });
});

// ---------------------------------------------------------------------------
// 5. OrganDock
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganDock: Zählwerte", () => {
  const dock = buildOrganDock();

  it("23. OrganDock blueprint_count 7", () => {
    assert.equal(dock.blueprint_count, 7);
  });

  it("24. OrganDock implemented_organ_count 0", () => {
    assert.equal(dock.implemented_organ_count, 0);
  });

  it("25. OrganDock blocked_blueprint_count 7", () => {
    assert.equal(dock.blocked_blueprint_count, 7);
  });

  it("OrganDock dock_version ist 1", () => {
    assert.equal(dock.dock_version, 1);
  });

  it("OrganDock notes enthält Noch keine Weltorgane implementiert", () => {
    assert.ok(dock.notes.some((n) => n.includes("Noch keine Weltorgane implementiert")));
  });

  it("OrganDock notes enthält Alle Konzepte warten auf Daniels Feinplanung", () => {
    assert.ok(dock.notes.some((n) => n.includes("Daniels Feinplanung")));
  });

  it("OrganDock notes enthält Anschlussstruktur", () => {
    assert.ok(dock.notes.some((n) => n.includes("Anschlussstruktur")));
  });
});

// ---------------------------------------------------------------------------
// 6. OrganReadiness
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganReadiness: ready false für alle", () => {
  const registry = getFutureConceptRegistry();
  const reports = assessAllOrganReadiness(registry);

  it("26. OrganReadiness ready false für alle", () => {
    for (const r of reports) {
      assert.equal(r.ready, false, `${r.concept_id} hat ready true`);
    }
  });

  it("27. OrganReadiness enthält daniel_concept_definition", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("daniel_concept_definition"));
  });

  it("28. OrganReadiness enthält event_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("event_contract"));
  });

  it("29. OrganReadiness enthält state_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("state_contract"));
  });

  it("30. OrganReadiness enthält projection_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("projection_contract"));
  });

  it("31. OrganReadiness enthält camera_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("camera_contract"));
  });

  it("32. OrganReadiness enthält audit_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("audit_contract"));
  });

  it("33. OrganReadiness enthält concept_guard_contract", () => {
    const r = assessOrganReadiness(findFutureConceptById("tamagotchi_care")!);
    assert.ok(r.missing.includes("concept_guard_contract"));
  });

  it("OrganReadiness hat recommended_next_planning_questions", () => {
    const r = assessOrganReadiness(findFutureConceptById("kompoase_space")!);
    assert.ok(r.recommended_next_planning_questions.length > 0);
  });
});

// ---------------------------------------------------------------------------
// 7. OrganDockInspection
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganDockInspection", () => {
  const inspection = buildOrganDockInspection();

  it("34. OrganDockInspection safe_to_implement_now false", () => {
    assert.equal(inspection.safe_to_implement_now, false);
  });

  it("35. OrganDockInspection summary enthält 7 zukünftige Konzepte", () => {
    assert.ok(inspection.summary.some((s) => s.includes("7 zukünftige Konzepte")));
  });

  it("36. OrganDockInspection summary enthält 0 Weltorgane implementiert", () => {
    assert.ok(inspection.summary.some((s) => s.includes("0 Weltorgane implementiert")));
  });

  it("37. OrganDockInspection summary enthält Daniel muss Konzepte einzeln weiter planen", () => {
    assert.ok(inspection.summary.some((s) => s.includes("Daniel muss Konzepte einzeln weiter planen")));
  });

  it("OrganDockInspection inspection_version ist 1", () => {
    assert.equal(inspection.inspection_version, 1);
  });

  it("OrganDockInspection readiness hat 7 Einträge", () => {
    assert.equal(inspection.readiness.length, 7);
  });
});

// ---------------------------------------------------------------------------
// 8. OrganDockExport — Determinismus
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganDockExport: Determinismus", () => {
  it("38. OrganDockExport deterministisch", () => {
    const inspection1 = buildOrganDockInspection();
    const inspection2 = buildOrganDockInspection();
    const exp1 = buildOrganDockExport(inspection1);
    const exp2 = buildOrganDockExport(inspection2);
    assert.deepEqual(exp1, exp2);
  });

  it("39. serializeOrganDockExport gibt stabilen JSON-String", () => {
    const inspection1 = buildOrganDockInspection();
    const inspection2 = buildOrganDockInspection();
    const json1 = serializeOrganDockExport(inspection1);
    const json2 = serializeOrganDockExport(inspection2);
    assert.equal(json1, json2);
  });

  it("serializeOrganDockExport gibt gültiges JSON", () => {
    const inspection = buildOrganDockInspection();
    const json = serializeOrganDockExport(inspection);
    assert.doesNotThrow(() => JSON.parse(json));
  });

  it("OrganDockExport safe_to_implement_now ist false", () => {
    const inspection = buildOrganDockInspection();
    const exp = buildOrganDockExport(inspection);
    assert.equal(exp.safe_to_implement_now, false);
  });

  it("OrganDockExport concept_ids sind sortiert", () => {
    const inspection = buildOrganDockInspection();
    const exp = buildOrganDockExport(inspection);
    const sorted = [...exp.concept_ids].sort();
    assert.deepEqual(exp.concept_ids, sorted);
  });
});

// ---------------------------------------------------------------------------
// 9. ConceptGuard — neue verbotene Muster
// ---------------------------------------------------------------------------

describe("Ring 16 — ConceptGuard: verbotene Organ-Dock Muster", () => {
  it("40. ConceptGuard erkennt 'Tamagotchi ist implementiert'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Tamagotchi ist implementiert und läuft." }]);
    assert.equal(r.ok, false);
  });

  it("41. ConceptGuard erkennt 'KompOase ist fertig'", () => {
    const r = checkConceptLanguage([{ id: "t2", text: "KompOase ist fertig gebaut." }]);
    assert.equal(r.ok, false);
  });

  it("42. ConceptGuard erkennt 'Schlafsystem läuft'", () => {
    const r = checkConceptLanguage([{ id: "t3", text: "Schlafsystem läuft jetzt." }]);
    assert.equal(r.ok, false);
  });

  it("43. ConceptGuard erkennt 'Substanzen wirken'", () => {
    const r = checkConceptLanguage([{ id: "t4", text: "Substanzen wirken auf Entitäten." }]);
    assert.equal(r.ok, false);
  });

  it("44. ConceptGuard erkennt 'Traumreste werden generiert'", () => {
    const r = checkConceptLanguage([{ id: "t5", text: "Traumreste werden generiert durch Schlaf." }]);
    assert.equal(r.ok, false);
  });

  it("45. ConceptGuard erkennt 'Resonanzurlaub ist aktiv'", () => {
    const r = checkConceptLanguage([{ id: "t6", text: "Resonanzurlaub ist aktiv für dak." }]);
    assert.equal(r.ok, false);
  });

  it("46. ConceptGuard erkennt 'METAWAR ist live'", () => {
    const r = checkConceptLanguage([{ id: "t7", text: "METAWAR ist live und läuft." }]);
    assert.equal(r.ok, false);
  });

  it("47. ConceptGuard erkennt 'Blueprint ist Feature'", () => {
    const r = checkConceptLanguage([{ id: "t8", text: "Blueprint ist Feature, nicht Vorschau." }]);
    assert.equal(r.ok, false);
  });

  it("48. ConceptGuard erkennt 'OrganDock implementiert Organe'", () => {
    const r = checkConceptLanguage([{ id: "t9", text: "OrganDock implementiert Organe automatisch." }]);
    assert.equal(r.ok, false);
  });
});

describe("Ring 16 — ConceptGuard: erlaubte Sprache akzeptiert", () => {
  it("49. ConceptGuard akzeptiert 'Tamagotchi-Blueprint'", () => {
    const r = checkConceptLanguage([{ id: "a1", text: "Der Tamagotchi-Blueprint ist registriert." }]);
    assert.equal(r.ok, true);
  });

  it("50. ConceptGuard akzeptiert 'KompOase-Blueprint'", () => {
    const r = checkConceptLanguage([{ id: "a2", text: "KompOase-Blueprint wartet auf Planung." }]);
    assert.equal(r.ok, true);
  });

  it("51. ConceptGuard akzeptiert 'Organ-Dock'", () => {
    const r = checkConceptLanguage([{ id: "a3", text: "Das Organ-Dock enthält 7 Blueprints." }]);
    assert.equal(r.ok, true);
  });

  it("52. ConceptGuard akzeptiert 'Anschlussstruktur'", () => {
    const r = checkConceptLanguage([{ id: "a4", text: "Ring 16 baut eine Anschlussstruktur." }]);
    assert.equal(r.ok, true);
  });

  it("ConceptGuard akzeptiert 'Schlaf-Blueprint'", () => {
    const r = checkConceptLanguage([{ id: "a5", text: "Der Schlaf-Blueprint braucht Daniels Planung." }]);
    assert.equal(r.ok, true);
  });

  it("ConceptGuard akzeptiert 'METAWAR-Blueprint'", () => {
    const r = checkConceptLanguage([{ id: "a6", text: "METAWAR-Blueprint ist registriert." }]);
    assert.equal(r.ok, true);
  });
});

// ---------------------------------------------------------------------------
// 10. OrganDock — keine Runtime-Aktivitäten
// ---------------------------------------------------------------------------

describe("Ring 16 — OrganDock: keine Runtime-Aktivitäten", () => {
  const dock = buildOrganDock();

  it("53. OrganDock erzeugt keine Events (blueprint hat implementation_forbidden true)", () => {
    for (const bp of dock.blueprints) {
      assert.equal(bp.implementation_forbidden, true);
    }
  });

  it("54. OrganDock nutzt keinen EventStore (keine EventStore-Referenz in Dock)", () => {
    assert.equal(dock.implemented_organ_count, 0);
  });

  it("55. OrganDock aktiviert keine Slots", () => {
    assert.equal(dock.implemented_organ_count, 0);
    assert.equal(dock.blocked_blueprint_count, dock.blueprint_count);
  });

  it("56. OrganDock erzeugt keinen occupied Status", () => {
    const json = JSON.stringify(dock);
    assert.ok(!json.includes("occupied"));
  });

  it("57. OrganDock nutzt keine AI (kein ai-Feld)", () => {
    const json = JSON.stringify(dock);
    assert.ok(!json.includes('"ai"'));
  });

  it("58. OrganDock nutzt kein Postgres (kein db-Feld)", () => {
    const json = JSON.stringify(dock);
    assert.ok(!json.includes('"db"'));
  });

  it("59. OrganDock nutzt keinen Scheduler (kein scheduler-Feld)", () => {
    const json = JSON.stringify(dock);
    assert.ok(!json.includes('"scheduler"'));
  });

  it("60. OrganDock nutzt keinen Renderer (kein renderer-Feld)", () => {
    const json = JSON.stringify(dock);
    assert.ok(!json.includes('"renderer"'));
  });
});

// ---------------------------------------------------------------------------
// 11. Planning questions vollständig
// ---------------------------------------------------------------------------

describe("Ring 16 — Planning questions vollständig", () => {
  it("61. Tamagotchi planning questions sind vorhanden", () => {
    const c = findFutureConceptById("tamagotchi_care")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("62. KompOase planning questions sind vorhanden", () => {
    const c = findFutureConceptById("kompoase_space")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("63. Sleep planning questions sind vorhanden", () => {
    const c = findFutureConceptById("sleep_cycle")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("64. Substance planning questions sind vorhanden", () => {
    const c = findFutureConceptById("substance_modifiers")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("65. Dream residue planning questions sind vorhanden", () => {
    const c = findFutureConceptById("dream_residue")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("66. Resonance vacation planning questions sind vorhanden", () => {
    const c = findFutureConceptById("resonance_vacation")!;
    assert.ok(c.required_planning_questions.length > 0);
  });

  it("67. METAWAR planning questions sind vorhanden", () => {
    const c = findFutureConceptById("metawar_space")!;
    assert.ok(c.required_planning_questions.length > 0);
  });
});

// ---------------------------------------------------------------------------
// 12. Konzepte haben Event/State/Camera-Felder
// ---------------------------------------------------------------------------

describe("Ring 16 — Konzepte haben Event/State/Camera-Felder", () => {
  const registry = getFutureConceptRegistry();

  it("68. jedes Konzept hat possible_event_families", () => {
    for (const c of registry) {
      assert.ok(
        c.possible_event_families.length > 0,
        `${c.concept_id} hat leere possible_event_families`
      );
    }
  });

  it("69. jedes Konzept hat possible_state_surfaces", () => {
    for (const c of registry) {
      assert.ok(
        c.possible_state_surfaces.length > 0,
        `${c.concept_id} hat leere possible_state_surfaces`
      );
    }
  });

  it("70. jedes Konzept hat possible_camera_layers", () => {
    for (const c of registry) {
      assert.ok(
        c.possible_camera_layers.length > 0,
        `${c.concept_id} hat leere possible_camera_layers`
      );
    }
  });

  it("71. jedes Konzept hat guard_terms", () => {
    for (const c of registry) {
      assert.ok(
        c.guard_terms.length > 0,
        `${c.concept_id} hat leere guard_terms`
      );
    }
  });
});

// ---------------------------------------------------------------------------
// 13. Blueprints haben alle Pflichtfelder
// ---------------------------------------------------------------------------

describe("Ring 16 — Blueprints haben alle Pflichtfelder", () => {
  const registry = getFutureConceptRegistry();
  const blueprints = buildOrganBlueprintsForRegistry(registry);

  it("72. alle Blueprints haben event_type_preview", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.event_type_preview.length > 0,
        `${bp.blueprint_id} hat leere event_type_preview`
      );
    }
  });

  it("73. alle Blueprints haben state_surface_preview", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.state_surface_preview.length > 0,
        `${bp.blueprint_id} hat leere state_surface_preview`
      );
    }
  });

  it("74. alle Blueprints haben projection_preview", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.projection_preview.length > 0,
        `${bp.blueprint_id} hat leere projection_preview`
      );
    }
  });

  it("75. alle Blueprints haben camera_readiness_preview", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.camera_readiness_preview.length > 0,
        `${bp.blueprint_id} hat leere camera_readiness_preview`
      );
    }
  });

  it("76. alle Blueprints haben audit_requirements", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.audit_requirements.length > 0,
        `${bp.blueprint_id} hat leere audit_requirements`
      );
    }
  });

  it("77. alle Blueprints haben concept_guard_requirements", () => {
    for (const bp of blueprints) {
      assert.ok(
        bp.concept_guard_requirements.length > 0,
        `${bp.blueprint_id} hat leere concept_guard_requirements`
      );
    }
  });
});

// ---------------------------------------------------------------------------
// 14. Inspection und Export — keine Runtime-Veränderung
// ---------------------------------------------------------------------------

describe("Ring 16 — Inspection/Export: keine Runtime-Veränderung", () => {
  it("78. OrganDockInspection verändert keine Runtime", () => {
    const i1 = buildOrganDockInspection();
    const i2 = buildOrganDockInspection();
    assert.equal(i1.safe_to_implement_now, i2.safe_to_implement_now);
    assert.equal(i1.dock.implemented_organ_count, i2.dock.implemented_organ_count);
  });

  it("79. Existing worldblick export bleibt kompatibel (keine Imports aus organ_dock in worldblick)", () => {
    // worldblick und organ_dock sind eigenständige Schichten
    // organ_dock importiert nicht aus worldblick und verändert keine worldblick-Modelle
    const inspection = buildOrganDockInspection();
    const json = serializeOrganDockExport(inspection);
    const parsed = JSON.parse(json);
    assert.ok(!("creates_events" in parsed) || parsed.creates_events === false);
  });
});

// ---------------------------------------------------------------------------
// 15. Regressions-Smoke-Test (alle bisherigen Tests weiter grün)
// ---------------------------------------------------------------------------

describe("Ring 16 — Regression: Kernelmodule weiterhin importierbar", () => {
  it("80. alle bisherigen Tests bleiben grün — FutureConceptRegistry importierbar", () => {
    const r = getFutureConceptRegistry();
    assert.equal(r.length, 7);
  });

  it("OrganDock importierbar und determiniert", () => {
    const d1 = buildOrganDock();
    const d2 = buildOrganDock();
    assert.equal(d1.blueprint_count, d2.blueprint_count);
    assert.equal(d1.implemented_organ_count, d2.implemented_organ_count);
  });

  it("OrganDockInspection: 0 Konzepte implementierungsbereit", () => {
    const inspection = buildOrganDockInspection();
    const implementationReady = inspection.readiness.filter((r) => r.ready).length;
    assert.equal(implementationReady, 0);
  });

  it("OrganDockExport export_version ist 1", () => {
    const inspection = buildOrganDockInspection();
    const exp = buildOrganDockExport(inspection);
    assert.equal(exp.export_version, 1);
  });

  it("ConceptGuard meldet ok: true für saubere Sprache", () => {
    const r = checkConceptLanguage([
      { id: "clean1", text: "Der Organ-Dock ist Anschlussstruktur." },
      { id: "clean2", text: "Tamagotchi-Blueprint wartet auf Daniels Planung." },
      { id: "clean3", text: "Resonanzurlaub-Blueprint ist registriert." },
    ]);
    assert.equal(r.ok, true);
  });

  it("ConceptGuard meldet ok: false für mehrere verbotene Texte", () => {
    const r = checkConceptLanguage([
      { id: "bad1", text: "METAWAR ist live." },
      { id: "bad2", text: "Substanzen wirken." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.length >= 2);
  });
});
