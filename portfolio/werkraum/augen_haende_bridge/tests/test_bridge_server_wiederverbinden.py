"""Wiederverbinden (G04): Die Sitzung läuft auf dem Starter weiter, wenn die Bridge (der Desktop) wegbricht. Nach dem Wiederverbinden ist es dieselbe Sitzung
(gleiche ID, gleicher Prozess, gleiche Startzeit), es entsteht keine neue Shell, die Ausgabe wird wieder eingespielt und Eingaben kommen genau einmal an.
Läuft gegen den echten Server-Prozess (Relay + Starter), der Desktop ist ein echter Client."""
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
from test_terminal_eingabe_paritaet import EMPFAENGER

ROOT = Path(__file__).resolve().parents[1]
READY_PORT = re.compile(r"127\.0\.0\.1:(\d+)")


class WiederverbindenTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix="bw-", dir="/tmp"))
        self.addCleanup(shutil.rmtree, self.temp, True)
        skript = self.temp / "empfaenger.py"
        skript.write_text(EMPFAENGER, encoding="utf-8")
        (self.temp / "starts.json").write_text(json.dumps({"starts": [
            {"start_id": "empf", "name": "Empfaenger", "ort": "Host", "ordner": "/tmp", "programm": f"python3 -u {skript}"}]}))
        (self.temp / "orte.json").write_text(json.dumps({"orte": {"Host": {"kind": "host"}}}))
        self.desktop_token = secrets.token_urlsafe(32)
        env = {**os.environ, "BRIDGE_DESKTOP_TOKEN": self.desktop_token, "BRIDGE_AGENT_TOKEN": secrets.token_urlsafe(32),
               "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), str(ROOT)]), "BRIDGE_SPRACHERKENNUNG": "aus"}
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, str(ROOT / "client_vps" / "bridge_server.py"), "--port", "0", "--journal", str(self.temp / "relay.sqlite3"),
            "--starts", str(self.temp / "starts.json"), "--orte", str(self.temp / "orte.json"), "--runtime-dir", str(self.temp / "run"),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env)
        ready = (await asyncio.wait_for(self.process.stdout.readline(), 20)).decode()
        self.url = f"ws://127.0.0.1:{READY_PORT.search(ready).group(1)}"

    async def asyncTearDown(self):
        self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), 10)
        except asyncio.TimeoutError:
            self.process.kill()

    @staticmethod
    async def naechstes(desktop, art, timeout=10):
        while True:
            event = await desktop.receive(timeout=timeout)
            if event.get("kind") != "event":
                continue
            if event.get("delivery_id") is not None:
                await desktop.confirm_received(event)
            if event["event_kind"] == art:
                return event["payload"]

    async def sammeln(self, desktop, bis, timeout=10):
        """Ausgabe sammeln, bis `bis` in ihr vorkommt; liefert (Text, Stücke)."""
        stuecke, text = [], b""
        while bis not in text:
            stueck = await self.naechstes(desktop, "terminal_output", timeout)
            stuecke.append(stueck)
            text += base64.b64decode(stueck["data"])
        return text, stuecke

    async def test_dieselbe_sitzung_nach_dem_wiederverbinden_ohne_neue_shell_und_ohne_doppelte_eingabe(self):
        async with BridgeClient(self.url, self.desktop_token) as erster:
            await erster.publish("terminal_start", {"start_id": "empf", "rows": 30, "cols": 100})
            zustand = await self.naechstes(erster, "terminal_state")
            while zustand["state"] != "running":
                zustand = await self.naechstes(erster, "terminal_state")
            tid = zustand["terminal_id"]
            await self.sammeln(erster, b"BEREIT")
            await erster.publish("terminal_list_request", {})
            vorher = (await self.naechstes(erster, "terminal_list"))["terminals"]
            self.assertEqual([t["terminal_id"] for t in vorher], [tid])
            await erster.publish("terminal_input", {"terminal_id": tid, "data": base64.b64encode(b"AAA").decode()})
            await self.sammeln(erster, b"HEX 414141")
        # Der Desktop ist weg (Bridge geschlossen, Tunnel getrennt). Die Sitzung läuft auf dem Starter weiter.
        await asyncio.sleep(0.5)
        async with BridgeClient(self.url, self.desktop_token) as zweiter:
            await zweiter.publish("terminal_list_request", {})
            nachher = (await self.naechstes(zweiter, "terminal_list"))["terminals"]
            self.assertEqual(len(nachher), 1)  # keine zweite Shell
            self.assertEqual((nachher[0]["terminal_id"], nachher[0]["pid"], nachher[0]["gestartet"]),
                             (tid, vorher[0]["pid"], vorher[0]["gestartet"]))  # derselbe Prozess, dieselbe Startzeit
            await zweiter.publish("terminal_attach", {"terminal_id": tid})
            text, stuecke = await self.sammeln(zweiter, b"HEX 414141")
            self.assertTrue(stuecke[0].get("replay"))  # die Bridge weiß: Bildschirm neu aufbauen
            self.assertIn(b"BEREIT", text)  # die Ausgabe seit dem Start ist wieder da
            self.assertEqual(text.count(b"HEX 414141"), 1)  # die alte Eingabe wird als Ausgabe gezeigt, aber nicht noch einmal gesendet
            await zweiter.publish("terminal_input", {"terminal_id": tid, "data": base64.b64encode(b"B").decode()})
            neu, _ = await self.sammeln(zweiter, b"HEX 42")
            self.assertEqual(neu.count(b"HEX 42"), 1)
            self.assertNotIn(b"HEX 4141", neu)  # AAA kam nicht noch einmal beim Programm an
            await asyncio.sleep(0.5)
            await zweiter.publish("terminal_list_request", {})
            ende = (await self.naechstes(zweiter, "terminal_list"))["terminals"]
            self.assertEqual([t["pid"] for t in ende], [vorher[0]["pid"]])


if __name__ == "__main__":
    unittest.main()
