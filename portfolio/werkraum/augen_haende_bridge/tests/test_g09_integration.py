"""G09 mit allem Echten: Relay-Prozess, Starter, zwei Agenten-Attrappen in echten PTY-Sitzungen, Desktops KDE 1 und Windows. Pause, Wiederaufnahme statt Neustart, Agent-zu-Agent-Zustellung über den echten Sprech-Socket."""

from __future__ import annotations

import base64
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from client_vps import anzeigeorte as ao
from client_vps import bridge_cli
from tests.test_bridge_server_anzeigeort import ENV, WURZEL, Desktop, freier_port

SKRIPT = '#!/bin/sh\necho "ID=$BRIDGE_TERMINAL_ID TOKEN=$BRIDGE_TERMINAL_TOKEN RT=$BRIDGE_RUNTIME_DIR"\nexec cat\n'


def zustand_von(pid: int) -> str:
    return Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()[0]


class G09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="g09-"))
        cls.runtime = cls.tmp / "runtime"
        starts = []
        for name in ("codex", "claude"):
            pfad = cls.tmp / name
            pfad.write_text(SKRIPT)
            pfad.chmod(pfad.stat().st_mode | stat.S_IXUSR)
            starts.append({"start_id": name, "name": name.capitalize(), "ort": "Host", "ordner": "/tmp", "programm": str(pfad), "bestaetigt": True})
        (cls.tmp / "starts.json").write_text(json.dumps({"starts": starts}))
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

    def warte_bis(self, bedingung, sekunden=10.0, was=""):
        t0 = time.monotonic()
        while time.monotonic() - t0 < sekunden:
            if bedingung():
                return
            time.sleep(0.05)
        self.fail(f"Zeit abgelaufen: {was}")

    def test_ablauf(self):
        win, k1 = self.d["windows"], self.d["kde1"]
        for d in (win, k1):
            d.senden("anzeigeorte_request", {})
            d.warte("anzeigeorte")
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})
        a = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "codex")["terminal_id"]
        k1.senden("terminal_start", {"start_id": "claude", "rows": 24, "cols": 80})
        c = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "claude")["terminal_id"]
        self.assertNotEqual(a, c)
        self.warte_bis(lambda: len(re.findall(rb"TOKEN=\S+", k1.ausgabe())) >= 2, was="beide Attrappen melden sich")
        ausgabe = k1.ausgabe().decode("utf-8", "replace")
        zugang = {m.group(1): m.group(2) for m in re.finditer(r"ID=(\S+) TOKEN=(\S+) RT=\S+", ausgabe)}
        self.assertEqual(set(zugang), {a, c})

        # Pause und Fortsetzen nur vom Anzeigeort
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})  # ein zweiter Codex: derselbe Strom, ein anderer Agent
        a2 = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["terminal_id"] not in (a, c))["terminal_id"]
        k1.senden("terminal_list_request", {})
        liste = k1.warte("terminal_list", lambda p: {a, c, a2} <= {t["terminal_id"] for t in p["terminals"]})
        pid_a = next(t["pid"] for t in liste["terminals"] if t["terminal_id"] == a)
        win.senden("terminal_steuern", {"terminal_id": a, "aktion": "pause"})  # Windows zeigt dieses Terminal nicht: wirkungslos
        time.sleep(0.6)
        self.assertNotEqual(zustand_von(pid_a), "T")
        k1.senden("terminal_steuern", {"terminal_id": a, "aktion": "pause"})
        k1.warte("terminal_state", lambda p: p["terminal_id"] == a and p["state"] == "paused")
        self.warte_bis(lambda: zustand_von(pid_a) == "T", was="Prozess angehalten")
        k1.senden("terminal_list_request", {})
        self.assertEqual(next(t["state"] for t in k1.warte("terminal_list", lambda p: any(t["terminal_id"] == a and t["state"] == "paused" for t in p["terminals"]))["terminals"] if t["terminal_id"] == a), "paused")

        # Anbinden statt Neustart: eine laufende (hier: pausierte) Sitzung wiederaufnehmen startet keine neue
        k1.senden("terminal_attach", {"terminal_id": a})
        k1.warte("terminal_output", lambda p: p["terminal_id"] == a and p.get("replay") is True)
        k1.senden("terminal_list_request", {})
        time.sleep(0.5)
        letzte = [p for p in k1.liste("terminal_list")][-1]
        self.assertEqual(sorted(t["terminal_id"] for t in letzte["terminals"]), sorted([a, c, a2]), "Anbinden hat keine vierte Sitzung erzeugt")

        k1.senden("terminal_steuern", {"terminal_id": a, "aktion": "fortsetzen"})
        k1.warte("terminal_state", lambda p: p["terminal_id"] == a and p["state"] == "running", 10)
        self.warte_bis(lambda: zustand_von(pid_a) != "T", was="Prozess läuft wieder")

        # Agent-zu-Agent über den echten Sprech-Socket: Claude bekommt, was Codex ihm schickt — auch nach einem Umzug auf einen anderen Desktop
        def agent(tid):
            return {"BRIDGE_TERMINAL_ID": tid, "BRIDGE_TERMINAL_TOKEN": zugang[tid], "BRIDGE_RUNTIME_DIR": str(self.runtime)}

        antwort = bridge_cli.ask({"cmd": "agenten"}, agent(a))
        namen = {x["terminal_id"]: x["name"] for x in antwort["agenten"]}
        self.assertEqual((namen[a], namen[a2], namen[c]), ("Codex", "Codex 2", "Claude"), "zwei Codex bleiben zwei Agenten")
        k1.senden("terminal_umziehen", {"terminal_id": c, "ort": "windows"})
        win.warte("terminal_ort", lambda p: p["aktiv"] and p["terminal_id"] == c)
        r = bridge_cli.ask({"cmd": "nachricht", "an": "Claude", "text": "Prüfe die Tests bitte"}, agent(a))
        self.assertEqual((r["ok"], r["zugestellt"]), (True, ["Claude"]))
        self.warte_bis(lambda: b"[Bridge \xc2\xb7 von Codex] Pr\xc3\xbcfe die Tests bitte" in win.ausgabe(), was="die Nachricht kommt auf dem neuen Anzeigeort an")
        auftrag = bridge_cli.ask({"cmd": "auftrag", "an": "Claude", "text": "Mach es fertig"}, agent(a))["auftrag"]
        self.warte_bis(lambda: f"Auftrag {auftrag['id']}".encode() in win.ausgabe(), was="Auftrag im Empfänger")
        self.assertFalse(bridge_cli.ask({"cmd": "auftrag_status", "id": auftrag["id"], "status": "fertig"}, agent(a))["ok"])
        self.assertTrue(bridge_cli.ask({"cmd": "auftrag_status", "id": auftrag["id"], "status": "fertig", "ergebnis": "ok"}, agent(c))["ok"])

        # Beenden eines pausierten Agenten
        k1.senden("terminal_steuern", {"terminal_id": a2, "aktion": "pause"})
        k1.warte("terminal_state", lambda p: p["terminal_id"] == a2 and p["state"] == "paused")
        k1.senden("terminal_close", {"terminal_id": a2})
        k1.warte("terminal_state", lambda p: p["terminal_id"] == a2 and p["state"] == "exited", 15)
        for t in (a, c):
            (k1 if t == a else win).senden("terminal_close", {"terminal_id": t})


if __name__ == "__main__":
    unittest.main()
