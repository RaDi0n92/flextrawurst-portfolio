"""Linux-Körper: Plattformbeschreibung, Selbsttest, Pfade, Startskript und ein echter Körper-Prozess gegen einen echten Relay (unter eigenem Xvfb)."""

from __future__ import annotations

import base64
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
ENV = {"BRIDGE_DESKTOP_TOKEN": "w" * 40, "BRIDGE_AGENT_TOKEN": "s" * 40}


def umgebung(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k != "BRIDGE_BACKEND"}
    env["PYTHONPATH"] = f"{WURZEL / 'src'}:{WURZEL}"
    env.update(extra)
    return env


class PlattformTests(unittest.TestCase):
    def test_windows_plattform_hat_die_bisherigen_bausteine(self):
        from augen_haende_bridge.koerper import haupt

        with patch("augen_haende_bridge.koerper.sichtbarkeit.WindowsQuelle", return_value=SimpleNamespace(name="q")), \
                patch("augen_haende_bridge.windows_capture.Win32CaptureApi", return_value=SimpleNamespace(name="c")):
            p = haupt.plattform_windows()
        self.assertEqual((p.name, p.ort, p.anzeigename), ("windows", "windows", "Windows"))
        self.assertEqual((p.quelle.name, p.capture_api.name), ("q", "c"))
        self.assertIsNone(p.haende_senden, "Windows nimmt die Standard-Hände (SendInput)")
        self.assertIsNone(p.scanner)
        self.assertTrue(str(p.einstellungen_pfad).endswith("einstellungen.json"))
        from augen_haende_bridge.koerper.dateiwahl import datei_waehlen
        from augen_haende_bridge.koerper.notaus import TastaturHook

        self.assertIs(p.datei_waehlen, datei_waehlen)
        self.assertIsInstance(p.hook_bauen(SimpleNamespace()), TastaturHook)

    def fenster(self, hwnd, rect, pid=1):
        return SimpleNamespace(hwnd=hwnd, rect=rect, process_id=pid)

    def test_verdeckt_erkennt_ein_wesentliches_fenster_davor(self):
        from augen_haende_bridge.koerper.haupt import ziel_verdeckt_pruefer

        api = SimpleNamespace(enumerate_windows=lambda: [self.fenster(2, (0, 0, 800, 600)), self.fenster(1, (100, 100, 500, 400))])  # oben zuerst
        self.assertTrue(ziel_verdeckt_pruefer(api, 99)(1))

    def test_ein_kleines_fenster_davor_oder_eines_der_bridge_oder_keines_verdeckt_nicht(self):
        from augen_haende_bridge.koerper.haupt import ziel_verdeckt_pruefer

        ziel = self.fenster(1, (100, 100, 500, 400))
        for davor in (self.fenster(2, (480, 380, 520, 420), pid=1), self.fenster(3, (0, 0, 800, 600), pid=99)):  # klein / ein Fenster der Bridge (eigene PID 99)
            api = SimpleNamespace(enumerate_windows=lambda d=davor: [d, ziel])
            self.assertFalse(ziel_verdeckt_pruefer(api, 99)(1), (davor.hwnd,))
        api = SimpleNamespace(enumerate_windows=lambda: [ziel, self.fenster(2, (0, 0, 800, 600))])  # das Ziel liegt oben
        self.assertFalse(ziel_verdeckt_pruefer(api, 99)(1))
        self.assertFalse(ziel_verdeckt_pruefer(api, 99)(777), "ein unbekanntes Fenster gilt nicht als verdeckt")

    def test_haupt_linux_waehlt_das_linux_backend_beim_import_und_kennt_nur_kde_orte(self):
        lauf = subprocess.run([sys.executable, "-c", "from augen_haende_bridge.koerper import haupt_linux, fenster; import os; print(os.environ['BRIDGE_BACKEND'], fenster.Fenster.__module__.rsplit('.',1)[-1], sorted(haupt_linux.ORTE))"],
                              env=umgebung(), capture_output=True, text=True, timeout=60)
        self.assertEqual(lauf.stdout.split(), ["linux", "fenster_linux", "['kde1',", "'kde2']"], lauf.stderr[-400:])

    def test_unbekannter_ort_und_fehlende_zugangsdaten_werden_klar_abgewiesen(self):
        lauf = subprocess.run([sys.executable, "-m", "augen_haende_bridge.koerper.haupt_linux", "--ort", "mars"], env=umgebung(), capture_output=True, text=True, timeout=60)
        self.assertEqual(lauf.returncode, 2)
        self.assertIn("Unbekannter Ort", lauf.stderr)
        lauf = subprocess.run([sys.executable, "-m", "augen_haende_bridge.koerper.haupt_linux", "--ort", "kde1"],
                              env=umgebung(BRIDGE_TOKEN_DATEI="/nichts/da.token", BRIDGE_TOKEN=""), capture_output=True, text=True, timeout=60)
        self.assertEqual(lauf.returncode, 3)
        self.assertIn("nicht lesbar", lauf.stderr)
        self.assertNotIn("Traceback", lauf.stderr)

    def test_die_version_wird_genannt(self):
        lauf = subprocess.run([sys.executable, "-m", "augen_haende_bridge.koerper.haupt_linux", "--ort", "kde2", "--version"], env=umgebung(), capture_output=True, text=True, timeout=60)
        self.assertRegex(lauf.stdout, r"AugenUndHaendeBridge \d+\.\d+\.\d+-g02 \(Linux\)")

    def test_haupt_hat_keine_windows_importe_mehr_im_lauf_fuer_den_linux_weg(self):
        """Der gemeinsame Ablauf `_lauf` bekommt alles Plattformabhängige über die Beschreibung (kein Win32-Konstruktor im Ablauf)."""
        quelle = (WURZEL / "src" / "augen_haende_bridge" / "koerper" / "haupt.py").read_text(encoding="utf-8")
        lauf = quelle[quelle.index("def _lauf("):]
        for verboten in ("TastaturHook(", "WindowsQuelle(", "Win32CaptureApi(", "standard_pfad()", "w.require_windows()"):
            self.assertNotIn(verboten, lauf, verboten)


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class SelbsttestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="st-"))
        self.server = socket.socket()
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(5)
        self.url = f"ws://127.0.0.1:{self.server.getsockname()[1]}"

    def tearDown(self):
        self.server.close()

    def zeilen(self, token_datei):
        from augen_haende_bridge.koerper import selbsttest_linux

        return {name: (stufe, text) for stufe, name, text in selbsttest_linux.pruefungen("kde1", self.url, token_datei)}

    def test_jede_pruefung_steht_einzeln_da_und_nichts_fehlt_mit_zugangsdaten(self):
        token = self.tmp / "t.token"
        token.write_text("x" * 40)
        z = self.zeilen(token)
        self.assertEqual(sorted(z), sorted(["Anzeige", "Fensterschicht", "Aufnahme", "Eingabe", "Not-Aus (F12)", "Hotkeys", "Schriften", "Compositor", "Relay", "Sitzung"]))
        for name in ("Anzeige", "Fensterschicht", "Aufnahme", "Eingabe", "Not-Aus (F12)", "Schriften", "Relay"):
            self.assertEqual(z[name][0], "ok", (name, z[name]))
        self.assertIn("XComposite", z["Aufnahme"][1])
        self.assertIn(z["Compositor"][0], ("ok", "Hinweis"))

    def test_fehlende_zugangsdaten_und_ein_nicht_erreichbarer_relay_werden_gemeldet(self):
        self.assertEqual(self.zeilen(self.tmp / "gibt-es-nicht")["Relay"][0], "fehlt")
        kurz = self.tmp / "k.token"
        kurz.write_text("zu kurz")
        self.assertIn("zu kurz", self.zeilen(kurz)["Relay"][1])
        self.server.close()
        z = self.zeilen(kurz)
        self.assertEqual(z["Relay"][0], "fehlt")

    def test_der_rueckgabewert_folgt_dem_ergebnis_und_still_gibt_nichts_aus(self):
        from augen_haende_bridge.koerper import selbsttest_linux

        token = self.tmp / "t.token"
        token.write_text("x" * 40)
        self.assertEqual(selbsttest_linux.lauf("9.9.9-test", "kde1", self.url, token, still=True), 0)
        self.assertEqual(selbsttest_linux.lauf("9.9.9-test", "kde1", self.url, self.tmp / "weg", still=True), 1)

    def test_der_selbsttest_aendert_nichts(self):
        from augen_haende_bridge.koerper import fenster_linux as fl

        vorher = len(fl._fenster)
        self.zeilen(None)
        self.assertEqual(len(fl._fenster), vorher, "das Testfenster ist wieder weg")


