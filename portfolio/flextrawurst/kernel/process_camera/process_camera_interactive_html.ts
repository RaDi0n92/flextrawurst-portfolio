import type { ProcessCameraModel, ProcessCameraNode } from "./process_camera_model.ts";
import type { ProcessCameraLayout, NodeLayout } from "./process_camera_layout.ts";

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const STATUS_COLOR: Record<string, string> = {
  derived:  "#4a9eff",
  modelled: "#8888cc",
  read_only:"#55aa77",
  unknown:  "#50506a",
  blocked:  "#cc4444",
  replay:   "#cc9933",
  measured: "#ff4444",
};

const EDGE_STROKE: Record<string, string> = {
  perception_edge:  "#1a7090",
  coordination_edge:"#1a4a9a",
  provenance_edge:  "#3a7048",
  trace_edge:       "#706030",
  governance_edge:  "#703060",
  search_edge:      "#204870",
  export_edge:      "#206848",
};

const LAYER_LABEL: Record<string, string> = {
  perception_layer:       "Wahrnehmung (GENI)",
  dialogue_core:          "Koordination (dak+gord)",
  system_layers:          "Metaschicht",
  flarum_origin_slots:    "namelessAI-Slots",
  infrastructure_processes:"Systemprozesse",
  placeholders:           "Platzhalter",
  guardrails:             "Guardrails",
};

function nodePos(layout: ProcessCameraLayout): Map<string, NodeLayout> {
  return new Map(layout.nodes.map((n) => [n.node_id, n]));
}

function buildSvgDefs(): string {
  return `<defs>
  <filter id="glow-blue" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glow-node" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="geni-grad" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="#0a2040" stop-opacity="0.7"/>
    <stop offset="60%"  stop-color="#061428" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="#030a14" stop-opacity="0.0"/>
  </radialGradient>
  <radialGradient id="geni-ring" cx="50%" cy="50%" r="50%">
    <stop offset="80%"  stop-color="#1a6090" stop-opacity="0.0"/>
    <stop offset="100%" stop-color="#1a6090" stop-opacity="0.25"/>
  </radialGradient>
</defs>`;
}

function buildGeniField(layout: ProcessCameraLayout): string {
  const nl = layout.nodes.find((n) => n.node_id === "geni");
  if (!nl || !nl.field_rx || !nl.field_ry) return "";
  const rx = nl.field_rx, ry = nl.field_ry;
  return `<g class="geni-field-group" data-layer="perception_layer">
  <ellipse cx="${nl.x}" cy="${nl.y}" rx="${rx}" ry="${ry}" fill="url(#geni-grad)" stroke="#1a6090" stroke-width="1" stroke-opacity="0.4" filter="url(#glow-blue)"/>
  <ellipse cx="${nl.x}" cy="${nl.y}" rx="${rx}" ry="${ry}" fill="url(#geni-ring)"/>
  <text x="${nl.x}" y="${nl.y - ry + 22}" text-anchor="middle" class="geni-label">GENI — Wahrnehmungsschicht</text>
  <text x="${nl.x}" y="${nl.y - ry + 42}" text-anchor="middle" class="geni-sublabel">omnipräsent · modelliert · kein Live-Zugriff · port 8020</text>
</g>`;
}

function buildEdges(layout: ProcessCameraLayout): string {
  const pos = nodePos(layout);
  return layout.edges.map((e) => {
    const from = pos.get(e.from_node_id);
    const to   = pos.get(e.to_node_id);
    if (!from || !to) return "";
    const stroke = EDGE_STROKE[e.edge_type] ?? "#333";
    return `<line class="edge" data-edge-id="${esc(e.edge_id)}" data-from="${esc(e.from_node_id)}" data-to="${esc(e.to_node_id)}" data-etype="${esc(e.edge_type)}" x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="${stroke}" stroke-width="1.4" stroke-opacity="0.45"/>`;
  }).join("\n  ");
}

