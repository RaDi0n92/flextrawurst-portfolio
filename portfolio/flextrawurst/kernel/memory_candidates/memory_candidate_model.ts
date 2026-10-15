export type CandidateKind =
  | "self_description"
  | "relationship_trace"
  | "concept_line"
  | "speaker_drift"
  | "admin_resonance"
  | "system_boundary";

export type AdoptionPolicy = "not_decided";

export interface MemoryCandidateModel {
  memory_candidate_id: string;
  origin_record_ids: string[];
  slot_id: string;
  candidate_kind: CandidateKind;
  candidate_text: string;
  evidence_count: number;
  confidence: number;
  adoption_policy: AdoptionPolicy;
  is_adopted_memory: false;
  requires_start_decision: true;
}

export const ALL_CANDIDATE_KINDS: CandidateKind[] = [
  "self_description",
  "relationship_trace",
  "concept_line",
  "speaker_drift",
  "admin_resonance",
  "system_boundary",
];
