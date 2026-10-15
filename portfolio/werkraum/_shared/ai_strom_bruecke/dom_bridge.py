#!/usr/bin/env python3
"""The only permitted interactive browser bridge: Firefox BiDi + DOM.

No display handle, image buffer, OCR call, screenshot API or native desktop
input is imported here.  The module deals in DOM reports and WebDriver BiDi
input actions only.  It is deliberately a separate command from the legacy
bridge so the policy boundary is obvious and testable.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from .dom_only_policy import POLICY_ID, PERCEPTION_SOURCE, status
from .firefox_dom import FirefoxDomError, FirefoxDomSession


LEASE = Path(os.environ.get("AI_STROM_BRUECKE_DOM_CONTROL_LOCK", "/tmp/ai-strom-bruecke-dom-control.lock"))


@contextmanager
def _lease() -> Iterator[None]:
    LEASE.parent.mkdir(parents=True, exist_ok=True)
    handle = LEASE.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit("AI-Strom-Brücke: DOM-Control-Lease ist bereits vergeben") from exc
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _report(session: FirefoxDomSession, context_id: str | None) -> tuple[str, dict[str, Any]]:
    target = session.target(context_id)
    report = session.inspect_google_earth(target.context_id)
    report.update({
        "context_id": target.context_id,
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
    })
    return target.context_id, report


def _result(action: str, before: dict[str, Any], after: dict[str, Any], **extra: Any) -> dict[str, Any]:
    value = {
        "schema": "ai-strom-bruecke.dom-action.v1",
        "policy": POLICY_ID,
        "perception_source": PERCEPTION_SOURCE,
        "action": action,
        "before": before,
        "after": after,
        "created_at": time.time(),
    }
    value.update(extra)
    return value


def execute(args: argparse.Namespace, session_factory: Callable[..., FirefoxDomSession] = FirefoxDomSession) -> int:
    if args.operation == "policy":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0

    with session_factory() as session:
        context_id, before = _report(session, args.context)
        if args.operation == "inspect":
            print(json.dumps(before, ensure_ascii=False, indent=2))
            return 0

        with _lease():
            try:
                if args.operation == "click-selector":
                    session.click_selector(context_id, args.selector)
                    action = f"click-selector:{args.selector}"
                elif args.operation == "pointer-click":
                    session.pointer_click(context_id, args.x, args.y, args.button)
                    action = f"pointer-click:{args.x},{args.y}:{args.button}"
                elif args.operation == "wheel":
                    session.wheel(context_id, args.delta_x, args.delta_y, args.x, args.y)
                    action = f"wheel:{args.delta_x},{args.delta_y}@{args.x},{args.y}"
                elif args.operation == "key":
                    session.key_down(context_id, args.key)
                    session.key_up(context_id, args.key)
                    action = f"key:{args.key}"
                elif args.operation == "keyhold":
                    session.key_down(context_id, args.key)
                    try:
                        time.sleep(max(0, args.duration_ms) / 1000)
                    finally:
                        session.key_up(context_id, args.key)
                    action = f"keyhold:{args.key}:{args.duration_ms}ms"
                elif args.operation == "release":
                    session.release_actions(context_id)
                    action = "release"
                else:  # pragma: no cover - argparse prevents this
                    raise SystemExit(f"Unbekannte DOM-Operation: {args.operation}")
                _, after = _report(session, context_id)
            finally:
                if session.held_buttons or session.held_keys:
                    session.release_actions(context_id)

    print(json.dumps(_result(action, before, after), ensure_ascii=False, indent=2))
    return 0


def add_parser(commands: argparse._SubParsersAction) -> None:
    dom = commands.add_parser("dom", help="einziger erlaubter Browserkanal: Firefox-BiDi-DOM")
    dom.add_argument("operation", choices=["policy", "inspect", "click-selector", "pointer-click", "wheel", "key", "keyhold", "release"])
    dom.add_argument("values", nargs="*")
    dom.add_argument("--context")
    dom.add_argument("--selector")
    dom.add_argument("--x", type=int, default=0)
    dom.add_argument("--y", type=int, default=0)
    dom.add_argument("--delta-x", type=int, default=0)
    dom.add_argument("--delta-y", type=int, default=0)
    dom.add_argument("--button", choices=["left", "middle", "right"], default="left")
    dom.add_argument("--key")
    dom.add_argument("--duration-ms", type=int, default=350)
    dom.set_defaults(func=_validate_and_execute)


def _validate_and_execute(args: argparse.Namespace) -> int:
    if args.operation in {"click-selector"} and not args.selector:
        raise SystemExit("dom click-selector verlangt --selector")
    if args.operation in {"key", "keyhold"} and not args.key:
        raise SystemExit(f"dom {args.operation} verlangt --key")
    if args.operation not in {"policy", "inspect", "click-selector", "pointer-click", "wheel", "key", "keyhold", "release"}:
        raise SystemExit("DOM-only policy: Operation abgewiesen")
    return execute(args)
