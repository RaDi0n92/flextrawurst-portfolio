"""Thread boundary between a native GUI and the async bridge transport.

The GUI must never run an asyncio loop in its Tk event thread. This wrapper is
also deliberately opt-in: constructing it does not connect anywhere.
"""

from __future__ import annotations

import asyncio
import threading
import uuid
from collections.abc import Callable

from .transport_client import BridgeClient


EventCallback = Callable[[dict[str, object]], None]
InventoryProvider = Callable[[], dict[str, object]]


class BridgeRuntime:
    """Own one explicitly configured BridgeClient on a private event loop."""

    def __init__(
        self,
        url: str,
        token: str,
        *,
        on_event: EventCallback | None = None,
        inventory_provider: InventoryProvider | None = None,
        receive_timeout: float = 60.0,
    ) -> None:
        self.url = url
        self.token = token
        self.on_event = on_event or (lambda _event: None)
        self.inventory_provider = inventory_provider
        self.receive_timeout = receive_timeout
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._client: BridgeClient | None = None
        self._connected = threading.Event()
        self._stopped = threading.Event()
        self._failure: BaseException | None = None

    @property
    def connected(self) -> bool:
        return self._connected.is_set()

    @property
    def failure(self) -> BaseException | None:
        return self._failure

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("bridge_runtime_already_started")
        self._thread = threading.Thread(target=self._run, name="bridge-transport", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connect_and_receive())
        except BaseException as exc:  # report to host; never crash the GUI thread
            self._failure = exc
            try:
                self.on_event({"kind": "runtime.failed", "reason": repr(exc)[:400]})
            except Exception:
                pass
        finally:
            self._stopped.set()
            self._connected.clear()
            self._loop.close()

    async def _connect_and_receive(self) -> None:
        async with BridgeClient(self.url, self.token) as client:
            self._client = client
            self._connected.set()
            self.on_event({"kind": "runtime.connected", "welcome": client.welcome or {}})
            while True:
                try:
                    event = await client.receive(timeout=self.receive_timeout)
                except asyncio.TimeoutError:
                    # WebSocket ping/pong keeps the connection alive, while
                    # application silence is a normal state for the overlay.
                    continue
                if event.get("kind") != "event":
                    self.on_event(event)
                    continue
                self.on_event(event)
                # Stromereignisse (Terminalbytes) tragen keine delivery_id und werden nicht quittiert.
                if event.get("delivery_id") is not None:
                    await client.confirm_received(event)
                if (
                    event.get("event_kind") == "target_inventory_request"
                    and self.inventory_provider is not None
                ):
                    try:
                        inventory = self.inventory_provider()
                        payload = {
                            "request_id": event["id"],
                            **inventory,
                        }
                    except Exception as exc:  # provider failure stays an explicit status
                        self.on_event({
                            "kind": "runtime.inventory_provider_failed",
                            "reason": repr(exc)[:400],
                        })
                        payload = {
                            "request_id": event.get("id", "unknown"),
                            "status": "error",
                            "captured_at_ms": 0,
                            "targets": [],
                            "error": str(exc)[:400],
                        }
                    # The wire validator intentionally does not accept an
                    # arbitrary error field; degrade provider failures to a
                    # valid empty error inventory.
                    payload.pop("error", None)
                    await client.publish(
                        "target_inventory",
                        payload,
                        # Keep the relay's 96-character identifier bound even
                        # if a future caller supplies the maximum event id.
                        message_id=f"inventory-{event['id'][-80:]}",
                    )

    async def _shutdown(self) -> None:
        if self._client is not None and self._client.socket is not None:
            await self._client.socket.close()

    def send_say(self, text: str) -> None:
        if self._loop is None or self._client is None or not self.connected:
            raise RuntimeError("bridge_runtime_not_connected")
        future = asyncio.run_coroutine_threadsafe(self._client.publish("say", {"text": text}), self._loop)
        future.result(timeout=5.0)

    def publish(self, kind: str, payload: dict[str, object], *, message_id: str | None = None) -> str:
        """Send one envelope to the paired peer; queued on the socket, not a delivery claim."""

        if self._loop is None or self._client is None or not self.connected:
            raise RuntimeError("bridge_runtime_not_connected")
        future = asyncio.run_coroutine_threadsafe(
            self._client.publish(kind, payload, message_id=message_id), self._loop
        )
        return future.result(timeout=5.0)

    def request_target_inventory(self) -> str:
        """Ask the paired agent for a read-only terminal inventory."""

        if self._loop is None or self._client is None or not self.connected:
            raise RuntimeError("bridge_runtime_not_connected")
        request_id = uuid.uuid4().hex
        try:
            self.on_event({"kind": "runtime.inventory_requested", "request_id": request_id})
        except Exception:
            pass
        future = asyncio.run_coroutine_threadsafe(
            self._client.publish(
                "target_inventory_request",
                {"scope": "terminals"},
                message_id=request_id,
            ),
            self._loop,
        )
        future.result(timeout=5.0)
        return request_id

    def stop(self) -> None:
        if self._loop is None or self._stopped.is_set():
            return
        future = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
        try:
            future.result(timeout=5.0)
        except (RuntimeError, TimeoutError):
            pass
        if self._thread is not threading.current_thread():
            self._thread.join(timeout=5.0)
