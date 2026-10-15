import type { EntityProjection } from "../kernel/projections/entity_projection.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";

export interface RenderHints {
  node_id: string;
  node_opacity: number;
  node_pulse_speed: "none" | "slow" | "normal" | "fast";
  node_layer: number;
  label: string;
  explanation: string;
  source_event_ids: string[];
}

export function buildRenderHints(
  projection: EntityProjection,
  events: readonly FlextrawurstEvent[]
): RenderHints {
  if (!projection.exists) {
    return {
      node_id: projection.entity_id,
      node_opacity: 0.0,
      node_pulse_speed: "none",
      node_layer: 0,
      label: projection.entity_id,
      explanation: "Entität noch nicht registriert",
      source_event_ids: [],
    };
  }

  const sourceIds = events
    .filter(
      (e) =>
        e.actor_id === projection.entity_id ||
        e.payload.entity_id === projection.entity_id ||
        e.target_id === projection.entity_id
    )
    .map((e) => e.event_id);

  if (projection.current_state.awake === false) {
    return {
      node_id: projection.entity_id,
      node_opacity: 0.3,
      node_pulse_speed: "none",
      node_layer: 0,
      label: projection.entity_id,
      explanation: "Entität registriert, nicht aktiv",
      source_event_ids: sourceIds,
    };
  }

  const lastTick = projection.current_state.last_tick_number;
  const pulseCount = projection.current_state.presence_pulse_count;
  const explanation =
    typeof lastTick === "number"
      ? `Entität registriert — Weltpuls #${lastTick} empfangen, Spur ${pulseCount}`
      : "Entität registriert und aktiv";

  return {
    node_id: projection.entity_id,
    node_opacity: 1.0,
    node_pulse_speed: "normal",
    node_layer: 0,
    label: projection.entity_id,
    explanation,
    source_event_ids: sourceIds,
  };
}
