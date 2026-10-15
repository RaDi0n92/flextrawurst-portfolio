import type { FlextrawurstEvent } from "../events/types.ts";
import type { InMemoryEventStore } from "../events/event_store.ts";

export const CANONICAL_ENTITY_IDS = [
  "Schorschel",
  "Resonanzknoten",
  "F3INSCHM3CK3R",
  "träumerlie",
  "R1ZZ1",
  "jumpa",
  "dak+gord-system",
] as const;

export type CanonicalEntityId = (typeof CANONICAL_ENTITY_IDS)[number];

export interface CreateSeedEventParams {
  entity_id: string;
  event_id: string;
  timestamp?: string;
}

export function createSeedEvent(
  params: CreateSeedEventParams
): FlextrawurstEvent {
  const now = new Date().toISOString();
  return {
    event_id: params.event_id,
    event_type: "system.seed_entity",
    actor_type: "world_engine",
    actor_id: "world_engine",
    target_type: "nameless_ai",
    target_id: params.entity_id,
    timestamp: params.timestamp ?? now,
    payload: {
      entity_id: params.entity_id,
      canonical: true,
      seed_group: "initial_six_nameless_ai",
    },
    kontext: null,
    causal_links: [],
    origin_type: "manual_seed",
    created_by_process: "canonical_entity_seed",
    visibility_layer: "system",
    projection_policy: null,
  };
}

export function seedCanonicalEntities(
  store: InMemoryEventStore,
  timestamp?: string
): void {
  for (const entityId of CANONICAL_ENTITY_IDS) {
    store.append(
      createSeedEvent({
        entity_id: entityId,
        event_id: `evt-seed-canonical-${entityId}`,
        timestamp,
      })
    );
  }
}
