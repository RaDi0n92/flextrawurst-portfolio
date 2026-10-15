"""Regie- und Medienleiste in der Anwendung: Auswahl, Regiesprüche, Medien, Not-Aus, Kamerabild zum Relay."""

from __future__ import annotations

import base64
import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper.anwendung import GESPERRTE_ARTEN
from augen_haende_bridge.koerper.kamera import KameraFrame
from augen_haende_bridge.koerper.medien import Medien
from augen_haende_bridge.koerper.regie_fenster import REGIESPRUECHE
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen


class FakeRegie:
    def __init__(self, x, y, **aufrufe):
        self.x, self.y, self.aufrufe = x, y, aufrufe
        self.hwnd, self.gezeigt, self.zustaende, self.geschlossen = 7, False, [], False

    def zeige(self, aktivieren=True):
        self.gezeigt = True

    def setze(self, **kwargs):
        self.zustaende.append(kwargs)

    def schliessen(self):
        self.geschlossen = True


class FakeChat:
    def __init__(self, x, y, **aufrufe):
        self.x, self.y, self.aufrufe = x, y, aufrufe
        self.verlauf, self.farben, self.empfaenger = [], {}, None
        self.gezeigt, self.sichtbar_ = False, True
        self.geschlossen = False

    def zeige(self, aktivieren=True): self.gezeigt, self.sichtbar_ = True, True
    def verberge(self): self.sichtbar_ = False
    def sichtbar(self): return self.sichtbar_
    def schliessen(self): self.geschlossen = True
    def farbe_setzen(self, sender, farbe): self.farben[sender] = farbe
    def empfaenger_setzen(self, name, farbe): self.empfaenger = (name, farbe)
    def empfangen(self, sender, text): self.verlauf.append((sender, text))


class FakeMedien:
    audio_uebertragung = False

    def __init__(self):
        self.mik, self.cam, self.fehler, self.gestoppt = "aus", "aus", "", []
        self._weitergeben = self._melden = None

    def mikrofon_zustand(self, t): return self.mik
    def kamera_zustand(self, t): return self.cam
    def fehlertext(self, t): return self.fehler

    def kamera_umschalten(self, t):
        self.cam = "aus" if self.cam == "ein" else "ein"

    def mikrofon_umschalten(self, t):
        self.mik = "aus" if self.mik == "ein" else "ein"

    def stoppen(self, t): self.gestoppt.append(t)
    def alles_stoppen(self): self.gestoppt.append("alle")


def gestartet(menue_wahl=0):
    medien = FakeMedien()
    basis, gebaut_ = _koerper_bauen()

    def bauen(**kwargs):
        koerper = basis(**kwargs)
        koerper.farbe_hex = "#00E5FF"
        return koerper

    app, gui, gebaut = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=medien, koerper_bauen=bauen,
                                  menue_anzeigen=lambda hwnd, eintraege, x, y: menue_wahl)
    app._regie_anzeigen()
    return app, gebaut_, medien


