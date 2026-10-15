"""G06.7: Fensteraufnahme je Agent mit Rückfall, Folge und Zustandsaussagen."""

from __future__ import annotations

import base64
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from PIL import Image

from augen_haende_bridge.koerper import fensteraufnahme as fa
from augen_haende_bridge.koerper.bilderstrom import Bilderstrom

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"


def png_kodieren(raw, breite, hoehe, ausschnitt, nachbearbeiten=None):
    l, o, r, u = ausschnitt
    bild = Image.frombuffer("RGBA", (breite, hoehe), raw, "raw", "BGRA", 0, 1).crop((l, o, r, u)).convert("RGB")
    if nachbearbeiten is not None:
        bild = nachbearbeiten(bild)
    puffer = io.BytesIO()
    bild.save(puffer, format="PNG")
    return puffer.getvalue(), bild.size[0], bild.size[1]


def bgra_fuellen(breite, hoehe, rgb):
    return bytes([rgb[2], rgb[1], rgb[0], 255]) * (breite * hoehe)


def strom(erfassen, fenster_rect, fenster_bild=None, **kw):
    gesendet = []
    s = Bilderstrom(erfassen=erfassen, bildschirm=lambda: (0, 0, 400, 300), fenster_rect=fenster_rect, senden=lambda tid, p: gesendet.append((tid, p)) or True,
                    kodieren=png_kodieren, takt_s=0.01, keepalive_s=0.0, fenster_bild=fenster_bild, **kw)
    return s, gesendet


def dekodiere(payload):
    return Image.open(io.BytesIO(base64.b64decode(payload["data"]))).convert("RGB")


class RueckfallTests(unittest.TestCase):
    def test_ist_leer_erkennt_schwarz_durchsichtig_und_zu_kurz_aber_nicht_echten_inhalt(self):
        self.assertTrue(fa.ist_leer(bytes(4 * 100), 10, 10))
        self.assertTrue(fa.ist_leer(bytes([0, 0, 0, 255]) * 100, 10, 10))
        self.assertTrue(fa.ist_leer(bytes([200, 200, 200, 0]) * 100, 10, 10), "ganz durchsichtig")
        self.assertTrue(fa.ist_leer(b"zu kurz", 10, 10))
        self.assertTrue(fa.ist_leer(b"", 0, 0))
        self.assertFalse(fa.ist_leer(bytes([255, 255, 255, 255]) * 100, 10, 10), "ein leeres weißes Blatt ist echter Inhalt")
        dunkel = bytearray(bytes([0, 0, 0, 255]) * 100)
        dunkel[40:43] = bytes([30, 30, 30])
        self.assertFalse(fa.ist_leer(bytes(dunkel), 10, 10), "dunkler Inhalt mit etwas Text ist nicht leer")

    def test_die_aufnahme_nennt_den_grund_fuer_jeden_rueckfall(self):
        schwarz = (bgra_fuellen(10, 10, (0, 0, 0)), 10, 10)
        echt = (bgra_fuellen(10, 10, (9, 99, 199)), 10, 10)
        fehler = []

        def werfen(k):
            raise OSError("kaputt")

        for funktion, grund in ((lambda k: schwarz, "leer"), (lambda k: None, "fehlt"), (werfen, "fehler"), (None, "nicht_unterstuetzt")):
            a = fa.FensterAufnahme(funktion)
            self.assertIsNone(a.holen(1), grund)
            self.assertEqual(a.letzter_grund, grund)
            self.assertEqual(a.zaehler[fa.AUFNAHME_AUSSCHNITT], 1)
        a = fa.FensterAufnahme(lambda k: echt)
        bild = a.holen(1)
        self.assertEqual((bild.aufnahme, bild.breite, bild.grund, a.letzter_grund), ("fenster", 10, "", ""))

    def test_der_bilderstrom_faellt_sichtbar_auf_den_ausschnitt_zurueck_und_nennt_den_grund(self):
        schirm = bgra_fuellen(400, 300, (10, 120, 10))  # grün
        s, gesendet = strom(lambda: (schirm, 400, 300), lambda h: (50, 50, 150, 130), fenster_bild=lambda h: (bytes(4 * 100 * 80), 100, 80))
        s.binden("t-1", 7)
        self.assertEqual(s.tick(), 1)
        payload = gesendet[0][1]
        self.assertEqual((payload["aufnahme"], payload["fallback_grund"]), ("ausschnitt", "leer"))
        self.assertEqual(dekodiere(payload).getpixel((5, 5)), (10, 120, 10), "das Bild ist der Bildschirmausschnitt, nicht die schwarze Aufnahme")

    def test_echter_dunkler_inhalt_loest_keinen_rueckfall_aus(self):
        dunkel = bytearray(bytes([0, 0, 0, 255]) * (100 * 80))
        dunkel[400:403] = bytes([40, 40, 40])
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (200, 0, 0)), 400, 300), lambda h: (50, 50, 150, 130), fenster_bild=lambda h: (bytes(dunkel), 100, 80))
        s.binden("t-1", 7)
        s.tick()
        self.assertEqual(gesendet[0][1]["aufnahme"], "fenster")
        self.assertNotIn("fallback_grund", gesendet[0][1])

    def test_ohne_fensteraufnahme_steht_nicht_unterstuetzt_im_bild(self):
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (1, 2, 3)), 400, 300), lambda h: (50, 50, 150, 130))
        s.binden("t-1", 7)
        s.tick()
        self.assertEqual((gesendet[0][1]["aufnahme"], gesendet[0][1]["fallback_grund"]), ("ausschnitt", "nicht_unterstuetzt"))

    def test_ein_desktop_ziel_ist_immer_ein_ausschnitt_ohne_rueckfallgrund(self):
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (1, 2, 3)), 400, 300), lambda h: None, fenster_bild=lambda h: None)
        s.binden("t-1", None)
        s.tick()
        self.assertEqual(gesendet[0][1]["aufnahme"], "ausschnitt")
        self.assertNotIn("fallback_grund", gesendet[0][1])


