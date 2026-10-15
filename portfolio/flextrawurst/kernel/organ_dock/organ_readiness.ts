import type { FutureConcept } from "../future_concepts/future_concept_model.ts";

export interface OrganReadinessReport {
  concept_id: string;
  ready: boolean;
  missing: string[];
  blockers: string[];
  recommended_next_planning_questions: string[];
}

const REQUIRED_CONTRACTS = [
  "daniel_concept_definition",
  "event_contract",
  "state_contract",
  "projection_contract",
  "camera_contract",
  "audit_contract",
  "concept_guard_contract",
];

export function assessOrganReadiness(concept: FutureConcept): OrganReadinessReport {
  return {
    concept_id: concept.concept_id,
    ready: false,
    missing: [...REQUIRED_CONTRACTS],
    blockers: [
      "Daniels Feinplanung ausstehend",
      "Kein Event-Contract definiert",
      "Kein State-Contract definiert",
    ],
    recommended_next_planning_questions: concept.required_planning_questions,
  };
}

export function assessAllOrganReadiness(
  concepts: FutureConcept[]
): OrganReadinessReport[] {
  return concepts.map(assessOrganReadiness);
}
