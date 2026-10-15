"""G11: der WorldDOM — Knotenmodell mit Herkunft, Konfidenz und Aktualität; echte Strukturquellen (Browser, Bedienungshilfen) und aus dem Bild erschlossene Knoten."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.koerper import uia
from augen_haende_bridge.koerper import weltdom as wd
from augen_haende_bridge.koerper import weltdom_quellen as wq

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
ZIEL = "kde1:window:42"


def knoten(**kw):
    werte = dict(id="rea-x-1", ziel=ZIEL, herkunft="real", quelle="atspi", rolle="button", name="OK", rect=(10, 10, 60, 30), gemessen_ms=1000)
    werte.update(kw)
    return wd.Knoten(**werte)


class ModellTests(unittest.TestCase):
    def test_aktualitaet_alter_und_veraltet(self):
        k = knoten(ttl_ms=5000)
        self.assertEqual((k.alter_ms(3000), k.veraltet(3000), k.veraltet(6000), k.veraltet(6001)), (2000, False, False, True))
        d = k.zu_dict(7000)
        self.assertEqual((d["alter_ms"], d["veraltet"], d["herkunft"], d["confidence"]), (6000, True, "real", 1.0))

    def test_aus_dict_ist_streng(self):
        k = knoten()
        self.assertEqual(wd.Knoten.aus_dict(k.zu_dict()), k)
        for kaputt in (None, 5, {}, {**k.zu_dict(), "herkunft": "gefaelscht"}, {**k.zu_dict(), "aufloesung": "magie"}, {**k.zu_dict(), "confidence": 1.5}, {**k.zu_dict(), "rect": [1, 2]},
                       {**k.zu_dict(), "rect": "x"}, {key: v for key, v in k.zu_dict().items() if key != "ziel"}):
            self.assertIsNone(wd.Knoten.aus_dict(kaputt), kaputt)

    def test_kennung_ist_stabil_und_unterscheidet(self):
        a = wd.knoten_id(ZIEL, "real", "atspi", 1, (0, 1), "button", "OK")
        self.assertEqual(a, wd.knoten_id(ZIEL, "real", "atspi", 1, (0, 1), "button", "OK"))
        self.assertNotEqual(a, wd.knoten_id(ZIEL, "real", "atspi", 1, (0, 2), "button", "OK"))
        self.assertTrue(a.startswith("rea-atspi-"))


class StoreTests(unittest.TestCase):
    def test_eine_messung_ersetzt_den_stand_der_quelle_und_meldet_verschwundene(self):
        w = wd.WeltDom()
        a, b = knoten(id="a"), knoten(id="b")
        self.assertEqual(w.ersetze(ZIEL, "real", "atspi", [a, b]), (2, 0))
        self.assertEqual(w.ersetze(ZIEL, "real", "atspi", [a]), (1, 1))
        self.assertIsNone(w.knoten(ZIEL, "b"), "verschwundene Knoten werden nicht als noch da behauptet")
        with self.assertRaises(ValueError):
            w.ersetze(ZIEL, "real", "atspi", [knoten(id="c", quelle="cdp")])

    def test_quellen_ueberschreiben_sich_nicht(self):
        w = wd.WeltDom()
        w.ersetze(ZIEL, "real", "atspi", [knoten(id="a")])
        w.ersetze(ZIEL, "inferred", "ocr", [knoten(id="o", herkunft="inferred", quelle="ocr", confidence=0.7)])
        w.ersetze(ZIEL, "real", "atspi", [])
        self.assertEqual([k.id for k in w.liste(ZIEL)], ["o"])
        self.assertEqual(w.zaehlung(ZIEL), {"real": 0, "inferred": 1, "authored": 0, "projected": 0})

    def test_filter_und_aktualitaet(self):
        w = wd.WeltDom()
        w.ersetze(ZIEL, "real", "atspi", [knoten(id="a", rolle="button", name="Speichern", gemessen_ms=1000), knoten(id="b", rolle="text", name="Name", gemessen_ms=9000, rect=(10, 40, 60, 60))])
        self.assertEqual([k.id for k in w.liste(ZIEL, rolle="button")], ["a"])
        self.assertEqual([k.id for k in w.liste(ZIEL, text="speich")], ["a"])
        self.assertEqual([k.id for k in w.liste(ZIEL, nur_aktuell=True, jetzt_ms=7000)], ["b"], "ein veralteter Knoten fällt aus der aktuellen Liste")
        self.assertEqual([k.id for k in w.liste(ZIEL)], ["a", "b"], "sortiert nach Lage von oben nach unten")

    def test_authored_anker_traegt_urheber_und_ort_und_ueberlebt_den_neustart(self):
        pfad = Path(tempfile.mkdtemp()) / "weltdom.json"
        w = wd.WeltDom(pfad)
        k = w.anker_anlegen(ZIEL, "Ziel-Slot", (100, 100, 140, 140), urheber="daniel", jetzt_ms=5000, beschreibung="hierhin")
        w.ersetze(ZIEL, "real", "atspi", [knoten(id="r")])
        self.assertEqual((k.herkunft, k.urheber, k.aufloesung, k.confidence), ("authored", "daniel", "koordinate", 1.0))
        self.assertIn("klick_koordinate", k.faehigkeiten)
        self.assertIn("nicht Teil der Anwendung", k.grenzen)
        neu = wd.WeltDom(pfad)
        self.assertEqual(neu.laden(), 1, "nur das Bewusste wird gespeichert")
        self.assertEqual(neu.knoten(ZIEL, k.id).zu_dict(), k.zu_dict())
        self.assertIsNone(neu.knoten(ZIEL, "r"))

    def test_projected_ist_nie_ausfuehrbar_und_authored_braucht_einen_ort(self):
        w = wd.WeltDom()
        p = w.anker_anlegen(ZIEL, "Schattenpfad", None, urheber="codex", jetzt_ms=1, herkunft="projected")
        self.assertEqual((p.herkunft, p.aufloesung, p.faehigkeiten, p.confidence), ("projected", "virtuell", ("zeigen",), 0.5))
        for kw in (dict(name="", rect=(1, 1, 2, 2), urheber="x"), dict(name="x", rect=(1, 1, 2, 2), urheber=""), dict(name="x", rect=None, urheber="x"), dict(name="x", rect=(1, 1, 2, 2), urheber="x", herkunft="real")):
            with self.assertRaises(ValueError, msg=str(kw)):
                w.anker_anlegen(ZIEL, kw.pop("name"), kw.pop("rect"), jetzt_ms=1, **kw)

    def test_kaputte_datei_und_ziel_vergessen(self):
        pfad = Path(tempfile.mkdtemp()) / "w.json"
        pfad.write_text("{kaputt")
        w = wd.WeltDom(pfad)
        self.assertEqual(w.laden(), 0)
        self.assertIn("unlesbar", w.fehler)
        pfad.write_text(json.dumps({"anker": {ZIEL: [{"nope": 1}, 5, knoten(herkunft="authored", id="gut", quelle="hand", aufloesung="koordinate").zu_dict(), knoten(herkunft="real", id="fremd").zu_dict()]}}))
        self.assertEqual(wd.WeltDom(pfad).laden(), 1, "kaputte Einträge und Nicht-Bewusstes werden übersprungen")
        w2 = wd.WeltDom()
        w2.anker_anlegen(ZIEL, "bleibt", (1, 1, 5, 5), urheber="d", jetzt_ms=1)
        w2.ersetze(ZIEL, "real", "atspi", [knoten(id="a")])
        w2.ziel_vergessen(ZIEL)
        self.assertEqual([k.herkunft for k in w2.liste(ZIEL)], ["authored"], "das Fenster ist weg: Gemessenes gilt nicht mehr, Bewusstes bleibt")

    def test_grenze_je_ziel(self):
        w = wd.WeltDom()
        w.ersetze(ZIEL, "real", "atspi", [knoten(id=f"k{i}") for i in range(wd.MAX_KNOTEN_JE_ZIEL + 50)])
        self.assertEqual(len(w.liste(ZIEL, limit=10_000)), wd.MAX_KNOTEN_JE_ZIEL)
        with self.assertRaises(ValueError):
            w.anker_anlegen(ZIEL, "zu viel", (1, 1, 2, 2), urheber="d", jetzt_ms=1)


class UiBaumTests(unittest.TestCase):
    def test_ui_baum_wird_zu_realen_knoten_mit_den_echten_faehigkeiten(self):
        blatt = uia.UiKnoten("atspi", "button", "OK", "", (1, 2, 30, 40), (), ("klick",), (0, 0))
        feld = uia.UiKnoten("atspi", "text", "Name", "Anna", (1, 50, 30, 70), (), ("text_setzen",), (0, 1))
        kachel = uia.UiKnoten("atspi", "filler", "", "", None, (), (), (0,), [blatt, feld])
        wurzel = uia.UiKnoten("atspi", "frame", "Fenster", "", None, (), (), (), [kachel])
        ks = wd.aus_ui_baum(ZIEL, wurzel, "atspi", 77, 5000)
        self.assertEqual([(k.rolle, k.name, k.faehigkeiten, k.geometrie) for k in ks], [("button", "OK", ("klick", "lesen"), "gemessen"), ("text", "Name", ("lesen", "text_setzen"), "gemessen")])
        self.assertEqual(ks[0].anker, {"pid": 77, "pfad": [0, 0], "rolle": "button", "name": "OK"})
        self.assertTrue(all(k.herkunft == "real" and k.confidence == 1.0 and k.gemessen_ms == 5000 for k in ks))


def bild_mit_flaechen():
    from PIL import Image, ImageDraw, ImageFont

    b = Image.new("RGB", (480, 300), (235, 235, 235))
    d = ImageDraw.Draw(b)
    d.rectangle((40, 40, 200, 90), fill=(40, 110, 220), outline=(10, 40, 120), width=2)
    d.rectangle((40, 140, 440, 190), fill=(255, 255, 255), outline=(60, 60, 60), width=2)
    schrift = ImageFont.load_default(size=26)
    d.text((70, 52), "Speichern", fill=(255, 255, 255), font=schrift)
    d.text((60, 250), "Fertig machen", fill=(0, 0, 0), font=schrift)
    return b


def als_bgra(b):
    r, g, bl = b.split()
    from PIL import Image

    return Image.merge("RGBA", (bl, g, r, Image.new("L", b.size, 255))).tobytes()


class ErschlossenTests(unittest.TestCase):
    def test_flaechen_werden_als_vermutung_erschlossen_mit_grenzen_und_konfidenz_unter_eins(self):
        bgra = als_bgra(bild_mit_flaechen())
        ks, hinweis = wq.flaechen_erschliessen(ZIEL, bgra, 480, 300, (100, 100, 580, 400), 7, 5000)
        self.assertEqual(hinweis, "")
        rects = [k.rect for k in ks]
        self.assertTrue(any(abs(r[0] - 140) <= 6 and abs(r[1] - 140) <= 6 and abs(r[2] - 300) <= 8 for r in rects), f"die blaue Fläche liegt bei Bildschirmpunkt 140,140: {rects}")
        self.assertTrue(any(k.rolle == "feld_aehnlich" for k in ks), [k.rolle for k in ks])
        for k in ks:
            self.assertEqual((k.herkunft, k.quelle, k.bild_seq, k.aufloesung), ("inferred", "flaeche", 7, "koordinate"))
            self.assertLess(k.confidence, 1.0)
            self.assertIn("vermutet", k.grenzen)
            self.assertEqual(set(k.faehigkeiten), {"zeigen", "klick_koordinate"}, "kein Knoten behauptet native Fähigkeiten")

    @unittest.skipUnless(shutil.which("tesseract"), "tesseract fehlt")
    def test_beschriftungen_per_ocr_und_benennung_der_flaechen(self):
        bgra = als_bgra(bild_mit_flaechen())
        texte, hinweis = wq.beschriftungen_erschliessen(ZIEL, bgra, 480, 300, (100, 100, 580, 400), 7, 5000)
        self.assertEqual(hinweis, "")
        self.assertIn("Fertig", " | ".join(t.name for t in texte))
        for t in texte:
            self.assertEqual((t.herkunft, t.quelle, t.rolle), ("inferred", "ocr", "text_ocr"))
            self.assertTrue(0.4 <= t.confidence <= 0.9)
            self.assertIn("Lesefehler", t.grenzen)
        f = next(t for t in texte if "Fertig" in t.name)
        self.assertTrue(abs(f.rect[0] - 160) < 20 and abs(f.rect[1] - 350) < 30, f.rect)
        fl, _ = wq.flaechen_erschliessen(ZIEL, bgra, 480, 300, (100, 100, 580, 400), 7, 5000)
        self.assertEqual(wq.flaechen_benennen(fl, bgra, 480, 300), "")
        s = next((k for k in fl if "Speichern" in k.name), None)
        self.assertIsNotNone(s, [(k.name, k.rect) for k in fl])
        self.assertEqual(s.rolle, "schaltflaeche_aehnlich")
        self.assertLessEqual(s.confidence, 0.9)
        self.assertTrue(abs(s.rect[0] - 140) <= 6 and abs(s.rect[1] - 140) <= 6)

    def test_fehlende_werkzeuge_und_kaputte_bilder_ergeben_einen_grund_keine_erfundenen_treffer(self):
        bgra = als_bgra(bild_mit_flaechen())
        ks, hinweis = wq.beschriftungen_erschliessen(ZIEL, bgra, 480, 300, (0, 0, 480, 300), None, 1, tesseract="/gibt/es/nicht")
        self.assertEqual(ks, [])
        self.assertTrue(hinweis)
        for aufruf in (lambda: wq.flaechen_erschliessen(ZIEL, b"", 480, 300, (0, 0, 480, 300), None, 1), lambda: wq.flaechen_erschliessen(ZIEL, b"x" * 10, 10, 10, (0, 0, 10, 10), None, 1),
                       lambda: wq.beschriftungen_erschliessen(ZIEL, b"", 480, 300, (0, 0, 480, 300), None, 1)):
            self.assertEqual(aufruf()[0], [])
            self.assertTrue(aufruf()[1])

    def test_ein_leeres_einfarbiges_bild_hat_keine_flaechen(self):
        from PIL import Image

        ks, hinweis = wq.flaechen_erschliessen(ZIEL, als_bgra(Image.new("RGB", (300, 200), (200, 200, 200))), 300, 200, (0, 0, 300, 200), None, 1)
        self.assertEqual((ks, hinweis), ([], ""))


@unittest.skipUnless(DISPLAY and shutil.which("dbus-run-session") and Path("/usr/libexec/at-spi-bus-launcher").exists(), "kein privater Xvfb, dbus-run-session oder AT-SPI fehlt")
class RealAtspiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lauf = subprocess.run(["dbus-run-session", "--", sys.executable, str(WURZEL / "tests" / "helfer_weltdom_lauf.py"), "aktion"], capture_output=True, text=True, timeout=180)
        zeilen = [z for z in lauf.stdout.splitlines() if z.startswith("{")]
        if not zeilen:
            raise AssertionError(lauf.stdout[-600:] + lauf.stderr[-600:])
        cls.r = json.loads(zeilen[-1])

    def test_echte_knoten_aus_einem_echten_programm_mit_herkunft_lage_und_aktualitaet(self):
        k = {x["rolle"]: x for x in self.r["knoten"]}
        self.assertTrue({"button", "text", "label"} <= set(k))
        for x in k.values():
            self.assertEqual((x["herkunft"], x["quelle"], x["confidence"], x["aufloesung"], x["veraltet"], x["alter_ms"]), ("real", "atspi", 1.0, "atspi", False, 0))
            self.assertIsNotNone(x["rect"])
        self.assertEqual(k["button"]["name"], "Zählen")
        self.assertIn("klick", k["button"]["faehigkeiten"])
        self.assertNotIn("klick", k["label"]["faehigkeiten"], "ein Etikett kann nur gelesen werden")


from tests.test_koerper_cdp import CHROMIUM, BrowserFall  # noqa: E402


@unittest.skipUnless(DISPLAY and CHROMIUM, "kein privater Xvfb oder kein Chromium")
class BrowserWeltdomTests(BrowserFall):
    def test_echte_knoten_aus_einer_echten_seite_mit_lage_und_herkunft(self):
        with self.seite() as s:
            ursprung = wq.seiten_ursprung(s)
            self.assertIsNotNone(ursprung)
            ks = wq.aus_cdp(ZIEL, s, 5000, inhalt_ursprung=ursprung)
        nach = {(k.rolle, k.name): k for k in ks}
        for schluessel in (("button", "Zaehlen"), ("textbox", "Eingabe"), ("heading", "Hallo Bridge")):
            self.assertIn(schluessel, nach, sorted(nach))
        knopf = nach[("button", "Zaehlen")]
        self.assertEqual((knopf.herkunft, knopf.quelle, knopf.confidence, knopf.aufloesung, knopf.geometrie), ("real", "cdp", 1.0, "cdp", "gemessen"))
        self.assertIn("klick", knopf.faehigkeiten)
        self.assertIn("text_setzen", nach[("textbox", "Eingabe")].faehigkeiten)
        self.assertNotIn("klick", nach[("heading", "Hallo Bridge")].faehigkeiten)
        self.assertIsNotNone(knopf.rect)
        self.assertTrue(knopf.rect[2] > knopf.rect[0] and knopf.rect[3] > knopf.rect[1])
        self.assertIsNotNone(knopf.anker["backend_id"])

    def test_ohne_ursprung_ist_die_geometrie_als_abgeleitet_gekennzeichnet(self):
        with self.seite() as s:
            ks = wq.aus_cdp(ZIEL, s, 5000)
        self.assertTrue(ks and all(k.geometrie == "abgeleitet" for k in ks))


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class ErschlossenRealTests(unittest.TestCase):
    def test_aus_dem_bild_eines_echten_fensters_entstehen_flaechen_und_beschriftungen(self):
        from tests.test_koerper_eingabe_adapter import GtkProgramm

        from augen_haende_bridge.koerper import linux_adapter as la

        app = GtkProgramm("WD")
        self.addCleanup(app.beenden)
        bgra, b, h = la.LinuxCaptureApi(ausnahmen=lambda: set()).capture_window(app.xid)
        flaechen, hinweis = wq.flaechen_erschliessen(ZIEL, bgra, b, h, app.rect(), 1, 5000)
        self.assertEqual(hinweis, "")
        self.assertTrue(any(k.rolle == "feld_aehnlich" for k in flaechen), [(k.rolle, k.rect) for k in flaechen])
        if shutil.which("tesseract"):
            texte, _ = wq.beschriftungen_erschliessen(ZIEL, bgra, b, h, app.rect(), 1, 5000)
            z = next((t for t in texte if "Zaehlen" in t.name), None)
            self.assertIsNotNone(z, [t.name for t in texte])
            knopf = app.stand()["rects"]["knopf"]
            self.assertTrue(knopf[0] <= (z.rect[0] + z.rect[2]) // 2 <= knopf[2] and knopf[1] <= (z.rect[1] + z.rect[3]) // 2 <= knopf[3], "der erkannte Text liegt auf dem echten Knopf")


if __name__ == "__main__":
    unittest.main()
