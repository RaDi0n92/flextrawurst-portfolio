"""Hände in der Anwendung: Auftrag `raute_tippen`, Schalter je Agent, Not-Aus, Rückmeldung an der Raute."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from augen_haende_bridge.koerper.einstellungen import Einstellungen
from augen_haende_bridge.koerper.tasten_senden import Ergebnis
from augen_haende_bridge.koerper.tastenkombi import Kombination
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


class FakeHaende:
    def __init__(self, ergebnis=Ergebnis(True), blockieren=None, fehler=None):
        self.aufrufe, self.ergebnis, self.blockieren, self.fehler = [], ergebnis, blockieren, fehler
        self.fertig = threading.Event()

    def schreiben(self, text, kombi, *, feld_hat_fokus, gesperrt, feld_schliessen, ruhig=lambda: True, eigene_markieren=lambda: None):
        self.aufrufe.append({"text": text, "kombi": kombi, "fokus": feld_hat_fokus, "gesperrt": gesperrt,
                             "schliessen": feld_schliessen, "ruhig": ruhig, "markieren": eigene_markieren})
        if self.blockieren is not None:
            self.blockieren.wait(5)
        self.fertig.set()
        if self.fehler:
            raise self.fehler
        return self.ergebnis


def baue(haende, pfad=None, vordergrund=lambda: 0):
    basis, gebaut_ = _koerper_bauen()

    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = "#00E5FF"
        k.terminal_ausgeblendet = False
        k.eingabe_hwnd.return_value = None
        k.raute.rechteck.return_value = (600, 200, 760, 252)
        k.raute.deckkraft, k.raute.groesse = 87, 52
        k.terminal.rechteck.return_value = (220, 100, 620, 400)
        k.terminal.deckkraft = 87
        return k

    einst = Einstellungen(pfad) if pfad else None
    if einst:
        einst.laden()
    app, gui, gebaut = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=bauen,
                                  haende=haende, vordergrund_hwnd=vordergrund, einstellungen=einst,
                                  bildschirm=lambda: (0, 0, 1920, 1080))
    return app, gebaut_


def tippen(app, text="Hallo"):
    app.ereignis(_event("raute_tippen", {"terminal_id": "t-1", "text": text}))


def warte(bedingung, sekunden=3.0):
    ende = time.monotonic() + sekunden
    while time.monotonic() < ende:
        if bedingung():
            return True
        time.sleep(0.01)
    return bedingung()


def tickertexte(koerper):
    return [c.args[0] for c in koerper.zeige_ticker.call_args_list]


class AuftragTests(unittest.TestCase):
    def test_auftrag_ruft_die_haende_mit_text_und_der_kombination_des_agenten(self):
        h = FakeHaende()
        app, gebaut = baue(h)
        tippen(app, "Hallo Daniel")
        self.assertTrue(h.fertig.wait(3))
        self.assertEqual(h.aufrufe[0]["text"], "Hallo Daniel")
        self.assertEqual(h.aufrufe[0]["kombi"], Kombination(0, 0x7C))

    def test_fokusabfrage_vergleicht_das_eingabefeld_mit_dem_vordergrund(self):
        h = FakeHaende()
        vorn = {"hwnd": 0}
        app, gebaut = baue(h, vordergrund=lambda: vorn["hwnd"])
        tippen(app)
        h.fertig.wait(3)
        fokus = h.aufrufe[0]["fokus"]
        self.assertFalse(fokus())  # kein Feld offen
        gebaut[0].eingabe_hwnd.return_value = 4711
        self.assertFalse(fokus())  # Feld offen, aber ein anderes Fenster vorn
        vorn["hwnd"] = 4711
        self.assertTrue(fokus())

    def test_sperre_fragt_den_not_aus(self):
        h = FakeHaende()
        app, _ = baue(h)
        tippen(app)
        h.fertig.wait(3)
        sperre = h.aufrufe[0]["gesperrt"]
        self.assertFalse(sperre())
        app.not_aus.ausloesen("test")
        self.assertTrue(sperre())

    def test_abbruch_schliesst_das_feld_im_gui_thread(self):
        h = FakeHaende()
        app, gebaut = baue(h)
        tippen(app)
        h.fertig.wait(3)
        h.aufrufe[0]["schliessen"]()
        gebaut[0].eingabe_schliessen.assert_called_once_with()


class SchalterUndSperreTests(unittest.TestCase):
    def test_haende_aus_tippt_nicht_und_meldet_es_an_der_raute(self):
        h = FakeHaende()
        app, gebaut = baue(h)
        app.haende_umschalten("t-1")
        tippen(app)
        self.assertEqual(h.aufrufe, [])
        self.assertTrue(any("aus" in t and "wollte schreiben" in t for t in tickertexte(gebaut[0])))

    def test_not_aus_tippt_nicht(self):
        h = FakeHaende()
        app, gebaut = baue(h)
        app.not_aus.ausloesen("x")
        tippen(app)
        self.assertEqual(h.aufrufe, [])
        self.assertTrue(any("Not-Aus" in t for t in tickertexte(gebaut[0])))

    def test_ohne_haende_objekt_nicht_verfuegbar(self):
        app, gebaut = baue(None)
        tippen(app)
        self.assertTrue(any("nicht verfügbar" in t for t in tickertexte(gebaut[0])))

    def test_unbekannter_agent_wird_ignoriert(self):
        h = FakeHaende()
        app, _ = baue(h)
        app.ereignis(_event("raute_tippen", {"terminal_id": "t-99", "text": "x"}))
        self.assertEqual(h.aufrufe, [])

    def test_zweiter_auftrag_waehrend_der_erste_laeuft_wird_abgewiesen(self):
        frei = threading.Event()
        h = FakeHaende(blockieren=frei)
        app, gebaut = baue(h)
        tippen(app, "eins")
        self.assertTrue(warte(lambda: len(h.aufrufe) == 1))
        tippen(app, "zwei")
        self.assertEqual(len(h.aufrufe), 1)
        self.assertTrue(any("beschäftigt" in t for t in tickertexte(gebaut[0])))
        frei.set()
        self.assertTrue(warte(lambda: not app.agenten["t-1"].haende_laufen))
        tippen(app, "drei")
        self.assertTrue(warte(lambda: len(h.aufrufe) == 2))


class RueckmeldungTests(unittest.TestCase):
    def test_fehlgeschlagener_auftrag_erscheint_als_klartext_an_der_raute(self):
        h = FakeHaende(ergebnis=Ergebnis(False, "feld_nicht_geoeffnet"))
        app, gebaut = baue(h)
        tippen(app)
        self.assertTrue(warte(lambda: any("nicht geöffnet" in t for t in tickertexte(gebaut[0]))))

    def test_ausnahme_in_den_haenden_wird_gemeldet_und_der_agent_ist_wieder_frei(self):
        h = FakeHaende(fehler=RuntimeError("kaputt"))
        app, gebaut = baue(h)
        tippen(app)
        self.assertTrue(warte(lambda: any("Fehler" in t for t in tickertexte(gebaut[0]))))
        self.assertTrue(warte(lambda: not app.agenten["t-1"].haende_laufen))

    def test_erfolg_meldet_nichts_der_text_erscheint_ueber_die_raute(self):
        h = FakeHaende()
        app, gebaut = baue(h)
        tippen(app)
        h.fertig.wait(3)
        self.assertTrue(warte(lambda: not app.agenten["t-1"].haende_laufen))
        self.assertEqual(tickertexte(gebaut[0]), [])


class MenueUndSpeichernTests(unittest.TestCase):
    def test_menue_text_und_umschalten(self):
        app, gebaut = baue(FakeHaende())
        self.assertEqual(gebaut[0].kwargs["haende_text"](), "an")
        gebaut[0].kwargs["haende_umschalten"]()
        self.assertEqual(gebaut[0].kwargs["haende_text"](), "aus")

    def test_schalter_wird_gespeichert_und_beim_naechsten_start_wiederhergestellt(self):
        with tempfile.TemporaryDirectory() as temp:
            pfad = Path(temp) / "e.json"
            app, _ = baue(FakeHaende(), pfad)
            app.haende_umschalten("t-1")
            app.beenden()
            self.assertFalse(json.loads(pfad.read_text(encoding="utf-8"))["elemente"]["raute:Codex"]["haende"])
            app2, _ = baue(FakeHaende(), pfad)
            self.assertFalse(app2.agenten["t-1"].haende)


if __name__ == "__main__":
    unittest.main()