function buildNodes(model: ProcessCameraModel, layout: ProcessCameraLayout): string {
  const pos = nodePos(layout);
  return model.nodes
    .filter((n) => n.node_id !== "geni")
    .map((node) => {
      const nl = pos.get(node.node_id);
      if (!nl) return "";
      const color = STATUS_COLOR[node.status_kind] ?? "#505060";
      const r = nl.r;
      const label = node.name.length > 18 ? node.name.slice(0, 16) + "…" : node.name;
      const d3mark = node.is_d3_slot
        ? `<text class="node-d3" dy="${r + 13}" text-anchor="middle" fill="#7799ff">[D3]</text>` : "";
      const pulseR = r + 5;
      const pulseDur = 2.5 + (nl.x % 6) * 0.25;
      return `<g class="node-g" data-node-id="${esc(node.node_id)}" data-layer="${esc(node.layer)}" data-name="${esc(node.name)}" transform="translate(${nl.x},${nl.y})">
  <circle class="node-pulse" r="${pulseR}" fill="none" stroke="${color}" stroke-width="0.8" opacity="0.0">
    <animate attributeName="r" values="${pulseR};${pulseR + 6};${pulseR}" dur="${pulseDur}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.0;0.25;0.0" dur="${pulseDur}s" repeatCount="indefinite"/>
  </circle>
  <circle class="node-circle" r="${r}" fill="${color}1a" stroke="${color}" stroke-width="1.6" data-base-color="${color}" data-r="${r}"/>
  <text class="node-label" dy="4" text-anchor="middle" fill="${color}">${esc(label)}</text>
  ${d3mark}
</g>`;
    }).join("\n  ");
}

function buildLayerButtons(model: ProcessCameraModel): string {
  const seen = new Set<string>();
  model.nodes.forEach((n) => seen.add(n.layer));
  return [...seen].map((layer) => {
    const label = LAYER_LABEL[layer] ?? layer;
    return `<button class="layer-btn active" data-layer="${esc(layer)}" onclick="toggleLayer('${esc(layer)}', this)">${esc(label)}</button>`;
  }).join("\n    ");
}

function buildLegend(model: ProcessCameraModel): string {
  const statusItems = model.legend.status_entries.map((e) =>
    `<span class="leg-item"><span class="leg-dot" style="background:${esc(e.color_hint)}"></span>${esc(e.label)}</span>`
  ).join("");
  const edgeItems = Object.entries(EDGE_STROKE).map(([k, v]) =>
    `<span class="leg-item"><span class="leg-line" style="background:${v}"></span>${k.replace(/_/g, " ")}</span>`
  ).join("");
  return `<div id="legend-bar">
  <div class="leg-group"><strong>Status:</strong>${statusItems}</div>
  <div class="leg-group"><strong>Kanten:</strong>${edgeItems}</div>
  <div class="leg-shield">Diese Karte zeigt statische, read-only Prozessspuren. Keine Live-Aktivität. Keine erfundene Innenwelt. Kein Einzug.</div>
</div>`;
}

function buildNodeDataJson(model: ProcessCameraModel, layout: ProcessCameraLayout): string {
  const pos = nodePos(layout);
  const obj: Record<string, unknown> = {};
  for (const n of model.nodes) {
    const nl = pos.get(n.node_id);
    obj[n.node_id] = {
      node_id: n.node_id,
      name: n.name,
      layer: n.layer,
      role: n.role,
      status_kind: n.status_kind,
      activity_mode: n.activity_mode,
      evidence: n.evidence,
      evidence_reason: n.evidence_reason ?? null,
      flarum_origin: n.flarum_origin ?? null,
      source_location: n.source_location ?? null,
      ring_origin: n.ring_origin ?? null,
      is_d3_slot: n.is_d3_slot,
      slot_state: n.slot_state ?? null,
      edge_count: n.edges.length,
      edge_types: n.edges.map((e) => e.trace_type),
      x: nl?.x ?? 0,
      y: nl?.y ?? 0,
    };
  }
  return JSON.stringify(obj);
}

