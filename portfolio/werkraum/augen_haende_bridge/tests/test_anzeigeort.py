"""G06: mehrere Desktops als Anzeigeorte. Konfiguration, Verteilung der Nachrichten, Arbeitsziel unabhängig vom Anzeigeort, getrennte Meldungen, Körper-Seite."""

from __future__ import annotations

import asyncio
import base64
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge.transport import Journal, Principal, ProtocolError, Relay
from client_vps import anzeigeorte as ao
from client_vps import terminal_launcher as tl
from client_vps.terminal_launcher import Launcher, Ort, StartEntry

CLI = Path(__file__).resolve().parent.parent / "client_vps" / "bridge_cli.py"
DESKTOPS = Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json"
ENV = {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40}


class KonfigurationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ao-"))

    def lade(self, **kw):
        return ao.lade_desktops(kw.pop("pfad", DESKTOPS), self.tmp, kw.pop("env", ENV))

    def test_die_ausgelieferte_datei_nennt_windows_kde1_kde2(self):
        d = self.lade()
        self.assertEqual([x.ort for x in d], ["windows", "kde1", "kde2"])

    def test_windows_behaelt_seine_bisherigen_kennungen(self):
        w = self.lade()[0]
        self.assertEqual((w.session_id, w.agent_session_id, w.target_id, w.token, w.agent_token), ("desktop", "agent", "desktop-main", "d" * 40, "a" * 40))

    def test_die_anderen_bekommen_eigene_kennungen_und_private_token_dateien(self):
        kde1 = self.lade()[1]
        self.assertEqual((kde1.session_id, kde1.agent_session_id, kde1.target_id), ("desktop-kde1", "agent-kde1", "desktop-kde1"))
        for name in ("desktop-kde1.token", "agent-kde1.token"):
            pfad = self.tmp / "tokens" / name
            self.assertEqual(stat.S_IMODE(pfad.stat().st_mode), 0o600)
            self.assertGreaterEqual(len(pfad.read_text().strip()), 32)
        self.assertEqual(stat.S_IMODE((self.tmp / "tokens").stat().st_mode), 0o700)

    def test_die_token_bleiben_beim_naechsten_start_gleich(self):
        self.assertEqual(self.lade()[1].token, self.lade()[1].token)

    def test_alle_zugangsdaten_sind_verschieden(self):
        d = self.lade()
        tokens = [t for x in d for t in (x.token, x.agent_token)]
        self.assertEqual(len(tokens), len(set(tokens)))

    def test_zu_offene_token_datei_wird_abgelehnt(self):
        self.lade()
        os.chmod(self.tmp / "tokens" / "desktop-kde1.token", 0o644)
        with self.assertRaisesRegex(ao.KonfigurationsFehler, "token_datei_zu_offen"):
            self.lade()

    def test_zu_kurzes_token_in_der_datei_wird_abgelehnt(self):
        self.lade()
        (self.tmp / "tokens" / "agent-kde2.token").write_text("kurz")
        with self.assertRaisesRegex(ao.KonfigurationsFehler, "token_zu_kurz"):
            self.lade()

    def test_fehlende_oder_schwache_umgebung_fuer_windows_wird_abgelehnt(self):
        with self.assertRaisesRegex(ao.KonfigurationsFehler, "zugangsdaten_fehlen:windows"):
            self.lade(env={})
        with self.assertRaisesRegex(ao.KonfigurationsFehler, "zugangsdaten_fehlen:windows"):
            self.lade(env={"BRIDGE_DESKTOP_TOKEN": "x" * 10, "BRIDGE_AGENT_TOKEN": "a" * 40})

    def test_gleicher_token_fuer_desktop_und_starter_wird_abgelehnt(self):
        with self.assertRaisesRegex(ao.KonfigurationsFehler, "zugangsdaten_nicht_verschieden"):
            self.lade(env={"BRIDGE_DESKTOP_TOKEN": "z" * 40, "BRIDGE_AGENT_TOKEN": "z" * 40})

    def test_doppelte_orte_und_ungueltige_namen_werden_abgelehnt(self):
        for inhalt, fehler in (('{"desktops":[{"ort":"kde1"},{"ort":"kde1"}]}', "ort_doppelt"), ('{"desktops":[{"ort":"KDE 1"}]}', "ungueltiger_ort"),
                               ('{"desktops":[]}', "desktops_fehlen"), ("kein json", "desktops_nicht_lesbar")):
            pfad = self.tmp / "d.json"
            pfad.write_text(inhalt)
            with self.assertRaisesRegex(ao.KonfigurationsFehler, fehler):
                ao.lade_desktops(pfad, self.tmp, ENV)

    def test_zugangsdaten_stehen_nie_in_der_darstellung(self):
        for d in self.lade():
            self.assertNotIn(d.token, repr(d))
            self.assertNotIn(d.agent_token, repr(d))

    def test_der_relay_nimmt_alle_paare_an_und_lehnt_doppelte_ab(self):
        principals = ao.baue_principals(self.lade())
        self.assertEqual(len(principals), 6)
        Relay(principals, Journal(self.tmp / "j.sqlite3")).journal.close()
        doppelt = principals + [Principal("x", principals[0].token, principals[1].session_id, "t")]
        with self.assertRaises(ValueError):
            Relay(doppelt, Journal(self.tmp / "j2.sqlite3"))

    def test_der_relay_laesst_alle_desktops_gleichzeitig_anmelden(self):
        from augen_haende_bridge.bridge_runtime import BridgeRuntime

        principals = ao.baue_principals(self.lade())
        journal = Journal(self.tmp / "j3.sqlite3")
        relay = Relay(principals, journal)

        async def lauf():
            async with relay.listen(0) as server:
                port = server.sockets[0].getsockname()[1]
                from augen_haende_bridge.transport_client import BridgeClient

                clients = [BridgeClient(f"ws://127.0.0.1:{port}", p.token) for p in principals]
                offen = []
                try:
                    for c in clients:
                        offen.append(await c.__aenter__())
                    return sorted(c.welcome["session_id"] for c in offen), [c.welcome["capabilities"] for c in offen]
                finally:
                    for c in offen:
                        await c.__aexit__(None, None, None)

        sessions, faehigkeiten = asyncio.run(lauf())
        journal.close()
        self.assertEqual(sessions, sorted(p.session_id for p in principals))
        self.assertTrue(all("anzeigeorte" in f for f in faehigkeiten), "der Relay meldet die neue Fähigkeit allen Desktops und Starter-Verbindungen")


