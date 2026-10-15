import type { AdminActor, AdminRole } from "./admin_permissions.ts";
import type { FeatureFlag } from "../features/feature_flag.ts";
import { hasPermission } from "./admin_permissions.ts";

export interface AdminControlSnapshot {
  snapshot_version: 1;
  admin_actor_id: string;
  role: AdminRole;
  feature_count: number;
  enabled_feature_count: number;
  disabled_feature_count: number;
  blocked_feature_count: number;
  pending_activation_count: number;
  critical_controls: {
    can_freeze_worldrun: boolean;
    can_stop_worldrun: boolean;
    can_approve_import: boolean;
    can_approve_feature_activation: boolean;
    can_create_readonly_export: boolean;
  };
  notes: string[];
}

export function buildAdminControlSnapshot(
  actor: AdminActor,
  featureRegistry: FeatureFlag[]
): AdminControlSnapshot {
  const enabledCount = featureRegistry.filter((f) => f.enabled).length;
  const disabledCount = featureRegistry.filter((f) => !f.enabled).length;
  const blockedCount = featureRegistry.filter(
    (f) => f.status === "activation_blocked" || f.blockers.length > 0
  ).length;
  const pendingCount = featureRegistry.filter(
    (f) => f.status === "activation_requested"
  ).length;

  return {
    snapshot_version: 1,
    admin_actor_id: actor.actor_id,
    role: actor.role,
    feature_count: featureRegistry.length,
    enabled_feature_count: enabledCount,
    disabled_feature_count: disabledCount,
    blocked_feature_count: blockedCount,
    pending_activation_count: pendingCount,
    critical_controls: {
      can_freeze_worldrun: hasPermission(actor, "worldrun.freeze"),
      can_stop_worldrun: hasPermission(actor, "worldrun.stop"),
      can_approve_import: hasPermission(actor, "import.approve"),
      can_approve_feature_activation: hasPermission(
        actor,
        "feature.approve_activation"
      ),
      can_create_readonly_export: hasPermission(
        actor,
        "export.create_readonly"
      ),
    },
    notes: [
      "Admin Control Plane aktiv.",
      "Alle Organ-Features deaktiviert.",
      "Aktivierung blockiert bis Daniel-Planung und Freigabe.",
    ],
  };
}
