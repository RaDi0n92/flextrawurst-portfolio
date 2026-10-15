"""G08 in der Anwendung: Zeichenmodus öffnen/schließen, Gate-Wahl, Speichern und Wiederkehr, Sichtbar-für-Menü, Anzeige, Komposition für den Agenten."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.arbeitsflaechen_anzeige import ArbeitsflaechenAnzeige
from augen_haende_bridge.koerper.bilderstrom import Bilderstrom
from augen_haende_bridge.koerper.komposition import Arbeitsflaechen
from augen_haende_bridge.koerper.objekte import Objekt
from test_koerper_anwendung_bilderstrom import bindung
from test_koerper_anwendung_identitaet import _zweiter
from test_koerper_anwendung_nur_terminal_ort import FakeFenster
from test_koerper_anwendung import _gestartet, _koerper_bauen
from test_koerper_anwendung_regie import FakeChat, FakeMedien, FakeRegie


class FakeZeichenFenster(FakeFenster):
    def __init__(self, rect, editor, farbe):
        super().__init__()
        self.x, self.y, self.b, self.h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
        self.editor, self.farbe, self.neu_aufrufe, self.geschlossen, self.hwnd = editor, farbe, 0, False, 321

    def neu(self):
        self.neu_aufrufe += 1

    def clientgroesse(self):
        return self.b, self.h

    def schliessen(self):
        self.geschlossen = True

    def fokus_erzwingen(self):
        return True


class FakeLeiste(FakeFenster):
    def __init__(self, x, y, editor, **kw):
        super().__init__()
        self.editor, self.kw, self.geschlossen, self.hwnd = editor, kw, False, 322
        self.b, self.h = 300, 90

    def neu_zeichnen(self):
        pass

    def schliessen(self):
        self.geschlossen = True


def baue(pfad=None, wahl=lambda h, e, x, y: 0):
    basis, gebaut = _koerper_bauen()

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
    arbeit = Arbeitsflaechen()
    fenster = []
    leisten = []
    app, gui, alle = _gestartet(regie_bauen=FakeRegie, chat_bauen=FakeChat, medien=FakeMedien(), koerper_bauen=bauen, menue_anzeigen=wahl,
                                bildschirm=lambda: (0, 0, 1920, 1080), bilderstrom=strom, bild_kodieren=lambda *a, **k: (b"\xff\xd8", 8, 8),
                                arbeit=arbeit, arbeit_pfad=Path(pfad) if pfad else None,
                                zeichen_bauen=lambda rect, editor, farbe: fenster.append(FakeZeichenFenster(rect, editor, farbe)) or fenster[-1],
                                leiste_bauen=lambda x, y, editor, **kw: leisten.append(FakeLeiste(x, y, editor, **kw)) or leisten[-1])
    return app, gebaut, strom, arbeit, fenster, leisten


class OeffnenTests(unittest.TestCase):
    def test_ohne_bindung_zeichnet_man_auf_dem_desktop_mit_hinweis(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        self.assertTrue(app.zeichnen_oeffnen("t-1"))
        self.assertEqual(app.editor_offen["schluessel"], "desktop")
        self.assertEqual((fenster[0].x, fenster[0].y, fenster[0].b, fenster[0].h), (0, 0, 1920, 1040))
        self.assertIn("nicht gebunden", app.hinweis)
        self.assertTrue(fenster[0].sichtbar_)

    def test_mit_fenster_ziel_liegt_der_editor_genau_auf_dem_fenster(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        from augen_haende_bridge.koerper import ziel_halter
        original = ziel_halter.fenster_zustand
        ziel_halter.fenster_zustand = lambda hwnd: (True, False, (300, 200, 900, 600))
        try:
            app.zeichnen_oeffnen("t-1")
        finally:
            ziel_halter.fenster_zustand = original
        self.assertEqual(app.editor_offen["schluessel"], "windows:window:77")
        self.assertEqual((fenster[0].x, fenster[0].y, fenster[0].b, fenster[0].h), (300, 200, 600, 400))

    def test_minimiertes_ziel_wird_erklaert_statt_gezeichnet(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        from augen_haende_bridge.koerper import ziel_halter
        original = ziel_halter.fenster_zustand
        ziel_halter.fenster_zustand = lambda hwnd: (True, True, None)
        try:
            self.assertFalse(app.zeichnen_oeffnen("t-1"))
        finally:
            ziel_halter.fenster_zustand = original
        self.assertIn("nicht sichtbar", app.hinweis)
        self.assertEqual(fenster, [])

    def test_schliessen_schliesst_beide_fenster_und_speichert(self):
        temp = tempfile.mkdtemp(prefix="zw-")
        app, gebaut, strom, arbeit, fenster, leisten = baue(Path(temp) / "a.json")
        app.zeichnen_oeffnen("t-1")
        app.editor_offen["editor"].werkzeug_setzen("rechteck")
        ed = app.editor_offen["editor"]
        ed.maus_runter(100, 100); ed.maus_bewegt(300, 300); ed.maus_hoch(300, 300)
        app.zeichnen_schliessen()
        self.assertTrue(fenster[0].geschlossen and leisten[0].geschlossen)
        self.assertIsNone(app.editor_offen)
        self.assertTrue((Path(temp) / "a.json").exists())

    def test_zweites_oeffnen_ersetzt_das_erste(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        app.zeichnen_oeffnen("t-1")
        app.zeichnen_oeffnen("t-1")
        self.assertTrue(fenster[0].geschlossen)
        self.assertFalse(fenster[1].geschlossen)

    def test_ohne_agent_oder_fensterfabrik_tut_es_nichts(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        self.assertFalse(app.zeichnen_oeffnen("t-99"))
        app._zeichen_bauen = None
        self.assertFalse(app.zeichnen_oeffnen("t-1"))

    def test_menues_raute_und_regie_oeffnen_den_zeichenmodus(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue(wahl=lambda h, e, x, y: 354)
        app.regie_menue(0, 0)
        self.assertIsNotNone(app.editor_offen)
        app.zeichnen_schliessen()
        gebaut[0].kwargs["zeichnen"]()
        self.assertIsNotNone(app.editor_offen)

    def test_aenderungen_im_editor_zeichnen_die_fenster_neu(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        app.zeichnen_oeffnen("t-1")
        vorher = fenster[0].neu_aufrufe
        app.editor_offen["editor"].werkzeug_setzen("kreis")
        self.assertGreater(fenster[0].neu_aufrufe, vorher)

    def test_beenden_der_anwendung_schliesst_den_zeichenmodus(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        app.zeichnen_oeffnen("t-1")
        app._abbauen()
        self.assertTrue(fenster[0].geschlossen)


class SichtbarMenueTests(unittest.TestCase):
    def test_privat_fuer_einen_agenten_und_nicht_fuer_den_anderen(self):
        auswahl = []
        app, gebaut, strom, arbeit, fenster, leisten = baue(wahl=lambda h, e, x, y: auswahl.append(e) or auswahl_wahl[0])
        auswahl_wahl = [0]
        _zweiter(app)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=None), "t-2": SimpleNamespace(hwnd=None)}  # beide am Desktop
        app.zeichnen_oeffnen("t-1")
        ed = app.editor_offen["editor"]
        auswahl_wahl[0] = 3610  # „Nur im Bild von Codex“ (erster Agent)
        app._zeichnen_sichtbar_menue(0, 0)
        texte = [e[1] for e in auswahl[0] if e]
        self.assertTrue(any("Nur im Bild von Codex" in t for t in texte) and any("Nur im Bild von Codex 2" in t for t in texte))
        self.assertEqual(ed.neu_empfaenger, ("t-1",))
        auswahl_wahl[0] = 3600  # Bildschirm umschalten
        app._zeichnen_sichtbar_menue(0, 0)
        self.assertFalse(ed.neu_bildschirm)

    def test_ohne_agenten_im_ziel_wird_es_erklaert(self):
        gesehen = []
        app, gebaut, strom, arbeit, fenster, leisten = baue(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.zeichnen_oeffnen("t-1")
        app.editor_offen["editor"]._agenten = lambda: []
        app._zeichnen_sichtbar_menue(0, 0)
        self.assertTrue(any(e and "Kein Agent in diesem Ziel" in e[1] for e in gesehen[0]))


class DauerhaftTests(unittest.TestCase):
    def test_objekte_kommen_nach_dem_neustart_wieder_sobald_dasselbe_programm_gebunden_wird(self):
        temp = tempfile.mkdtemp(prefix="dh-")
        pfad = Path(temp) / "a.json"
        app, gebaut, strom, arbeit, fenster, leisten = baue(pfad)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=4242)}
        b = bindung("windows:window:4242")
        b.item.process_path = "C:\\Programme\\Chrome.exe"
        gebaut[0].kwargs["ziel_gebunden"](b)
        arbeit.dokument("windows:window:4242").hinzufuegen(Objekt("o1", "text", [(0.2, 0.2)], text="bleibt", bildschirm=True))
        app.einstellungen_sichern()
        app2, gebaut2, strom2, arbeit2, *_ = baue(pfad)
        self.assertEqual(len(arbeit2.dokumente), 0)
        strom2.ziele = {"t-1": SimpleNamespace(hwnd=9999)}  # neues Fensterhandle, dasselbe Programm
        b2 = bindung("windows:window:9999")
        b2.item.process_path = "C:\\Andere\\chrome.exe"
        gebaut2[0].kwargs["ziel_gebunden"](b2)
        self.assertEqual([o.text for o in arbeit2.dokument("windows:window:9999").objekte.values()], ["bleibt"])

    def test_anderes_programm_bekommt_die_objekte_nicht(self):
        temp = tempfile.mkdtemp(prefix="dh-")
        pfad = Path(temp) / "a.json"
        app, gebaut, strom, arbeit, fenster, leisten = baue(pfad)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=4242)}
        b = bindung("windows:window:4242")
        b.item.process_path = "C:\\x\\chrome.exe"
        gebaut[0].kwargs["ziel_gebunden"](b)
        arbeit.dokument("windows:window:4242").hinzufuegen(Objekt("o1", "text", [(0.2, 0.2)], text="chrome"))
        app.einstellungen_sichern()
        app2, gebaut2, strom2, arbeit2, *_ = baue(pfad)
        strom2.ziele = {"t-1": SimpleNamespace(hwnd=5)}
        b2 = bindung("windows:window:5")
        b2.item.process_path = "C:\\x\\blender.exe"
        gebaut2[0].kwargs["ziel_gebunden"](b2)
        self.assertEqual(len(arbeit2.dokument("windows:window:5").objekte), 0)

    def test_leeres_dokument_loescht_den_gespeicherten_eintrag(self):
        temp = tempfile.mkdtemp(prefix="dh-")
        pfad = Path(temp) / "a.json"
        app, gebaut, strom, arbeit, fenster, leisten = baue(pfad)
        dok = arbeit.dokument("desktop")
        dok.hinzufuegen(Objekt("o1", "kreis", [(0.1, 0.1), (0.2, 0.2)]))
        app.einstellungen_sichern()
        self.assertIn("desktop", arbeit.gespeichert)
        dok.entfernen(["o1"])
        app.einstellungen_sichern()
        self.assertNotIn("desktop", arbeit.gespeichert)

    def test_kaputte_datei_ergibt_leere_arbeitsflaeche(self):
        temp = tempfile.mkdtemp(prefix="dh-")
        pfad = Path(temp) / "a.json"
        pfad.write_text("{kaputt")
        app, *_ = baue(pfad)
        self.assertEqual(app.arbeit.gespeichert, {})


class KompositionImAgentenbildTests(unittest.TestCase):
    def test_komposit_nur_fuer_den_empfaenger_und_nicht_bei_nur_terminal(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        strom.ziele = {"t-1": SimpleNamespace(hwnd=None)}
        arbeit.dokument("desktop").hinzufuegen(Objekt("o", "rechteck", [(0.1, 0.1), (0.5, 0.5)], empfaenger=("t-1",)))
        gate = (0, 0, 100, 100)
        self.assertIsNotNone(app.komposit_fuer("t-1", gate, gate))
        self.assertIsNone(app.komposit_fuer("t-2", gate, gate))
        app.nur_terminal_setzen("t-1", True)
        self.assertIsNone(app.komposit_fuer("t-1", gate, gate))

    def test_erstes_bild_nach_der_bindung_enthaelt_die_objekte(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue()
        gesehen = []
        app._bild_kodieren = lambda *a, **k: gesehen.append(k.get("nachbearbeiten")) or (b"\xff\xd8", 8, 8)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=None)}
        arbeit.dokument("desktop").hinzufuegen(Objekt("o", "rechteck", [(0.1, 0.1), (0.5, 0.5)], empfaenger=("t-1",)))
        gebaut[0].kwargs["ziel_gebunden"](bindung("windows:desktop:0"))
        self.assertTrue(gesehen and gesehen[-1] is not None)


class AnzeigeTests(unittest.TestCase):
    def _anzeige(self, zustand=None):
        arbeit = Arbeitsflaechen()
        gebaut = []

        class F(FakeFenster):
            def __init__(self, rect):
                super().__init__()
                self.rgba, self.sichtbar_ = None, False

            def setze_rgba(self, bild):
                self.rgba = bild

        def bauen(rect):
            gebaut.append(F(rect))
            return gebaut[-1]

        offen = [None]
        anzeige = ArbeitsflaechenAnzeige(arbeit, bauen, zustand or (lambda k: (True, False, (100, 100, 300, 250))), lambda: (0, 0, 400, 300),
                                         editor_offen=lambda: offen[0])
        return anzeige, arbeit, gebaut, offen

    def test_nur_bildschirmobjekte_erscheinen_und_nur_wenn_es_welche_gibt(self):
        anzeige, arbeit, gebaut, offen = self._anzeige()
        dok = arbeit.dokument("windows:window:7")
        dok.hinzufuegen(Objekt("p", "rechteck", [(0.1, 0.1), (0.5, 0.5)], empfaenger=("A",)))  # nur für einen Agenten
        anzeige.tick()
        self.assertEqual(gebaut, [])  # privat: nichts auf dem Bildschirm
        dok.hinzufuegen(Objekt("s", "rechteck", [(0.1, 0.1), (0.5, 0.5)], bildschirm=True, farbe="#FF0000", staerke=6))
        anzeige.tick()
        self.assertEqual(len(gebaut), 1)
        self.assertTrue(gebaut[0].sichtbar_)
        self.assertEqual(gebaut[0].rgba.size, (200, 150))

    def test_das_privatobjekt_steht_nicht_im_bild_des_bildschirmfensters(self):
        anzeige, arbeit, gebaut, offen = self._anzeige()
        dok = arbeit.dokument("windows:window:7")
        dok.hinzufuegen(Objekt("p", "rechteck", [(0.0, 0.0), (1.0, 1.0)], empfaenger=("A",), farbe="#00FF00", staerke=10))
        dok.hinzufuegen(Objekt("s", "kreis", [(0.4, 0.4), (0.6, 0.6)], bildschirm=True, farbe="#FF0000", staerke=4))
        anzeige.tick()
        bild = gebaut[0].rgba
        self.assertEqual(bild.getpixel((3, 70))[3], 0)  # am Rand des Privatobjekts: nichts
        self.assertGreater(sum(1 for y in range(150) for x in range(200) if bild.getpixel((x, y))[3] > 0), 20)

    def test_minimiert_oder_geschlossen_verschwindet_wiederherstellen_bringt_zurueck(self):
        zustand = {"w": (True, False, (100, 100, 300, 250))}
        anzeige, arbeit, gebaut, offen = self._anzeige(lambda k: zustand["w"])
        arbeit.dokument("windows:window:7").hinzufuegen(Objekt("s", "kreis", [(0.2, 0.2), (0.8, 0.8)], bildschirm=True))
        anzeige.tick()
        self.assertTrue(gebaut[0].sichtbar_)
        zustand["w"] = (True, True, None)
        anzeige.tick()
        self.assertFalse(gebaut[0].sichtbar_)
        zustand["w"] = (True, False, (120, 110, 320, 260))
        anzeige.tick()
        self.assertTrue(gebaut[0].sichtbar_)
        self.assertEqual((gebaut[0].x, gebaut[0].y), (120, 110))  # am neuen Ort
        zustand["w"] = (False, False, None)
        anzeige.tick()
        self.assertFalse(gebaut[0].sichtbar_)

    def test_unveraendertes_dokument_wird_nicht_neu_gezeichnet(self):
        anzeige, arbeit, gebaut, offen = self._anzeige()
        dok = arbeit.dokument("windows:window:7")
        dok.hinzufuegen(Objekt("s", "kreis", [(0.2, 0.2), (0.8, 0.8)], bildschirm=True))
        anzeige.tick()
        erstes = gebaut[0].rgba
        anzeige.tick()
        self.assertIs(gebaut[0].rgba, erstes)
        dok.aendern(["s"], farbe="#00FF00")
        anzeige.tick()
        self.assertIsNot(gebaut[0].rgba, erstes)

    def test_waehrend_der_editor_offen_ist_zeigt_die_anzeige_das_gate_nicht_doppelt(self):
        anzeige, arbeit, gebaut, offen = self._anzeige()
        arbeit.dokument("windows:window:7").hinzufuegen(Objekt("s", "kreis", [(0.2, 0.2), (0.8, 0.8)], bildschirm=True))
        anzeige.tick()
        offen[0] = "windows:window:7"
        anzeige.tick()
        self.assertFalse(gebaut[0].sichtbar_)
        offen[0] = None
        anzeige.tick()
        self.assertTrue(gebaut[0].sichtbar_)

    def test_desktop_gate_steht_auf_dem_desktop_und_ausgeblendete_objekte_fehlen(self):
        anzeige, arbeit, gebaut, offen = self._anzeige()
        dok = arbeit.dokument("desktop")
        dok.hinzufuegen(Objekt("s", "kreis", [(0.2, 0.2), (0.8, 0.8)], bildschirm=True))
        anzeige.tick()
        self.assertEqual(gebaut[0].rgba.size, (400, 300))
        dok.aendern(["s"], sichtbar=False)
        anzeige.tick()
        self.assertFalse(gebaut[0].sichtbar_)


if __name__ == "__main__":
    unittest.main()
