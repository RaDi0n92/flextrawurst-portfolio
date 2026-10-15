import type { ProcessCameraModel, ProcessCameraNode } from "./process_camera_model.ts";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function statusColor(kind: string): string {
  const map: Record<string, string> = {
    derived: "#4a9eff",
    modelled: "#8888cc",
    read_only: "#55aa77",
    unknown: "#555566",
    blocked: "#cc4444",
    replay: "#cc9933",
    measured: "#ff4444",
  };
  return map[kind] ?? "#555566";
}

function statusLabel(kind: string): string {
  const map: Record<string, string> = {
    derived: "abgeleitet",
    modelled: "modelliert",
    read_only: "read-only",
    unknown: "unbekannt",
    blocked: "blockiert",
    replay: "replay",
    measured: "GEMESSEN",
  };
  return map[kind] ?? kind;
}

function renderNodeCard(node: ProcessCameraNode, compact = false): string {
  const color = statusColor(node.status_kind);
  const d3Badge = node.is_d3_slot
    ? `<span class="badge badge-d3">[D3]</span> `
    : "";
  const slotBadge = node.slot_state
    ? `<span class="badge badge-slot">${esc(node.slot_state)}</span> `
    : "";
  const statusBadge = `<span class="badge" style="color:${color};border-color:${color}40">${statusLabel(node.status_kind)}</span>`;
  const readOnlyBadge = node.status_kind === "read_only"
    ? `<span class="badge badge-ro">read-only</span>`
    : "";
  const traceCount = node.edges.length;
  const flarum = node.flarum_origin
    ? `<div class="node-detail">Herkunft: <span class="muted">${esc(node.flarum_origin)}</span></div>`
    : "";
  const loc = node.source_location
    ? `<div class="node-detail">Quelle: <span class="muted">${esc(node.source_location)}</span></div>`
    : "";
  const ring = node.ring_origin !== undefined
    ? `<div class="node-detail">Ring: <span class="muted">${node.ring_origin}</span></div>`
    : "";
  const traceHtml = traceCount > 0
    ? `<div class="node-detail">Spuren: <span class="muted">${traceCount} (${node.edges.map((e) => esc(e.trace_type)).join(", ")})</span></div>`
    : "";
  const occupiedNote = `<div class="node-detail muted-warn">nicht besetzt — kein Live-Zustand</div>`;

  if (compact) {
    return `<div class="node-card node-compact">
  <div class="node-name">${d3Badge}${slotBadge}${esc(node.name)}</div>
  <div class="node-badges">${statusBadge}${readOnlyBadge}</div>
  ${flarum}
  ${occupiedNote}
</div>`;
  }

  return `<div class="node-card">
  <div class="node-name">${d3Badge}${slotBadge}${esc(node.name)}</div>
  <div class="node-badges">${statusBadge}${readOnlyBadge}</div>
  <div class="node-detail">Rolle: <span class="muted">${esc(node.role)}</span></div>
  <div class="node-detail">Aktivität: <span class="muted">${esc(node.activity_mode)}</span></div>
  ${loc}
  ${flarum}
  ${ring}
  ${traceHtml}
  ${node.evidence_reason ? `<div class="node-detail muted-warn">${esc(node.evidence_reason)}</div>` : ""}
  ${occupiedNote}
</div>`;
}

function renderGeniBackground(model: ProcessCameraModel): string {
  const geniNode = model.nodes.find((n) => n.node_id === "geni");
  if (!geniNode) return "";
  return `<section class="geni-field">
  <div class="geni-label">GENI — Wahrnehmungsschicht</div>
  <div class="geni-desc">Omnipräsentes Wahrnehmungshintergrundfeld. Kein Einzelknoten. Kein Live-Zugriff.<br>
  Modus: <span class="muted">${esc(geniNode.activity_mode)}</span> &nbsp;|&nbsp;
  Evidenz: <span class="muted">${statusLabel(geniNode.status_kind)}</span> &nbsp;|&nbsp;
  Quelle: <span class="muted">${esc(geniNode.source_location ?? "extern — port 8020")}</span>
  </div>
  <div class="geni-reason muted-warn">${esc(geniNode.evidence_reason ?? "Keine Live-API-Brücke zu GENI")}</div>
  <div class="geni-notmeasured">measured: 0 &nbsp;|&nbsp; active_claim: 0 &nbsp;|&nbsp; nicht besetzt</div>
</section>`;
}

