"""G05.5: „nur Terminal“ (R122) und Ort der Elemente (R121) in der Anwendung."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
from augen_haende_bridge.koerper.einstellungen import Einstellungen
from augen_haende_bridge.koerper.ziel_halter import ORT_DESKTOP, ORT_ZIEL, ZielHalter
from test_koerper_anwendung import _event, _gestartet, _koerper_bauen
from test_koerper_anwendung_bilderstrom import bindung
from test_koerper_anwendung_identitaet import _zweiter
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


class FakeFenster:
    def __init__(self):
        self.x, self.y, self.b, self.h, self.sichtbar_ = 300, 200, 100, 60, True
        self.deckkraft = 200

    def rechteck(self):
        return (self.x, self.y, self.x + self.b, self.y + self.h)

    def verschiebe(self, x, y, b=None, h=None):
        self.x, self.y = x, y
        if b is not None:
            self.b = b
        if h is not None:
            self.h = h

    def verberge(self):
        self.sichtbar_ = False

    def zeige(self, aktivieren=True):
        self.sichtbar_ = True

    def sichtbar(self):
        return self.sichtbar_

    def setze_deckkraft(self, a):
        self.deckkraft = a

    hwnd = 5


class Welt:
    def __init__(self):
        self.rect, self.minimiert, self.da = (200, 100, 800, 500), False, True

    def zustand(self, hwnd):
        return (self.da, self.minimiert if self.da else False, None if (self.minimiert or not self.da) else self.rect)


def baue(pfad=None, wahl=lambda h, e, x, y: 0, mit_welt=True):
    basis, gebaut = _koerper_bauen()
    welt = Welt()
    gesendet = []

    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = "#00E5FF"
        k.raute = FakeFenster()
        k.terminal = FakeFenster()
        k.raute.status = "verbunden"
        k.terminal.setze_augen = Mock()
        k.terminal.setze_zustand = Mock()
        k.augen_setzen = Mock()
        k.setze_identitaet = Mock()
        k.zeige_daniel = Mock()
        k.zeige_ticker = Mock()
        k.terminal_ausgeblendet = False
        return k

    strom = Mock(spec=Bilderstrom)
    strom.ziele = {}
    halter = ZielHalter(zustand=welt.zustand)
    einst = Einstellungen(Path(pfad)) if pfad else None
    if einst:
        einst.laden()
    medien = FakeMedien()
    app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=medien, koerper_bauen=bauen, einstellungen=einst,
                                menue_anzeigen=wahl, bildschirm=lambda: (0, 0, 1920, 1080), bilderstrom=strom,
                                bild_kodieren=lambda *a: (b"\xff\xd8\xff", 32, 16), ziel_halter=halter)
    return app, gebaut, strom, halter, welt, medien, einst


def arten(app):
    return [k for k, _ in app.runtime.gesendet]


class NurTerminalTests(unittest.TestCase):
    def test_einschalten_stoppt_bilder_kamera_und_raute_meldungen_fuer_diesen_agenten(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        medien.cam = "ein"
        app.nur_terminal_setzen("t-1", True)
        self.assertTrue(app.agenten["t-1"].nur_terminal)
        self.assertEqual(medien.cam, "aus")  # die laufende Kamera wurde ausgeschaltet
        gebaut[0].augen_setzen.assert_called_with(False)
        self.assertEqual(gebaut[0].kwargs["augen_an"](), False)

    def test_bilder_werden_nicht_gesendet_weder_stream_noch_erstes_bild(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app.nur_terminal_setzen("t-1", True)
        vorher = arten(app).count("frame")
        gebaut[0].kwargs["ziel_gebunden"](bindung())
        self.assertEqual(arten(app).count("frame"), vorher)
        self.assertFalse(app.strom_senden("t-1", {"mime": "image/jpeg"}))
        app.nur_terminal_setzen("t-1", False)
        self.assertTrue(app.strom_senden("t-1", {"mime": "image/jpeg", "data": "AA==", "source": "capture", "captured_at_ms": 1,
                                                  "width": 1, "height": 1, "terminal_id": "t-1"}))

    def test_kamerabilder_gehen_nicht_hinaus_und_die_kamera_laesst_sich_nicht_einschalten(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app.nur_terminal_setzen("t-1", True)
        vorher = arten(app).count("frame")
        app._kamera_frame("t-1", SimpleNamespace(bgr=b"\x00" * 12, breite=2, hoehe=2, aufgenommen_ms=1))
        self.assertEqual(arten(app).count("frame"), vorher)
        app.gewaehlt = "t-1"
        app.kamera_umschalten()
        self.assertEqual(medien.cam, "aus")
        self.assertIn("nur Terminal", app.hinweis)

    def test_haende_tippen_nicht(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app.nur_terminal_setzen("t-1", True)
        app._raute_tippt({"terminal_id": "t-1", "text": "hallo"})
        gebaut[0].zeige_ticker.assert_not_called()  # nicht einmal eine Meldung, es passiert nichts

    def test_mikrofon_bleibt_unberuehrt(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        medien.mik = "ein"
        app.nur_terminal_setzen("t-1", True)
        self.assertEqual(medien.mik, "ein")

    def test_ausschalten_stellt_alles_wieder_her(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app.agenten["t-1"].haende = False  # eigener Schalter vorher
        app.nur_terminal_setzen("t-1", True)
        app.nur_terminal_setzen("t-1", False)
        self.assertFalse(app.agenten["t-1"].nur_terminal)
        self.assertFalse(app.agenten["t-1"].haende)  # die einzelnen Schalter behalten ihre Werte
        gebaut[0].augen_setzen.assert_called_with(True)

    def test_je_agent_einzeln_der_andere_bleibt_unberuehrt(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        _zweiter(app)
        app.nur_terminal_setzen("t-1", True)
        self.assertTrue(app.strom_senden("t-2", {"mime": "image/jpeg", "data": "AA==", "source": "capture", "captured_at_ms": 1,
                                                  "width": 1, "height": 1, "terminal_id": "t-2"}))
        self.assertFalse(app.agenten["t-2"].nur_terminal)

    def test_fuer_alle_gleichzeitig_und_wieder_zurueck(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        _zweiter(app)
        app.nur_terminal_alle()
        self.assertTrue(all(a.nur_terminal for a in app.agenten.values()))
        app.nur_terminal_alle()
        self.assertFalse(any(a.nur_terminal for a in app.agenten.values()))
        app.nur_terminal_setzen("t-1", True)  # nur einer ist an: „alle“ schaltet dann alle an
        app.nur_terminal_alle()
        self.assertTrue(all(a.nur_terminal for a in app.agenten.values()))

    def test_umschalten_ueber_menue_der_raute_und_die_regie(self):
        gesehen = []
        app, gebaut, strom, halter, welt, medien, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 352)
        app.regie_menue(0, 0)
        self.assertTrue(all(a.nur_terminal for a in app.agenten.values()))
        self.assertTrue(any(e and "Nur Terminal für alle Agenten: an" in e[1] for e in gesehen[0]))
        gebaut[0].kwargs["nur_terminal_umschalten"]()
        self.assertFalse(app.agenten["t-1"].nur_terminal)

    def test_der_zustand_ueberlebt_den_neustart(self):
        temp = tempfile.mkdtemp(prefix="nt-")
        pfad = Path(temp) / "e.json"
        app, gebaut, *_ = baue(pfad)
        app.nur_terminal_setzen("t-1", True)
        app.beenden()
        app2, gebaut2, *_ = baue(pfad)
        self.assertTrue(app2.agenten["t-1"].nur_terminal)
        gebaut2[0].augen_setzen.assert_called_with(False)


class OrtTests(unittest.TestCase):
    def test_ohne_fenster_ziel_geht_es_nicht(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app.ort_wechseln("t-1", "raute")
        self.assertEqual(halter.ort("raute:t-1"), ORT_DESKTOP)
        self.assertIn("Kein einzelnes Fenster", app.hinweis)

    def test_mit_fenster_ziel_wechselt_das_element_und_bleibt_im_rahmen(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_wechseln("t-1", "raute")
        self.assertEqual(halter.ort("raute:t-1"), ORT_ZIEL)
        self.assertEqual(halter.ort("terminal:t-1"), ORT_DESKTOP)  # jedes Element einzeln
        welt.rect = (600, 300, 1200, 700)
        halter.tick()
        self.assertEqual((gebaut[0].raute.x, gebaut[0].raute.y), (700, 400))

    def test_minimieren_und_schliessen_des_ziels(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_wechseln("t-1", "raute")
        app.ort_wechseln("t-1", "terminal")
        welt.minimiert = True
        halter.tick()
        self.assertFalse(gebaut[0].raute.sichtbar_)
        self.assertFalse(gebaut[0].terminal.sichtbar_)
        welt.minimiert = False
        halter.tick()
        self.assertTrue(gebaut[0].raute.sichtbar_)
        welt.da = False
        halter.tick()
        self.assertFalse(gebaut[0].raute.sichtbar_)

    def test_desktop_element_bleibt_von_ziel_und_minimieren_unberuehrt(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_wechseln("t-1", "raute")
        welt.minimiert = True
        halter.tick()
        self.assertTrue(gebaut[0].terminal.sichtbar_)

    def test_menue_zeigt_den_ort_jedes_elements_und_wechselt(self):
        gesehen = []
        app, gebaut, strom, halter, welt, medien, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 3300)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_menue("t-1", 0, 0)
        texte = [e[1] for e in gesehen[0] if e]
        self.assertTrue(any("Raute" in t and "auf dem Desktop → ins Zielfenster" in t for t in texte))
        self.assertTrue(any("Terminal" in t for t in texte))
        self.assertEqual(halter.ort("raute:t-1"), ORT_ZIEL)

    def test_menue_ohne_fenster_ziel_erklaert_und_sperrt(self):
        gesehen = []
        app, gebaut, strom, halter, welt, medien, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.ort_menue("t-1", 0, 0)
        self.assertIn("Kein einzelnes Fenster", gesehen[0][0][1])
        self.assertTrue(all(e[2] for e in gesehen[0] if e and e[0] >= 3300))

    def test_wunsch_ueberlebt_den_neustart_und_gilt_beim_naechsten_fenster_ziel(self):
        temp = tempfile.mkdtemp(prefix="ort-")
        pfad = Path(temp) / "e.json"
        app, gebaut, strom, halter, welt, medien, einst = baue(pfad)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_wechseln("t-1", "raute")
        app.beenden()
        app2, gebaut2, strom2, halter2, welt2, *_ = baue(pfad)
        self.assertEqual(app2.agenten["t-1"].orte_gewuenscht, ("raute",))
        self.assertEqual(halter2.ort("raute:t-1"), ORT_DESKTOP)  # noch kein Fenster gebunden
        strom2.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        gebaut2[0].kwargs["ziel_gebunden"](bindung())
        self.assertEqual(halter2.ort("raute:t-1"), ORT_ZIEL)

    def test_bindung_loesen_schaltet_den_strom_auf_den_desktop_und_holt_die_elemente_zurueck(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        app.ort_wechseln("t-1", "raute")
        strom.ziele = {}  # Bilderstrom hat das Ziel verloren
        strom.binden.reset_mock()
        gebaut[0].kwargs["ziel_geloest"]()
        strom.binden.assert_called_once_with("t-1", None)  # ganzer Desktop, die Augen bleiben an
        strom.loesen.assert_not_called()
        self.assertEqual(halter.ort("raute:t-1"), ORT_DESKTOP)
        self.assertIn("Bindung gelöst", app.hinweis)

    def test_agent_entfernen_meldet_die_elemente_ab(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app._agent_entfernen("t-1")
        self.assertNotIn("raute:t-1", halter.elemente)


if __name__ == "__main__":
    unittest.main()
