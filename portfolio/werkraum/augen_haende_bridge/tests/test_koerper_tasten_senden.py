"""Hände des Agenten: Ereignisse, Reihenfolge, Abbruch bei verlorenem Fokus/Not-Aus, nichts ohne Hotkey."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.tasten_senden import (
    KEYEVENTF_KEYUP,
    KEYEVENTF_UNICODE,
    Haende,
    VK_RETURN,
    enter_ereignisse,
    kombination_ereignisse,
    text_ereignisse,
)
from augen_haende_bridge.koerper.tastenkombi import Kombination


class EreignisTests(unittest.TestCase):
    def test_einfache_funktionstaste(self):
        self.assertEqual(kombination_ereignisse(Kombination(0, 0x7C)), [(0x7C, 0, 0), (0x7C, 0, KEYEVENTF_KEYUP)])

    def test_modifikatoren_runter_taste_hoch_modifikatoren_in_umgekehrter_reihenfolge(self):
        e = kombination_ereignisse(Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74))
        self.assertEqual(e, [(0x11, 0, 0), (0x12, 0, 0), (0x74, 0, 0), (0x74, 0, KEYEVENTF_KEYUP),
                             (0x12, 0, KEYEVENTF_KEYUP), (0x11, 0, KEYEVENTF_KEYUP)])

    def test_text_wird_unicode_gedrueckt_und_losgelassen(self):
        e = text_ereignisse("Hä")
        self.assertEqual(e, [(0, ord("H"), KEYEVENTF_UNICODE), (0, ord("H"), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP),
                             (0, ord("ä"), KEYEVENTF_UNICODE), (0, ord("ä"), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP)])

    def test_zeichen_ausserhalb_der_grundebene_werden_zu_zwei_einheiten(self):
        self.assertEqual(len(text_ereignisse("😀")), 4)

    def test_zeilenumbrueche_werden_zu_leerzeichen(self):
        self.assertEqual([x[1] for x in text_ereignisse("a\nb")][::2], [ord("a"), 32, ord("b")])

    def test_enter(self):
        self.assertEqual(enter_ereignisse(), [(VK_RETURN, 0, 0), (VK_RETURN, 0, KEYEVENTF_KEYUP)])


class Basis(unittest.TestCase):
    def haende(self, **ueber):
        self.gesendet = []
        self.zeit = {"t": 0.0}
        h = Haende(senden=lambda e: self.gesendet.append(list(e)) or len(e), uhr=lambda: self.zeit["t"],
                   schlafen=lambda dt: self.zeit.update(t=self.zeit["t"] + dt))
        return h

    def lauf(self, h, text="Hallo", kombi=Kombination(0, 0x7C), fokus=lambda: True, gesperrt=lambda: False):
        self.geschlossen = []
        return h.schreiben(text, kombi, feld_hat_fokus=fokus, gesperrt=gesperrt,
                           feld_schliessen=lambda: self.geschlossen.append(1))


class RuheTests(Basis):
    """Daniel tippt oder klickt: Der Schreibweg der Raute drückt dann nichts, denn die Tastenkombination holt sich den Fokus."""

    def lauf_ruhig(self, h, ruhig, markiere=lambda: None):
        self.geschlossen = []
        return h.schreiben("Hallo", Kombination(0, 0x7C), feld_hat_fokus=lambda: True, gesperrt=lambda: False,
                           feld_schliessen=lambda: self.geschlossen.append(1), ruhig=ruhig, eigene_markieren=markiere)

    def test_ohne_ruhe_wird_nichts_gedrueckt_und_der_grund_heisst_daniel_uebernimmt(self):
        h = self.haende()
        e = self.lauf_ruhig(h, ruhig=lambda: False)
        self.assertEqual((e.ok, e.grund), (False, "daniel_uebernimmt"))
        self.assertEqual(self.gesendet, [], "keine einzige Taste, auch nicht die Tastenkombination")
        self.assertGreaterEqual(self.zeit["t"], 6.0, "es wartet die volle Zeit auf Ruhe, bevor es aufgibt")

    def test_kommt_die_ruhe_nach_einer_weile_wird_geschrieben(self):
        h = self.haende()
        zaehler = {"n": 0}

        def ruhig():
            zaehler["n"] += 1
            return zaehler["n"] > 5
        e = self.lauf_ruhig(h, ruhig=ruhig)
        self.assertTrue(e.ok, e.grund)
        self.assertEqual(self.gesendet[0], kombination_ereignisse(Kombination(0, 0x7C)))

    def test_eigene_tasten_werden_vor_jedem_senden_markiert(self):
        h = self.haende()
        marken = []
        e = self.lauf_ruhig(h, ruhig=lambda: True, markiere=lambda: marken.append(len(self.gesendet)))
        self.assertTrue(e.ok)
        self.assertEqual(marken, list(range(len(self.gesendet))), "vor jedem einzelnen Senden eine Markierung")

    def test_not_aus_waehrend_des_wartens_bricht_ab(self):
        h = self.haende()
        self.geschlossen = []
        e = h.schreiben("Hallo", Kombination(0, 0x7C), feld_hat_fokus=lambda: True, gesperrt=lambda: True,
                        feld_schliessen=lambda: None, ruhig=lambda: False)
        self.assertEqual((e.ok, e.grund), (False, "gesperrt"))


class SchreibenTests(Basis):
    def test_reihenfolge_kombination_text_enter(self):
        h = self.haende()
        r = self.lauf(h)
        self.assertTrue(r.ok)
        self.assertEqual(self.gesendet[0], kombination_ereignisse(Kombination(0, 0x7C)))
        getippt = [e for gruppe in self.gesendet[1:-1] for e in gruppe]
        self.assertEqual(getippt, text_ereignisse("Hallo"))
        self.assertEqual(self.gesendet[-1], enter_ereignisse())

    def test_langer_text_geht_in_stuecken(self):
        h = self.haende()
        self.lauf(h, text="x" * 40)
        self.assertGreater(len(self.gesendet), 4)

    def test_ohne_hotkey_wird_nichts_gedrueckt(self):
        h = self.haende()
        r = self.lauf(h, kombi=None)
        self.assertEqual((r.ok, r.grund, self.gesendet), (False, "keine_tastenkombination", []))

    def test_leerer_text(self):
        h = self.haende()
        self.assertEqual(self.lauf(h, text="  ").grund, "leerer_text")
        self.assertEqual(self.gesendet, [])

    def test_not_aus_vorher_verhindert_alles(self):
        h = self.haende()
        r = self.lauf(h, gesperrt=lambda: True)
        self.assertEqual((r.ok, r.grund, self.gesendet), (False, "gesperrt", []))

    def test_oeffnet_sich_das_feld_nicht_wird_nur_die_kombination_gedrueckt(self):
        h = self.haende()
        r = self.lauf(h, fokus=lambda: False)
        self.assertEqual((r.ok, r.grund), (False, "feld_nicht_geoeffnet"))
        self.assertEqual(len(self.gesendet), 1)  # nur die Kombination, kein Text, kein Enter
        self.assertGreaterEqual(self.zeit["t"], 2.5)

    def test_feld_oeffnet_sich_spaeter(self):
        h = self.haende()
        aufrufe = {"n": 0}

        def fokus():
            aufrufe["n"] += 1
            return aufrufe["n"] > 5

        self.assertTrue(self.lauf(h, fokus=fokus).ok)

    def test_fokus_verloren_mitten_im_text_bricht_ab_und_druckt_nichts_mehr(self):
        h = self.haende()
        zaehler = {"n": 0}

        def fokus():
            zaehler["n"] += 1
            return zaehler["n"] <= 2  # Öffnen + erstes Stück ok, dann weg

        r = self.lauf(h, text="y" * 40, fokus=fokus)
        self.assertEqual((r.ok, r.grund), (False, "fokus_verloren"))
        self.assertEqual(self.geschlossen, [1])
        self.assertNotIn(enter_ereignisse(), self.gesendet)

    def test_not_aus_mitten_im_text_bricht_ab(self):
        h = self.haende()
        zaehler = {"n": 0}

        def gesperrt():
            zaehler["n"] += 1
            return zaehler["n"] > 3

        r = self.lauf(h, text="z" * 40, gesperrt=gesperrt)
        self.assertEqual((r.ok, r.grund), (False, "gesperrt"))
        self.assertEqual(self.geschlossen, [1])
        self.assertNotIn(enter_ereignisse(), self.gesendet)

    def test_fokus_weg_direkt_vor_dem_enter_drueckt_kein_enter(self):
        h = self.haende()
        zustand = {"aufrufe": 0}

        def fokus():
            zustand["aufrufe"] += 1
            return zustand["aufrufe"] < 3  # Öffnen und Textstück ok, beim letzten Check vor Enter weg

        r = self.lauf(h, text="ab", fokus=fokus)
        self.assertEqual(r.grund, "fokus_verloren")
        self.assertNotIn(enter_ereignisse(), self.gesendet)

    def test_sendinput_fehler_bei_der_kombination(self):
        h = Haende(senden=lambda e: 0, uhr=lambda: 0.0, schlafen=lambda dt: None)
        r = h.schreiben("x", Kombination(0, 0x7C), feld_hat_fokus=lambda: True, gesperrt=lambda: False,
                        feld_schliessen=lambda: None)
        self.assertEqual(r.grund, "sendinput_fehlgeschlagen")


if __name__ == "__main__":
    unittest.main()
