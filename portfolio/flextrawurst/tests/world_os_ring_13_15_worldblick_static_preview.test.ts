import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  buildWorldInspectionExportFixture,
  FIXTURE_EXPORT_ID,
  FIXTURE_EXPORT_VERSION,
  FIXTURE_CREATED_AT,
} from "../kernel/export/world_inspection_export_fixture.ts";
import { buildWorldInspectionExport } from "../kernel/export/world_inspection_export_builder.ts";
import {
  serializeWorldInspectionExportToJson,
  serializeWorldInspectionExportToMarkdown,
} from "../kernel/export/world_inspection_export_serializer.ts";
import { buildStaticPreview } from "../kernel/static_preview/static_preview_builder.ts";
import { buildStaticPreviewHtml } from "../kernel/static_preview/static_preview_html.ts";
import { buildWorldblickOutput } from "../kernel/worldblick/worldblick_builder.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

// ---------------------------------------------------------------------------
// Ring 13 — WorldInspectionExport Modell
// ---------------------------------------------------------------------------

describe("Ring 13 — WorldInspectionExport Pflichtfelder", () => {
  const exp = buildWorldInspectionExportFixture();

  it("is_read_only ist true", () => {
    assert.equal(exp.is_read_only, true);
  });

  it("creates_events ist false", () => {
    assert.equal(exp.creates_events, false);
  });

  it("activates_slots ist false", () => {
    assert.equal(exp.activates_slots, false);
  });

  it("is_live_flextrawurst_state ist false", () => {
    assert.equal(exp.is_live_flextrawurst_state, false);
  });

  it("origin_layer ist inspection_export", () => {
    assert.equal(exp.origin_layer, "inspection_export");
  });

  it("export_id stimmt mit Fixture ueberein", () => {
    assert.equal(exp.export_id, FIXTURE_EXPORT_ID);
  });

  it("export_version stimmt mit Fixture ueberein", () => {
    assert.equal(exp.export_version, FIXTURE_EXPORT_VERSION);
  });

  it("created_at stimmt mit Fixture ueberein", () => {
    assert.equal(exp.created_at, FIXTURE_CREATED_AT);
  });

  it("sections ist ein Array", () => {
    assert.ok(Array.isArray(exp.sections));
  });

  it("hat genau 11 Sections", () => {
    assert.equal(exp.sections.length, 11);
  });

  it("warnings ist ein Array", () => {
    assert.ok(Array.isArray(exp.warnings));
  });

  it("next_human_decisions ist ein Array", () => {
    assert.ok(Array.isArray(exp.next_human_decisions));
  });

  it("warnings sind nicht leer", () => {
    assert.ok(exp.warnings.length > 0);
  });

  it("next_human_decisions sind nicht leer", () => {
    assert.ok(exp.next_human_decisions.length > 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 13 — Pflicht-Sections vorhanden
// ---------------------------------------------------------------------------

describe("Ring 13 — Pflicht-Sections vorhanden", () => {
  const exp = buildWorldInspectionExportFixture();
  const sectionIds = exp.sections.map((s) => s.section_id);

  it("spine Section vorhanden", () => {
    assert.ok(sectionIds.includes("spine"));
  });

  it("import_gate Section vorhanden", () => {
    assert.ok(sectionIds.includes("import_gate"));
  });

  it("visual_meaning Section vorhanden", () => {
    assert.ok(sectionIds.includes("visual_meaning"));
  });

  it("replay_explanation Section vorhanden", () => {
    assert.ok(sectionIds.includes("replay_explanation"));
  });

  it("worldview_graph Section vorhanden", () => {
    assert.ok(sectionIds.includes("worldview_graph"));
  });

  it("origin_archive Section vorhanden", () => {
    assert.ok(sectionIds.includes("origin_archive"));
  });

  it("memory_candidate Section vorhanden", () => {
    assert.ok(sectionIds.includes("memory_candidate"));
  });

  it("continuity_dossier Section vorhanden", () => {
    assert.ok(sectionIds.includes("continuity_dossier"));
  });

  it("world_start_readiness Section vorhanden", () => {
    assert.ok(sectionIds.includes("world_start_readiness"));
  });

  it("concept_guard Section vorhanden", () => {
    assert.ok(sectionIds.includes("concept_guard"));
  });

  it("activation_firewall Section vorhanden", () => {
    assert.ok(sectionIds.includes("activation_firewall"));
  });
});

// ---------------------------------------------------------------------------
// Ring 13 — Section Inhalte
// ---------------------------------------------------------------------------

describe("Ring 13 — Section Inhalte", () => {
  const exp = buildWorldInspectionExportFixture();
  const find = (id: string) => exp.sections.find((s) => s.section_id === id)!;

  it("spine section hat item_count > 0", () => {
    assert.ok(find("spine").item_count > 0);
  });

  it("origin_archive section hat notes", () => {
    assert.ok(find("origin_archive").notes.length > 0);
  });

  it("memory_candidate summary enthaelt is_adopted_memory", () => {
    assert.ok(find("memory_candidate").summary.includes("is_adopted_memory"));
  });

  it("continuity_dossier summary enthaelt can_start_as_live_entity", () => {
    assert.ok(find("continuity_dossier").summary.includes("can_start_as_live_entity"));
  });

  it("world_start_readiness summary enthaelt ready_for_activation: false", () => {
    assert.ok(find("world_start_readiness").summary.includes("ready_for_activation: false"));
  });

  it("world_start_readiness summary enthaelt ready_for_ui: false", () => {
    assert.ok(find("world_start_readiness").summary.includes("ready_for_ui: false"));
  });

  it("activation_firewall summary enthaelt blocked", () => {
    assert.ok(find("activation_firewall").summary.includes("blocked"));
  });

  it("visual_meaning section hat item_count > 0", () => {
    assert.ok(find("visual_meaning").item_count > 0);
  });

  it("worldview_graph section hat notes", () => {
    assert.ok(find("worldview_graph").notes.length > 0);
  });

  it("replay_explanation notes enthalten creates_new_events", () => {
    const notes = find("replay_explanation").notes;
    assert.ok(notes.some((n) => n.includes("creates_new_events")));
  });

  it("concept_guard section item_count ist 0", () => {
    assert.equal(find("concept_guard").item_count, 0);
  });

  it("activation_firewall item_count ist 0", () => {
    assert.equal(find("activation_firewall").item_count, 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 13 — Serializer JSON
// ---------------------------------------------------------------------------

describe("Ring 13 — JSON Export Serializer", () => {
  const exp = buildWorldInspectionExportFixture();

  it("JSON Export ist deterministisch (gleicher Output zweimal)", () => {
    const a = serializeWorldInspectionExportToJson(exp);
    const b = serializeWorldInspectionExportToJson(exp);
    assert.equal(a, b);
  });

  it("JSON Export beginnt mit {", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.trimStart().startsWith("{"));
  });

  it("JSON Export enthaelt export_id", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("export_id"));
  });

  it("JSON Export enthaelt is_read_only", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("is_read_only"));
  });

  it("JSON Export enthaelt creates_events", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("creates_events"));
  });

  it("JSON Export enthaelt activates_slots", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("activates_slots"));
  });

  it("JSON Export enthaelt is_live_flextrawurst_state", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("is_live_flextrawurst_state"));
  });

  it("JSON Export enthaelt origin_layer", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("origin_layer"));
  });

  it("JSON Export enthaelt sections", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    assert.ok(json.includes("sections"));
  });

  it("JSON Parse: is_read_only ist true", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    const parsed = JSON.parse(json);
    assert.equal(parsed.is_read_only, true);
  });

  it("JSON Parse: creates_events ist false", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    const parsed = JSON.parse(json);
    assert.equal(parsed.creates_events, false);
  });

  it("JSON Parse: activates_slots ist false", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    const parsed = JSON.parse(json);
    assert.equal(parsed.activates_slots, false);
  });

  it("JSON Parse: is_live_flextrawurst_state ist false", () => {
    const json = serializeWorldInspectionExportToJson(exp);
    const parsed = JSON.parse(json);
    assert.equal(parsed.is_live_flextrawurst_state, false);
  });
});

