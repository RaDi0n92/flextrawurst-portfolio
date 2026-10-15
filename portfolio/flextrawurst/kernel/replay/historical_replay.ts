import type { FlextrawurstEvent } from "../events/types.ts";
import type { EntityProjection } from "../projections/entity_projection.ts";
import { buildEntityProjection } from "../projections/entity_projection.ts";
import type { RenderHints } from "../../vme/meaning_projection.ts";
import { buildRenderHints } from "../../vme/meaning_projection.ts";
import { buildWorldProjection } from "../projections/world_projection.ts";
import type { WorldProjection } from "../projections/world_projection.ts";
import { buildWorldRenderHints } from "../../vme/world_meaning_projection.ts";

export interface ReplayResult {
  projection: EntityProjection;
  renderHints: RenderHints;
}

export function replay(
  events: readonly FlextrawurstEvent[],
  entityId: string,
  upToIndex: number
): ReplayResult {
  const slice = events.slice(0, upToIndex + 1);
  const projection = buildEntityProjection(entityId, slice);
  const renderHints = buildRenderHints(projection, slice);
  return { projection, renderHints };
}

export interface WorldReplayResult {
  worldProjection: WorldProjection;
  worldRenderHints: RenderHints[];
}

export function replayWorld(
  events: readonly FlextrawurstEvent[],
  upToIndex?: number
): WorldReplayResult {
  const slice =
    upToIndex !== undefined
      ? events.slice(0, upToIndex + 1)
      : [...events];
  const worldProjection = buildWorldProjection(slice);
  const worldRenderHints = buildWorldRenderHints(worldProjection, slice);
  return { worldProjection, worldRenderHints };
}
