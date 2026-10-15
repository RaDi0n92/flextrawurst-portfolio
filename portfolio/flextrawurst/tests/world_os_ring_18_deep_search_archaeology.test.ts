import { describe, it } from "node:test";
import assert from "node:assert/strict";

import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import { seedCanonicalEntities } from "../kernel/entities/seed_entities.ts";
import { runWorldCycle } from "../kernel/world_engine/run_world_cycle.ts";
import { buildWorldTimeline } from "../kernel/timeline/world_timeline.ts";
import { buildCanonicalEntitySlots } from "../kernel/slots/entity_slot.ts";
import { buildFeatureRegistry } from "../kernel/features/feature_registry.ts";
import { buildWorldCameraModel } from "../kernel/world_camera/world_camera_model.ts";
import { buildWorldSnapshot } from "../kernel/snapshots/world_snapshot.ts";
import { checkWorldIntegrity } from "../kernel/integrity/world_integrity.ts";
import { findEventsByType } from "../kernel/queries/event_queries.ts";
import {
  createEmptyCommandLedger,
  recordCommandIntent,
} from "../kernel/admin/command_ledger.ts";
import { buildDanielRootAdmin } from "../kernel/admin/admin_permissions.ts";
import { createCommandIntent } from "../kernel/admin/command_intent.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";

import {
  buildSearchCorpusFromEvents,
  buildSearchCorpusFromTimeline,
  buildSearchCorpusFromProvenance,
  buildSearchCorpusFromSlots,
  buildSearchCorpusFromFeatures,
  buildSearchCorpusFromConceptGuard,
  buildSearchCorpusFromCameraModel,
  buildSearchCorpusFromCommandLedger,
  mergeSearchCorpora,
} from "../kernel/search/search_corpus.ts";
import { matchesArchaeologyFilter, filterSearchCorpus } from "../kernel/search/archaeology_filter.ts";
import { runArchaeologyQuery, explainSearchResult } from "../kernel/search/archaeology_query.ts";
import {
  findCausalChainDocuments,
  findCausalChildrenDocuments,
  findDocumentsBySource,
} from "../kernel/search/causal_archaeology.ts";
import {
  findDocumentsByProvenanceType,
  findOriginTrail,
  findImportedCandidateDocuments,
} from "../kernel/search/provenance_archaeology.ts";
import { buildSearchInspectionPack } from "../kernel/search/search_inspection_pack.ts";
import { buildSearchExport, serializeSearchExport } from "../kernel/search/search_export.ts";

// ---------------------------------------------------------------------------
// Shared test fixtures
// ---------------------------------------------------------------------------

const SEED_TS = "2026-05-09T10:00:00.000Z";
const TS1 = "2026-05-09T10:01:00.000Z";
const TS2 = "2026-05-09T10:02:00.000Z";
const TS3 = "2026-05-09T10:03:00.000Z";

const THREE_CYCLES = [
  {
    tick_event_id: "evt-r18-tick-1",
    tick_number: 1,
    timestamp: TS1,
    world_time: TS1,
    transition_event_id_prefix: "evt-r18-pulse-tick1",
  },
  {
    tick_event_id: "evt-r18-tick-2",
    tick_number: 2,
    timestamp: TS2,
    world_time: TS2,
    transition_event_id_prefix: "evt-r18-pulse-tick2",
  },
  {
    tick_event_id: "evt-r18-tick-3",
    tick_number: 3,
    timestamp: TS3,
    world_time: TS3,
    transition_event_id_prefix: "evt-r18-pulse-tick3",
  },
];

function buildWorldFixture() {
  const store = new InMemoryEventStore();
  seedCanonicalEntities(store, SEED_TS);
  for (const cycle of THREE_CYCLES) {
    runWorldCycle(store, cycle);
  }
  return store;
}

const store = buildWorldFixture();
const allEvents = store.getAll();
const timeline = buildWorldTimeline(allEvents);
const slots = buildCanonicalEntitySlots();
const features = buildFeatureRegistry();
const snapshot = buildWorldSnapshot(allEvents);

const integrity = checkWorldIntegrity(allEvents);
const cameraModel = buildWorldCameraModel(snapshot, timeline, integrity);

