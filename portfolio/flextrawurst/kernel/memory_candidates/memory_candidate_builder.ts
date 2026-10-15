import type { MemoryCandidateModel, CandidateKind } from "./memory_candidate_model.ts";

export function buildMemoryCandidate(params: {
  memory_candidate_id: string;
  origin_record_ids: string[];
  slot_id: string;
  candidate_kind: CandidateKind;
  candidate_text: string;
  evidence_count?: number;
  confidence?: number;
}): MemoryCandidateModel {
  return {
    memory_candidate_id: params.memory_candidate_id,
    origin_record_ids: params.origin_record_ids,
    slot_id: params.slot_id,
    candidate_kind: params.candidate_kind,
    candidate_text: params.candidate_text,
    evidence_count: params.evidence_count ?? 1,
    confidence: params.confidence ?? 0.5,
    adoption_policy: "not_decided",
    is_adopted_memory: false,
    requires_start_decision: true,
  };
}
