"""G10 mit allem Echten: Relay-Prozess, Starter, zwei Agenten-Attrappen mit dem echten Werkzeug `bridge_cli`, ein Körper-Ersatz mit der echten Hände-Engine und XTEST — gegen echte GTK-Fenster unter Xvfb."""

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

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper.notaus import NotAus
from client_vps import anzeigeorte as ao
from client_vps import bridge_cli
from tests.test_bridge_server_anzeigeort import ENV, WURZEL, Desktop, freier_port
from tests.test_koerper_eingabe_adapter import DISPLAY, GtkProgramm

SKRIPT = '#!/bin/sh\necho "ID=$BRIDGE_TERMINAL_ID TOKEN=$BRIDGE_TERMINAL_TOKEN RT=$BRIDGE_RUNTIME_DIR"\nexec cat\n'
JPEG = b"\xff\xd8\xff\xe0" + b"JFIF-Testbild" * 4


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class G10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from augen_haende_bridge.koerper import x11_helfer as x

        cls.x = x
        cls.tmp = Path(tempfile.mkdtemp(prefix="g10-"))
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
        cls.d = {x_.ort: Desktop(f"ws://127.0.0.1:{cls.port}", x_.token, x_.ort) for x_ in desktops}
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

    # ---- Körper-Ersatz: echte Engine, echte XTEST-Eingabe ---------------------------------------------------------------------
    def koerper_starten(self, apps: dict):
        """apps: terminal_id -> GtkProgramm. Der Ersatz verwaltet, was der Bilderstrom wüsste: das gesendete Bild je Agent."""
        from augen_haende_bridge.koerper.eingabe_adapter import X11Backend

        from augen_haende_bridge.koerper.controller_adapter import AttrappenBackend, ControllerEngine

        self.na = NotAus()
        self.controller_na = NotAus()
        self.controller_backend = AttrappenBackend()
        self.controller = ControllerEngine(self.controller_backend, not_aus=lambda: self.controller_na.aktiv)
        self.controller_profil = True
        self.backend = X11Backend()
        self.keys = {f"kde1:window:{a.xid}": a.xid for a in apps.values()}
        self.bilder: dict[tuple[str, int], ea.Bildbezug] = {}
        self.engine = ea.HaendeEngine(self.backend, not_aus=self.na, ziel_stand=lambda z: (lambda r: ea.ZielStand(r is not None, r, False, self.keys.get(z), None))(self.x.fenster_rechteck(self.keys[z]) if z in self.keys else None),
                                      ziel_kennung=lambda z: self.keys.get(z), protokoll=lambda e: self.protokoll.append(e))
        self.protokoll = []
        self.stop = threading.Event()
        self.erledigt: set[str] = set()
        self.apps = apps

        def lauf():
            while not self.stop.is_set():
                for p in list(self.d["kde1"].liste("haende_auftrag")):
                    if p["auftrag_id"] in self.erledigt:
                        continue
                    self.erledigt.add(p["auftrag_id"])
                    threading.Thread(target=self.ausfuehren, args=(p,), daemon=True).start()
                time.sleep(0.02)

        threading.Thread(target=lauf, daemon=True).start()
        self.addCleanup(self.stop.set)
        self.addCleanup(self.backend.schliessen)

    def ausfuehren(self, p):
        if p["aktion"].get("art") == "controller":
            from augen_haende_bridge.koerper.controller_adapter import ControllerAktion, ControllerEngine
            e = self.controller.ausfuehren(p["auftrag_id"], ControllerAktion.aus_dict(p["aktion"]), lease_grund="" if time.time() * 1000 < p["lease_bis_ms"] else "lease_abgelaufen",
                                           haende_erlaubt=True, profil_erlaubt=self.controller_profil)
            d = e.zu_dict()
            self.d["kde1"].senden("haende_ergebnis", {"terminal_id": p["terminal_id"], "auftrag_id": p["auftrag_id"], "status": d["status"], "grund": d["grund"], "accepted": d["accepted"],
                                                      "delivered": d["delivered"], "observed": {}, "dauer_ms": d["dauer_ms"], "audited": False})
            return
        a = ea.Aktion.aus_dict(p["aktion"])
        bezug = self.bilder.get((p["terminal_id"], p["seq"]))
        lease_grund = "" if time.time() * 1000 < p["lease_bis_ms"] else "lease_abgelaufen"
        e = self.engine.ausfuehren(p["auftrag_id"], a, ziel=p["ziel"], bezug=bezug, lease_grund=lease_grund, haende_erlaubt=True)
        d = e.zu_dict()
        self.d["kde1"].senden("haende_ergebnis", {"terminal_id": p["terminal_id"], "auftrag_id": p["auftrag_id"], "status": d["status"], "grund": d["grund"], "accepted": d["accepted"],
                                                  "delivered": d["delivered"], "observed": {k: v for k, v in d["observed"].items() if k in ("zeiger", "erwartet")}, "dauer_ms": d["dauer_ms"], "audited": d["audited"]})

    def bild_senden(self, tid: str, app: GtkProgramm, seq: int):
        r = app.rect()
        ms = int(time.time() * 1000)
        self.bilder[(tid, seq)] = ea.Bildbezug(f"kde1:window:{app.xid}", seq, ms, r[2] - r[0], r[3] - r[1], r, app.xid, None, r)
        self.d["kde1"].senden("ziel_zustand", {"terminal_id": tid, "target_id": f"kde1:window:{app.xid}", "zustand": "ok", "faehigkeit": "frisch", "seit_ms": ms})
        self.d["kde1"].senden("frame", {"mime": "image/jpeg", "data": base64.b64encode(JPEG + bytes([seq])).decode(), "source": "capture", "captured_at_ms": ms, "width": r[2] - r[0],
                                         "height": r[3] - r[1], "terminal_id": tid, "aufnahme": "fenster", "seq": seq})
        t0 = time.monotonic()
        while time.monotonic() - t0 < 8:
            meta = self.runtime / "frames" / tid / "latest.json"
            if meta.exists() and json.loads(meta.read_text()).get("seq") == seq:
                return
            time.sleep(0.05)
        raise AssertionError("Bild kam nicht an")

    def agent_env(self, zugang, tid):
        return {"BRIDGE_TERMINAL_ID": tid, "BRIDGE_TERMINAL_TOKEN": zugang[tid], "BRIDGE_RUNTIME_DIR": str(self.runtime)}

    def cli(self, zugang, tid, *argv):
        """Das echte Werkzeug als eigener Prozess."""
        lauf = subprocess.run([sys.executable, str(WURZEL / "client_vps" / "bridge_cli.py"), *argv], env={**os.environ, **self.agent_env(zugang, tid)}, capture_output=True, text=True, timeout=40)
        return lauf.returncode, json.loads(lauf.stdout)

    def test_ablauf(self):
        k1 = self.d["kde1"]
        for d in self.d.values():
            d.senden("anzeigeorte_request", {})
            d.warte("anzeigeorte")
        a_app, b_app = GtkProgramm("G10A", 40, 40), GtkProgramm("G10B", 600, 40)
        self.addCleanup(a_app.beenden)
        self.addCleanup(b_app.beenden)
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})
        a = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "codex")["terminal_id"]
        k1.senden("terminal_start", {"start_id": "claude", "rows": 24, "cols": 80})
        b = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "claude")["terminal_id"]
        ende = time.monotonic() + 10
        while time.monotonic() < ende and len(re.findall(rb"TOKEN=\S+", k1.ausgabe())) < 2:
            time.sleep(0.05)
        zugang = {m.group(1): m.group(2) for m in re.finditer(r"ID=(\S+) TOKEN=(\S+) RT=\S+", k1.ausgabe().decode("utf-8", "replace"))}
        self.assertEqual(set(zugang), {a, b})
        self.koerper_starten({a: a_app, b: b_app})
        self.bild_senden(a, a_app, 1)
        self.bild_senden(b, b_app, 1)

        # ohne Lease geht nichts, und `see` nennt das Bild mit Folge und Quelle
        code, antwort = self.cli(zugang, a, "klick", "10", "10")
        self.assertEqual((code, antwort["reason"]), (1, "lease_fehlt"))
        code, antwort = self.cli(zugang, a, "see")
        self.assertEqual((antwort["frame"]["seq"], antwort["frame"]["aufnahme"]), (1, "fenster"))
        self.assertEqual(a_app.stand()["klicks"], 0)

        # Lease nehmen, klicken: ein echter Klick im echten Programm, vier getrennte Aussagen
        code, antwort = self.cli(zugang, a, "lease", "120")
        self.assertEqual((code, antwort["ok"]), (0, True), antwort)
        mitte = a_app.widget_mitte("knopf")
        code, antwort = self.cli(zugang, a, "klick", str(mitte[0]), str(mitte[1]))
        self.assertEqual((code, antwort["status"], antwort["accepted"], antwort["audited"]), (0, "ausgefuehrt", True, True), antwort)
        self.assertGreaterEqual(antwort["delivered"], 3)
        self.assertEqual(a_app.warte(lambda s: s["klicks"] >= 1)["klicks"], 1)
        self.assertEqual(b_app.stand()["klicks"], 0, "das andere Fenster bekam nichts")
        self.assertEqual(self.protokoll[-1]["ergebnis"]["status"], "ausgefuehrt")

        # Tippen und Hotkey
        feld = a_app.widget_mitte("feld")
        self.assertEqual(self.cli(zugang, a, "klick", str(feld[0]), str(feld[1]))[1]["status"], "ausgefuehrt")
        code, antwort = self.cli(zugang, a, "tippe", "Hallo", "Welt", "äöü")
        self.assertEqual((code, antwort["status"]), (0, "ausgefuehrt"), antwort)
        self.assertEqual(a_app.warte(lambda s: s["text"] == "Hallo Welt äöü")["text"], "Hallo Welt äöü")
        self.assertEqual(self.cli(zugang, a, "taste", "Strg+A")[1]["status"], "ausgefuehrt")
        self.assertEqual(self.cli(zugang, a, "tippe", "x")[1]["status"], "ausgefuehrt")
        self.assertEqual(a_app.warte(lambda s: s["text"] == "x")["text"], "x")

        # Controller: ohne Lease nichts (b hat keine), mit Lease von a: Knopf, Stick, Loslassen; falsche Eingaben werden schon im Werkzeug abgewiesen
        self.assertEqual(self.cli(zugang, b, "controller", "knopf", "a")[1]["reason"], "lease_fehlt")
        self.assertEqual(self.controller_backend.ereignisse, [])
        code, antwort = self.cli(zugang, a, "controller", "knopf", "a", "40")
        self.assertEqual((code, antwort["status"], antwort["delivered"]), (0, "ausgefuehrt", 1), antwort)
        self.assertEqual(self.controller_backend.ereignisse[:2], [("knopf", 0, "a", True), ("knopf", 0, "a", False)])
        self.assertEqual(self.cli(zugang, a, "controller", "stick", "links", "1", "-1", "40", "--geraet=1")[1]["status"], "ausgefuehrt")
        self.assertEqual(self.controller_backend.zustand[1]["sticks"]["links"], (0.0, 0.0), "danach in der Mitte")
        self.assertEqual(self.cli(zugang, a, "controller", "knopf", "zz")[1]["reason"], "aktion_ungueltig")
        self.assertEqual(self.cli(zugang, a, "controller", "knopf", "a", "99999")[1]["reason"], "aktion_ungueltig")
        self.controller_profil = False
        self.assertEqual(self.cli(zugang, a, "controller", "knopf", "b")[1]["grund"], "profil_erlaubt_nicht")
        self.controller_profil = True

        # zweiter Agent unabhängig, eigene Lease, anderes Fenster; kein Zugriff auf das Fenster des ersten
        code, antwort = self.cli(zugang, b, "klick", "10", "10")
        self.assertEqual(antwort["reason"], "lease_fehlt")
        self.assertEqual(self.cli(zugang, b, "lease")[1]["ok"], True)
        mb = b_app.widget_mitte("knopf")
        for _ in range(2):
            self.assertEqual(self.cli(zugang, b, "klick", str(mb[0]), str(mb[1]))[1]["status"], "ausgefuehrt")
        self.assertEqual(b_app.warte(lambda s: s["klicks"] >= 2)["klicks"], 2)
        self.assertEqual(a_app.stand()["klicks"], 1)

        # falsches Bild (unbekannte Folge) und Punkt außerhalb
        code, antwort = self.cli(zugang, a, "klick", str(mitte[0]), str(mitte[1]), "--seq=99")
        self.assertEqual((antwort.get("status"), antwort.get("grund")), ("abgelehnt", "frame_unbekannt"), str(antwort))
        code, antwort = self.cli(zugang, a, "klick", "9999", "9999")
        self.assertEqual((antwort["status"], antwort["grund"]), ("abgelehnt", "ausserhalb"))
        self.assertEqual(a_app.stand()["klicks"], 1)

        # Windows hat nie einen Auftrag gesehen
        self.assertEqual(self.d["windows"].liste("haende_auftrag"), [])

        # Not-Aus mitten im Ziehen: der echte Befehl wird abgebrochen, die Lease ist weg, nichts bleibt gedrückt
        fl = a_app.stand()["rects"]["flaeche"]
        w = a_app.rect()
        ergebnis = {}
        faden = threading.Thread(target=lambda: ergebnis.update(r=self.cli(zugang, a, "ziehe", str(fl[0] + 20 - w[0]), str(fl[1] + 20 - w[1]), str(fl[0] + 380 - w[0]), str(fl[1] + 100 - w[1]), "4000")))
        faden.start()
        a_app.warte(lambda s: s["gedrueckt"], 8)
        self.na.ausloesen("F12")
        faden.join(30)
        code, antwort = ergebnis["r"]
        self.assertEqual((antwort["status"], antwort["grund"]), ("abgebrochen", "not_aus"), antwort)
        self.assertFalse(a_app.warte(lambda s: not s["gedrueckt"])["gedrueckt"])
        self.assertEqual(self.cli(zugang, a, "klick", str(mitte[0]), str(mitte[1]))[1]["reason"], "lease_fehlt", "nach dem Not-Aus muss der Agent die Lease neu holen")
        self.assertEqual(self.cli(zugang, b, "klick", str(mb[0]), str(mb[1]))[1]["reason"], "lease_fehlt", "der Not-Aus entzieht alle Leases")
        self.na.freigeben()
        self.assertTrue(self.cli(zugang, a, "lease")[1]["ok"])
        self.assertEqual(self.cli(zugang, a, "klick", str(mitte[0]), str(mitte[1]))[1]["status"], "ausgefuehrt")

        # Controller und Not-Aus (zuletzt: ein Not-Aus entzieht allen die Lease, wie bei den Händen)
        self.assertEqual(self.cli(zugang, a, 'lease', '60')[1]['ok'], True)
        n_vorher = len(self.controller_backend.ereignisse)
        self.controller_na.ausloesen('test')
        self.assertEqual(self.cli(zugang, a, "controller", "knopf", "b")[1]["grund"], "not_aus")
        self.controller_na.freigeben()
        self.assertEqual(len(self.controller_backend.ereignisse), n_vorher)

        for t, d in ((a, k1), (b, k1)):
            d.senden("terminal_close", {"terminal_id": t})


if __name__ == "__main__":
    unittest.main()
