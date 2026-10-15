import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";

export type ProvenanceType =
  | "canonical_seed"
  | "runtime_generated"
  | "flarum_import_candidate"
  | "chat_import_candidate"
  | "obsidian_import_candidate"
  | "manual_note";

export type ProvenanceConfidence =
  | "structural"
  | "imported"
  | "manual"
  | "unknown";

export interface ProvenanceRecord {
  record_id: string;
  subject_type: "entity_slot" | "event" | "scenario" | "inspection_pack";
  subject_id: string;
  provenance_type: ProvenanceType;
  origin_label: string;
  source_event_ids: string[];
  confidence: ProvenanceConfidence;
  notes: string[];
}

export function buildProvenanceForInspectionPack(
  pack: WorldInspectionPack
): ProvenanceRecord[] {
  const records: ProvenanceRecord[] = [];

  records.push({
    record_id: `prov-pack-${pack.scenario_id}`,
    subject_type: "inspection_pack",
    subject_id: pack.scenario_id,
    provenance_type: "canonical_seed",
    origin_label: "in_memory_scenario_runtime",
    source_event_ids: [],
    confidence: "structural",
    notes: [
      "InspectionPack aus deterministischem Scenario-Lauf. Kein echtes Import-Ereignis.",
    ],
  });

  records.push({
    record_id: `prov-scenario-${pack.scenario_id}`,
    subject_type: "scenario",
    subject_id: pack.scenario_id,
    provenance_type: "canonical_seed",
    origin_label: "createInitialSixSlotsThreeTickScenario",
    source_event_ids: [],
    confidence: "structural",
    notes: ["Deterministisches Scenario. Kein Import. Keine Aktivierung."],
  });

  for (const event of pack.events) {
    if (event.event_type === "system.seed_entity") {
      records.push({
        record_id: `prov-seed-${event.event_id}`,
        subject_type: "event",
        subject_id: event.event_id,
        provenance_type: "canonical_seed",
        origin_label: event.created_by_process ?? "canonical_entity_seed",
        source_event_ids: [event.event_id],
        confidence: "structural",
        notes: ["Seed-Event. Registriert Entitätsslot. Kein Einzug."],
      });
    } else if (
      event.event_type === "system.tick" ||
      event.event_type === "entity.state_changed"
    ) {
      records.push({
        record_id: `prov-rt-${event.event_id}`,
        subject_type: "event",
        subject_id: event.event_id,
        provenance_type: "runtime_generated",
        origin_label: "world_engine_runtime",
        source_event_ids: [event.event_id],
        confidence: "structural",
        notes: ["Runtime-generiertes Event. Deterministisch. Kein Import."],
      });
    }
  }

  return records;
}

export function buildProvenanceForSlots(
  slots: EntitySlot[],
  pack: WorldInspectionPack
): ProvenanceRecord[] {
  const seedEventsBySlot = new Map<string, string>();
  for (const e of pack.events) {
    if (
      e.event_type === "system.seed_entity" &&
      typeof e.payload.entity_id === "string"
    ) {
      seedEventsBySlot.set(e.payload.entity_id as string, e.event_id);
    }
  }

  return slots.map((slot) => {
    const seedEventId = seedEventsBySlot.get(slot.slot_id);
    return {
      record_id: `prov-slot-${slot.slot_id}`,
      subject_type: "entity_slot",
      subject_id: slot.slot_id,
      provenance_type: "canonical_seed",
      origin_label: "canonical_entity_seed",
      source_event_ids: seedEventId ? [seedEventId] : [],
      confidence: "structural",
      notes: [
        "Kanonischer Slot. Nur Träger. Kein Wesen. Kein Einzug. Kein Import-Mapping in diesem Ring.",
      ],
    };
  });
}
