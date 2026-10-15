# ws_manager.py — WebSocket Connection Manager für Gruppen-Chat
from fastapi import WebSocket
import asyncio
from typing import Callable, Dict, Set


class GroupChatManager:
    def __init__(self):
        self.rooms: Dict[int, Set[WebSocket]] = {}
        self.guards: Dict[WebSocket, Callable[[], int | None]] = {}

    async def connect(self, websocket: WebSocket, group_id: int, guard: Callable[[], int | None]):
        await websocket.accept()
        self.guards[websocket] = guard
        if group_id not in self.rooms:
            self.rooms[group_id] = set()
        self.rooms[group_id].add(websocket)

    def disconnect(self, websocket: WebSocket, group_id: int):
        self.guards.pop(websocket, None)
        if group_id in self.rooms:
            self.rooms[group_id].discard(websocket)
            if not self.rooms[group_id]:
                del self.rooms[group_id]

    async def authorize(self, websocket: WebSocket, group_id: int) -> bool:
        if websocket not in self.rooms.get(group_id, set()):
            return False
        guard = self.guards.get(websocket)
        try:
            code = await asyncio.to_thread(guard) if guard else 1011
        except Exception:
            code = 1011
        # Another broadcast or the receive loop may have removed this socket.
        if websocket not in self.rooms.get(group_id, set()):
            return False
        if code is not None:
            self.disconnect(websocket, group_id)
            try:
                await websocket.close(code=code)
            except Exception:
                pass
            return False
        return True

    async def send(self, websocket: WebSocket, group_id: int, message: dict):
        if not await self.authorize(websocket, group_id):
            return
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket, group_id)

    async def broadcast(self, group_id: int, message: dict, exclude: WebSocket = None):
        # Checks await I/O; connections can disappear while broadcasting.
        for ws in tuple(self.rooms.get(group_id, ())):
            if ws is not exclude:
                await self.send(ws, group_id, message)

    def online_count(self, group_id: int) -> int:
        return len(self.rooms.get(group_id, set()))


manager = GroupChatManager()
