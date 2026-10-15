import type { AdminControlInspection } from "./admin_control_inspection.ts";

export interface AdminControlExport {
  export_version: 1;
  inspection_version: number;
  actor_id: string;
  actor_role: string;
  feature_count: number;
  enabled_feature_count: number;
  disabled_feature_count: number;
  blocked_feature_count: number;
  organ_features_enabled: boolean;
  safe_to_activate_organs: boolean;
  feature_ids: string[];
  summary: string[];
}

export function buildAdminControlExport(
  inspection: AdminControlInspection
): AdminControlExport {
  const organFeaturesEnabled = inspection.features
    .filter((f) => f.kind === "organ")
    .some((f) => f.enabled);

  return {
    export_version: 1,
    inspection_version: inspection.inspection_version,
    actor_id: inspection.actor.actor_id,
    actor_role: inspection.actor.role,
    feature_count: inspection.snapshot.feature_count,
    enabled_feature_count: inspection.snapshot.enabled_feature_count,
    disabled_feature_count: inspection.snapshot.disabled_feature_count,
    blocked_feature_count: inspection.snapshot.blocked_feature_count,
    organ_features_enabled: organFeaturesEnabled,
    safe_to_activate_organs: false,
    feature_ids: inspection.features.map((f) => f.feature_id).sort(),
    summary: [...inspection.summary],
  };
}

export function serializeAdminControlExport(
  inspection: AdminControlInspection
): string {
  const exp = buildAdminControlExport(inspection);
  return JSON.stringify(exp, Object.keys(exp).sort(), 2);
}