function buildLayoutIndexJson(layout: ProcessCameraLayout): string {
  const obj: Record<string, { x: number; y: number }> = {};
  for (const n of layout.nodes) obj[n.node_id] = { x: n.x, y: n.y };
  return JSON.stringify(obj);
}

const CSS = `
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; }
body {
  font-family: 'Courier New', monospace;
  background: #050810;
  color: #c0c8d8;
  display: flex;
  flex-direction: column;
}
#topbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background: #080d16;
  border-bottom: 1px solid #141e2c;
  flex-shrink: 0;
  z-index: 10;
}
#topbar h1 { font-size: 0.82rem; color: #4a7a9a; white-space: nowrap; margin-right: 6px; letter-spacing: 0.08em; }
#search-input {
  background: #0a1020;
  border: 1px solid #1a2a3a;
  color: #a0b4c8;
  padding: 4px 10px;
  border-radius: 3px;
  font-family: inherit;
  font-size: 0.78rem;
  width: 200px;
  outline: none;
}
#search-input:focus { border-color: #2a5a7a; }
button {
  background: #0a1220;
  border: 1px solid #1a2a3a;
  color: #7a9ab8;
  padding: 3px 9px;
  border-radius: 3px;
  font-family: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}
button:hover { background: #0f1e30; border-color: #2a4a6a; }
#reset-btn { color: #6a9a8a; border-color: #1a3a2a; }
.focus-btn { color: #7a8ab8; }
.layer-btn { color: #6a7a88; }
.layer-btn.active { color: #8aaccc; border-color: #1e3858; background: #0c1828; }
.layer-btn.off { opacity: 0.35; }
#main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}
#main-svg {
  flex: 1;
  display: block;
  cursor: default;
  background: radial-gradient(ellipse at 50% 50%, #070f1e 0%, #040810 70%);
}
#detail-panel {
  width: 280px;
  flex-shrink: 0;
  background: #06090f;
  border-left: 1px solid #121c28;
  overflow-y: auto;
  padding: 14px;
  font-size: 0.75rem;
  line-height: 1.65;
}
.detail-hint { color: #2a3a4a; font-style: italic; }
.det-name { font-size: 0.95rem; color: #d0dae8; font-weight: bold; margin-bottom: 8px; }
.det-row { display: flex; gap: 6px; margin-bottom: 3px; }
.det-key { color: #3a5a6a; min-width: 90px; }
.det-val { color: #8aacbe; }
.det-warn { color: #3a5040; font-style: italic; margin-top: 6px; }
.det-badge-d3 { display: inline-block; background: #0a1838; border: 1px solid #2244aa40; color: #7799ff; padding: 1px 6px; border-radius: 2px; font-size: 0.68rem; margin-top: 4px; }
.det-sep { border: none; border-top: 1px solid #111820; margin: 8px 0; }
.det-traces { color: #3a5060; font-size: 0.7rem; margin-top: 4px; }
#legend-bar {
  flex-shrink: 0;
  background: #060a12;
  border-top: 1px solid #101820;
  padding: 5px 12px;
  font-size: 0.68rem;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.leg-group { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; color: #3a4a58; }
.leg-group strong { color: #2a4a5a; }
.leg-item { display: inline-flex; align-items: center; gap: 4px; }
.leg-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.leg-line { width: 16px; height: 2px; border-radius: 1px; flex-shrink: 0; }
.leg-shield { color: #1e3a2a; font-size: 0.65rem; font-style: italic; margin-left: auto; }
.geni-label { font-size: 0.78rem; fill: #4a90b8; letter-spacing: 0.06em; }
.geni-sublabel { font-size: 0.62rem; fill: #2a5a78; }
.node-label { font-size: 0.68rem; pointer-events: none; }
.node-d3 { font-size: 0.6rem; pointer-events: none; }
.node-g { cursor: pointer; }
.node-g.highlighted .node-circle { filter: url(#glow-node); }
.edge.highlighted { stroke-opacity: 0.85 !important; stroke-width: 2.2 !important; }
.node-g.dimmed { opacity: 0.15; }
.edge.dimmed { opacity: 0.08; }
.node-g.layer-hidden { display: none; }
.edge.layer-hidden { display: none; }
#search-match .node-circle { filter: url(#glow-node); }
`;

