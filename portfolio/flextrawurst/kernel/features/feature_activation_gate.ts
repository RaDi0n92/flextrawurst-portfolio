import type { FeatureFlag } from "./feature_flag.ts";
import type { AdminActor } from "../admin/admin_permissions.ts";
import { hasPermission } from "../admin/admin_permissions.ts";

export interface FeatureActivationGateReport {
  feature_id: string;
  allowed: boolean;
  blocked: boolean;
  missing_permissions: string[];
  blockers: string[];
  required_approvals: string[];
  notes: string[];
}

export function evaluateFeatureActivationGate(
  feature: FeatureFlag,
  actor: AdminActor
): FeatureActivationGateReport {
  const missingPermissions: string[] = [];
  const blockers: string[] = [...feature.blockers];
  const requiredApprovals: string[] = [];
  const notes: string[] = [];

  if (!hasPermission(actor, "feature.approve_activation")) {
    missingPermissions.push("feature.approve_activation");
  }

  if (!feature.can_enable_now) {
    blockers.push("can_enable_now_is_false");
  }

  if (
    feature.requires_daniel_approval &&
    actor.role !== "daniel_root"
  ) {
    blockers.push("requires_daniel_root_approval");
    requiredApprovals.push("daniel_root");
  }

  if (feature.requires_daniel_approval) {
    requiredApprovals.push("daniel_explicit_approval");
  }

  if (feature.requires_concept_readiness) {
    blockers.push("concept_readiness_required");
    notes.push("Konzept braucht Daniels Feinplanung.");
  }

  const blocked =
    missingPermissions.length > 0 ||
    !feature.can_enable_now ||
    (feature.requires_daniel_approval && actor.role !== "daniel_root") ||
    feature.blockers.length > 0;

  return {
    feature_id: feature.feature_id,
    allowed: !blocked,
    blocked,
    missing_permissions: missingPermissions,
    blockers,
    required_approvals: [...new Set(requiredApprovals)],
    notes,
  };
}
