import type { FlextrawurstEvent } from "../events/types.ts";

export interface WorldTimelineFrame {
  index: number;
  event_id: string;
  event_type: string;
  timestamp: string;
  actor_type: string;
  actor_id: string;
  target_type: string | null;
  target_id: string | null;
  causal_links: string[];
  summary: string;
}

export interface WorldTimeline {
  frames: WorldTimelineFrame[];
  first_event_id: string | null;
  last_event_id: string | null;
  tick_count: number;
  entity_count: number;
}

function buildSummary(event: FlextrawurstEvent): string {
  const p = event.payload as Record<string, unknown>;

  if (event.event_type === "system.seed_entity") {
    const entityId = typeof p.entity_id === "string" ? p.entity_id : event.target_id ?? "?";
    return `Seed: ${entityId} als kanonischer Entitätsslot registriert`;
  }

  if (event.event_type === "system.tick") {
    const num = typeof p.tick_number === "number" ? p.tick_number : "?";
    return `Tick #${num}: Weltpuls erzeugt`;
  }

  if (event.event_type === "entity.state_changed") {
    if (p.transition_rule === "presence_pulse") {
      const patch = (p.state_patch ?? {}) as Record<string, unknown>;
      const tickNum =
        typeof patch.last_tick_number === "number" ? patch.last_tick_number : "?";
      return `Spur: ${event.target_id ?? "?"} durch Weltpuls #${tickNum} berührt`;
    }
    return `Zustand: ${event.target_id ?? event.actor_id} hat sich verändert`;
  }

  if (event.event_type === "entity.post_stub") {
    return `Beitrag: ${event.actor_id} hat etwas gepostet`;
  }

  return `Event: ${event.event_type}`;
}

export function buildWorldTimeline(
  events: readonly FlextrawurstEvent[]
): WorldTimeline {
  const seededEntityIds = new Set<string>();
  for (const e of events) {
    if (
      e.event_type === "system.seed_entity" &&
      typeof e.payload.entity_id === "string"
    ) {
      seededEntityIds.add(e.payload.entity_id as string);
    }
  }

  const tick_count = events.filter((e) => e.event_type === "system.tick").length;

  const frames: WorldTimelineFrame[] = events.map((event, index) => ({
    index,
    event_id: event.event_id,
    event_type: event.event_type,
    timestamp: event.timestamp,
    actor_type: event.actor_type,
    actor_id: event.actor_id,
    target_type: event.target_type,
    target_id: event.target_id,
    causal_links: [...event.causal_links],
    summary: buildSummary(event),
  }));

  return {
    frames,
    first_event_id: events.length > 0 ? events[0].event_id : null,
    last_event_id: events.length > 0 ? events[events.length - 1].event_id : null,
    tick_count,
    entity_count: seededEntityIds.size,
  };
}