class FakeVerteiler:
    def __init__(self, orte=("windows", "kde1", "kde2")):
        self.desktops = {o: SimpleNamespace(ort=o, name={"windows": "Windows", "kde1": "KDE 1", "kde2": "KDE 2"}[o]) for o in orte}
        self.gesendet: list[tuple] = []
        self.offline: set[str] = set()

    def publish(self, kind, payload, *, message_id=None, ort=None):
        self.gesendet.append((ort, kind, payload))
        return message_id or "x"

    def online(self, ort):
        return ort not in self.offline

    def orte_wire(self):
        return [{"ort": o, "name": d.name, "online": self.online(o)} for o, d in self.desktops.items()]

    def veraenderungen(self):
        return False

    def an(self, ort, kind=None):
        return [p for o, k, p in self.gesendet if o == ort and (kind is None or k == kind)]


def baue(orte=("windows", "kde1", "kde2")):
    fv = FakeVerteiler(orte)
    start = StartEntry("cat", "Katze", "Host", "/tmp", "cat")
    l = Launcher(object(), {"cat": start}, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()), cli_pfad=CLI, verteiler=fv)
    return l, fv


def falsche_sitzung(l, tid="t-1", pid=77, gestartet=5):
    geschrieben, getan = [], []
    s = SimpleNamespace(terminal_id=tid, entry=l.starts["cat"], state="running", rows=24, cols=80, pid=pid, gestartet=gestartet, replay=bytearray(b"Verlauf"),
                        letzte_ausgabe=0.0, write=geschrieben.append, resize=lambda r, c: getan.append(("resize", r, c)), close=lambda: getan.append("close"))
    s.geschrieben, s.getan = geschrieben, getan
    l.sessions[tid] = s
    l._seq[tid] = 0
    return s


