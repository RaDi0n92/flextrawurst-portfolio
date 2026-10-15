"""Tests für koerper/anwendung.py (Relay-Anschluss des ersten Körpers) und koerper/bild.py.

GUI, Runtime und Körper sind injiziert; der echte Relay-Weg läuft in `tests/test_koerper_anwendung_relay.py`.
"""

from __future__ import annotations

import base64
import io
import threading
import unittest
from unittest.mock import Mock

from augen_haende_bridge.koerper import bild
from augen_haende_bridge.koerper.anwendung import (
    VK_F13,
    KoerperAnwendung,
    Sender,
    eingabe_stuecke,
    platz_fuer,
)
from augen_haende_bridge.transport import MAX_TERMINAL_INPUT


class FakeGui:
    def __init__(self):
        self.hotkeys = []
        self.beendet = None

    def post(self, aufgabe):
        aufgabe()

    def hotkey(self, modifikatoren, vk, aufruf):
        self.hotkeys.append((modifikatoren, vk, aufruf))
        return True

    def beenden(self, code=0):
        self.beendet = code


class FakeRuntime:
    def __init__(self, url, token, *, on_event):
        self.url, self.token, self.on_event = url, token, on_event
        self.gestartet = False
        self.gestoppt = False
        self.gesendet = []

    def start(self):
        self.gestartet = True

    def stop(self):
        self.gestoppt = True

    def publish(self, kind, payload, *, message_id=None):
        self.gesendet.append((kind, payload))
        return "id"


class SofortSender:
    def __init__(self, veroeffentlichen, fehler, gesperrt=lambda kind: False):
        self.veroeffentlichen, self.fehler, self.gesperrt = veroeffentlichen, fehler, gesperrt
        self.gestoppt = False

    def senden(self, kind, payload):
        if self.gesperrt(kind):
            return False
        self.veroeffentlichen(kind, payload)
        return True

    def stop(self):
        self.gestoppt = True


def _koerper_bauen():
    gebaut = []

    def bauen(**kwargs):
        koerper = Mock()
        koerper.kwargs = kwargs
        koerper.raute.status = "offline"
        koerper.raute.letzte_nachricht = ""
        koerper.terminal.zustand = "startet…"
        koerper.terminal.ziel_text = "Ziel: Desktop (ungebunden)"
        koerper.terminal.text_aller_zeilen.return_value = ["hallo", ""]
        gebaut.append(koerper)
        return koerper
    return bauen, gebaut


def _anwendung(**kwargs):
    bauen, gebaut = _koerper_bauen()
    gui = FakeGui()
    werte = dict(url="ws://127.0.0.1:19880", token="t" * 40, gui=gui, koerper_bauen=bauen, runtime_bauen=FakeRuntime,
                 arbeitsflaeche=lambda: (0, 0, 1920, 1040), sender_bauen=SofortSender)
    werte.update(kwargs)
    app = KoerperAnwendung(**werte)
    return app, gui, gebaut


def _event(kind, payload):
    return {"kind": "event", "event_kind": kind, "payload": payload}


STARTS = [{"start_id": "codex-vd1", "name": "Codex", "ort": "vd1", "ordner": "/config", "programm": "codex"}]


def _verbunden(**kwargs):
    app, gui, gebaut = _anwendung(**kwargs)
    app.starten()
    app.ereignis({"kind": "runtime.connected", "welcome": {}})
    app.ereignis(_event("terminal_list", {"request_id": "r", "starts": STARTS, "terminals": []}))
    return app, gui, gebaut


def _gestartet(**kwargs):
    app, gui, gebaut = _verbunden(**kwargs)
    app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                           "state": "starting", "exit_code": None, "reason": ""}))
    app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                           "state": "running", "exit_code": None, "reason": ""}))
    return app, gui, gebaut


class WiederaufnahmeTests(unittest.TestCase):
    def test_bereits_laufende_sitzung_zeigt_laeuft(self) -> None:
        app, _gui, gebaut = _verbunden()
        app.ereignis(_event("terminal_list", {"request_id": "r2", "starts": STARTS, "terminals": [
            {"terminal_id": "t-9", "start_id": "codex-vd1", "name": "Codex", "state": "running"}]}))
        gebaut[0].terminal.setze_zustand.assert_called_with("läuft")


