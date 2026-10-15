"""G11: der WorldDOM im Ganzen angeschlossen — Befehle, Relay, Starter, Körper-Anwendung, Plattform-Anbindung, Dienst und das Werkzeug des Agenten."""

from __future__ import annotations

import tempfile
import base64
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge import transport as tr
from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import weltdom as wd
from augen_haende_bridge.koerper import weltdom_anbindung as wa
from augen_haende_bridge.koerper import weltdom_befehle as wb
from augen_haende_bridge.koerper.weltdom_dienst import WeltdomDienst
from tests.test_anzeigeort import baue, ereignis, falsche_sitzung
from tests.test_koerper_anwendung import _event, _gestartet

ZIEL = "kde1:window:77"


class BefehlsTests(unittest.TestCase):
    def test_gueltige_befehle_werden_bereinigt_zurueckgegeben(self):
        self.assertEqual(wb.pruefe_args("liste", {}), {})
        self.assertEqual(wb.pruefe_args("liste", {"herkunft": "real", "rolle": "button", "text": "ok", "neu_messen": False})["herkunft"], "real")
        self.assertEqual(wb.pruefe_args("aktion", {"knoten": "k1", "aktion": "klick"}), {"knoten": "k1", "aktion": "klick"})
        self.assertEqual(wb.pruefe_args("aktion", {"knoten": "k1", "aktion": "text_setzen", "text": ""})["text"], "")
        self.assertEqual(wb.pruefe_args("zeige", {"punkt": (3, 4), "modus": "praesentieren"}), {"punkt": [3, 4], "modus": "praesentieren", "empfaenger": []})
        self.assertEqual(wb.pruefe_args("anker_neu", {"name": "Slot", "punkt": [1, 2]}), {"name": "Slot", "punkt": [1, 2]})
        self.assertEqual(wb.pruefe_args("anker_neu", {"name": "Schatten", "herkunft": "projected"})["herkunft"], "projected")
        self.assertEqual(wb.pruefe_args("anker_weg", {"knoten": "k1"}), {"knoten": "k1"})

    def test_ungueltiges_wird_abgelehnt(self):
        schlecht = [("liste", {"herkunft": "erfunden"}), ("liste", {"neu_messen": "ja"}), ("liste", {"x": 1}), ("liste", None), ("tanzen", {}), ("aktion", {"aktion": "klick"}),
                    ("aktion", {"knoten": "k", "aktion": "loeschen"}), ("aktion", {"knoten": "k", "aktion": "text_setzen"}), ("aktion", {"knoten": "k", "aktion": "klick", "text": 5}),
                    ("aktion", {"knoten": "x" * 121, "aktion": "klick"}), ("zeige", {"punkt": [1], "modus": "praesentieren"}), ("zeige", {"punkt": [1, 2], "modus": "heimlich"}),
                    ("zeige", {"punkt": [1, 2], "modus": "einfuegen", "aktion": "ziehen"}), ("zeige", {"punkt": [1, 2], "modus": "praesentieren", "empfaenger": ["a"] * 9}),
                    ("zeige", {"punkt": [1, 2], "modus": "praesentieren", "urheber": "ich"}), ("anker_neu", {"name": ""}), ("anker_neu", {"name": "x", "herkunft": "real"}),
                    ("anker_neu", {"name": "x", "punkt": ["a", 1]}), ("anker_weg", {}), ("anker_weg", {"knoten": "\x00"})]
        for befehl, args in schlecht:
            self.assertIsNone(wb.pruefe_args(befehl, args), (befehl, args))

    def test_der_urheber_kommt_nur_intern_durch(self):
        self.assertIsNone(wb.pruefe_args("zeige", {"punkt": [1, 2], "modus": "praesentieren", "urheber": "Codex"}))
        self.assertEqual(wb.pruefe_args("zeige", {"punkt": [1, 2], "modus": "praesentieren", "urheber": "Codex"}, intern=True)["urheber"], "Codex")
        self.assertIsNone(wb.pruefe_args("zeige", {"punkt": [1, 2], "modus": "praesentieren", "urheber": "x" * 61}, intern=True))

    def test_nur_handelndes_braucht_die_lease(self):
        self.assertTrue(wb.braucht_lease("aktion", {"aktion": "klick"}))
        self.assertTrue(wb.braucht_lease("aktion", {"aktion": "text_setzen"}))
        self.assertTrue(wb.braucht_lease("zeige", {"modus": "einfuegen"}))
        for befehl, args in (("aktion", {"aktion": "lesen"}), ("zeige", {"modus": "praesentieren"}), ("liste", {}), ("anker_neu", {}), ("anker_weg", {})):
            self.assertFalse(wb.braucht_lease(befehl, args), befehl)


