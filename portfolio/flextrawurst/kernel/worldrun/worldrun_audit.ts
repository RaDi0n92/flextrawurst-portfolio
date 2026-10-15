import type { WorldRunCommandHandlingResult } from "./worldrun_command_handler.ts";

export interface WorldRunAuditEntry {
  audit_id: string;
  command_id: string;
  transition_type: string;
  accepted: boolean;
  previous_status: string;
  next_status: string | null;
  dry_run: boolean;
  notes: string[];
}

export interface WorldRunAudit {
  audit_version: 1;
  entries: WorldRunAuditEntry[];
}

export function createEmptyWorldRunAudit(): WorldRunAudit {
  return {
    audit_version: 1,
    entries: [],
  };
}

export function recordWorldRunCommandResult(
  audit: WorldRunAudit,
  result: WorldRunCommandHandlingResult
): WorldRunAudit {
  const transition_type = result.gate.transition_type;
  const previous_status = result.transition?.previous_status ?? "unknown";
  const next_status = result.transition?.next_status ?? null;

  const entry: WorldRunAuditEntry = {
    audit_id: `audit_${result.command_id}_${Date.now()}`,
    command_id: result.command_id,
    transition_type,
    accepted: result.accepted,
    previous_status,
    next_status: result.accepted && !result.dry_run ? next_status ?? null : null,
    dry_run: result.dry_run,
    notes: [...result.notes],
  };

  return {
    audit_version: 1,
    entries: [...audit.entries, entry],
  };
}
