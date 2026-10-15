import type { FlextrawurstEvent } from "../events/types.ts";
import type { InMemoryEventStore } from "../events/event_store.ts";
import { buildEntityProjection } from "../projections/entity_projection.ts";
import { applyPresencePulse } from "./state_transitions/presence_pulse.ts";

export interface RunPulseForEntitiesParams {
  timestamp?: string;
  event_id_prefix?: string;
}

export function runPresencePulseForExistingEntities(
  store: InMemoryEventStore,
  tick: FlextrawurstEvent,
  params: RunPulseForEntitiesParams = {}
): FlextrawurstEvent[] {
  // Snapshot: read all current events ONCE before any appends
  const snapshot = store.getAll();

  // Auto-discover seeded entity IDs from the snapshot
  const entityIds: string[] = [];
  for (const event of snapshot) {
    if (
      event.event_type === "system.seed_entity" &&
      typeof event.payload.entity_id === "string"
    ) {
      entityIds.push(event.payload.entity_id as string);
    }
  }

  const tickNum = (tick.payload as Record<string, unknown>).tick_number as number;
  const stored: FlextrawurstEvent[] = [];

  for (const entityId of entityIds) {
    const projection = buildEntityProjection(entityId, snapshot);

    const prefix = params.event_id_prefix ?? `evt-pulse-tick${tickNum}`;
    const event = applyPresencePulse(tick, projection, {
      event_id: `${prefix}-${entityId}`,
      timestamp: params.timestamp,
    });

    if (event === null) continue;

    store.append(event);
    stored.push(store.getById(event.event_id)!);
  }

  return stored;
}