// ---------------------------------------------------------------------------
// Ring 13 — Serializer Markdown
// ---------------------------------------------------------------------------

describe("Ring 13 — Markdown Export Serializer", () => {
  const exp = buildWorldInspectionExportFixture();

  it("Markdown Export ist deterministisch (gleicher Output zweimal)", () => {
    const a = serializeWorldInspectionExportToMarkdown(exp);
    const b = serializeWorldInspectionExportToMarkdown(exp);
    assert.equal(a, b);
  });

  it("Markdown Export beginnt mit # World Inspection Export", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.startsWith("# World Inspection Export"));
  });

  it("Markdown enthaelt export_id", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("export_id") || md.includes(FIXTURE_EXPORT_ID));
  });

  it("Markdown enthaelt is_read_only", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("is_read_only"));
  });

  it("Markdown enthaelt Sections-Header", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("## Sections"));
  });

  it("Markdown enthaelt Warnings-Header", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("## Warnings"));
  });

  it("Markdown enthaelt Next Human Decisions-Header", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("## Next Human Decisions"));
  });

  it("Markdown enthaelt alle Section-Labels", () => {
    const md = serializeWorldInspectionExportToMarkdown(exp);
    assert.ok(md.includes("Spine Summary"));
    assert.ok(md.includes("Origin Archive Summary"));
    assert.ok(md.includes("Concept Guard Summary"));
    assert.ok(md.includes("Activation Firewall Summary"));
  });

  it("Fixture Build ist deterministisch (zweifacher Aufbau gleich)", () => {
    const a = buildWorldInspectionExportFixture();
    const b = buildWorldInspectionExportFixture();
    assert.deepEqual(a, b);
  });
});

