import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import {
  getInventory,
  getInventorySummary,
  getByStatus,
  getByBauort,
} from "../kernel/surface/feature_idea_inventory.ts";

const INVENTORY_MD = "docs/43_FLEXTRAWURST_FEATURE_IDEA_INVENTORY.md";
const HTML_PATH = "out/surface/flextrawurst_surface.html";

describe("Feature Idea Inventory — Kernel", () => {
  it("Inventar hat 490 Einträge", () => {
    assert.equal(getInventory().length, 490);
  });

  it("alle IDs sind eindeutig", () => {
    const ids = getInventory().map(i => i.id);
    const unique = new Set(ids);
    assert.equal(unique.size, ids.length, "Doppelte IDs gefunden");
  });

  it("alle list_number-Werte im Bereich 1–490", () => {
    for (const item of getInventory()) {
      assert.ok(item.list_number >= 1 && item.list_number <= 490, `Ungültige Nummer: ${item.list_number}`);
    }
  });

  it("core_surface-Einträge sind vorhanden und plausibel", () => {
    const core = getByStatus("core_surface");
    assert.ok(core.length >= 40, `Zu wenige core_surface: ${core.length}`);
  });

  it("visible_slot-Einträge decken alle bekannten Organ-Slots ab", () => {
    const slots = getByStatus("visible_slot");
    assert.ok(slots.length >= 20, `Zu wenige visible_slots: ${slots.length}`);
  });

  it("hidden_blueprint-Einträge vorhanden für Governance/Admin", () => {
    const bp = getByStatus("hidden_blueprint");
    assert.ok(bp.length >= 40, `Zu wenige hidden_blueprints: ${bp.length}`);
  });

  it("getByBauort('O') liefert Organ-Slot-Einträge", () => {
    const organItems = getByBauort("O");
    assert.ok(organItems.length >= 20, `Zu wenige Organ-Bauort-Einträge: ${organItems.length}`);
  });

  it("Zusammenfassung ergibt 490 gesamt", () => {
    const summary = getInventorySummary();
    const total = Object.values(summary).reduce((a, b) => a + b, 0);
    assert.equal(total, 490);
  });
});

describe("Feature Idea Inventory — Markdown", () => {
  it("docs/43_FLEXTRAWURST_FEATURE_IDEA_INVENTORY.md existiert", () => {
    assert.ok(existsSync(INVENTORY_MD), `${INVENTORY_MD} nicht gefunden`);
  });

  it("Markdown enthält Status-Legende", () => {
    const md = readFileSync(INVENTORY_MD, "utf-8");
    assert.ok(md.includes("core_surface"), "core_surface fehlt");
    assert.ok(md.includes("visible_slot"), "visible_slot fehlt");
    assert.ok(md.includes("hidden_blueprint"), "hidden_blueprint fehlt");
    assert.ok(md.includes("blocked_until_concept"), "blocked_until_concept fehlt");
  });

  it("Markdown enthält alle 31 Themengruppen-Sections", () => {
    const md = readFileSync(INVENTORY_MD, "utf-8");
    assert.ok(md.includes("## 1 ·"), "Sektion 1 fehlt");
    assert.ok(md.includes("## 31 ·"), "Sektion 31 fehlt");
    assert.ok(md.includes("Saatgut"), "Saatgut-Hinweis fehlt");
  });

  it("Markdown enthält FW-IDs für Schlüssel-Einträge", () => {
    const md = readFileSync(INVENTORY_MD, "utf-8");
    assert.ok(md.includes("FW-001"), "FW-001 fehlt");
    assert.ok(md.includes("FW-490"), "FW-490 fehlt");
    assert.ok(md.includes("FW-178"), "FW-178 (METAWAR) fehlt");
    assert.ok(md.includes("FW-157"), "FW-157 (Tamagotchi) fehlt");
  });
});

describe("Feature Idea Inventory — Surface HTML", () => {
  it("HTML enthält WISSEN-View und Admin-Inventar", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("view-wissen"), "view-wissen fehlt");
    assert.ok(html.includes("Inventar-Themen"), "Inventar-Themen im Admin-View fehlt");
  });

  it("HTML zeigt 490 Einträge im Admin-View", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Einträge gesamt") && html.includes(">490<"), "490-Zähler im Admin-View fehlt");
  });
});
