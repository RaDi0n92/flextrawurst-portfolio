"""Isolierte Regression: keine produktiven Imports, Logs oder Wesen-Dateien."""
import ast
import logging
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


class ContainerAdminPathSecurity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="container-admin-security-")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.base = root / "wesen"
        self.container = self.base / "synthetic" / "container" / "notizen"
        self.container.mkdir(parents=True)
        self.outside = root / "outside.md"
        self.outside.write_text("unveraendert", encoding="utf-8")
        source = Path(__file__).resolve().parents[1] / "codewesen_container.py"
        names = {"name_sicher", "_admin_container_ordner", "admin_entferne"}
        nodes = [n for n in ast.parse(source.read_text()).body
                 if isinstance(n, ast.FunctionDef) and n.name in names]
        self.ns = {"Path": Path, "BASE": self.base, "re": re,
                   "log": logging.getLogger("isolated-test"),
                   "flarum_stopp_protokoll": SimpleNamespace(schreibe=lambda **kw: None)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), self.ns)

    def test_valid_entry_and_protected_descriptor(self):
        entry = self.container / "entry.md"
        entry.write_text("synthetic", encoding="utf-8")
        descriptor = self.container / "container.md"
        descriptor.write_text("retain", encoding="utf-8")
        self.assertTrue(self.ns["admin_entferne"]("synthetic", "notizen", "entry.md"))
        self.assertFalse(entry.exists())
        self.assertFalse(self.ns["admin_entferne"]("synthetic", "notizen", "container.md"))
        self.assertTrue(descriptor.exists())

    def test_rejects_path_components(self):
        for name in ("../outside.md", str(self.outside), "..", "a/b.md", "a\\b.md", "x\x00.md"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.ns["admin_entferne"]("synthetic", "notizen", name)
        self.assertEqual(self.outside.read_text(), "unveraendert")

    def test_rejects_entity_escape_and_unknown_entity(self):
        for entity in ("../outside", "/tmp", "missing", "..", "a\\b"):
            with self.subTest(entity=entity), self.assertRaises(ValueError):
                self.ns["admin_entferne"](entity, "notizen", "entry.md")

    def test_rejects_file_and_directory_symlinks(self):
        (self.container / "link.md").symlink_to(self.outside)
        with self.assertRaises(ValueError):
            self.ns["admin_entferne"]("synthetic", "notizen", "link.md")
        (self.container.parent / "alias").symlink_to(self.container, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.ns["admin_entferne"]("synthetic", "alias", "entry.md")
        self.assertEqual(self.outside.read_text(), "unveraendert")


if __name__ == "__main__":
    unittest.main()
