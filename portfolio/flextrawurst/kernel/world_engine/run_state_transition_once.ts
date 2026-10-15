import type { FlextrawurstEvent } from "../events/types.ts";
import type { InMemoryEventStore } from "../events/event_store.ts";
import { buildEntityProjection } from "../projections/entity_projection.ts";
import { applyPresencePulse } from "./state_transitions/presence_pulse.ts";

export interface RunStateTransitionParams {
  event_id: string;
  entityId: string;
  timestamp?: string;
}

export function runStateTransitionOnce(
  store: InMemoryEventStore,
  tick: FlextrawurstEvent,
  params: RunStateTransitionParams
): FlextrawurstEvent | null {
  const projection = buildEntityProjection(params.entityId, store.getAll());

  const event = applyPresencePulse(tick, projection, {
    event_id: params.event_id,
    timestamp: params.timestamp,
  });

  if (event === null) return null;

  store.append(event);
  return store.getById(event.event_id)!;
}
