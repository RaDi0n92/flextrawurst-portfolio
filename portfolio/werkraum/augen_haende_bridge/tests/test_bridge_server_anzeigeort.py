"""G06 mit allem Echten: Relay-Prozess, Starter, PTY-Sitzung und drei verbundene Desktops (Windows, KDE 1, KDE 2) über dieselbe Laufzeit wie der Körper."""

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

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from client_vps import anzeigeorte as ao

WURZEL = Path(__file__).resolve().parent.parent
ENV = {"BRIDGE_DESKTOP_TOKEN": "w" * 40, "BRIDGE_AGENT_TOKEN": "s" * 40}
JPEG = b"\xff\xd8\xff\xe0" + b"JFIF-Testbild" * 4


def freier_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Desktop:
    """Ein verbundener Körper-Ersatz: dieselbe Laufzeit (BridgeRuntime), Ereignisse werden gesammelt."""

    def __init__(self, url: str, token: str, ort: str):
        self.ort, self.events, self._sperre = ort, [], threading.Lock()
        self.runtime = BridgeRuntime(url, token, on_event=self._merken)

    def _merken(self, ereignis: dict) -> None:
        with self._sperre:
            self.events.append(ereignis)

    def start(self):
        self.runtime.start()
        t0 = time.monotonic()
        while not self.runtime.connected and time.monotonic() - t0 < 10:
            time.sleep(0.05)
        assert self.runtime.connected, f"{self.ort} nicht verbunden: {self.runtime.failure!r}"

    def senden(self, art: str, nutzlast: dict) -> None:
        self.runtime.publish(art, nutzlast)

    def liste(self, art: str) -> list[dict]:
        with self._sperre:
            return [e["payload"] for e in self.events if e.get("kind") == "event" and e.get("event_kind") == art]

    def warte(self, art: str, bedingung=lambda p: True, sekunden=8.0) -> dict:
        t0 = time.monotonic()
        while time.monotonic() - t0 < sekunden:
            for p in self.liste(art):
                if bedingung(p):
                    return p
            time.sleep(0.03)
        raise AssertionError(f"{self.ort}: kein {art} mit Bedingung; gesehen: {self.liste(art)[-3:]}")

    def ausgabe(self) -> bytes:
        return b"".join(base64.b64decode(p["data"]) for p in self.liste("terminal_output"))

    def stop(self):
        self.runtime.stop()


class EndeZuEndeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="g06-"))
        cls.runtime = cls.tmp / "runtime"
        (cls.tmp / "starts.json").write_text(json.dumps({"starts": [{"start_id": "katze", "name": "Katze", "ort": "Host", "ordner": "/tmp", "programm": "cat", "bestaetigt": True}]}))
        (cls.tmp / "orte.json").write_text(json.dumps({"orte": {"Host": {"kind": "host"}}}))
        (cls.tmp / "desktops.json").write_text((WURZEL / "client_vps" / "desktops.json").read_text())
        cls.port = freier_port()
        env = {**os.environ, **ENV, "BRIDGE_SPRACHERKENNUNG": "aus", "PYTHONPATH": f"{WURZEL / 'src'}:{WURZEL}"}
        cls.server = subprocess.Popen([sys.executable, str(WURZEL / "client_vps" / "bridge_server.py"), "--port", str(cls.port), "--journal", str(cls.tmp / "j.sqlite3"),
                                       "--starts", str(cls.tmp / "starts.json"), "--orte", str(cls.tmp / "orte.json"), "--runtime-dir", str(cls.runtime),
                                       "--desktops", str(cls.tmp / "desktops.json")], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        zeile = ""
        t0 = time.monotonic()
        while "Bridge relay ready" not in zeile and time.monotonic() - t0 < 30:
            zeile = cls.server.stdout.readline()
            if not zeile and cls.server.poll() is not None:
                raise RuntimeError("Relay ist nicht gestartet")
        assert "3 desktop(s)" in zeile, zeile
        threading.Thread(target=lambda: [None for _ in cls.server.stdout], daemon=True).start()  # Ausgabe leeren, damit der Prozess nie blockiert
        desktops = ao.lade_desktops(cls.tmp / "desktops.json", cls.runtime, ENV)
        cls.d = {x.ort: Desktop(f"ws://127.0.0.1:{cls.port}", x.token, x.ort) for x in desktops}
        for d in cls.d.values():
            d.start()

    @classmethod
    def tearDownClass(cls):
        for d in cls.d.values():
            d.stop()
        cls.server.send_signal(signal.SIGTERM)
        try:
            cls.server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            cls.server.kill()

    def test_ablauf_start_ausgabe_umzug_wiederaufnahme_eingabe_ziel_beenden(self):
        win, k1, k2 = self.d["windows"], self.d["kde1"], self.d["kde2"]
        for d in (win, k1, k2):
            d.senden("anzeigeorte_request", {})
        for d in (win, k1, k2):
            orte = d.warte("anzeigeorte")["orte"]
            self.assertEqual([(o["ort"], o["online"]) for o in orte], [("windows", True), ("kde1", True), ("kde2", True)])

        # Start auf KDE 1: nur KDE 1 sieht das Terminal
        k1.senden("terminal_start", {"start_id": "katze", "rows": 24, "cols": 80})
        tid = k1.warte("terminal_state", lambda p: p["state"] == "running")["terminal_id"]
        k1.senden("terminal_input", {"terminal_id": tid, "data": base64.b64encode(b"hallo-vor-dem-umzug\n").decode()})
        t0 = time.monotonic()
        while b"hallo-vor-dem-umzug" not in k1.ausgabe() and time.monotonic() - t0 < 8:
            time.sleep(0.05)
        self.assertIn(b"hallo-vor-dem-umzug", k1.ausgabe())
        self.assertEqual((win.liste("terminal_state"), win.liste("terminal_output")), ([], []), "Windows zeigt dieses Terminal nicht")

        # Eingabe von einem Desktop, der das Terminal nicht zeigt: wirkungslos
        win.senden("terminal_input", {"terminal_id": tid, "data": base64.b64encode(b"FREMDE-EINGABE\n").decode()})
        time.sleep(0.6)
        self.assertNotIn(b"FREMDE-EINGABE", k1.ausgabe() + win.ausgabe())

        # Frames: das Ziel folgt dem Anzeigeort (KDE 1); Windows darf nichts unterschieben, KDE 1 schon
        def bild(nr):
            return {"mime": "image/jpeg", "data": base64.b64encode(JPEG + bytes([nr])).decode(), "source": "capture", "captured_at_ms": 5000 + nr, "width": 16, "height": 16,
                    "terminal_id": tid}
        win.senden("frame", bild(1))
        k1.senden("frame", bild(2))
        meta = self.runtime / "frames" / tid / "latest.json"
        t0 = time.monotonic()
        while not meta.exists() and time.monotonic() - t0 < 8:
            time.sleep(0.05)
        self.assertEqual(json.loads(meta.read_text())["captured_at_ms"], 5002, "nur das Bild vom Zielort (KDE 1) gilt")

        # Umzug auf Windows
        k1.senden("terminal_umziehen", {"terminal_id": tid, "ort": "windows"})
        neu = win.warte("terminal_ort", lambda p: p["aktiv"])
        alt = k1.warte("terminal_ort", lambda p: not p["aktiv"] and p["anzeigeort"] == "windows")
        self.assertEqual((neu["anzeigeort"], neu["zielort"], neu["laufort"]), ("windows", "windows", "Host"))
        liste = win.warte("terminal_list", lambda p: any(t["terminal_id"] == tid for t in p["terminals"]))
        sitzung = next(t for t in liste["terminals"] if t["terminal_id"] == tid)
        self.assertEqual((alt["pid"], alt["gestartet"]), (sitzung["pid"], sitzung["gestartet"]), "dieselbe Sitzung")
        win.senden("terminal_attach", {"terminal_id": tid})
        wieder = win.warte("terminal_output", lambda p: p.get("replay") is True)
        self.assertIn(b"hallo-vor-dem-umzug", base64.b64decode(wieder["data"]) + win.ausgabe(), "die Wiederaufnahme spielt den Verlauf noch einmal")

        # Eingabe jetzt von Windows; KDE 1 hört nichts mehr
        k1_vorher = len(k1.liste("terminal_output"))
        win.senden("terminal_input", {"terminal_id": tid, "data": base64.b64encode(b"hallo-nach-dem-umzug\n").decode()})
        t0 = time.monotonic()
        while b"hallo-nach-dem-umzug" not in win.ausgabe() and time.monotonic() - t0 < 8:
            time.sleep(0.05)
        self.assertIn(b"hallo-nach-dem-umzug", win.ausgabe())
        self.assertEqual(len(k1.liste("terminal_output")), k1_vorher, "der alte Desktop bekommt nichts mehr")

        # Ziel unabhängig: Körper bleibt auf Windows, Ziel auf KDE 2
        win.senden("terminal_ziel", {"terminal_id": tid, "ort": "kde2"})
        z = k2.warte("terminal_ort", lambda p: p["zielort"] == "kde2")
        self.assertFalse(z["aktiv"], "KDE 2 ist nur Ziel, nicht Anzeigeort")
        win.senden("frame", bild(3))
        k2.senden("frame", bild(4))
        time.sleep(0.8)
        self.assertEqual(json.loads(meta.read_text())["captured_at_ms"], 5004)
        k2.senden("ziel_zustand", {"terminal_id": tid, "target_id": "kde2:window:77", "zustand": "verdeckt", "faehigkeit": "frisch", "seit_ms": 1})
        m = win.warte("terminal_ort", lambda p: p["ziel"]["zustand"] == "verdeckt")
        self.assertEqual((m["anzeigeort"], m["zielort"], m["ziel"]["target_id"]), ("windows", "kde2", "kde2:window:77"))

        # Beenden nur vom Anzeigeort
        k1.senden("terminal_close", {"terminal_id": tid})
        time.sleep(0.5)
        self.assertFalse(any(p["state"] == "exited" for p in win.liste("terminal_state")))
        win.senden("terminal_close", {"terminal_id": tid})
        win.warte("terminal_state", lambda p: p["state"] == "exited")


if __name__ == "__main__":
    unittest.main()
