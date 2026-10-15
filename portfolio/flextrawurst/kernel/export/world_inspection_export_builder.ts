import type { WorldInspectionExport, ExportSection } from "./world_inspection_export_model.ts";

export interface WorldInspectionExportParams {
  export_id: string;
  export_version: string;
  created_at: string;
  spine_summary: ExportSection;
  import_gate_summary: ExportSection;
  visual_meaning_summary: ExportSection;
  replay_explanation_summary: ExportSection;
  worldview_graph_summary: ExportSection;
  origin_archive_summary: ExportSection;
  memory_candidate_summary: ExportSection;
  continuity_dossier_summary: ExportSection;
  world_start_readiness_summary: ExportSection;
  concept_guard_summary: ExportSection;
  activation_firewall_summary: ExportSection;
  warnings?: string[];
  next_human_decisions?: string[];
}

export function buildWorldInspectionExport(
  params: WorldInspectionExportParams
): WorldInspectionExport {
  const sections: ExportSection[] = [
    params.spine_summary,
    params.import_gate_summary,
    params.visual_meaning_summary,
    params.replay_explanation_summary,
    params.worldview_graph_summary,
    params.origin_archive_summary,
    params.memory_candidate_summary,
    params.continuity_dossier_summary,
    params.world_start_readiness_summary,
    params.concept_guard_summary,
    params.activation_firewall_summary,
  ];

  return {
    export_id: params.export_id,
    export_version: params.export_version,
    created_at: params.created_at,
    is_read_only: true,
    creates_events: false,
    activates_slots: false,
    is_live_flextrawurst_state: false,
    origin_layer: "inspection_export",
    sections,
    warnings: params.warnings ?? [],
    next_human_decisions: params.next_human_decisions ?? [],
  };
}