class WiederaufnahmeClientTests(unittest.TestCase):
    def _liste(self, terminals):
        return _event("terminal_list", {"request_id": "r", "starts": STARTS, "terminals": terminals})

    def _terminal(self, tid="t-9", pid=4711, gestartet=1790000000):
        return {"terminal_id": tid, "start_id": "codex-vd1", "name": "Codex", "state": "running", "rows": 30, "cols": 100,
                "pid": pid, "gestartet": gestartet}

    def test_laufende_sitzung_wird_angelegt_und_die_wiederaufnahme_angefordert(self) -> None:
        app, _gui, gebaut = _verbunden()
        app.ereignis(self._liste([self._terminal()]))
        self.assertIn(("terminal_attach", {"terminal_id": "t-9"}), app.runtime.gesendet)
        agent = app.agenten["t-9"]
        self.assertEqual((agent.pid, agent.gestartet, agent.neue_sitzung), (4711, 1790000000, False))

    def test_beim_wiederverbinden_wird_auch_eine_bekannte_sitzung_neu_aufgenommen_ohne_neuen_koerper(self) -> None:
        app, _gui, gebaut = _verbunden()
        app.ereignis(self._liste([self._terminal()]))
        koerper = len(gebaut)
        app.ereignis(self._liste([self._terminal()]))
        self.assertEqual(len(gebaut), koerper)  # kein zweiter Körper, keine zweite Raute
        self.assertEqual(sum(1 for g in app.runtime.gesendet if g[0] == "terminal_attach"), 2)
        self.assertFalse(app.agenten["t-9"].neue_sitzung)

    def test_anderer_prozess_unter_derselben_id_wird_erkannt_und_gemeldet(self) -> None:
        app, _gui, _g = _verbunden()
        app.ereignis(self._liste([self._terminal()]))
        app.ereignis(self._liste([self._terminal(pid=9999, gestartet=1790000500)]))
        agent = app.agenten["t-9"]
        self.assertTrue(agent.neue_sitzung)
        self.assertEqual(agent.pid, 9999)
        self.assertIn("neuer Prozess", app.hinweis)

    def test_beendete_sitzung_wird_nicht_aufgenommen(self) -> None:
        app, _gui, _g = _verbunden()
        beendet = {**self._terminal(), "state": "exited"}
        app.ereignis(self._liste([beendet]))
        self.assertFalse(any(g[0] == "terminal_attach" for g in app.runtime.gesendet))

    def test_replay_stueck_setzt_den_bildschirm_zurueck_und_zaehlt_keine_luecke(self) -> None:
        app, _gui, gebaut = _gestartet()
        agent = app.agenten["t-1"]
        agent.ausgabe_seq = 40
        app.ereignis(_event("terminal_output", {"terminal_id": "t-1", "seq": 100, "data": base64.b64encode(b"neu").decode(), "replay": True}))
        gebaut[0].terminal.zuruecksetzen.assert_called_once_with()
        gebaut[0].terminal.ausgabe.assert_called_with(b"neu")
        self.assertEqual((agent.ausgabe_seq, agent.luecken), (100, 0))
        app.ereignis(_event("terminal_output", {"terminal_id": "t-1", "seq": 101, "data": base64.b64encode(b"!").decode()}))
        self.assertEqual(gebaut[0].terminal.zuruecksetzen.call_count, 1)  # nur das erste Stück setzt zurück
        self.assertEqual(agent.luecken, 0)

    def test_ausgabe_ohne_replay_zaehlt_luecken_wie_bisher(self) -> None:
        app, _gui, gebaut = _gestartet()
        agent = app.agenten["t-1"]
        agent.ausgabe_seq = 5
        app.ereignis(_event("terminal_output", {"terminal_id": "t-1", "seq": 9, "data": base64.b64encode(b"x").decode()}))
        self.assertEqual(agent.luecken, 1)
        gebaut[0].terminal.zuruecksetzen.assert_not_called()


