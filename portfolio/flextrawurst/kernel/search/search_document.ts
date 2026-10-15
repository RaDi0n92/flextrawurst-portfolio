export type SearchDocumentKind =
  | "event"
  | "timeline_frame"
  | "provenance_record"
  | "slot"
  | "feature_flag"
  | "concept_guard_violation"
  | "audit"
  | "camera_node"
  | "camera_edge"
  | "worldblick_output"
  | "inspection_export_section"
  | "command_ledger_entry"
  | "os_spine_summary"
  | "worldrun_state"
  | "worldrun_audit_entry"
  | "worldrun_control_snapshot"
  | "governance_action"
  | "governance_gate_report"
  | "governance_audit_entry"
  | "governance_snapshot"
  | "global_lock_state"
  | "process_body"
  | "process_trace"
  | "process_snapshot"
  | "process_camera_node"
  | "process_camera_layer"
  | "process_camera_model";

export interface SearchDocument {
  document_id: string;
  kind: SearchDocumentKind;
  title: string;
  body: string;
  tags: string[];
  source_ids: string[];
  layer: string;
  provenance_type: string | null;
  event_type: string | null;
  actor_type: string | null;
  actor_id: string | null;
  target_type: string | null;
  target_id: string | null;
  slot_id: string | null;
  feature_id: string | null;
  policy_id: string | null;
  command_id: string | null;
  timeline_index: number | null;
  created_at: string | null;
  raw: unknown;
}
