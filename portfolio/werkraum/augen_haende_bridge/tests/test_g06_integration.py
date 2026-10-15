"""G06 als Ganzes: die Nachrichten passen zusammen, Windows- und Linux-Fassung sehen gleich aus, und der Körper wandert zwischen zwei echten Desktops (KDE 1 und KDE 2)."""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ENV = {"BRIDGE_DESKTOP_TOKEN": "w" * 40, "BRIDGE_AGENT_TOKEN": "s" * 40}
PRIVAT = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
WINE_PREFIX = Path("/config/wine-bridge-build/prefix")


def umgebung(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("BRIDGE_BACKEND",)}
    env["PYTHONPATH"] = f"{WURZEL / 'src'}:{WURZEL}"
    env.update(extra)
    return env


class SchnittstellenTests(unittest.TestCase):
    """Jede Nachricht, die der Relay erlaubt, hat auf der Gegenseite jemanden, der sie versteht."""

    def test_der_starter_versteht_jede_desktop_nachricht(self):
        from augen_haende_bridge.transport import DESKTOP_TERMINAL_KINDS

        quelle = (WURZEL / "client_vps" / "terminal_launcher.py").read_text(encoding="utf-8")
        handle = quelle[quelle.index("    def handle(self, event"):quelle.index("    # ---- Anzeigeort und Zielort")]
        vorhanden = set(re.findall(r'^\s*"([a-z_]+)": lambda', handle, re.M))
        self.assertEqual(sorted(DESKTOP_TERMINAL_KINDS - vorhanden - {"frame"}), [], "diese Desktop-Nachrichten würde der Starter ignorieren")
        self.assertIn("frame", vorhanden)

    def test_der_koerper_versteht_jede_nachricht_des_starters(self):
        from augen_haende_bridge.transport import LAUNCHER_TERMINAL_KINDS

        quelle = (WURZEL / "src" / "augen_haende_bridge" / "koerper" / "anwendung.py").read_text(encoding="utf-8")
        tabelle = quelle[quelle.index('"terminal_list": self._terminal_liste'):quelle.index('}.get(ereignis.get("event_kind")')]
        vorhanden = set(re.findall(r'"([a-z_]+)": self\.', tabelle))
        self.assertEqual(sorted(LAUNCHER_TERMINAL_KINDS - vorhanden), [], "diese Nachrichten des Starters würde der Körper ignorieren")

    def test_jede_nachricht_hat_eine_pruefung_im_relay(self):
        from augen_haende_bridge.transport import DESKTOP_TERMINAL_KINDS, LAUNCHER_TERMINAL_KINDS

        quelle = (WURZEL / "src" / "augen_haende_bridge" / "transport.py").read_text(encoding="utf-8")
        pruefung = quelle[quelle.index("def terminal_payload"):quelle.index("def payload(self, conn")]
        for art in sorted(DESKTOP_TERMINAL_KINDS | LAUNCHER_TERMINAL_KINDS):
            # `terminal_list` ist der abschließende Fall ohne eigenen Zweig und steht als Kommentar
            self.assertTrue(f'"{art}"' in pruefung or f"# {art}" in pruefung, f"keine Prüfung für {art}")

    def test_ziel_schluessel_und_scanner_sprechen_dieselbe_sprache(self):
        from augen_haende_bridge.koerper import ziele
        from augen_haende_bridge.windows_scanner import WindowsWindowScanner

        class Api:
            def virtual_screen_rect(self):
                return 0, 0, 10, 10

            def enumerate_windows(self):
                from augen_haende_bridge.windows_scanner import WindowInfo

                return [WindowInfo(77, "t", "c", (0, 0, 5, 5), 1, "/x")]

        for ort in ("windows", "kde1", "kde2"):
            snap = WindowsWindowScanner(Api(), ort=ort).scan(frame_ref="r", frame_hash="h")
            fenster = snap.items[1].target_id
            self.assertEqual((ziele.ort_von(fenster), ziele.fenster_kennung(fenster)), (ort, 77))
            self.assertEqual(snap.default_target_id, f"{ort}:desktop")


