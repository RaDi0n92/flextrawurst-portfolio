"""Tastenkombination je Agent (steht in der Raute) und wählbare Bedientaste in der Anwendung."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.koerper import win32 as w
from augen_haende_bridge.koerper.einstellungen import Einstellungen
from augen_haende_bridge.koerper.tastenkombi import Bedientaste, Erfasser, Kombination
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


class Erfasser2:
    """Liefert sofort eine vorgegebene Kombination (oder None)."""

    def __init__(self, ergebnis):
        self.ergebnis = ergebnis

    def im_hintergrund(self, fertig, timeout_s=8.0):
        fertig(self.ergebnis)


class GuiMitHotkeys:
    def __init__(self):
        self.belegt = {}
        self.gesetzt = []
        self.abgelehnt = set()

    def post(self, aufgabe):
        aufgabe()

    def hotkey(self, mods, vk, aufruf):
        return True

    def hotkey_setzen(self, name, mods, vk, aufruf):
        if (mods, vk) in self.abgelehnt:
            return False
        self.belegt[name] = (mods, vk, aufruf)
        self.gesetzt.append((name, mods, vk))
        return True

    def hotkey_loeschen(self, name):
        self.belegt.pop(name, None)

    def beenden(self, code=0):
        self.beendet = code


def baue(pfad=None, erfasser=None, bedientaste=None, wahl=lambda h, e, x, y: 0, gui=None):
    basis, gebaut_ = _koerper_bauen()

    def bauen(**kwargs):
        koerper = basis(**kwargs)
        koerper.farbe_hex = "#00E5FF"
        koerper.terminal_ausgeblendet = False
        koerper.raute.rechteck.return_value = (600, 200, 760, 252)
        koerper.raute.deckkraft, koerper.raute.groesse = 87, 52
        koerper.terminal.rechteck.return_value = (220, 100, 620, 400)
        koerper.terminal.deckkraft = 87
        return koerper

    einst = Einstellungen(pfad) if pfad else None
    if einst:
        einst.laden()
    app, g, gebaut = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=bauen,
                                menue_anzeigen=wahl, einstellungen=einst, bedientaste=bedientaste,
                                erfasser=erfasser or Erfasser2(None), bildschirm=lambda: (0, 0, 1920, 1080))
    return app, gebaut_, einst


def zweiter_agent(app):
    app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Zwei",
                                           "state": "running", "exit_code": None, "reason": ""}))


class StandardTests(unittest.TestCase):
    def test_erste_agenten_bekommen_f13_f14_und_sie_stehen_in_der_raute(self):
        app, gebaut, _ = baue()
        zweiter_agent(app)
        self.assertEqual([g.kwargs["hotkey"] for g in gebaut], ["F13", "F14"])
        self.assertEqual([a.hotkey for a in app.agenten.values()], ["F13", "F14"])

    def test_nach_dem_entfernen_wird_die_erste_freie_kombination_genommen(self):
        app, gebaut, _ = baue()
        zweiter_agent(app)
        app.agent_beenden("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        app.ereignis(_event("terminal_state", {"terminal_id": "t-3", "start_id": "codex-vd1", "name": "Drei",
                                               "state": "running", "exit_code": None, "reason": ""}))
        self.assertEqual(app.agenten["t-3"].hotkey, "F13")

    def test_die_kombination_oeffnet_das_eingabefeld_genau_dieser_raute(self):
        app, gebaut, _ = baue()
        zweiter_agent(app)
        kombi_f14 = [h for h in app.gui.hotkeys if h[1] == 0x7D][0]
        kombi_f14[2]()
        gebaut[1].eingabe_oeffnen.assert_called_once_with()
        gebaut[0].eingabe_oeffnen.assert_not_called()

    def test_eingabe_oeffnen_fuer_unbekannten_agenten_ist_harmlos(self):
        app, _, _ = baue()
        app.eingabe_oeffnen("gibtsnicht")


class FreigabeTests(unittest.TestCase):
    def test_entfernter_agent_gibt_seine_tastenkombination_frei(self):
        gui = GuiMitHotkeys()
        basis, gebaut_ = _koerper_bauen()

        def bauen(**kwargs):
            k = basis(**kwargs)
            k.farbe_hex = "#00E5FF"
            return k

        app, _g, gebaut = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=bauen)
        geloescht = []
        app.gui.hotkey_loeschen = geloescht.append
        app.agent_beenden("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        self.assertEqual(geloescht, ["agent:t-1"])


class FestlegenTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pfad = Path(self.temp.name) / "e.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_neue_kombination_wird_angemeldet_in_der_raute_gezeigt_und_gespeichert(self):
        kombi = Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74)
        app, gebaut, einst = baue(self.pfad, erfasser=Erfasser2(kombi))
        app.hotkey_festlegen("t-1")
        gebaut[0].setze_hotkey.assert_called_once_with("Strg+Alt+F5")
        self.assertEqual(app.agenten["t-1"].hotkey, "Strg+Alt+F5")
        app.beenden()
        self.assertEqual(json.loads(self.pfad.read_text(encoding="utf-8"))["elemente"]["raute:Codex"]["hotkey"], "Strg+Alt+F5")

    def test_gespeicherte_kombination_kommt_beim_naechsten_start_zurueck(self):
        kombi = Kombination(w.MOD_CONTROL | w.MOD_ALT, 0x74)
        app, gebaut, einst = baue(self.pfad, erfasser=Erfasser2(kombi))
        app.hotkey_festlegen("t-1")
        app.einstellungen_sichern()
        app2, gebaut2, _ = baue(self.pfad)
        self.assertEqual(gebaut2[0].kwargs["hotkey"], "Strg+Alt+F5")

    def test_abbruch_aendert_nichts(self):
        app, gebaut, _ = baue(erfasser=Erfasser2(None))
        app.hotkey_festlegen("t-1")
        gebaut[0].setze_hotkey.assert_not_called()
        self.assertEqual(app.agenten["t-1"].hotkey, "F13")
        self.assertIn("Keine Änderung", [c.args[0] for c in gebaut[0].zeige_ticker.call_args_list])

    def test_buchstabe_ohne_modifikator_wird_abgelehnt(self):
        app, gebaut, _ = baue(erfasser=Erfasser2(Kombination(0, 0x41)))
        app.hotkey_festlegen("t-1")
        gebaut[0].setze_hotkey.assert_not_called()
        self.assertTrue(any("nicht erlaubt" in c.args[0] for c in gebaut[0].zeige_ticker.call_args_list))

    def test_schon_bei_anderem_agenten_wird_abgelehnt(self):
        app, gebaut, _ = baue(erfasser=Erfasser2(Kombination(0, 0x7D)))  # F14 gehört dem zweiten
        zweiter_agent(app)
        app.hotkey_festlegen("t-1")
        gebaut[0].setze_hotkey.assert_not_called()
        self.assertTrue(any("anderen Agenten" in c.args[0] for c in gebaut[0].zeige_ticker.call_args_list))

    def test_von_windows_belegte_kombination_wird_gemeldet_und_die_alte_bleibt(self):
        app, gebaut, _ = baue(erfasser=Erfasser2(Kombination(w.MOD_WIN, 0x44)))
        app.gui.hotkey_setzen = lambda *a, **k: False
        app.hotkey_festlegen("t-1")
        gebaut[0].setze_hotkey.assert_not_called()
        self.assertEqual(app.agenten["t-1"].hotkey, "F13")
        self.assertTrue(any("belegt" in c.args[0] for c in gebaut[0].zeige_ticker.call_args_list))

    def test_beim_festlegen_erscheint_die_aufforderung_an_der_raute(self):
        app, gebaut, _ = baue(erfasser=Mock(im_hintergrund=Mock()))
        app.hotkey_festlegen("t-1")
        gebaut[0].zeige_ticker.assert_called_once()
        self.assertIn("Tastenkombination drücken", gebaut[0].zeige_ticker.call_args.args[0])

    def test_raute_menue_bietet_das_festlegen(self):
        app, gebaut, _ = baue()
        gebaut[0].kwargs["hotkey_festlegen"]()  # ruft hotkey_festlegen(t-1) auf: darf nicht scheitern


class BedientasteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pfad = Path(self.temp.name) / "e.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_raute_bekommt_die_bedientaste(self):
        b = Bedientaste("strg+alt", gehalten=lambda vk: True)
        app, gebaut, _ = baue(bedientaste=b)
        self.assertEqual(gebaut[0].kwargs["modifikator"], b.gedrueckt)
        self.assertEqual(gebaut[0].kwargs["bedientaste_text"](), "Strg+Alt")

    def test_regie_menue_zeigt_die_bedientaste_und_oeffnet_die_auswahl(self):
        b = Bedientaste("strg")
        gesehen = []
        folge = iter([330, 2001])  # 2001 = zweite Option (strg+alt)

        def wahl(h, eintraege, x, y):
            gesehen.append(eintraege)
            return next(folge)

        app, _, _ = baue(self.pfad, bedientaste=b, wahl=wahl)
        app.regie_menue(1, 1)
        self.assertIn("Bedientaste für alle Fenster: Strg …", [e[1] for e in gesehen[0] if e])
        self.assertEqual(b.name, "strg+alt")
        self.assertEqual(json.loads(self.pfad.read_text(encoding="utf-8"))["elemente"]["_global"]["bedientaste"], "strg+alt")

    def test_auswahlmenue_hat_haken_bei_der_aktuellen(self):
        b = Bedientaste("alt")
        gesehen = []
        folge = iter([330, 0])
        app, _, _ = baue(self.pfad, bedientaste=b, wahl=lambda h, e, x, y: gesehen.append(e) or next(folge))
        app.regie_menue(1, 1)
        gehakt = [e[1] for e in gesehen[1] if e and e[2]]
        self.assertEqual(gehakt, ["Alt"])

    def test_menues_nennen_die_aktuelle_bedientaste(self):
        b = Bedientaste("alt+umschalt")
        gesehen = []
        app, _, _ = baue(bedientaste=b, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(1, 1)
        texte = [e[1] for e in gesehen[-1] if e]
        self.assertIn("Chat: durchklickbar, Alt+Umschalt zum Bedienen — aus", texte)


if __name__ == "__main__":
    unittest.main()
