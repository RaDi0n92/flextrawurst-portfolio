export type AdminRole =
  | "daniel_root"
  | "operator"
  | "observer"
  | "system_process";

export type OperatorPermission =
  | "feature.view"
  | "feature.request_activation"
  | "feature.approve_activation"
  | "feature.deactivate"
  | "import.view"
  | "import.approve"
  | "slot.view"
  | "slot.approve_activation"
  | "worldrun.view"
  | "worldrun.pause"
  | "worldrun.resume"
  | "worldrun.freeze"
  | "worldrun.stop"
  | "export.view"
  | "export.create_readonly"
  | "concept_guard.view"
  | "policy.view"
  | "policy.set"
  | "governance.view"
  | "governance.global_lock"
  | "governance.audit_full"
  | "governance.approve"
  | "governance.future_organ_activate";

export interface AdminActor {
  actor_id: string;
  role: AdminRole;
  permissions: OperatorPermission[];
}

const ALL_PERMISSIONS: OperatorPermission[] = [
  "feature.view",
  "feature.request_activation",
  "feature.approve_activation",
  "feature.deactivate",
  "import.view",
  "import.approve",
  "slot.view",
  "slot.approve_activation",
  "worldrun.view",
  "worldrun.pause",
  "worldrun.resume",
  "worldrun.freeze",
  "worldrun.stop",
  "export.view",
  "export.create_readonly",
  "concept_guard.view",
  "policy.view",
  "policy.set",
  "governance.view",
  "governance.global_lock",
  "governance.audit_full",
  "governance.approve",
  "governance.future_organ_activate",
];

const VIEW_PERMISSIONS: OperatorPermission[] = [
  "feature.view",
  "import.view",
  "slot.view",
  "worldrun.view",
  "export.view",
  "concept_guard.view",
  "policy.view",
];

export function buildDanielRootAdmin(): AdminActor {
  return {
    actor_id: "daniel_root",
    role: "daniel_root",
    permissions: [...ALL_PERMISSIONS],
  };
}

export function buildObserverAdmin(actor_id: string): AdminActor {
  return {
    actor_id,
    role: "observer",
    permissions: [...VIEW_PERMISSIONS],
  };
}

export function buildSystemProcessActor(actor_id: string): AdminActor {
  return {
    actor_id,
    role: "system_process",
    permissions: [
      "feature.view",
      "worldrun.view",
      "export.view",
      "export.create_readonly",
    ],
  };
}

export function hasPermission(
  actor: AdminActor,
  permission: OperatorPermission
): boolean {
  return actor.permissions.includes(permission);
}
