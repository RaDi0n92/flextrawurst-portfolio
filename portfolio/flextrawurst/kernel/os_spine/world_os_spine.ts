import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";
import type { ProvenanceRecord } from "../provenance/provenance_record.ts";
import type { ActivationReadinessReport } from "../activation/activation_readiness.ts";
import type { CameraReadinessReport } from "../world_camera/camera_readiness.ts";
import type { RuntimeReadinessReport } from "../runtime/runtime_readiness.ts";
import type { ConceptGuardReport } from "../concept_guard/concept_guard.ts";
import { buildSlotsFromScenarioPack } from "../slots/entity_slot.ts";
import {
  buildProvenanceForInspectionPack,
  buildProvenanceForSlots,
} from "../provenance/provenance_record.ts";
import { assessAllSlotsActivationReadiness } from "../activation/activation_readiness.ts";
import { buildWorldCameraNavigation } from "../world_camera/world_camera_navigation.ts";
import { assessCameraReadiness } from "../world_camera/camera_readiness.ts";
import { assessRuntimeReadiness } from "../runtime/runtime_readiness.ts";
import { checkConceptLanguage } from "../concept_guard/concept_guard.ts";

export interface WorldOSSpine {
  spine_version: 1;
  scenario_id: string;
  slots: EntitySlot[];
  provenance: ProvenanceRecord[];
  activation_readiness: ActivationReadinessReport[];
  camera_readiness: CameraReadinessReport;
  runtime_readiness: RuntimeReadinessReport;
  concept_guard: ConceptGuardReport;
  audit_ok: boolean;
  summary: string[];
}

export function buildWorldOSSpine(pack: WorldInspectionPack): WorldOSSpine {
  const slots = buildSlotsFromScenarioPack(pack);

  const packProvenance = buildProvenanceForInspectionPack(pack);
  const slotProvenance = buildProvenanceForSlots(slots, pack);
  const provenance = [...packProvenance, ...slotProvenance];

  const activation_readiness = assessAllSlotsActivationReadiness(
    slots,
    provenance,
    pack
  );

  const navigation = buildWorldCameraNavigation(pack.audit.camera_model);
  const camera_readiness = assessCameraReadiness(
    pack.audit.camera_model,
    navigation,
    pack.audit.timeline
  );

  const runtime_readiness = assessRuntimeReadiness(pack);

  const conceptTexts = [
    { id: "spine-scenario-id", text: pack.scenario_id },
    { id: "spine-label", text: pack.label },
    ...slots.map((s) => ({ id: `slot-${s.slot_id}`, text: s.notes.join(" ") })),
  ];
  const concept_guard = checkConceptLanguage(conceptTexts);

  const occupiedCount = slots.filter((s) => s.status === "occupied").length;

  const summary: string[] = [
    `${slots.length} kanonische Entitätsslots erkannt.`,
    `${occupiedCount} Slots belegt.`,
    `0 Wesen eingezogen.`,
    `${slots.length - occupiedCount} Slots technisch vorbereitet, aber nicht aktivierungsfrei.`,
    `Runtime deterministisch.`,
    `Weltkamera-Daten klick-/zoom-/tracebar vorbereitet.`,
    `Kein Einzug ohne explizites Aktivierungsereignis.`,
  ];

  return {
    spine_version: 1,
    scenario_id: pack.scenario_id,
    slots,
    provenance,
    activation_readiness,
    camera_readiness,
    runtime_readiness,
    concept_guard,
    audit_ok: pack.audit_ok,
    summary,
  };
}
