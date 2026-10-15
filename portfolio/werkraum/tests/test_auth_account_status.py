"""Execute the actual auth functions without loading production signing secrets."""
import ast
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import UUID


class InvalidToken(Exception):
    pass


class AccountStatusTests(unittest.TestCase):
    user_id = "12345678-1234-1234-1234-123456789abc"

    def setUp(self):
        self.row = ("mensch", True)
        self.closed = False
        self.queries = []
        self.decoded = {"sub": self.user_id, "role": "admin"}
        outer = self

        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, params): outer.queries.append((sql, params))
            def fetchone(self): return outer.row
            def close(self): outer.closed = True

        self.driver = types.SimpleNamespace(connect=lambda *a, **kw: Connection())
        source = Path(__file__).resolve().parents[1] / "welt/auth.py"
        names = {"verify_token", "_current_human_account"}
        nodes = [n for n in ast.parse(source.read_text()).body
                 if isinstance(n, ast.FunctionDef) and n.name in names]
        self.scope = {"UUID": UUID, "os": os, "_SECRET": "synthetic", "_ALGORITHM": "HS256",
                      "jwt": types.SimpleNamespace(get_unverified_header=lambda token: {"alg": "HS256"},
                                                   decode=lambda *a, **kw: self.decoded,
                                                   InvalidTokenError=InvalidToken)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), self.scope)

    def verify(self):
        with patch.dict(sys.modules, {"psycopg2": self.driver}):
            return self.scope["verify_token"]("synthetic")

    def test_demotion_takes_effect_for_same_token(self):
        self.row = ("admin", True)
        self.assertEqual(self.verify()["role"], "admin")
        self.row = ("mensch", True)
        self.assertEqual(self.verify()["role"], "mensch")
        self.assertEqual(len(self.queries), 2)
        self.assertTrue(self.closed)
        self.assertEqual(self.queries[-1][1], (self.user_id,))

    def test_disabled_and_deleted_accounts_rejected(self):
        for row in (("admin", False), None):
            with self.subTest(row=row):
                self.row = row
                with self.assertRaises(InvalidToken): self.verify()
                self.assertTrue(self.closed)

    def test_current_admin_role_applies_to_old_user_token(self):
        self.decoded["role"] = "mensch"
        self.row = ("admin", True)
        self.assertEqual(self.verify()["role"], "admin")

    def test_database_failure_does_not_accept_old_claim(self):
        def unavailable(*args, **kwargs): raise ConnectionError("synthetic unavailable")
        self.driver.connect = unavailable
        with self.assertRaises(ConnectionError): self.verify()

    def test_legacy_user_id_claim_is_checked(self):
        self.decoded = {"sub": "legacy-name", "user_id": self.user_id, "role": "admin"}
        self.assertEqual(self.verify()["role"], "mensch")
        self.assertEqual(self.queries[-1][1], (self.user_id,))

    def test_entity_contract_unchanged_but_service_denied_by_default(self):
        self.decoded = {"sub": "synthetic-entity", "role": "entity"}
        self.assertEqual(self.verify()["role"], "entity")
        self.decoded = {"sub": "synthetic-service", "role": "admin"}
        with self.assertRaises(InvalidToken):
            self.verify()
        self.assertEqual(self.queries, [])

    def test_invalid_signature_is_rejected_before_database_access(self):
        def invalid(*args, **kwargs): raise InvalidToken("signature")
        self.scope["jwt"].decode = invalid
        with self.assertRaises(InvalidToken): self.verify()
        self.assertEqual(self.queries, [])


if __name__ == "__main__":
    unittest.main()
