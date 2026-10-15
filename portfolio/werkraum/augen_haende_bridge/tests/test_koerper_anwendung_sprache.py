"""Sprache in der Anwendung: Äußerung an den VPS, erkannter Text zurück in Chat und Ticker, Sprechtaste, Modus."""

from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.koerper.anwendung import GESPERRTE_ARTEN
from augen_haende_bridge.koerper.einstellungen import Einstellungen
from augen_haende_bridge.koerper.tastenkombi import Kombination
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


class SprachMedien(FakeMedien):
    def __init__(self):
        super().__init__()
        self.modus, self.sprechtaste_vk, self.audio, self.mik_geraet = "sprechtaste", 0x77, None, None

    def audio_verbinden(self, rueckruf):
        self.audio = rueckruf


class Erfasser3:
    def __init__(self, ergebnis):
        self.ergebnis = ergebnis

    def im_hintergrund(self, fertig, timeout_s=8.0):
        fertig(self.ergebnis)


def baue(pfad=None, erfasser=None, wahl=lambda h, e, x, y: 0):
    basis, gebaut_ = _koerper_bauen()

    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = "#00E5FF"
        k.terminal_ausgeblendet = False
        k.raute.rechteck.return_value = (600, 200, 760, 252)
        k.raute.deckkraft, k.raute.groesse = 87, 52
        k.terminal.rechteck.return_value = (220, 100, 620, 400)
        k.terminal.deckkraft = 87
        return k

    medien = SprachMedien()
    einst = Einstellungen(pfad) if pfad else None
    if einst:
        einst.laden()
    app, gui, gebaut = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=medien, koerper_bauen=bauen,
                                  einstellungen=einst, mik_geraete=lambda: [(1, "Internes Mikrofon"), (5, "WO Mic")], erfasser=erfasser or Erfasser3(None), menue_anzeigen=wahl,
                                  bildschirm=lambda: (0, 0, 1920, 1080))
    return app, gebaut_, medien


def tickertexte(k):
    return [c.args[0] for c in k.zeige_ticker.call_args_list]


class AudioSendenTests(unittest.TestCase):
    def test_medien_bekommt_den_rueckruf_der_anwendung(self):
        app, _, medien = baue()
        self.assertEqual(medien.audio, app.audio_senden)

    def test_aeusserung_geht_als_terminal_audio_hinaus_und_die_raute_meldet_die_erkennung(self):
        app, gebaut, _ = baue()
        app.audio_senden("t-1", b"RIFFdaten", 1500)
        art, nutzlast = app.runtime.gesendet[-1]
        self.assertEqual(art, "terminal_audio")
        self.assertEqual((nutzlast["terminal_id"], nutzlast["mime"], nutzlast["dauer_ms"]), ("t-1", "audio/wav", 1500))
        self.assertEqual(base64.b64decode(nutzlast["data"]), b"RIFFdaten")
        self.assertIn("Sprache wird erkannt …", tickertexte(gebaut[0]))

    def test_not_aus_offline_und_unbekannter_agent_senden_nichts(self):
        app, _, _ = baue()
        n = len(app.runtime.gesendet)
        app.audio_senden("t-99", b"RIFF", 500)
        app.status = "offline"
        app.audio_senden("t-1", b"RIFF", 500)
        app.status = "verbunden"
        app.not_aus.ausloesen("x")
        app.audio_senden("t-1", b"RIFF", 500)
        self.assertEqual(len(app.runtime.gesendet), n)

    def test_der_sender_sperrt_audio_bei_not_aus(self):
        self.assertIn("terminal_audio", GESPERRTE_ARTEN)


class ErkannterTextTests(unittest.TestCase):
    def test_text_erscheint_im_chat_und_als_banner_nicht_im_terminal(self):
        app, gebaut, _ = baue()
        app.ereignis(_event("sprache_text", {"terminal_id": "t-1", "text": "Schau mal links", "dauer_ms": 1200, "modell": "medium"}))
        self.assertEqual(app.chat.verlauf[-1], ("Daniel → Codex", "(Sprache) Schau mal links"))
        self.assertIn("Daniel: (Sprache) Schau mal links", [c.args[0] for c in gebaut[0].zeige_daniel.call_args_list])
        gebaut[0].terminal.tippe.assert_not_called()

    def test_text_fuer_unbekannten_agenten_wird_ignoriert(self):
        app, _, _ = baue()
        app.ereignis(_event("sprache_text", {"terminal_id": "t-99", "text": "x", "dauer_ms": 1, "modell": "m"}))
        self.assertEqual(app.chat.verlauf, [])


