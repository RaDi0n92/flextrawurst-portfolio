import type { CommandIntent } from "../admin/command_intent.ts";
import type { AdminActor } from "../admin/admin_permissions.ts";
import type { WorldRunState } from "./worldrun_state.ts";
import type { WorldRunTransitionResult } from "./worldrun_transition.ts";
import type { WorldRunGateReport } from "./worldrun_gate.ts";
import type { WorldRunTransitionType } from "./worldrun_transition.ts";
import { evaluateWorldRunGate } from "./worldrun_gate.ts";
import { applyWorldRunTransition } from "./worldrun_transition.ts";

export interface WorldRunCommandHandlingResult {
  command_id: string;
  accepted: boolean;
  dry_run: boolean;
  gate: WorldRunGateReport;
  transition: WorldRunTransitionResult | null;
  notes: string[];
}

const COMMAND_TO_TRANSITION: Partial<Record<string, WorldRunTransitionType>> = {
  pause_worldrun: "pause",
  resume_worldrun: "resume",
  freeze_worldrun: "freeze",
  stop_worldrun: "stop",
};

export function handleWorldRunCommand(
  state: WorldRunState,
  command: CommandIntent,
  actor: AdminActor
): WorldRunCommandHandlingResult {
  const notes: string[] = [];
  const transition_type = COMMAND_TO_TRANSITION[command.command_type];

  if (transition_type === undefined) {
    const gate = evaluateWorldRunGate(actor, state, "pause");
    return {
      command_id: command.command_id,
      accepted: false,
      dry_run: command.dry_run,
      gate: {
        ...gate,
        transition_type: "pause",
        allowed: false,
        blocked: true,
        missing_permissions: [],
        blockers: [`command_type ${command.command_type} is not a worldrun control command`],
        notes: [],
      },
      transition: null,
      notes: [`command_type ${command.command_type} not handled by WorldRunCommandHandler`],
    };
  }

  const gate = evaluateWorldRunGate(actor, state, transition_type);

  if (!gate.allowed) {
    return {
      command_id: command.command_id,
      accepted: false,
      dry_run: command.dry_run,
      gate,
      transition: null,
      notes: ["gate blocked — no transition applied"],
    };
  }

  if (command.dry_run) {
    notes.push("dry_run=true — gate passed but state not mutated");
    return {
      command_id: command.command_id,
      accepted: true,
      dry_run: true,
      gate,
      transition: null,
      notes,
    };
  }

  const result = applyWorldRunTransition(state, {
    transition_id: command.command_id,
    transition_type,
    requested_by: command.requested_by,
    reason: command.reason,
    created_at: command.created_at,
  });

  return {
    command_id: command.command_id,
    accepted: result.allowed,
    dry_run: false,
    gate,
    transition: result,
    notes,
  };
}
