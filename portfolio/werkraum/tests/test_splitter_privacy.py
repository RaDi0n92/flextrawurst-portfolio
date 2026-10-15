"""Regression checks for the public splitter visibility contract.

These tests are deliberately source-isolated: they do not connect to the
production database and use only synthetic rows.
"""
import ast
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "welt" / "api.py"
TEXT = SOURCE.read_text(encoding="utf-8")


def isolated_function(name):
    tree = ast.parse(TEXT)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    node.decorator_list = []
    scope = {"_PUBLIC_SPLITTER_STATUSES": ("aktiv", "aufgenommen", "verarbeitet")}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), scope)
    return scope[name]


class SplitterPrivacy(unittest.TestCase):
    def test_public_predicate_uses_fragment_release_not_profile_visibility(self):
        predicate = isolated_function("_splitter_public_predicate")("s")
        self.assertIn("s.herkunft_sichtbar IS TRUE", predicate)
        self.assertIn("s.status IN ('aktiv','aufgenommen','verarbeitet')", predicate)
        self.assertNotIn("human_profiles", predicate)

    def test_python_policy_rejects_unreleased_but_allows_attributed_private_profiles(self):
        public = isolated_function("_splitter_is_public")
        base = {"herkunft_sichtbar": True, "status": "aktiv", "human_id": None}
        self.assertTrue(public(base))
        for row in (
            {**base, "herkunft_sichtbar": False},
            {**base, "status": "verblasst"},
        ):
            with self.subTest(row=row):
                self.assertFalse(public(row))
        self.assertTrue(public({**base, "human_id": "human-1", "human_profile_visibility": "private"}))

    def test_citation_default_and_explicit_override(self):
        effective = isolated_function("_zitierbar_effektiv")
        class Cursor:
            row = None
            def execute(self, *args): pass
            def fetchone(self): return self.row
        cur = Cursor()
        self.assertTrue(effective(cur, "synthetic", None))
        cur.row = {"meta": {}}
        self.assertTrue(effective(cur, "synthetic", None))
        self.assertFalse(effective(cur, "synthetic", False))
        cur.row = {"meta": {"zitierbar_standard": False}}
        self.assertFalse(effective(cur, "synthetic", None))

    def test_public_payload_is_allowlisted(self):
        payload = isolated_function("_public_event_payload")
        self.assertEqual(payload({"post_ref": "p", "emojis": ["✨"], "secret": "no"}),
                         {"post_ref": "p", "emojis": ["✨"]})
        self.assertEqual(payload(None), {})

    def test_all_public_splitter_reads_reference_the_same_policy(self):
        tree = ast.parse(TEXT)
        names = {
            "splitter_liste", "splitter_detail", "splitter_spur",
            "kompoase_splitter_liste", "kompoase_splitter_detail",
            "kompoase_splitter_spur", "splitter_story_view",
            "entity_splitter_aufnahmen", "search_global", "suche",
            "api_splitter_aufnahmen", "mw_feed",
        }
        functions = {n.name: ast.get_source_segment(TEXT, n) for n in tree.body
                     if isinstance(n, ast.FunctionDef) and n.name in names}
        self.assertEqual(names, set(functions))
        for name, source in functions.items():
            with self.subTest(function=name):
                self.assertTrue(
                    "_splitter_public_predicate" in source or "_splitter_is_public" in source
                )

    def test_public_story_filters_events_groups_and_connections(self):
        source = ast.get_source_segment(
            TEXT, next(n for n in ast.parse(TEXT).body
                       if isinstance(n, ast.FunctionDef) and n.name == "splitter_story_view"))
        self.assertIn("visibility_layer IN ('public','world')", source)
        self.assertIn("g.visibility_layer = 'public'", source)
        self.assertIn("ml.visibility_layer = 'public'", source)
        self.assertIn("splitter_verbindungen", source)
        self.assertIn("_splitter_public_predicate(\"sa\")", source)
        self.assertIn("_splitter_public_predicate(\"sb\")", source)

    def test_public_source_post_requires_public_visibility(self):
        self.assertGreaterEqual(TEXT.count("p.sichtbarkeit = 'public'"), 3)

    def test_story_group_output_excludes_private_snapshots(self):
        """Execute the real route; assert output and query boundaries."""
        node = next(n for n in ast.parse(TEXT).body
                    if isinstance(n, ast.FunctionDef) and n.name == "splitter_story_view")
        node.decorator_list = []
        class Connection:
            def __init__(self): self.query = ""; self.closed = False; self.queries = []
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, query, params):
                self.query = query
                self.queries.append(query)
            def fetchone(self):
                return {"id": "synthetic", "status": "aktiv", "herkunft_sichtbar": True}
            def fetchall(self):
                if "FROM group_material_links" in self.query:
                    return [{"id": 1, "group_id": 2, "group_name": "Public",
                             "rights_snapshot": {"private": "secret"},
                             "provenance_snapshot": {"human_id": "hidden"},
                             "meta": {"raw": "private"}, "added_by_id": "hidden"}]
                return []
            def close(self): self.closed = True
        for admin in (False, True):
            with self.subTest(admin=admin):
                conn = Connection()
                scope = {"Header": lambda **kw: None, "get_conn": lambda: conn,
                         "_current_admin_session": lambda _: admin,
                         "_splitter_is_public": isolated_function("_splitter_is_public"),
                         "_splitter_public_predicate": isolated_function("_splitter_public_predicate"),
                         "_public_event_payload": isolated_function("_public_event_payload")}
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), scope)
                result = scope["splitter_story_view"]("synthetic", authorization=None)
                link = result["group_links"][0]
                self.assertEqual(link["group_name"], "Public")
                self.assertEqual("rights_snapshot" in link, admin)
                self.assertEqual("provenance_snapshot" in link, admin)
                self.assertEqual("meta" in link, admin)
                self.assertEqual("added_by_id" in link, admin)
                query = next(q for q in conn.queries if "FROM group_material_links" in q)
                self.assertEqual("g.visibility_layer = 'public'" in query, not admin)
                self.assertEqual("ml.visibility_layer = 'public'" in query, not admin)
                self.assertTrue(conn.closed)


if __name__ == "__main__":
    unittest.main()
