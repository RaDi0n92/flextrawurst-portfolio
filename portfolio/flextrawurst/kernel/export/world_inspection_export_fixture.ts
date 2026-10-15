import { buildWorldInspectionExport } from "./world_inspection_export_builder.ts";
import type { WorldInspectionExport } from "./world_inspection_export_model.ts";

export const FIXTURE_EXPORT_ID = "fixture-export-001";
export const FIXTURE_EXPORT_VERSION = "1.0.0";
export const FIXTURE_CREATED_AT = "2026-05-09T00:00:00.000Z";

export function buildWorldInspectionExportFixture(): WorldInspectionExport {
  return buildWorldInspectionExport({
    export_id: FIXTURE_EXPORT_ID,
    export_version: FIXTURE_EXPORT_VERSION,
    created_at: FIXTURE_CREATED_AT,
    spine_summary: {
      section_id: "spine",
      label: "Spine Summary",
      summary: "OS Spine: 2 Slots, 0 aktiviert, 0 live",
      item_count: 2,
      notes: [
        "Slots sind technische Traeger ohne Bewohner",
        "Kein Einzug vollzogen",
      ],
    },
    import_gate_summary: {
      section_id: "import_gate",
      label: "Import Gate Summary",
      summary: "Import Gate: dry-run only, keine Live-Importe",
      item_count: 0,
      notes: [
        "Kein echter Import ausgefuehrt",
        "Aktivierungsfirewall blockiert",
      ],
    },
    visual_meaning_summary: {
      section_id: "visual_meaning",
      label: "Visual Meaning Summary",
      summary: "3 VisualMeanings mit Herkunft, 0 dekorativ",
      item_count: 3,
      notes: [
        "Jedes VisualMeaning hat Weltgrund",
        "is_decorative: false bei allen",
      ],
    },
    replay_explanation_summary: {
      section_id: "replay_explanation",
      label: "Replay Explanation Summary",
      summary: "2 ReplayExplanations, keine neuen Events erzeugt",
      item_count: 2,
      notes: ["creates_new_events: false", "activates_slots: false"],
    },
    worldview_graph_summary: {
      section_id: "worldview_graph",
      label: "Worldview Graph Summary",
      summary: "4 Nodes, 3 Edges, kein Live-Zustand",
      item_count: 4,
      notes: ["Kein Renderer", "Nur Datenstruktur"],
    },
    origin_archive_summary: {
      section_id: "origin_archive",
      label: "Origin Archive Summary",
      summary:
        "5 Flarum-Herkunftsdatensaetze, is_live_flextrawurst_state: false",
      item_count: 5,
      notes: ["Flarum bleibt Vorphase", "can_create_events: false"],
    },
    memory_candidate_summary: {
      section_id: "memory_candidate",
      label: "Memory Candidate Summary",
      summary: "3 Erinnerungskandidaten, is_adopted_memory: false",
      item_count: 3,
      notes: [
        "Kandidaten sind keine Erinnerungen",
        "adoption_policy: not_decided",
      ],
    },
    continuity_dossier_summary: {
      section_id: "continuity_dossier",
      label: "Continuity Dossier Summary",
      summary: "2 Kontinuitaets-Dossiers, can_start_as_live_entity: false",
      item_count: 2,
      notes: [
        "Dossiers sind keine Biografien",
        "requires_start_decision: true",
      ],
    },
    world_start_readiness_summary: {
      section_id: "world_start_readiness",
      label: "World Start Readiness Summary",
      summary: "ready_for_activation: false, ready_for_ui: false",
      item_count: 1,
      notes: [
        "Kein Einzug",
        "Kein Weltstart vollzogen",
        "requires_admin_confirmation: true",
      ],
    },
    concept_guard_summary: {
      section_id: "concept_guard",
      label: "Concept Guard Summary",
      summary: "0 Verletzungen erkannt",
      item_count: 0,
      notes: ["Keine verbotenen Begriffe im Fixture"],
    },
    activation_firewall_summary: {
      section_id: "activation_firewall",
      label: "Activation Firewall Summary",
      summary: "Firewall: blocked, allowed_slot_ids: []",
      item_count: 0,
      notes: ["Kein Slot aktiviert", "Einzug strukturell blockiert"],
    },
    warnings: [
      "Kein echter Weltstart. Nur statischer Inspektion-Export.",
      "Keine AI-Ausfuehrung. Keine Aktivierung. Keine Migration.",
    ],
    next_human_decisions: [
      "Waehle Speicher-Policy fuer Erinnerungskandidaten.",
      "Waehle Roster-Policy fuer Slot-Auswahl.",
      "Bestatige als Admin vor jedem echten Weltstart.",
    ],
  });
}
