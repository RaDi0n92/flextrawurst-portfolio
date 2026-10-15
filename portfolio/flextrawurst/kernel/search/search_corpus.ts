import type { SearchDocument, SearchDocumentKind } from "./search_document.ts";
import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldTimeline, WorldTimelineFrame } from "../timeline/world_timeline.ts";
import type { ProvenanceRecord } from "../provenance/provenance_record.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";
import type { FeatureFlag } from "../features/feature_flag.ts";
import type { ConceptGuardReport } from "../concept_guard/concept_guard.ts";
import type { WorldCameraModel } from "../world_camera/world_camera_model.ts";
import type { CommandLedger } from "../admin/command_ledger.ts";
import type { WorldRunState } from "../worldrun/worldrun_state.ts";
import type { WorldRunAudit } from "../worldrun/worldrun_audit.ts";
import type { WorldRunControlSnapshot } from "../worldrun/worldrun_control_snapshot.ts";
import type { GovernanceMatrix } from "../governance/governance_matrix.ts";
import type { GovernanceGateReport } from "../governance/governance_gate.ts";
import type { GovernanceAudit } from "../governance/governance_audit.ts";
import type { GovernanceSnapshot } from "../governance/governance_snapshot.ts";
import type { GlobalLockState } from "../governance/global_lock.ts";

export interface SearchCorpus {
  corpus_version: 1;
  documents: SearchDocument[];
  counts: Record<string, number>;
}

function buildCounts(documents: SearchDocument[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const doc of documents) {
    counts[doc.kind] = (counts[doc.kind] ?? 0) + 1;
  }
  return counts;
}

