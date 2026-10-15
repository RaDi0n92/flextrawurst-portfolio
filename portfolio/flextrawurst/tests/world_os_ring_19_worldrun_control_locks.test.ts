import { describe, it } from "node:test";
import assert from "node:assert/strict";

import {
  createInitialWorldRunState,
} from "../kernel/worldrun/worldrun_state.ts";
import type { WorldRunState } from "../kernel/worldrun/worldrun_state.ts";

import {
  applyWorldRunTransition,
} from "../kernel/worldrun/worldrun_transition.ts";
import type { WorldRunTransitionRequest } from "../kernel/worldrun/worldrun_transition.ts";

import {
  evaluateWorldRunGate,
} from "../kernel/worldrun/worldrun_gate.ts";

import {
  handleWorldRunCommand,
} from "../kernel/worldrun/worldrun_command_handler.ts";

import {
  buildWorldRunControlSnapshot,
} from "../kernel/worldrun/worldrun_control_snapshot.ts";

import {
  createEmptyWorldRunAudit,
  recordWorldRunCommandResult,
} from "../kernel/worldrun/worldrun_audit.ts";

import {
  buildDanielRootAdmin,
  buildObserverAdmin,
  buildSystemProcessActor,
} from "../kernel/admin/admin_permissions.ts";

import {
  buildSearchCorpusFromWorldRunState,
  buildSearchCorpusFromWorldRunAudit,
  buildSearchCorpusFromWorldRunControlSnapshot,
} from "../kernel/search/search_corpus.ts";

import {
  checkConceptLanguage,
} from "../kernel/concept_guard/concept_guard.ts";

const TS = "2026-05-09T12:00:00.000Z";

function mkRequest(type: WorldRunTransitionRequest["transition_type"], id = "t1"): WorldRunTransitionRequest {
  return {
    transition_id: id,
    transition_type: type,
    requested_by: "daniel_root",
    reason: `test ${type}`,
    created_at: TS,
  };
}

function mkCommand(type: string, dry_run = true) {
  return {
    command_id: `cmd_${type}`,
    command_type: type as any,
    requested_by: "daniel_root",
    target_type: "worldrun" as const,
    target_id: "world_1",
    reason: `test ${type}`,
    created_at: TS,
    dry_run,
  };
}

describe("Ring 19 — WorldRunState", () => {
  it("1. Initial WorldRunState status not_started", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.status, "not_started");
  });

  it("2. Initial current_tick 0", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.current_tick, 0);
  });

  it("3. Initial locked false", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.locked, false);
  });

  it("4. Initial run_id preserved", () => {
    const s = createInitialWorldRunState("myrun", TS);
    assert.equal(s.run_id, "myrun");
  });

  it("5. Initial last_event_id null", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.last_event_id, null);
  });

  it("6. Initial lock_reason null", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.lock_reason, null);
  });

  it("7. Initial paused_reason null", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.paused_reason, null);
  });

  it("8. Initial stopped_reason null", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.stopped_reason, null);
  });

  it("9. Initial frozen_reason null", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.frozen_reason, null);
  });

  it("10. Initial updated_at matches timestamp", () => {
    const s = createInitialWorldRunState("run_1", TS);
    assert.equal(s.updated_at, TS);
  });
});

