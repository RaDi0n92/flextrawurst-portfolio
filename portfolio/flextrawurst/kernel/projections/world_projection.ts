import type { FlextrawurstEvent } from "../events/types.ts";
import { buildEntityProjection } from "./entity_projection.ts";
import type { EntityProjection } from "./entity_projection.ts";

export interface WorldProjection {
  entities: Record<string, EntityProjection>;
  entity_count: number;
  last_event_id: string | null;
}

export function buildWorldProjection(
  events: readonly FlextrawurstEvent[]
): WorldProjection {
  // Auto-discover all seeded entity IDs from the event stream
  const entityIdSet = new Set<string>();
  for (const event of events) {
    if (
      event.event_type === "system.seed_entity" &&
      typeof event.payload.entity_id === "string"
    ) {
      entityIdSet.add(event.payload.entity_id as string);
    }
  }

  const entities: Record<string, EntityProjection> = {};
  for (const entityId of entityIdSet) {
    const proj = buildEntityProjection(entityId, events);
    if (proj.exists) {
      entities[entityId] = proj;
    }
  }

  const last_event_id =
    events.length > 0 ? events[events.length - 1].event_id : null;

  return {
    entities,
    entity_count: Object.keys(entities).length,
    last_event_id,
  };
}
