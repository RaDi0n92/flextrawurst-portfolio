import type { OrganDock } from "./organ_dock.ts";
import type { OrganReadinessReport } from "./organ_readiness.ts";
import { buildOrganDock } from "./organ_dock.ts";
import { assessAllOrganReadiness } from "./organ_readiness.ts";
import { getFutureConceptRegistry } from "../future_concepts/future_concept_registry.ts";

export interface OrganDockInspection {
  inspection_version: 1;
  dock: OrganDock;
  readiness: OrganReadinessReport[];
  safe_to_implement_now: boolean;
  summary: string[];
}

export function buildOrganDockInspection(): OrganDockInspection {
  const dock = buildOrganDock();
  const concepts = getFutureConceptRegistry();
  const readiness = assessAllOrganReadiness(concepts);

  const implementationReady = readiness.filter((r) => r.ready).length;

  return {
    inspection_version: 1,
    dock,
    readiness,
    safe_to_implement_now: false,
    summary: [
      `${dock.blueprint_count} zukünftige Konzepte registriert.`,
      `${dock.implemented_organ_count} Weltorgane implementiert.`,
      `${implementationReady} Konzepte implementierungsbereit.`,
      "Daniel muss Konzepte einzeln weiter planen.",
    ],
  };
}