describe("Ring 19 — WorldRunTransitions", () => {
  it("11. start transition not_started → running", () => {
    const s = createInitialWorldRunState("run_1", TS);
    const r = applyWorldRunTransition(s, mkRequest("start"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "running");
  });

  it("12. pause transition running → paused", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = applyWorldRunTransition(s, mkRequest("pause"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "paused");
  });

  it("13. resume transition paused → running", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const r = applyWorldRunTransition(s, mkRequest("resume"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "running");
  });

  it("14. freeze transition running → frozen", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = applyWorldRunTransition(s, mkRequest("freeze"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "frozen");
  });

  it("15. freeze transition paused → frozen", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const r = applyWorldRunTransition(s, mkRequest("freeze"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "frozen");
  });

  it("16. frozen + resume blocked", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "frozen" };
    const r = applyWorldRunTransition(s, mkRequest("resume"));
    assert.equal(r.allowed, false);
    assert.ok(r.blockers.length > 0);
  });

  it("17. frozen + stop → stopped", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "frozen" };
    const r = applyWorldRunTransition(s, mkRequest("stop"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "stopped");
  });

  it("18. running + stop → stopped", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = applyWorldRunTransition(s, mkRequest("stop"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "stopped");
  });

  it("19. paused + stop → stopped", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const r = applyWorldRunTransition(s, mkRequest("stop"));
    assert.equal(r.allowed, true);
    assert.equal(r.next_status, "stopped");
  });

  it("20. stopped + start blocked", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "stopped" };
    const r = applyWorldRunTransition(s, mkRequest("start"));
    assert.equal(r.allowed, false);
  });

  it("21. stopped + resume blocked", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "stopped" };
    const r = applyWorldRunTransition(s, mkRequest("resume"));
    assert.equal(r.allowed, false);
  });

  it("22. lock sets locked true", () => {
    const s = createInitialWorldRunState("r", TS);
    const r = applyWorldRunTransition(s, mkRequest("lock"));
    assert.equal(r.allowed, true);
    assert.equal(r.state.locked, true);
  });

  it("23. locked blocks start", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), locked: true };
    const r = applyWorldRunTransition(s, mkRequest("start"));
    assert.equal(r.allowed, false);
    assert.ok(r.blockers.some((b) => b.includes("locked")));
  });

  it("24. locked blocks resume", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused", locked: true };
    const r = applyWorldRunTransition(s, mkRequest("resume"));
    assert.equal(r.allowed, false);
  });

  it("25. unlock sets locked false", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), locked: true, lock_reason: "test" };
    const r = applyWorldRunTransition(s, mkRequest("unlock"));
    assert.equal(r.allowed, true);
    assert.equal(r.state.locked, false);
    assert.equal(r.state.lock_reason, null);
  });

  it("26. unlock keeps status unchanged", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused", locked: true };
    const r = applyWorldRunTransition(s, mkRequest("unlock"));
    assert.equal(r.state.status, "paused");
  });

  it("27. pause sets paused_reason", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const req = { ...mkRequest("pause"), reason: "maintenance" };
    const r = applyWorldRunTransition(s, req);
    assert.equal(r.state.paused_reason, "maintenance");
  });

  it("28. freeze sets frozen_reason", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const req = { ...mkRequest("freeze"), reason: "emergency" };
    const r = applyWorldRunTransition(s, req);
    assert.equal(r.state.frozen_reason, "emergency");
  });

  it("29. stop sets stopped_reason", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const req = { ...mkRequest("stop"), reason: "shutdown" };
    const r = applyWorldRunTransition(s, req);
    assert.equal(r.state.stopped_reason, "shutdown");
  });

  it("30. start from not_started has no blockers", () => {
    const s = createInitialWorldRunState("r", TS);
    const r = applyWorldRunTransition(s, mkRequest("start"));
    assert.equal(r.blockers.length, 0);
  });
});