export function buildSearchCorpusFromEvents(
  events: readonly FlextrawurstEvent[]
): SearchCorpus {
  const documents: SearchDocument[] = events.map((e) => ({
    document_id: `search_event_${e.event_id}`,
    kind: "event" as SearchDocumentKind,
    title: `Event: ${e.event_type} by ${e.actor_id}`,
    body: `event_type=${e.event_type} actor=${e.actor_type}:${e.actor_id} target=${e.target_type}:${e.target_id ?? "null"} origin=${e.origin_type}`,
    tags: [e.event_type, e.actor_type, e.origin_type, e.visibility_layer],
    source_ids: [e.event_id, ...e.causal_links],
    layer: e.visibility_layer,
    provenance_type: null,
    event_type: e.event_type,
    actor_type: e.actor_type,
    actor_id: e.actor_id,
    target_type: e.target_type,
    target_id: e.target_id,
    slot_id: e.target_type === "nameless_ai" ? e.target_id : null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: e.timestamp,
    raw: e,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromTimeline(
  timeline: WorldTimeline
): SearchCorpus {
  const documents: SearchDocument[] = timeline.frames.map(
    (frame: WorldTimelineFrame) => ({
      document_id: `search_timeline_${frame.index}_${frame.event_id}`,
      kind: "timeline_frame" as SearchDocumentKind,
      title: `Timeline[${frame.index}]: ${frame.event_type}`,
      body: `index=${frame.index} event_type=${frame.event_type} actor=${frame.actor_type}:${frame.actor_id} target=${frame.target_type}:${frame.target_id ?? "null"} summary=${frame.summary}`,
      tags: [frame.event_type, frame.actor_type, "timeline"],
      source_ids: [frame.event_id, ...frame.causal_links],
      layer: "timeline",
      provenance_type: null,
      event_type: frame.event_type,
      actor_type: frame.actor_type,
      actor_id: frame.actor_id,
      target_type: frame.target_type,
      target_id: frame.target_id,
      slot_id:
        frame.target_type === "nameless_ai" ? frame.target_id : null,
      feature_id: null,
      policy_id: null,
      command_id: null,
      timeline_index: frame.index,
      created_at: frame.timestamp,
      raw: frame,
    })
  );
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromProvenance(
  records: ProvenanceRecord[]
): SearchCorpus {
  const documents: SearchDocument[] = records.map((r) => ({
    document_id: `search_prov_${r.record_id}`,
    kind: "provenance_record" as SearchDocumentKind,
    title: `Provenance: ${r.provenance_type} for ${r.subject_id}`,
    body: `subject=${r.subject_type}:${r.subject_id} type=${r.provenance_type} origin=${r.origin_label} confidence=${r.confidence} notes=${r.notes.join(" ")}`,
    tags: [r.provenance_type, r.subject_type, r.confidence, "provenance"],
    source_ids: [...r.source_event_ids],
    layer: "provenance",
    provenance_type: r.provenance_type,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: r.subject_type,
    target_id: r.subject_id,
    slot_id:
      r.subject_type === "entity_slot" ? r.subject_id : null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: r,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromSlots(
  slots: EntitySlot[]
): SearchCorpus {
  const documents: SearchDocument[] = slots.map((s) => ({
    document_id: `search_slot_${s.slot_id}`,
    kind: "slot" as SearchDocumentKind,
    title: `Slot: ${s.slot_id} (${s.status})`,
    body: `slot_id=${s.slot_id} status=${s.status} source=${s.source} canonical=${s.canonical} occupant=${s.occupant_id ?? "null"}`,
    tags: [s.status, s.source, "slot", s.canonical ? "canonical" : "non-canonical"],
    source_ids: [],
    layer: "slots",
    provenance_type: s.source === "canonical_seed" ? "canonical_seed" : null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: "nameless_ai",
    target_id: s.slot_id,
    slot_id: s.slot_id,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: s,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromFeatures(
  features: FeatureFlag[]
): SearchCorpus {
  const documents: SearchDocument[] = features.map((f) => ({
    document_id: `search_feature_${f.feature_id}`,
    kind: "feature_flag" as SearchDocumentKind,
    title: `Feature: ${f.label} (${f.status})`,
    body: `feature_id=${f.feature_id} kind=${f.kind} status=${f.status} enabled=${f.enabled} can_enable_now=${f.can_enable_now} blockers=${f.blockers.join(" ")}`,
    tags: [f.kind, f.status, f.enabled ? "enabled" : "disabled", "feature"],
    source_ids: f.source_blueprint_id ? [f.source_blueprint_id] : [],
    layer: "features",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: f.feature_id,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: f,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromConceptGuard(
  report: ConceptGuardReport
): SearchCorpus {
  const documents: SearchDocument[] = report.violations.map((v) => ({
    document_id: `search_guard_${v.id}_${v.term.replace(/\s+/g, "_")}`,
    kind: "concept_guard_violation" as SearchDocumentKind,
    title: `ConceptGuard: ${v.term}`,
    body: `term=${v.term} message=${v.message} id=${v.id}`,
    tags: ["concept_guard", "violation", v.term],
    source_ids: [v.id],
    layer: "concept_guard",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: v,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromCameraModel(
  cameraModel: WorldCameraModel
): SearchCorpus {
  const nodeDocs: SearchDocument[] = cameraModel.nodes.map((n) => ({
    document_id: `search_camera_node_${n.id}`,
    kind: "camera_node" as SearchDocumentKind,
    title: `CameraNode: ${n.label} (${n.type})`,
    body: `id=${n.id} type=${n.type} label=${n.label} layer=${n.layer}`,
    tags: [n.type, "camera", "node"],
    source_ids: [...n.source_event_ids],
    layer: `camera_layer_${n.layer}`,
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: n.id,
    slot_id: n.type === "entity_slot" ? n.id : null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: n,
  }));
  const edgeDocs: SearchDocument[] = cameraModel.edges.map((e) => ({
    document_id: `search_camera_edge_${e.id}`,
    kind: "camera_edge" as SearchDocumentKind,
    title: `CameraEdge: ${e.from} → ${e.to} (${e.type})`,
    body: `id=${e.id} from=${e.from} to=${e.to} type=${e.type}`,
    tags: [e.type, "camera", "edge"],
    source_ids: [...e.source_event_ids],
    layer: "camera_edges",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: e,
  }));
  const documents = [...nodeDocs, ...edgeDocs];
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromCommandLedger(
  ledger: CommandLedger
): SearchCorpus {
  const documents: SearchDocument[] = ledger.entries.map((entry) => ({
    document_id: `search_ledger_${entry.ledger_id}`,
    kind: "command_ledger_entry" as SearchDocumentKind,
    title: `Command: ${entry.command.command_type} (${entry.status})`,
    body: `command_id=${entry.command.command_id} type=${entry.command.command_type} target=${entry.command.target_type}:${entry.command.target_id} status=${entry.status} role=${entry.actor_role} reason=${entry.command.reason}`,
    tags: [entry.command.command_type, entry.status, entry.actor_role, "command"],
    source_ids: [entry.command.command_id],
    layer: "admin",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: entry.command.requested_by,
    target_type: entry.command.target_type,
    target_id: entry.command.target_id,
    slot_id: null,
    feature_id:
      entry.command.target_type === "feature" || entry.command.target_type === "organ"
        ? entry.command.target_id
        : null,
    policy_id: null,
    command_id: entry.command.command_id,
    timeline_index: null,
    created_at: entry.command.created_at,
    raw: entry,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromWorldRunState(
  state: WorldRunState
): SearchCorpus {
  const doc: SearchDocument = {
    document_id: `search_worldrun_state_${state.run_id}`,
    kind: "worldrun_state" as SearchDocumentKind,
    title: `WorldRunState: ${state.run_id} (${state.status})`,
    body: `run_id=${state.run_id} status=${state.status} tick=${state.current_tick} locked=${state.locked} lock_reason=${state.lock_reason ?? "null"} paused_reason=${state.paused_reason ?? "null"} frozen_reason=${state.frozen_reason ?? "null"} stopped_reason=${state.stopped_reason ?? "null"}`,
    tags: ["worldrun", "control", state.status, state.locked ? "lock" : "unlocked", "pause", "freeze", "stop", "lock"],
    source_ids: [state.run_id],
    layer: "worldrun_control",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: state.updated_at,
    raw: state,
  };
  return { corpus_version: 1, documents: [doc], counts: buildCounts([doc]) };
}

export function buildSearchCorpusFromWorldRunAudit(
  audit: WorldRunAudit
): SearchCorpus {
  const documents: SearchDocument[] = audit.entries.map((entry) => ({
    document_id: `search_worldrun_audit_${entry.audit_id}`,
    kind: "worldrun_audit_entry" as SearchDocumentKind,
    title: `WorldRunAudit: ${entry.transition_type} (${entry.accepted ? "accepted" : "rejected"})`,
    body: `audit_id=${entry.audit_id} command_id=${entry.command_id} transition=${entry.transition_type} accepted=${entry.accepted} prev=${entry.previous_status} next=${entry.next_status ?? "null"} dry_run=${entry.dry_run} notes=${entry.notes.join(" ")}`,
    tags: ["worldrun", "control", "audit", entry.transition_type, entry.accepted ? "accepted" : "rejected"],
    source_ids: [entry.audit_id, entry.command_id],
    layer: "worldrun_control",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: entry.command_id,
    timeline_index: null,
    created_at: null,
    raw: entry,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromWorldRunControlSnapshot(
  snapshot: WorldRunControlSnapshot
): SearchCorpus {
  const state = snapshot.run_state;
  const doc: SearchDocument = {
    document_id: `search_worldrun_snapshot_${state.run_id}`,
    kind: "worldrun_control_snapshot" as SearchDocumentKind,
    title: `WorldRunControlSnapshot: ${state.run_id} (${state.status})`,
    body: `run_id=${state.run_id} status=${state.status} can_pause=${snapshot.can_pause} can_resume=${snapshot.can_resume} can_freeze=${snapshot.can_freeze} can_stop=${snapshot.can_stop} can_lock=${snapshot.can_lock} available=${snapshot.available_transitions.join(",")} blocked=${snapshot.blocked_transitions.join(",")}`,
    tags: ["worldrun", "control", "snapshot", state.status, "pause", "freeze", "stop", "lock"],
    source_ids: [state.run_id],
    layer: "worldrun_control",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: state.updated_at,
    raw: snapshot,
  };
  return { corpus_version: 1, documents: [doc], counts: buildCounts([doc]) };
}

export function buildSearchCorpusFromGovernanceMatrix(
  matrix: GovernanceMatrix
): SearchCorpus {
  const documents: SearchDocument[] = matrix.rows.map((row) => ({
    document_id: `search_gov_action_${row.action.action_id.replace(/\./g, "_")}`,
    kind: "governance_action" as SearchDocumentKind,
    title: `GovernanceAction: ${row.action.action_id} (${row.action.risk_level})`,
    body: `action_id=${row.action.action_id} class=${row.action.action_class} risk=${row.action.risk_level} permission=${row.action.required_permission} daniel_root=${row.action.requires_daniel_root} blocked_by_lock=${row.action.blocked_by_global_lock} notes=${row.action.notes.join(" ")}`,
    tags: [
      "governance",
      row.action.action_class,
      row.action.risk_level,
      row.action.blocked_by_global_lock ? "global_lock_blocked" : "lock_allowed",
      row.action.requires_daniel_root ? "daniel_required" : "operator_allowed",
      row.action.risk_level === "critical" ? "critical" : "non_critical",
    ],
    source_ids: [row.action.action_id],
    layer: "governance",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: row.action.action_id,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: row,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromGovernanceGateReport(
  report: GovernanceGateReport
): SearchCorpus {
  const doc: SearchDocument = {
    document_id: `search_gov_gate_${report.action_id}_${report.actor_id}`,
    kind: "governance_gate_report" as SearchDocumentKind,
    title: `GovernanceGate: ${report.action_id} (${report.allowed ? "allowed" : "blocked"})`,
    body: `action_id=${report.action_id} actor=${report.actor_id} role=${report.actor_role} allowed=${report.allowed} blocked=${report.blocked} missing_permissions=${report.missing_permissions.join(" ")} blockers=${report.blockers.join(" ")}`,
    tags: [
      "governance",
      "gate",
      report.allowed ? "allowed" : "blocked",
      report.actor_role,
    ],
    source_ids: [report.action_id, report.actor_id],
    layer: "governance",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: report.actor_id,
    target_type: null,
    target_id: report.action_id,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: report,
  };
  return { corpus_version: 1, documents: [doc], counts: buildCounts([doc]) };
}

export function buildSearchCorpusFromGovernanceAudit(
  audit: GovernanceAudit
): SearchCorpus {
  const documents: SearchDocument[] = audit.entries.map((entry) => ({
    document_id: `search_gov_audit_${entry.audit_id}`,
    kind: "governance_audit_entry" as SearchDocumentKind,
    title: `GovernanceAudit: ${entry.action_id} (${entry.allowed ? "allowed" : "blocked"})`,
    body: `audit_id=${entry.audit_id} action_id=${entry.action_id} actor=${entry.actor_id} role=${entry.actor_role} allowed=${entry.allowed} blocked=${entry.blocked} blockers=${entry.blockers.join(" ")} created_at=${entry.created_at}`,
    tags: [
      "governance",
      "audit",
      entry.allowed ? "allowed" : "blocked",
      entry.actor_role,
    ],
    source_ids: [
      entry.audit_id,
      ...(entry.command_id ? [entry.command_id] : []),
    ],
    layer: "governance",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: entry.actor_id,
    target_type: null,
    target_id: entry.action_id,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: entry.command_id,
    timeline_index: null,
    created_at: entry.created_at,
    raw: entry,
  }));
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromGovernanceSnapshot(
  snapshot: GovernanceSnapshot
): SearchCorpus {
  const doc: SearchDocument = {
    document_id: `search_gov_snapshot_v${snapshot.snapshot_version}`,
    kind: "governance_snapshot" as SearchDocumentKind,
    title: `GovernanceSnapshot v${snapshot.snapshot_version}`,
    body: `snapshot_version=${snapshot.snapshot_version} action_count=${snapshot.matrix.rows.length} critical=${snapshot.critical_actions.join(",")} daniel_required=${snapshot.daniel_required_actions.join(",")} locked=${snapshot.global_lock.locked} coverage_ok=${snapshot.coverage.ok}`,
    tags: [
      "governance",
      "snapshot",
      snapshot.global_lock.locked ? "global_lock" : "unlocked",
      snapshot.coverage.ok ? "coverage_ok" : "coverage_incomplete",
    ],
    source_ids: snapshot.critical_actions,
    layer: "governance",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: snapshot,
  };
  return { corpus_version: 1, documents: [doc], counts: buildCounts([doc]) };
}

export function buildSearchCorpusFromGlobalLockState(
  lock: GlobalLockState
): SearchCorpus {
  const doc: SearchDocument = {
    document_id: `search_global_lock_${lock.lock_id ?? "unlocked"}`,
    kind: "global_lock_state" as SearchDocumentKind,
    title: `GlobalLockState: ${lock.locked ? "locked" : "unlocked"}`,
    body: `lock_version=${lock.lock_version} locked=${lock.locked} lock_id=${lock.lock_id ?? "null"} locked_by=${lock.locked_by ?? "null"} reason=${lock.reason ?? "null"} created_at=${lock.created_at ?? "null"} blocks_all_non_view=${lock.blocks_all_non_view_actions}`,
    tags: [
      "governance",
      "global_lock",
      lock.locked ? "locked" : "unlocked",
    ],
    source_ids: lock.lock_id ? [lock.lock_id] : [],
    layer: "governance",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: lock.locked_by,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: lock.created_at,
    raw: lock,
  };
  return { corpus_version: 1, documents: [doc], counts: buildCounts([doc]) };
}

import type { ProcessSnapshot } from "../process_model/process_snapshot.ts";

export function buildSearchCorpusFromProcessSnapshot(
  snapshot: ProcessSnapshot
): SearchCorpus {
  const bodyDocs: SearchDocument[] = snapshot.process_bodies.map((b) => ({
    document_id: `search_process_body_${b.id}`,
    kind: "process_body" as SearchDocumentKind,
    title: `ProcessBody: ${b.name} (${b.kind})`,
    body: `id=${b.id} kind=${b.kind} role=${b.role} status=${b.status} evidence=${b.visibility.evidence} is_canonical=${b.is_canonical}`,
    tags: [b.kind, b.role, b.status, b.visibility.evidence, "process_body"],
    source_ids: b.file_ref ? [b.file_ref] : b.forum_ref ? [b.forum_ref] : [],
    layer: "process_model",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: "process_body",
    target_id: b.id,
    slot_id: b.kind === "entity_slot" ? b.id : null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: b,
  }));

  const traceDocs: SearchDocument[] = snapshot.process_bodies.flatMap((b) =>
    b.traces.map((t) => ({
      document_id: `search_process_trace_${b.id}_${t.trace_type}`,
      kind: "process_trace" as SearchDocumentKind,
      title: `ProcessTrace: ${t.trace_type} for ${b.id}`,
      body: `body_id=${t.body_id} trace_type=${t.trace_type} source_type=${t.source_type} ref_id=${t.ref_id ?? "null"} summary=${t.summary ?? ""}`,
      tags: [t.trace_type, t.source_type, "process_trace"],
      source_ids: t.ref_id ? [t.ref_id] : [],
      layer: "process_model",
      provenance_type: null,
      event_type: null,
      actor_type: null,
      actor_id: null,
      target_type: "process_body",
      target_id: t.body_id,
      slot_id: null,
      feature_id: null,
      policy_id: null,
      command_id: null,
      timeline_index: null,
      created_at: null,
      raw: t,
    }))
  );

  const snapshotDoc: SearchDocument = {
    document_id: `search_process_snapshot_v${snapshot.snapshot_version}`,
    kind: "process_snapshot" as SearchDocumentKind,
    title: `ProcessSnapshot v${snapshot.snapshot_version}`,
    body: `process_count=${snapshot.process_count} active_claim_count=${snapshot.active_claim_count} measured_count=${snapshot.measured_count} derived_count=${snapshot.derived_count} modelled_count=${snapshot.modelled_count} is_read_only=${snapshot.is_read_only}`,
    tags: ["process_snapshot", "read_only", "static"],
    source_ids: [],
    layer: "process_model",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: snapshot.created_at,
    raw: snapshot,
  };

  const documents = [...bodyDocs, ...traceDocs, snapshotDoc];
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function buildSearchCorpusFromProcessCameraModel(
  model: import("../process_camera/process_camera_model.ts").ProcessCameraModel
): SearchCorpus {
  const nodeDocs: SearchDocument[] = model.nodes.map((n) => ({
    document_id: `search_camera_node_${n.node_id}`,
    kind: "process_camera_node" as SearchDocumentKind,
    title: `CameraNode: ${n.name} (${n.layer})`,
    body: `node_id=${n.node_id} layer=${n.layer} role=${n.role} status=${n.status_kind} evidence=${n.evidence} activity=${n.activity_mode} is_d3_slot=${n.is_d3_slot}`,
    tags: [n.layer, n.role, n.status_kind, n.evidence, "process_camera_node", ...(n.is_d3_slot ? ["d3_slot"] : [])],
    source_ids: n.flarum_origin ? [n.flarum_origin] : n.source_location ? [n.source_location] : [],
    layer: "process_camera",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: "process_camera_node",
    target_id: n.node_id,
    slot_id: n.is_d3_slot ? n.node_id : null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: n,
  }));

  const layerDocs: SearchDocument[] = model.layers.map((l) => ({
    document_id: `search_camera_layer_${l.layer_id}`,
    kind: "process_camera_layer" as SearchDocumentKind,
    title: `CameraLayer: ${l.label}`,
    body: `layer_id=${l.layer_id} label=${l.label} node_count=${l.node_ids.length} nodes=${l.node_ids.join(",")}`,
    tags: [l.layer_id, "process_camera_layer"],
    source_ids: [],
    layer: "process_camera",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: "process_camera_layer",
    target_id: l.layer_id,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: null,
    raw: l,
  }));

  const modelDoc: SearchDocument = {
    document_id: `search_camera_model_v${model.model_version}`,
    kind: "process_camera_model" as SearchDocumentKind,
    title: `ProcessCameraModel v${model.model_version}`,
    body: `model_version=${model.model_version} process_count=${model.status_summary.process_count} measured_count=${model.status_summary.measured_count} active_claim_count=${model.status_summary.active_claim_count} is_static=${model.is_static} is_read_only=${model.is_read_only}`,
    tags: ["process_camera_model", "static", "read_only"],
    source_ids: [],
    layer: "process_camera",
    provenance_type: null,
    event_type: null,
    actor_type: null,
    actor_id: null,
    target_type: null,
    target_id: null,
    slot_id: null,
    feature_id: null,
    policy_id: null,
    command_id: null,
    timeline_index: null,
    created_at: model.created_at,
    raw: model,
  };

  const documents = [...nodeDocs, ...layerDocs, modelDoc];
  return { corpus_version: 1, documents, counts: buildCounts(documents) };
}

export function mergeSearchCorpora(...corpora: SearchCorpus[]): SearchCorpus {
  const allDocs: SearchDocument[] = [];
  for (const c of corpora) {
    allDocs.push(...c.documents);
  }
  return {
    corpus_version: 1,
    documents: allDocs,
    counts: buildCounts(allDocs),
  };
}
