"""G11 mit allem Echten: Relay-Prozess, Starter, zwei Agenten-Attrappen mit dem echten Werkzeug, ein Körper-Ersatz mit dem echten WorldDOM-Dienst — gegen einen echten Chromium (CDP) und die echte Arbeitsfläche."""

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

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import weltdom_quellen as wq
from augen_haende_bridge.koerper.komposition import Arbeitsflaechen
from augen_haende_bridge.koerper.objekte import Objekt
from augen_haende_bridge.koerper.weltdom import WeltDom
from augen_haende_bridge.koerper.weltdom_befehle import pruefe_args
from augen_haende_bridge.koerper.weltdom_dienst import WeltdomDienst
from augen_haende_bridge.koerper.weltdom_profile import ProfilSpeicher
from client_vps import anzeigeorte as ao
from tests.test_bridge_server_anzeigeort import ENV, WURZEL, Desktop, freier_port
from tests.test_koerper_cdp import CHROMIUM, BrowserFall

DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
SKRIPT = '#!/bin/sh\necho "ID=$BRIDGE_TERMINAL_ID TOKEN=$BRIDGE_TERMINAL_TOKEN RT=$BRIDGE_RUNTIME_DIR"\nexec cat\n'
ZIEL = "kde1:window:4711"


@unittest.skipUnless(DISPLAY and CHROMIUM, "kein privater Xvfb oder kein Chromium")
class G11Tests(BrowserFall):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp = Path(tempfile.mkdtemp(prefix="g11-"))
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
        cls.port_relay = freier_port()
        env = {**os.environ, **ENV, "BRIDGE_SPRACHERKENNUNG": "aus", "PYTHONPATH": f"{WURZEL / 'src'}:{WURZEL}"}
        cls.server = subprocess.Popen([sys.executable, str(WURZEL / "client_vps" / "bridge_server.py"), "--port", str(cls.port_relay), "--journal", str(cls.tmp / "j.sqlite3"),
                                       "--starts", str(cls.tmp / "starts.json"), "--orte", str(cls.tmp / "orte.json"), "--runtime-dir", str(cls.runtime),
                                       "--desktops", str(cls.tmp / "desktops.json")], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        zeile, t0 = "", time.monotonic()
        while "Bridge relay ready" not in zeile and time.monotonic() - t0 < 30:
            zeile = cls.server.stdout.readline()
            if not zeile and cls.server.poll() is not None:
                raise RuntimeError("Relay ist nicht gestartet")
        threading.Thread(target=lambda: [None for _ in cls.server.stdout], daemon=True).start()
        desktops = ao.lade_desktops(cls.tmp / "desktops.json", cls.runtime, ENV)
        cls.d = {x.ort: Desktop(f"ws://127.0.0.1:{cls.port_relay}", x.token, x.ort) for x in desktops}
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
        super().tearDownClass()

    # ---- Körper-Ersatz ------------------------------------------------------------------------------------------------------------
    def koerper_starten(self, agent_a: str, agent_b: str):
        self.arbeit = Arbeitsflaechen()
        self.welt = WeltDom()
        self.seite_offen = self.seite()
        self.addCleanup(self.seite_offen.schliessen)
        s = self.seite_offen
        self.ursprung = wq.seiten_ursprung(s) or (0, 0)
        w, h = s.fenstermass()
        rect = (self.ursprung[0], self.ursprung[1], self.ursprung[0] + w, self.ursprung[1] + h)
        self.bezug = ea.Bildbezug(ZIEL, 1, int(time.time() * 1000), w, h, rect, "seite", None, rect)

        def overlay(tid, ziel, rel, text, empfaenger):
            return self.arbeit.dokument(ziel).hinzufuegen(Objekt(f"zeige-{len(self.arbeit.dokument(ziel).objekte)}", "marker", [rel], text=text, bildschirm=True, empfaenger=tuple(dict.fromkeys((tid, *empfaenger)))))

        self.dienst = WeltdomDienst(self.welt, cdp_seite=lambda z: s, ziel_stand=lambda z: ea.ZielStand(True, rect, False, "seite", None), bezug=lambda tid, z, seq: self.bezug, overlay=overlay, profile=ProfilSpeicher(),
                                    schlafen=time.sleep)
        self.stop = threading.Event()
        self.erledigt: set[str] = set()
        self.addCleanup(self.stop.set)

        def lauf():
            while not self.stop.is_set():
                for p in list(self.d["kde1"].liste("weltdom_auftrag")):
                    if p["auftrag_id"] in self.erledigt:
                        continue
                    self.erledigt.add(p["auftrag_id"])
                    threading.Thread(target=self.bearbeiten, args=(p,), daemon=True).start()
                time.sleep(0.02)

        threading.Thread(target=lauf, daemon=True).start()

    def bearbeiten(self, p):
        args = pruefe_args(p["befehl"], p["args"], intern=True)
        lease_grund = "lease_fehlt" if not p["lease_bis_ms"] else ("" if time.time() * 1000 < p["lease_bis_ms"] else "lease_abgelaufen")
        d, tid, ziel, seq = self.dienst, p["terminal_id"], p["ziel"], p["seq"]
        b = p["befehl"]
        if b == "liste":
            r = d.liste(ziel, herkunft=args.get("herkunft"), rolle=args.get("rolle"), text=args.get("text"), neu_messen=args.get("neu_messen", True))
        elif b == "aktion":
            r = d.aktion(tid, ziel, args["knoten"], args["aktion"], args.get("text"), args.get("erwartung"), seq, haende_erlaubt=True, profil="hintergrund", lease_grund=lease_grund)
        elif b == "zeige":
            r = d.zeige(tid, ziel, tuple(args["punkt"]), seq, args["urheber"], args["modus"], tuple(args["empfaenger"]), aktion=args.get("aktion", "klick"), text=args.get("text"),
                        haende_erlaubt=True, profil="hintergrund", lease_grund=lease_grund)
        elif b == "anker_neu":
            r = d.anker_neu(tid, ziel, args["name"], tuple(args["punkt"]) if args.get("punkt") else None, seq, args["urheber"], args.get("herkunft", "authored"))
        elif b == "profil_speichern":
            r = d.profil_speichern(ziel, args["name"], args["urheber"], args.get("passt_auf"), args.get("beschreibung", ""))
        elif b == "profil_laden":
            r = d.profil_laden(tid, ziel, args["name"], seq, args["urheber"], args.get("version"))
        elif b == "profil_liste":
            r = d.profil_liste(args.get("passt_auf"), bool(args.get("alle")))
        elif b == "profil_weg":
            r = d.profil_weg(args["name"], bool(args.get("aktiv", False)))
        else:
            r = d.anker_weg(ziel, args["knoten"])
        status = str(r.pop("status", "ok"))
        self.d["kde1"].senden("weltdom_ergebnis", {"terminal_id": tid, "auftrag_id": p["auftrag_id"], "status": status[:30], "daten": json.loads(json.dumps(r, default=str))})

    def cli(self, zugang, tid, *argv):
        env = {**os.environ, "BRIDGE_TERMINAL_ID": tid, "BRIDGE_TERMINAL_TOKEN": zugang[tid], "BRIDGE_RUNTIME_DIR": str(self.runtime)}
        lauf = subprocess.run([sys.executable, str(WURZEL / "client_vps" / "bridge_cli.py"), *argv], env=env, capture_output=True, text=True, timeout=90)
        return lauf.returncode, json.loads(lauf.stdout)

    def zahl(self):
        return int(self.seite_offen.auswerten("document.getElementById('zahl').innerText"))

    def test_ablauf(self):
        k1 = self.d["kde1"]
        for d in self.d.values():
            d.senden("anzeigeorte_request", {})
            d.warte("anzeigeorte")
        k1.senden("terminal_start", {"start_id": "codex", "rows": 24, "cols": 80})
        a = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "codex")["terminal_id"]
        k1.senden("terminal_start", {"start_id": "claude", "rows": 24, "cols": 80})
        b = k1.warte("terminal_state", lambda p: p["state"] == "running" and p["start_id"] == "claude")["terminal_id"]
        ende = time.monotonic() + 10
        while time.monotonic() < ende and len(re.findall(rb"TOKEN=\S+", k1.ausgabe())) < 2:
            time.sleep(0.05)
        zugang = {m.group(1): m.group(2) for m in re.finditer(r"ID=(\S+) TOKEN=(\S+) RT=\S+", k1.ausgabe().decode("utf-8", "replace"))}
        self.koerper_starten(a, b)
        ms = int(time.time() * 1000)
        for t in (a, b):
            k1.senden("ziel_zustand", {"terminal_id": t, "target_id": ZIEL, "zustand": "ok", "faehigkeit": "frisch", "seit_ms": ms})
        time.sleep(0.5)

        # Messen: echte Knoten mit Herkunft, Konfidenz, Alter; fehlende Quellen werden genannt
        code, r = self.cli(zugang, a, "weltdom")
        self.assertEqual((code, r["status"]), (0, "ok"), r)
        self.assertTrue(r["quellen"]["cdp"].startswith("ok"), r["quellen"])
        self.assertTrue(r["quellen"]["ui"].startswith("nicht verfügbar") and r["quellen"]["bild"].startswith("nicht verfügbar"))
        knopf = next(k for k in r["knoten"] if (k["rolle"], k["name"]) == ("button", "Zaehlen"))
        self.assertEqual((knopf["herkunft"], knopf["quelle"], knopf["confidence"], knopf["aufloesung"], knopf["veraltet"]), ("real", "cdp", 1.0, "cdp", False))
        self.assertIsNotNone(knopf["rect"])
        feld = next(k for k in r["knoten"] if k["rolle"] == "textbox")

        # Handeln braucht die Lease
        code, r = self.cli(zugang, a, "knoten", knopf["id"], "klick")
        self.assertEqual((code, r["reason"]), (1, "lease_fehlt"))
        self.assertEqual(self.zahl(), 0)
        self.assertTrue(self.cli(zugang, a, "lease", "60")[1]["ok"])
        code, r = self.cli(zugang, a, "knoten", knopf["id"], "klick", "--erwartung=1")
        self.assertEqual((code, r["status"], r["methode"], r["ruecklese"]["bestaetigt"]), (0, "ausgefuehrt", "cdp", True), r)
        self.assertEqual(self.zahl(), 1, "wirklich einmal geklickt")
        code, r = self.cli(zugang, a, "knoten", knopf["id"], "klick")
        self.assertIsNone(r["ruecklese"]["bestaetigt"], "ohne Erwartung ist die Wirkung nicht nachgeprüft")
        code, r = self.cli(zugang, a, "knoten", feld["id"], "text", "Grüße", "Welt")
        self.assertEqual((r["status"], r["ruecklese"]["nachher"], r["ruecklese"]["bestaetigt"]), ("ausgefuehrt", "Grüße Welt", True))
        code, r = self.cli(zugang, a, "knoten", feld["id"], "lesen")
        self.assertEqual(r["gelesen"], "Grüße Welt")
        vorher = self.zahl()
        code, r = self.cli(zugang, a, "knoten", "gibt-es-nicht", "klick")
        self.assertEqual((r["status"], r["grund"]), ("unaufloesbar", "knoten_unbekannt"))
        self.assertEqual(self.zahl(), vorher)

        # Der zweite Agent bindet dasselbe Fenster, aber die Lease hält der erste
        self.assertEqual(self.cli(zugang, b, "knoten", knopf["id"], "klick")[1]["reason"], "lease_fremd")

        # Bewusst angelegte Knoten: Herkunft authored, Urheber, sichtbar in der Liste
        code, r = self.cli(zugang, a, "anker", "Mein Slot", "10", "10")
        self.assertEqual((r["status"], r["knoten"]["herkunft"], r["knoten"]["urheber"], r["knoten"]["confidence"]), ("ok", "authored", "Codex", 1.0), r)
        code, r = self.cli(zugang, b, "weltdom", "--herkunft=authored", "--alt")
        self.assertEqual([k["name"] for k in r["knoten"]], ["Mein Slot"], "der andere Agent sieht ihn")
        slot_id = r["knoten"][0]["id"]
        code, r = self.cli(zugang, a, "knoten", slot_id, "klick")
        self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "haende_nicht_verfuegbar"), "ein erfundener Anker ohne Hände-Engine löst keinen Klick aus")
        self.assertEqual(self.zahl(), vorher)
        # Profile: der Anker wird als Profil gespeichert, der andere Agent findet es über den Namen und lädt es; Löschen gibt es nicht, nur Ausblenden
        code, r = self.cli(zugang, a, "profil", "speichern", "Test-Seite", "--programm=chromium", "--seite=localhost")
        self.assertEqual((code, r["status"]), (0, "ok"), r)
        self.assertEqual(r["version"], 1)
        code, r = self.cli(zugang, b, "profil", "liste", "--programm=chrom")
        self.assertEqual([e["name"] for e in r["profile"]], ["Test-Seite"], r)
        self.assertEqual(self.cli(zugang, a, "anker-weg", slot_id)[1]["status"], "ok")
        code, r = self.cli(zugang, b, "profil", "laden", "Test-Seite")
        self.assertEqual((r["status"], r["geladen"]), ("ok", 1), r)
        code, r = self.cli(zugang, b, "weltdom", "--herkunft=authored", "--alt")
        self.assertEqual([(k["name"], k["urheber"]) for k in r["knoten"]], [("Mein Slot", "Claude")], "geladen mit dem Urheber, der lädt")
        self.assertEqual(self.cli(zugang, b, "profil", "weg", "Test-Seite")[1]["status"], "ok")
        self.assertEqual(self.cli(zugang, b, "profil", "laden", "Test-Seite")[1]["grund"], "profil_ausgeblendet")
        self.assertEqual(self.cli(zugang, b, "profil", "zurueck", "Test-Seite")[1]["status"], "ok")
        self.assertEqual(self.cli(zugang, b, "anker-weg", r["knoten"][0]["id"])[1]["status"], "ok")

        # Zeigen: Darstellung ohne Wirkung in der Anwendung, nur für die Gewählten
        mitte = ((knopf["rect"][0] + knopf["rect"][2]) // 2 - self.ursprung[0], (knopf["rect"][1] + knopf["rect"][3]) // 2 - self.ursprung[1])
        zahl_vorher = self.zahl()
        code, r = self.cli(zugang, b, "zeige", str(mitte[0]), str(mitte[1]), f"--an=Codex")
        self.assertEqual((r["status"], r["wirkung_in_anwendung"], r["pruefung"]["status"], r["geste"]["knoten_name"]), ("praesentiert", False, "gueltig", "Zaehlen"), r)
        marker = list(self.arbeit.dokument(ZIEL).objekte.values())
        self.assertEqual(len(marker), 1)
        self.assertEqual(sorted(marker[0].empfaenger), sorted([b, a]), "Urheber und Gewählter sehen es")
        self.assertEqual(self.zahl(), zahl_vorher, "die Darstellung hat die Anwendung nicht berührt")

        # Einfügen: echte Handlung am Inhalt unter der Geste, eigener Beleg; ohne Lease nicht
        code, r = self.cli(zugang, b, "zeige", str(mitte[0]), str(mitte[1]), "--einfuegen", "klick")
        self.assertEqual((r["ok"], r["reason"]), (False, "lease_fremd"))
        code, r = self.cli(zugang, a, "zeige", str(mitte[0]), str(mitte[1]), "--einfuegen", "klick")
        self.assertEqual((r["status"], r["wirkung_in_anwendung"]), ("eingefuegt", True), r)
        self.assertEqual(self.zahl(), zahl_vorher + 1)

        # Layoutwechsel: die alte Geste warnt, der alte Pixel wird nie geklickt
        s = self.seite_offen
        s.auswerten("(() => { const st = document.createElement('style'); st.textContent = '#knopf { position: fixed; right: 20px; top: 20px; }'; document.head.appendChild(st); })()")
        s.befehl("Emulation.setDeviceMetricsOverride", width=800, height=500, deviceScaleFactor=1, mobile=False)
        time.sleep(0.3)
        code, r = self.cli(zugang, a, "weltdom", "--rolle=button")
        neu = next(k for k in r["knoten"] if k["name"] == "Zaehlen")
        neu_mitte = ((neu["rect"][0] + neu["rect"][2]) // 2 - self.ursprung[0], (neu["rect"][1] + neu["rect"][3]) // 2 - self.ursprung[1])
        w, h = s.fenstermass()
        rect = (self.ursprung[0], self.ursprung[1], self.ursprung[0] + w, self.ursprung[1] + h)
        self.bezug = ea.Bildbezug(ZIEL, 2, int(time.time() * 1000), w, h, rect, "seite", None, rect)
        self.dienst._ziel_stand = lambda z: ea.ZielStand(True, rect, False, "seite", None)
        code, r = self.cli(zugang, a, "zeige", str(neu_mitte[0]), str(neu_mitte[1]), "--einfuegen", "klick")
        self.assertEqual(r["status"], "eingefuegt", r)
        self.assertEqual(self.zahl(), zahl_vorher + 2, "nach dem Layoutwechsel trifft der frisch gemessene Punkt den Knopf")

        for t in (a, b):
            k1.senden("terminal_close", {"terminal_id": t})


if __name__ == "__main__":
    unittest.main()
