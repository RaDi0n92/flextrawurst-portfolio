"""G07 (Bildfolge, Überlastanzeige) und R020 (Terminal-Plätze tauschen)."""

from __future__ import annotations

import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.bildfolge import Bildfolgen, bilder_im_ordner
from test_koerper_anwendung_identitaet import _zweiter
from test_koerper_anwendung_nur_terminal_ort import FakeFenster, baue, arten


def warte(bedingung, timeout=5.0):
    ende = time.monotonic() + timeout
    while time.monotonic() < ende and not bedingung():
        time.sleep(0.01)
    return bedingung()


class OrdnerTests(unittest.TestCase):
    def test_bilder_in_namensreihenfolge_und_nur_bilddateien(self):
        t = tempfile.mkdtemp(prefix="bf-")
        for n in ("b.png", "a.JPG", "c.txt", "d.gif", ".versteckt"):
            Path(t, n).write_bytes(b"x")
        self.assertEqual([os.path.basename(p) for p in bilder_im_ordner(t)], ["a.JPG", "b.png", "d.gif"])

    def test_fehlender_ordner_ergibt_leere_liste(self):
        self.assertEqual(bilder_im_ordner("/gibt/es/nicht"), [])

    def test_begrenzt_auf_500_bilder(self):
        t = tempfile.mkdtemp(prefix="bf-")
        for i in range(520):
            Path(t, f"{i:04d}.png").write_bytes(b"x")
        self.assertEqual(len(bilder_im_ordner(t)), 500)


class FolgenTests(unittest.TestCase):
    def test_sendet_der_reihe_nach_und_endet(self):
        gesendet, fertig = [], []
        f = Bildfolgen(lambda tid, p: gesendet.append((tid, p)) or True, takt_s=0.01, fertig=fertig.append)
        self.assertTrue(f.starten("t-1", ["a", "b", "c"]))
        self.assertTrue(warte(lambda: fertig))
        self.assertEqual(gesendet, [("t-1", "a"), ("t-1", "b"), ("t-1", "c")])
        self.assertEqual(f.folgen["t-1"].text(), "beendet")

    def test_leere_liste_startet_nichts(self):
        self.assertFalse(Bildfolgen(lambda t, p: True).starten("t-1", []))

    def test_pausieren_haelt_an_und_fortsetzen_macht_weiter(self):
        gesendet = []
        f = Bildfolgen(lambda tid, p: gesendet.append(p) or True, takt_s=0.05)
        f.starten("t-1", [str(i) for i in range(50)])
        self.assertTrue(warte(lambda: len(gesendet) >= 2))
        f.pausieren("t-1", True)
        time.sleep(0.15)
        stand = len(gesendet)
        time.sleep(0.3)
        self.assertEqual(len(gesendet), stand)
        self.assertIn("pausiert", f.text("t-1"))
        f.pausieren("t-1", False)
        self.assertTrue(warte(lambda: len(gesendet) > stand))
        f.stoppen("t-1")

    def test_stoppen_beendet_sofort_und_nichts_startet_von_selbst_neu(self):
        gesendet = []
        f = Bildfolgen(lambda tid, p: gesendet.append(p) or True, takt_s=0.02)
        f.starten("t-1", [str(i) for i in range(1000)])
        warte(lambda: len(gesendet) >= 2)
        f.stoppen("t-1")
        n = len(gesendet)
        time.sleep(0.2)
        self.assertEqual(len(gesendet), n)
        self.assertEqual(f.text("t-1"), "keine")

    def test_fehlgeschlagene_bilder_werden_gezaehlt_die_folge_geht_weiter(self):
        fertig = []
        f = Bildfolgen(lambda tid, p: p != "b", takt_s=0.01, fertig=fertig.append)
        f.starten("t-1", ["a", "b", "c"])
        self.assertTrue(warte(lambda: fertig))
        self.assertEqual((f.folgen["t-1"].index, f.folgen["t-1"].fehler), (3, 1))

    def test_neue_folge_ersetzt_die_alte_fuer_denselben_agenten(self):
        gesendet = []
        f = Bildfolgen(lambda tid, p: gesendet.append(p) or True, takt_s=0.02)
        f.starten("t-1", ["alt"] * 100)
        warte(lambda: gesendet)
        f.starten("t-1", ["neu1", "neu2"])
        self.assertTrue(warte(lambda: "neu2" in gesendet))
        f.stoppen("t-1")


