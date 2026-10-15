import type { FlextrawurstEvent } from "../events/types.ts";
import type { InMemoryEventStore } from "../events/event_store.ts";
import { createWorldTick } from "./create_tick.ts";

export interface RunTickParams {
  event_id: string;
  tick_number?: number;
  timestamp?: string;
  world_time?: string;
}

export function runWorldTickOnce(
  store: InMemoryEventStore,
  params: RunTickParams
): FlextrawurstEvent {
  const tickNumber =
    params.tick_number ??
    store.getAll().filter((e) => e.event_type === "system.tick").length;

  const event = createWorldTick({
    event_id: params.event_id,
    tick_number: tickNumber,
    timestamp: params.timestamp,
    world_time: params.world_time,
  });

  store.append(event);
  return store.getById(event.event_id)!;
}
