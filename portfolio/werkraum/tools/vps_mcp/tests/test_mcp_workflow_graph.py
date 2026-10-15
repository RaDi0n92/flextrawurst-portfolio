import json

import pytest

import mcp_workflow_graph as g


def _set_runtime(monkeypatch, tmp_path):
    path = tmp_path / "workflow.json"
    monkeypatch.setattr(g, "_RUNTIME_PATH", path)
    monkeypatch.setattr(g, "_workflow_connection", lambda: None)
    monkeypatch.setattr(g, "_directive_guard", lambda *args, **kwargs: {"allowed": True})
    original_default = g._default_session

    def completed_inventory_session():
        state = original_default()
        state["path_inventory_complete"] = True
        state["state"] = g.STATE_MANUAL_DISCOVERY
        return state

    monkeypatch.setattr(g, "_default_session", completed_inventory_session)
    return path


def _read(path):
    return {"path": str(path)}


def _ok():
    return {"ok": True, "data": {}}


def test_mutation_without_prior_read_is_blocked(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    g.set_mode(g.MODE_SURGICAL, "Nutzer will diesen Bereich gezielt manuell aufraeumen.")
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    d = g.preflight_action("vps.edit_file", {
        "path": str(target),
        "old_string": "a",
        "new_string": "b",
    })
    assert d.allowed is False
    assert d.state == g.STATE_MANUAL_DISCOVERY
    assert "Lese" in d.reason


def test_read_read_mutate_verify_cycle(monkeypatch, tmp_path):
    runtime = _set_runtime(monkeypatch, tmp_path)
    g.set_mode(g.MODE_SURGICAL, "Nutzer will diesen Bereich gezielt manuell aufraeumen.")
    a = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    b = g.PORTFOLIO_ROOT / "PORTFOLIO" / "03_ENTWICKLUNGSLINIEN.md"

    d1 = g.preflight_action("vps.read_file", _read(a))
    assert d1.allowed
    g.record_outcome("vps.read_file", _read(a), d1, _ok())

    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_FOCUSED_READING
    assert state["reads_since_mutation"] == 1

    d2 = g.preflight_action("vps.read_file", _read(b))
    assert d2.allowed
    g.record_outcome("vps.read_file", _read(b), d2, _ok())

    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_CHANGE_READY
    assert len(state["distinct_read_paths"]) == 2

    edit_args = {
        "path": str(a),
        "old_string": "a",
        "new_string": "b",
    }
    d3 = g.preflight_action("vps.edit_file", edit_args)
    assert d3.allowed
    assert d3.next_state_on_success == g.STATE_VERIFY
    g.record_outcome("vps.edit_file", edit_args, d3, _ok())

    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_VERIFY
    assert state["reads_since_mutation"] == 0
    assert state["pending_verification"] == [str(a)]

    new_note = g.PORTFOLIO_ROOT / "PORTFOLIO" / "new_note.md"
    d4 = g.preflight_action("vps.write_file", {
        "path": str(new_note),
        "content": "x",
    })
    assert d4.allowed
    assert d4.state == g.STATE_VERIFY
    g.record_outcome(
        "vps.write_file",
        {"path": str(new_note), "content": "x"},
        d4,
        _ok(),
    )
    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_VERIFY
    assert set(state["pending_verification"]) == {str(a), str(new_note)}

    d5 = g.preflight_action("vps.read_file", _read(a))
    assert d5.allowed
    g.record_outcome("vps.read_file", _read(a), d5, _ok())
    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_VERIFY
    assert state["pending_verification"] == [str(new_note)]

    d6 = g.preflight_action("vps.read_file", _read(new_note))
    assert d6.allowed
    g.record_outcome("vps.read_file", _read(new_note), d6, _ok())
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_FOCUSED_READING

    assert json.loads(runtime.read_text())["sessions"]["default"]["recent_events"]


def test_block_records_recover_and_read_recovers(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    bad = {
        "cwd": str(g.PORTFOLIO_ROOT),
        "command": "python3 -c 'print(1)'",
    }
    d1 = g.preflight_action("vps.shell", bad)
    assert not d1.allowed
    g.record_outcome("vps.shell", bad, d1, {"ok": False})
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_RECOVER

    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    d2 = g.preflight_action("vps.read_file", _read(target))
    assert d2.allowed
    g.record_outcome("vps.read_file", _read(target), d2, _ok())
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_FOCUSED_READING


def test_repeated_read_guidance_is_soft_not_blocking(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    args = _read(target)

    for _ in range(3):
        d = g.preflight_action("vps.read_file", args)
        assert d.allowed
        g.record_outcome("vps.read_file", args, d, _ok())

    d = g.preflight_action("vps.read_file", args)
    assert d.allowed
    assert any("kreist" in hint for hint in d.guidance)


def test_failed_allowed_action_goes_to_recover(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    args = _read(target)
    d = g.preflight_action("vps.read_file", args)
    assert d.allowed
    g.record_outcome("vps.read_file", args, d, {"ok": False})
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_RECOVER


def test_shell_relative_reads_track_concrete_files(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    a = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    b = g.PORTFOLIO_ROOT / "PORTFOLIO" / "03_ENTWICKLUNGSLINIEN.md"

    args_a = {
        "cwd": str(g.PORTFOLIO_ROOT),
        "command": "sed -n '1,5p' PORTFOLIO/README.md",
    }
    d1 = g.preflight_action("vps.shell", args_a)
    g.record_outcome("vps.shell", args_a, d1, _ok())

    args_b = {
        "cwd": str(g.PORTFOLIO_ROOT),
        "command": "sed -n '1,5p' PORTFOLIO/03_ENTWICKLUNGSLINIEN.md",
    }
    d2 = g.preflight_action("vps.shell", args_b)
    g.record_outcome("vps.shell", args_b, d2, _ok())

    state = g.graph_snapshot()["runtime"]
    assert str(a) in state["distinct_read_paths"]
    assert str(b) in state["distinct_read_paths"]
    assert str(g.PORTFOLIO_ROOT) not in state["distinct_read_paths"]
    assert state["state"] == g.STATE_CHANGE_READY


def test_edit_requires_that_exact_target_was_read(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    g.set_mode(g.MODE_SURGICAL, "Nutzer will diesen Bereich gezielt manuell aufraeumen.")
    a = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    b = g.PORTFOLIO_ROOT / "PORTFOLIO" / "03_ENTWICKLUNGSLINIEN.md"

    read_b = _read(b)
    d1 = g.preflight_action("vps.read_file", read_b)
    g.record_outcome("vps.read_file", read_b, d1, _ok())

    edit_a = {"path": str(a), "old_string": "x", "new_string": "y"}
    d2 = g.preflight_action("vps.edit_file", edit_a)
    assert not d2.allowed
    assert "Zieldatei" in d2.reason


def test_verify_survives_block_and_unrelated_read(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    g.set_mode(g.MODE_SURGICAL, "Nutzer will diesen Bereich gezielt manuell aufraeumen.")
    a = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    b = g.PORTFOLIO_ROOT / "PORTFOLIO" / "03_ENTWICKLUNGSLINIEN.md"

    read_a = _read(a)
    d1 = g.preflight_action("vps.read_file", read_a)
    g.record_outcome("vps.read_file", read_a, d1, _ok())

    edit_a = {"path": str(a), "old_string": "x", "new_string": "y"}
    d2 = g.preflight_action("vps.edit_file", edit_a)
    assert d2.allowed
    g.record_outcome("vps.edit_file", edit_a, d2, _ok())
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_VERIFY

    d3 = g.preflight_action("vps.edit_file", edit_a)
    assert not d3.allowed
    g.record_outcome("vps.edit_file", edit_a, d3, {"ok": False})
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_VERIFY

    read_b = _read(b)
    d4 = g.preflight_action("vps.read_file", read_b)
    g.record_outcome("vps.read_file", read_b, d4, _ok())
    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_VERIFY
    assert state["pending_verification"] == [str(a)]

    d5 = g.preflight_action("vps.read_file", read_a)
    g.record_outcome("vps.read_file", read_a, d5, _ok())
    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_FOCUSED_READING
    assert state["pending_verification"] == []


def test_new_file_does_not_require_fake_target_read(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    g.set_mode(g.MODE_SURGICAL, "Nutzer will diesen Bereich gezielt manuell aufraeumen.")
    new_file = g.PORTFOLIO_ROOT / "PORTFOLIO" / "new_unique_note.md"

    decision = g.preflight_action(
        "vps.write_file",
        {"path": str(new_file), "content": "x"},
    )

    assert decision.allowed
    assert decision.action_node == g.NODE_SINGLE_WRITE
    assert decision.next_state_on_success == g.STATE_VERIFY


def test_explicit_directive_can_mutate_without_a_second_mode_switch(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    d1 = g.preflight_action("vps.read_file", _read(target))
    g.record_outcome("vps.read_file", _read(target), d1, _ok())

    edit_args = {"path": str(target), "old_string": "x", "new_string": "y"}
    d2 = g.preflight_action("vps.edit_file", edit_args)
    assert d2.allowed


def test_mode_change_requires_visible_user_instruction(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    with pytest.raises(ValueError):
        g.set_mode(g.MODE_SURGICAL, "mach")


def test_surgical_mode_is_explicit_and_resets_workflow(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    d1 = g.preflight_action("vps.read_file", _read(target))
    g.record_outcome("vps.read_file", _read(target), d1, _ok())
    assert g.graph_snapshot()["runtime"]["state"] == g.STATE_FOCUSED_READING

    changed = g.set_mode(
        g.MODE_SURGICAL,
        "Nutzer verlangt jetzt explizit gezielte Einzelkorrekturen.",
    )
    assert changed["mode"] == g.MODE_SURGICAL
    state = g.graph_snapshot()["runtime"]
    assert state["state"] == g.STATE_MANUAL_DISCOVERY
    assert state["reads_since_mutation"] == 0
    assert "gezielte Einzelkorrekturen" in state["mode_user_instruction"]


def test_legacy_build_mode_label_is_only_a_surgical_intent_alias(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    changed = g.set_mode(
        g.MODE_BUILD_ALLOWED,
        "Legacy-Modus wird ohne zweite Codebau-Freigabe weitergefuehrt.",
    )
    assert changed["mode"] == g.MODE_SURGICAL


def test_control_plane_does_not_relax_shell_automation(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    g.set_mode(
        g.MODE_CONTROL_PLANE,
        "Nutzer erlaubt gezielte MCP-Kontrollarbeit, aber keine Shell-Automation.",
    )
    d = g.preflight_action(
        "vps.shell",
        {"cwd": str(g.CONTROL_PLANE_ROOT), "command": "python3 build_everything.py"},
    )
    assert not d.allowed
    assert d.action_node == g.NODE_SHELL_AUTOMATION


def test_learning_rule_stays_active_when_new_trace_still_supports_it():
    status, _reason = g._decide_reassessed_rule_status(
        {},
        {
            "source_covered": True,
            "success_collisions": 0,
            "passed_for_activation": True,
        },
    )
    assert status == "ACTIVE"


@pytest.mark.parametrize(
    ("feedback", "regression"),
    [
        (
            {},
            {
                "source_covered": True,
                "success_collisions": 1,
                "passed_for_activation": False,
            },
        ),
        (
            {"HARMFUL": 1},
            {
                "source_covered": True,
                "success_collisions": 0,
                "passed_for_activation": True,
            },
        ),
        (
            {},
            {
                "source_covered": False,
                "success_collisions": 0,
                "passed_for_activation": False,
            },
        ),
    ],
)
def test_learning_rule_can_be_weakened_by_new_experience(feedback, regression):
    status, _reason = g._decide_reassessed_rule_status(feedback, regression)
    assert status == "WEAKENED"


@pytest.mark.parametrize(
    ("feedback", "regression"),
    [
        (
            {},
            {
                "source_covered": True,
                "success_collisions": 2,
                "passed_for_activation": False,
            },
        ),
        (
            {"HARMFUL": 1, "CONTRADICTED": 1},
            {
                "source_covered": True,
                "success_collisions": 0,
                "passed_for_activation": True,
            },
        ),
    ],
)
def test_learning_rule_can_be_retired_after_repeated_negative_evidence(feedback, regression):
    status, _reason = g._decide_reassessed_rule_status(feedback, regression)
    assert status == "RETIRED"


def test_known_drift_only_creates_candidate_shape_not_direct_activation():
    candidate = g._default_candidate_for_drift("MUTATION_NOT_REREAD", {})
    assert candidate is not None
    assert candidate["rule_kind"] == "REQUIRE_REREAD_AFTER_MUTATION"
    assert candidate["enforcement"]["type"] == "REQUIRE_REREAD_SAME_TARGET"


def test_unknown_drift_has_no_automatic_candidate_rule():
    assert g._default_candidate_for_drift("SEMANTIC_MYSTERY", {}) is None


def test_learning_cycle_runs_regression_before_activation(monkeypatch):
    calls = []

    def fake_test(rule_id):
        calls.append(("test", rule_id))
        return {
            "rule_id": rule_id,
            "status": "TESTING",
            "source_covered": True,
            "success_collisions": 0,
            "passed_for_activation": True,
        }

    def fake_activate(rule_id):
        calls.append(("activate", rule_id))
        return {
            "rule_id": rule_id,
            "activated": True,
            "status": "ACTIVE",
        }

    monkeypatch.setattr(g, "test_candidate_rule", fake_test)
    monkeypatch.setattr(g, "activate_tested_rule", fake_activate)

    result = g.run_learning_cycle("lr-test")

    assert calls == [("test", "lr-test"), ("activate", "lr-test")]
    assert result["regression_test"]["passed_for_activation"] is True
    assert result["activation"]["status"] == "ACTIVE"



def _task_scope_layer_snapshot(
    *,
    verified=True,
    tool_patterns=None,
    target_patterns=None,
    core_status="ACTIVE",
    created_actor=None,
    provenance=None,
):
    if created_actor is None:
        created_actor = "DANIEL_DASHBOARD" if verified else "CHATGPT"
    if provenance is None:
        provenance = (
            {"source": "CHATGPTHARNESS", "authority_verified": True}
            if verified
            else {"source": "MODEL_NOTE", "authority_verified": False}
        )
    return {
        "ok": True,
        "master": {"effective_status": "ACTIVE"},
        "layers": [
            {
                "layer_id": "core.task_scope",
                "kind": "CORE",
                "effective_status": core_status,
                "scope": {"type": "GLOBAL"},
                "provenance": {"source": "mcp_workflow_graph", "builtin": True},
                "created_at": 1.0,
                "last_event_at": None,
            },
            {
                "layer_id": "task.current",
                "kind": "TASK",
                "effective_status": "ACTIVE",
                "scope": {
                    "task_id": "task-current",
                    "raw_goal": "Aktuellen Fix bis zum Abschluss fertigstellen.",
                    "allowed_tool_patterns": list(tool_patterns or ["vps.read_file"]),
                    "allowed_target_patterns": list(target_patterns or []),
                    "completion_criteria": ["Tests gruen", "Gegenpruefung bestanden"],
                    "sidequest_policy": "park_only",
                },
                "provenance": provenance,
                "created_actor": created_actor,
                "created_event_at": 2.0,
                "created_at": 2.0,
                "last_event_at": 2.0,
            },
        ],
        "leases": [],
    }


def _verified_task_create_kwargs(scope):
    return {
        "layer_id": "task.validation",
        "kind": "TASK",
        "title": "Validierungs-Task",
        "purpose": "Prueft die TASK-Invariante.",
        "does_text": "Grenzt einen verifizierten Auftrag ein.",
        "pause_effect": "Der Auftragsscope greift nicht.",
        "actor": "DANIEL_DASHBOARD",
        "reason": "Regressionstest.",
        "scope": scope,
        "provenance": {"source": "CHATGPTHARNESS", "authority_verified": True},
    }


def test_verified_task_create_requires_goal_before_db():
    with pytest.raises(ValueError, match="klares Ziel"):
        g.harness_create_layer(**_verified_task_create_kwargs({
            "allowed_tool_patterns": ["vps.read_file"],
        }))


def test_verified_task_create_requires_tool_pattern_before_db():
    with pytest.raises(ValueError, match="allowed_tool_pattern"):
        g.harness_create_layer(**_verified_task_create_kwargs({
            "raw_goal": "Gezielten Auftrag fertigstellen.",
        }))


def test_verified_task_create_rejects_unbounded_target_pattern_before_db():
    with pytest.raises(ValueError, match="begrenzte absolute VPS-Pfade"):
        g.harness_create_layer(**_verified_task_create_kwargs({
            "raw_goal": "Gezielten Auftrag fertigstellen.",
            "allowed_tool_patterns": ["vps.read_file"],
            "allowed_target_patterns": ["/root/*"],
        }))


def test_task_scope_blocks_before_other_gates(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )

    decision = g.preflight_action("agents.list_sessions", {"provider": "codex"})

    assert not decision.allowed
    assert decision.action_node == g.NODE_TASK_SCOPE
    assert decision.reason.startswith("TASK_SCOPE_BLOCK:")


def test_chatgpt_cannot_forge_task_scope_authority(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=False,
            tool_patterns=["vps.read_file"],
            created_actor="CHATGPT",
            provenance={"source": "CHATGPTHARNESS", "authority_verified": True},
        ),
    )

    snapshot = g.task_scope_snapshot()
    decision = g._task_scope_preflight(
        "agents.list_sessions",
        {"provider": "codex"},
        session_id="default",
        current_state=g.STATE_MANUAL_DISCOVERY,
    )

    assert snapshot["visible_layer_id"] == "task.current"
    assert snapshot["authority_verified"] is False
    assert snapshot["hard_enforced"] is False
    assert decision is None


def test_unverified_task_scope_never_hard_blocks(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=False,
            tool_patterns=["vps.read_file"],
        ),
    )

    snapshot = g.task_scope_snapshot()
    decision = g._task_scope_preflight(
        "agents.list_sessions",
        {"provider": "codex"},
        session_id="default",
        current_state=g.STATE_MANUAL_DISCOVERY,
    )

    assert snapshot["visible_layer_id"] == "task.current"
    assert snapshot["authority_verified"] is False
    assert snapshot["hard_enforced"] is False
    assert decision is None


def test_task_scope_target_mismatch_is_blocked(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    allowed = str(g.PORTFOLIO_ROOT / "PORTFOLIO" / "*")
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
            target_patterns=[allowed],
        ),
    )

    decision = g.preflight_action(
        "vps.read_file",
        {"path": str(g.PORTFOLIO_ROOT / "tools" / "outside.md")},
    )

    assert not decision.allowed
    assert decision.action_node == g.NODE_TASK_SCOPE
    assert "Ziel liegt ausserhalb" in decision.reason


def test_in_scope_action_still_passes_through_existing_gates(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.edit_file"],
            target_patterns=[str(target)],
        ),
    )
    monkeypatch.setattr(g, "_learned_rule_guard", lambda *args, **kwargs: {"allowed": True})

    decision = g.preflight_action(
        "vps.edit_file",
        {"path": str(target), "old_string": "x", "new_string": "y"},
    )

    assert not decision.allowed
    assert decision.action_node == g.NODE_SINGLE_EDIT
    assert "Lese-/Pruefschritt" in decision.reason


def test_preinventory_observation_does_not_build_read_state(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    state = g._default_session()
    state["path_inventory_complete"] = False
    state["path_scan_id"] = "scan-test"
    state["state"] = g.STATE_PATH_INVENTORY
    g._save_all({"schema": g._RUNTIME_SCHEMA, "sessions": {"default": state}})

    args = {"provider": "codex"}
    decision = g.preflight_action("agents.list_sessions", args)

    assert decision.allowed
    assert decision.action_node == g.NODE_NAVIGATE
    g.record_outcome("agents.list_sessions", args, decision, _ok())
    runtime = g.graph_snapshot()["runtime"]
    assert runtime["state"] == g.STATE_PATH_INVENTORY
    assert runtime["reads_since_mutation"] == 0
    assert runtime["distinct_read_paths"] == []


def test_task_scope_block_does_not_enter_recover(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )

    args = {"provider": "codex"}
    decision = g.preflight_action("agents.list_sessions", args)
    g.record_outcome("agents.list_sessions", args, decision, {"ok": False})

    runtime = g.graph_snapshot()["runtime"]
    assert runtime["state"] == g.STATE_MANUAL_DISCOVERY
    assert runtime["blocked_streak"] == 0


def test_task_scope_block_has_no_automatic_learning_candidate():
    assert g._default_candidate_for_drift("TASK_SCOPE_BLOCK", {}) is None


def test_graph_exposes_task_scope_and_control_channel_bypasses_scope(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )

    snapshot = g.graph_snapshot()
    control = g._task_scope_preflight(
        "harness.graph",
        {},
        session_id="default",
        current_state=g.STATE_MANUAL_DISCOVERY,
    )

    assert snapshot["task_scope"]["task_id"] == "task-current"
    assert snapshot["task_scope"]["hard_enforced"] is True
    assert control is None


def test_non_control_harness_tool_is_still_task_scoped(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )
    decision = g._task_scope_preflight(
        "harness.wander",
        {},
        session_id="default",
        current_state=g.STATE_MANUAL_DISCOVERY,
    )
    assert decision is not None
    assert not decision.allowed
    assert decision.action_node == g.NODE_TASK_SCOPE
    assert "ausserhalb" in decision.reason



def test_chatgpt_cannot_pause_or_archive_layer_without_dashboard_lease(monkeypatch):
    import vps_mcp_server as srv

    monkeypatch.setattr(srv, "harness_control_allowed", lambda grantee, layer_id: False)
    calls = []
    monkeypatch.setattr(srv, "harness_layer_set", lambda *args, **kwargs: calls.append((args, kwargs)) or {})

    for desired_status in ("PAUSED", "ARCHIVED"):
        result = srv.tool_harness_layer_set({
            "layer_id": "core.task_scope",
            "desired_status": desired_status,
            "reason": "red-team probe",
        })
        assert result["ok"] is False
        assert "keine aktive Control-Lease" in result["error"]

    assert calls == []


def test_chatgpt_can_reactivate_layer_without_dashboard_lease(monkeypatch):
    import vps_mcp_server as srv

    monkeypatch.setattr(srv, "harness_control_allowed", lambda grantee, layer_id: False)
    captured = {}

    def fake_set(layer_id, desired_status, *, actor, reason, ttl_seconds=None):
        captured.update({
            "layer_id": layer_id,
            "desired_status": desired_status,
            "actor": actor,
            "reason": reason,
            "ttl_seconds": ttl_seconds,
        })
        return {"layer_id": layer_id, "effective_status": desired_status}

    monkeypatch.setattr(srv, "harness_layer_set", fake_set)
    result = srv.tool_harness_layer_set({
        "layer_id": "core.task_scope",
        "desired_status": "ACTIVE",
        "reason": "Schutz wieder aktivieren",
    })

    assert result["ok"] is True
    assert captured["actor"] == "CHATGPT"
    assert captured["desired_status"] == "ACTIVE"


def test_control_lease_grant_and_revoke_are_not_public_chatgpt_tools():
    import vps_mcp_server as srv

    assert "harness.control_lease_grant" not in srv.TOOLS
    assert "harness.control_lease_revoke" not in srv.TOOLS


def test_chatgpt_create_layer_actor_is_server_fixed(monkeypatch):
    import vps_mcp_server as srv

    captured = {}

    def fake_create_layer(**kwargs):
        captured.update(kwargs)
        return {"layer_id": kwargs["layer_id"]}

    monkeypatch.setattr(srv, "harness_create_layer", fake_create_layer)
    result = srv.tool_harness_create_layer({
        "layer_id": "task.forgery-probe",
        "kind": "TASK",
        "title": "Probe",
        "purpose": "Probe",
        "does": "Probe",
        "pause_effect": "Probe",
        "reason": "red-team",
        "actor": "DANIEL_DASHBOARD",
        "scope": {"allowed_tool_patterns": ["*"]},
        "provenance": {"source": "CHATGPTHARNESS", "authority_verified": True},
    })

    assert result["ok"] is True
    assert captured["actor"] == "CHATGPT"



def test_additional_harness_sidequest_tools_are_task_scoped(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )

    for tool_name, args in (
        ("harness.path_scan", {"session_id": "sidequest"}),
        ("harness.note", {"node_type": "OBSERVATION", "text": "Nebenpfad"}),
        ("harness.create_layer", {"layer_id": "task.sidequest"}),
    ):
        decision = g._task_scope_preflight(
            tool_name,
            args,
            session_id="default",
            current_state=g.STATE_MANUAL_DISCOVERY,
        )
        assert decision is not None
        assert not decision.allowed
        assert decision.action_node == g.NODE_TASK_SCOPE


def test_task_scope_keeps_control_safety_corridor_reachable(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    monkeypatch.setattr(
        g,
        "harness_layers_snapshot",
        lambda session_id=None: _task_scope_layer_snapshot(
            verified=True,
            tool_patterns=["vps.read_file"],
        ),
    )

    for tool_name in sorted(g._TASK_SCOPE_CONTROL_TOOLS):
        assert g._task_scope_preflight(
            tool_name,
            {},
            session_id="default",
            current_state=g.STATE_MANUAL_DISCOVERY,
        ) is None


def test_multiple_verified_task_scopes_fail_closed(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    snap = _task_scope_layer_snapshot(verified=True, tool_patterns=["vps.read_file"])
    second = dict(snap["layers"][-1])
    second["layer_id"] = "task.second"
    second["scope"] = {**second["scope"], "task_id": "task-second"}
    second["last_event_at"] = 3.0
    snap["layers"].append(second)
    monkeypatch.setattr(g, "harness_layers_snapshot", lambda session_id=None: snap)
    scope = g.task_scope_snapshot()
    decision = g._task_scope_preflight(
        "vps.read_file", {}, session_id="default", current_state=g.STATE_MANUAL_DISCOVERY
    )
    assert scope["scope_conflict"] is True
    assert not decision.allowed
    assert decision.action_node == g.NODE_TASK_SCOPE


def test_directive_status_exposes_raw_authority_rules_and_history(monkeypatch):
    class FakeCursor:
        def __init__(self):
            self.query = ""

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, query, params=None):
            self.query = str(query)

        def fetchall(self):
            if ".directive_events" in self.query:
                return [
                    ("d-new", "neuer originalwortlaut", "TRUSTED_CLIENT_CAPTURE", {"origin": "client"}, None),
                    ("d-old", "alter originalwortlaut", "TRUSTED_CLIENT_CAPTURE", {}, None),
                    ("d-note", "nur erinnerung", "UNVERIFIED_MODEL_CLAIM", {}, None),
                ]
            if ".directive_constraints" in self.query:
                return [
                    ("d-new", "dc-1", "DENY", "vps.delete", "/root/wichtig/*", "Nicht loeschen.", {}, None),
                ]
            if ".directive_invariants" in self.query:
                return [
                    ("d-new", "di-1", "MUST_EXIST", "/root/wichtig", None, {}, None),
                ]
            if ".directive_relations" in self.query:
                return [
                    ("d-new", "d-old", "SUPERSEDES", "spaeter ersetzt", None),
                ]
            if ".directive_status_events" in self.query:
                return [
                    ("d-note", "dse-1", "ARCHIVED", "DANIEL_DASHBOARD", "Nicht mehr wirksam.", None),
                ]
            raise AssertionError(self.query)

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(g, "_workflow_connection", lambda: FakeConnection())
    monkeypatch.setattr(g, "_ensure_directive_tables", lambda conn: None)

    status = g.directive_status(session_id="default", limit=200)

    assert status["counts"] == {
        "total": 3,
        "active_verified": 1,
        "active_unverified": 0,
        "archived": 1,
        "superseded": 1,
    }
    new = next(item for item in status["directives"] if item["event_id"] == "d-new")
    old = next(item for item in status["directives"] if item["event_id"] == "d-old")
    note = next(item for item in status["directives"] if item["event_id"] == "d-note")
    assert new["raw_text"] == "neuer originalwortlaut"
    assert new["authority_verified"] is True
    assert new["status"] == "ACTIVE"
    assert new["constraints"][0]["effect"] == "DENY"
    assert new["invariants"][0]["type"] == "MUST_EXIST"
    assert new["supersedes"] == ["d-old"]
    assert old["status"] == "SUPERSEDED"
    assert old["superseded_by"] == ["d-new"]
    assert note["authority_verified"] is False
    assert note["status"] == "ARCHIVED"
    assert note["status_actor"] == "DANIEL_DASHBOARD"
    assert note["status_reason"] == "Nicht mehr wirksam."
    assert len(note["status_history"]) == 1


def test_set_directive_status_appends_status_event(monkeypatch):
    calls = []

    class FakeCursor:
        def __init__(self):
            self.query = ""

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, query, params=None):
            self.query = str(query)
            calls.append((self.query, params))

        def fetchone(self):
            if "SELECT session_id" in self.query:
                return ("default",)
            raise AssertionError(self.query)

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(g, "_workflow_connection", lambda: FakeConnection())
    monkeypatch.setattr(g, "_ensure_directive_tables", lambda conn: None)
    monkeypatch.setattr(
        g,
        "directive_status",
        lambda session_id=None, limit=200: {
            "directives": [{"event_id": "d-1", "status": "ARCHIVED"}]
        },
    )

    result = g.set_directive_status(
        "d-1",
        "ARCHIVED",
        actor="DANIEL_DASHBOARD",
        reason="Nicht mehr wirksam.",
    )

    insert = next(
        (params for query, params in calls if "INSERT INTO" in query and ".directive_status_events" in query),
        None,
    )
    assert insert is not None
    assert insert[1:] == ("d-1", "ARCHIVED", "DANIEL_DASHBOARD", "Nicht mehr wirksam.")
    assert result["status"] == "ARCHIVED"
    assert result["directive"]["status"] == "ARCHIVED"


def test_dashboard_definition_proposal_applies_as_authenticated_dashboard_actor(monkeypatch):
    import vps_mcp_server as srv

    monkeypatch.setattr(
        srv,
        "harness_feedback_entry",
        lambda entry_id: {
            "entry_id": entry_id,
            "entry_type": "PROPOSAL",
            "status": "OPEN",
            "layer_id": "core.path_inventory",
            "payload": {
                "action": "UPDATE_LAYER_DEFINITION",
                "layer_id": "core.path_inventory",
                "changes": {
                    "purpose": "Verständlicher neuer Zweck.",
                    "pause_effect": "Nur die Pfadorientierung pausiert.",
                },
                "reason": "Definition präzisieren.",
            },
        },
    )
    captured = {}

    def fake_update(layer_id, **kwargs):
        captured["layer_id"] = layer_id
        captured.update(kwargs)
        return {
            "changed": True,
            "event_id": "hld-test",
            "before": {"purpose": "alt"},
            "after": {"purpose": "Verständlicher neuer Zweck."},
        }

    monkeypatch.setattr(srv, "harness_update_layer_definition", fake_update)
    result = srv._harness_dashboard_apply_proposal("proposal-1")

    assert result["applied"] is True
    assert result["action"] == "UPDATE_LAYER_DEFINITION"
    assert result["layer_id"] == "core.path_inventory"
    assert captured["actor"] == "DANIEL_DASHBOARD"
    assert captured["purpose"] == "Verständlicher neuer Zweck."
    assert captured["pause_effect"] == "Nur die Pfadorientierung pausiert."


def test_dashboard_html_contains_definition_editor():
    import vps_mcp_server as srv

    html_text = srv._harness_dashboard_html()
    assert "Definition bearbeiten / Verlauf" in html_text
    assert "/chatgptharness/api/update-layer-definition" in html_text


def test_shell_cwd_is_not_a_mutation_target():
    cwd = g.PORTFOLIO_ROOT / "tools" / "vps_mcp"
    target = cwd / "tests" / "test_mcp_workflow_graph.py"

    paths = g._portfolio_paths(
        {
            "cwd": str(cwd),
            "command": "python3 -m pytest -q tests/test_mcp_workflow_graph.py",
        },
        "vps.shell",
    )

    assert str(cwd) not in paths
    assert str(target) in paths


def test_stale_directory_pending_verification_self_heals(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    state = g._default_session()
    state["state"] = g.STATE_VERIFY
    state["pending_verification"] = [str(tmp_path)]
    data = {"schema": g._RUNTIME_SCHEMA, "sessions": {"default": state}}

    healed = g._get_session(data, "default")

    assert healed["pending_verification"] == []
    assert healed["state"] == g.STATE_FOCUSED_READING


def test_http_probe_get_is_preinventory_observation_but_post_is_not(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    state = g._default_session()
    state["path_inventory_complete"] = False
    state["state"] = g.STATE_PATH_INVENTORY
    g._save_all({"schema": g._RUNTIME_SCHEMA, "sessions": {"default": state}})

    get_decision = g.preflight_action(
        "network.http_probe",
        {"url": "http://127.0.0.1:8091/health", "method": "GET"},
    )
    post_decision = g.preflight_action(
        "network.http_probe",
        {
            "url": "http://127.0.0.1:8091/chatgptharness/api/set-layer",
            "method": "POST",
            "body": "{}",
        },
    )

    assert get_decision.allowed
    assert get_decision.action_node == g.NODE_NAVIGATE
    assert not (post_decision.allowed and post_decision.action_node == g.NODE_NAVIGATE)


def test_verify_recover_layer_can_pause_verify_gate(monkeypatch, tmp_path):
    _set_runtime(monkeypatch, tmp_path)
    target = g.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"
    state = g._default_session()
    state["path_inventory_complete"] = True
    state["state"] = g.STATE_VERIFY
    state["mode"] = g.MODE_SURGICAL
    state["pending_verification"] = [str(target)]
    state["distinct_read_paths"] = [str(target)]
    state["reads_since_mutation"] = 1
    g._save_all({"schema": g._RUNTIME_SCHEMA, "sessions": {"default": state}})
    monkeypatch.setattr(g, "_learned_rule_guard", lambda *args, **kwargs: {"allowed": True})
    monkeypatch.setattr(g, "_directive_guard", lambda *args, **kwargs: {"allowed": True})

    def snapshot(status):
        return {
            "ok": True,
            "master": {"effective_status": "ACTIVE"},
            "layers": [
                {
                    "layer_id": "core.path_inventory",
                    "kind": "CORE",
                    "effective_status": "ACTIVE",
                    "scope": {"type": "GLOBAL"},
                    "provenance": {"builtin": True},
                },
                {
                    "layer_id": "core.verify_recover",
                    "kind": "CORE",
                    "effective_status": status,
                    "scope": {"type": "GLOBAL"},
                    "provenance": {"builtin": True},
                },
            ],
            "leases": [],
        }

    monkeypatch.setattr(g, "harness_layers_snapshot", lambda session_id=None: snapshot("ACTIVE"))
    blocked = g.preflight_action(
        "vps.edit_file",
        {"path": str(target), "old_string": "x", "new_string": "y"},
    )
    assert not blocked.allowed
    assert "vorige Eingriff" in blocked.reason

    monkeypatch.setattr(g, "harness_layers_snapshot", lambda session_id=None: snapshot("PAUSED"))
    allowed = g.preflight_action(
        "vps.edit_file",
        {"path": str(target), "old_string": "x", "new_string": "y"},
    )
    assert allowed.allowed
    assert allowed.action_node == g.NODE_SINGLE_EDIT
