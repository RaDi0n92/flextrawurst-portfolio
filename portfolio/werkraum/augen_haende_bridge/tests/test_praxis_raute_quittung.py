"""Body completion ACKs, with injected input only; no native desktop proof."""
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper.anwendung import KoerperAnwendung
from augen_haende_bridge.transport import Relay, ProtocolError


class RauteQuittungTests(unittest.TestCase):
    def setUp(self):
        self.app = KoerperAnwendung.__new__(KoerperAnwendung)
        self.agent = SimpleNamespace(nur_terminal=False, haende=True, haende_laufen=False,
                                     hotkey="F13", name="Test", koerper=Mock())
        self.app.agenten = {"t": self.agent}
        self.app.bilderstrom = None  # kein Bilderstrom im Test: kein Sofortbild an Gate-Nachbarn
        self.app.haende_gruende = {}
        self.app.not_aus = SimpleNamespace(aktiv=False)
        self.app.gui = SimpleNamespace(post=lambda f: f())
        self.app._haende = Mock()
        self.done = threading.Event()
        self.sent = []
        self.app._senden = self.send
        self.request = {"terminal_id": "t", "text": "Test", "request_id": "req-1"}

    def send(self, kind, payload):
        self.sent.append((kind, payload))
        self.done.set()

    def test_success_ack_waits_for_backend_completion(self):
        entered, release = threading.Event(), threading.Event()
        def write(*args, **kwargs):
            entered.set()
            release.wait(2)
            return SimpleNamespace(ok=True, grund="")
        self.app._haende.schreiben.side_effect = write
        self.app._raute_tippt(self.request)
        try:
            self.assertTrue(entered.wait(1))
            self.assertFalse(self.done.is_set())
        finally:
            release.set()
        self.assertTrue(self.done.wait(2))
        self.assertEqual(self.sent, [("raute_tippen_ergebnis", {**{k: self.request[k] for k in ("terminal_id", "request_id")}, "ok": True, "grund": ""})])

    def test_disabled_hands_negative_ack_without_backend_call(self):
        self.agent.haende = False
        self.app._raute_tippt(self.request)
        self.assertEqual(self.sent[0][1]["grund"], "haende_aus")
        self.assertFalse(self.sent[0][1]["ok"])
        self.app._haende.schreiben.assert_not_called()

    def test_der_schreibweg_bekommt_ruhe_und_markierung_der_anwendung(self):
        """Ohne diese beiden Funktionen drückt die Raute die Tastenkombination, während Daniel tippt."""
        self.app._haende.schreiben.return_value = SimpleNamespace(ok=True, grund="")
        self.app._raute_tippt(self.request)
        self.assertTrue(self.done.wait(2))
        kw = self.app._haende.schreiben.call_args.kwargs
        self.assertEqual(kw["ruhig"], self.app._daniel_ist_ruhig)
        self.assertEqual(kw["eigene_markieren"], self.app._eigene_tasten_markieren)

    def test_daniel_ist_ruhig_nach_zwei_sekunden_ohne_tippen_oder_klicken(self):
        beobachter = SimpleNamespace(ruhig_seit=lambda: 1.9)
        self.app.haende_engine = SimpleNamespace(beobachter=beobachter, letzte_sendung=0.0)
        self.assertFalse(self.app._daniel_ist_ruhig())
        beobachter.ruhig_seit = lambda: 2.0
        self.assertTrue(self.app._daniel_ist_ruhig())
        self.app.haende_engine.beobachter = None  # ohne Beobachter (Windows) gilt Ruhe
        self.assertTrue(self.app._daniel_ist_ruhig())

    def test_eigene_tasten_markieren_setzt_die_letzte_sendung(self):
        self.app.haende_engine = SimpleNamespace(letzte_sendung=0.0)
        self.app._eigene_tasten_markieren()
        self.assertGreater(self.app.haende_engine.letzte_sendung, 0.0)

    def test_daniels_chatantwort_landet_in_der_gewaehlten_session(self):
        """G03/E05: nicht nur Banner und Chat, die Antwort kommt als Eingabe in der Session des Angesprochenen an; Sprache lässt das Terminal unberührt."""
        import base64
        self.app.chat = None
        self.app.empfaenger = None
        self.agent.zustand = "running"
        zweiter = SimpleNamespace(nur_terminal=False, haende=True, haende_laufen=False, hotkey="F14", name="Zwei", koerper=Mock(), zustand="running")
        self.app.agenten["u"] = zweiter
        self.app.daniel_sagt("Hallo", "u")  # nur an u
        eingaben = [(k, p) for k, p in self.sent if k == "terminal_input"]
        self.assertEqual([(p["terminal_id"], base64.b64decode(p["data"])) for k, p in eingaben], [("u", b"Daniel: Hallo\r")])
        self.sent.clear()
        self.app.daniel_sagt("an alle")
        self.assertEqual({p["terminal_id"] for k, p in self.sent if k == "terminal_input"}, {"t", "u"})
        self.sent.clear()
        self.app.daniel_sagt("(Sprache) hi", "t", in_session=False)
        self.assertEqual([k for k, p in self.sent if k == "terminal_input"], [], "Sprache: das Terminal bleibt unberührt")
        self.agent.zustand = "paused"
        self.app.daniel_sagt("keiner", "t")
        self.assertEqual([k for k, p in self.sent if k == "terminal_input"], [], "nur in laufende Sessions")

    def test_hände_auf_ein_bridge_fenster_geben_es_fuer_die_aktion_frei(self):
        """Regieleiste und Chat sind im Normalmodus durchklickbar: ohne Freigabe fände der Käfig das Fenster darunter (punkt_verdeckt)."""
        from augen_haende_bridge.koerper.durchklick import DurchklickVerwalter

        v = DurchklickVerwalter(strg=lambda: False)
        v.registrieren("regie", Mock(hwnd=33554435), aktiv=True)
        self.app.durchklick = v
        posts = []
        self.app.gui = SimpleNamespace(post=lambda f: (posts.append(f), f()))
        aktion = SimpleNamespace(dauer_ms=0)
        self.assertTrue(self.app._bridge_fenster_freigeben("kde1:window:33554435", aktion))
        self.assertGreater(v._erzwungen_bis, 0)
        self.app._bridge_fenster_wieder_durchklickbar()
        self.assertEqual(v._erzwungen_bis, 0)
        self.assertFalse(self.app._bridge_fenster_freigeben("kde1:window:104857603", aktion), "ein fremdes Fenster wird nie freigegeben")
        self.assertFalse(self.app._bridge_fenster_freigeben("kde1:desktop", aktion))

    def test_haende_auf_die_raute_eines_agenten_geben_sie_fuer_die_aktion_frei(self):
        """Die Raute regelt ihr Durchklicken selbst (Bedientaste im Timer): ohne Erzwingung fände der Käfig das Fenster darunter (`punkt_verdeckt`)."""
        from augen_haende_bridge.koerper.raute_fenster import RauteFenster

        raute = Mock(spec=["hwnd", "erzwingen", "bedienbar_setzen"])
        raute.hwnd = 33554599
        andere = Mock(spec=["hwnd", "erzwingen", "bedienbar_setzen"])
        andere.hwnd = 33554777
        self.app.agenten = {"t": SimpleNamespace(koerper=SimpleNamespace(raute=raute)), "u": SimpleNamespace(koerper=SimpleNamespace(raute=andere))}
        self.app.durchklick = None
        self.app.gui = SimpleNamespace(post=lambda f: f())
        aktion = SimpleNamespace(dauer_ms=500)
        self.assertTrue(self.app._bridge_fenster_freigeben("kde1:window:33554599", aktion))
        raute.erzwingen.assert_called_once_with(4.5)
        raute.bedienbar_setzen.assert_called_once_with(True)
        andere.erzwingen.assert_not_called()
        self.app._bridge_fenster_wieder_durchklickbar()
        self.assertEqual([c.args for c in raute.erzwingen.call_args_list][-1], (0,))
        self.assertEqual([c.args for c in andere.erzwingen.call_args_list][-1], (0,))
        self.assertFalse(self.app._bridge_fenster_freigeben("kde1:window:104857603", aktion), "ein fremdes Fenster wird nie freigegeben")
        self.assertTrue(hasattr(RauteFenster, "erzwingen"))

    def test_die_erzwingung_der_raute_gilt_wie_eine_gehaltene_bedientaste_und_endet(self):
        from augen_haende_bridge.koerper import raute_fenster as rf

        zeit = {"t": 100.0}
        ohne = Mock(spec=rf.RauteFenster)
        ohne._erzwungen_bis, ohne._modifikator, ohne._modifikator_vk = 0.0, (lambda: False), 0x11
        original = rf.time.monotonic
        rf.time.monotonic = lambda: zeit["t"]
        try:
            self.assertFalse(rf.RauteFenster.modifikator_gedrueckt(ohne))
            rf.RauteFenster.erzwingen(ohne, 4.0)
            self.assertTrue(rf.RauteFenster.modifikator_gedrueckt(ohne))
            zeit["t"] = 103.9
            self.assertTrue(rf.RauteFenster.modifikator_gedrueckt(ohne))
            zeit["t"] = 104.1
            self.assertFalse(rf.RauteFenster.modifikator_gedrueckt(ohne), "nach Ablauf gilt wieder die echte Taste")
            rf.RauteFenster.erzwingen(ohne, 4.0)
            rf.RauteFenster.erzwingen(ohne, 0)
            self.assertFalse(rf.RauteFenster.modifikator_gedrueckt(ohne), "0 hebt die Erzwingung auf")
        finally:
            rf.time.monotonic = original

    def test_backend_exception_negative_ack_and_busy_reset(self):
        self.app._haende.schreiben.side_effect = RuntimeError("injected")
        self.app._raute_tippt(self.request)
        self.assertTrue(self.done.wait(2))
        self.assertEqual(self.sent[0][1]["grund"], "schreibfehler")
        self.assertFalse(self.agent.haende_laufen)

    def test_protocol_ack_requires_boolean_and_correlation(self):
        relay = Relay.__new__(Relay)
        valid = {"terminal_id": "t", "request_id": "req-1", "ok": True, "grund": ""}
        self.assertEqual(relay.terminal_payload("raute_tippen_ergebnis", valid), valid)
        for bad in ({**valid, "ok": "true"}, {k: v for k, v in valid.items() if k != "request_id"},
                    {**valid, "request_id": "invalid/id"}):
            with self.subTest(payload=bad), self.assertRaises(ProtocolError):
                relay.terminal_payload("raute_tippen_ergebnis", bad)
