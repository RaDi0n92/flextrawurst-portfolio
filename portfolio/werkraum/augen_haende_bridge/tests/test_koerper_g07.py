"""G07: Bilddatei als Quelle, Auslieferungszähler im Menü, Bridge-Fenster aus der Aufnahme ausnehmen (R038, R036, R039)."""

from __future__ import annotations

import base64
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper import bild
from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
from test_koerper_anwendung import _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


def mit_farbe(basis):
    def bauen(**kwargs):
        k = basis(**kwargs)
        k.farbe_hex = "#00E5FF"
        return k
    return bauen


def baue(datei="C:/bild.png", kodieren=lambda p: (b"\xff\xd8JPEG", 40, 30), wahl=lambda h, e, x, y: 0):
    basis, gebaut = _koerper_bauen()
    strom = Mock(spec=Bilderstrom)
    strom.ziele = {}
    waehlen = Mock(return_value=datei)
    app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=mit_farbe(basis), bilderstrom=strom,
                                datei_waehlen=waehlen, datei_kodieren=kodieren, menue_anzeigen=wahl, bildschirm=lambda: (0, 0, 1920, 1080))
    return app, gebaut, strom, waehlen


class BilddateiTests(unittest.TestCase):
    def test_gewaehlte_datei_geht_als_frame_mit_quelle_file_an_genau_diesen_agenten(self):
        app, gebaut, strom, waehlen = baue()
        self.assertTrue(app.bild_datei_senden("t-1"))
        art, payload = app.runtime.gesendet[-1]
        self.assertEqual(art, "frame")
        self.assertEqual((payload["source"], payload["terminal_id"], payload["mime"]), ("file", "t-1", "image/jpeg"))
        self.assertEqual((payload["width"], payload["height"]), (40, 30))
        self.assertEqual(base64.b64decode(payload["data"]), b"\xff\xd8JPEG")
        self.assertIn("Bild an", app.hinweis)

    def test_abbruch_im_dialog_sendet_nichts(self):
        app, gebaut, strom, waehlen = baue(datei=None)
        vorher = len(app.runtime.gesendet)
        self.assertFalse(app.bild_datei_senden("t-1"))
        self.assertEqual(len(app.runtime.gesendet), vorher)

    def test_unlesbare_datei_wird_gemeldet_und_nichts_gesendet(self):
        def kaputt(pfad):
            raise OSError("kaputt")
        app, gebaut, strom, waehlen = baue(kodieren=kaputt)
        vorher = len(app.runtime.gesendet)
        self.assertFalse(app.bild_datei_senden("t-1"))
        self.assertEqual(len(app.runtime.gesendet), vorher)
        self.assertIn("nicht lesbar", app.hinweis)

    def test_nur_terminal_und_not_aus_sperren_das_senden(self):
        app, gebaut, strom, waehlen = baue()
        app.nur_terminal_setzen("t-1", True)
        self.assertFalse(app.bild_datei_senden("t-1"))
        app.nur_terminal_setzen("t-1", False)
        app.not_aus.ausloesen("x")
        self.assertFalse(app.bild_datei_senden("t-1"))
        waehlen.assert_not_called()

    def test_ueber_das_raute_menue_erreichbar(self):
        app, gebaut, strom, waehlen = baue()
        gebaut[0].kwargs["bild_datei"]()
        self.assertEqual(app.runtime.gesendet[-1][0], "frame")


