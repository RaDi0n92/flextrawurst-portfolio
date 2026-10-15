import type { WorldOSSpine } from "../os_spine/world_os_spine.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { WorldOSSpineImportExtension } from "../os_spine/world_os_spine_import_extension.ts";
import {
  createVisualMeaning,
} from "./visual_meaning_model.ts";
import type { VisualMeaning } from "./visual_meaning_model.ts";

const FIXED_TS = "2026-01-01T00:00:00.000Z";

export function buildVisualMeaningsFromSpine(
  spine: WorldOSSpine,
  pack: WorldInspectionPack,
  importExtension: WorldOSSpineImportExtension
): VisualMeaning[] {
  const results: VisualMeaning[] = [];

  const seedEventBySlot = new Map<string, string>();
  for (const e of pack.events) {
    if (
      e.event_type === "system.seed_entity" &&
      typeof e.payload.entity_id === "string"
    ) {
      seedEventBySlot.set(e.payload.entity_id as string, e.event_id);
    }
  }

  for (const slot of spine.slots) {
    const seedEventId = seedEventBySlot.get(slot.slot_id);
    results.push(
      createVisualMeaning({
        visual_id: `vm-node-pulse-${slot.slot_id}`,
        visual_kind: "node_pulse",
        source_event_ids: seedEventId ? [seedEventId] : [],
        source_slot_ids: seedEventId ? [] : [slot.slot_id],
        meaning: `Entitätsslot ${slot.slot_id} im Weltpuls. Kein Einzug. Kein Wesen.`,
        intensity: 0.3,
        confidence: "structural",
        created_from: "buildVisualMeaningsFromSpine",
        created_at: FIXED_TS,
        is_live_flextrawurst_state: true,
        requires_start_decision: false,
      })
    );
  }

  for (const slot of spine.slots) {
    results.push(
      createVisualMeaning({
        visual_id: `vm-activation-block-${slot.slot_id}`,
        visual_kind: "activation_block",
        source_slot_ids: [slot.slot_id],
        meaning: `Slot ${slot.slot_id} ist durch Activation Firewall blockiert. Kein Einzug möglich.`,
        intensity: 0.8,
        confidence: "structural",
        created_from: "buildVisualMeaningsFromSpine",
        created_at: FIXED_TS,
        is_live_flextrawurst_state: true,
        requires_start_decision: false,
      })
    );
  }

  const flarumMarkers = buildFlarumOriginMarkers(importExtension);
  results.push(...flarumMarkers);

  return results;
}

export function buildFlarumOriginMarkers(
  importExtension: WorldOSSpineImportExtension
): VisualMeaning[] {
  const results: VisualMeaning[] = [];

  for (const mapping of importExtension.dry_run.mappings) {
    if (
      mapping.mapping_status === "matched_canonical_slot" &&
      mapping.slot_id !== null
    ) {
      results.push(
        createVisualMeaning({
          visual_id: `vm-origin-marker-${mapping.account_id}`,
          visual_kind: "origin_marker",
          source_slot_ids: [mapping.slot_id],
          meaning: `Flarum-Herkunft für Account ${mapping.account_id}. Ursprungsraum, kein aktueller Lebensraum.`,
          intensity: 0.5,
          confidence: "inferred",
          created_from: "buildFlarumOriginMarkers",
          created_at: FIXED_TS,
          origin_layer: "flarum_vorphase",
          is_live_flextrawurst_state: false,
          requires_start_decision: true,
        })
      );
    }
  }

  return results;
}
