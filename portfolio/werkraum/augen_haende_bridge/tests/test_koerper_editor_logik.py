"""G08: Bedienlogik des Zeichen-Editors — Werkzeuge, Auswahl, Ziehen, Skalieren, Gummiband, Text, Tasten, Empfänger."""

from __future__ import annotations

import io
import unittest

from PIL import Image

from augen_haende_bridge.koerper.editor_logik import FARBEN, Editor, VK_DELETE, VK_ESC, VK_NEXT, VK_PRIOR
from augen_haende_bridge.koerper.objekte import Dokument, Objekt

B, H = 200, 100


def baue():
    dok = Dokument("t")
    gemeldet = {"geaendert": 0, "beendet": 0}
    ed = Editor(dok, lambda: (B, H), bei_aenderung=lambda: gemeldet.__setitem__("geaendert", gemeldet["geaendert"] + 1),
                bei_beenden=lambda: gemeldet.__setitem__("beendet", gemeldet["beendet"] + 1), agenten=lambda: [("A", "Codex"), ("B", "Claude")])
    return ed, dok, gemeldet


def ziehe(ed, a, b, schritte=4, umschalt=False):
    ed.maus_runter(*a, umschalt=umschalt)
    for i in range(1, schritte + 1):
        ed.maus_bewegt(a[0] + (b[0] - a[0]) * i / schritte, a[1] + (b[1] - a[1]) * i / schritte)
    ed.maus_hoch(*b)


