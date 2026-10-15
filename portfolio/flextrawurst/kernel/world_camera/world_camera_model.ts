import type { WorldSnapshot } from "../snapshots/world_snapshot.ts";
import type { WorldTimeline } from "../timeline/world_timeline.ts";
import type { WorldIntegrityReport } from "../integrity/world_integrity.ts";

export interface WorldCameraNode {
  id: string;
  type: "entity_slot" | "tick" | "trace";
  label: string;
  layer: number;
  state: Record<string, unknown>;
  source_event_ids: string[];
}

export interface WorldCameraEdge {
  id: string;
  from: string;
  to: string;
  type: "causal" | "runtime_trace";
  source_event_ids: string[];
}

export interface WorldCameraLayer {
  layer: number;
  label: string;
  node_count: number;
}

export interface WorldCameraTimelineMarker {
  frame_index: number;
  event_id: string;
  label: string;
}

export interface WorldCameraModel {
  camera_version: 1;
  world_health: "ok" | "warning" | "error";
  nodes: WorldCameraNode[];
  edges: WorldCameraEdge[];
  layers: WorldCameraLayer[];
  timeline_markers: WorldCameraTimelineMarker[];
  explanations: string[];
}

export function buildWorldCameraModel(
  snapshot: WorldSnapshot,
  timeline: WorldTimeline,
  integrityReport: WorldIntegrityReport
): WorldCameraModel {
  const nodes: WorldCameraNode[] = [];
  const edges: WorldCameraEdge[] = [];
  const timeline_markers: WorldCameraTimelineMarker[] = [];

  // Layer 0: entity_slot nodes
  for (const [entityId, proj] of Object.entries(snapshot.entities)) {
    nodes.push({
      id: `node-entity-${entityId}`,
      type: "entity_slot",
      label: entityId,
      layer: 0,
      state: { ...proj.current_state },
      source_event_ids: proj.last_event_id ? [proj.last_event_id] : [],
    });
  }

  // Layer 1: tick nodes + timeline markers
  for (const frame of timeline.frames) {
    if (frame.event_type !== "system.tick") continue;
    nodes.push({
      id: `node-tick-${frame.event_id}`,
      type: "tick",
      label: frame.summary,
      layer: 1,
      state: {},
      source_event_ids: [frame.event_id],
    });
    timeline_markers.push({
      frame_index: frame.index,
      event_id: frame.event_id,
      label: frame.summary,
    });
  }

  // Layer 2: trace nodes + edges
  for (const frame of timeline.frames) {
    if (frame.event_type !== "entity.state_changed") continue;

    const traceNodeId = `node-trace-${frame.event_id}`;
    nodes.push({
      id: traceNodeId,
      type: "trace",
      label: frame.summary,
      layer: 2,
      state: {},
      source_event_ids: [frame.event_id],
    });

    // causal edge: tick → trace
    for (const causalLink of frame.causal_links) {
      const tickNodeId = `node-tick-${causalLink}`;
      edges.push({
        id: `edge-causal-${frame.event_id}`,
        from: tickNodeId,
        to: traceNodeId,
        type: "causal",
        source_event_ids: [frame.event_id, causalLink],
      });
    }

    // runtime_trace edge: trace → entity_slot
    if (frame.target_id) {
      const entityNodeId = `node-entity-${frame.target_id}`;
      edges.push({
        id: `edge-trace-${frame.event_id}`,
        from: traceNodeId,
        to: entityNodeId,
        type: "runtime_trace",
        source_event_ids: [frame.event_id],
      });
    }
  }

  // Build layer summary (layer 3 = audit/system, always present)
  const layerNodeCounts: Record<number, number> = { 0: 0, 1: 0, 2: 0, 3: 0 };
  for (const node of nodes) {
    layerNodeCounts[node.layer] = (layerNodeCounts[node.layer] ?? 0) + 1;
  }

  const layers: WorldCameraLayer[] = [
    { layer: 0, label: "Entitätsslots", node_count: layerNodeCounts[0] },
    { layer: 1, label: "Weltpulse", node_count: layerNodeCounts[1] },
    { layer: 2, label: "Präsenzspuren", node_count: layerNodeCounts[2] },
    { layer: 3, label: "Audit/System", node_count: layerNodeCounts[3] ?? 0 },
  ];

  // world_health
  let world_health: "ok" | "warning" | "error" = "ok";
  if (integrityReport.errors.length > 0) {
    world_health = "error";
  } else if (integrityReport.warnings.length > 0) {
    world_health = "warning";
  }

  const explanations: string[] = [
    ...integrityReport.errors,
    ...integrityReport.warnings,
  ];

  return {
    camera_version: 1,
    world_health,
    nodes,
    edges,
    layers,
    timeline_markers,
    explanations,
  };
}
