import type { MemoryCandidateModel } from "./memory_candidate_model.ts";

export interface MemoryAdoptionPreview {
  preview_id: string;
  candidates: MemoryCandidateModel[];
  is_adoption: false;
  requires_start_decision: true;
  preview_note: string;
}

export function buildMemoryAdoptionPreview(
  preview_id: string,
  candidates: MemoryCandidateModel[]
): MemoryAdoptionPreview {
  return {
    preview_id,
    candidates,
    is_adoption: false,
    requires_start_decision: true,
    preview_note:
      "MemoryAdoptionPreview ist keine Adoption. Kein Kandidat wird übernommen.",
  };
}
