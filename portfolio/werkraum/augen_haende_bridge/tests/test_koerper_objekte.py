"""G08: Objektmodell (Befehle, Rückgängig/Wiederholen, Gruppen, Z-Ordnung, Speichern), Zeichner und Komposition je Empfänger."""

from __future__ import annotations

import io
import unittest

from PIL import Image

from augen_haende_bridge.koerper.komposition import Arbeitsflaechen, komponiere, token_fuer
from augen_haende_bridge.koerper.objekte import Dokument, MAX_OBJEKTE, Objekt, neue_id
from augen_haende_bridge.koerper.zeichnen_render import rendern, text_grenzen


def rechteck(i="a", empfaenger=(), bildschirm=False, punkte=((0.1, 0.1), (0.5, 0.5)), **kw):
    return Objekt(i, "rechteck", list(punkte), empfaenger=tuple(empfaenger), bildschirm=bildschirm, **kw)


class BefehleTests(unittest.TestCase):
    def test_hinzufuegen_vergibt_z_und_zaehlt_die_version(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        d.hinzufuegen(rechteck("b"))
        self.assertEqual([o.id for o in d.sortiert()], ["a", "b"])
        self.assertLess(d.objekte["a"].z, d.objekte["b"].z)
        self.assertEqual(d.version, 2)

    def test_unbekannte_art_und_leere_punkte_werden_abgelehnt(self):
        d = Dokument()
        self.assertIsNone(d.hinzufuegen(Objekt("x", "zauberei", [(0, 0)])))
        self.assertIsNone(d.hinzufuegen(Objekt("y", "linie", [])))
        self.assertEqual(len(d.objekte), 0)

    def test_grenze_fuer_die_anzahl(self):
        d = Dokument()
        for i in range(MAX_OBJEKTE + 5):
            d.hinzufuegen(rechteck(f"o{i}"))
        self.assertEqual(len(d.objekte), MAX_OBJEKTE)

    def test_undo_redo_fuer_hinzufuegen_entfernen_aendern_verschieben(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        d.aendern(["a"], farbe="#00FF00", staerke=9)
        d.verschieben(["a"], 0.1, 0.2)
        d.entfernen(["a"])
        self.assertEqual(len(d.objekte), 0)
        d.rueckgaengig()  # entfernen zurück
        self.assertIn("a", d.objekte)
        d.rueckgaengig()  # verschieben zurück
        self.assertAlmostEqual(d.objekte["a"].punkte[0][0], 0.1)
        d.rueckgaengig()  # ändern zurück
        self.assertEqual((d.objekte["a"].farbe, d.objekte["a"].staerke), ("#FF0055", 4))
        d.rueckgaengig()  # hinzufügen zurück
        self.assertEqual(len(d.objekte), 0)
        self.assertFalse(d.rueckgaengig())
        self.assertTrue(d.wiederholen() and d.wiederholen() and d.wiederholen() and d.wiederholen())
        self.assertEqual(len(d.objekte), 0)  # alles wiederholt, am Ende entfernt
        self.assertFalse(d.wiederholen())

    def test_neuer_befehl_loescht_die_wiederholen_liste(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        d.rueckgaengig()
        self.assertTrue(d.kann_wiederholen)
        d.hinzufuegen(rechteck("b"))
        self.assertFalse(d.kann_wiederholen)

    def test_undo_betrifft_nur_die_objekte_des_befehls(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        d.hinzufuegen(rechteck("b"))
        d.aendern(["a"], farbe="#111111")
        d.aendern(["b"], farbe="#222222")
        d.rueckgaengig()
        self.assertEqual((d.objekte["a"].farbe, d.objekte["b"].farbe), ("#111111", "#FF0055"))

    def test_undo_hat_eine_grenze_und_die_version_steigt_auch_beim_rueckgaengig(self):
        d = Dokument()
        for i in range(250):
            d.hinzufuegen(rechteck(f"o{i}"))
        n = 0
        while d.rueckgaengig():
            n += 1
        self.assertEqual(n, 200)
        v = d.version
        d.wiederholen()
        self.assertGreater(d.version, v)

    def test_aendern_laesst_nur_erlaubte_felder_zu(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        d.aendern(["a"], id="boese", art="text", z=99, farbe="#123456")
        o = d.objekte["a"]
        self.assertEqual((o.id, o.art, o.farbe), ("a", "rechteck", "#123456"))
        self.assertNotEqual(o.z, 99)

    def test_ein_befehl_ohne_wirkung_landet_nicht_im_verlauf(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a"))
        v = d.version
        self.assertEqual(d.aendern(["a"], farbe="#FF0055"), 1)
        self.assertEqual(d.version, v)


class GruppenOrdnungTests(unittest.TestCase):
    def _drei(self):
        d = Dokument()
        for i in "abc":
            d.hinzufuegen(rechteck(i))
        return d

    def test_gruppe_bewegt_gemeinsam_und_loesen_trennt(self):
        d = self._drei()
        self.assertIsNotNone(d.gruppieren(["a", "b"]))
        d.verschieben(["a"], 0.2, 0)  # nur a angefasst, b geht mit
        self.assertAlmostEqual(d.objekte["b"].punkte[0][0], 0.3)
        self.assertAlmostEqual(d.objekte["c"].punkte[0][0], 0.1)
        d.aufloesen(["a"])
        d.verschieben(["a"], 0.2, 0)
        self.assertAlmostEqual(d.objekte["b"].punkte[0][0], 0.3)

    def test_gruppe_braucht_mindestens_zwei(self):
        d = self._drei()
        self.assertIsNone(d.gruppieren(["a"]))

    def test_undo_der_gruppierung(self):
        d = self._drei()
        d.gruppieren(["a", "b"])
        d.rueckgaengig()
        self.assertIsNone(d.objekte["a"].gruppe)

    def test_z_ordnung_ganz_vor_zurueck_und_schrittweise(self):
        d = self._drei()
        d.ordnung(["a"], "ganz_vor")
        self.assertEqual([o.id for o in d.sortiert()], ["b", "c", "a"])
        d.ordnung(["a"], "ganz_zurueck")
        self.assertEqual([o.id for o in d.sortiert()], ["a", "b", "c"])
        d.ordnung(["a"], "vor")
        self.assertEqual([o.id for o in d.sortiert()], ["b", "a", "c"])
        d.ordnung(["c"], "zurueck")
        self.assertEqual([o.id for o in d.sortiert()], ["b", "c", "a"])
        d.rueckgaengig()
        self.assertEqual([o.id for o in d.sortiert()], ["b", "a", "c"])

    def test_z_ordnung_am_rand_aendert_nichts(self):
        d = self._drei()
        v = d.version
        self.assertEqual(d.ordnung(["c"], "ganz_vor"), 0)
        self.assertEqual(d.version, v)

    def test_duplizieren_haelt_gruppen_zusammen_und_ist_rueckgaengig_zu_machen(self):
        d = self._drei()
        d.gruppieren(["a", "b"])
        neue = d.duplizieren(["a"])
        self.assertEqual(len(neue), 2)
        gruppen = {d.objekte[i].gruppe for i in neue}
        self.assertEqual(len(gruppen), 1)
        self.assertNotIn(d.objekte["a"].gruppe, gruppen)
        d.rueckgaengig()
        self.assertEqual(len(d.objekte), 3)

    def test_skalieren_um_einen_ankerpunkt(self):
        d = Dokument()
        d.hinzufuegen(rechteck("a", punkte=((0.2, 0.2), (0.4, 0.6))))
        d.skalieren(["a"], 2.0, 0.5, (0.2, 0.2))
        (x1, y1), (x2, y2) = d.objekte["a"].punkte
        self.assertEqual((round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3)), (0.2, 0.2, 0.6, 0.4))
        self.assertEqual(d.skalieren(["a"], 0, 1, (0, 0)), 0)


class TreffenTests(unittest.TestCase):
    def test_oberstes_objekt_wird_getroffen_unsichtbare_nicht(self):
        d = Dokument()
        d.hinzufuegen(rechteck("unten", punkte=((0.0, 0.0), (0.5, 0.5))))
        d.hinzufuegen(rechteck("oben", punkte=((0.2, 0.2), (0.6, 0.6))))
        self.assertEqual(d.treffer(0.3, 0.3), "oben")
        d.aendern(["oben"], sichtbar=False)
        self.assertEqual(d.treffer(0.3, 0.3), "unten")
        self.assertIsNone(d.treffer(0.9, 0.9))

    def test_striche_werden_in_der_naehe_getroffen(self):
        d = Dokument()
        d.hinzufuegen(Objekt("l", "linie", [(0.1, 0.1), (0.9, 0.1)]))
        self.assertEqual(d.treffer(0.5, 0.105), "l")
        self.assertIsNone(d.treffer(0.5, 0.4))

    def test_gummiband_waehlt_nur_vollstaendig_enthaltene(self):
        d = Dokument()
        d.hinzufuegen(rechteck("drin", punkte=((0.2, 0.2), (0.3, 0.3))))
        d.hinzufuegen(rechteck("halb", punkte=((0.2, 0.2), (0.9, 0.9))))
        self.assertEqual(d.im_rechteck(0.1, 0.1, 0.5, 0.5), ["drin"])


class SpeichernTests(unittest.TestCase):
    def test_hin_und_zurueck_inklusive_bild_und_gruppe(self):
        puffer = io.BytesIO()
        Image.new("RGB", (4, 4), (255, 0, 0)).save(puffer, "PNG")
        d = Dokument("chrome.exe")
        d.hinzufuegen(Objekt("b", "bild", [(0.1, 0.1), (0.4, 0.4)], bild=puffer.getvalue(), empfaenger=("t-1", "t-2")))
        d.hinzufuegen(Objekt("t", "text", [(0.5, 0.5)], text="Hallo äöü", bildschirm=True))
        d.gruppieren(["b", "t"])
        neu = Dokument.aus_dict(d.zu_dict(), "chrome.exe")
        self.assertEqual([o.id for o in neu.sortiert()], ["b", "t"])
        self.assertEqual(neu.objekte["b"].bild, puffer.getvalue())
        self.assertEqual(neu.objekte["b"].empfaenger, ("t-1", "t-2"))
        self.assertEqual((neu.objekte["t"].text, neu.objekte["t"].bildschirm), ("Hallo äöü", True))
        self.assertEqual(neu.objekte["b"].gruppe, neu.objekte["t"].gruppe)

    def test_kaputte_daten_ergeben_ein_leeres_oder_teilweises_dokument_nie_einen_absturz(self):
        for muell in (None, 5, "x", {"objekte": 5}, {"objekte": [None, 3, {"art": "kreis"}, {"art": "kreis", "punkte": "x"}]}):
            self.assertEqual(len(Dokument.aus_dict(muell).objekte), 0)
        teil = Dokument.aus_dict({"objekte": [{"art": "linie", "punkte": [[0, 0], [1, 1]], "farbe": "rot", "staerke": 999}, {"art": "kaputt"}]})
        self.assertEqual(len(teil.objekte), 1)
        o = next(iter(teil.objekte.values()))
        self.assertEqual((o.farbe, o.staerke), ("#FF0055", 60))  # ungültige Farbe → Standard, Stärke geklemmt

    def test_zu_grosses_bild_wird_verworfen(self):
        import base64
        gross = base64.b64encode(b"x" * 4_100_000).decode()
        self.assertIsNone(Objekt.aus_dict({"art": "bild", "punkte": [[0, 0], [1, 1]], "bild": gross}))


class ZeichnerTests(unittest.TestCase):
    def pixel(self, bild, x, y):
        return bild.getpixel((x, y))

    def test_rechteck_hat_einen_rand_und_ist_innen_durchsichtig(self):
        b = rendern([rechteck("a", farbe="#FF0000", staerke=3, punkte=((0.2, 0.2), (0.8, 0.8)))], 100, 100)
        self.assertEqual(self.pixel(b, 20, 50)[:3], (255, 0, 0))
        self.assertEqual(self.pixel(b, 50, 50)[3], 0)
        self.assertEqual(self.pixel(b, 5, 5)[3], 0)

    def test_linie_und_pfeil_haben_pixel_pfeil_hat_eine_spitze(self):
        linie = rendern([Objekt("l", "linie", [(0.1, 0.5), (0.9, 0.5)], farbe="#00FF00", staerke=3)], 100, 100)
        pfeil = rendern([Objekt("p", "pfeil", [(0.1, 0.5), (0.9, 0.5)], farbe="#00FF00", staerke=3)], 100, 100)
        self.assertEqual(self.pixel(linie, 50, 50)[:3], (0, 255, 0))
        # Die Spitze macht den Pfeil am Ende höher als die Linie
        hoehe = lambda b: sum(1 for y in range(100) if b.getpixel((85, y))[3] > 0)  # noqa: E731
        self.assertGreater(hoehe(pfeil), hoehe(linie))

    def test_marker_ist_halbdurchsichtig_freihand_voll(self):
        pts = [(0.1, 0.5), (0.9, 0.5)]
        frei = rendern([Objekt("f", "freihand", pts, farbe="#0000FF", staerke=4)], 100, 100)
        mark = rendern([Objekt("m", "marker", pts, farbe="#0000FF", staerke=4)], 100, 100)
        self.assertEqual(self.pixel(frei, 50, 50)[3], 255)
        self.assertTrue(0 < self.pixel(mark, 50, 50)[3] < 255)

    def test_kreis_trifft_die_ellipse_nicht_die_ecke(self):
        b = rendern([Objekt("k", "kreis", [(0.1, 0.1), (0.9, 0.9)], farbe="#FFFFFF", staerke=3)], 100, 100)
        self.assertEqual(self.pixel(b, 50, 10)[3], 255)
        self.assertEqual(self.pixel(b, 11, 11)[3], 0)

    def test_text_zeichnet_pixel_und_hat_eine_groesse(self):
        b = rendern([Objekt("t", "text", [(0.1, 0.1)], text="Hallo", farbe="#FFFF00", schriftgroesse=30)], 300, 100)
        self.assertIsNotNone(b.getbbox())
        breite, hoehe = text_grenzen("Hallo", 30, 300, 100)
        self.assertTrue(0.1 < breite < 0.9 and 0.1 < hoehe < 0.9)

    def test_bild_wird_in_den_rahmen_skaliert(self):
        p = io.BytesIO()
        Image.new("RGB", (2, 2), (255, 0, 255)).save(p, "PNG")
        b = rendern([Objekt("i", "bild", [(0.25, 0.25), (0.75, 0.75)], bild=p.getvalue())], 100, 100)
        self.assertEqual(self.pixel(b, 50, 50)[:3], (255, 0, 255))
        self.assertEqual(self.pixel(b, 10, 10)[3], 0)

    def test_kaputtes_bild_verhindert_den_rest_nicht(self):
        objekte = [Objekt("i", "bild", [(0, 0), (0.5, 0.5)], bild=b"kein png"),
                   rechteck("a", farbe="#FF0000", punkte=((0.5, 0.5), (0.9, 0.9)))]
        self.assertIsNotNone(rendern(objekte, 100, 100).getbbox())

    def test_reihenfolge_oben_gewinnt(self):
        unten = Objekt("u", "rechteck", [(0.1, 0.1), (0.9, 0.9)], farbe="#FF0000", staerke=20)
        oben = Objekt("o", "rechteck", [(0.1, 0.1), (0.9, 0.9)], farbe="#0000FF", staerke=20)
        self.assertEqual(rendern([unten, oben], 100, 100).getpixel((12, 50))[:3], (0, 0, 255))


class KompositionTests(unittest.TestCase):
    def setUp(self):
        self.d = Dokument("ziel")
        self.d.hinzufuegen(rechteck("fuer_a", empfaenger=("A",), farbe="#FF0000", staerke=6, punkte=((0.0, 0.0), (1.0, 1.0))))
        self.d.hinzufuegen(rechteck("fuer_b", empfaenger=("B",), farbe="#0000FF", staerke=6, punkte=((0.3, 0.3), (0.7, 0.7))))
        self.d.hinzufuegen(rechteck("nur_bildschirm", bildschirm=True, farbe="#00FF00", staerke=6, punkte=((0.1, 0.1), (0.9, 0.9))))
        self.basis = Image.new("RGB", (100, 100), (30, 30, 30))
        self.gate = (0, 0, 100, 100)

    def test_jeder_empfaenger_sieht_nur_seine_objekte(self):
        a = komponiere(self.basis, self.d, "A", self.gate, self.gate)
        b = komponiere(self.basis, self.d, "B", self.gate, self.gate)
        self.assertEqual(a.getpixel((2, 50)), (255, 0, 0))  # A sieht sein Rechteck
        self.assertEqual(a.getpixel((30, 50)), (30, 30, 30))  # und nicht das von B
        self.assertEqual(b.getpixel((31, 50)), (0, 0, 255))
        self.assertEqual(b.getpixel((2, 50)), (30, 30, 30))

    def test_bildschirmobjekte_werden_nicht_in_das_bild_gemalt_sie_sind_schon_im_basisbild(self):
        a = komponiere(self.basis, self.d, "A", self.gate, self.gate)
        self.assertNotEqual(a.getpixel((11, 50)), (0, 255, 0))

    def test_dritter_agent_ohne_objekte_bekommt_das_bild_unveraendert(self):
        c = komponiere(self.basis, self.d, "C", self.gate, self.gate)
        self.assertIs(c, self.basis)

    def test_basisbild_wird_nicht_veraendert(self):
        komponiere(self.basis, self.d, "A", self.gate, self.gate)
        self.assertEqual(self.basis.getpixel((2, 50)), (30, 30, 30))

    def test_ausschnitt_eines_teils_des_gates_stimmt_mit_dem_gesamtbild_ueberein(self):
        gesamt = komponiere(self.basis, self.d, "A", self.gate, self.gate)
        links = komponiere(self.basis.crop((0, 0, 50, 100)), self.d, "A", self.gate, (0, 0, 50, 100))
        self.assertEqual(links.tobytes(), gesamt.crop((0, 0, 50, 100)).tobytes())

    def test_gate_ausserhalb_der_aufnahme_wird_beschnitten(self):
        gate = (-20, 0, 80, 100)  # 20 px links außerhalb
        ausschnitt = (0, 0, 80, 100)
        bild = Image.new("RGB", (80, 100), (30, 30, 30))
        ergebnis = komponiere(bild, self.d, "A", gate, ausschnitt)
        self.assertEqual(ergebnis.size, (80, 100))
        self.assertEqual(ergebnis.getpixel((78, 50)), (255, 0, 0))  # rechter Rand des Gates

    def test_token_aendert_sich_mit_dem_inhalt_und_ist_leer_ohne_objekte(self):
        t1 = token_fuer(self.d, "A", self.gate)
        self.d.aendern(["fuer_a"], farbe="#00FFFF")
        self.assertNotEqual(t1, token_fuer(self.d, "A", self.gate))
        self.assertEqual(token_fuer(self.d, "C", self.gate), b"")

    def test_ausgeblendete_objekte_verschwinden_auch_aus_dem_bild(self):
        self.d.aendern(["fuer_a"], sichtbar=False)
        self.assertIs(komponiere(self.basis, self.d, "A", self.gate, self.gate), self.basis)

    def test_arbeitsflaechen_liefern_nur_etwas_wenn_es_etwas_zu_komponieren_gibt(self):
        af = Arbeitsflaechen()
        af.dokumente["ziel"] = self.d
        self.assertIsNone(af.komposit("C", "ziel", self.gate, self.gate))
        self.assertIsNone(af.komposit("A", "anderes", self.gate, self.gate))
        k = af.komposit("A", "ziel", self.gate, self.gate)
        self.assertEqual(k.anwenden(self.basis).getpixel((2, 50)), (255, 0, 0))


if __name__ == "__main__":
    unittest.main()


class BilderstromKompositionTests(unittest.TestCase):
    """Der echte Bilderstrom: die Objekte landen im Bild des Empfängers, nur dort, und ändern den Fingerabdruck."""

    def _strom(self, af, gesendet):
        import base64
        from augen_haende_bridge.koerper import bild
        from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
        raw = bytes([30, 30, 30, 255]) * (100 * 100)

        def kodieren(raw_, b, h, ausschnitt, nachbearbeiten=None):
            return bild.bgra_zu_jpeg(raw_, b, h, ausschnitt, nachbearbeiten)

        def senden(tid, payload):
            gesendet.append((tid, base64.b64decode(payload["data"])))
            return True

        strom = Bilderstrom(erfassen=lambda: (raw, 100, 100), bildschirm=lambda: (0, 0, 100, 100), fenster_rect=lambda h: None, senden=senden,
                            kodieren=kodieren, komposit=lambda tid, gate, ausschnitt: af.komposit(tid, "desktop", gate, ausschnitt))
        return strom

    def _rot(self, jpeg):
        bild_ = Image.open(io.BytesIO(jpeg)).convert("RGB")
        return sum(1 for p in bild_.getdata() if p[0] > 200 and p[1] < 80)

    def test_nur_der_empfaenger_bekommt_das_rote_rechteck_im_bild(self):
        af = Arbeitsflaechen()
        af.dokument("desktop").hinzufuegen(rechteck("r", empfaenger=("A",), farbe="#FF0000", staerke=8, punkte=((0.1, 0.1), (0.9, 0.9))))
        gesendet = []
        strom = self._strom(af, gesendet)
        strom.binden("A", None)
        strom.binden("B", None)
        strom.tick()
        bilder = dict(gesendet)
        self.assertGreater(self._rot(bilder["A"]), 100)
        self.assertEqual(self._rot(bilder["B"]), 0)

    def test_aenderung_der_objekte_erzwingt_ein_neues_bild_ohne_aenderung_wird_nichts_wiederholt(self):
        af = Arbeitsflaechen()
        dok = af.dokument("desktop")
        gesendet = []
        strom = self._strom(af, gesendet)
        strom.binden("A", None)
        strom.tick()
        n1 = len(gesendet)
        strom.tick()
        self.assertEqual(len(gesendet), n1)  # unverändert: nicht noch einmal
        dok.hinzufuegen(rechteck("r", empfaenger=("A",), farbe="#FF0000", staerke=8, punkte=((0.1, 0.1), (0.9, 0.9))))
        strom.tick()
        self.assertEqual(len(gesendet), n1 + 1)  # neues Objekt: sofort ein neues Bild
        dok.rueckgaengig()
        strom.tick()
        self.assertEqual(len(gesendet), n1 + 2)  # Rückgängig ebenfalls
        self.assertEqual(self._rot(gesendet[-1][1]), 0)

    def test_ohne_objekte_ist_der_pfad_unveraendert(self):
        af = Arbeitsflaechen()
        gesendet = []
        strom = self._strom(af, gesendet)
        strom.binden("A", None)
        self.assertEqual(strom.tick(), 1)
