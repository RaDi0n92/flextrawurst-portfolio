#!/usr/bin/env python3
"""Small shared runtime for the AI-Strom-Brücke.

The daemon is intentionally boring: it receives Selkies' best-effort input
mirror, appends it to a JSONL ledger, and exposes a small state file. Browser
observation and explicit control are CLI capabilities so an AI runner can use
the same contract without owning a permanent process identity.
"""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from PIL import Image


# ``bridge.py`` remains a directly executable CLI.  Import the package by
# parent path so the new evidence contracts also work in that mode.
ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))
from ai_strom_bruecke.actions import ActionExecutor, XdotoolBackend  # noqa: E402
from ai_strom_bruecke.analysis_overlay import render_analysis_overlay  # noqa: E402
from ai_strom_bruecke.contracts import ActionExpectation, ActionPhase, CameraState, CoordinateKind, DiffKind, jsonable  # noqa: E402
from ai_strom_bruecke.earth_perception import ocr_status_bar, parse_earth_status_text  # noqa: E402
from ai_strom_bruecke.timeline import FrameTimeline, compare_frames  # noqa: E402
from ai_strom_bruecke.dom_only_policy import status as dom_only_status, reject as reject_non_dom  # noqa: E402
from ai_strom_bruecke.dom_bridge import add_parser as add_dom_parser  # noqa: E402


LEDGER = Path(os.environ.get("AI_STROM_BRUECKE_LEDGER", ROOT / "events.jsonl"))
STATE = Path(os.environ.get("AI_STROM_BRUECKE_STATE", ROOT / "state.json"))
TIMELINE_DIR = Path(os.environ.get("AI_STROM_BRUECKE_TIMELINE_DIR", ROOT / "timeline_frames"))
TIMELINE_JSON = Path(os.environ.get("AI_STROM_BRUECKE_TIMELINE_JSON", ROOT / "timeline.json"))
ACTIONS = Path(os.environ.get("AI_STROM_BRUECKE_ACTIONS", ROOT / "actions.jsonl"))
ANALYSIS_OVERLAY = Path(os.environ.get("AI_STROM_BRUECKE_ANALYSIS_OVERLAY", ROOT / "analysis-overlay.png"))
SOCKET = Path(
    os.environ.get(
        "AI_STROM_BRUECKE_EVENTS_SOCKET",
        "/var/lib/docker/volumes/webtop2_config/_data/ai-strom-bruecke-events.sock",
    )
)
LOCK = Path(os.environ.get("AI_STROM_BRUECKE_CONTROL_LOCK", "/tmp/ai-strom-bruecke-control.lock"))
VISION_GATE = Path(
    os.environ.get("AI_STROM_BRUECKE_INPUT_GATE", "/tmp/ai-strom-bruecke-input-gate.json")
)
DESKTOP_URL = os.environ.get("AI_STROM_BRUECKE_DESKTOP_URL", "http://127.0.0.1:3091/")
X11_CONTAINER = os.environ.get("AI_STROM_BRUECKE_X11_CONTAINER", "virtuellerdesktop2")
X11_DISPLAY = os.environ.get("AI_STROM_BRUECKE_X11_DISPLAY", ":1")
FRAME_TIMELINE = FrameTimeline(
    retention_seconds=float(os.environ.get("AI_STROM_BRUECKE_TIMELINE_SECONDS", "60")),
    fps=float(os.environ.get("AI_STROM_BRUECKE_TIMELINE_FPS", "10")),
    frame_dir=TIMELINE_DIR,
)
LAST_FRAME_PAYLOAD: bytes | None = None
LAST_OCR_AT = 0.0
LAST_OCR_TEXT = ""
LAST_OCR_CLAIM = None


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Several daemons write state/timeline files concurrently.  A shared
    # ``state.json.tmp`` lets one writer replace or unlink another writer's
    # temporary file, which used to cause restart loops with FileNotFoundError.
    # Give every write its own same-directory temporary inode and replace the
    # destination only after the complete JSON document has been flushed.
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _read_json(path: Path, fallback: dict) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else dict(fallback)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(fallback)