// ---------------------------------------------------------------------------
// Ring 14 — StaticPreview Modell
// ---------------------------------------------------------------------------

describe("Ring 14 — StaticPreview Pflichtfelder", () => {
  const exp = buildWorldInspectionExportFixture();
  const preview = buildStaticPreview("preview-001", exp);

  it("is_static ist true", () => {
    assert.equal(preview.is_static, true);
  });

  it("is_read_only ist true", () => {
    assert.equal(preview.is_read_only, true);
  });

  it("has_external_dependencies ist false", () => {
    assert.equal(preview.has_external_dependencies, false);
  });

  it("can_activate_slots ist false", () => {
    assert.equal(preview.can_activate_slots, false);
  });

  it("can_create_events ist false", () => {
    assert.equal(preview.can_create_events, false);
  });

  it("html_title enthaelt Flextrawurst", () => {
    assert.ok(preview.html_title.includes("Flextrawurst"));
  });

  it("html_title enthaelt Weltkamera Preview", () => {
    assert.ok(preview.html_title.includes("Weltkamera Preview"));
  });

  it("section_count entspricht export.sections.length", () => {
    assert.equal(preview.section_count, exp.sections.length);
  });

  it("source_export_id entspricht export_id", () => {
    assert.equal(preview.source_export_id, exp.export_id);
  });

  it("html ist ein nicht-leerer String", () => {
    assert.ok(typeof preview.html === "string" && preview.html.length > 0);
  });
});

// ---------------------------------------------------------------------------
// Ring 14 — HTML Inhalt
// ---------------------------------------------------------------------------

