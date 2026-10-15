import { CANONICAL_ENTITY_IDS } from "../entities/seed_entities.ts";

export interface WorldScenarioCycle {
  tick_event_id: string;
  tick_number: number;
  timestamp: string;
  world_time: string;
  transition_event_id_prefix: string;
}

export interface WorldScenario {
  scenario_id: string;
  label: string;
  description: string;
  seed_timestamp: string;
  entity_ids: string[];
  cycles: WorldScenarioCycle[];
}

export function createInitialSixSlotsThreeTickScenario(): WorldScenario {
  return {
    scenario_id: "initial_six_slots_three_ticks",
    label: "Sechs kanonische Slots, drei Weltpulse",
    description:
      "Sechs reservierte Entitätsslots durchlaufen drei kontrollierte Weltpulse. " +
      "Kein Einzug. Kein Leben. Nur deterministische Tragstruktur.",
    seed_timestamp: "2026-05-09T10:00:00.000Z",
    entity_ids: [...CANONICAL_ENTITY_IDS],
    cycles: [
      {
        tick_event_id: "evt-scenario-tick-1",
        tick_number: 1,
        timestamp: "2026-05-09T10:01:00.000Z",
        world_time: "2026-05-09T10:01:00.000Z",
        transition_event_id_prefix: "evt-scenario-pulse-tick1",
      },
      {
        tick_event_id: "evt-scenario-tick-2",
        tick_number: 2,
        timestamp: "2026-05-09T10:02:00.000Z",
        world_time: "2026-05-09T10:02:00.000Z",
        transition_event_id_prefix: "evt-scenario-pulse-tick2",
      },
      {
        tick_event_id: "evt-scenario-tick-3",
        tick_number: 3,
        timestamp: "2026-05-09T10:03:00.000Z",
        world_time: "2026-05-09T10:03:00.000Z",
        transition_event_id_prefix: "evt-scenario-pulse-tick3",
      },
    ],
  };
}
