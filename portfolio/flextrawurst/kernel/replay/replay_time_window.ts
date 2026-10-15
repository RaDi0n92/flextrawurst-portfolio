import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldReplayFrame } from "./world_replay_frames.ts";

export interface ReplayTimeWindow {
  window_id: string;
  from_event_id: string | null;
  to_event_id: string | null;
  included_event_ids: string[];
  tick_count: number;
  frame_count: number;
  creates_new_events: false;
}

export function buildReplayTimeWindow(
  events: readonly FlextrawurstEvent[],
  frames: WorldReplayFrame[],
  fromEventId?: string,
  toEventId?: string
): ReplayTimeWindow {
  let startIdx = 0;
  let endIdx = events.length - 1;

  if (fromEventId !== undefined) {
    const idx = events.findIndex((e) => e.event_id === fromEventId);
    if (idx >= 0) startIdx = idx;
  }

  if (toEventId !== undefined) {
    const idx = events.findIndex((e) => e.event_id === toEventId);
    if (idx >= 0) endIdx = idx;
  }

  const included =
    endIdx >= startIdx ? [...events].slice(startIdx, endIdx + 1) : [];

  const tickCount = included.filter(
    (e) => e.event_type === "system.tick"
  ).length;

  const includedIdSet = new Set(included.map((e) => e.event_id));
  const relevantFrameCount = frames.filter((f) =>
    includedIdSet.has(f.until_event_id)
  ).length;

  return {
    window_id: `window-${fromEventId ?? "start"}-${toEventId ?? "end"}`,
    from_event_id: fromEventId ?? null,
    to_event_id: toEventId ?? null,
    included_event_ids: included.map((e) => e.event_id),
    tick_count: tickCount,
    frame_count: relevantFrameCount,
    creates_new_events: false,
  };
}
