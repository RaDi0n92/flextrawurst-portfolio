"""0.9.1: Radierer, Rechtsklick-Menü, Text-Stil, Deckkraft, Größe ändern, Ziel-Wahl und Bild-Element."""

from __future__ import annotations

import io
import tempfile
import unittest
from types import SimpleNamespace

from PIL import Image

from augen_haende_bridge.koerper import anwendung as anw
from augen_haende_bridge.koerper.objekte import Dokument, Objekt
from augen_haende_bridge.koerper.zeichnen_render import rendern, text_masse_px
from test_koerper_editor_logik import baue, ziehe
from test_koerper_zeichnen_anwendung import baue as baue_app


def rechteck(dok, l=0.1, t=0.1, r=0.4, u=0.4, **kw):
    return dok.hinzufuegen(Objekt("r" + str(len(dok.objekte)), "rechteck", [(l, t), (r, u)], **kw))


class ModellTests(unittest.TestCase):
    def test_neue_felder_ueberleben_speichern_und_laden(self):
        dok = Dokument("x")
        dok.hinzufuegen(Objekt("a", "text", [(0.1, 0.1)], text="Hi", deckkraft=40, fett=True, kursiv=True, unterstrichen=True))
        neu = Dokument.aus_dict(dok.zu_dict())
        o = neu.objekte["a"]
        self.assertEqual((o.deckkraft, o.fett, o.kursiv, o.unterstrichen), (40, True, True, True))

    def test_alte_dateien_ohne_die_felder_laden_mit_standardwerten(self):
        o = Objekt.aus_dict({"id": "z", "art": "rechteck", "punkte": [[0, 0], [1, 1]]})
        self.assertEqual((o.deckkraft, o.fett), (100, False))

    def test_deckkraft_wird_geklemmt(self):
        o = Objekt.aus_dict({"id": "z", "art": "rechteck", "punkte": [[0, 0], [1, 1]], "deckkraft": 0})
        self.assertEqual(o.deckkraft, 5)

    def test_groesser_um_die_mitte_und_ein_undo(self):
        dok = Dokument("x")
        rechteck(dok, 0.2, 0.2, 0.4, 0.4)
        dok.groesse_aendern(["r0"], 2.0)
        self.assertEqual([round(v, 3) for p in dok.objekte["r0"].punkte for v in p], [0.1, 0.1, 0.5, 0.5])
        dok.rueckgaengig()
        self.assertEqual([round(v, 3) for p in dok.objekte["r0"].punkte for v in p], [0.2, 0.2, 0.4, 0.4])

    def test_text_wird_ueber_die_schriftgroesse_groesser(self):
        dok = Dokument("x")
        dok.hinzufuegen(Objekt("t", "text", [(0.1, 0.1)], text="Hi", schriftgroesse=20))
        dok.groesse_aendern(["t"], 1.5)
        self.assertEqual(dok.objekte["t"].schriftgroesse, 30)


class RenderTests(unittest.TestCase):
    def _deckend(self, **kw):
        o = Objekt("a", "rechteck", [(0.1, 0.1), (0.9, 0.9)], farbe="#FF0000", staerke=10, **kw)
        bild = rendern([o], 100, 100)
        return bild.getpixel((10, 50))[3]

    def test_deckkraft_macht_durchsichtiger(self):
        self.assertEqual(self._deckend(), 255)
        halb = self._deckend(deckkraft=50)
        self.assertTrue(120 <= halb <= 135, halb)

    def test_unterstrichen_malt_mehr_pixel(self):
        def pixel(**kw):
            o = Objekt("t", "text", [(0.05, 0.05)], text="Hallo", schriftgroesse=24, farbe="#FFFFFF", **kw)
            return sum(1 for p in rendern([o], 200, 60).getchannel("A").tobytes() if p > 0)
        self.assertGreater(pixel(unterstrichen=True), pixel())

    def test_fett_und_kursiv_aendern_nichts_am_zeilenaufbau_abbruch(self):
        b, h = text_masse_px("Hallo\nWelt", 24, fett=True, kursiv=True)
        self.assertGreater(h, text_masse_px("Hallo", 24)[1])
        self.assertGreater(b, 0)


