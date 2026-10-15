"""Tests für koerper/terminal_fenster.py: Geometrie, Treffer, Maus-Auswahl, Tastatur- und Knopf-Routing.

`TerminalFenster.__init__` baut echte Win32-Fenster, DIBs und GDI-Schriften auf und braucht deshalb Windows (oder Wine).
Die eigentliche Fensterlogik – wo eine Kante ist, was ein Klick auslöst, wie Auswahl beim Ziehen wächst, wie Tasten und
Zeichen zu Bytes werden, wann Deckkraft oder Verlauf reagieren – ist reines Python auf `self`-Zustand. Für diese Tests
wird ein `TerminalFenster` daher per `object.__new__` ohne Konstruktor gebaut (siehe `_baue`) und mit genau der Geometrie
versehen, die ein echter Konstruktor auch berechnen würde; jede Methode der Win32-Basisklasse `Fenster`, die tatsächlich
eine DLL anfassen würde (`clientgroesse`, `rechteck`, `neu_zeichnen`, `erfasse_maus`, `gib_maus_frei`, `setze_deckkraft`,
`starte_timer`, `stoppe_timer`, `mauszeiger`, `maus_position`), wird pro Instanz durch einen Stub ersetzt.
"""

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock, patch

from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper import terminal_fenster as tf
from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.terminal_fenster import TerminalFenster

# Geometrie, wie sie TerminalFenster.__init__ bei DPI=96 (GRUNDDPI, Faktor 1) tatsächlich berechnen würde.
ZEILEN, SPALTEN = 24, 80
RAND, PAD, TITEL_H, UNTEN_H, KNOPF = 5, 4, 28, 26, 20
ZELL_B, ZELL_H = 8, 16
ROLLBALKEN_B = 10
BREITE = 2 * (RAND + PAD) + SPALTEN * ZELL_B + ROLLBALKEN_B
HOEHE = TITEL_H + UNTEN_H + 2 * PAD + ZEILEN * ZELL_H


def _baue(*, zeilen: int = ZEILEN, spalten: int = SPALTEN, **overrides) -> TerminalFenster:
    f = object.__new__(TerminalFenster)
    f.name, f.ort, f.farbe_hex = "codex", "vd1", "#FFD600"
    f.farbe = w.rgb_hex(f.farbe_hex)
    f.zustand = "läuft"
    f.ziel_text, f.ziel_gebunden = "Ziel: Desktop (ungebunden)", False
    f._senden = Mock()
    f._groesse_gemeldet = Mock()
    f._schliessen = Mock()
    f._verbergen = Mock()
    f._scanner = Mock()
    f._layout_geaendert = Mock()
    f.modell = tf.TerminalModell(zeilen, spalten, antwort=f._senden)
    f._gemeldet = (zeilen, spalten)
    f._hat_fokus = False
    f._cursor_phase = True
    f._zeichnen_geplant = False
    f._char_unterdruecken = False
    f._hohes_ersatzzeichen = 0
    f._auswahl_anker = None
    f._ziehen = False
    f._ersatz = {}
    f._knopf_unten = None
    f.dpi = 96
    f.zell_b, f.zell_h = ZELL_B, ZELL_H
    f.titel_h, f.unten_h, f.rand, f.pad, f.knopf = TITEL_H, UNTEN_H, RAND, PAD, KNOPF
    f.rollbalken_b = ROLLBALKEN_B
    f._balken_ziehen = None
    f._maus_y = 0
    f.stoppe_timer = Mock()
    f.hwnd = 999
    f.deckkraft = stil.deckkraft_alpha(stil.DECKKRAFT_START_PROZENT)
    f.leinwand = None
    f._timer = {}

    breite = 2 * (RAND + PAD) + spalten * ZELL_B + ROLLBALKEN_B
    hoehe = TITEL_H + UNTEN_H + 2 * PAD + zeilen * ZELL_H
    f.clientgroesse = Mock(return_value=(breite, hoehe))
    f.rechteck = Mock(return_value=(0, 0, breite, hoehe))
    f.neu_zeichnen = Mock()
    f.erfasse_maus = Mock()
    f.gib_maus_frei = Mock()
    f.setze_deckkraft = Mock(side_effect=lambda alpha: setattr(f, "deckkraft", max(0, min(255, int(alpha)))))
    f.starte_timer = Mock()
    f.stoppe_timer = Mock()
    f.mauszeiger = Mock()
    f.maus_position = Mock(return_value=(0, 0))
    f._umschalter = Mock(return_value=(False, False, False))  # (umschalt, alt, strg)
    for name, wert in overrides.items():
        setattr(f, name, wert)
    return f


