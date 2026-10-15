"""Collection route uses the stable auth identity contract by role."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


class CollectionIdentity(unittest.TestCase):
    def load(self, claims):
        source = ROOT / "welt/api.py"
        node = next(n for n in ast.walk(ast.parse(source.read_text()))
                    if isinstance(n, ast.FunctionDef) and n.name == "splitter_einsammeln")
        node.decorator_list = []
        updates = []
        events = []

        class Cursor:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, params):
                if sql.lstrip().startswith("SELECT id, status"):
                    self.row = {"id": "splitter-1", "status": "aktiv", "entity_id": "origin", "essenz": "x"}
                elif sql.lstrip().startswith("UPDATE splitter"):
                    updates.append(params)
                elif "INSERT INTO events" in sql:
                    events.append(params)
            def fetchone(self): return getattr(self, "row", None)

        class Connection:
            def cursor(self): return Cursor()
            def commit(self): pass
            def close(self): pass

        def require_auth(_authorization): return claims
        scope = {
            "_require_auth": require_auth,
            "Header": lambda default=None: default,
            "HTTPException": type("HTTPException", (Exception,),
                                   {"__init__": lambda self, status_code, detail: setattr(self, "status_code", status_code)}),
            "get_conn": lambda: Connection(),
            "datetime": SimpleNamespace(utcnow=lambda: SimpleNamespace(isoformat=lambda: "now")),
            "psycopg2": SimpleNamespace(extras=SimpleNamespace(Json=lambda value: value)),
        }
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), scope)
        return scope["splitter_einsammeln"]("splitter-1", "Bearer token"), updates, events

    def test_entity_uses_user_id_as_entity(self):
        result, updates, events = self.load({"user_id": "wesen-1", "role": "entity"})
        self.assertEqual(result["eingesammelt_von_typ"], "entity")
        self.assertEqual(result["eingesammelt_von"], "wesen-1")
        self.assertEqual(events[0][0], "wesen-1")

    def test_human_uses_user_id_without_entity_impersonation(self):
        result, updates, events = self.load({"user_id": "00000000-0000-0000-0000-000000000001", "role": "mensch"})
        self.assertEqual(result["eingesammelt_von_typ"], "human")
        self.assertIsNone(events[0][0])

    def test_service_token_is_still_denied(self):
        with self.assertRaises(Exception) as error:
            self.load({"user_id": "codex-abwurf", "role": "service"})
        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__": unittest.main()