describe("Ring 19 — WorldRunGate", () => {
  it("31. observer darf pause nicht", () => {
    const actor = buildObserverAdmin("obs_1");
    const s = createInitialWorldRunState("r", TS);
    const g = evaluateWorldRunGate(actor, s, "pause");
    assert.equal(g.allowed, false);
    assert.ok(g.missing_permissions.includes("worldrun.pause"));
  });

  it("32. observer darf freeze nicht", () => {
    const actor = buildObserverAdmin("obs_1");
    const s = createInitialWorldRunState("r", TS);
    const g = evaluateWorldRunGate(actor, s, "freeze");
    assert.equal(g.allowed, false);
    assert.ok(g.missing_permissions.includes("worldrun.freeze"));
  });

  it("33. observer darf stop nicht", () => {
    const actor = buildObserverAdmin("obs_1");
    const s = createInitialWorldRunState("r", TS);
    const g = evaluateWorldRunGate(actor, s, "stop");
    assert.equal(g.allowed, false);
    assert.ok(g.missing_permissions.includes("worldrun.stop"));
  });

  it("34. daniel_root darf pause", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "pause");
    assert.equal(g.allowed, true);
  });

  it("35. daniel_root darf freeze", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "freeze");
    assert.equal(g.allowed, true);
  });

  it("36. daniel_root darf stop", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "stop");
    assert.equal(g.allowed, true);
  });

  it("37. system_process darf freeze nicht", () => {
    const actor = buildSystemProcessActor("sys_1");
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "freeze");
    assert.equal(g.allowed, false);
    assert.ok(g.missing_permissions.includes("worldrun.freeze"));
  });

  it("38. system_process darf stop nicht", () => {
    const actor = buildSystemProcessActor("sys_1");
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "stop");
    assert.equal(g.allowed, false);
    assert.ok(g.missing_permissions.includes("worldrun.stop"));
  });

  it("39. Gate meldet missing permission korrekt", () => {
    const actor = buildObserverAdmin("obs_1");
    const s = createInitialWorldRunState("r", TS);
    const g = evaluateWorldRunGate(actor, s, "resume");
    assert.ok(g.missing_permissions.length > 0);
  });

  it("40. Gate meldet blockers bei stopped", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "stopped" };
    const g = evaluateWorldRunGate(actor, s, "resume");
    assert.ok(g.blockers.length > 0);
  });

  it("41. Gate blocked = true wenn nicht erlaubt", () => {
    const actor = buildObserverAdmin("obs_1");
    const s = createInitialWorldRunState("r", TS);
    const g = evaluateWorldRunGate(actor, s, "stop");
    assert.equal(g.blocked, true);
  });

  it("42. Gate blocked = false wenn erlaubt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "stop");
    assert.equal(g.blocked, false);
  });

  it("43. locked blockiert resume im Gate", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused", locked: true };
    const g = evaluateWorldRunGate(actor, s, "resume");
    assert.equal(g.allowed, false);
    assert.ok(g.blockers.some((b) => b.includes("locked")));
  });

  it("44. frozen blockiert resume im Gate", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "frozen" };
    const g = evaluateWorldRunGate(actor, s, "resume");
    assert.equal(g.allowed, false);
    assert.ok(g.blockers.some((b) => b.includes("frozen")));
  });
});

describe("Ring 19 — WorldRunCommandHandler", () => {
  it("45. CommandIntent pause_worldrun wird erkannt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    assert.equal(r.gate.transition_type, "pause");
  });

  it("46. CommandIntent resume_worldrun wird erkannt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const r = handleWorldRunCommand(s, mkCommand("resume_worldrun", true), actor);
    assert.equal(r.gate.transition_type, "resume");
  });

  it("47. CommandIntent freeze_worldrun wird erkannt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("freeze_worldrun", true), actor);
    assert.equal(r.gate.transition_type, "freeze");
  });

  it("48. CommandIntent stop_worldrun wird erkannt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("stop_worldrun", true), actor);
    assert.equal(r.gate.transition_type, "stop");
  });

  it("49. handleWorldRunCommand blockiert falschen CommandType", () => {
    const actor = buildDanielRootAdmin();
    const s = createInitialWorldRunState("r", TS);
    const r = handleWorldRunCommand(s, mkCommand("approve_import", true), actor);
    assert.equal(r.accepted, false);
    assert.ok(r.gate.blocked);
  });

  it("50. dry_run true verändert State nicht", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    assert.equal(r.dry_run, true);
    assert.equal(r.transition, null);
  });

  it("51. dry_run false verändert State bei erlaubtem Gate", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", false), actor);
    assert.equal(r.accepted, true);
    assert.notEqual(r.transition, null);
    assert.equal(r.transition!.next_status, "paused");
  });

  it("52. blocked Command erzeugt transition null", () => {
    const actor = buildObserverAdmin("obs");
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", false), actor);
    assert.equal(r.accepted, false);
    assert.equal(r.transition, null);
  });

  it("53. command_id wird übertragen", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const cmd = mkCommand("stop_worldrun", true);
    const r = handleWorldRunCommand(s, cmd, actor);
    assert.equal(r.command_id, cmd.command_id);
  });

  it("54. dry_run false + observer = rejected", () => {
    const actor = buildObserverAdmin("obs");
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("stop_worldrun", false), actor);
    assert.equal(r.accepted, false);
  });
});