function renderLegend(model: ProcessCameraModel): string {
  const statusItems = model.legend.status_entries
    .map(
      (e) =>
        `<span class="legend-item"><span class="legend-dot" style="background:${esc(e.color_hint)}"></span>${esc(e.label)}</span>`
    )
    .join("");
  const layerItems = model.legend.layer_entries
    .map((e) => `<span class="legend-item">${esc(e.kind)}: ${esc(e.label)}</span>`)
    .join("");
  return `<section class="legend-section">
  <h2>Legende</h2>
  <div class="legend-group"><strong>Status:</strong> ${statusItems}</div>
  <div class="legend-group"><strong>Layer:</strong> ${layerItems}</div>
  <div class="legend-warning">
    Kein Zustand ist live gemessen. measured_count = ${model.status_summary.measured_count}.
    active_claim_count = ${model.status_summary.active_claim_count}.
    Kein Prozesskörper ist besetzt. Atmosphäre entsteht aus Rollen, Herkunft und Spuren — nicht aus erfundener Innenwelt.
  </div>
</section>`;
}

function renderStatusBar(model: ProcessCameraModel): string {
  const s = model.status_summary;
  return `<div class="status-bar">
  <span class="tag">static</span>
  <span class="tag">read-only</span>
  <span class="tag">no-runtime</span>
  <span class="tag">no-activation</span>
  <span class="tag">no-live-claims</span>
  <span class="tag">kein Renderer</span>
  <span class="tag">kein Canvas</span>
  <span class="tag">kein Server</span>
  <span class="tag tag-count">Prozesskörper: ${s.process_count}</span>
  <span class="tag tag-count">measured: ${s.measured_count}</span>
  <span class="tag tag-count">active_claims: ${s.active_claim_count}</span>
  <span class="tag tag-count">besetzt: ${s.occupied_count}</span>
</div>`;
}

function nodesForLayer(
  model: ProcessCameraModel,
  layerId: string
): ProcessCameraNode[] {
  return model.nodes.filter((n) => n.layer === layerId);
}