const JS = `
var scale = 1, tx = 0, ty = 0;
var isDragging = false, dragStartX = 0, dragStartY = 0, dragTx = 0, dragTy = 0, didDrag = false;
var selectedNodeId = null;
var VW = 1200, VH = 780;

var svg = document.getElementById('main-svg');
var world = document.getElementById('world');

function applyTransform() {
  world.setAttribute('transform', 'translate(' + tx + ',' + ty + ') scale(' + scale + ')');
}

svg.addEventListener('wheel', function(e) {
  e.preventDefault();
  var rect = svg.getBoundingClientRect();
  var mx = (e.clientX - rect.left) / rect.width * VW;
  var my = (e.clientY - rect.top) / rect.height * VH;
  var factor = e.deltaY < 0 ? 1.12 : 0.89;
  tx = mx - (mx - tx) * factor;
  ty = my - (my - ty) * factor;
  scale *= factor;
  scale = Math.max(0.15, Math.min(8, scale));
  applyTransform();
}, { passive: false });

svg.addEventListener('mousedown', function(e) {
  if (e.button !== 0) return;
  isDragging = true;
  didDrag = false;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragTx = tx;
  dragTy = ty;
  e.preventDefault();
});

window.addEventListener('mousemove', function(e) {
  if (!isDragging) return;
  var dx = e.clientX - dragStartX;
  var dy = e.clientY - dragStartY;
  if (Math.abs(dx) > 4 || Math.abs(dy) > 4) didDrag = true;
  var rect = svg.getBoundingClientRect();
  var sx = VW / rect.width;
  var sy = VH / rect.height;
  tx = dragTx + dx * sx;
  ty = dragTy + dy * sy;
  applyTransform();
});

window.addEventListener('mouseup', function() { isDragging = false; });

function resetView() {
  tx = 0; ty = 0; scale = 1;
  applyTransform();
}

function animateTo(targetTx, targetTy, targetScale) {
  var startTx = tx, startTy = ty, startScale = scale;
  var start = performance.now();
  var dur = 380;
  function step(now) {
    var t = Math.min((now - start) / dur, 1);
    t = t < 0.5 ? 2*t*t : -1 + (4-2*t)*t;
    tx = startTx + (targetTx - startTx) * t;
    ty = startTy + (targetTy - startTy) * t;
    scale = startScale + (targetScale - startScale) * t;
    applyTransform();
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function focusOn(nodeId) {
  var pos = LAYOUT[nodeId];
  if (!pos) return;
  var s = 2.2;
  animateTo(VW/2 - pos.x * s, VH/2 - pos.y * s, s);
}

function focusCluster(cx, cy, s) {
  animateTo(VW/2 - cx * s, VH/2 - cy * s, s);
}

var layerState = {};

function toggleLayer(layer, btn) {
  layerState[layer] = !layerState[layer];
  var hidden = layerState[layer];
  btn.classList.toggle('off', hidden);
  btn.classList.toggle('active', !hidden);
  document.querySelectorAll('[data-layer="' + layer + '"]').forEach(function(el) {
    el.classList.toggle('layer-hidden', hidden);
  });
  document.querySelectorAll('.edge').forEach(function(el) {
    var from = el.getAttribute('data-from');
    var to = el.getAttribute('data-to');
    var fromEl = document.querySelector('[data-node-id="' + from + '"]');
    var toEl = document.querySelector('[data-node-id="' + to + '"]');
    var hide = (fromEl && fromEl.classList.contains('layer-hidden')) ||
               (toEl && toEl.classList.contains('layer-hidden'));
    el.classList.toggle('layer-hidden', hide);
  });
}

function showDetail(nodeId) {
  var d = NODE_DATA[nodeId];
  if (!d) return;
  selectedNodeId = nodeId;
  var statusColor = {
    derived:'#4a9eff', modelled:'#8888cc', read_only:'#55aa77',
    unknown:'#50506a', blocked:'#cc4444', replay:'#cc9933', measured:'#ff4444'
  };
  var col = statusColor[d.status_kind] || '#888';
  var d3html = d.is_d3_slot ? '<div class="det-badge-d3">[D3] Flarum-Slot</div>' : '';
  var tracesHtml = d.edge_types.length
    ? '<div class="det-traces">Spuren: ' + d.edge_types.join(', ') + '</div>' : '';
  var html = '<div class="det-name">' + d.name + '</div>' +
    d3html +
    '<hr class="det-sep">' +
    '<div class="det-row"><span class="det-key">node_id</span><span class="det-val">' + d.node_id + '</span></div>' +
    '<div class="det-row"><span class="det-key">layer</span><span class="det-val">' + d.layer.replace(/_/g,' ') + '</span></div>' +
    '<div class="det-row"><span class="det-key">role</span><span class="det-val">' + d.role + '</span></div>' +
    '<div class="det-row"><span class="det-key">status</span><span class="det-val" style="color:' + col + '">' + d.status_kind + '</span></div>' +
    '<div class="det-row"><span class="det-key">aktivität</span><span class="det-val">' + d.activity_mode + '</span></div>' +
    '<div class="det-row"><span class="det-key">evidenz</span><span class="det-val">' + d.evidence + '</span></div>' +
    (d.evidence_reason ? '<div class="det-row"><span class="det-key">grund</span><span class="det-val">' + d.evidence_reason + '</span></div>' : '') +
    (d.source_location ? '<div class="det-row"><span class="det-key">quelle</span><span class="det-val">' + d.source_location + '</span></div>' : '') +
    (d.flarum_origin ? '<div class="det-row"><span class="det-key">herkunft</span><span class="det-val">' + d.flarum_origin + '</span></div>' : '') +
    (d.ring_origin !== null ? '<div class="det-row"><span class="det-key">ring</span><span class="det-val">' + d.ring_origin + '</span></div>' : '') +
    (d.slot_state ? '<div class="det-row"><span class="det-key">slot</span><span class="det-val">' + d.slot_state + '</span></div>' : '') +
    '<hr class="det-sep">' +
    tracesHtml +
    '<div class="det-warn">nicht besetzt · kein Live-Zustand · kein Einzug</div>';
  document.getElementById('detail-content').innerHTML = html;
}

function highlightNode(nodeId) {
  var connectedNodes = new Set([nodeId]);
  var connectedEdges = new Set();
  document.querySelectorAll('.edge').forEach(function(el) {
    var from = el.getAttribute('data-from');
    var to = el.getAttribute('data-to');
    if (from === nodeId || to === nodeId) {
      connectedEdges.add(el.getAttribute('data-edge-id'));
      connectedNodes.add(from);
      connectedNodes.add(to);
    }
  });
  document.querySelectorAll('.node-g').forEach(function(el) {
    var nid = el.getAttribute('data-node-id');
    el.classList.toggle('highlighted', connectedNodes.has(nid));
    el.classList.toggle('dimmed', !connectedNodes.has(nid));
  });
  document.querySelectorAll('.edge').forEach(function(el) {
    var eid = el.getAttribute('data-edge-id');
    el.classList.toggle('highlighted', connectedEdges.has(eid));
    el.classList.toggle('dimmed', !connectedEdges.has(eid));
  });
}

function clearHighlight() {
  document.querySelectorAll('.node-g, .edge').forEach(function(el) {
    el.classList.remove('highlighted', 'dimmed');
  });
}

document.querySelectorAll('.node-g').forEach(function(el) {
  el.addEventListener('click', function(e) {
    if (didDrag) return;
    var nid = el.getAttribute('data-node-id');
    showDetail(nid);
    highlightNode(nid);
    e.stopPropagation();
  });
  el.addEventListener('mouseenter', function() {
    if (selectedNodeId) return;
    highlightNode(el.getAttribute('data-node-id'));
  });
  el.addEventListener('mouseleave', function() {
    if (selectedNodeId) return;
    clearHighlight();
  });
});

svg.addEventListener('click', function(e) {
  if (didDrag) return;
  if (e.target === svg || e.target.id === 'world') {
    selectedNodeId = null;
    clearHighlight();
    document.getElementById('detail-content').innerHTML = '<p class="detail-hint">Klick auf einen Prozessknoten</p>';
  }
});

var searchInput = document.getElementById('search-input');
searchInput.addEventListener('input', function() {
  var q = searchInput.value.trim().toLowerCase();
  if (!q) { clearHighlight(); selectedNodeId = null; return; }
  var found = Object.values(NODE_DATA).find(function(d) {
    return d.name.toLowerCase().includes(q) || d.node_id.toLowerCase().includes(q);
  });
  if (found) {
    focusOn(found.node_id);
    showDetail(found.node_id);
    highlightNode(found.node_id);
    selectedNodeId = found.node_id;
  }
});
`;

