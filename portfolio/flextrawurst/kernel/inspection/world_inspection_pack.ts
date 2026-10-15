import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldAudit } from "../audit/world_audit.ts";
import type { WorldReplayFrame } from "../replay/world_replay_frames.ts";

export interface WorldInspectionPack {
  pack_version: 1;
  scenario_id: string;
  label: string;
  event_count: number;
  entity_slot_count: number;
  tick_count: number;
  trace_count: number;
  audit_ok: boolean;
  events: readonly FlextrawurstEvent[];
  audit: WorldAudit;
  replay_frames: WorldReplayFrame[];
  notes: string[];
}
