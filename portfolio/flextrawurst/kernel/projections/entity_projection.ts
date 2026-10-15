import type { FlextrawurstEvent } from "../events/types.ts";

export interface EntityProjection {
  entity_id: string;
  actor_type: "nameless_ai" | "human";
  exists: boolean;
  last_event_id: string | null;
  current_state: Record<string, unknown>;
}

export function buildEntityProjection(
  entityId: string,
  events: readonly FlextrawurstEvent[]
): EntityProjection {
  const projection: EntityProjection = {
    entity_id: entityId,
    actor_type: "nameless_ai",
    exists: false,
    last_event_id: null,
    current_state: {},
  };

  for (const event of events) {
    if (
      event.event_type === "system.seed_entity" &&
      event.payload.entity_id === entityId
    ) {
      projection.exists = true;
      if (event.payload.actor_type === "human") {
        projection.actor_type = "human";
      }
      if (
        event.payload.initial_state &&
        typeof event.payload.initial_state === "object"
      ) {
        projection.current_state = {
          ...(event.payload.initial_state as Record<string, unknown>),
        };
      }
      projection.last_event_id = event.event_id;
    }

    if (
      (event.event_type === "entity.state_changed" ||
        event.event_type === "entity.post_stub") &&
      (event.actor_id === entityId || event.target_id === entityId)
    ) {
      if (event.payload.state && typeof event.payload.state === "object") {
        Object.assign(
          projection.current_state,
          event.payload.state as Record<string, unknown>
        );
      }
      if (
        event.payload.state_patch &&
        typeof event.payload.state_patch === "object"
      ) {
        Object.assign(
          projection.current_state,
          event.payload.state_patch as Record<string, unknown>
        );
      }
      projection.last_event_id = event.event_id;
    }
  }

  return projection;
}
