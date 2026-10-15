import type { WorldOSSpine } from "./world_os_spine.ts";

export interface WorldOSSpineExport {
  export_version: 1;
  created_from: "in_memory_os_spine";
  scenario_id: string;
  spine_version: 1;
  slot_count: number;
  occupied_count: number;
  provenance_record_count: number;
  all_activation_readiness_false: boolean;
  camera_ok: boolean;
  runtime_ok: boolean;
  runtime_deterministic: boolean;
  uses_ai: boolean;
  uses_ui: boolean;
  uses_postgres: boolean;
  uses_scheduler: boolean;
  concept_guard_ok: boolean;
  audit_ok: boolean;
  summary: string[];
}

export function buildWorldOSSpineExport(
  spine: WorldOSSpine
): WorldOSSpineExport {
  const allReadinessFalse = spine.activation_readiness.every(
    (r) => r.may_activate_now === false
  );

  return {
    export_version: 1,
    created_from: "in_memory_os_spine",
    scenario_id: spine.scenario_id,
    spine_version: spine.spine_version,
    slot_count: spine.slots.length,
    occupied_count: spine.slots.filter((s) => s.status === "occupied").length,
    provenance_record_count: spine.provenance.length,
    all_activation_readiness_false: allReadinessFalse,
    camera_ok: spine.camera_readiness.ok,
    runtime_ok: spine.runtime_readiness.ok,
    runtime_deterministic: spine.runtime_readiness.deterministic,
    uses_ai: spine.runtime_readiness.uses_ai,
    uses_ui: spine.runtime_readiness.uses_ui,
    uses_postgres: spine.runtime_readiness.uses_postgres,
    uses_scheduler: spine.runtime_readiness.uses_scheduler,
    concept_guard_ok: spine.concept_guard.ok,
    audit_ok: spine.audit_ok,
    summary: [...spine.summary],
  };
}

export function serializeWorldOSSpineExport(spine: WorldOSSpine): string {
  return JSON.stringify(buildWorldOSSpineExport(spine));
}
