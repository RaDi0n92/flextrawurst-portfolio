"""G06.7: Chromium über das DevTools-Protokoll lesen und bedienen (echter Chromium unter privatem Xvfb), plus ehrliche Fehlerfälle."""

from __future__ import annotations

import http.server
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path

from augen_haende_bridge.koerper import cdp

DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")

SEITE = b"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Prueftafel</title>
<style>body{margin:0;background:#fff} #flaeche{width:300px;height:100px;background:#c22}</style></head>
<body><h1 id="ueberschrift">Hallo Bridge</h1>
<button id="knopf" aria-label="Zaehlen" onclick="document.getElementById('zahl').innerText=String(Number(document.getElementById('zahl').innerText)+1)">Zaehlen</button>
<span id="zahl">0</span><br><input id="feld" aria-label="Eingabe" value=""><div id="flaeche"></div></body></html>"""


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(SEITE)

    def log_message(self, *_):
        pass


def freier_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(DISPLAY and CHROMIUM, "kein privater Xvfb (BRIDGE_TEST_XVFB=1) oder kein Chromium")
class BrowserFall(unittest.TestCase):
    groesse = "900,600"

    @classmethod
    def setUpClass(cls):
        cls.http = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()
        cls.port = freier_port()
        cls.profil = tempfile.mkdtemp()
        cls.prozess = subprocess.Popen([CHROMIUM, "--no-sandbox", "--disable-gpu", "--no-first-run", "--no-default-browser-check", f"--user-data-dir={cls.profil}",
                                        f"--remote-debugging-port={cls.port}", f"--window-size={cls.groesse}", "--window-position=0,0",
                                        f"http://127.0.0.1:{cls.http.server_address[1]}/"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.browser = cdp.CdpBrowser(cls.port)
        ende = time.monotonic() + 30
        while time.monotonic() < ende:
            if cls.browser.verfuegbar() and any(z.titel == "Prueftafel" for z in cls.browser.ziele()):
                return
            time.sleep(0.3)
        raise RuntimeError("Chromium kam nicht hoch")

    @classmethod
    def tearDownClass(cls):
        cls.prozess.terminate()
        try:
            cls.prozess.wait(10)
        except subprocess.TimeoutExpired:
            cls.prozess.kill()
        cls.http.shutdown()
        shutil.rmtree(cls.profil, ignore_errors=True)

    def seite(self):
        return self.browser.verbinden(next(z for z in self.browser.ziele() if z.titel == "Prueftafel"))


class LesenTests(BrowserFall):
    def test_ziele_titel_text_seitenbild_und_baum(self):
        ziele = self.browser.ziele()
        self.assertTrue(any(z.titel == "Prueftafel" and z.url.startswith("http://127.0.0.1:") for z in ziele))
        self.assertIn("Chrom", self.browser.version().get("Browser", "") + "Chrom")
        with self.seite() as s:
            self.assertEqual(s.titel(), "Prueftafel")
            self.assertEqual(s.auswerten("document.getElementById('ueberschrift').innerText"), "Hallo Bridge")
            png, b, h = s.seitenbild()
            self.assertTrue(png.startswith(b"\x89PNG") and b > 100 and h > 100)
            baum = s.ax_baum()
            namen = {(k.rolle, k.name) for k in baum}
            self.assertIn(("button", "Zaehlen"), namen)
            self.assertIn(("textbox", "Eingabe"), namen)
            self.assertIn(("heading", "Hallo Bridge"), namen)
            self.assertTrue(all(k.quelle == "ax" for k in baum))

    def test_dom_knoten_hat_lage_und_der_selektor_findet_nichts_erfundenes(self):
        with self.seite() as s:
            k = s.dom_knoten("#flaeche")
            self.assertEqual((k.rolle, round(k.rect[2] - k.rect[0]), round(k.rect[3] - k.rect[1])), ("div", 300, 100))
            self.assertIsNone(s.dom_knoten("#gibt-es-nicht"))


class BedienenTests(BrowserFall):
    def test_klick_tippen_und_zuruecklesen(self):
        with self.seite() as s:
            self.assertTrue(s.klick("#knopf"))
            self.assertTrue(s.klick("#knopf"))
            self.assertEqual(s.auswerten("document.getElementById('zahl').innerText"), "2", "zwei echte Klicks, zurückgelesen")
            self.assertTrue(s.tippen("#feld", "Grüße 🌍"))
            self.assertEqual(s.auswerten("document.getElementById('feld').value"), "Grüße 🌍")

    def test_ein_nicht_auffindbarer_knoten_loest_nichts_aus(self):
        with self.seite() as s:
            vorher = s.auswerten("document.getElementById('zahl').innerText")
            self.assertFalse(s.klick("#gibt-es-nicht"))
            self.assertFalse(s.tippen("#gibt-es-nicht", "x"))
            self.assertEqual(s.auswerten("document.getElementById('zahl').innerText"), vorher)


class FensterZustandTests(BrowserFall):
    """Gemessen, nicht angenommen: das Seitenbild kommt vom Browser selbst, nicht vom Bildschirm."""

    def test_verdecktes_fenster_liefert_trotzdem_das_seitenbild(self):
        from Xlib import X

        from augen_haende_bridge.koerper import x11_helfer as x

        anzeige = x.anzeige()
        wurzel = anzeige.screen().root
        decke = wurzel.create_window(0, 0, 1280, 800, 0, anzeige.screen().root_depth, X.InputOutput, X.CopyFromParent, background_pixel=0x22CC22, override_redirect=True)
        decke.map()
        anzeige.sync()
        try:
            time.sleep(0.3)
            with self.seite() as s:
                png, b, h = s.seitenbild()
                from PIL import Image
                import io

                bild = Image.open(io.BytesIO(png)).convert("RGB")
                farben = {bild.getpixel((px, py)) for px in range(0, bild.size[0], 40) for py in range(0, bild.size[1], 40)}
                self.assertNotIn((0x22, 0xCC, 0x22), farben, "kein Pixel des davorliegenden Fensters")
                self.assertIn((0xCC, 0x22, 0x22), farben, "die rote Fläche der Seite ist da")
        finally:
            decke.destroy()
            anzeige.sync()

    @unittest.skipUnless(shutil.which("openbox"), "ohne Fensterverwaltung lässt sich nichts minimieren")
    def test_minimiert_wird_gemessen_und_ehrlich_gemeldet(self):
        """Mit Fensterverwaltung (openbox, leere Konfiguration) wird das Fenster wirklich minimiert; gemessen: der Browser liefert sein Seitenbild trotzdem (er rendert die Seite selbst)."""
        rc = Path(tempfile.mkdtemp()) / "rc.xml"
        rc.write_text('<openbox_config xmlns="http://openbox.org/3.4/rc"><applications/></openbox_config>')
        wm = subprocess.Popen(["openbox", "--config-file", str(rc)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(1.0)
            with self.seite() as s:
                kennung = s.befehl("Browser.getWindowForTarget")["windowId"]
                try:
                    s.befehl("Browser.setWindowBounds", windowId=kennung, bounds={"windowState": "minimized"})
                    time.sleep(0.6)
                    zustand = s.befehl("Browser.getWindowBounds", windowId=kennung)["bounds"]["windowState"]
                    png, b, h = s.seitenbild()
                finally:
                    s.befehl("Browser.setWindowBounds", windowId=kennung, bounds={"windowState": "normal"})
            self.assertEqual(zustand, "minimized", "das Fenster war wirklich minimiert")
            self.assertTrue(png.startswith(b"\x89PNG") and b > 100, "gemessen: das Seitenbild kommt über CDP auch bei minimiertem Fenster")
        finally:
            wm.terminate()
            wm.wait(10)

    def test_kleines_fenster_kommt_vollstaendig(self):
        with self.seite() as s:
            s.befehl("Emulation.setDeviceMetricsOverride", width=200, height=150, deviceScaleFactor=1, mobile=False)
            try:
                png, b, h = s.seitenbild()
                self.assertEqual((b, h), (200, 150))
                self.assertEqual(s.fenstermass(), (200, 150))
            finally:
                s.befehl("Emulation.clearDeviceMetricsOverride")


class FehlerTests(unittest.TestCase):
    def test_kein_debug_anschluss_ist_nicht_verfuegbar_statt_erfunden(self):
        b = cdp.CdpBrowser(freier_port(), timeout=1.0)
        self.assertFalse(b.verfuegbar())
        with self.assertRaises(cdp.CdpFehler):
            b.ziele()
        with self.assertRaises(cdp.CdpFehler):
            b.verbinden()

    def test_nur_loopback(self):
        with self.assertRaises(cdp.CdpFehler):
            cdp.CdpBrowser(9222, host="192.168.0.5")

    def test_ungueltige_antworten_werden_gemeldet(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"{\"kaputt\": " if self.path.endswith("version") else json.dumps({"kein": "array"}).encode())

            def log_message(self, *_):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            b = cdp.CdpBrowser(server.server_address[1], timeout=2.0)
            self.assertFalse(b.verfuegbar(), "kaputtes JSON ist nicht verfügbar")
            with self.assertRaises(cdp.CdpFehler):
                b.ziele()
        finally:
            server.shutdown()

    def test_eine_fremde_websocket_adresse_wird_nicht_verbunden(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps([{"type": "page", "id": "1", "title": "x", "url": "u", "webSocketDebuggerUrl": "ws://10.0.0.9:1/devtools/page/1"}]).encode())

            def log_message(self, *_):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with self.assertRaises(cdp.CdpFehler) as ctx:
                cdp.CdpBrowser(server.server_address[1], timeout=2.0).verbinden()
            self.assertIn("fremde_adresse", str(ctx.exception))
        finally:
            server.shutdown()

    def test_ein_geschlossener_websocket_ergibt_cdp_fehler(self):
        with self.assertRaises(cdp.CdpFehler):
            cdp.CdpSeite(cdp.Ziel("1", "", "", "page", f"ws://127.0.0.1:{freier_port()}/x"), timeout=1.0)


if __name__ == "__main__":
    unittest.main()