describe("Ring 14 — HTML Pflichtinhalt", () => {
  const exp = buildWorldInspectionExportFixture();
  const html = buildStaticPreviewHtml(exp);

  it("HTML enthaelt DOCTYPE", () => {
    assert.ok(html.includes("<!DOCTYPE html>"));
  });

  it("HTML enthaelt <html", () => {
    assert.ok(html.includes("<html"));
  });

  it("HTML enthaelt Flextrawurst", () => {
    assert.ok(html.includes("Flextrawurst"));
  });

  it("HTML enthaelt Weltkamera Preview", () => {
    assert.ok(html.includes("Weltkamera Preview"));
  });

  it("HTML enthaelt read-only", () => {
    assert.ok(html.includes("read-only"));
  });

  it("HTML enthaelt no activation", () => {
    assert.ok(html.includes("no activation"));
  });

  it("HTML enthaelt no live import", () => {
    assert.ok(html.includes("no live import"));
  });

  it("HTML enthaelt OriginArchive", () => {
    assert.ok(html.includes("OriginArchive"));
  });

  it("HTML enthaelt MemoryCandidates", () => {
    assert.ok(html.includes("MemoryCandidates"));
  });

  it("HTML enthaelt ContinuityDossiers", () => {
    assert.ok(html.includes("ContinuityDossiers"));
  });

  it("HTML enthaelt WorldviewGraph", () => {
    assert.ok(html.includes("WorldviewGraph"));
  });

  it("HTML enthaelt VisualMeanings", () => {
    assert.ok(html.includes("VisualMeanings"));
  });

  it("HTML enthaelt NextHumanDecisions", () => {
    assert.ok(html.includes("NextHumanDecisions"));
  });

  it("HTML enthaelt kein script src", () => {
    assert.ok(!html.includes("script src"));
  });

  it("HTML enthaelt kein CDN", () => {
    const lower = html.toLowerCase();
    assert.ok(!lower.includes("cdn."));
  });

  it("HTML enthaelt kein <canvas", () => {
    assert.ok(!html.toLowerCase().includes("<canvas"));
  });

  it("HTML enthaelt kein websocket", () => {
    assert.ok(!html.toLowerCase().includes("websocket"));
  });

  it("HTML enthaelt kein fetch(", () => {
    assert.ok(!html.includes("fetch("));
  });

  it("HTML enthaelt kein XMLHttpRequest", () => {
    assert.ok(!html.includes("XMLHttpRequest"));
  });

  it("HTML enthaelt kein import(", () => {
    assert.ok(!html.includes("import("));
  });

  it("HTML enthaelt is_read_only: true im Meta-Bereich", () => {
    assert.ok(html.includes("is_read_only"));
  });

  it("HTML enthaelt creates_events: false im Meta-Bereich", () => {
    assert.ok(html.includes("creates_events"));
  });

  it("HTML enthaelt activates_slots: false im Meta-Bereich", () => {
    assert.ok(html.includes("activates_slots"));
  });

  it("HTML enthaelt is_live_flextrawurst_state: false im Meta-Bereich", () => {
    assert.ok(html.includes("is_live_flextrawurst_state"));
  });

  it("HTML ist deterministisch (gleicher Output zweimal)", () => {
    const a = buildStaticPreviewHtml(exp);
    const b = buildStaticPreviewHtml(exp);
    assert.equal(a, b);
  });

  it("HTML Preview ist deterministisch fuer gleichen Export", () => {
    const expA = buildWorldInspectionExportFixture();
    const expB = buildWorldInspectionExportFixture();
    const htmlA = buildStaticPreviewHtml(expA);
    const htmlB = buildStaticPreviewHtml(expB);
    assert.equal(htmlA, htmlB);
  });

  it("HTML hat keine externen Dependencies (kein http:// in src/href)", () => {
    const hasSrcHttp = /src\s*=\s*["']https?:/.test(html);
    const hasHrefHttp = /href\s*=\s*["']https?:/.test(html);
    assert.ok(!hasSrcHttp && !hasHrefHttp);
  });

  it("HTML enthaelt ConceptGuardWarnings", () => {
    assert.ok(html.includes("ConceptGuardWarnings"));
  });

  it("HTML enthaelt ReplayExplanations", () => {
    assert.ok(html.includes("ReplayExplanations"));
  });
});

// ---------------------------------------------------------------------------
// Ring 15 — Worldblick Output Modell
// ---------------------------------------------------------------------------

describe("Ring 15 — WorldblickOutput Pflichtfelder", () => {
  const output = buildWorldblickOutput({
    output_id: "wbl-001",
    created_at: "2026-05-09T00:00:00.000Z",
    base_dir: "out/worldblick",
  });

  it("json_path endet auf .json", () => {
    assert.ok(output.json_path.endsWith(".json"));
  });

  it("markdown_path endet auf .md", () => {
    assert.ok(output.markdown_path.endsWith(".md"));
  });

  it("html_path endet auf .html", () => {
    assert.ok(output.html_path.endsWith(".html"));
  });

  it("creates_events ist false", () => {
    assert.equal(output.creates_events, false);
  });

  it("activates_slots ist false", () => {
    assert.equal(output.activates_slots, false);
  });

  it("imports_live_data ist false", () => {
    assert.equal(output.imports_live_data, false);
  });

  it("starts_world ist false", () => {
    assert.equal(output.starts_world, false);
  });

  it("is_read_only ist true", () => {
    assert.equal(output.is_read_only, true);
  });

  it("json_path enthaelt world_inspection_export", () => {
    assert.ok(output.json_path.includes("world_inspection_export"));
  });

  it("markdown_path enthaelt world_inspection_export", () => {
    assert.ok(output.markdown_path.includes("world_inspection_export"));
  });

  it("html_path enthaelt worldview_static_preview", () => {
    assert.ok(output.html_path.includes("worldview_static_preview"));
  });

  it("Output-Pfade sind deterministisch fuer gleiche base_dir", () => {
    const a = buildWorldblickOutput({ output_id: "x", created_at: "t", base_dir: "out/worldblick" });
    const b = buildWorldblickOutput({ output_id: "y", created_at: "u", base_dir: "out/worldblick" });
    assert.equal(a.json_path, b.json_path);
    assert.equal(a.markdown_path, b.markdown_path);
    assert.equal(a.html_path, b.html_path);
  });

  it("output_id wird korrekt gesetzt", () => {
    assert.equal(output.output_id, "wbl-001");
  });
});

// ---------------------------------------------------------------------------
// Ring 13/15 — ConceptGuard neue Muster
// ---------------------------------------------------------------------------

describe("ConceptGuard — neue Ring-13-15 Muster", () => {
  it("StaticPreview ist Live-Welt wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "StaticPreview ist Live-Welt — das darf nicht sein" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "StaticPreview ist Live-Welt"));
  });

  it("HTMLPreview aktiviert Wesen wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "HTMLPreview aktiviert Wesen im System" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "HTMLPreview aktiviert Wesen"));
  });

  it("Worldblick startet Flextrawurst wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Worldblick startet Flextrawurst jetzt" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Worldblick startet Flextrawurst"));
  });

  it("Export erzeugt Events wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Export erzeugt Events bei jedem Aufruf" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Export erzeugt Events"));
  });

  it("InspectionExport ist Migration wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "InspectionExport ist Migration der Daten" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "InspectionExport ist Migration"));
  });

  it("Weltkamera ist Renderer wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Weltkamera ist Renderer fuer Canvas" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Weltkamera ist Renderer"));
  });

  it("Preview ist Einzug wird erkannt", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Preview ist Einzug der Wesen" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Preview ist Einzug"));
  });

  it("sauberer Text erzeugt keine Verletzungen (Fixture-Warntext)", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Statischer Weltblick — kein Einzug, keine Aktivierung." },
    ]);
    assert.equal(report.ok, true);
    assert.equal(report.violations.length, 0);
  });

  it("ConceptGuard-Violation-Message enthaelt Korrekt-Formulierung fuer StaticPreview", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "StaticPreview ist Live-Welt" },
    ]);
    const v = report.violations.find((v) => v.term === "StaticPreview ist Live-Welt");
    assert.ok(v?.message.includes("is_static") || v?.message.includes("statisch"));
  });

  it("ConceptGuard-Violation-Message enthaelt Korrekt-Formulierung fuer Export erzeugt Events", () => {
    const report = checkConceptLanguage([
      { id: "x", text: "Export erzeugt Events" },
    ]);
    const v = report.violations.find((v) => v.term === "Export erzeugt Events");
    assert.ok(v?.message.includes("creates_events") || v?.message.includes("read-only"));
  });
});

