import type { InMemoryEventStore } from "../events/event_store.ts";
import type { WorldSnapshot } from "../snapshots/world_snapshot.ts";
import { buildWorldSnapshot } from "../snapshots/world_snapshot.ts";
import { runWorldTickOnce } from "./run_tick_once.ts";
import { runPresencePulseForExistingEntities } from "./run_presence_pulse_for_entities.ts";

export interface WorldCycleParams {
  tick_event_id: string;
  tick_number: number;
  timestamp: string;
  world_time: string;
  transition_event_id_prefix: string;
}

export function runWorldCycle(
  store: InMemoryEventStore,
  params: WorldCycleParams
): WorldSnapshot {
  const tick = runWorldTickOnce(store, {
    event_id: params.tick_event_id,
    tick_number: params.tick_number,
    timestamp: params.timestamp,
    world_time: params.world_time,
  });

  runPresencePulseForExistingEntities(store, tick, {
    timestamp: params.timestamp,
    event_id_prefix: params.transition_event_id_prefix,
  });

  return buildWorldSnapshot(store.getAll());
}
