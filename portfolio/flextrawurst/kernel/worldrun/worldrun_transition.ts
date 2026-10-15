import type { WorldRunState, WorldRunStatus } from "./worldrun_state.ts";

export type WorldRunTransitionType =
  | "start"
  | "pause"
  | "resume"
  | "freeze"
  | "stop"
  | "lock"
  | "unlock";

export interface WorldRunTransitionRequest {
  transition_id: string;
  transition_type: WorldRunTransitionType;
  requested_by: string;
  reason: string;
  created_at: string;
}

export interface WorldRunTransitionResult {
  allowed: boolean;
  previous_status: WorldRunStatus;
  next_status: WorldRunStatus;
  state: WorldRunState;
  blockers: string[];
  notes: string[];
}

const VALID_TRANSITIONS: Partial<Record<WorldRunStatus, Partial<Record<WorldRunTransitionType, WorldRunStatus>>>> = {
  not_started: { start: "running" },
  running: { pause: "paused", freeze: "frozen", stop: "stopped" },
  paused: { resume: "running", freeze: "frozen", stop: "stopped" },
  frozen: { stop: "stopped" },
  stopped: {},
};

export function applyWorldRunTransition(
  state: WorldRunState,
  request: WorldRunTransitionRequest
): WorldRunTransitionResult {
  const previous_status = state.status;
  const blockers: string[] = [];
  const notes: string[] = [];

  if (state.locked && (request.transition_type === "start" || request.transition_type === "resume")) {
    blockers.push("state is locked — start/resume blocked");
    return {
      allowed: false,
      previous_status,
      next_status: previous_status,
      state,
      blockers,
      notes,
    };
  }

  if (request.transition_type === "lock") {
    const next: WorldRunState = {
      ...state,
      locked: true,
      lock_reason: request.reason,
      updated_at: request.created_at,
    };
    return {
      allowed: true,
      previous_status,
      next_status: previous_status,
      state: next,
      blockers,
      notes: ["locked=true set"],
    };
  }

  if (request.transition_type === "unlock") {
    const next: WorldRunState = {
      ...state,
      locked: false,
      lock_reason: null,
      updated_at: request.created_at,
    };
    return {
      allowed: true,
      previous_status,
      next_status: previous_status,
      state: next,
      blockers,
      notes: ["locked=false set, status unchanged"],
    };
  }

  if (state.status === "stopped") {
    blockers.push("state is stopped — no further transitions allowed");
    return {
      allowed: false,
      previous_status,
      next_status: previous_status,
      state,
      blockers,
      notes,
    };
  }

  if (state.status === "frozen" && request.transition_type === "resume") {
    blockers.push("frozen state cannot be resumed directly — must stop first");
    return {
      allowed: false,
      previous_status,
      next_status: previous_status,
      state,
      blockers,
      notes,
    };
  }

  const validMap = VALID_TRANSITIONS[state.status] ?? {};
  const next_status = validMap[request.transition_type];

  if (next_status === undefined) {
    blockers.push(`transition ${request.transition_type} not valid from status ${state.status}`);
    return {
      allowed: false,
      previous_status,
      next_status: previous_status,
      state,
      blockers,
      notes,
    };
  }

  const next: WorldRunState = {
    ...state,
    status: next_status,
    paused_reason: next_status === "paused" ? request.reason : state.paused_reason,
    frozen_reason: next_status === "frozen" ? request.reason : state.frozen_reason,
    stopped_reason: next_status === "stopped" ? request.reason : state.stopped_reason,
    updated_at: request.created_at,
  };

  return {
    allowed: true,
    previous_status,
    next_status,
    state: next,
    blockers,
    notes,
  };
}
