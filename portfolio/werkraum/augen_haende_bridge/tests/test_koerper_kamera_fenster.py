"""Selbstbild-Fenster: Geometrie und Bedienung ohne echtes Win32-Fenster (wie bei den anderen Fenstertests)."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from augen_haende_bridge.koerper import kamera_fenster as kf
from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.kamera_fenster import KameraFenster


def _baue(breite: int = 240, hoehe: int = 190, **overrides) -> KameraFenster:
    f = object.__new__(KameraFenster)
    f.name, f.farbe, f.bild = "Claude", w.rgb_hex("#00E5FF"), None
    f._verbergen = Mock()
    f.deckkraft = stil.deckkraft_alpha(85)
    f.clientgroesse = Mock(return_value=(breite, hoehe))
    f.rechteck = Mock(return_value=(100, 50, 100 + breite, 50 + hoehe))
    f.neu_zeichnen = Mock()
    f.setze_deckkraft = Mock(side_effect=lambda alpha: setattr(f, "deckkraft", int(alpha)))
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class GeometrieTests(unittest.TestCase):
    def test_bild_bleibt_unverzerrt_und_mittig(self):
        links, oben, b, h = kf.bild_flaeche(240, 190, 640, 480)
        self.assertAlmostEqual(b / h, 640 / 480, delta=0.02)
        self.assertGreaterEqual(oben, kf.KOPF_H)
        self.assertLessEqual(links + b, 240)
        self.assertLessEqual(oben + h, 190)

    def test_breites_fenster_laesst_seitlich_platz(self):
        links, _, b, _ = kf.bild_flaeche(600, 190, 640, 480)
        self.assertGreater(links, 100)

    def test_kopfknoepfe_liegen_im_kopf_und_ueberlappen_nicht(self):
        r = kf.kopf_rechtecke(240)
        self.assertLessEqual(r["deckkraft"][2], r["schliessen"][0])
        self.assertTrue(all(0 <= v[1] and v[3] <= kf.KOPF_H for v in r.values()))

    def test_kanten_liefern_groessenaenderung(self):
        self.assertEqual(kf.kante_bei(0, 0, 240, 190), w.HTTOPLEFT)
        self.assertEqual(kf.kante_bei(120, 189, 240, 190), w.HTBOTTOM)
        self.assertIsNone(kf.kante_bei(120, 90, 240, 190))


class BedienungTests(unittest.TestCase):
    def test_treffer_kopf_verschiebt_inneres_ist_client_kanten_vergroessern(self):
        f = _baue()
        self.assertEqual(f.treffer(100 + 60, 50 + 10), w.HTCAPTION)
        self.assertEqual(f.treffer(100 + 120, 50 + 100), w.HTCLIENT)
        self.assertEqual(f.treffer(100 + 239, 50 + 100), w.HTRIGHT)

    def test_kopfknoepfe_sind_keine_verschiebeflaeche(self):
        f = _baue()
        r = kf.kopf_rechtecke(240)["schliessen"]
        self.assertEqual(f.treffer(100 + r[0] + 2, 50 + 5), w.HTCLIENT)

    def test_prozentknopf_schaltet_die_deckkraft_weiter(self):
        f = _baue()
        vorher = f.deckkraft_prozent()
        d = kf.kopf_rechtecke(240)["deckkraft"]
        f.bei_maus_runter(d[0] + 3, 5, 1)
        self.assertNotEqual(f.deckkraft_prozent(), vorher)

    def test_x_verbirgt_nur_das_fenster_ruft_den_besitzer(self):
        f = _baue()
        s = kf.kopf_rechtecke(240)["schliessen"]
        f.bei_maus_runter(s[0] + 3, 5, 1)
        f._verbergen.assert_called_once_with()

    def test_rad_aendert_die_deckkraft_in_5_prozent_und_klemmt(self):
        f = _baue(deckkraft=stil.deckkraft_alpha(10))
        f.bei_rad(-120, 0, 0, 0)
        self.assertGreaterEqual(f.deckkraft_prozent(), 10)
        f.bei_rad(120, 0, 0, 0)
        self.assertGreater(f.deckkraft_prozent(), 10)

    def test_bild_setzen_und_loeschen(self):
        f = _baue()
        f.bild_setzen(b"\x00" * 12, 2, 2)
        self.assertEqual(f.bild, (b"\x00" * 12, 2, 2))
        f.bild_loeschen()
        self.assertIsNone(f.bild)


class ZeichnenTests(unittest.TestCase):
    def _leinwand(self):
        l = Mock()
        l.breite, l.hoehe = 240, 190
        l.hdc = 1
        return l

    def test_zeichnen_mit_bild_blittet_gespiegelt(self):
        f = _baue(f_text=Mock(zellhoehe=14, breite=Mock(return_value=20)))
        f.bild = (b"\x00" * (4 * 4 * 3), 4, 4)
        l = self._leinwand()
        f.zeichnen(l)
        args, kwargs = l.bgr_zeichnen.call_args
        self.assertTrue(kwargs["spiegeln"])
        self.assertEqual(args[1:3], (4, 4))

    def test_zeichnen_ohne_bild_zeigt_den_wartetext(self):
        f = _baue(f_text=Mock(zellhoehe=14, breite=Mock(return_value=20)))
        l = self._leinwand()
        f.zeichnen(l)
        l.bgr_zeichnen.assert_not_called()
        self.assertTrue(any("startet" in str(c.args[2]) for c in l.text.call_args_list))


if __name__ == "__main__":
    unittest.main()
