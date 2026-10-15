"""Real signed JWTs and actual auth/route functions; synthetic DB, no secrets."""
import ast
import copy
import os
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import UUID
import jwt

ROOT = Path(__file__).resolve().parents[1]
SECRET = 'synthetic-service-policy-test-secret-at-least-32-bytes'


class Denied(Exception):
    def __init__(self, status_code, detail): self.status_code = status_code


def load_functions(path, names, scope):
    nodes = [n for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    for n in nodes: n.decorator_list = []
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)


class ServiceTokens(unittest.TestCase):
    def setUp(self):
        self.grants = {'splitter:create': {'origin_types': ['codex_abwurf'], 'entity_ids': ['codex']}}
        self.row = (True, self.grants)
        self.closed = 0
        self.queries = []
        outer = self

        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, params): outer.queries.append((sql, params))
            def fetchone(self): return outer.row
            def close(self): outer.closed += 1

        self.driver = types.SimpleNamespace(connect=lambda *a, **k: Connection())
        self.scope = dict(UUID=UUID, os=os, jwt=jwt, _SECRET=SECRET, _ALGORITHM='HS256')
        load_functions(ROOT / 'welt/auth.py',
                       {'verify_token', '_current_human_account', '_current_service_account'}, self.scope)
        load_functions(ROOT / 'welt/api.py',
                       {'_require_auth', '_require_admin', '_require_splitter_writer'},
                       self.scope)
        self.scope['HTTPException'] = Denied
        self.token = self.mint()
        self.body = types.SimpleNamespace(origin_type='codex_abwurf', entity_id='codex', human_id=None)
        self.patch = patch.dict(sys.modules, {'psycopg2': self.driver})
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def mint(self, subject='codex-abwurf', role='admin', **extra):
        return jwt.encode({'sub': subject, 'role': role,
                           'exp': datetime.now(timezone.utc) + timedelta(minutes=1), **extra},
                          SECRET, algorithm='HS256')

    def verify(self, **kwargs): return self.scope['verify_token'](self.token, **kwargs)
    def writer(self): return self.scope['_require_splitter_writer']('Bearer '+self.token, self.body)

    def test_old_admin_service_token_denied_by_default(self):
        with self.assertRaises(jwt.InvalidTokenError): self.verify()
        with self.assertRaises(Denied) as caught:
            self.scope['_require_admin']('Bearer '+self.token)
        self.assertEqual(caught.exception.status_code, 401)
        self.assertEqual(self.queries, [])

    def test_explicit_route_uses_current_grants_and_never_admin_role(self):
        self.assertEqual(self.writer()['role'], 'service')
        self.assertEqual(self.queries[-1][1], ('codex-abwurf',))
        self.grants.clear()
        with self.assertRaises(Denied) as caught: self.writer()
        self.assertEqual(caught.exception.status_code, 403)
        self.assertEqual(self.closed, 2)

    def test_deleted_disabled_unknown_and_malformed_registry_fail_closed(self):
        for row in (None, (False, self.grants), (True, [])):
            self.row = row
            with self.subTest(row=row), self.assertRaises(jwt.InvalidTokenError):
                self.verify(allow_service=True)

    def test_origin_entity_and_human_impersonation_rejected(self):
        for key, value in [('origin_type', 'claude_abwurf'), ('entity_id', 'claude'),
                           ('human_id', '12345678-1234-1234-1234-123456789abc')]:
            body = copy.copy(self.body)
            setattr(self.body, key, value)
            with self.subTest(key=key), self.assertRaises(Denied): self.writer()
            self.body = body

    def test_none_entity_only_allowed_when_explicit(self):
        self.body.entity_id = None
        with self.assertRaises(Denied): self.writer()
        self.grants['splitter:create']['entity_ids'] = [None]
        self.assertEqual(self.writer()['role'], 'service')

    def test_db_outage_fails_closed(self):
        def unavailable(*a, **k): raise ConnectionError('synthetic')
        self.driver.connect = unavailable
        with self.assertRaises(Denied) as caught: self.writer()
        self.assertEqual(caught.exception.status_code, 401)

    def test_token_grants_cannot_override_database(self):
        self.token = self.mint(grants={'splitter:create': {'origin_types': ['evil'], 'entity_ids': ['other']}})
        self.assertEqual(self.writer()['grants'], self.grants)

    def test_expired_and_invalid_signature_never_reach_db(self):
        for token in (self.mint(exp=datetime.now(timezone.utc)-timedelta(seconds=1)),
                      jwt.encode({'sub':'codex-abwurf','role':'admin'}, SECRET+'wrong',algorithm='HS256')):
            self.token = token
            with self.assertRaises(jwt.InvalidTokenError): self.verify(allow_service=True)
        self.assertEqual(self.queries, [])

    def test_human_admin_retains_create_access_and_demotion_applies(self):
        self.token = self.mint('12345678-1234-1234-1234-123456789abc')
        self.row = ('admin', True)
        self.assertEqual(self.writer()['role'], 'admin')
        self.row = ('mensch', True)
        with self.assertRaises(Denied): self.writer()

    def test_service_cannot_access_collection_or_other_auth_routes(self):
        # Both helpers use default verification; no opt-in reaches those routes.
        with self.assertRaises(Denied): self.scope['_require_auth']('Bearer '+self.token)
        claims = self.verify(allow_service=True)
        self.assertNotIn('sub', claims)
        self.assertNotIn('human_id', claims)


if __name__ == '__main__': unittest.main()
