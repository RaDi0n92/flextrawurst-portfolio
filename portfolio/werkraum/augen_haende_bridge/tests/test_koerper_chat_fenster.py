"""Tests für koerper/chat_fenster.py: Verlauf, Bildlauf, Eingabe/Senden — als reine Funktionen bzw. per
`object.__new__`-Fixture wie bei den anderen koerper-Fenstern (der Konstruktor selbst braucht Windows/Wine)."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import win32 as w

from augen_haende_bridge.koerper.chat_fenster import (
    ChatFenster,
    KOPF_H,
    TIMER_CURSOR,
    kante_bei,
    griff_rechteck,
    kopf_rechtecke,
    maximaler_versatz,
    rollbalken_rechteck,
    sprung_versatz,
    versatz_fuer,
    sichtbare_zeilen,
    umbrechen,
    verlauf_anhaengen,
)


def _baue(**overrides) -> ChatFenster:
    f = object.__new__(ChatFenster)
    f.farben = {}
    f.empfaenger, f.empfaenger_farbe = "kein Agent", 0
    f._empfaenger_wechseln = Mock()
    f.deckkraft = 255
    f.rechteck = Mock(return_value=(0, 0, 320, 220))
    f._gesendet = Mock()
    f._jetzt_text = Mock(return_value="12:00")
    f.verlauf = []
    f.eingabe = ""
    f._bildlauf_versatz = 0
    f._cursor_phase = True
    f._hat_fokus = False
    f.f_text = Mock(zellhoehe=16)
    f.f_kopf = Mock(zellhoehe=22)
    f._messen_kopf = lambda text: len(text) * 9  # Zeit und Name: größere Schrift, 9 px je Zeichen
    f._mess_hdc = None
    f._umbruch_stand, f._umbruch_zeilen, f._umbruch_anfaenge = None, [], []
    f._balken_ziehen = None
    f.erfasse_maus = Mock()
    f.gib_maus_frei = Mock()
    f._messen = lambda text: len(text) * 7  # jedes Zeichen 7 px breit
    f.hwnd = 999
    f.leinwand = None
    f._timer = {}
    f.clientgroesse = Mock(return_value=(320, 220))
    f.neu_zeichnen = Mock()
    f.starte_timer = Mock()
    f.stoppe_timer = Mock()
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class VerlaufFunktionenTests(unittest.TestCase):
    def test_verlauf_anhaengen_haengt_ans_ende(self) -> None:
        v = verlauf_anhaengen([("a", "eins", "12:00")], "b", "zwei", "12:01", maximal=10)
        self.assertEqual(v, [("a", "eins", "12:00"), ("b", "zwei", "12:01")])

    def test_verlauf_anhaengen_kappt_bei_maximal_und_wirft_die_aeltesten_weg(self) -> None:
        v = []
        for i in range(5):
            v = verlauf_anhaengen(v, "a", str(i), "12:00", maximal=3)
        self.assertEqual([e[1] for e in v], ["2", "3", "4"])

    def test_sichtbare_zeilen_ohne_versatz_zeigt_das_ende(self) -> None:
        v = [("a", str(i), "12:00") for i in range(10)]
        self.assertEqual([e[1] for e in sichtbare_zeilen(v, 3, 0)], ["7", "8", "9"])

    def test_sichtbare_zeilen_mit_versatz_blaettert_zurueck(self) -> None:
        v = [("a", str(i), "12:00") for i in range(10)]
        self.assertEqual([e[1] for e in sichtbare_zeilen(v, 3, 2)], ["5", "6", "7"])

    def test_sichtbare_zeilen_kappt_am_anfang_des_verlaufs(self) -> None:
        v = [("a", str(i), "12:00") for i in range(3)]
        self.assertEqual([e[1] for e in sichtbare_zeilen(v, 5, 0)], ["0", "1", "2"])

    def test_maximaler_versatz_ist_null_wenn_alles_hineinpasst(self) -> None:
        self.assertEqual(maximaler_versatz(gesamt=3, anzahl=5), 0)

    def test_maximaler_versatz_ist_die_differenz_sonst(self) -> None:
        self.assertEqual(maximaler_versatz(gesamt=10, anzahl=4), 6)


class UmbruchTests(unittest.TestCase):
    messen = staticmethod(lambda t: len(t) * 7)

    def test_kurzer_text_bleibt_eine_zeile(self) -> None:
        self.assertEqual(umbrechen("hallo welt", 200, self.messen), ["hallo welt"])

    def test_langer_text_bricht_an_wortgrenzen_und_geht_nichts_verloren(self) -> None:
        text = "das ist eine ziemlich lange nachricht die nicht in eine zeile passt"
        zeilen = umbrechen(text, 100, self.messen)  # 14 Zeichen je Zeile
        self.assertGreater(len(zeilen), 3)
        self.assertTrue(all(self.messen(z) <= 100 for z in zeilen))
        self.assertEqual(" ".join(zeilen), text)

    def test_zu_langes_wort_wird_zeichenweise_getrennt(self) -> None:
        zeilen = umbrechen("a " + "x" * 40 + " b", 70, self.messen)  # 10 Zeichen je Zeile
        self.assertTrue(all(self.messen(z) <= 70 for z in zeilen))
        self.assertEqual("".join(zeilen).replace(" ", ""), "a" + "x" * 40 + "b")

    def test_zeilenumbrueche_im_text_bleiben_erhalten(self) -> None:
        self.assertEqual(umbrechen("eins\nzwei", 200, self.messen), ["eins", "zwei"])

    def test_folgezeilen_koennen_schmaler_sein_fuer_den_einzug(self) -> None:
        zeilen = umbrechen("aaa bbb ccc ddd eee", 70, self.messen, folge_breite=42)  # erste 10, weitere 6 Zeichen
        self.assertLessEqual(self.messen(zeilen[0]), 70)
        self.assertTrue(all(self.messen(z) <= 42 for z in zeilen[1:]))
        self.assertEqual(" ".join(zeilen), "aaa bbb ccc ddd eee")

    def test_leerer_text_ergibt_eine_leere_zeile(self) -> None:
        self.assertEqual(umbrechen("", 100, self.messen), [""])

    def test_extrem_schmal_haengt_nicht_und_verliert_nichts(self) -> None:
        zeilen = umbrechen("abc def", 3, self.messen)  # schmaler als ein Zeichen
        self.assertEqual("".join(zeilen).replace(" ", ""), "abcdef")


class AnzeigezeilenTests(unittest.TestCase):
    def test_kopf_nur_in_der_ersten_zeile_folgezeilen_eingerueckt(self) -> None:
        f = _baue(verlauf=[("Claude", "wort " * 30, "12:00")])
        zeilen = f.anzeigezeilen()
        self.assertGreater(len(zeilen), 2)
        self.assertEqual(zeilen[0][:2], ("Claude", "[12:00] Claude:"))
        self.assertTrue(all(kopf == "" for _, kopf, _ in zeilen[1:]))
        self.assertTrue(all(text.startswith("    ") for _, _, text in zeilen[1:]))
        self.assertTrue(all(sender == "Claude" for sender, _, _ in zeilen))

    def test_der_kopf_steht_nicht_im_text_und_der_text_steht_nicht_im_kopf(self) -> None:
        f = _baue(verlauf=[("A", "hallo", "09:05")])
        (sender, kopf, text), = f.anzeigezeilen()
        self.assertEqual((kopf, text), ("[09:05] A:", "hallo"))

    def test_nichts_geht_beim_umbrechen_verloren(self) -> None:
        text = " ".join(f"wort{i}" for i in range(40))
        f = _baue(verlauf=[("A", text, "09:05")])
        gezeigt = " ".join(t.strip() for _, _, t in f.anzeigezeilen())
        for i in range(40):
            self.assertIn(f"wort{i}", gezeigt)

    def test_zeilen_passen_in_die_fensterbreite_mit_dem_breiteren_kopf(self) -> None:
        f = _baue(verlauf=[("Claude", "x" * 300, "12:00")])
        for _, kopf, text in f.anzeigezeilen():
            breite = (f._messen_kopf(kopf + " ") if kopf else 0) + f._messen(text)
            self.assertLessEqual(breite, 320)

    def test_ergebnis_wird_gemerkt_bis_sich_verlauf_oder_breite_aendern(self) -> None:
        f = _baue(verlauf=[("A", "eins", "12:00")])
        erste = f.anzeigezeilen()
        self.assertIs(f.anzeigezeilen(), erste)
        f.verlauf = [*f.verlauf, ("A", "zwei", "12:01")]
        self.assertIsNot(f.anzeigezeilen(), erste)
        gemerkt = f.anzeigezeilen()
        f.clientgroesse = Mock(return_value=(200, 220))
        self.assertIsNot(f.anzeigezeilen(), gemerkt)

    def test_bildlauf_zaehlt_umgebrochene_zeilen(self) -> None:
        f = _baue(verlauf=[("A", "wort " * 200, "12:00")])  # ein Eintrag, viele Zeilen
        f.bei_rad(120, 0, 0, 0)
        f.bei_rad(120, 0, 0, 0)
        self.assertEqual(f._bildlauf_versatz, 2)  # ein Eintrag allein würde nur 0 erlauben

    def test_zeilenhoehe_ist_die_der_groesseren_schrift(self) -> None:
        self.assertEqual(_baue()._zeilenhoehe(), 22)


class NuanceTests(unittest.TestCase):
    def test_mischen_liegt_zwischen_farbe_und_ziel(self) -> None:
        rot, weiss = w.rgb(200, 0, 0), w.rgb(255, 255, 255)
        gemischt = stil.mischen(rot, weiss, 0.5)
        self.assertEqual(gemischt, w.rgb(228, 128, 128))
        self.assertEqual(stil.mischen(rot, weiss, 0.0), rot)
        self.assertEqual(stil.mischen(rot, weiss, 1.0), weiss)

    def test_nachrichtentext_ist_eine_andere_nuance_als_der_kopf(self) -> None:
        farbe = w.rgb(0, 229, 255)
        self.assertNotEqual(stil.mischen(farbe, stil.FARBE_TEXT, 0.45), farbe)


class RollbalkenSprungTests(unittest.TestCase):
    BEREICH = (300, 24, 310, 200)  # Streifen rechts, 176 px hoch

    def test_kein_griff_wenn_alles_sichtbar_ist(self) -> None:
        self.assertIsNone(griff_rechteck(5, 10, 0, self.BEREICH))

    def test_griff_unten_bei_versatz_null_und_oben_beim_aeltesten(self) -> None:
        unten = griff_rechteck(100, 10, 0, self.BEREICH)
        oben = griff_rechteck(100, 10, 90, self.BEREICH)
        self.assertEqual(unten[3], self.BEREICH[3])
        self.assertEqual(oben[1], self.BEREICH[1])

    def test_griff_hat_eine_mindesthoehe(self) -> None:
        griff = griff_rechteck(100000, 10, 0, self.BEREICH)
        self.assertGreaterEqual(griff[3] - griff[1], 20)

    def test_versatz_fuer_oben_unten_und_mitte(self) -> None:
        self.assertEqual(versatz_fuer(0, 0, 100, 10, self.BEREICH), 90)  # ganz oben
        self.assertEqual(versatz_fuer(10_000, 0, 100, 10, self.BEREICH), 0)  # ganz unten
        mitte = versatz_fuer(112, 0, 100, 10, self.BEREICH)
        self.assertTrue(30 < mitte < 60)

    def test_sprung_hoch_stellt_den_anfang_der_vorigen_nachricht_nach_oben(self) -> None:
        anfaenge = [0, 5, 12, 20]  # 30 Zeilen, 8 sichtbar; unten: oben-Index = 22
        versatz = sprung_versatz(anfaenge, 30, 8, 0, True)
        oben = 30 - versatz - 8
        self.assertEqual(oben, 20)  # Anfang der letzten Nachricht
        versatz = sprung_versatz(anfaenge, 30, 8, versatz, True)
        self.assertEqual(30 - versatz - 8, 12)
        versatz = sprung_versatz(anfaenge, 30, 8, versatz, True)
        self.assertEqual(30 - versatz - 8, 5)

    def test_sprung_hoch_mitten_in_einer_nachricht_geht_an_ihren_eigenen_anfang(self) -> None:
        anfaenge = [0, 10, 20]
        versatz = 30 - 14 - 8  # oben steht Zeile 14, mitten in der Nachricht ab 10
        self.assertEqual(30 - sprung_versatz(anfaenge, 30, 8, versatz, True) - 8, 10)

    def test_sprung_hoch_am_anfang_bleibt_am_anfang(self) -> None:
        anfaenge = [0, 10, 20]
        versatz = sprung_versatz(anfaenge, 30, 8, 22, True)
        self.assertEqual(versatz, 22)  # oben steht schon Zeile 0

    def test_sprung_runter_geht_zur_naechsten_und_hinter_der_letzten_nach_unten(self) -> None:
        anfaenge = [0, 10, 20]
        self.assertEqual(30 - sprung_versatz(anfaenge, 30, 8, 22, False) - 8, 10)
        self.assertEqual(sprung_versatz(anfaenge, 30, 8, 2, False), 0)  # oben steht Zeile 20 = letzter Anfang: nichts danach → unten
        self.assertEqual(sprung_versatz(anfaenge, 30, 8, 0, False), 0)

    def test_sprung_bei_kurzem_verlauf_bleibt_unten(self) -> None:
        self.assertEqual(sprung_versatz([0, 2], 4, 10, 0, True), 0)

    def test_kopfknoepfe_ueberlappen_nicht_und_empfaenger_bleibt_breit_genug(self) -> None:
        for breite in (200, 320, 600):
            r = kopf_rechtecke(breite)
            self.assertLessEqual(r["hoch"][2], r["runter"][0])
            self.assertLessEqual(r["runter"][2], r["deckkraft"][0])
            self.assertLess(r["empfaenger"][0], r["empfaenger"][2])


class RollbalkenFensterTests(unittest.TestCase):
    def _fenster(self):
        f = _baue(verlauf=[("A", f"nachricht {i}", "12:00") for i in range(60)])
        f._eingabe_hoehe = Mock(return_value=26)
        return f

    def test_klick_in_die_leiste_oben_blaettert_zurueck_und_hoch_runter_springen(self) -> None:
        f = self._fenster()
        l, o, r, u = f._balken_bereich()
        f.bei_maus_runter(l + 3, o + 2, 1)
        self.assertGreater(f._bildlauf_versatz, 20)
        f.bei_maus_hoch(l + 3, o + 2, 0)
        self.assertIsNone(f._balken_ziehen)

    def test_ziehen_am_griff(self) -> None:
        f = self._fenster()
        griff = f._griff()
        mitte = (griff[1] + griff[3]) // 2
        f.bei_maus_runter(griff[0] + 2, mitte, 1)
        self.assertEqual(f._bildlauf_versatz, 0)
        f.bei_maus_bewegt(griff[0] + 2, mitte - 40, 0x0001)
        self.assertGreater(f._bildlauf_versatz, 0)
        f.bei_maus_hoch(0, 0, 0)

    def test_hochknopf_springt_zur_vorigen_nachricht(self) -> None:
        f = self._fenster()
        a, b, c, d = kopf_rechtecke(320)["hoch"]
        f.bei_maus_runter(a + 2, b + 2, 1)
        self.assertGreater(f._bildlauf_versatz, 0)
        runter = kopf_rechtecke(320)["runter"]
        f.bei_maus_runter(runter[0] + 2, runter[1] + 2, 1)
        self.assertEqual(f._bildlauf_versatz, 0)

    def test_der_text_reicht_nicht_unter_den_rollbalken(self) -> None:
        f = _baue(verlauf=[("A", "x" * 300, "12:00")])
        breite, _ = f.clientgroesse()
        balken = rollbalken_rechteck(breite, 220, 26)
        self.assertTrue(all((f._messen_kopf(k + " ") if k else 0) + f._messen(t) <= balken[0] for _, k, t in f.anzeigezeilen()))


class GatingTests(unittest.TestCase):
    def test_konstruktor_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            ChatFenster(0, 0)


class EmpfangenUndSendenTests(unittest.TestCase):
    def test_empfangen_haengt_an_und_springt_ans_ende_des_verlaufs(self) -> None:
        f = _baue(_bildlauf_versatz=5)
        f.empfangen("codex", "Shader kompiliert!")
        self.assertEqual(f.verlauf, [("codex", "Shader kompiliert!", "12:00")])
        self.assertEqual(f._bildlauf_versatz, 0)
        f.neu_zeichnen.assert_called_once_with()

    def test_senden_gibt_den_text_an_den_besitzer_und_traegt_selbst_nichts_ein(self) -> None:
        f = _baue()
        f.eingabe = "  hallo agent  "
        f.senden()
        self.assertEqual(f.verlauf, [])  # der Besitzer trägt ihn mit Empfänger ein und zeigt ihn auf dem Bildschirm
        f._gesendet.assert_called_once_with("hallo agent")
        self.assertEqual(f.eingabe, "")

    def test_senden_mit_leerer_eingabe_tut_nichts(self) -> None:
        f = _baue()
        f.eingabe = "   "
        f.senden()
        self.assertEqual(f.verlauf, [])
        f._gesendet.assert_not_called()


class TastaturTests(unittest.TestCase):
    def test_zeichen_werden_an_die_eingabe_angehaengt(self) -> None:
        f = _baue()
        f.bei_zeichen(ord("h"), False)
        f.bei_zeichen(ord("i"), False)
        self.assertEqual(f.eingabe, "hi")

    def test_backspace_loescht_das_letzte_zeichen(self) -> None:
        f = _baue(eingabe="hallo")
        f.bei_zeichen(0x08, False)
        self.assertEqual(f.eingabe, "hall")

    def test_backspace_auf_leerer_eingabe_bricht_nicht(self) -> None:
        f = _baue(eingabe="")
        f.bei_zeichen(0x08, False)
        self.assertEqual(f.eingabe, "")

    def test_enter_sendet_und_leert_die_eingabe(self) -> None:
        f = _baue(eingabe="hallo")
        f.bei_zeichen(0x0D, False)
        f._gesendet.assert_called_once_with("hallo")
        self.assertEqual(f.eingabe, "")

    def test_steuerzeichen_unter_0x20_werden_ignoriert(self) -> None:
        f = _baue()
        f.bei_zeichen(0x1B, False)  # Escape
        self.assertEqual(f.eingabe, "")

    def test_verirrte_ersatzzeichen_landen_nicht_in_der_eingabe(self) -> None:
        f = _baue()
        f.bei_zeichen(0xD83D, False)
        self.assertEqual(f.eingabe, "")


class BildlaufTests(unittest.TestCase):
    def test_rad_blaettert_zurueck_und_wieder_vor(self) -> None:
        f = _baue(verlauf=[("a", str(i), "12:00") for i in range(50)])  # mehr Zeilen als sichtbar, damit Blaettern etwas bewegt
        f.bei_rad(120, 0, 0, 0)
        self.assertEqual(f._bildlauf_versatz, 1)
        f.bei_rad(-120, 0, 0, 0)
        self.assertEqual(f._bildlauf_versatz, 0)

    def test_rad_kappt_am_anfang_des_verlaufs(self) -> None:
        f = _baue(verlauf=[("a", "eins", "12:00")])
        f.bei_rad(120, 0, 0, 0)
        f.bei_rad(120, 0, 0, 0)
        self.assertEqual(f._bildlauf_versatz, maximaler_versatz(1, f.zeilen_sichtbar()))

    def test_rad_kappt_bei_null_statt_negativ_zu_werden(self) -> None:
        f = _baue(verlauf=[("a", "eins", "12:00")])
        f.bei_rad(-120, 0, 0, 0)
        self.assertEqual(f._bildlauf_versatz, 0)


class FokusUndTimerTests(unittest.TestCase):
    def test_timer_cursor_zeichnet_nur_bei_fokus_neu(self) -> None:
        f = _baue(_hat_fokus=False)
        f.bei_timer(TIMER_CURSOR)
        f.neu_zeichnen.assert_not_called()

        f2 = _baue(_hat_fokus=True)
        f2.bei_timer(TIMER_CURSOR)
        f2.neu_zeichnen.assert_called_once_with()

    def test_bei_fokus_setzt_den_zustand_und_zeichnet_neu(self) -> None:
        f = _baue()
        f.bei_fokus(True)
        self.assertTrue(f._hat_fokus)
        f.neu_zeichnen.assert_called_once_with()


class KopfUndKantenTests(unittest.TestCase):
    def test_kopfknoepfe_ueberlappen_nicht_und_liegen_im_kopf(self) -> None:
        r = kopf_rechtecke(320)
        self.assertLessEqual(r["empfaenger"][2], r["deckkraft"][0])
        for rechteck in r.values():
            self.assertTrue(0 <= rechteck[1] < rechteck[3] <= KOPF_H and rechteck[2] <= 320)

    def test_kanten_liefern_groessenaenderungs_trefferwerte(self) -> None:
        self.assertEqual(kante_bei(0, 0, 320, 220), w.HTTOPLEFT)
        self.assertEqual(kante_bei(319, 219, 320, 220), w.HTBOTTOMRIGHT)
        self.assertEqual(kante_bei(0, 100, 320, 220), w.HTLEFT)
        self.assertEqual(kante_bei(160, 219, 320, 220), w.HTBOTTOM)
        self.assertIsNone(kante_bei(160, 100, 320, 220))

    def test_kopf_ist_zum_verschieben_die_knoepfe_nicht(self) -> None:
        f = _baue()
        self.assertEqual(f.treffer(10, 12), w.HTCAPTION)
        r = kopf_rechtecke(320)["deckkraft"]
        self.assertEqual(f.treffer((r[0] + r[2]) // 2, 12), w.HTCLIENT)
        self.assertEqual(f.treffer(100, 100), w.HTCLIENT)


class KopfKlickTests(unittest.TestCase):
    def test_klick_auf_empfaenger_wechselt_den_agenten(self) -> None:
        f = _baue()
        r = kopf_rechtecke(320)["empfaenger"]
        f.bei_maus_runter((r[0] + r[2]) // 2, 12, 0)
        f._empfaenger_wechseln.assert_called_once_with()

    def test_klick_auf_prozent_schaltet_die_deckkraft_weiter(self) -> None:
        f = _baue(deckkraft=stil.deckkraft_alpha(34))
        f.setze_deckkraft = Mock()
        r = kopf_rechtecke(320)["deckkraft"]
        f.bei_maus_runter((r[0] + r[2]) // 2, 12, 0)
        f.setze_deckkraft.assert_called_once_with(stil.deckkraft_alpha(50))

    def test_farbe_und_empfaenger_werden_gemerkt(self) -> None:
        f = _baue()
        f.farbe_setzen("Claude", 0x123456)
        f.empfaenger_setzen("Claude", 0x123456)
        self.assertEqual((f.farben["Claude"], f.empfaenger), (0x123456, "Claude"))


class AufraeumenTests(unittest.TestCase):
    def test_bei_zerstoert_gibt_die_schrift_frei(self) -> None:
        f = _baue()
        schrift = f.f_text
        f.bei_zerstoert()
        schrift.freigeben.assert_called_once_with()
        self.assertIsNone(f.f_text)


if __name__ == "__main__":
    unittest.main()
