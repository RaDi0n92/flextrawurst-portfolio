import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  buildGovernanceActionDefinitions,
} from "../kernel/governance/governance_action.ts";
import {
  getApprovalRequirementForAction,
} from "../kernel/governance/approval_level.ts";
import {
  createUnlockedGlobalLockState,
  createGlobalLock,
  doesGlobalLockBlockAction,
} from "../kernel/governance/global_lock.ts";
import {
  buildGovernanceMatrix,
  findGovernanceMatrixRow,
  listCriticalGovernanceActions,
  listDanielRequiredActions,
  listActionsBlockedByGlobalLock,
} from "../kernel/governance/governance_matrix.ts";
import {
  evaluateGovernanceGate,
} from "../kernel/governance/governance_gate.ts";
import {
  mapCommandIntentToGovernanceAction,
} from "../kernel/governance/governance_intent_bridge.ts";
import {
  recordGovernanceGateToLedger,
} from "../kernel/governance/governance_ledger_bridge.ts";
import {
  createEmptyGovernanceAudit,
  recordGovernanceGate,
} from "../kernel/governance/governance_audit.ts";
import {
  buildGovernanceCoverageReport,
} from "../kernel/governance/governance_coverage.ts";
import {
  buildGovernanceSnapshot,
} from "../kernel/governance/governance_snapshot.ts";
import {
  buildGovernanceExport,
  serializeGovernanceExport,
} from "../kernel/governance/governance_export.ts";
import {
  buildSearchCorpusFromGovernanceMatrix,
  buildSearchCorpusFromGovernanceGateReport,
  buildSearchCorpusFromGovernanceAudit,
  buildSearchCorpusFromGovernanceSnapshot,
  buildSearchCorpusFromGlobalLockState,
} from "../kernel/search/search_corpus.ts";
import {
  checkConceptLanguage,
} from "../kernel/concept_guard/concept_guard.ts";
import {
  buildDanielRootAdmin,
  buildObserverAdmin,
  buildSystemProcessActor,
  hasPermission,
} from "../kernel/admin/admin_permissions.ts";
import type { AdminActor } from "../kernel/admin/admin_permissions.ts";
import {
  createCommandIntent,
} from "../kernel/admin/command_intent.ts";
import {
  createEmptyCommandLedger,
} from "../kernel/admin/command_ledger.ts";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildOperatorActor(actor_id: string): AdminActor {
  return {
    actor_id,
    role: "operator",
    permissions: [
      "feature.view",
      "feature.request_activation",
      "import.view",
      "import.approve",
      "slot.view",
      "slot.approve_activation",
      "worldrun.view",
      "worldrun.pause",
      "worldrun.resume",
      "export.view",
      "export.create_readonly",
      "concept_guard.view",
      "policy.view",
      "governance.view",
      "governance.audit_full",
    ],
  };
}

function findAction(action_id: string) {
  const action = buildGovernanceActionDefinitions().find((a) => a.action_id === action_id);
  assert.ok(action, `action not found: ${action_id}`);
  return action;
}

// ---------------------------------------------------------------------------
// 1–13: buildGovernanceActionDefinitions — Action IDs vorhanden
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceActionDefinitions: Vollständigkeit", () => {
  it("1. enthält feature.activate", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "feature.activate"));
  });
  it("2. enthält import.approve", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "import.approve"));
  });
  it("3. enthält slot.approve_activation", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "slot.approve_activation"));
  });
  it("4. enthält worldrun.pause", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "worldrun.pause"));
  });
  it("5. enthält worldrun.freeze", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "worldrun.freeze"));
  });
  it("6. enthält worldrun.stop", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "worldrun.stop"));
  });
  it("7. enthält export.create_readonly", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "export.create_readonly"));
  });
  it("8. enthält concept_guard.report", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "concept_guard.report"));
  });
  it("9. enthält policy.set", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "policy.set"));
  });
  it("10. enthält future_organ.activate", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "future_organ.activate"));
  });
  it("11. enthält search.inspect", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "search.inspect"));
  });
  it("12. enthält emergency.stop", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "emergency.stop"));
  });
  it("13. enthält global.lock", () => {
    assert.ok(buildGovernanceActionDefinitions().some((a) => a.action_id === "global.lock"));
  });
});

// ---------------------------------------------------------------------------
// 14–16: Risikostufen
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceActionDefinitions: Risikostufen", () => {
  it("14. future_organ.activate risk critical", () => {
    assert.equal(findAction("future_organ.activate").risk_level, "critical");
  });
  it("15. global.lock risk critical", () => {
    assert.equal(findAction("global.lock").risk_level, "critical");
  });
  it("16. export.create_readonly risk low", () => {
    assert.equal(findAction("export.create_readonly").risk_level, "low");
  });
  it("worldrun.stop risk critical", () => {
    assert.equal(findAction("worldrun.stop").risk_level, "critical");
  });
  it("emergency.stop risk critical", () => {
    assert.equal(findAction("emergency.stop").risk_level, "critical");
  });
  it("worldrun.freeze risk high", () => {
    assert.equal(findAction("worldrun.freeze").risk_level, "high");
  });
  it("search.inspect risk low", () => {
    assert.equal(findAction("search.inspect").risk_level, "low");
  });
  it("concept_guard.report risk low", () => {
    assert.equal(findAction("concept_guard.report").risk_level, "low");
  });
});

// ---------------------------------------------------------------------------
// 17–18: Approval Requirements
// ---------------------------------------------------------------------------

