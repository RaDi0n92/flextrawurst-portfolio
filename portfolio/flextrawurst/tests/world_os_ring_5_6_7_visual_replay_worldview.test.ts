import { describe, it, before } from "node:test";
import assert from "node:assert/strict";
import { InMemoryEventStore } from "../kernel/events/event_store.ts";
import {
  createInitialSixSlotsThreeTickScenario,
} from "../kernel/scenario/world_scenario.ts";
import { runWorldScenario } from "../kernel/scenario/run_world_scenario.ts";
import type { WorldInspectionPack } from "../kernel/inspection/world_inspection_pack.ts";
import { buildWorldOSSpine } from "../kernel/os_spine/world_os_spine.ts";
import type { WorldOSSpine } from "../kernel/os_spine/world_os_spine.ts";
import {
  createForumImportFixtureForCanonicalSlots,
} from "../kernel/import_gate/forum_import_candidate.ts";
import type { ForumImportBundle } from "../kernel/import_gate/forum_import_candidate.ts";
import {
  extendSpineWithImportGate,
} from "../kernel/os_spine/world_os_spine_import_extension.ts";
import type { WorldOSSpineImportExtension } from "../kernel/os_spine/world_os_spine_import_extension.ts";
import {
  createVisualMeaning,
  type VisualMeaning,
} from "../kernel/visual_meaning/visual_meaning_model.ts";
import {
  buildVisualMeaningsFromSpine,
  buildFlarumOriginMarkers,
} from "../kernel/visual_meaning/visual_meaning_engine.ts";
import {
  getVisualKindLabel,
  buildVisualExplanationText,
} from "../kernel/visual_meaning/visual_explanation.ts";
import {
  buildReplayTimeWindow,
} from "../kernel/replay/replay_time_window.ts";
import type { ReplayTimeWindow } from "../kernel/replay/replay_time_window.ts";
import {
  buildWorldReplayTrace,
  buildAllSlotReplayTraces,
} from "../kernel/replay/world_replay_trace.ts";
import type { WorldReplayTrace } from "../kernel/replay/world_replay_trace.ts";
import {
  explainVisualMeaning,
  buildAllVisualExplanations,
} from "../kernel/replay/visual_replay_explanation.ts";
import type { VisualReplayExplanation } from "../kernel/replay/visual_replay_explanation.ts";
import {
  buildWorldviewGraph,
} from "../kernel/worldview/worldview_graph_builder.ts";
import type { WorldviewGraph } from "../kernel/worldview/worldview_graph_model.ts";
import { buildWorldviewZoomModel } from "../kernel/worldview/worldview_zoom_model.ts";
import { ZOOM_LEVEL_KINDS } from "../kernel/worldview/worldview_zoom_model.ts";
import {
  buildDefaultRoomWeather,
  buildRoomWeather,
} from "../kernel/worldview/room_weather_model.ts";
import type { RoomWeather } from "../kernel/worldview/room_weather_model.ts";
import { checkConceptLanguage } from "../kernel/concept_guard/concept_guard.ts";
import { buildOSConvergenceReport } from "../kernel/os_spine/os_convergence_report.ts";
import { buildReadOnlyConsoleModel } from "../kernel/console/read_only_console_model.ts";

let store: InMemoryEventStore;
let pack: WorldInspectionPack;
let spine: WorldOSSpine;
let bundle: ForumImportBundle;
let importExtension: WorldOSSpineImportExtension;
let visuals: VisualMeaning[];
let replayTimeWindow: ReplayTimeWindow;
let replayTraces: WorldReplayTrace[];
let visualExplanations: VisualReplayExplanation[];
let worldviewGraph: WorldviewGraph;
let roomWeather: RoomWeather;

