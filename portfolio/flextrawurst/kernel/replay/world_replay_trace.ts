import type { FlextrawurstEvent } from "../events/types.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";
import type { WorldReplayFrame } from "./world_replay_frames.ts";

export interface WorldReplayTrace {
  trace_id: string;
  slot_id: string;
  event_ids: string[];
  frame_indices: number[];
  created_without_side_effects: true;
  creates_new_events: false;
  activates_slots: false;
}

export function buildWorldReplayTrace(
  slot: EntitySlot,
  events: readonly FlextrawurstEvent[],
  frames: WorldReplayFrame[]
): WorldReplayTrace {
  const slotEventIds = events
    .filter(
      (e) =>
        (e.event_type === "system.seed_entity" &&
          e.payload.entity_id === slot.slot_id) ||
        e.target_id === slot.slot_id
    )
    .map((e) => e.event_id);

  const eventIndexMap = new Map<string, number>();
  for (let i = 0; i < events.length; i++) {
    eventIndexMap.set(events[i].event_id, i);
  }

  const frameIndices: number[] = [];
  for (const frame of frames) {
    const frameEventIdx = eventIndexMap.get(frame.until_event_id) ?? -1;
    if (frameEventIdx < 0) continue;

    const frameContainsSlot = slotEventIds.some((id) => {
      const eIdx = eventIndexMap.get(id) ?? -1;
      return eIdx >= 0 && eIdx <= frameEventIdx;
    });

    if (frameContainsSlot) {
      frameIndices.push(frame.frame_index);
    }
  }

  return {
    trace_id: `trace-${slot.slot_id}`,
    slot_id: slot.slot_id,
    event_ids: slotEventIds,
    frame_indices: frameIndices.sort((a, b) => a - b),
    created_without_side_effects: true,
    creates_new_events: false,
    activates_slots: false,
  };
}

export function buildAllSlotReplayTraces(
  slots: EntitySlot[],
  events: readonly FlextrawurstEvent[],
  frames: WorldReplayFrame[]
): WorldReplayTrace[] {
  return slots.map((slot) => buildWorldReplayTrace(slot, events, frames));
}
