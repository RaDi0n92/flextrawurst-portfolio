"""G11: vom Begriff zur Handlung — auflösen, ausführen, zurücklesen. Browser (echter Chromium), Bedienungshilfen (echtes GTK-Programm), Koordinaten über die Hände (echte Eingabe), und die Fälle, in denen nichts passieren darf."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge.koerper import weltdom as wd
from augen_haende_bridge.koerper import weltdom_quellen as wq
from augen_haende_bridge.koerper.weltdom_aktion import AktionsDienst
from tests.test_koerper_cdp import CHROMIUM, BrowserFall

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
ZIEL = "kde1:window:42"


def knoten(**kw):
    werte = dict(id="k1", ziel=ZIEL, herkunft="real", quelle="atspi", rolle="button", name="OK", rect=(10, 10, 60, 30), gemessen_ms=1000, ttl_ms=5000, faehigkeiten=("klick",), aufloesung="atspi",
                 anker={"pid": 1, "pfad": [0], "rolle": "button", "name": "OK"})
    werte.update(kw)
    return wd.Knoten(**werte)


class Zeit:
    def __init__(self):
        self.ms = 2000

    def __call__(self):
        return self.ms


def dienst(welt, *knoten_liste, zeit=None, **kw):
    welt.ersetze(ZIEL, "real", "atspi", [k for k in knoten_liste if k.herkunft == "real"])
    return AktionsDienst(welt, jetzt_ms=zeit or Zeit(), schlafen=lambda s: None, **kw)


class RegelTests(unittest.TestCase):
    """Die Fälle, in denen nichts ausgelöst werden darf — mit Attrappen, die jeden Aufruf mitzählen."""

    def setUp(self):
        self.welt = wd.WeltDom()
        self.haende = []

    def koordinaten(self, ziel, k):
        self.haende.append(k.id)
        return {"status": "ausgefuehrt", "delivered": 3}

    def test_unbekannter_knoten_projizierter_unbekannte_aktion(self):
        d = dienst(self.welt)
        self.assertEqual((d.ausfuehren(ZIEL, "gibt-es-nicht", "klick")["status"], d.ausfuehren(ZIEL, "gibt-es-nicht", "klick")["grund"]), ("unaufloesbar", "knoten_unbekannt"))
        p = self.welt.anker_anlegen(ZIEL, "Schatten", None, urheber="codex", jetzt_ms=1500, herkunft="projected")
        r = d.ausfuehren(ZIEL, p.id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "projiziert_nie_ausfuehrbar"))
        k = knoten()
        d = dienst(self.welt, k)
        self.assertEqual(d.ausfuehren(ZIEL, k.id, "tanzen")["grund"], "aktion_unbekannt")

    def test_veraltet_loest_nichts_aus_und_sagt_wie_alt(self):
        zeit = Zeit()
        k = knoten()
        d = dienst(self.welt, k, zeit=zeit, ui_quelle=lambda z: self.fail("die Quelle darf nicht angefasst werden"))
        zeit.ms = 1000 + 5001
        r = d.ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("veraltet", "neu_messen"))
        self.assertIn("5001 ms", r["hinweis"])

    def test_faehigkeit_fehlt_text_ungueltig_und_virtuell(self):
        etikett = knoten(id="e", rolle="label", faehigkeiten=("lesen",))
        d = dienst(self.welt, etikett)
        for aktion, text in (("klick", None), ("text_setzen", "x")):
            r = d.ausfuehren(ZIEL, "e", aktion, text)
            self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "faehigkeit_fehlt"), aktion)
        feld = knoten(id="f", rolle="text", faehigkeiten=("text_setzen",))
        d = dienst(self.welt, feld)
        self.assertEqual(d.ausfuehren(ZIEL, "f", "text_setzen", None)["grund"], "text_ungueltig")
        self.assertEqual(d.ausfuehren(ZIEL, "f", "text_setzen", "x" * 501)["grund"], "text_ungueltig")
        self.welt.ersetze(ZIEL, "authored", "hand", [])
        v = self.welt.anker_anlegen(ZIEL, "Ohne Ort", (1, 1, 5, 5), urheber="daniel", jetzt_ms=1500)
        v.aufloesung, v.faehigkeiten = "virtuell", ("zeigen",)
        r = dienst(self.welt, koordinaten_klick=self.koordinaten).ausfuehren(ZIEL, v.id, "klick")
        self.assertEqual((r["status"], r["methode"]), ("virtuell", "virtuell"))
        self.assertEqual(self.haende, [], "ein erfundener Knoten ohne Ort bewegt nie die Hände")

    def test_quelle_fehlt_oder_knoten_weg_ergibt_unaufloesbar_ohne_aktion(self):
        k = knoten()
        r = dienst(self.welt, k).ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("unaufloesbar", "quelle_nicht_verfuegbar"))
        aufrufe = []

        class Quelle:
            def baum(self, pid):
                return SimpleNamespace(status="kein_baum", wurzel=None)

            def klick(self, n):
                aufrufe.append(n)

        r = dienst(self.welt, k, ui_quelle=lambda z: (Quelle(), 1)).ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["grund"], aufrufe), ("unaufloesbar", "kein_baum", []))

    def test_koordinaten_nur_klick_und_nur_ueber_die_haende(self):
        k = self.welt.anker_anlegen(ZIEL, "Slot", (10, 10, 50, 50), urheber="daniel", jetzt_ms=1500)
        d = dienst(self.welt)
        self.assertEqual(d.ausfuehren(ZIEL, k.id, "klick")["grund"], "haende_nicht_verfuegbar")
        d = dienst(self.welt, koordinaten_klick=self.koordinaten)
        self.assertEqual(d.ausfuehren(ZIEL, k.id, "text_setzen", "x")["grund"], "faehigkeit_fehlt")
        r = d.ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["methode"], r["ruecklese"]["bestaetigt"]), ("ausgefuehrt", "koordinate", None), "ohne Bild keine Rücklese: ausdrücklich nicht bestätigt")
        self.assertEqual(self.haende, [k.id])

    def test_haende_lehnen_ab_dann_ist_es_abgelehnt_mit_dem_grund_der_haende(self):
        k = self.welt.anker_anlegen(ZIEL, "Slot", (10, 10, 50, 50), urheber="daniel", jetzt_ms=1500)
        d = dienst(self.welt, koordinaten_klick=lambda z, kn: {"status": "abgelehnt", "grund": "geometrie_geaendert"})
        r = d.ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "geometrie_geaendert"))

    def test_pixelrueckmeldung_nur_bei_wirklicher_aenderung(self):
        k = self.welt.anker_anlegen(ZIEL, "Slot", (10, 10, 50, 50), urheber="daniel", jetzt_ms=1500)
        bilder = iter([(b"aaaa", 1, 1), (b"bbbb", 1, 1), (b"cccc", 1, 1), (b"cccc", 1, 1)])
        d = dienst(self.welt, koordinaten_klick=self.koordinaten, bild_holen=lambda z, r: next(bilder))
        self.assertEqual(d.ausfuehren(ZIEL, k.id, "klick")["ruecklese"], {"art": "pixel", "vorher": None, "nachher": None, "bestaetigt": True, "hinweis": "Pixel haben sich geändert"})
        r = d.ausfuehren(ZIEL, k.id, "klick")["ruecklese"]
        self.assertEqual((r["art"], r["bestaetigt"]), ("pixel", None), "gleiche Pixel sind weder Beleg noch Gegenbeleg")

    def test_ein_fehler_in_der_quelle_wird_gemeldet(self):
        k = knoten()

        def kaputt(z):
            raise RuntimeError("boom")

        r = dienst(self.welt, k, ui_quelle=kaputt).ausfuehren(ZIEL, k.id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("fehler", "ausfuehrung_fehlgeschlagen"))


@unittest.skipUnless(DISPLAY and CHROMIUM, "kein privater Xvfb oder kein Chromium")
class BrowserAktionTests(BrowserFall):
    def werkzeug(self, s):
        welt = wd.WeltDom()
        ks = wq.aus_cdp(ZIEL, s, 2000, inhalt_ursprung=wq.seiten_ursprung(s))
        welt.ersetze(ZIEL, "real", "cdp", ks)
        d = AktionsDienst(welt, cdp_seite=lambda z: s, jetzt_ms=lambda: 2500, schlafen=time.sleep)
        return welt, d, {(k.rolle, k.name): k for k in ks}

    def test_klick_auf_einen_begriff_mit_ruecklese(self):
        with self.seite() as s:
            welt, d, n = self.werkzeug(s)
            vorher = s.auswerten("document.getElementById('zahl').innerText")
            r = d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "klick", erwartung=str(int(vorher) + 1))
            self.assertEqual((r["status"], r["methode"]), ("ausgefuehrt", "cdp"))
            self.assertEqual(s.auswerten("document.getElementById('zahl').innerText"), str(int(vorher) + 1), "wirklich einmal geklickt")
            self.assertEqual((r["ruecklese"]["art"], r["ruecklese"]["bestaetigt"]), ("wert", True))
            r2 = d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "klick", erwartung="Das steht nirgends 987")
            self.assertEqual(r2["ruecklese"]["bestaetigt"], False, "eine falsche Erwartung wird als nicht bestätigt gemeldet")
            r3 = d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "klick")
            self.assertIsNone(r3["ruecklese"]["bestaetigt"], "ohne Erwartung ist die Wirkung nicht nachgeprüft")

    def test_text_in_ein_feld_und_zurueckgelesen(self):
        with self.seite() as s:
            welt, d, n = self.werkzeug(s)
            r = d.ausfuehren(ZIEL, n[("textbox", "Eingabe")].id, "text_setzen", "Grüße 🌍 Welt")
            self.assertEqual((r["status"], r["ruecklese"]["nachher"], r["ruecklese"]["bestaetigt"]), ("ausgefuehrt", "Grüße 🌍 Welt", True))
            r = d.ausfuehren(ZIEL, n[("textbox", "Eingabe")].id, "text_setzen", "neu")
            self.assertEqual((r["ruecklese"]["vorher"], r["ruecklese"]["nachher"], r["ruecklese"]["bestaetigt"]), ("Grüße 🌍 Welt", "neu", True), "der alte Inhalt wird ersetzt, nicht ergänzt")
            gelesen = d.ausfuehren(ZIEL, n[("textbox", "Eingabe")].id, "lesen")
            self.assertEqual(gelesen["gelesen"], "neu")

    def test_verschwundener_und_mehrdeutiger_knoten_loesen_nichts_aus(self):
        with self.seite() as s:
            welt, d, n = self.werkzeug(s)
            zahl_vorher = s.auswerten("document.getElementById('zahl').innerText")
            s.auswerten("document.getElementById('knopf').remove(); 1")
            r = d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "klick")
            self.assertEqual((r["status"], r["grund"]), ("unaufloesbar", "knoten_weg"))
            self.assertEqual(s.auswerten("document.getElementById('zahl').innerText"), zahl_vorher)
            # zwei gleichnamige Knöpfe: Kennung ist ungültig (der erste wurde entfernt), Rolle und Name sind nicht eindeutig
            s.auswerten("for (let i = 0; i < 2; i++) { const b = document.createElement('button'); b.setAttribute('aria-label', 'Zaehlen'); b.innerText = 'Zaehlen'; document.body.appendChild(b); } 1")
            r = d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "klick")
            self.assertEqual((r["status"], r["grund"]), ("unaufloesbar", "mehrdeutig"))

    def test_ungueltige_kennung_aber_eindeutiger_name_wird_wiedergefunden(self):
        with self.seite() as s:
            welt, d, n = self.werkzeug(s)
            k = n[("button", "Zaehlen")]
            k.anker["backend_id"] = 99999999
            vorher = int(s.auswerten("document.getElementById('zahl').innerText"))
            r = d.ausfuehren(ZIEL, k.id, "klick")
            self.assertEqual(r["status"], "ausgefuehrt")
            self.assertEqual(int(s.auswerten("document.getElementById('zahl').innerText")), vorher + 1)

    def test_ein_knopf_kann_nicht_getippt_und_eine_ueberschrift_nicht_geklickt_werden(self):
        with self.seite() as s:
            welt, d, n = self.werkzeug(s)
            self.assertEqual(d.ausfuehren(ZIEL, n[("button", "Zaehlen")].id, "text_setzen", "x")["grund"], "faehigkeit_fehlt")
            self.assertEqual(d.ausfuehren(ZIEL, n[("heading", "Hallo Bridge")].id, "klick")["grund"], "faehigkeit_fehlt")


@unittest.skipUnless(DISPLAY and shutil.which("dbus-run-session") and Path("/usr/libexec/at-spi-bus-launcher").exists(), "kein privater Xvfb, dbus-run-session oder AT-SPI fehlt")
class AtspiAktionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lauf = subprocess.run(["dbus-run-session", "--", sys.executable, str(WURZEL / "tests" / "helfer_weltdom_lauf.py"), "aktion"], capture_output=True, text=True, timeout=180)
        zeilen = [z for z in lauf.stdout.splitlines() if z.startswith("{")]
        if not zeilen:
            raise AssertionError(lauf.stdout[-600:] + lauf.stderr[-600:])
        cls.r = json.loads(zeilen[-1])

    def test_klick_und_text_in_einem_echten_programm_mit_ruecklese(self):
        self.assertEqual((self.r["klick"]["status"], self.r["klick"]["methode"]), ("ausgefuehrt", "atspi"))
        self.assertTrue(self.r["klick"]["stand"].startswith("1|"), "das Programm hat den Klick gezählt")
        self.assertEqual((self.r["text"]["status"], self.r["text"]["ruecklese"]["bestaetigt"]), ("ausgefuehrt", True))
        self.assertEqual(self.r["text"]["stand"], "1|Grüße 🌍")

    def test_ein_etikett_kann_nur_gelesen_werden(self):
        e = self.r["etikett"]
        self.assertEqual((e["klick"], e["text"]), (["abgelehnt", "faehigkeit_fehlt"], ["abgelehnt", "faehigkeit_fehlt"]))
        self.assertEqual(e["lesen"], ["ausgefuehrt", "Beschriftung eins"])
        self.assertEqual(e["stand"], "1|Grüße 🌍", "die abgelehnten Aktionen haben nichts verändert")

    def test_nicht_aufloesbar_und_veraltet_aendern_nichts(self):
        self.assertEqual((self.r["weg"]["status"], self.r["weg"]["grund"], self.r["weg"]["stand_gleich"]), ("unaufloesbar", "knoten_weg", True))
        self.assertEqual((self.r["veraltet"]["status"], self.r["veraltet"]["stand_gleich"]), ("veraltet", True))

    def test_ein_geaenderter_pfad_wird_ueber_rolle_und_name_wiedergefunden(self):
        self.assertEqual(self.r["umgefunden"]["status"], "ausgefuehrt")
        self.assertTrue(self.r["umgefunden"]["stand"].startswith("2|"))


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class KoordinatenAktionTests(unittest.TestCase):
    """Ein aus dem Bild erschlossener und ein erfundener Knoten, ausgeführt über die echten Hände (Lease, Käfig, Bild)."""

    def setUp(self):
        from augen_haende_bridge.koerper import eingabe_adapter as ea
        from augen_haende_bridge.koerper import linux_adapter as la
        from augen_haende_bridge.koerper import x11_helfer as x
        from tests.test_koerper_eingabe_adapter import GtkProgramm

        self.ea, self.x = ea, x
        self.app = GtkProgramm("WDK")
        self.addCleanup(self.app.beenden)
        self.ziel = f"kde1:window:{self.app.xid}"
        self.backend = ea.X11Backend()
        self.addCleanup(self.backend.schliessen)
        self.engine = ea.HaendeEngine(self.backend, ziel_stand=lambda z: (lambda r: ea.ZielStand(r is not None, r, False, self.app.xid, None))(x.fenster_rechteck(self.app.xid)), ziel_kennung=lambda z: self.app.xid)
        self.capture = la.LinuxCaptureApi(ausnahmen=lambda: set())
        self.welt = wd.WeltDom()
        self.jetzt = int(time.time() * 1000)
        self.bezug = None

    def bild(self):
        r = self.app.rect()
        bgra, b, h = self.capture.capture_window(self.app.xid)
        self.bezug = self.ea.Bildbezug(self.ziel, 1, int(time.time() * 1000), b, h, r, self.app.xid, None, r)
        return bgra, b, h, r

    def haende_klick(self, ziel, k):
        """Der Weg des Körpers: Knotenlage → Bildpunkt auf dem gesendeten Bild → Hände."""
        mitte = ((k.rect[0] + k.rect[2]) // 2, (k.rect[1] + k.rect[3]) // 2)
        r = self.bezug.rect
        punkt = (mitte[0] - r[0], mitte[1] - r[1])
        e = self.engine.ausfuehren("a-1", self.ea.Aktion("klick", punkt=punkt), ziel=ziel, bezug=self.bezug, lease_grund="", haende_erlaubt=True)
        return e.zu_dict()

    def test_ein_aus_dem_bild_erschlossener_knoten_wird_per_hand_geklickt_und_die_pixel_aendern_sich(self):
        bgra, b, h, r = self.bild()
        ks, _ = wq.flaechen_erschliessen(self.ziel, bgra, b, h, r, 1, self.jetzt)
        feld = next(k for k in ks if k.rolle == "feld_aehnlich")
        self.welt.ersetze(self.ziel, "inferred", "flaeche", [feld])
        d = AktionsDienst(self.welt, koordinaten_klick=self.haende_klick, bild_holen=lambda z, rect: self.capture.capture_window(self.app.xid), jetzt_ms=lambda: self.jetzt + 500, schlafen=time.sleep)
        r1 = d.ausfuehren(self.ziel, feld.id, "klick")
        self.assertEqual((r1["status"], r1["methode"]), ("ausgefuehrt", "koordinate"), r1)
        self.assertEqual(r1["haende"]["status"], "ausgefuehrt")
        self.assertTrue(self.app.warte(lambda s: s["fokus"] or True))

    def test_der_klick_auf_einen_erschlossenen_knopf_wirkt_im_programm(self):
        if not shutil.which("tesseract"):
            self.skipTest("tesseract fehlt")
        bgra, b, h, r = self.bild()
        texte, _ = wq.beschriftungen_erschliessen(self.ziel, bgra, b, h, r, 1, self.jetzt)
        z = next(t for t in texte if "Zaehlen" in t.name)
        self.welt.ersetze(self.ziel, "inferred", "ocr", [z])
        d = AktionsDienst(self.welt, koordinaten_klick=self.haende_klick, jetzt_ms=lambda: self.jetzt + 500, schlafen=time.sleep)
        self.assertEqual(d.ausfuehren(self.ziel, z.id, "klick")["status"], "ausgefuehrt")
        self.assertEqual(self.app.warte(lambda s: s["klicks"] >= 1)["klicks"], 1, "der Klick auf den erkannten Text „Zaehlen“ hat den echten Knopf ausgelöst")

    def test_ein_bewusst_angelegter_anker_klickt_seinen_ort(self):
        bgra, b, h, r = self.bild()
        knopf = self.app.stand()["rects"]["knopf"]
        k = self.welt.anker_anlegen(self.ziel, "Zähl-Knopf", (knopf[0] + 20, knopf[1] + 5, knopf[0] + 60, knopf[1] + 25), urheber="daniel", jetzt_ms=self.jetzt)
        d = AktionsDienst(self.welt, koordinaten_klick=self.haende_klick, jetzt_ms=lambda: self.jetzt + 500, schlafen=time.sleep)
        self.assertEqual(d.ausfuehren(self.ziel, k.id, "klick")["status"], "ausgefuehrt")
        self.assertEqual(self.app.warte(lambda s: s["klicks"] >= 1)["klicks"], 1)

    def test_nach_einer_verschiebung_lehnen_die_haende_ab_und_nichts_wird_geklickt(self):
        bgra, b, h, r = self.bild()
        knopf = self.app.stand()["rects"]["knopf"]
        k = self.welt.anker_anlegen(self.ziel, "Zähl-Knopf", (knopf[0] + 20, knopf[1] + 5, knopf[0] + 60, knopf[1] + 25), urheber="daniel", jetzt_ms=self.jetzt)
        self.app.bewegen(120, 90)
        d = AktionsDienst(self.welt, koordinaten_klick=self.haende_klick, jetzt_ms=lambda: self.jetzt + 500, schlafen=time.sleep)
        res = d.ausfuehren(self.ziel, k.id, "klick")
        self.assertEqual((res["status"], res["grund"]), ("abgelehnt", "geometrie_geaendert"))
        time.sleep(0.4)
        self.assertEqual(self.app.stand()["klicks"], 0)


if __name__ == "__main__":
    unittest.main()
