import type { FlarumOriginArchive } from "../origin_archive/flarum_origin_archive.ts";
import type { MemoryCandidateModel } from "../memory_candidates/memory_candidate_model.ts";
import type { EntityContinuityDossier } from "../continuity/entity_continuity_dossier.ts";
import type { StartDecisionPreview } from "../start_decision/start_decision_preview.ts";

export interface WorldStartReadinessPack {
  pack_id: string;
  origin_archive_count: number;
  memory_candidate_count: number;
  continuity_dossier_count: number;
  start_decision_options: StartDecisionPreview[];
  recommended_next_human_decision: string;
  ready_for_clean_start: false;
  ready_for_memory_adoption: false;
  ready_for_roster_reduction_decision: true;
  ready_for_activation: false;
  ready_for_ui: false;
  requires_admin_confirmation: true;
}

export function buildWorldStartReadinessPack(params: {
  pack_id: string;
  archive: FlarumOriginArchive;
  memory_candidates: MemoryCandidateModel[];
  continuity_dossiers: EntityContinuityDossier[];
  start_decision_options: StartDecisionPreview[];
}): WorldStartReadinessPack {
  return {
    pack_id: params.pack_id,
    origin_archive_count: params.archive.records.length,
    memory_candidate_count: params.memory_candidates.length,
    continuity_dossier_count: params.continuity_dossiers.length,
    start_decision_options: params.start_decision_options,
    recommended_next_human_decision:
      "Wähle Speicher-Policy und Roster-Policy. Bestätige als Admin. Kein Schritt wird automatisch vollzogen.",
    ready_for_clean_start: false,
    ready_for_memory_adoption: false,
    ready_for_roster_reduction_decision: true,
    ready_for_activation: false,
    ready_for_ui: false,
    requires_admin_confirmation: true,
  };
}