class VerbindenTests(unittest.TestCase):
    def test_ohne_url_oder_token_bleibt_sie_sichtbar_offline(self) -> None:
        app, _gui, _g = _anwendung(url=None)
        app.starten()
        self.assertEqual(app.status, "offline")
        self.assertIn("BRIDGE_URL/BRIDGE_TOKEN fehlen", app.hinweis)
        self.assertIsNone(app.runtime)

    def test_starten_baut_die_runtime_und_verbindet(self) -> None:
        app, _gui, _g = _anwendung()
        app.starten()
        self.assertTrue(app.runtime.gestartet)
        self.assertEqual(app.status, "verbindet")

    def test_verbunden_fragt_die_startliste_an(self) -> None:
        app, _gui, _g = _anwendung()
        app.starten()
        app.ereignis({"kind": "runtime.connected", "welcome": {}})
        self.assertEqual(app.status, "verbunden")
        self.assertEqual(app.runtime.gesendet, [("terminal_list_request", {})])

    def test_transportfehler_wird_status_fehler(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.ereignis({"kind": "runtime.failed", "reason": "ConnectionClosed"})
        self.assertEqual(app.status, "fehler")
        gebaut[0].setze_status.assert_called_with("fehler")

    def test_starter_nicht_verbunden_wird_sichtbar(self) -> None:
        app, _gui, _g = _verbunden()
        app.ereignis({"kind": "result", "id": "x", "status": "peer_offline"})
        self.assertIn("peer_offline", app.hinweis)

    def test_ohne_verbindung_wird_nichts_gesendet(self) -> None:
        app, _gui, _g = _anwendung()
        app.starten()
        self.assertFalse(app.agent_starten("codex-vd1"))
        self.assertEqual(app.runtime.gesendet, [])


class StartlisteUndKoerperTests(unittest.TestCase):
    def test_startliste_wird_uebernommen_und_start_schickt_nur_die_start_id(self) -> None:
        app, _gui, _g = _verbunden()
        self.assertEqual(sorted(app.startliste), ["codex-vd1"])
        self.assertTrue(app.agent_starten("codex-vd1"))
        self.assertEqual(app.runtime.gesendet[-1], ("terminal_start", {"start_id": "codex-vd1", "rows": 30, "cols": 100}))
        self.assertFalse(app.agent_starten("nicht-in-der-liste"))

    def test_ein_koerper_entsteht_erst_mit_dem_start_der_sitzung(self) -> None:
        app, gui, gebaut = _verbunden()
        self.assertEqual(gebaut, [])
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "starting", "exit_code": None, "reason": ""}))
        self.assertEqual(len(gebaut), 1)
        kwargs = gebaut[0].kwargs
        self.assertEqual((kwargs["name"], kwargs["ort"], kwargs["hotkey"]), ("Codex", "vd1", "F13"))
        gebaut[0].zeigen.assert_called_once_with()
        self.assertEqual(gui.hotkeys[0][1], VK_F13)
        self.assertIn("gesprochen", kwargs)  # Gesprochenes geht an den gemeinsamen Chat der Anwendung
        self.assertTrue(callable(gui.hotkeys[0][2]))  # F13 wählt den Agenten und zeigt den Chat

    def test_fehlgeschlagener_start_ohne_koerper_wird_nur_gemeldet(self) -> None:
        app, _gui, gebaut = _verbunden()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-9", "start_id": "x", "name": "unbekannt",
                                               "state": "failed", "exit_code": None, "reason": "unknown_start_id"}))
        self.assertEqual(gebaut, [])
        self.assertIn("unknown_start_id", app.hinweis)

    def test_laufende_sitzungen_aus_der_liste_bekommen_einen_koerper(self) -> None:
        app, _gui, gebaut = _anwendung()
        app.starten()
        app.ereignis({"kind": "runtime.connected", "welcome": {}})
        app.ereignis(_event("terminal_list", {"request_id": "r", "starts": STARTS, "terminals": [
            {"terminal_id": "t-5", "start_id": "codex-vd1", "name": "Codex", "state": "running", "rows": 30, "cols": 100}]}))
        self.assertEqual(len(gebaut), 1)

    def test_test_autostart_startet_genau_einmal(self) -> None:
        app, _gui, _g = _verbunden(test_autostart="codex-vd1")
        starts = [g for g in app.runtime.gesendet if g[0] == "terminal_start"]
        self.assertEqual(len(starts), 1)
        app.ereignis(_event("terminal_list", {"request_id": "r2", "starts": STARTS, "terminals": []}))
        self.assertEqual(len([g for g in app.runtime.gesendet if g[0] == "terminal_start"]), 1)

    def test_zustaende_erscheinen_am_terminal_und_an_der_raute(self) -> None:
        app, _gui, gebaut = _gestartet()
        koerper = gebaut[0]
        koerper.terminal.setze_zustand.assert_called_with("läuft")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        koerper.terminal.setze_zustand.assert_called_with("beendet (Code 0)")
        koerper.setze_status.assert_called_with("beendet")

    def test_test_tippe_tippt_einmal_sobald_die_sitzung_laeuft(self) -> None:
        _app, _gui, gebaut = _gestartet(test_tippe="hallo\r")
        gebaut[0].terminal.tippe.assert_called_once_with("hallo\r")


