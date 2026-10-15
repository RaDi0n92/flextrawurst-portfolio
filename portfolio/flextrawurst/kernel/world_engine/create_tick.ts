import type { FlextrawurstEvent } from "../events/types.ts";

export interface CreateTickParams {
  event_id: string;
  tick_number: number;
  timestamp?: string;
  world_time?: string;
}

export function createWorldTick(params: CreateTickParams): FlextrawurstEvent {
  const now = new Date().toISOString();
  return {
    event_id: params.event_id,
    event_type: "system.tick",
    actor_type: "world_engine",
    actor_id: "world_engine",
    target_type: null,
    target_id: null,
    timestamp: params.timestamp ?? now,
    payload: {
      tick_number: params.tick_number,
      tick_reason: "manual_test",
      world_time: params.world_time ?? now,
    },
    kontext: null,
    causal_links: [],
    origin_type: "live_world",
    created_by_process: "world_engine_tick",
    visibility_layer: "system",
    projection_policy: null,
  };
}