def ereignis(art, payload, ort, i="e1"):
    return {"kind": "event", "event_kind": art, "id": i, "payload": payload, "_ort": ort}


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.l, self.fv = baue()
        for o in ("windows", "kde1"):
            self.l.handle(ereignis("anzeigeorte_request", {}, o))
        self.fv.gesendet.clear()

    def tearDown(self):
        for s in self.l.sessions.values():
            try:
                s.close()
            except Exception:
                pass

    def start_auf(self, ort):
        self.l.handle(ereignis("terminal_start", {"start_id": "cat", "rows": 24, "cols": 80}, ort))
        tid = next(t for t in self.l.sessions if t not in getattr(self, "_alt", set()))
        return tid

    def test_der_start_legt_den_anzeigeort_fest_und_meldungen_gehen_nur_dorthin(self):
        tid = self.start_auf("kde1")
        self.assertEqual(self.l.anzeige[tid], "kde1")
        self.assertEqual(self.l.ziel[tid], "kde1", "das Ziel folgt dem Anzeigeort, bis es ausdrücklich gewählt wird")
        zustaende = self.fv.an("kde1", "terminal_state")
        self.assertEqual([z["state"] for z in zustaende], ["starting", "running"])
        self.assertEqual(self.fv.an("windows"), [])
        self.l._output(tid, b"hallo")
        self.assertEqual(len(self.fv.an("kde1", "terminal_output")), 1)
        self.assertEqual(self.fv.an("windows", "terminal_output"), [])

    def test_die_liste_zeigt_jedem_desktop_nur_seine_terminals(self):
        a = falsche_sitzung(self.l, "t-1")
        b = falsche_sitzung(self.l, "t-2")
        self.l.anzeige.update({"t-1": "windows", "t-2": "kde1"})
        self.l.handle(ereignis("terminal_list_request", {}, "windows", "l1"))
        self.l.handle(ereignis("terminal_list_request", {}, "kde1", "l2"))
        self.assertEqual([t["terminal_id"] for t in self.fv.an("windows", "terminal_list")[0]["terminals"]], ["t-1"])
        self.assertEqual([t["terminal_id"] for t in self.fv.an("kde1", "terminal_list")[0]["terminals"]], ["t-2"])
        self.assertEqual(len(self.fv.an("windows", "terminal_list")[0]["starts"]), 1, "die Startliste sieht jeder")

    def test_eingabe_groesse_schliessen_und_wiederaufnahme_gelten_nur_vom_anzeigeort(self):
        s = falsche_sitzung(self.l)
        self.l.anzeige["t-1"] = "kde1"
        daten = base64.b64encode(b"x").decode()
        for art, nutzlast in (("terminal_input", {"terminal_id": "t-1", "data": daten}), ("terminal_resize", {"terminal_id": "t-1", "rows": 30, "cols": 90}),
                              ("terminal_close", {"terminal_id": "t-1"}), ("terminal_attach", {"terminal_id": "t-1"})):
            self.l.handle(ereignis(art, nutzlast, "windows"))
        self.assertEqual((s.geschrieben, s.getan, self.fv.gesendet), ([], [], []))
        self.assertEqual(self.l.abgewiesen["falscher_anzeigeort"], 4)
        self.l.handle(ereignis("terminal_input", {"terminal_id": "t-1", "data": daten}, "kde1"))
        self.l.handle(ereignis("terminal_attach", {"terminal_id": "t-1"}, "kde1"))
        self.assertEqual(s.geschrieben, [b"x"])
        self.assertTrue(self.fv.an("kde1", "terminal_output")[0]["replay"])

    def prepariere_umzug(self):
        s = falsche_sitzung(self.l)
        self.l.anzeige["t-1"] = self.l.ziel["t-1"] = "kde1"
        return s

    def test_umziehen_entfernt_vom_alten_zeigt_auf_dem_neuen_und_laesst_die_sitzung_unberuehrt(self):
        s = self.prepariere_umzug()
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"}, "kde1"))
        self.assertEqual(self.l.anzeige["t-1"], "windows")
        alt, neu = self.fv.an("kde1", "terminal_ort")[-1], self.fv.an("windows", "terminal_ort")[-1]
        self.assertFalse(alt["aktiv"])
        self.assertTrue(neu["aktiv"])
        for m in (alt, neu):
            self.assertEqual((m["pid"], m["gestartet"], m["terminal_id"], m["laufort"], m["anzeigeort"]), (77, 5, "t-1", "Host", "windows"))
        liste = self.fv.an("windows", "terminal_list")[-1]["terminals"]
        self.assertEqual([(t["terminal_id"], t["pid"], t["gestartet"]) for t in liste], [("t-1", 77, 5)], "dieselbe Sitzung, nicht eine neue")
        self.assertEqual(self.fv.an("kde1", "terminal_list"), [], "der alte Desktop bekommt keine Liste mehr, nur die Abmeldung")
        self.assertEqual((s.geschrieben, s.getan), ([], []), "die Sitzung selbst wird nicht berührt")
        self.assertEqual(self.l.ziel["t-1"], "windows", "das Ziel folgte, weil es nie ausdrücklich gewählt war")
        self.fv.gesendet.clear()
        self.l._output("t-1", b"neu")
        self.assertEqual([o for o, k, p in self.fv.gesendet if k == "terminal_output"], ["windows"])

    def test_der_neue_desktop_kann_das_terminal_zu_sich_holen(self):
        self.prepariere_umzug()
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"}, "windows"))
        self.assertEqual(self.l.anzeige["t-1"], "windows")

    def test_abgelehnte_umzuege_ändern_nichts_und_werden_dem_anfragenden_gemeldet(self):
        self.prepariere_umzug()
        faelle = {
            "ort_unbekannt": ({"terminal_id": "t-1", "ort": "mars"}, "kde1"),
            "schon_dort": ({"terminal_id": "t-1", "ort": "kde1"}, "kde1"),
            "terminal_unbekannt": ({"terminal_id": "t-9", "ort": "windows"}, "kde1"),
            "nicht_beteiligt": ({"terminal_id": "t-1", "ort": "windows"}, "kde2"),
        }
        for grund, (nutzlast, von) in faelle.items():
            self.l.handle(ereignis("terminal_umziehen", nutzlast, von))
            self.assertEqual(self.l.anzeige["t-1"], "kde1", grund)
            self.assertGreaterEqual(self.l.abgewiesen.get(grund, 0), 1, grund)
        self.fv.offline.add("windows")
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"}, "kde1"))
        self.assertEqual((self.l.anzeige["t-1"], self.l.abgewiesen["ort_offline"]), ("kde1", 1))
        self.fv.offline.clear()
        self.l.faehig.discard("windows")  # ein alter Körper, der die neuen Meldungen nicht kennt, darf nichts verschoben bekommen
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"}, "kde1"))
        self.assertEqual((self.l.anzeige["t-1"], self.l.abgewiesen["nicht_unterstuetzt"]), ("kde1", 1))
        grund_meldung = [m["grund"] for m in self.fv.an("kde1", "terminal_ort")]
        self.assertIn("ort_unbekannt", grund_meldung)
        self.assertIn("nicht_unterstuetzt", grund_meldung)

    def test_ein_beendetes_terminal_wandert_nicht(self):
        s = self.prepariere_umzug()
        s.state = "exited"
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"}, "kde1"))
        self.assertEqual(self.l.anzeige["t-1"], "kde1")

    def test_ohne_verteiler_bleibt_alles_beim_alten(self):
        start = StartEntry("cat", "Katze", "Host", "/tmp", "cat")
        sent = []
        rt = SimpleNamespace(publish=lambda kind, payload, *, message_id=None: sent.append((kind, payload)) or "x")
        l = Launcher(rt, {"cat": start}, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()), cli_pfad=CLI)
        falsche_sitzung(l)
        l.handle({"kind": "event", "event_kind": "terminal_list_request", "id": "l", "payload": {}})
        l.handle({"kind": "event", "event_kind": "terminal_input", "id": "i", "payload": {"terminal_id": "t-1", "data": base64.b64encode(b"q").decode()}})
        self.assertEqual(l.sessions["t-1"].geschrieben, [b"q"])
        self.assertEqual([k for k, _ in sent], ["terminal_list"])
        self.assertEqual(len(sent[0][1]["terminals"]), 1)

    def test_die_anzeigeorte_gehen_nur_an_desktops_die_danach_fragen(self):
        self.l.handle(ereignis("anzeigeorte_request", {}, "kde2"))
        liste = self.fv.an("kde2", "anzeigeorte")[-1]["orte"]
        self.assertEqual([(o["ort"], o["online"]) for o in liste], [("windows", True), ("kde1", True), ("kde2", True)])
        self.fv.gesendet.clear()
        self.fv.offline.add("kde1")
        self.l.anzeigeorte_senden_alle()
        self.assertEqual(sorted(o for o, k, p in self.fv.gesendet), ["kde1", "kde2", "windows"][:0] + ["kde2", "windows"] if False else sorted(["windows", "kde2"]))


