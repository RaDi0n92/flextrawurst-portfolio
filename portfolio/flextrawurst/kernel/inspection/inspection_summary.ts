import type { WorldInspectionPack } from "./world_inspection_pack.ts";

export function buildInspectionSummary(pack: WorldInspectionPack): string[] {
  return [
    `Szenario ${pack.scenario_id} ausgeführt.`,
    `${pack.entity_slot_count} Entitätsslots, ${pack.tick_count} Ticks, ${pack.trace_count} Spuren, ${pack.event_count} Events.`,
    `Integrity ${pack.audit_ok ? "ok" : "fehlgeschlagen"}.`,
    `ReplayFrames: ${pack.replay_frames.length}.`,
    `Weltkamera-Datenmodell vorbereitet.`,
    `Keine UI, keine AI, kein Renderer, kein Postgres beteiligt.`,
  ];
}
