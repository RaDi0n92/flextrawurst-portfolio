import type { FlextrawurstEvent } from "../events/types.ts";

export interface WorldIntegrityCounts {
  total_events: number;
  seed_events: number;
  tick_events: number;
  state_changed_events: number;
  unknown_events: number;
}

export interface WorldIntegrityReport {
  ok: boolean;
  errors: string[];
  warnings: string[];
  counts: WorldIntegrityCounts;
  forbidden_fields_found: string[];
  duplicate_event_ids: string[];
  missing_causal_links: string[];
  orphan_transitions: string[];
}

const KNOWN_EVENT_TYPES = new Set([
  "system.seed_entity",
  "system.tick",
  "entity.state_changed",
  "entity.post_stub",
]);

export function checkWorldIntegrity(
  events: readonly FlextrawurstEvent[]
): WorldIntegrityReport {
  const errors: string[] = [];
  const warnings: string[] = [];
  const forbidden_fields_found: string[] = [];
  const duplicate_event_ids: string[] = [];
  const missing_causal_links: string[] = [];
  const orphan_transitions: string[] = [];

  const seenIds = new Set<string>();
  const tickIds = new Set<string>();
  const seededEntityIds = new Set<string>();

  let seed_events = 0;
  let tick_events = 0;
  let state_changed_events = 0;
  let unknown_events = 0;

  // First pass: collect tick IDs and seeded entity IDs
  for (const event of events) {
    if (event.event_type === "system.tick") tickIds.add(event.event_id);
    if (
      event.event_type === "system.seed_entity" &&
      typeof event.payload.entity_id === "string"
    ) {
      seededEntityIds.add(event.payload.entity_id as string);
    }
  }

  // Second pass: full checks
  for (const event of events) {
    const raw = event as unknown as Record<string, unknown>;

    // Forbidden fields
    if ("source" in raw) {
      forbidden_fields_found.push(`source on ${event.event_id}`);
      errors.push(`Event ${event.event_id} hat verbotenes Feld 'source'`);
    }
    if ("redaction_state" in raw) {
      forbidden_fields_found.push(`redaction_state on ${event.event_id}`);
      errors.push(`Event ${event.event_id} hat verbotenes Feld 'redaction_state'`);
    }

    // Duplicate IDs
    if (seenIds.has(event.event_id)) {
      duplicate_event_ids.push(event.event_id);
      errors.push(`Doppelte event_id: ${event.event_id}`);
    } else {
      seenIds.add(event.event_id);
    }

    // Count by type
    if (event.event_type === "system.seed_entity") seed_events++;
    else if (event.event_type === "system.tick") tick_events++;
    else if (event.event_type === "entity.state_changed") state_changed_events++;
    else if (!KNOWN_EVENT_TYPES.has(event.event_type)) unknown_events++;

    // Tick actor check
    if (event.event_type === "system.tick" && event.actor_type !== "world_engine") {
      errors.push(`system.tick ${event.event_id} hat actor_type '${event.actor_type}' statt 'world_engine'`);
    }

    // system_layer actors: warning in this ring
    if (event.actor_type === "system_layer") {
      warnings.push(`Event ${event.event_id} hat actor_type 'system_layer' — unerwartet in diesem Ring`);
    }

    // presence_pulse transition checks
    if (
      event.event_type === "entity.state_changed" &&
      event.actor_type === "world_engine" &&
      typeof event.payload === "object" &&
      (event.payload as Record<string, unknown>).transition_rule === "presence_pulse"
    ) {
      // Must have causal_links
      if (!event.causal_links || event.causal_links.length === 0) {
        missing_causal_links.push(event.event_id);
        errors.push(`presence_pulse Transition ${event.event_id} hat keine causal_links`);
      } else {
        // All causal_links must point to existing tick events
        for (const link of event.causal_links) {
          if (!tickIds.has(link)) {
            errors.push(
              `presence_pulse Transition ${event.event_id} verweist auf unbekannten Tick '${link}'`
            );
          }
        }
      }

      // target_id must be a seeded entity
      if (!event.target_id || !seededEntityIds.has(event.target_id)) {
        orphan_transitions.push(event.event_id);
        errors.push(
          `presence_pulse Transition ${event.event_id} verweist auf unbekannte Entität '${event.target_id}'`
        );
      }
    }
  }

  const ok = errors.length === 0;

  return {
    ok,
    errors,
    warnings,
    counts: {
      total_events: events.length,
      seed_events,
      tick_events,
      state_changed_events,
      unknown_events,
    },
    forbidden_fields_found,
    duplicate_event_ids,
    missing_causal_links,
    orphan_transitions,
  };
}
