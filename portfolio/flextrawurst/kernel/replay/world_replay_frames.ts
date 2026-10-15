import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldSnapshot } from "../snapshots/world_snapshot.ts";
import { buildWorldSnapshot } from "../snapshots/world_snapshot.ts";

export interface WorldReplayFrame {
  frame_index: number;
  until_event_id: string;
  snapshot: WorldSnapshot;
}

// One frame per complete cycle: boundary is after the last entity.state_changed
// event causally linked to each system.tick. If a tick has no transitions,
// the boundary is the tick event itself.
export function buildWorldReplayFrames(
  events: readonly FlextrawurstEvent[]
): WorldReplayFrame[] {
  const frames: WorldReplayFrame[] = [];
  let frameIndex = 0;

  for (let i = 0; i < events.length; i++) {
    if (events[i].event_type !== "system.tick") continue;

    const tickEventId = events[i].event_id;
    let lastRelatedIdx = i;

    for (let j = i + 1; j < events.length; j++) {
      if (events[j].causal_links.includes(tickEventId)) {
        lastRelatedIdx = j;
      } else if (events[j].event_type === "system.tick") {
        break;
      }
    }

    const slice = events.slice(0, lastRelatedIdx + 1);
    frames.push({
      frame_index: frameIndex++,
      until_event_id: events[lastRelatedIdx].event_id,
      snapshot: buildWorldSnapshot(slice),
    });
  }

  return frames;
}