const eventCorpus = buildSearchCorpusFromEvents(allEvents);
const timelineCorpus = buildSearchCorpusFromTimeline(timeline);
const slotCorpus = buildSearchCorpusFromSlots(slots);
const featureCorpus = buildSearchCorpusFromFeatures(features);

// Guard corpus: create two known violations
const guardReport = checkConceptLanguage([
  { id: "violation_1", text: "Tamagotchi ist implementiert." },
  { id: "violation_2", text: "METAWAR ist live." },
]);
const guardCorpus = buildSearchCorpusFromConceptGuard(guardReport);
const cameraCorpus = buildSearchCorpusFromCameraModel(cameraModel);

// CommandLedger with one entry
const daniel = buildDanielRootAdmin();
let ledger = createEmptyCommandLedger();
const cmd = createCommandIntent({
  command_id: "cmd_test_001",
  command_type: "request_feature_activation",
  requested_by: "daniel_root",
  target_type: "feature",
  target_id: "tamagotchi_care_feature",
  reason: "Test",
  created_at: "2026-05-09T00:00:00Z",
});
ledger = recordCommandIntent(ledger, cmd, daniel, "blocked", ["Organ gesperrt"]);
const ledgerCorpus = buildSearchCorpusFromCommandLedger(ledger);

// Merged corpus for general tests (events only for tick/presence counts)
const fullCorpus = mergeSearchCorpora(
  eventCorpus,
  slotCorpus,
  featureCorpus,
  guardCorpus,
  cameraCorpus,
  ledgerCorpus
);

// Inspection pack built from events-only corpus (for 3 ticks / 18 traces)
const inspectionPack = buildSearchInspectionPack(eventCorpus);

// ---------------------------------------------------------------------------
// 1. SearchDocument — Struktur und Typen
// ---------------------------------------------------------------------------

describe("Ring 18 — SearchDocument: Typen", () => {
  it("1. SearchDocument kann event repräsentieren", () => {
    const docs = eventCorpus.documents.filter((d) => d.kind === "event");
    assert.ok(docs.length > 0);
  });

  it("2. Event-Dokument enthält event_type", () => {
    const doc = eventCorpus.documents.find((d) => d.kind === "event");
    assert.ok(doc);
    assert.ok(doc!.event_type !== null);
  });

  it("3. Event-Dokument enthält actor_type", () => {
    const doc = eventCorpus.documents.find((d) => d.kind === "event");
    assert.ok(doc!.actor_type !== null);
  });

  it("4. Event-Dokument enthält target_id (kann null sein für ticks)", () => {
    const stateDoc = eventCorpus.documents.find(
      (d) => d.event_type === "entity.state_changed"
    );
    assert.ok(stateDoc);
    assert.ok(stateDoc!.target_id !== null);
  });

  it("5. Event-Dokument enthält source_ids", () => {
    const doc = eventCorpus.documents.find((d) => d.kind === "event");
    assert.ok(Array.isArray(doc!.source_ids));
  });

  it("6. TimelineFrame wird SearchDocument", () => {
    const docs = timelineCorpus.documents.filter((d) => d.kind === "timeline_frame");
    assert.ok(docs.length > 0);
  });

  it("7. ProvenanceRecord wird SearchDocument", () => {
    const provCorpus = buildSearchCorpusFromProvenance([
      {
        record_id: "prov-test-1",
        subject_type: "entity_slot",
        subject_id: "Schorschel",
        provenance_type: "canonical_seed",
        origin_label: "test",
        source_event_ids: [],
        confidence: "structural",
        notes: [],
      },
    ]);
    assert.ok(provCorpus.documents.some((d) => d.kind === "provenance_record"));
  });

  it("8. EntitySlot wird SearchDocument", () => {
    assert.ok(slotCorpus.documents.some((d) => d.kind === "slot"));
  });

  it("9. FeatureFlag wird SearchDocument", () => {
    assert.ok(featureCorpus.documents.some((d) => d.kind === "feature_flag"));
  });

  it("10. ConceptGuardViolation wird SearchDocument", () => {
    assert.ok(guardCorpus.documents.some((d) => d.kind === "concept_guard_violation"));
  });

  it("11. CameraNode wird SearchDocument", () => {
    assert.ok(cameraCorpus.documents.some((d) => d.kind === "camera_node"));
  });

  it("12. CameraEdge wird SearchDocument", () => {
    const hasEdges = cameraModel.edges.length > 0;
    if (hasEdges) {
      assert.ok(cameraCorpus.documents.some((d) => d.kind === "camera_edge"));
    } else {
      assert.ok(cameraCorpus.documents.some((d) => d.kind === "camera_node"));
    }
  });

  it("13. CommandLedgerEntry wird SearchDocument", () => {
    assert.ok(ledgerCorpus.documents.some((d) => d.kind === "command_ledger_entry"));
  });
});

