export type WorldRunStatus =
  | "not_started"
  | "running"
  | "paused"
  | "frozen"
  | "stopped"
  | "locked";

export interface WorldRunState {
  run_id: string;
  status: WorldRunStatus;
  current_tick: number;
  last_event_id: string | null;
  locked: boolean;
  lock_reason: string | null;
  paused_reason: string | null;
  stopped_reason: string | null;
  frozen_reason: string | null;
  updated_at: string;
}

export function createInitialWorldRunState(
  run_id: string,
  timestamp: string
): WorldRunState {
  return {
    run_id,
    status: "not_started",
    current_tick: 0,
    last_event_id: null,
    locked: false,
    lock_reason: null,
    paused_reason: null,
    stopped_reason: null,
    frozen_reason: null,
    updated_at: timestamp,
  };
}