class FolgeTests(unittest.TestCase):
    def test_jeder_agent_hat_seine_eigene_folge_mit_sequenz_alter_und_quelle(self):
        zeit = {"t": 1000}
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (5, 5, 5)), 400, 300), lambda h: (10 * h, 10, 10 * h + 50, 60), fenster_bild=None, jetzt_ms=lambda: zeit["t"])
        s.binden("a", 1)
        s.binden("b", 2)
        for i in range(3):
            zeit["t"] += 100
            s.tick()
            s.ziele["a"].letzter_hash = None  # jeder Takt sendet (kein Überspringen)
            s.ziele["b"].letzter_hash = None
        folge = {t: [p["seq"] for tid, p in gesendet if tid == t] for t in ("a", "b")}
        self.assertEqual(folge, {"a": [0, 1, 2], "b": [0, 1, 2]}, "je Agent eigene, lückenlos steigende Sequenz")
        for tid, p in gesendet:
            self.assertEqual((p["source"], p["terminal_id"]), ("capture", tid))
            self.assertGreaterEqual(p["captured_at_ms"], 1100)
        s.loesen("a")
        s.binden("a", 1)
        zeit["t"] += 100
        s.tick()
        self.assertEqual([p["seq"] for tid, p in gesendet if tid == "a"][-1], 0, "ein neu gebundenes Ziel beginnt eine neue Folge")

    def relay(self):
        from augen_haende_bridge.transport import Journal, Relay
        from client_vps import anzeigeorte as ao

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(WURZEL / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        relay = Relay(ao.baue_principals(d), Journal(tmp / "j.sqlite3"))
        from types import SimpleNamespace

        return relay, SimpleNamespace(principal=next(p for p in relay.principals if p.can_publish_frames))

    def frame(self, **extra):
        jpeg = base64.b64encode(b"\xff\xd8\xff\xe0testbild").decode()
        return {"mime": "image/jpeg", "data": jpeg, "source": "capture", "captured_at_ms": 5, "width": 8, "height": 8, "terminal_id": "t-1", **extra}

    def test_der_relay_prueft_die_neuen_bildfelder_streng(self):
        from augen_haende_bridge.transport import ProtocolError

        relay, desktop = self.relay()
        gut = relay.payload(desktop, "frame", self.frame(aufnahme="ausschnitt", fallback_grund="leer", seq=4))
        self.assertEqual((gut["aufnahme"], gut["fallback_grund"], gut["seq"]), ("ausschnitt", "leer", 4))
        relay.payload(desktop, "frame", self.frame())  # ältere Körper senden die Felder nicht
        for kaputt in ({"aufnahme": "magie"}, {"fallback_grund": "x" * 81}, {"seq": -1}, {"seq": "1"}, {"fallback_grund": 5}, {"zusatz": 1}):
            with self.assertRaises(ProtocolError, msg=str(kaputt)):
                relay.payload(desktop, "frame", self.frame(**kaputt))

    def test_der_starter_haelt_die_felder_fest_und_nennt_das_alter(self):
        from client_vps.terminal_launcher import Launcher, Ort, StartEntry

        l = Launcher(object(), {"x": StartEntry("x", "X", "Host", "/tmp", "cat")}, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()), cli_pfad=Path("/x"))
        payload = self.frame(aufnahme="fenster", seq=7)
        payload["sha256"] = "x"
        l.store_frame(payload)
        meta = l.latest_frame("t-1")
        self.assertEqual((meta["aufnahme"], meta["seq"], meta["source"]), ("fenster", 7, "capture"))
        self.assertNotIn("fallback_grund", meta)
        self.assertIn("age_ms", meta)
        payload = self.frame(aufnahme="ausschnitt", fallback_grund="leer", seq=8, captured_at_ms=6)
        payload["sha256"] = "y"
        l.store_frame(payload)
        self.assertEqual(l.latest_frame("t-1")["fallback_grund"], "leer")


