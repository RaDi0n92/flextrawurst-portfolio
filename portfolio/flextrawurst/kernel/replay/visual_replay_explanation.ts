import type { VisualMeaning } from "../visual_meaning/visual_meaning_model.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { ActivationFirewallReport } from "../activation/activation_firewall.ts";

export interface VisualReplayExplanation {
  visual_id: string;
  why_visible: string;
  source_summary: string;
  world_ground: string;
  provenance_markers: string[];
  activation_status: "blocked" | "not_ready";
  is_live_state: boolean;
  is_import_origin: boolean;
  can_trigger_activation: false;
}

export function explainVisualMeaning(
  visual: VisualMeaning,
  _pack: WorldInspectionPack,
  firewall: ActivationFirewallReport
): VisualReplayExplanation {
  const isImportOrigin =
    visual.visual_kind === "origin_marker" ||
    visual.origin_layer === "flarum_vorphase";

  const isLiveState =
    visual.is_live_flextrawurst_state === true ||
    (!isImportOrigin && visual.is_live_flextrawurst_state !== false);

  const provenanceMarkers: string[] = [
    ...visual.source_event_ids.map((id) => `event:${id}`),
    ...visual.source_slot_ids.map((id) => `slot:${id}`),
    ...visual.source_state_ids.map((id) => `state:${id}`),
    ...visual.source_room_ids.map((id) => `room:${id}`),
  ];

  const sourceSummary = provenanceMarkers.join("; ");

  const whyVisible =
    `${visual.visual_kind} basiert auf: ${sourceSummary || "(keine direkten Quellen)"}. ` +
    `Bedeutung: ${visual.meaning}`;

  const worldGround =
    `Weltgrund: ${visual.confidence} Herkunft aus '${visual.created_from}'. ` +
    (isImportOrigin
      ? `Flarum-Vorphase. Kein aktueller Lebensraum.`
      : `Aktueller Weltlauf.`);

  return {
    visual_id: visual.visual_id,
    why_visible: whyVisible,
    source_summary: sourceSummary,
    world_ground: worldGround,
    provenance_markers: provenanceMarkers,
    activation_status: firewall.blocked ? "blocked" : "not_ready",
    is_live_state: isLiveState,
    is_import_origin: isImportOrigin,
    can_trigger_activation: false,
  };
}

export function buildAllVisualExplanations(
  visuals: VisualMeaning[],
  pack: WorldInspectionPack,
  firewall: ActivationFirewallReport
): VisualReplayExplanation[] {
  return visuals.map((v) => explainVisualMeaning(v, pack, firewall));
}
