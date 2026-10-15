"""G05 (R024, UQ02, UQ06): gleiche Namen bleiben unterscheidbar, Name und Farbe sind Daniels Wahl und bleiben nach einem Neustart,
alles lässt sich auf den Standard zurücksetzen, und das Regie-Menü sagt, wohin die Sprüche gehen."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.koerper import stil
from augen_haende_bridge.koerper.einstellungen import Einstellungen
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


def _zweiter(app):
    app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Codex", "state": "starting",
                                           "exit_code": None, "reason": ""}))
    app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Codex", "state": "running",
                                           "exit_code": None, "reason": ""}))


def baue(pfad=None, wahl=lambda h, e, x, y: 0):
    basis, gebaut = _koerper_bauen()

    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = kwargs.get("farbe_hex") or stil.agentenfarbe(kwargs["name"])
        k.name = kwargs["name"]
        k.terminal_ausgeblendet = False
        k.raute.rechteck.return_value = (600, 200, 760, 252)
        k.raute.deckkraft, k.raute.groesse = 87, 52
        k.terminal.rechteck.return_value = (220, 100, 620, 400)
        k.terminal.deckkraft = 87
        return k

    einst = Einstellungen(Path(pfad)) if pfad else None
    if einst:
        einst.laden()
    app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=bauen,
                                einstellungen=einst, menue_anzeigen=wahl, bildschirm=lambda: (0, 0, 1920, 1080))
    return app, gebaut, einst


class GleicheNamenTests(unittest.TestCase):
    def test_zweite_sitzung_gleichen_namens_wird_nummeriert_und_hat_eigene_einstellungen(self):
        app, gebaut, _ = baue()
        _zweiter(app)
        self.assertEqual([a.name for a in app.agenten.values()], ["Codex", "Codex 2"])
        self.assertEqual([a.schluessel for a in app.agenten.values()], ["Codex", "Codex 2"])
        self.assertIn("raute:t-2", app._fenster_art)
        self.assertEqual(app._fenster_art["raute:t-2"][1], "raute:Codex 2")  # eigener Speicherplatz für Ort und Größe
        self.assertEqual(app._fenster_art["raute:t-1"][1], "raute:Codex")

    def test_beendete_nummer_wird_wieder_frei(self):
        app, gebaut, _ = baue()
        _zweiter(app)
        app._agent_entfernen("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-3", "start_id": "codex-vd1", "name": "Codex", "state": "running",
                                               "exit_code": None, "reason": ""}))
        self.assertEqual(sorted(a.name for a in app.agenten.values()), ["Codex", "Codex 2"])


class NameUndFarbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp(prefix="id-")
        self.pfad = Path(self.temp) / "einstellungen.json"

    def test_umbenennen_aendert_alle_anzeigen_und_wird_gespeichert(self):
        app, gebaut, einst = baue(self.pfad)
        k = gebaut[0]
        self.assertTrue(app.umbenennen("t-1", "  Chef   Codex "))
        self.assertEqual(app.agenten["t-1"].name, "Chef Codex")
        k.setze_identitaet.assert_called_with(name="Chef Codex")
        self.assertEqual(app.chat.farben.get("Chef Codex"), app.chat.farben.get("Codex") or app.chat.farben["Chef Codex"])
        self.assertEqual(einst.element("agent:Codex"), {"name": "Chef Codex"})
        self.assertIn("heißt jetzt", app.hinweis)

    def test_neustart_stellt_name_und_farbe_wieder_her_die_fensterschluessel_bleiben(self):
        app, gebaut, _ = baue(self.pfad)
        app.umbenennen("t-1", "Chef")
        app.farbe_setzen("t-1", stil.AGENTENFARBEN[5])
        app.beenden()
        app2, gebaut2, _ = baue(self.pfad)
        self.assertEqual(app2.agenten["t-1"].name, "Chef")
        self.assertEqual(app2.agenten["t-1"].schluessel, "Codex")
        self.assertEqual(gebaut2[0].name, "Chef")
        self.assertEqual(gebaut2[0].farbe_hex, stil.AGENTENFARBEN[5])
        self.assertEqual(app2._fenster_art["raute:t-1"][1], "raute:Codex")  # Ort und Größe finden sich weiter unter dem festen Schlüssel

    def test_umbenennen_lehnt_leer_zu_lang_und_doppelt_ab(self):
        app, gebaut, _ = baue(self.pfad)
        _zweiter(app)
        self.assertFalse(app.umbenennen("t-1", "   "))
        self.assertFalse(app.umbenennen("t-1", "x" * 25))
        self.assertIn("zu lang", app.hinweis)
        self.assertFalse(app.umbenennen("t-1", "Codex 2"))  # heißt schon eine andere Sitzung so
        self.assertIn("schon vergeben", app.hinweis)
        self.assertEqual(app.agenten["t-1"].name, "Codex")
        self.assertFalse(app.umbenennen("t-99", "Neu"))

    def test_farbwahl_ueber_das_menue_und_standardfarbe(self):
        app, gebaut, einst = baue(self.pfad, wahl=lambda h, e, x, y: 3200 + 2)
        app.farbe_menue("t-1", 10, 10)
        self.assertEqual(gebaut[0].setze_identitaet.call_args.kwargs["farbe_hex"], stil.AGENTENFARBEN[2])
        self.assertEqual(einst.element("agent:Codex"), {"farbe": stil.AGENTENFARBEN[2]})
        app._menue_anzeigen = lambda h, e, x, y: 3299  # Standardfarbe
        app.farbe_menue("t-1", 10, 10)
        self.assertEqual(einst.element("agent:Codex"), {})
        self.assertEqual(gebaut[0].setze_identitaet.call_args.kwargs["farbe_hex"], stil.agentenfarbe("Codex"))

    def test_menue_markiert_die_aktuelle_farbe_und_nennt_acht_farben_mit_namen(self):
        gesehen = []
        app, gebaut, _ = baue(self.pfad, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.farbe_menue("t-1", 0, 0)
        eintraege = gesehen[0]
        self.assertEqual(len([e for e in eintraege if e and e[0] >= 3200 and e[0] < 3299]), 8)
        self.assertTrue(any("Cyan" in e[1] for e in eintraege if e))
        self.assertEqual(sum(1 for e in eintraege if e and e[2]), 1)  # genau eine ist abgehakt

    def test_name_aendern_oeffnet_das_eingabefeld_mit_titel_und_callback(self):
        app, gebaut, _ = baue(self.pfad)
        app.name_aendern("t-1")
        titel, callback = gebaut[0].eingabe_oeffnen.call_args.args
        self.assertEqual(titel, "Neuer Name")
        callback("Neu")
        self.assertEqual(app.agenten["t-1"].name, "Neu")


class ZuruecksetzenTests(unittest.TestCase):
    def test_fenster_namen_und_farben_gehen_auf_den_standard_zurueck(self):
        temp = tempfile.mkdtemp(prefix="zr-")
        app, gebaut, einst = baue(Path(temp) / "e.json")
        app.umbenennen("t-1", "Chef")
        app.farbe_setzen("t-1", stil.AGENTENFARBEN[6])
        gebaut[0].terminal.verschiebe.reset_mock()
        app.fenster_zuruecksetzen()
        self.assertEqual(app.agenten["t-1"].name, "Codex")
        self.assertEqual(gebaut[0].setze_identitaet.call_args_list[-1].kwargs["farbe_hex"], stil.agentenfarbe("Codex"))
        gebaut[0].terminal.verschiebe.assert_called()  # zurück auf den Standardplatz
        self.assertEqual(einst.element("agent:Codex"), {})
        self.assertIn("zurückgesetzt", app.hinweis)

    def test_nachfrage_vor_dem_zuruecksetzen_nein_aendert_nichts(self):
        antworten = iter([0])
        app, gebaut, _ = baue(wahl=lambda h, e, x, y: next(antworten))
        app.umbenennen("t-1", "Chef")
        app.zuruecksetzen_fragen(5, 5)
        self.assertEqual(app.agenten["t-1"].name, "Chef")

    def test_nachfrage_ja_setzt_zurueck(self):
        app, gebaut, _ = baue(wahl=lambda h, e, x, y: 351)
        app.umbenennen("t-1", "Chef")
        app.zuruecksetzen_fragen(5, 5)
        self.assertEqual(app.agenten["t-1"].name, "Codex")


class RegieMenueTests(unittest.TestCase):
    def test_menue_sagt_wohin_die_spruche_gehen(self):
        gesehen = []
        app, gebaut, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(0, 0)
        self.assertIn("Sprüche gehen an: alle Agenten", gesehen[0][0][1])
        app.empfaenger = "t-1"
        app.regie_menue(0, 0)
        self.assertIn("Sprüche gehen an: Codex", gesehen[1][0][1])

    def test_menue_hat_den_zuruecksetzen_eintrag(self):
        gesehen = []
        app, gebaut, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(0, 0)
        self.assertTrue(any(e and "zurücksetzen" in e[1] for e in gesehen[0]))


if __name__ == "__main__":
    unittest.main()