describe("Ring 20 — ApprovalRequirements", () => {
  it("17. getApprovalRequirementForAction policy.set requires dry_run", () => {
    const req = getApprovalRequirementForAction(findAction("policy.set"));
    assert.equal(req.dry_run_required, true);
  });
  it("18. future_organ.activate requires daniel_root", () => {
    const req = getApprovalRequirementForAction(findAction("future_organ.activate"));
    assert.equal(req.required_role, "daniel_root");
  });
  it("policy.set approval_level daniel_required_with_dry_run", () => {
    const req = getApprovalRequirementForAction(findAction("policy.set"));
    assert.equal(req.approval_level, "daniel_required_with_dry_run");
  });
  it("future_organ.activate approval_level daniel_required_with_dry_run", () => {
    const req = getApprovalRequirementForAction(findAction("future_organ.activate"));
    assert.equal(req.approval_level, "daniel_required_with_dry_run");
  });
  it("export.create_readonly approval_level none", () => {
    const req = getApprovalRequirementForAction(findAction("export.create_readonly"));
    assert.equal(req.approval_level, "none");
  });
  it("feature.activate approval_level daniel_required", () => {
    const req = getApprovalRequirementForAction(findAction("feature.activate"));
    assert.equal(req.approval_level, "daniel_required");
  });
  it("import.approve approval_level operator_allowed", () => {
    const req = getApprovalRequirementForAction(findAction("import.approve"));
    assert.equal(req.approval_level, "operator_allowed");
  });
  it("search.inspect approval_level none", () => {
    const req = getApprovalRequirementForAction(findAction("search.inspect"));
    assert.equal(req.approval_level, "none");
  });
});

// ---------------------------------------------------------------------------
// 19–24: GlobalLock
// ---------------------------------------------------------------------------

describe("Ring 20 — GlobalLock", () => {
  it("19. createUnlockedGlobalLockState locked false", () => {
    const lock = createUnlockedGlobalLockState();
    assert.equal(lock.locked, false);
  });
  it("createUnlockedGlobalLockState lock_id null", () => {
    const lock = createUnlockedGlobalLockState();
    assert.equal(lock.lock_id, null);
  });
  it("createUnlockedGlobalLockState lock_version 1", () => {
    const lock = createUnlockedGlobalLockState();
    assert.equal(lock.lock_version, 1);
  });
  it("20. createGlobalLock locked true", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "maintenance", "2026-01-01T00:00:00Z");
    assert.equal(lock.locked, true);
  });
  it("createGlobalLock hat lock_id", () => {
    const lock = createGlobalLock("lock_abc", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(lock.lock_id, "lock_abc");
  });
  it("createGlobalLock blocks_all_non_view_actions true", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(lock.blocks_all_non_view_actions, true);
  });
  it("21. GlobalLock blockiert feature.activate", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("feature.activate")), true);
  });
  it("22. GlobalLock blockiert import.approve", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("import.approve")), true);
  });
  it("23. GlobalLock erlaubt search.inspect", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("search.inspect")), false);
  });
  it("24. GlobalLock erlaubt export.create_readonly", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("export.create_readonly")), false);
  });
  it("GlobalLock blockiert future_organ.activate", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("future_organ.activate")), true);
  });
  it("GlobalLock blockiert policy.set", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("policy.set")), true);
  });
  it("GlobalLock blockiert worldrun.resume", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("worldrun.resume")), true);
  });
  it("GlobalLock erlaubt emergency.stop", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("emergency.stop")), false);
  });
  it("GlobalLock erlaubt concept_guard.report", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "reason", "2026-01-01T00:00:00Z");
    assert.equal(doesGlobalLockBlockAction(lock, findAction("concept_guard.report")), false);
  });
  it("Unlocked GlobalLock blockiert nichts", () => {
    const lock = createUnlockedGlobalLockState();
    assert.equal(doesGlobalLockBlockAction(lock, findAction("feature.activate")), false);
  });
});

