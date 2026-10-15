from types import SimpleNamespace

import pytest

import mcp_cognitive_graph as c
import mcp_workflow_graph as w


def _runtime(monkeypatch, tmp_path):
    cpath = tmp_path / "cognitive.json"
    wpath = tmp_path / "workflow.json"
    monkeypatch.setattr(c, "_RUNTIME_PATH", cpath)
    monkeypatch.setattr(w, "_RUNTIME_PATH", wpath)
    monkeypatch.setattr(c, "_memory_connection", lambda: None)
    monkeypatch.setattr(w, "_workflow_connection", lambda: None)
    monkeypatch.setattr(w, "_directive_guard", lambda *args, **kwargs: {"allowed": True})
    original_default = w._default_session

    def completed_inventory_session():
        state = original_default()
        state["path_inventory_complete"] = True
        state["state"] = w.STATE_MANUAL_DISCOVERY
        return state

    monkeypatch.setattr(w, "_default_session", completed_inventory_session)
    return cpath, wpath


def test_observation_requires_source(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    with pytest.raises(c.CognitiveGraphError):
        c.add_node("OBSERVATION", "Das ist eine Tatsache.")


def test_unverified_hypothesis_is_allowed_and_guides_next(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    node = c.add_node("HYPOTHESIS", "Vielleicht ist der Name Builder-Muell.")
    assert node["epistemic_status"] == "UNVERIFIED"

    moves = c.next_moves()
    assert any(move["move"] == "SEEK_EVIDENCE_FOR_HYPOTHESIS" for move in moves)


def test_contradiction_needs_two_sources(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    with pytest.raises(c.CognitiveGraphError):
        c.add_node(
            "CONTRADICTION",
            "A und B widersprechen sich.",
            source_refs=["/one.md"],
        )

    node = c.add_node(
        "CONTRADICTION",
        "A und B widersprechen sich.",
        source_refs=["/one.md", "/two.md"],
        confidence="high",
    )
    assert node["epistemic_status"] == "GROUNDED"
    assert any(move["move"] == "COMPARE_CONFLICTING_EVIDENCE" for move in c.next_moves())


def test_edges_require_existing_nodes(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    a = c.add_node("QUESTION", "Was ist das?")
    b = c.add_node("HYPOTHESIS", "Vielleicht X.")

    edge = c.add_edge(a["id"], b["id"], "LEADS_TO", "Frage erzeugt Hypothese")
    assert edge["from"] == a["id"]
    assert edge["to"] == b["id"]

    with pytest.raises(c.CognitiveGraphError):
        c.add_edge("missing", b["id"], "LEADS_TO")


def test_user_directive_is_not_observation(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    node = c.add_node("USER_DIRECTIVE", "Lies hier echt und baue keinen Builder.")
    assert node["epistemic_status"] == "EXPLICIT_USER_INPUT"
    assert node["type"] == "USER_DIRECTIVE"


def test_source_read_is_deduplicated_with_counter(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    decision = SimpleNamespace(
        project_scoped=True,
        action_node="READ",
        state=w.STATE_MANUAL_DISCOVERY,
        allowed=True,
        reason="lesen",
    )
    args = {"path": str(w.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md")}
    result = {"ok": True, "data": {}}

    c.record_tool_event("vps.read_file", args, decision, result)
    c.record_tool_event("vps.read_file", args, decision, result)

    snap = c.snapshot()
    sources = [node for node in snap["nodes"] if node["type"] == "SOURCE_READ"]
    assert len(sources) == 1
    assert sources[0]["metadata"]["read_count"] == 2


def test_action_then_verification_creates_edge(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    target = str(w.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md")

    action_decision = SimpleNamespace(
        project_scoped=True,
        action_node="SINGLE_EDIT",
        state=w.STATE_CHANGE_READY,
        allowed=True,
        reason="gezielte Aenderung",
    )
    c.record_tool_event(
        "vps.edit_file",
        {"path": target},
        action_decision,
        {"ok": True, "data": {}},
    )

    verify_decision = SimpleNamespace(
        project_scoped=True,
        action_node="READ",
        state=w.STATE_VERIFY,
        allowed=True,
        reason="gegenlesen",
    )
    c.record_tool_event(
        "vps.read_file",
        {"path": target},
        verify_decision,
        {"ok": True, "data": {}},
    )

    snap = c.snapshot()
    actions = [node for node in snap["nodes"] if node["type"] == "ACTION"]
    verifications = [node for node in snap["nodes"] if node["type"] == "VERIFICATION"]
    assert len(actions) == 1
    assert len(verifications) == 1
    assert any(
        edge["type"] == "VERIFIED_BY"
        and edge["from"] == actions[0]["id"]
        and edge["to"] == verifications[0]["id"]
        for edge in snap["edges"]
    )


def test_workflow_verify_is_first_next_move(monkeypatch, tmp_path):
    _runtime(monkeypatch, tmp_path)
    w.set_mode(w.MODE_SURGICAL, "Nutzer verlangt gezielte Aenderungen nach echtem Lesen.")
    target = w.PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"

    read_args = {"path": str(target)}
    d1 = w.preflight_action("vps.read_file", read_args)
    w.record_outcome("vps.read_file", read_args, d1, {"ok": True, "data": {}})

    edit_args = {"path": str(target), "old_string": "x", "new_string": "y"}
    d2 = w.preflight_action("vps.edit_file", edit_args)
    assert d2.allowed
    w.record_outcome("vps.edit_file", edit_args, d2, {"ok": True, "data": {}})

    moves = c.next_moves()
    assert moves[0]["move"] == "VERIFY_PENDING_ACTION"


def test_directory_scan_returns_path_metadata_only(tmp_path):
    sample = tmp_path / "probe.txt"
    sample.write_text("INHALT_DARF_NICHT_IM_SCAN_LANDEN", encoding="utf-8")

    entries = list(c._iter_directory_entries(str(tmp_path)))
    matches = [item for item in entries if item[0] == str(sample)]

    assert len(matches) == 1
    path, entry_type, fingerprint = matches[0]
    assert path == str(sample)
    assert entry_type == "f"
    assert set(fingerprint) == {"mtime", "size", "inode"}
    assert "INHALT_DARF_NICHT_IM_SCAN_LANDEN" not in repr(entries)


def test_path_drift_is_blocked(monkeypatch):
    class Cursor:
        def execute(self, *args, **kwargs):
            return None

        def fetchone(self):
            return ({"scan_fingerprint": {"mtime": "1", "size": "2", "inode": "3"}},)

    monkeypatch.setattr(
        c,
        "_path_fingerprint_now",
        lambda path: {"type": "f", "mtime": "1", "size": "9", "inode": "3"},
    )

    with pytest.raises(c.CognitiveGraphError, match="veraendert"):
        c._require_no_path_drift(Cursor(), "scan", "/probe.txt")


def test_path_scan_fails_closed_without_postgres(monkeypatch, tmp_path):
    monkeypatch.setattr(c, "_memory_connection", lambda: None)

    with pytest.raises(c.CognitiveGraphError, match="Postgres"):
        c.path_scan_step(
            roots=[str(tmp_path)],
            session_id="test-path-scan",
        )
