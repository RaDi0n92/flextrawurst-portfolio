import unittest
import asyncio
import queue
import secrets
import tempfile
from pathlib import Path

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from augen_haende_bridge.transport import Journal, Principal, Relay
from augen_haende_bridge.transport_client import BridgeClient


class BridgeRuntimeTests(unittest.TestCase):
    def test_is_opt_in_and_does_not_connect_on_construction(self):
        runtime = BridgeRuntime("ws://127.0.0.1:9880", "t" * 32)
        self.assertFalse(runtime.connected)
        self.assertIsNone(runtime.failure)
        runtime.stop()

    def test_send_requires_an_explicit_live_connection(self):
        runtime = BridgeRuntime("ws://127.0.0.1:9880", "t" * 32)
        with self.assertRaisesRegex(RuntimeError, "not_connected"):
            runtime.send_say("test")

    def test_runtime_receives_and_confirms_real_relay_event(self):
        asyncio.run(self._integration())

    def test_runtime_requests_and_receives_readonly_inventory(self):
        asyncio.run(self._inventory_integration())

    def test_runtime_treats_application_idle_as_connected(self):
        asyncio.run(self._idle_integration())

    async def _integration(self):
        with tempfile.TemporaryDirectory(prefix="bridge-runtime-") as temp:
            desktop_token = secrets.token_urlsafe(32)
            agent_token = secrets.token_urlsafe(32)
            journal = Journal(Path(temp) / "events.sqlite")
            relay = Relay([
                Principal("desktop", desktop_token, "agent", "integration-target"),
                Principal("agent", agent_token, "desktop", "integration-target"),
            ], journal)
            events: queue.Queue[dict[str, object]] = queue.Queue()
            async with relay.listen() as server:
                port = server.sockets[0].getsockname()[1]
                runtime = BridgeRuntime(
                    f"ws://127.0.0.1:{port}", desktop_token,
                    on_event=events.put,
                )
                runtime.start()
                try:
                    for _ in range(100):
                        if runtime.connected:
                            break
                        await asyncio.sleep(.01)
                    self.assertTrue(runtime.connected, repr(runtime.failure))
                    async with BridgeClient(f"ws://127.0.0.1:{port}", agent_token) as agent:
                        await agent.publish("say", {"text": "runtime-first-contact"}, message_id="integration-say")
                        result = await agent.receive()
                        self.assertEqual(result["status"], "forwarded")
                        incoming = await asyncio.to_thread(events.get, True, 2)
                        while incoming.get("kind") != "event":
                            incoming = await asyncio.to_thread(events.get, True, 2)
                        self.assertEqual(incoming["event_kind"], "say")
                        self.assertEqual(incoming["payload"]["text"], "runtime-first-contact")
                        receipt = await agent.receive()
                        self.assertEqual(receipt["status"], "received")
                finally:
                    await asyncio.to_thread(runtime.stop)
                    self.assertFalse(runtime.connected)
            journal.close()

    async def _inventory_integration(self):
        with tempfile.TemporaryDirectory(prefix="bridge-inventory-") as temp:
            desktop_token = secrets.token_urlsafe(32)
            agent_token = secrets.token_urlsafe(32)
            journal = Journal(Path(temp) / "events.sqlite")
            relay = Relay([
                Principal("desktop", desktop_token, "agent", "inventory-target",
                          can_request_inventory=True),
                Principal("agent", agent_token, "desktop", "inventory-target",
                          can_publish_inventory=True),
            ], journal)
            desktop_events: queue.Queue[dict[str, object]] = queue.Queue()
            agent_events: queue.Queue[dict[str, object]] = queue.Queue()
            async with relay.listen() as server:
                port = server.sockets[0].getsockname()[1]
                desktop = BridgeRuntime(
                    f"ws://127.0.0.1:{port}", desktop_token,
                    on_event=desktop_events.put,
                )
                agent = BridgeRuntime(
                    f"ws://127.0.0.1:{port}", agent_token,
                    on_event=agent_events.put,
                    inventory_provider=lambda: {
                        "status": "ok",
                        "captured_at_ms": 99,
                        "targets": [{
                            "id": "terminal-1", "kind": "linux.terminal", "host": "vps",
                            "label": "Original-Terminal 1", "source": "real",
                            "availability": "available", "capture_method": "konsole-dbus",
                            "identity": "service|session|pid=1",
                        }],
                    },
                )
                desktop.start()
                agent.start()
                try:
                    for _ in range(100):
                        if desktop.connected and agent.connected:
                            break
                        await asyncio.sleep(.01)
                    self.assertTrue(desktop.connected, repr(desktop.failure))
                    self.assertTrue(agent.connected, repr(agent.failure))
                    request_id = await asyncio.to_thread(desktop.request_target_inventory)
                    self.assertTrue(request_id)
                    incoming = await asyncio.to_thread(desktop_events.get, True, 2)
                    while incoming.get("kind") != "event":
                        incoming = await asyncio.to_thread(desktop_events.get, True, 2)
                    self.assertEqual(incoming["event_kind"], "target_inventory")
                    self.assertEqual(incoming["payload"]["request_id"], request_id)
                    self.assertEqual(incoming["payload"]["targets"][0]["id"], "terminal-1")
                    request_event = await asyncio.to_thread(agent_events.get, True, 2)
                    while request_event.get("kind") != "event":
                        request_event = await asyncio.to_thread(agent_events.get, True, 2)
                    self.assertEqual(request_event["event_kind"], "target_inventory_request")
                finally:
                    await asyncio.gather(
                        asyncio.to_thread(desktop.stop),
                        asyncio.to_thread(agent.stop),
                    )
            journal.close()

    async def _idle_integration(self):
        with tempfile.TemporaryDirectory(prefix="bridge-idle-") as temp:
            desktop_token = secrets.token_urlsafe(32)
            agent_token = secrets.token_urlsafe(32)
            journal = Journal(Path(temp) / "events.sqlite")
            relay = Relay([
                Principal("desktop", desktop_token, "agent", "idle-target"),
                Principal("agent", agent_token, "desktop", "idle-target"),
            ], journal)
            async with relay.listen() as server:
                port = server.sockets[0].getsockname()[1]
                runtime = BridgeRuntime(
                    f"ws://127.0.0.1:{port}", desktop_token,
                    receive_timeout=.02,
                )
                runtime.start()
                try:
                    for _ in range(100):
                        if runtime.connected:
                            break
                        await asyncio.sleep(.01)
                    self.assertTrue(runtime.connected, repr(runtime.failure))
                    await asyncio.sleep(.12)
                    self.assertTrue(runtime.connected, repr(runtime.failure))
                finally:
                    await asyncio.to_thread(runtime.stop)
            journal.close()


if __name__ == "__main__":
    unittest.main()