class RelayTests(unittest.TestCase):
    def setUp(self):
        from client_vps import anzeigeorte as ao

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        self.relay = tr.Relay(ao.baue_principals(d), tr.Journal(tmp / "j.sqlite3"))
        self.desktop = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_control_terminals))
        self.starter = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_serve_terminals))

    AUFTRAG = {"terminal_id": "t-1", "auftrag_id": "w-1", "befehl": "liste", "ziel": ZIEL, "lease_bis_ms": 0, "seq": None, "args": {}}
    ERGEBNIS = {"terminal_id": "t-1", "auftrag_id": "w-1", "status": "ok", "daten": {"knoten": []}}

    def test_auftrag_nur_vom_starter_und_streng(self):
        self.assertEqual(self.relay.payload(self.starter, "weltdom_auftrag", dict(self.AUFTRAG))["befehl"], "liste")
        for kaputt in ({"befehl": "tanzen"}, {"x": 1}, {"seq": -1}, {"args": []}, {"args": {"x": "y" * 3000}}, {"ziel": ""}, {"lease_bis_ms": -1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                self.relay.payload(self.starter, "weltdom_auftrag", {**self.AUFTRAG, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.desktop, "weltdom_auftrag", dict(self.AUFTRAG))

    def test_ergebnis_nur_vom_desktop_und_begrenzt(self):
        self.assertEqual(self.relay.payload(self.desktop, "weltdom_ergebnis", dict(self.ERGEBNIS))["status"], "ok")
        for kaputt in ({"status": ""}, {"status": "x" * 31}, {"daten": []}, {"daten": {"x": "y" * 210_000}}, {"x": 1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)[:40]):
                self.relay.payload(self.desktop, "weltdom_ergebnis", {**self.ERGEBNIS, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.starter, "weltdom_ergebnis", dict(self.ERGEBNIS))


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.l, self.fv = baue()
        for o in ("windows", "kde1"):
            self.l.handle(ereignis("anzeigeorte_request", {}, o))
        self.s = falsche_sitzung(self.l, "t-1")
        self.l.register.anlegen("t-1", "Codex", strom="codex", zustand="running")
        self.l.register.anlegen("t-2", "Claude", strom="claude", zustand="running")
        self.l.anzeige["t-1"] = self.l.ziel["t-1"] = "kde1"
        self.l.ziel_info["t-1"] = {"target_id": ZIEL, "zustand": "ok", "faehigkeit": "frisch", "seit_ms": 1}
        self.fv.gesendet.clear()

    def befehl(self, befehl, args, antwort=None, **kw):
        self.fv.gesendet.clear()
        fertig = threading.Event()

        def koerper():
            ende = time.monotonic() + 3
            while time.monotonic() < ende and not fertig.is_set():
                for ort, kind, p in list(self.fv.gesendet):
                    if kind == "weltdom_auftrag" and antwort is not None:
                        self.l.handle(ereignis("weltdom_ergebnis", {"terminal_id": p["terminal_id"], "auftrag_id": p["auftrag_id"], "status": antwort.get("status", "ok"), "daten": antwort.get("daten", {})}, "kde1"))
                        return
                time.sleep(0.01)

        t = threading.Thread(target=koerper)
        t.start()
        r = self.l.weltdom_befehl("t-1", {"befehl": befehl, "args": args, **kw})
        fertig.set()
        t.join(5)
        return r

    def test_lesende_befehle_brauchen_keine_lease_und_gehen_an_den_zielort(self):
        r = self.befehl("liste", {"herkunft": "real"}, antwort={"daten": {"knoten": [{"id": "k"}], "quellen": {"cdp": "ok"}}})
        self.assertEqual((r["ok"], r["status"], r["knoten"], r["quellen"]), (True, "ok", [{"id": "k"}], {"cdp": "ok"}))
        p = self.fv.an("kde1", "weltdom_auftrag")[0]
        self.assertEqual((p["befehl"], p["ziel"], p["lease_bis_ms"], p["args"]), ("liste", ZIEL, 0, {"herkunft": "real"}))
        self.assertEqual(self.fv.an("windows", "weltdom_auftrag"), [])
        r = self.befehl("aktion", {"knoten": "k", "aktion": "lesen"}, antwort={"daten": {"gelesen": "x"}, "status": "ausgefuehrt"})
        self.assertEqual((r["ok"], r["gelesen"]), (True, "x"))
        r = self.befehl("zeige", {"punkt": [1, 2], "modus": "praesentieren"}, antwort={"status": "praesentiert"})
        self.assertTrue(r["ok"])

    def test_handelnde_befehle_verlangen_die_lease_des_agenten(self):
        for befehl, args in (("aktion", {"knoten": "k", "aktion": "klick"}), ("aktion", {"knoten": "k", "aktion": "text_setzen", "text": "x"}), ("zeige", {"punkt": [1, 2], "modus": "einfuegen"})):
            r = self.befehl(befehl, args)
            self.assertEqual((r["ok"], r["reason"], r["status"]), (False, "lease_fehlt", "abgelehnt"), befehl)
            self.assertEqual(self.fv.an("kde1", "weltdom_auftrag"), [])
        lease = self.l.lease_befehl("t-1", {})
        self.assertTrue(lease["ok"])
        r = self.befehl("aktion", {"knoten": "k", "aktion": "klick"}, antwort={"status": "ausgefuehrt", "daten": {"ruecklese": {"bestaetigt": True}}})
        self.assertEqual((r["ok"], r["ruecklese"]), (True, {"bestaetigt": True}))
        self.assertGreater(self.fv.an("kde1", "weltdom_auftrag")[0]["lease_bis_ms"], int(time.time() * 1000))
        self.l.ziel_info["t-1"]["target_id"] = ZIEL
        self.l.leases._leases[ZIEL].halter = "t-2"
        self.assertEqual(self.befehl("aktion", {"knoten": "k", "aktion": "klick"})["reason"], "lease_fremd")

    def test_ungueltige_befehle_und_ziele_werden_vor_dem_senden_abgelehnt(self):
        for befehl, args in (("liste", {"herkunft": "x"}), ("tanzen", {}), ("aktion", {})):
            self.assertEqual(self.befehl(befehl, args)["reason"], "befehl_ungueltig")
        self.l.ziel_info["t-1"]["target_id"] = "desktop"
        self.assertEqual(self.befehl("liste", {})["reason"], "kein_fenster_ziel")
        self.assertEqual(self.fv.an("kde1", "weltdom_auftrag"), [])

    def test_empfaenger_namen_werden_zu_terminal_ids_und_der_urheber_wird_ergaenzt(self):
        self.befehl("zeige", {"punkt": [1, 2], "modus": "praesentieren", "empfaenger": ["claude"]}, antwort={"status": "praesentiert"})
        a = self.fv.an("kde1", "weltdom_auftrag")[0]["args"]
        self.assertEqual((a["empfaenger"], a["urheber"]), (["t-2"], "Codex"))
        self.assertEqual(self.befehl("zeige", {"punkt": [1, 2], "modus": "praesentieren", "empfaenger": ["niemand"]})["reason"], "empfaenger_unbekannt")

    def test_stoppgrund_entzieht_die_lease(self):
        self.l.lease_befehl("t-1", {})
        r = self.befehl("aktion", {"knoten": "k", "aktion": "klick"}, antwort={"status": "abgelehnt", "daten": {"grund": "daniel_uebernimmt"}})
        self.assertEqual((r["ok"], r["grund"]), (False, "daniel_uebernimmt"))
        self.assertIsNone(self.l.leases.von(ZIEL))

    def test_schweigen_ergebnis_von_falschem_ort_und_ein_auftrag_zugleich(self):
        import client_vps.terminal_launcher as tl

        alt, tl.WELTDOM_WARTEN_S = tl.WELTDOM_WARTEN_S, 0.3
        self.addCleanup(lambda: setattr(tl, "WELTDOM_WARTEN_S", alt))
        r = self.befehl("liste", {})
        self.assertEqual((r["ok"], r["reason"]), (False, "keine_antwort"))
        self.assertEqual(self.l._weltdom_wartend, {})
        wartend = {"terminal_id": "t-1", "ziel": ZIEL, "event": threading.Event(), "ergebnis": None}
        self.l._weltdom_wartend["w-1"] = wartend
        self.l.handle(ereignis("weltdom_ergebnis", {"terminal_id": "t-1", "auftrag_id": "w-1", "status": "ok", "daten": {}}, "windows"))
        self.assertFalse(wartend["event"].is_set())
        self.assertEqual(self.l.abgewiesen["weltdom_ergebnis_vom_falschen_ort"], 1)
        self.l.handle(ereignis("weltdom_ergebnis", {"terminal_id": "t-1", "auftrag_id": "w-9", "status": "ok", "daten": {}}, "kde1"))
        self.assertEqual(self.l.abgewiesen["weltdom_ergebnis_unbekannt"], 1)
        self.assertEqual(self.l.weltdom_befehl("t-1", {"befehl": "liste", "args": {}})["reason"], "weltdom_laeuft_schon")

    def test_agent_request_leitet_weltdom_weiter(self):
        self.s.token = "tok"
        r = self.l.agent_request({"terminal_id": "t-1", "token": "tok", "cmd": "weltdom", "befehl": "tanzen", "args": {}})
        self.assertEqual(r["reason"], "befehl_ungueltig")


class AnwendungTests(unittest.TestCase):
    def maschine(self):
        app, gui, gebaut = _gestartet()
        aufrufe = []

        class Dienst:
            def liste(self_, ziel, **kw):
                aufrufe.append(("liste", ziel, kw))
                return {"status": "ok", "knoten": [], "quellen": {}}

            def aktion(self_, tid, ziel, knoten, aktion, text, erwartung, seq, **kw):
                aufrufe.append(("aktion", knoten, aktion, text, erwartung, seq, kw))
                return {"status": "ausgefuehrt", "grund": "", "ruecklese": {"bestaetigt": True}}

            def zeige(self_, tid, ziel, punkt, seq, urheber, modus, empfaenger, **kw):
                aufrufe.append(("zeige", punkt, modus, empfaenger, urheber, kw))
                return {"status": "praesentiert"}

            def anker_neu(self_, tid, ziel, name, punkt, seq, urheber, herkunft):
                aufrufe.append(("anker_neu", name, punkt, herkunft))
                return {"status": "ok"}

            def anker_weg(self_, ziel, knoten):
                aufrufe.append(("anker_weg", knoten))
                return {"status": "ok"}

            def markiert(self_, ziel, **kw):
                aufrufe.append(("markiert", ziel, kw))
                return {"status": "ok", "_jpeg": b"\xff\xd8JPEG", "breite": 640, "hoehe": 480, "tabelle": [{"nr": 1, "knoten": "k1"}], "weggelassen": 0}

        app.weltdom_dienst = Dienst()
        return app, aufrufe

    def auftrag(self, befehl, args, **kw):
        p = {"terminal_id": "t-1", "auftrag_id": "w-1", "befehl": befehl, "ziel": ZIEL, "lease_bis_ms": int(time.time() * 1000) + 60_000, "seq": 3, "args": args}
        p.update(kw)
        return p

    def warte(self, app, n=1):
        ende = time.monotonic() + 3
        while time.monotonic() < ende and len([g for g in app.runtime.gesendet if g[0] == "weltdom_ergebnis"]) < n:
            time.sleep(0.02)
        return [g[1] for g in app.runtime.gesendet if g[0] == "weltdom_ergebnis"]

    def test_jeder_befehl_geht_an_den_dienst_mit_rechten_profil_und_lease(self):
        app, aufrufe = self.maschine()
        for befehl, args in (("liste", {"herkunft": "real"}), ("aktion", {"knoten": "k1", "aktion": "klick", "erwartung": "x"}), ("zeige", {"punkt": [4, 5], "modus": "praesentieren", "empfaenger": ["t-2"], "urheber": "Codex"}),
                             ("anker_neu", {"name": "A", "punkt": [1, 2]}), ("anker_weg", {"knoten": "k9"})):
            app.ereignis(_event("weltdom_auftrag", self.auftrag(befehl, args, auftrag_id=f"w-{befehl}")))
        erg = self.warte(app, 5)
        self.assertEqual(sorted(e["status"] for e in erg), ["ausgefuehrt", "ok", "ok", "ok", "praesentiert"])
        arten = {a[0]: a for a in aufrufe}
        self.assertEqual(arten["aktion"][1:6], ("k1", "klick", None, "x", 3))
        self.assertEqual((arten["aktion"][6]["haende_erlaubt"], arten["aktion"][6]["profil"], arten["aktion"][6]["lease_grund"]), (True, "geteilte_maus", ""))
        self.assertEqual(arten["zeige"][1:5], ((4, 5), "praesentieren", ("t-2",), "Codex"))
        self.assertEqual(arten["anker_neu"][1:], ("A", (1, 2), "authored"))

    def test_markiert_sendet_das_bild_als_frame_und_die_tabelle_als_ergebnis_ohne_die_bilddaten(self):
        app, aufrufe = self.maschine()
        app.ereignis(_event("weltdom_auftrag", self.auftrag("markiert", {"neu_messen": False}, auftrag_id="w-m")))
        erg = self.warte(app, 1)[0]
        self.assertEqual((erg["status"], erg["daten"]["tabelle"], "_jpeg" in erg["daten"]), ("ok", [{"nr": 1, "knoten": "k1"}], False))
        frames = [g[1] for g in app.runtime.gesendet if g[0] == "frame"]
        self.assertEqual(len(frames), 1)
        self.assertEqual((frames[0]["terminal_id"], frames[0]["aufnahme"], frames[0]["source"], frames[0]["width"]), ("t-1", "markiert", "synthetic", 640))
        self.assertEqual(base64.b64decode(frames[0]["data"]), b"\xff\xd8JPEG")
        self.assertEqual(aufrufe[0][2], {"neu_messen": False})
        self.assertLess([g[0] for g in app.runtime.gesendet].index("frame"), [g[0] for g in app.runtime.gesendet].index("weltdom_ergebnis"), "erst das Bild, dann das Ergebnis")

    def test_lease_und_haende_werden_dem_dienst_gemeldet(self):
        app, aufrufe = self.maschine()
        app.ereignis(_event("weltdom_auftrag", self.auftrag("aktion", {"knoten": "k", "aktion": "klick"}, lease_bis_ms=0, auftrag_id="w-a")))
        app.agenten["t-1"].haende = False
        app.ereignis(_event("weltdom_auftrag", self.auftrag("aktion", {"knoten": "k", "aktion": "klick"}, lease_bis_ms=1, auftrag_id="w-b")))
        self.warte(app, 2)
        k = {a[6]["lease_grund"]: a[6] for a in aufrufe}
        self.assertIn("lease_fehlt", k)
        self.assertIn("lease_abgelaufen", k)
        self.assertFalse(k["lease_abgelaufen"]["haende_erlaubt"])

    def test_ohne_dienst_ungueltig_und_unbekannter_agent_werden_abgelehnt_und_fehler_gemeldet(self):
        app, aufrufe = self.maschine()
        app.ereignis(_event("weltdom_auftrag", self.auftrag("aktion", {"aktion": "klick"}, auftrag_id="w-a")))
        app.ereignis(_event("weltdom_auftrag", self.auftrag("liste", {}, terminal_id="t-99", auftrag_id="w-b")))
        app.weltdom_dienst.liste = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        app.ereignis(_event("weltdom_auftrag", self.auftrag("liste", {}, auftrag_id="w-c")))
        dienst, app.weltdom_dienst = app.weltdom_dienst, None
        app.ereignis(_event("weltdom_auftrag", self.auftrag("liste", {}, auftrag_id="w-d")))
        erg = {e["auftrag_id"]: (e["status"], e["daten"].get("grund")) for e in self.warte(app, 4)}
        self.assertEqual(erg, {"w-a": ("abgelehnt", "befehl_ungueltig"), "w-b": ("abgelehnt", "kein_ziel"), "w-c": ("fehler", "ausfuehrung_fehlgeschlagen"), "w-d": ("abgelehnt", "weltdom_nicht_verfuegbar")})
        self.assertEqual(aufrufe, [])

    def test_das_zeichen_geht_in_die_arbeitsflaeche_fuer_agent_und_gewaehlte_und_nur_dorthin(self):
        from augen_haende_bridge.koerper.komposition import Arbeitsflaechen

        app, _ = self.maschine()
        app.arbeit = Arbeitsflaechen()
        oid = app.zeige_overlay("t-1", ZIEL, (0.25, 1.5), "Codex: Knopf", ("t-2", "t-1"))
        o = app.arbeit.dokument(ZIEL).objekte[oid]
        self.assertEqual((o.art, o.empfaenger, o.bildschirm, o.punkte), ("marker", ("t-1", "t-2"), True, [(0.25, 1.0)]))
        self.assertEqual([x.id for x in app.arbeit.dokument(ZIEL).fuer_empfaenger("t-3")], [])


class FakeFenster:
    def __init__(self, hwnd, title, pid):
        self.hwnd, self.title, self.process_id = hwnd, title, pid


class PlattformTests(unittest.TestCase):
    def bauen(self, name="linux", **kw):
        plattform = SimpleNamespace(name=name, quelle=SimpleNamespace(_api=None), fenster_bild=kw.pop("fenster_bild", None),
                                    capture_api=kw.pop("capture_api", SimpleNamespace(capture_bgra=lambda rect: b"\x00" * ((rect[2] - rect[0]) * (rect[3] - rect[1]) * 4))))
        ref = kw.pop("ref", [])
        return wa.baue_weltdom(plattform, "kde1", None, ref, fenster_zustand=kw.pop("fenster_zustand", lambda k: (True, False, (10, 20, 110, 70))), **kw), plattform

    def test_ziel_stand_bild_und_fremde_orte(self):
        d, _ = self.bauen(fenster_liste=lambda: [FakeFenster(77, "Fenster", 5)])
        self.assertEqual(d._ziel_stand(ZIEL), ea.ZielStand(True, (10, 20, 110, 70), False, 77, None))
        self.assertIsNone(d._ziel_stand("windows:window:77"))
        self.assertIsNone(d._ziel_stand("desktop"))
        bgra, b, h, rect = d._bild(ZIEL)
        self.assertEqual((b, h, rect, len(bgra)), (100, 50, (10, 20, 110, 70), 100 * 50 * 4), "ohne Fensteraufnahme der Bildschirmausschnitt des Fensters")
        d2, _ = self.bauen(fenster_bild=lambda k: (b"\x01" * 16, 2, 2), fenster_liste=lambda: [])
        self.assertEqual(d2._bild(ZIEL)[:3], (b"\x01" * 16, 2, 2))
        d3, _ = self.bauen(fenster_zustand=lambda k: (True, True, None), fenster_liste=lambda: [])
        self.assertIsNone(d3._bild(ZIEL), "ein minimiertes Fenster wird nicht aufgenommen")
        d4, _ = self.bauen(fenster_zustand=lambda k: (False, False, None), fenster_liste=lambda: [])
        self.assertIsNone(d4._bild(ZIEL))

    def test_ohne_browser_anschluss_und_ohne_bedienungshilfen_ist_beides_nicht_verfuegbar(self):
        d, _ = self.bauen(fenster_liste=lambda: [FakeFenster(77, "Fenster", 5)], cdp_port=1)
        self.assertIsNone(d._cdp_seite(ZIEL))
        self.assertIsNone(d._cdp_seite("windows:window:77"))
        self.assertIsNone(d._ui_quelle("windows:window:77"))
        self.assertIsNone(d._ui_quelle("kde1:window:999"), "ein Fenster, das es nicht gibt, hat keine Quelle")

    def test_bezug_und_overlay_laufen_ueber_die_anwendung(self):
        gesehen = []

        class App:
            def _bildbezug(self_, tid, seq):
                gesehen.append(("bezug", tid, seq))
                return ea.Bildbezug(ZIEL, 3, 5, 10, 10, (0, 0, 10, 10), None, None, None) if tid == "t-1" else None

            def zeige_overlay(self_, tid, ziel, rel, text, empf):
                gesehen.append(("overlay", tid, ziel, rel, text, empf))
                return "o-1"

        d, _ = self.bauen(ref=[App()], fenster_liste=lambda: [])
        self.assertEqual(d._bezug("t-1", ZIEL, 3).seq, 3)
        self.assertIsNone(d._bezug("t-1", "kde1:window:5", 3), "ein Bild eines anderen Ziels ist keine Grundlage")
        self.assertIsNone(d._bezug("t-9", ZIEL, 3))
        self.assertEqual(d._overlay("t-1", ZIEL, (0.1, 0.2), "x", ["t-2"]), "o-1")
        d2, _ = self.bauen(fenster_liste=lambda: [])
        self.assertIsNone(d2._bezug("t-1", ZIEL, 3))
        self.assertIsNone(d2._overlay("t-1", ZIEL, (0.1, 0.2), "x", []))

    def test_authored_anker_werden_geladen(self):
        pfad = Path(tempfile.mkdtemp()) / "weltdom.json"
        w = wd.WeltDom(pfad)
        w.anker_anlegen(ZIEL, "Slot", (1, 1, 5, 5), urheber="daniel", jetzt_ms=1)
        d, _ = self.bauen(pfad=pfad, fenster_liste=lambda: [])
        self.assertEqual([k.name for k in d.welt.liste(ZIEL)], ["Slot"])


class DienstTests(unittest.TestCase):
    def dienst(self, **kw):
        welt = wd.WeltDom()
        werte = dict(jetzt_ms=lambda: 5000, schlafen=lambda s: None)
        werte.update(kw)
        return WeltdomDienst(welt, **werte), welt

    def test_ohne_quellen_sagt_die_antwort_warum_nicht_eine_leere_liste(self):
        d, _ = self.dienst()
        r = d.liste(ZIEL)
        self.assertEqual((r["status"], r["knoten"]), ("ok", []))
        self.assertTrue(r["quellen"]["cdp"].startswith("nicht verfügbar"))
        self.assertTrue(r["quellen"]["ui"].startswith("nicht verfügbar"))
        self.assertTrue(r["quellen"]["bild"].startswith("nicht verfügbar"))

    def test_quellenfehler_werden_gemeldet_nicht_verschluckt(self):
        def kaputt(z):
            raise RuntimeError("boom")

        d, _ = self.dienst(cdp_seite=kaputt, ui_quelle=kaputt, bild=kaputt)
        q = d.messen(ZIEL)
        self.assertEqual((q["cdp"], q["ui"], q["bild"]), ("fehler: RuntimeError",) * 3)

    def test_handelnde_aktion_ohne_haende_oder_lease_geschieht_nichts_lesen_geht(self):
        welt = wd.WeltDom()
        welt.ersetze(ZIEL, "real", "atspi", [wd.Knoten("k1", ZIEL, "real", "atspi", "button", "OK", gemessen_ms=4000, faehigkeiten=("klick", "lesen"), aufloesung="atspi", anker={"pid": 1, "pfad": [], "rolle": "button", "name": "OK"})])
        d = WeltdomDienst(welt, jetzt_ms=lambda: 5000, schlafen=lambda s: None, ui_quelle=lambda z: self.fail("die Quelle darf nicht angefasst werden"))
        self.assertEqual(d.aktion("t-1", ZIEL, "k1", "klick", None, None, 1, haende_erlaubt=False, profil="geteilte_maus", lease_grund=""), {"status": "abgelehnt", "grund": "haende_aus"})
        self.assertEqual(d.aktion("t-1", ZIEL, "k1", "klick", None, None, 1, haende_erlaubt=True, profil="geteilte_maus", lease_grund="lease_fehlt"), {"status": "abgelehnt", "grund": "lease_fehlt"})

    def test_anker_anlegen_und_entfernen_nur_eigene(self):
        gesehen = []
        d, welt = self.dienst(bezug=lambda tid, ziel, seq: ea.Bildbezug(ZIEL, 3, 4000, 100, 50, (10, 20, 110, 70), None, None, (10, 20, 110, 70)))
        r = d.anker_neu("t-1", ZIEL, "Slot", (50, 25), 3, "Codex")
        self.assertEqual((r["status"], r["knoten"]["herkunft"], r["knoten"]["urheber"], r["knoten"]["rect"]), ("ok", "authored", "Codex", [48, 33, 72, 57]))
        self.assertEqual(d.anker_neu("t-1", ZIEL, "", (1, 1), 3, "Codex")["status"], "abgelehnt")
        k = welt.liste(ZIEL)[0]
        self.assertEqual(d.anker_weg(ZIEL, k.id)["status"], "ok")
        self.assertEqual(d.anker_weg(ZIEL, "gibt-es-nicht")["status"], "unaufloesbar")
        welt.ersetze(ZIEL, "real", "atspi", [wd.Knoten("rea", ZIEL, "real", "atspi", "button", "OK")])
        self.assertEqual(d.anker_weg(ZIEL, "rea"), {"status": "abgelehnt", "grund": "nur_eigene_anker_entfernbar"})
        d2, _ = self.dienst()
        self.assertEqual(d2.anker_neu("t-1", ZIEL, "Slot", (1, 1), 3, "x"), {"status": "abgelehnt", "grund": "frame_unbekannt"})
        self.assertEqual(d2.anker_neu("t-1", ZIEL, "Ohne Ort", None, 3, "x")["status"], "abgelehnt", "ein bewusst angelegter Knoten ohne Ort ist nur projiziert erlaubt")

    def test_zeigen_darstellung_einfuegung_und_die_zugangsregeln(self):
        b = ea.Bildbezug(ZIEL, 3, 4000, 100, 50, (10, 20, 110, 70), 77, None, (10, 20, 110, 70))
        marken = []
        d, welt = self.dienst(bezug=lambda tid, ziel, seq: b, ziel_stand=lambda z: ea.ZielStand(True, (10, 20, 110, 70), False, 77, None), overlay=lambda tid, z, rel, text, emp: marken.append((rel, text, emp)) or "o-1")
        r = d.zeige("t-1", ZIEL, (50, 25), 3, "Codex", "praesentieren", ("t-2",), neu_messen=False)
        self.assertEqual((r["status"], r["wirkung_in_anwendung"], marken), ("praesentiert", False, [((0.5, 0.5), "Codex: hier", ("t-2",))]))
        r = d.zeige("t-1", ZIEL, (50, 25), 3, "Codex", "einfuegen", (), haende_erlaubt=False, neu_messen=False)
        self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "haende_aus"))
        r = d.zeige("t-1", ZIEL, (50, 25), 3, "Codex", "einfuegen", (), haende_erlaubt=True, lease_grund="lease_fehlt", neu_messen=False)
        self.assertEqual((r["status"], r["grund"]), ("abgelehnt", "lease_fehlt"))
        self.assertEqual(d.zeige("t-1", ZIEL, (50, 25), 3, "Codex", "heimlich", (), neu_messen=False)["grund"], "modus_unbekannt")
        d2, _ = self.dienst()
        self.assertEqual(d2.zeige("t-1", ZIEL, (1, 1), 3, "x", "praesentieren", (), neu_messen=False)["grund"], "frame_unbekannt")
        d3, _ = self.dienst(bezug=lambda *a: b, ziel_stand=lambda z: None)
        r = d3.zeige("t-1", ZIEL, (50, 25), 3, "x", "praesentieren", (), neu_messen=False)
        self.assertEqual(r["grund"], "arbeitsflaeche_nicht_verfuegbar")

    def test_die_gestenliste_ist_begrenzt(self):
        b = ea.Bildbezug(ZIEL, 3, 4000, 100, 50, (10, 20, 110, 70), 77, None, (10, 20, 110, 70))
        d, _ = self.dienst(bezug=lambda *a: b, ziel_stand=lambda z: ea.ZielStand(True, (10, 20, 110, 70), False, 77, None), overlay=lambda *a: "o")
        for _ in range(120):
            d.zeige("t-1", ZIEL, (5, 5), 3, "x", "praesentieren", (), neu_messen=False)
        self.assertEqual(len(d.gesten), 100)


class CliTests(unittest.TestCase):
    def anfrage(self, *argv):
        from unittest import mock

        from client_vps import bridge_cli

        with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
            code = bridge_cli.main(list(argv))
        return code, ask.call_args.args[0] if ask.call_args else None

    def test_alle_befehle(self):
        faelle = {
            ("weltdom",): {"cmd": "weltdom", "befehl": "liste", "args": {}},
            ("weltdom", "--herkunft=real", "--rolle=button", "--text=OK", "--alt"): {"cmd": "weltdom", "befehl": "liste", "args": {"herkunft": "real", "rolle": "button", "text": "OK", "neu_messen": False}},
            ("knoten", "k1", "klick"): {"cmd": "weltdom", "befehl": "aktion", "args": {"knoten": "k1", "aktion": "klick"}},
            ("knoten", "k1", "lesen"): {"cmd": "weltdom", "befehl": "aktion", "args": {"knoten": "k1", "aktion": "lesen"}},
            ("knoten", "k1", "text", "Hallo", "Welt", "--erwartung=Hallo Welt"): {"cmd": "weltdom", "befehl": "aktion", "args": {"knoten": "k1", "aktion": "text_setzen", "text": "Hallo Welt", "erwartung": "Hallo Welt"}},
            ("zeige", "10", "20"): {"cmd": "weltdom", "befehl": "zeige", "args": {"punkt": [10, 20], "modus": "praesentieren"}},
            ("zeige", "10", "20", "--an=Claude,Gemgem"): {"cmd": "weltdom", "befehl": "zeige", "args": {"punkt": [10, 20], "modus": "praesentieren", "empfaenger": ["Claude", "Gemgem"]}},
            ("zeige", "10", "20", "--einfuegen", "klick"): {"cmd": "weltdom", "befehl": "zeige", "args": {"punkt": [10, 20], "modus": "einfuegen", "aktion": "klick"}},
            ("zeige", "10", "20", "--einfuegen", "text", "Hi"): {"cmd": "weltdom", "befehl": "zeige", "args": {"punkt": [10, 20], "modus": "einfuegen", "aktion": "text_setzen", "text": "Hi"}},
            ("anker", "Slot", "5", "6"): {"cmd": "weltdom", "befehl": "anker_neu", "args": {"name": "Slot", "herkunft": "authored", "punkt": [5, 6]}},
            ("anker", "Schatten", "--projiziert"): {"cmd": "weltdom", "befehl": "anker_neu", "args": {"name": "Schatten", "herkunft": "projected"}},
            ("anker-weg", "k9"): {"cmd": "weltdom", "befehl": "anker_weg", "args": {"knoten": "k9"}},
            ("markiert",): {"cmd": "weltdom", "befehl": "markiert", "args": {"neu_messen": True}},
            ("markiert", "--alt"): {"cmd": "weltdom", "befehl": "markiert", "args": {"neu_messen": False}},
            ("knoten", "k1", "klick", "--seq=4"): {"cmd": "weltdom", "befehl": "aktion", "args": {"knoten": "k1", "aktion": "klick"}, "seq": 4},
        }
        for argv, erwartet in faelle.items():
            code, gesendet = self.anfrage(*argv)
            self.assertEqual((code, gesendet), (0, erwartet), argv)

    def test_falsche_aufrufe_senden_nichts(self):
        for argv in (("weltdom", "x"), ("weltdom", "--quatsch"), ("knoten", "k1"), ("knoten", "k1", "tanzen"), ("knoten", "k1", "text"), ("knoten", "k1", "klick", "extra"), ("zeige", "a", "b"),
                     ("zeige", "1", "2", "klick"), ("zeige", "1", "2", "--einfuegen", "tanzen"), ("zeige", "1"), ("anker",), ("anker", "n", "1"), ("anker-weg",), ("weltdom", "--seq=x")):
            code, gesendet = self.anfrage(*argv)
            self.assertEqual((code, gesendet), (2, None), argv)

    def test_die_hilfe_nennt_alle_befehle(self):
        from client_vps import bridge_cli

        for befehl in ("weltdom", "knoten", "zeige", "anker", "anker-weg"):
            self.assertIn(befehl, bridge_cli.__doc__)


if __name__ == "__main__":
    unittest.main()