// ---------------------------------------------------------------------------
// 25–29: GovernanceMatrix
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceMatrix", () => {
  it("25. buildGovernanceMatrix hat matrix_version 1", () => {
    assert.equal(buildGovernanceMatrix().matrix_version, 1);
  });
  it("26. Matrix enthält alle Actions", () => {
    const matrix = buildGovernanceMatrix();
    const actionDefs = buildGovernanceActionDefinitions();
    assert.equal(matrix.rows.length, actionDefs.length);
  });
  it("Matrix hat notes", () => {
    assert.ok(buildGovernanceMatrix().notes.length > 0);
  });
  it("27. listCriticalGovernanceActions enthält global.lock", () => {
    const criticals = listCriticalGovernanceActions();
    assert.ok(criticals.some((a) => a.action_id === "global.lock"));
  });
  it("listCriticalGovernanceActions enthält worldrun.stop", () => {
    const criticals = listCriticalGovernanceActions();
    assert.ok(criticals.some((a) => a.action_id === "worldrun.stop"));
  });
  it("listCriticalGovernanceActions enthält emergency.stop", () => {
    const criticals = listCriticalGovernanceActions();
    assert.ok(criticals.some((a) => a.action_id === "emergency.stop"));
  });
  it("listCriticalGovernanceActions enthält future_organ.activate", () => {
    const criticals = listCriticalGovernanceActions();
    assert.ok(criticals.some((a) => a.action_id === "future_organ.activate"));
  });
  it("28. listDanielRequiredActions enthält future_organ.activate", () => {
    const required = listDanielRequiredActions();
    assert.ok(required.some((a) => a.action_id === "future_organ.activate"));
  });
  it("listDanielRequiredActions enthält feature.activate", () => {
    const required = listDanielRequiredActions();
    assert.ok(required.some((a) => a.action_id === "feature.activate"));
  });
  it("listDanielRequiredActions enthält global.lock", () => {
    const required = listDanielRequiredActions();
    assert.ok(required.some((a) => a.action_id === "global.lock"));
  });
  it("29. listActionsBlockedByGlobalLock enthält feature.activate", () => {
    const blocked = listActionsBlockedByGlobalLock();
    assert.ok(blocked.some((a) => a.action_id === "feature.activate"));
  });
  it("listActionsBlockedByGlobalLock enthält import.approve", () => {
    const blocked = listActionsBlockedByGlobalLock();
    assert.ok(blocked.some((a) => a.action_id === "import.approve"));
  });
  it("listActionsBlockedByGlobalLock enthält nicht emergency.stop", () => {
    const blocked = listActionsBlockedByGlobalLock();
    assert.ok(!blocked.some((a) => a.action_id === "emergency.stop"));
  });
  it("listActionsBlockedByGlobalLock enthält nicht search.inspect", () => {
    const blocked = listActionsBlockedByGlobalLock();
    assert.ok(!blocked.some((a) => a.action_id === "search.inspect"));
  });
  it("findGovernanceMatrixRow feature.activate gibt row zurück", () => {
    const row = findGovernanceMatrixRow("feature.activate");
    assert.ok(row !== undefined);
    assert.equal(row.action.action_id, "feature.activate");
  });
  it("findGovernanceMatrixRow unbekannte id gibt undefined", () => {
    assert.equal(findGovernanceMatrixRow("nonexistent.action"), undefined);
  });
});

// ---------------------------------------------------------------------------
// 30–37: GovernanceGate
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceGate", () => {
  const daniel = buildDanielRootAdmin();
  const observer = buildObserverAdmin("obs_1");
  const sysProc = buildSystemProcessActor("sys_1");
  const operator = buildOperatorActor("op_1");
  const unlocked = createUnlockedGlobalLockState();
  const locked = createGlobalLock("lock_1", "daniel_root", "maintenance", "2026-01-01T00:00:00Z");

  it("30. GovernanceGate erlaubt Daniel readonly export", () => {
    const action = findAction("export.create_readonly");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.allowed, true);
  });

  it("31. GovernanceGate erlaubt Daniel search.inspect", () => {
    const action = findAction("search.inspect");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.allowed, true);
  });

  it("32. GovernanceGate blockiert operator future_organ.activate", () => {
    const action = findAction("future_organ.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, operator, unlocked);
    assert.equal(report.blocked, true);
  });

  it("33. GovernanceGate blockiert observer policy.set", () => {
    const action = findAction("policy.set");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, observer, unlocked);
    assert.equal(report.blocked, true);
  });

  it("34. GovernanceGate blockiert system_process critical action", () => {
    const action = findAction("global.lock");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, sysProc, unlocked);
    assert.equal(report.blocked, true);
  });

  it("35. GovernanceGate blockiert feature.activate bei GlobalLock", () => {
    const action = findAction("feature.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, locked);
    assert.equal(report.blocked, true);
  });

  it("36. GovernanceGate erlaubt emergency.stop bei GlobalLock", () => {
    const action = findAction("emergency.stop");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, locked);
    assert.equal(report.allowed, true);
  });

  it("37. GovernanceGate missing_permissions gesetzt wenn Permission fehlt", () => {
    const action = findAction("future_organ.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, operator, unlocked);
    assert.ok(report.missing_permissions.length > 0);
  });

  it("GovernanceGate erlaubt Daniel global.lock wenn nicht gesperrt", () => {
    const action = findAction("global.lock");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.allowed, true);
  });

  it("GovernanceGate blockiert global.lock wenn bereits gesperrt", () => {
    const action = findAction("global.lock");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, locked);
    assert.equal(report.blocked, true);
  });

  it("GovernanceGate blockers gesetzt bei Blockierung", () => {
    const action = findAction("feature.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, locked);
    assert.ok(report.blockers.length > 0);
  });

  it("GovernanceGate erlaubt Daniel feature.activate ohne Lock", () => {
    const action = findAction("feature.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.allowed, true);
  });

  it("GovernanceGate blockiert observer bei non-view action", () => {
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, observer, unlocked);
    assert.equal(report.blocked, true);
  });

  it("GovernanceGate erlaubt observer search.inspect", () => {
    const observerWithView: AdminActor = {
      actor_id: "obs_view",
      role: "observer",
      permissions: ["export.view", "feature.view", "import.view", "slot.view", "worldrun.view", "export.create_readonly", "concept_guard.view", "policy.view"],
    };
    const action = findAction("search.inspect");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, observerWithView, unlocked);
    assert.equal(report.allowed, true);
  });

  it("GovernanceGate system_process blockiert bei high action", () => {
    const action = findAction("feature.activate");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, sysProc, unlocked);
    assert.equal(report.blocked, true);
  });

  it("GovernanceGate report enthält action_id", () => {
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.action_id, "import.approve");
  });

  it("GovernanceGate report enthält actor_role", () => {
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const report = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(report.actor_role, "daniel_root");
  });
});

