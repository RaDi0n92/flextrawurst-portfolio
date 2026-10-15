import type { GovernanceGateReport } from "./governance_gate.ts";

export interface GovernanceAuditEntry {
  audit_id: string;
  action_id: string;
  command_id: string | null;
  actor_id: string;
  actor_role: string;
  allowed: boolean;
  blocked: boolean;
  blockers: string[];
  created_at: string;
}

export interface GovernanceAudit {
  audit_version: 1;
  entries: GovernanceAuditEntry[];
}

export function createEmptyGovernanceAudit(): GovernanceAudit {
  return {
    audit_version: 1,
    entries: [],
  };
}

export function recordGovernanceGate(
  audit: GovernanceAudit,
  gate: GovernanceGateReport,
  command_id: string | null,
  created_at: string
): GovernanceAudit {
  const entry: GovernanceAuditEntry = {
    audit_id: `gov_audit_${gate.action_id}_${created_at}`,
    action_id: gate.action_id,
    command_id,
    actor_id: gate.actor_id,
    actor_role: gate.actor_role,
    allowed: gate.allowed,
    blocked: gate.blocked,
    blockers: [...gate.blockers],
    created_at,
  };
  return {
    audit_version: 1,
    entries: [...audit.entries, entry],
  };
}
