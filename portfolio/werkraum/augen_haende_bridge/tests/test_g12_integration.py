"""G12 mit allem Echten: Relay-Prozess, Starter mit Ablauf-Dienst, zwei Agenten-Attrappen mit dem echten Werkzeug, ein Desktop als Daniel (Freigaben, Regiesprüche, Steuerung)."""

from __future__ import annotations

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
from tests.test_bridge_server_anzeigeort import ENV, WURZEL, Desktop, freier_port

SKRIPT = '#!/bin/sh\necho "ID=$BRIDGE_TERMINAL_ID TOKEN=$BRIDGE_TERMINAL_TOKEN RT=$BRIDGE_RUNTIME_DIR"\nexec cat\n'


class G12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="g12-"))
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

    def cli(self, zugang, tid, *argv):
        env = {**os.environ, "BRIDGE_TERMINAL_ID": tid, "BRIDGE_TERMINAL_TOKEN": zugang[tid], "BRIDGE_RUNTIME_DIR": str(self.runtime)}
        lauf = subprocess.run([sys.executable, str(WURZEL / "client_vps" / "bridge_cli.py"), *argv], env=env, capture_output=True, text=True, timeout=90)
        return lauf.returncode, json.loads(lauf.stdout)

    def warte_bis(self, bedingung, s=15.0, was=""):
        ende = time.monotonic() + s
        while time.monotonic() < ende:
            w = bedingung()
            if w:
                return w
            time.sleep(0.05)
        self.fail(f"Zeit abgelaufen: {was}")

    def stand(self):
        liste = self.d["kde1"].liste("ablauf_stand")
        return liste[-1] if liste else {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": []}

    def lauf_status(self, lauf_id):
        return next((l["status"] for l in self.stand()["laeufe"] if l["id"] == lauf_id), None)

    def test_ablauf(self):
        k1 = self.d["kde1"]
        k1.senden("anzeigeorte_request", {})
        k1.warte("anzeigeorte")
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})
        a = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "codex")["terminal_id"]
        k1.senden("terminal_start", {"start_id": "claude", "rows": 24, "cols": 80})
        b = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "claude")["terminal_id"]
        self.warte_bis(lambda: len(re.findall(rb"TOKEN=\S+", k1.ausgabe())) >= 2, 10, "Attrappen melden sich")
        zugang = {m.group(1): m.group(2) for m in re.finditer(r"ID=(\S+) TOKEN=(\S+) RT=\S+", k1.ausgabe().decode("utf-8", "replace"))}

        # 1. Ein Agent entwirft einen Ablauf, speichert ihn (Version bleibt sichtbar) und führt ihn aus; Teilauftrag an den zweiten mit Zustand und Unsicherheit
        teilen = {"id": "teilen", "name": "Teilen", "start": "z", "knoten": {
            "z": {"art": "zustand", "setze": {"phase": "vorbereitet"}, "unsicherheit": "unklar, ob die Tests laufen"},
            "d": {"art": "delegieren", "an": "Claude", "text": "Prüfe die Tests", "warte_s": 30, "nachher": [{"pfad": "d.auftrag.status", "gleich": "fertig"}]},
            "ende": {"art": "zustand", "setze": {"ergebnis": "da"}}}, "kanten": [{"von": "z", "nach": "d", "wenn": "ok"}, {"von": "d", "nach": "ende", "wenn": "ok"}]}
        datei = self.tmp / "teilen.json"
        datei.write_text(json.dumps(teilen))
        code, r = self.cli(zugang, a, "ablauf", "neu", str(datei))
        self.assertEqual((code, r["version"]), (0, 1))
        datei.write_text(json.dumps({**teilen, "name": "Teilen v2"}))
        self.assertEqual(self.cli(zugang, a, "ablauf", "neu", str(datei))[1]["versionen"], [1, 2], "die erste Version bleibt")
        self.assertEqual(self.cli(zugang, b, "ablauf", "zeige", "teilen", "1")[1]["ablauf"]["name"], "Teilen", "auch der andere Agent sieht Version 1")
        code, r = self.cli(zugang, a, "ablauf", "start", "teilen", "--modi=witness")
        self.assertEqual((code, r["ok"]), (0, True), r)
        lauf = r["lauf"]
        self.warte_bis(lambda: b"Pr\xc3\xbcfe die Tests" in k1.ausgabe() and f"Lauf {lauf}".encode() in k1.ausgabe(), 15, "der Auftrag kommt beim Empfänger an, mit Lauf-Kennung")
        ausgabe = k1.ausgabe().decode("utf-8", "replace")
        self.assertIn("vorbereitet", ausgabe, "der Zustand geht mit")
        self.assertIn("unklar, ob die Tests laufen", ausgabe, "die Unsicherheit geht mit")
        aid = self.cli(zugang, b, "auftraege")[1]["erhalten"][0]["id"]
        self.assertEqual(self.cli(zugang, a, "ablauf", "status", lauf)[1]["lauf"]["status"], "running", "solange der Empfänger nichts meldet, gilt nichts als fertig")
        self.cli(zugang, b, "auftrag-status", aid, "angenommen")
        self.cli(zugang, b, "auftrag-status", aid, "fertig", "alles grün", "ein Test übersprungen")
        self.warte_bis(lambda: self.cli(zugang, a, "ablauf", "status", lauf)[1]["lauf"]["status"] == "completed", 15, "Lauf endet, sobald der Empfänger fertig meldet")
        s = self.cli(zugang, a, "ablauf", "status", lauf)[1]["lauf"]
        self.assertEqual((s["zustand"], s["ctx"]["d"]["auftrag"]["ergebnis"], s["ablauf_version"]), ({"phase": "vorbereitet", "ergebnis": "da"}, "alles grün", 2))
        self.assertIn("ein Test übersprungen", [u["text"] for u in s["unsicherheit"]])
        self.assertEqual(self.cli(zugang, b, "ablauf", "status", lauf)[1]["reason"], "nicht_dein_lauf")
        spur = self.cli(zugang, a, "ablauf", "replay", lauf)[1]
        self.assertEqual([e["knoten"] for e in spur["spur"]], ["z", "d", "ende"])

        # 2. Daniel-Gate: nichts geschieht vor der Freigabe, Nein führt nichts aus, Ja führt aus
        gruss = {"id": "gruss", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Claude", "text": "freigegebener Gruss"}}}, "kanten": []}
        datei.write_text(json.dumps(gruss))
        self.cli(zugang, a, "ablauf", "neu", str(datei))
        k1.senden("ablauf_steuern", {"aktion": "start", "terminal_id": a, "ablauf_id": "gruss", "modi": ["daniel_gate"]})
        offen = self.warte_bis(lambda: self.stand()["offen"], 10, "die Frage an Daniel")[0]
        self.assertEqual(self.stand()["offen"][0]["knoten"], "n")
        time.sleep(0.5)
        self.assertNotIn(b"freigegebener Gruss", k1.ausgabe(), "vor der Antwort geschieht nichts")
        k1.senden("ablauf_steuern", {"aktion": "verweigern", "frage_id": offen["id"]})
        self.warte_bis(lambda: not self.stand()["offen"], 10, "Frage beantwortet")
        time.sleep(0.8)
        self.assertNotIn(b"freigegebener Gruss", k1.ausgabe(), "Nein führt nichts aus")
        k1.senden("ablauf_steuern", {"aktion": "start", "terminal_id": a, "ablauf_id": "gruss", "modi": ["daniel_gate"]})
        offen = self.warte_bis(lambda: self.stand()["offen"], 10, "zweite Frage")[0]
        k1.senden("ablauf_steuern", {"aktion": "freigeben", "frage_id": offen["id"]})
        self.warte_bis(lambda: b"freigegebener Gruss" in k1.ausgabe(), 15, "Ja führt aus")

        # 3. Shadow: der Lauf geht durch, es wird nichts zugestellt
        time.sleep(1.0)  # Echo des Terminals und Antwort von cat sind zwei Ausgaben derselben Zustellung: erst zur Ruhe kommen lassen
        vorher = k1.ausgabe().count(b"freigegebener Gruss")
        code, r = self.cli(zugang, a, "ablauf", "start", "gruss", "--modi=shadow", "--warten")
        self.assertTrue(r["ok"])
        self.warte_bis(lambda: self.cli(zugang, a, "ablauf", "status", r["lauf"])[1]["lauf"]["status"] == "completed", 10, "Shadow-Lauf fertig")
        time.sleep(0.8)
        self.assertEqual(k1.ausgabe().count(b"freigegebener Gruss"), vorher, "Shadow führt nichts aus")
        self.assertTrue(self.cli(zugang, a, "ablauf", "status", r["lauf"])[1]["lauf"]["verlauf"][0]["simuliert"])

        # 4. Regiesprüche: Pause wirkt auf den Ablauf, Denk nach ist ein Gespräch, Weiter setzt fort
        langsam = {"id": "langsam", "start": "w1", "knoten": {"w1": {"art": "warten", "sekunden": 2}, "w2": {"art": "zustand", "setze": {"fertig": True}}}, "kanten": [{"von": "w1", "nach": "w2", "wenn": "ok"}]}
        datei.write_text(json.dumps(langsam))
        self.cli(zugang, a, "ablauf", "neu", str(datei))
        r = self.cli(zugang, a, "ablauf", "start", "langsam")[1]
        lauf2 = r["lauf"]
        k1.senden("regie_spruch", {"terminal_id": a, "spruch": "Denk nach"})
        e = k1.warte("regie_ergebnis", lambda p: p["spruch"] == "Denk nach")
        self.assertEqual((e["wirkung"], e["zugestellt"]), ("gespraech", True))
        self.assertEqual(self.cli(zugang, a, "ablauf", "status", lauf2)[1]["lauf"]["status"], "running", "Denk nach stoppt nichts")
        k1.senden("regie_spruch", {"terminal_id": a, "spruch": "Pause"})
        e = k1.warte("regie_ergebnis", lambda p: p["spruch"] == "Pause")
        self.assertEqual((e["wirkung"], e["aktion"]), ("echt", "ablauf_pausiert"))
        self.warte_bis(lambda: self.cli(zugang, a, "ablauf", "status", lauf2)[1]["lauf"]["status"] == "paused", 10, "Ablauf pausiert")
        self.assertEqual(self.cli(zugang, a, "ablauf", "status", lauf2)[1]["lauf"]["zustand"], {}, "der nächste Knoten wurde nicht betreten")
        k1.senden("regie_spruch", {"terminal_id": a, "spruch": "Weiter"})
        e = k1.warte("regie_ergebnis", lambda p: p["spruch"] == "Weiter")
        self.assertEqual(e["aktion"], "ablauf_fortgesetzt")
        self.warte_bis(lambda: self.cli(zugang, a, "ablauf", "status", lauf2)[1]["lauf"]["status"] == "completed", 10, "Ablauf fertig")
        self.assertEqual(self.cli(zugang, a, "ablauf", "status", lauf2)[1]["lauf"]["zustand"], {"fertig": True})

        # 5. Lernen: nur Daniel
        code, r = self.cli(zugang, a, "ablauf", "start", "langsam", "--modi=learning")
        self.assertEqual(r["reason"], "lernen_ist_aus")
        k1.senden("ablauf_steuern", {"aktion": "lernen", "an": True})
        self.warte_bis(lambda: self.stand()["lernen"], 5, "Lernen an")
        self.assertTrue(self.cli(zugang, a, "ablauf", "start", "langsam", "--modi=learning")[1]["ok"])
        self.warte_bis(lambda: (self.runtime / "ablauf" / "lernen.jsonl").exists(), 10, "Erfahrung aufgezeichnet")

        for t in (a, b):
            k1.senden("terminal_close", {"terminal_id": t})


if __name__ == "__main__":
    unittest.main()
