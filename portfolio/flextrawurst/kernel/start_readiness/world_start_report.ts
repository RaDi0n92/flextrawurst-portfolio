import type { WorldStartReadinessPack } from "./world_start_readiness_pack.ts";
import type { WorldStartGateResult } from "./world_start_gate.ts";
import type { EntityContinuityDossier } from "../continuity/entity_continuity_dossier.ts";

export interface WorldStartReport {
  report_id: string;
  pack: WorldStartReadinessPack;
  gate_result: WorldStartGateResult;
  dossiers: EntityContinuityDossier[];
  summary: string;
  is_ready_to_execute: false;
}

export function buildWorldStartReport(params: {
  report_id: string;
  pack: WorldStartReadinessPack;
  gate_result: WorldStartGateResult;
  dossiers: EntityContinuityDossier[];
}): WorldStartReport {
  return {
    report_id: params.report_id,
    pack: params.pack,
    gate_result: params.gate_result,
    dossiers: params.dossiers,
    summary:
      `Pack mit ${params.pack.origin_archive_count} Herkunftseinträgen, ` +
      `${params.pack.memory_candidate_count} Erinnerungskandidaten, ` +
      `${params.pack.continuity_dossier_count} Kontinuitäts-Dossiers. ` +
      `Gate blockiert: ${params.gate_result.blocked}`,
    is_ready_to_execute: false,
  };
}
