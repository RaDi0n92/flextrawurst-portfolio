import type { ProcessSnapshot } from "../process_model/process_snapshot.ts";
import type { ProcessBody } from "../process_model/process_types.ts";
import type {
  ProcessCameraModel,
  ProcessCameraNode,
  ProcessCameraLayer,
  ProcessCameraSection,
  ProcessCameraLegend,
  ProcessCameraStatusSummary,
  ProcessCameraLayerKind,
  ProcessCameraStatusKind,
  ProcessCameraEdge,
} from "./process_camera_model.ts";

function toStatusKind(evidence: string): ProcessCameraStatusKind {
  if (evidence === "derived_from_file" || evidence === "derived_from_forum" || evidence === "derived_from_event") {
    return "derived";
  }
  if (evidence === "measured") return "measured";
  if (evidence === "modelled") return "modelled";
  if (evidence === "unknown") return "unknown";
  if (evidence === "blocked") return "blocked";
  if (evidence === "read_only") return "read_only";
  if (evidence === "replay") return "replay";
  return "unknown";
}

function toLayerKind(body: ProcessBody): ProcessCameraLayerKind {
  if (body.kind === "perception_layer") return "perception_layer";
  if (body.kind === "dialogue_core") return "dialogue_core";
  if (body.kind === "entity_slot") return "flarum_origin_slots";
  if (body.kind === "placeholder") return "placeholders";
  if (body.kind === "system_layer") {
    if (body.role === "system_knowledge") return "system_layers";
    return "infrastructure_processes";
  }
  return "placeholders";
}

function buildEdgesForBody(body: ProcessBody): readonly ProcessCameraEdge[] {
  return body.traces.map((t, i) => ({
    edge_id: `edge_${body.id}_${t.trace_type}_${i}`,
    from_node_id: body.id,
    trace_type: t.trace_type,
    ref_id: t.ref_id,
    summary: t.summary,
  }));
}

function buildNode(body: ProcessBody): ProcessCameraNode {
  return {
    node_id: body.id,
    name: body.name,
    layer: toLayerKind(body),
    role: body.role,
    status_kind: toStatusKind(body.visibility.evidence),
    activity_mode: body.activity.mode,
    evidence: body.visibility.evidence,
    evidence_reason: body.visibility.reason,
    edges: buildEdgesForBody(body),
    flarum_origin: body.forum_ref,
    is_d3_slot: body.kind === "entity_slot",
    slot_state: body.slot_state,
    ring_origin: body.ring_origin,
    source_location: body.source.location,
    is_occupied: false,
    is_measured: false,
  };
}

const LAYER_DEFS: readonly {
  id: ProcessCameraLayerKind;
  label: string;
  description: string;
}[] = [
  {
    id: "perception_layer",
    label: "Wahrnehmungsschicht",
    description: "GENI als omnipräsentes Hintergrundfeld — keine Messung, kein Live-Zugriff",
  },
  {
    id: "dialogue_core",
    label: "Koordinationskern",
    description: "dak+gord-system als Dialog- und Koordinationszentrum",
  },
  {
    id: "system_layers",
    label: "Metaschicht",
    description: "Systemweiser als konzeptuelle Kontrollinstanz",
  },
  {
    id: "flarum_origin_slots",
    label: "Flarum-Herkunfts-Slots",
    description: "Sechs namelessAI-Wesen — D3-Slots, pre_einzug, Flarum-Herkunft",
  },
  {
    id: "infrastructure_processes",
    label: "Systemprozesse",
    description: "Search, Governance, WorldRun, Worldblick/Export — read-only, abgeleitet",
  },
  {
    id: "placeholders",
    label: "Platzhalter",
    description: "Reader, Writer, Runner — noch nicht gebaut",
  },
  {
    id: "guardrails",
    label: "Schutzschicht",
    description: "Konzeptuelle Schutzregeln — keine Aktivierung, kein Einzug, kein Live-Claim",
  },
];

const LEGEND: ProcessCameraLegend = {
  status_entries: [
    { kind: "derived", label: "Abgeleitet", color_hint: "#4a9eff" },
    { kind: "modelled", label: "Modelliert", color_hint: "#8888cc" },
    { kind: "read_only", label: "Read-Only", color_hint: "#55aa77" },
    { kind: "unknown", label: "Unbekannt", color_hint: "#666666" },
    { kind: "blocked", label: "Blockiert", color_hint: "#cc4444" },
    { kind: "replay", label: "Replay", color_hint: "#cc9933" },
    { kind: "measured", label: "Gemessen", color_hint: "#ff6666" },
  ],
  layer_entries: LAYER_DEFS.map((l) => ({ kind: l.id, label: l.label })),
};

export function buildProcessCameraModel(
  snapshot: ProcessSnapshot,
  created_at = "2026-05-09T00:00:00.000Z"
): ProcessCameraModel {
  const nodes: ProcessCameraNode[] = snapshot.process_bodies.map(buildNode);

  const nodesByLayer = new Map<ProcessCameraLayerKind, string[]>();
  for (const n of nodes) {
    const existing = nodesByLayer.get(n.layer) ?? [];
    existing.push(n.node_id);
    nodesByLayer.set(n.layer, existing);
  }

  const layers: ProcessCameraLayer[] = LAYER_DEFS.map((def) => ({
    layer_id: def.id,
    label: def.label,
    description: def.description,
    node_ids: nodesByLayer.get(def.id) ?? [],
  }));

  const sections: ProcessCameraSection[] = layers
    .filter((l) => l.node_ids.length > 0)
    .map((l) => ({
      section_id: l.layer_id,
      label: l.label,
      node_count: l.node_ids.length,
      node_ids: l.node_ids,
    }));

  const derived = nodes.filter((n) => n.status_kind === "derived").length;
  const modelled = nodes.filter((n) => n.status_kind === "modelled").length;
  const blocked = nodes.filter((n) => n.status_kind === "blocked").length;
  const read_only = nodes.filter((n) => n.status_kind === "read_only").length;
  const replay = nodes.filter((n) => n.status_kind === "replay").length;
  const unknown = nodes.filter((n) => n.status_kind === "unknown").length;

  const status_summary: ProcessCameraStatusSummary = {
    process_count: nodes.length,
    measured_count: 0,
    active_claim_count: 0,
    occupied_count: 0,
    derived_count: derived,
    modelled_count: modelled,
    blocked_count: blocked,
    read_only_count: read_only,
    replay_count: replay,
    unknown_count: unknown,
  };

  return {
    model_version: 1,
    is_static: true,
    is_read_only: true,
    no_runtime: true,
    no_activation: true,
    no_live_claims: true,
    no_renderer: true,
    created_at,
    snapshot_version: snapshot.snapshot_version,
    nodes,
    layers,
    sections,
    legend: LEGEND,
    status_summary,
  };
}
