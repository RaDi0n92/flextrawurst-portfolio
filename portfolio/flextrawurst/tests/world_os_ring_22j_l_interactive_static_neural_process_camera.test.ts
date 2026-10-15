import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { buildCanonicalProcessSnapshot } from "../kernel/process_model/process_snapshot.ts";
import { buildProcessCameraModel } from "../kernel/process_camera/process_camera_builder.ts";
import { exportProcessCameraModelToJSON } from "../kernel/process_camera/process_camera_export.ts";
import { buildProcessCameraInteractiveHtml } from "../kernel/process_camera/process_camera_interactive_html.ts";
import { PROCESS_CAMERA_LAYOUT, getNodeLayout } from "../kernel/process_camera/process_camera_layout.ts";

const CREATED_AT = "2026-05-09T00:00:00.000Z";

function snapshot() { return buildCanonicalProcessSnapshot(CREATED_AT); }
function model()    { return buildProcessCameraModel(snapshot(), CREATED_AT); }
function html()     { return buildProcessCameraInteractiveHtml(model(), PROCESS_CAMERA_LAYOUT); }

// ── SVG-Struktur ──────────────────────────────────────────────────────────────

describe("Ring 22J-L — SVG-Struktur", () => {
  it("HTML enthält <svg", () => {
    assert.ok(html().includes("<svg"));
  });

  it("HTML enthält <g id=\"world\"", () => {
    assert.ok(html().includes('id="world"'));
  });

  it("HTML enthält Kanten-Elemente", () => {
    assert.ok(html().includes('class="edge"'));
  });

  it("HTML enthält Node-Elemente", () => {
    assert.ok(html().includes('class="node-g"'));
  });

  it("HTML enthält GENI-Feld als Ellipse", () => {
    assert.ok(html().includes("geni-field-group"));
  });
});

// ── Interaktivitäts-Controls ──────────────────────────────────────────────────

describe("Ring 22J-L — Interaktivitäts-Controls", () => {
  it("HTML enthält Suchfeld (search-input)", () => {
    assert.ok(html().includes('id="search-input"'));
  });

  it("HTML enthält Reset-View Button", () => {
    assert.ok(html().includes('id="reset-btn"'));
  });

  it("HTML enthält Layer-Toggle-Buttons", () => {
    assert.ok(html().includes('class="layer-btn active"'));
  });

  it("HTML enthält Fokus-Buttons", () => {
    assert.ok(html().includes('class="focus-btn"'));
  });

  it("HTML enthält Detailpanel", () => {
    assert.ok(html().includes('id="detail-panel"'));
  });

  it("HTML enthält Detailpanel-Inhalt-Container", () => {
    assert.ok(html().includes('id="detail-content"'));
  });
});

// ── Zoom/Pan JavaScript ───────────────────────────────────────────────────────

describe("Ring 22J-L — Zoom/Pan JavaScript", () => {
  it("HTML enthält wheel-Event-Handler (Zoom)", () => {
    assert.ok(html().includes("addEventListener('wheel'"));
  });

  it("HTML enthält mousedown-Handler (Pan)", () => {
    assert.ok(html().includes("addEventListener('mousedown'"));
  });

  it("HTML enthält resetView-Funktion", () => {
    assert.ok(html().includes("function resetView()"));
  });

  it("HTML enthält animateTo-Funktion", () => {
    assert.ok(html().includes("function animateTo("));
  });

  it("HTML enthält applyTransform-Funktion", () => {
    assert.ok(html().includes("function applyTransform()"));
  });
});

// ── Node-Vollständigkeit ──────────────────────────────────────────────────────

describe("Ring 22J-L — Node-Vollständigkeit", () => {
  it("alle 16 Prozesskörper sind als node_id im HTML", () => {
    const h = html();
    const nodeIds = model().nodes.map((n) => n.node_id);
    assert.equal(nodeIds.length, 16);
    for (const id of nodeIds) {
      assert.ok(h.includes(id), `node_id "${id}" fehlt im HTML`);
    }
  });

  it("GENI ist als Wahrnehmungsschicht / perception field markiert", () => {
    assert.ok(html().includes("Wahrnehmungsschicht"));
  });

  it("dak+gord ist als Koordinationskern erkennbar", () => {
    assert.ok(html().includes("dak_gord_system"));
  });

  it("namelessAI-Slots haben D3-Markierung", () => {
    assert.ok(html().includes("[D3]"));
  });

  it("Slot-State pre_einzug ist in Node-Daten eingebettet", () => {
    assert.ok(html().includes("pre_einzug"));
  });
});

// ── Schutzsatz und Sicherheit ─────────────────────────────────────────────────

describe("Ring 22J-L — Schutzsatz und Sicherheit", () => {
  it("HTML enthält Schutzsatz gegen Live-Behauptung", () => {
    assert.ok(html().includes("Keine Live-Aktivit"));
  });

  it("HTML enthält Schutzsatz gegen Einzug", () => {
    assert.ok(html().includes("Kein Einzug"));
  });

  it("HTML enthält keine fetch-Aufrufe", () => {
    assert.ok(!html().includes("fetch("));
  });

  it("HTML enthält kein WebSocket", () => {
    assert.ok(!html().includes("WebSocket"));
  });

  it("HTML enthält keine externen Script-Src", () => {
    assert.ok(!html().match(/<script[^>]+src=/));
  });

  it("HTML enthält kein React-Import", () => {
    assert.ok(!html().includes("react"));
  });

  it("HTML enthält kein Three.js-Import", () => {
    assert.ok(!html().includes("three"));
  });
});

// ── Layout ────────────────────────────────────────────────────────────────────

describe("Ring 22J-L — Layout", () => {
  it("Layout hat 16 Node-Einträge (incl. GENI-Feld)", () => {
    assert.equal(PROCESS_CAMERA_LAYOUT.nodes.length, 16);
  });

  it("GENI ist als is_field markiert", () => {
    const geni = PROCESS_CAMERA_LAYOUT.nodes.find((n) => n.node_id === "geni");
    assert.equal(geni?.is_field, true);
  });

  it("dak_gord_system hat größten Radius (Koordinationskern)", () => {
    const dak = getNodeLayout("dak_gord_system");
    const others = PROCESS_CAMERA_LAYOUT.nodes.filter((n) => !n.is_field && n.node_id !== "dak_gord_system");
    assert.ok(dak && others.every((n) => dak.r >= n.r));
  });

  it("Kanten-Definitionen enthalten perception_edge", () => {
    assert.ok(PROCESS_CAMERA_LAYOUT.edges.some((e) => e.edge_type === "perception_edge"));
  });

  it("Kanten-Definitionen enthalten provenance_edge", () => {
    assert.ok(PROCESS_CAMERA_LAYOUT.edges.some((e) => e.edge_type === "provenance_edge"));
  });
});

// ── Determinismus ─────────────────────────────────────────────────────────────

describe("Ring 22J-L — Determinismus", () => {
  it("HTML ist deterministisch (zwei Aufrufe identisch)", () => {
    assert.equal(html(), html());
  });

  it("JSON ist deterministisch", () => {
    const m = model();
    assert.equal(exportProcessCameraModelToJSON(m), exportProcessCameraModelToJSON(m));
  });
});
