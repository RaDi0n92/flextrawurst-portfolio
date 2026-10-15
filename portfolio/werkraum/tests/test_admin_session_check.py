import ast
import unittest
from pathlib import Path


class Denied(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code


class AdminSessionCheck(unittest.TestCase):
    def run_check(self, row, role="admin"):
        source = Path(__file__).resolve().parents[1] / "welt" / "api.py"
        node = next(n for n in ast.parse(source.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == "admin_session_check")
        node.decorator_list = []
        class Connection:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, query, params):
                assert "is_active" in query and params == ("synthetic",)
            def fetchone(self): return row
            def close(self): pass
        scope = {"Header": lambda **kw: None, "HTTPException": Denied,
                 "get_conn": Connection,
                 "_require_auth": lambda token: {"user_id": "synthetic", "role": role}}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), scope)
        return scope["admin_session_check"]("Bearer synthetic")

    def test_active_admin_allowed(self):
        self.assertEqual(self.run_check({"role": "admin", "is_active": True}), {"ok": True})

    def test_current_role_not_stale_token_is_authoritative(self):
        self.assertEqual(self.run_check({"role": "admin", "is_active": True}, "user"), {"ok": True})
        for row in (None, {"role": "user", "is_active": True}, {"role": "admin", "is_active": False}):
            with self.subTest(row=row), self.assertRaises(Denied): self.run_check(row)

    def test_entity_not_an_admin_account(self):
        with self.assertRaises(Denied): self.run_check({"role": "admin", "is_active": True}, "entity")


if __name__ == "__main__": unittest.main()
