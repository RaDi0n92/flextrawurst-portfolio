import type { GovernanceActionDefinition } from "./governance_action.ts";

export interface GlobalLockState {
  lock_version: 1;
  locked: boolean;
  lock_id: string | null;
  locked_by: string | null;
  reason: string | null;
  created_at: string | null;
  blocks_all_non_view_actions: boolean;
}

export function createUnlockedGlobalLockState(): GlobalLockState {
  return {
    lock_version: 1,
    locked: false,
    lock_id: null,
    locked_by: null,
    reason: null,
    created_at: null,
    blocks_all_non_view_actions: false,
  };
}

export function createGlobalLock(
  lock_id: string,
  locked_by: string,
  reason: string,
  created_at: string
): GlobalLockState {
  return {
    lock_version: 1,
    locked: true,
    lock_id,
    locked_by,
    reason,
    created_at,
    blocks_all_non_view_actions: true,
  };
}

export function doesGlobalLockBlockAction(
  lock: GlobalLockState,
  action: GovernanceActionDefinition
): boolean {
  if (!lock.locked) {
    return false;
  }
  return action.blocked_by_global_lock;
}
