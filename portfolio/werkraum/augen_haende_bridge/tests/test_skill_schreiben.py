"""Skill „skill-schreiben“: das Gerüst-Skript erzeugt prüfbare Skills (und überschreibt nie), der Prüfer findet echte Mängel — und der Skill besteht seine eigene Prüfung."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SKILL = WURZEL / "skills" / "skill-schreiben"


def lade(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


geruest, pruefer = lade("skill_geruest"), lade("skill_pruefen")


def fehler(befunde):
    return [t for a, t in befunde if a == "Fehler"]


def hinweise(befunde):
    return [t for a, t in befunde if a == "Hinweis"]


GUT = """---
name: beispiel
description: Zeigt, wie man Beispiele ordnet. Verwenden, wenn jemand "Beispiele ordnen" sagt. Nicht verwenden für Tabellenkalkulation.
---

# Beispiel

Fertig ist es, wenn die Liste sortiert vor dir liegt (Beleg: die Ausgabe).

## Warum das so ist
- Sortierte Listen findet man schneller.
"""


def skill(inhalt=GUT, name="beispiel", refs=None):
    wurzel = Path(tempfile.mkdtemp())
    ordner = wurzel / name
    ordner.mkdir()
    if inhalt is not None:
        (ordner / "SKILL.md").write_text(inhalt, encoding="utf-8")
    for n, t in (refs or {}).items():
        (ordner / "references").mkdir(exist_ok=True)
        (ordner / "references" / n).write_text(t, encoding="utf-8")
    return ordner


class PrueferTests(unittest.TestCase):
    def pruef(self, ordner, **kw):
        return pruefer.pruefen(ordner, Path("/nicht/da/cli.py"), Path(tempfile.mkdtemp()), **kw)

    def test_ein_guter_skill_hat_keine_befunde(self):
        self.assertEqual(self.pruef(skill()), [])

    def test_fehlende_datei_und_kaputter_kopf(self):
        self.assertIn("fehlt die Datei SKILL.md", fehler(self.pruef(skill(None)))[0])
        self.assertIn("Der Kopf fehlt", fehler(self.pruef(skill("# ohne Kopf\n")))[0])

    def test_name_und_beschreibung(self):
        self.assertTrue(any("Ordnername" in f for f in fehler(self.pruef(skill(GUT.replace("name: beispiel", "name: anders"))))))
        self.assertTrue(any("1024" in f for f in fehler(self.pruef(skill(GUT.replace("Zeigt, wie man Beispiele ordnet.", "x" * 1100))))))
        self.assertTrue(any("description" in f for f in fehler(self.pruef(skill(GUT.replace("description: Zeigt", "beschreibung: Zeigt"))))))

    def test_hinweise_zu_ton_und_aufbau(self):
        h = hinweise(self.pruef(skill(GUT.replace("Zeigt, wie", "Ich zeige dir, wie"))))
        self.assertTrue(any("dritter Person" in x for x in h))
        h = hinweise(self.pruef(skill(GUT.replace(" Verwenden, wenn jemand \"Beispiele ordnen\" sagt.", ""))))
        self.assertTrue(any("Auslöser" in x for x in h))
        h = hinweise(self.pruef(skill(GUT.replace(" Nicht verwenden für Tabellenkalkulation.", ""))))
        self.assertTrue(any("nicht* passt" in x for x in h))
        h = hinweise(self.pruef(skill(GUT + "\nDu MUSS das tun und NIEMALS vergessen.\n")))
        self.assertEqual(len([x for x in h if "Großbuchstaben" in x]), 2)
        h = hinweise(self.pruef(skill(GUT.replace("## Warum das so ist", "## Hinweise"))))
        self.assertTrue(any("Warum" in x for x in h))

    def test_zu_lang_platzhalter_und_verweise(self):
        self.assertTrue(any("500" in f for f in fehler(self.pruef(skill(GUT + "\nzeile\n" * 600)))))
        self.assertTrue(any("Platzhalter" in f for f in fehler(self.pruef(skill(GUT + "\n@ausfüllen@\n")))))
        f = fehler(self.pruef(skill(GUT + "\nSiehe `references/gibtsnicht.md`.\n")))
        self.assertTrue(any("gibtsnicht" in x for x in f))
        h = hinweise(self.pruef(skill(GUT, refs={"unerwaehnt.md": "# Text\n"})))
        self.assertTrue(any("nicht erwähnt" in x for x in h))
        h = hinweise(self.pruef(skill(GUT + "\nSiehe `references/a.md`.\n", refs={"a.md": "zeile\n" * 320})))
        self.assertTrue(any("Inhaltsverzeichnis" in x for x in h))
        h = hinweise(self.pruef(skill(GUT + "\nSiehe `references/a/b.md`.\n")))
        self.assertTrue(any("tiefer als eine Ebene" in x for x in h))

    def test_lesbarkeitsregel_findet_lange_absaetze_und_schont_tabellen_code_und_adressen(self):
        lang = "Das ist ein sehr langer Satz, der weit über die Grenze hinausgeht und deshalb in kürzere Absätze gehört, damit man ihn gut lesen kann."
        h = hinweise(self.pruef(skill(GUT + "\n" + lang + "\n")))
        self.assertTrue(any("länger als 110" in x for x in h))
        geschont = GUT + f"\n| {lang} | {lang} |\n\n```\n{lang}\n```\n\nSiehe https://example.org/{'x' * 120}\n"
        self.assertEqual(self.pruef(skill(geschont)), [], "Tabellen, Code und Adressen sind ausgenommen")
        self.assertEqual(pruefer.lange_zeilen("---\nname: a\ndescription: " + "x" * 300 + "\n---\nkurz\n"), [], "der Kopf zählt nicht")
        h = hinweise(self.pruef(skill(GUT, refs={"ref.md": lang + "\n"})))
        self.assertTrue(any("references/ref.md" in x and "länger als 110" in x for x in h), "auch Referenzen werden geprüft")

    def test_befehle_im_text_muessen_im_werkzeug_existieren(self):
        cli = Path(tempfile.mkdtemp()) / "bridge_cli.py"
        cli.write_text('"""Hilfe\n  bridge_cli.py say "Text"   sagen\n  bridge_cli.py test karte   Karte\n"""\n')
        text = GUT + "\nMach `bridge_cli.py say hallo` und `sh x/bridge.sh tanzen nun`.\n"
        f = fehler(pruefer.pruefen(skill(text), cli, Path(tempfile.mkdtemp())))
        self.assertEqual(len(f), 1)
        self.assertIn("tanzen", f[0])

    def test_ein_vorhandenes_szenario_wird_geprueft_und_im_text_erwartet(self):
        sz = Path(tempfile.mkdtemp())
        (sz / "szenario_beispiel.json").write_text(json.dumps({"schritte": []}))
        self.assertTrue(any("ungültig" in f for f in fehler(pruefer.pruefen(skill(), Path("/x"), sz))))
        gut = {"id": "b", "schritte": [{"nr": 1, "teil": "T", "ziel": "Z", "titel": "t", "pruefe": "p", "mache": "m", "erwarte": "e", "evidenz": ["sehen"]}]}
        (sz / "szenario_beispiel.json").write_text(json.dumps(gut))
        b = pruefer.pruefen(skill(), Path("/x"), sz)
        self.assertEqual(fehler(b), [])
        self.assertTrue(any("--szenario=beispiel" in x for x in hinweise(b)))
        self.assertEqual(pruefer.pruefen(skill(GUT + "\nStart mit `--szenario=beispiel`.\n"), Path("/x"), sz), [])


class GeruestTests(unittest.TestCase):
    def test_geruest_erzeugt_einen_skill_der_nur_noch_ausgefuellt_werden_muss(self):
        ziel, sz = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        angelegt = geruest.erzeugen("mein-ablauf", "Mein Ablauf", ziel, True, sz)
        self.assertEqual(len(angelegt), 4)
        text = (ziel / "mein-ablauf" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: mein-ablauf", text)
        self.assertIn("--szenario=mein-ablauf", text)
        f = fehler(pruefer.pruefen(ziel / "mein-ablauf", Path("/x"), sz))
        self.assertTrue(any("Platzhalter" in x for x in f), "frisch erzeugt ist noch auszufüllen: der Prüfer sagt es")
        s = json.loads((sz / "szenario_mein-ablauf.json").read_text(encoding="utf-8"))
        self.assertEqual((s["id"], len(s["schritte"])), ("mein-ablauf", 2))
        from augen_haende_bridge.praxis.lauf import lade_szenario

        self.assertEqual(len(lade_szenario(sz / "szenario_mein-ablauf.json")["schritte"]), 2, "das erzeugte Szenario ist gültig")

    def test_ueberschreibt_nie_und_prueft_den_namen(self):
        ziel, sz = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        geruest.erzeugen("a", "A", ziel, True, sz)
        with self.assertRaises(SystemExit) as c:
            geruest.erzeugen("a", "A", ziel, False, sz)
        self.assertIn("überschreibe nichts", str(c.exception))
        (sz / "szenario_b.json").write_text("{}")
        with self.assertRaises(SystemExit):
            geruest.erzeugen("b", "B", ziel, True, sz)
        self.assertFalse((ziel / "b").exists() and (ziel / "b" / "SKILL.md").exists() and False)
        for schlecht in ("Gross", "../x", "", "-a", "a b", "x" * 41):
            with self.assertRaises(SystemExit, msg=schlecht):
                geruest.erzeugen(schlecht, "T", ziel, False, sz)

    def test_hauptprogramm(self):
        ziel = Path(tempfile.mkdtemp())
        self.assertEqual(geruest.main(["neuer-skill", f"--ziel={ziel}", "--titel=Neuer Skill"]), 0)
        self.assertTrue((ziel / "neuer-skill" / "SKILL.md").is_file())
        self.assertEqual(geruest.main([]), 2)
        self.assertEqual(geruest.main(["a", "b"]), 2)
        self.assertEqual(geruest.main(["a", "--quatsch"]), 2)


class EigenerSkillTests(unittest.TestCase):
    def test_beide_skills_bestehen_die_eigene_pruefung(self):
        for name in ("skill-schreiben", "bridge-praxistest"):
            self.assertEqual(pruefer.pruefen(WURZEL / "skills" / name), [], name)

    def test_der_skill_nennt_seine_beiden_werkzeuge_und_die_harness(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for muss in ("skill_geruest.py", "skill_pruefen.py", "szenario-schema.md", "praxis/", "--szenario=", "Gegenprobe"):
            self.assertIn(muss, text)

    def test_die_evidenzarten_im_schema_sind_die_der_harness(self):
        from augen_haende_bridge.praxis.lauf import EVIDENZ_ARTEN

        schema = (SKILL / "references" / "szenario-schema.md").read_text(encoding="utf-8")
        for art in EVIDENZ_ARTEN:
            self.assertIn(f"`{art}`", schema, f"Evidenzart {art} fehlt in der Schema-Anleitung")


if __name__ == "__main__":
    unittest.main()
