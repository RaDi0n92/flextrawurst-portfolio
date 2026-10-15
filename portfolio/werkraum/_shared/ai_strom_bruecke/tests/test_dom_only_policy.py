import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "bridge.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT.parent)}
    return subprocess.run(
        [sys.executable, str(BRIDGE), *args],
        cwd=ROOT.parent.parent,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_status_declares_fail_closed_dom_only_policy():
    result = _run("status")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["policy"] == "ai-strom-bruecke.dom-only.v1"
    assert payload["screenshots"] == "forbidden"
    assert payload["native_x11"] == "forbidden"


def test_visual_and_native_commands_are_rejected():
    for command in (
        ("snapshot", "--output", "/tmp/blocked.png"),
        ("observe", "--output", "/tmp/blocked.png"),
        ("control", "key", "w", "--lease"),
    ):
        result = _run(*command)
        assert result.returncode != 0
        assert "dom-only" in result.stderr.lower() or "dom-only" in result.stdout.lower()


def test_dom_policy_command_does_not_need_a_browser_connection():
    result = _run("dom", "policy")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["allowed_browser_channel"] == "Firefox WebDriver BiDi DOM"