class ZielTests(unittest.TestCase):
    def setUp(self):
        self.l, self.fv = baue()
        for o in ("windows", "kde1", "kde2"):
            self.l.handle(ereignis("anzeigeorte_request", {}, o))
        falsche_sitzung(self.l)
        self.l.anzeige["t-1"] = self.l.ziel["t-1"] = "windows"
        self.l.frames_dir.mkdir(parents=True, exist_ok=True)
        self.fv.gesendet.clear()

    def bild(self, nr=1):
        return {"mime": "image/jpeg", "data": base64.b64encode(b"\xff\xd8\xff\xe0jpg" + bytes([nr])).decode(), "source": "capture", "captured_at_ms": 1000 + nr,
                "width": 10, "height": 10, "terminal_id": "t-1", "sha256": "x"}

    def test_bilder_kommen_vom_zielort_an_und_nur_von_dort(self):
        self.l.handle(ereignis("frame", self.bild(1), "windows"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1001)
        self.l.handle(ereignis("frame", self.bild(2), "kde1"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1001, "ein anderer Desktop darf kein Bild unterschieben")
        self.assertEqual((self.l.frames_abgewiesen["t-1"], self.l.abgewiesen["frame_vom_falschen_ziel"]), (1, 1))

    def test_das_ziel_ist_vom_anzeigeort_unabhaengig(self):
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "kde2"}, "windows"))
        self.assertEqual((self.l.anzeige["t-1"], self.l.ziel["t-1"]), ("windows", "kde2"))
        self.l.handle(ereignis("frame", self.bild(1), "windows"))
        self.assertIsNone(self.l.latest_frame("t-1"), "der Anzeigeort ist nicht mehr das Ziel")
        self.l.handle(ereignis("frame", self.bild(2), "kde2"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1002)

    def test_alle_beteiligten_erfahren_von_der_zielaenderung_und_nur_sie(self):
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "kde2"}, "windows"))
        beteiligte = sorted({o for o, k, p in self.fv.gesendet if k == "terminal_ort"})
        self.assertEqual(beteiligte, ["kde2", "windows"])
        windows = self.fv.an("windows", "terminal_ort")[-1]
        self.assertEqual((windows["anzeigeort"], windows["zielort"], windows["aktiv"]), ("windows", "kde2", True))
        kde2 = self.fv.an("kde2", "terminal_ort")[-1]
        self.assertFalse(kde2["aktiv"], "kde2 ist nur Ziel, zeigt den Körper nicht")

    def test_das_ziel_folgt_dem_umzug_nicht_mehr_wenn_es_ausdruecklich_gewaehlt_wurde(self):
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "kde2"}, "windows"))
        self.l.handle(ereignis("terminal_umziehen", {"terminal_id": "t-1", "ort": "kde1"}, "windows"))
        self.assertEqual((self.l.anzeige["t-1"], self.l.ziel["t-1"]), ("kde1", "kde2"))

    def test_ein_dritter_desktop_darf_das_ziel_nicht_setzen(self):
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "kde2"}, "kde1"))
        self.assertEqual(self.l.ziel["t-1"], "windows")
        self.assertEqual(self.l.abgewiesen["ziel_abgelehnt"], 1)

    def melde(self, von, zustand="ok", target="windows:window:42", faehig="frisch"):
        self.l.handle(ereignis("ziel_zustand", {"terminal_id": "t-1", "target_id": target, "zustand": zustand, "faehigkeit": faehig, "seit_ms": 5}, von))

    def test_ein_verschwundenes_ziel_laesst_keine_bilder_mehr_durch_und_bindet_nie_still_ein_anderes(self):
        self.melde("windows", "ok")
        self.l.handle(ereignis("frame", self.bild(1), "windows"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1001)
        self.melde("windows", "weg", target="windows:window:42", faehig="keine_aufnahme")
        self.l.handle(ereignis("frame", self.bild(2), "windows"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1001, "nach dem Schließen kommt kein Bild mehr, auch nicht von einem Ersatzfenster")
        self.assertEqual(self.l.abgewiesen["frame_ziel_weg"], 1)
        self.assertEqual(self.l.ziel_info["t-1"]["target_id"], "windows:window:42", "das Ziel wird nicht stillschweigend ersetzt")
        self.melde("windows", "ok", target="windows:window:43")  # erst die ausdrückliche neue Bindung gibt es wieder frei
        self.l.handle(ereignis("frame", self.bild(3), "windows"))
        self.assertEqual(self.l.latest_frame("t-1")["captured_at_ms"], 1003)

    def test_ein_ersetztes_ziel_setzt_den_zustand_zurueck_wenn_der_ort_wechselt(self):
        self.melde("windows", "ok")
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "kde1"}, "windows"))
        self.assertNotIn("t-1", self.l.ziel_info, "das alte Ziel gilt nicht mehr")

    def test_zielzustand_nur_vom_zielort(self):
        self.melde("kde1")
        self.assertNotIn("t-1", self.l.ziel_info)
        self.assertEqual(self.l.abgewiesen["ziel_zustand_vom_falschen_ort"], 1)


