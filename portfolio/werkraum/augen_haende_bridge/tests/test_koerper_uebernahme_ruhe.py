"""Daniels Tippen und Klicken wird getrennt vom Zeigerrauschen gemerkt (Selkies sendet den Zeiger alle 0,8 s)."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper.uebernahme import RUHE_GNADE_S, Uebernahme


class FakeEngine:
    def __init__(self):
        self.busy = False
        self.letzte_sendung = -100.0
        self.zeiger_gesendet = 0
        self.daniel_uebernimmt = False
        self.beobachter = None

    def abbrechen(self, grund: str = "") -> None:
        pass


class RuheTests(unittest.TestCase):
    def setUp(self):
        self.t = {"s": 1000.0}
        self.engine = FakeEngine()
        self.ueb = Uebernahme(self.engine, uhr=lambda: self.t["s"])

    def test_ohne_eingabe_ist_die_ruhe_unendlich(self):
        self.assertEqual(self.ueb.ruhig_seit(), float("inf"))

    def test_nur_zeigerrauschen_zaehlt_nicht_als_tippen_oder_klicken(self):
        for _ in range(20):
            self.ueb.ereignis_x11("zeiger")
        self.assertEqual(self.ueb.ruhig_seit(), float("inf"))

    def test_tasten_und_klicks_von_daniel_setzen_die_ruhe_zurueck(self):
        self.ueb.ereignis_x11("taste")
        self.t["s"] += 3.0
        self.assertAlmostEqual(self.ueb.ruhig_seit(), 3.0)
        self.ueb.ereignis_x11("klick")
        self.assertAlmostEqual(self.ueb.ruhig_seit(), 0.0)

    def test_eigene_sendung_zaehlt_nicht_als_daniel(self):
        self.engine.letzte_sendung = self.t["s"]  # die Hände haben eben selbst gesendet
        self.ueb.ereignis_x11("taste")
        self.ueb.ereignis_x11("klick")
        self.assertEqual(self.ueb.ruhig_seit(), float("inf"))
        self.t["s"] += RUHE_GNADE_S + 0.05  # danach ist es wieder Daniel
        self.ueb.ereignis_x11("taste")
        self.assertAlmostEqual(self.ueb.ruhig_seit(), 0.0)

    def test_auch_mit_ausnahme_wird_sein_tippen_gemerkt(self):
        ueb = Uebernahme(self.engine, ausnahme=lambda: True, uhr=lambda: self.t["s"])
        ueb.ereignis_x11("taste")
        self.assertAlmostEqual(ueb.ruhig_seit(), 0.0, msg="die Ausnahme betrifft die Hände, nicht den Schutz seiner Felder")


if __name__ == "__main__":
    unittest.main()
