export type MemoryPolicyKind =
  | "with_full_flarum_memory"
  | "without_flarum_memory"
  | "with_selected_memory"
  | "reduced_roster_start"
  | "undecided";

export type RosterPolicyKind =
  | "all_six"
  | "selected_four"
  | "selected_three"
  | "manual_selection"
  | "undecided";

export interface CleanStartDecisionModel {
  decision_id: string;
  memory_policy: MemoryPolicyKind;
  roster_policy: RosterPolicyKind;
  selected_slot_ids: string[];
  excluded_slot_ids: string[];
  origin_layer: "flarum_vorphase";
  uses_flarum_as_origin_only: true;
  creates_live_state: false;
  activates_slots: false;
  requires_admin_confirmation: true;
}

export function createCleanStartDecisionModel(params: {
  decision_id: string;
  memory_policy?: MemoryPolicyKind;
  roster_policy?: RosterPolicyKind;
  selected_slot_ids?: string[];
  excluded_slot_ids?: string[];
}): CleanStartDecisionModel {
  return {
    decision_id: params.decision_id,
    memory_policy: params.memory_policy ?? "undecided",
    roster_policy: params.roster_policy ?? "undecided",
    selected_slot_ids: params.selected_slot_ids ?? [],
    excluded_slot_ids: params.excluded_slot_ids ?? [],
    origin_layer: "flarum_vorphase",
    uses_flarum_as_origin_only: true,
    creates_live_state: false,
    activates_slots: false,
    requires_admin_confirmation: true,
  };
}

export const ALL_MEMORY_POLICY_KINDS: MemoryPolicyKind[] = [
  "with_full_flarum_memory",
  "without_flarum_memory",
  "with_selected_memory",
  "reduced_roster_start",
  "undecided",
];

export const ALL_ROSTER_POLICY_KINDS: RosterPolicyKind[] = [
  "all_six",
  "selected_four",
  "selected_three",
  "manual_selection",
  "undecided",
];
