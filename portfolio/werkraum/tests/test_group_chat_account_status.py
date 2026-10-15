import ast
import asyncio
import unittest
from pathlib import Path
from typing import Optional


class Disconnected(Exception):
    pass


class GroupChatAccountStatus(unittest.IsolatedAsyncioTestCase):
    async def run_chat(self, current, message_type="typing"):
        source = Path(__file__).resolve().parents[1] / "welt/groups_api.py"
        node = next(n for n in ast.walk(ast.parse(source.read_text()))
                    if isinstance(n, ast.AsyncFunctionDef) and n.name == "ws_group_chat")
        node.decorator_list = []
        verified = []
        broadcasts = []
        roles = []

        def verify(token):
            verified.append(token)
            if len(verified) == 1:
                return {"user_id": "synthetic", "role": "admin"}
            if isinstance(current, Exception): raise current
            return current

        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def close(self): pass

        class Socket:
            code = None
            received = False
            async def close(self, code): self.code = code
            async def receive_json(self):
                if self.received: raise Disconnected()
                self.received = True
                return {"type": message_type, "content": "synthetic"}

        class Manager:
            disconnected = False
            async def connect(self, *args): pass
            async def authorize(self, *args): return True
            async def broadcast(self, group, data, **kwargs): broadcasts.append(data)
            def disconnect(self, *args): self.disconnected = True
            def online_count(self, *args): return 0

        def can_post(cur, group, uid, role):
            roles.append(role)
            return role == "admin"

        manager = Manager()
        scope = {"asyncio": asyncio, "Optional": Optional, "WebSocket": Socket,
                 "WebSocketDisconnect": Disconnected, "verify_token": verify,
                 "get_conn": Connection, "_can_post_group": can_post, "_chat_manager": manager}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), scope)
        socket = Socket()
        await scope["ws_group_chat"](socket, 123, "synthetic-token")
        self.assertEqual(len(verified), 2)
        self.assertTrue(manager.disconnected)
        return socket.code, broadcasts, roles

    async def test_revoked_or_expired_session_cannot_type_or_write(self):
        for kind in ("typing", "message"):
            with self.subTest(kind=kind):
                code, broadcasts, roles = await self.run_chat(ValueError("revoked"), kind)
                self.assertEqual(code, 4001)
                self.assertTrue(all(b["type"] == "presence" for b in broadcasts))

    async def test_demoted_admin_rechecks_group_permission(self):
        for kind in ("typing", "message"):
            with self.subTest(kind=kind):
                code, broadcasts, roles = await self.run_chat(
                    {"user_id": "synthetic", "role": "mensch"}, kind)
                self.assertEqual(code, 4003)
                self.assertEqual(roles, ["admin", "mensch"])
                self.assertTrue(all(b["type"] == "presence" for b in broadcasts))

    async def test_active_admin_can_still_type(self):
        code, broadcasts, roles = await self.run_chat({"user_id": "synthetic", "role": "admin"})
        self.assertIsNone(code)
        self.assertTrue(any(b["type"] == "typing" for b in broadcasts))


if __name__ == "__main__": unittest.main()
