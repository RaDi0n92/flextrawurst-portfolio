import { describe, it } from "node:test";
import assert from "node:assert/strict";

import { buildCanonicalProcessSnapshot } from "../kernel/process_model/process_snapshot.ts";
import { buildProcessCameraModel } from "../kernel/process_camera/process_camera_builder.ts";
import { exportProcessCameraModelToJSON } from "../kernel/process_camera/process_camera_export.ts";
import { buildProcessCameraHtml } from "../kernel/process_camera/process_camera_html.ts";
import { buildSearchCorpusFromProcessCameraModel } from "../kernel/search/search_corpus.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

const CREATED_AT = "2026-05-09T00:00:00.000Z";

function snapshot() {
  return buildCanonicalProcessSnapshot(CREATED_AT);
}

function model() {
  return buildProcessCameraModel(snapshot(), CREATED_AT);
}

// ── ProcessCameraModel — Grundstruktur ────────────────────────────────────────

describe("Ring 22D-H — ProcessCameraModel Grundstruktur", () => {
  it("model hat 16 Prozesskörper-Nodes", () => {
    assert.equal(model().nodes.length, 16);
  });

  it("model ist static", () => {
    assert.equal(model().is_static, true);
  });

  it("model ist read_only", () => {
    assert.equal(model().is_read_only, true);
  });

  it("model hat no_runtime true", () => {
    assert.equal(model().no_runtime, true);
  });

  it("model hat no_activation true", () => {
    assert.equal(model().no_activation, true);
  });

  it("model hat no_live_claims true", () => {
    assert.equal(model().no_live_claims, true);
  });

  it("model hat no_renderer true", () => {
    assert.equal(model().no_renderer, true);
  });

  it("model_version ist 1", () => {
    assert.equal(model().model_version, 1);
  });
});

// ── StatusSummary ─────────────────────────────────────────────────────────────

describe("Ring 22D-H — StatusSummary", () => {
  it("measured_count ist 0", () => {
    assert.equal(model().status_summary.measured_count, 0);
  });

  it("active_claim_count ist 0", () => {
    assert.equal(model().status_summary.active_claim_count, 0);
  });

  it("occupied_count ist 0", () => {
    assert.equal(model().status_summary.occupied_count, 0);
  });

  it("process_count ist 16", () => {
    assert.equal(model().status_summary.process_count, 16);
  });
});

// ── Layer-Zuordnung ───────────────────────────────────────────────────────────

describe("Ring 22D-H — Layer-Zuordnung", () => {
  it("GENI liegt in perception_layer", () => {
    const geni = model().nodes.find((n) => n.node_id === "geni");
    assert.ok(geni);
    assert.equal(geni.layer, "perception_layer");
  });

  it("dak+gord liegt in dialogue_core", () => {
    const dag = model().nodes.find((n) => n.node_id === "dak_gord_system");
    assert.ok(dag);
    assert.equal(dag.layer, "dialogue_core");
  });

  it("Systemweiser liegt in system_layers", () => {
    const sw = model().nodes.find((n) => n.node_id === "systemweiser");
    assert.ok(sw);
    assert.equal(sw.layer, "system_layers");
  });

  it("Search liegt in infrastructure_processes", () => {
    const s = model().nodes.find((n) => n.node_id === "search");
    assert.ok(s);
    assert.equal(s.layer, "infrastructure_processes");
  });

  it("Governance liegt in infrastructure_processes", () => {
    const g = model().nodes.find((n) => n.node_id === "governance");
    assert.ok(g);
    assert.equal(g.layer, "infrastructure_processes");
  });

  it("WorldRun liegt in infrastructure_processes", () => {
    const w = model().nodes.find((n) => n.node_id === "worldrun");
    assert.ok(w);
    assert.equal(w.layer, "infrastructure_processes");
  });

  it("Worldblick/Export liegt in infrastructure_processes", () => {
    const wb = model().nodes.find((n) => n.node_id === "worldblick_export");
    assert.ok(wb);
    assert.equal(wb.layer, "infrastructure_processes");
  });

  it("Reader-Platzhalter liegt in placeholders", () => {
    const r = model().nodes.find((n) => n.node_id === "reader_placeholder");
    assert.ok(r);
    assert.equal(r.layer, "placeholders");
  });

  it("Writer-Platzhalter liegt in placeholders", () => {
    const w = model().nodes.find((n) => n.node_id === "writer_placeholder");
    assert.ok(w);
    assert.equal(w.layer, "placeholders");
  });

  it("Runner-Platzhalter liegt in placeholders", () => {
    const r = model().nodes.find((n) => n.node_id === "runner_placeholder");
    assert.ok(r);
    assert.equal(r.layer, "placeholders");
  });
});

