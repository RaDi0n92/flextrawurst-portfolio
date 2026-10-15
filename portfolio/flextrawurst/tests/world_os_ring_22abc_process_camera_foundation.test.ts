import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  CANONICAL_PROCESS_BODIES,
  findProcessBodyById,
  getEntitySlotBodies,
  getPlaceholderBodies,
} from "../kernel/process_model/process_registry.ts";
import {
  buildTracesForBody,
  buildTracesForSnapshot,
} from "../kernel/process_model/process_trace_builder.ts";
import {
  buildProcessSnapshot,
  buildCanonicalProcessSnapshot,
} from "../kernel/process_model/process_snapshot.ts";
import { exportProcessSnapshotToJSON } from "../kernel/process_model/process_export.ts";
import { buildSearchCorpusFromProcessSnapshot } from "../kernel/search/search_corpus.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

// ── Registry ─────────────────────────────────────────────────────────────────

describe("Ring 22ABC — Registry", () => {
  it("contains exactly 16 canonical process bodies (14 named + reader/writer/runner)", () => {
    assert.equal(CANONICAL_PROCESS_BODIES.length, 16);
  });

  it("all bodies have is_canonical = true", () => {
    assert.ok(CANONICAL_PROCESS_BODIES.every((b) => b.is_canonical === true));
  });

  it("GENI body exists with kind perception_layer", () => {
    const geni = findProcessBodyById("geni");
    assert.ok(geni);
    assert.equal(geni.kind, "perception_layer");
  });

  it("dak+gord body exists with kind dialogue_core", () => {
    const dag = findProcessBodyById("dak_gord_system");
    assert.ok(dag);
    assert.equal(dag.kind, "dialogue_core");
  });

  it("entity_slot bodies are exactly 6 (namelessAI Flarum-Wesen)", () => {
    assert.equal(getEntitySlotBodies().length, 6);
  });

  it("all entity_slot bodies have slot_state = pre_einzug", () => {
    assert.ok(getEntitySlotBodies().every((b) => b.slot_state === "pre_einzug"));
  });

  it("no entity_slot body has slot_state = einzug_vollzogen", () => {
    assert.ok(getEntitySlotBodies().every((b) => b.slot_state !== "einzug_vollzogen"));
  });

  it("all entity_slot bodies have forum_ref set", () => {
    assert.ok(getEntitySlotBodies().every((b) => typeof b.forum_ref === "string"));
  });

  it("all placeholder bodies have status = future", () => {
    assert.ok(getPlaceholderBodies().every((b) => b.status === "future"));
  });

  it("no body has visibility.evidence = measured", () => {
    assert.ok(CANONICAL_PROCESS_BODIES.every((b) => b.visibility.evidence !== "measured"));
  });
});

// ── Snapshot ──────────────────────────────────────────────────────────────────

describe("Ring 22ABC — Snapshot", () => {
  const snapshot = buildCanonicalProcessSnapshot("2026-05-09T00:00:00.000Z");

  it("is_read_only = true", () => {
    assert.equal(snapshot.is_read_only, true);
  });

  it("is_static = true", () => {
    assert.equal(snapshot.is_static, true);
  });

  it("active_claim_count = 0", () => {
    assert.equal(snapshot.active_claim_count, 0);
  });

  it("measured_count = 0", () => {
    assert.equal(snapshot.measured_count, 0);
  });

  it("process_count = 16", () => {
    assert.equal(snapshot.process_count, 16);
  });

  it("process_bodies length = 16", () => {
    assert.equal(snapshot.process_bodies.length, 16);
  });

  it("derived + modelled + unknown + blocked + read_only + replay = process_count", () => {
    const total =
      snapshot.derived_count +
      snapshot.modelled_count +
      snapshot.blocked_count +
      snapshot.read_only_count +
      snapshot.replay_count +
      snapshot.unknown_count;
    assert.equal(total, snapshot.process_count);
  });

  it("buildProcessSnapshot throws if body has measured evidence", () => {
    const bogus = {
      ...CANONICAL_PROCESS_BODIES[0],
      visibility: { evidence: "measured" as const },
    };
    assert.throws(() => buildProcessSnapshot([bogus]));
  });
});

