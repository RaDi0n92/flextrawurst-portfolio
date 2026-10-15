import type { EntitySlot } from "../slots/entity_slot.ts";
import type { ProvenanceRecord } from "../provenance/provenance_record.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";

export type ActivationReadinessStatus =
  | "not_ready"
  | "partially_ready"
  | "ready_for_manual_activation"
  | "blocked";

export interface ActivationReadinessReport {
  slot_id: string;
  status: ActivationReadinessStatus;
  missing: string[];
  blockers: string[];
  warnings: string[];
  may_activate_now: boolean;
}

const REQUIRED_FOR_ACTIVATION = [
  "resident_profile",
  "explicit_daniel_activation_approval",
  "memory_import",
  "activation_event_type",
  "ai_runtime_binding",
] as const;

const STRUCTURAL_BLOCKERS = [
  "no_occupancy_without_explicit_activation",
] as const;

export function assessActivationReadiness(
  slot: EntitySlot,
  _provenanceRecords: ProvenanceRecord[],
  _pack: WorldInspectionPack
): ActivationReadinessReport {
  return {
    slot_id: slot.slot_id,
    status: "not_ready",
    missing: [...REQUIRED_FOR_ACTIVATION],
    blockers: [...STRUCTURAL_BLOCKERS],
    warnings: [
      "presence_pulse ist kein Lebenszeichen.",
      "Seed erzeugt keinen Einzug.",
      "Slot ist technischer Träger, kein aktives Wesen.",
    ],
    may_activate_now: false,
  };
}

export function assessAllSlotsActivationReadiness(
  slots: EntitySlot[],
  provenanceRecords: ProvenanceRecord[],
  pack: WorldInspectionPack
): ActivationReadinessReport[] {
  return slots.map((slot) =>
    assessActivationReadiness(slot, provenanceRecords, pack)
  );
}
