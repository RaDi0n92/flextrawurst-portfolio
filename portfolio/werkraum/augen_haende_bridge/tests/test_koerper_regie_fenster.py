import unittest
from unittest import mock

from augen_haende_bridge.koerper import regie_fenster as r
from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w


def fenster():
    f = object.__new__(r.RegieFenster)
    f.agent_name, f.agent_farbe = "kein Agent", 0
    f.mikrofon, f.kamera, f.notaus, f.hinweis = "aus", "aus", False, ""
    f._knopf_unten = None
    f.aufrufe = []
    f._aufrufe = {k: (lambda k=k: f.aufrufe.append(k)) for k in ("agent", "mikrofon", "kamera", "notaus")}
    f._regie_menue = lambda x, y: f.aufrufe.append(("menue", x, y))
    f.neu_zeichnen = lambda: None
    f.erfasse_maus = lambda: None
    f.gib_maus_frei = lambda: None
    f.rechteck = lambda: (100, 200, 100 + r.BREITE, 200 + r.HOEHE)
    f.deckkraft = 255
    f.setze_deckkraft = lambda alpha: setattr(f, 'deckkraft', alpha)
    return f


class LayoutTest(unittest.TestCase):
    def test_knoepfe_ueberlappen_nicht_und_passen_ins_fenster(self):
        rects = list(r.knopf_rechtecke().values())
        for i, a in enumerate(rects):
            self.assertTrue(0 <= a[0] < a[2] <= r.BREITE and 0 <= a[1] < a[3] <= r.HOEHE)
            for b in rects[i + 1:]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    def test_knopf_bei_trifft_mitte_jedes_knopfes(self):
        for name, (l, o, ri, u) in r.knopf_rechtecke().items():
            self.assertEqual(r.knopf_bei((l + ri) // 2, (o + u) // 2), name)
        self.assertIsNone(r.knopf_bei(-1, -1))

    def test_position_unten_links(self):
        self.assertEqual(r.leiste_position((0, 0, 1000, 800)), (12, 800 - r.HOEHE - 12))

    def test_farbe_und_beschriftung(self):
        self.assertEqual(r.knopf_farbe("kamera", "ein", False), stil.FARBE_OK)
        self.assertEqual(r.knopf_farbe("kamera", "fehler", False), stil.FARBE_FEHLER)
        self.assertEqual(r.knopf_farbe("mikrofon", "aus", False), stil.FARBE_KNOPF)
        self.assertEqual(r.knopf_beschriftung("notaus", True), "frei")
        self.assertEqual(r.knopf_beschriftung("notaus", False), "STOP")

    def test_regiespruecher_vollstaendig(self):
        self.assertEqual(len(r.REGIESPRUECHE), 14)
        self.assertEqual(len(set(r.REGIESPRUECHE)), 14)

    def test_kreis(self):
        pts = r.kreis(50, 50, 10)
        self.assertEqual(len(pts), 28)
        self.assertIn((60, 50), pts)


class VerschiebenUndDeckkraftTest(unittest.TestCase):
    def test_griff_oben_verschiebt_der_rest_ist_bedienflaeche(self):
        f = fenster()
        self.assertEqual(f.treffer(100 + 30, 200 + 3), w.HTCAPTION)
        self.assertEqual(f.treffer(100 + 30, 200 + r.GRIFF_H + 5), w.HTCLIENT)
        self.assertEqual(f.treffer(100 + 30, 200 + r.HOEHE - 3), w.HTCLIENT)

    def test_klick_auf_den_griff_loest_nichts_aus(self):
        f = fenster()
        x, y = 30, 3
        f.bei_maus_runter(x, y, 0)
        f.bei_maus_hoch(x, y, 0)
        self.assertEqual(f.aufrufe, [])

    def test_prozent_knopf_schaltet_die_deckkraft_weiter(self):
        f = fenster()
        l, o, ri, u = r.knopf_rechtecke()["deckkraft"]
        x, y = (l + ri) // 2, (o + u) // 2
        werte = []
        for _ in range(5):
            f.bei_maus_runter(x, y, 0)
            f.bei_maus_hoch(x, y, 0)
            werte.append(f.deckkraft_prozent())
        self.assertEqual(werte, [34, 50, 75, 100, 34])
        self.assertEqual(f.aufrufe, [])  # ein Prozent-Klick ist kein Regie-Befehl

    def test_leiste_liegt_ganz_in_der_arbeitsflaeche(self):
        x, y = r.leiste_position((0, 0, 1000, 800))
        self.assertTrue(y >= 0 and y + r.HOEHE <= 800 and x + r.BREITE <= 1000)


class MausTest(unittest.TestCase):
    def mitte(self, name):
        l, o, ri, u = r.knopf_rechtecke()[name]
        return (l + ri) // 2, (o + u) // 2

    def test_klick_loest_erst_beim_loslassen_am_selben_knopf_aus(self):
        f = fenster()
        x, y = self.mitte("kamera")
        f.bei_maus_runter(x, y, 0)
        self.assertEqual(f.aufrufe, [])
        f.bei_maus_hoch(x, y, 0)
        self.assertEqual(f.aufrufe, ["kamera"])

    def test_loslassen_woanders_loest_nichts_aus(self):
        f = fenster()
        f.bei_maus_runter(*self.mitte("kamera"), 0)
        f.bei_maus_hoch(*self.mitte("mikrofon"), 0)
        self.assertEqual(f.aufrufe, [])

    def test_regie_oeffnet_menue_rechts_am_knopf(self):
        f = fenster()
        x, y = self.mitte("regie")
        f.bei_maus_runter(x, y, 0)
        f.bei_maus_hoch(x, y, 0)
        rect = r.knopf_rechtecke()["regie"]
        self.assertEqual(f.aufrufe, [("menue", 100 + rect[2], 200 + rect[1])])

    def test_notaus_und_agent(self):
        f = fenster()
        for name in ("notaus", "agent"):
            x, y = self.mitte(name)
            f.bei_maus_runter(x, y, 0)
            f.bei_maus_hoch(x, y, 0)
        self.assertEqual(f.aufrufe, ["notaus", "agent"])

    def test_setze_und_zustand(self):
        f = fenster()
        f.setze(agent_name="Nova", mikrofon="ein", kamera="fehler", notaus=True)
        self.assertEqual((f.agent_name, f.zustand_von("mikrofon"), f.zustand_von("kamera"), f.notaus),
                         ("Nova", "ein", "fehler", True))
        self.assertEqual(f.zustand_von("regie"), "aus")


if __name__ == "__main__":
    unittest.main()


class ZustandswortTests(unittest.TestCase):
    def test_mik_und_cam_zeigen_ihren_zustand_auch_als_wort(self):
        from augen_haende_bridge.koerper.regie_fenster import zustandswort
        self.assertEqual([zustandswort("mikrofon", z) for z in ("aus", "startet", "ein", "fehler")], ["aus", "…", "an", "Fehler"])
        self.assertEqual(zustandswort("kamera", "ein"), "an")

    def test_regie_und_stop_haben_kein_zustandswort(self):
        from augen_haende_bridge.koerper.regie_fenster import zustandswort
        self.assertEqual((zustandswort("regie", "ein"), zustandswort("notaus", "fehler")), ("", ""))

    def test_unbekannter_zustand_ergibt_kein_wort(self):
        from augen_haende_bridge.koerper.regie_fenster import zustandswort
        self.assertEqual(zustandswort("mikrofon", "komisch"), "")