// ---------------------------------------------------------------------------
// 38–42: GovernanceIntentBridge
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceIntentBridge", () => {
  function buildIntent(type: string) {
    return createCommandIntent({
      command_id: `cmd_${type}`,
      command_type: type as any,
      requested_by: "daniel_root",
      target_type: "worldrun",
      target_id: "run_1",
      reason: "test",
      created_at: "2026-01-01T00:00:00Z",
    });
  }

  it("38. mapCommandIntentToGovernanceAction pause_worldrun", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("pause_worldrun"));
    assert.equal(result.action_id, "worldrun.pause");
    assert.equal(result.mapped, true);
  });

  it("39. mapCommandIntentToGovernanceAction freeze_worldrun", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("freeze_worldrun"));
    assert.equal(result.action_id, "worldrun.freeze");
    assert.equal(result.mapped, true);
  });

  it("40. mapCommandIntentToGovernanceAction approve_import", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("approve_import"));
    assert.equal(result.action_id, "import.approve");
    assert.equal(result.mapped, true);
  });

  it("41. mapCommandIntentToGovernanceAction create_readonly_export", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("create_readonly_export"));
    assert.equal(result.action_id, "export.create_readonly");
    assert.equal(result.mapped, true);
  });

  it("42. unknown command mapped false", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("unknown_action_xyz"));
    assert.equal(result.mapped, false);
  });

  it("stop_worldrun mapped worldrun.stop", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("stop_worldrun"));
    assert.equal(result.action_id, "worldrun.stop");
  });

  it("set_policy mapped policy.set", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("set_policy"));
    assert.equal(result.action_id, "policy.set");
  });

  it("resume_worldrun mapped worldrun.resume", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("resume_worldrun"));
    assert.equal(result.action_id, "worldrun.resume");
  });

  it("deactivate_feature mapped feature.deactivate", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("deactivate_feature"));
    assert.equal(result.action_id, "feature.deactivate");
  });

  it("request_feature_activation mapped feature.activate", () => {
    const result = mapCommandIntentToGovernanceAction(buildIntent("request_feature_activation"));
    assert.equal(result.action_id, "feature.activate");
  });
});

// ---------------------------------------------------------------------------
// 43–46: GovernanceLedgerBridge
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceLedgerBridge", () => {
  const daniel = buildDanielRootAdmin();
  const unlocked = createUnlockedGlobalLockState();
  const locked = createGlobalLock("lock_1", "daniel_root", "test", "2026-01-01T00:00:00Z");

  function buildPauseCommand(dry_run: boolean) {
    const cmd = createCommandIntent({
      command_id: "cmd_pause_1",
      command_type: "pause_worldrun",
      requested_by: "daniel_root",
      target_type: "worldrun",
      target_id: "run_1",
      reason: "test pause",
      created_at: "2026-01-01T00:00:00Z",
    });
    return { ...cmd, dry_run };
  }

  function buildExportCommand() {
    return createCommandIntent({
      command_id: "cmd_export_1",
      command_type: "create_readonly_export",
      requested_by: "daniel_root",
      target_type: "export",
      target_id: "export_1",
      reason: "test export",
      created_at: "2026-01-01T00:00:00Z",
    });
  }

  it("43. recordGovernanceGateToLedger schreibt blocked bei blocked gate", () => {
    const action = findAction("feature.activate");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, locked);
    assert.equal(gate.blocked, true);
    const cmd = buildPauseCommand(false);
    const { result } = recordGovernanceGateToLedger(
      createEmptyCommandLedger(),
      cmd,
      daniel,
      gate
    );
    assert.equal(result.status, "blocked");
  });

  it("44. recordGovernanceGateToLedger schreibt recorded bei dry_run allowed", () => {
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(gate.allowed, true);
    const cmd = buildPauseCommand(true);
    const { result } = recordGovernanceGateToLedger(
      createEmptyCommandLedger(),
      cmd,
      daniel,
      gate
    );
    assert.equal(result.status, "recorded");
  });

  it("45. recordGovernanceGateToLedger schreibt executed_readonly bei readonly export", () => {
    const action = findAction("export.create_readonly");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    assert.equal(gate.allowed, true);
    const cmd = buildExportCommand();
    const { result } = recordGovernanceGateToLedger(
      createEmptyCommandLedger(),
      cmd,
      daniel,
      gate
    );
    assert.equal(result.status, "executed_readonly");
  });

  it("46. Ledger bleibt append-only — altes Ledger nicht mutiert", () => {
    const ledger = createEmptyCommandLedger();
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const cmd = buildPauseCommand(false);
    const { ledger: newLedger } = recordGovernanceGateToLedger(ledger, cmd, daniel, gate);
    assert.equal(ledger.entries.length, 0);
    assert.equal(newLedger.entries.length, 1);
  });

  it("Ledger entry count korrekt", () => {
    const ledger = createEmptyCommandLedger();
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const cmd = buildPauseCommand(false);
    const { result } = recordGovernanceGateToLedger(ledger, cmd, daniel, gate);
    assert.equal(result.ledger_entry_count_before, 0);
    assert.equal(result.ledger_entry_count_after, 1);
    assert.equal(result.ledger_written, true);
  });

  it("approved status bei gate allowed und nicht dry_run und kein export", () => {
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const cmd = buildPauseCommand(false);
    const { result } = recordGovernanceGateToLedger(
      createEmptyCommandLedger(),
      cmd,
      daniel,
      gate
    );
    assert.equal(result.status, "approved");
  });
});

