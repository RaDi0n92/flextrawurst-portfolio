import type { AdminActor } from "../admin/admin_permissions.ts";
import { hasPermission } from "../admin/admin_permissions.ts";
import type { WorldRunState } from "./worldrun_state.ts";
import type { WorldRunTransitionType } from "./worldrun_transition.ts";
import type { OperatorPermission } from "../admin/admin_permissions.ts";

export interface WorldRunGateReport {
  transition_type: WorldRunTransitionType;
  allowed: boolean;
  blocked: boolean;
  missing_permissions: string[];
  blockers: string[];
  notes: string[];
}

const PERMISSION_MAP: Record<WorldRunTransitionType, OperatorPermission> = {
  pause: "worldrun.pause",
  resume: "worldrun.resume",
  freeze: "worldrun.freeze",
  stop: "worldrun.stop",
  start: "worldrun.resume",
  lock: "worldrun.freeze",
  unlock: "worldrun.resume",
};

export function evaluateWorldRunGate(
  actor: AdminActor,
  state: WorldRunState,
  transition_type: WorldRunTransitionType
): WorldRunGateReport {
  const missing_permissions: string[] = [];
  const blockers: string[] = [];
  const notes: string[] = [];

  const required = PERMISSION_MAP[transition_type];
  if (!hasPermission(actor, required)) {
    missing_permissions.push(required);
  }

  if (state.locked && (transition_type === "start" || transition_type === "resume")) {
    blockers.push("state is locked — start/resume blocked");
  }

  if (state.status === "stopped" && transition_type !== "lock" && transition_type !== "unlock") {
    blockers.push("state is stopped — no transitions allowed");
  }

  if (state.status === "frozen" && transition_type === "resume") {
    blockers.push("frozen state cannot be resumed directly");
  }

  const allowed = missing_permissions.length === 0 && blockers.length === 0;

  if (allowed) {
    notes.push(`actor ${actor.actor_id} (${actor.role}) allowed ${transition_type}`);
  }

  return {
    transition_type,
    allowed,
    blocked: !allowed,
    missing_permissions,
    blockers,
    notes,
  };
}