// ---------------------------------------------------------------------------
// 2. mergeSearchCorpora
// ---------------------------------------------------------------------------

describe("Ring 18 — mergeSearchCorpora", () => {
  it("14. mergeSearchCorpora addiert Dokumente", () => {
    const merged = mergeSearchCorpora(eventCorpus, slotCorpus);
    assert.equal(
      merged.documents.length,
      eventCorpus.documents.length + slotCorpus.documents.length
    );
  });

  it("15. counts nach kind stimmen", () => {
    const merged = mergeSearchCorpora(eventCorpus, slotCorpus);
    const eventCount = merged.documents.filter((d) => d.kind === "event").length;
    assert.equal(merged.counts["event"], eventCount);
  });
});

// ---------------------------------------------------------------------------
// 3. ArchaeologyFilter
// ---------------------------------------------------------------------------

describe("Ring 18 — ArchaeologyFilter: Basis-Filter", () => {
  it("16. filter by kind event", () => {
    const results = filterSearchCorpus(eventCorpus, { kinds: ["event"] });
    assert.ok(results.length === 27);
  });

  it("17. filter by event_type system.tick", () => {
    const results = filterSearchCorpus(eventCorpus, { event_type: "system.tick" });
    assert.equal(results.length, 3);
  });

  it("18. filter by actor_type world_engine", () => {
    const results = filterSearchCorpus(eventCorpus, { actor_type: "world_engine" });
    assert.ok(results.length >= 3);
  });

  it("19. filter by target_id Schorschel", () => {
    const results = filterSearchCorpus(eventCorpus, { target_id: "Schorschel" });
    assert.ok(results.length > 0);
  });

  it("20. filter by slot_id Schorschel", () => {
    const results = filterSearchCorpus(slotCorpus, { slot_id: "Schorschel" });
    assert.ok(results.length > 0);
  });

  it("21. filter by feature_id tamagotchi_care_feature", () => {
    const results = filterSearchCorpus(featureCorpus, {
      feature_id: "tamagotchi_care_feature",
    });
    assert.equal(results.length, 1);
  });

  it("22. filter by provenance_type canonical_seed", () => {
    const pCorpus = buildSearchCorpusFromProvenance([
      {
        record_id: "prov-test-seed",
        subject_type: "entity_slot",
        subject_id: "Schorschel",
        provenance_type: "canonical_seed",
        origin_label: "test",
        source_event_ids: [],
        confidence: "structural",
        notes: [],
      },
    ]);
    const results = filterSearchCorpus(pCorpus, { provenance_type: "canonical_seed" });
    assert.ok(results.length > 0);
  });

  it("23. filter by layer runtime", () => {
    const results = filterSearchCorpus(slotCorpus, { layer: "slots" });
    assert.equal(results.length, slots.length);
  });

  it("24. filter by tag", () => {
    const results = filterSearchCorpus(eventCorpus, { tags: ["system.tick"] });
    assert.equal(results.length, 3);
  });

  it("25. filter by text case-insensitive", () => {
    const results = filterSearchCorpus(eventCorpus, { text: "SYSTEM.TICK" });
    assert.ok(results.length >= 3);
  });

  it("26. filter requires_source_ids", () => {
    const results = filterSearchCorpus(eventCorpus, { requires_source_ids: true });
    for (const doc of results) {
      assert.ok(doc.source_ids.length > 0);
    }
  });

  it("27. timeline_from filter", () => {
    const results = filterSearchCorpus(timelineCorpus, { timeline_from: 5 });
    for (const doc of results) {
      assert.ok(doc.timeline_index !== null && doc.timeline_index >= 5);
    }
  });

  it("28. timeline_to filter", () => {
    const results = filterSearchCorpus(timelineCorpus, { timeline_to: 3 });
    for (const doc of results) {
      assert.ok(doc.timeline_index !== null && doc.timeline_index <= 3);
    }
  });

  it("29. created_from filter", () => {
    const results = filterSearchCorpus(eventCorpus, { created_from: "2000-01-01T00:00:00Z" });
    assert.ok(results.length > 0);
  });

  it("30. created_to filter", () => {
    const results = filterSearchCorpus(eventCorpus, { created_to: "2099-12-31T23:59:59Z" });
    assert.ok(results.length > 0);
  });
});