class EchteDateiTests(unittest.TestCase):
    def test_png_wird_zu_jpeg_und_grosse_bilder_werden_verkleinert(self):
        from PIL import Image
        temp = Path(tempfile.mkdtemp(prefix="bd-"))
        Image.new("RGBA", (3000, 1500), (10, 200, 30, 128)).save(temp / "gross.png")
        daten, b, h = bild.datei_zu_jpeg(str(temp / "gross.png"))
        self.assertEqual((b, h), (1920, 960))
        self.assertTrue(daten.startswith(b"\xff\xd8"))
        self.assertLessEqual(len(daten), bild.MAX_JPEG_BYTES)
        Image.new("RGB", (40, 30), (255, 0, 0)).save(temp / "klein.bmp")
        self.assertEqual(bild.datei_zu_jpeg(str(temp / "klein.bmp"))[1:], (40, 30))

    def test_keine_bilddatei_wirft(self):
        temp = Path(tempfile.mkdtemp(prefix="bd-"))
        (temp / "x.png").write_text("kein bild")
        with self.assertRaises(Exception):
            bild.datei_zu_jpeg(str(temp / "x.png"))


class BilderTextTests(unittest.TestCase):
    def test_menutext_nennt_den_auslieferungszaehler_und_nur_terminal(self):
        app, gebaut, strom, waehlen = baue()
        strom.ziele = {"t-1": SimpleNamespace(gesendet=7)}
        strom.an.return_value = True
        self.assertEqual(app._bilder_text("t-1"), "an, 7 gesendet")
        strom.an.return_value = False
        self.assertEqual(app._bilder_text("t-1"), "aus, 7 gesendet")
        app.nur_terminal_setzen("t-1", True)
        self.assertEqual(app._bilder_text("t-1"), "aus (nur Terminal)")


class BridgeImBildTests(unittest.TestCase):
    def test_umschalten_ausnehmen_und_zurueck_wird_gespeichert(self):
        from augen_haende_bridge.koerper import fenster as fm
        aufrufe = []
        original = fm.bild_ausnahme_setzen
        fm.bild_ausnahme_setzen = lambda an: aufrufe.append(an) or 3
        try:
            temp = tempfile.mkdtemp(prefix="bb-")
            from augen_haende_bridge.koerper.einstellungen import Einstellungen
            einst = Einstellungen(Path(temp) / "e.json")
            basis, gebaut = _koerper_bauen()
            app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=mit_farbe(basis),
                                        einstellungen=einst, bildschirm=lambda: (0, 0, 1920, 1080))
            app.bridge_im_bild_umschalten()
            self.assertEqual((app.bridge_im_bild, aufrufe), (False, [True]))
            self.assertEqual(einst.element("_global").get("bridge_im_bild"), False)
            self.assertIn("ausgenommen", app.hinweis)
            app.bridge_im_bild_umschalten()
            self.assertEqual((app.bridge_im_bild, aufrufe), (True, [True, False]))
            self.assertNotIn("bridge_im_bild", einst.element("_global"))
        finally:
            fm.bild_ausnahme_setzen = original

    def test_nimmt_windows_die_ausnahme_nicht_an_bleibt_alles_wie_es_war(self):
        from augen_haende_bridge.koerper import fenster as fm
        original = fm.bild_ausnahme_setzen
        fm.bild_ausnahme_setzen = lambda an: 0
        try:
            basis, gebaut = _koerper_bauen()
            app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=mit_farbe(basis),
                                        bildschirm=lambda: (0, 0, 1920, 1080))
            app._fenster_art["x"] = ("chat", "chat", Mock())
            app.bridge_im_bild_umschalten()
            self.assertTrue(app.bridge_im_bild)
            self.assertIn("nimmt die Ausnahme nicht an", app.hinweis)
        finally:
            fm.bild_ausnahme_setzen = original

    def test_regie_menue_hat_den_eintrag_mit_warnung(self):
        gesehen = []
        app, gebaut, strom, waehlen = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.regie_menue(0, 0)
        self.assertTrue(any(e and "Bridge-Fenster im Bild der Agenten: an" in e[1] for e in gesehen[0]))
        app.bridge_im_bild = False
        app.regie_menue(0, 0)
        self.assertTrue(any(e and "sehen deine Banner nicht" in e[1] for e in gesehen[1]))


if __name__ == "__main__":
    unittest.main()
