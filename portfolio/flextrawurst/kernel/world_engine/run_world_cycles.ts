import type { InMemoryEventStore } from "../events/event_store.ts";
import type { WorldSnapshot } from "../snapshots/world_snapshot.ts";
import type { WorldCycleParams } from "./run_world_cycle.ts";
import { runWorldCycle } from "./run_world_cycle.ts";

export function runWorldCycles(
  store: InMemoryEventStore,
  cycles: WorldCycleParams[]
): WorldSnapshot[] {
  return cycles.map((params) => runWorldCycle(store, params));
}
