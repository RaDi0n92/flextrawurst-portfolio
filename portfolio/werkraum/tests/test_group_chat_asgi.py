"""ASGI WebSocket regression using production route/manager and synthetic DB/auth."""
import ast
import asyncio
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None


@unittest.skipIf(TestClient is None, 'run with the host API virtualenv')
class ChatASGI(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('tested_ws_manager', root / 'welt/ws_manager.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.manager = module.GroupChatManager()
        self.active = True
        self.allowed = True

        def verify(token):
            if not self.active: raise ValueError('synthetic revocation')
            return {'user_id': 'synthetic', 'role': 'mensch'}

        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def close(self): pass

        async def short_wait(awaitable, timeout):
            return await asyncio.wait_for(awaitable, timeout=.05)

        source = root / 'welt/groups_api.py'
        node = next(n for n in ast.walk(ast.parse(source.read_text()))
                    if isinstance(n, ast.AsyncFunctionDef) and n.name == 'ws_group_chat')
        node.decorator_list = []
        scope = dict(asyncio=SimpleNamespace(wait_for=short_wait, TimeoutError=asyncio.TimeoutError,
                                            get_running_loop=asyncio.get_running_loop),
                     Optional=Optional, WebSocket=WebSocket, WebSocketDisconnect=WebSocketDisconnect,
                     verify_token=verify, get_conn=Connection,
                     _can_post_group=lambda *args: self.allowed, _chat_manager=self.manager)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
        app = FastAPI()
        app.websocket('/ws/groups/{group_id}/chat')(scope['ws_group_chat'])
        self.client = TestClient(app)

    def test_passive_receiver_loses_group_rights_before_next_message(self):
        with self.client as client:
            with client.websocket_connect('/ws/groups/42/chat?token=synthetic') as ws:
                self.assertEqual(ws.receive_json()['type'], 'presence')
                client.portal.call(self.manager.broadcast, 42, {'type': 'message', 'content': 'allowed'})
                self.assertEqual(ws.receive_json()['content'], 'allowed')
                self.allowed = False
                client.portal.call(self.manager.broadcast, 42, {'type': 'message', 'content': 'secret'})
                with self.assertRaises(WebSocketDisconnect) as caught:
                    ws.receive_json()
                self.assertEqual(caught.exception.code, 4003)

    def test_idle_receiver_is_closed_on_account_revocation(self):
        with self.client as client:
            with client.websocket_connect('/ws/groups/42/chat?token=synthetic') as ws:
                self.assertEqual(ws.receive_json()['type'], 'presence')
                self.active = False
                with self.assertRaises(WebSocketDisconnect) as caught:
                    ws.receive_json()
                self.assertEqual(caught.exception.code, 4001)


if __name__ == '__main__': unittest.main()