class AnwendungsTests(unittest.TestCase):
    def _ordner(self, n=3):
        t = tempfile.mkdtemp(prefix="bf-")
        pfade = [str(Path(t, f"{i}.png")) for i in range(n)]
        for p in pfade:
            Path(p).write_bytes(b"x")
        return pfade

    def test_start_sendet_ab_dem_gewaehlten_bild_als_frames_mit_quelle_file(self):
        pfade = self._ordner(3)
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app._datei_waehlen = lambda hwnd: pfade[1]
        app._datei_kodieren = lambda p: (b"\xff\xd8", 10, 10)
        app.bildfolgen._takt_s = 0.01
        self.assertTrue(app.bildfolge_starten("t-1"))
        self.assertTrue(warte(lambda: arten(app).count("frame") >= 2))
        frames = [p for k, p in app.runtime.gesendet if k == "frame"]
        self.assertTrue(all(p["source"] == "file" and p["terminal_id"] == "t-1" for p in frames))
        self.assertTrue("gestartet (2 Bilder)" in app.hinweis or "zu Ende (2/2 gesendet" in app.hinweis, app.hinweis)  # die kurze Folge kann schon fertig sein

    def test_nur_terminal_und_not_aus_stoppen_die_folge(self):
        pfade = self._ordner(50)
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app._datei_waehlen = lambda hwnd: pfade[0]
        app._datei_kodieren = lambda p: (b"\xff\xd8", 10, 10)
        app.bildfolgen._takt_s = 0.02
        app.bildfolge_starten("t-1")
        warte(lambda: "frame" in arten(app))
        app.nur_terminal_setzen("t-1", True)
        self.assertNotIn("t-1", app.bildfolgen.folgen)
        app.nur_terminal_setzen("t-1", False)
        self.assertTrue(app.bildfolge_starten("t-1"))
        app.not_aus.ausloesen("test")
        self.assertTrue(warte(lambda: "t-1" not in app.bildfolgen.folgen))

    def test_leerer_ordner_wird_gemeldet(self):
        t = tempfile.mkdtemp(prefix="bf-")
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app._datei_waehlen = lambda hwnd: str(Path(t, "x.png"))
        self.assertFalse(app.bildfolge_starten("t-1"))
        self.assertIn("keine Bilder", app.hinweis)

    def test_agent_entfernen_beendet_die_folge(self):
        pfade = self._ordner(50)
        app, gebaut, strom, halter, welt, medien, _ = baue()
        app._datei_waehlen = lambda hwnd: pfade[0]
        app._datei_kodieren = lambda p: (b"\xff\xd8", 10, 10)
        app.bildfolgen._takt_s = 0.02
        app.bildfolge_starten("t-1")
        app._agent_entfernen("t-1")
        self.assertNotIn("t-1", app.bildfolgen.folgen)

    def test_menue_zeigt_den_zustand_und_pausieren_stoppen(self):
        pfade = self._ordner(60)
        gesehen = []
        app, gebaut, strom, halter, welt, medien, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 3501)
        app._datei_waehlen = lambda hwnd: pfade[0]
        app._datei_kodieren = lambda p: (b"\xff\xd8", 10, 10)
        app.bildfolgen._takt_s = 0.05
        app.bildfolge_starten("t-1")
        app.bildfolge_menue("t-1", 0, 0)
        self.assertIn("läuft", gesehen[0][0][1])
        self.assertTrue(app.bildfolgen.folgen["t-1"].pausiert)  # 3501 = Pausieren
        app._menue_anzeigen = lambda h, e, x, y: 3502
        app.bildfolge_menue("t-1", 0, 0)
        self.assertNotIn("t-1", app.bildfolgen.folgen)

    def test_ueberlast_steht_im_bilder_text(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        strom.ziele = {"t-1": SimpleNamespace(gesendet=5)}
        strom.an.return_value = True
        app.sender = SimpleNamespace(verworfen=3, senden=lambda *a: True)
        self.assertEqual(app._bilder_text("t-1"), "an, 5 gesendet, Überlast: 3 verworfen")


class PlaetzeTests(unittest.TestCase):
    def test_zwei_terminals_tauschen_ort_und_groesse_und_behalten_ihre_sitzung(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        _zweiter(app)
        a, b = gebaut[0].terminal, gebaut[1].terminal
        a.x, a.y, a.b, a.h = 100, 100, 400, 300
        b.x, b.y, b.b, b.h = 900, 500, 600, 200
        self.assertTrue(app.plaetze_tauschen("t-1", "t-2"))
        self.assertEqual((a.x, a.y, a.b, a.h), (900, 500, 600, 200))
        self.assertEqual((b.x, b.y, b.b, b.h), (100, 100, 400, 300))
        self.assertEqual([x.terminal_id for x in app.agenten.values()], ["t-1", "t-2"])  # Sitzungen unverändert
        self.assertIn("getauscht", app.hinweis)

    def test_doppelt_tauschen_stellt_den_ursprung_wieder_her(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        _zweiter(app)
        a, b = gebaut[0].terminal, gebaut[1].terminal
        a.x, a.y = 10, 20
        b.x, b.y = 300, 400
        app.plaetze_tauschen("t-1", "t-2")
        app.plaetze_tauschen("t-1", "t-2")
        self.assertEqual(((a.x, a.y), (b.x, b.y)), ((10, 20), (300, 400)))

    def test_mit_sich_selbst_oder_unbekanntem_agenten_tut_es_nichts(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        self.assertFalse(app.plaetze_tauschen("t-1", "t-1"))
        self.assertFalse(app.plaetze_tauschen("t-1", "t-99"))

    def test_menue_nennt_die_anderen_agenten_oder_erklaert_dass_keiner_da_ist(self):
        gesehen = []
        app, gebaut, strom, halter, welt, medien, _ = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.plaetze_menue("t-1", 0, 0)
        self.assertIn("Kein anderer Agent", gesehen[0][-1][1])
        _zweiter(app)
        app.plaetze_menue("t-1", 0, 0)
        self.assertTrue(any(e and e[1] == "Codex 2" for e in gesehen[1]))

    def test_menuewahl_tauscht(self):
        app, gebaut, strom, halter, welt, medien, _ = baue()
        _zweiter(app)
        gebaut[0].terminal.x = 5
        gebaut[1].terminal.x = 700
        app._menue_anzeigen = lambda h, e, x, y: 3401  # der zweite Agent (Index 1)
        app.plaetze_menue("t-1", 0, 0)
        self.assertEqual(gebaut[0].terminal.x, 700)


if __name__ == "__main__":
    unittest.main()