class AnzeigeTests(unittest.TestCase):
    def setUp(self):
        self.l, self.fv = baue()
        for o in ("windows", "kde1"):
            self.l.handle(ereignis("anzeigeorte_request", {}, o))
        falsche_sitzung(self.l)
        self.l.anzeige["t-1"] = "kde1"
        self.l.ziel["t-1"] = "windows"
        self.l.ziel_explizit.add("t-1")
        self.fv.gesendet.clear()

    def test_vier_angaben_stehen_getrennt_in_der_meldung(self):
        self.l.handle(ereignis("ziel_zustand", {"terminal_id": "t-1", "target_id": "windows:window:42", "zustand": "verdeckt", "faehigkeit": "letztes_bild", "seit_ms": 9}, "windows"))
        m = self.fv.an("kde1", "terminal_ort")[-1]
        self.assertEqual(m["laufort"], "Host", "Laufort: wo das Programm läuft")
        self.assertEqual(m["anzeigeort"], "kde1", "Arbeitsplatz: wo der Körper steht")
        self.assertEqual((m["pid"], m["gestartet"]), (77, 5), "Sitzung")
        self.assertEqual(m["zielort"], "windows", "Ziel: eigener Ort")
        self.assertEqual(m["ziel"], {"target_id": "windows:window:42", "zustand": "verdeckt", "faehigkeit": "letztes_bild"})

    def test_ohne_gemeldetes_ziel_steht_unbekannt_statt_einer_erfundenen_frische(self):
        self.l.handle(ereignis("terminal_ziel", {"terminal_id": "t-1", "ort": "windows"}, "kde1"))
        m = self.fv.an("kde1", "terminal_ort")[-1]
        self.assertEqual(m["ziel"], {"target_id": None, "zustand": "unbekannt", "faehigkeit": "unbekannt"})

    def relay_payload(self, art, wert):
        d = ao.lade_desktops(DESKTOPS, Path(tempfile.mkdtemp()), ENV)
        relay = Relay(ao.baue_principals(d), Journal(Path(tempfile.mkdtemp()) / "j.sqlite3"))
        lauscher = next(p for p in relay.principals if p.can_serve_terminals)
        desktop = next(p for p in relay.principals if p.can_control_terminals)
        return relay, SimpleNamespace(principal=lauscher if art in ("terminal_ort", "anzeigeorte") else desktop)

    def test_der_relay_prueft_die_neuen_nachrichten_streng(self):
        relay, starter = self.relay_payload("terminal_ort", None)
        gut = {"terminal_id": "t-1", "laufort": "Host", "anzeigeort": "kde1", "zielort": "windows", "aktiv": True, "pid": 1, "gestartet": 2,
               "ziel": {"target_id": None, "zustand": "ok", "faehigkeit": "frisch"}, "grund": ""}
        self.assertEqual(relay.payload(starter, "terminal_ort", gut), gut)
        for kaputt in ({**gut, "zusatz": 1}, {**gut, "aktiv": "ja"}, {**gut, "ziel": {**gut["ziel"], "zustand": "magisch"}}, {**gut, "anzeigeort": ""},
                       {**gut, "ziel": {"target_id": None, "zustand": "ok"}}, {**gut, "grund": "x" * 81}):
            with self.assertRaises(ProtocolError):
                relay.payload(starter, "terminal_ort", kaputt)
        relay2, desktop = self.relay_payload("ziel_zustand", None)
        gut2 = {"terminal_id": "t-1", "target_id": "kde1:window:5", "zustand": "minimiert", "faehigkeit": "keine_aufnahme", "seit_ms": 3}
        self.assertEqual(relay2.payload(desktop, "ziel_zustand", gut2), gut2)
        for kaputt in ({**gut2, "faehigkeit": "toll"}, {**gut2, "seit_ms": -1}, {**gut2, "extra": 1}, {"terminal_id": "t-1"}):
            with self.assertRaises(ProtocolError):
                relay2.payload(desktop, "ziel_zustand", kaputt)
        self.assertEqual(relay2.payload(desktop, "terminal_umziehen", {"terminal_id": "t-1", "ort": "kde2"}), {"terminal_id": "t-1", "ort": "kde2"})
        with self.assertRaises(ProtocolError):
            relay2.payload(desktop, "terminal_umziehen", {"terminal_id": "t-1"})
        with self.assertRaises(ProtocolError):
            relay2.payload(starter, "terminal_umziehen", {"terminal_id": "t-1", "ort": "kde2"})  # nur Desktops dürfen das verlangen

    def test_die_faehigkeit_fuer_inaktive_minimierte_verdeckte_ziele_ist_ein_eigener_wert(self):
        from augen_haende_bridge.transport import ZIEL_FAEHIGKEITEN, ZIEL_ZUSTAENDE

        for z in ("verdeckt", "minimiert", "inaktiv", "weg"):
            self.assertIn(z, ZIEL_ZUSTAENDE)
        self.assertEqual(set(ZIEL_FAEHIGKEITEN), {"frisch", "fremde_pixel", "letztes_bild", "keine_aufnahme", "unbekannt"})


