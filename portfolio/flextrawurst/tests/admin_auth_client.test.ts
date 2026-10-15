import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

function setup() {
  const calls: any[] = [];
  const ctx = {
    window: { location: {href:"https://site.example/solarius/synthetic", origin:"https://site.example"},
      fetch: async (input: any, init: any) => { calls.push({input, init}); return new Response("{}"); } },
    localStorage: {getItem: () => "synthetic-token" as string | null},
    URL, Request, Response, Headers, document: {body: null},
  };
  vm.runInNewContext(readFileSync(new URL("../scripts/admin_auth_client.js", import.meta.url), "utf8"), ctx);
  return {ctx, calls};
}

test("existing platform login authenticates writes without changing body", async () => {
  const {ctx, calls} = setup();
  await ctx.window.fetch("/wesen/save", {method:"POST", body:"{}"});
  assert.equal(calls[0].init.headers.get("Authorization"), "Bearer synthetic-token");
  assert.equal(calls[0].init.body, "{}");
  assert.equal(calls[0].init.redirect, "error");
});

test("no token is added to external origins or public reads; logout takes effect", async () => {
  const {ctx, calls} = setup();
  await ctx.window.fetch("https://external.example/wesen/save", {method:"POST"});
  assert.equal(calls[0].init.headers, undefined);
  await ctx.window.fetch("/wesen/solarius/synthetic/data", undefined);
  assert.equal(calls[1].init, undefined);
  ctx.localStorage.getItem = () => null;
  await ctx.window.fetch("/wesen/save", {method:"POST"});
  assert.equal(calls[2].init.headers.has("Authorization"), false);
});

test("explicit Request credentials retained; private Flarumstyler reads get token", async () => {
  const {ctx, calls} = setup();
  await ctx.window.fetch(new Request("https://site.example/wesen/save", {method:"POST", body:"{}", headers:{Authorization:"Bearer explicit"}}), undefined);
  assert.equal(calls[0].init.headers.get("Authorization"), "Bearer explicit");
  await ctx.window.fetch("/api/flarumstyler_verlauf", undefined);
  assert.equal(calls[1].init.headers.get("Authorization"), "Bearer synthetic-token");
});