class GeometrieTests(unittest.TestCase):
    def test_gitter_rechteck_zieht_rand_titel_und_leiste_ab(self) -> None:
        f = _baue()
        self.assertEqual(f.gitter_rechteck(), (RAND + PAD, TITEL_H + PAD, BREITE - RAND - PAD - ROLLBALKEN_B, HOEHE - UNTEN_H - PAD))

    def test_zeilen_spalten_ist_zum_konstruktor_passend_umgekehrt(self) -> None:
        f = _baue()
        self.assertEqual(f.zeilen_spalten(), (ZEILEN, SPALTEN))

    def test_knopf_rechtecke_liegen_von_rechts_nach_links_ohne_ueberlappung(self) -> None:
        f = _baue()
        rechtecke = f.knopf_rechtecke()
        schliessen, verbergen, deckkraft = rechtecke["schliessen"], rechtecke["verbergen"], rechtecke["deckkraft"]
        self.assertEqual(schliessen[2], BREITE - RAND)
        self.assertLessEqual(verbergen[2], schliessen[0])
        self.assertLessEqual(deckkraft[2], verbergen[0])
        for rect in rechtecke.values():
            self.assertLess(rect[0], rect[2])
            self.assertLess(rect[1], rect[3])

    def test_scanner_rechteck_sitzt_unten_rechts_in_der_leiste(self) -> None:
        f = _baue()
        a, b, c, d = f.scanner_rechteck()
        self.assertGreaterEqual(b, HOEHE - UNTEN_H)
        self.assertLess(d, HOEHE)
        self.assertLess(c, BREITE - RAND)

    def test_zelle_bei_rechnet_pixel_in_zeile_spalte_um(self) -> None:
        f = _baue()
        links, oben, _, _ = f.gitter_rechteck()
        self.assertEqual(f.zelle_bei(links + 5 * ZELL_B + 3, oben + 3 * ZELL_H + 2), (3, 5))

    def test_zelle_bei_kappt_am_gitterrand(self) -> None:
        f = _baue()
        self.assertEqual(f.zelle_bei(-1000, -1000), (0, 0))
        self.assertEqual(f.zelle_bei(100000, 100000), (ZEILEN - 1, SPALTEN - 1))


