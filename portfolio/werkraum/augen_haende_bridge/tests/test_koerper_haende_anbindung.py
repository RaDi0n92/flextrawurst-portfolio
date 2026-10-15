"""G10: die Hände im Ganzen angeschlossen — Relay-Prüfung, Starter (Lease, Weiterleitung, Ergebnis), Körper-Anwendung und Anbindung (Engine, Protokoll)."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge import transport as tr
from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import haende_anbindung as ha
from augen_haende_bridge.koerper.bilderstrom import Bilderstrom, Gesendet
from tests.test_anzeigeort import baue, ereignis, falsche_sitzung
from tests.test_koerper_anwendung import _event, _gestartet

ZIEL = "kde1:window:77"


class RelayPruefTests(unittest.TestCase):
    def setUp(self):
        from client_vps import anzeigeorte as ao

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        self.relay = tr.Relay(ao.baue_principals(d), tr.Journal(tmp / "j.sqlite3"))
        self.desktop = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_control_terminals))
        self.starter = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_serve_terminals))

    AUFTRAG = {"terminal_id": "t-1", "auftrag_id": "h-1", "ziel": ZIEL, "lease": "l-1", "lease_bis_ms": 5, "seq": 3, "aktion": {"art": "klick", "punkt": [1, 2]}}
    ERGEBNIS = {"terminal_id": "t-1", "auftrag_id": "h-1", "status": "ausgefuehrt", "grund": "", "accepted": True, "delivered": 3, "observed": {"zeiger": [1, 2]}, "dauer_ms": 20, "audited": True}

    def test_auftrag_kommt_nur_vom_starter_und_streng(self):
        self.assertEqual(self.relay.payload(self.starter, "haende_auftrag", dict(self.AUFTRAG))["seq"], 3)
        self.assertIsNone(self.relay.payload(self.starter, "haende_auftrag", {**self.AUFTRAG, "seq": None})["seq"])
        for kaputt in ({"x": 1}, {"seq": -1}, {"seq": "3"}, {"ziel": ""}, {"ziel": "x" * 200}, {"lease": "a b"}, {"aktion": "klick"}, {"aktion": {"art": "x" * 3000}}, {"lease_bis_ms": -1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                self.relay.payload(self.starter, "haende_auftrag", {**self.AUFTRAG, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.desktop, "haende_auftrag", dict(self.AUFTRAG))  # ein Desktop darf sich keine Aufträge schicken

    def test_ergebnis_kommt_nur_vom_desktop_und_streng(self):
        self.assertEqual(self.relay.payload(self.desktop, "haende_ergebnis", dict(self.ERGEBNIS))["status"], "ausgefuehrt")
        for kaputt in ({"status": "ok"}, {"grund": "x" * 61}, {"accepted": 1}, {"audited": "ja"}, {"observed": []}, {"observed": {"x": "y" * 700}}, {"delivered": -1}, {"dauer_ms": "5"}, {"x": 1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                self.relay.payload(self.desktop, "haende_ergebnis", {**self.ERGEBNIS, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.starter, "haende_ergebnis", dict(self.ERGEBNIS))


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.l, self.fv = baue()
        for o in ("windows", "kde1"):
            self.l.handle(ereignis("anzeigeorte_request", {}, o))
        self.s = falsche_sitzung(self.l, "t-1")
        self.s2 = falsche_sitzung(self.l, "t-2")
        self.l.register.anlegen("t-1", "Codex", strom="codex", zustand="running")
        self.l.register.anlegen("t-2", "Claude", strom="claude", zustand="running")
        for t in ("t-1", "t-2"):
            self.l.anzeige[t] = self.l.ziel[t] = "kde1"
        self.l.ziel_info["t-1"] = {"target_id": ZIEL, "zustand": "ok", "faehigkeit": "frisch", "seit_ms": 1}
        self.l.ziel_info["t-2"] = {"target_id": "kde1:window:88", "zustand": "ok", "faehigkeit": "frisch", "seit_ms": 1}
        self.fv.gesendet.clear()

    def lease(self, t="t-1", **kw):
        return self.l.lease_befehl(t, kw)

    def haende(self, aktion, t="t-1", antwort=None, **kw):
        """Führt den Befehl aus; ein Hilfsfaden spielt den Körper und antwortet (oder schweigt, wenn antwort None)."""
        self.fv.gesendet.clear()
        fertig = threading.Event()

        def koerper():
            ende = time.monotonic() + 3
            while time.monotonic() < ende and not fertig.is_set():
                for ort, kind, p in list(self.fv.gesendet):
                    if kind == "haende_auftrag" and antwort is not None:
                        self.l.handle(ereignis("haende_ergebnis", {"terminal_id": p["terminal_id"], "auftrag_id": p["auftrag_id"], "observed": {}, "dauer_ms": 5, "audited": True, "delivered": 3,
                                                                    "accepted": True, **{"status": "ausgefuehrt", "grund": "", **antwort}}, kw.get("von", "kde1")))
                        return
                time.sleep(0.01)

        faden = threading.Thread(target=koerper)
        faden.start()
        r = self.l.haende_befehl(t, {"aktion": aktion, **{k: v for k, v in kw.items() if k != "von"}})
        fertig.set()
        faden.join(5)
        return r

    KLICK = {"art": "klick", "punkt": [10, 20]}

    def test_lease_nehmen_ist_exklusiv_und_pro_ziel(self):
        r = self.lease()
        self.assertEqual((r["ok"], r["ziel"]), (True, ZIEL))
        self.assertTrue(r["lease"].startswith("l-"))
        self.assertTrue(self.lease("t-2")["ok"], "ein anderes Fenster, eine andere Lease")
        self.l.ziel_info["t-2"]["target_id"] = ZIEL
        self.assertEqual(self.lease("t-2"), {"ok": False, "reason": "belegt", "ziel": ZIEL})
        self.assertTrue(self.lease(aktion="freigeben")["ok"])
        self.assertTrue(self.lease("t-2")["ok"])

    def test_lease_nur_auf_das_gebundene_fensterziel_des_eigenen_ortes(self):
        self.assertEqual(self.lease(ziel="kde1:window:5")["reason"], "ziel_nicht_gebunden", "kein Fenster, das der Agent nicht gebunden hat")
        self.assertEqual(self.lease(ziel="windows:window:5")["reason"], "ziel_anderer_ort")
        self.assertEqual(self.lease(ziel="desktop")["reason"], "kein_fenster_ziel")
        self.l.ziel_info["t-1"]["target_id"] = "desktop"
        self.assertEqual(self.lease()["reason"], "kein_fenster_ziel", "der ganze Desktop ist kein Hände-Ziel")
        self.l.ziel_info.pop("t-1")
        self.assertEqual(self.lease()["reason"], "kein_fenster_ziel")
        self.assertEqual(self.lease(ttl_s="x")["reason"], "kein_fenster_ziel")

    def test_ttl_wird_geprueft_und_begrenzt(self):
        self.assertEqual(self.lease(ttl_s=True)["reason"], "ttl_ungueltig")
        self.assertEqual(self.lease(ttl_s=-5)["reason"], "ttl_ungueltig")
        self.assertLessEqual(self.lease(ttl_s=99999)["laeuft_ab_in_s"], 300)

    def test_ohne_lease_und_mit_fremder_lease_wird_nichts_gesendet(self):
        self.assertEqual(self.haende(self.KLICK)["reason"], "lease_fehlt")
        self.l.ziel_info["t-2"]["target_id"] = ZIEL
        self.lease("t-2")
        self.assertEqual(self.l.leases.von(ZIEL).halter, "t-2")
        r = self.haende(self.KLICK)
        self.assertEqual((r["reason"], r["status"]), ("lease_fremd", "abgelehnt"))
        self.assertEqual(self.fv.an("kde1", "haende_auftrag"), [], "nichts ging an den Körper")

    def test_ungueltige_aktion_und_ziel_werden_vor_dem_senden_abgelehnt(self):
        self.lease()
        for aktion in (None, {}, {"art": "klick"}, {"art": "klick", "punkt": [1, 2], "x": 1}, {"art": "ziehen", "punkt": [1, 1], "bis": [2, 2], "dauer_ms": 1}):
            self.assertEqual(self.haende(aktion)["reason"], "aktion_ungueltig", aktion)
        self.assertEqual(self.l.haende_befehl("t-1", {"aktion": self.KLICK, "seq": -2})["reason"], "seq_ungueltig")
        self.assertEqual(self.fv.an("kde1", "haende_auftrag"), [])

    def test_der_auftrag_geht_an_den_desktop_des_ziels_und_das_ergebnis_kommt_zurueck(self):
        self.lease()
        self.l.latest_frame = lambda t: {"seq": 5}
        r = self.haende(self.KLICK, antwort={})
        self.assertEqual((r["ok"], r["status"], r["accepted"], r["delivered"], r["audited"]), (True, "ausgefuehrt", True, 3, True))
        gesendet = self.fv.an("kde1", "haende_auftrag")
        self.assertEqual(len(gesendet), 1)
        p = gesendet[0]
        self.assertEqual((p["ziel"], p["seq"], p["aktion"], p["terminal_id"]), (ZIEL, 5, {"art": "klick", "punkt": [10, 20]}, "t-1"))
        self.assertGreater(p["lease_bis_ms"], int(time.time() * 1000))
        self.assertEqual(self.fv.an("windows", "haende_auftrag"), [], "der andere Desktop bekommt nichts")

    def test_ein_ablehnungsgrund_des_koerpers_kommt_an_ohne_dass_ok_behauptet_wird(self):
        self.lease()
        r = self.haende(self.KLICK, antwort={"status": "abgelehnt", "grund": "geometrie_geaendert", "accepted": False, "delivered": 0})
        self.assertEqual((r["ok"], r["status"], r["grund"], r["accepted"], r["delivered"]), (False, "abgelehnt", "geometrie_geaendert", False, 0))
        self.assertIsNotNone(self.l.leases.von(ZIEL), "eine normale Ablehnung entzieht die Lease nicht")

    def test_stoppgruende_entziehen_die_lease_keine_heimliche_wiederaufnahme(self):
        for grund in ("not_aus", "daniel_uebernimmt", "verbindung_weg"):
            self.lease()
            r = self.haende(self.KLICK, antwort={"status": "abgebrochen", "grund": grund, "accepted": True})
            self.assertEqual((r["ok"], r.get("grund")), (False, grund))
            self.assertIsNone(self.l.leases.von(ZIEL), grund)
            self.assertEqual(self.haende(self.KLICK)["reason"], "lease_fehlt")

    def test_not_aus_entzieht_alle_leases(self):
        self.lease()
        self.lease("t-2")
        self.haende(self.KLICK, antwort={"status": "abgelehnt", "grund": "not_aus", "accepted": False, "delivered": 0})
        self.assertEqual((self.l.leases.von(ZIEL), self.l.leases.von("kde1:window:88")), (None, None))

    def test_schweigt_der_koerper_ist_der_ausgang_unbekannt(self):
        import client_vps.terminal_launcher as tl

        alt, tl.HAENDE_WARTEN_S = tl.HAENDE_WARTEN_S, 0.3
        self.addCleanup(lambda: setattr(tl, "HAENDE_WARTEN_S", alt))
        self.lease()
        r = self.l.haende_befehl("t-1", {"aktion": self.KLICK})
        self.assertEqual((r["ok"], r["reason"]), (False, "keine_antwort"))
        self.assertIn("unbekannt", r["hinweis"])
        self.assertEqual(self.l._haende_wartend, {}, "nichts bleibt hängen")

    def test_ergebnis_von_falschem_ort_oder_fremder_id_zaehlt_nicht(self):
        self.lease()
        wartend = {"terminal_id": "t-1", "ziel": ZIEL, "event": threading.Event(), "ergebnis": None}
        self.l._haende_wartend["h-1"] = wartend
        basis = {"terminal_id": "t-1", "observed": {}, "dauer_ms": 1, "audited": True, "delivered": 0, "accepted": True, "status": "ausgefuehrt", "grund": ""}
        self.l.handle(ereignis("haende_ergebnis", {**basis, "auftrag_id": "h-1"}, "windows"))
        self.assertFalse(wartend["event"].is_set())
        self.assertEqual(self.l.abgewiesen["haende_ergebnis_vom_falschen_ort"], 1)
        self.l.handle(ereignis("haende_ergebnis", {**basis, "auftrag_id": "h-9"}, "kde1"))
        self.l.handle(ereignis("haende_ergebnis", {**basis, "auftrag_id": "h-1", "terminal_id": "t-2"}, "kde1"))
        self.assertEqual(self.l.abgewiesen["haende_ergebnis_unbekannt"], 2)
        self.l.handle(ereignis("haende_ergebnis", {**basis, "auftrag_id": "h-1"}, "kde1"))
        self.assertTrue(wartend["event"].is_set())

    def test_ein_auftrag_zugleich_je_agent(self):
        self.lease()
        self.l._haende_wartend["h-x"] = {"terminal_id": "t-1", "ziel": ZIEL, "event": threading.Event(), "ergebnis": None}
        self.assertEqual(self.l.haende_befehl("t-1", {"aktion": self.KLICK})["reason"], "haende_laeuft_schon")

    def test_geht_ein_desktop_offline_verfallen_seine_leases(self):
        self.lease()
        self.fv.offline.add("kde1")
        self.fv.veraenderungen = lambda: True
        self.l.anzeigeorte_senden_alle = lambda: None
        self.l.start()
        self.addCleanup(self.l.shutdown)
        ende = time.monotonic() + 4
        while time.monotonic() < ende and self.l.leases.von(ZIEL) is not None:
            time.sleep(0.1)
        self.assertIsNone(self.l.leases.von(ZIEL))

    def test_ohne_verteiler_gibt_es_keine_haende(self):
        import client_vps.terminal_launcher as tl

        l = tl.Launcher(object(), {}, {}, Path(tempfile.mkdtemp()))
        self.assertEqual(l.lease_befehl("t-1", {})["reason"], "haende_brauchen_verteiler")

    def test_agent_request_leitet_lease_und_haende_weiter_und_verlangt_das_token(self):
        self.s.token, self.s2.token = "tok-1", "tok-2"
        self.assertFalse(self.l.agent_request({"terminal_id": "t-1", "token": "falsch", "cmd": "lease"})["ok"])
        r = self.l.agent_request({"terminal_id": "t-1", "token": "tok-1", "cmd": "lease", "aktion": "nehmen"})
        self.assertEqual((r["ok"], r["ziel"]), (True, ZIEL))
        r = self.l.agent_request({"terminal_id": "t-2", "token": "tok-2", "cmd": "haende", "aktion": self.KLICK})
        self.assertEqual(r["reason"], "lease_fehlt")
        self.assertEqual(self.l.agent_request({"terminal_id": "t-1", "token": "tok-1", "cmd": "haende", "aktion": {"art": "magie"}})["reason"], "aktion_ungueltig")


class AnwendungTests(unittest.TestCase):
    def maschine(self, **kw):
        app, gui, gebaut = _gestartet()
        aufrufe = []

        class Engine:
            verbindung_ereignisse = []

            def ausfuehren(self_, auftrag_id, aktion, **k):
                aufrufe.append((auftrag_id, aktion, k))
                return ea.Ergebnis(auftrag_id, "ausgefuehrt", accepted=True, delivered=3, observed={"zeiger": [1, 2], "ignoriert": 1}, dauer_ms=7, audited=True)

            def verbindung_verloren(self_):
                self_.verbindung_ereignisse.append("weg")

            def verbindung_da(self_):
                self_.verbindung_ereignisse.append("da")

        app.haende_engine = Engine()
        app.bilderstrom = Bilderstrom(erfassen=lambda: (b"", 0, 0), bildschirm=lambda: (0, 0, 1, 1), fenster_rect=lambda h: None, senden=lambda t, p: True)
        return app, gebaut, aufrufe

    def auftrag(self, **kw):
        p = {"terminal_id": "t-1", "auftrag_id": "h-1", "ziel": ZIEL, "lease": "l-1", "lease_bis_ms": int(time.time() * 1000) + 60_000, "seq": 3, "aktion": {"art": "klick", "punkt": [5, 6]}}
        p.update(kw)
        return p

    def warte(self, app, n=1):
        ende = time.monotonic() + 3
        while time.monotonic() < ende and len([g for g in app.runtime.gesendet if g[0] == "haende_ergebnis"]) < n:
            time.sleep(0.02)
        return [g[1] for g in app.runtime.gesendet if g[0] == "haende_ergebnis"]

    def test_der_auftrag_wird_mit_bild_rechten_und_profil_ausgefuehrt_und_das_ergebnis_gesendet(self):
        app, _g, aufrufe = self.maschine()
        app.bilderstrom.verlauf["t-1"] = __import__("collections").deque([Gesendet(3, 5000, 400, 300, (100, 100, 500, 400), (100, 100, 500, 400), 77)])
        app.ereignis(_event("haende_auftrag", self.auftrag()))
        erg = self.warte(app)[0]
        self.assertEqual((erg["status"], erg["accepted"], erg["delivered"], erg["audited"], erg["observed"]), ("ausgefuehrt", True, 3, True, {"zeiger": [1, 2]}), "nur bekannte Felder gehen zurück")
        auftrag_id, aktion, k = aufrufe[0]
        self.assertEqual((aktion.art, k["ziel"], k["haende_erlaubt"], k["profil_erlaubt"], k["lease_grund"]), ("klick", ZIEL, True, True, ""))
        b = k["bezug"]
        self.assertEqual((b.ziel, b.seq, b.breite, b.hoehe, b.rect, b.bild_rect, b.captured_at_ms), ("windows:window:77", 3, 400, 300, (100, 100, 500, 400), (100, 100, 500, 400), 5000))

    def test_ort_des_ziel_schluessels_ist_der_dieses_koerpers(self):
        app, _g, aufrufe = self.maschine()
        self.assertEqual(app.ort, "windows", "der Test-Körper steht auf windows; ein Bild von hwnd 77 hieße windows:window:77")
        app.bilderstrom.verlauf["t-1"] = __import__("collections").deque([Gesendet(3, 5000, 400, 300, (100, 100, 500, 400), (100, 100, 500, 400), 77)])
        self.assertEqual(app._bildbezug("t-1", 3).ziel, "windows:window:77")
        self.assertIsNone(app._bildbezug("t-1", 99), "ein unbekanntes Bild")
        self.assertEqual(app._bildbezug("t-1", None).seq, 3, "ohne Angabe das letzte")
        app.bilderstrom.verlauf["t-1"].append(Gesendet(4, 5000, 400, 300, None, (0, 0, 10, 10), None))
        self.assertIsNone(app._bildbezug("t-1", 4), "ein Desktop-Bild ist keine Grundlage für Hände")

    def test_rechte_profil_lease_und_nur_terminal_werden_dem_kaefig_mitgegeben(self):
        app, _g, aufrufe = self.maschine()
        agent = app.agenten["t-1"]
        agent.haende = False
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-2")))
        agent.haende, agent.steuerprofil = True, "hintergrund"
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-3")))
        agent.steuerprofil = "geteilte_maus"
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-4", lease_bis_ms=1)))
        agent.nur_terminal = True
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-5")))
        self.warte(app, 4)
        k = {a[0]: a[2] for a in aufrufe}
        self.assertFalse(k["h-2"]["haende_erlaubt"])
        self.assertFalse(k["h-3"]["profil_erlaubt"])
        self.assertEqual(k["h-4"]["lease_grund"], "lease_abgelaufen")
        self.assertFalse(k["h-5"]["haende_erlaubt"], "„nur Terminal“ schaltet die Hände aus")

    def test_ohne_engine_ungueltige_aktion_und_unbekannter_agent_werden_ehrlich_abgelehnt(self):
        app, _g, aufrufe = self.maschine()
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-a", aktion={"art": "klick"})))
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-b", terminal_id="t-99")))
        app.haende_engine = None
        app.ereignis(_event("haende_auftrag", self.auftrag(auftrag_id="h-c")))
        erg = {e["auftrag_id"]: e for e in self.warte(app, 3)}
        self.assertEqual((erg["h-a"]["grund"], erg["h-b"]["grund"], erg["h-c"]["grund"]), ("aktion_ungueltig", "kein_ziel", "haende_nicht_verfuegbar"))
        self.assertTrue(all(e["status"] == "abgelehnt" and not e["accepted"] and e["delivered"] == 0 for e in erg.values()))
        self.assertEqual(aufrufe, [])

    def test_ein_fehler_der_engine_wird_gemeldet_nicht_verschluckt(self):
        app, _g, _a = self.maschine()

        def kaputt(*a, **k):
            raise RuntimeError("boom")

        app.haende_engine.ausfuehren = kaputt
        app.ereignis(_event("haende_auftrag", self.auftrag()))
        erg = self.warte(app)[0]
        self.assertEqual((erg["status"], erg["grund"]), ("fehler", "backend_fehler"))

    def test_verbindungsabbruch_wird_ohne_den_gui_faden_an_die_haende_gemeldet(self):
        app, _g, _a = self.maschine()
        app._verbindung_schnell({"kind": "runtime.failed", "reason": "x"})
        app._verbindung_schnell({"kind": "runtime.connected"})
        app._verbindung_schnell({"kind": "event"})
        self.assertEqual(app.haende_engine.verbindung_ereignisse, ["weg", "da"])

    def test_steuerprofil_wechselt_reihum_und_wird_gespeichert(self):
        app, _g, _a = self.maschine()
        gesehen = []
        for _ in range(5):
            app.agent_profil_wechseln("t-1")
            gesehen.append(app.agenten["t-1"].steuerprofil)
        self.assertEqual(gesehen, ["controller", "hybrid", "hintergrund", "geteilte_maus", "controller"])
        app.agent_profil_wechseln("t-gibt-es-nicht")

    def test_ausnahme_wird_umgeschaltet(self):
        app, _g, _a = self.maschine()
        self.assertFalse(app.daniel_ausnahme)
        app.ausnahme_umschalten()
        self.assertTrue(app.daniel_ausnahme)
        app.ausnahme_umschalten()
        self.assertFalse(app.daniel_ausnahme)


class AnbindungTests(unittest.TestCase):
    def test_ohne_backend_sind_die_haende_ehrlich_nicht_verfuegbar(self):
        import augen_haende_bridge.koerper.eingabe_adapter as e

        alt = e.X11Backend

        class Kaputt:
            def __init__(self):
                raise RuntimeError("XTEST fehlt")

        e.X11Backend = Kaputt
        try:
            b = ha.baue_haende("linux", "kde1", None)
        finally:
            e.X11Backend = alt
        self.assertIsNone(b.engine)
        self.assertIn("nicht verfügbar", b.fehler)

    def test_stand_und_kennung_nur_fuer_den_eigenen_ort(self):
        backend = SimpleNamespace()
        b = ha.baue_haende("linux", "kde1", None, backend=backend, fenster_zustand=lambda k: (True, False, (1, 2, 3, 4)))
        self.assertEqual(b.engine._ziel_stand("kde1:window:9"), ea.ZielStand(True, (1, 2, 3, 4), False, 9, None))
        self.assertIsNone(b.engine._ziel_stand("windows:window:9"), "ein Fenster eines anderen Arbeitsplatzes ist hier kein Ziel")
        self.assertIsNone(b.engine._ziel_stand("desktop"))
        self.assertEqual((b.engine._ziel_kennung("kde1:window:9"), b.engine._ziel_kennung("kde2:window:9")), (9, None))

    def test_protokoll_schreibt_zeilen_und_rotiert_einmal(self):
        pfad = Path(tempfile.mkdtemp()) / "haende.jsonl"
        p = ha.Protokoll(pfad)
        p({"a": 1})
        p({"ä": "ö"})
        self.assertEqual([json.loads(z) for z in pfad.read_text(encoding="utf-8").splitlines()], [{"a": 1}, {"ä": "ö"}])
        pfad.write_bytes(b"x" * (ha.PROTOKOLL_MAX_BYTES + 1))
        p({"neu": 1})
        self.assertEqual(json.loads(pfad.read_text()), {"neu": 1})
        self.assertEqual(pfad.with_suffix(".jsonl.1").stat().st_size, ha.PROTOKOLL_MAX_BYTES + 1, "nichts wird gelöscht")
        with self.assertRaises(OSError):
            ha.Protokoll(None)({"x": 1})

    def test_ohne_anzeige_gibt_es_keine_aufzeichnung_aber_die_haende_laufen(self):
        import os

        alt = os.environ.pop("DISPLAY", None)
        try:
            b = ha.baue_haende("linux", "kde1", None, backend=SimpleNamespace(), fenster_zustand=lambda k: (False, False, None))
        finally:
            if alt is not None:
                os.environ["DISPLAY"] = alt
        self.assertIsNotNone(b.engine)
        self.assertEqual(b.quellen, [])
        b.starten()
        b.stoppen()


if __name__ == "__main__":
    unittest.main()
