import type { GovernanceSnapshot } from "./governance_snapshot.ts";

export interface GovernanceExport {
  export_version: 1;
  snapshot: GovernanceSnapshot;
}

export function buildGovernanceExport(snapshot: GovernanceSnapshot): GovernanceExport {
  return {
    export_version: 1,
    snapshot,
  };
}

export function serializeGovernanceExport(snapshot: GovernanceSnapshot): string {
  return JSON.stringify(buildGovernanceExport(snapshot), null, 2);
}
