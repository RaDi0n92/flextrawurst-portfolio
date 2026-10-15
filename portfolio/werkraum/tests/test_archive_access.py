"""Isolated archive gate tests; no imports of production services or secrets."""
import ast
import secrets
import unittest
from pathlib import Path
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / "welt" / "api.py"


class Denied(Exception):
    def __init__(self, status_code, detail, headers):
        self.status_code = status_code


class ArchiveAccess(unittest.TestCase):
    def setUp(self):
        self.tree = ast.parse(SOURCE.read_text())
        node = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "_require_archive_access")
        self.state = {"arch": "synthetic-arch", "crawl": "synthetic-crawl"}
        scope = {"Request": object, "Response": object, "secrets": secrets,
                 "HTTPException": Denied,
                 "_archkey_lesen": lambda: {"schluessel": self.state["arch"]},
                 "_crawlschluessel_lesen": lambda: {"schluessel": self.state["crawl"]},
                 "_current_admin_session": lambda token: token == "Bearer current-admin"}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), scope)
        self.gate = scope[node.name]

    def check(self, headers=None, query=None):
        response = SimpleNamespace(headers={})
        self.gate(SimpleNamespace(headers=headers or {}, query_params=query or {}), response)
        self.assertEqual(response.headers["Cache-Control"], "private, no-store")

    def test_anonymous_user_and_old_admin_denied(self):
        for token in (None, "Bearer ordinary", "Bearer stale-admin"):
            with self.subTest(token=token), self.assertRaises(Denied):
                self.check({"authorization": token})

    def test_current_admin_and_both_key_types_allowed(self):
        self.check({"authorization": "Bearer current-admin"})
        self.check({"x-archive-key": "synthetic-arch"})
        self.check({"x-crawl-key": "synthetic-crawl"})
        self.check(query={"archkey": "synthetic-arch"})
        self.check(query={"crawlschluessel": "synthetic-crawl"})

    def test_rotation_and_missing_state_fail_closed(self):
        self.check(query={"archkey": "synthetic-arch"})
        for replacement in ("rotated", "", None):
            self.state["arch"] = replacement
            with self.assertRaises(Denied):
                self.check(query={"archkey": "synthetic-arch"})

    def test_non_ascii_and_oversized_key_denied(self):
        for value in ("ö", "x" * 513):
            with self.subTest(value=value[:8]), self.assertRaises(Denied):
                self.check(query={"archkey": value})

    def test_every_archive_route_registers_guard(self):
        found = []
        for node in self.tree.body:
            if not isinstance(node, ast.FunctionDef): continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call) or not decorator.args: continue
                path = decorator.args[0]
                if not isinstance(path, ast.Constant) or not isinstance(path.value, str): continue
                if not path.value.startswith(("/code-archaeologie/", "/codegeil/", "/guardianstyle/", "/systemweite-archaeologie/")): continue
                found.append(path.value)
                deps = next(k.value for k in decorator.keywords if k.arg == "dependencies")
                self.assertEqual(ast.unparse(deps), "[Depends(_require_archive_access)]")
        self.assertEqual(len(found), 12)


if __name__ == "__main__": unittest.main()
