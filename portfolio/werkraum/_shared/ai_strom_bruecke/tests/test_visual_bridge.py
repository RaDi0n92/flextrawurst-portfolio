import base64
import json
from pathlib import Path

from ai_strom_bruecke.visual_bridge import _capture, _parser
from ai_strom_bruecke.visual_firefox import FirefoxVisualSession
from ai_strom_bruecke.visual_policy import status


class _FakeVisualSession:
    def __init__(self):
        self.index = 0

    def target(self, context_id=None):
        return type(
            "Target",
            (),
            {
                "context_id": "ctx",
                "url": "https://earth.google.com/web/",
                "title": "Google Earth",
            },
        )()

    def inspect_google_earth(self, context_id):
        return {"url": "https://earth.google.com/web/", "title": "Google Earth", "canvases": []}

    def capture_screenshot(self, context_id):
        self.index += 1
        return f"png-{self.index}".encode()


def test_visual_policy_is_separate_and_explicit():
    payload = status()
    assert payload["policy"] == "ai-strom-bruecke.visual.v1"
    assert payload["screenshots"] == "allowed-via-firefox-bidi"
    assert payload["native_x11"] == "forbidden"


def test_visual_capture_writes_hashable_frame(tmp_path: Path):
    session = _FakeVisualSession()
    frame = _capture(session, "ctx", tmp_path, "before", 0)
    assert Path(frame["path"]).read_bytes() == b"png-1"
    assert len(frame["sha256"]) == 64
    assert frame["dom"]["title"] == "Google Earth"


def test_visual_parser_defaults_to_100ms():
    args = _parser().parse_args(["action", "keyhold", "--key", "w"])
    assert args.interval_ms == 100
    assert args.observe_ms == 1000


def test_visual_batch_parser_accepts_only_physical_commands():
    actions = json.dumps(
        [
            {"type": "keyhold", "key": "w", "duration_ms": 500},
            {"type": "key", "key": "a"},
            {"type": "click", "x": 10, "y": 20},
        ]
    )
    args = _parser().parse_args(["action", "batch", "--actions", actions])
    assert args.operation == "batch"
    assert args.interval_ms == 100


def test_visual_batch_is_one_bidi_input_command_without_screenshot():
    session = FirefoxVisualSession("ws://unused")
    calls = []

    def command(method, params=None):
        calls.append((method, params or {}))
        return {}

    session.command = command
    session.perform_input_batch(
        "ctx",
        [
            {"type": "keyhold", "key": "w", "duration_ms": 500},
            {"type": "key", "key": "a"},
            {"type": "click", "x": 10, "y": 20},
        ],
    )
    assert [method for method, _ in calls] == ["input.performActions"]
    sources = calls[0][1]["actions"]
    assert {source["type"] for source in sources} == {"key", "pointer"}
    assert all("captureScreenshot" not in method for method, _ in calls)


def test_visual_screenshot_command_decodes_bidi_data():
    session = FirefoxVisualSession("ws://unused")
    calls = []

    def command(method, params=None):
        calls.append((method, params or {}))
        return {"data": base64.b64encode(b"png").decode()}

    session.command = command
    assert session.capture_screenshot("ctx") == b"png"
    assert calls[0][0] == "browsingContext.captureScreenshot"
    assert calls[0][1]["context"] == "ctx"
    assert calls[0][1]["format"] == {"type": "image/jpeg", "quality": 0.3}


def test_visual_context_activation_is_a_bidi_focus_sync():
    session = FirefoxVisualSession("ws://unused")
    calls = []

    def command(method, params=None):
        calls.append((method, params or {}))
        return {}

    session.command = command
    session.activate_context("ctx")
    assert calls == [("browsingContext.activate", {"context": "ctx"})]
