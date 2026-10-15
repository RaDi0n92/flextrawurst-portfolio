"""Ampel-Fenster: Fläche und Zeilen, Größe, Treffer, Texte, Farbe (rein) – Zeichnen ist Sache des Fenstergerüsts."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import ampel, ampel_fenster as af
from augen_haende_bridge.koerper.regie_fenster import BREITE as REGIE_B, HOEHE as REGIE_H


class DreiLampenTests(unittest.TestCase):
    def test_das_fenster_ist_klein_und_hat_immer_dieselbe_form(self):
        b, h = af.masse(1.0)
        self.assertLessEqual(b * h, REGIE_B * REGIE_H * 0.5)  # höchstens halb so groß wie „Stop, Regie, Cam, Mik“
        self.assertEqual(af.masse(1.0, 0), af.masse(1.0, 5))  # Form hängt nicht vom Zustand ab

    def test_die_groesse_folgt_dem_faktor_und_wird_geklemmt(self):
        self.assertLess(af.masse(0.7)[0], af.masse(1.0)[0])
        self.assertLess(af.masse(1.0)[0], af.masse(2.0)[0])
        self.assertEqual(af.klemmen(0.01), af.FAKTOR_MIN)
        self.assertEqual(af.klemmen(99), af.FAKTOR_MAX)

    def test_groesser_und_kleiner_gehen_in_festen_schritten_und_stossen_an_die_grenzen(self):
        f = 1.0
        for _ in range(20):
            f = af.klemmen(f + af.FAKTOR_SCHRITT)
        self.assertEqual(f, af.FAKTOR_MAX)
        for _ in range(20):
            f = af.klemmen(f - af.FAKTOR_SCHRITT)
        self.assertEqual(f, af.FAKTOR_MIN)

    def test_bedienung_wie_die_raute_ziehen_ueberall_ohne_eigene_kanten_und_ohne_mausrad(self):
        self.assertEqual(af.AmpelFenster.treffer(None, 3, 3), af.w.HTCLIENT)  # kein System-Fensterzug, kein Kantenziehen
        self.assertNotIn("bei_rad", vars(af.AmpelFenster))  # kein eigenes Mausrad
        self.assertEqual(af.ZIEH_SCHWELLE, 4)

    def test_drei_lampen_liegen_nebeneinander_im_fenster(self):
        b, h = af.masse(1.0)
        mitten = [af.lampen_mitte(i, 1.0) for i in range(3)]
        self.assertEqual(len({y for _x, y in mitten}), 1)
        self.assertTrue(all(0 < x < b for x, _y in mitten) and mitten[0][0] < mitten[1][0] < mitten[2][0])

    def test_treffer_auf_jede_lampe_und_daneben(self):
        for i in range(3):
            x, y = af.lampen_mitte(i, 1.0)
            self.assertEqual(af.lampe_bei(x, y, 1.0), i)
        self.assertIsNone(af.lampe_bei(-1, 5, 1.0))
        self.assertIsNone(af.lampe_bei(5, 999, 1.0))
        x, y = af.lampen_mitte(2, 1.0)
        self.assertEqual(af.lampe_bei(x, y, 1.0, 2), 1)  # nur zwei Lampen da: der Rand gehört zur letzten

    def test_blau_heisst_laeuft_orange_achtung_rot_kaputt_vier_unterscheidbare_farben(self):
        self.assertEqual((af.FARBEN[ampel.GRUEN], af.FARBEN[ampel.GELB], af.FARBEN[ampel.ROT]), (af.BLAU, af.ORANGE, af.ROT))
        self.assertEqual(len({af.BLAU, af.ORANGE, af.ROT, af.GRAU}), 4)


class BuchstabenTests(unittest.TestCase):
    def test_neben_den_lampen_stehen_a_h_und_z_in_der_reihenfolge_augen_haende_ziel(self):
        self.assertEqual(af.LAMPEN_BUCHSTABEN, ("A", "H", "Z"))
        self.assertEqual(tuple(n[0] for n in af.LAMPEN_NAMEN), af.LAMPEN_BUCHSTABEN)  # der Buchstabe ist der Anfang des Namens

    def test_der_buchstabe_liegt_rechts_der_lampe_und_im_eigenen_drittel(self):
        for faktor in (0.7, 1.0, 2.0, 3.0):
            b, _h = af.masse(faktor)
            for i in range(3):
                mx, _my = af.lampen_mitte(i, faktor)
                links = af.buchstabe_links(i, faktor)
                lampe_rechts = mx + af._s(af.LAMPE_D, faktor) // 2
                self.assertGreater(links, lampe_rechts, (faktor, i))
                self.assertLess(links + af._s(8, faktor), (i + 1) * b // 3, (faktor, i))  # ein Zeichen von etwa 8 px (bei Faktor 1) passt noch in sein Drittel

    def test_ein_klick_auf_den_buchstaben_zaehlt_zur_selben_lampe(self):
        for i in range(3):
            x = af.buchstabe_links(i, 1.0) + 2
            self.assertEqual(af.lampe_bei(x, af.masse(1.0)[1] // 2, 1.0), i)


class SammellampenTests(unittest.TestCase):
    def lampen(self, **ueber):
        werte = dict(name="A", alter_s=3.0, ziel_zustand="ok", aufnahme="frisch")
        werte.update(ueber)
        return ampel.lampen(ampel.Zustand(**werte))

    def test_es_gibt_genau_drei_lampen_augen_haende_ziel(self):
        drei = ampel.drei_lampen(self.lampen())
        self.assertEqual([l.kennung for l in drei], ["augen", "haende", "ziel"])
        self.assertEqual([l.name for l in drei], ["Augen", "Hände", "Ziel"])
        self.assertTrue(all(l.farbe == ampel.GRUEN for l in drei))

    def test_jede_lampe_zeigt_das_schlimmste_ihrer_gruppe_und_zaehlt_die_weiteren(self):
        drei = {l.kennung: l for l in ampel.drei_lampen(self.lampen(alter_s=900.0, probleme=frozenset({"senden_abgelehnt"})))}
        self.assertEqual(drei["augen"].farbe, ampel.ROT)
        self.assertIn("weitere", drei["augen"].wort)
        self.assertEqual(drei["haende"].farbe, ampel.GRUEN)  # die Gruppen stören sich nicht
        self.assertEqual(drei["ziel"].farbe, ampel.GRUEN)

    def test_hande_je_art_und_programm_gehoeren_zur_haende_lampe(self):
        z = ampel.Zustand(name="A", alter_s=3.0, haende_arten={"klick": ("abgelehnt", "punkt_verdeckt", 2.0)})
        drei = {l.kennung: l for l in ampel.drei_lampen(ampel.lampen(z))}
        self.assertEqual((drei["haende"].farbe, drei["haende"].behebe), (ampel.ROT, "fenster_vor"))

    def test_fenster_weg_und_verbindung_machen_die_ziel_lampe_rot(self):
        self.assertEqual({l.kennung: l for l in ampel.drei_lampen(self.lampen(fenster_weg=True))}["ziel"].farbe, ampel.ROT)
        self.assertEqual({l.kennung: l for l in ampel.drei_lampen(self.lampen(verbunden=False))}["ziel"].farbe, ampel.ROT)

    def test_jede_funktion_gehoert_zu_genau_einer_der_drei_lampen(self):
        for l in ampel.lampen(ampel.Zustand(name="A", alter_s=3.0, haende_arten={"klick": ("ausgefuehrt", "", 1.0)}, haende_ziele={"Kate": ("ausgefuehrt", "", 1.0)})):
            self.assertIn(ampel.gruppe_von(l.kennung), ("augen", "haende", "ziel"), l.kennung)

    def test_das_menue_ordnet_alle_funktionen_unter_erklaerten_ueberschriften(self):
        gruppen = list(ampel.menue_gruppen(ampel.lampen(ampel.Zustand(name="A", alter_s=3.0))))
        self.assertEqual(len(gruppen), 3)
        self.assertTrue(gruppen[0][0].startswith("Augen: Kommen Bilder"))
        self.assertEqual(sum(len(t) for _u, t in gruppen), len(ampel.lampen(ampel.Zustand(name="A", alter_s=3.0))))


class FarbeTests(unittest.TestCase):
    def test_die_echte_agentenfarbe_wird_gelesen(self):
        self.assertEqual(af.hex_zu_rgb("#ff8000"), af.w.rgb(255, 128, 0))
        self.assertEqual(af.hex_zu_rgb("ff8000"), af.w.rgb(255, 128, 0))

    def test_kaputte_farbe_ergibt_einen_sichtbaren_ersatz_statt_eines_absturzes(self):
        for kaputt in ("", "#12", "zzzzzz", None):
            self.assertIsInstance(af.hex_zu_rgb(kaputt), int)

    def test_blau_heisst_laeuft_orange_achtung_rot_kaputt(self):
        self.assertEqual(af.FARBEN[ampel.GRUEN], af.BLAU)
        self.assertEqual(af.FARBEN[ampel.GELB], af.ORANGE)
        self.assertEqual(af.FARBEN[ampel.ROT], af.ROT)
        self.assertEqual(len({af.BLAU, af.ORANGE, af.ROT, af.GRAU}), 4, "vier unterscheidbare Farben")


class KreisTests(unittest.TestCase):
    def test_der_kreis_hat_genug_ecken_und_liegt_um_die_mitte(self):
        punkte = af.kreis(50, 50, 7)
        self.assertGreaterEqual(len(punkte), 16)
        self.assertTrue(all(43 <= x <= 57 and 43 <= y <= 57 for x, y in punkte))


class KeineNamenskollisionTests(unittest.TestCase):
    """Die Fensterbasis setzt in ihrem Konstruktor eigene Attribute (z. B. `_aktion` fürs Verschieben) und überschreibt gleichnamige der
    Unterklasse. Die Ampel darf keinen dieser Namen benutzen."""

    @staticmethod
    def zugewiesen(pfad, klasse):
        import ast
        baum = ast.parse(open(pfad, encoding="utf-8").read())
        namen = set()
        for k in ast.walk(baum):
            if isinstance(k, ast.ClassDef) and k.name == klasse:
                for n in ast.walk(k):
                    if isinstance(n, (ast.Assign, ast.AnnAssign)):
                        ziele = n.targets if isinstance(n, ast.Assign) else [n.target]
                        for z in ziele:
                            for t in ast.walk(z):
                                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
                                    namen.add(t.attr)
        return namen

    def test_keine_attribute_der_ampel_ueberschneiden_sich_mit_der_fensterbasis(self):
        import inspect
        from augen_haende_bridge.koerper import fenster_linux
        basis = self.zugewiesen(inspect.getsourcefile(fenster_linux), "Fenster")
        ampel_namen = self.zugewiesen(inspect.getsourcefile(af), "AmpelFenster")
        self.assertTrue(basis, "die Basis muss Attribute setzen, sonst prüft der Test nichts")
        self.assertEqual(sorted(basis & ampel_namen), [])


if __name__ == "__main__":
    unittest.main()
