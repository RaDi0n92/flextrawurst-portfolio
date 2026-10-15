"""Actual loopback sockets and a temporary SQLite journal; no platform input."""
import asyncio
import base64
import json
import tempfile
import unittest
from pathlib import Path

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

from augen_haende_bridge.transport import Journal, Principal, Relay, MAX_WIRE

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aE1sAAAAASUVORK5CYII="


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "journal.sqlite"
        self.journal = Journal(self.path)
        self.principals = [Principal("desktop", "d"*40, "agent", "target", True, True, False),
                           Principal("agent", "a"*40, "desktop", "target", False, False, True)]
        self.relay = Relay(self.principals, self.journal, auth_timeout=.15, receipt_ttl=.2)
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

    async def recv(self, ws):
        return json.loads(await asyncio.wait_for(ws.recv(), 2))

    async def login(self, name):
        ws = await connect(self.url)
        self.clients.append(ws)
        await ws.send(json.dumps({"v": 1, "kind": "hello", "token": ("d" if name == "desktop" else "a")*40}))
        return ws, await self.recv(ws)

    def message(self, welcome, *, message_id="m1", kind="say", payload=None):
        return {"v": 1, "kind": kind, "epoch": welcome["epoch"], "id": message_id,
                "recipient": welcome["peer_id"], "target_id": "target",
                "payload": {"text": "private hello"} if payload is None else payload}

    async def test_bidirectional_and_explicit_receipt(self):
        desktop, dw = await self.login("desktop")
        agent, aw = await self.login("agent")
        await desktop.send(json.dumps(self.message(dw)))
        event = await self.recv(agent)
        self.assertEqual(event["sender"], "desktop")
        self.assertEqual((await self.recv(desktop))["status"], "forwarded")
        await agent.send(json.dumps({"v": 1, "kind": "receipt", "epoch": aw["epoch"], "delivery_id": event["delivery_id"]}))
        self.assertEqual((await self.recv(agent))["kind"], "receipt_recorded")
        self.assertEqual((await self.recv(desktop))["status"], "received")
        await agent.send(json.dumps(self.message(aw, message_id="reply")))
        self.assertEqual((await self.recv(desktop))["payload"]["text"], "private hello")
        self.assertEqual((await self.recv(agent))["status"], "forwarded")

    async def test_readonly_target_inventory_request_and_response(self):
        desktop, dw = await self.login("desktop")
        agent, aw = await self.login("agent")
        request = self.message(dw, message_id="inventory-request", kind="target_inventory_request",
                               payload={"scope": "terminals"})
        await desktop.send(json.dumps(request))
        event = await self.recv(agent)
        self.assertEqual(event["event_kind"], "target_inventory_request")
        self.assertEqual(event["payload"], {"scope": "terminals"})
        self.assertEqual((await self.recv(desktop))["status"], "forwarded")
        await agent.send(json.dumps({"v": 1, "kind": "receipt", "epoch": aw["epoch"],
                                     "delivery_id": event["delivery_id"]}))
        self.assertEqual((await self.recv(agent))["kind"], "receipt_recorded")
        self.assertEqual((await self.recv(desktop))["status"], "received")

        inventory = {"request_id": "inventory-request", "status": "ok", "captured_at_ms": 123,
                     "targets": [{"id": "terminal-1", "kind": "linux.terminal", "host": "vps",
                                   "label": "Original-Terminal 1", "source": "real",
                                   "availability": "available", "capture_method": "konsole-dbus",
                                   "identity": "org.kde.konsole-1|/Sessions/1|pid=7"}]}
        await agent.send(json.dumps(self.message(aw, message_id="inventory-response",
                                                  kind="target_inventory", payload=inventory)))
        self.assertEqual((await self.recv(agent))["status"], "forwarded")
        response = await self.recv(desktop)
        self.assertEqual(response["event_kind"], "target_inventory")
        self.assertEqual(response["payload"], inventory)
        await desktop.send(json.dumps({"v": 1, "kind": "receipt", "epoch": dw["epoch"],
                                       "delivery_id": response["delivery_id"]}))
        self.assertEqual((await self.recv(desktop))["kind"], "receipt_recorded")
        self.assertEqual((await self.recv(agent))["status"], "received")

    async def test_unknown_auth_duplicate_session_and_origin(self):
        async with connect(self.url) as ws:
            await ws.send(json.dumps({"v": 1, "kind": "hello", "token": "wrong"}))
            self.assertEqual((await self.recv(ws))["reason"], "authentication_failed")
        await self.login("desktop")
        _, rejected = await self.login("desktop")
        self.assertEqual(rejected["reason"], "session_already_connected")
        with self.assertRaises(InvalidStatus):
            async with connect(self.url, origin="https://untrusted.invalid"):
                pass

    async def test_auth_timeout(self):
        async with connect(self.url) as ws:
            self.assertEqual((await self.recv(ws))["reason"], "timeout")

    async def test_invalid_envelopes_do_not_break_connection(self):
        ws, welcome = await self.login("desktop")
        cases = [("[1]", "unsupported_protocol"), ("{", "invalid_json")]
        for raw, reason in cases:
            await ws.send(raw)
            self.assertEqual((await self.recv(ws))["reason"], reason)
        for field, value, reason in [("recipient", "other", "grant_denied"),
                                      ("target_id", "other", "grant_denied"),
                                      ("epoch", "old", "stale_connection"),
                                      ("kind", "shell", "unsupported_capability")]:
            message = self.message(welcome)
            message[field] = value
            await ws.send(json.dumps(message))
            self.assertEqual((await self.recv(ws))["reason"], reason)
        message = self.message(welcome)
        message["sender"] = "agent"
        await ws.send(json.dumps(message))
        self.assertEqual((await self.recv(ws))["reason"], "invalid_envelope")
        await ws.send(json.dumps(self.message(welcome)))
        self.assertEqual((await self.recv(ws))["status"], "peer_offline")

    async def test_frames_hash_and_grants(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        payload = {"mime": "image/png", "data": PNG, "source": "synthetic", "captured_at_ms": 1, "width": 1, "height": 1}
        await d.send(json.dumps(self.message(dw, kind="frame", payload=payload)))
        event = await self.recv(a)
        import hashlib
        self.assertEqual(event["payload"]["sha256"], hashlib.sha256(base64.b64decode(PNG)).hexdigest())
        self.assertFalse(event["payload"]["metadata_verified"])
        await self.recv(d)
        await a.send(json.dumps(self.message(aw, kind="frame", payload=payload)))
        self.assertEqual((await self.recv(a))["reason"], "unsupported_capability")
        for bad in ({**payload, "data": "bad!"}, {**payload, "data": "eA=="}, {**payload, "width": True}):
            await d.send(json.dumps(self.message(dw, kind="frame", payload=bad)))
            self.assertEqual((await self.recv(d))["kind"], "error")

    async def test_retry_id_conflict_no_redelivery(self):
        d, dw = await self.login("desktop")
        a, _ = await self.login("agent")
        msg = self.message(dw)
        await d.send(json.dumps(msg)); await self.recv(a); await self.recv(d)
        await d.send(json.dumps(msg))
        self.assertTrue((await self.recv(d))["duplicate"])
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(a.recv(), .05)
        msg["payload"]["text"] = "different"
        await d.send(json.dumps(msg))
        self.assertEqual((await self.recv(d))["reason"], "id_conflict")

    async def test_receipt_wrong_session_and_expiration(self):
        d, dw = await self.login("desktop")
        a, aw = await self.login("agent")
        await d.send(json.dumps(self.message(dw)))
        event = await self.recv(a); await self.recv(d)
        receipt = {"v": 1, "kind": "receipt", "epoch": dw["epoch"], "delivery_id": event["delivery_id"]}
        await d.send(json.dumps(receipt))
        self.assertEqual((await self.recv(d))["reason"], "unknown_delivery")
        await asyncio.sleep(.25)
        receipt["epoch"] = aw["epoch"]
        await a.send(json.dumps(receipt))
        self.assertEqual((await self.recv(a))["reason"], "unknown_delivery")

    async def test_reconnect_and_disk_deduplication(self):
        d, dw = await self.login("desktop")
        msg = self.message(dw)
        await d.send(json.dumps(msg))
        self.assertEqual((await self.recv(d))["status"], "peer_offline")
        await d.close()
        self.server.close(); await self.server.wait_closed()
        self.journal.close()
        self.journal = Journal(self.path)
        self.relay = Relay(self.principals, self.journal)
        self.server = await self.relay.listen()
        self.url = f"ws://127.0.0.1:{self.server.sockets[0].getsockname()[1]}"
        d, fresh = await self.login("desktop")
        self.assertEqual(fresh["session_id"], dw["session_id"])
        self.assertNotEqual(fresh["epoch"], dw["epoch"])
        await d.send(json.dumps(msg))
        self.assertEqual((await self.recv(d))["reason"], "stale_connection")
        msg["epoch"] = fresh["epoch"]
        await d.send(json.dumps(msg))
        self.assertTrue((await self.recv(d))["duplicate"])
        rows = str(self.journal.db.execute("SELECT * FROM events").fetchall())
        self.assertNotIn("private hello", rows)
        self.assertNotIn("d"*40, rows)

    async def test_oversized_wire_message(self):
        ws, _ = await self.login("desktop")
        await ws.send("x"*(MAX_WIRE+1))
        with self.assertRaises(ConnectionClosed):
            await ws.recv()


if __name__ == "__main__":
    unittest.main()
