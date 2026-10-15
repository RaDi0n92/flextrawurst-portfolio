"""Die Anwendung des ersten Körpers gegen den echten VPS-Weg: Relay, Starter mit echter PTY, Sprech-Socket.

Nur die Fenster sind ersetzt (unter Linux gibt es keine); alles dazwischen ist der Produktionscode:
`transport.Relay`, `bridge_runtime.BridgeRuntime` auf beiden Seiten, `client_vps.terminal_launcher.Launcher`,
`client_vps.bridge_cli.ask` als Agentenwerkzeug. Der Starteintrag ist ein harmloses `cat` in einer echten PTY.
"""

from __future__ import annotations

import asyncio
import base64
import json
import queue
import secrets
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from augen_haende_bridge.koerper.anwendung import KoerperAnwendung
from augen_haende_bridge.transport import Journal, Relay
from client_vps.bridge_cli import ask
from client_vps.bridge_server import build_principals
from client_vps.terminal_launcher import Launcher, load_orte, load_starts


class WarteschlangenGui:
    """Wie der echte GUI-Thread: post legt ab, abgearbeitet wird nur im Test-Hauptfaden."""

    def __init__(self):
        self.schlange: queue.Queue = queue.Queue()
        self.hotkeys = []

    def post(self, aufgabe):
        self.schlange.put(aufgabe)

    def hotkey(self, modifikatoren, vk, aufruf):
        self.hotkeys.append(vk)
        return True

    def beenden(self, code=0):
        pass

    def pumpen_bis(self, bedingung, sekunden=10.0):
        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            try:
                self.schlange.get(timeout=0.05)()
            except queue.Empty:
                pass
            if bedingung():
                return True
        return False


def _koerper_bauen():
    gebaut = []

    def bauen(**kwargs):
        koerper = Mock()
        koerper.kwargs = kwargs
        koerper.ausgabe = bytearray()
        koerper.terminal.ausgabe.side_effect = koerper.ausgabe.extend
        koerper.terminal.text_aller_zeilen.return_value = []
        koerper.raute.status, koerper.raute.letzte_nachricht = "offline", ""
        koerper.terminal.zustand, koerper.terminal.ziel_text = "", ""
        gebaut.append(koerper)
        return koerper
    return bauen, gebaut


class RelayFaden:
    """Relay in einem eigenen Faden mit eigenem Event-Loop, wie `bridge_server.py` es im Hauptfaden tut.
    Journal und Relay entstehen in diesem Faden (SQLite-Verbindungen gehören ihrem Faden)."""

    def __init__(self, principals, journal_pfad: Path):
        self.principals, self.journal_pfad = principals, journal_pfad
        self.port = None
        self._bereit = threading.Event()
        self._stop = None
        self._loop = None
        self._faden = threading.Thread(target=self._lauf, daemon=True)

    def _lauf(self):
        self._loop = asyncio.new_event_loop()
        self._stop = asyncio.Event()
        journal = Journal(self.journal_pfad)

        async def main():
            async with Relay(self.principals, journal).listen(0) as server:
                self.port = server.sockets[0].getsockname()[1]
                self._bereit.set()
                await self._stop.wait()
        try:
            self._loop.run_until_complete(main())
        finally:
            journal.close()

    def start(self):
        self._faden.start()
        assert self._bereit.wait(5)

    def stop(self):
        self._loop.call_soon_threadsafe(self._stop.set)
        self._faden.join(5)


class EchterRelayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="koerper-relay-")
        root = Path(self.temp.name)
        (root / "starts.json").write_text(json.dumps({"starts": [
            {"start_id": "echo-host", "name": "Echo", "ort": "Host", "ordner": "/tmp", "programm": "cat"}]}))
        (root / "orte.json").write_text(json.dumps({"orte": {"Host": {"kind": "host"}}}))
        orte = load_orte(root / "orte.json")
        starts = load_starts(root / "starts.json", orte)
        desktop_token, agent_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        self.relay_faden = RelayFaden(build_principals(desktop_token=desktop_token, agent_token=agent_token),
                                      root / "relay.sqlite")
        self.relay_faden.start()
        url = f"ws://127.0.0.1:{self.relay_faden.port}"
        self.launcher: Launcher | None = None
        self.agent_runtime = BridgeRuntime(url, agent_token, on_event=lambda e: self.launcher.on_event(e))
        self.runtime_dir = root / "runtime"
        self.launcher = Launcher(self.agent_runtime, starts, orte, self.runtime_dir)
        self.launcher.start()
        self.agent_socket = self.launcher.serve_agents(self.runtime_dir / "agent.sock")
        self.agent_runtime.start()
        deadline = time.monotonic() + 5
        while not self.agent_runtime.connected and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(self.agent_runtime.connected)

        self.gui = WarteschlangenGui()
        bauen, self.gebaut = _koerper_bauen()
        self.app = KoerperAnwendung(url=url, token=desktop_token, gui=self.gui, koerper_bauen=bauen,
                                    arbeitsflaeche=lambda: (0, 0, 1920, 1040))

    def tearDown(self):
        if self.app.runtime is not None:
            self.app.runtime.stop()
        if self.app.sender is not None:
            self.app.sender.stop()
        self.launcher.shutdown()
        self.agent_socket.shutdown()
        self.agent_socket.server_close()
        self.agent_runtime.stop()
        self.relay_faden.stop()
        self.temp.cleanup()

    def test_startliste_start_ein_und_ausgabe_sprechen_und_bild_ueber_den_echten_weg(self):
        app, gui = self.app, self.gui
        app.starten()
        self.assertTrue(gui.pumpen_bis(lambda: "echo-host" in app.startliste), app.bericht())
        self.assertEqual(app.status, "verbunden")

        # Start aus der Startliste: der Desktop schickt nur die start_id.
        self.assertTrue(app.agent_starten("echo-host"))
        self.assertTrue(gui.pumpen_bis(lambda: any(a.zustand == "running" for a in app.agenten.values())), app.bericht())
        agent = next(iter(app.agenten.values()))
        koerper = self.gebaut[0]
        self.assertEqual(koerper.kwargs["name"], "Echo")
        self.assertEqual(koerper.kwargs["ort"], "Host")

        # Eingabe durch die echte PTY: cat gibt sie zurück, die Ausgabe kommt als Strom ans Terminal.
        marker = f"koerper-{secrets.token_hex(4)}"
        koerper.kwargs["terminal_senden"]((marker + "\n").encode())
        self.assertTrue(gui.pumpen_bis(lambda: koerper.ausgabe.count(marker.encode()) >= 2), bytes(koerper.ausgabe))

        # Der Agent spricht über sein Werkzeug (Sprech-Socket) — die Raute seines Körpers bekommt es.
        session = self.launcher.sessions[agent.terminal_id]
        antwort = ask({"cmd": "say", "text": "Shader kompiliert!"},
                      env={"BRIDGE_TERMINAL_ID": agent.terminal_id, "BRIDGE_TERMINAL_TOKEN": session.token,
                           "BRIDGE_RUNTIME_DIR": str(self.runtime_dir)})
        self.assertEqual(antwort, {"ok": True})
        self.assertTrue(gui.pumpen_bis(lambda: koerper.raute.sagen.called))
        koerper.raute.sagen.assert_called_with("Shader kompiliert!")

        # Größenänderung kommt in der PTY an.
        koerper.kwargs["terminal_groesse"](40, 120)
        self.assertTrue(gui.pumpen_bis(lambda: (session.rows, session.cols) == (40, 120)))

        # Das gebundene Bild geht an genau diesen Agenten; er sieht es über sein Werkzeug.
        bindung = Mock()
        bindung.frame.width, bindung.frame.height, bindung.frame.captured_at_ms = 64, 32, int(time.time() * 1000)
        bindung.frame.bgra_bytes = bytes([0, 128, 255, 255]) * (64 * 32)
        bindung.snapshot.items = [Mock(rect=(0, 0, 64, 32))]
        bindung.item.rect = (8, 8, 40, 24)
        koerper.kwargs["ziel_gebunden"](bindung)
        gesehen = {}
        self.assertTrue(gui.pumpen_bis(lambda: gesehen.update(ask({"cmd": "see"}, env={
            "BRIDGE_TERMINAL_ID": agent.terminal_id, "BRIDGE_TERMINAL_TOKEN": session.token,
            "BRIDGE_RUNTIME_DIR": str(self.runtime_dir)})) or gesehen.get("ok")), gesehen)
        self.assertEqual(gesehen["frame"]["mime"], "image/jpeg")
        self.assertEqual((gesehen["frame"]["width"], gesehen["frame"]["height"]), (32, 16))
        self.assertTrue(Path(gesehen["frame"]["path"]).read_bytes().startswith(b"\xff\xd8\xff"))

        # Beenden über das Raute-Menü schließt die Sitzung auf dem VPS und danach den ganzen Körper.
        koerper.kwargs["agent_beenden"]()
        self.assertTrue(gui.pumpen_bis(lambda: agent.zustand == "exited", 12), app.bericht())
        koerper.schliessen.assert_called_once_with()  # gewünschtes Beenden: Raute und Terminal verschwinden
        self.assertNotIn(agent.terminal_id, app.agenten)
        self.assertEqual(agent.luecken, 0)


if __name__ == "__main__":
    unittest.main()
