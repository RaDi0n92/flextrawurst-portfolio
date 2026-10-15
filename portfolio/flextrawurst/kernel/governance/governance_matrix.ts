import type { GovernanceActionDefinition } from "./governance_action.ts";
import { buildGovernanceActionDefinitions } from "./governance_action.ts";
import type { ApprovalRequirement } from "./approval_level.ts";
import { getApprovalRequirementForAction } from "./approval_level.ts";

export interface GovernanceMatrixRow {
  action: GovernanceActionDefinition;
  approval: ApprovalRequirement;
  permission: string;
  gate_required: boolean;
  command_intent_required: boolean;
  ledger_required: boolean;
  audit_required: boolean;
  search_required: boolean;
}

export interface GovernanceMatrix {
  matrix_version: 1;
  rows: GovernanceMatrixRow[];
  notes: string[];
}

export function buildGovernanceMatrix(): GovernanceMatrix {
  const actions = buildGovernanceActionDefinitions();
  const rows: GovernanceMatrixRow[] = actions.map((action) => ({
    action,
    approval: getApprovalRequirementForAction(action),
    permission: action.required_permission,
    gate_required: action.requires_command_intent || action.risk_level !== "low",
    command_intent_required: action.requires_command_intent,
    ledger_required: action.requires_ledger_entry,
    audit_required: action.requires_audit_entry,
    search_required: action.requires_search_document,
  }));
  return {
    matrix_version: 1,
    rows,
    notes: [
      "Governance Matrix v1 — Ring 20.",
      "Governance ist die Kontrollkarte. Sie startet nichts. Sie löscht nichts.",
    ],
  };
}

export function findGovernanceMatrixRow(
  action_id: string
): GovernanceMatrixRow | undefined {
  return buildGovernanceMatrix().rows.find((r) => r.action.action_id === action_id);
}

export function listCriticalGovernanceActions(): GovernanceActionDefinition[] {
  return buildGovernanceActionDefinitions().filter(
    (a) => a.risk_level === "critical"
  );
}

export function listDanielRequiredActions(): GovernanceActionDefinition[] {
  return buildGovernanceActionDefinitions().filter((a) => a.requires_daniel_root);
}

export function listActionsBlockedByGlobalLock(): GovernanceActionDefinition[] {
  return buildGovernanceActionDefinitions().filter((a) => a.blocked_by_global_lock);
}
