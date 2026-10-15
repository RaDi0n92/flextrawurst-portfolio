import type { AdminActor } from "../admin/admin_permissions.ts";
import type { WorldRunState } from "./worldrun_state.ts";
import type { WorldRunTransitionType } from "./worldrun_transition.ts";
import { evaluateWorldRunGate } from "./worldrun_gate.ts";

export interface WorldRunControlSnapshot {
  snapshot_version: 1;
  run_state: WorldRunState;
  available_transitions: WorldRunTransitionType[];
  blocked_transitions: WorldRunTransitionType[];
  can_pause: boolean;
  can_resume: boolean;
  can_freeze: boolean;
  can_stop: boolean;
  can_lock: boolean;
  notes: string[];
}

const ALL_TRANSITIONS: WorldRunTransitionType[] = [
  "start", "pause", "resume", "freeze", "stop", "lock", "unlock",
];

export function buildWorldRunControlSnapshot(
  actor: AdminActor,
  state: WorldRunState
): WorldRunControlSnapshot {
  const available: WorldRunTransitionType[] = [];
  const blocked: WorldRunTransitionType[] = [];
  const notes: string[] = [];

  for (const t of ALL_TRANSITIONS) {
    const gate = evaluateWorldRunGate(actor, state, t);
    if (gate.allowed) {
      available.push(t);
    } else {
      blocked.push(t);
    }
  }

  return {
    snapshot_version: 1,
    run_state: state,
    available_transitions: available,
    blocked_transitions: blocked,
    can_pause: available.includes("pause"),
    can_resume: available.includes("resume"),
    can_freeze: available.includes("freeze"),
    can_stop: available.includes("stop"),
    can_lock: available.includes("lock"),
    notes,
  };
}