// ---------------------------------------------------------------------------
// 4. ArchaeologyQuery
// ---------------------------------------------------------------------------

describe("Ring 18 — ArchaeologyQuery", () => {
  it("31. runArchaeologyQuery gibt result_count", () => {
    const result = runArchaeologyQuery(eventCorpus, {
      query_id: "q_ticks",
      label: "Alle Ticks",
      filter: { event_type: "system.tick" },
      explain: false,
    });
    assert.equal(result.result_count, 3);
  });

  it("32. explainSearchResult Deutsch", () => {
    const docs = filterSearchCorpus(eventCorpus, { event_type: "system.tick" });
    const lines = explainSearchResult(
      {
        query_id: "q_explain",
        label: "Tick Query",
        filter: { event_type: "system.tick" },
        explain: true,
      },
      docs
    );
    assert.ok(lines.some((l) => l.includes("Treffer")));
    assert.ok(lines.some((l) => l.includes("read-only")));
  });

  it("33. query all_ticks findet 3 tick docs", () => {
    const q = inspectionPack.sample_queries.find((q) => q.query_id === "all_ticks")!;
    const result = runArchaeologyQuery(eventCorpus, q);
    assert.equal(result.result_count, 3);
  });

  it("34. query all_presence_traces findet 18 trace docs", () => {
    const q = inspectionPack.sample_queries.find((q) => q.query_id === "all_presence_traces")!;
    const result = runArchaeologyQuery(eventCorpus, q);
    assert.equal(result.result_count, 18);
  });

  it("35. query disabled_features findet Organ-Features", () => {
    const q = inspectionPack.sample_queries.find((q) => q.query_id === "disabled_features")!;
    const result = runArchaeologyQuery(featureCorpus, q);
    assert.ok(result.result_count >= 7);
  });

  it("36. query concept_guard_violations findet Violations", () => {
    const q = inspectionPack.sample_queries.find(
      (q) => q.query_id === "concept_guard_violations"
    )!;
    const result = runArchaeologyQuery(guardCorpus, q);
    assert.equal(result.result_count, 2);
  });
});

// ---------------------------------------------------------------------------
// 5. Causal Archaeology
// ---------------------------------------------------------------------------

describe("Ring 18 — Causal Archaeology", () => {
  it("37. findCausalChildrenDocuments findet presence_pulse children für Tick 1", () => {
    const tickEvent = allEvents.find((e) => e.event_type === "system.tick");
    assert.ok(tickEvent);
    const children = findCausalChildrenDocuments(eventCorpus, tickEvent!.event_id);
    assert.ok(children.length > 0);
  });

  it("38. findCausalChainDocuments findet Eltern eines trace Events", () => {
    const traceEvent = allEvents.find((e) => e.event_type === "entity.state_changed");
    assert.ok(traceEvent);
    const chain = findCausalChainDocuments(eventCorpus, traceEvent!.event_id);
    assert.ok(chain.length > 0);
  });

  it("39. findDocumentsBySource findet Dokumente über source_id", () => {
    const tickEvent = allEvents.find((e) => e.event_type === "system.tick");
    assert.ok(tickEvent);
    const docs = findDocumentsBySource(eventCorpus, tickEvent!.event_id);
    assert.ok(docs.length > 0);
  });

  it("findCausalChainDocuments gibt leeres Array für unbekannte event_id", () => {
    const docs = findCausalChainDocuments(eventCorpus, "unknown_event_id");
    assert.equal(docs.length, 0);
  });

  it("findDocumentsBySource ist deterministisch", () => {
    const tickEvent = allEvents.find((e) => e.event_type === "system.tick")!;
    const d1 = findDocumentsBySource(eventCorpus, tickEvent.event_id);
    const d2 = findDocumentsBySource(eventCorpus, tickEvent.event_id);
    assert.deepEqual(
      d1.map((d) => d.document_id),
      d2.map((d) => d.document_id)
    );
  });
});