def _append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def _record_action(transaction) -> None:
    _append_jsonl(ACTIONS, jsonable(transaction))
    state = _read_json(STATE, {"name": "AI-Strom-Brücke"})
    state.update({
        "schema": "ai-strom-bruecke.state.v2",
        "action": jsonable(transaction),
        "action_id": transaction.action_id,
        "phase": transaction.phase.value,
        "decision_summary": transaction.result.get("decision_summary", transaction.phase.value),
    })
    _write_json(STATE, state)


def _record_capture_error(target: str, error: Exception) -> None:
    state = _read_json(STATE, {"name": "AI-Strom-Brücke"})
    state.update({
        "schema": "ai-strom-bruecke.state.v2", "mode": "observing", "target": target,
        "capture_error": str(error), "capture_error_at": time.time(),
        "gate": {"allow_input": False, "reason": "capture-error"},
    })
    _write_json(STATE, state)


def _record_frame(output: Path, target: str, capture_latency_ms: float | None = None) -> None:
    """Add one real capture to the bounded evidence timeline and state."""
    global LAST_FRAME_PAYLOAD, LAST_OCR_AT, LAST_OCR_TEXT, LAST_OCR_CLAIM
    payload = output.read_bytes()
    record = FRAME_TIMELINE.ingest(payload, source="x11", target=target, capture_latency_ms=capture_latency_ms)
    diff = compare_frames(LAST_FRAME_PAYLOAD, payload)
    LAST_FRAME_PAYLOAD = payload
    timeline = FRAME_TIMELINE.metadata()
    _write_json(TIMELINE_JSON, timeline)
    state = _read_json(STATE, {"name": "AI-Strom-Brücke"})
    state.update({
        "schema": "ai-strom-bruecke.state.v2",
        "mode": "observing",
        "target": target,
        "frame_id": record.envelope.frame_id,
        "frame_sequence": record.envelope.sequence,
        "frame_digest": record.envelope.digest,
        "frame_width": record.envelope.width,
        "frame_height": record.envelope.height,
        "frame_age_ms": 0.0,
        "frame_freshness": record.envelope.freshness,
        "frame_duplicate_of": record.envelope.duplicate_of,
        "capture_latency_ms": record.envelope.capture_latency_ms,
        "frame_diff": diff.to_dict(),
        "timeline": timeline,
        "last_frame_at": record.envelope.captured_at,
    })
    if target == "google-earth":
        now = time.time()
        ocr_interval = max(0.1, float(os.environ.get("AI_STROM_BRUECKE_OCR_INTERVAL", "0.5")))
        pointer_xy = None
        try:
            location = _xdotool("getmouselocation", "--shell")
            values = {}
            for line in location.splitlines():
                key, _, value = line.partition("=")
                if key in {"X", "Y"}:
                    values[key] = int(float(value))
            if "X" in values and "Y" in values:
                pointer_xy = {"x": values["X"], "y": values["Y"]}
        except (OSError, subprocess.CalledProcessError, ValueError):
            state["pointer_probe_error"] = "X11-Mausposition nicht lesbar"
        if now - LAST_OCR_AT >= ocr_interval or LAST_OCR_CLAIM is None:
            try:
                with Image.open(output) as image:
                    crop_height = min(100, image.height)
                    crop = (0, image.height - crop_height, image.width, image.height)
                LAST_OCR_TEXT = ocr_status_bar(payload, crop=crop)
                LAST_OCR_CLAIM = parse_earth_status_text(
                    LAST_OCR_TEXT,
                    frame_id=record.envelope.frame_id,
                    pointer_xy=pointer_xy,
                    coordinate_kind=CoordinateKind.POINTER,
                )
                LAST_OCR_AT = now
            except Exception as error:
                state["ocr_error"] = str(error)
        elif LAST_OCR_CLAIM is not None and pointer_xy:
            LAST_OCR_CLAIM.pointer_xy = pointer_xy
            LAST_OCR_CLAIM.frame_id = record.envelope.frame_id
        if LAST_OCR_CLAIM is not None:
            state["claims"] = [LAST_OCR_CLAIM.to_dict()]
            state["ocr_raw_text"] = LAST_OCR_TEXT
            state["camera"] = CameraState(
                state_id=f"camera-{record.envelope.sequence}",
                frame_id=record.envelope.frame_id,
                pointer_anchor=LAST_OCR_CLAIM,
                map_center=None,
                zoom=None,
                eye_altitude_m=LAST_OCR_CLAIM.eye_altitude_m,
                heading=None,
                tilt=None,
                loading=False,
                popup=None,
                street_view=False,
                focus=True,
                target=target,
                confidence=LAST_OCR_CLAIM.confidence,
                updated_at=now,
            ).to_dict()
        if pointer_xy:
            overlay = render_analysis_overlay(
                payload,
                pointer_xy=pointer_xy,
                label=f"pointer {pointer_xy['x']},{pointer_xy['y']} · {record.envelope.frame_id}",
            )
            ANALYSIS_OVERLAY.parent.mkdir(parents=True, exist_ok=True)
            temporary = ANALYSIS_OVERLAY.with_suffix(ANALYSIS_OVERLAY.suffix + ".tmp")
            temporary.write_bytes(overlay)
            temporary.replace(ANALYSIS_OVERLAY)
            state["analysis_overlay_url"] = "/analysis-overlay.png"
            state["analysis_overlay_frame_id"] = record.envelope.frame_id
    _write_json(STATE, state)


