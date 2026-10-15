"""Eingabefeld an der Raute: Tippen, Enter sendet, Esc bricht ab, Fokusverlust und Leerlauf schließen, Position."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper.eingabe_fenster import (
    BREITE,
    MAX_ZEICHEN,
    TIMER_CURSOR,
    TIMER_LEERLAUF,
    RauteEingabe,
    feld_position,
    sichtbarer_text,
)

BILDSCHIRM = (0, 0, 1920, 1080)


def baue(**ueber):
    f = object.__new__(RauteEingabe)
    f.name = "Claude"
    f.eingabe = ""
    f._cursor_phase = True
    f._hatte_fokus = False
    f._zu = False
    f._gesendet = Mock()
    f._abgebrochen = Mock()
    f._geschlossen = Mock()
    f.f_text = Mock(zellhoehe=18)
    f.hwnd = 5
    f.schliessen = Mock(side_effect=lambda: f.bei_zerstoert())
    f.neu_zeichnen = Mock()
    f.starte_timer = Mock()
    f.stoppe_timer = Mock()
    for k, v in ueber.items():
        setattr(f, k, v)
    return f


class PositionTests(unittest.TestCase):
    def test_rechts_neben_der_raute_auf_ihrer_mitte(self):
        self.assertEqual(feld_position((100, 200, 300, 252), 34, BILDSCHIRM), (308, 226 - 17 + 0))

    def test_am_rechten_rand_springt_es_nach_links(self):
        x, y = feld_position((1700, 200, 1900, 252), 34, BILDSCHIRM)
        self.assertEqual(x, 1700 - 8 - BREITE)

    def test_bleibt_auf_dem_bildschirm(self):
        x, y = feld_position((0, 1070, 100, 1080), 34, BILDSCHIRM)
        self.assertTrue(y + 34 <= 1080)
        x, y = feld_position((0, -50, 100, -10), 34, BILDSCHIRM)
        self.assertTrue(y >= 0)


class TextTests(unittest.TestCase):
    def test_kurzer_text_bleibt(self):
        self.assertEqual(sichtbarer_text("hallo", len, 10), "hallo")

    def test_langer_text_zeigt_das_ende(self):
        self.assertEqual(sichtbarer_text("abcdefghij", len, 4), "ghij")

    def test_leerer_text(self):
        self.assertEqual(sichtbarer_text("", len, 4), "")


class TippenTests(unittest.TestCase):
    def test_zeichen_werden_angehaengt_backspace_loescht(self):
        f = baue()
        for c in "Hi!":
            f.bei_zeichen(ord(c), False)
        f.bei_zeichen(0x08, False)
        self.assertEqual(f.eingabe, "Hi")

    def test_enter_sendet_den_text_einmal_und_schliesst(self):
        f = baue()
        for c in " Go! ":
            f.bei_zeichen(ord(c), False)
        f.bei_zeichen(0x0D, False)
        f._gesendet.assert_called_once_with("Go!")
        f.schliessen.assert_called_once()
        f._abgebrochen.assert_not_called()
        f.bei_zeichen(0x0D, False)  # nach dem Schließen nichts mehr
        f._gesendet.assert_called_once()

    def test_enter_ohne_text_laesst_das_feld_offen(self):
        f = baue()
        f.bei_zeichen(0x0D, False)
        f.bei_zeichen(ord(" "), False)
        f.bei_zeichen(0x0D, False)
        f._gesendet.assert_not_called()
        f.schliessen.assert_not_called()

    def test_escape_bricht_ab_ohne_zu_senden(self):
        f = baue()
        f.bei_zeichen(ord("x"), False)
        f.bei_zeichen(0x1B, False)
        f._gesendet.assert_not_called()
        f._abgebrochen.assert_called_once()
        f.schliessen.assert_called_once()

    def test_laenge_ist_begrenzt_und_steuerzeichen_zaehlen_nicht(self):
        f = baue()
        f.bei_zeichen(0x07, False)
        f.bei_zeichen(0xD83D, False)
        self.assertEqual(f.eingabe, "")
        f.eingabe = "a" * MAX_ZEICHEN
        f.bei_zeichen(ord("b"), False)
        self.assertEqual(len(f.eingabe), MAX_ZEICHEN)

    def test_jeder_tastendruck_setzt_den_leerlauf_zurueck(self):
        f = baue()
        f.bei_zeichen(ord("a"), False)
        f.stoppe_timer.assert_called_with(TIMER_LEERLAUF)
        f.starte_timer.assert_called_with(TIMER_LEERLAUF, unittest.mock.ANY)


class SchliessenTests(unittest.TestCase):
    def test_fokusverlust_schliesst_nach_dem_ersten_fokus_ohne_zu_senden(self):
        f = baue()
        f.bei_fokus(False)  # noch nie Fokus gehabt: darf nicht schließen (Fokus kommt erst)
        f.schliessen.assert_not_called()
        f.bei_fokus(True)
        f.bei_fokus(False)
        f.schliessen.assert_called_once()
        f._abgebrochen.assert_called_once()
        f._gesendet.assert_not_called()

    def test_leerlauf_schliesst(self):
        f = baue()
        f.bei_timer(TIMER_LEERLAUF)
        f.schliessen.assert_called_once()
        f._abgebrochen.assert_called_once()

    def test_cursor_blinkt_nur_solange_offen(self):
        f = baue()
        f.bei_timer(TIMER_CURSOR)
        f.neu_zeichnen.assert_called_once()
        f._zu = True
        f.bei_timer(TIMER_CURSOR)
        f.neu_zeichnen.assert_called_once()

    def test_schliessen_meldet_es_dem_besitzer_und_gibt_die_schrift_frei(self):
        f = baue()
        schrift = f.f_text
        f.bei_zerstoert()
        f._geschlossen.assert_called_once()
        schrift.freigeben.assert_called_once()

    def test_doppeltes_schliessen_wird_einmal_gemeldet(self):
        f = baue()
        f.bei_zeichen(ord("a"), False)
        f.bei_zeichen(0x1B, False)
        f.bei_fokus(True)
        f.bei_fokus(False)  # Fokusverlust beim Zerstören
        f._abgebrochen.assert_called_once()


class GatingTests(unittest.TestCase):
    def test_konstruktor_verlangt_windows(self):
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            RauteEingabe(0, 0, name="x", farbe_hex="#00E5FF")


if __name__ == "__main__":
    unittest.main()
