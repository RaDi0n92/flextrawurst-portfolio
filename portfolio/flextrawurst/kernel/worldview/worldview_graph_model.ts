export type WorldviewNodeKind =
  | "entity_slot_node"
  | "room_node"
  | "event_node"
  | "import_origin_node"
  | "visual_meaning_node"
  | "replay_trace_node";

export type WorldviewEdgeKind =
  | "slot_has_origin"
  | "event_affects_slot"
  | "visual_explains_event"
  | "room_contains_slot"
  | "replay_references_event"
  | "origin_candidate_maps_to_slot";

export type WorldviewConfidence = "structural" | "inferred" | "weak";

export interface WorldviewGraphNode {
  node_id: string;
  node_kind: WorldviewNodeKind;
  label: string;
  source_ids: string[];
  origin_layer: string;
  is_live_flextrawurst_state: boolean;
  requires_start_decision: boolean;
  explanation: string;
}

export interface WorldviewGraphEdge {
  edge_id: string;
  edge_kind: WorldviewEdgeKind;
  from_node_id: string;
  to_node_id: string;
  source_ids: string[];
  confidence: WorldviewConfidence;
  explanation: string;
}

export interface WorldviewGraph {
  graph_id: string;
  nodes: WorldviewGraphNode[];
  edges: WorldviewGraphEdge[];
  is_read_only: true;
  uses_renderer: false;
  uses_ui: false;
  created_at: string;
}