// ── D3-Slots / namelessAI ────────────────────────────────────────────────────

describe("Ring 22D-H — namelessAI D3-Slots", () => {
  it("genau 6 Nodes sind D3-Slots", () => {
    assert.equal(model().nodes.filter((n) => n.is_d3_slot).length, 6);
  });

  it("alle D3-Slots liegen in flarum_origin_slots", () => {
    assert.ok(
      model().nodes.filter((n) => n.is_d3_slot).every((n) => n.layer === "flarum_origin_slots")
    );
  });

  it("alle D3-Slots haben slot_state pre_einzug", () => {
    assert.ok(
      model().nodes.filter((n) => n.is_d3_slot).every((n) => n.slot_state === "pre_einzug")
    );
  });

  it("alle D3-Slots haben flarum_origin gesetzt", () => {
    assert.ok(
      model().nodes.filter((n) => n.is_d3_slot).every((n) => !!n.flarum_origin)
    );
  });

  it("kein D3-Slot ist besetzt (is_occupied false)", () => {
    assert.ok(
      model().nodes.filter((n) => n.is_d3_slot).every((n) => n.is_occupied === false)
    );
  });
});

// ── Alle Nodes: Schutzinvarianten ────────────────────────────────────────────

describe("Ring 22D-H — Schutzinvarianten aller Nodes", () => {
  it("kein Node ist gemessen (is_measured false für alle)", () => {
    assert.ok(model().nodes.every((n) => n.is_measured === false));
  });

  it("kein Node ist besetzt (is_occupied false für alle)", () => {
    assert.ok(model().nodes.every((n) => n.is_occupied === false));
  });

  it("kein Node hat status_kind measured", () => {
    assert.ok(model().nodes.every((n) => n.status_kind !== "measured"));
  });
});

// ── JSON Export ───────────────────────────────────────────────────────────────

describe("Ring 22D-H — JSON Export", () => {
  it("JSON Export ist deterministisch", () => {
    const m = model();
    assert.equal(exportProcessCameraModelToJSON(m), exportProcessCameraModelToJSON(m));
  });

  it("JSON enthält export_kind process_camera_model", () => {
    const json = exportProcessCameraModelToJSON(model());
    assert.ok(json.includes('"export_kind"'));
    assert.ok(json.includes("process_camera_model"));
  });

  it("JSON enthält is_static true", () => {
    const json = exportProcessCameraModelToJSON(model());
    assert.ok(json.includes('"is_static": true'));
  });

  it("JSON enthält no_runtime true", () => {
    const json = exportProcessCameraModelToJSON(model());
    assert.ok(json.includes('"no_runtime": true'));
  });
});

// ── HTML Export ───────────────────────────────────────────────────────────────

describe("Ring 22D-H — HTML Export", () => {
  it("HTML ist deterministisch", () => {
    const m = model();
    assert.equal(buildProcessCameraHtml(m), buildProcessCameraHtml(m));
  });

  it("HTML enthält GENI", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("GENI"));
  });

  it("HTML enthält dak+gord", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("dak+gord"));
  });

  it("HTML enthält namelessAI", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("namelessAI"));
  });

  it("HTML enthält Search", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("Search"));
  });

  it("HTML enthält Governance", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("Governance"));
  });

  it("HTML enthält WorldRun", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("WorldRun"));
  });

  it("HTML enthält Worldblick", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("Worldblick"));
  });

  it("HTML enthält Legende", () => {
    assert.ok(buildProcessCameraHtml(model()).includes("Legende"));
  });

  it("HTML enthält Schutzhinweis gegen Live-Zustände", () => {
    const html = buildProcessCameraHtml(model());
    assert.ok(html.includes("measured_count") || html.includes("kein Live"));
  });

  it("HTML enthält kein fetch", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("fetch("));
  });

  it("HTML enthält kein WebSocket", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("websocket"));
  });

  it("HTML enthält kein canvas", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("<canvas"));
  });

  it("HTML enthält kein three", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("three.js"));
  });

  it("HTML enthält kein react", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("react"));
  });

  it("HTML enthält kein vite", () => {
    assert.ok(!buildProcessCameraHtml(model()).toLowerCase().includes("vite"));
  });

  it("HTML enthält keine externe URL (http://)", () => {
    assert.ok(!buildProcessCameraHtml(model()).includes("http://"));
  });

  it("HTML enthält keine externe URL (https://)", () => {
    assert.ok(!buildProcessCameraHtml(model()).includes("https://"));
  });

  it("HTML beginnt mit DOCTYPE", () => {
    assert.ok(buildProcessCameraHtml(model()).startsWith("<!DOCTYPE html>"));
  });
});