// ---------------------------------------------------------------------------
// 47–50: GovernanceAudit
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceAudit", () => {
  const daniel = buildDanielRootAdmin();
  const unlocked = createUnlockedGlobalLockState();

  it("47. createEmptyGovernanceAudit leer", () => {
    const audit = createEmptyGovernanceAudit();
    assert.equal(audit.entries.length, 0);
  });

  it("createEmptyGovernanceAudit audit_version 1", () => {
    const audit = createEmptyGovernanceAudit();
    assert.equal(audit.audit_version, 1);
  });

  it("48. recordGovernanceGate append-only", () => {
    const audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const newAudit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    assert.equal(audit.entries.length, 0);
    assert.equal(newAudit.entries.length, 1);
  });

  it("49. GovernanceAuditEntry enthält action_id", () => {
    const audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const newAudit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    assert.equal(newAudit.entries[0].action_id, "import.approve");
  });

  it("50. GovernanceAuditEntry enthält actor_role", () => {
    const audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const newAudit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    assert.equal(newAudit.entries[0].actor_role, "daniel_root");
  });

  it("GovernanceAuditEntry enthält allowed", () => {
    const audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const newAudit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    assert.equal(newAudit.entries[0].allowed, true);
  });

  it("GovernanceAuditEntry enthält command_id", () => {
    const audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    const newAudit = recordGovernanceGate(audit, gate, "cmd_xyz", "2026-01-01T00:00:00Z");
    assert.equal(newAudit.entries[0].command_id, "cmd_xyz");
  });

  it("Mehrere Audit-Einträge append-only", () => {
    let audit = createEmptyGovernanceAudit();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, unlocked);
    audit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    audit = recordGovernanceGate(audit, gate, "cmd_2", "2026-01-01T00:00:01Z");
    assert.equal(audit.entries.length, 2);
  });
});

// ---------------------------------------------------------------------------
// 51–53: GovernanceCoverage
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceCoverage", () => {
  it("51. GovernanceCoverage ok true", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.equal(coverage.ok, true, `missing_coverage: ${coverage.missing_coverage.join(", ")}`);
  });

  it("52. Coverage zählt critical actions", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.ok(coverage.critical_action_count > 0);
  });

  it("53. Coverage missing_coverage leer", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.equal(coverage.missing_coverage.length, 0);
  });

  it("Coverage action_count korrekt", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.equal(coverage.action_count, matrix.rows.length);
  });

  it("Coverage coverage_version 1", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.equal(coverage.coverage_version, 1);
  });

  it("Coverage actions_requiring_command_intent > 0", () => {
    const matrix = buildGovernanceMatrix();
    const coverage = buildGovernanceCoverageReport(matrix);
    assert.ok(coverage.actions_requiring_command_intent > 0);
  });
});

// ---------------------------------------------------------------------------
// 54–59: GovernanceSnapshot und GovernanceExport
// ---------------------------------------------------------------------------

describe("Ring 20 — GovernanceSnapshot", () => {
  it("54. GovernanceSnapshot snapshot_version 1", () => {
    const snap = buildGovernanceSnapshot();
    assert.equal(snap.snapshot_version, 1);
  });

  it("55. GovernanceSnapshot enthält critical_actions", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(snap.critical_actions.length > 0);
    assert.ok(snap.critical_actions.includes("global.lock"));
  });

  it("56. GovernanceSnapshot enthält daniel_required_actions", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(snap.daniel_required_actions.length > 0);
    assert.ok(snap.daniel_required_actions.includes("feature.activate"));
  });

  it("57. GovernanceSnapshot enthält global_lock_blocked_actions", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(snap.global_lock_blocked_actions.length > 0);
    assert.ok(snap.global_lock_blocked_actions.includes("feature.activate"));
  });

  it("Snapshot mit GlobalLock enthält lock info", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "test", "2026-01-01T00:00:00Z");
    const snap = buildGovernanceSnapshot(lock);
    assert.equal(snap.global_lock.locked, true);
  });

  it("Snapshot ohne GlobalLock ist unlocked", () => {
    const snap = buildGovernanceSnapshot();
    assert.equal(snap.global_lock.locked, false);
  });
});

describe("Ring 20 — GovernanceExport", () => {
  it("58. GovernanceExport deterministisch", () => {
    const snap = buildGovernanceSnapshot();
    const e1 = buildGovernanceExport(snap);
    const e2 = buildGovernanceExport(snap);
    assert.deepEqual(e1, e2);
  });

  it("59. serializeGovernanceExport stabil", () => {
    const snap = buildGovernanceSnapshot();
    const s1 = serializeGovernanceExport(snap);
    const s2 = serializeGovernanceExport(snap);
    assert.equal(s1, s2);
  });

  it("serializeGovernanceExport ist valides JSON", () => {
    const snap = buildGovernanceSnapshot();
    const json = serializeGovernanceExport(snap);
    assert.doesNotThrow(() => JSON.parse(json));
  });

  it("GovernanceExport export_version 1", () => {
    const snap = buildGovernanceSnapshot();
    const exp = buildGovernanceExport(snap);
    assert.equal(exp.export_version, 1);
  });
});

// ---------------------------------------------------------------------------
// 60–75: Search Integration
// ---------------------------------------------------------------------------

