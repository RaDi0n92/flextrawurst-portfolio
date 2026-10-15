import type { FlextrawurstEvent } from "../events/types.ts";

export function findEventsByType(
  events: readonly FlextrawurstEvent[],
  event_type: string
): FlextrawurstEvent[] {
  return events.filter((e) => e.event_type === event_type);
}

export function findEventsByActor(
  events: readonly FlextrawurstEvent[],
  actor_type: string,
  actor_id?: string
): FlextrawurstEvent[] {
  return events.filter(
    (e) =>
      e.actor_type === actor_type &&
      (actor_id === undefined || e.actor_id === actor_id)
  );
}

export function findEventsByTarget(
  events: readonly FlextrawurstEvent[],
  target_type: string,
  target_id?: string
): FlextrawurstEvent[] {
  return events.filter(
    (e) =>
      e.target_type === target_type &&
      (target_id === undefined || e.target_id === target_id)
  );
}

export function findCausalChildren(
  events: readonly FlextrawurstEvent[],
  event_id: string
): FlextrawurstEvent[] {
  return events.filter((e) => e.causal_links.includes(event_id));
}

export function findCausalParents(
  events: readonly FlextrawurstEvent[],
  event_id: string
): FlextrawurstEvent[] {
  const event = events.find((e) => e.event_id === event_id);
  if (!event || event.causal_links.length === 0) return [];
  const parentIds = new Set(event.causal_links);
  return events.filter((e) => parentIds.has(e.event_id));
}

export function findEntityTrace(
  events: readonly FlextrawurstEvent[],
  entity_id: string
): FlextrawurstEvent[] {
  return events.filter(
    (e) =>
      (e.event_type === "system.seed_entity" &&
        e.payload.entity_id === entity_id) ||
      e.target_id === entity_id ||
      e.actor_id === entity_id
  );
}
