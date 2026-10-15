"""Exercise the packaged Windows GUI against the local relay under Wine.

This is a package/process proof only. Wine is explicitly not treated as
native Windows evidence. The relay receipt proves that the packaged process
received the message; the window title is the external visible render witness.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import time

from augen_haende_bridge.transport import Journal, Principal, Relay
from augen_haende_bridge.transport_client import BridgeClient


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "dist" / "AugenUndHaendeBridge" / "AugenUndHaendeBridge.exe"
WINE_PREFIX = Path(os.environ.get("WINEPREFIX", "/tmp/augen-haende-winbuild.ieRV30/wine"))
WINDOW_MARKER = "say-received"


def _window_tree() -> str:
    result = subprocess.run(
        ["xwininfo", "-root", "-tree"],
        env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")},
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


async def run() -> None:
    wine = shutil.which("wine")
    xwininfo = shutil.which("xwininfo")
    if wine is None or xwininfo is None:
        raise RuntimeError("wine_and_xwininfo_required")
    if not EXE.is_file():
        raise RuntimeError(f"packaged_exe_missing:{EXE}")
    if not WINE_PREFIX.is_dir():
        raise RuntimeError(f"wine_prefix_missing:{WINE_PREFIX}")

    with tempfile.TemporaryDirectory(prefix="bridge-g06-") as temp:
        journal = Journal(Path(temp) / "g06.sqlite")
        desktop_token = secrets.token_urlsafe(32)
        agent_token = secrets.token_urlsafe(32)
        relay = Relay(
            [
                Principal("desktop", desktop_token, "agent", "g06-target", can_request_inventory=True),
                Principal("agent", agent_token, "desktop", "g06-target", can_publish_inventory=True),
            ],
            journal,
        )
        process: subprocess.Popen[bytes] | None = None
        process_log = Path(temp) / "wine-process.log"
        process_log_handle = None
        try:
            async with relay.listen(origins=[None]) as server:
                url = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}"
                async with BridgeClient(url, agent_token) as agent:
                    env = {
                        **os.environ,
                        "DISPLAY": os.environ.get("DISPLAY", ":1"),
                        "WINEPREFIX": str(WINE_PREFIX),
                        "WINEARCH": "win64",
                        "WINEDEBUG": "-all",
                        "BRIDGE_URL": url,
                        "BRIDGE_TOKEN": desktop_token,
                    }
                    process_log_handle = process_log.open("wb")
                    process = subprocess.Popen(
                        [wine, str(EXE)],
                        env=env,
                        stdout=process_log_handle,
                        stderr=subprocess.STDOUT,
                    )

                    for _ in range(150):
                        if "desktop" in relay.connections:
                            break
                        if process.poll() is not None:
                            raise RuntimeError(f"packaged_exe_exited:{process.returncode}")
                        await asyncio.sleep(0.1)
                    else:
                        raise RuntimeError("packaged_exe_bridge_connect_timeout")

                    inventory_request = await agent.receive()
                    if inventory_request.get("event_kind") != "target_inventory_request":
                        raise AssertionError(f"unexpected_inventory_request:{inventory_request}")
                    await agent.confirm_received(inventory_request)
                    inventory_receipt = await agent.receive()
                    if inventory_receipt.get("kind") != "receipt_recorded":
                        raise AssertionError(f"inventory_receipt_missing:{inventory_receipt}")
                    await agent.publish(
                        "target_inventory",
                        {
                            "request_id": inventory_request["id"],
                            "status": "ok",
                            "captured_at_ms": int(time.time() * 1000),
                            "targets": [
                                {
                                    "id": "g06-terminal",
                                    "kind": "linux.terminal",
                                    "host": "vps",
                                    "label": "G06 Original-Terminal",
                                    "source": "g06-test-agent",
                                    "availability": "available",
                                    "capture_method": "read-only-test-inventory",
                                    "identity": "g06-service:/Sessions/1:pid=123",
                                }
                            ],
                        },
                        message_id="g06-wine-inventory",
                    )
                    inventory_forwarded = await agent.receive()
                    if inventory_forwarded.get("status") != "forwarded":
                        raise AssertionError(f"inventory_not_forwarded:{inventory_forwarded}")
                    inventory_received = await agent.receive()
                    if inventory_received.get("status") != "received":
                        raise AssertionError(f"inventory_not_received:{inventory_received}")

                    await agent.publish(
                        "say",
                        {"text": "G06 packaged first contact"},
                        message_id="g06-wine-say",
                    )
                    forwarded = await agent.receive()
                    if forwarded.get("status") != "forwarded":
                        raise AssertionError(f"unexpected_forward_status:{forwarded}")

                    for _ in range(100):
                        rows = journal.db.execute(
                            "SELECT session_id, kind, message_id, status FROM events ORDER BY sequence"
                        ).fetchall()
                        if any(
                            row[0] == "agent"
                            and row[1] == "message.received"
                            and row[2] == "g06-wine-say"
                            and row[3] == "received"
                            for row in rows
                        ):
                            break
                        await asyncio.sleep(0.05)
                    else:
                        rows = journal.db.execute(
                            "SELECT session_id, kind, message_id, status FROM events ORDER BY sequence"
                        ).fetchall()
                        process_output = process_log.read_text(errors="replace")[-4000:]
                        raise RuntimeError(
                            f"packaged_exe_receipt_timeout rows={rows!r} output={process_output!r}"
                        )

                    window_tree = _window_tree()
                    if WINDOW_MARKER not in window_tree:
                        raise AssertionError("visible_message_title_not_observed")
                    match = re.search(r'0x[0-9a-f]+ "([^"]*say-received[^"]*)"', window_tree)
                    print(
                        {
                            "status": "PASS",
                            "scope": "packaged Windows EXE under Wine; local relay; visible title readback",
                            "exe": str(EXE),
                            "window": match.group(1) if match else "marker-observed",
                            "native_windows": "UNKNOWN",
                        }
                    )
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
            if process_log_handle is not None:
                process_log_handle.close()
            journal.close()


if __name__ == "__main__":
    asyncio.run(run())
