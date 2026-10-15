import type { WorldOSSpine } from "../os_spine/world_os_spine.ts";
import type { WorldInspectionPack } from "../inspection/world_inspection_pack.ts";
import type { WorldOSSpineImportExtension } from "../os_spine/world_os_spine_import_extension.ts";
import type { VisualMeaning } from "../visual_meaning/visual_meaning_model.ts";
import type { WorldReplayTrace } from "../replay/world_replay_trace.ts";
import type {
  WorldviewGraph,
  WorldviewGraphNode,
  WorldviewGraphEdge,
} from "./worldview_graph_model.ts";

const FIXED_TS = "2026-01-01T00:00:00.000Z";

export function buildWorldviewGraph(
  spine: WorldOSSpine,
  pack: WorldInspectionPack,
  importExtension: WorldOSSpineImportExtension,
  visuals: VisualMeaning[],
  replayTraces: WorldReplayTrace[]
): WorldviewGraph {
  const nodes: WorldviewGraphNode[] = [];
  const edges: WorldviewGraphEdge[] = [];

  const roomNodeId = "node-room-world-main";
  nodes.push({
    node_id: roomNodeId,
    node_kind: "room_node",
    label: "Hauptraum der Welt",
    source_ids: [spine.scenario_id],
    origin_layer: "world_runtime",
    is_live_flextrawurst_state: false,
    requires_start_decision: false,
    explanation:
      "Standardraum. Enthält alle kanonischen Slots. Keine aktiven Bewohner.",
  });

  for (const slot of spine.slots) {
    const nodeId = `node-slot-${slot.slot_id}`;
    nodes.push({
      node_id: nodeId,
      node_kind: "entity_slot_node",
      label: `Entitätsslot ${slot.slot_id}`,
      source_ids: [slot.slot_id],
      origin_layer: "canonical_seed",
      is_live_flextrawurst_state: false,
      requires_start_decision: false,
      explanation: `Kanonischer Slot. Kein Einzug. Kein Wesen. Kein Bewohner.`,
    });

    edges.push({
      edge_id: `edge-room-slot-${slot.slot_id}`,
      edge_kind: "room_contains_slot",
      from_node_id: roomNodeId,
      to_node_id: nodeId,
      source_ids: [slot.slot_id],
      confidence: "structural",
      explanation: `Hauptraum enthält Slot ${slot.slot_id}.`,
    });
  }

  const seedEventBySlot = new Map<string, string>();
  for (const e of pack.events) {
    if (
      e.event_type === "system.seed_entity" &&
      typeof e.payload.entity_id === "string"
    ) {
      seedEventBySlot.set(e.payload.entity_id as string, e.event_id);
    }
  }

  const keyEvents = pack.events.filter(
    (e) =>
      e.event_type === "system.seed_entity" ||
      e.event_type === "system.tick"
  );

  for (const e of keyEvents) {
    const nodeId = `node-event-${e.event_id}`;
    const isLive = e.origin_type === "live_world" || e.origin_type === "manual_seed";
    nodes.push({
      node_id: nodeId,
      node_kind: "event_node",
      label: `${e.event_type} (${e.event_id})`,
      source_ids: [e.event_id],
      origin_layer: e.origin_type ?? "unknown",
      is_live_flextrawurst_state: isLive,
      requires_start_decision: false,
      explanation: `Event ${e.event_type} von ${e.actor_type}.`,
    });
  }

  for (const [slotId, seedEventId] of seedEventBySlot) {
    const slotNodeId = `node-slot-${slotId}`;
    const eventNodeId = `node-event-${seedEventId}`;
    const slotNodeExists = nodes.some((n) => n.node_id === slotNodeId);
    const eventNodeExists = nodes.some((n) => n.node_id === eventNodeId);

    if (slotNodeExists && eventNodeExists) {
      edges.push({
        edge_id: `edge-event-slot-${slotId}`,
        edge_kind: "event_affects_slot",
        from_node_id: eventNodeId,
        to_node_id: slotNodeId,
        source_ids: [seedEventId, slotId],
        confidence: "structural",
        explanation: `Seed-Event ${seedEventId} erzeugt Slot ${slotId}.`,
      });
    }
  }

  for (const mapping of importExtension.dry_run.mappings) {
    if (
      mapping.mapping_status === "matched_canonical_slot" &&
      mapping.slot_id !== null
    ) {
      const importNodeId = `node-import-${mapping.account_id}`;
      nodes.push({
        node_id: importNodeId,
        node_kind: "import_origin_node",
        label: `Flarum-Herkunft: ${mapping.account_id}`,
        source_ids: [mapping.account_id],
        origin_layer: "flarum_vorphase",
        is_live_flextrawurst_state: false,
        requires_start_decision: true,
        explanation:
          `Flarum-Import-Kandidat. Vorphase. Kein Einzug. Kein Bewohner.`,
      });

      const slotNodeId = `node-slot-${mapping.slot_id}`;
      edges.push({
        edge_id: `edge-origin-slot-${mapping.account_id}`,
        edge_kind: "origin_candidate_maps_to_slot",
        from_node_id: importNodeId,
        to_node_id: slotNodeId,
        source_ids: [mapping.account_id, mapping.slot_id],
        confidence: "structural",
        explanation: `Flarum-Account ${mapping.account_id} ist Import-Kandidat für Slot ${mapping.slot_id}.`,
      });

      edges.push({
        edge_id: `edge-slot-origin-${mapping.slot_id}`,
        edge_kind: "slot_has_origin",
        from_node_id: slotNodeId,
        to_node_id: importNodeId,
        source_ids: [mapping.slot_id, mapping.account_id],
        confidence: "structural",
        explanation: `Slot ${mapping.slot_id} hat Flarum-Herkunft ${mapping.account_id}.`,
      });
    }
  }

  for (const visual of visuals) {
    const visualNodeId = `node-visual-${visual.visual_id}`;
    nodes.push({
      node_id: visualNodeId,
      node_kind: "visual_meaning_node",
      label: `${visual.visual_kind}: ${visual.visual_id}`,
      source_ids: [
        ...visual.source_event_ids,
        ...visual.source_slot_ids,
        ...visual.source_state_ids,
        ...visual.source_room_ids,
      ],
      origin_layer: visual.origin_layer ?? "world_runtime",
      is_live_flextrawurst_state: visual.is_live_flextrawurst_state ?? true,
      requires_start_decision: visual.requires_start_decision ?? false,
      explanation: visual.meaning,
    });

    for (const eventId of visual.source_event_ids) {
      const eventNodeId = `node-event-${eventId}`;
      if (nodes.some((n) => n.node_id === eventNodeId)) {
        edges.push({
          edge_id: `edge-visual-event-${visual.visual_id}-${eventId}`,
          edge_kind: "visual_explains_event",
          from_node_id: visualNodeId,
          to_node_id: eventNodeId,
          source_ids: [visual.visual_id, eventId],
          confidence: "structural",
          explanation: `${visual.visual_kind} erklärt Event ${eventId}.`,
        });
      }
    }
  }

  for (const trace of replayTraces) {
    const traceNodeId = `node-trace-${trace.trace_id}`;
    nodes.push({
      node_id: traceNodeId,
      node_kind: "replay_trace_node",
      label: `Replay-Spur: ${trace.slot_id}`,
      source_ids: trace.event_ids,
      origin_layer: "replay_layer",
      is_live_flextrawurst_state: false,
      requires_start_decision: false,
      explanation: `Replay-Spur für Slot ${trace.slot_id}. Keine Seiteneffekte.`,
    });

    if (trace.event_ids.length > 0) {
      const firstEventId = trace.event_ids[0];
      const eventNodeId = `node-event-${firstEventId}`;
      if (nodes.some((n) => n.node_id === eventNodeId)) {
        edges.push({
          edge_id: `edge-trace-event-${trace.trace_id}-${firstEventId}`,
          edge_kind: "replay_references_event",
          from_node_id: traceNodeId,
          to_node_id: eventNodeId,
          source_ids: [trace.trace_id, firstEventId],
          confidence: "structural",
          explanation: `Replay-Spur ${trace.trace_id} referenziert Erstes Event ${firstEventId}.`,
        });
      }
    }
  }

  return {
    graph_id: `worldview-${spine.scenario_id}`,
    nodes,
    edges,
    is_read_only: true,
    uses_renderer: false,
    uses_ui: false,
    created_at: FIXED_TS,
  };
}
