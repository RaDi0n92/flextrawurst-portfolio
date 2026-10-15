import type { WorldCameraModel } from "./world_camera_model.ts";
import type { WorldCameraNavigation } from "./world_camera_navigation.ts";
import type { WorldTimeline } from "../timeline/world_timeline.ts";

export interface CameraReadinessReport {
  ok: boolean;
  clickable: boolean;
  zoomable: boolean;
  traceable: boolean;
  has_timeline: boolean;
  has_source_events: boolean;
  has_navigation_paths: boolean;
  missing: string[];
  notes: string[];
}

export function assessCameraReadiness(
  cameraModel: WorldCameraModel,
  navigation: WorldCameraNavigation,
  timeline: WorldTimeline
): CameraReadinessReport {
  const clickable = cameraModel.nodes.length > 0;
  const zoomable = navigation.zoom_paths.length > 0;
  const traceable =
    cameraModel.edges.length > 0 &&
    cameraModel.nodes.some((n) => n.source_event_ids.length > 0);
  const has_timeline = timeline.frames.length > 0;
  const has_source_events = cameraModel.nodes.some(
    (n) => n.source_event_ids.length > 0
  );
  const has_navigation_paths = navigation.zoom_paths.length > 0;

  const missing: string[] = [];
  if (!clickable) missing.push("camera_nodes");
  if (!zoomable) missing.push("zoom_paths");
  if (!traceable) missing.push("traceable_edges");
  if (!has_timeline) missing.push("timeline_frames");
  if (!has_navigation_paths) missing.push("navigation_paths");

  const ok =
    clickable && zoomable && traceable && has_timeline && has_navigation_paths;

  return {
    ok,
    clickable,
    zoomable,
    traceable,
    has_timeline,
    has_source_events,
    has_navigation_paths,
    missing,
    notes: [
      "Kein Renderer beteiligt.",
      "Kein Canvas, kein D3, kein Three.js.",
      "Nur Navigationsdaten für spätere Weltkamera.",
    ],
  };
}