class StromTests(unittest.TestCase):
    def test_terminalausgabe_geht_dekodiert_ans_terminal_und_luecken_werden_gezaehlt(self) -> None:
        app, _gui, gebaut = _gestartet()
        for seq in (0, 1, 3):
            app.ereignis(_event("terminal_output", {"terminal_id": "t-1", "seq": seq,
                                                    "data": base64.b64encode(b"x%d" % seq).decode()}))
        self.assertEqual([c.args[0] for c in gebaut[0].terminal.ausgabe.call_args_list], [b"x0", b"x1", b"x3"])
        self.assertEqual(app.agenten["t-1"].luecken, 1)

    def test_raute_say_laesst_die_richtige_raute_sprechen(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.ereignis(_event("raute_say", {"terminal_id": "t-1", "text": "Shader kompiliert!"}))
        gebaut[0].raute.sagen.assert_called_once_with("Shader kompiliert!")

    def test_ausgabe_fuer_unbekanntes_terminal_wird_ignoriert(self) -> None:
        app, _gui, _g = _gestartet()
        app.ereignis(_event("terminal_output", {"terminal_id": "t-x", "seq": 0, "data": "eA=="}))

    def test_eingaben_gehen_in_relay_tauglichen_stuecken(self) -> None:
        app, _gui, _g = _gestartet()
        app.eingabe_senden("t-1", b"a" * (MAX_TERMINAL_INPUT + 10))
        eingaben = [p for k, p in app.runtime.gesendet if k == "terminal_input"]
        self.assertEqual(len(eingaben), 2)
        self.assertEqual(len(base64.b64decode(eingaben[0]["data"])), MAX_TERMINAL_INPUT)
        self.assertEqual(eingaben[0]["terminal_id"], "t-1")

    def test_gesperrte_eingaben_werden_nicht_gesendet(self) -> None:
        app, _gui, _g = _gestartet()
        app.eingaben_gesperrt = True
        app.eingabe_senden("t-1", b"x")
        self.assertFalse(any(k == "terminal_input" for k, _p in app.runtime.gesendet))
        self.assertIn("Not-Aus", app.hinweis)

    def test_groessenaenderung_geht_als_terminal_resize(self) -> None:
        app, _gui, gebaut = _gestartet()
        gebaut[0].kwargs["terminal_groesse"](40, 120)
        self.assertEqual(app.runtime.gesendet[-1], ("terminal_resize", {"terminal_id": "t-1", "rows": 40, "cols": 120}))


class NotAusTests(unittest.TestCase):
    def test_not_aus_zeigt_sich_an_allen_rauten_und_sperrt_eingaben_bilder_und_starts(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.not_aus.ausloesen("F12")
        gebaut[0].setze_status.assert_called_with("notaus")
        self.assertIn("Not-Aus", app.hinweis)
        app.eingabe_senden("t-1", b"x")
        self.assertFalse(app.agent_starten("codex-vd1"))
        bindung = Mock()
        app.bild_senden("t-1", bindung)
        gesendet = [k for k, _p in app.runtime.gesendet]
        self.assertNotIn("terminal_input", gesendet)
        self.assertNotIn("frame", gesendet)
        self.assertEqual(gesendet.count("terminal_start"), 0)

    def test_der_sender_verwirft_bereits_eingereihtes_auch_ohne_gui(self) -> None:
        aus = []
        from augen_haende_bridge.koerper.notaus import NotAus
        na = NotAus()
        fertig = threading.Event()
        sender = Sender(lambda kind, p: (aus.append(kind), fertig.set()), lambda t: None,
                        lambda kind: na.aktiv and kind in ("terminal_input", "frame", "terminal_start"))
        na.ausloesen("F12")
        sender.senden("terminal_input", {})
        sender.senden("terminal_close", {})  # Schließen bleibt erlaubt
        self.assertTrue(fertig.wait(2))
        sender.stop()
        self.assertEqual(aus, ["terminal_close"])
        self.assertEqual(sender.verworfen, 1)

    def test_freigeben_hebt_die_sperre_und_die_anzeige_auf(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.not_aus.ausloesen("F12")
        app.not_aus.freigeben()
        gebaut[0].setze_status.assert_called_with("verbunden")
        app.eingabe_senden("t-1", b"x")
        self.assertIn("terminal_input", [k for k, _p in app.runtime.gesendet])

    def test_neu_entstehende_koerper_zeigen_den_not_aus(self) -> None:
        app, _gui, gebaut = _verbunden()
        app.not_aus.ausloesen("F12")
        app.ereignis(_event("terminal_state", {"terminal_id": "t-2", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "starting", "exit_code": None, "reason": ""}))
        gebaut[-1].setze_status.assert_called_with("notaus")

    def test_der_bericht_nennt_den_not_aus(self) -> None:
        app, _gui, _g = _gestartet()
        app.not_aus.ausloesen("F12")
        self.assertTrue(app.bericht()["not_aus"])


class BeendenTests(unittest.TestCase):
    def test_laufenden_agenten_beenden_schickt_terminal_close(self) -> None:
        app, _gui, gebaut = _gestartet()
        gebaut[0].kwargs["agent_beenden"]()
        self.assertEqual(app.runtime.gesendet[-1], ("terminal_close", {"terminal_id": "t-1"}))
        self.assertIn("t-1", app.agenten)

    def test_nach_gewuenschtem_beenden_verschwindet_der_ganze_koerper_wenn_die_sitzung_endet(self) -> None:
        app, _gui, gebaut = _gestartet()
        gebaut[0].kwargs["agent_beenden"]()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        gebaut[0].schliessen.assert_called_once_with()
        self.assertNotIn("t-1", app.agenten)

    def test_von_selbst_beendeter_agent_bleibt_sichtbar_als_beendet(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 1, "reason": ""}))
        gebaut[0].schliessen.assert_not_called()
        self.assertIn("t-1", app.agenten)
        gebaut[0].setze_status.assert_called_with("beendet")

    def test_beendeten_agenten_beenden_schliesst_nur_die_fenster(self) -> None:
        app, _gui, gebaut = _gestartet()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex",
                                               "state": "exited", "exit_code": 0, "reason": ""}))
        app.agent_beenden("t-1")
        gebaut[0].schliessen.assert_called_once_with()
        self.assertNotIn("t-1", app.agenten)

    def test_bridge_beenden_schliesst_alles(self) -> None:
        app, gui, gebaut = _gestartet()
        app.beenden()
        gebaut[0].schliessen.assert_called_once_with()
        self.assertTrue(app.runtime.gestoppt)
        self.assertTrue(app.sender.gestoppt)
        self.assertEqual(gui.beendet, 0)


