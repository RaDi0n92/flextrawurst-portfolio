"""Isolated query-contract tests; no production data or service imports."""
import ast
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "welt" / "api.py"


class ProfilePrivacy(unittest.TestCase):
    def invoke(self, name, anonymous=False, missing=False):
        node = next(n for n in ast.parse(SOURCE.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == name)
        node.decorator_list = []
        queries = []
        class Denied(Exception):
            def __init__(self, status_code, detail): self.status_code = status_code
        class Connection:
            closed = False
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, params): queries.append(sql)
            def fetchall(self): return []
            def fetchone(self):
                if len(queries) != 1 or missing: return None
                return dict(id="synthetic", username="test", display_name="Test",
                            role="user", created_at=None, bio=None, public_tags=[],
                            avatar_symbol=None, gedankenwelt="synthetic thought",
                            profil_meta={"gedankenwelt_anonym": anonymous})
            def close(self): self.closed = True
        conn = Connection()
        scope = {"get_conn": lambda: conn, "HTTPException": Denied,
                 "Query": lambda **kw: kw.get("default")}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), scope)
        try:
            result = scope[name]("synthetic") if name == "public_profile" else scope[name]()
        except Denied as error:
            result = error.status_code
        self.assertTrue(conn.closed)
        return result, queries

    def test_directory_requires_public_profile_and_attributable_splitters(self):
        _, queries = self.invoke("menschen_liste")
        self.assertIn("p.visibility = 'public'", queries[0])
        self.assertIn("herkunft_sichtbar IS TRUE", queries[0])
        self.assertIn("status IN ('aktiv','aufgenommen','verarbeitet')", queries[0])

    def test_profile_entries_and_counts_exclude_anonymous_and_private(self):
        _, queries = self.invoke("public_profile")
        statements = [s for q in queries for s in q.split("SELECT") if "FROM mw_" in s]
        self.assertEqual(len(statements), 12)
        for sql in statements:
            self.assertIn("sichtbarkeit = 'public'", sql)
            self.assertNotIn("'anonym'", sql)
            self.assertIn("(meta->>'deleted') IS DISTINCT FROM 'true'", sql)

    def test_profile_splitter_counts_and_content_require_visible_origin(self):
        _, queries = self.invoke("public_profile")
        splitters = [q for q in queries if "FROM splitter" in q]
        self.assertEqual(len(splitters), 2)
        for sql in splitters:
            self.assertIn("herkunft_sichtbar IS TRUE", sql)
            self.assertIn("status IN ('aktiv','aufgenommen','verarbeitet')", sql)

    def test_anonymous_thought_not_attached_to_identity(self):
        result, _ = self.invoke("public_profile", anonymous=True)
        self.assertIsNone(result["gedankenwelt"])
        self.assertTrue(result["gedankenwelt_anonym"])
        result, _ = self.invoke("public_profile")
        self.assertEqual(result["gedankenwelt"], "synthetic thought")

    def test_missing_profile_stops_before_content_queries(self):
        result, queries = self.invoke("public_profile", missing=True)
        self.assertEqual(result, 404)
        self.assertEqual(len(queries), 1)
        self.assertIn("p.visibility = 'public'", queries[0])


if __name__ == "__main__": unittest.main()
