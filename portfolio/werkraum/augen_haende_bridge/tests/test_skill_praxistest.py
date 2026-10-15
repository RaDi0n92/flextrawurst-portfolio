"""Der Skill bridge-praxistest bleibt gesund: Kopf, Länge, Verweise, und jeder Befehl, den er nennt, gibt es wirklich im Werkzeug (damit die Anleitung nicht veraltet)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest import mock

from augen_haende_bridge.praxis.lauf import lade_szenario

SKILL = Path(__file__).resolve().parent.parent / "skills" / "bridge-praxistest"


def kopf(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "kein Kopf"
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_kopf_und_umfang(self):
        k = kopf(self.text)
        self.assertEqual(k["name"], "bridge-praxistest")
        self.assertLessEqual(len(k["description"]), 1024, "die Beschreibung ist das Einzige, was vor dem Auslösen im Kontext steht")
        self.assertIn("Nicht verwenden", k["description"], "Beschreibung nennt auch, wann der Skill nicht passt")
        self.assertLess(len(self.text.splitlines()), 500)

    def test_jeder_verweis_zeigt_auf_eine_vorhandene_datei_eine_ebene_tief(self):
        for pfad in re.findall(r"`(references/[\w.-]+)`", self.text):
            self.assertTrue((SKILL / pfad).is_file(), pfad)
            self.assertEqual(pfad.count("/"), 1)
        self.assertTrue((SKILL / "scripts" / "bridge.sh").is_file())

    def test_jeder_genannte_test_befehl_nimmt_das_werkzeug_an(self):
        from client_vps import bridge_cli

        genannt = set(re.findall(r"`test (\w+)", self.text)) | set(re.findall(r"test (\w+) \"", self.text))
        genannt |= {"start", "karte", "status", "nochmal", "kuer", "ansage", "getan", "gesehen", "zuschauer", "planaenderung"}
        beispiele = {"vorflug": ["vorflug", "Gemgem"], "start": ["start", "Gemgem"], "karte": ["karte"], "status": ["status"], "nochmal": ["nochmal"], "kuer": ["kuer", "eine Idee"], "ansage": ["ansage", "Schritt 1"],
                     "getan": ["getan", "etwas getan"], "gesehen": ["gesehen", "etwas gesehen", "ok"], "zuschauer": ["zuschauer", "ich sehe es", "bestaetigt"], "planaenderung": ["planaenderung", "anders"], "ursache": ["ursache", "Das Ziel war nicht gebunden, jetzt gebunden"], "nicht_getestet": ["nicht_getestet", "bewusst ausgelassen"]}
        for befehl in sorted(genannt):
            self.assertIn(befehl, beispiele, f"Skill nennt „test {befehl}“, aber der Test kennt ihn nicht")
            with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
                code = bridge_cli.main(["test", *beispiele[befehl]])
            self.assertEqual(code, 0, befehl)
            self.assertEqual(ask.call_args.args[0]["cmd"], "test")

    def test_keine_drohenden_grossbuchstaben_woerter_der_ton_erklaert(self):
        for wort in ("MUSS", "NIEMALS", "UNBEDINGT", "VERBOTEN", "ACHTUNG"):
            self.assertNotIn(wort, self.text)
        self.assertIn("Warum das so ist", self.text)
        self.assertIn("Wenn du dir einen Ausweg denkst", self.text)

    def test_schritte_tabelle_stimmt_mit_dem_szenario_ueberein(self):
        tabelle = (SKILL / "references" / "schritte.md").read_text(encoding="utf-8")
        for s in lade_szenario()["schritte"]:
            self.assertIn(f"| {s['nr']} | {s['teil']} | {s['titel']} |", tabelle)

    def test_die_ansage_vorlage_der_karte_erfuellt_die_eigene_regel(self):
        from augen_haende_bridge.praxis.lauf import PraxisLauf

        l = PraxisLauf(lade_szenario(), "a", "b", raute=lambda t, x: True)
        for nr in (1, 7, 23):
            l2 = PraxisLauf(lade_szenario(), "a", "b", raute=lambda t, x: True, ab=nr, menue_freigabe=True)
            k = l2.karte(l2.handelnder())
            self.assertTrue(l2.ansage(l2.handelnder(), k["ansage_vorlage"])["ok"], k["ansage_vorlage"])


if __name__ == "__main__":
    unittest.main()
