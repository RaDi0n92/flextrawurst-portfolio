import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";

export interface RuntimeReadinessReport {
  ok: boolean;
  event_count: number;
  tick_count: number;
  trace_count: number;
  replay_frame_count: number;
  deterministic: boolean;
  uses_ai: boolean;
  uses_ui: boolean;
  uses_postgres: boolean;
  uses_scheduler: boolean;
  notes: string[];
}

export function assessRuntimeReadiness(
  pack: WorldInspectionPack
): RuntimeReadinessReport {
  const ok =
    pack.audit_ok &&
    pack.event_count > 0 &&
    pack.tick_count > 0 &&
    pack.replay_frames.length > 0;

  return {
    ok,
    event_count: pack.event_count,
    tick_count: pack.tick_count,
    trace_count: pack.trace_count,
    replay_frame_count: pack.replay_frames.length,
    deterministic: true,
    uses_ai: false,
    uses_ui: false,
    uses_postgres: false,
    uses_scheduler: false,
    notes: [
      "Deterministischer In-Memory-Lauf.",
      "Keine AI, keine UI, kein Renderer, kein Postgres, kein Scheduler beteiligt.",
      "Replay-Frames verifizieren Determinismus.",
    ],
  };
}
