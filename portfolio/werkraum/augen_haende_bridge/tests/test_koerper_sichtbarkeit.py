"""Sichtbarkeitsregeln pro Fenster: Kanten, eigene Fenster vorn, Nutzer-Ausblenden, Regel-Datei."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.sichtbarkeit import (
    IMMER,
    Regel,
    Sichtbarkeit,
    Vordergrund,
    WindowsQuelle,
    dateiname,
    programm_regel,
)

EIGENE = 4242


class Quelle:
    def __init__(self):
        self.vorn = None

    def vordergrund(self):
        return self.vorn


def fremd(programm, titel="", pid=100):
    return Vordergrund(pid, programm, titel)


def baue():
    quelle = Quelle()
    s = Sichtbarkeit(quelle, eigene_pid=EIGENE)
    return s, quelle


class RegelTests(unittest.TestCase):
    def test_dict_rundlauf(self):
        r = programm_regel("Notepad.EXE", "Unbenannt - Editor")
        self.assertEqual(Regel.aus_dict(r.zu_dict()), r)
        self.assertEqual(r.programm, "notepad.exe")

    def test_kaputte_daten_werden_zu_immer(self):
        for daten in (None, 5, {}, {"modus": "programm"}, {"modus": "programm", "programm": "  "},
                      {"modus": "quatsch", "programm": "x.exe"}, {"modus": "programm", "programm": 7}):
            self.assertEqual(Regel.aus_dict(daten), IMMER)

    def test_text(self):
        self.assertEqual(IMMER.text(), "immer sichtbar")
        self.assertEqual(programm_regel("a.exe").text(), "nur bei a.exe")

    def test_dateiname_aus_windows_und_unix_pfad(self):
        self.assertEqual(dateiname("C:\\Games\\Foo\\Foo.EXE"), "foo.exe")
        self.assertEqual(dateiname("/usr/bin/x"), "x")
        self.assertEqual(dateiname(None), "")


class KantenTests(unittest.TestCase):
    def test_fenster_erscheint_nur_mit_seinem_programm(self):
        s, q = baue()
        f = Mock()
        s.registrieren("raute", f, programm_regel("spiel.exe"))
        q.vorn = fremd("spiel.exe")
        s.tick()
        f.zeige.assert_called_once_with(aktivieren=False)
        q.vorn = fremd("browser.exe")
        s.tick()
        f.verberge.assert_called_once_with()
        q.vorn = fremd("spiel.exe")
        s.tick()
        self.assertEqual(f.zeige.call_count, 2)

    def test_immer_sichtbar_wird_nie_angefasst(self):
        s, q = baue()
        f = Mock()
        s.registrieren("chat", f)
        for programm in ("a.exe", "b.exe", "c.exe"):
            q.vorn = fremd(programm)
            s.tick()
        f.zeige.assert_not_called()
        f.verberge.assert_not_called()

    def test_gleicher_vordergrund_loest_nichts_erneut_aus(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f, programm_regel("a.exe"))
        q.vorn = fremd("a.exe")
        s.tick()
        s.tick()
        s.tick()
        self.assertEqual(f.zeige.call_count, 1)

    def test_eigene_fenster_vorn_aendern_nichts(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f, programm_regel("a.exe"))
        q.vorn = fremd("a.exe")
        s.tick()
        q.vorn = Vordergrund(EIGENE, "augenundhaendebridge.exe", "Chat")
        s.tick()
        f.verberge.assert_not_called()

    def test_kein_vordergrund_aendert_nichts(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f, programm_regel("a.exe"))
        q.vorn = None
        s.tick()
        f.zeige.assert_not_called()
        f.verberge.assert_not_called()

    def test_vom_nutzer_verborgenes_fenster_kommt_nicht_von_selbst_zurueck(self):
        s, q = baue()
        f = Mock()
        s.registrieren("terminal", f, programm_regel("a.exe"), nutzer_verborgen=lambda: True)
        q.vorn = fremd("a.exe")
        s.tick()
        f.zeige.assert_not_called()

    def test_regel_setzen_wirkt_sofort_mit_dem_zuletzt_gesehenen_programm(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f)
        q.vorn = fremd("browser.exe")
        s.tick()
        s.regel_setzen("t", programm_regel("spiel.exe"))
        f.verberge.assert_called_once_with()
        s.regel_setzen("t", IMMER)  # zurück auf immer: kein weiterer Eingriff
        self.assertEqual(f.verberge.call_count, 1)

    def test_erst_registrieren_dann_erster_tick_verbirgt_falls_falsches_programm(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f, programm_regel("spiel.exe"))
        f.verberge.assert_not_called()  # noch nichts gesehen
        q.vorn = fremd("browser.exe")
        s.tick()
        f.verberge.assert_called_once_with()

    def test_sichtbar_erlaubt_fuer_meldungen(self):
        s, q = baue()
        s.registrieren("raute", Mock(), programm_regel("spiel.exe"))
        s.registrieren("frei", Mock())
        q.vorn = fremd("browser.exe")
        s.tick()
        self.assertFalse(s.sichtbar_erlaubt("raute"))
        self.assertTrue(s.sichtbar_erlaubt("frei"))
        self.assertTrue(s.sichtbar_erlaubt("unbekannt"))
        q.vorn = fremd("spiel.exe")
        s.tick()
        self.assertTrue(s.sichtbar_erlaubt("raute"))

    def test_fehler_der_quelle_halten_nichts_auf(self):
        s, q = baue()
        q.vordergrund = Mock(side_effect=OSError("kaputt"))
        s.tick()

    def test_entfernen(self):
        s, q = baue()
        f = Mock()
        s.registrieren("t", f, programm_regel("a.exe"))
        s.entfernen("t")
        q.vorn = fremd("b.exe")
        s.tick()
        f.verberge.assert_not_called()


class TaktTests(unittest.TestCase):
    def test_faden_stoesst_tick_im_gui_thread_an(self):
        import time
        s, q = baue()
        s._takt_s = 0.01
        aufgaben, nebenbei = [], []
        s.starten(aufgaben.append, nebenbei=lambda: nebenbei.append(1), nebenbei_alle_s=0.03)
        time.sleep(0.2)
        s.stoppen()
        self.assertTrue(any(a == s.tick for a in aufgaben))
        self.assertTrue(nebenbei == [] or len(aufgaben) > 0)


class WindowsQuelleTests(unittest.TestCase):
    def test_offene_programme_ohne_eigenes_und_ohne_leere_titel_je_programm_einmal(self):
        fenster = [
            SimpleNamespace(process_id=1, process_path="C:\\a\\Spiel.exe", title="Spiel - Level 1"),
            SimpleNamespace(process_id=1, process_path="C:\\a\\Spiel.exe", title="Spiel - Menü"),
            SimpleNamespace(process_id=EIGENE, process_path="C:\\b\\Bridge.exe", title="Chat"),
            SimpleNamespace(process_id=2, process_path="C:\\c\\Leer.exe", title="  "),
            SimpleNamespace(process_id=3, process_path=None, title="Ohne Pfad"),
            SimpleNamespace(process_id=4, process_path="C:\\d\\Browser.exe", title="Suche"),
        ]
        api = Mock()
        api.enumerate_windows.return_value = fenster
        q = WindowsQuelle(api)
        programme = q.offene_programme(ohne_pid=EIGENE)
        self.assertEqual([(p.programm, p.titel) for p in programme],
                         [("browser.exe", "Suche"), ("spiel.exe", "Spiel - Level 1")])


if __name__ == "__main__":
    unittest.main()