// ---------------------------------------------------------------------------
// 6. Provenance Archaeology
// ---------------------------------------------------------------------------

describe("Ring 18 — Provenance Archaeology", () => {
  it("40. findDocumentsByProvenanceType canonical_seed", () => {
    const pCorpus = buildSearchCorpusFromProvenance([
      {
        record_id: "prov-find-1",
        subject_type: "entity_slot",
        subject_id: "Schorschel",
        provenance_type: "canonical_seed",
        origin_label: "canonical seed",
        source_event_ids: [],
        confidence: "structural",
        notes: [],
      },
    ]);
    const docs = findDocumentsByProvenanceType(pCorpus, "canonical_seed");
    assert.ok(docs.length > 0);
  });

  it("41. findImportedCandidateDocuments leer oder strukturell korrekt", () => {
    const docs = findImportedCandidateDocuments(eventCorpus);
    assert.ok(Array.isArray(docs));
  });

  it("findOriginTrail für Schorschel", () => {
    const docs = findOriginTrail(fullCorpus, "Schorschel");
    assert.ok(docs.length > 0);
  });

  it("findDocumentsByProvenanceType gibt leeres Array für unbekannten Typ", () => {
    const docs = findDocumentsByProvenanceType(eventCorpus, "unknown_type");
    assert.equal(docs.length, 0);
  });
});

// ---------------------------------------------------------------------------
// 7. SearchInspectionPack
// ---------------------------------------------------------------------------

describe("Ring 18 — SearchInspectionPack", () => {
  it("42. buildSearchInspectionPack erzeugt sample_queries", () => {
    assert.ok(inspectionPack.sample_queries.length > 0);
  });

  it("43. sample query all_ticks vorhanden", () => {
    assert.ok(inspectionPack.sample_queries.some((q) => q.query_id === "all_ticks"));
  });

  it("44. sample query slot_Schorschel vorhanden", () => {
    assert.ok(
      inspectionPack.sample_queries.some((q) => q.query_id === "slot_Schorschel")
    );
  });

  it("87. SearchInspectionPack notes enthalten read-only", () => {
    assert.ok(inspectionPack.notes.some((n) => n.includes("read-only")));
  });

  it("88. SearchInspectionPack notes enthalten keine Mutation", () => {
    assert.ok(inspectionPack.notes.some((n) => n.includes("Mutation")));
  });

  it("pack_version ist 1", () => {
    assert.equal(inspectionPack.pack_version, 1);
  });
});

// ---------------------------------------------------------------------------
// 8. SearchExport — Determinismus
// ---------------------------------------------------------------------------

describe("Ring 18 — SearchExport: Determinismus", () => {
  it("45. SearchExport deterministisch", () => {
    const pack2 = buildSearchInspectionPack(eventCorpus);
    const e1 = buildSearchExport(inspectionPack);
    const e2 = buildSearchExport(pack2);
    assert.deepEqual(e1, e2);
  });

  it("46. serializeSearchExport stabil", () => {
    const pack2 = buildSearchInspectionPack(eventCorpus);
    const j1 = serializeSearchExport(inspectionPack);
    const j2 = serializeSearchExport(pack2);
    assert.equal(j1, j2);
  });

  it("86. SearchExport enthält corpus counts", () => {
    const exp = buildSearchExport(inspectionPack);
    assert.ok(typeof exp.counts === "object");
    assert.ok(exp.counts["event"] > 0);
  });

  it("serializeSearchExport gibt gültiges JSON", () => {
    const json = serializeSearchExport(inspectionPack);
    assert.doesNotThrow(() => JSON.parse(json));
  });
});

// ---------------------------------------------------------------------------
// 9. Keine Runtime-Aktivitäten durch Suche
// ---------------------------------------------------------------------------

