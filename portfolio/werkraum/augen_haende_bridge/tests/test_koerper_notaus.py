"""Tests für koerper/notaus.py: das thread-sichere Flag und die Auslöse-Logik. Der echte Hook läuft nur unter Windows
oder Wine (`probes/koerper_smoketest.py`)."""

from __future__ import annotations

import threading
import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.notaus import NotAus, TastaturHook, ist_ausloeser


class NotAusTests(unittest.TestCase):
    def test_zu_anfang_nicht_aktiv(self) -> None:
        self.assertFalse(NotAus().aktiv)

    def test_ausloesen_setzt_das_flag_und_ruft_alle_lauscher_einmal(self) -> None:
        na, a, b = NotAus(), Mock(), Mock()
        na.bei_ausloesen(a)
        na.bei_ausloesen(b)
        self.assertTrue(na.ausloesen("F12"))
        self.assertTrue(na.aktiv)
        self.assertEqual(na.grund, "F12")
        a.assert_called_once_with("F12")
        b.assert_called_once_with("F12")

    def test_zweites_ausloesen_aendert_nichts(self) -> None:
        na, a = NotAus(), Mock()
        na.bei_ausloesen(a)
        na.ausloesen("F12")
        self.assertFalse(na.ausloesen("Menü"))
        self.assertEqual(na.grund, "F12")
        a.assert_called_once()

    def test_ein_kaputter_lauscher_haelt_die_anderen_nicht_auf(self) -> None:
        na, gut = NotAus(), Mock()
        na.bei_ausloesen(Mock(side_effect=RuntimeError("kaputt")))
        na.bei_ausloesen(gut)
        na.ausloesen("F12")
        gut.assert_called_once()
        self.assertTrue(na.aktiv)

    def test_freigeben_loescht_das_flag_und_meldet_es(self) -> None:
        na, frei = NotAus(), Mock()
        na.bei_freigabe(frei)
        self.assertFalse(na.freigeben())
        na.ausloesen("F12")
        self.assertTrue(na.freigeben())
        self.assertFalse(na.aktiv)
        self.assertEqual(na.grund, "")
        frei.assert_called_once_with()

    def test_ausloesen_aus_einem_fremden_faden_ist_sofort_sichtbar(self) -> None:
        na = NotAus()
        faden = threading.Thread(target=na.ausloesen, args=("F12",))
        faden.start()
        faden.join()
        self.assertTrue(na.aktiv)


class AusloeserTests(unittest.TestCase):
    def test_nur_taste_runter_der_richtigen_taste_loest_aus(self) -> None:
        self.assertTrue(ist_ausloeser(w.WM_KEYDOWN, w.VK_F12, w.VK_F12))
        self.assertTrue(ist_ausloeser(w.WM_SYSKEYDOWN, w.VK_F12, w.VK_F12))
        self.assertFalse(ist_ausloeser(w.WM_KEYUP, w.VK_F12, w.VK_F12))
        self.assertFalse(ist_ausloeser(w.WM_KEYDOWN, w.VK_F1, w.VK_F12))


class GatingTests(unittest.TestCase):
    def test_hook_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            TastaturHook(NotAus()).start()


if __name__ == "__main__":
    unittest.main()
