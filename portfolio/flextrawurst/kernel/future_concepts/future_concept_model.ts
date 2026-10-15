export type FutureConceptKind =
  | "care_system"
  | "space_system"
  | "runtime_state_system"
  | "modifier_system"
  | "artifact_system"
  | "policy_system"
  | "conflict_system";

export type FutureConceptStatus =
  | "raw_idea"
  | "blueprint"
  | "needs_daniel_planning"
  | "ready_for_architecture"
  | "blocked_from_implementation"
  | "implemented";

export interface FutureConcept {
  concept_id: string;
  label: string;
  kind: FutureConceptKind;
  status: FutureConceptStatus;
  short_description: string;
  not_yet: string[];
  must_not_confuse_with: string[];
  required_planning_questions: string[];
  possible_event_families: string[];
  possible_state_surfaces: string[];
  possible_camera_layers: string[];
  guard_terms: string[];
}
