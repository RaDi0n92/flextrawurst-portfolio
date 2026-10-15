import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  isSafePath,
  getContentType,
  buildIndexHtml,
  SERVE_ROOT,
} from "../scripts/serve_process_camera_preview.ts";

const PKG = JSON.parse(readFileSync(resolve("package.json"), "utf-8"));
const SERVE_SCRIPT = readFileSync(resolve("scripts/serve_process_camera_preview.ts"), "utf-8");

// ── Pfadsicherheit ────────────────────────────────────────────────────────────

describe("Ring 22I — Pfadsicherheit", () => {
  it("erlaubt /process_camera_worldblick.html", () => {
    assert.equal(isSafePath("/process_camera_worldblick.html"), true);
  });

  it("erlaubt /process_camera_model.json", () => {
    assert.equal(isSafePath("/process_camera_model.json"), true);
  });

  it("blockiert Directory Traversal /../../../etc/passwd", () => {
    assert.equal(isSafePath("/../../../etc/passwd"), false);
  });

  it("blockiert Directory Traversal /../../", () => {
    assert.equal(isSafePath("/../../"), false);
  });

  it("blockiert /.. allein", () => {
    assert.equal(isSafePath("/.."), false);
  });
});

// ── Content-Type ──────────────────────────────────────────────────────────────

describe("Ring 22I — Content-Type", () => {
  it("HTML-Route liefert text/html", () => {
    assert.ok(getContentType("/process_camera_worldblick.html")?.includes("text/html"));
  });

  it("JSON-Route liefert application/json", () => {
    assert.ok(getContentType("/process_camera_model.json")?.includes("application/json"));
  });

  it(".css-Route liefert null", () => {
    assert.equal(getContentType("/style.css"), null);
  });

  it("Root-Route / liefert null (wird separat behandelt)", () => {
    assert.equal(getContentType("/"), null);
  });

  it("neue HTML-Dateien werden akzeptiert (extension-based)", () => {
    assert.ok(getContentType("/kompOase_vorform.html")?.includes("text/html"));
  });
});

// ── Index-Seite ───────────────────────────────────────────────────────────────

describe("Ring 22I — Index-Seite", () => {
  it("enthält Link zu worldblick.html", () => {
    assert.ok(buildIndexHtml().includes("process_camera_worldblick.html"));
  });

  it("enthält Link zu model.json", () => {
    assert.ok(buildIndexHtml().includes("process_camera_model.json"));
  });

  it("enthält Link zu kompOase_vorform.html", () => {
    assert.ok(buildIndexHtml().includes("kompOase_vorform.html"));
  });
});

// ── package.json Scripts ──────────────────────────────────────────────────────

describe("Ring 22I — package.json Scripts", () => {
  it("process-camera:serve Script existiert", () => {
    assert.ok("process-camera:serve" in PKG.scripts);
  });

  it("process-camera:preview Script existiert", () => {
    assert.ok("process-camera:preview" in PKG.scripts);
  });

  it("bestehendes process-camera Script bleibt erhalten", () => {
    assert.ok("process-camera" in PKG.scripts);
  });
});

// ── Kein Daemon-Verhalten ─────────────────────────────────────────────────────

describe("Ring 22I — Kein Daemon-Verhalten", () => {
  it("kein setInterval im Server-Skript", () => {
    assert.ok(!SERVE_SCRIPT.includes("setInterval"));
  });

  it("kein WebSocket-Import im Server-Skript", () => {
    assert.ok(!SERVE_SCRIPT.includes("WebSocket"));
  });

  it("kein fetch-Aufruf im Server-Skript", () => {
    assert.ok(!SERVE_SCRIPT.includes("fetch("));
  });

  it("keine externen Imports im Server-Skript (nur node:)", () => {
    const imports = SERVE_SCRIPT.match(/from ["']([^"']+)["']/g) ?? [];
    const external = imports.filter(
      (i) => !i.includes("node:") && !i.includes("./") && !i.includes("../")
    );
    assert.equal(external.length, 0);
  });
});
