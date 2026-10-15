"""Selbstbild in der Anwendung: Fenster erscheint bei eingeschalteter Kamera, zeigt Frames, verschwindet wieder."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie
from test_koerper_anwendung import _gestartet, _koerper_bauen


class FakeKameraFenster:
    def __init__(self, x, y, **aufrufe):
        self.x, self.y, self.aufrufe = x, y, aufrufe
        self.sichtbar_, self.bild, self.geschlossen, self.deckkraft = False, None, False, 217

    def zeige(self, aktivieren=True): self.sichtbar_ = True
    def verberge(self): self.sichtbar_ = False
    def schliessen(self): self.geschlossen = True
    def bild_setzen(self, bgr, b, h): self.bild = (bgr, b, h)
    def bild_loeschen(self): self.bild = None
    def rechteck(self): return (self.x, self.y, self.x + 240, self.y + 190)
    def verschiebe(self, *a, **k): pass
    def setze_deckkraft(self, alpha): self.deckkraft = alpha


def baue():
    basis, _ = _koerper_bauen()

    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = "#00E5FF"
        return k

    gebaut = []

    def kamera_bauen(x, y, **kwargs):
        f = FakeKameraFenster(x, y, **kwargs)
        gebaut.append(f)
        return f

    medien = FakeMedien()
    app, gui, _ = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=medien, koerper_bauen=bauen,
                             kamera_bauen=kamera_bauen, bildschirm=lambda: (0, 0, 1920, 1080))
    return app, medien, gebaut


def frame():
    return SimpleNamespace(bgr=b"\x01" * 12, breite=2, hoehe=2)


class SelbstbildTests(unittest.TestCase):
    def test_ohne_kamera_gibt_es_kein_fenster(self):
        app, medien, gebaut = baue()
        app._kamera_fenster_abgleichen()
        self.assertEqual(gebaut, [])

    def test_kamera_ein_baut_und_zeigt_das_fenster_mit_name_und_farbe(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        self.assertEqual(len(gebaut), 1)
        self.assertTrue(gebaut[0].sichtbar_)
        self.assertEqual(gebaut[0].aufrufe["name"], "Codex")
        self.assertEqual(gebaut[0].aufrufe["farbe_hex"], "#00E5FF")

    def test_frames_kommen_im_fenster_an_und_nur_das_neueste_wird_gezeigt(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        app._kamera_vorschau("t-1", frame())
        self.assertEqual(gebaut[0].bild, (b"\x01" * 12, 2, 2))

    def test_kamera_aus_versteckt_das_fenster_und_wieder_an_zeigt_es(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        medien.cam = "aus"
        app._medien_gemeldet()
        self.assertFalse(gebaut[0].sichtbar_)
        medien.cam = "ein"
        app._medien_gemeldet()
        self.assertTrue(gebaut[0].sichtbar_)
        self.assertEqual(len(gebaut), 1)  # dasselbe Fenster, kein neues

    def test_startet_zeigt_den_wartetext(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        app._kamera_vorschau("t-1", frame())
        medien.cam = "startet"
        app._medien_gemeldet()
        self.assertIsNone(gebaut[0].bild)

    def test_x_blendet_aus_bis_die_kamera_aus_und_wieder_an_geht(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        gebaut[0].aufrufe["verbergen_gewuenscht"]()
        self.assertFalse(gebaut[0].sichtbar_)
        app._kamera_vorschau("t-1", frame())
        self.assertIsNone(gebaut[0].bild)  # versteckt: keine Arbeit
        app._medien_gemeldet()
        self.assertFalse(gebaut[0].sichtbar_)
        medien.cam = "aus"
        app._medien_gemeldet()
        medien.cam = "ein"
        app._medien_gemeldet()
        self.assertTrue(gebaut[0].sichtbar_)

    def test_agent_entfernen_schliesst_das_fenster(self):
        app, medien, gebaut = baue()
        medien.cam = "ein"
        app._medien_gemeldet()
        app._agent_entfernen("t-1")
        self.assertTrue(gebaut[0].geschlossen)
        self.assertNotIn("t-1", app.kamera_fenster)

    def test_ohne_kamera_bauer_tut_die_vorschau_nichts(self):
        basis, _ = _koerper_bauen()
        app, _, _ = _gestartet(medien=FakeMedien(), koerper_bauen=basis)
        app._kamera_vorschau("t-1", frame())
        app._kamera_fenster_abgleichen()
        self.assertEqual(app.kamera_fenster, {})


if __name__ == "__main__":
    unittest.main()
