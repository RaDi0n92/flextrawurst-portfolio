import type { ContinuityStatus } from "./continuity_score.ts";

export interface EntityContinuityDossier {
  slot_id: string;
  canonical_label: string;
  origin_account_ids: string[];
  origin_record_count: number;
  memory_candidate_count: number;
  speaker_drift_count: number;
  self_reference_count: number;
  admin_resonance_count: number;
  continuity_score: number;
  continuity_status: ContinuityStatus;
  can_start_as_live_entity: false;
  requires_start_decision: true;
}