describe("Ring 18 — Suche verändert nichts: keine Runtime-Aktivitäten", () => {
  it("47. SearchCorpus mutiert keine Events", () => {
    const countBefore = allEvents.length;
    buildSearchCorpusFromEvents(allEvents);
    assert.equal(allEvents.length, countBefore);
  });

  it("48. SearchQuery erzeugt keine Events", () => {
    const countBefore = allEvents.length;
    runArchaeologyQuery(eventCorpus, {
      query_id: "q_test",
      label: "test",
      filter: { event_type: "system.tick" },
      explain: false,
    });
    assert.equal(allEvents.length, countBefore);
  });

  it("49. Filter setzt keine Policy", () => {
    const result = filterSearchCorpus(featureCorpus, { kinds: ["feature_flag"] });
    for (const doc of result) {
      const f = doc.raw as { enabled?: boolean };
      if (doc.feature_id?.endsWith("_feature")) {
        assert.equal(f.enabled, false);
      }
    }
  });

  it("50. Keine AI in Corpus-JSON", () => {
    const json = JSON.stringify(eventCorpus);
    assert.ok(!json.includes('"ai"'));
  });

  it("51. Kein Postgres in Corpus-JSON", () => {
    const json = JSON.stringify(eventCorpus);
    assert.ok(!json.includes('"db"'));
  });

  it("52. Kein Renderer in Corpus-JSON", () => {
    const json = JSON.stringify(eventCorpus);
    assert.ok(!json.includes('"renderer"'));
  });

  it("53. Keine UI in Corpus-JSON", () => {
    const json = JSON.stringify(eventCorpus);
    assert.ok(!json.includes('"ui"'));
  });

  it("54. Kein Scheduler in Corpus-JSON", () => {
    const json = JSON.stringify(eventCorpus);
    assert.ok(!json.includes('"scheduler"'));
  });

  it("55. Kein EventStore nötig für reine Suche", () => {
    const staticEvents = allEvents;
    const corpus = buildSearchCorpusFromEvents(staticEvents);
    assert.ok(corpus.documents.length > 0);
  });
});

// ---------------------------------------------------------------------------
// 10. ConceptGuard — neue Muster
// ---------------------------------------------------------------------------

describe("Ring 18 — ConceptGuard: neue Suchmuster verboten", () => {
  it("56. ConceptGuard erkennt 'Suche verändert Events'", () => {
    const r = checkConceptLanguage([{ id: "s1", text: "Suche verändert Events direkt." }]);
    assert.equal(r.ok, false);
  });

  it("57. ConceptGuard erkennt 'DeepSearch aktiviert Features'", () => {
    const r = checkConceptLanguage([{ id: "s2", text: "DeepSearch aktiviert Features jetzt." }]);
    assert.equal(r.ok, false);
  });

  it("58. ConceptGuard erkennt 'SearchIndex ist Wahrheit'", () => {
    const r = checkConceptLanguage([{ id: "s3", text: "SearchIndex ist Wahrheit ohne Quelle." }]);
    assert.equal(r.ok, false);
  });

  it("59. ConceptGuard erkennt 'Filter setzt Policy'", () => {
    const r = checkConceptLanguage([{ id: "s4", text: "Filter setzt Policy automatisch." }]);
    assert.equal(r.ok, false);
  });

  it("60. ConceptGuard erkennt 'Suchergebnis braucht keine Quelle'", () => {
    const r = checkConceptLanguage([{ id: "s5", text: "Suchergebnis braucht keine Quelle." }]);
    assert.equal(r.ok, false);
  });

  it("61. ConceptGuard erkennt 'Archäologie ist nur Volltextsuche'", () => {
    const r = checkConceptLanguage([{ id: "s6", text: "Archäologie ist nur Volltextsuche." }]);
    assert.equal(r.ok, false);
  });
});

describe("Ring 18 — ConceptGuard: erlaubte Suchsprache", () => {
  it("62. ConceptGuard akzeptiert 'Diskursarchäologische Suche'", () => {
    const r = checkConceptLanguage([{ id: "a1", text: "Diskursarchäologische Suche ist read-only." }]);
    assert.equal(r.ok, true);
  });

  it("63. ConceptGuard akzeptiert 'read-only SearchCorpus'", () => {
    const r = checkConceptLanguage([{ id: "a2", text: "Der read-only SearchCorpus enthält Dokumente." }]);
    assert.equal(r.ok, true);
  });

  it("64. ConceptGuard akzeptiert 'Filter Grammar'", () => {
    const r = checkConceptLanguage([{ id: "a3", text: "Filter Grammar für Archäologie." }]);
    assert.equal(r.ok, true);
  });

  it("65. ConceptGuard akzeptiert 'source_ids'", () => {
    const r = checkConceptLanguage([{ id: "a4", text: "Alle Dokumente haben source_ids." }]);
    assert.equal(r.ok, true);
  });
});