class RegieTests(unittest.TestCase):
    def test_leiste_erscheint_mit_dem_ersten_agenten_unten_links(self):
        app, gebaut, _ = gestartet()
        self.assertTrue(app.regie.gezeigt)
        self.assertEqual(app.gewaehlt, "t-1")
        self.assertEqual(app.regie.zustaende[-1]["agent_name"], "Codex")
        self.assertLess(app.regie.x, 100)
        self.assertGreater(app.regie.y, 600)

    def test_regiespruch_erscheint_im_chat_und_als_banner_nicht_im_terminal(self):
        app, gebaut, _ = gestartet(menue_wahl=3)
        app.regie_menue(10, 10)
        gebaut[0].terminal.tippe.assert_not_called()
        self.assertEqual(app.chat.verlauf[-1], ("Daniel → alle", REGIESPRUECHE[2]))
        gebaut[0].zeige_daniel.assert_called_once_with(f"Daniel: {REGIESPRUECHE[2]}", "#F2F2F2")
        self.assertEqual([k for k, _ in app.runtime.gesendet if k == "terminal_input"], [])

    def test_chat_eingabe_geht_an_den_gewaehlten_agenten_nur_auf_den_schirm(self):
        app, gebaut, _ = gestartet()
        app.chat.aufrufe["gesendet"]("Schau mal links")
        gebaut[0].terminal.tippe.assert_not_called()
        self.assertEqual(app.chat.verlauf[-1], ("Daniel → alle", "Schau mal links"))
        gebaut[0].zeige_daniel.assert_called_once_with("Daniel: Schau mal links", "#F2F2F2")

    def test_agent_spricht_landet_im_gemeinsamen_chat(self):
        app, gebaut, _ = gestartet()
        app.ereignis(_event("raute_say", {"terminal_id": "t-1", "text": "Hallo Daniel"}))
        gebaut[0].raute.sagen.assert_called_once_with("Hallo Daniel")
        app._agent_hat_gesprochen("Codex", "Hallo Daniel")  # so meldet der Körper es der Anwendung
        self.assertEqual(app.chat.verlauf[-1], ("Codex", "Hallo Daniel"))
        self.assertIn("Codex", app.chat.farben)

    def test_chat_geht_standardmaessig_an_alle(self):
        app, _, _ = gestartet()
        self.assertEqual(app.chat.empfaenger[0], "alle")

    def _mit_zwei_agenten(self):
        app, gebaut, medien = gestartet()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Zwei",
                                               "state": "running", "exit_code": None, "reason": ""}))
        return app, gebaut

    def test_an_alle_zeigt_das_banner_im_ziel_jedes_agenten(self):
        app, gebaut = self._mit_zwei_agenten()
        app.daniel_sagt("Schaut mal")
        for koerper in gebaut:
            koerper.zeige_daniel.assert_called_once_with("Daniel: Schaut mal", "#F2F2F2")
        self.assertEqual(app.chat.verlauf[-1], ("Daniel → alle", "Schaut mal"))

    def test_klick_auf_an_schaltet_alle_agent_agent_alle_durch(self):
        app, gebaut = self._mit_zwei_agenten()
        namen = []
        for _ in range(4):
            app.empfaenger_wechseln()
            namen.append(app.chat.empfaenger[0])
        self.assertEqual(namen, ["Codex", "Zwei", "alle", "Codex"])

    def test_an_einen_einzelnen_nur_dessen_banner(self):
        app, gebaut = self._mit_zwei_agenten()
        app.empfaenger_wechseln()  # Codex
        app.daniel_sagt("nur du")
        gebaut[0].zeige_daniel.assert_called_once()
        gebaut[1].zeige_ticker.assert_not_called()
        self.assertEqual(app.chat.verlauf[-1], ("Daniel → Codex", "nur du"))

    def test_beendeter_agent_nimmt_den_empfaenger_zurueck_auf_alle(self):
        app, gebaut = self._mit_zwei_agenten()
        app.empfaenger_wechseln()
        app.agenten["t-1"].zustand = "exited"
        app.agent_beenden("t-1")
        self.assertIsNone(app.empfaenger)

    def test_chat_ohne_agent_geht_nur_in_den_verlauf(self):
        from test_koerper_anwendung import _anwendung
        app, _gui, _g = _anwendung(url=None, regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien())
        app.starten()
        app.daniel_sagt("hallo?")
        self.assertEqual(app.chat.verlauf[-1], ("Daniel", "hallo?"))

    def test_chat_ein_ausblenden_aus_dem_regie_menue(self):
        app, _, _ = gestartet(menue_wahl=300)
        app.regie_menue(10, 10)
        self.assertFalse(app.chat.sichtbar())

    def test_chat_steht_rechts_neben_der_leiste_unten(self):
        app, _, _ = gestartet()
        self.assertGreater(app.chat.x, app.regie.x)
        self.assertGreater(app.chat.y, 600)

    def test_menue_bietet_startliste_und_startet_aus_der_liste(self):
        app, gebaut, _ = gestartet(menue_wahl=100)
        app.regie_menue(10, 10)
        art, nutz = app.runtime.gesendet[-1]
        self.assertEqual((art, nutz["start_id"]), ("terminal_start", "codex-vd1"))

    def test_menue_start_gesperrt_bei_notaus(self):
        app, _, _ = gestartet(menue_wahl=100)
        n = len(app.runtime.gesendet)
        app.not_aus.ausloesen("x")
        app.regie_menue(10, 10)
        self.assertEqual(len(app.runtime.gesendet), n)

    def test_menue_bridge_beenden(self):
        app, _, medien = gestartet(menue_wahl=200)
        app.regie_menue(10, 10)
        self.assertIn("alle", medien.gestoppt)

    def test_leiste_steht_schon_vor_dem_ersten_agenten(self):
        from test_koerper_anwendung import _anwendung
        app, _gui, _g = _anwendung(url=None, regie_bauen=FakeRegie, medien=FakeMedien())
        app.starten()
        self.assertTrue(app.regie.gezeigt)
        self.assertEqual(app.regie.zustaende[-1]["agent_name"], "kein Agent")

    def test_abgebrochenes_menue_tippt_nichts(self):
        app, gebaut, _ = gestartet(menue_wahl=0)
        app.regie_menue(10, 10)
        gebaut[0].terminal.tippe.assert_not_called()

    def test_medienknoepfe_zeigen_echten_zustand(self):
        app, _, medien = gestartet()
        app.kamera_umschalten()
        app.mikrofon_umschalten()
        self.assertEqual((app.regie.zustaende[-1]["kamera"], app.regie.zustaende[-1]["mikrofon"]), ("ein", "ein"))

    def test_medienfehler_wird_sichtbar_gemeldet(self):
        app, _, medien = gestartet()
        medien.fehler = "Kamera: kamera_nicht_gefunden"
        app.kamera_umschalten()
        self.assertIn("kamera_nicht_gefunden", app.hinweis)

    def test_notaus_knopf_schaltet_und_zeigt_zustand(self):
        app, _, _ = gestartet()
        app.notaus_umschalten()
        self.assertTrue(app.not_aus.aktiv)
        self.assertTrue(app.regie.zustaende[-1]["notaus"])
        app.notaus_umschalten()
        self.assertFalse(app.not_aus.aktiv)
        self.assertFalse(app.regie.zustaende[-1]["notaus"])

    def test_regiespruch_bei_notaus_geht_nicht_hinaus(self):
        app, gebaut, _ = gestartet()
        app.not_aus.ausloesen("test")
        gebaut[0].kwargs["terminal_senden"](b"Go!\r")
        self.assertIn("Not-Aus", app.hinweis)

    def test_agent_wechseln_ist_ein_ring(self):
        app, _, _ = gestartet()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Zwei",
                                               "state": "running", "exit_code": None, "reason": ""}))
        app.agent_wechseln()
        self.assertEqual(app.gewaehlt, "t-2")
        app.agent_wechseln()
        self.assertEqual(app.gewaehlt, "t-1")

    def test_kamerabild_geht_als_frame_mit_terminal_id(self):
        app, _, _ = gestartet()
        gesendet = app.runtime.gesendet
        frame = KameraFrame(1, 5, 4, 2, bytes(range(24)), "test")
        app._kamera_frame("t-1", frame)
        art, nutz = gesendet[-1]
        self.assertEqual((art, nutz["terminal_id"], nutz["mime"], nutz["width"], nutz["height"]),
                         ("frame", "t-1", "image/jpeg", 4, 2))
        self.assertTrue(base64.b64decode(nutz["data"]).startswith(b"\xff\xd8"))
        self.assertIn("frame", GESPERRTE_ARTEN)

    def test_kamerabild_bei_notaus_verworfen(self):
        app, _, _ = gestartet()
        n = len(app.runtime.gesendet)
        app.not_aus.ausloesen("x")
        app._kamera_frame("t-1", KameraFrame(1, 5, 4, 2, bytes(24), "test"))
        self.assertEqual(len(app.runtime.gesendet), n)

    def test_beenden_stoppt_medien_und_schliesst_leiste(self):
        app, _, medien = gestartet()
        regie, chat = app.regie, app.chat
        app.beenden()
        self.assertIn("alle", medien.gestoppt)
        self.assertTrue(regie.geschlossen)
        self.assertTrue(chat.geschlossen)
        self.assertIsNone(app.chat)