// ── Export ────────────────────────────────────────────────────────────────────

describe("Ring 22ABC — Export", () => {
  const snapshot = buildCanonicalProcessSnapshot("2026-05-09T00:00:00.000Z");
  const json = exportProcessSnapshotToJSON(snapshot);

  it("returns a non-empty string", () => {
    assert.ok(json.length > 0);
  });

  it("is valid JSON", () => {
    assert.doesNotThrow(() => JSON.parse(json));
  });

  it("parsed export has process_count = 16", () => {
    const parsed = JSON.parse(json);
    assert.equal(parsed.process_count, 16);
  });

  it("parsed export has active_claim_count = 0", () => {
    const parsed = JSON.parse(json);
    assert.equal(parsed.active_claim_count, 0);
  });

  it("export is deterministic", () => {
    const s2 = buildCanonicalProcessSnapshot("2026-05-09T00:00:00.000Z");
    assert.equal(exportProcessSnapshotToJSON(s2), json);
  });
});

// ── Trace Builder ─────────────────────────────────────────────────────────────

describe("Ring 22ABC — Trace Builder", () => {
  it("entity_slot body produces a forum trace", () => {
    const slot = getEntitySlotBodies()[0];
    const traces = buildTracesForBody(slot);
    assert.ok(traces.some((t) => t.trace_type === "forum"));
  });

  it("system_layer body with file_ref produces a file trace", () => {
    const search = findProcessBodyById("search")!;
    const traces = buildTracesForBody(search);
    assert.ok(traces.some((t) => t.trace_type === "file"));
  });

  it("all traces reference a known body_id", () => {
    const enriched = buildTracesForSnapshot(CANONICAL_PROCESS_BODIES);
    const knownIds = new Set(CANONICAL_PROCESS_BODIES.map((b) => b.id));
    for (const body of enriched) {
      for (const trace of body.traces) {
        assert.ok(knownIds.has(trace.body_id), `Unknown body_id in trace: ${trace.body_id}`);
      }
    }
  });

  it("no trace claims evidence = measured", () => {
    const enriched = buildTracesForSnapshot(CANONICAL_PROCESS_BODIES);
    for (const body of enriched) {
      for (const trace of body.traces) {
        assert.notEqual(trace.source_type, "measured");
      }
    }
  });
});

// ── Search ────────────────────────────────────────────────────────────────────

describe("Ring 22ABC — Search", () => {
  const snapshot = buildCanonicalProcessSnapshot("2026-05-09T00:00:00.000Z");
  const corpus = buildSearchCorpusFromProcessSnapshot(snapshot);

  it("corpus contains process_body documents", () => {
    assert.ok(corpus.documents.some((d) => d.kind === "process_body"));
  });

  it("corpus contains exactly 16 process_body documents", () => {
    assert.equal(corpus.documents.filter((d) => d.kind === "process_body").length, 16);
  });

  it("corpus contains exactly 1 process_snapshot document", () => {
    assert.equal(corpus.documents.filter((d) => d.kind === "process_snapshot").length, 1);
  });

  it("process_body document for geni has target_id = geni", () => {
    const doc = corpus.documents.find((d) => d.kind === "process_body" && d.target_id === "geni");
    assert.ok(doc);
  });
});

// ── ConceptGuard ──────────────────────────────────────────────────────────────

describe("Ring 22ABC — ConceptGuard", () => {
  it("detects: Prozesskamera ist Live-Dashboard", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Prozesskamera ist Live-Dashboard" },
    ]);
    assert.equal(report.ok, false);
  });

  it("detects: Prozesskörper ist eingezogenes Wesen", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Prozesskörper ist eingezogenes Wesen" },
    ]);
    assert.equal(report.ok, false);
  });

  it("detects: read-only Spur ist echte Aktivität", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "read-only Spur ist echte Aktivität" },
    ]);
    assert.equal(report.ok, false);
  });

  it("detects: Atmosphäre beweist Innenwelt", () => {
    const report = checkConceptLanguage([
      { id: "test", text: "Atmosphäre beweist Innenwelt" },
    ]);
    assert.equal(report.ok, false);
  });
});
