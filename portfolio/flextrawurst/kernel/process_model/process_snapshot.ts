import type { ProcessBody } from "./process_types.ts";
import { CANONICAL_PROCESS_BODIES } from "./process_registry.ts";
import { buildTracesForSnapshot } from "./process_trace_builder.ts";

export interface ProcessSnapshot {
  readonly snapshot_version: 1;
  readonly is_read_only: true;
  readonly is_static: true;
  readonly created_at: string;
  readonly process_count: number;
  readonly active_claim_count: 0;
  readonly measured_count: number;
  readonly derived_count: number;
  readonly modelled_count: number;
  readonly blocked_count: number;
  readonly read_only_count: number;
  readonly replay_count: number;
  readonly unknown_count: number;
  readonly process_bodies: readonly ProcessBody[];
}

export function buildProcessSnapshot(
  bodies: readonly ProcessBody[],
  created_at = "2026-05-09T00:00:00.000Z"
): ProcessSnapshot {
  const measured = bodies.filter((b) => b.visibility.evidence === "measured");
  if (measured.length !== 0) {
    throw new Error(
      `buildProcessSnapshot: measured bodies not allowed in Ring 22. Found: ${measured.map((b) => b.id).join(", ")}`
    );
  }

  const evidenceCounts = (ev: string) =>
    bodies.filter((b) => b.visibility.evidence === ev).length;

  return {
    snapshot_version: 1,
    is_read_only: true,
    is_static: true,
    created_at,
    process_count: bodies.length,
    active_claim_count: 0,
    measured_count: 0,
    derived_count:
      evidenceCounts("derived_from_file") +
      evidenceCounts("derived_from_forum") +
      evidenceCounts("derived_from_event"),
    modelled_count: evidenceCounts("modelled"),
    blocked_count: evidenceCounts("blocked"),
    read_only_count: evidenceCounts("read_only"),
    replay_count: evidenceCounts("replay"),
    unknown_count: evidenceCounts("unknown"),
    process_bodies: bodies,
  };
}

export function buildCanonicalProcessSnapshot(
  created_at?: string
): ProcessSnapshot {
  const enriched = buildTracesForSnapshot(CANONICAL_PROCESS_BODIES);
  return buildProcessSnapshot(enriched, created_at);
}