class GeraetTests(unittest.TestCase):
    def test_geraet_waehlen_und_standard_zurueck(self):
        app, _, medien = baue()
        app._menue_anzeigen = lambda h, e, x, y: 3002  # zweites Gerät (WO Mic)
        app.mik_geraet_waehlen(1, 1)
        self.assertEqual(medien.mik_geraet, "WO Mic")
        self.assertTrue(any("WO Mic" in e[1] for e in app.chat.verlauf))
        app._menue_anzeigen = lambda h, e, x, y: 3000
        app.mik_geraet_waehlen(1, 1)
        self.assertIsNone(medien.mik_geraet)

    def test_abbruch_laesst_es_unveraendert(self):
        app, _, medien = baue()
        medien.mik_geraet = "Internes Mikrofon"
        app._menue_anzeigen = lambda h, e, x, y: 0
        app.mik_geraet_waehlen(1, 1)
        self.assertEqual(medien.mik_geraet, "Internes Mikrofon")

    def test_menue_zeigt_geraete_mit_haken_und_der_regie_eintrag_nennt_das_aktuelle(self):
        gesehen = []
        app, _, medien = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        medien.mik_geraet = "WO Mic"
        app.regie_menue(1, 1)
        self.assertIn("Mikrofon-Gerät: WO Mic …", [e[1] for e in gesehen[-1] if e])
        app.mik_geraet_waehlen(1, 1)
        gehakt = [e[1] for e in gesehen[-1] if e and e[2]]
        self.assertEqual(gehakt, ["WO Mic"])

    def test_regie_menue_eintrag_oeffnet_die_auswahl(self):
        app, _, medien = baue()
        folge = iter([342, 3001])
        app._menue_anzeigen = lambda h, e, x, y: next(folge)
        app.regie_menue(1, 1)
        self.assertEqual(medien.mik_geraet, "Internes Mikrofon")

    def test_geraet_wird_gespeichert(self):
        with tempfile.TemporaryDirectory() as temp:
            pfad = Path(temp) / "e.json"
            app, _, medien = baue(pfad)
            app._menue_anzeigen = lambda h, e, x, y: 3002
            app.mik_geraet_waehlen(1, 1)
            app.beenden()
            self.assertEqual(json.loads(pfad.read_text(encoding="utf-8"))["elemente"]["_global"]["mik_geraet"], "WO Mic")

    def test_ohne_geraete_steht_ein_hinweis_im_menue(self):
        gesehen = []
        app, _, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app._mik_geraete = lambda: []
        app.mik_geraet_waehlen(1, 1)
        self.assertIn("Keine Eingabegeräte gefunden", [e[1] for e in gesehen[-1] if e])


class SprechtasteUndModusTests(unittest.TestCase):
    def test_sprechtaste_festlegen_uebernimmt_die_gedrueckte_taste(self):
        app, _, medien = baue(erfasser=Erfasser3(Kombination(0, 0x78)))
        app.sprechtaste_festlegen()
        self.assertEqual(medien.sprechtaste_vk, 0x78)
        self.assertIn("Sprechtaste: F9 (gedrückt halten zum Sprechen)", [e[1] for e in app.chat.verlauf])

    def test_abbruch_laesst_die_taste_unveraendert(self):
        app, _, medien = baue(erfasser=Erfasser3(None))
        app.sprechtaste_festlegen()
        self.assertEqual(medien.sprechtaste_vk, 0x77)
        self.assertIn("Sprechtaste: keine Änderung", [e[1] for e in app.chat.verlauf])

    def test_modus_umschalten_mit_klarem_hinweis(self):
        app, _, medien = baue()
        app.mik_modus_umschalten()
        self.assertEqual(medien.modus, "offen")
        self.assertTrue(any("alles, was es hört" in e[1] for e in app.chat.verlauf))
        app.mik_modus_umschalten()
        self.assertEqual(medien.modus, "sprechtaste")

    def test_regie_menue_zeigt_taste_und_modus(self):
        gesehen = []
        app, _, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(1, 1)
        texte = [e[1] for e in gesehen[-1] if e]
        self.assertIn("Sprechtaste (halten zum Sprechen): F8 …", texte)
        self.assertIn("Mikrofon-Modus: Sprechtaste …", texte)

    def test_regie_menue_eintraege_loesen_die_aktionen_aus(self):
        app, _, medien = baue()
        folge = iter([341, 340])
        app._menue_anzeigen = lambda h, e, x, y: next(folge)
        app.regie_menue(1, 1)
        self.assertEqual(medien.modus, "offen")
        app._erfasser = Erfasser3(Kombination(0, 0x79))
        app.regie_menue(1, 1)
        self.assertEqual(medien.sprechtaste_vk, 0x79)

    def test_einstellungen_werden_gespeichert(self):
        with tempfile.TemporaryDirectory() as temp:
            pfad = Path(temp) / "e.json"
            app, _, medien = baue(pfad)
            app.mik_modus_umschalten()
            app._erfasser = Erfasser3(Kombination(0, 0x7A))
            app.sprechtaste_festlegen()
            app.beenden()
            g = json.loads(pfad.read_text(encoding="utf-8"))["elemente"]["_global"]
            self.assertEqual((g["mik_modus"], g["sprechtaste_vk"]), ("offen", 0x7A))


if __name__ == "__main__":
    unittest.main()
