export type ProcessCameraLayerKind =
  | "perception_layer"
  | "dialogue_core"
  | "system_layers"
  | "flarum_origin_slots"
  | "infrastructure_processes"
  | "placeholders"
  | "guardrails";

export type ProcessCameraStatusKind =
  | "measured"
  | "derived"
  | "modelled"
  | "unknown"
  | "blocked"
  | "read_only"
  | "replay";

export interface ProcessCameraEdge {
  readonly edge_id: string;
  readonly from_node_id: string;
  readonly trace_type: string;
  readonly ref_id?: string;
  readonly summary?: string;
}

export interface ProcessCameraNode {
  readonly node_id: string;
  readonly name: string;
  readonly layer: ProcessCameraLayerKind;
  readonly role: string;
  readonly status_kind: ProcessCameraStatusKind;
  readonly activity_mode: string;
  readonly evidence: string;
  readonly evidence_reason?: string;
  readonly edges: readonly ProcessCameraEdge[];
  readonly flarum_origin?: string;
  readonly is_d3_slot: boolean;
  readonly slot_state?: string;
  readonly ring_origin?: number;
  readonly source_location?: string;
  readonly is_occupied: false;
  readonly is_measured: false;
}

export interface ProcessCameraLayer {
  readonly layer_id: ProcessCameraLayerKind;
  readonly label: string;
  readonly description: string;
  readonly node_ids: readonly string[];
}

export interface ProcessCameraSection {
  readonly section_id: string;
  readonly label: string;
  readonly node_count: number;
  readonly node_ids: readonly string[];
}

export interface ProcessCameraLegend {
  readonly status_entries: readonly {
    readonly kind: ProcessCameraStatusKind;
    readonly label: string;
    readonly color_hint: string;
  }[];
  readonly layer_entries: readonly {
    readonly kind: ProcessCameraLayerKind;
    readonly label: string;
  }[];
}

export interface ProcessCameraStatusSummary {
  readonly process_count: number;
  readonly measured_count: 0;
  readonly active_claim_count: 0;
  readonly occupied_count: 0;
  readonly derived_count: number;
  readonly modelled_count: number;
  readonly blocked_count: number;
  readonly read_only_count: number;
  readonly replay_count: number;
  readonly unknown_count: number;
}

export interface ProcessCameraModel {
  readonly model_version: 1;
  readonly is_static: true;
  readonly is_read_only: true;
  readonly no_runtime: true;
  readonly no_activation: true;
  readonly no_live_claims: true;
  readonly no_renderer: true;
  readonly created_at: string;
  readonly snapshot_version: number;
  readonly nodes: readonly ProcessCameraNode[];
  readonly layers: readonly ProcessCameraLayer[];
  readonly sections: readonly ProcessCameraSection[];
  readonly legend: ProcessCameraLegend;
  readonly status_summary: ProcessCameraStatusSummary;
}
