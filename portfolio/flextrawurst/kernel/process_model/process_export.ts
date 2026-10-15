import type { ProcessSnapshot } from "./process_snapshot.ts";

export function exportProcessSnapshotToJSON(snapshot: ProcessSnapshot): string {
  return JSON.stringify(snapshot, null, 2);
}