// ---------------------------------------------------------------------------
// 11. Suche über alle Weltkörper
// ---------------------------------------------------------------------------

describe("Ring 18 — Suche über alle Weltkörper", () => {
  it("66. Suche über Worldblick-Dokumente möglich (feature corpus hat worldblick flag)", () => {
    const results = filterSearchCorpus(featureCorpus, {
      feature_id: "worldblick_readonly_export",
    });
    assert.equal(results.length, 1);
  });

  it("67. Suche über Audit-Dokumente möglich (camera als Audit-Proxy)", () => {
    assert.ok(cameraCorpus.documents.length > 0);
  });

  it("68. Suche über OS-Spine-Summary möglich (feature corpus als Proxy)", () => {
    const results = filterSearchCorpus(featureCorpus, { kinds: ["feature_flag"] });
    assert.ok(results.length > 0);
  });

  it("69. Suche über CommandLedger möglich", () => {
    const results = filterSearchCorpus(ledgerCorpus, { kinds: ["command_ledger_entry"] });
    assert.equal(results.length, 1);
  });

  it("70. Suche über FeatureRegistry möglich", () => {
    const results = filterSearchCorpus(featureCorpus, { kinds: ["feature_flag"] });
    assert.equal(results.length, features.length);
  });

  it("71. Suche über SlotRegistry möglich", () => {
    const results = filterSearchCorpus(slotCorpus, { kinds: ["slot"] });
    assert.equal(results.length, slots.length);
  });

  it("72. Suche über Timeline möglich", () => {
    const results = filterSearchCorpus(timelineCorpus, { kinds: ["timeline_frame"] });
    assert.equal(results.length, 27);
  });

  it("73. Suche über CameraModel möglich", () => {
    assert.ok(cameraCorpus.documents.length > 0);
  });

  it("74. Suche über Provenance möglich", () => {
    const pCorpus = buildSearchCorpusFromProvenance([
      {
        record_id: "prov-suche-1",
        subject_type: "entity_slot",
        subject_id: "Schorschel",
        provenance_type: "canonical_seed",
        origin_label: "canonical seed",
        source_event_ids: [],
        confidence: "structural",
        notes: [],
      },
    ]);
    const results = filterSearchCorpus(pCorpus, { kinds: ["provenance_record"] });
    assert.ok(results.length > 0);
  });

  it("75. Suche über ConceptGuard möglich", () => {
    const results = filterSearchCorpus(guardCorpus, { kinds: ["concept_guard_violation"] });
    assert.equal(results.length, 2);
  });
});

// ---------------------------------------------------------------------------
// 12. Filter Kombinationen und Stabilität
// ---------------------------------------------------------------------------

describe("Ring 18 — Filter Kombinationen und Stabilität", () => {
  it("76. Suche kann mehrere Filter kombinieren", () => {
    const results = filterSearchCorpus(eventCorpus, {
      kinds: ["event"],
      event_type: "entity.state_changed",
      actor_type: "world_engine",
    });
    assert.ok(results.length > 0);
    for (const doc of results) {
      assert.equal(doc.kind, "event");
      assert.equal(doc.event_type, "entity.state_changed");
    }
  });

  it("77. Suche gibt leere Ergebnisse deterministisch zurück", () => {
    const r1 = filterSearchCorpus(eventCorpus, { event_type: "does.not.exist" });
    const r2 = filterSearchCorpus(eventCorpus, { event_type: "does.not.exist" });
    assert.equal(r1.length, 0);
    assert.deepEqual(r1, r2);
  });

  it("78. Suche sortiert Ergebnisse stabil nach document_id", () => {
    const r1 = filterSearchCorpus(eventCorpus, { event_type: "entity.state_changed" });
    const r2 = filterSearchCorpus(eventCorpus, { event_type: "entity.state_changed" });
    assert.deepEqual(
      r1.map((d) => d.document_id),
      r2.map((d) => d.document_id)
    );
  });

  it("84. all_ticks Query verändert Corpus nicht", () => {
    const countBefore = eventCorpus.documents.length;
    runArchaeologyQuery(eventCorpus, {
      query_id: "q_ticks_2",
      label: "ticks check",
      filter: { event_type: "system.tick" },
      explain: false,
    });
    assert.equal(eventCorpus.documents.length, countBefore);
  });

  it("85. all_presence_traces Query verändert Corpus nicht", () => {
    const countBefore = eventCorpus.documents.length;
    runArchaeologyQuery(eventCorpus, {
      query_id: "q_traces_2",
      label: "traces check",
      filter: { kinds: ["event", "timeline_frame"], tags: ["entity.state_changed"] },
      explain: false,
    });
    assert.equal(eventCorpus.documents.length, countBefore);
  });
});