describe("Ring 19 — WorldRunControlSnapshot", () => {
  it("55. ControlSnapshot hat snapshot_version 1", () => {
    const actor = buildDanielRootAdmin();
    const s = createInitialWorldRunState("r", TS);
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.snapshot_version, 1);
  });

  it("56. ControlSnapshot für running erlaubt pause", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_pause, true);
  });

  it("57. ControlSnapshot für paused erlaubt resume", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_resume, true);
  });

  it("58. ControlSnapshot für running erlaubt freeze", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_freeze, true);
  });

  it("59. ControlSnapshot für running erlaubt stop", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_stop, true);
  });

  it("60. ControlSnapshot für frozen blockiert resume", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "frozen" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_resume, false);
    assert.ok(snap.blocked_transitions.includes("resume"));
  });

  it("61. ControlSnapshot observer: kein pause", () => {
    const actor = buildObserverAdmin("obs");
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.can_pause, false);
  });

  it("62. ControlSnapshot enthält available_transitions", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.ok(Array.isArray(snap.available_transitions));
    assert.ok(snap.available_transitions.length > 0);
  });

  it("63. ControlSnapshot enthält blocked_transitions", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.ok(Array.isArray(snap.blocked_transitions));
  });

  it("64. ControlSnapshot run_state korrekt gesetzt", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.equal(snap.run_state.status, "paused");
  });
});

describe("Ring 19 — WorldRunAudit", () => {
  it("65. WorldRunAudit initial leer", () => {
    const audit = createEmptyWorldRunAudit();
    assert.equal(audit.entries.length, 0);
  });

  it("66. WorldRunAudit audit_version 1", () => {
    const audit = createEmptyWorldRunAudit();
    assert.equal(audit.audit_version, 1);
  });

  it("67. recordWorldRunCommandResult append-only", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    const audit1 = createEmptyWorldRunAudit();
    const audit2 = recordWorldRunCommandResult(audit1, r);
    assert.equal(audit1.entries.length, 0);
    assert.equal(audit2.entries.length, 1);
  });

  it("68. altes Audit bleibt unverändert", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r1 = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    const r2 = handleWorldRunCommand(s, mkCommand("freeze_worldrun", true), actor);
    const a0 = createEmptyWorldRunAudit();
    const a1 = recordWorldRunCommandResult(a0, r1);
    const a2 = recordWorldRunCommandResult(a1, r2);
    assert.equal(a0.entries.length, 0);
    assert.equal(a1.entries.length, 1);
    assert.equal(a2.entries.length, 2);
  });

  it("69. AuditEntry enthält command_id", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const cmd = mkCommand("stop_worldrun", true);
    const r = handleWorldRunCommand(s, cmd, actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    assert.equal(audit.entries[0].command_id, cmd.command_id);
  });

  it("70. AuditEntry enthält previous_status", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", false), actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    assert.equal(audit.entries[0].previous_status, "running");
  });

  it("71. AuditEntry enthält next_status bei akzeptiertem non-dry-run", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", false), actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    assert.equal(audit.entries[0].next_status, "paused");
  });

  it("72. Audit erzeugt keine Events", () => {
    const audit = createEmptyWorldRunAudit();
    assert.ok(!("events" in audit));
    assert.ok(!("event_ids" in audit));
  });

  it("73. dry_run true im AuditEntry", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    assert.equal(audit.entries[0].dry_run, true);
  });

  it("74. dry_run false im AuditEntry", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", false), actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    assert.equal(audit.entries[0].dry_run, false);
  });
});

