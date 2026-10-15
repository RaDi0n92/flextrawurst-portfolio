import type { FlextrawurstEvent } from "../events/types.ts";
import type { EntityProjection } from "../projections/entity_projection.ts";
import type { RenderHints } from "../../vme/meaning_projection.ts";
import { buildWorldProjection } from "../projections/world_projection.ts";
import { buildWorldRenderHints } from "../../vme/world_meaning_projection.ts";

export interface WorldSnapshot {
  last_event_id: string | null;
  event_count: number;
  tick_count: number;
  entity_count: number;
  transition_count: number;
  latest_tick_number: number | null;
  entities: Record<string, EntityProjection>;
  render_hints: RenderHints[];
}

export function buildWorldSnapshot(
  events: readonly FlextrawurstEvent[]
): WorldSnapshot {
  const worldProjection = buildWorldProjection(events);
  const render_hints = buildWorldRenderHints(worldProjection, events);

  const tick_count = events.filter((e) => e.event_type === "system.tick").length;

  const transition_count = events.filter(
    (e) =>
      e.event_type === "entity.state_changed" &&
      e.actor_type === "world_engine" &&
      typeof e.payload === "object" &&
      e.payload !== null &&
      (e.payload as Record<string, unknown>).transition_rule === "presence_pulse"
  ).length;

  const tickEvents = events.filter((e) => e.event_type === "system.tick");
  const latest_tick_number =
    tickEvents.length > 0
      ? ((tickEvents[tickEvents.length - 1].payload as Record<string, unknown>)
          .tick_number as number)
      : null;

  return {
    last_event_id: events.length > 0 ? events[events.length - 1].event_id : null,
    event_count: events.length,
    tick_count,
    entity_count: worldProjection.entity_count,
    transition_count,
    latest_tick_number,
    entities: worldProjection.entities,
    render_hints,
  };
}
