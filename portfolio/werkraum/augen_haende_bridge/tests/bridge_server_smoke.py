"""G08 live proof: current VPS relay plus read-only inventory agent.

This stays local and ephemeral. It does not touch the stale historical
listener, Windows, or any production journal.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import secrets
import sys
import tempfile
from pathlib import Path

from augen_haende_bridge.transport_client import BridgeClient


READY_PORT = re.compile(r"127\.0\.0\.1:(\d+)")


async def _read_ready(process: asyncio.subprocess.Process) -> str:
    if process.stdout is None:
        raise RuntimeError("server_stdout_missing")
    try:
        line = await asyncio.wait_for(process.stdout.readline(), timeout=15)
    except asyncio.TimeoutError as exc:
        raise RuntimeError("server_ready_timeout") from exc
    decoded = line.decode("utf-8", "replace").strip()
    if process.returncode is not None:
        raise RuntimeError(f"server_exited_before_ready: {process.returncode}")
    if READY_PORT.search(decoded) is None:
        raise RuntimeError(f"unexpected_server_ready_line: {decoded!r}")
    return decoded


async def _run() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    desktop_token = secrets.token_urlsafe(32)
    agent_token = secrets.token_urlsafe(32)
    environment = os.environ.copy()
    environment["BRIDGE_DESKTOP_TOKEN"] = desktop_token
    environment["BRIDGE_AGENT_TOKEN"] = agent_token
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(root / "src"), str(root), environment.get("PYTHONPATH", "")]
    )

    with tempfile.TemporaryDirectory(prefix="bridge-g08-smoke-") as temp:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(root / "client_vps" / "bridge_server.py"),
            "--port",
            "0",
            "--journal",
            str(Path(temp) / "relay.sqlite3"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
        )
        try:
            ready_line = await _read_ready(process)
            port_match = READY_PORT.search(ready_line)
            assert port_match is not None
            url = f"ws://127.0.0.1:{port_match.group(1)}"
            async with BridgeClient(url, desktop_token) as desktop:
                await desktop.publish(
                    "target_inventory_request",
                    {"scope": "terminals"},
                    message_id="g08-smoke-inventory",
                )
                event = await desktop.receive(timeout=5)
                while event.get("kind") != "event":
                    event = await desktop.receive(timeout=5)
                assert event["event_kind"] == "target_inventory"
                assert event["payload"]["request_id"] == "g08-smoke-inventory"
                await desktop.confirm_received(event)
                return {
                    "relay": "current_entrypoint",
                    "transport": "loopback",
                    "vps_agent": "connected",
                    "inventory_event": "received_and_confirmed",
                    "target_count": len(event["payload"]["targets"]),
                }
        finally:
            if process.returncode is None:
                process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()


def main() -> int:
    result = asyncio.run(_run())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
