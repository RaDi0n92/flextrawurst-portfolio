import type { MemoryCandidateModel } from "./memory_candidate_model.ts";

export type FilterPolicy =
  | "include_all"
  | "exclude_speaker_drift"
  | "only_self_descriptions"
  | "only_admin_resonance"
  | "only_high_confidence"
  | "manual_selection";

export function filterMemoryCandidates(
  candidates: MemoryCandidateModel[],
  policy: FilterPolicy,
  manual_ids?: string[]
): MemoryCandidateModel[] {
  switch (policy) {
    case "include_all":
      return candidates.slice();
    case "exclude_speaker_drift":
      return candidates.filter((c) => c.candidate_kind !== "speaker_drift");
    case "only_self_descriptions":
      return candidates.filter((c) => c.candidate_kind === "self_description");
    case "only_admin_resonance":
      return candidates.filter((c) => c.candidate_kind === "admin_resonance");
    case "only_high_confidence":
      return candidates.filter((c) => c.confidence >= 0.8);
    case "manual_selection":
      return candidates.filter((c) =>
        (manual_ids ?? []).includes(c.memory_candidate_id)
      );
  }
}