describe("Ring 19 — Search Integration", () => {
  it("75. SearchDocumentKind enthält worldrun_state", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    assert.equal(corpus.documents[0].kind, "worldrun_state");
  });

  it("76. buildSearchCorpusFromWorldRunState erzeugt 1 doc", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    assert.equal(corpus.documents.length, 1);
  });

  it("77. worldrun_state doc hat source_ids mit run_id", () => {
    const state = createInitialWorldRunState("run_99", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    assert.ok(corpus.documents[0].source_ids.includes("run_99"));
  });

  it("78. worldrun_state doc layer worldrun_control", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    assert.equal(corpus.documents[0].layer, "worldrun_control");
  });

  it("79. buildSearchCorpusFromWorldRunAudit erzeugt audit docs", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("stop_worldrun", true), actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    const corpus = buildSearchCorpusFromWorldRunAudit(audit);
    assert.equal(corpus.documents.length, 1);
    assert.equal(corpus.documents[0].kind, "worldrun_audit_entry");
  });

  it("80. buildSearchCorpusFromWorldRunControlSnapshot erzeugt snapshot doc", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    const corpus = buildSearchCorpusFromWorldRunControlSnapshot(snap);
    assert.equal(corpus.documents.length, 1);
    assert.equal(corpus.documents[0].kind, "worldrun_control_snapshot");
  });

  it("81. Filter nach kind worldrun_state funktioniert", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    const filtered = corpus.documents.filter((d) => d.kind === "worldrun_state");
    assert.equal(filtered.length, 1);
  });

  it("82. Filter nach layer worldrun_control funktioniert", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    const filtered = corpus.documents.filter((d) => d.layer === "worldrun_control");
    assert.equal(filtered.length, 1);
  });

  it("83. Textsuche freeze findet Freeze-Dokumente", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "frozen" };
    const state: WorldRunState = { ...s, frozen_reason: "emergency freeze" };
    const corpus = buildSearchCorpusFromWorldRunState(state);
    const found = corpus.documents.some((d) => d.body.toLowerCase().includes("frozen") || d.tags.includes("frozen"));
    assert.ok(found);
  });

  it("84. Textsuche pause findet Pause-Dokumente", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused", paused_reason: "test pause" };
    const corpus = buildSearchCorpusFromWorldRunState(s);
    const found = corpus.documents.some((d) => d.body.includes("paused") || d.tags.includes("pause"));
    assert.ok(found);
  });

  it("85. audit doc hat command_id", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const cmd = mkCommand("freeze_worldrun", true);
    const r = handleWorldRunCommand(s, cmd, actor);
    const audit = recordWorldRunCommandResult(createEmptyWorldRunAudit(), r);
    const corpus = buildSearchCorpusFromWorldRunAudit(audit);
    assert.ok(corpus.documents[0].source_ids.includes(cmd.command_id));
  });

  it("86. empty audit corpus has 0 docs", () => {
    const audit = createEmptyWorldRunAudit();
    const corpus = buildSearchCorpusFromWorldRunAudit(audit);
    assert.equal(corpus.documents.length, 0);
  });
});

describe("Ring 19 — ConceptGuard neue Muster", () => {
  it("87. ConceptGuard erkennt 'Pause löscht Events'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Pause löscht Events im System" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Pause löscht Events"));
  });

  it("88. ConceptGuard erkennt 'Freeze startet Daemon'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Freeze startet Daemon" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Freeze startet Daemon"));
  });

  it("89. ConceptGuard erkennt 'Stop löscht Welt'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Stop löscht Welt sofort" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Stop löscht Welt"));
  });

  it("90. ConceptGuard erkennt 'Lock aktiviert Feature'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Lock aktiviert Feature X" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "Lock aktiviert Feature"));
  });

  it("91. ConceptGuard erkennt 'WorldRunControl ist Scheduler'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "WorldRunControl ist Scheduler" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "WorldRunControl ist Scheduler"));
  });

  it("92. ConceptGuard erkennt 'CommandHandler startet Runtime'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "CommandHandler startet Runtime jetzt" }]);
    assert.equal(r.ok, false);
    assert.ok(r.violations.some((v) => v.term === "CommandHandler startet Runtime"));
  });

  it("93. ConceptGuard akzeptiert 'WorldRunControl'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "WorldRunControl ist Kontrollsemantik" }]);
    assert.ok(!r.violations.some((v) => v.term === "WorldRunControl ist Scheduler"));
  });

  it("94. ConceptGuard akzeptiert 'Freeze-Modell'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Freeze-Modell ist reine Semantik" }]);
    assert.equal(r.ok, true);
  });

  it("95. ConceptGuard akzeptiert 'Pause-Modell'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "Das Pause-Modell blockiert den Weltlauf" }]);
    assert.equal(r.ok, true);
  });

  it("96. ConceptGuard akzeptiert 'read-only Control Snapshot'", () => {
    const r = checkConceptLanguage([{ id: "t1", text: "read-only Control Snapshot enthält Zustand" }]);
    assert.equal(r.ok, true);
  });
});

