import { describe, it } from "node:test";
import assert from "node:assert/strict";

import { buildKompOaseVorformHtml } from "../kernel/landscape/kompOase_landscape_html.ts";

function html() { return buildKompOaseVorformHtml(); }

// ── SVG-Struktur ──────────────────────────────────────────────────────────────

describe("Ring 22M — SVG-Struktur", () => {
  it("HTML enthält <svg", () => {
    assert.ok(html().includes("<svg"));
  });

  it("HTML enthält Terrain-Layer (far-mountains)", () => {
    assert.ok(html().includes('id="far-mountains"'));
  });

  it("HTML enthält Sterne (layer-stars)", () => {
    assert.ok(html().includes('id="layer-stars"'));
  });

  it("HTML enthält GENI-Gitternetz (layer-geni)", () => {
    assert.ok(html().includes('id="layer-geni"'));
  });

  it("HTML enthält namelessAI-Layer", () => {
    assert.ok(html().includes('id="layer-nameless"'));
  });

  it("HTML enthält Lava-Zone", () => {
    assert.ok(html().includes("lava-g"));
  });

  it("HTML enthält Wasser-Zone", () => {
    assert.ok(html().includes("water-g"));
  });

  it("HTML enthält Splitterfeld", () => {
    assert.ok(html().includes('id="layer-splitter"'));
  });

  it("HTML enthält Pflanzen-Layer", () => {
    assert.ok(html().includes('id="layer-plants"'));
  });
});

// ── GENI-Grid LOD ─────────────────────────────────────────────────────────────

describe("Ring 22M — GENI-Grid LOD", () => {
  it("GENI-Grid hat drei Ebenen (gg1r, gg2r, gg3r)", () => {
    const h = html();
    assert.ok(h.includes('id="gg1r"'));
    assert.ok(h.includes('id="gg2r"'));
    assert.ok(h.includes('id="gg3r"'));
  });

  it("GENI-Grid-Patterns sind definiert", () => {
    assert.ok(html().includes('id="gg1"'));
  });

  it("updateGeniGrid-Funktion vorhanden", () => {
    assert.ok(html().includes("function updateGeniGrid("));
  });
});

// ── namelessAI ────────────────────────────────────────────────────────────────

describe("Ring 22M — namelessAI-Knoten", () => {
  it("alle 6 namelessAI-IDs sind im HTML", () => {
    const h = html();
    const ids = ['Schorschel','Resonanzknoten','F3INSCHM3CK3R','träumerlie','R1ZZ1','jumpa'];
    for (const id of ids) assert.ok(h.includes(id), `${id} fehlt`);
  });

  it("D3-Slot-Markierung vorhanden", () => {
    assert.ok(html().includes("[D3]"));
  });

  it("pre_einzug-Status vorhanden", () => {
    assert.ok(html().includes("pre_einzug"));
  });

  it("Flarum-Archiv-Ursprungsknoten vorhanden", () => {
    assert.ok(html().includes("Flarum-Archiv"));
  });

  it("Flarum-Herkunft hat echte Quellenangabe", () => {
    assert.ok(html().includes("kernel/process_model/process_registry.ts"));
  });
});

// ── Interaktion ───────────────────────────────────────────────────────────────

describe("Ring 22M — Interaktion", () => {
  it("Mausrad-Zoom (wheel-Handler) vorhanden", () => {
    assert.ok(html().includes("addEventListener('wheel'"));
  });

  it("Drag-Pan (mousedown-Handler) vorhanden", () => {
    assert.ok(html().includes("addEventListener('mousedown'"));
  });

  it("Zoom-Schieberegler vorhanden", () => {
    assert.ok(html().includes('id="zoom-slider"'));
  });

  it("Location-Popup vorhanden", () => {
    assert.ok(html().includes('id="loc-popup"'));
  });

  it("applyTransform-Funktion vorhanden", () => {
    assert.ok(html().includes("function applyTransform()"));
  });

  it("flyTo-Funktion vorhanden", () => {
    assert.ok(html().includes("function flyTo("));
  });
});

// ── dak+gord Panel ───────────────────────────────────────────────────────────

describe("Ring 22M — dak+gord Panel", () => {
  it("dak+gord-Panel vorhanden", () => {
    assert.ok(html().includes('id="dak-panel"'));
  });

  it("dak+gord als Obsidian-Navigator markiert", () => {
    assert.ok(html().includes("Obsidian-Navigator"));
  });

  it("Einzug-Status (0 besetzt) sichtbar", () => {
    assert.ok(html().includes("0 / 6 besetzt"));
  });
});

// ── Schutzsatz / Ehrlichkeit ──────────────────────────────────────────────────

describe("Ring 22M — Schutzsatz", () => {
  it("Atmosphäre-Markierung in Zone-Daten vorhanden", () => {
    assert.ok(html().includes("atmosphärisch modelliert") || html().includes("Atmosphärisch modelliert"));
  });

  it("kein fetch", () => {
    assert.ok(!html().includes("fetch("));
  });

  it("kein WebSocket", () => {
    assert.ok(!html().includes("WebSocket"));
  });

  it("keine externen Script-Src", () => {
    assert.ok(!html().match(/<script[^>]+src=/));
  });

  it("kein React", () => {
    assert.ok(!html().includes("react"));
  });

  it("static:true im HTML-Kommentar", () => {
    assert.ok(html().includes("static:true"));
  });
});

// ── Determinismus ─────────────────────────────────────────────────────────────

describe("Ring 22M — Determinismus", () => {
  it("HTML ist deterministisch", () => {
    assert.equal(html(), html());
  });
});
