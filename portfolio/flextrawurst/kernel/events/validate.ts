import { ALLOWED_EVENT_TYPES } from "./types.ts";

const ACTOR_TYPES = new Set([
  "nameless_ai",
  "human",
  "system_layer",
  "world_engine",
  "policy_engine",
]);

const ORIGIN_TYPES = new Set([
  "live_world",
  "flarum_import",
  "chat_import",
  "obsidian_import",
  "manual_seed",
  "system_analysis",
  "simulation",
]);

const VISIBILITY_LAYERS = new Set(["public", "system", "internal"]);

const ALLOWED_SET = new Set<string>(ALLOWED_EVENT_TYPES);

export function validateEvent(
  event: unknown,
  existingIds: ReadonlySet<string>
): void {
  if (typeof event !== "object" || event === null) {
    throw new Error("Event muss ein Objekt sein");
  }

  if ("source" in event) {
    throw new Error(
      'Feld "source" ist verboten — verwende actor_type, origin_type, created_by_process'
    );
  }
  if ("redaction_state" in event) {
    throw new Error(
      'Feld "redaction_state" ist verboten — Redaction läuft über Policy-Events und Projektionen'
    );
  }

  const e = event as Record<string, unknown>;

  if (!e.event_id || typeof e.event_id !== "string") {
    throw new Error("event_id muss ein nicht-leerer String sein");
  }
  if (existingIds.has(e.event_id)) {
    throw new Error(`event_id "${e.event_id}" ist nicht eindeutig`);
  }

  if (!ALLOWED_SET.has(e.event_type as string)) {
    throw new Error(
      `event_type "${e.event_type}" nicht erlaubt. Erlaubt: ${[...ALLOWED_SET].join(", ")}`
    );
  }

  if (!ACTOR_TYPES.has(e.actor_type as string)) {
    throw new Error(`actor_type "${e.actor_type}" nicht erlaubt`);
  }

  if (!ORIGIN_TYPES.has(e.origin_type as string)) {
    throw new Error(`origin_type "${e.origin_type}" nicht erlaubt`);
  }

  if (!VISIBILITY_LAYERS.has(e.visibility_layer as string)) {
    throw new Error(`visibility_layer "${e.visibility_layer}" nicht erlaubt`);
  }

  if (e.event_type === "system.seed_entity") {
    if (e.actor_type !== "world_engine" || e.origin_type !== "manual_seed") {
      throw new Error(
        'system.seed_entity erfordert actor_type "world_engine" und origin_type "manual_seed"'
      );
    }
  }

  if (e.event_type === "system.tick") {
    if (e.actor_type !== "world_engine") {
      throw new Error('system.tick erfordert actor_type "world_engine"');
    }
    if (e.actor_id !== "world_engine") {
      throw new Error('system.tick erfordert actor_id "world_engine"');
    }
    if (e.target_type !== null) {
      throw new Error("system.tick erfordert target_type null");
    }
    if (e.target_id !== null) {
      throw new Error("system.tick erfordert target_id null");
    }
    if (e.origin_type !== "live_world") {
      throw new Error('system.tick erfordert origin_type "live_world"');
    }
    if (!e.created_by_process || typeof e.created_by_process !== "string") {
      throw new Error("system.tick erfordert created_by_process (nicht null)");
    }
    const p =
      typeof e.payload === "object" && e.payload !== null
        ? (e.payload as Record<string, unknown>)
        : {};
    if (typeof p.tick_number !== "number") {
      throw new Error("system.tick erfordert payload.tick_number als number");
    }
    if (typeof p.world_time !== "string") {
      throw new Error("system.tick erfordert payload.world_time als string");
    }
    if (p.tick_reason !== "manual_test") {
      throw new Error('system.tick erfordert payload.tick_reason "manual_test"');
    }
  }

  if (e.event_type === "entity.state_changed") {
    if (e.actor_type === "world_engine") {
      if (e.created_by_process !== "state_transition_presence_pulse") {
        throw new Error(
          'entity.state_changed mit actor_type "world_engine" erfordert created_by_process "state_transition_presence_pulse"'
        );
      }
      if (e.target_type !== "nameless_ai") {
        throw new Error(
          'entity.state_changed mit actor_type "world_engine" erfordert target_type "nameless_ai"'
        );
      }
      if (!e.target_id || typeof e.target_id !== "string") {
        throw new Error(
          'entity.state_changed mit actor_type "world_engine" erfordert target_id'
        );
      }
      if (!Array.isArray(e.causal_links) || (e.causal_links as unknown[]).length === 0) {
        throw new Error(
          'entity.state_changed mit actor_type "world_engine" erfordert mindestens einen causal_link'
        );
      }
      const p =
        typeof e.payload === "object" && e.payload !== null
          ? (e.payload as Record<string, unknown>)
          : {};
      if (p.transition_rule !== "presence_pulse") {
        throw new Error(
          'entity.state_changed mit actor_type "world_engine" erfordert payload.transition_rule "presence_pulse"'
        );
      }
      const patch =
        typeof p.state_patch === "object" && p.state_patch !== null
          ? (p.state_patch as Record<string, unknown>)
          : null;
      if (!patch) {
        throw new Error(
          "entity.state_changed (presence_pulse) erfordert payload.state_patch"
        );
      }
      if (typeof patch.last_tick_number !== "number") {
        throw new Error(
          "entity.state_changed (presence_pulse) erfordert state_patch.last_tick_number als number"
        );
      }
      if (typeof patch.last_world_time !== "string") {
        throw new Error(
          "entity.state_changed (presence_pulse) erfordert state_patch.last_world_time als string"
        );
      }
      if (typeof patch.presence_pulse_count !== "number") {
        throw new Error(
          "entity.state_changed (presence_pulse) erfordert state_patch.presence_pulse_count als number"
        );
      }
    } else if (e.actor_type !== "nameless_ai" && e.actor_type !== "human") {
      throw new Error(
        'entity.state_changed erfordert actor_type "nameless_ai", "human" oder "world_engine"'
      );
    }
  }

  if (e.event_type === "entity.post_stub") {
    if (e.actor_type !== "nameless_ai" && e.actor_type !== "human") {
      throw new Error(
        'entity.post_stub erfordert actor_type "nameless_ai" oder "human"'
      );
    }
  }

  if (e.causal_links !== undefined) {
    if (!Array.isArray(e.causal_links)) {
      throw new Error("causal_links muss ein Array sein");
    }
    for (const link of e.causal_links as unknown[]) {
      if (typeof link !== "string" || !existingIds.has(link)) {
        throw new Error(`causal_link "${link}" verweist auf unbekannte event_id`);
      }
    }
  }

  if (
    typeof e.timestamp !== "string" ||
    isNaN(Date.parse(e.timestamp))
  ) {
    throw new Error("timestamp muss ein gültiger ISO 8601 String sein");
  }
}
