"""Run real manager and route code with synthetic accounts, DB and sockets."""
import ast
import asyncio
import threading
import unittest
from pathlib import Path
from typing import Callable, Dict, Optional, Set
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


class Disconnected(Exception):
    pass


class Socket:
    def __init__(self):
        self.messages = []
        self.closed = asyncio.Event()
        self.code = None

    async def accept(self): pass
    async def close(self, code):
        self.code = code
        self.closed.set()
    async def send_json(self, data): self.messages.append(data)
    async def receive_json(self):
        await self.closed.wait()
        raise Disconnected()


def manager_class():
    source = ROOT / 'welt/ws_manager.py'
    node = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.ClassDef))
    scope = dict(asyncio=asyncio, WebSocket=Socket, Callable=Callable, Dict=Dict, Set=Set)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    return scope['GroupChatManager']


class ReceiveRevocation(unittest.IsolatedAsyncioTestCase):
    async def exercise_route(self, revoke, expected_code, idle=False):
        manager = manager_class()()
        socket = Socket()
        state = {'role': 'admin', 'active': True, 'member': True, 'db': True, 'uid': 'account'}

        def verify(token):
            if not state['active']: raise ValueError('revoked or expired')
            return {'user_id': state['uid'], 'role': state['role']}

        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def close(self): pass

        def can_post(cur, group, uid, role):
            if not state['db']: raise ConnectionError('unavailable')
            return role == 'admin' or state['member']

        async def short_wait(awaitable, timeout):
            self.assertEqual(timeout, 30)
            return await asyncio.wait_for(awaitable, timeout=.02)

        source = ROOT / 'welt/groups_api.py'
        node = next(n for n in ast.walk(ast.parse(source.read_text()))
                    if isinstance(n, ast.AsyncFunctionDef) and n.name == 'ws_group_chat')
        node.decorator_list = []
        scope = dict(asyncio=SimpleNamespace(wait_for=short_wait, TimeoutError=asyncio.TimeoutError),
                     Optional=Optional, WebSocket=Socket, WebSocketDisconnect=Disconnected,
                     verify_token=verify, get_conn=Connection, _can_post_group=can_post,
                     _chat_manager=manager)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
        task = asyncio.create_task(scope['ws_group_chat'](socket, 42, 'synthetic'))
        try:
            async def ready():
                while not socket.messages: await asyncio.sleep(.001)
            await asyncio.wait_for(ready(), 2)
            await manager.broadcast(42, {'type': 'message', 'content': 'allowed'})
            self.assertTrue(any(m.get('content') == 'allowed' for m in socket.messages))
            state.update(revoke)
            if not idle:
                await manager.broadcast(42, {'type': 'message', 'content': 'must not arrive'})
            await asyncio.wait_for(task, 2)
            self.assertEqual(socket.code, expected_code)
            self.assertFalse(any(m.get('content') == 'must not arrive' for m in socket.messages))
            self.assertEqual(manager.online_count(42), 0)
            self.assertFalse(manager.guards)
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    async def test_passive_account_revocation(self):
        await self.exercise_route({'active': False}, 4001)

    async def test_passive_demotion_and_membership_removal(self):
        await self.exercise_route({'role': 'mensch', 'member': False}, 4003)

    async def test_identity_change(self):
        await self.exercise_route({'uid': 'different-account'}, 4001)

    async def test_permission_database_failure(self):
        await self.exercise_route({'db': False}, 1011)

    async def test_idle_connection_is_closed_without_broadcast(self):
        await self.exercise_route({'active': False}, 4001, idle=True)

    async def test_one_rejected_recipient_does_not_block_others(self):
        manager = manager_class()()
        allowed, rejected = Socket(), Socket()
        await manager.connect(allowed, 42, lambda: None)
        await manager.connect(rejected, 42, lambda: 4003)
        await manager.broadcast(42, {'content': 'allowed only'})
        self.assertEqual(allowed.messages, [{'content': 'allowed only'}])
        self.assertEqual(rejected.messages, [])
        self.assertEqual(rejected.code, 4003)
        self.assertEqual(manager.online_count(42), 1)

    async def test_disconnect_during_permission_check_does_not_send(self):
        manager = manager_class()()
        socket = Socket()
        await manager.connect(socket, 42, lambda: None)
        original = manager.guards[socket]
        # Simulate removal by another task while authorize awaits the executor.
        loop = asyncio.get_running_loop()
        removed = threading.Event()
        def remove():
            manager.disconnect(socket, 42)
            removed.set()
        def guard():
            loop.call_soon_threadsafe(remove)
            if not removed.wait(2):
                raise TimeoutError('test removal did not run')
            return original()
        manager.guards[socket] = guard
        await manager.broadcast(42, {'content': 'must not arrive'})
        self.assertEqual(socket.messages, [])


if __name__ == '__main__': unittest.main()