describe("Ring 19 — Strukturelle Grenzprüfungen", () => {
  it("97. Keine Events werden erzeugt — WorldRunState hat keine event-Felder", () => {
    const s = createInitialWorldRunState("r", TS);
    assert.ok(!("events" in s));
    assert.ok(!("event_type" in s));
  });

  it("98. Kein EventStore nötig — Audit hat keine event_store-Referenz", () => {
    const audit = createEmptyWorldRunAudit();
    assert.ok(!("event_store" in audit));
  });

  it("99. Keine UI — ControlSnapshot hat kein render-Feld", () => {
    const actor = buildDanielRootAdmin();
    const s = createInitialWorldRunState("r", TS);
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.ok(!("render" in snap));
    assert.ok(!("dom" in snap));
    assert.ok(!("html" in snap));
  });

  it("100. Kein Scheduler — WorldRunState hat kein interval-Feld", () => {
    const s = createInitialWorldRunState("r", TS);
    assert.ok(!("interval" in s));
    assert.ok(!("daemon" in s));
    assert.ok(!("scheduler" in s));
  });

  it("101. Kein Postgres — keine db-Referenzen in Audit", () => {
    const audit = createEmptyWorldRunAudit();
    assert.ok(!("db" in audit));
    assert.ok(!("postgres" in audit));
  });

  it("102. Kein Renderer — WorldRunControlSnapshot kein canvas", () => {
    const actor = buildDanielRootAdmin();
    const s = createInitialWorldRunState("r", TS);
    const snap = buildWorldRunControlSnapshot(actor, s);
    assert.ok(!("canvas" in snap));
    assert.ok(!("threejs" in snap));
  });

  it("103. Stop-Modell ist terminal — stopped blockiert alle weiteren Übergänge", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "stopped" };
    const types: Array<WorldRunTransitionRequest["transition_type"]> = ["start", "pause", "resume", "freeze"];
    for (const t of types) {
      const r = applyWorldRunTransition(s, mkRequest(t));
      assert.equal(r.allowed, false, `${t} should be blocked from stopped`);
    }
  });

  it("104. WorldRunAudit ist append-only — entries werden nie mutiert", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = handleWorldRunCommand(s, mkCommand("pause_worldrun", true), actor);
    const a1 = createEmptyWorldRunAudit();
    const a2 = recordWorldRunCommandResult(a1, r);
    const a3 = recordWorldRunCommandResult(a2, r);
    assert.equal(a1.entries.length, 0);
    assert.equal(a2.entries.length, 1);
    assert.equal(a3.entries.length, 2);
  });

  it("105. SearchCorpus für WorldRun hat corpus_version 1", () => {
    const state = createInitialWorldRunState("r", TS);
    const corpus = buildSearchCorpusFromWorldRunState(state);
    assert.equal(corpus.corpus_version, 1);
  });

  it("106. buildSearchCorpusFromWorldRunControlSnapshot hat layer worldrun_control", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const snap = buildWorldRunControlSnapshot(actor, s);
    const corpus = buildSearchCorpusFromWorldRunControlSnapshot(snap);
    assert.equal(corpus.documents[0].layer, "worldrun_control");
  });

  it("107. Keine Feature-Aktivierung — WorldRunState hat kein feature_activated-Feld", () => {
    const s = createInitialWorldRunState("r", TS);
    assert.ok(!("feature_activated" in s));
    assert.ok(!("activated_features" in s));
  });

  it("108. Lock ohne Stop — lock lässt Status unverändert", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const r = applyWorldRunTransition(s, mkRequest("lock"));
    assert.equal(r.state.status, "running");
    assert.equal(r.state.locked, true);
  });

  it("109. Unlock lässt Status unverändert", () => {
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "paused", locked: true };
    const r = applyWorldRunTransition(s, mkRequest("unlock"));
    assert.equal(r.state.status, "paused");
    assert.equal(r.state.locked, false);
  });

  it("110. WorldRunGate note enthält actor_id bei erlaubtem Übergang", () => {
    const actor = buildDanielRootAdmin();
    const s: WorldRunState = { ...createInitialWorldRunState("r", TS), status: "running" };
    const g = evaluateWorldRunGate(actor, s, "pause");
    assert.ok(g.notes.some((n) => n.includes("daniel_root")));
  });
});
