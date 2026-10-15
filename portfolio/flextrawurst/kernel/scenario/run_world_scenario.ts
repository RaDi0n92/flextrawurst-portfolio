import type { InMemoryEventStore } from "../events/event_store.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { WorldScenario } from "./world_scenario.ts";
import { createSeedEvent } from "../entities/seed_entities.ts";
import { runWorldCycles } from "../world_engine/run_world_cycles.ts";
import { buildWorldAudit } from "../audit/world_audit.ts";
import { buildWorldReplayFrames } from "../replay/world_replay_frames.ts";

export function runWorldScenario(
  store: InMemoryEventStore,
  scenario: WorldScenario
): WorldInspectionPack {
  for (const entityId of scenario.entity_ids) {
    store.append(
      createSeedEvent({
        entity_id: entityId,
        event_id: `evt-seed-${scenario.scenario_id}-${entityId}`,
        timestamp: scenario.seed_timestamp,
      })
    );
  }

  runWorldCycles(store, scenario.cycles);

  const events = store.getAll();
  const audit = buildWorldAudit(events);
  const replay_frames = buildWorldReplayFrames(events);

  const tick_count = [...events].filter(
    (e) => e.event_type === "system.tick"
  ).length;

  const trace_count = [...events].filter(
    (e) =>
      e.event_type === "entity.state_changed" &&
      (e.payload as Record<string, unknown>).transition_rule === "presence_pulse"
  ).length;

  return {
    pack_version: 1,
    scenario_id: scenario.scenario_id,
    label: scenario.label,
    event_count: events.length,
    entity_slot_count: scenario.entity_ids.length,
    tick_count,
    trace_count,
    audit_ok: audit.integrity.ok,
    events: Object.freeze([...events]),
    audit,
    replay_frames,
    notes: [
      "Slots bleiben Slots. Kein Einzug. Kein Leben.",
      "Keine UI, keine AI, kein Renderer, kein Postgres beteiligt.",
    ],
  };
}
