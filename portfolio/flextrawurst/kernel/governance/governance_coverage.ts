import type { GovernanceMatrix } from "./governance_matrix.ts";

export interface GovernanceCoverageReport {
  coverage_version: 1;
  action_count: number;
  actions_requiring_command_intent: number;
  actions_requiring_ledger: number;
  actions_requiring_audit: number;
  actions_requiring_search: number;
  critical_action_count: number;
  missing_coverage: string[];
  ok: boolean;
}

export function buildGovernanceCoverageReport(
  matrix: GovernanceMatrix
): GovernanceCoverageReport {
  const missing_coverage: string[] = [];
  let actions_requiring_command_intent = 0;
  let actions_requiring_ledger = 0;
  let actions_requiring_audit = 0;
  let actions_requiring_search = 0;
  let critical_action_count = 0;

  for (const row of matrix.rows) {
    const { action } = row;
    if (action.requires_command_intent) actions_requiring_command_intent++;
    if (action.requires_ledger_entry) actions_requiring_ledger++;
    if (action.requires_audit_entry) actions_requiring_audit++;
    if (action.requires_search_document) actions_requiring_search++;
    if (action.risk_level === "critical") critical_action_count++;

    if (action.risk_level === "high" || action.risk_level === "critical") {
      if (!action.requires_command_intent) {
        missing_coverage.push(`${action.action_id}: missing command_intent`);
      }
      if (!action.requires_ledger_entry) {
        missing_coverage.push(`${action.action_id}: missing ledger`);
      }
      if (!action.requires_audit_entry) {
        missing_coverage.push(`${action.action_id}: missing audit`);
      }
      if (!action.requires_search_document) {
        missing_coverage.push(`${action.action_id}: missing search`);
      }
    }
  }

  return {
    coverage_version: 1,
    action_count: matrix.rows.length,
    actions_requiring_command_intent,
    actions_requiring_ledger,
    actions_requiring_audit,
    actions_requiring_search,
    critical_action_count,
    missing_coverage,
    ok: missing_coverage.length === 0,
  };
}