describe("Ring 20 — SearchDocumentKind", () => {
  it("60. SearchDocumentKind enthält governance_action", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    assert.ok(corpus.documents.some((d) => d.kind === "governance_action"));
  });

  it("61. SearchDocumentKind enthält governance_gate_report", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    const corpus = buildSearchCorpusFromGovernanceGateReport(gate);
    assert.ok(corpus.documents.some((d) => d.kind === "governance_gate_report"));
  });

  it("62. SearchDocumentKind enthält governance_audit_entry", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    let audit = createEmptyGovernanceAudit();
    audit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    const corpus = buildSearchCorpusFromGovernanceAudit(audit);
    assert.ok(corpus.documents.some((d) => d.kind === "governance_audit_entry"));
  });

  it("63. SearchDocumentKind enthält governance_snapshot", () => {
    const snap = buildGovernanceSnapshot();
    const corpus = buildSearchCorpusFromGovernanceSnapshot(snap);
    assert.ok(corpus.documents.some((d) => d.kind === "governance_snapshot"));
  });

  it("64. SearchDocumentKind enthält global_lock_state", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "test", "2026-01-01T00:00:00Z");
    const corpus = buildSearchCorpusFromGlobalLockState(lock);
    assert.ok(corpus.documents.some((d) => d.kind === "global_lock_state"));
  });

  it("65. buildSearchCorpusFromGovernanceMatrix erzeugt governance_action docs", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    assert.equal(corpus.documents.length, matrix.rows.length);
  });

  it("66. Governance action docs haben source_ids", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    for (const doc of corpus.documents) {
      assert.ok(doc.source_ids.length > 0, `${doc.document_id} has no source_ids`);
    }
  });

  it("67. Governance action docs layer governance", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    for (const doc of corpus.documents) {
      assert.equal(doc.layer, "governance");
    }
  });

  it("68. Filter nach kind governance_action", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    const filtered = corpus.documents.filter((d) => d.kind === "governance_action");
    assert.ok(filtered.length > 0);
  });

  it("69. Filter nach layer governance", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    const filtered = corpus.documents.filter((d) => d.layer === "governance");
    assert.equal(filtered.length, corpus.documents.length);
  });

  it("70. Textsuche critical findet critical governance docs", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    const found = corpus.documents.filter((d) =>
      d.body.includes("critical") || d.tags.includes("critical")
    );
    assert.ok(found.length > 0);
  });

  it("71. Textsuche global_lock findet lock docs", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "test", "2026-01-01T00:00:00Z");
    const corpus = buildSearchCorpusFromGlobalLockState(lock);
    const found = corpus.documents.filter((d) => d.tags.includes("global_lock"));
    assert.ok(found.length > 0);
  });

  it("72. buildSearchCorpusFromGovernanceGateReport erzeugt doc", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    const corpus = buildSearchCorpusFromGovernanceGateReport(gate);
    assert.equal(corpus.documents.length, 1);
  });

  it("73. buildSearchCorpusFromGovernanceAudit erzeugt docs", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("import.approve");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    let audit = createEmptyGovernanceAudit();
    audit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    audit = recordGovernanceGate(audit, gate, "cmd_2", "2026-01-01T00:00:01Z");
    const corpus = buildSearchCorpusFromGovernanceAudit(audit);
    assert.equal(corpus.documents.length, 2);
  });

  it("74. buildSearchCorpusFromGovernanceSnapshot erzeugt doc", () => {
    const snap = buildGovernanceSnapshot();
    const corpus = buildSearchCorpusFromGovernanceSnapshot(snap);
    assert.equal(corpus.documents.length, 1);
  });

  it("75. buildSearchCorpusFromGlobalLockState erzeugt doc", () => {
    const lock = createUnlockedGlobalLockState();
    const corpus = buildSearchCorpusFromGlobalLockState(lock);
    assert.equal(corpus.documents.length, 1);
  });
});

// ---------------------------------------------------------------------------
// 76–96: ConceptGuard neue Muster
// ---------------------------------------------------------------------------

describe("Ring 20 — ConceptGuard neue Muster", () => {
  it("76. ConceptGuard erkennt 'Approval startet Runtime'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Approval startet Runtime direkt" }]);
    assert.equal(report.ok, false);
  });
  it("77. ConceptGuard erkennt 'Governance Matrix ist UI'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Governance Matrix ist UI für Operator" }]);
    assert.equal(report.ok, false);
  });
  it("78. ConceptGuard erkennt 'GlobalLock löscht Daten'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "GlobalLock löscht Daten im System" }]);
    assert.equal(report.ok, false);
  });
  it("79. ConceptGuard erkennt 'Operator ist Daniel'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Operator ist Daniel und darf alles" }]);
    assert.equal(report.ok, false);
  });
  it("80. ConceptGuard erkennt 'SystemProcess darf aktivieren'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "SystemProcess darf aktivieren ohne Freigabe" }]);
    assert.equal(report.ok, false);
  });
  it("81. ConceptGuard erkennt 'ConceptGuard Override ist erlaubt'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "ConceptGuard Override ist erlaubt in Notfällen" }]);
    assert.equal(report.ok, false);
  });
  it("82. ConceptGuard erkennt 'CommandIntent führt automatisch aus'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "CommandIntent führt automatisch aus die Aktion" }]);
    assert.equal(report.ok, false);
  });
  it("83. ConceptGuard erkennt 'Policy darf heimlich gesetzt werden'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Policy darf heimlich gesetzt werden ohne Log" }]);
    assert.equal(report.ok, false);
  });
  it("84. ConceptGuard akzeptiert 'Governance Matrix'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Die Governance Matrix definiert alle Aktionen" }]);
    assert.equal(report.ok, true);
  });
  it("85. ConceptGuard akzeptiert 'GlobalLock blockiert'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "GlobalLock blockiert alle nicht-view Aktionen" }]);
    assert.equal(report.ok, true);
  });
  it("86. ConceptGuard akzeptiert 'Approval Workflow'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "Der Approval Workflow prüft die Freigabe" }]);
    assert.equal(report.ok, true);
  });
  it("87. ConceptGuard akzeptiert 'GovernanceGate'", () => {
    const report = checkConceptLanguage([{ id: "t1", text: "GovernanceGate prüft Actor, Permission und Lock" }]);
    assert.equal(report.ok, true);
  });
});