class KoerperTests(unittest.TestCase):
    def test_der_stand_nennt_vier_angaben_und_die_wechselziele(self):
        from augen_haende_bridge.koerper import anzeigeort as k

        s = k.AnzeigeOrteStand("kde1")
        s.setze_orte([{"ort": "windows", "name": "Windows", "online": True}, {"ort": "kde1", "name": "KDE 1", "online": True}, {"ort": "kde2", "name": "KDE 2", "online": False}])
        s.merke(k.TerminalOrt.aus_payload({"terminal_id": "t-1", "laufort": "vd1", "anzeigeort": "kde1", "zielort": "windows", "aktiv": True, "pid": 9, "gestartet": 1,
                                           "ziel": {"target_id": "windows:window:7", "zustand": "minimiert", "faehigkeit": "keine_aufnahme"}, "grund": ""}))
        text = "\n".join(s.beschreibung("t-1"))
        for erwartet in ("Läuft auf: vd1", "Angezeigt auf: KDE 1", "Sitzung: PID 9", "Ziel: Windows", "minimiert", "keine Aufnahme"):
            self.assertIn(erwartet, text)
        self.assertEqual([o["ort"] for o in s.ziele_fuer_wechsel("t-1")], ["windows"], "offline und der eigene Desktop sind keine Wechselziele")
        eintraege = s.menue_eintraege("t-1", 4000)
        self.assertEqual([e for e in eintraege if e and e[0] >= 4000], [(4000, "Anzeigeort wechseln zu Windows …", 0)])
        self.assertEqual(s.wahl_zu_ort("t-1", 4000, 4000), "windows")
        self.assertIsNone(s.wahl_zu_ort("t-1", 4000, 4001))

    def test_ohne_unterstuetzung_wird_das_gesagt_und_nichts_angeboten(self):
        from augen_haende_bridge.koerper import anzeigeort as k

        s = k.AnzeigeOrteStand("windows")
        text = [e[1] for e in s.menue_eintraege("t-1", 4000) if e]
        self.assertTrue(any("Relay meldet keine" in t for t in text))
        self.assertFalse(any(e and e[0] >= 4000 for e in s.menue_eintraege("t-1", 4000)))


