import type { OrganBlueprint } from "./organ_blueprint.ts";
import {
  buildOrganBlueprintsForRegistry,
} from "./organ_blueprint.ts";
import { getFutureConceptRegistry } from "../future_concepts/future_concept_registry.ts";

export interface OrganDock {
  dock_version: 1;
  blueprint_count: number;
  implemented_organ_count: number;
  blocked_blueprint_count: number;
  blueprints: OrganBlueprint[];
  notes: string[];
}

export function buildOrganDock(): OrganDock {
  const concepts = getFutureConceptRegistry();
  const blueprints = buildOrganBlueprintsForRegistry(concepts);

  const implemented = concepts.filter(c => c.status === "implemented").length;
  return {
    dock_version: 1,
    blueprint_count: blueprints.length,
    implemented_organ_count: implemented,
    blocked_blueprint_count: blueprints.length - implemented,
    blueprints,
    notes: [
      "Implementiert: Schlaf-System, Cyberling-Pflegesystem.",
      "Offen: Substanz, KompOase, METAWAR, quality me time, Resonanzurlaub, Traumreste.",
    ],
  };
}
