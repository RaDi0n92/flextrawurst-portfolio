"""Tests für koerper/nachricht_fenster.py: Banner-Geometrie und kontinuierliches Ausblenden, Ticker an der Raute.

Die Konstruktoren brauchen Windows oder Wine (echte Fenster, GDI-Schrift) — das prüft
`probes/koerper_smoketest.py`. Geometrie und Ausblendkurve sind freie Funktionen, die Timer-Logik läuft per
`object.__new__`-Fixture.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper.nachricht_fenster import (
    BANNER_DAUER_MS,
    TICKER_DAUER_MS,
    TIMER_ENDE,
    TIMER_TAKT,
    BannerFenster,
    TickerFenster,
    banner_alpha,
    banner_breite,
    banner_position,
    kuerzen,
    schneidet,
    ticker_position,
)

ZIEL = (0, 0, 1920, 1040)  # Arbeitsfläche ohne Taskleiste
RAUTE_OBEN_LINKS = (100, 100, 148, 148)
RAUTE_UNTEN_RECHTS = (1800, 950, 1848, 998)


class DauerTests(unittest.TestCase):
    def test_banner_6_6_s_und_box_an_der_raute_9_9_s(self) -> None:
        """Daniel 2026-10-01: Banner im Bildschirm 6,6 s mit Fade, Box neben der Raute 9,9 s (vorher 3,3 s und 6,6 s)."""
        self.assertEqual(BANNER_DAUER_MS, 6600)
        self.assertEqual(TICKER_DAUER_MS, 9900)


class BannerGeometrieTests(unittest.TestCase):
    def test_banner_ist_schmal_hoechstens_35_prozent_des_ziels(self) -> None:
        self.assertEqual(banner_breite(400, ZIEL), 420)
        self.assertEqual(banner_breite(5000, ZIEL), 672)

    def test_banner_sitzt_fast_mittig_mit_zug_zur_raute(self) -> None:
        breite, hoehe = 420, 50
        x_links, y_links = banner_position(ZIEL, RAUTE_OBEN_LINKS, breite, hoehe)
        x_rechts, y_rechts = banner_position(ZIEL, RAUTE_UNTEN_RECHTS, breite, hoehe)
        mitte_x = ZIEL[2] // 2 - breite // 2
        # Zug zur Raute: links/oben stehende Raute zieht nach links/oben, rechts/unten nach rechts/unten.
        self.assertLess(x_links, mitte_x)
        self.assertGreater(x_rechts, mitte_x)
        self.assertLess(y_links, y_rechts)
        # "fast mittig": höchstens gut ein Drittel des Wegs zur Raute.
        self.assertGreater(x_links, mitte_x - (mitte_x - RAUTE_OBEN_LINKS[0]) * 0.5)

    def test_banner_bleibt_innerhalb_des_zielbereichs(self) -> None:
        ziel = (500, 300, 900, 500)  # kleines gebundenes Programmfenster
        x, y = banner_position(ziel, (0, 0, 48, 48), 380, 60)
        self.assertGreaterEqual(x, ziel[0])
        self.assertGreaterEqual(y, ziel[1])
        self.assertLessEqual(x + 380, ziel[2])
        self.assertLessEqual(y + 60, ziel[3])


class AusblendkurveTests(unittest.TestCase):
    def test_voller_kontrast_am_anfang_unsichtbar_nach_3_3_s(self) -> None:
        self.assertEqual(banner_alpha(0), 255)
        self.assertEqual(banner_alpha(BANNER_DAUER_MS), 0)
        self.assertEqual(banner_alpha(BANNER_DAUER_MS + 500), 0)

    def test_kontinuierlich_abnehmend(self) -> None:
        werte = [banner_alpha(t) for t in range(0, BANNER_DAUER_MS + 1, 33)]
        self.assertTrue(all(a >= b for a, b in zip(werte, werte[1:])))
        self.assertGreater(len(set(werte)), 50)  # viele Zwischenstufen, kein harter Sprung
        self.assertAlmostEqual(banner_alpha(BANNER_DAUER_MS // 2), 128, delta=1)


class TickerGeometrieTests(unittest.TestCase):
    def test_ticker_sitzt_direkt_rechts_neben_der_raute_auf_ihrer_mitte(self) -> None:
        self.assertEqual(ticker_position(RAUTE_OBEN_LINKS, 20), (154, 114))

    def test_am_rechten_rand_geht_die_box_links_der_raute_auf(self) -> None:
        x, y = ticker_position(RAUTE_UNTEN_RECHTS, 120, 320, ZIEL)
        self.assertEqual(x, RAUTE_UNTEN_RECHTS[0] - 6 - 320)
        self.assertLessEqual(x + 320, ZIEL[2])

    def test_hohe_box_bleibt_unten_und_oben_im_bildschirm(self) -> None:
        _, y = ticker_position(RAUTE_UNTEN_RECHTS, 300, 320, ZIEL)
        self.assertLessEqual(y + 300, ZIEL[3])
        _, y_oben = ticker_position((100, 0, 148, 30), 300, 320, ZIEL)
        self.assertGreaterEqual(y_oben, ZIEL[1])

    def test_box_neben_der_raute_ohne_grenzen_wie_bisher(self) -> None:
        self.assertEqual(ticker_position(RAUTE_UNTEN_RECHTS, 20, 320), (1854, 964))


class UeberlappungTests(unittest.TestCase):
    def test_banner_weicht_der_box_aus_statt_sie_zu_ueberdecken(self) -> None:
        raute = (900, 500, 948, 548)
        breite, hoehe = 400, 300
        box = (954, 420, 1254, 580)  # direkt neben der Raute, genau dort, wo das Banner sonst landen würde
        ohne = banner_position(ZIEL, raute, breite, hoehe)
        mit = banner_position(ZIEL, raute, breite, hoehe, [box])
        self.assertTrue(schneidet((*ohne, ohne[0] + breite, ohne[1] + hoehe), box))  # Voraussetzung: es würde überlappen
        rechteck = (mit[0], mit[1], mit[0] + breite, mit[1] + hoehe)
        self.assertFalse(schneidet(rechteck, box))
        self.assertFalse(schneidet(rechteck, raute))
        self.assertTrue(ZIEL[0] <= rechteck[0] and rechteck[2] <= ZIEL[2] and ZIEL[1] <= rechteck[1] and rechteck[3] <= ZIEL[3])

    def test_banner_ohne_hindernis_bleibt_wo_es_war(self) -> None:
        raute = (100, 100, 148, 148)
        self.assertEqual(banner_position(ZIEL, raute, 400, 300, [(1700, 900, 1900, 1000)]), banner_position(ZIEL, raute, 400, 300))

    def test_box_weicht_dem_banner_aus(self) -> None:
        raute = (900, 500, 948, 548)
        banner = (954, 400, 1354, 700)  # steht genau rechts neben der Raute
        x, y = ticker_position(raute, 120, 320, ZIEL, [banner])
        box = (x, y, x + 320, y + 120)
        self.assertFalse(schneidet(box, banner))
        self.assertFalse(schneidet(box, raute))

    def test_box_ueberdeckt_die_raute_nie_auch_nicht_am_rand(self) -> None:
        raute = (1800, 950, 1848, 998)
        x, y = ticker_position(raute, 120, 320, ZIEL, [])
        self.assertFalse(schneidet((x, y, x + 320, y + 120), raute))

    def test_mehrere_hindernisse_alles_bleibt_frei(self) -> None:
        raute = (900, 500, 948, 548)
        hindernisse = [(954, 420, 1254, 580), (400, 300, 880, 760)]
        mit = banner_position(ZIEL, raute, 380, 260, hindernisse)
        rechteck = (mit[0], mit[1], mit[0] + 380, mit[1] + 260)
        self.assertFalse(any(schneidet(rechteck, h) for h in [*hindernisse, raute]))


class KuerzenTests(unittest.TestCase):
    messen = staticmethod(lambda t: len(t) * 7)

    def test_kurze_texte_bleiben_unveraendert(self) -> None:
        self.assertEqual(kuerzen(["a", "b"], 3, 100, self.messen), ["a", "b"])

    def test_zu_lange_texte_enden_mit_auslassung_und_passen_in_die_breite(self) -> None:
        zeilen = [f"zeile nummer {i} voll" for i in range(20)]
        ergebnis = kuerzen(zeilen, 4, 140, self.messen)
        self.assertEqual(len(ergebnis), 4)
        self.assertEqual(ergebnis[:3], zeilen[:3])
        self.assertTrue(ergebnis[3].endswith(" …"))
        self.assertTrue(all(self.messen(z) <= 140 for z in ergebnis))

    def test_genau_das_maximum_wird_nicht_gekuerzt(self) -> None:
        self.assertEqual(kuerzen(["a"] * 6, 6, 100, self.messen), ["a"] * 6)


class GatingTests(unittest.TestCase):
    def test_konstruktoren_verlangen_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            BannerFenster(text="x", farbe_hex="#FFD600", ziel_rechteck=ZIEL, raute_rechteck=RAUTE_OBEN_LINKS,
                          jetzt_ms=lambda: 0)
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            TickerFenster(text="x", farbe_hex="#FFD600", raute_rechteck=RAUTE_OBEN_LINKS)


def _banner(**overrides) -> BannerFenster:
    f = object.__new__(BannerFenster)
    f.text = "Shader kompiliert!"
    f.start_ms = 1000
    f._jetzt_ms = Mock(return_value=1000)
    f._geschlossen = Mock()
    f.f_text = Mock()
    f.hwnd = 1
    f.setze_deckkraft = Mock()
    f.stoppe_timer = Mock()
    f.schliessen = Mock()
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class BannerTimerTests(unittest.TestCase):
    def test_jeder_takt_setzt_die_deckkraft_nach_der_kurve(self) -> None:
        f = _banner(_jetzt_ms=Mock(return_value=1000 + 1650))
        f.bei_timer(TIMER_TAKT)
        f.setze_deckkraft.assert_called_once_with(banner_alpha(1650))
        f.schliessen.assert_not_called()

    def test_nach_3_3_s_schliesst_sich_das_banner_selbst(self) -> None:
        f = _banner(_jetzt_ms=Mock(return_value=1000 + BANNER_DAUER_MS))
        f.bei_timer(TIMER_TAKT)
        f.stoppe_timer.assert_called_once_with(TIMER_TAKT)
        f._geschlossen.assert_called_once_with()
        f.schliessen.assert_called_once_with()


def _ticker(**overrides) -> TickerFenster:
    f = object.__new__(TickerFenster)
    f.text = "Shader kompiliert!"
    f._geschlossen = Mock()
    f.f_text = Mock()
    f.hwnd = 2
    f.hoehe, f.breite, f._grenzen, f._meiden = 20, 100, None, None
    f.verschiebe = Mock()
    f.stoppe_timer = Mock()
    f.schliessen = Mock()
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class TickerTests(unittest.TestCase):
    def test_ticker_folgt_der_verschobenen_raute(self) -> None:
        f = _ticker()
        f.an_raute((300, 300, 348, 348))
        f.verschiebe.assert_called_once_with(354, 314)

    def test_nach_6_6_s_schliesst_sich_der_ticker_selbst(self) -> None:
        f = _ticker()
        f.bei_timer(TIMER_ENDE)
        f.stoppe_timer.assert_called_once_with(TIMER_ENDE)
        f._geschlossen.assert_called_once_with()
        f.schliessen.assert_called_once_with()

    def test_bei_zerstoert_gibt_die_schrift_frei(self) -> None:
        f = _ticker()
        schrift = f.f_text
        f.bei_zerstoert()
        schrift.freigeben.assert_called_once_with()
        self.assertIsNone(f.f_text)


if __name__ == "__main__":
    unittest.main()
