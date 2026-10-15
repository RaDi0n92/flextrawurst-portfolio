"""R121: Elemente im Zielfenster (eingerahmt, wandern mit, minimieren mit, verschwinden beim Schließen) — Logik mit Attrappen, ohne Windows."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper.ziel_halter import ORT_DESKTOP, ORT_ZIEL, ZielHalter, klemmen


class FakeFenster:
    def __init__(self, x, y, b=100, h=60):
        self.x, self.y, self.b, self.h = x, y, b, h
        self.sichtbar = True
        self.log = []

    def rechteck(self):
        return (self.x, self.y, self.x + self.b, self.y + self.h)

    def verschiebe(self, x, y, b=None, h=None):
        self.x, self.y = x, y
        self.log.append((x, y))

    def verberge(self):
        self.sichtbar = False

    def zeige(self, aktivieren=True):
        self.sichtbar = True


class FakeWelt:
    """Das Zielfenster: Rechteck, minimiert, geschlossen."""

    def __init__(self, rect=(200, 100, 800, 500)):
        self.rect, self.minimiert, self.da = rect, False, True

    def zustand(self, hwnd):
        if not self.da:
            return False, False, None
        return True, self.minimiert, (None if self.minimiert else self.rect)


def bauen(rect=(200, 100, 800, 500), hwnd=77):
    welt = FakeWelt(rect)
    ziel = {"hwnd": hwnd}
    gemeldet = []
    halter = ZielHalter(zustand=welt.zustand, melden=lambda: gemeldet.append(1))
    fenster = FakeFenster(300, 200)
    halter.anmelden("raute:t-1", fenster, lambda: ziel["hwnd"])
    return halter, fenster, welt, ziel, gemeldet


class KlemmenTests(unittest.TestCase):
    def test_innerhalb_bleibt_wie_es_ist(self):
        self.assertEqual(klemmen((300, 200), (100, 60), (200, 100, 800, 500)), (300, 200))

    def test_rechts_unten_hinaus_wird_zurueckgeholt(self):
        self.assertEqual(klemmen((790, 490), (100, 60), (200, 100, 800, 500)), (700, 440))

    def test_links_oben_hinaus_wird_zurueckgeholt(self):
        self.assertEqual(klemmen((10, 10), (100, 60), (200, 100, 800, 500)), (200, 100))

    def test_groesser_als_das_ziel_sitzt_an_der_oberen_linken_ecke(self):
        self.assertEqual(klemmen((0, 0), (900, 700), (200, 100, 800, 500)), (200, 100))


class OrtTests(unittest.TestCase):
    def test_standard_ist_desktop_und_nichts_wird_bewegt(self):
        halter, fenster, welt, _, _ = bauen()
        welt.rect = (0, 0, 100, 100)
        halter.tick()
        self.assertEqual((halter.ort("raute:t-1"), fenster.log), (ORT_DESKTOP, []))

    def test_ohne_fenster_ziel_geht_es_nicht_und_sagt_warum(self):
        halter, _, _, ziel, _ = bauen()
        ziel["hwnd"] = None
        fehler = halter.setze_ort("raute:t-1", ORT_ZIEL)
        self.assertIn("Kein einzelnes Fenster", fehler)
        self.assertEqual(halter.ort("raute:t-1"), ORT_DESKTOP)

    def test_ins_ziel_stellen_merkt_die_stelle_im_fenster(self):
        halter, fenster, welt, _, _ = bauen()
        self.assertIsNone(halter.setze_ort("raute:t-1", ORT_ZIEL))
        self.assertEqual(halter.elemente["raute:t-1"].rel, (100, 100))  # (300,200) minus (200,100)
        self.assertEqual((fenster.x, fenster.y), (300, 200))

    def test_element_ausserhalb_des_ziels_wird_beim_hineinstellen_eingerahmt(self):
        halter, fenster, welt, _, _ = bauen()
        fenster.x, fenster.y = 50, 50  # auf dem Desktop links oben, außerhalb des Zielfensters
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        self.assertEqual((fenster.x, fenster.y), (200, 100))

    def test_zurueck_auf_den_desktop_laesst_es_stehen_und_bewegt_nichts_mehr(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        halter.setze_ort("raute:t-1", ORT_DESKTOP)
        welt.rect = (0, 0, 400, 300)
        halter.tick()
        self.assertEqual((fenster.x, fenster.y), (300, 200))


class MitwandernTests(unittest.TestCase):
    def test_ziel_wird_verschoben_element_geht_an_derselben_stelle_mit(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.rect = (400, 150, 1000, 550)  # um (200, 50) verschoben
        halter.tick()
        self.assertEqual((fenster.x, fenster.y), (500, 250))

    def test_daniel_verschiebt_das_element_neue_stelle_wird_gemerkt(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        fenster.x, fenster.y = 350, 250  # Daniel zieht es
        halter.tick()
        self.assertEqual(halter.elemente["raute:t-1"].rel, (150, 150))
        welt.rect = (300, 100, 900, 500)
        halter.tick()
        self.assertEqual((fenster.x, fenster.y), (450, 250))

    def test_ziehen_aus_dem_ziel_heraus_wird_zurueckgeholt(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        fenster.x, fenster.y = 1500, 900
        halter.tick()
        self.assertEqual((fenster.x + fenster.b, fenster.y + fenster.h), (800, 500))  # unten rechts im Ziel

    def test_ziel_wird_kleiner_element_bleibt_drin(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.rect = (200, 100, 450, 250)
        halter.tick()
        self.assertTrue(200 <= fenster.x and fenster.x + fenster.b <= 450 and 100 <= fenster.y and fenster.y + fenster.h <= 250)


class MinimierenUndSchliessenTests(unittest.TestCase):
    def test_minimieren_versteckt_das_element_und_wiederherstellen_bringt_es_zurueck(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.minimiert = True
        halter.tick()
        self.assertFalse(fenster.sichtbar)
        self.assertTrue(halter.versteckt("raute:t-1"))
        welt.minimiert = False
        welt.rect = (250, 120, 850, 520)  # beim Zurückkommen an anderer Stelle
        halter.tick()
        self.assertTrue(fenster.sichtbar)
        self.assertEqual((fenster.x, fenster.y), (350, 220))  # gemerkte Stelle im Fenster

    def test_schliessen_laesst_das_element_verschwinden_es_geht_nicht_auf_den_desktop(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.da = False
        halter.tick()
        self.assertFalse(fenster.sichtbar)
        self.assertEqual(halter.ort("raute:t-1"), ORT_ZIEL)  # die Wahl bleibt; ein neues Ziel holt es wieder

    def test_minimiert_bewegt_das_element_nicht(self):
        halter, fenster, welt, _, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.minimiert = True
        fenster.log.clear()
        halter.tick()
        halter.tick()
        self.assertEqual(fenster.log, [])

    def test_vom_nutzer_ausgeblendetes_element_kommt_nicht_von_selbst_zurueck(self):
        halter, fenster, welt, _, _ = bauen()
        halter.elemente["raute:t-1"].nutzer_verborgen = lambda: True
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.minimiert = True
        halter.tick()
        welt.minimiert = False
        fenster.sichtbar = False
        halter.tick()
        self.assertFalse(fenster.sichtbar)


class ZielWechselTests(unittest.TestCase):
    def test_wird_ein_ganzer_desktop_gebunden_steht_das_element_wieder_auf_dem_desktop(self):
        halter, fenster, welt, ziel, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        welt.minimiert = True
        halter.tick()
        self.assertFalse(fenster.sichtbar)
        ziel["hwnd"] = None
        halter.tick()
        self.assertEqual(halter.ort("raute:t-1"), ORT_DESKTOP)
        self.assertTrue(fenster.sichtbar)

    def test_anderes_zielfenster_wird_sofort_gefolgt(self):
        halter, fenster, welt, ziel, _ = bauen()
        halter.setze_ort("raute:t-1", ORT_ZIEL)
        ziel["hwnd"] = 88
        welt.rect = (1000, 500, 1600, 900)
        halter.tick()
        halter.tick()
        self.assertTrue(1000 <= fenster.x and fenster.x + fenster.b <= 1600)

    def test_abmelden_entfernt_das_element(self):
        halter, fenster, welt, _, _ = bauen()
        halter.abmelden("raute:t-1")
        self.assertEqual(halter.ort("raute:t-1"), ORT_DESKTOP)
        halter.tick()


if __name__ == "__main__":
    unittest.main()
