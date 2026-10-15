"""Terminal- und Raute-Nachrichten des Relays: echte Loopback-Sockets, temporäres SQLite-Journal, keine Plattform-Eingabe."""
import asyncio
import base64
import json
import tempfile
import unittest
from pathlib import Path

from websockets.asyncio.client import connect

from augen_haende_bridge.transport import Journal, Principal, Relay, MAX_TERMINAL_CHUNK, MAX_TERMINAL_INPUT

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aE1sAAAAASUVORK5CYII="


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


class TerminalTransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.journal = Journal(Path(self.temp.name) / "journal.sqlite")
        self.principals = [
            Principal("desktop", "d" * 40, "agent", "target", can_publish_frames=True, can_control_terminals=True),
            Principal("agent", "a" * 40, "desktop", "target", can_serve_terminals=True),
        ]
        self.relay = Relay(self.principals, self.journal, auth_timeout=.15, receipt_ttl=.5)
        self.server = await self.relay.listen()
        self.url = f"ws://127.0.0.1:{self.server.sockets[0].getsockname()[1]}"
        self.clients = []

    async def asyncTearDown(self):
        for ws in self.clients:
            await ws.close()
        self.server.close()
        await self.server.wait_closed()
        self.journal.close()
        self.temp.cleanup()

    async def recv(self, ws, timeout=2):
        return json.loads(await asyncio.wait_for(ws.recv(), timeout))

    async def login(self, name):
        ws = await connect(self.url)
        self.clients.append(ws)
        await ws.send(json.dumps({"v": 1, "kind": "hello", "token": ("d" if name == "desktop" else "a") * 40}))
        return ws, await self.recv(ws)

    def message(self, welcome, kind, payload, *, message_id):
        return json.dumps({"v": 1, "kind": kind, "epoch": welcome["epoch"], "id": message_id,
                           "recipient": welcome["peer_id"], "target_id": "target", "payload": payload})

    async def assert_rejected(self, ws, welcome, kind, payload, reason, message_id="bad"):
        await ws.send(self.message(welcome, kind, payload, message_id=message_id))
        answer = await self.recv(ws)
        self.assertEqual((answer["kind"], answer["reason"]), ("error", reason), (kind, payload))

    async def test_capabilities_are_granted_per_principal(self):
        _, dw = await self.login("desktop")
        _, aw = await self.login("agent")
        self.assertIn("terminal_control", dw["capabilities"])
        self.assertNotIn("terminal_serve", dw["capabilities"])
        self.assertIn("terminal_serve", aw["capabilities"])
        self.assertNotIn("terminal_control", aw["capabilities"])

    async def test_start_and_state_are_reliable_with_receipts(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await d.send(self.message(dw, "terminal_start", {"start_id": "claude-vd1", "rows": 30, "cols": 100}, message_id="s1"))
        event = await self.recv(a)
        self.assertEqual(event["event_kind"], "terminal_start")
        self.assertEqual(event["payload"], {"start_id": "claude-vd1", "rows": 30, "cols": 100})
        self.assertIn("delivery_id", event)
        self.assertEqual((await self.recv(d))["status"], "forwarded")
        await a.send(json.dumps({"v": 1, "kind": "receipt", "epoch": aw["epoch"], "delivery_id": event["delivery_id"]}))
        self.assertEqual((await self.recv(a))["kind"], "receipt_recorded")
        self.assertEqual((await self.recv(d))["status"], "received")
        state = {"terminal_id": "t1", "start_id": "claude-vd1", "name": "Claude", "state": "running",
                 "exit_code": None, "reason": ""}
        await a.send(self.message(aw, "terminal_state", state, message_id="st1"))
        got = await self.recv(d)
        self.assertEqual(got["event_kind"], "terminal_state")
        self.assertEqual(got["payload"], state)

    async def test_terminal_list_request_and_list(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await d.send(self.message(dw, "terminal_list_request", {}, message_id="l1"))
        self.assertEqual((await self.recv(a))["event_kind"], "terminal_list_request")
        await self.recv(d)
        listing = {"request_id": "l1",
                   "starts": [{"start_id": "haiku-host", "name": "Haiku", "ort": "Host",
                               "ordner": "/home/claude_haiku", "programm": "claude"}],
                   "terminals": [{"terminal_id": "t1", "start_id": "haiku-host", "name": "Haiku",
                                  "state": "running", "rows": 30, "cols": 100}]}
        await a.send(self.message(aw, "terminal_list", listing, message_id="l1r"))
        self.assertEqual((await self.recv(d))["payload"], listing)

    async def test_list_may_carry_the_session_identity(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        listing = {"request_id": "l2", "starts": [],
                   "terminals": [{"terminal_id": "t1", "start_id": "haiku-host", "name": "Haiku", "state": "running",
                                  "rows": 30, "cols": 100, "pid": 4711, "gestartet": 1790000000}]}
        await a.send(self.message(aw, "terminal_list", listing, message_id="l2r"))
        self.assertEqual((await self.recv(d))["payload"], listing)

    async def test_attach_is_a_live_request_and_replay_output_carries_the_flag(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await d.send(self.message(dw, "terminal_attach", {"terminal_id": "t1"}, message_id="at-1"))
        got = await self.recv(a)
        self.assertEqual((got["event_kind"], got["payload"]), ("terminal_attach", {"terminal_id": "t1"}))
        self.assertNotIn("delivery_id", got)  # kein Journal, keine Quittung: nach einem Wiederverbinden wird nichts alt wiederholt
        await a.send(self.message(aw, "terminal_output", {"terminal_id": "t1", "seq": 5, "data": b64(b"alt"), "replay": True}, message_id="o-5"))
        event = await self.recv(d)
        self.assertTrue(event["payload"]["replay"])

    async def test_output_and_input_are_live_streams_without_journal_or_receipt(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        secret = b"geheime-tastatureingabe"
        await a.send(self.message(aw, "terminal_output", {"terminal_id": "t1", "seq": 0, "data": b64(b"\x1b[31mrot\x1b[0m")}, message_id="o-0"))
        event = await self.recv(d)
        self.assertEqual(event["event_kind"], "terminal_output")
        self.assertNotIn("delivery_id", event)
        self.assertEqual(base64.b64decode(event["payload"]["data"]), b"\x1b[31mrot\x1b[0m")
        await d.send(self.message(dw, "terminal_input", {"terminal_id": "t1", "data": b64(secret)}, message_id="i-0"))
        got = await self.recv(a)
        self.assertEqual(got["event_kind"], "terminal_input")
        self.assertNotIn("delivery_id", got)
        await d.send(self.message(dw, "terminal_resize", {"terminal_id": "t1", "rows": 40, "cols": 120}, message_id="r-0"))
        self.assertEqual((await self.recv(a))["event_kind"], "terminal_resize")
        # Der Absender bekommt für Stromnachrichten kein Ergebnis.
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(a.recv(), .1)
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(d.recv(), .1)
        self.assertEqual(self.relay.pending, {})
        rows = str(self.journal.db.execute("SELECT * FROM events").fetchall()) + \
            str(self.journal.db.execute("SELECT * FROM messages").fetchall())
        self.assertNotIn(b64(secret), rows)
        self.assertNotIn("geheime", rows)
        self.assertNotIn("o-0", rows)
        self.assertNotIn("i-0", rows)

    async def test_stream_to_offline_peer_is_dropped_silently(self):
        a, aw = await self.login("agent")
        await a.send(self.message(aw, "terminal_output", {"terminal_id": "t1", "seq": 1, "data": b64(b"x")}, message_id="o-1"))
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(a.recv(), .1)

    async def test_raute_say_is_reliable_and_bound_to_a_terminal(self):
        d, _ = await self.login("desktop")
        a, aw = await self.login("agent")
        await a.send(self.message(aw, "raute_say", {"terminal_id": "t1", "text": "Hast du deinen Turm ungedeckt gelassen?"}, message_id="say1"))
        event = await self.recv(d)
        self.assertEqual(event["event_kind"], "raute_say")
        self.assertEqual(event["payload"]["terminal_id"], "t1")
        self.assertIn("delivery_id", event)
        self.assertEqual((await self.recv(a))["status"], "forwarded")

    async def test_raute_tippen_is_reliable_bounded_and_only_from_the_launcher(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await a.send(self.message(aw, "raute_tippen", {"terminal_id": "t1", "text": "Ich sehe den Turm"}, message_id="tip1"))
        event = await self.recv(d)
        self.assertEqual((event["event_kind"], event["payload"]["text"]), ("raute_tippen", "Ich sehe den Turm"))
        self.assertEqual((await self.recv(a))["status"], "forwarded")
        await self.assert_rejected(d, dw, "raute_tippen", {"terminal_id": "t1", "text": "x"}, "unsupported_capability")
        for payload in ({"terminal_id": "t1", "text": ""}, {"terminal_id": "t1", "text": "x" * 501},
                        {"terminal_id": "t1", "text": "x", "extra": 1}, {"terminal_id": "../x", "text": "x"}):
            await self.assert_rejected(a, aw, "raute_tippen", payload,
                                       "invalid_raute_tippen" if "extra" in payload else
                                       ("invalid_identifier" if payload["terminal_id"] == "../x" else "invalid_text"))

    async def test_terminal_audio_is_a_lossy_stream_from_the_desktop_only(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        wav = b"RIFF" + b"\x00" * 2000
        await d.send(self.message(dw, "terminal_audio", {"terminal_id": "t1", "mime": "audio/wav", "data": b64(wav), "dauer_ms": 60},
                                  message_id="au-1"))
        event = await self.recv(a)
        self.assertEqual(event["event_kind"], "terminal_audio")
        self.assertEqual(event["payload"]["dauer_ms"], 60)
        with self.assertRaises(asyncio.TimeoutError):  # Live-Strom: keine Quittung
            await asyncio.wait_for(d.recv(), .1)
        await self.assert_rejected(a, aw, "terminal_audio", {"terminal_id": "t1", "mime": "audio/wav", "data": b64(wav),
                                                             "dauer_ms": 60}, "unsupported_capability")

    async def test_terminal_audio_shapes_are_strict(self):
        d, dw = await self.login("desktop")
        ok = {"terminal_id": "t1", "mime": "audio/wav", "data": b64(b"RIFF" + b"\x00" * 100), "dauer_ms": 500}
        for aendern, grund in (({"mime": "audio/mpeg"}, "invalid_terminal_audio"), ({"dauer_ms": 0}, "invalid_terminal_audio"),
                               ({"dauer_ms": 999999}, "invalid_terminal_audio"), ({"data": b64(b"NOPE" + b"\x00" * 50)}, "invalid_audio_signature"),
                               ({"data": "***"}, "invalid_base64"), ({"data": b64(b"RIFF" + b"\x00" * 1_000_000)}, "invalid_terminal_audio"),
                               ({"terminal_id": "../x"}, "invalid_identifier"), ({"extra": 1}, "invalid_terminal_audio")):
            await self.assert_rejected(d, dw, "terminal_audio", {**ok, **aendern}, grund)

    async def test_sprache_text_comes_only_from_the_launcher(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await a.send(self.message(aw, "sprache_text", {"terminal_id": "t1", "text": "Schau mal links", "dauer_ms": 1200, "modell": "medium"},
                                  message_id="sp-1"))
        event = await self.recv(d)
        self.assertEqual((event["event_kind"], event["payload"]["text"]), ("sprache_text", "Schau mal links"))
        self.assertEqual((await self.recv(a))["status"], "forwarded")
        await self.assert_rejected(d, dw, "sprache_text", {"terminal_id": "t1", "text": "x", "dauer_ms": 1, "modell": "m"},
                                   "unsupported_capability")
        for payload, grund in (({"terminal_id": "t1", "text": "", "dauer_ms": 1, "modell": "m"}, "invalid_text"),
                               ({"terminal_id": "t1", "text": "x" * 4001, "dauer_ms": 1, "modell": "m"}, "invalid_text"),
                               ({"terminal_id": "t1", "text": "x", "dauer_ms": -1, "modell": "m"}, "invalid_sprache_text"),
                               ({"terminal_id": "t1", "text": "x", "dauer_ms": 1}, "invalid_sprache_text")):
            await self.assert_rejected(a, aw, "sprache_text", payload, grund)

    async def test_wrong_principal_cannot_use_terminal_kinds(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await self.assert_rejected(a, aw, "terminal_start", {"start_id": "x", "rows": 1, "cols": 1}, "unsupported_capability")
        await self.assert_rejected(a, aw, "terminal_input", {"terminal_id": "t1", "data": b64(b"x")}, "unsupported_capability")
        await self.assert_rejected(d, dw, "terminal_output", {"terminal_id": "t1", "seq": 0, "data": b64(b"x")}, "unsupported_capability")
        await self.assert_rejected(d, dw, "raute_say", {"terminal_id": "t1", "text": "x"}, "unsupported_capability")
        await self.assert_rejected(d, dw, "terminal_state", {"terminal_id": "t1", "start_id": "s", "name": "n",
                                                            "state": "running", "exit_code": None, "reason": ""}, "unsupported_capability")

    async def test_shapes_sizes_and_identifiers_are_strict(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        ok_out = {"terminal_id": "t1", "seq": 0, "data": b64(b"x")}
        cases = [
            (d, dw, "terminal_start", {"start_id": "s", "rows": 0, "cols": 10}, "invalid_terminal_size"),
            (d, dw, "terminal_start", {"start_id": "s", "rows": 10, "cols": 1001}, "invalid_terminal_size"),
            (d, dw, "terminal_start", {"start_id": "s", "rows": True, "cols": 10}, "invalid_terminal_size"),
            (d, dw, "terminal_start", {"start_id": "bad id", "rows": 10, "cols": 10}, "invalid_identifier"),
            (d, dw, "terminal_start", {"start_id": "s", "rows": 10, "cols": 10, "cmd": "rm -rf /"}, "invalid_terminal_start"),
            (d, dw, "terminal_input", {"terminal_id": "t1", "data": "***"}, "invalid_base64"),
            (d, dw, "terminal_input", {"terminal_id": "t1", "data": ""}, "invalid_terminal_input"),
            (d, dw, "terminal_input", {"terminal_id": "t1", "data": b64(b"x" * (MAX_TERMINAL_INPUT + 1))}, "invalid_terminal_input"),
            (d, dw, "terminal_input", {"terminal_id": "../x", "data": b64(b"x")}, "invalid_identifier"),
            (d, dw, "terminal_resize", {"terminal_id": "t1", "rows": 5}, "invalid_terminal_resize"),
            (d, dw, "terminal_close", {"terminal_id": "t1", "force": True}, "invalid_terminal_close"),
            (d, dw, "terminal_list_request", {"scope": "all"}, "invalid_terminal_list_request"),
            (a, aw, "terminal_output", {**ok_out, "seq": -1}, "invalid_terminal_sequence"),
            (a, aw, "terminal_output", {**ok_out, "data": b64(b"x" * (MAX_TERMINAL_CHUNK + 1))}, "invalid_terminal_output"),
            (a, aw, "terminal_output", {**ok_out, "extra": 1}, "invalid_terminal_output"),
            (a, aw, "terminal_output", {**ok_out, "replay": False}, "invalid_terminal_output"),
            (a, aw, "terminal_output", {**ok_out, "replay": 1}, "invalid_terminal_output"),
            (d, dw, "terminal_attach", {"terminal_id": "t1", "alles": True}, "invalid_terminal_attach"),
            (d, dw, "terminal_attach", {}, "invalid_terminal_attach"),
            (d, dw, "terminal_attach", {"terminal_id": "../x"}, "invalid_identifier"),
            (a, aw, "terminal_list", {"request_id": "r", "starts": [], "terminals": [{"terminal_id": "t1", "start_id": "s", "name": "n",
                                      "state": "running", "rows": 5, "cols": 5, "pid": -3, "gestartet": 1}]}, "invalid_terminal_list"),
            (a, aw, "raute_say", {"terminal_id": "t1", "text": ""}, "invalid_text"),
            (a, aw, "raute_say", {"terminal_id": "t1", "text": "x" * 8001}, "invalid_text"),
            (a, aw, "terminal_state", {"terminal_id": "t1", "start_id": "s", "name": "n", "state": "zombie",
                                       "exit_code": None, "reason": ""}, "invalid_terminal_state"),
            (a, aw, "terminal_state", {"terminal_id": "t1", "start_id": "s", "name": "n", "state": "exited",
                                       "exit_code": "0", "reason": ""}, "invalid_terminal_state"),
            (a, aw, "terminal_list", {"request_id": "r", "starts": [{"start_id": "s"}], "terminals": []}, "invalid_terminal_list"),
            (a, aw, "terminal_list", {"request_id": "r", "terminals": []}, "invalid_terminal_list"),
        ]
        for ws, welcome, kind, payload, reason in cases:
            await self.assert_rejected(ws, welcome, kind, payload, reason)
        two_starts = [{"start_id": "s", "name": "n", "ort": "vd1", "ordner": "/x", "programm": "p"}] * 2
        await self.assert_rejected(a, aw, "terminal_list", {"request_id": "r", "starts": two_starts, "terminals": []}, "duplicate_start_id")

    async def test_frame_may_name_its_terminal_but_only_with_a_valid_identifier(self):
        d, dw = await self.login("desktop")
        a, _ = await self.login("agent")
        frame = {"mime": "image/png", "data": PNG, "source": "capture", "captured_at_ms": 1, "width": 1, "height": 1}
        await d.send(self.message(dw, "frame", {**frame, "terminal_id": "t1"}, message_id="f1"))
        event = await self.recv(a)
        self.assertEqual(event["payload"]["terminal_id"], "t1")
        await self.recv(d)
        await self.assert_rejected(d, dw, "frame", {**frame, "terminal_id": "bad id"}, "invalid_identifier")
        await self.assert_rejected(d, dw, "frame", {**frame, "other": 1}, "invalid_frame")


if __name__ == "__main__":
    unittest.main()
