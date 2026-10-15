import type { WorldCameraModel } from "./world_camera_model.ts";

export interface WorldCameraZoomPath {
  id: string;
  label: string;
  node_ids: string[];
  explanation: string;
}

export interface WorldCameraFocusGroup {
  id: string;
  label: string;
  node_ids: string[];
  layer: number;
}

export interface WorldCameraNavigation {
  entry_node_ids: string[];
  zoom_paths: WorldCameraZoomPath[];
  focus_groups: WorldCameraFocusGroup[];
}

export function buildWorldCameraNavigation(
  cameraModel: WorldCameraModel
): WorldCameraNavigation {
  const entitySlotIds = cameraModel.nodes
    .filter((n) => n.type === "entity_slot")
    .map((n) => n.id);
  const tickIds = cameraModel.nodes
    .filter((n) => n.type === "tick")
    .map((n) => n.id);
  const traceIds = cameraModel.nodes
    .filter((n) => n.type === "trace")
    .map((n) => n.id);

  const entry_node_ids =
    entitySlotIds.length > 0
      ? entitySlotIds
      : cameraModel.nodes.slice(0, 1).map((n) => n.id);

  const focus_groups: WorldCameraFocusGroup[] = [
    {
      id: "entity_slots",
      label: "Entitätsslots",
      node_ids: entitySlotIds,
      layer: 0,
    },
    {
      id: "world_ticks",
      label: "Weltpulse",
      node_ids: tickIds,
      layer: 1,
    },
    {
      id: "presence_traces",
      label: "Präsenzspuren",
      node_ids: traceIds,
      layer: 2,
    },
    {
      id: "audit_layer",
      label: "Audit/System",
      node_ids: [],
      layer: 3,
    },
  ];

  const zoom_paths: WorldCameraZoomPath[] = [
    {
      id: "overview_to_entities",
      label: "Übersicht → Entitätsslots",
      node_ids: entitySlotIds,
      explanation:
        "Navigiert von der Weltübersicht zu allen kanonischen Entitätsslots.",
    },
    {
      id: "overview_to_ticks",
      label: "Übersicht → Weltpulse",
      node_ids: tickIds,
      explanation: "Navigiert von der Weltübersicht zu allen Weltpuls-Knoten.",
    },
    {
      id: "tick_to_traces",
      label: "Weltpuls → Spuren",
      node_ids: [...tickIds, ...traceIds],
      explanation:
        "Navigiert von einem Weltpuls zu den ausgelösten Präsenzspuren.",
    },
    {
      id: "entity_to_trace_history",
      label: "Entitätsslot → Spurenhistorie",
      node_ids: [...entitySlotIds, ...traceIds],
      explanation:
        "Navigiert von einem Entitätsslot zu seiner vollständigen Spurenhistorie.",
    },
  ];

  return { entry_node_ids, zoom_paths, focus_groups };
}
