import type { WorldInspectionExport } from "../export/world_inspection_export_model.ts";
import type { ExportSection } from "../export/world_inspection_export_model.ts";

function esc(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderSection(section: ExportSection): string {
  const notesHtml = section.notes
    .map((n) => `<div class="note">${esc(n)}</div>`)
    .join("");
  return `<div class="section">
    <p class="summary">${esc(section.summary)}</p>
    <span class="badge">Items: ${section.item_count}</span>
    ${notesHtml}
  </div>`;
}

function findSection(exp: WorldInspectionExport, id: string): string {
  const s = exp.sections.find((sec) => sec.section_id === id);
  if (!s) return `<div class="section"><p class="note">Kein Abschnitt fuer ${esc(id)}.</p></div>`;
  return renderSection(s);
}

function allSectionsHtml(exp: WorldInspectionExport): string {
  return exp.sections
    .map(
      (s) => `<div class="section">
    <h3>${esc(s.label)}</h3>
    <p class="summary">${esc(s.summary)}</p>
    <span class="badge">Items: ${s.item_count}</span>
    ${s.notes.map((n) => `<div class="note">${esc(n)}</div>`).join("")}
  </div>`
    )
    .join("\n");
}

export function buildStaticPreviewHtml(exp: WorldInspectionExport): string {
  const warningsHtml = exp.warnings.length > 0
    ? exp.warnings.map((w) => `<li>${esc(w)}</li>`).join("")
    : `<li class="note">Keine Warnungen.</li>`;

  const decisionsHtml = exp.next_human_decisions.length > 0
    ? exp.next_human_decisions.map((d) => `<li>${esc(d)}</li>`).join("")
    : `<li class="note">Keine ausstehenden Entscheidungen.</li>`;

  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Flextrawurst &#8212; Weltkamera Preview</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: monospace; background: #0a0a0a; color: #d0d0d0; margin: 0; padding: 2rem; line-height: 1.5; }
  h1 { color: #e8e8e8; border-bottom: 1px solid #2a2a2a; padding-bottom: 0.5rem; margin-top: 0; }
  h2 { color: #aaa; margin-top: 2rem; margin-bottom: 0.5rem; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em; }
  h3 { color: #c0c0c0; margin-bottom: 0.25rem; font-size: 0.95rem; }
  .status-bar { background: #111; border: 1px solid #2a2a2a; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 2rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .tag { background: #1e1010; color: #cc6666; border: 1px solid #4a2020; border-radius: 3px; padding: 0.15rem 0.5rem; font-size: 0.8rem; }
  .section { background: #0f0f0f; border: 1px solid #1e1e1e; border-radius: 4px; padding: 1rem; margin-bottom: 0.75rem; }
  .summary { color: #aaa; margin: 0.25rem 0 0.5rem 0; font-size: 0.9rem; }
  .badge { display: inline-block; background: #0f1e0f; color: #66cc66; border: 1px solid #1e4a1e; border-radius: 3px; padding: 0.1rem 0.4rem; font-size: 0.78rem; }
  .note { color: #777; font-size: 0.82rem; margin-top: 0.3rem; padding-left: 0.6rem; border-left: 2px solid #252525; }
  .meta { color: #555; font-size: 0.78rem; margin-bottom: 0.3rem; }
  ul.warn-list li { color: #cc9933; margin-bottom: 0.3rem; }
  ul.decision-list li { color: #6699cc; margin-bottom: 0.3rem; }
  ul { padding-left: 1.5rem; margin: 0.5rem 0; }
</style>
</head>
<body>
<h1>Flextrawurst &#8212; Weltkamera Preview</h1>

<div class="status-bar">
  <span class="tag">read-only</span>
  <span class="tag">no activation</span>
  <span class="tag">no live import</span>
  <span class="tag">static export</span>
  <span class="tag">kein Renderer</span>
  <span class="tag">kein Einzug</span>
  <span class="tag">kein Canvas</span>
  <span class="tag">kein Server</span>
</div>

<h2>Export-Metadaten</h2>
<div class="section">
  <div class="meta">export_id: ${esc(exp.export_id)}</div>
  <div class="meta">export_version: ${esc(exp.export_version)}</div>
  <div class="meta">created_at: ${esc(exp.created_at)}</div>
  <div class="meta">origin_layer: ${esc(exp.origin_layer)}</div>
  <div class="meta">is_read_only: ${exp.is_read_only} &nbsp;|&nbsp; creates_events: ${exp.creates_events} &nbsp;|&nbsp; activates_slots: ${exp.activates_slots} &nbsp;|&nbsp; is_live_flextrawurst_state: ${exp.is_live_flextrawurst_state}</div>
</div>

<h2>OriginArchive</h2>
${findSection(exp, "origin_archive")}

<h2>MemoryCandidates</h2>
${findSection(exp, "memory_candidate")}

<h2>ContinuityDossiers</h2>
${findSection(exp, "continuity_dossier")}

<h2>WorldviewGraph</h2>
${findSection(exp, "worldview_graph")}

<h2>VisualMeanings</h2>
${findSection(exp, "visual_meaning")}

<h2>ReplayExplanations</h2>
${findSection(exp, "replay_explanation")}

<h2>ConceptGuardWarnings</h2>
${findSection(exp, "concept_guard")}

<h2>Alle Sections</h2>
${allSectionsHtml(exp)}

<h2>Warnungen</h2>
<ul class="warn-list">${warningsHtml}</ul>

<h2>NextHumanDecisions</h2>
<ul class="decision-list">${decisionsHtml}</ul>

</body>
</html>`;
}
