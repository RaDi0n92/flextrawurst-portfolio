import type { CommandIntent } from "./command_intent.ts";
import type { AdminRole } from "./admin_permissions.ts";
import type { AdminActor } from "./admin_permissions.ts";

export interface CommandLedgerEntry {
  ledger_id: string;
  command: CommandIntent;
  status: "recorded" | "blocked" | "approved" | "executed_readonly";
  actor_role: AdminRole;
  notes: string[];
}

export interface CommandLedger {
  ledger_version: 1;
  entries: CommandLedgerEntry[];
}

export function createEmptyCommandLedger(): CommandLedger {
  return {
    ledger_version: 1,
    entries: [],
  };
}

export function recordCommandIntent(
  ledger: CommandLedger,
  command: CommandIntent,
  actor: AdminActor,
  status: CommandLedgerEntry["status"],
  notes: string[]
): CommandLedger {
  const entry: CommandLedgerEntry = {
    ledger_id: `ledger_${command.command_id}`,
    command,
    status,
    actor_role: actor.role,
    notes: [...notes],
  };
  return {
    ledger_version: 1,
    entries: [...ledger.entries, entry],
  };
}
