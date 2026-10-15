"""Linux-Körper: die gemeinsame Fensterklasse darf keine Methode tragen, die Raute oder Terminal als eigenes Attribut überschreiben (Ziehen mit der Maus warf sonst TypeError)."""

import ast
import unittest
from pathlib import Path

KOERPER = Path(__file__).resolve().parent.parent / "src" / "augen_haende_bridge" / "koerper"


def methoden(datei: str, klasse: str) -> set[str]:
    baum = ast.parse((KOERPER / datei).read_text(encoding="utf-8"))
    for k in baum.body:
        if isinstance(k, ast.ClassDef) and k.name == klasse:
            return {f.name for f in k.body if isinstance(f, ast.FunctionDef)}
    raise AssertionError(f"{klasse} nicht gefunden")


def attribute(datei: str) -> set[str]:
    baum = ast.parse((KOERPER / datei).read_text(encoding="utf-8"))
    return {n.attr for n in ast.walk(baum) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self" and isinstance(n.ctx, ast.Store)}


class NamenTests(unittest.TestCase):
    def test_keine_methode_der_linux_fensterbasis_wird_von_unterklassen_als_attribut_ueberschrieben(self):
        basis = methoden("fenster_linux.py", "Fenster")
        for datei in ("raute_fenster.py", "terminal_fenster.py", "chat_fenster.py", "regie_fenster.py"):
            kollision = basis & attribute(datei)
            self.assertEqual(kollision, set(), f"{datei} überschreibt Methoden der Fensterbasis: {sorted(kollision)}")


if __name__ == "__main__":
    unittest.main()
