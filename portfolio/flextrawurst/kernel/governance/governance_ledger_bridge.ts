import type { CommandLedger } from "../admin/command_ledger.ts";
import { recordCommandIntent } from "../admin/command_ledger.ts";
import type { AdminActor } from "../admin/admin_permissions.ts";
import type { CommandIntent } from "../admin/command_intent.ts";
import type { GovernanceGateReport } from "./governance_gate.ts";

export interface GovernanceLedgerBridgeResult {
  ledger_written: boolean;
  ledger_entry_count_before: number;
  ledger_entry_count_after: number;
  status: "recorded" | "blocked" | "approved" | "executed_readonly";
  notes: string[];
}

export function recordGovernanceGateToLedger(
  ledger: CommandLedger,
  command: CommandIntent,
  actor: AdminActor,
  gate: GovernanceGateReport
): { ledger: CommandLedger; result: GovernanceLedgerBridgeResult } {
  const countBefore = ledger.entries.length;

  let status: GovernanceLedgerBridgeResult["status"];
  const notes: string[] = [];

  if (gate.blocked) {
    status = "blocked";
    notes.push(`gate blocked: ${gate.blockers.join("; ")}`);
  } else if (command.command_type === "create_readonly_export") {
    status = "executed_readonly";
    notes.push("read-only export executed");
  } else if (command.dry_run) {
    status = "recorded";
    notes.push("dry_run: command recorded but not executed");
  } else {
    status = "approved";
    notes.push("gate allowed — command approved");
  }

  const updatedLedger = recordCommandIntent(ledger, command, actor, status, notes);
  const countAfter = updatedLedger.entries.length;

  return {
    ledger: updatedLedger,
    result: {
      ledger_written: true,
      ledger_entry_count_before: countBefore,
      ledger_entry_count_after: countAfter,
      status,
      notes,
    },
  };
}
