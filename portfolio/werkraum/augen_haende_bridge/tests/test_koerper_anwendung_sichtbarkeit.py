"""Sichtbarkeitsregeln und gespeicherte Einstellungen in der Anwendung: Menü, Kanten, Speichern, Wiederherstellen."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.koerper.durchklick import DurchklickVerwalter
from augen_haende_bridge.koerper.einstellungen import Einstellungen
from augen_haende_bridge.koerper.sichtbarkeit import (
    IMMER,
    Programm,
    Sichtbarkeit,
    Vordergrund,
    programm_regel,
)
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie

EIGENE = 4242
SPIEL = Programm("spiel.exe", "Spiel - Level 1")
BROWSER = Programm("browser.exe", "Suche")


class Quelle:
    def __init__(self):
        self.vorn = None

    def vordergrund(self):
        return self.vorn


class RegieMitRect(FakeRegie):
    def rechteck(self):
        return (30, 500, 106, 800)

    deckkraft = 230

    def verschiebe(self, x, y, b=None, h=None):
        self.verschoben = (x, y, b, h)

    def setze_deckkraft(self, alpha):
        self.deckkraft = alpha


class ChatMitRect(FakeChat):
    hwnd = 77
    deckkraft = 255

    def rechteck(self):
        return (120, 560, 500, 800)

    def verschiebe(self, x, y, b=None, h=None):
        self.verschoben = (x, y, b, h)

    def setze_deckkraft(self, alpha):
        self.deckkraft = alpha


def baue(pfad, wahl=lambda hwnd, eintraege, x, y: 0, **extra):
    quelle = Quelle()
    sicht = Sichtbarkeit(quelle, eigene_pid=EIGENE)
    einst = Einstellungen(pfad)
    einst.laden()
    durch = DurchklickVerwalter(strg=lambda: False)
    basis, gebaut_ = _koerper_bauen()

    def bauen(**kwargs):
        koerper = basis(**kwargs)
        koerper.farbe_hex = "#00E5FF"
        koerper.terminal_ausgeblendet = False
        koerper.raute.rechteck.return_value = (600, 200, 648, 248)
        koerper.raute.deckkraft = 87
        koerper.raute.groesse = 48
        koerper.terminal.rechteck.return_value = (220, 100, 620, 400)
        koerper.terminal.deckkraft = 87
        return koerper

    app, gui, gebaut = _gestartet(
        regie_bauen=RegieMitRect, chat_bauen=ChatMitRect, medien=FakeMedien(), koerper_bauen=bauen,
        menue_anzeigen=wahl, sichtbarkeit=sicht, durchklick=durch, einstellungen=einst, bildschirm=lambda: (0, 0, 1920, 1080),
        programme=lambda: [BROWSER, SPIEL], **extra)
    app.durchklick_verwalter = durch
    return app, gebaut_, sicht, quelle, einst


class Basis(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pfad = Path(self.temp.name) / "einstellungen.json"

    def tearDown(self):
        self.temp.cleanup()


class RegelWaehlenTests(Basis):
    def test_alle_vier_fensterarten_sind_angemeldet(self):
        app, _, sicht, _, _ = baue(self.pfad)
        self.assertEqual(sorted(sicht.elemente), ["chat", "raute:t-1", "regie", "terminal:t-1"])

    def test_programm_waehlen_setzt_regel_und_speichert_sie(self):
        # Menü: 1000 immer, 1001 = erstes offenes Programm (browser), 1002 = spiel
        app, gebaut, sicht, quelle, einst = baue(self.pfad, wahl=lambda h, e, x, y: 1002)
        app.regel_menue("terminal:t-1", 5, 5)
        self.assertEqual(sicht.regel("terminal:t-1"), programm_regel("spiel.exe", "Spiel - Level 1"))
        gespeichert = json.loads(self.pfad.read_text(encoding="utf-8"))
        self.assertEqual(gespeichert["elemente"]["terminal:Codex"]["regel"]["programm"], "spiel.exe")

    def test_immer_waehlen_setzt_zurueck(self):
        app, _, sicht, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: 1002)
        app.regel_menue("raute:t-1", 5, 5)
        app._menue_anzeigen = lambda h, e, x, y: 1000
        app.regel_menue("raute:t-1", 5, 5)
        self.assertEqual(sicht.regel("raute:t-1"), IMMER)

    def test_abbruch_aendert_nichts(self):
        app, _, sicht, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: 0)
        app.regel_menue("chat", 5, 5)
        self.assertEqual(sicht.regel("chat"), IMMER)

    def test_menue_listet_immer_und_die_offenen_programme_mit_haken_fuer_die_aktuelle_regel(self):
        gesehen = []
        app, _, sicht, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        sicht.regel_setzen("chat", programm_regel("spiel.exe"))
        app.regel_menue("chat", 5, 5)
        texte = [(e[1], e[2]) for e in gesehen[-1] if e]
        self.assertEqual(texte[0][0], "Immer sichtbar (Desktop)")
        self.assertTrue(any("browser.exe" in t for t, _ in texte))
        gehakt = [t for t, f in texte if f]
        self.assertEqual(len(gehakt), 1)
        self.assertIn("spiel.exe", gehakt[0])

    def test_nicht_geoeffnetes_programm_bleibt_als_aktuelle_regel_sichtbar(self):
        gesehen = []
        app, _, sicht, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        sicht.regel_setzen("chat", programm_regel("altes.exe"))
        app.regel_menue("chat", 5, 5)
        texte = [e[1] for e in gesehen[-1] if e]
        self.assertTrue(any("altes.exe" in t and "nicht geöffnet" in t for t in texte))

    def test_unbekanntes_fenster_wird_ignoriert(self):
        app, _, _, _, _ = baue(self.pfad)
        app.regel_menue("gibtsnicht", 1, 1)


class KantenTests(Basis):
    def test_terminal_verschwindet_wenn_ein_anderes_programm_vorn_ist(self):
        app, gebaut, sicht, quelle, _ = baue(self.pfad)
        sicht.regel_setzen("terminal:t-1", programm_regel("spiel.exe"))
        quelle.vorn = Vordergrund(1, "browser.exe")
        sicht.tick()
        gebaut[0].terminal.verberge.assert_called()
        quelle.vorn = Vordergrund(2, "spiel.exe")
        sicht.tick()
        gebaut[0].terminal.zeige.assert_called_with(aktivieren=False)

    def test_vom_nutzer_ausgeblendetes_terminal_kommt_nicht_zurueck(self):
        app, gebaut, sicht, quelle, _ = baue(self.pfad)
        sicht.regel_setzen("terminal:t-1", programm_regel("spiel.exe"))
        gebaut[0].terminal_ausgeblendet = True
        quelle.vorn = Vordergrund(2, "spiel.exe")
        sicht.tick()
        gebaut[0].terminal.zeige.assert_not_called()

    def test_raute_meldungen_nur_wenn_ihre_regel_passt(self):
        app, gebaut, sicht, quelle, _ = baue(self.pfad)
        sicht.regel_setzen("raute:t-1", programm_regel("spiel.exe"))
        quelle.vorn = Vordergrund(1, "browser.exe")
        sicht.tick()
        self.assertFalse(gebaut[0].kwargs["meldungen_zeigen"]())
        quelle.vorn = Vordergrund(2, "spiel.exe")
        sicht.tick()
        self.assertTrue(gebaut[0].kwargs["meldungen_zeigen"]())

    def test_taktfaden_wird_mit_der_anwendung_gestartet_und_beim_beenden_gestoppt(self):
        app, _, sicht, _, _ = baue(self.pfad)
        self.assertIsNotNone(sicht._faden)
        app.beenden()
        self.assertTrue(sicht._stop.is_set())


class SpeichernTests(Basis):
    def test_beenden_speichert_orte_regeln_und_deckkraft_aller_fenster(self):
        app, gebaut, sicht, _, einst = baue(self.pfad)
        sicht.regel_setzen("regie", programm_regel("spiel.exe"))
        app.beenden()
        daten = json.loads(self.pfad.read_text(encoding="utf-8"))["elemente"]
        self.assertEqual(sorted(daten), ["chat", "raute:Codex", "regie", "terminal:Codex"])
        self.assertEqual((daten["regie"]["x"], daten["regie"]["y"], daten["regie"]["deckkraft"]), (30, 500, 230))
        self.assertEqual(daten["regie"]["regel"]["programm"], "spiel.exe")
        self.assertEqual(daten["terminal:Codex"]["b"], 400)
        self.assertEqual(daten["raute:Codex"]["groesse"], 48)

    def test_entfernter_agent_hinterlaesst_seinen_ort(self):
        app, gebaut, sicht, _, einst = baue(self.pfad)
        app.agent_beenden("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        daten = json.loads(self.pfad.read_text(encoding="utf-8"))["elemente"]
        self.assertEqual(daten["terminal:Codex"]["x"], 220)
        self.assertNotIn("terminal:t-1", sicht.elemente)

    def test_naechster_start_stellt_ort_und_regel_wieder_her(self):
        app, _, sicht, _, _ = baue(self.pfad)
        sicht.regel_setzen("chat", programm_regel("spiel.exe"))
        app.beenden()
        app2, gebaut2, sicht2, _, _ = baue(self.pfad)
        self.assertEqual(sicht2.regel("chat").programm, "spiel.exe")
        self.assertEqual(app2.chat.verschoben[:2], (120, 560))
        self.assertEqual(app2.regie.verschoben[:2], (30, 500))

    def test_kaputte_datei_stoert_den_start_nicht(self):
        self.pfad.write_text("{kaputt", encoding="utf-8")
        app, _, sicht, _, _ = baue(self.pfad)
        self.assertEqual(sicht.regel("chat"), IMMER)


class DurchklickTests(Basis):
    def test_chat_leiste_und_terminal_sind_standardmaessig_durchklickbar_die_raute_nicht_hier(self):
        app, _, _, _, _ = baue(self.pfad)
        self.assertEqual(sorted(app.durchklick.eintraege), ["chat", "regie", "terminal:t-1"])
        self.assertTrue(all(e.aktiv for e in app.durchklick.eintraege.values()))

    def test_umschalten_wird_gespeichert_und_beim_naechsten_start_wiederhergestellt(self):
        app, _, _, _, _ = baue(self.pfad)
        app.durchklick_umschalten("chat")
        self.assertFalse(app.durchklick.aktiv("chat"))
        app.beenden()
        gespeichert = json.loads(self.pfad.read_text(encoding="utf-8"))["elemente"]
        self.assertFalse(gespeichert["chat"]["durchklick"])
        self.assertTrue(gespeichert["regie"]["durchklick"])
        app2, _, _, _, _ = baue(self.pfad)
        self.assertFalse(app2.durchklick.aktiv("chat"))
        self.assertTrue(app2.durchklick.aktiv("regie"))

    def test_regie_menue_schaltet_chat_und_leiste_einzeln(self):
        app, _, _, _, _ = baue(self.pfad)
        folge = iter([320, 321])
        app._menue_anzeigen = lambda h, e, x, y: next(folge)
        app.regie_menue(1, 1)
        app.regie_menue(1, 1)
        self.assertFalse(app.durchklick.aktiv("chat"))
        self.assertFalse(app.durchklick.aktiv("regie"))

    def test_regie_menue_zeigt_den_zustand(self):
        gesehen = []
        app, _, _, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(1, 1)
        texte = [e[1] for e in gesehen[-1] if e]
        self.assertIn("Chat: durchklickbar, Strg zum Bedienen — an", texte)
        self.assertIn("Leiste: durchklickbar, Strg zum Bedienen — an", texte)

    def test_terminal_durchklick_ueber_das_raute_menue(self):
        app, gebaut, _, _, _ = baue(self.pfad)
        self.assertEqual(gebaut[0].kwargs["durchklick_text"]("terminal"), "an")
        gebaut[0].kwargs["durchklick_umschalten"]("terminal")
        self.assertEqual(gebaut[0].kwargs["durchklick_text"]("terminal"), "aus")

    def test_entfernter_agent_raeumt_sein_terminal_aus_dem_verwalter(self):
        app, gebaut, _, _, _ = baue(self.pfad)
        app.agent_beenden("t-1")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        self.assertNotIn("terminal:t-1", app.durchklick.eintraege)

    def test_beenden_stoppt_den_takt(self):
        app, _, _, _, _ = baue(self.pfad)
        app.beenden()
        self.assertTrue(app.durchklick._stop.is_set())


class MenuTests(Basis):
    def test_regie_menue_hat_regeleintraege_fuer_chat_und_leiste(self):
        gesehen = []
        app, _, sicht, _, _ = baue(self.pfad, wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(1, 1)
        texte = [e[1] for e in gesehen[-1] if e]
        self.assertIn("Chat: immer sichtbar …", texte)
        self.assertIn("Leiste: immer sichtbar …", texte)

    def test_regie_menue_eintrag_oeffnet_das_auswahlmenue_fuer_den_chat(self):
        app, _, sicht, _, _ = baue(self.pfad)
        folge = iter([310, 1002])
        app._menue_anzeigen = lambda h, e, x, y: next(folge)
        app.regie_menue(1, 1)
        self.assertEqual(sicht.regel("chat").programm, "spiel.exe")

    def test_raute_menue_regeltext_und_aufruf(self):
        app, gebaut, sicht, _, _ = baue(self.pfad)
        sicht.regel_setzen("terminal:t-1", programm_regel("spiel.exe"))
        self.assertEqual(gebaut[0].kwargs["regeltext"]("terminal"), "nur bei spiel.exe")
        app._menue_anzeigen = lambda h, e, x, y: 1002
        gebaut[0].kwargs["regel_menue"]("raute", 5, 5)
        self.assertEqual(sicht.regel("raute:t-1").programm, "spiel.exe")


if __name__ == "__main__":
    unittest.main()
