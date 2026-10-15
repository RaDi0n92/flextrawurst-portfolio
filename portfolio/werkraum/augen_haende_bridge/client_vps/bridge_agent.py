"""Read-only VPS-side Bridge agent for the first target-inventory slice.

This process does not execute shell commands or accept terminal input. It owns
the Linux-side TargetRegistry and answers only the authenticated inventory
request handled by BridgeRuntime.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import threading

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from augen_haende_bridge.target_registry import TargetRegistry


def build_inventory_agent(
    url: str,
    token: str,
    *,
    registry: TargetRegistry | None = None,
    on_event=None,
) -> tuple[BridgeRuntime, TargetRegistry]:
    """Build an explicit VPS agent without connecting during construction."""

    target_registry = registry or TargetRegistry()
    runtime = BridgeRuntime(
        url,
        token,
        on_event=on_event or _report_event,
        inventory_provider=target_registry.bridge_inventory,
    )
    return runtime, target_registry


def _report_event(event: dict[str, object]) -> None:
    if event.get("kind") in {
        "runtime.failed",
        "runtime.inventory_provider_failed",
        "error",
    }:
        print(json.dumps(event, ensure_ascii=False), flush=True)


def run(url: str, token: str) -> int:
    runtime, _registry = build_inventory_agent(url, token)
    stopped = threading.Event()

    def stop(_signum, _frame) -> None:
        stopped.set()

    for signal_name in ("SIGINT", "SIGTERM"):
        signal_number = getattr(signal, signal_name, None)
        if signal_number is not None:
            signal.signal(signal_number, stop)

    runtime.start()
    try:
        while not stopped.wait(.25):
            if runtime.failure is not None:
                return 1
    finally:
        runtime.stop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("BRIDGE_URL", "ws://127.0.0.1:19880"))
    parser.add_argument("--token", default=os.environ.get("BRIDGE_AGENT_TOKEN"))
    args = parser.parse_args()
    if not args.token:
        parser.error("--token or BRIDGE_AGENT_TOKEN is required")
    return run(args.url, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
