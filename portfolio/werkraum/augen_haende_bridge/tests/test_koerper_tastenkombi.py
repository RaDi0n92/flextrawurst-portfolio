"""Bedientaste und Tastenkombinationen: Text, Zulässigkeit, Erfassung."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.tastenkombi import (
    BEDIENTASTEN,
    Bedientaste,
    Erfasser,
    Kombination,
    standard_kombination,
)


class BedientasteTests(unittest.TestCase):
    def test_standard_ist_strg_alt(self):
        self.assertEqual(Bedientaste().text(), "Strg+Alt")

    def test_alle_gedrueckten_tasten_noetig(self):
        gehalten = set()
        b = Bedientaste("strg+alt", gehalten=lambda vk: vk in gehalten)
        self.assertFalse(b.gedrueckt())
        gehalten.add(0x11)
        self.assertFalse(b.gedrueckt())
        gehalten.add(0x12)
        self.assertTrue(b.gedrueckt())

    def test_einzelne_taste(self):
        b = Bedientaste("strg", gehalten=lambda vk: vk == 0x11)
        self.assertTrue(b.gedrueckt())

    def test_unbekannter_name_aendert_nichts(self):
        b = Bedientaste("alt")
        b.setzen("quatsch")
        b.setzen(5)
        self.assertEqual(b.name, "alt")

    def test_alle_optionen_haben_text_und_tasten(self):
        for name, (text, tasten) in BEDIENTASTEN.items():
            self.assertTrue(text and tasten, name)


class KombinationTests(unittest.TestCase):
    def test_text(self):
        self.assertEqual(Kombination(0, 0x7C).text(), "F13")
        self.assertEqual(Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74).text(), "Strg+Alt+F5")
        self.assertEqual(Kombination(w.MOD_SHIFT, 0x41).text(), "Umschalt+A")

    def test_text_rundlauf(self):
        for kombi in (Kombination(0, 0x7C), Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x35),
                      Kombination(w.MOD_WIN | w.MOD_SHIFT, 0x20), Kombination(w.MOD_ALT, 0x26)):
            self.assertEqual(Kombination.aus_text(kombi.text()), kombi)

    def test_buchstaben_ohne_modifikator_sind_nicht_zulaessig(self):
        self.assertFalse(Kombination(0, 0x41).zulaessig())
        self.assertFalse(Kombination(0, 0x31).zulaessig())
        self.assertFalse(Kombination(0, 0x20).zulaessig())
        self.assertTrue(Kombination(0, 0x7C).zulaessig())
        self.assertTrue(Kombination(w.MOD_CONTROL, 0x41).zulaessig())

    def test_unbekannte_taste_nie_zulaessig(self):
        self.assertFalse(Kombination(w.MOD_CONTROL, 0xE8).zulaessig())

    def test_aus_text_ist_tolerant(self):
        for text in (None, "", "  ", "Quatsch", "Strg+", "Strg+Nix", "A", 5, "Hyper+F5"):
            self.assertIsNone(Kombination.aus_text(text), text)

    def test_standard_kombinationen(self):
        self.assertEqual(standard_kombination(0).text(), "F13")
        self.assertEqual(standard_kombination(11).text(), "F24")
        self.assertIsNone(standard_kombination(12))


class ErfasserTests(unittest.TestCase):
    def baue(self, ereignisse):
        """ereignisse: Liste je Takt mit der Menge der gehaltenen Tasten."""
        zustand = {"takt": 0, "t": 0.0}

        def gehalten(vk):
            takt = min(zustand["takt"], len(ereignisse) - 1)
            return vk in ereignisse[takt]

        def schlafen(dt):
            zustand["takt"] += 1
            zustand["t"] += dt

        return Erfasser(gehalten=gehalten, jetzt=lambda: zustand["t"], schlafen=schlafen, takt_s=0.1)

    def test_erfasst_taste_mit_gehaltenen_modifikatoren(self):
        e = self.baue([set(), {0x11}, {0x11, 0x12}, {0x11, 0x12, 0x74}])
        kombi = e.erfassen(5)
        self.assertEqual(kombi, Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74))

    def test_nur_modifikatoren_reichen_nicht(self):
        e = self.baue([set(), {0x11}, {0x11, 0x12}])
        self.assertIsNone(e.erfassen(1))

    def test_escape_bricht_ab(self):
        e = self.baue([set(), {0x1B}])
        self.assertIsNone(e.erfassen(5))

    def test_beim_start_schon_gehaltene_taste_zaehlt_nicht(self):
        e = self.baue([{0x0D}, {0x0D}, {0x0D, 0x7C}])
        self.assertEqual(e.erfassen(5), Kombination(0, 0x7C))

    def test_zeitablauf(self):
        e = self.baue([set()])
        self.assertIsNone(e.erfassen(0.5))

    def test_im_hintergrund_meldet_das_ergebnis(self):
        ergebnisse = []
        e = self.baue([set(), {0x70}])
        e.im_hintergrund(ergebnisse.append, 5).join(2)
        self.assertEqual(ergebnisse, [Kombination(0, 0x70)])


if __name__ == "__main__":
    unittest.main()
