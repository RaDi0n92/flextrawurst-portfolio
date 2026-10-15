import type { VisualMeaning, VisualKind } from "./visual_meaning_model.ts";

export function getVisualKindLabel(kind: VisualKind): string {
  const labels: Record<VisualKind, string> = {
    node_pulse: "Knotenpuls",
    edge_pressure: "Kantendruck",
    silence_shell: "Schweige-Hülle",
    memory_echo: "Gedächtnisecho",
    dream_residue_hint: "Traumrückstandshinweis",
    room_density: "Raumdichte",
    activation_block: "Aktivierungsblockade",
    origin_marker: "Herkunftsmarker",
    replay_trace: "Replay-Spur",
  };
  return labels[kind];
}

export function buildVisualExplanationText(visual: VisualMeaning): string {
  const kindLabel = getVisualKindLabel(visual.visual_kind);
  const sources: string[] = [
    ...visual.source_event_ids.map((id) => `event:${id}`),
    ...visual.source_slot_ids.map((id) => `slot:${id}`),
    ...visual.source_state_ids.map((id) => `state:${id}`),
    ...visual.source_room_ids.map((id) => `room:${id}`),
  ];

  const originInfo =
    visual.origin_layer === "flarum_vorphase"
      ? " (Flarum-Vorphase, kein aktueller Lebensraum)"
      : "";

  return (
    `${kindLabel}${originInfo}: ${visual.meaning} ` +
    `Herkunft: [${sources.join(", ")}]. ` +
    `Intensität: ${visual.intensity.toFixed(2)}. ` +
    `Konfidenz: ${visual.confidence}. ` +
    `Dekorativ: ${visual.is_decorative}.`
  );
}

export function buildVisualExplanationSummary(
  visuals: VisualMeaning[]
): string[] {
  return visuals.map((v) => buildVisualExplanationText(v));
}