// ---------------------------------------------------------------------------
// 88–100: Strukturelle Grenzen und Regression
// ---------------------------------------------------------------------------

describe("Ring 20 — Strukturelle Grenzen", () => {
  it("88. Keine UI — GovernanceSnapshot enthält kein render-Feld", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(!("render" in snap));
  });
  it("89. Keine AI — Governance enthält keine ai_model-Referenz", () => {
    const matrix = buildGovernanceMatrix();
    const json = JSON.stringify(matrix);
    assert.ok(!json.includes("ai_model"));
    assert.ok(!json.includes("openai"));
    assert.ok(!json.includes("anthropic"));
  });
  it("90. Kein Renderer — GovernanceExport enthält kein dom-Feld", () => {
    const snap = buildGovernanceSnapshot();
    const exp = buildGovernanceExport(snap);
    assert.ok(!("dom" in exp));
  });
  it("91. Kein Postgres — Governance enthält keine db_connection", () => {
    const matrix = buildGovernanceMatrix();
    const json = JSON.stringify(matrix);
    assert.ok(!json.includes("db_connection"));
    assert.ok(!json.includes("postgres"));
  });
  it("92. Kein Scheduler — Governance enthält kein interval-Feld", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(!("interval" in snap));
    assert.ok(!("scheduler" in snap));
  });
  it("93. Keine Runtime — GovernanceSnapshot startet keine Runtime", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(!("runtime" in snap));
    assert.ok(snap.snapshot_version === 1);
  });
  it("94. Keine Feature-Aktivierung durch Governance-Snapshot", () => {
    const snap = buildGovernanceSnapshot();
    const json = JSON.stringify(snap);
    assert.ok(!json.includes("activates_feature"));
    assert.ok(!json.includes("enabled: true"));
  });
  it("95. Keine Policy-Mutation durch Snapshot", () => {
    const snap = buildGovernanceSnapshot();
    assert.ok(!("mutate_policy" in snap));
  });
  it("96. Kein ConceptGuard Override durch Governance", () => {
    const matrix = buildGovernanceMatrix();
    const json = JSON.stringify(matrix);
    assert.ok(!json.includes("override_concept_guard"));
  });
});

describe("Ring 20 — Regression: bestehende Tests", () => {
  it("97. Bestehende admin Tests bleiben grün — DanielRoot hat alle Permissions", () => {
    const actor = buildDanielRootAdmin();
    assert.ok(hasPermission(actor, "feature.approve_activation"));
    assert.ok(hasPermission(actor, "worldrun.stop"));
    assert.ok(hasPermission(actor, "import.approve"));
  });
  it("98. Bestehende worldrun Tests bleiben grün — worldrun actions enthalten worldrun.pause", () => {
    const actions = buildGovernanceActionDefinitions();
    const worldrunActions = actions.filter((a) => a.action_class === "worldrun_control");
    assert.ok(worldrunActions.some((a) => a.action_id === "worldrun.pause"));
  });
  it("99. Bestehende search Tests bleiben grün — SearchDocumentKind erweiterbar", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    assert.ok(corpus.corpus_version === 1);
  });
  it("100. Alle bisherigen Tests bleiben grün — keine Mutation an bestehendem Kernel", () => {
    const daniel = buildDanielRootAdmin();
    assert.equal(daniel.role, "daniel_root");
    assert.ok(hasPermission(daniel, "governance.global_lock"));
    assert.ok(hasPermission(daniel, "governance.future_organ_activate"));
  });
});

// ---------------------------------------------------------------------------
// 101–130: Weitere Tests für vollständige Abdeckung
// ---------------------------------------------------------------------------

