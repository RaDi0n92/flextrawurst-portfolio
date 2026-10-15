#!/usr/bin/env python3
"""Opt-in visual companion to the DOM-only AI-Strom-Brücke.

This is a second entry point. ``bridge.py`` and ``dom_bridge.py`` keep their
DOM-only contract. This companion adds one explicit capability: Firefox BiDi
viewport screenshots. Every action keeps the same control lease, reads a
fresh DOM report before and after the action, and records a screenshot/DOM
pair immediately and at a fixed 100 ms cadence. Physical actions can also be
combined into one atomic BiDi input batch; no screenshot is taken between
commands inside that batch.

It does not connect to Selkies, Playwright, X11, xdotool, OCR or a vision
model. A screenshot is an evidence artefact for a human/agent to inspect; the
bridge does not invent a semantic place claim from pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from ai_strom_bruecke.dom_bridge import _lease  # noqa: E402
from ai_strom_bruecke.firefox_dom import FirefoxDomSession  # noqa: E402
from ai_strom_bruecke.timeline import compare_frames  # noqa: E402
from ai_strom_bruecke.visual_firefox import SCREENSHOT_FORMAT, FirefoxVisualSession  # noqa: E402
from ai_strom_bruecke.visual_policy import PERCEPTION_SOURCE, POLICY_ID, status  # noqa: E402


DEFAULT_OUTPUT_ROOT = Path(
    os.environ.get("AI_STROM_BRUECKE_VISUAL_DIR", "/tmp/ai-strom-bruecke-visual")
)
DEFAULT_INTERVAL_MS = 100
DEFAULT_OBSERVE_MS = 1000


def _report(session: FirefoxDomSession, context_id: str | None) -> tuple[str, dict[str, Any]]:
    target = session.target(context_id)
    report = session.inspect_google_earth(target.context_id)
    report.update(
        {
            "context_id": target.context_id,
            "policy": POLICY_ID,
            "perception_source": PERCEPTION_SOURCE,
        }
    )
    return target.context_id, report


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _capture(
    session: FirefoxVisualSession,
    context_id: str,
    run_dir: Path,
    phase: str,
    index: int,
    *,
    return_payload: bool = False,
    include_dom: bool = True,
    scheduled_at: float | None = None,
) -> dict[str, Any]:
    started_at = time.monotonic()
    dom = _report(session, context_id)[1] if include_dom else None
    payload = session.capture_screenshot(context_id)
    completed_at = time.monotonic()
    captured_at = time.time()
    digest = hashlib.sha256(payload).hexdigest()
    path = run_dir / f"{index:04d}-{phase}.jpg"
    path.write_bytes(payload)
    result = {
        "index": index,
        "phase": phase,
        "captured_at": captured_at,
        "monotonic_at": completed_at,
        "path": str(path),
        "sha256": digest,
        "bytes": len(payload),
        "format": dict(SCREENSHOT_FORMAT),
        "dom": dom,
        "dom_checked": include_dom,
        "capture_latency_ms": round((completed_at - started_at) * 1000, 3),
    }
    if scheduled_at is not None:
        elapsed = max(0.0, completed_at - scheduled_at)
        result["scheduled_at_monotonic"] = scheduled_at
        result["cadence_lag_ms"] = round(elapsed * 1000, 3)
    if return_payload:
        result["_payload"] = payload
    return result


def _sample(
    session: FirefoxVisualSession,
    context_id: str,
    run_dir: Path,
    *,
    interval_ms: int,
    observe_ms: int,
    phase: str,
    start_index: int,
    previous_payload: bytes | None = None,
) -> tuple[list[dict[str, Any]], bytes | None]:
    interval = max(1, interval_ms) / 1000
    deadline = time.monotonic() + max(0, observe_ms) / 1000
    next_at = time.monotonic()
    frames: list[dict[str, Any]] = []
    index = start_index
    while True:
        wait = next_at - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        scheduled_at = next_at
        frame = _capture(
            session,
            context_id,
            run_dir,
            phase,
            index,
            return_payload=True,
            include_dom=False,
            scheduled_at=scheduled_at,
        )
        payload = frame.pop("_payload")
        frame["analysis"] = compare_frames(previous_payload, payload).to_dict()
        frame["cadence_missed_ticks"] = max(
            0,
            math.ceil(
                max(0.0, frame["monotonic_at"] - scheduled_at) / interval
            )
            - 1,
        )
        frames.append(frame)
        previous_payload = payload
        index += 1
        if time.monotonic() >= deadline:
            break
        next_at += interval
    return frames, previous_payload


def _analysis_summary(frames: list[dict[str, Any]]) -> dict[str, Any]:
    analyses = [frame["analysis"] for frame in frames if "analysis" in frame]
    changed = [item for item in analyses if item.get("digest_changed")]
    return {
        "frames": len(frames),
        "changed_frames": len(changed),
        "unchanged_frames": len(analyses) - len(changed),
        "missed_100ms_ticks": sum(frame.get("cadence_missed_ticks", 0) for frame in frames),
        "dom_checked_frames": sum(1 for frame in frames if frame.get("dom_checked")),
        "screenshot_only_frames": sum(1 for frame in frames if not frame.get("dom_checked")),
        "last": analyses[-1] if analyses else None,
    }


def _parse_batch(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        raise SystemExit("visual action batch verlangt --actions mit JSON-Liste")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"visual action batch: ungültiges JSON: {exc}") from exc
    if not isinstance(value, list) or not value:
        raise SystemExit("visual action batch verlangt eine nichtleere JSON-Liste")
    if not all(isinstance(item, dict) for item in value):
        raise SystemExit("visual action batch: jedes Element muss ein Objekt sein")
    allowed = {"key", "keyhold", "click", "wheel"}
    for index, item in enumerate(value):
        if item.get("type") not in allowed:
            raise SystemExit(
                f"visual action batch command {index}: nur key, keyhold, click und wheel sind erlaubt"
            )
    return value


def _dispatch(session: FirefoxVisualSession, context_id: str, args: argparse.Namespace) -> str:
    if args.operation == "batch":
        session.perform_input_batch(context_id, args.batch_commands)
        return f"batch:{len(args.batch_commands)}-commands"
    if args.operation == "pointer-click":
        session.pointer_click(context_id, args.x, args.y, args.button)
        return f"pointer-click:{args.x},{args.y}:{args.button}"
    if args.operation == "wheel":
        session.wheel(context_id, args.delta_x, args.delta_y, args.x, args.y)
        return f"wheel:{args.delta_x},{args.delta_y}@{args.x},{args.y}"
    if args.operation == "key":
        session.key_down(context_id, args.key)
        session.key_up(context_id, args.key)
        return f"key:{args.key}"
    if args.operation == "release":
        session.release_actions(context_id)
        return "release"
    raise SystemExit(f"Unbekannte Visual-Operation: {args.operation}")


def _run_action(
    args: argparse.Namespace,
    session_factory: Callable[..., FirefoxVisualSession] = FirefoxVisualSession,
) -> dict[str, Any]:
    run_id = f"visual-{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir = Path(args.output_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    with session_factory() as session:
        with _lease():
            context_id, before = _report(session, args.context)
            activation = session.activate_context(context_id)
            before_frame = _capture(
                session,
                context_id,
                run_dir,
                "before",
                0,
                return_payload=True,
            )
            before_payload = before_frame.pop("_payload")
            before_frame["analysis"] = compare_frames(None, before_payload).to_dict()
            frames: list[dict[str, Any]] = []
            current_payload = before_payload
            action: str
            try:
                if args.operation == "keyhold":
                    session.key_down(context_id, args.key)
                    try:
                        frames, current_payload = _sample(
                            session,
                            context_id,
                            run_dir,
                            interval_ms=args.interval_ms,
                            observe_ms=args.hold_ms,
                            phase="held",
                            start_index=1,
                            previous_payload=current_payload,
                        )
                    finally:
                        session.key_up(context_id, args.key)
                    remaining_ms = max(0, args.observe_ms - args.hold_ms)
                    if remaining_ms:
                        released, current_payload = _sample(
                            session,
                            context_id,
                            run_dir,
                            interval_ms=args.interval_ms,
                            observe_ms=remaining_ms,
                            phase="released",
                            start_index=len(frames) + 1,
                            previous_payload=current_payload,
                        )
                        frames.extend(released)
                    action = f"keyhold:{args.key}:{args.hold_ms}ms"
                else:
                    action = _dispatch(session, context_id, args)
                    frames, current_payload = _sample(
                        session,
                        context_id,
                        run_dir,
                        interval_ms=args.interval_ms,
                        observe_ms=args.observe_ms,
                        phase="after",
                        start_index=1,
                        previous_payload=current_payload,
                    )
            finally:
                if session.held_buttons or session.held_keys:
                    session.release_actions(context_id)
            _, after = _report(session, context_id)

    result = {
        "schema": "ai-strom-bruecke.visual-action.v1",
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "action": action,
        "context_id": context_id,
        "activation": {"method": "browsingContext.activate", "result": activation},
        "before": before,
        "after": after,
        "before_frame": before_frame,
        "frames": frames,
        "batch_commands": getattr(args, "batch_commands", None),
        "interval_ms": args.interval_ms,
        "observe_ms": args.observe_ms,
        "visual_frame_changed": any(
            frame.get("analysis", {}).get("digest_changed") for frame in frames
        ),
        "screenshot_analysis": _analysis_summary(frames),
        "screenshot_boundary": "after-complete-action-or-batch",
        "created_at": time.time(),
    }
    _write_json(run_dir / "run.json", result)
    return result


def _inspect(
    args: argparse.Namespace,
    session_factory: Callable[..., FirefoxVisualSession] = FirefoxVisualSession,
) -> dict[str, Any]:
    run_id = f"inspect-{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    run_dir = Path(args.output_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    with session_factory() as session:
        context_id, report = _report(session, args.context)
        activation = session.activate_context(context_id)
        frame = _capture(session, context_id, run_dir, "inspect", 0)
    result = {
        "schema": "ai-strom-bruecke.visual-inspect.v1",
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "context_id": context_id,
        "activation": {"method": "browsingContext.activate", "result": activation},
        "dom": report,
        "frame": frame,
    }
    _write_json(run_dir / "run.json", result)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-strom-bruecke-visual")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status").set_defaults(operation="status")
    inspect = commands.add_parser(
        "inspect", help="frischer DOM-Bericht plus ein Firefox-BiDi-Screenshot"
    )
    inspect.add_argument("--context")
    inspect.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT)
    inspect.set_defaults(operation="inspect")
    action = commands.add_parser(
        "action",
        help="physische Tastatur/Maus-Aktion plus Screenshotfolge; batch ohne Zwischenbilder",
    )
    action.add_argument(
        "operation",
        choices=["pointer-click", "wheel", "key", "keyhold", "batch", "release"],
    )
    action.add_argument("--context")
    action.add_argument("--actions", help="JSON-Liste für batch")
    action.add_argument("--x", type=int, default=0)
    action.add_argument("--y", type=int, default=0)
    action.add_argument("--delta-x", type=int, default=0)
    action.add_argument("--delta-y", type=int, default=0)
    action.add_argument("--button", choices=["left", "middle", "right"], default="left")
    action.add_argument("--key")
    action.add_argument("--hold-ms", type=int, default=350)
    action.add_argument("--interval-ms", type=int, default=DEFAULT_INTERVAL_MS)
    action.add_argument("--observe-ms", type=int, default=DEFAULT_OBSERVE_MS)
    action.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.operation == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0
    if args.operation == "inspect":
        result = _inspect(args)
    else:
        if args.operation in {"key", "keyhold"} and not args.key:
            raise SystemExit(f"visual action {args.operation} verlangt --key")
        if args.operation == "batch":
            args.batch_commands = _parse_batch(args.actions)
        if args.interval_ms != DEFAULT_INTERVAL_MS:
            raise SystemExit(
                f"Visual-Workflow verlangt den festen Screenshot-Takt von {DEFAULT_INTERVAL_MS} ms"
            )
        if args.observe_ms < 0 or args.hold_ms < 0:
            raise SystemExit("--observe-ms und --hold-ms dürfen nicht negativ sein")
        result = _run_action(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