def _status() -> dict:
    value = {
        "name": "AI-Strom-Brücke",
        "schema": "ai-strom-bruecke.status.v1",
        "socket": str(SOCKET),
        "socket_present": SOCKET.exists(),
        "ledger": str(LEDGER),
        "ledger_present": LEDGER.exists(),
        "state": str(STATE),
        "state_present": STATE.exists(),
        "desktop_observer": "disabled-by-dom-only-policy",
        "playwright_primary_safe": False,
        "control_lease": str(LOCK),
    }
    value.update(dom_only_status())
    return value


def run_status(_: argparse.Namespace) -> int:
    print(json.dumps(_status(), ensure_ascii=False, indent=2))
    return 0


def run_daemon(_: argparse.Namespace) -> int:
    SOCKET.parent.mkdir(parents=True, exist_ok=True)
    try:
        SOCKET.unlink()
    except FileNotFoundError:
        pass

    receiver = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    receiver.bind(str(SOCKET))
    os.chmod(SOCKET, 0o660)
    _write_json(STATE, {"name": "AI-Strom-Brücke", "mode": "observing", "started": time.time()})
    print(f"AI-Strom-Brücke listening on {SOCKET}", flush=True)

    try:
        while True:
            raw = receiver.recv(65535)
            try:
                event = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                event = {"schema": "ai-strom-bruecke.event.v1", "raw": raw.decode("utf-8", "replace")}
            event.setdefault("received", time.time())
            with LEDGER.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            state = _read_json(STATE, {"name": "AI-Strom-Brücke", "mode": "observing"})
            state.update({"schema": "ai-strom-bruecke.state.v2", "mode": "observing", "last_event": event})
            _write_json(STATE, state)
    except KeyboardInterrupt:
        return 0
    finally:
        receiver.close()
        try:
            SOCKET.unlink()
        except FileNotFoundError:
            pass


def run_events(args: argparse.Namespace) -> int:
    deadline = time.monotonic() + args.seconds if args.seconds else None
    position = 0
    while True:
        if LEDGER.exists():
            with LEDGER.open(encoding="utf-8") as stream:
                stream.seek(position)
                for line in stream:
                    print(line, end="")
                position = stream.tell()
        if not args.follow or deadline is not None and time.monotonic() >= deadline:
            return 0
        time.sleep(0.25)


def _launch_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise SystemExit(f"Playwright fehlt: {error}") from error
    return sync_playwright()


def run_snapshot(args: argparse.Namespace) -> int:
    reject_non_dom("snapshot")
    started = time.monotonic()
    if args.wait_ms:
        time.sleep(args.wait_ms / 1000)
    _capture_x11(args.output, args.target)
    _record_frame(args.output, args.target, capture_latency_ms=(time.monotonic() - started) * 1000)
    print(args.output)
    return 0