// ── Search Integration ────────────────────────────────────────────────────────

describe("Ring 22D-H — Search Integration", () => {
  it("Corpus enthält 16 process_camera_node Dokumente", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const nodes = corpus.documents.filter((d) => d.kind === "process_camera_node");
    assert.equal(nodes.length, 16);
  });

  it("Corpus enthält process_camera_layer Dokumente", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const layers = corpus.documents.filter((d) => d.kind === "process_camera_layer");
    assert.ok(layers.length > 0);
  });

  it("Corpus enthält genau 1 process_camera_model Dokument", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const modelDocs = corpus.documents.filter((d) => d.kind === "process_camera_model");
    assert.equal(modelDocs.length, 1);
  });

  it("Search findet GENI CameraNode", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const geniDoc = corpus.documents.find(
      (d) => d.kind === "process_camera_node" && d.target_id === "geni"
    );
    assert.ok(geniDoc);
  });

  it("Search findet dak_gord_system CameraNode", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const doc = corpus.documents.find(
      (d) => d.kind === "process_camera_node" && d.target_id === "dak_gord_system"
    );
    assert.ok(doc);
  });

  it("D3-Slot-Nodes haben slot_id gesetzt", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    const slotDocs = corpus.documents.filter(
      (d) => d.kind === "process_camera_node" && d.slot_id !== null
    );
    assert.equal(slotDocs.length, 6);
  });

  it("corpus_version ist 1", () => {
    const corpus = buildSearchCorpusFromProcessCameraModel(model());
    assert.equal(corpus.corpus_version, 1);
  });
});

// ── ConceptGuard — neue Driftmuster ──────────────────────────────────────────

describe("Ring 22D-H — ConceptGuard neue Muster", () => {
  it("erkennt 'Prozesskamera beweist Live-Aktivität' als Drift", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Prozesskamera beweist Live-Aktivität im System" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Prozesskamera beweist Live-Aktivität"));
  });

  it("erkennt 'GENI ist ein normaler Knoten' als Drift", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "GENI ist ein normaler Knoten in der Weltkarte" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "GENI ist ein normaler Knoten"));
  });

  it("erkennt 'namelessAI ist eingezogen' als Drift", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "namelessAI ist eingezogen und aktiv" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "namelessAI ist eingezogen"));
  });

  it("erkennt 'atmosphärische Karte ist Innenwelt' als Drift", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Die atmosphärische Karte ist Innenwelt der Wesen" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "atmosphärische Karte ist Innenwelt"));
  });

  it("erkennt 'Platzhalter ist aktiver Runner' als Drift", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Platzhalter ist aktiver Runner im System" },
    ]);
    assert.equal(report.ok, false);
    assert.ok(report.violations.some((v) => v.term === "Platzhalter ist aktiver Runner"));
  });

  it("sauberer Text erzeugt keine Verletzungen", () => {
    const report = checkConceptLanguage([
      { id: "clean", text: "Der D3-Slot ist pre_einzug. GENI ist die Wahrnehmungsschicht. Atmosphäre aus Metadaten." },
    ]);
    assert.equal(report.ok, true);
  });
});

// ── Keine verbotenen Systeme ──────────────────────────────────────────────────

describe("Ring 22D-H — Keine verbotenen Systeme", () => {
  it("kein AI-Flag im Model", () => {
    const json = exportProcessCameraModelToJSON(model());
    assert.ok(!json.includes('"ai_active"'));
    assert.ok(!json.includes('"postgres"'));
    assert.ok(!json.includes('"scheduler"'));
    assert.ok(!json.includes('"daemon"'));
  });

  it("kein Renderer-Flag im Model", () => {
    const json = exportProcessCameraModelToJSON(model());
    assert.ok(!json.includes('"renderer"'));
  });
});
