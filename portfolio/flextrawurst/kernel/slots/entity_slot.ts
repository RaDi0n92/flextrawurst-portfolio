import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import { CANONICAL_ENTITY_IDS } from "../entities/seed_entities.ts";

export type EntitySlotStatus =
  | "reserved"
  | "seeded"
  | "import_mapped"
  | "activation_ready"
  | "occupied";

export type EntitySlotSource =
  | "canonical_seed"
  | "flarum_account_mapping"
  | "manual_reservation";

export interface EntitySlot {
  slot_id: string;
  account_id: string;
  status: EntitySlotStatus;
  canonical: boolean;
  source: EntitySlotSource;
  occupant_id: string | null;
  notes: string[];
}

function deriveStatusFromEvents(
  slotId: string,
  events: readonly FlextrawurstEvent[]
): EntitySlotStatus {
  const wasSeeded = events.some(
    (e) =>
      e.event_type === "system.seed_entity" &&
      e.payload.entity_id === slotId
  );
  if (wasSeeded) return "seeded";
  return "reserved";
}

export function buildCanonicalEntitySlots(): EntitySlot[] {
  return CANONICAL_ENTITY_IDS.map((id) => ({
    slot_id: id,
    account_id: id,
    status: "reserved" as EntitySlotStatus,
    canonical: true,
    source: "canonical_seed" as EntitySlotSource,
    occupant_id: null,
    notes: [
      "Kanonischer Entitätsslot. Kein Einzug. Kein Wesen. Reservierter Träger.",
    ],
  }));
}

export function buildSlotsFromScenarioPack(
  pack: WorldInspectionPack
): EntitySlot[] {
  const events = pack.events;

  const seededIds = new Set<string>();
  for (const e of events) {
    if (
      e.event_type === "system.seed_entity" &&
      typeof e.payload.entity_id === "string"
    ) {
      seededIds.add(e.payload.entity_id as string);
    }
  }

  const canonicalSet = new Set<string>(CANONICAL_ENTITY_IDS);

  return [...seededIds].map((id) => ({
    slot_id: id,
    account_id: id,
    status: deriveStatusFromEvents(id, events),
    canonical: canonicalSet.has(id),
    source: "canonical_seed" as EntitySlotSource,
    occupant_id: null,
    notes: [
      "Entitätsslot aus Scenario-InspectionPack. Kein Einzug. Kein Wesen.",
    ],
  }));
}