@unittest.skipUnless(PRIVAT, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
@unittest.skipUnless(shutil.which("wine") and WINE_PREFIX.exists(), "Wine fehlt")
class ParitaetTests(unittest.TestCase):
    """Dieselben Fenster, einmal mit der Windows-Fensterschicht (GDI unter Wine) und einmal mit der Linux-Fensterschicht (GTK): Größen und Bilder stimmen überein."""

    @classmethod
    def setUpClass(cls):
        from PIL import Image

        cls.Image = Image
        cls.tmp = Path(tempfile.mkdtemp(prefix="par-"))
        win_env = {**os.environ, "WINEPREFIX": str(WINE_PREFIX), "WINEARCH": "win64", "WINEDEBUG": "-all", "WINEDLLOVERRIDES": "mscoree,mshtml=",
                   "PYTHONPATH": "Z:" + str(WURZEL / "src").replace("/", "\\")}
        win_env.pop("BRIDGE_TEST_XVFB", None)
        lauf = subprocess.run(["xvfb-run", "-a", "wine", "C:\\Python313\\python.exe", str(WURZEL / "probes" / "paritaet_fenster.py"), "Z:" + str(cls.tmp / "win").replace("/", "\\")],
                              env=win_env, capture_output=True, text=True, timeout=180)
        assert "paritaet probe ok" in lauf.stdout, lauf.stdout[-800:] + lauf.stderr[-800:]
        lauf = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1280x800x24", sys.executable, str(WURZEL / "probes" / "paritaet_fenster.py"), str(cls.tmp / "lin")],
                              env=umgebung(BRIDGE_BACKEND="linux", BRIDGE_TEST_XVFB="1"), capture_output=True, text=True, timeout=180)
        assert "paritaet probe ok" in lauf.stdout, lauf.stdout[-800:] + lauf.stderr[-800:]
        cls.win = json.loads((cls.tmp / "win" / "groessen.json").read_text())
        cls.lin = json.loads((cls.tmp / "lin" / "groessen.json").read_text())

    def test_beide_fassungen_bauen_dieselben_fenster(self):
        self.assertEqual(sorted(self.win), sorted(self.lin))
        self.assertGreaterEqual(len(self.win), 8)

    def test_die_groessen_stimmen_bis_auf_die_schriftmasse_ueberein(self):
        """Breite und Höhe richten sich nach der Schrift (Segoe UI/Consolas gegen Noto/DejaVu): bis 12 % Abweichung, Fenster ohne Text exakt gleich."""
        for name, (wb, wh) in self.win.items():
            lb, lh = self.lin[name]
            self.assertLessEqual(abs(wb - lb) / max(wb, lb), 0.12, (name, wb, lb))
            self.assertLessEqual(abs(wh - lh) / max(wh, lh), 0.12, (name, wh, lh))
        for name in ("chat", "regie", "kamera", "bild_element"):
            self.assertEqual(self.win[name], self.lin[name], name)

    def test_die_bilder_stimmen_im_wesentlichen_ueberein(self):
        """Pixel mit höchstens 40 Stufen Unterschied zählen als gleich (Schrift ist antialiasing- und schriftabhängig). Gemessen wird nicht erfunden: Schwellen sind Mindestwerte."""
        Image = self.Image
        from PIL import ImageChops

        ergebnisse = {}
        for name in self.win:
            a = Image.open(self.tmp / "win" / f"{name}.png").convert("RGB")
            b = Image.open(self.tmp / "lin" / f"{name}.png").convert("RGB")
            w, h = min(a.size[0], b.size[0]), min(a.size[1], b.size[1])
            unterschied = ImageChops.difference(a.crop((0, 0, w, h)), b.crop((0, 0, w, h))).convert("L")
            ergebnisse[name] = sum(1 for p in unterschied.getdata() if p < 40) / (w * h)
        print("Bildübereinstimmung:", {k: round(v, 3) for k, v in ergebnisse.items()}, file=sys.stderr)
        self.assertGreaterEqual(min(ergebnisse.values()), 0.80, ergebnisse)
        self.assertGreaterEqual(sum(ergebnisse.values()) / len(ergebnisse), 0.92, ergebnisse)


def _ausgabe_leeren(prozess):
    threading.Thread(target=lambda: [None for _ in prozess.stdout], daemon=True).start()