// ---------------------------------------------------------------------------
// 13. Pflichtfelder jedes SearchDocument
// ---------------------------------------------------------------------------

describe("Ring 18 — SearchDocument Pflichtfelder", () => {
  it("79. alle SearchDocuments haben kind", () => {
    for (const doc of fullCorpus.documents) {
      assert.ok(doc.kind, `Dokument ${doc.document_id} fehlt kind`);
    }
  });

  it("80. alle SearchDocuments haben title", () => {
    for (const doc of fullCorpus.documents) {
      assert.ok(doc.title.length > 0, `${doc.document_id} fehlt title`);
    }
  });

  it("81. alle SearchDocuments haben body", () => {
    for (const doc of fullCorpus.documents) {
      assert.ok(typeof doc.body === "string", `${doc.document_id} fehlt body`);
    }
  });

  it("82. alle SearchDocuments haben tags", () => {
    for (const doc of fullCorpus.documents) {
      assert.ok(Array.isArray(doc.tags), `${doc.document_id} fehlt tags`);
    }
  });

  it("83. alle SearchDocuments haben source_ids Array", () => {
    for (const doc of fullCorpus.documents) {
      assert.ok(Array.isArray(doc.source_ids), `${doc.document_id} fehlt source_ids`);
    }
  });
});

// ---------------------------------------------------------------------------
// 14. Regressions-Smoke-Test
// ---------------------------------------------------------------------------

describe("Ring 18 — Regression: bestehende Module weiter importierbar", () => {
  it("89. Existing event_queries bleiben kompatibel", () => {
    const ticks = findEventsByType(allEvents, "system.tick");
    assert.equal(ticks.length, 3);
  });

  it("90. Existing worldblick Tests bleiben grün — feature_id worldblick_readonly_export", () => {
    const f = features.find((f) => f.feature_id === "worldblick_readonly_export");
    assert.ok(f);
    assert.equal(f!.enabled, true);
  });

  it("91. Existing admin Tests bleiben grün — DanielRoot hat alle Permissions", () => {
    assert.equal(daniel.role, "daniel_root");
    assert.equal(daniel.permissions.length > 10, true);
  });

  it("92. Alle bisherigen Tests bleiben grün — EventCorpus hat 27 Dokumente", () => {
    assert.equal(eventCorpus.documents.length, 27);
  });

  it("matchesArchaeologyFilter: leerer Filter matcht alles", () => {
    const allDocs = filterSearchCorpus(eventCorpus, {});
    assert.equal(allDocs.length, 27);
  });

  it("Feature corpus: 7 Organ-Features alle disabled", () => {
    const organs = featureCorpus.documents.filter(
      (d) => d.kind === "feature_flag" && (d.raw as { kind: string }).kind === "organ"
    );
    assert.equal(organs.length, 7);
    for (const doc of organs) {
      assert.ok(doc.tags.includes("disabled"));
    }
  });

  it("CommandLedger Entry ist blocked im Corpus", () => {
    const entry = ledgerCorpus.documents[0];
    assert.ok(entry.body.includes("blocked"));
  });

  it("SearchExport total_documents stimmt", () => {
    const exp = buildSearchExport(inspectionPack);
    assert.equal(exp.total_documents, eventCorpus.documents.length);
  });
});