before(() => {
  store = new InMemoryEventStore();
  const scenario = createInitialSixSlotsThreeTickScenario();
  pack = runWorldScenario(store, scenario);
  spine = buildWorldOSSpine(pack);
  bundle = createForumImportFixtureForCanonicalSlots();
  importExtension = extendSpineWithImportGate(spine, bundle);

  visuals = buildVisualMeaningsFromSpine(spine, pack, importExtension);
  replayTimeWindow = buildReplayTimeWindow(
    pack.events,
    pack.replay_frames
  );
  replayTraces = buildAllSlotReplayTraces(
    spine.slots,
    pack.events,
    pack.replay_frames
  );
  visualExplanations = buildAllVisualExplanations(
    visuals,
    pack,
    importExtension.activation_firewall
  );
  worldviewGraph = buildWorldviewGraph(
    spine,
    pack,
    importExtension,
    visuals,
    replayTraces
  );
  roomWeather = buildDefaultRoomWeather(spine, importExtension);
});

describe("Weltbetriebssystem Ring 5/6/7 — Visual Meaning + Replay + Worldview", () => {

  // ─── Ring 5: Visual Meaning Model ───

  it("1. createVisualMeaning mit Herkunft wird akzeptiert", () => {
    const vm = createVisualMeaning({
      visual_id: "vm-test-001",
      visual_kind: "node_pulse",
      source_slot_ids: ["Schorschel"],
      meaning: "Test-Weltpuls.",
      intensity: 0.5,
      confidence: "structural",
      created_from: "test",
      created_at: "2026-01-01T00:00:00.000Z",
    });
    assert.ok(vm);
    assert.equal(vm.visual_id, "vm-test-001");
    assert.equal(vm.is_decorative, false);
  });

  it("2. VisualMeaning ohne Herkunft wird abgelehnt", () => {
    assert.throws(
      () =>
        createVisualMeaning({
          visual_id: "vm-no-source",
          visual_kind: "node_pulse",
          source_event_ids: [],
          source_state_ids: [],
          source_slot_ids: [],
          source_room_ids: [],
          meaning: "Verboten.",
          intensity: 0.5,
          confidence: "structural",
          created_from: "test",
          created_at: "2026-01-01T00:00:00.000Z",
        }),
      /Herkunft/
    );
  });

  it("3. VisualMeaning ist nie dekorativ — is_decorative ist immer false", () => {
    assert.ok(visuals.every((v) => v.is_decorative === false));
  });

  it("4. buildVisualMeaningsFromSpine erzeugt VisualMeanings", () => {
    assert.ok(visuals.length > 0);
  });

  it("5. buildVisualMeaningsFromSpine erzeugt node_pulse für jeden Slot", () => {
    const pulses = visuals.filter((v) => v.visual_kind === "node_pulse");
    assert.equal(pulses.length, spine.slots.length);
  });

  it("6. buildVisualMeaningsFromSpine erzeugt activation_block für jeden Slot", () => {
    const blocks = visuals.filter((v) => v.visual_kind === "activation_block");
    assert.equal(blocks.length, spine.slots.length);
  });

  it("7. buildFlarumOriginMarkers erzeugt origin_marker für gemappte Accounts", () => {
    const markers = buildFlarumOriginMarkers(importExtension);
    assert.equal(markers.length, 6);
    assert.ok(markers.every((m) => m.visual_kind === "origin_marker"));
  });

  it("8. origin_marker hat origin_layer flarum_vorphase", () => {
    const markers = visuals.filter((v) => v.visual_kind === "origin_marker");
    assert.ok(markers.length > 0);
    assert.ok(
      markers.every((m) => m.origin_layer === "flarum_vorphase")
    );
  });

  it("9. origin_marker is_live_flextrawurst_state ist false", () => {
    const markers = visuals.filter((v) => v.visual_kind === "origin_marker");
    assert.ok(markers.every((m) => m.is_live_flextrawurst_state === false));
  });

  it("10. origin_marker requires_start_decision ist true", () => {
    const markers = visuals.filter((v) => v.visual_kind === "origin_marker");
    assert.ok(markers.every((m) => m.requires_start_decision === true));
  });

  it("11. VisualMeaning erzeugt keine Events im EventStore", () => {
    buildVisualMeaningsFromSpine(spine, pack, importExtension);
    assert.equal(store.length, 27);
  });

  it("12. node_pulse hat mindestens eine Herkunft (source_event_ids oder source_slot_ids)", () => {
    const pulses = visuals.filter((v) => v.visual_kind === "node_pulse");
    assert.ok(
      pulses.every(
        (p) => p.source_event_ids.length > 0 || p.source_slot_ids.length > 0
      )
    );
  });

  it("13. activation_block hat source_slot_ids befüllt", () => {
    const blocks = visuals.filter((v) => v.visual_kind === "activation_block");
    assert.ok(blocks.every((b) => b.source_slot_ids.length > 0));
  });

  it("14. intensity liegt zwischen 0 und 1", () => {
    assert.ok(visuals.every((v) => v.intensity >= 0 && v.intensity <= 1));
  });

  it("15. getVisualKindLabel gibt Label für alle Kinds zurück", () => {
    const kinds = [
      "node_pulse",
      "edge_pressure",
      "silence_shell",
      "memory_echo",
      "dream_residue_hint",
      "room_density",
      "activation_block",
      "origin_marker",
      "replay_trace",
    ] as const;
    for (const kind of kinds) {
      const label = getVisualKindLabel(kind);
      assert.ok(label.length > 0, `Kein Label für ${kind}`);
    }
  });

  it("16. buildVisualExplanationText gibt nicht-leere Erklärung zurück", () => {
    const vm = visuals[0];
    const text = buildVisualExplanationText(vm);
    assert.ok(text.length > 0);
    assert.ok(text.includes(vm.visual_id) || text.includes(vm.meaning.substring(0, 10)));
  });

  it("17. Flarum origin_marker enthält Hinweis auf Vorphase in Erklärung", () => {
    const marker = visuals.find((v) => v.visual_kind === "origin_marker");
    assert.ok(marker);
    const text = buildVisualExplanationText(marker);
    assert.ok(text.includes("Flarum-Vorphase") || text.includes("flarum_vorphase") || text.includes("Vorphase"));
  });

  it("18. Gesamtzahl VisualMeanings: 6 node_pulse + 6 activation_block + 6 origin_marker = 18", () => {
    assert.equal(visuals.length, 18);
  });

  // ─── Ring 6: Replay Time Window ───

  it("19. buildReplayTimeWindow erzeugt ReplayTimeWindow", () => {
    assert.ok(replayTimeWindow);
    assert.equal(replayTimeWindow.creates_new_events, false);
  });

  it("20. ReplayTimeWindow ohne Grenzen enthält alle Events", () => {
    assert.equal(
      replayTimeWindow.included_event_ids.length,
      pack.event_count
    );
  });

  it("21. ReplayTimeWindow ohne Grenzen zählt 3 Ticks", () => {
    assert.equal(replayTimeWindow.tick_count, 3);
  });

  it("22. ReplayTimeWindow ohne Grenzen zählt 3 Frames", () => {
    assert.equal(replayTimeWindow.frame_count, 3);
  });

  it("23. ReplayTimeWindow mit Grenzen schränkt Events ein", () => {
    const firstEventId = pack.events[0].event_id;
    const thirdEventId = pack.events[2].event_id;
    const window = buildReplayTimeWindow(
      pack.events,
      pack.replay_frames,
      firstEventId,
      thirdEventId
    );
    assert.equal(window.included_event_ids.length, 3);
    assert.equal(window.creates_new_events, false);
  });

  it("24. ReplayTimeWindow erzeugt keine neuen Events", () => {
    buildReplayTimeWindow(pack.events, pack.replay_frames);
    assert.equal(store.length, 27);
  });

  // ─── Ring 6: World Replay Trace ───

  it("25. buildWorldReplayTrace erzeugt WorldReplayTrace", () => {
    const slot = spine.slots[0];
    const trace = buildWorldReplayTrace(slot, pack.events, pack.replay_frames);
    assert.ok(trace);
    assert.equal(trace.slot_id, slot.slot_id);
  });

  it("26. WorldReplayTrace creates_new_events ist false", () => {
    assert.ok(replayTraces.every((t) => t.creates_new_events === false));
  });

  it("27. WorldReplayTrace activates_slots ist false", () => {
    assert.ok(replayTraces.every((t) => t.activates_slots === false));
  });

  it("28. WorldReplayTrace created_without_side_effects ist true", () => {
    assert.ok(
      replayTraces.every((t) => t.created_without_side_effects === true)
    );
  });

  it("29. buildAllSlotReplayTraces erzeugt einen Trace pro Slot", () => {
    assert.equal(replayTraces.length, spine.slots.length);
  });

  it("30. Jeder ReplayTrace enthält Event-IDs des Slots", () => {
    for (const trace of replayTraces) {
      assert.ok(
        trace.event_ids.length > 0,
        `Trace für ${trace.slot_id} hat keine Events`
      );
    }
  });

  it("31. Jeder ReplayTrace enthält alle 3 Frame-Indices", () => {
    for (const trace of replayTraces) {
      assert.ok(
        trace.frame_indices.includes(0) &&
          trace.frame_indices.includes(1) &&
          trace.frame_indices.includes(2),
        `Trace für ${trace.slot_id} hat nicht alle Frame-Indices`
      );
    }
  });

  it("32. Replay erzeugt keine neuen Events im EventStore", () => {
    buildAllSlotReplayTraces(spine.slots, pack.events, pack.replay_frames);
    assert.equal(store.length, 27);
  });

  it("33. Replay aktiviert keine Slots — occupant_id bleibt null", () => {
    buildAllSlotReplayTraces(spine.slots, pack.events, pack.replay_frames);
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
  });

  // ─── Ring 6: Visual Replay Explanation ───

  it("34. explainVisualMeaning gibt VisualReplayExplanation zurück", () => {
    const vm = visuals[0];
    const exp = explainVisualMeaning(vm, pack, importExtension.activation_firewall);
    assert.ok(exp);
    assert.equal(exp.visual_id, vm.visual_id);
  });

  it("35. explainVisualMeaning can_trigger_activation ist false", () => {
    assert.ok(
      visualExplanations.every((e) => e.can_trigger_activation === false)
    );
  });

  it("36. explainVisualMeaning activation_status ist blocked", () => {
    assert.ok(
      visualExplanations.every((e) => e.activation_status === "blocked")
    );
  });

  it("37. explainVisualMeaning — origin_marker is_import_origin ist true", () => {
    const markerExps = visualExplanations.filter((e) =>
      e.visual_id.includes("origin-marker")
    );
    assert.ok(markerExps.length > 0);
    assert.ok(markerExps.every((e) => e.is_import_origin === true));
  });

  it("38. explainVisualMeaning — node_pulse is_import_origin ist false", () => {
    const pulseExps = visualExplanations.filter((e) =>
      e.visual_id.includes("node-pulse")
    );
    assert.ok(pulseExps.length > 0);
    assert.ok(pulseExps.every((e) => e.is_import_origin === false));
  });

  it("39. explainVisualMeaning — origin_marker is_live_state ist false", () => {
    const markerExps = visualExplanations.filter((e) =>
      e.visual_id.includes("origin-marker")
    );
    assert.ok(markerExps.every((e) => e.is_live_state === false));
  });

  it("40. explainVisualMeaning — node_pulse is_live_state ist true", () => {
    const pulseExps = visualExplanations.filter((e) =>
      e.visual_id.includes("node-pulse")
    );
    assert.ok(pulseExps.every((e) => e.is_live_state === true));
  });

  it("41. Replay erklärt source_event_ids deterministisch", () => {
    const vm = visuals.find(
      (v) =>
        v.visual_kind === "node_pulse" && v.source_event_ids.length > 0
    );
    assert.ok(vm);
    const exp1 = explainVisualMeaning(
      vm,
      pack,
      importExtension.activation_firewall
    );
    const exp2 = explainVisualMeaning(
      vm,
      pack,
      importExtension.activation_firewall
    );
    assert.equal(JSON.stringify(exp1), JSON.stringify(exp2));
    assert.ok(exp1.provenance_markers.some((m) => m.includes(vm.source_event_ids[0])));
  });

  it("42. Replay erklärt source_state_ids deterministisch — vollständige Erklärungsliste", () => {
    const all1 = JSON.stringify(
      buildAllVisualExplanations(
        visuals,
        pack,
        importExtension.activation_firewall
      )
    );
    const all2 = JSON.stringify(
      buildAllVisualExplanations(
        visuals,
        pack,
        importExtension.activation_firewall
      )
    );
    assert.equal(all1, all2);
  });

  it("43. explainVisualMeaning gibt why_visible zurück", () => {
    assert.ok(visualExplanations.every((e) => e.why_visible.length > 0));
  });

  it("44. explainVisualMeaning gibt world_ground zurück", () => {
    assert.ok(visualExplanations.every((e) => e.world_ground.length > 0));
  });

  it("45. explainVisualMeaning gibt provenance_markers zurück", () => {
    assert.ok(visualExplanations.every((e) => e.provenance_markers.length > 0));
  });

  // ─── Ring 7: Worldview Graph ───

  it("46. WorldviewGraph wird erzeugt", () => {
    assert.ok(worldviewGraph);
    assert.ok(worldviewGraph.graph_id.length > 0);
  });

  it("47. WorldviewGraph ist read-only", () => {
    assert.equal(worldviewGraph.is_read_only, true);
  });

  it("48. WorldviewGraph uses_renderer ist false", () => {
    assert.equal(worldviewGraph.uses_renderer, false);
  });

  it("49. WorldviewGraph uses_ui ist false", () => {
    assert.equal(worldviewGraph.uses_ui, false);
  });

  it("50. WorldviewGraph enthält EntitySlotNodes — 6 Stück", () => {
    const slotNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "entity_slot_node"
    );
    assert.equal(slotNodes.length, 6);
  });

  it("51. WorldviewGraph enthält ImportOriginNodes — 6 Stück", () => {
    const importNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "import_origin_node"
    );
    assert.equal(importNodes.length, 6);
  });

  it("52. WorldviewGraph enthält mindestens einen RoomNode", () => {
    const roomNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "room_node"
    );
    assert.ok(roomNodes.length >= 1);
  });

  it("53. WorldviewGraph enthält visual_meaning_nodes", () => {
    const vmNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "visual_meaning_node"
    );
    assert.ok(vmNodes.length > 0);
  });

  it("54. WorldviewGraph enthält replay_trace_nodes", () => {
    const traceNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "replay_trace_node"
    );
    assert.ok(traceNodes.length > 0);
  });

  it("55. WorldviewGraph markiert Flarum als Ursprung — origin_layer flarum_vorphase", () => {
    const importNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "import_origin_node"
    );
    assert.ok(
      importNodes.every((n) => n.origin_layer === "flarum_vorphase")
    );
  });

  it("56. WorldviewGraph entity_slot_nodes is_live_flextrawurst_state ist false", () => {
    const slotNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "entity_slot_node"
    );
    assert.ok(slotNodes.every((n) => n.is_live_flextrawurst_state === false));
  });

  it("57. WorldviewGraph import_origin_nodes is_live_flextrawurst_state ist false", () => {
    const importNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "import_origin_node"
    );
    assert.ok(importNodes.every((n) => n.is_live_flextrawurst_state === false));
  });

  it("58. WorldviewGraph import_origin_nodes requires_start_decision ist true", () => {
    const importNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "import_origin_node"
    );
    assert.ok(importNodes.every((n) => n.requires_start_decision === true));
  });

  it("59. WorldviewGraph markiert nichts als Bewohner", () => {
    const hasResident = worldviewGraph.nodes.some(
      (n) =>
        n.node_kind.includes("bewohner") ||
        n.node_kind.includes("resident") ||
        n.label.toLowerCase().includes("bewohner")
    );
    assert.equal(hasResident, false);
  });

  it("60. WorldviewGraph enthält keine Renderer-Felder (kein HTML/CSS)", () => {
    const serialized = JSON.stringify(worldviewGraph);
    assert.ok(!serialized.includes("<html"));
    assert.ok(!serialized.includes("<div"));
    assert.ok(!serialized.includes("<style"));
    assert.ok(!serialized.includes("document."));
    assert.ok(!serialized.includes("canvas"));
    assert.ok(!serialized.includes("three.js"));
    assert.ok(!serialized.includes("cytoscape"));
  });

  it("61. WorldviewGraph node_id ist eindeutig", () => {
    const ids = worldviewGraph.nodes.map((n) => n.node_id);
    const uniqueIds = new Set(ids);
    assert.equal(uniqueIds.size, ids.length);
  });

  it("62. WorldviewGraph edge_id ist eindeutig", () => {
    const ids = worldviewGraph.edges.map((e) => e.edge_id);
    const uniqueIds = new Set(ids);
    assert.equal(uniqueIds.size, ids.length);
  });

  it("63. WorldviewGraph Edges haben confidence-Feld", () => {
    assert.ok(worldviewGraph.edges.every((e) => e.confidence.length > 0));
  });

  it("64. WorldviewGraph enthält origin_candidate_maps_to_slot Edges", () => {
    const edges = worldviewGraph.edges.filter(
      (e) => e.edge_kind === "origin_candidate_maps_to_slot"
    );
    assert.ok(edges.length > 0);
  });

  it("65. WorldviewGraph enthält event_affects_slot Edges", () => {
    const edges = worldviewGraph.edges.filter(
      (e) => e.edge_kind === "event_affects_slot"
    );
    assert.ok(edges.length > 0);
  });

  it("66. WorldviewGraph enthält room_contains_slot Edges", () => {
    const edges = worldviewGraph.edges.filter(
      (e) => e.edge_kind === "room_contains_slot"
    );
    assert.equal(edges.length, 6);
  });

  it("67. buildWorldviewGraph erzeugt keine neuen Events", () => {
    buildWorldviewGraph(
      spine,
      pack,
      importExtension,
      visuals,
      replayTraces
    );
    assert.equal(store.length, 27);
  });

  // ─── Ring 7: Zoom Model ───

  it("68. ZoomModel enthält genau die geplanten Ebenen", () => {
    const zoomModel = buildWorldviewZoomModel();
    assert.equal(zoomModel.levels.length, ZOOM_LEVEL_KINDS.length);
    for (const kind of ZOOM_LEVEL_KINDS) {
      const level = zoomModel.levels.find((l) => l.kind === kind);
      assert.ok(level, `Zoom-Ebene '${kind}' fehlt`);
    }
  });

  it("69. ZoomModel enthält genau 6 Zoom-Ebenen", () => {
    const zoomModel = buildWorldviewZoomModel();
    assert.equal(zoomModel.levels.length, 6);
  });

  it("70. ZoomModel Ebenen haben shows_renderer false", () => {
    const zoomModel = buildWorldviewZoomModel();
    assert.ok(zoomModel.levels.every((l) => l.shows_renderer === false));
  });

  it("71. ZoomModel default_level ist cosmos", () => {
    const zoomModel = buildWorldviewZoomModel();
    assert.equal(zoomModel.default_level, "cosmos");
  });

  it("72. ZoomModel Ebenen-Reihenfolge: cosmos=0, provenance=5", () => {
    const zoomModel = buildWorldviewZoomModel();
    const cosmos = zoomModel.levels.find((l) => l.kind === "cosmos");
    const provenance = zoomModel.levels.find((l) => l.kind === "provenance");
    assert.ok(cosmos);
    assert.ok(provenance);
    assert.equal(cosmos.index, 0);
    assert.equal(provenance.index, 5);
  });

  // ─── Ring 7: Room Weather ───

  it("73. RoomWeather wird erzeugt", () => {
    assert.ok(roomWeather);
    assert.ok(roomWeather.room_id.length > 0);
  });

  it("74. RoomWeather live_presence ist 0 ohne echte Bewohner", () => {
    assert.equal(roomWeather.live_presence, 0.0);
  });

  it("75. RoomWeather import_presence ist 1.0 bei vorhandenem Import", () => {
    assert.equal(roomWeather.import_presence, 1.0);
  });

  it("76. RoomWeather ist deterministisch", () => {
    const w1 = buildDefaultRoomWeather(spine, importExtension);
    const w2 = buildDefaultRoomWeather(spine, importExtension);
    assert.equal(JSON.stringify(w1), JSON.stringify(w2));
  });

  it("77. RoomWeather für benannten Raum hat korrekte room_id", () => {
    const w = buildRoomWeather("raum-test-xyz", spine, importExtension);
    assert.equal(w.room_id, "raum-test-xyz");
  });

  it("78. RoomWeather density und activity liegen zwischen 0 und 1", () => {
    assert.ok(roomWeather.density >= 0 && roomWeather.density <= 1);
    assert.ok(roomWeather.activity >= 0 && roomWeather.activity <= 1);
  });

  // ─── Concept Guard neue Muster ───

  it("79. ConceptGuard erkennt 'Visualisierung ist Deko'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Visualisierung ist Deko ohne Bedeutung." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Visualisierung ist Deko"));
  });

  it("80. ConceptGuard erkennt 'Graph ist Hintergrund'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Graph ist Hintergrund des Layouts." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Graph ist Hintergrund"));
  });

  it("81. ConceptGuard erkennt 'Flarum ist Flextrawurst'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Flarum ist Flextrawurst." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "Flarum ist Flextrawurst")
    );
  });

  it("82. ConceptGuard erkennt 'Flarum ist Gegenwart'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Flarum ist Gegenwart der Welt." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Flarum ist Gegenwart"));
  });

  it("83. ConceptGuard erkennt 'Importierter Ursprung ist Live-Zustand'", () => {
    const r = checkConceptLanguage([
      {
        id: "t",
        text: "Importierter Ursprung ist Live-Zustand der Entität.",
      },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some(
        (v) => v.term === "Importierter Ursprung ist Live-Zustand"
      )
    );
  });

  it("84. ConceptGuard erkennt 'Replay erzeugt Events'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Replay erzeugt Events im Store." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "Replay erzeugt Events")
    );
  });

  it("85. ConceptGuard erkennt 'Replay aktiviert Slots'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Replay aktiviert Slots zur Laufzeit." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "Replay aktiviert Slots")
    );
  });

  it("86. ConceptGuard erkennt 'VisualMeaning ohne Herkunft'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "VisualMeaning ohne Herkunft ist erlaubt." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "VisualMeaning ohne Herkunft")
    );
  });

  it("87. ConceptGuard erkennt 'Worldview ist UI'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "Worldview ist UI für den Nutzer." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Worldview ist UI"));
  });

  it("88. ConceptGuard erkennt 'GraphModel ist Renderer'", () => {
    const r = checkConceptLanguage([
      { id: "t", text: "GraphModel ist Renderer der Szene." },
    ]);
    assert.equal(r.ok, false);
    assert.ok(
      r.violations.some((v) => v.term === "GraphModel ist Renderer")
    );
  });

  it("89. ConceptGuard akzeptiert erlaubte Sprache aus Ring 5/6/7", () => {
    const r = checkConceptLanguage([
      {
        id: "t",
        text:
          "Weltbedeutungshinweis mit Herkunft. Weltsicht-Graphmodell. " +
          "Replay-Spur. Herkunfts-Kandidat. Flarum-Vorphase. " +
          "Read-only Weltgraph-Modell. Bedeutungs-Hinweis mit Provenienz.",
      },
    ]);
    assert.equal(r.ok, true);
    assert.equal(r.violations.length, 0);
  });

  // ─── Strukturelle Invarianten ───

  it("90. EventStore bleibt nach VisualMeaning-Operationen unverändert", () => {
    buildVisualMeaningsFromSpine(spine, pack, importExtension);
    buildFlarumOriginMarkers(importExtension);
    assert.equal(store.length, 27);
  });

  it("91. EventStore bleibt nach Replay-Operationen unverändert", () => {
    buildAllSlotReplayTraces(spine.slots, pack.events, pack.replay_frames);
    buildReplayTimeWindow(pack.events, pack.replay_frames);
    buildAllVisualExplanations(
      visuals,
      pack,
      importExtension.activation_firewall
    );
    assert.equal(store.length, 27);
  });

  it("92. EventStore bleibt nach Graph-Build unverändert", () => {
    buildWorldviewGraph(spine, pack, importExtension, visuals, replayTraces);
    assert.equal(store.length, 27);
  });

  it("93. ActivationFirewall bleibt blockierend nach Ring 5/6/7", () => {
    assert.equal(importExtension.activation_firewall.blocked, true);
    assert.equal(
      importExtension.activation_firewall.allowed_slot_ids.length,
      0
    );
  });

  it("94. ready_for_ui bleibt false", () => {
    const consoleModel = buildReadOnlyConsoleModel(spine, importExtension);
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_ui, false);
  });

  it("95. ready_for_activation bleibt false", () => {
    const consoleModel = buildReadOnlyConsoleModel(spine, importExtension);
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_activation, false);
  });

  it("96. ready_for_real_import_files bleibt true", () => {
    const consoleModel = buildReadOnlyConsoleModel(spine, importExtension);
    const report = buildOSConvergenceReport(spine, importExtension, consoleModel);
    assert.equal(report.ready_for_real_import_files, true);
  });

  it("97. Slots bleiben unverändert nach allen Ring-5/6/7-Operationen", () => {
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
    assert.ok(spine.slots.every((s) => s.status !== "occupied"));
  });

  it("98. Kein Renderer, keine UI, kein Three.js, kein Cytoscape, keine AI, kein Postgres", () => {
    assert.equal(spine.runtime_readiness.uses_ai, false);
    assert.equal(spine.runtime_readiness.uses_ui, false);
    assert.equal(spine.runtime_readiness.uses_postgres, false);
    assert.equal(spine.runtime_readiness.uses_scheduler, false);
    assert.equal(worldviewGraph.uses_renderer, false);
    assert.equal(worldviewGraph.uses_ui, false);
  });

  it("99. Kein Einzug durch Ring 5/6/7 — alle Slots bleiben leer", () => {
    const slotNodes = worldviewGraph.nodes.filter(
      (n) => n.node_kind === "entity_slot_node"
    );
    assert.ok(
      slotNodes.every((n) => !n.label.toLowerCase().includes("bewohner"))
    );
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
    assert.equal(store.length, 27);
  });

  it("100. Gesamtbeweis Ring 5+6+7: Bedeutung → Replay → Graph, ohne Renderer, ohne Einzug", () => {
    assert.ok(visuals.length > 0, "Keine VisualMeanings");
    assert.ok(
      visuals.every((v) => v.is_decorative === false),
      "Dekorative Visuals vorhanden"
    );
    assert.ok(
      visuals.every(
        (v) =>
          v.source_event_ids.length > 0 ||
          v.source_slot_ids.length > 0 ||
          v.source_state_ids.length > 0 ||
          v.source_room_ids.length > 0
      ),
      "VisualMeaning ohne Herkunft"
    );
    assert.ok(
      replayTraces.every((t) => t.creates_new_events === false),
      "Replay erzeugt Events"
    );
    assert.ok(
      replayTraces.every((t) => t.activates_slots === false),
      "Replay aktiviert Slots"
    );
    assert.ok(
      visualExplanations.every((e) => e.can_trigger_activation === false),
      "Erklärung triggert Aktivierung"
    );
    assert.equal(worldviewGraph.is_read_only, true);
    assert.equal(worldviewGraph.uses_renderer, false);
    assert.equal(worldviewGraph.uses_ui, false);
    assert.equal(store.length, 27);
    assert.ok(spine.slots.every((s) => s.occupant_id === null));
  });
});