@unittest.skipUnless(PRIVAT and shutil.which("Xvfb"), "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class ZweiKoerperTests(unittest.TestCase):
    """Zwei echte Linux-Körper auf zwei getrennten Bildschirmen (KDE 1 und KDE 2) gegen einen echten Relay: der Körper eines Agenten wandert und nimmt die Sitzung wieder auf."""

    @classmethod
    def setUpClass(cls):
        from test_bridge_server_anzeigeort import freier_port

        cls.tmp = Path(tempfile.mkdtemp(prefix="g06z-"))
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
        _ausgabe_leeren(cls.server)
        cls.prozesse = []

    @classmethod
    def tearDownClass(cls):
        for p in reversed(cls.prozesse):
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
        cls.server.send_signal(signal.SIGTERM)
        try:
            cls.server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            cls.server.kill()

    def xvfb(self):
        lesen, schreiben = os.pipe()
        p = subprocess.Popen(["Xvfb", "-displayfd", str(schreiben), "-screen", "0", "1280x800x24", "-nolisten", "tcp"], pass_fds=(schreiben,),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(schreiben)
        nummer = os.read(lesen, 16).decode().strip()
        os.close(lesen)
        self.prozesse.append(p)
        return f":{nummer}"

    def koerper(self, ort, anzeige, **extra):
        env = umgebung(DISPLAY=anzeige, BRIDGE_URL=f"ws://127.0.0.1:{self.port}", BRIDGE_TOKEN_DATEI=str(self.runtime / "tokens" / f"desktop-{ort}.token"),
                       XDG_CONFIG_HOME=str(self.tmp / f"config-{ort}"), XDG_STATE_HOME=str(self.tmp / f"state-{ort}"), HOME=str(self.tmp), **extra)
        env.pop("BRIDGE_TOKEN", None)
        p = subprocess.Popen(["sh", str(WURZEL / "client_vps" / "koerper_linux_starten.sh"), ort], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        _ausgabe_leeren(p)
        self.prozesse.append(p)
        return p

    def fenster(self, anzeige, pid):
        code = ("import json,sys\nfrom augen_haende_bridge.koerper import linux_adapter as la\n"
                f"print(json.dumps([f.title for f in la.LinuxWindowApi().enumerate_windows() if f.process_id == {pid}]))")
        lauf = subprocess.run([sys.executable, "-c", code], env=umgebung(DISPLAY=anzeige), capture_output=True, text=True, timeout=30)
        try:
            return json.loads(lauf.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return []

    def warte(self, bedingung, sekunden, text):
        t0 = time.monotonic()
        while time.monotonic() - t0 < sekunden:
            wert = bedingung()
            if wert:
                return wert
            time.sleep(0.5)
        raise AssertionError(f"Zeitüberschreitung: {text}")

    def test_der_koerper_wandert_von_kde1_nach_kde2_und_nimmt_die_sitzung_wieder_auf(self):
        a, b = self.xvfb(), self.xvfb()
        berichte = {o: self.tmp / f"bericht-{o}.json" for o in ("kde1", "kde2")}
        k2 = self.koerper("kde2", b, BRIDGE_TEST_BERICHT=str(berichte["kde2"]), BRIDGE_TEST_ENDE_S="75")
        time.sleep(2)
        k1 = self.koerper("kde1", a, BRIDGE_TEST_AUTOSTART="katze", BRIDGE_TEST_TIPPE="hallo-vor-dem-umzug", BRIDGE_TEST_UMZIEHEN="kde2@18",
                          BRIDGE_TEST_BERICHT=str(berichte["kde1"]), BRIDGE_TEST_ENDE_S="60")
        # erst auf KDE 1: Raute und Terminal dort, auf KDE 2 noch nichts von dem Agenten
        self.warte(lambda: any("Katze" in t for t in self.fenster(a, k1.pid)), 40, "Katze erscheint nicht auf KDE 1")
        self.assertFalse(any("Katze" in t for t in self.fenster(b, k2.pid)), "auf KDE 2 gibt es den Agenten noch nicht")
        # dann auf KDE 2: der Körper ist umgezogen
        titel_b = self.warte(lambda: [t for t in self.fenster(b, k2.pid) if "Katze" in t] if len([t for t in self.fenster(b, k2.pid) if "Katze" in t]) >= 2 else None, 60,
                             "der Körper erscheint nicht auf KDE 2")
        self.warte(lambda: not any("Katze" in t for t in self.fenster(a, k1.pid)), 20, "der Körper verschwindet nicht von KDE 1")
        self.assertTrue(any("· Host" in t for t in titel_b), titel_b)
        for p in (k1, k2):
            p.wait(timeout=100)
            self.assertEqual(p.returncode, 0)
        r1, r2 = (json.loads(berichte[o].read_text()) for o in ("kde1", "kde2"))
        self.assertEqual(r1["agenten"], [], "KDE 1 hat den Agenten abgegeben")
        agent = next(x for x in r2["agenten"] if x["name"] == "Katze")
        self.assertEqual(agent["zustand"], "running")
        self.assertIn("hallo-vor-dem-umzug", "\n".join(agent["terminal_text"]), "die Wiederaufnahme zeigt den Verlauf von vorher")
        for ort in ("kde1", "kde2"):
            log = (self.tmp / f"state-{ort}" / "AugenUndHaendeBridge" / "bridge.log").read_text()
            self.assertNotIn("Fehler in", log, (ort, log[-1200:]))
            self.assertNotIn("Traceback", log)


if __name__ == "__main__":
    unittest.main()
