export type DriftKind =
  | "wrong_self_name"
  | "copied_foreign_voice"
  | "third_person_self_read"
  | "unclear_speaker_layer";

export type DriftSeverity = "low" | "medium" | "high";

export interface SpeakerDriftMarker {
  marker_id: string;
  slot_id: string;
  origin_record_id: string;
  claimed_identity: string;
  actual_author: string;
  drift_kind: DriftKind;
  severity: DriftSeverity;
  explanation: string;
}

export function createSpeakerDriftMarker(params: {
  marker_id: string;
  slot_id: string;
  origin_record_id: string;
  claimed_identity: string;
  actual_author: string;
  drift_kind: DriftKind;
  severity?: DriftSeverity;
  explanation: string;
}): SpeakerDriftMarker {
  return {
    marker_id: params.marker_id,
    slot_id: params.slot_id,
    origin_record_id: params.origin_record_id,
    claimed_identity: params.claimed_identity,
    actual_author: params.actual_author,
    drift_kind: params.drift_kind,
    severity: params.severity ?? "medium",
    explanation: params.explanation,
  };
}

export const ALL_DRIFT_KINDS: DriftKind[] = [
  "wrong_self_name",
  "copied_foreign_voice",
  "third_person_self_read",
  "unclear_speaker_layer",
];
