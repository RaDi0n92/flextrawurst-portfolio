import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";

export interface WorldStateExport {
  export_version: 1;
  created_from: "in_memory_runtime";
  scenario_id: string;
  summary: string;
  counts: {
    events: number;
    entity_slots: number;
    ticks: number;
    traces: number;
  };
  integrity: {
    ok: boolean;
    error_count: number;
    warning_count: number;
  };
  timeline: {
    first_event_id: string | null;
    last_event_id: string | null;
    tick_count: number;
  };
  camera_model: {
    node_count: number;
    edge_count: number;
    layer_count: number;
  };
  replay_frame_count: number;
}

export function buildWorldStateExport(pack: WorldInspectionPack): WorldStateExport {
  const { audit } = pack;

  return {
    export_version: 1,
    created_from: "in_memory_runtime",
    scenario_id: pack.scenario_id,
    summary: `${pack.entity_slot_count} Entitätsslots, ${pack.tick_count} Ticks, ${pack.trace_count} Spuren, ${pack.event_count} Events`,
    counts: {
      events: pack.event_count,
      entity_slots: pack.entity_slot_count,
      ticks: pack.tick_count,
      traces: pack.trace_count,
    },
    integrity: {
      ok: audit.integrity.ok,
      error_count: audit.integrity.errors.length,
      warning_count: audit.integrity.warnings.length,
    },
    timeline: {
      first_event_id: audit.timeline.first_event_id,
      last_event_id: audit.timeline.last_event_id,
      tick_count: audit.timeline.tick_count,
    },
    camera_model: {
      node_count: audit.camera_model.nodes.length,
      edge_count: audit.camera_model.edges.length,
      layer_count: audit.camera_model.layers.length,
    },
    replay_frame_count: pack.replay_frames.length,
  };
}

export function serializeWorldStateExport(pack: WorldInspectionPack): string {
  return JSON.stringify(buildWorldStateExport(pack));
}
