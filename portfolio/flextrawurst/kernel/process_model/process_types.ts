export type ProcessKind =
  | "perception_layer"
  | "dialogue_core"
  | "entity_slot"
  | "system_layer"
  | "placeholder";

export type ProcessRole =
  | "memory_perception"
  | "dialogue_coordination"
  | "entity_slot_pre_einzug"
  | "search_layer"
  | "governance_layer"
  | "worldrun_layer"
  | "export_layer"
  | "system_knowledge"
  | "future_placeholder";

export type ProcessStateEvidence =
  | "measured"
  | "derived_from_file"
  | "derived_from_forum"
  | "derived_from_event"
  | "modelled"
  | "unknown"
  | "blocked"
  | "read_only"
  | "replay";

export type ProcessActivityKind =
  | "thinking"
  | "reading_file"
  | "reading_forum"
  | "writing_forum"
  | "writing_file"
  | "waiting"
  | "blocked"
  | "searching"
  | "governing"
  | "exporting"
  | "replaying"
  | "unknown";

export type ProcessTraceKind =
  | "audit"
  | "search"
  | "governance"
  | "worldrun"
  | "event"
  | "forum"
  | "file"
  | "origin";

export type ProcessStatus =
  | "live"
  | "read_only"
  | "modelled"
  | "future"
  | "pre_einzug"
  | "blocked"
  | "unknown";

export type SlotState =
  | "pre_einzug"
  | "einzug_vollzogen";

export interface ProcessVisibility {
  readonly evidence: ProcessStateEvidence;
  readonly reason?: string;
  readonly source_ref?: string;
}

export interface ProcessSource {
  readonly source_type: ProcessStateEvidence;
  readonly location?: string;
  readonly timestamp_available: boolean;
  readonly notes?: string;
}

export interface ProcessActivity {
  readonly mode: ProcessActivityKind;
  readonly visibility: ProcessVisibility;
  readonly description?: string;
  readonly timestamp_model?: string;
}

export interface ProcessTrace {
  readonly trace_type: ProcessTraceKind;
  readonly body_id: string;
  readonly ref_id?: string;
  readonly source_type: ProcessStateEvidence;
  readonly summary?: string;
  readonly timestamp_model?: string;
}

export interface ProcessBody {
  readonly id: string;
  readonly name: string;
  readonly kind: ProcessKind;
  readonly role: ProcessRole;
  readonly status: ProcessStatus;
  readonly slot_state?: SlotState;
  readonly visibility: ProcessVisibility;
  readonly activity: ProcessActivity;
  readonly traces: ProcessTrace[];
  readonly source: ProcessSource;
  readonly lock_state?: string;
  readonly governance_state?: string;
  readonly feature_gate?: string;
  readonly forum_ref?: string;
  readonly file_ref?: string;
  readonly event_ref?: string;
  readonly search_ref?: string;
  readonly audit_ref?: string;
  readonly is_canonical: boolean;
  readonly ring_origin?: number;
}
