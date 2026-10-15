import type { FeatureFlag } from "./feature_flag.ts";
import type { AdminActor } from "../admin/admin_permissions.ts";
import { hasPermission } from "../admin/admin_permissions.ts";

export interface FeatureDeactivationGateReport {
  feature_id: string;
  allowed: boolean;
  blocked: boolean;
  notes: string[];
}

export function evaluateFeatureDeactivationGate(
  feature: FeatureFlag,
  actor: AdminActor
): FeatureDeactivationGateReport {
  if (!feature.enabled) {
    return {
      feature_id: feature.feature_id,
      allowed: false,
      blocked: false,
      notes: ["Feature ist bereits deaktiviert. Keine Deactivation nötig."],
    };
  }

  if (!hasPermission(actor, "feature.deactivate")) {
    return {
      feature_id: feature.feature_id,
      allowed: false,
      blocked: true,
      notes: ["Fehlende Permission: feature.deactivate"],
    };
  }

  return {
    feature_id: feature.feature_id,
    allowed: true,
    blocked: false,
    notes: ["Deactivation erlaubt."],
  };
}
