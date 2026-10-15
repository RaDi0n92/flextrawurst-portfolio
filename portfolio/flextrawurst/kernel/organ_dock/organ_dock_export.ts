import type { OrganDockInspection } from "./organ_dock_inspection.ts";
import { buildOrganDockInspection } from "./organ_dock_inspection.ts";

export interface OrganDockExport {
  export_version: 1;
  inspection_version: number;
  blueprint_count: number;
  implemented_organ_count: number;
  blocked_blueprint_count: number;
  safe_to_implement_now: boolean;
  concept_ids: string[];
  summary: string[];
}

export function buildOrganDockExport(
  inspection: OrganDockInspection
): OrganDockExport {
  return {
    export_version: 1,
    inspection_version: inspection.inspection_version,
    blueprint_count: inspection.dock.blueprint_count,
    implemented_organ_count: inspection.dock.implemented_organ_count,
    blocked_blueprint_count: inspection.dock.blocked_blueprint_count,
    safe_to_implement_now: inspection.safe_to_implement_now,
    concept_ids: inspection.dock.blueprints.map((b) => b.concept_id).sort(),
    summary: [...inspection.summary],
  };
}

export function serializeOrganDockExport(
  inspection: OrganDockInspection
): string {
  const exp = buildOrganDockExport(inspection);
  return JSON.stringify(exp, Object.keys(exp).sort(), 2);
}
