import type { FutureConcept } from "../future_concepts/future_concept_model.ts";

export interface OrganBlueprint {
  blueprint_id: string;
  concept_id: string;
  label: string;
  status: "blueprint_only" | "blocked_until_planned" | "ready_for_future_architecture";
  event_type_preview: string[];
  state_surface_preview: string[];
  projection_preview: string[];
  camera_readiness_preview: string[];
  audit_requirements: string[];
  concept_guard_requirements: string[];
  implementation_forbidden: boolean;
  forbidden_reason: string;
}

export function buildOrganBlueprint(concept: FutureConcept): OrganBlueprint {
  return {
    blueprint_id: `blueprint_${concept.concept_id}`,
    concept_id: concept.concept_id,
    label: concept.label,
    status: "blueprint_only",
    event_type_preview: concept.possible_event_families,
    state_surface_preview: concept.possible_state_surfaces,
    projection_preview: concept.possible_state_surfaces.map(
      (s) => `projection_${s}`
    ),
    camera_readiness_preview: concept.possible_camera_layers,
    audit_requirements: [
      "audit_trail_required",
      "no_silent_state_change",
      "all_events_must_have_source",
    ],
    concept_guard_requirements: concept.guard_terms,
    implementation_forbidden: true,
    forbidden_reason:
      "Konzept braucht Daniels explizite Feinplanung vor Implementierung.",
  };
}

export function buildOrganBlueprintsForRegistry(
  concepts: FutureConcept[]
): OrganBlueprint[] {
  return concepts.map(buildOrganBlueprint);
}
