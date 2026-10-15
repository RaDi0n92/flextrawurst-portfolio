import type { WorldStartReadinessPack } from "./world_start_readiness_pack.ts";
import type { CleanStartDecisionModel } from "../start_decision/clean_start_decision_model.ts";

export interface WorldStartGateResult {
  blocked: boolean;
  reason: string;
  block_reasons: string[];
}

export function checkWorldStartGate(
  _pack: WorldStartReadinessPack,
  decision: CleanStartDecisionModel
): WorldStartGateResult {
  const block_reasons: string[] = [];

  if (decision.memory_policy === "undecided") {
    block_reasons.push(
      "memory_policy ist 'undecided'. Entscheidung erforderlich."
    );
  }
  if (decision.roster_policy === "undecided") {
    block_reasons.push(
      "roster_policy ist 'undecided'. Entscheidung erforderlich."
    );
  }
  if (decision.requires_admin_confirmation) {
    block_reasons.push(
      "requires_admin_confirmation ist true. Admin-Bestätigung fehlt."
    );
  }

  const blocked = block_reasons.length > 0;
  return {
    blocked,
    reason: blocked
      ? "WorldStartGate blockiert: " + block_reasons.join(" | ")
      : "WorldStartGate offen.",
    block_reasons,
  };
}