export function buildProcessCameraHtml(model: ProcessCameraModel): string {
  const geniHtml = renderGeniBackground(model);
  const statusBarHtml = renderStatusBar(model);

  const dakGordNode = model.nodes.find((n) => n.node_id === "dak_gord_system");
  const dakGordHtml = dakGordNode
    ? `<section class="layer-section dialogue-core-section">
  <h2 class="layer-title">Koordinationskern</h2>
  ${renderNodeCard(dakGordNode)}
</section>`
    : "";

  const systemwiserNode = model.nodes.find((n) => n.node_id === "systemweiser");
  const systemweiserHtml = systemwiserNode
    ? `<section class="layer-section meta-section">
  <h2 class="layer-title">Metaschicht</h2>
  ${renderNodeCard(systemwiserNode)}
</section>`
    : "";

  const slotNodes = nodesForLayer(model, "flarum_origin_slots");
  const slotsHtml = `<section class="layer-section slots-section">
  <h2 class="layer-title">Flarum-Herkunfts-Slots <span class="layer-note">6 × namelessAI — D3 — pre_einzug — kein Einzug vollzogen</span></h2>
  <div class="nodes-grid">${slotNodes.map((n) => renderNodeCard(n, true)).join("")}</div>
</section>`;

  const infraNodes = nodesForLayer(model, "infrastructure_processes");
  const infraHtml = `<section class="layer-section infra-section">
  <h2 class="layer-title">Systemprozesse</h2>
  <div class="nodes-grid">${infraNodes.map((n) => renderNodeCard(n)).join("")}</div>
</section>`;

  const placeholderNodes = nodesForLayer(model, "placeholders");
  const placeholderHtml = `<section class="layer-section placeholder-section">
  <h2 class="layer-title">Platzhalter <span class="layer-note">noch nicht gebaut</span></h2>
  <div class="nodes-grid">${placeholderNodes.map((n) => renderNodeCard(n, true)).join("")}</div>
</section>`;

  const legendHtml = renderLegend(model);

  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Flextrawurst &#8212; Prozesskamera Weltblick</title>
<meta name="generator" content="flextrawurst-process-camera-ring-22d-h">
<meta name="robots" content="noindex,nofollow">
<style>
*, *::before, *::after { box-sizing: border-box; }
body {
  font-family: monospace;
  background: #070b0f;
  color: #c8ccd4;
  margin: 0;
  padding: 2rem;
  line-height: 1.6;
  min-height: 100vh;
}
h1 {
  color: #e0e4ec;
  font-size: 1.3rem;
  border-bottom: 1px solid #1a2030;
  padding-bottom: 0.6rem;
  margin: 0 0 1rem 0;
  letter-spacing: 0.04em;
}
h2 {
  color: #8892a4;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0 0 0.75rem 0;
}
.layer-note {
  font-size: 0.72rem;
  color: #555;
  text-transform: none;
  letter-spacing: 0;
  font-weight: normal;
}
.status-bar {
  background: #0d1117;
  border: 1px solid #1a2030;
  border-radius: 4px;
  padding: 0.6rem 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.5rem;
}
.tag {
  background: #0f1825;
  color: #6688aa;
  border: 1px solid #1e3050;
  border-radius: 3px;
  padding: 0.1rem 0.45rem;
  font-size: 0.75rem;
}
.tag-count {
  color: #88aabb;
  border-color: #1e3050;
}
.geni-field {
  background: linear-gradient(135deg, #070f1a 0%, #0a1428 50%, #081020 100%);
  border: 1px solid #1a3050;
  border-radius: 8px;
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.geni-field::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 20% 40%, #0a2040 0%, transparent 60%),
              radial-gradient(ellipse at 80% 60%, #0a1830 0%, transparent 60%);
  pointer-events: none;
}
.geni-label {
  font-size: 1.05rem;
  color: #6ab0dd;
  font-weight: bold;
  margin-bottom: 0.5rem;
  position: relative;
}
.geni-desc {
  color: #7a9ab8;
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
  position: relative;
}
.geni-reason {
  font-size: 0.78rem;
  position: relative;
}
.geni-notmeasured {
  font-size: 0.72rem;
  color: #3a5065;
  margin-top: 0.6rem;
  position: relative;
}
.layer-section {
  background: #0a0e14;
  border: 1px solid #151e2a;
  border-radius: 6px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}
.dialogue-core-section {
  border-color: #1e3040;
  background: #080d14;
}
.meta-section {
  border-color: #1a1a2e;
}
.slots-section {
  border-color: #1e2a18;
}
.infra-section {
  border-color: #1a2218;
}
.placeholder-section {
  opacity: 0.55;
  border-color: #141414;
}
.nodes-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.node-card {
  background: #0d1218;
  border: 1px solid #1a2030;
  border-radius: 5px;
  padding: 0.75rem 1rem;
  min-width: 200px;
  max-width: 320px;
  flex: 1 1 200px;
}
.node-compact {
  min-width: 160px;
  max-width: 240px;
  padding: 0.5rem 0.75rem;
}
.node-name {
  font-size: 0.9rem;
  color: #d0d8e4;
  font-weight: bold;
  margin-bottom: 0.35rem;
}
.node-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.4rem;
}
.badge {
  display: inline-block;
  border: 1px solid #333;
  border-radius: 2px;
  padding: 0.05rem 0.35rem;
  font-size: 0.72rem;
  color: #888;
}
.badge-d3 {
  color: #77aaff;
  border-color: #2244aa40;
  background: #0a1030;
}
.badge-slot {
  color: #aaa;
  border-color: #2a2a2a;
}
.badge-ro {
  color: #55aa77;
  border-color: #1a4a2a40;
}
.node-detail {
  font-size: 0.75rem;
  color: #606878;
  margin-top: 0.15rem;
}
.muted { color: #4a5568; }
.muted-warn { color: #3a4555; font-style: italic; }
.layer-title { color: #6a7888; }
.legend-section {
  background: #0a0e14;
  border: 1px solid #141e28;
  border-radius: 6px;
  padding: 1.25rem 1.5rem;
  margin-top: 1.5rem;
}
.legend-group {
  font-size: 0.78rem;
  color: #5a6a7a;
  margin-bottom: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.legend-warning {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #0c0f13;
  border: 1px solid #1a2028;
  border-left: 3px solid #2a4a5a;
  border-radius: 3px;
  font-size: 0.78rem;
  color: #4a5a6a;
  line-height: 1.6;
}
</style>
</head>
<body>
<h1>Flextrawurst &#8212; Prozesskamera Weltblick</h1>
<p style="color:#3a5060;font-size:0.78rem;margin-top:-0.5rem;margin-bottom:1.25rem">
  Ring 22D&#8211;H &#8212; Statischer read-only Prozessblick &#8212; ${esc(model.created_at)}
  &#8212; Kein Live-Dashboard. Kein Renderer. Kein Fetch. Kein Server.
</p>

${statusBarHtml}

${geniHtml}

${dakGordHtml}

${systemweiserHtml}

${slotsHtml}

${infraHtml}

${placeholderHtml}

${legendHtml}

</body>
</html>`;
}
