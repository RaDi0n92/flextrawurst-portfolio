from pathlib import Path

from mcp_action_graph import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    NODE_SHELL_AUTOMATION,
    NODE_SINGLE_EDIT,
    NODE_SINGLE_WRITE,
    PORTFOLIO_ROOT,
    STATE_MANUAL_DISCOVERY,
    evaluate_action,
    graph_snapshot,
)


def test_portfolio_read_is_allowed():
    result = evaluate_action(
        "vps.read_file",
        {"path": str(PORTFOLIO_ROOT / "PORTFOLIO" / "README.md")},
    )
    assert result.decision == DECISION_ALLOW
    assert result.state == STATE_MANUAL_DISCOVERY
    assert result.project_scoped is True


def test_single_markdown_write_is_allowed():
    result = evaluate_action(
        "vps.write_file",
        {"path": str(PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"), "content": "x"},
    )
    assert result.decision == DECISION_ALLOW


def test_new_python_file_is_an_ordinary_single_file_write():
    result = evaluate_action(
        "vps.write_file",
        {"path": str(PORTFOLIO_ROOT / "tools" / "build_something.py"), "content": "print('x')"},
    )
    assert result.decision == DECISION_ALLOW
    assert result.action_node == NODE_SINGLE_WRITE


def test_manifest_filename_is_not_a_special_write_block():
    result = evaluate_action(
        "vps.write_file",
        {"path": str(PORTFOLIO_ROOT / "MANIFEST.json"), "content": "{}"},
    )
    assert result.decision == DECISION_ALLOW


def test_existing_python_file_is_an_ordinary_single_file_edit():
    result = evaluate_action(
        "vps.edit_file",
        {
            "path": str(PORTFOLIO_ROOT / "evidence.py"),
            "old_string": "x",
            "new_string": "y",
        },
    )
    assert result.decision == DECISION_ALLOW
    assert result.action_node == NODE_SINGLE_EDIT


def test_replace_all_is_blocked_in_manual_discovery():
    result = evaluate_action(
        "vps.edit_file",
        {
            "path": str(PORTFOLIO_ROOT / "PORTFOLIO" / "README.md"),
            "old_string": "x",
            "new_string": "y",
            "replace_all": True,
        },
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == "BULK_MUTATION"


def test_directory_delete_is_blocked(tmp_path):
    directory = tmp_path / "ordner"
    directory.mkdir()
    result = evaluate_action(
        "vps.delete",
        {"path": str(directory)},
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == "BULK_MUTATION"


def test_shell_python_inside_portfolio_is_blocked():
    result = evaluate_action(
        "vps.shell",
        {"cwd": str(PORTFOLIO_ROOT), "command": "python3 analyse.py"},
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == NODE_SHELL_AUTOMATION


def test_shell_relative_cd_bypass_is_blocked():
    result = evaluate_action(
        "vps.shell",
        {
            "cwd": "/root/werkraum",
            "command": "cd in_gpt/job-portfolio-try && python3 -c 'print(1)'",
        },
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == NODE_SHELL_AUTOMATION


def test_allowlisted_exec_inside_portfolio_is_blocked():
    result = evaluate_action(
        "vps.exec_allowlisted",
        {"cwd": str(PORTFOLIO_ROOT), "argv": ["python3", "analyse.py"]},
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == NODE_SHELL_AUTOMATION


def test_read_only_shell_navigation_inside_portfolio_is_allowed():
    result = evaluate_action(
        "vps.shell",
        {"cwd": str(PORTFOLIO_ROOT), "command": "find PORTFOLIO -maxdepth 2 -type f"},
    )
    assert result.decision == DECISION_ALLOW


def test_read_only_search_for_meta_word_is_allowed():
    result = evaluate_action(
        "vps.shell",
        {"cwd": str(PORTFOLIO_ROOT), "command": "grep -R MANIFEST PORTFOLIO"},
    )
    assert result.decision == DECISION_ALLOW


def test_dev_null_redirection_is_read_only_enough_for_graph():
    result = evaluate_action(
        "vps.shell",
        {"cwd": str(PORTFOLIO_ROOT), "command": "grep -R MANIFEST PORTFOLIO 2>/dev/null | head -5"},
    )
    assert result.decision == DECISION_ALLOW


def test_real_file_redirection_is_blocked():
    result = evaluate_action(
        "vps.shell",
        {"cwd": str(PORTFOLIO_ROOT), "command": "printf x > generated.txt"},
    )
    assert result.decision == DECISION_BLOCK
    assert result.action_node == "BULK_MUTATION"


def test_single_script_write_is_not_blocked_by_its_suffix():
    result = evaluate_action(
        "vps.write_file",
        {"path": "/root/werkraum/some-other-project/build_something.py", "content": "print('x')"},
    )
    assert result.decision == DECISION_ALLOW
    assert result.project_scoped is True
    assert result.action_node == NODE_SINGLE_WRITE


def test_nested_output_path_is_seen():
    result = evaluate_action(
        "something.convert",
        {"options": {"output_path": str(PORTFOLIO_ROOT / "generated.bin")}},
    )
    assert result.decision == DECISION_BLOCK
    assert result.project_scoped is True


def test_graph_exposes_block_and_allowed_edges():
    graph = graph_snapshot()
    assert graph["state"] == STATE_MANUAL_DISCOVERY
    decisions = {(edge["to"], edge["decision"]) for edge in graph["edges"]}
    assert (NODE_SINGLE_WRITE, DECISION_ALLOW) in decisions
    assert any(decision == DECISION_ALLOW for _, decision in decisions)
