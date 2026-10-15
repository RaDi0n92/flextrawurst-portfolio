export type ActorType =
  | "nameless_ai"
  | "human"
  | "system_layer"
  | "world_engine"
  | "policy_engine";

export type TargetType =
  | "nameless_ai"
  | "human"
  | "system_layer"
  | "raum"
  | "artefakt"
  | "graph"
  | "event"
  | null;

export type OriginType =
  | "live_world"
  | "flarum_import"
  | "chat_import"
  | "obsidian_import"
  | "manual_seed"
  | "system_analysis"
  | "simulation";

export type VisibilityLayer = "public" | "system" | "internal";

export type PulseSpeed = "none" | "slow" | "normal" | "fast";

export const ALLOWED_EVENT_TYPES = [
  "system.seed_entity",
  "system.tick",
  "entity.state_changed",
  "entity.post_stub",
] as const;

export type EventType = (typeof ALLOWED_EVENT_TYPES)[number];

export interface FlextrawurstEvent {
  event_id: string;
  event_type: EventType;
  actor_type: ActorType;
  actor_id: string;
  target_type: TargetType;
  target_id: string | null;
  timestamp: string;
  payload: Record<string, unknown>;
  kontext: string | null;
  causal_links: string[];
  origin_type: OriginType;
  created_by_process: string | null;
  visibility_layer: VisibilityLayer;
  projection_policy: string | null;
}