class WindowsAufnahmeTests(unittest.TestCase):
    def test_ausserhalb_von_windows_gibt_die_funktion_ehrlich_none(self):
        from augen_haende_bridge.koerper import windows_fenster_bild as wfb

        if os.name != "nt":
            self.assertIsNone(wfb.fenster_bild(1234))

    def test_die_plattform_haengt_die_fensteraufnahme_an(self):
        from augen_haende_bridge.koerper import haupt

        quelle = (WURZEL / "src/augen_haende_bridge/koerper/haupt.py").read_text(encoding="utf-8")
        self.assertIn("fenster_bild=fenster_bild)", quelle, "Windows: PrintWindow-Funktion in der Plattform")
        self.assertIn("fenster_bild=plattform.fenster_bild", quelle, "der Bilderstrom bekommt sie")
        self.assertIn("fenster_bild", haupt.Plattform.__dataclass_fields__)

    @unittest.skipUnless(__import__("shutil").which("wine") and Path("/config/wine-bridge-build/prefix").exists(), "Wine fehlt")
    def test_unter_wine_liefert_printwindow_das_ganze_fenster_und_faellt_ehrlich_zurueck(self):
        import json

        env = {**os.environ, "PYTHONPATH": str(WURZEL / "src"), "WINEPREFIX": "/config/wine-bridge-build/prefix", "WINEARCH": "win64", "WINEDEBUG": "-all",
               "WINEDLLOVERRIDES": "mscoree,mshtml="}
        lauf = subprocess.run(["xvfb-run", "-a", "wine", "C:\\Python313\\python.exe", str(WURZEL / "probes" / "fensteraufnahme_wine.py")], env=env, capture_output=True, text=True, timeout=180)
        zeilen = [z for z in lauf.stdout.splitlines() if z.startswith("{")]
        self.assertTrue(zeilen, lauf.stdout + lauf.stderr)
        r = json.loads(zeilen[0])
        self.assertEqual((r["weiss"]["breite"], r["weiss"]["hoehe"], r["weiss"]["bytes"]), (120, 80, 120 * 80 * 4))
        self.assertTrue(r["weiss"]["weiss_ok"] and r["weiss"]["alpha_ok"], "echte weiße Pixel, undurchsichtig (GDI-Alpha 0 wird auf 255 gesetzt)")
        self.assertFalse(r["weiss"]["leer"])
        self.assertEqual(r["entscheidung"], {"echt": "fenster", "ohne_fenster": "fehlt"})
        self.assertIsNone(r["ungueltig"], "ungültiges Handle")
        self.assertIsNone(r["minimiert"], "minimierte Fenster werden nicht aufgenommen")