class ZeichnenTests(unittest.TestCase):
    def test_freihand_sammelt_punkte_und_ist_ein_befehl(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("freihand")
        ziehe(ed, (20, 20), (120, 60), schritte=8)
        (o,) = dok.objekte.values()
        self.assertEqual(o.art, "freihand")
        self.assertGreaterEqual(len(o.punkte), 8)
        self.assertEqual(dok.version, 1)
        ed.rueckgaengig()
        self.assertEqual(len(dok.objekte), 0)

    def test_formen_haben_anfang_und_ende_aus_den_pixeln(self):
        for werkzeug in ("linie", "pfeil", "rechteck", "kreis"):
            with self.subTest(werkzeug):
                ed, dok, _ = baue()
                ed.werkzeug_setzen(werkzeug)
                ziehe(ed, (20, 10), (100, 50))
                (o,) = dok.objekte.values()
                self.assertEqual(o.art, werkzeug)
                self.assertEqual([tuple(round(c, 3) for c in p) for p in o.punkte], [(0.1, 0.1), (0.5, 0.5)])

    def test_ein_klick_ohne_ziehen_malt_keine_form_aber_einen_punkt_mit_freihand(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("rechteck")
        ed.maus_runter(50, 50)
        ed.maus_hoch(50, 50)
        self.assertEqual(len(dok.objekte), 0)
        ed.werkzeug_setzen("freihand")
        ed.maus_runter(50, 50)
        ed.maus_hoch(50, 50)
        self.assertEqual(len(dok.objekte), 1)

    def test_farbe_staerke_und_marker(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("marker")
        ed.farbe_setzen(FARBEN[3])
        ed.staerke_setzen(14)
        ziehe(ed, (10, 10), (100, 10))
        (o,) = dok.objekte.values()
        self.assertEqual((o.art, o.farbe, o.staerke), ("marker", FARBEN[3], 14))

    def test_esc_waehrend_des_zeichnens_bricht_ab_ohne_den_modus_zu_verlassen(self):
        ed, dok, g = baue()
        ed.werkzeug_setzen("rechteck")
        ed.maus_runter(20, 20)
        ed.maus_bewegt(80, 60)
        ed.taste(VK_ESC)
        ed.maus_hoch(80, 60)
        self.assertEqual((len(dok.objekte), g["beendet"]), (0, 0))

    def test_esc_ohne_etwas_abzubrechen_verlaesst_den_modus(self):
        ed, dok, g = baue()
        ed.taste(VK_ESC)
        self.assertEqual(g["beendet"], 1)

    def test_neue_objekte_tragen_die_gewaehlten_empfaenger_und_den_bildschirmschalter(self):
        ed, dok, _ = baue()
        ed.bildschirm_umschalten()  # nicht mehr auf dem Bildschirm
        ed.empfaenger_umschalten("A")
        ed.werkzeug_setzen("kreis")
        ziehe(ed, (20, 20), (100, 60))
        (o,) = dok.objekte.values()
        self.assertEqual((o.bildschirm, o.empfaenger), (False, ("A",)))
        self.assertEqual(ed.empfaenger_stand(), (False, ("A",)))


class TextTests(unittest.TestCase):
    def tippe(self, ed, text):
        for c in text:
            ed.zeichen(ord(c))

    def test_klick_tippen_enter_ergibt_ein_textobjekt(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "Hallo äö")
        self.assertEqual(len(dok.objekte), 0)  # noch nicht festgeschrieben
        ed.zeichen(0x0D)
        (o,) = dok.objekte.values()
        self.assertEqual((o.art, o.text), ("text", "Hallo äö"))

    def test_rueckschritt_loescht_und_leerer_text_wird_nicht_angelegt(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "ab")
        ed.zeichen(0x08)
        ed.zeichen(0x08)
        ed.zeichen(0x0D)
        self.assertEqual(len(dok.objekte), 0)

    def test_esc_bricht_den_text_ab_und_laesst_den_modus_offen(self):
        ed, dok, g = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "weg")
        ed.taste(VK_ESC)
        self.assertEqual((len(dok.objekte), g["beendet"], ed.text_objekt), (0, 0, None))

    def test_neuer_klick_schreibt_den_text_fest(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "eins")
        ed.maus_runter(100, 60)
        self.tippe(ed, "zwei")
        ed.zeichen(0x0D)
        self.assertEqual(sorted(o.text for o in dok.objekte.values()), ["eins", "zwei"])

    def test_text_bearbeiten_per_doppelklick_aendert_den_text_als_ein_befehl(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "alt")
        ed.zeichen(0x0D)
        ed.werkzeug_setzen("auswahl")
        ed.maus_runter(41, 31, doppelt=True)
        self.assertIsNotNone(ed.text_objekt)
        self.tippe(ed, "er")
        ed.zeichen(0x0D)
        self.assertEqual([o.text for o in dok.objekte.values()], ["alter"])
        ed.rueckgaengig()
        self.assertEqual([o.text for o in dok.objekte.values()], ["alt"])

    def test_text_leer_machen_loescht_das_objekt(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.tippe(ed, "x")
        ed.zeichen(0x0D)
        ed.werkzeug_setzen("auswahl")
        ed.maus_runter(41, 31, doppelt=True)
        ed.zeichen(0x08)
        ed.zeichen(0x0D)
        self.assertEqual(len(dok.objekte), 0)

    def test_tasten_waehrend_des_tippens_loesen_keine_befehle_aus(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("text")
        ed.maus_runter(40, 30)
        self.assertFalse(ed.taste(VK_DELETE))


class AuswahlTests(unittest.TestCase):
    def zwei(self):
        ed, dok, g = baue()
        ed.werkzeug_setzen("rechteck")
        ziehe(ed, (20, 20), (60, 50))
        ziehe(ed, (100, 20), (140, 50))
        ed.werkzeug_setzen("auswahl")
        a, b = sorted(dok.objekte, key=lambda i: dok.objekte[i].punkte[0][0])
        return ed, dok, a, b

    def test_klick_waehlt_und_leere_stelle_hebt_auf(self):
        ed, dok, a, b = self.zwei()
        ed.maus_runter(20, 35)  # auf dem linken Rand von a
        ed.maus_hoch(20, 35)
        self.assertEqual(ed.auswahl, {a})
        ed.maus_runter(10, 90)
        ed.maus_hoch(10, 90)
        self.assertEqual(ed.auswahl, set())

    def test_umschalt_klick_fuegt_hinzu_und_nimmt_wieder_weg(self):
        ed, dok, a, b = self.zwei()
        ed.maus_runter(20, 35); ed.maus_hoch(20, 35)
        ed.maus_runter(100, 35, umschalt=True); ed.maus_hoch(100, 35)
        self.assertEqual(ed.auswahl, {a, b})
        ed.maus_runter(100, 35, umschalt=True); ed.maus_hoch(100, 35)
        self.assertEqual(ed.auswahl, {a})

    def test_gummiband_waehlt_vollstaendig_enthaltene(self):
        ed, dok, a, b = self.zwei()
        ed.maus_runter(5, 5)
        ed.maus_bewegt(70, 60)
        ed.maus_hoch(70, 60)
        self.assertEqual(ed.auswahl, {a})
        ed.maus_runter(5, 5)
        ed.maus_bewegt(190, 90)
        ed.maus_hoch(190, 90)
        self.assertEqual(ed.auswahl, {a, b})

    def test_ziehen_verschiebt_als_ein_befehl_und_rueckgaengig_stellt_her(self):
        ed, dok, a, b = self.zwei()
        v = dok.version
        ziehe(ed, (20, 35), (40, 55))
        self.assertAlmostEqual(dok.objekte[a].punkte[0][0], 0.2)  # 0.1 + 20/200
        self.assertAlmostEqual(dok.objekte[a].punkte[0][1], 0.4)  # 0.2 + 20/100
        self.assertEqual(dok.version, v + 1)
        ed.rueckgaengig()
        self.assertAlmostEqual(dok.objekte[a].punkte[0][0], 0.1)

    def test_klick_ohne_ziehen_aendert_das_dokument_nicht(self):
        ed, dok, a, b = self.zwei()
        v = dok.version
        ed.maus_runter(20, 35)
        ed.maus_hoch(20, 35)
        self.assertEqual(dok.version, v)

    def test_gruppe_wird_gemeinsam_gewaehlt_und_bewegt(self):
        ed, dok, a, b = self.zwei()
        dok.gruppieren([a, b])
        ed.maus_runter(20, 35)
        ed.maus_hoch(20, 35)
        self.assertEqual(ed.auswahl, {a, b})
        ziehe(ed, (20, 35), (30, 35))
        self.assertAlmostEqual(dok.objekte[b].punkte[0][0], 0.55)

    def test_skaliergriff_vergroessert_um_die_gegenueberliegende_ecke(self):
        ed, dok, a, b = self.zwei()
        ed.maus_runter(20, 35); ed.maus_hoch(20, 35)
        # a: (0.1,0.2)-(0.3,0.5) → Pixel (20,20)-(60,50); Griff unten rechts bei (60,50) ziehen nach (100,80)
        ziehe(ed, (60, 50), (100, 80))
        (x1, y1), (x2, y2) = dok.objekte[a].punkte
        self.assertEqual((round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)), (0.1, 0.2, 0.5, 0.8))
        ed.rueckgaengig()
        self.assertEqual(round(dok.objekte[a].punkte[1][0], 3), 0.3)

    def test_skalieren_auf_null_oder_umgekehrt_wird_ignoriert(self):
        ed, dok, a, b = self.zwei()
        ed.maus_runter(20, 35); ed.maus_hoch(20, 35)
        ziehe(ed, (60, 50), (10, 10))  # über die Gegenecke hinaus
        self.assertEqual(round(dok.objekte[a].punkte[1][0], 3), 0.3)

    def test_loeschen_gruppieren_ordnung_duplizieren_per_tasten(self):
        ed, dok, a, b = self.zwei()
        ed.taste(ord("A"), strg=True)
        self.assertEqual(ed.auswahl, {a, b})
        ed.taste(ord("G"), strg=True)
        self.assertEqual(dok.objekte[a].gruppe, dok.objekte[b].gruppe)
        ed.taste(ord("G"), strg=True, umschalt=True)
        self.assertIsNone(dok.objekte[a].gruppe)
        ed.auswahl = {a}
        ed.taste(VK_PRIOR, strg=True)
        self.assertEqual([o.id for o in dok.sortiert()][-1], a)
        ed.taste(VK_NEXT, strg=True)
        self.assertEqual([o.id for o in dok.sortiert()][0], a)
        ed.taste(ord("D"), strg=True)
        self.assertEqual(len(dok.objekte), 3)
        ed.taste(VK_DELETE)
        self.assertEqual(len(dok.objekte), 2)
        ed.taste(ord("Z"), strg=True)
        self.assertEqual(len(dok.objekte), 3)
        ed.taste(ord("Y"), strg=True)
        self.assertEqual(len(dok.objekte), 2)

    def test_ausblenden_und_alle_einblenden(self):
        ed, dok, a, b = self.zwei()
        ed.auswahl = {a}
        ed.ausblenden()
        self.assertFalse(dok.objekte[a].sichtbar)
        self.assertEqual(ed.auswahl, set())
        ed.alle_einblenden()
        self.assertTrue(dok.objekte[a].sichtbar)

    def test_farbe_und_empfaenger_gelten_fuer_die_auswahl(self):
        ed, dok, a, b = self.zwei()
        ed.auswahl = {a, b}
        ed.farbe_setzen("#123456")
        ed.empfaenger_umschalten("A")
        self.assertEqual((dok.objekte[a].farbe, dok.objekte[a].empfaenger, dok.objekte[b].empfaenger), ("#123456", ("A",), ("A",)))
        ed.empfaenger_umschalten("A")  # alle haben ihn: wieder raus
        self.assertEqual(dok.objekte[a].empfaenger, ())
        ed.bildschirm_umschalten()
        self.assertFalse(dok.objekte[a].bildschirm)

    def test_empfaenger_stand_zeigt_nur_was_alle_ausgewaehlten_gemeinsam_haben(self):
        ed, dok, a, b = self.zwei()
        dok.aendern([a], empfaenger=("A", "B"))
        dok.aendern([b], empfaenger=("B",))
        ed.auswahl = {a, b}
        self.assertEqual(ed.empfaenger_stand()[1], ("B",))


class BildUndAnzeigeTests(unittest.TestCase):
    def test_bild_einfuegen_mittig_hoechstens_halb_so_gross_mit_seitenverhaeltnis(self):
        ed, dok, _ = baue()
        p = io.BytesIO()
        Image.new("RGB", (400, 100), (1, 2, 3)).save(p, "PNG")
        neu = ed.bild_einfuegen(p.getvalue(), 400, 100)
        (x1, y1), (x2, y2) = dok.objekte[neu].punkte
        self.assertAlmostEqual((x1 + x2) / 2, 0.5)
        self.assertAlmostEqual((y1 + y2) / 2, 0.5)
        self.assertAlmostEqual((x2 - x1) * B / ((y2 - y1) * H), 4.0, places=2)
        self.assertLessEqual(x2 - x1, 0.5001)
        self.assertEqual(ed.auswahl, {neu})

    def test_rendern_zeigt_objekte_auswahl_und_privates_blasser(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("rechteck")
        ed.farbe_setzen("#FF0000")
        ed.staerke_setzen(8)
        ziehe(ed, (20, 20), (100, 80))
        bild = ed.rendern(B, H)
        self.assertEqual(bild.getpixel((22, 50))[:3], (255, 0, 0))
        ed.werkzeug_setzen("auswahl")
        ed.maus_runter(22, 50); ed.maus_hoch(22, 50)
        ed.bildschirm_umschalten()  # die Auswahl steht nicht mehr auf dem Bildschirm, sondern ist nur noch für Empfänger
        ed.auswahl = set()
        self.assertTrue(0 < ed.rendern(B, H).getpixel((22, 50))[3] < 255)  # privat: blasser

    def test_waehrend_des_ziehens_zeigt_die_vorschau_die_neue_lage_das_dokument_aber_noch_nicht(self):
        ed, dok, _ = baue()
        ed.werkzeug_setzen("rechteck")
        ziehe(ed, (20, 20), (60, 50))
        ed.werkzeug_setzen("auswahl")
        ed.maus_runter(20, 35)
        ed.maus_bewegt(120, 35)
        (vor,) = [o for o in ed.vorschau_objekte()]
        self.assertAlmostEqual(vor.punkte[0][0], 0.6)
        self.assertAlmostEqual(next(iter(dok.objekte.values())).punkte[0][0], 0.1)
        ed.maus_hoch(120, 35)

    def test_jede_aenderung_meldet_sich(self):
        ed, dok, g = baue()
        ed.werkzeug_setzen("kreis")
        ziehe(ed, (20, 20), (60, 50))
        self.assertGreater(g["geaendert"], 3)


if __name__ == "__main__":
    unittest.main()