class BildSendenTests(unittest.TestCase):
    def test_gebundenes_bild_geht_als_jpeg_frame_an_genau_diesen_agenten(self) -> None:
        kodieren = Mock(return_value=(b"\xff\xd8\xffJPEG", 800, 600))
        app, _gui, _g = _gestartet(bild_kodieren=kodieren)
        bindung = Mock()
        bindung.frame.width, bindung.frame.height = 1920, 1080
        bindung.frame.bgra_bytes = b"...."
        bindung.frame.captured_at_ms = 1234
        bindung.snapshot.items = [Mock(rect=(0, 0, 1920, 1080))]
        bindung.item.rect = (10, 10, 810, 610)
        app.bild_senden("t-1", bindung)
        kodieren.assert_called_once_with(b"....", 1920, 1080, (10, 10, 810, 610))
        kind, payload = app.runtime.gesendet[-1]
        self.assertEqual(kind, "frame")
        self.assertEqual(payload["terminal_id"], "t-1")
        self.assertEqual((payload["mime"], payload["source"], payload["width"], payload["height"]),
                         ("image/jpeg", "capture", 800, 600))
        self.assertEqual(base64.b64decode(payload["data"]), b"\xff\xd8\xffJPEG")


class ReineFunktionenTests(unittest.TestCase):
    def test_eingabe_stuecke(self) -> None:
        self.assertEqual(eingabe_stuecke(b""), [])
        self.assertEqual(eingabe_stuecke(b"abcde", 2), [b"ab", b"cd", b"e"])

    def test_platz_fuer_versetzt_terminals_unten_und_rauten_oben_rechts(self) -> None:
        raute0, terminal0 = platz_fuer(0, (0, 0, 1920, 1040))
        raute1, terminal1 = platz_fuer(1, (0, 0, 1920, 1040))
        self.assertGreater(terminal0[1], 1040 // 2 - 200)
        self.assertNotEqual(terminal0, terminal1)
        self.assertGreater(raute0[0], 1920 // 2)
        self.assertNotEqual(raute0, raute1)


class SenderTests(unittest.TestCase):
    def test_echter_sender_veroeffentlicht_im_eigenen_faden(self) -> None:
        gesehen, faeden = [], []
        fertig = threading.Event()

        def veroeffentlichen(kind, payload):
            gesehen.append((kind, payload))
            faeden.append(threading.current_thread().name)
            fertig.set()

        sender = Sender(veroeffentlichen, lambda text: None)
        self.assertTrue(sender.senden("terminal_input", {"x": 1}))
        self.assertTrue(fertig.wait(2))
        sender.stop()
        self.assertEqual(gesehen, [("terminal_input", {"x": 1})])
        self.assertEqual(faeden, ["koerper-sender"])

    def test_fehler_beim_senden_wird_gemeldet_und_der_faden_lebt_weiter(self) -> None:
        fehler, fertig = [], threading.Event()
        aufrufe = []

        def veroeffentlichen(kind, payload):
            aufrufe.append(kind)
            if kind == "kaputt":
                raise RuntimeError("bridge_runtime_not_connected")
            fertig.set()

        sender = Sender(veroeffentlichen, fehler.append)
        sender.senden("kaputt", {})
        sender.senden("heil", {})
        self.assertTrue(fertig.wait(2))
        sender.stop()
        self.assertEqual(aufrufe, ["kaputt", "heil"])
        self.assertIn("bridge_runtime_not_connected", fehler[0])


class BildTests(unittest.TestCase):
    def test_ausschnitt_wird_auf_den_frame_geklemmt(self) -> None:
        self.assertEqual(bild.ausschnitt_im_frame((10, 10, 810, 610), (0, 0), 1920, 1080), (10, 10, 810, 610))
        self.assertEqual(bild.ausschnitt_im_frame((-50, -50, 100, 100), (0, 0), 1920, 1080), (0, 0, 100, 100))
        # Zweiter Monitor links: der virtuelle Bildschirm beginnt bei x = -1920 und ist 3840 breit.
        self.assertEqual(bild.ausschnitt_im_frame((100, 100, 300, 300), (-1920, 0), 3840, 1080), (2020, 100, 2220, 300))
        self.assertIsNone(bild.ausschnitt_im_frame((100, 100, 300, 300), (-1920, 0), 1920, 1080))
        self.assertIsNone(bild.ausschnitt_im_frame((5000, 5000, 5100, 5100), (0, 0), 1920, 1080))

    def test_skalierung_auf_hoechstens_1920x1080(self) -> None:
        self.assertEqual(bild.skaliert_auf(800, 600), (800, 600))
        self.assertEqual(bild.skaliert_auf(3840, 2160), (1920, 1080))

    def test_echtes_jpeg_aus_bgra(self) -> None:
        breite, hoehe = 64, 32
        bgra = bytes([255, 0, 0, 255]) * (breite * hoehe)  # reines Blau in BGRA
        daten, b, h = bild.bgra_zu_jpeg(bgra, breite, hoehe, (0, 0, 32, 16))
        self.assertTrue(daten.startswith(b"\xff\xd8\xff"))
        self.assertEqual((b, h), (32, 16))
        from PIL import Image
        pixel = Image.open(io.BytesIO(daten)).convert("RGB").getpixel((16, 8))
        self.assertGreater(pixel[2], 200)  # blau bleibt blau: BGRA richtig gelesen
        self.assertLess(pixel[0], 60)


if __name__ == "__main__":
    unittest.main()