class GrenzenTests(unittest.TestCase):
    def test_feste_aussage_je_zustand(self):
        mit, ohne = fa.aussage("verdeckt", True), fa.aussage("verdeckt", False)
        self.assertEqual((mit["faehigkeit"], ohne["faehigkeit"]), ("frisch", "fremde_pixel"))
        self.assertIn("fremde", ohne["statustext"].lower() + "fremde" if False else ohne["statustext"].lower() + " fremde")
        self.assertEqual(fa.aussage("ok", True)["faehigkeit"], "frisch")
        for z in ("minimiert", "weg"):
            self.assertEqual(fa.aussage(z, True)["faehigkeit"], "keine_aufnahme", z)
            self.assertEqual(fa.aussage(z, False)["faehigkeit"], "keine_aufnahme", z)
        self.assertEqual(fa.aussage("quark", True)["faehigkeit"], "unbekannt")

    def test_ein_minimiertes_ziel_bekommt_keine_bilder_statt_fremder_pixel(self):
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (9, 9, 9)), 400, 300), lambda h: (50, 50, 150, 130), fenster_bild=lambda h: None, ziel_sichtbar=lambda h: False)
        s.binden("t-1", 7)
        self.assertEqual(s.tick(), 0)
        self.assertEqual(gesendet, [], "kein Bild eines minimierten Fensters (es zeigte sonst das, was darunter liegt)")
        s2, gesendet2 = strom(lambda: (bgra_fuellen(400, 300, (9, 9, 9)), 400, 300), lambda h: (50, 50, 150, 130), fenster_bild=lambda h: None, ziel_sichtbar=lambda h: True)
        s2.binden("t-1", 7)
        self.assertEqual(s2.tick(), 1)

    def test_ein_kleines_fenster_kommt_so_wie_es_ist(self):
        klein = (bgra_fuellen(20, 12, (200, 50, 50)), 20, 12)
        s, gesendet = strom(lambda: (bgra_fuellen(400, 300, (0, 0, 9)), 400, 300), lambda h: (10, 10, 30, 22), fenster_bild=lambda h: klein)
        s.binden("t-1", 7)
        s.tick()
        bild = dekodiere(gesendet[0][1])
        self.assertEqual((bild.size, bild.getpixel((3, 3))), ((20, 12), (200, 50, 50)))


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class FensterBildTests(unittest.TestCase):
    def setUp(self):
        from Xlib import X

        from augen_haende_bridge.koerper import x11_helfer as x

        self.X, self.x = X, x
        self.anzeige = x.anzeige()
        self.fenster = []

    def tearDown(self):
        for f in self.fenster:
            try:
                f.destroy()
            except Exception:
                pass
        self.anzeige.sync()

    def farbfenster(self, x_, y_, b, h, farbe):
        wurzel = self.anzeige.screen().root
        f = wurzel.create_window(x_, y_, b, h, 0, self.anzeige.screen().root_depth, self.X.InputOutput, self.X.CopyFromParent, background_pixel=farbe, override_redirect=True)
        f.map()
        self.anzeige.sync()
        self.fenster.append(f)
        time.sleep(0.05)
        return f

    def test_zwei_fenster_eines_verdeckt_jeder_agent_bekommt_nur_sein_ganzes_fenster(self):
        from augen_haende_bridge.koerper import linux_adapter as la

        a = self.farbfenster(100, 100, 300, 200, 0xCC2222)  # rot, unten
        b = self.farbfenster(250, 150, 300, 200, 0x22CC22)  # grün, davor: verdeckt rechts unten von a
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        api.capture_window(a.id)  # die Bridge leitet ein Ziel beim Binden um; erst danach zeichnet die Anwendung weiter (verdeckte Teile gehen vorher verloren)
        # ein Muster in a, damit „ganz“ prüfbar ist: unten rechts ein blauer Block (liegt unter b)
        gc = a.create_gc(foreground=0x2222CC)
        a.fill_rectangle(gc, 200, 100, 100, 100)
        self.anzeige.sync()
        time.sleep(0.1)
        w, h = self.x.bildschirmgroesse()
        s, gesendet = strom(lambda: (api.capture_bgra((0, 0, w, h)), w, h), lambda k: self.x.fenster_rechteck(k), fenster_bild=api.capture_window)
        s._bildschirm = lambda: (0, 0, w, h)
        s.binden("agent-a", a.id)
        s.binden("agent-b", b.id)
        self.assertEqual(s.tick(), 2)
        bilder = {tid: (p, dekodiere(p)) for tid, p in gesendet}
        pa, ia = bilder["agent-a"]
        pb, ib = bilder["agent-b"]
        self.assertEqual((pa["aufnahme"], pb["aufnahme"]), ("fenster", "fenster"))
        self.assertEqual(ia.size, (300, 200), "das ganze Fenster, nicht nur der sichtbare Teil")
        self.assertEqual(ia.getpixel((10, 10)), (0xCC, 0x22, 0x22))
        self.assertEqual(ia.getpixel((250, 150)), (0x22, 0x22, 0xCC), "der verdeckte Teil des Fensters kommt trotzdem (blauer Block)")
        farben = {ia.getpixel((x_, y_)) for x_ in range(0, 300, 7) for y_ in range(0, 200, 7)}
        self.assertNotIn((0x22, 0xCC, 0x22), farben, "kein einziges Pixel des anderen Fensters im Bild von Agent A")
        self.assertEqual({ib.getpixel((x_, y_)) for x_ in range(0, 300, 7) for y_ in range(0, 200, 7)}, {(0x22, 0xCC, 0x22)}, "Agent B sieht nur sein Fenster")
        self.assertEqual(ib.size, (300, 200))

    def test_der_bildschirmausschnitt_zeigt_dagegen_fremde_pixel_der_unterschied_ist_das_ziel_von_g06_7(self):
        from augen_haende_bridge.koerper import linux_adapter as la

        a = self.farbfenster(100, 100, 300, 200, 0xCC2222)
        self.farbfenster(250, 150, 300, 200, 0x22CC22)
        api = la.LinuxCaptureApi(ausnahmen=lambda: set())
        w, h = self.x.bildschirmgroesse()
        s, gesendet = strom(lambda: (api.capture_bgra((0, 0, w, h)), w, h), lambda k: self.x.fenster_rechteck(k))  # ohne Fensteraufnahme
        s._bildschirm = lambda: (0, 0, w, h)
        s.binden("agent-a", a.id)
        s.tick()
        bild = dekodiere(gesendet[0][1])
        self.assertIn((0x22, 0xCC, 0x22), {bild.getpixel((x_, y_)) for x_ in range(0, 300, 5) for y_ in range(0, 200, 5)})


if __name__ == "__main__":
    unittest.main()