class TrefferTests(unittest.TestCase):
    def test_ecken_liefern_diagonale_resize_treffer(self) -> None:
        f = _baue()
        self.assertEqual(f.treffer(0, 0), w.HTTOPLEFT)
        self.assertEqual(f.treffer(BREITE - 1, 0), w.HTTOPRIGHT)
        self.assertEqual(f.treffer(0, HOEHE - 1), w.HTBOTTOMLEFT)
        self.assertEqual(f.treffer(BREITE - 1, HOEHE - 1), w.HTBOTTOMRIGHT)

    def test_kanten_liefern_geraden_resize_treffer(self) -> None:
        f = _baue()
        mitte_x = BREITE // 2
        self.assertEqual(f.treffer(mitte_x, 0), w.HTTOP)
        self.assertEqual(f.treffer(mitte_x, HOEHE - 1), w.HTBOTTOM)
        self.assertEqual(f.treffer(0, HOEHE // 2), w.HTLEFT)
        self.assertEqual(f.treffer(BREITE - 1, HOEHE // 2), w.HTRIGHT)

    def test_titelleiste_ausserhalb_der_knoepfe_ist_die_zugflaeche(self) -> None:
        f = _baue()
        self.assertEqual(f.treffer(RAND + 20, TITEL_H // 2), w.HTCAPTION)

    def test_titelleiste_ueber_einem_knopf_ist_kein_zug(self) -> None:
        f = _baue()
        a, b, c, d = f.knopf_rechtecke()["schliessen"]
        self.assertEqual(f.treffer((a + c) // 2, (b + d) // 2), w.HTCLIENT)

    def test_das_gitter_selbst_ist_htclient(self) -> None:
        f = _baue()
        links, oben, _, _ = f.gitter_rechteck()
        self.assertEqual(f.treffer(links + 10, oben + 10), w.HTCLIENT)


class MausAuswahlTests(unittest.TestCase):
    def setUp(self) -> None:
        # bei_maus_runter ruft SetFocus direkt über w.user32 auf (kein Stub auf der Instanz möglich).
        patcher = patch.object(w, "user32", Mock())
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rechtsklick(self, wahl: int, auswahl: bool = False):
        f = _baue(hwnd=1, neu_zeichnen=Mock(), kopieren=Mock(), einfuegen=Mock())
        f._im_gitter = Mock(return_value=True)
        if auswahl:
            f.modell.einspeisen(b"hallo")
            f.modell.auswahl_setzen((0, 0), (0, 3))
        with patch("augen_haende_bridge.koerper.terminal_fenster.zeige_menue", return_value=wahl) as menue:
            f.bei_rechtsklick(10, 20, 0)
        return f, menue

    def test_rechtsklick_zeigt_ein_menue_an_der_klickstelle(self) -> None:
        f, menue = self._rechtsklick(0)
        eintraege = menue.call_args.args[1]
        self.assertEqual([e[1] for e in eintraege if e], ["Kopieren", "Einfügen", "Alles markieren", "Auswahl aufheben"])
        self.assertEqual(menue.call_args.args[2:], (10, 20))
        f.kopieren.assert_not_called()
        f.einfuegen.assert_not_called()

    def test_menue_wird_an_der_bildschirmstelle_gezeigt_nicht_in_fensterkoordinaten(self) -> None:
        f = _baue(hwnd=1, neu_zeichnen=Mock())
        f.rechteck = Mock(return_value=(500, 300, 500 + BREITE, 300 + HOEHE))
        f._im_gitter = Mock(return_value=True)
        with patch("augen_haende_bridge.koerper.terminal_fenster.zeige_menue", return_value=0) as menue:
            f.bei_rechtsklick(10, 20, 0)
        self.assertEqual(menue.call_args.args[2:], (510, 320))

    def test_rechtsklick_ohne_auswahl_graut_kopieren_aus(self) -> None:
        _, menue = self._rechtsklick(0)
        eintraege = [e for e in menue.call_args.args[1] if e]
        self.assertTrue(eintraege[0][2])  # Kopieren abgeblendet
        self.assertFalse(eintraege[1][2])

    def test_rechtsklick_menuepunkte_fuehren_aus(self) -> None:
        f, _ = self._rechtsklick(TerminalFenster.MENUE_KOPIEREN, auswahl=True)
        f.kopieren.assert_called_once_with()
        f, _ = self._rechtsklick(TerminalFenster.MENUE_EINFUEGEN)
        f.einfuegen.assert_called_once_with()
        f, _ = self._rechtsklick(TerminalFenster.MENUE_ALLES)
        self.assertIsNotNone(f.modell.auswahl)
        f, _ = self._rechtsklick(TerminalFenster.MENUE_AUFHEBEN, auswahl=True)
        self.assertIsNone(f.modell.auswahl)

    def test_rechtsklick_ausserhalb_des_gitters_tut_nichts(self) -> None:
        f = _baue(hwnd=1)
        f._im_gitter = Mock(return_value=False)
        with patch("augen_haende_bridge.koerper.terminal_fenster.zeige_menue") as menue:
            f.bei_rechtsklick(1, 1, 0)
        menue.assert_not_called()

    def test_klick_und_ziehen_im_gitter_baut_eine_auswahl_auf(self) -> None:
        f = _baue()
        links, oben, _, _ = f.gitter_rechteck()
        start = (links + 5 * ZELL_B + 2, oben + 3 * ZELL_H + 2)
        ende = (links + 10 * ZELL_B + 2, oben + 3 * ZELL_H + 2)
        f.bei_maus_runter(*start, 0)
        self.assertEqual(f._auswahl_anker, (3, 5))
        f.erfasse_maus.assert_called_once_with()
        f.bei_maus_bewegt(*ende, 0x0001)
        self.assertTrue(f._ziehen)
        self.assertEqual(f.modell.auswahl, ((3, 5), (3, 11)))
        f.bei_maus_hoch(*ende, 0)
        self.assertIsNone(f._auswahl_anker)
        self.assertEqual(f.modell.auswahl, ((3, 5), (3, 11)))  # eine gezogene Auswahl bleibt nach Loslassen stehen
        f.gib_maus_frei.assert_called_once_with()

    def test_klick_ohne_bewegung_hinterlaesst_keine_auswahl(self) -> None:
        f = _baue()
        links, oben, _, _ = f.gitter_rechteck()
        punkt = (links + ZELL_B, oben + ZELL_H)
        f.bei_maus_runter(*punkt, 0)
        f.bei_maus_hoch(*punkt, 0)
        self.assertFalse(f._ziehen)
        self.assertIsNone(f.modell.auswahl)

    def test_klick_ausserhalb_von_gitter_und_knoepfen_ist_wirkungslos(self) -> None:
        f = _baue()
        f.modell.auswahl_setzen((0, 0), (0, 3))
        f.bei_maus_runter(RAND + 20, TITEL_H // 2, 0)  # Titelzugfläche, kein Knopf, kein Gitter
        self.assertIsNone(f._auswahl_anker)
        self.assertEqual(f.modell.auswahl, ((0, 0), (0, 3)))  # unangetastet

    def test_doppelklick_waehlt_das_wort_unter_dem_cursor(self) -> None:
        f = _baue()
        f.modell.einspeisen(b"hallo welt")
        links, oben, _, _ = f.gitter_rechteck()
        f.bei_doppelklick(links + 2 * ZELL_B, oben, 0)
        self.assertEqual(f.modell.auswahl_text(), "hallo")


class KnopfTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch.object(w, "user32", Mock())
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_schliessen_knopf_loest_erst_beim_loslassen_ueber_demselben_knopf_aus(self) -> None:
        f = _baue()
        a, b, c, d = f.knopf_rechtecke()["schliessen"]
        mitte = ((a + c) // 2, (b + d) // 2)
        f.bei_maus_runter(*mitte, 0)
        self.assertEqual(f._knopf_unten, "schliessen")
        f.bei_maus_hoch(*mitte, 0)
        f._schliessen.assert_called_once_with()
        self.assertIsNone(f._knopf_unten)

    def test_wegziehen_vor_dem_loslassen_verhindert_das_ausloesen(self) -> None:
        f = _baue()
        a, b, c, d = f.knopf_rechtecke()["schliessen"]
        f.bei_maus_runter((a + c) // 2, (b + d) // 2, 0)
        f.bei_maus_hoch(0, 0, 0)  # weit weg vom Knopf losgelassen
        f._schliessen.assert_not_called()
        self.assertIsNone(f._knopf_unten)

    def test_verbergen_knopf_ruft_verbergen_gewuenscht(self) -> None:
        f = _baue()
        a, b, c, d = f.knopf_rechtecke()["verbergen"]
        mitte = ((a + c) // 2, (b + d) // 2)
        f.bei_maus_runter(*mitte, 0)
        f.bei_maus_hoch(*mitte, 0)
        f._verbergen.assert_called_once_with()

    def test_deckkraft_knopf_springt_zur_naechsten_stufe(self) -> None:
        f = _baue()
        self.assertEqual(f.deckkraft_prozent(), stil.DECKKRAFT_START_PROZENT)
        f._knopf_ausloesen("deckkraft")
        self.assertEqual(f.deckkraft_prozent(), stil.naechste_stufe(stil.DECKKRAFT_START_PROZENT))
        f._layout_geaendert.assert_called_once_with()

    def test_scanner_knopf_meldet_absolute_bildschirmkoordinaten(self) -> None:
        f = _baue(rechteck=Mock(return_value=(100, 200, 100 + BREITE, 200 + HOEHE)))
        a, b, _, _ = f.scanner_rechteck()
        f._knopf_ausloesen("scanner")
        f._scanner.assert_called_once_with(100 + a, 200 + b)

    def test_scanner_verbinden_ersetzt_den_scanner_callback_nachtraeglich(self) -> None:
        f = _baue(rechteck=Mock(return_value=(100, 200, 100 + BREITE, 200 + HOEHE)))
        alter_callback = f._scanner
        neuer_callback = Mock()
        f.scanner_verbinden(neuer_callback)
        f._knopf_ausloesen("scanner")
        neuer_callback.assert_called_once()
        alter_callback.assert_not_called()  # der alte, in _baue() gesetzte Callback wurde wirklich ersetzt


class RadTests(unittest.TestCase):
    def test_rad_ueber_dem_titel_aendert_die_deckkraft(self) -> None:
        f = _baue()
        vorher = f.deckkraft_prozent()
        f.bei_rad(120, RAND + 5, TITEL_H // 2, 0)
        self.assertEqual(f.deckkraft_prozent(), min(100, vorher + 5))
        f._layout_geaendert.assert_called_once_with()

    def test_rad_ueber_dem_titel_kappt_bei_10_prozent(self) -> None:
        f = _baue()
        f.setze_deckkraft(stil.deckkraft_alpha(10))
        f.bei_rad(-120, RAND + 5, TITEL_H // 2, 0)
        self.assertGreaterEqual(f.deckkraft_prozent(), 10)

    def test_rad_ueber_dem_gitter_blaettert_den_verlauf(self) -> None:
        f = _baue()
        f.modell.blaettern_zeilen = Mock()
        links, oben, _, _ = f.gitter_rechteck()
        f.bei_rad(120, links + 5, oben + 5, 0)
        f.modell.blaettern_zeilen.assert_called_once_with(3)
        f.bei_rad(-120, links + 5, oben + 5, 0)
        f.modell.blaettern_zeilen.assert_called_with(-3)


class RollbalkenTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch.object(w, "user32", Mock())  # bei_maus_runter ruft SetFocus direkt über w.user32 auf
        patcher.start()
        self.addCleanup(patcher.stop)

    def _mit_verlauf(self, zeilen_text: int = 100):
        f = _baue()
        f.modell.einspeisen(b"".join(b"zeile %d\r\n" % i for i in range(zeilen_text)))
        return f

    def test_ohne_verlauf_gibt_es_keinen_griff(self) -> None:
        self.assertIsNone(_baue().griff_rechteck())

    def test_griff_sitzt_unten_und_waechst_mit_dem_sichtbaren_anteil(self) -> None:
        f = self._mit_verlauf()
        _, oben, _, unten = f.rollbalken_rechteck()
        griff = f.griff_rechteck()
        self.assertEqual(griff[3], unten)  # ganz unten = Gegenwart
        self.assertGreaterEqual(griff[3] - griff[1], 24)
        f.modell.zu_versatz(f.modell.verlauf_laenge())
        self.assertEqual(f.griff_rechteck()[1], oben)  # ganz oben = ältester Verlauf

    def test_rollbalken_liegt_im_eigenen_streifen_und_nicht_im_gitter(self) -> None:
        f = _baue()
        self.assertLessEqual(f.gitter_rechteck()[2], f.rollbalken_rechteck()[0])
        self.assertEqual(f.zeilen_spalten()[1], SPALTEN)

    def test_klick_in_die_leiste_oben_blaettert_zurueck(self) -> None:
        f = self._mit_verlauf()
        _, oben, rechts_a, _ = f.rollbalken_rechteck()
        links = f.rollbalken_rechteck()[0]
        f.bei_maus_runter(links + 3, oben + 2, 1)
        self.assertGreater(f.modell.verlauf_versatz(), f.modell.verlauf_laenge() // 2)
        f.bei_maus_hoch(links + 3, oben + 2, 0)
        self.assertIsNone(f._balken_ziehen)

    def test_ziehen_am_griff_folgt_der_maus_ohne_zu_springen(self) -> None:
        f = self._mit_verlauf()
        griff = f.griff_rechteck()
        x = griff[0] + 2
        mitte_y = (griff[1] + griff[3]) // 2
        f.bei_maus_runter(x, mitte_y, 1)
        self.assertEqual(f.modell.verlauf_versatz(), 0)  # nur gepackt
        f.bei_maus_bewegt(x, mitte_y - 40, 0x0001)
        self.assertGreater(f.modell.verlauf_versatz(), 0)
        f.bei_maus_hoch(x, mitte_y - 40, 0)

    def test_rad_blaettert_um_drei_zeilen(self) -> None:
        f = self._mit_verlauf()
        links, oben, _, _ = f.gitter_rechteck()
        f.bei_rad(120, links + 5, oben + 5, 0)
        self.assertEqual(f.modell.verlauf_versatz(), 3)
        f.bei_rad(-120, links + 5, oben + 5, 0)
        self.assertEqual(f.modell.verlauf_versatz(), 0)

    def test_rad_geht_an_das_programm_wenn_es_mausereignisse_angefordert_hat(self) -> None:
        f = self._mit_verlauf()
        f.modell.einspeisen(b"\x1b[?1000h\x1b[?1006h")
        links, oben, _, _ = f.gitter_rechteck()
        f.bei_rad(120, links + 5, oben + 5, 0)
        f._senden.assert_called_once_with(b"\x1b[<64;1;1M" * 3)
        self.assertEqual(f.modell.verlauf_versatz(), 0)  # selbst nicht geblättert

    def test_markieren_ueber_den_unteren_rand_blaettert_vor_und_waechst(self) -> None:
        f = self._mit_verlauf()
        f.modell.zu_versatz(9)
        links, oben, _, unten = f.gitter_rechteck()
        f.bei_maus_runter(links + 2, oben + 2 * ZELL_H + 1, 1)
        f.bei_maus_bewegt(links + 40, unten + 30, 0x0001)
        f.starte_timer.assert_called_with(4, 60)
        f._maus_y = unten + 30
        f._autoscroll()
        self.assertEqual(f.modell.verlauf_versatz(), 6)
        self.assertIsNotNone(f.modell.auswahl)

    def test_autoscroll_stoppt_ohne_anker(self) -> None:
        f = _baue()
        f._autoscroll()
        f.stoppe_timer.assert_called_with(4)


class TastaturTests(unittest.TestCase):
    def test_pfeiltaste_ohne_modifikator_sendet_die_reine_xterm_folge(self) -> None:
        f = _baue()
        f.bei_taste(w.VK_LEFT, 0, False)
        f._senden.assert_called_once_with(b"\x1b[D")

    def test_altgr_wird_nicht_als_strg_alt_modifikator_gewertet(self) -> None:
        f = _baue(_umschalter=Mock(return_value=(False, True, True)))  # AltGr = Alt+Strg gemeinsam
        f.bei_taste(w.VK_LEFT, 0, False)
        f._senden.assert_called_once_with(b"\x1b[D")  # keine Modifikatorfolge, wie ohne AltGr

    def test_strg_umschalt_c_kopiert_und_unterdrueckt_das_folgende_zeichen(self) -> None:
        f = _baue(_umschalter=Mock(return_value=(True, False, True)), kopieren=Mock())
        ergebnis = f.bei_taste(ord("C"), 0, False)
        f.kopieren.assert_called_once_with()
        self.assertTrue(f._char_unterdruecken)
        self.assertEqual(ergebnis, 0)

    def test_strg_umschalt_v_und_umschalt_einfuegen_fuegen_beide_ein(self) -> None:
        f = _baue(_umschalter=Mock(return_value=(True, False, True)), einfuegen=Mock())
        f.bei_taste(ord("V"), 0, False)
        f.einfuegen.assert_called_once_with()

        f2 = _baue(_umschalter=Mock(return_value=(True, False, False)), einfuegen=Mock())
        f2.bei_taste(w.VK_INSERT, 0, False)
        f2.einfuegen.assert_called_once_with()

    def test_umschalt_tab_setzt_unterdrueckung_normale_tab_nicht(self) -> None:
        f = _baue(_umschalter=Mock(return_value=(True, False, False)))
        f.bei_taste(w.VK_TAB, 0, False)
        self.assertTrue(f._char_unterdruecken)
        f._senden.assert_called_once_with(b"\x1b[Z")

        f2 = _baue()
        ergebnis = f2.bei_taste(w.VK_TAB, 0, False)
        self.assertFalse(f2._char_unterdruecken)
        f2._senden.assert_not_called()
        self.assertIsNone(ergebnis)

    def test_unbekannte_taste_ist_normal_unbehandelt_aber_als_systemtaste_verschluckt(self) -> None:
        f = _baue()
        self.assertIsNone(f.bei_taste(ord("Q"), 0, False))
        self.assertEqual(f.bei_taste(ord("Q"), 0, True), 0)

    def test_umschalt_strg_alt_selbst_loesen_nichts_aus(self) -> None:
        f = _baue()
        for vk in (w.VK_SHIFT, w.VK_CONTROL, w.VK_MENU):
            self.assertEqual(f.bei_taste(vk, 0, False), 0)
        f._senden.assert_not_called()


class ZeichenTests(unittest.TestCase):
    def test_normales_zeichen_wird_als_utf8_gesendet(self) -> None:
        f = _baue()
        f.bei_zeichen(ord("a"), False)
        f._senden.assert_called_once_with(b"a")

    def test_alt_zeichen_wird_mit_escape_vorangestellt(self) -> None:
        f = _baue()
        f.bei_zeichen(ord("a"), True)
        f._senden.assert_called_once_with(b"\x1ba")

    def test_unterdruecktes_zeichen_nach_strg_umschalt_v_wird_verschluckt(self) -> None:
        f = _baue()
        f._char_unterdruecken = True
        f.bei_zeichen(ord("v"), False)
        f._senden.assert_not_called()
        self.assertFalse(f._char_unterdruecken)  # nur einmal verschluckt

    def test_utf16_ersatzpaar_wird_zu_einem_zeichen_zusammengesetzt(self) -> None:
        f = _baue()
        hoch, tief = 0xD83D, 0xDE00  # 😀 U+1F600
        self.assertEqual(f.bei_zeichen(hoch, False), 0)
        f._senden.assert_not_called()
        f.bei_zeichen(tief, False)
        f._senden.assert_called_once_with("\U0001F600".encode("utf-8"))

    def test_verirrtes_tiefes_ersatzzeichen_ohne_vorlauf_erzeugt_keine_eingabe(self) -> None:
        f = _baue()
        f.bei_zeichen(0xDE00, False)
        f._senden.assert_not_called()


class VerlaufUndEingabeTests(unittest.TestCase):
    def test_eingabe_waehrend_im_verlauf_springt_zuerst_ans_ende(self) -> None:
        f = _baue(zeilen=5, spalten=20)
        for i in range(200):
            f.modell.einspeisen(f"zeile {i}\r\n".encode())
        f.modell.blaettern(1)
        self.assertTrue(f.modell.im_verlauf())
        f.tippe("x")
        self.assertFalse(f.modell.im_verlauf())
        f._senden.assert_called_once_with(b"x")


class ZwischenablageTests(unittest.TestCase):
    def test_kopieren_ohne_auswahl_fasst_die_zwischenablage_nicht_an(self) -> None:
        f = _baue()
        with patch.object(tf, "text_in_zwischenablage") as fake:
            self.assertFalse(f.kopieren())
            fake.assert_not_called()

    def test_kopieren_mit_auswahl_schreibt_in_die_zwischenablage(self) -> None:
        f = _baue()
        f.modell.einspeisen(b"abcdef")
        f.modell.auswahl_setzen((0, 0), (0, 3))
        with patch.object(tf, "text_in_zwischenablage", return_value=True) as fake:
            self.assertTrue(f.kopieren())
            fake.assert_called_once_with(f.hwnd, "abc")

    def test_einfuegen_mit_leerer_zwischenablage_sendet_nichts(self) -> None:
        f = _baue()
        with patch.object(tf, "text_aus_zwischenablage", return_value=""):
            f.einfuegen()
        f._senden.assert_not_called()

    def test_einfuegen_schickt_den_zwischenablagetext_als_eingabe(self) -> None:
        f = _baue()
        with patch.object(tf, "text_aus_zwischenablage", return_value="pasted"):
            f.einfuegen()
        f._senden.assert_called_once_with(b"pasted")


class GroesseUndTimerTests(unittest.TestCase):
    def test_bei_groesse_meldet_und_startet_den_entprellungs_timer_nur_bei_aenderung(self) -> None:
        f = _baue()
        f.clientgroesse = Mock(return_value=(BREITE + ZELL_B * 10, HOEHE))  # 10 Spalten breiter
        f.bei_groesse(0, 0)
        f.starte_timer.assert_called_once_with(tf.TIMER_GROESSE, 150)
        f._layout_geaendert.assert_called_once_with()

        f.starte_timer.reset_mock()
        f._layout_geaendert.reset_mock()
        f.modell.groesse_setzen(*f.zeilen_spalten())  # bereits auf dieser Größe: keine echte Änderung mehr
        f.bei_groesse(0, 0)
        f.starte_timer.assert_not_called()
        f._layout_geaendert.assert_called_once_with()

    def test_timer_zeichnen_setzt_den_zeichnen_geplant_zustand_zurueck(self) -> None:
        f = _baue()
        f._zeichnen_geplant = True
        f.bei_timer(tf.TIMER_ZEICHNEN)
        f.stoppe_timer.assert_called_once_with(tf.TIMER_ZEICHNEN)
        self.assertFalse(f._zeichnen_geplant)
        f.neu_zeichnen.assert_called_once_with()

    def test_timer_cursor_zeichnet_nur_bei_fokus_neu(self) -> None:
        f = _baue()
        f._hat_fokus = False
        f.bei_timer(tf.TIMER_CURSOR)
        f.neu_zeichnen.assert_not_called()
        self.assertFalse(f._cursor_phase)

        f._hat_fokus = True
        f.bei_timer(tf.TIMER_CURSOR)
        f.neu_zeichnen.assert_called_once_with()

    def test_timer_groesse_meldet_nur_eine_tatsaechlich_geaenderte_groesse(self) -> None:
        f = _baue()
        f.modell.groesse_setzen(30, 90)
        f.bei_timer(tf.TIMER_GROESSE)
        f._groesse_gemeldet.assert_called_once_with(30, 90)
        self.assertEqual(f._gemeldet, (30, 90))

        f._groesse_gemeldet.reset_mock()
        f.bei_timer(tf.TIMER_GROESSE)
        f._groesse_gemeldet.assert_not_called()

    def test_ausgabe_speist_das_modell_und_plant_hoechstens_einen_zeichentimer(self) -> None:
        f = _baue()
        f.ausgabe(b"hallo")
        self.assertEqual(f.modell.empfangen, 5)
        f.starte_timer.assert_called_once_with(tf.TIMER_ZEICHNEN, 16)
        f.ausgabe(b"welt")  # Zeichnen schon geplant: kein zweiter Timer
        f.starte_timer.assert_called_once_with(tf.TIMER_ZEICHNEN, 16)


class NachrichtRoutingTests(unittest.TestCase):
    def test_wm_getminmaxinfo_setzt_eine_mindestgroesse_von_20_spalten_und_4_zeilen(self) -> None:
        f = _baue()
        info = w.MINMAXINFO()
        f.bei_nachricht(w.WM_GETMINMAXINFO, 0, ctypes.addressof(info))
        self.assertEqual(info.ptMinTrackSize.x, 2 * (RAND + PAD) + 20 * ZELL_B)
        self.assertEqual(info.ptMinTrackSize.y, TITEL_H + UNTEN_H + 2 * PAD + 4 * ZELL_H)

    def test_wm_mouseactivate_aktiviert_immer(self) -> None:
        f = _baue()
        self.assertEqual(f.bei_nachricht(w.WM_MOUSEACTIVATE, 0, 0), w.MA_ACTIVATE)

    def test_wm_move_und_exitsizemove_melden_layoutaenderung(self) -> None:
        f = _baue()
        f.bei_nachricht(w.WM_MOVE, 0, 0)
        f.bei_nachricht(w.WM_EXITSIZEMOVE, 0, 0)
        self.assertEqual(f._layout_geaendert.call_count, 2)

    def test_wm_setcursor_zeigt_ibalken_im_gitter_und_pfeil_daneben(self) -> None:
        f = _baue()
        links, oben, _, _ = f.gitter_rechteck()
        f.maus_position = Mock(return_value=(links + 5, oben + 5))
        f.bei_nachricht(w.WM_SETCURSOR, 0, w.HTCLIENT)
        f.mauszeiger.assert_called_once_with(w.IDC_IBEAM)

        f2 = _baue()
        f2.maus_position = Mock(return_value=(0, 0))  # Titelzeile, außerhalb des Gitters
        f2.bei_nachricht(w.WM_SETCURSOR, 0, w.HTCLIENT)
        f2.mauszeiger.assert_called_once_with(w.IDC_ARROW)

    def test_bei_zerstoert_gibt_alle_schriften_frei(self) -> None:
        f = _baue()
        f.f_terminal, f.f_fett, f.f_ui = Mock(), Mock(), Mock()
        f.f_ersatz = [Mock(), Mock()]
        f.bei_zerstoert()
        f.f_terminal.freigeben.assert_called_once_with()
        f.f_fett.freigeben.assert_called_once_with()
        f.f_ui.freigeben.assert_called_once_with()
        for ersatz in f.f_ersatz:
            ersatz.freigeben.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
