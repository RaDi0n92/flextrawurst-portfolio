import type { GovernanceMatrix } from "./governance_matrix.ts";
import { buildGovernanceMatrix } from "./governance_matrix.ts";
import type { GlobalLockState } from "./global_lock.ts";
import { createUnlockedGlobalLockState } from "./global_lock.ts";
import type { GovernanceCoverageReport } from "./governance_coverage.ts";
import { buildGovernanceCoverageReport } from "./governance_coverage.ts";
import {
  listCriticalGovernanceActions,
  listDanielRequiredActions,
  listActionsBlockedByGlobalLock,
} from "./governance_matrix.ts";

export interface GovernanceSnapshot {
  snapshot_version: 1;
  matrix: GovernanceMatrix;
  global_lock: GlobalLockState;
  coverage: GovernanceCoverageReport;
  critical_actions: string[];
  daniel_required_actions: string[];
  global_lock_blocked_actions: string[];
  notes: string[];
}

export function buildGovernanceSnapshot(
  globalLock?: GlobalLockState
): GovernanceSnapshot {
  const lock = globalLock ?? createUnlockedGlobalLockState();
  const matrix = buildGovernanceMatrix();
  const coverage = buildGovernanceCoverageReport(matrix);
  const critical_actions = listCriticalGovernanceActions().map((a) => a.action_id);
  const daniel_required_actions = listDanielRequiredActions().map((a) => a.action_id);
  const global_lock_blocked_actions = listActionsBlockedByGlobalLock().map(
    (a) => a.action_id
  );

  return {
    snapshot_version: 1,
    matrix,
    global_lock: lock,
    coverage,
    critical_actions,
    daniel_required_actions,
    global_lock_blocked_actions,
    notes: [
      "Governance Snapshot v1 — Ring 20.",
      lock.locked
        ? `Global lock active: ${lock.lock_id ?? "unknown"}`
        : "Global lock: inactive.",
    ],
  };
}
