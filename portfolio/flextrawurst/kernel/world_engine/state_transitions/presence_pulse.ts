import type { FlextrawurstEvent } from "../../events/types.ts";
import type { EntityProjection } from "../../projections/entity_projection.ts";

export interface PresencePulseParams {
  event_id: string;
  timestamp?: string;
}

export function applyPresencePulse(
  tick: FlextrawurstEvent,
  projection: EntityProjection,
  params: PresencePulseParams
): FlextrawurstEvent | null {
  if (!projection.exists || projection.actor_type !== "nameless_ai") {
    return null;
  }

  const tickPayload = tick.payload as Record<string, unknown>;
  const tickNumber = tickPayload.tick_number as number;
  const worldTime = tickPayload.world_time as string;

  const existingCount =
    typeof projection.current_state.presence_pulse_count === "number"
      ? projection.current_state.presence_pulse_count
      : 0;

  const now = new Date().toISOString();

  return {
    event_id: params.event_id,
    event_type: "entity.state_changed",
    actor_type: "world_engine",
    actor_id: "world_engine",
    target_type: "nameless_ai",
    target_id: projection.entity_id,
    timestamp: params.timestamp ?? now,
    payload: {
      transition_rule: "presence_pulse",
      state_patch: {
        last_tick_number: tickNumber,
        last_world_time: worldTime,
        presence_pulse_count: existingCount + 1,
      },
    },
    kontext: null,
    causal_links: [tick.event_id],
    origin_type: "live_world",
    created_by_process: "state_transition_presence_pulse",
    visibility_layer: "system",
    projection_policy: null,
  };
}
