import type { WorldProjection } from "../kernel/projections/world_projection.ts";
import type { FlextrawurstEvent } from "../kernel/events/types.ts";
import { buildRenderHints } from "./meaning_projection.ts";
import type { RenderHints } from "./meaning_projection.ts";

export function buildWorldRenderHints(
  worldProjection: WorldProjection,
  events: readonly FlextrawurstEvent[]
): RenderHints[] {
  return Object.values(worldProjection.entities).map((proj) =>
    buildRenderHints(proj, events)
  );
}