class EditorTests(unittest.TestCase):
    def test_radierer_loescht_alles_beruehrte_in_einem_schritt(self):
        ed, dok, _ = baue()
        rechteck(dok, 0.1, 0.1, 0.3, 0.3)
        rechteck(dok, 0.6, 0.6, 0.9, 0.9)
        v = dok.version
        ed.werkzeug_setzen("radierer")
        ziehe(ed, (20, 10), (20, 30))  # trifft nur das erste (Kante bei x=20)
        self.assertEqual(list(dok.objekte), ["r1"])
        self.assertEqual(dok.version, v + 1)
        ed.rueckgaengig()
        self.assertEqual(len(dok.objekte), 2)

    def test_radierer_zeigt_beruehrtes_vor_dem_loslassen_noch_im_dokument(self):
        ed, dok, _ = baue()
        rechteck(dok, 0.1, 0.1, 0.3, 0.3)
        ed.werkzeug_setzen("radierer")
        ed.maus_runter(20, 10)
        self.assertEqual(ed.radiert, {"r0"})
        self.assertIn("r0", dok.objekte)
        ed.maus_hoch(20, 10)
        self.assertEqual(dok.objekte, {})

    def test_rechtsklick_waehlt_das_objekt_und_meldet_das_menue(self):
        ed, dok, _ = baue()
        rechteck(dok, 0.1, 0.1, 0.5, 0.5)
        gesehen = []
        ed.kontext_menue = lambda x, y: gesehen.append((x, y))
        ed.rechtsklick(20, 10)
        self.assertEqual(ed.auswahl, {"r0"})
        self.assertEqual(gesehen, [(20, 10)])
        schluessel = [e[0] for e in ed.kontext_eintraege() if e]
        self.assertIn("loeschen", schluessel)
        self.assertIn("deck:50", schluessel)
        self.assertNotIn("fett", schluessel)  # kein Text gewählt

    def test_rechtsklick_ins_leere_zeigt_die_voreinstellungen_fuer_neue_objekte(self):
        ed, dok, _ = baue()
        ed.rechtsklick(150, 90)
        schluessel = [e[0] for e in ed.kontext_eintraege() if e]
        self.assertIn("fett", schluessel)
        self.assertNotIn("loeschen", schluessel)
        ed.kontext_ausfuehren("fett")
        ed.kontext_ausfuehren("deck:50")
        ed.werkzeug_setzen("text")
        ed.maus_runter(10, 10)
        for c in "Hi":
            ed.zeichen(ord(c))
        ed.zeichen(0x0D)
        (o,) = dok.objekte.values()
        self.assertTrue(o.fett)
        self.assertEqual(o.deckkraft, 50)

    def test_stil_aendert_schon_geschriebenen_text_und_ist_rueckgaengig(self):
        ed, dok, _ = baue()
        dok.hinzufuegen(Objekt("t", "text", [(0.1, 0.1)], text="Hallo"))
        ed.auswahl = {"t"}
        ed.stil_umschalten("kursiv")
        ed.stil_umschalten("unterstrichen")
        self.assertTrue(dok.objekte["t"].kursiv and dok.objekte["t"].unterstrichen)
        ed.stil_umschalten("kursiv")
        self.assertFalse(dok.objekte["t"].kursiv)
        ed.rueckgaengig()
        self.assertTrue(dok.objekte["t"].kursiv)

    def test_deckkraft_und_groesse_der_auswahl_ueber_das_menue(self):
        ed, dok, _ = baue()
        rechteck(dok, 0.2, 0.2, 0.4, 0.4)
        ed.auswahl = {"r0"}
        ed.kontext_ausfuehren("deck:25")
        ed.kontext_ausfuehren("gross")
        o = dok.objekte["r0"]
        self.assertEqual(o.deckkraft, 25)
        self.assertGreater(o.punkte[1][0] - o.punkte[0][0], 0.2)
        ed.kontext_ausfuehren("dick")
        self.assertEqual(o.staerke, 6)

    def test_das_menue_hakt_den_aktuellen_zustand_an(self):
        ed, dok, _ = baue()
        dok.hinzufuegen(Objekt("t", "text", [(0.1, 0.1)], text="x", fett=True, deckkraft=75))
        ed.auswahl = {"t"}
        e = {x[0]: x[2] for x in ed.kontext_eintraege() if x}
        self.assertTrue(e["fett"] and not e["kursiv"] and e["deck:75"] and not e["deck:100"])


