"""Small platform-neutral client; receiving does not auto-confirm rendering."""
from __future__ import annotations

import asyncio
import json
import uuid
from urllib.parse import urlsplit

from websockets.asyncio.client import connect

from .transport import MAX_WIRE, decode


class BridgeClient:
    def __init__(self, url: str, token: str):
        address = urlsplit(url)
        if (address.scheme != "ws" or address.hostname != "127.0.0.1" or
                address.username or address.password or address.query or address.fragment or
                address.path not in ("", "/")):
            raise ValueError("local_transport_only")
        self.url, self.token = url, token
        self.socket = None
        self.welcome = None

    async def __aenter__(self):
        if self.socket is not None:
            raise RuntimeError("already_connected")
        self.socket = await connect(self.url, max_size=MAX_WIRE, max_queue=4, compression=None, proxy=None)
        try:
            await self.socket.send(json.dumps({"v": 1, "kind": "hello", "token": self.token}))
            self.welcome = await self.receive()
            if self.welcome.get("kind") != "welcome":
                raise RuntimeError("bridge_authentication_failed")
            return self
        except BaseException:
            await self.socket.close()
            self.socket = None
            self.welcome = None
            raise

    async def __aexit__(self, *_):
        if self.socket is not None:
            await self.socket.close()
        self.socket = None
        self.welcome = None

    async def receive(self, timeout=5.0):
        if self.socket is None:
            raise RuntimeError("not_connected")
        return decode(await asyncio.wait_for(self.socket.recv(), timeout))

    async def publish(self, kind: str, payload: dict, *, message_id: str | None = None):
        if self.welcome is None or self.socket is None:
            raise RuntimeError("not_connected")
        message_id = message_id or uuid.uuid4().hex
        await self.socket.send(json.dumps({
            "v": 1, "kind": kind, "id": message_id, "epoch": self.welcome["epoch"],
            "recipient": self.welcome["peer_id"], "target_id": self.welcome["target_id"],
            "payload": payload,
        }))
        return message_id  # queued to socket, NOT a delivery claim

    async def confirm_received(self, event: dict):
        if self.welcome is None or self.socket is None:
            raise RuntimeError("not_connected")
        if event.get("kind") != "event" or event.get("recipient") != self.welcome["session_id"]:
            raise ValueError("not_our_event")
        await self.socket.send(json.dumps({"v": 1, "kind": "receipt",
            "epoch": self.welcome["epoch"], "delivery_id": event["delivery_id"]}))
