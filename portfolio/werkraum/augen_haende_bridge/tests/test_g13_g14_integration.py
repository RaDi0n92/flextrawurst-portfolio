"""G13/G14 mit allem Echten: Relay, Starter mit Kapsel-Dienst, zwei Agenten-Attrappen mit dem echten Werkzeug; Protokoll, Kapseln, Scrubber, Mischpult und Beobachtung (Fake-Modell auf freiem Port)."""

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
from tests.test_hauhaucs import FakeServer
from tests.test_bridge_server_anzeigeort import ENV, WURZEL, Desktop, freier_port

SKRIPT = '#!/bin/sh\necho "ID=$BRIDGE_TERMINAL_ID TOKEN=$BRIDGE_TERMINAL_TOKEN RT=$BRIDGE_RUNTIME_DIR"\nexec cat\n'


class G13G14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="g13-"))
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
        cls.modell = FakeServer(antwort="Codex schickte eine Nachricht an Claude.")
        env = {**os.environ, **ENV, "BRIDGE_SPRACHERKENNUNG": "aus", "PYTHONPATH": f"{WURZEL / 'src'}:{WURZEL}", "BRIDGE_CHAT_URL": cls.modell.url}
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
        cls.modell.schliessen()
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

    def test_g13_g14(self):
        k1 = self.d["kde1"]
        k1.senden("anzeigeorte_request", {})
        k1.warte("anzeigeorte")
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})
        a = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "codex")["terminal_id"]
        k1.senden("terminal_start", {"start_id": "claude", "rows": 24, "cols": 80})
        b = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "claude")["terminal_id"]
        self.warte_bis(lambda: len(re.findall(rb"TOKEN=\S+", k1.ausgabe())) >= 2, 10, "Attrappen melden sich")
        zugang = {m.group(1): m.group(2) for m in re.finditer(r"ID=(\S+) TOKEN=(\S+) RT=\S+", k1.ausgabe().decode("utf-8", "replace"))}

        # Beobachtung ohne Modell: aufzeichnen und zustellen
        code, r = self.cli(zugang, a, "beobachtung", "start", "Codex", "Claude")
        self.assertEqual((code, r["ok"], r["aktiv"]), (0, True, True), r)
        self.assertEqual(self.cli(zugang, a, "beobachtung", "start", "Codex", "Gemini")[1]["reason"], "agent_unbekannt:Gemini", "ein unbekannter Name startet nichts")
        self.cli(zugang, a, "sende", "Claude", "hallo vom Test")
        r = self.warte_bis(lambda: (lambda x: x if x["agenten"][0]["aufgezeichnet"] >= 1 else None)(self.cli(zugang, a, "beobachtung", "status")[1]), 10, "Ereignis aufgezeichnet")
        z = r["agenten"][0]
        self.assertEqual((z["zugestellt"], z["verarbeitet"]), (0, 0))
        self.assertEqual(self.modell.anfragen, [], "kein Modellaufruf nur durch Aufzeichnen")
        self.assertGreaterEqual(self.cli(zugang, a, "beobachtung", "zustellen")[1]["zugestellt"], 1)
        self.assertIn("hallo vom Test", json.dumps(self.cli(zugang, a, "pult", "zeige")[1]["vorschau"]))

        # Kapsel: unverändert, mit benannten Lücken (Körper/WorldDOM liefern in dieser Umgebung keine Daten)
        code, r = self.cli(zugang, a, "kapsel", "moment", "--art=agent", "Test-Moment")
        self.assertEqual((code, r["ok"]), (0, True), r)
        kid = r["kapsel"]
        self.assertTrue(any("koerper" in l["feld"] for l in r["luecken"]), r["luecken"])
        z = self.cli(zugang, a, "kapsel", "zeige", kid)[1]
        self.assertTrue(z["kapsel"]["unveraendert"])
        e = self.cli(zugang, a, "kapsel", "ebene", kid, "kommentar", "Beinahe geklappt")[1]
        self.assertTrue(e["ok"], e)
        self.assertEqual(self.cli(zugang, a, "kapsel", "zeige", kid)[1]["kapsel"]["unveraendert"], True, "eine Ebene verändert das Original nicht")
        self.assertEqual(len(self.cli(zugang, a, "kapsel", "liste")[1]["kapseln"]), 1)
        self.assertFalse(self.cli(zugang, a, "kapsel", "zeige", "k-gibtsnicht")[1]["ok"])

        # Scrubber: nur lesen
        self.warte_bis(lambda: k1.ausgabe().count(b"hallo vom Test") >= 2, 10, "die Zustellung ist im Terminal angekommen (Echo)")
        time.sleep(0.5)
        vorher = k1.ausgabe()
        zl = self.cli(zugang, a, "kapsel", "zeitlinie")[1]
        self.assertTrue(zl["ok"] and zl["marken"] and zl["wirkung_auf_anwendung"] is False)
        s = self.cli(zugang, a, "kapsel", "zeitlinie", str(zl["marken"][-1]))[1]
        self.assertTrue(s["ok"], s)
        time.sleep(0.3)
        self.assertEqual(k1.ausgabe(), vorher, "Scrubben schickt nichts ans Terminal")

        # Hauhaucs: erst auf Wort ein Modellaufruf, mit geprüften Quellen
        r = self.cli(zugang, a, "beobachtung", "jetzt", "Fasse zusammen")[1]
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(self.modell.anfragen), 1)
        self.assertIn("Fasse zusammen", json.dumps(self.modell.anfragen[0]["messages"]))
        self.assertTrue(r["ohne_quellenbezug"] or r["quellen"] is not None)
        z = self.cli(zugang, a, "beobachtung", "status")[1]["agenten"][0]
        self.assertGreaterEqual(z["verarbeitet"], 1)
        self.assertEqual(self.cli(zugang, a, "beobachtung", "jetzt", "--bilder")[1].get("reason"), "bilder_nicht_zugeschaltet")

        # G15: ein Seed wird vorgeschlagen, Daniel sagt über seine Oberfläche Ja, er wird zugestellt, Daniel zieht ihn zurück
        r = self.cli(zugang, a, "seed", "vorschlagen", "kontext", "Hinweis", "--inhalt=Bitte zuerst messen.", "--an=Claude")[1]
        self.assertEqual((r["ok"], r["status"]), (True, "vorschlag"), r)
        sid = r["seed"]
        erg = {}
        faden = threading.Thread(target=lambda: erg.update(r=self.cli(zugang, a, "seed", "ausliefern", sid)))
        faden.start()

        def offene_frage():
            liste = k1.liste("ablauf_stand")
            return liste[-1]["offen"][0]["id"] if liste and liste[-1].get("offen") else None

        frage = self.warte_bis(offene_frage, 15, "Daniels offene Frage")
        k1.senden("ablauf_steuern", {"aktion": "freigeben", "frage_id": frage})
        faden.join(30)
        self.assertEqual((erg["r"][1]["ok"], erg["r"][1]["zugestellt"]), (True, ["Claude"]), erg)
        self.warte_bis(lambda: b"Seed " + sid.encode() in k1.ausgabe(), 10, "der Seed kommt im Terminal des Empfängers an")
        self.assertEqual(self.cli(zugang, a, "seed", "zeige", sid)[1]["seed"]["status"], "aktiv")
        self.warte_bis(lambda: any(x["id"] == sid for x in (k1.liste("ablauf_stand") or [{}])[-1].get("seeds", [])), 10, "der aktive Seed steht in Daniels Stand")
        k1.senden("ablauf_steuern", {"aktion": "seed_zurueckziehen", "seed_id": sid})
        self.warte_bis(lambda: self.cli(zugang, a, "seed", "zeige", sid)[1]["seed"]["status"] == "zurueckgezogen", 10, "Daniel hat zurückgezogen")
        self.assertEqual(self.cli(zugang, a, "loop", "liste")[1]["loops"], [])

        # Freies Gespräch mit dem Modell, über das echte Werkzeug
        c = self.cli(zugang, a, "chat", "Hallo", "Hauhaucs")[1]
        self.assertEqual((c["ok"], c["text"]), (True, "Codex schickte eine Nachricht an Claude."), c)
        self.assertIn("Hallo Hauhaucs", json.dumps(self.modell.anfragen[-1]["messages"]))
        self.assertEqual(self.cli(zugang, a, "chat", "Noch", "was")[1]["ok"], True)
        self.assertEqual(len(self.modell.anfragen[-1]["messages"]) >= 3, True, "der Verlauf geht mit")
        vor = len(self.modell.anfragen)

        # Mischpult
        p = self.cli(zugang, a, "pult", "halbieren")[1]
        self.assertTrue(p["ok"])
        self.assertTrue(self.cli(zugang, a, "pult", "zurueck")[1]["ok"])
        self.assertTrue(self.cli(zugang, a, "pult", "leeren")[1]["ok"])
        self.assertEqual(self.cli(zugang, a, "pult", "zeige")[1]["nachrichten"], [])

        # Stop wirkt sofort
        self.assertFalse(self.cli(zugang, a, "beobachtung", "stop")[1]["aktiv"])
        self.assertEqual(self.cli(zugang, a, "beobachtung", "jetzt")[1]["reason"], "gestoppt")
        self.assertEqual(len(self.modell.anfragen), vor)


if __name__ == "__main__":
    unittest.main()
