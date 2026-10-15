"""G15: Seeds — Lebenslauf, Versionen, Zielumfang nur mit Daniels Freigabe, Einfügen als markierter Block, Rücknahme ohne fremde Arbeit anzurühren."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.seeds import Freigaben, SeedFehler, SeedStore


def store(freigaben=None):
    o = Path(tempfile.mkdtemp())
    if freigaben is not None:
        (o / "freigaben.json").write_text(json.dumps(freigaben))
    return SeedStore(o), o


def dokument(s, pfad, inhalt="Immer zuerst die Tests lesen.", **kw):
    return s.vorschlagen(von="Codex", zieltyp="skill", titel="Tests zuerst", inhalt=inhalt, ziel_pfad=str(pfad), kapseln=["k-abc123"], **kw)


class VorschlagTests(unittest.TestCase):
    def test_vorschlag_version_und_ansicht(self):
        s, _ = store()
        a = s.vorschlagen(von="Codex", zieltyp="kontext", titel="Hinweis", inhalt="Bitte zuerst messen.", empfaenger=["Claude"], kapseln=["k-1"])
        self.assertEqual((a["version"], a["status"], a["von"]), (1, "vorschlag", "Codex"))
        b = s.vorschlagen(von="Codex", zieltyp="kontext", titel="Hinweis neu", inhalt="Zweite Fassung", empfaenger=["Claude"], seed_id=a["id"])
        self.assertEqual((b["id"], b["version"]), (a["id"], 2))
        self.assertEqual(s.hole(a["id"], 1)["inhalt"], "Bitte zuerst messen.", "die alte Version bleibt")
        self.assertEqual(s.hole(a["id"])["version"], 2)
        self.assertEqual([x["versionen"] for x in s.liste()], [2])
        self.assertEqual(s.liste("freigegeben"), [])

    def test_ungueltiges_wird_abgelehnt(self):
        s, _ = store()
        gut = dict(von="Codex", zieltyp="kontext", titel="T", inhalt="x", empfaenger=["Claude"])
        for aenderung, grund in (({"zieltyp": "wild"}, "zieltyp_unbekannt"), ({"titel": ""}, "titel_ungueltig"), ({"titel": "x" * 121}, "titel_ungueltig"), ({"inhalt": ""}, "inhalt_ungueltig"),
                                 ({"inhalt": "a\x00b"}, "inhalt_ungueltig"), ({"inhalt": "x" * 20_001}, "inhalt_ungueltig"), ({"empfaenger": []}, "empfaenger_fehlen"), ({"empfaenger": [""]}, "empfaenger_ungueltig"),
                                 ({"kapseln": ["../x"]}, "kapseln_ungueltig"), ({"seed_id": "s-00000000"}, "seed_unbekannt"), ({"zieltyp": "skill"}, "ziel_pfad_fehlt"), ({"zieltyp": "loop"}, "budget_fehlt"),
                                 ({"zieltyp": "ablauf", "inhalt": "kein dict"}, "inhalt_ungueltig")):
            with self.assertRaises(SeedFehler, msg=str(aenderung)) as c:
                s.vorschlagen(**{**gut, **aenderung})
            self.assertEqual(str(c.exception), grund, aenderung)
        self.assertEqual(s.liste(), [], "nichts Halbes ist entstanden")

    def test_ueberlebt_den_neustart(self):
        s, o = store()
        a = s.vorschlagen(von="C", zieltyp="kontext", titel="T", inhalt="x", empfaenger=["A"])
        s.freigeben(a["id"], "Daniel")
        neu = SeedStore(o)
        self.assertEqual(neu.hole(a["id"])["status"], "freigegeben")
        (o / "seeds.json").write_text("kaputt{")
        self.assertEqual(SeedStore(o).liste(), [], "eine kaputte Datei ergibt keinen Absturz")


class LebenslaufTests(unittest.TestCase):
    def test_zustandsuebergaenge_sind_streng(self):
        s, _ = store()
        a = s.vorschlagen(von="C", zieltyp="kontext", titel="T", inhalt="x", empfaenger=["A"])
        with self.assertRaises(SeedFehler):
            s.aktiv_setzen(a["id"], None, "Daniel")  # nicht freigegeben
        s.freigeben(a["id"], "Daniel")
        with self.assertRaises(SeedFehler):
            s.freigeben(a["id"], "Daniel")  # schon freigegeben
        self.assertEqual(s.aktiv_setzen(a["id"], None, "Starter")["status"], "aktiv")
        z = s.zurueckziehen(a["id"], None, "Daniel", grund="nicht mehr nötig")
        self.assertEqual(z["status"], "zurueckgezogen")
        with self.assertRaises(SeedFehler):
            s.zurueckziehen(a["id"], None, "Daniel")
        self.assertEqual([e["was"] for e in s.hole(a["id"])["ereignisse"]], ["vorgeschlagen", "freigegeben", "aktiv", "zurueckgezogen"], "jeder Schritt steht im Verlauf")

    def test_export_nennt_dass_kein_modellgewicht_veraendert_wird(self):
        s, _ = store()
        a = s.vorschlagen(von="C", zieltyp="kontext", titel="T", inhalt="x", empfaenger=["A"])
        e = s.exportieren(a["id"])
        self.assertEqual(len(e["versionen"]), 1)
        self.assertIn("kein Modellgewicht", e["hinweis"])
        with self.assertRaises(SeedFehler):
            s.exportieren("s-00000000")


class ZielumfangTests(unittest.TestCase):
    def test_ohne_freigabedatei_ist_nichts_erlaubt_und_das_profil_ist_vorsichtig(self):
        s, o = store()
        ziel = o / "ziel" / "SKILL.md"
        a = dokument(s, ziel)
        p = s.pruefen(a["id"])
        self.assertEqual((p["hindernisse"], p["braucht_daniel"], p["freiheit"]), (["ziel_nicht_freigegeben"], True, "nach_freigabe"))
        s.freigeben(a["id"], "Daniel")
        with self.assertRaises(SeedFehler) as c:
            s.datei_einfuegen(a["id"], None, "Starter")
        self.assertEqual(str(c.exception), "ziel_nicht_freigegeben")
        self.assertFalse(ziel.exists())

    def test_nur_freigegebene_pfade_und_arten(self):
        o = Path(tempfile.mkdtemp())
        f = Freigaben(None)
        (o / "f.json").write_text(json.dumps({"ziele": [{"pfad": str(o / "skills"), "arten": ["skill"]}, {"pfad": str(o / "einzeln.md"), "arten": ["dokument"]}, {"pfad": "relativ", "arten": ["skill"]},
                                                       {"pfad": str(o / "leer"), "arten": []}, 5, {"arten": ["skill"]}], "freiheit": "selbststaendig"}))
        f = Freigaben(o / "f.json")
        self.assertTrue(f.erlaubt(str(o / "skills" / "a" / "SKILL.md"), "skill"))
        self.assertFalse(f.erlaubt(str(o / "skills" / "a" / "SKILL.md"), "dokument"), "andere Art")
        self.assertTrue(f.erlaubt(str(o / "einzeln.md"), "dokument"))
        self.assertFalse(f.erlaubt(str(o / "einzeln.md.bak"), "dokument"), "nur dieser Pfad, kein Namensanfang")
        self.assertFalse(f.erlaubt(str(o / "skills" / ".." / "geheim.md"), "skill"), "kein Entkommen über ..")
        self.assertFalse(f.erlaubt("relativ/x", "skill"))
        self.assertFalse(f.erlaubt(str(o / "leer" / "x"), "skill"))
        self.assertEqual(f.freiheit(), "selbststaendig")
        self.assertEqual(Freigaben(o / "gibtsnicht.json").freiheit(), "nach_freigabe")
        (o / "kaputt.json").write_text("{")
        self.assertEqual((Freigaben(o / "kaputt.json").ziele(), Freigaben(o / "kaputt.json").freiheit()), ([], "nach_freigabe"))

    def test_ein_link_aus_dem_freigegebenen_ordner_heraus_wird_nicht_gefolgt(self):
        o = Path(tempfile.mkdtemp())
        (o / "frei").mkdir()
        (o / "fremd").mkdir()
        os.symlink(o / "fremd", o / "frei" / "link")
        (o / "f.json").write_text(json.dumps({"ziele": [{"pfad": str(o / "frei"), "arten": ["skill"]}]}))
        self.assertFalse(Freigaben(o / "f.json").erlaubt(str(o / "frei" / "link" / "x.md"), "skill"))


class DateiTests(unittest.TestCase):
    def aufbau(self, vorher: str | None = "# Mein Skill\nVorhandener Text.\n"):
        o = Path(tempfile.mkdtemp())
        ziel = o / "skills" / "SKILL.md"
        if vorher is not None:
            ziel.parent.mkdir(parents=True)
            ziel.write_text(vorher)
        s, _ = store({"ziele": [{"pfad": str(o / "skills"), "arten": ["skill"]}]})
        return s, ziel, vorher

    def test_einfuegen_sichert_das_original_haengt_nur_einen_block_an_und_ziehen_stellt_wieder_her(self):
        s, ziel, vorher = self.aufbau()
        a = dokument(s, ziel)
        s.freigeben(a["id"], "Daniel")
        r = s.datei_einfuegen(a["id"], None, "Starter")
        self.assertEqual(r["status"], "aktiv")
        text = ziel.read_text()
        self.assertTrue(text.startswith(vorher), "das Vorhandene bleibt unverändert davor stehen")
        self.assertIn(f"<!-- seed:{a['id']} v1 -->\nImmer zuerst die Tests lesen.\n<!-- /seed:{a['id']} -->", text)
        self.assertEqual((s._backup_pfad(s.hole(a["id"])) / "original.bin").read_bytes(), vorher.encode())
        z = s.datei_entfernen(a["id"], None, "Daniel")
        self.assertEqual(z["status"], "zurueckgezogen")
        self.assertEqual(ziel.read_text(), vorher, "Byte für Byte wie vorher")
        self.assertTrue(z["ereignisse"][-1]["wiederhergestellt"])

    def test_eine_neue_datei_verschwindet_wieder_wenn_nur_der_seed_sie_gefuellt_hat(self):
        s, ziel, _ = self.aufbau(vorher=None)
        a = dokument(s, ziel)
        s.freigeben(a["id"], "Daniel")
        s.datei_einfuegen(a["id"], None, "Starter")
        self.assertTrue(ziel.exists())
        s.datei_entfernen(a["id"], None, "Daniel")
        self.assertFalse(ziel.exists())

    def test_fremde_aenderungen_nach_dem_einfuegen_bleiben_erhalten(self):
        s, ziel, vorher = self.aufbau()
        a = dokument(s, ziel)
        s.freigeben(a["id"], "Daniel")
        s.datei_einfuegen(a["id"], None, "Starter")
        ziel.write_text(ziel.read_text() + "\nEine Zeile, die jemand anderes danach geschrieben hat.\n")
        s.datei_entfernen(a["id"], None, "Daniel")
        text = ziel.read_text()
        self.assertIn("Eine Zeile, die jemand anderes", text)
        self.assertNotIn("seed:", text)
        self.assertTrue(text.startswith(vorher))

    def test_wurde_der_block_veraendert_wird_nichts_entfernt(self):
        s, ziel, _ = self.aufbau()
        a = dokument(s, ziel)
        s.freigeben(a["id"], "Daniel")
        s.datei_einfuegen(a["id"], None, "Starter")
        ziel.write_text(ziel.read_text().replace("Tests lesen", "Tests lesen und mehr"))
        vor = ziel.read_bytes()
        with self.assertRaises(SeedFehler) as c:
            s.datei_entfernen(a["id"], None, "Daniel")
        self.assertEqual(str(c.exception), "block_veraendert_oder_weg")
        self.assertEqual(ziel.read_bytes(), vor)
        self.assertEqual(s.hole(a["id"])["status"], "aktiv", "es bleibt aktiv, bis ein Mensch entscheidet")

    def test_doppeltes_einfuegen_ohne_freigabe_und_nicht_dateiseeds(self):
        s, ziel, _ = self.aufbau()
        a = dokument(s, ziel)
        with self.assertRaises(SeedFehler) as c:
            s.datei_einfuegen(a["id"], None, "Starter")
        self.assertEqual(str(c.exception), "nicht_freigegeben")
        s.freigeben(a["id"], "Daniel")
        s.datei_einfuegen(a["id"], None, "Starter")
        with self.assertRaises(SeedFehler):
            s.datei_einfuegen(a["id"], None, "Starter")  # nicht mehr „freigegeben“
        k = s.vorschlagen(von="C", zieltyp="kontext", titel="T", inhalt="x", empfaenger=["A"])
        s.freigeben(k["id"], "Daniel")
        with self.assertRaises(SeedFehler) as c:
            s.datei_einfuegen(k["id"], None, "Starter")
        self.assertEqual(str(c.exception), "kein_datei_seed")

    def test_zwei_seeds_in_derselben_datei_lassen_sich_einzeln_entfernen(self):
        s, ziel, vorher = self.aufbau()
        a, b = dokument(s, ziel, "Erster"), dokument(s, ziel, "Zweiter")
        for x in (a, b):
            s.freigeben(x["id"], "Daniel")
            s.datei_einfuegen(x["id"], None, "Starter")
        s.datei_entfernen(a["id"], None, "Daniel")
        text = ziel.read_text()
        self.assertIn("Zweiter", text)
        self.assertNotIn("Erster", text)
        s.datei_entfernen(b["id"], None, "Daniel")
        self.assertEqual(ziel.read_text(), vorher)

    def test_eine_neue_version_ersetzt_nicht_die_aktive(self):
        s, ziel, _ = self.aufbau()
        a = dokument(s, ziel, "Fassung eins")
        s.freigeben(a["id"], "Daniel")
        s.datei_einfuegen(a["id"], None, "Starter")
        v2 = s.vorschlagen(von="Codex", zieltyp="skill", titel="Tests zuerst 2", inhalt="Fassung zwei", ziel_pfad=str(ziel), seed_id=a["id"])
        self.assertEqual(v2["status"], "vorschlag")
        self.assertIn("Fassung eins", ziel.read_text())
        self.assertNotIn("Fassung zwei", ziel.read_text(), "die zweite Fassung ist erst ein Vorschlag")
        self.assertEqual(s.hole(a["id"], 1)["status"], "aktiv")


if __name__ == "__main__":
    unittest.main()
