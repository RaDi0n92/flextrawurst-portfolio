import type { AdminActor, OperatorPermission } from "../admin/admin_permissions.ts";
import { hasPermission } from "../admin/admin_permissions.ts";
import type { GovernanceActionDefinition } from "./governance_action.ts";
import type { ApprovalRequirement } from "./approval_level.ts";
import type { GlobalLockState } from "./global_lock.ts";
import { doesGlobalLockBlockAction } from "./global_lock.ts";

export interface GovernanceGateReport {
  action_id: string;
  allowed: boolean;
  blocked: boolean;
  actor_id: string;
  actor_role: string;
  missing_permissions: string[];
  missing_approvals: string[];
  blockers: string[];
  notes: string[];
}

export function evaluateGovernanceGate(
  action: GovernanceActionDefinition,
  approval: ApprovalRequirement,
  actor: AdminActor,
  globalLock: GlobalLockState
): GovernanceGateReport {
  const missing_permissions: string[] = [];
  const missing_approvals: string[] = [];
  const blockers: string[] = [];
  const notes: string[] = [];

  if (!hasPermission(actor, action.required_permission as OperatorPermission)) {
    missing_permissions.push(action.required_permission);
  }

  if (action.requires_daniel_root && actor.role !== "daniel_root") {
    blockers.push(`action ${action.action_id} requires daniel_root role`);
  }

  if (doesGlobalLockBlockAction(globalLock, action)) {
    blockers.push(`global lock active — action ${action.action_id} blocked`);
  }

  if (action.action_id === "global.lock" && globalLock.locked) {
    blockers.push("global lock already active — cannot double-lock");
  }

  const isViewAction =
    action.action_class === "search_inspection" ||
    action.action_class === "concept_guard_report" ||
    action.action_class === "readonly_export";

  if (actor.role === "observer" && !isViewAction) {
    blockers.push("observer role cannot perform non-view actions");
  }

  if (
    actor.role === "system_process" &&
    (action.risk_level === "high" || action.risk_level === "critical")
  ) {
    blockers.push("system_process cannot perform high/critical governance actions");
  }

  if (actor.role === "operator" && action.action_id === "future_organ.activate") {
    blockers.push("operator cannot activate future organs — daniel_root required");
  }

  if (action.requires_dry_run_first) {
    missing_approvals.push(`dry run required before ${action.action_id}`);
    notes.push(`dry_run_required: true for ${action.action_id}`);
  }

  const allowed = missing_permissions.length === 0 && blockers.length === 0;

  if (allowed) {
    notes.push(`actor ${actor.actor_id} (${actor.role}) allowed for ${action.action_id}`);
  }

  return {
    action_id: action.action_id,
    allowed,
    blocked: !allowed,
    actor_id: actor.actor_id,
    actor_role: actor.role,
    missing_permissions,
    missing_approvals,
    blockers,
    notes,
  };
}
