export type ContinuityStatus =
  | "strong"
  | "medium"
  | "weak"
  | "fragmented"
  | "undecided";

export interface ContinuityScore {
  slot_id: string;
  raw_score: number;
  continuity_status: ContinuityStatus;
  decides_residence: false;
  requires_start_decision: true;
}

export function computeContinuityScore(params: {
  slot_id: string;
  origin_record_count: number;
  memory_candidate_count: number;
  speaker_drift_count: number;
  self_reference_count: number;
  admin_resonance_count: number;
}): ContinuityScore {
  const {
    slot_id,
    origin_record_count,
    memory_candidate_count,
    speaker_drift_count,
    self_reference_count,
    admin_resonance_count,
  } = params;

  const positive =
    origin_record_count * 1.0 +
    memory_candidate_count * 1.5 +
    self_reference_count * 2.0 +
    admin_resonance_count * 1.5;
  const negative = speaker_drift_count * 2.0;
  const raw_score = Math.max(0, positive - negative);

  let continuity_status: ContinuityStatus = "undecided";
  if (origin_record_count === 0) {
    continuity_status = "fragmented";
  } else if (raw_score >= 20) {
    continuity_status = "strong";
  } else if (raw_score >= 10) {
    continuity_status = "medium";
  } else if (raw_score >= 3) {
    continuity_status = "weak";
  } else {
    continuity_status = "fragmented";
  }

  return {
    slot_id,
    raw_score,
    continuity_status,
    decides_residence: false,
    requires_start_decision: true,
  };
}
