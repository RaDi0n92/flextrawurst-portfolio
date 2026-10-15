import type { FlextrawurstEvent } from "../events/types.ts";
import type { WorldIntegrityReport } from "../integrity/world_integrity.ts";
import type { WorldTimeline } from "../timeline/world_timeline.ts";
import type { WorldSnapshot } from "../snapshots/world_snapshot.ts";
import type { WorldCameraModel } from "../world_camera/world_camera_model.ts";
import { checkWorldIntegrity } from "../integrity/world_integrity.ts";
import { buildWorldTimeline } from "../timeline/world_timeline.ts";
import { buildWorldSnapshot } from "../snapshots/world_snapshot.ts";
import { buildWorldCameraModel } from "../world_camera/world_camera_model.ts";

export interface WorldAudit {
  integrity: WorldIntegrityReport;
  timeline: WorldTimeline;
  snapshot: WorldSnapshot;
  camera_model: WorldCameraModel;
}

export function buildWorldAudit(
  events: readonly FlextrawurstEvent[]
): WorldAudit {
  const integrity = checkWorldIntegrity(events);
  const timeline = buildWorldTimeline(events);
  const snapshot = buildWorldSnapshot(events);
  const camera_model = buildWorldCameraModel(snapshot, timeline, integrity);

  return { integrity, timeline, snapshot, camera_model };
}