class AnwendungTests(unittest.TestCase):
    def test_rechtsklick_menue_fuehrt_die_gewaehlte_aktion_aus(self):
        gesehen = []

        def wahl(hwnd, eintraege, x, y):
            gesehen.append(eintraege)
            ids = {e[1]: e[0] for e in eintraege if e}
            return ids.get("Löschen", 0)

        app, gebaut, strom, arbeit, fenster, leisten = baue_app(wahl=wahl)
        app.zeichnen_oeffnen("t-1")
        ed = app.editor_offen["editor"]
        rechteck(ed.dok, 0.1, 0.1, 0.5, 0.5)
        ed.rechtsklick(10, 10) if False else None
        ed.auswahl = {"r0"}
        app._zeichnen_kontext_menue(10, 10)
        self.assertEqual(ed.dok.objekte, {})
        self.assertTrue(any(e and e[1] == "Löschen" for e in gesehen[0]))

    def test_ziel_menue_wechselt_das_gate_und_holt_gespeichertes_zum_programm(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue_app(wahl=lambda h, e, x, y: anw.ZIEL_ID + 1)
        app._fenster_liste = lambda: [(55, "Notepad", "C:\\Windows\\notepad.exe")]
        from augen_haende_bridge.koerper import ziel_halter
        original = ziel_halter.fenster_zustand
        ziel_halter.fenster_zustand = lambda hwnd: (True, False, (100, 100, 700, 500))
        try:
            app.zeichnen_oeffnen("t-1")
            self.assertEqual(app.editor_offen["schluessel"], "desktop")
            app._zeichnen_ziel_menue(0, 0)
        finally:
            ziel_halter.fenster_zustand = original
        self.assertEqual(app.editor_offen["schluessel"], "windows:window:55")
        self.assertEqual(arbeit.stabil["windows:window:55"], "notepad.exe")
        self.assertTrue(fenster[0].geschlossen)  # das alte Fenster ist weg, ein neues steht auf dem Ziel
        self.assertEqual((fenster[-1].x, fenster[-1].y, fenster[-1].b, fenster[-1].h), (100, 100, 600, 400))

    def test_ziel_desktop(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue_app(wahl=lambda h, e, x, y: anw.ZIEL_ID)
        strom.ziele = {"t-1": SimpleNamespace(hwnd=77)}
        from augen_haende_bridge.koerper import ziel_halter
        original = ziel_halter.fenster_zustand
        ziel_halter.fenster_zustand = lambda hwnd: (True, False, (300, 200, 900, 600))
        try:
            app.zeichnen_oeffnen("t-1")
            app._zeichnen_ziel_menue(0, 0)
        finally:
            ziel_halter.fenster_zustand = original
        self.assertEqual(app.editor_offen["schluessel"], "desktop")

    def test_sichtbar_menue_bietet_alle_agenten_wenn_im_ziel_noch_keiner_sitzt(self):
        gesehen = []
        app, gebaut, strom, arbeit, fenster, leisten = baue_app(wahl=lambda h, e, x, y: gesehen.append(e) or 0)
        app.zeichnen_oeffnen("t-1")
        app._zeichnen_sichtbar_menue(0, 0)
        self.assertTrue(any(e and "Nur im Bild von Codex" in e[1] for e in gesehen[0]))

    def test_bild_element_legt_ein_schwebendes_bild_ins_gate_ohne_editor(self):
        png = io.BytesIO()
        Image.new("RGB", (40, 20), (200, 10, 10)).save(png, format="PNG")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png.getvalue())
        app, gebaut, strom, arbeit, fenster, leisten = baue_app()
        app._datei_waehlen = lambda hwnd: f.name
        self.assertTrue(app.bild_element_neu("t-1"))
        self.assertIsNone(app.editor_offen)
        (o,) = arbeit.dokument("desktop").objekte.values()
        self.assertEqual((o.art, o.bildschirm, o.schwebend), ("bild", True, True))
        l, t, r, u = o.grenzen()
        self.assertAlmostEqual((r - l) * 1920 / ((u - t) * 1040), 2.0, places=1)  # Seitenverhältnis des Bildes

    def test_menue_des_bild_elements_stellt_sichtbarkeit_deckkraft_und_entfernen_ein(self):
        app, gebaut, strom, arbeit, fenster, leisten = baue_app(wahl=lambda h, e, x, y: anw.SICHTBAR_AGENT_ID)
        dok = arbeit.dokument("desktop")
        dok.hinzufuegen(Objekt("b", "bild", [(0.1, 0.1), (0.3, 0.3)], bild=b"x", bildschirm=True, schwebend=True))
        app.anzeige = SimpleNamespace(_bild_elemente=SimpleNamespace(stand={}), tick=lambda: None)
        app.bild_element_menue("b", "desktop", 5, 5)
        self.assertEqual(dok.objekte["b"].empfaenger, ("t-1",))
        app._menue_anzeigen = lambda h, e, x, y: anw.KONTEXT_ID + 50
        app.bild_element_menue("b", "desktop", 5, 5)
        self.assertEqual(dok.objekte["b"].deckkraft, 50)
        app._menue_anzeigen = lambda h, e, x, y: anw.KONTEXT_ID + 2
        app.bild_element_menue("b", "desktop", 5, 5)
        self.assertEqual(dok.objekte, {})


class FakeBildFenster:
    def __init__(self, x, y, b, h, **kw):
        self.r = (x, y, x + b, y + h)
        self.kw, self.sicht, self.zu, self.prozent, self.ausnahme = kw, False, False, 100, None

    def rechteck(self): return self.r
    def verschiebe(self, x, y, b=None, h=None):
        self.r = (x, y, x + (b if b is not None else self.r[2] - self.r[0]), y + (h if h is not None else self.r[3] - self.r[1]))
    def sichtbar(self): return self.sicht
    def zeige(self, aktivieren=True): self.sicht = True
    def verberge(self): self.sicht = False
    def schliessen(self): self.zu = True
    def prozent_setzen(self, p): self.prozent = p
    def aufnahme_ausnehmen(self, an):
        self.ausnahme = an
        return self.kann
    kann = True


def png_bytes():
    puffer = io.BytesIO()
    Image.new("RGB", (40, 20), (9, 9, 9)).save(puffer, format="PNG")
    return puffer.getvalue()


class BildElementeTests(unittest.TestCase):
    def aufbau(self, **kw):
        from augen_haende_bridge.koerper.bild_elemente import BildElemente
        gebaut = []
        be = BildElemente(lambda x, y, b, h, **k: gebaut.append(FakeBildFenster(x, y, b, h, **k)) or gebaut[-1])
        dok = Dokument("g")
        dok.hinzufuegen(Objekt("b", "bild", [(0.1, 0.2), (0.3, 0.3)], bild=png_bytes(), bildschirm=True, schwebend=True, **kw))
        return be, dok, gebaut

    GATE = (100, 100, 1100, 600)

    def test_fenster_steht_genau_auf_dem_objekt_und_folgt_dem_gate(self):
        be, dok, gebaut = self.aufbau()
        be.tick("g", dok, True, self.GATE, False)
        self.assertEqual(gebaut[0].r, (200, 200, 400, 250))
        self.assertTrue(gebaut[0].sicht)
        be.tick("g", dok, True, (300, 100, 1300, 600), False)  # Gate wandert
        self.assertEqual(gebaut[0].r, (400, 200, 600, 250))

    def test_minimiertes_gate_und_offener_editor_verbergen_das_fenster(self):
        be, dok, gebaut = self.aufbau()
        be.tick("g", dok, True, self.GATE, False)
        be.tick("g", dok, False, None, False)
        self.assertFalse(gebaut[0].sicht)
        be.tick("g", dok, True, self.GATE, True)
        self.assertFalse(gebaut[0].sicht)
        be.tick("g", dok, True, self.GATE, False)
        self.assertTrue(gebaut[0].sicht)

    def test_verschieben_und_groesse_gehen_erst_nach_stillstand_als_ein_befehl_ins_dokument(self):
        be, dok, gebaut = self.aufbau()
        be.tick("g", dok, True, self.GATE, False)
        v = dok.version
        gebaut[0].verschiebe(300, 300, 300, 10)  # Daniel zieht: neues Format, Höhe passt nicht zum Bild
        be.tick("g", dok, True, self.GATE, False)
        self.assertEqual(dok.version, v)  # noch in Bewegung
        be.tick("g", dok, True, self.GATE, False)
        self.assertEqual(dok.version, v + 1)
        self.assertEqual(gebaut[0].r, (300, 300, 600, 450))  # Seitenverhältnis 2:1 wiederhergestellt
        (l, t), (r, u) = dok.objekte["b"].punkte
        self.assertAlmostEqual((l, t, r, u), (0.2, 0.4, 0.5, 0.7), places=3)
        dok.rueckgaengig()
        be.tick("g", dok, True, self.GATE, False)
        self.assertEqual(gebaut[0].r, (200, 200, 400, 250))  # Rückgängig wirkt auf das Fenster

    def test_deckkraft_geht_in_beide_richtungen(self):
        be, dok, gebaut = self.aufbau()
        be.tick("g", dok, True, self.GATE, False)
        gebaut[0].kw["bei_deckkraft"](40)
        self.assertEqual(dok.objekte["b"].deckkraft, 40)
        dok.aendern(["b"], deckkraft=70)
        be.tick("g", dok, True, self.GATE, False)
        self.assertEqual(gebaut[0].prozent, 70)

    def test_ausblenden_und_entfernen(self):
        be, dok, gebaut = self.aufbau()
        be.tick("g", dok, True, self.GATE, False)
        gebaut[0].kw["bei_ausblenden"]()
        be.tick("g", dok, True, self.GATE, False)
        self.assertFalse(gebaut[0].sicht)
        dok.entfernen(["b"])
        be.tick("g", dok, True, self.GATE, False)
        self.assertTrue(gebaut[0].zu)

    def test_nur_fuer_agenten_steht_nur_mit_aufnahme_ausnahme(self):
        be, dok, gebaut = self.aufbau()
        dok.aendern(["b"], bildschirm=False, empfaenger=("t-1",))
        FakeBildFenster.kann = False
        try:
            be.tick("g", dok, True, self.GATE, False)
            self.assertFalse(gebaut[0].sicht)  # Windows nimmt es nicht aus: bleibt unsichtbar
        finally:
            FakeBildFenster.kann = True
        gebaut[0].kann = True
        be2, dok2, gebaut2 = self.aufbau()
        dok2.aendern(["b"], bildschirm=False, empfaenger=("t-1",))
        be2.tick("g", dok2, True, self.GATE, False)
        self.assertTrue(gebaut2[0].sicht and gebaut2[0].ausnahme)

    def test_schwebende_stehen_nicht_in_der_durchklickbaren_anzeige_aber_im_agentenbild(self):
        be, dok, gebaut = self.aufbau()
        self.assertEqual(dok.auf_dem_bildschirm(), [])
        dok.aendern(["b"], empfaenger=("t-1",))
        self.assertEqual([o.id for o in dok.fuer_empfaenger("t-1")], ["b"])


if __name__ == "__main__":
    unittest.main()