def _with_control_lease():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        handle.close()
        raise SystemExit("AI-Strom-Brücke: Control-Lease ist bereits vergeben") from error
    return handle


def _require_fresh_vision(args: argparse.Namespace) -> None:
    """Refuse input unless the vision consumer is receiving fresh frames."""
    if args.unsafe_no_vision_gate:
        return
    try:
        gate = json.loads(VISION_GATE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as error:
        raise SystemExit(
            "AI-Strom-Brücke: Eingabe blockiert — kein Vision-Runner-Gate ("
            f"{VISION_GATE}; {error})"
        ) from error
    if not gate.get("allow_input"):
        raise SystemExit(
            "AI-Strom-Brücke: Eingabe blockiert — Vision-Runner: "
            + str(gate.get("reason", "unbekannter Zustand"))
        )
    age = gate.get("last_frame_age_s")
    last_frame_at = gate.get("last_frame_at")
    if last_frame_at is not None:
        try:
            age = max(0.0, time.time() - float(last_frame_at))
        except (TypeError, ValueError):
            age = None
    max_age = float(os.environ.get("AI_STROM_BRUECKE_MAX_FRAME_AGE", "1.0"))
    if age is None or float(age) > max_age:
        raise SystemExit(
            "AI-Strom-Brücke: Eingabe blockiert — letzter Vision-Frame ist zu alt "
            f"({age!r}s)"
        )


def _xdotool(*arguments: str) -> str:
    command = [
        "docker", "exec", "-e", f"DISPLAY={X11_DISPLAY}", X11_CONTAINER, "xdotool", *arguments
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout


def _window_id(target: str) -> str:
    if target == "active":
        return _xdotool("getactivewindow").strip()
    if target == "google-earth":
        try:
            windows = _xdotool("search", "--name", "Google Earth Pro").splitlines()
        except subprocess.CalledProcessError as error:
            raise SystemExit("AI-Strom-Brücke: Google Earth Pro ist nicht geöffnet") from error
        if not windows:
            raise SystemExit("AI-Strom-Brücke: Google Earth Pro ist nicht geöffnet")
        return windows[-1].strip()
    raise SystemExit(f"AI-Strom-Brücke: unbekanntes Snapshot-Ziel {target}")


def _activate_target(target: str) -> None:
    """Activate and focus a native target before dispatching input.

    Google Earth may report an active top-level window while its OpenGL map
    child still does not own keyboard focus.  ``windowactivate`` alone is
    therefore not a sufficient dispatch contract for real X11 actions.
    """
    if target == "active":
        return
    window = _window_id(target)
    _xdotool("windowactivate", "--sync", window)
    _xdotool("windowfocus", "--sync", window)


def _capture_x11(output: Path, target: str) -> None:
    """Capture one X11 window without opening a Selkies/Webtop client."""
    window = _window_id(target)
    captured = subprocess.run(
        [
            "docker", "exec", "-e", f"DISPLAY={X11_DISPLAY}", X11_CONTAINER,
            "import", "-window", window, "png:-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(captured)
    temporary.replace(output)


def run_observe(args: argparse.Namespace) -> int:
    reject_non_dom("observe")
    started = time.monotonic()
    interval = 1.0 / max(1.0, min(args.fps, 12.0))
    last_error = None
    last_error_at = 0.0
    while True:
        try:
            capture_started = time.monotonic()
            _capture_x11(args.output, args.target)
            _record_frame(args.output, args.target, capture_latency_ms=(time.monotonic() - capture_started) * 1000)
        except (OSError, subprocess.CalledProcessError) as error:
            # A closed app or an OpenGL/root window is a missing frame, not a
            # reason to crash-loop the systemd unit. The vision runner sees no
            # fresh mtime and closes the input gate on its own.
            now = time.monotonic()
            message = str(error)
            if message != last_error or now - last_error_at >= 10.0:
                print(
                    f"AI-Strom-Brücke: X11-Frame momentan nicht verfügbar: {error}",
                    file=sys.stderr,
                )
                last_error = message
                last_error_at = now
            _record_capture_error(args.target, error)
        if args.seconds and time.monotonic() - started >= args.seconds:
            return 0
        time.sleep(interval)


def _native_x11_control(args: argparse.Namespace, x: float | None = None, y: float | None = None) -> None:
    if args.action in {"move", "click"}:
        location = _xdotool("getmouselocation", "--shell")
        current = {}
        for line in location.splitlines():
            key, _, value = line.partition("=")
            if key in {"X", "Y"}:
                current[key] = float(value)
        start_x, start_y = current.get("X", 0), current.get("Y", 0)
        for step in range(1, max(1, args.steps) + 1):
            ratio = step / max(1, args.steps)
            target_x = round(start_x + (x - start_x) * ratio)
            target_y = round(start_y + (y - start_y) * ratio)
            _xdotool("mousemove", "--sync", str(target_x), str(target_y))
            time.sleep(0.012)
        if args.action == "click":
            _xdotool("click", "1")
    elif args.action == "type":
        _xdotool("type", "--delay", str(max(0, int(args.delay_ms))), args.values[0])
    elif args.action == "key":
        key = args.values[0]
        for old, new in (("Control", "ctrl"), ("Shift", "shift"), ("Alt", "alt"), ("Meta", "super")):
            key = key.replace(old, new)
        _xdotool("key", key)


def _parse_points(values: list[str], encoded: str | None) -> list[tuple[int, int]]:
    raw_points = encoded.split(";") if encoded else values
    points = []
    for raw in raw_points:
        parts = raw.replace(" ", "").split(",")
        if len(parts) != 2:
            raise SystemExit(f"Geste erwartet X,Y; erhalten: {raw!r}")
        try:
            points.append((int(float(parts[0])), int(float(parts[1]))))
        except ValueError as error:
            raise SystemExit(f"ungültiger Geste-Punkt: {raw!r}") from error
    if len(points) < 2:
        raise SystemExit("gesture braucht mindestens zwei X,Y-Punkte")
    return points


def _capture_for_action(target: str) -> tuple[Path, bytes]:
    path = Path(tempfile.gettempdir()) / f"ai-strom-action-{uuid.uuid4().hex}.png"
    _capture_x11(path, target)
    payload = path.read_bytes()
    return path, payload


def _acknowledge_native_action(transaction, before: bytes, target: str, wait_ms: int) -> None:
    """Use one fresh post-action frame as the first honest visual ack."""
    if wait_ms:
        time.sleep(wait_ms / 1000)
    path, after = _capture_for_action(target)
    try:
        diff = compare_frames(before, after)
        transaction.result["post_action_diff"] = diff.to_dict()
        accepted = diff.kind != DiffKind.UNCHANGED
        ActionExecutor.acknowledge(
            transaction,
            accepted=accepted,
            frame_ids=[f"post-action:{path.name}"],
            evidence={"diff": diff.to_dict()},
            reason="Post-Action-Frame blieb unverändert" if not accepted else None,
        )
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def run_control(args: argparse.Namespace) -> int:
    reject_non_dom("native control")
    if not args.lease:
        raise SystemExit("Steuerung verlangt ausdrücklich --lease")
    if args.action in {"move", "click"}:
        if len(args.values) != 2:
            raise SystemExit(f"{args.action} erwartet X Y")
        x, y = (float(value) for value in args.values)
    elif args.action == "gesture":
        points = _parse_points(args.values, args.points)
        x = y = None
    elif args.action == "keyhold":
        if len(args.values) != 1:
            raise SystemExit("keyhold erwartet genau einen Key")
        x = y = None
    elif args.action == "wheel":
        if len(args.values) > 1:
            raise SystemExit("wheel erwartet höchstens eine Richtung")
        x = y = None
    elif args.action == "stop":
        if args.values:
            raise SystemExit("stop erwartet keine Werte")
        x = y = None
    elif len(args.values) != 1:
        raise SystemExit(f"{args.action} erwartet genau einen Wert")
    if args.target != "active":
        # Resolve the target before taking the lease or sending any input. A
        # closed application must fail closed instead of steering another
        # foreground window.
        _window_id(args.target)
    if args.action != "stop":
        _require_fresh_vision(args)

    if args.action in {"gesture", "keyhold", "wheel", "stop"}:
        if args.webtop:
            raise SystemExit("Neue Held-/Stop-Aktionen dürfen nicht über --webtop laufen")
        _activate_target(args.target)
        if args.action == "stop":
            released = []
            for button in (1, 2, 3):
                try:
                    _xdotool("mouseup", str(button))
                    released.append({"kind": "mouseup", "value": button})
                except subprocess.CalledProcessError:
                    pass
            for key in ("w", "a", "s", "d", "Up", "Down", "Left", "Right", "shift", "ctrl"):
                try:
                    _xdotool("keyup", key)
                    released.append({"kind": "keyup", "value": key})
                except subprocess.CalledProcessError:
                    pass
            _append_jsonl(ACTIONS, {
                "schema": "ai-strom-bruecke.action.v2",
                "action_id": f"action-{uuid.uuid4().hex}",
                "action_type": "stop",
                "phase": ActionPhase.ACCEPTED.value,
                "released": released,
                "created_at": time.time(),
            })
            return 0
        backend = XdotoolBackend(container=X11_CONTAINER, display=X11_DISPLAY)
        executor = ActionExecutor(backend, lease_path=LOCK)
        before_path, before = _capture_for_action(args.target)
        # Window capture can leave the native OpenGL app without child focus.
        # Resolve and activate again immediately before dispatching input.
        _activate_target(args.target)
        try:
            if args.action == "gesture":
                transaction = executor.gesture(
                    actor=args.actor,
                    target=args.target,
                    points=points,
                    button=args.button,
                    hold_delay_s=max(0, args.hold_delay_ms) / 1000,
                    expectation=ActionExpectation(timeout_ms=args.timeout_ms, explanation=args.expectation),
                    timeout_s=args.timeout_ms / 1000,
                )
            elif args.action == "keyhold":
                transaction = executor.key_hold(
                    actor=args.actor,
                    target=args.target,
                    key=args.values[0],
                    duration_s=max(1, args.duration_ms) / 1000,
                    expectation=ActionExpectation(timeout_ms=args.timeout_ms, explanation=args.expectation),
                )
            else:
                direction = int(args.values[0]) if args.values else args.direction
                if direction == 0:
                    raise SystemExit("wheel direction darf nicht 0 sein")
                transaction = executor.wheel(
                    actor=args.actor,
                    target=args.target,
                    direction=direction,
                    expectation=ActionExpectation(timeout_ms=args.timeout_ms, explanation=args.expectation),
                )
            if transaction.phase == ActionPhase.DISPATCHED:
                _acknowledge_native_action(transaction, before, args.target, args.observe_wait_ms)
            _record_action(transaction)
            print(json.dumps(jsonable(transaction), ensure_ascii=False, indent=2))
            return 0 if transaction.phase == ActionPhase.ACCEPTED else 2
        finally:
            try:
                before_path.unlink()
            except FileNotFoundError:
                pass

    # Legacy-looking commands use the same transaction/evidence path when
    # they stay on the safe native X11 route.  Only explicit --webtop keeps
    # the old browser-primary compatibility branch below.
    if args.action in {"move", "click", "type", "key"} and not args.webtop:
        _activate_target(args.target)
        backend = XdotoolBackend(container=X11_CONTAINER, display=X11_DISPLAY)
        executor = ActionExecutor(backend, lease_path=LOCK)
        before_path, before = _capture_for_action(args.target)
        _activate_target(args.target)
        try:
            expectation = ActionExpectation(timeout_ms=args.timeout_ms, explanation=args.expectation)
            if args.action == "move":
                location = _xdotool("getmouselocation", "--shell")
                current = {}
                for line in location.splitlines():
                    key, _, value = line.partition("=")
                    if key in {"X", "Y"}:
                        current[key] = int(float(value))
                points = [(current.get("X", int(x)), current.get("Y", int(y))), (int(x), int(y))]
                transaction = executor.move_path(actor=args.actor, target=args.target, points=points, hold_delay_s=max(0, args.hold_delay_ms) / 1000, expectation=expectation, timeout_s=args.timeout_ms / 1000)
            elif args.action == "click":
                transaction = executor.click(actor=args.actor, target=args.target, button=1, expectation=expectation)
            elif args.action == "type":
                transaction = executor.type_text(actor=args.actor, target=args.target, value=args.values[0], delay_ms=args.delay_ms, expectation=expectation)
            else:
                transaction = executor.key_press(actor=args.actor, target=args.target, key=args.values[0], expectation=expectation)
            if transaction.phase == ActionPhase.DISPATCHED:
                _acknowledge_native_action(transaction, before, args.target, args.observe_wait_ms)
            _record_action(transaction)
            print(json.dumps(jsonable(transaction), ensure_ascii=False, indent=2))
            return 0 if transaction.phase == ActionPhase.ACCEPTED else 2
        finally:
            try:
                before_path.unlink()
            except FileNotFoundError:
                pass

    lease = _with_control_lease()
    try:
        if args.webtop:
            with _launch_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
                page = browser.new_page(viewport={"width": 1280, "height": 720})
                page.goto(DESKTOP_URL, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                if args.action == "move":
                    page.mouse.move(x, y, steps=max(1, args.steps))
                elif args.action == "click":
                    page.mouse.move(x, y, steps=max(1, args.steps))
                    page.mouse.click(x, y)
                elif args.action == "type":
                    page.keyboard.type(args.values[0], delay=args.delay_ms)
                elif args.action == "key":
                    page.keyboard.press(args.values[0])
                browser.close()
        else:
            _activate_target(args.target)
            _native_x11_control(args, x, y)
    finally:
        fcntl.flock(lease.fileno(), fcntl.LOCK_UN)
        lease.close()
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="ai-strom-bruecke")
    commands = root.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status")
    status.set_defaults(func=run_status)
    daemon = commands.add_parser("daemon")
    daemon.set_defaults(func=run_daemon)
    events = commands.add_parser("events")
    events.add_argument("--follow", action="store_true")
    events.add_argument("--seconds", type=float)
    events.set_defaults(func=run_events)
    add_dom_parser(commands)
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument("--wait-ms", type=int, default=1500)
    snapshot.add_argument("--target", choices=["active", "google-earth"], default="active")
    snapshot.set_defaults(func=run_snapshot)
    observe = commands.add_parser(
        "observe",
        help="Schreibt laufend aktuelle X11-Frames, ohne eine Selkies-Verbindung zu öffnen",
    )
    observe.add_argument("--output", type=Path, required=True)
    observe.add_argument("--target", choices=["active", "google-earth"], default="active")
    observe.add_argument("--fps", type=float, default=10.0)
    observe.add_argument("--seconds", type=float, default=0.0)
    observe.set_defaults(func=run_observe)
    control = commands.add_parser("control")
    control.add_argument("action", choices=["move", "click", "type", "key", "gesture", "keyhold", "wheel", "stop"])
    control.add_argument("values", nargs="*")
    control.add_argument("--lease", action="store_true")
    control.add_argument("--steps", type=int, default=12)
    control.add_argument("--delay-ms", type=float, default=15)
    control.add_argument("--points", help="gesture points als X,Y;X,Y;...")
    control.add_argument("--button", type=int, choices=[1, 2, 3], default=1)
    control.add_argument("--hold-delay-ms", type=float, default=12)
    control.add_argument("--duration-ms", type=int, default=350)
    control.add_argument("--direction", type=int, default=1)
    control.add_argument("--timeout-ms", type=int, default=2500)
    control.add_argument("--observe-wait-ms", type=int, default=150)
    control.add_argument("--expectation", default="native action with fresh post-action frame")
    control.add_argument("--actor", default="codex")
    control.add_argument("--target", choices=["active", "google-earth"], default="active")
    control.add_argument("--webtop", action="store_true", help="legacy: use a Selkies primary connection")
    control.set_defaults(func=run_control)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    sys.exit(arguments.func(arguments))