class KoerperAnwendungTests(unittest.TestCase):
    """Die Anwendung des Körpers mit Anzeigeorten (die Fenster selbst sind ersetzt, wie in den anderen Körper-Tests)."""

    def setUp(self):
        from test_koerper_anwendung import STARTS, _event, _verbunden

        self.STARTS, self._event, self._verbunden = STARTS, _event, _verbunden

    def liste(self, tid="t-1", pid=7, gestartet=1):
        return self._event("terminal_list", {"request_id": "r", "starts": self.STARTS, "terminals": [
            {"terminal_id": tid, "start_id": "codex-vd1", "name": "Codex", "state": "running", "rows": 24, "cols": 80, "pid": pid, "gestartet": gestartet}]})

    def ort_nachricht(self, tid="t-1", anzeige="kde1", ziel="kde1", aktiv=True, grund="", zustand="unbekannt", faehigkeit="unbekannt", target=None):
        return self._event("terminal_ort", {"terminal_id": tid, "laufort": "vd1", "anzeigeort": anzeige, "zielort": ziel, "aktiv": aktiv, "pid": 7, "gestartet": 1,
                                            "ziel": {"target_id": target, "zustand": zustand, "faehigkeit": faehigkeit}, "grund": grund})

    def verbinden(self, faehigkeiten, **kw):
        from test_koerper_anwendung import _anwendung

        app, gui, gebaut = _anwendung(ort="kde1", **kw)
        app.starten()
        app.ereignis({"kind": "runtime.connected", "welcome": {"capabilities": faehigkeiten}})
        return app, gebaut

    def test_die_anzeigeorte_werden_nur_bei_einem_relay_angefragt_der_sie_kennt(self):
        neu, _ = self.verbinden(["say", "anzeigeorte"])
        self.assertIn(("anzeigeorte_request", {}), neu.runtime.gesendet)
        alt, _ = self.verbinden(["say", "terminal_control"])
        self.assertNotIn("anzeigeorte_request", [k for k, _ in alt.runtime.gesendet])
        windows_alt, _ = self.verbinden([])
        self.assertEqual([k for k, _ in windows_alt.runtime.gesendet], ["terminal_list_request"], "ein älterer Relay: nichts Neues, nichts kaputt")

    def test_der_stand_kommt_vom_relay_und_der_eigene_ort_steht_im_schluessel(self):
        app, _ = self.verbinden(["anzeigeorte"])
        self.assertEqual(app.ort, "kde1")
        self.assertFalse(app.anzeigeorte.unterstuetzt)
        app.ereignis(self._event("anzeigeorte", {"orte": [{"ort": "windows", "name": "Windows", "online": True}, {"ort": "kde1", "name": "KDE 1", "online": True}]}))
        self.assertTrue(app.anzeigeorte.unterstuetzt)
        self.assertEqual(app.anzeigeorte.name("windows"), "Windows")

    def test_der_ziel_schluessel_traegt_die_kennung_dieses_arbeitsplatzes(self):
        from types import SimpleNamespace

        strom = self.strom()
        strom.ziele["t-1"] = SimpleNamespace(hwnd=4711)
        app, _ = self.verbinden(["anzeigeorte"], bilderstrom=strom)
        self.assertEqual(app.ziel_schluessel("t-1"), "kde1:window:4711")

    def menue_wahl(self, wahl):
        gesehen = []

        def anzeigen(hwnd, eintraege, x, y):
            gesehen.append(eintraege)
            return wahl(eintraege)

        return anzeigen, gesehen

    def test_das_menue_zeigt_vier_angaben_und_wechselt_den_anzeigeort(self):
        from augen_haende_bridge.koerper import anwendung as a

        anzeigen, gesehen = self.menue_wahl(lambda e: a.ANZEIGEORT_WECHSEL_ID)
        app, _ = self.verbinden(["anzeigeorte"], menue_anzeigen=anzeigen)
        app.ereignis(self.liste())
        app.ereignis(self._event("anzeigeorte", {"orte": [{"ort": "windows", "name": "Windows", "online": True}, {"ort": "kde1", "name": "KDE 1", "online": True},
                                                          {"ort": "kde2", "name": "KDE 2", "online": False}]}))
        app.ereignis(self.ort_nachricht(zustand="verdeckt", faehigkeit="frisch", target="kde1:window:5"))
        app.runtime.gesendet.clear()
        app.anzeigeort_menue("t-1", 5, 5)
        texte = [e[1] for e in gesehen[0] if e]
        for erwartet in ("Läuft auf: vd1", "Angezeigt auf: KDE 1", "Sitzung: PID 7", "Ziel: KDE 1", "Anzeigeort wechseln zu Windows", "Arbeitsziel auf Windows legen"):
            self.assertTrue(any(erwartet in t for t in texte), (erwartet, texte))
        self.assertFalse(any("KDE 2" in t and "wechseln" in t for t in texte), "ein offline-Desktop wird nicht angeboten")
        self.assertEqual(app.runtime.gesendet, [("terminal_umziehen", {"terminal_id": "t-1", "ort": "windows"})])

    def test_das_menue_legt_das_arbeitsziel_auf_einen_anderen_desktop(self):
        from augen_haende_bridge.koerper import anwendung as a

        anzeigen, _ = self.menue_wahl(lambda e: a.ANZEIGEORT_ZIEL_ID)
        app, _ = self.verbinden(["anzeigeorte"], menue_anzeigen=anzeigen)
        app.ereignis(self.liste())
        app.ereignis(self._event("anzeigeorte", {"orte": [{"ort": "windows", "name": "Windows", "online": True}, {"ort": "kde1", "name": "KDE 1", "online": True}]}))
        app.runtime.gesendet.clear()
        app.anzeigeort_menue("t-1", 5, 5)
        self.assertEqual(app.runtime.gesendet, [("terminal_ziel", {"terminal_id": "t-1", "ort": "windows"})])

    def test_wandert_der_koerper_fort_verschwindet_er_hier_und_die_sitzung_bleibt_unberuehrt(self):
        app, gebaut = self.verbinden(["anzeigeorte"])
        app.ereignis(self.liste())
        self.assertIn("t-1", app.agenten)
        app.runtime.gesendet.clear()
        app.ereignis(self.ort_nachricht(anzeige="windows", ziel="windows", aktiv=False))
        self.assertNotIn("t-1", app.agenten)
        gebaut[0].schliessen.assert_called_once()
        self.assertEqual([k for k, _ in app.runtime.gesendet], [], "weder schließen noch sonst etwas an die Sitzung")

    def test_kommt_der_koerper_an_entsteht_er_aus_der_liste_und_nimmt_die_sitzung_wieder_auf(self):
        app, _ = self.verbinden(["anzeigeorte"])
        app.ereignis(self.ort_nachricht(anzeige="kde1", aktiv=True))
        self.assertNotIn("t-1", app.agenten, "die Nachricht allein legt keinen Körper an")
        app.ereignis(self.liste())
        self.assertIn("t-1", app.agenten)
        self.assertIn(("terminal_attach", {"terminal_id": "t-1"}), app.runtime.gesendet)

    def test_eine_abgelehnte_anfrage_wird_mit_grund_im_status_gesagt(self):
        app, _ = self.verbinden(["anzeigeorte"])
        app.ereignis(self.liste())
        app.ereignis(self.ort_nachricht(grund="ort_offline"))
        self.assertIn("nicht verbunden", app.hinweis)
        self.assertIn("t-1", app.agenten)

    def strom(self):
        from unittest.mock import Mock

        from augen_haende_bridge.koerper.bilderstrom import Bilderstrom

        strom = Mock(spec=Bilderstrom)
        strom.ziele = {}
        strom.binden.side_effect = lambda tid, hwnd, rect=None: strom.ziele.__setitem__(tid, object())
        strom.loesen.side_effect = lambda tid: strom.ziele.pop(tid, None)
        return strom

    def test_liegt_das_ziel_hier_der_koerper_aber_woanders_sendet_dieser_desktop_als_ziel_gast_seinen_ganzen_bildschirm(self):
        strom = self.strom()
        app, _ = self.verbinden(["anzeigeorte"], bilderstrom=strom)
        app.ereignis(self.ort_nachricht(tid="t-7", anzeige="windows", ziel="kde1", aktiv=False))
        strom.binden.assert_called_once_with("t-7", None)
        self.assertIn("t-7", app.ziel_gaeste)
        app.ereignis(self.ort_nachricht(tid="t-7", anzeige="windows", ziel="kde2", aktiv=False))  # das Ziel wandert weg
        strom.loesen.assert_called_once_with("t-7")
        self.assertNotIn("t-7", app.ziel_gaeste)

    def test_ein_ziel_gast_bindet_nicht_doppelt_und_beruehrt_fremde_bindungen_nicht(self):
        strom = self.strom()
        app, _ = self.verbinden(["anzeigeorte"], bilderstrom=strom)
        for _ in range(3):
            app.ereignis(self.ort_nachricht(tid="t-7", anzeige="windows", ziel="kde1", aktiv=False))
        self.assertEqual(strom.binden.call_count, 1)
        strom.ziele["t-8"] = object()  # eine eigene Bindung eines hier gezeigten Agenten
        app.ereignis(self.ort_nachricht(tid="t-8", anzeige="kde1", ziel="kde1", aktiv=True))
        strom.loesen.assert_not_called()

    def test_die_eigene_bindung_endet_wenn_das_ziel_auf_einen_anderen_desktop_wandert(self):
        strom = self.strom()
        app, _ = self.verbinden(["anzeigeorte"], bilderstrom=strom)
        app.ereignis(self.liste())
        strom.ziele["t-1"] = object()
        app.ereignis(self.ort_nachricht(anzeige="kde1", ziel="windows", aktiv=True))
        strom.loesen.assert_called_once_with("t-1")
        self.assertIn("t-1", app.agenten, "der Körper bleibt hier, nur das Ziel liegt anderswo")

    def test_ziel_zustaende_werden_gemeldet_nur_bei_aenderung_und_nur_fuer_ziele_dieses_desktops(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        strom = self.strom()
        verdeckt = {"an": False}
        app, _ = self.verbinden(["anzeigeorte"], bilderstrom=strom, ziel_verdeckt=lambda hwnd: verdeckt["an"])
        app.ereignis(self._event("anzeigeorte", {"orte": [{"ort": "kde1", "name": "KDE 1", "online": True}]}))
        strom.ziele["t-1"] = SimpleNamespace(hwnd=42)
        strom.ziele["t-2"] = SimpleNamespace(hwnd=None)
        app.runtime.gesendet.clear()
        zustand = {"wert": (True, False, (0, 0, 10, 10))}
        with patch("augen_haende_bridge.koerper.anwendung.fenster_zustand", side_effect=lambda hwnd: zustand["wert"]):
            app.ziel_zustaende_melden()
            gesendet = {p["terminal_id"]: p for k, p in app.runtime.gesendet if k == "ziel_zustand"}
            self.assertEqual((gesendet["t-1"]["target_id"], gesendet["t-1"]["zustand"], gesendet["t-1"]["faehigkeit"]), ("kde1:window:42", "ok", "frisch"))
            self.assertEqual((gesendet["t-2"]["target_id"], gesendet["t-2"]["zustand"]), ("kde1:desktop", "ok"))
            app.runtime.gesendet.clear()
            app.ziel_zustaende_melden()
            self.assertEqual(app.runtime.gesendet, [], "unverändert: nichts senden")
            verdeckt["an"] = True
            app.ziel_zustaende_melden()
            m = [p for k, p in app.runtime.gesendet if k == "ziel_zustand"]
            self.assertEqual([(x["zustand"], x["faehigkeit"]) for x in m], [("verdeckt", "fremde_pixel")], "mit Bildschirmausschnitt zeigt das Bild fremde Fenster")
            app.runtime.gesendet.clear()
            zustand["wert"] = (True, True, None)
            app.ziel_zustaende_melden()
            self.assertEqual([(p["zustand"], p["faehigkeit"]) for k, p in app.runtime.gesendet], [("minimiert", "keine_aufnahme")])
            app.runtime.gesendet.clear()
            zustand["wert"] = (False, False, None)
            app.ziel_zustaende_melden()
            self.assertEqual([p["zustand"] for k, p in app.runtime.gesendet], ["weg"])
            app.ereignis(self.ort_nachricht(anzeige="kde1", ziel="windows", aktiv=True))  # das Ziel liegt jetzt woanders: hier nichts mehr melden
            app.runtime.gesendet.clear()
            strom.ziele["t-1"] = SimpleNamespace(hwnd=42)
            zustand["wert"] = (True, False, (0, 0, 10, 10))
            app.ziel_zustaende_melden()
            self.assertNotIn("t-1", [p["terminal_id"] for k, p in app.runtime.gesendet if k == "ziel_zustand"])

    def test_mit_fensteraufnahme_ist_ein_verdecktes_ziel_trotzdem_frisch(self):
        from augen_haende_bridge.koerper import anzeigeort as k

        self.assertEqual(k.faehigkeit_standard("verdeckt"), "fremde_pixel")
        self.assertEqual(k.faehigkeit_fensteraufnahme("verdeckt"), "frisch")
        for z in ("minimiert", "weg"):
            self.assertEqual(k.faehigkeit_fensteraufnahme(z), "keine_aufnahme")

    def test_ohne_unterstuetzung_wird_nichts_gemeldet(self):
        from types import SimpleNamespace

        strom = self.strom()
        strom.ziele["t-1"] = SimpleNamespace(hwnd=None)
        app, _ = self.verbinden([], bilderstrom=strom)
        app.runtime.gesendet.clear()
        app.ziel_zustaende_melden()
        self.assertEqual(app.runtime.gesendet, [])

    def test_das_raute_menue_bietet_anzeigeort_und_ziel_an(self):
        from test_koerper_erster_koerper import _bauen
        from augen_haende_bridge.koerper.erster_koerper import MENUE_ANZEIGEORT

        aufrufe = []
        koerper, *_ = _bauen(anzeigeort_menue=lambda x, y: aufrufe.append((x, y)), menue_anzeigen=lambda hwnd, eintraege, x, y: MENUE_ANZEIGEORT)
        self.assertTrue(any(e and e[0] == MENUE_ANZEIGEORT for e in koerper.menue_eintraege()))
        koerper._raute_menue(3, 4)
        self.assertEqual(aufrufe, [(3, 4)])


if __name__ == "__main__":
    unittest.main()