class BeendenTests(unittest.TestCase):
    def test_ein_fehler_in_einem_schritt_haelt_das_beenden_nicht_auf(self):
        app, gebaut, medien = gestartet()
        gebaut[0].schliessen.side_effect = RuntimeError("kaputt")
        regie, chat = app.regie, app.chat
        gemeldet = []
        app.fehler_haken = lambda wo, fehler: gemeldet.append(wo)
        app.beenden()
        self.assertTrue(regie.geschlossen)
        self.assertTrue(chat.geschlossen)
        self.assertEqual(app.gui.beendet, 0)
        self.assertEqual(len(app.abbau_fehler), 1)
        self.assertEqual(gemeldet, ["beenden/koerper Codex"])

    def test_fenster_werden_vor_den_langsamen_schritten_geschlossen(self):
        app, gebaut, medien = gestartet()
        reihenfolge = []
        regie, chat = app.regie, app.chat
        gebaut[0].schliessen.side_effect = lambda: reihenfolge.append("koerper")
        regie.schliessen = lambda: reihenfolge.append("regie")
        chat.schliessen = lambda: reihenfolge.append("chat")
        medien.alles_stoppen = lambda: reihenfolge.append("medien")
        app.runtime.stop = lambda: reihenfolge.append("runtime")
        app.beenden()
        self.assertEqual(reihenfolge, ["koerper", "regie", "chat", "medien", "runtime"])

    def test_notbremse_wird_beim_beenden_scharf_gestellt(self):
        import augen_haende_bridge.koerper.anwendung as modul
        app, _, _ = gestartet()
        ausgeloest = []
        app.notbremse = lambda: ausgeloest.append(1)
        alt = modul.NOTBREMSE_S
        modul.NOTBREMSE_S = 0.05
        try:
            app.beenden()
            import time
            time.sleep(0.3)
        finally:
            modul.NOTBREMSE_S = alt
        self.assertEqual(ausgeloest, [1])

    def test_jeder_schritt_steht_im_log(self):
        app, _, _ = gestartet()
        zeilen = []
        app.log = zeilen.append
        app.beenden()
        self.assertEqual(zeilen[0], "beenden: Anfang")
        self.assertEqual(zeilen[-1], "beenden: Ende")
        self.assertIn("beenden: runtime", zeilen)

    def test_beenden_laeuft_ueber_den_gui_thread(self):
        app, _, _ = gestartet()
        aufgaben = []
        app.gui.post = aufgaben.append
        app.beenden()
        self.assertEqual(len(aufgaben), 1)
        self.assertIsNone(app.gui.beendet)
        aufgaben[0]()
        self.assertEqual(app.gui.beendet, 0)


if __name__ == "__main__":
    unittest.main()
