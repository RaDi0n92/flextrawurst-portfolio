"""Der echte Server-Prozess (Relay + Starter) von außen: Liste, Start, Strom, Eingabe, Sprechen des Agenten, Ende."""
import asyncio
import base64
import json
import os
import re
import secrets
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.transport_client import BridgeClient

ROOT = Path(__file__).resolve().parents[1]
READY_PORT = re.compile(r"127\.0\.0\.1:(\d+)")


class ServerTerminalTests(unittest.IsolatedAsyncioTestCase):
    async def test_server_process_serves_terminals_end_to_end(self):
        temp = Path(tempfile.mkdtemp(prefix="bs-", dir="/tmp"))
        self.addCleanup(shutil.rmtree, temp, True)
        programm = (f"printf 'READY\\n'; read line; printf 'GOT:%s\\n' \"$line\"; "
                    f"python3 {ROOT}/client_vps/bridge_cli.py say 'Turm ungedeckt'; exit 0")
        (temp / "starts.json").write_text(json.dumps({"starts": [
            {"start_id": "echo", "name": "Echo", "ort": "Host", "ordner": "/tmp", "programm": programm}]}))
        (temp / "orte.json").write_text(json.dumps({"orte": {"Host": {"kind": "host"}}}))
        desktop_token, agent_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        env = {**os.environ, "BRIDGE_DESKTOP_TOKEN": desktop_token, "BRIDGE_AGENT_TOKEN": agent_token,
               "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), str(ROOT)]), "BRIDGE_SPRACHERKENNUNG": "aus"}
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(ROOT / "client_vps" / "bridge_server.py"), "--port", "0",
            "--journal", str(temp / "relay.sqlite3"), "--starts", str(temp / "starts.json"),
            "--orte", str(temp / "orte.json"), "--runtime-dir", str(temp / "run"),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        try:
            ready = (await asyncio.wait_for(process.stdout.readline(), 20)).decode()
            self.assertIn("1 start entries", ready)
            url = f"ws://127.0.0.1:{READY_PORT.search(ready).group(1)}"
            async with BridgeClient(url, desktop_token) as desktop:
                async def next_event(kind, timeout=10):
                    while True:
                        event = await desktop.receive(timeout=timeout)
                        if event.get("kind") != "event":
                            continue
                        if event.get("delivery_id") is not None:
                            await desktop.confirm_received(event)
                        if event["event_kind"] == kind:
                            return event["payload"]

                request_id = await desktop.publish("terminal_list_request", {})
                listing = await next_event("terminal_list")
                self.assertEqual(listing["request_id"], request_id)
                self.assertEqual([s["start_id"] for s in listing["starts"]], ["echo"])

                await desktop.publish("terminal_start", {"start_id": "echo", "rows": 30, "cols": 100})
                state = await next_event("terminal_state")
                self.assertEqual(state["state"], "starting")
                state = await next_event("terminal_state")
                self.assertEqual(state["state"], "running")
                terminal_id = state["terminal_id"]

                collected = b""
                while b"READY" not in collected:
                    collected += base64.b64decode((await next_event("terminal_output"))["data"])
                await desktop.publish("terminal_input", {"terminal_id": terminal_id,
                                                         "data": base64.b64encode(b"pong\n").decode()})
                said = await next_event("raute_say")
                self.assertEqual(said, {"terminal_id": terminal_id, "text": "Turm ungedeckt"})
                while True:
                    event = await next_event("terminal_state")
                    if event["state"] == "exited":
                        break
                self.assertEqual(event["exit_code"], 0)
                self.assertEqual(event["terminal_id"], terminal_id)
        finally:
            if process.returncode is None:
                process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=8)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()


if __name__ == "__main__":
    unittest.main()
