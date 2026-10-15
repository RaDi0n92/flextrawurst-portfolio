import type { EntityContinuityDossier } from "./entity_continuity_dossier.ts";
import type { SpeakerDriftMarker } from "./speaker_drift_marker.ts";
import type { MemoryCandidateModel } from "../memory_candidates/memory_candidate_model.ts";
import { computeContinuityScore } from "./continuity_score.ts";

export function buildEntityContinuityDossier(params: {
  slot_id: string;
  canonical_label: string;
  origin_account_ids: string[];
  origin_record_count: number;
  memory_candidates: MemoryCandidateModel[];
  speaker_drift_markers: SpeakerDriftMarker[];
  self_reference_count: number;
  admin_resonance_count: number;
}): EntityContinuityDossier {
  const {
    slot_id,
    canonical_label,
    origin_account_ids,
    origin_record_count,
    memory_candidates,
    speaker_drift_markers,
    self_reference_count,
    admin_resonance_count,
  } = params;

  const memory_candidate_count = memory_candidates.length;
  const speaker_drift_count = speaker_drift_markers.length;

  const score = computeContinuityScore({
    slot_id,
    origin_record_count,
    memory_candidate_count,
    speaker_drift_count,
    self_reference_count,
    admin_resonance_count,
  });

  return {
    slot_id,
    canonical_label,
    origin_account_ids,
    origin_record_count,
    memory_candidate_count,
    speaker_drift_count,
    self_reference_count,
    admin_resonance_count,
    continuity_score: score.raw_score,
    continuity_status: score.continuity_status,
    can_start_as_live_entity: false,
    requires_start_decision: true,
  };
}

export function buildAllContinuityDossiers(
  slotParams: Array<{
    slot_id: string;
    canonical_label: string;
    origin_account_ids: string[];
    origin_record_count: number;
    memory_candidates: MemoryCandidateModel[];
    speaker_drift_markers: SpeakerDriftMarker[];
    self_reference_count: number;
    admin_resonance_count: number;
  }>
): EntityContinuityDossier[] {
  return slotParams.map(buildEntityContinuityDossier);
}