class PfadeTests(unittest.TestCase):
    def test_linux_einstellungen_liegen_in_der_xdg_konfiguration_je_ort(self):
        from augen_haende_bridge.koerper.einstellungen import standard_pfad

        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/tmp/xdgk"}, clear=False):
            os.environ.pop("LOCALAPPDATA", None)
            self.assertEqual(standard_pfad("kde1"), Path("/tmp/xdgk/AugenUndHaendeBridge/einstellungen-kde1.json"))
            self.assertEqual(standard_pfad("kde2").name, "einstellungen-kde2.json")
            self.assertEqual(standard_pfad().name, "einstellungen.json")

    def test_ohne_xdg_gilt_das_home_verzeichnis(self):
        from augen_haende_bridge.koerper.einstellungen import standard_pfad

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("LOCALAPPDATA", None)
            os.environ.pop("XDG_CONFIG_HOME", None)
            self.assertEqual(standard_pfad("kde1"), Path.home() / ".config" / "AugenUndHaendeBridge" / "einstellungen-kde1.json")

    def test_windows_pfad_bleibt_localappdata(self):
        from augen_haende_bridge.koerper.einstellungen import standard_pfad

        with patch.dict(os.environ, {"LOCALAPPDATA": "C:\\Users\\x\\AppData\\Local"}):
            self.assertEqual(standard_pfad().name, "einstellungen.json")
            self.assertIn("AugenUndHaendeBridge", str(standard_pfad()))
            self.assertNotIn("kde1", str(standard_pfad("kde1")))

    def test_das_log_liegt_im_xdg_zustandsordner(self):
        from augen_haende_bridge.koerper import haupt

        tmp = tempfile.mkdtemp()
        with patch.dict(os.environ, {"XDG_STATE_HOME": tmp}):
            os.environ.pop("LOCALAPPDATA", None)
            self.assertEqual(haupt.log_pfad(), Path(tmp) / "AugenUndHaendeBridge" / "bridge.log")

    def test_einstellungen_speichern_und_laden_ueber_den_linux_pfad(self):
        from augen_haende_bridge.koerper.einstellungen import Einstellungen, standard_pfad

        tmp = tempfile.mkdtemp()
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": tmp}):
            os.environ.pop("LOCALAPPDATA", None)
            e = Einstellungen(standard_pfad("kde1"))
            e.setzen("raute:Codex", {"x": 12})
            self.assertTrue(e.speichern())
            neu = Einstellungen(standard_pfad("kde1"))
            neu.laden()
            self.assertEqual(neu.element("raute:Codex").get("x"), 12)
            andere = Einstellungen(standard_pfad("kde2"))
            andere.laden()
            self.assertEqual(andere.element("raute:Codex"), {}, "KDE 2 hat seine eigenen Einstellungen")


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class EinstellungenFensterTests(unittest.TestCase):
    def test_ort_und_groesse_werden_gemerkt_und_nach_dem_neustart_wiederhergestellt(self):
        from augen_haende_bridge.koerper import fenster_linux as fl
        from augen_haende_bridge.koerper.einstellungen import Einstellungen, anwenden, erfassen

        app = fl.Anwendung()
        app.starten()
        tmp = Path(tempfile.mkdtemp()) / "e.json"
        f = fl.Fenster(120, 90, 301, 205, titel="Probe")
        f.zeige(aktivieren=False)
        app.pumpen(150)
        f.verschiebe(333, 222, 410, 260)
        app.pumpen(150)
        e = Einstellungen(tmp)
        e.setzen("terminal:Codex", erfassen(f, "terminal"))
        self.assertTrue(e.speichern())
        f.schliessen()
        app.pumpen(100)
        neu = Einstellungen(tmp)
        neu.laden()
        g = fl.Fenster(0, 0, 100, 100, titel="Probe 2")
        g.zeige(aktivieren=False)
        anwenden(g, neu.element("terminal:Codex"), "terminal", lambda: (0, 0, 1280, 800))
        app.pumpen(200)
        self.assertEqual(g.rechteck(), (333, 222, 333 + 410, 222 + 260))
        g.schliessen()


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class KoerperEndeZuEndeTests(unittest.TestCase):
    """Ein echter Linux-Körper-Prozess (über das Startskript) gegen einen echten Relay und Starter; zwei Desktops spielen KDE 2 mit derselben Laufzeit wie der Körper."""

    @classmethod
    def setUpClass(cls):
        from test_bridge_server_anzeigeort import Desktop, freier_port

        cls.Desktop = Desktop
        cls.tmp = Path(tempfile.mkdtemp(prefix="g06k-"))
        cls.runtime = cls.tmp / "runtime"
        (cls.tmp / "starts.json").write_text(json.dumps({"starts": [{"start_id": "katze", "name": "Katze", "ort": "Host", "ordner": "/tmp", "programm": "cat", "bestaetigt": True}]}))
        (cls.tmp / "orte.json").write_text(json.dumps({"orte": {"Host": {"kind": "host"}}}))
        (cls.tmp / "desktops.json").write_text((WURZEL / "client_vps" / "desktops.json").read_text())
        cls.port = freier_port()
        env = {**os.environ, **ENV, "BRIDGE_SPRACHERKENNUNG": "aus", "PYTHONPATH": f"{WURZEL / 'src'}:{WURZEL}"}
        cls.server = subprocess.Popen([sys.executable, str(WURZEL / "client_vps" / "bridge_server.py"), "--port", str(cls.port), "--journal", str(cls.tmp / "j.sqlite3"),
                                       "--starts", str(cls.tmp / "starts.json"), "--orte", str(cls.tmp / "orte.json"), "--runtime-dir", str(cls.runtime),
                                       "--desktops", str(cls.tmp / "desktops.json")], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        zeile, t0 = "", time.monotonic()
        while "Bridge relay ready" not in zeile and time.monotonic() - t0 < 30:
            zeile = cls.server.stdout.readline()
            if not zeile and cls.server.poll() is not None:
                raise RuntimeError("Relay ist nicht gestartet")
        threading.Thread(target=lambda: [None for _ in cls.server.stdout], daemon=True).start()
        cls.koerper = None

    @classmethod
    def tearDownClass(cls):
        if cls.koerper is not None and cls.koerper.poll() is None:
            cls.koerper.send_signal(signal.SIGTERM)
            try:
                cls.koerper.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.koerper.kill()
        cls.server.send_signal(signal.SIGTERM)
        try:
            cls.server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            cls.server.kill()

    def fenster_des_koerpers(self, pid):
        from augen_haende_bridge.koerper import linux_adapter as la

        return {f.title: f for f in la.LinuxWindowApi().enumerate_windows() if f.process_id == pid}

    def warte(self, bedingung, sekunden, text):
        t0 = time.monotonic()
        while time.monotonic() - t0 < sekunden:
            wert = bedingung()
            if wert:
                return wert
            time.sleep(0.2)
        raise AssertionError(f"Zeitüberschreitung: {text}")

    def test_der_koerper_laeuft_wie_unter_windows(self):
        from Xlib import X, XK
        from Xlib.ext import xtest
        from PIL import Image

        from augen_haende_bridge.koerper import x11_helfer as x
        from client_vps import anzeigeorte as ao

        desktops = ao.lade_desktops(self.tmp / "desktops.json", self.runtime, ENV)
        token_kde1 = self.runtime / "tokens" / "desktop-kde1.token"
        self.assertTrue(token_kde1.exists(), "der Relay legt die Zugangsdaten beim ersten Start an")
        bericht, config, state = self.tmp / "bericht.json", self.tmp / "config", self.tmp / "state"
        env = umgebung(BRIDGE_URL=f"ws://127.0.0.1:{self.port}", BRIDGE_TOKEN_DATEI=str(token_kde1), BRIDGE_TEST_AUTOSTART="katze", BRIDGE_TEST_TIPPE="hallo-aus-dem-koerper",
                       BRIDGE_TEST_BERICHT=str(bericht), BRIDGE_TEST_ENDE_S="55", XDG_CONFIG_HOME=str(config), XDG_STATE_HOME=str(state), HOME=str(self.tmp))
        env.pop("BRIDGE_TOKEN", None)
        type(self).koerper = subprocess.Popen(["sh", str(WURZEL / "client_vps" / "koerper_linux_starten.sh"), "kde1"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=lambda: [None for _ in self.koerper.stdout], daemon=True).start()
        pid = self.koerper.pid

        # 1. Raute, Terminal, Chat, Regie stehen als echte Fenster da
        def fenster_da():
            f = self.fenster_des_koerpers(pid)
            return f if any("Katze" in t for t in f) and any("Regie" in t for t in f) else None

        fenster = self.warte(fenster_da, 40, "Fenster des Körpers erscheinen nicht")
        titel = sorted(fenster)
        terminal = next(f for t, f in fenster.items() if "Katze · Host" in t)
        self.assertTrue(any("Regie" in t for t in titel), titel)
        self.assertTrue(any("Chat" in t for t in titel), titel)

        # 2. Tastatur: in das Terminalfenster tippen
        anzeige = x.anzeige()
        mitte_x, mitte_y = (terminal.rect[0] + terminal.rect[2]) // 2, (terminal.rect[1] + terminal.rect[3]) // 2
        time.sleep(6)  # der Agent läuft, der erste Text ist getippt
        xtest.fake_input(anzeige, X.MotionNotify, x=mitte_x, y=mitte_y)
        anzeige.sync()
        time.sleep(0.5)
        # Was ein Fensterverwalter nach einem Klick ins Terminal tut: die Tastatur gehört jetzt diesem Fenster (ohne Verwalter folgt sie sonst dem Zeiger)
        anzeige.create_resource_object("window", terminal.hwnd).set_input_focus(X.RevertToParent, X.CurrentTime)
        anzeige.sync()
        time.sleep(0.4)
        for zeichen in (XK.XK_x, XK.XK_y, XK.XK_z, XK.XK_Return):
            code = anzeige.keysym_to_keycode(zeichen)
            xtest.fake_input(anzeige, X.KeyPress, code)
            xtest.fake_input(anzeige, X.KeyRelease, code)
            anzeige.sync()
            time.sleep(0.15)

        # 3. Ziel-Gast: KDE 2 startet ein Terminal und legt dessen Arbeitsziel auf diesen Desktop (KDE 1)
        kde2 = self.Desktop(f"ws://127.0.0.1:{self.port}", next(d.token for d in desktops if d.ort == "kde2"), "kde2")
        kde2.start()
        kde2.senden("anzeigeorte_request", {})
        kde2.warte("anzeigeorte")
        kde2.senden("terminal_start", {"start_id": "katze", "rows": 24, "cols": 80})
        tid2 = kde2.warte("terminal_state", lambda p: p["state"] == "running")["terminal_id"]
        kde2.senden("terminal_ziel", {"terminal_id": tid2, "ort": "kde1"})
        meta = self.runtime / "frames" / tid2 / "latest.json"
        self.warte(meta.exists, 30, "kein Bild vom Ziel-Gast")
        daten = json.loads(meta.read_text())
        self.assertEqual(daten["source"], "capture")
        bild = Image.open(self.runtime / "frames" / tid2 / daten["file"])
        self.assertEqual(bild.size, x.bildschirmgroesse(), "der ganze Bildschirm dieses Desktops")
        ziel_meldung = kde2.warte("terminal_ort", lambda p: p["zielort"] == "kde1")
        self.assertEqual((ziel_meldung["anzeigeort"], ziel_meldung["aktiv"]), ("kde2", True))
        ablage = os.environ.get("LINUX_KOERPER_BILD")
        if ablage:
            bild.save(ablage)

        # 4. Ende abwarten und den Bericht lesen
        kde2.senden("terminal_close", {"terminal_id": tid2})
        kde2.stop()
        self.koerper.wait(timeout=80)
        self.assertEqual(self.koerper.returncode, 0, "der Körper beendet sich sauber")
        daten = json.loads(bericht.read_text())
        self.assertEqual(daten["status"], "verbunden")
        agent = next(a for a in daten["agenten"] if a["name"] == "Katze")
        text = "\n".join(agent["terminal_text"])
        self.assertIn("hallo-aus-dem-koerper", text, "der getippte Text kam über den Relay und die PTY zurück")
        self.assertIn("xyz", text, "Tastatureingaben im Terminalfenster kamen an")
        self.assertEqual(agent["zustand"], "running")
        self.assertEqual(agent["luecken"], 0)
        # 5. Log und Einstellungen am XDG-Ort, keine Fehler
        log = (state / "AugenUndHaendeBridge" / "bridge.log").read_text()
        self.assertIn("Start", log)
        self.assertIn("linux, Ort kde1", log)
        self.assertNotIn("Fehler in", log, log[-1500:])
        self.assertNotIn("Traceback", log)
        einstellungen = json.loads((config / "AugenUndHaendeBridge" / "einstellungen-kde1.json").read_text())
        self.assertTrue(any(k.startswith("raute:") for k in einstellungen["elemente"]), einstellungen)


class StartskriptTests(unittest.TestCase):
    SKRIPT = WURZEL / "client_vps" / "koerper_linux_starten.sh"

    def lauf(self, *argumente, **env):
        return subprocess.run(["sh", str(self.SKRIPT), *argumente], env=umgebung(**env), capture_output=True, text=True, timeout=60)

    def test_die_syntax_ist_gueltig_und_die_datei_ausfuehrbar(self):
        self.assertEqual(subprocess.run(["sh", "-n", str(self.SKRIPT)]).returncode, 0)
        self.assertTrue(os.access(self.SKRIPT, os.X_OK))

    def test_unbekannte_orte_werden_verweigert(self):
        for ort in ((), ("mars",), ("windows",), ("",)):
            lauf = self.lauf(*ort)
            self.assertEqual(lauf.returncode, 2, ort)
            self.assertIn("Aufruf", lauf.stderr)

    def test_kde1_und_kde2_starten_den_linux_koerper(self):
        for ort in ("kde1", "kde2"):
            lauf = self.lauf(ort, "--version")
            self.assertEqual(lauf.returncode, 0, lauf.stderr[-300:])
            self.assertIn("(Linux)", lauf.stdout)

    def test_die_zugangsdaten_kommen_aus_der_datei_des_orts(self):
        quelle = self.SKRIPT.read_text()
        self.assertIn('runtime/tokens/desktop-$ORT.token', quelle)
        self.assertNotIn("BRIDGE_DESKTOP_TOKEN", quelle, "der Desktop kennt nur sein eigenes Token, nie das eines anderen")


if __name__ == "__main__":
    unittest.main()