export function buildProcessCameraInteractiveHtml(
  model: ProcessCameraModel,
  layout: ProcessCameraLayout,
): string {
  const nodeDataJson   = buildNodeDataJson(model, layout);
  const layoutJson     = buildLayoutIndexJson(layout);
  const svgDefs        = buildSvgDefs();
  const geniField      = buildGeniField(layout);
  const edges          = buildEdges(layout);
  const nodes          = buildNodes(model, layout);
  const layerBtns      = buildLayerButtons(model);
  const legendHtml     = buildLegend(model);
  const s              = model.status_summary;

  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Prozesskamera — Neural Process Map</title>
<meta name="generator" content="flextrawurst-process-camera-ring-22j-l">
<meta name="robots" content="noindex,nofollow">
<style>${CSS}</style>
</head>
<body>
<div id="topbar">
  <h1>Prozesskamera</h1>
  <input id="search-input" type="text" placeholder="Knoten suchen…" autocomplete="off">
  <button class="focus-btn" onclick="focusOn('dak_gord_system')">dak+gord</button>
  <button class="focus-btn" onclick="focusCluster(210,390,2.0)">namelessAI</button>
  <button class="focus-btn" onclick="focusCluster(620,595,1.6)">Systemprozesse</button>
  <button class="focus-btn" onclick="focusOn('systemweiser')">Metaschicht</button>
  <button id="reset-btn" onclick="resetView()">Reset-View</button>
  <span style="width:1px;height:18px;background:#1a2a3a;display:inline-block"></span>
  ${layerBtns}
</div>
<div id="main">
  <svg id="main-svg" viewBox="0 0 ${layout.viewbox_width} ${layout.viewbox_height}" xmlns="http://www.w3.org/2000/svg">
    ${svgDefs}
    <g id="world">
      ${geniField}
      <g id="edges">${edges}</g>
      <g id="nodes">${nodes}</g>
    </g>
  </svg>
  <div id="detail-panel">
    <div id="detail-content">
      <p class="detail-hint">Klick auf einen Prozessknoten</p>
    </div>
  </div>
</div>
${legendHtml}
<script>
var NODE_DATA = ${nodeDataJson};
var LAYOUT    = ${layoutJson};
${JS}
</script>
<!-- static:true | read_only:true | no_runtime:true | no_activation:true | process_count:${s.process_count} | measured:${s.measured_count} | occupied:${s.occupied_count} | created:${esc(model.created_at)} -->
</body>
</html>`;
}