// ---------------------------------------------------------------------------
// Ring 13/15 — Systemzustand: unverändert
// ---------------------------------------------------------------------------

describe("Ring 13–15 — Systemzustand unberuehrt", () => {
  it("EventStore bleibt unberuehrt: buildWorldblickOutput erzeugt keine Events", () => {
    const output = buildWorldblickOutput({
      output_id: "test-out",
      created_at: "2026-05-09T00:00:00.000Z",
      base_dir: "out/test",
    });
    assert.equal(output.creates_events, false);
    assert.equal(output.activates_slots, false);
  });

  it("ActivationFirewall bleibt blocked: activation_firewall section zeigt blocked", () => {
    const exp = buildWorldInspectionExportFixture();
    const s = exp.sections.find((sec) => sec.section_id === "activation_firewall");
    assert.ok(s?.summary.includes("blocked"));
  });

  it("ready_for_ui bleibt false (aus world_start_readiness section)", () => {
    const exp = buildWorldInspectionExportFixture();
    const s = exp.sections.find((sec) => sec.section_id === "world_start_readiness");
    assert.ok(s?.summary.includes("ready_for_ui: false"));
  });

  it("ready_for_activation bleibt false (aus world_start_readiness section)", () => {
    const exp = buildWorldInspectionExportFixture();
    const s = exp.sections.find((sec) => sec.section_id === "world_start_readiness");
    assert.ok(s?.summary.includes("ready_for_activation: false"));
  });

  it("InspectionExport ist_live_flextrawurst_state false", () => {
    const exp = buildWorldInspectionExportFixture();
    assert.equal(exp.is_live_flextrawurst_state, false);
  });

  it("InspectionExport erzeugt keine Events", () => {
    const exp = buildWorldInspectionExportFixture();
    assert.equal(exp.creates_events, false);
  });

  it("StaticPreview aktiviert keine Slots", () => {
    const exp = buildWorldInspectionExportFixture();
    const preview = buildStaticPreview("p", exp);
    assert.equal(preview.can_activate_slots, false);
  });

  it("StaticPreview erzeugt keine Events", () => {
    const exp = buildWorldInspectionExportFixture();
    const preview = buildStaticPreview("p", exp);
    assert.equal(preview.can_create_events, false);
  });

  it("buildWorldInspectionExport gibt is_read_only: true zurueck", () => {
    const exp = buildWorldInspectionExport({
      export_id: "test",
      export_version: "0.0.1",
      created_at: "2026-01-01T00:00:00.000Z",
      spine_summary: { section_id: "spine", label: "Spine", summary: "ok", item_count: 0, notes: [] },
      import_gate_summary: { section_id: "import_gate", label: "Import Gate", summary: "ok", item_count: 0, notes: [] },
      visual_meaning_summary: { section_id: "visual_meaning", label: "Visual Meaning", summary: "ok", item_count: 0, notes: [] },
      replay_explanation_summary: { section_id: "replay_explanation", label: "Replay", summary: "ok", item_count: 0, notes: [] },
      worldview_graph_summary: { section_id: "worldview_graph", label: "Worldview", summary: "ok", item_count: 0, notes: [] },
      origin_archive_summary: { section_id: "origin_archive", label: "Origin", summary: "ok", item_count: 0, notes: [] },
      memory_candidate_summary: { section_id: "memory_candidate", label: "Memory", summary: "ok", item_count: 0, notes: [] },
      continuity_dossier_summary: { section_id: "continuity_dossier", label: "Continuity", summary: "ok", item_count: 0, notes: [] },
      world_start_readiness_summary: { section_id: "world_start_readiness", label: "Readiness", summary: "ok", item_count: 0, notes: [] },
      concept_guard_summary: { section_id: "concept_guard", label: "Concept Guard", summary: "ok", item_count: 0, notes: [] },
      activation_firewall_summary: { section_id: "activation_firewall", label: "Firewall", summary: "ok", item_count: 0, notes: [] },
    });
    assert.equal(exp.is_read_only, true);
    assert.equal(exp.creates_events, false);
    assert.equal(exp.activates_slots, false);
    assert.equal(exp.is_live_flextrawurst_state, false);
    assert.equal(exp.origin_layer, "inspection_export");
  });

  it("Worldblick startet keine Welt", () => {
    const output = buildWorldblickOutput({ output_id: "x", created_at: "t", base_dir: "out" });
    assert.equal(output.starts_world, false);
  });

  it("Worldblick importiert keine Live-Daten", () => {
    const output = buildWorldblickOutput({ output_id: "x", created_at: "t", base_dir: "out" });
    assert.equal(output.imports_live_data, false);
  });
});
