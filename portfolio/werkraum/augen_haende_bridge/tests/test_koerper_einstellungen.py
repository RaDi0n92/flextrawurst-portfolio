"""Einstellungen: speichern, laden, kaputte Dateien, Klemmen, Anwenden."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.koerper.einstellungen import Einstellungen, anwenden, erfassen, klemmen, standard_pfad

BILDSCHIRM = (0, 0, 1920, 1080)


class DateiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pfad = Path(self.temp.name) / "unter" / "einstellungen.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_speichern_und_laden(self):
        e = Einstellungen(self.pfad)
        e.setzen("chat", {"x": 10, "y": 20, "deckkraft": 128, "regel": {"modus": "immer"}})
        self.assertTrue(e.speichern())
        neu = Einstellungen(self.pfad)
        neu.laden()
        self.assertEqual(neu.element("chat")["x"], 10)
        self.assertEqual(neu.element("gibtsnicht"), {})

    def test_fehlende_datei_ist_kein_fehler(self):
        e = Einstellungen(self.pfad)
        e.laden()
        self.assertEqual(e.daten, {})
        self.assertIsNone(e.fehler)

    def test_kaputte_datei_wird_gemeldet_nicht_geworfen(self):
        self.pfad.parent.mkdir(parents=True)
        self.pfad.write_text("{nicht json", encoding="utf-8")
        e = Einstellungen(self.pfad)
        e.laden()
        self.assertEqual(e.daten, {})
        self.assertIn("nicht gelesen", e.fehler)

    def test_unerwartete_struktur_wird_ignoriert(self):
        self.pfad.parent.mkdir(parents=True)
        self.pfad.write_text(json.dumps({"elemente": {"a": 5, "b": {"x": 1}}}), encoding="utf-8")
        e = Einstellungen(self.pfad)
        e.laden()
        self.assertEqual(list(e.daten), ["b"])

    def test_nicht_schreibbar_wird_gemeldet(self):
        e = Einstellungen(Path(self.temp.name) / "datei" / "x.json")
        (Path(self.temp.name) / "datei").write_text("ich bin eine datei", encoding="utf-8")
        self.assertFalse(e.speichern())
        self.assertIn("nicht gespeichert", e.fehler)

    def test_ohne_pfad_nur_im_speicher(self):
        e = Einstellungen(None)
        e.setzen("x", {"a": 1})
        self.assertFalse(e.speichern())

    def test_none_werte_werden_nicht_gespeichert(self):
        e = Einstellungen(None)
        e.setzen("x", {"a": 1, "b": None})
        self.assertEqual(e.element("x"), {"a": 1})

    def test_standardpfad_liegt_unter_localappdata(self):
        import os
        os.environ["LOCALAPPDATA"] = "C:\\Users\\x\\AppData\\Local"
        self.assertTrue(str(standard_pfad()).endswith("einstellungen.json"))


class KlemmenTests(unittest.TestCase):
    def test_im_bildschirm_bleibt_es_wo_es_ist(self):
        self.assertEqual(klemmen(100, 100, 300, 200, BILDSCHIRM), (100, 100))

    def test_weit_rechts_unten_wird_hereingeholt(self):
        x, y = klemmen(5000, 5000, 300, 200, BILDSCHIRM)
        self.assertTrue(x <= 1920 - 40 and y <= 1080 - 40)

    def test_weit_links_oben_wird_hereingeholt(self):
        x, y = klemmen(-5000, -5000, 300, 200, BILDSCHIRM)
        self.assertTrue(x + 300 >= 40 and y >= 0)


def fenster(rect=(100, 100, 400, 300), deckkraft=200, groesse=48):
    f = Mock()
    f.rechteck.return_value = rect
    f.deckkraft = deckkraft
    f.groesse = groesse
    return f


class AnwendenTests(unittest.TestCase):
    def test_erfassen(self):
        d = erfassen(fenster(), "chat")
        self.assertEqual((d["x"], d["y"], d["b"], d["h"], d["deckkraft"]), (100, 100, 300, 200, 200))
        self.assertNotIn("groesse", d)
        self.assertEqual(erfassen(fenster(), "raute")["groesse"], 48)

    def test_anwenden_setzt_ort_groesse_und_deckkraft(self):
        f = fenster()
        anwenden(f, {"x": 50, "y": 60, "b": 500, "h": 400, "deckkraft": 87}, "chat", lambda: BILDSCHIRM)
        f.setze_deckkraft.assert_called_once_with(87)
        f.verschiebe.assert_called_once_with(50, 60, 500, 400)

    def test_regieleiste_behaelt_ihre_groesse(self):
        f = fenster((0, 0, 76, 300))
        anwenden(f, {"x": 50, "y": 60, "b": 999, "h": 999}, "regie", lambda: BILDSCHIRM)
        f.verschiebe.assert_called_once_with(50, 60, 76, 300)

    def test_raute_groesse_wird_vor_dem_ort_gesetzt(self):
        f = fenster()
        anwenden(f, {"x": 50, "y": 60, "groesse": 96}, "raute", lambda: BILDSCHIRM)
        f.groesse_setzen.assert_called_once_with(96)

    def test_unbrauchbare_werte_werden_uebergangen(self):
        f = fenster()
        anwenden(f, {"x": "links", "y": None, "deckkraft": 999, "b": -5}, "chat", lambda: BILDSCHIRM)
        f.setze_deckkraft.assert_not_called()
        f.verschiebe.assert_not_called()

    def test_ort_ausserhalb_wird_geklemmt(self):
        f = fenster()
        anwenden(f, {"x": 90000, "y": 90000}, "regie", lambda: BILDSCHIRM)
        x, y = f.verschiebe.call_args.args[:2]
        self.assertTrue(x < 1920 and y < 1080)


if __name__ == "__main__":
    unittest.main()
