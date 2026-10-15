"""Durchklick-Modus: Strg-Taste steuert den Fensterstil, Standard und Umschalten je Fenster."""

from __future__ import annotations

import time
import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper.durchklick import DurchklickVerwalter


class Strg:
    def __init__(self):
        self.gedrueckt = False

    def __call__(self):
        return self.gedrueckt


def baue():
    strg = Strg()
    return DurchklickVerwalter(strg=strg), strg


class HaendeFreigabeTests(unittest.TestCase):
    """Die Hände eines Agenten bedienen ein Bridge-Fenster: es ist für die Aktion klickbar, danach wieder durchklickbar."""

    def test_erzwingen_wirkt_wie_gehaltene_bedientaste_und_endet(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("regie", f, aktiv=True)
        f.durchklick_setzen.reset_mock()
        v.erzwingen(5.0)
        v.tick()
        f.durchklick_setzen.assert_called_with(False)
        v.erzwingen(0)
        v.tick()
        f.durchklick_setzen.assert_called_with(True)

    def test_erzwingen_laeuft_von_selbst_ab(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("regie", f, aktiv=True)
        v.erzwingen(0.05)
        v.tick()
        f.durchklick_setzen.assert_called_with(False)
        time.sleep(0.1)
        v.tick()
        f.durchklick_setzen.assert_called_with(True)

    def test_gehoert_erkennt_nur_registrierte_fenster(self):
        v, strg = baue()
        v.registrieren("regie", Mock(hwnd=33554435), aktiv=True)
        self.assertTrue(v.gehoert(33554435))
        self.assertFalse(v.gehoert(104857603))
        self.assertFalse(v.gehoert(None))


class ModusTests(unittest.TestCase):
    def test_ohne_strg_durchlaessig_mit_strg_bedienbar(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("chat", f, aktiv=True)
        f.durchklick_setzen.assert_called_with(True)
        strg.gedrueckt = True
        v.tick()
        f.durchklick_setzen.assert_called_with(False)
        strg.gedrueckt = False
        v.tick()
        f.durchklick_setzen.assert_called_with(True)
        self.assertEqual(f.durchklick_setzen.call_count, 3)

    def test_ohne_zustandswechsel_wird_der_stil_nicht_erneut_gesetzt(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("chat", f, aktiv=True)
        for _ in range(10):
            v.tick()
        self.assertEqual(f.durchklick_setzen.call_count, 1)

    def test_aus_heisst_immer_bedienbar(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("chat", f, aktiv=False)
        f.durchklick_setzen.assert_called_with(False)
        strg.gedrueckt = True
        v.tick()
        strg.gedrueckt = False
        v.tick()
        self.assertEqual(f.durchklick_setzen.call_count, 1)

    def test_umschalten_wirkt_sofort(self):
        v, strg = baue()
        f = Mock()
        v.registrieren("t", f, aktiv=True)
        self.assertFalse(v.umschalten("t"))
        f.durchklick_setzen.assert_called_with(False)
        self.assertTrue(v.umschalten("t"))
        f.durchklick_setzen.assert_called_with(True)

    def test_fenster_sind_unabhaengig(self):
        v, strg = baue()
        a, b = Mock(), Mock()
        v.registrieren("a", a, aktiv=True)
        v.registrieren("b", b, aktiv=False)
        strg.gedrueckt = True
        v.tick()
        strg.gedrueckt = False
        v.tick()
        a.durchklick_setzen.assert_called_with(True)
        b.durchklick_setzen.assert_called_once_with(False)

    def test_unbekanntes_fenster_und_entfernen(self):
        v, _ = baue()
        self.assertFalse(v.aktiv("gibtsnicht"))
        v.setzen("gibtsnicht", True)
        f = Mock()
        v.registrieren("a", f)
        v.entfernen("a")
        v.tick()
        self.assertFalse(v.aktiv("a"))

    def test_ein_fehler_beim_setzen_wird_beim_naechsten_takt_wiederholt(self):
        v, _ = baue()
        f = Mock()
        f.durchklick_setzen.side_effect = [OSError("weg"), None]
        v.registrieren("a", f, aktiv=True)
        v.tick()
        self.assertEqual(f.durchklick_setzen.call_count, 2)

    def test_faden_stoesst_tick_an(self):
        v, _ = baue()
        v._takt_s = 0.01
        aufgaben = []
        v.starten(aufgaben.append)
        time.sleep(0.15)
        v.stoppen()
        self.assertTrue(any(a == v.tick for a in aufgaben))


if __name__ == "__main__":
    unittest.main()
