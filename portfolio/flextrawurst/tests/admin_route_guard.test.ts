import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { requiresAdministrativeAuth as needs, permitsAdministrativeOrigin as origin, administrativeAuthStatus, withAdministrativeClient } from "../scripts/admin_route_guard.ts";

test("all administrative mutation families, including query variants, require auth", () => {
  for (const path of ["/wesen/save", "/wesen/solarius/synthetic/memory", "/wesen/solarius/synthetic/files/a.md", "/wesen/solarius/synthetic/soft-delete", "/wesen/solarius/synthetic/url-lesen", "/api/wesen-dienst-wizard/ausloesen", "/api/wesen-dienst-wizard/container/synthetic/notes/admin-eintrag/a.md", "/api/flarumstyler/action", "/dolphin/session/synthetic/delete", "/aufgabenchats/synthetic/starten"]) {
    for (const method of ["POST", "PUT", "PATCH", "DELETE"]) {
      assert.equal(needs(path, method), true, `${method} ${path}`);
      assert.equal(needs(path + "?x=1", method), true);
    }
  }
});

test("public reads and unrelated platform routes remain unchanged", () => {
  for (const path of ["/", "/wesen/", "/wesen/solarius/synthetic/data", "/api/wesen-dienst-wizard/wesen-liste", "/dolphin/sessions"]) {
    for (const method of ["GET", "HEAD", "OPTIONS"]) assert.equal(needs(path, method), false);
  }
  assert.equal(needs("/api/auth/login", "POST"), false);
  assert.equal(needs("/wesen-other/save", "POST"), false);
  assert.equal(needs("/verwaltung-anmelden?x=1", "GET"), false);
});

test("rejects foreign, opaque, malformed and sibling-site browser origins", () => {
  for (const value of ["https://foreign.example", "null", "not a URL", "https://site.example/path"]) {
    assert.equal(origin({ host: "site.example", origin: value }), false);
  }
  assert.equal(origin({host: "site.example", origin: "https://site.example", "sec-fetch-site": "cross-site"}), false);
  assert.equal(origin({host: "site.example", "sec-fetch-site": "same-site"}), false);
});

test("allows same-origin browsers and explicit non-browser authentication path", () => {
  assert.equal(origin({host: "site.example", origin: "https://site.example", "sec-fetch-site": "same-origin"}), true);
  assert.equal(origin({host: "127.0.0.1:8787"}), true);
  assert.equal(needs("/wesen/save", "POST"), true); // no local-address auth bypass
});

test("server integrates guard and authentication before route dispatch", () => {
  const text = readFileSync(new URL("../scripts/serve_process_camera_preview.ts", import.meta.url), "utf8");
  const start = text.indexOf("export function startServer(");
  const guard = text.indexOf("const adminAccess = requiresAdministrativeAuth", start);
  const auth = text.indexOf("await administrativeAuthStatus(req.headers)", guard);
  const dispatch = text.indexOf('if (url === "/werkraum-write"', start);
  assert.ok(start < guard && guard < auth && auth < dispatch);
});

test("Bearer verification fails closed, without Basic fallback or stale role trust", async () => {
  for (const header of [undefined, "Basic synthetic", "Bearer "]) {
    assert.equal(await administrativeAuthStatus({authorization: header}, async () => { throw Error("must not call"); }), 401);
  }
  for (const [upstream, expected] of [[200,200],[401,401],[403,403],[404,503],[500,503]]) {
    const verifier: typeof fetch = async (url, init) => {
      assert.equal(url, "http://127.0.0.1:8030/auth/admin-check");
      assert.equal(new Headers(init?.headers).get("Authorization"), "Bearer synthetic");
      assert.equal(init?.redirect, "error");
      return new Response('{"ok":true}', {status:upstream});
    };
    assert.equal(await administrativeAuthStatus({authorization:"Bearer synthetic"}, verifier), expected);
  }
  assert.equal(await administrativeAuthStatus({authorization:"Bearer synthetic"}, async () => {throw Error("offline");}), 503);
  assert.equal(await administrativeAuthStatus({authorization:"Bearer synthetic"}, async () => new Response('{"ok":false}')), 503);
});

test("HTML injection adds only a fixed helper, retaining original content", () => {
  assert.equal(withAdministrativeClient('<html><head><title>A</title></head>'), '<html><head><script src="/admin-auth-client.js"></script><title>A</title></head>');
});

test("existing private Flarumstyler reads stay protected during proxy migration", () => {
  for (const path of ["/api/flarumstyler", "/api/flarumstyler_verlauf", "/api/flarumstyler/status"]) {
    for (const method of ["GET", "HEAD", "POST", "DELETE"]) assert.equal(needs(path, method), true);
    assert.equal(needs(path, "OPTIONS"), false);
  }
});