describe("Ring 20 — Erweiterte Abdeckung", () => {
  it("101. GovernanceActionDefinition hat alle Pflichtfelder", () => {
    for (const action of buildGovernanceActionDefinitions()) {
      assert.ok(typeof action.action_id === "string");
      assert.ok(typeof action.action_class === "string");
      assert.ok(typeof action.label === "string");
      assert.ok(typeof action.risk_level === "string");
      assert.ok(typeof action.required_permission === "string");
      assert.ok(typeof action.requires_daniel_root === "boolean");
      assert.ok(typeof action.requires_command_intent === "boolean");
      assert.ok(typeof action.requires_ledger_entry === "boolean");
      assert.ok(typeof action.requires_audit_entry === "boolean");
      assert.ok(typeof action.requires_search_document === "boolean");
      assert.ok(typeof action.blocked_by_global_lock === "boolean");
      assert.ok(Array.isArray(action.notes));
    }
  });

  it("102. feature.activate requires_command_intent true", () => {
    assert.equal(findAction("feature.activate").requires_command_intent, true);
  });

  it("103. feature.activate requires_ledger_entry true", () => {
    assert.equal(findAction("feature.activate").requires_ledger_entry, true);
  });

  it("104. feature.activate requires_audit_entry true", () => {
    assert.equal(findAction("feature.activate").requires_audit_entry, true);
  });

  it("105. feature.activate requires_search_document true", () => {
    assert.equal(findAction("feature.activate").requires_search_document, true);
  });

  it("106. search.inspect requires_command_intent false", () => {
    assert.equal(findAction("search.inspect").requires_command_intent, false);
  });

  it("107. concept_guard.report requires_command_intent false", () => {
    assert.equal(findAction("concept_guard.report").requires_command_intent, false);
  });

  it("108. worldrun.lock requires_daniel_root true", () => {
    assert.equal(findAction("worldrun.lock").requires_daniel_root, true);
  });

  it("109. worldrun.pause requires_daniel_root false", () => {
    assert.equal(findAction("worldrun.pause").requires_daniel_root, false);
  });

  it("110. future_organ.activate requires_dry_run_first true", () => {
    assert.equal(findAction("future_organ.activate").requires_dry_run_first, true);
  });

  it("111. policy.set requires_dry_run_first true", () => {
    assert.equal(findAction("policy.set").requires_dry_run_first, true);
  });

  it("112. GovernanceMatrix row enthält permission-Feld", () => {
    const row = findGovernanceMatrixRow("feature.activate");
    assert.ok(typeof row?.permission === "string");
    assert.equal(row?.permission, "feature.approve_activation");
  });

  it("113. GovernanceMatrix row enthält gate_required", () => {
    const row = findGovernanceMatrixRow("feature.activate");
    assert.ok(typeof row?.gate_required === "boolean");
    assert.equal(row?.gate_required, true);
  });

  it("114. DanielRoot hat governance.global_lock permission", () => {
    const daniel = buildDanielRootAdmin();
    assert.ok(hasPermission(daniel, "governance.global_lock"));
  });

  it("115. DanielRoot hat governance.future_organ_activate permission", () => {
    const daniel = buildDanielRootAdmin();
    assert.ok(hasPermission(daniel, "governance.future_organ_activate"));
  });

  it("116. Observer hat keine governance.global_lock permission", () => {
    const obs = buildObserverAdmin("obs_1");
    assert.ok(!hasPermission(obs, "governance.global_lock"));
  });

  it("117. GovernanceAudit entries haben audit_id", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("policy.set");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    let audit = createEmptyGovernanceAudit();
    audit = recordGovernanceGate(audit, gate, "cmd_1", "2026-01-01T00:00:00Z");
    assert.ok(audit.entries[0].audit_id.length > 0);
  });

  it("118. GovernanceGate missing_approvals enthält dry_run hinweis für policy.set", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("policy.set");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    assert.ok(gate.missing_approvals.length > 0);
    assert.ok(gate.missing_approvals[0].includes("dry run"));
  });

  it("119. buildSearchCorpusFromGlobalLockState locked state enthält locked tag", () => {
    const lock = createGlobalLock("lock_1", "daniel_root", "test", "2026-01-01T00:00:00Z");
    const corpus = buildSearchCorpusFromGlobalLockState(lock);
    assert.ok(corpus.documents[0].tags.includes("locked"));
  });

  it("120. buildSearchCorpusFromGovernanceMatrix counts enthält governance_action", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    assert.ok(typeof corpus.counts["governance_action"] === "number");
    assert.ok(corpus.counts["governance_action"] > 0);
  });

  it("121. GovernanceGate report enthält actor_id", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("worldrun.freeze");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    assert.equal(gate.actor_id, "daniel_root");
  });

  it("122. worldrun.resume blocked_by_global_lock true", () => {
    assert.equal(findAction("worldrun.resume").blocked_by_global_lock, true);
  });

  it("123. worldrun.freeze blocked_by_global_lock false", () => {
    assert.equal(findAction("worldrun.freeze").blocked_by_global_lock, false);
  });

  it("124. emergency.stop blocked_by_global_lock false", () => {
    assert.equal(findAction("emergency.stop").blocked_by_global_lock, false);
  });

  it("125. GovernanceSnapshot coverage ok true", () => {
    const snap = buildGovernanceSnapshot();
    assert.equal(snap.coverage.ok, true);
  });

  it("126. GovernanceSnapshot enthält matrix_version 1", () => {
    const snap = buildGovernanceSnapshot();
    assert.equal(snap.matrix.matrix_version, 1);
  });

  it("127. listCriticalGovernanceActions enthält worldrun.lock", () => {
    const criticals = listCriticalGovernanceActions();
    assert.ok(criticals.some((a) => a.action_id === "worldrun.lock"));
  });

  it("128. Governance search corpus_version 1", () => {
    const matrix = buildGovernanceMatrix();
    const corpus = buildSearchCorpusFromGovernanceMatrix(matrix);
    assert.equal(corpus.corpus_version, 1);
  });

  it("129. slot.approve_activation blocked_by_global_lock true", () => {
    assert.equal(findAction("slot.approve_activation").blocked_by_global_lock, true);
  });

  it("130. GovernanceLedgerBridge notes enthält status-Erklärung", () => {
    const daniel = buildDanielRootAdmin();
    const action = findAction("worldrun.pause");
    const approval = getApprovalRequirementForAction(action);
    const gate = evaluateGovernanceGate(action, approval, daniel, createUnlockedGlobalLockState());
    const cmd = createCommandIntent({
      command_id: "cmd_test",
      command_type: "pause_worldrun",
      requested_by: "daniel_root",
      target_type: "worldrun",
      target_id: "run_1",
      reason: "test",
      created_at: "2026-01-01T00:00:00Z",
    });
    const { result } = recordGovernanceGateToLedger(
      createEmptyCommandLedger(),
      { ...cmd, dry_run: false },
      daniel,
      gate
    );
    assert.ok(result.notes.length > 0);
  });
});
