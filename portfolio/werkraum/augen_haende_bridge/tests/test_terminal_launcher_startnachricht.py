"""Startnachricht: dem Agenten beim Start sagen, wie er über die Bridge spricht (opt-in je Startliste-Eintrag)."""
import base64
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from client_vps import terminal_launcher as tl
from client_vps.terminal_launcher import Launcher, Ort, StartEntry, load_orte, load_starts, standard_startnachricht

CLI = Path("/root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py")


class Runtime:
    def __init__(self):
        self.sent = []

    def publish(self, kind, payload, *, message_id=None):
        self.sent.append((kind, payload))
        return message_id or "x"


def launcher(start: StartEntry, orte=None):
    orte = orte or {"Host": Ort("host", None), "vd1": Ort("docker", "vd1", "/root", "/vps_root")}
    return Launcher(Runtime(), {start.start_id: start}, orte, Path(tempfile.mkdtemp()), cli_pfad=CLI)


def eintrag(ort="Host", nachricht="standard"):
    return StartEntry("x", "X", ort, "/tmp", "cat", nachricht)


class TextTests(unittest.TestCase):
    def test_keine_nachricht_ohne_opt_in(self):
        l = launcher(eintrag(nachricht=""))
        self.assertEqual(l.startnachricht_text(SimpleNamespace(entry=l.starts["x"])), "")

    def test_standardtext_nennt_den_pfad_wie_der_ort_ihn_sieht(self):
        host = launcher(eintrag("Host"))
        self.assertIn("python3 /root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py say", host.startnachricht_text(SimpleNamespace(entry=host.starts["x"])))
        vd = launcher(eintrag("vd1"))
        text = vd.startnachricht_text(SimpleNamespace(entry=vd.starts["x"]))
        self.assertIn("/vps_root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py", text)
        self.assertNotIn("/root/werkraum", text)

    def test_eigener_text_ersetzt_den_platzhalter(self):
        l = launcher(eintrag(nachricht="Sprich mit {cli} say Hallo"))
        self.assertEqual(l.startnachricht_text(SimpleNamespace(entry=l.starts["x"])),
                         "Sprich mit /root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py say Hallo")

    def test_standardtext_ist_eine_zeile(self):
        self.assertNotIn("\n", standard_startnachricht("/x/bridge_cli.py"))


class LadenTests(unittest.TestCase):
    def schreibe(self, **extra):
        pfad = Path(tempfile.mkdtemp()) / "starts.json"
        eintrag = {"start_id": "a", "name": "A", "ort": "Host", "ordner": "/tmp", "programm": "cat", **extra}
        pfad.write_text(json.dumps({"starts": [eintrag]}), encoding="utf-8")
        return pfad

    def test_feld_ist_optional(self):
        s = load_starts(self.schreibe(), {"Host": Ort("host", None)})
        self.assertEqual(s["a"].startnachricht, "")

    def test_feld_wird_gelesen_und_steht_nicht_im_wire(self):
        s = load_starts(self.schreibe(startnachricht="standard"), {"Host": Ort("host", None)})
        self.assertEqual(s["a"].startnachricht, "standard")
        self.assertNotIn("startnachricht", s["a"].wire())

    def test_ungueltiges_feld_wird_abgelehnt(self):
        for wert in (5, "a\nb", "x" * 3000, "a\x00b"):
            with self.assertRaises(ValueError):
                load_starts(self.schreibe(startnachricht=wert), {"Host": Ort("host", None)})

    def test_die_echte_startliste_laedt(self):
        konfig = Path(tl.__file__).parent
        orte = load_orte(konfig / "orte.json")
        starts = load_starts(konfig / "starts.json", orte)
        self.assertEqual(starts["claude-vd1"].startnachricht, "standard")
        self.assertEqual(starts["haiku-host"].startnachricht, "")


class SendenTests(unittest.TestCase):
    def fake(self, **ueber):
        s = SimpleNamespace(state="running", letzte_ausgabe=0.0, geschrieben=[], terminal_id="t-1")
        s.write = s.geschrieben.append
        for k, v in ueber.items():
            setattr(s, k, v)
        return s

    def test_tippt_erst_nach_ruhe_der_ausgabe(self):
        l = launcher(eintrag())
        zeit = {"t": 100.0}
        l._uhr = lambda: zeit["t"]
        session = self.fake(letzte_ausgabe=100.0)

        def schlafen(dt):
            zeit["t"] += dt
            if zeit["t"] < 101.5:
                session.letzte_ausgabe = zeit["t"]  # Ausgabe läuft noch

        l._schlafen = schlafen
        l._startnachricht_senden(session, "Hallo")
        self.assertEqual(session.geschrieben, [b"Hallo", b"\r"])  # Text und Enter getrennt
        self.assertGreaterEqual(zeit["t"], 101.5 + tl.STARTNACHRICHT_RUHE_S - 0.3)

    def test_ohne_jede_ausgabe_wird_nichts_getippt(self):
        l = launcher(eintrag())
        zeit = {"t": 0.0}
        l._uhr = lambda: zeit["t"]
        l._schlafen = lambda dt: zeit.update(t=zeit["t"] + dt * 10)
        session = self.fake()
        l._startnachricht_senden(session, "Hallo")
        self.assertEqual(session.geschrieben, [])

    def test_beendete_sitzung_bekommt_nichts(self):
        l = launcher(eintrag())
        session = self.fake(state="exited", letzte_ausgabe=1.0)
        l._startnachricht_senden(session, "Hallo")
        self.assertEqual(session.geschrieben, [])

    def test_schreibfehler_wird_verschluckt(self):
        l = launcher(eintrag())
        l._uhr = lambda: 100.0
        session = self.fake(letzte_ausgabe=1.0)

        def kaputt(data):
            raise OSError("pty weg")

        session.write = kaputt
        l._startnachricht_senden(session, "Hallo")


class EchtTests(unittest.TestCase):
    """Echte PTY: `cat` gibt zurück, was getippt wird."""

    def test_die_startnachricht_kommt_in_der_sitzung_an(self):
        alt = tl.STARTNACHRICHT_RUHE_S
        tl.STARTNACHRICHT_RUHE_S = 0.4
        try:
            start = StartEntry("echo", "Echo", "Host", "/tmp", "cat", "Hallo Agent, sag {cli} say Hi")
            l = launcher(start)
            ausgabe = bytearray()
            l._publish = lambda kind, payload, message_id=None: (
                ausgabe.extend(base64.b64decode(payload["data"])) if kind == "terminal_output" else None)
            l.start_terminal({"start_id": "echo", "rows": 24, "cols": 80})
            # cat gibt selbst keine Ausgabe: ohne erste Ausgabe wird nichts getippt -> wir erzeugen eine
            session = next(iter(l.sessions.values()))
            session.write(b"los\r")
            ende = time.monotonic() + 10
            while time.monotonic() < ende and b"Hallo Agent" not in ausgabe:
                time.sleep(0.05)
            self.assertIn(b"Hallo Agent, sag /root/werkraum/augen_haende_bridge/client_vps/bridge_cli.py say Hi", bytes(ausgabe))
            session.close()
        finally:
            tl.STARTNACHRICHT_RUHE_S = alt




class BestaetigungTests(unittest.TestCase):
    DIALOG = ("\x1b[2J\x1b[1mAccessing\x1b[0m workspace:\r\n/config\r\nQuick safety check: Is this a project you created or one you trust?\r\n"
              "\x1b[36m❯ 1. No, exit\x1b[0m\r\n  2. Yes, I trust this folder\r\nEnter to confirm · Esc to cancel").encode()

    def maschine(self, replay):
        l = launcher(eintrag())
        geschrieben, uhr = [], [0.0]
        s = SimpleNamespace(terminal_id="t-1", state="running", letzte_ausgabe=0.0, replay=bytearray(replay), write=geschrieben.append)
        l._uhr = lambda: uhr[0]

        def schlafen(sek):
            uhr[0] += max(sek, 0.25)
            s.letzte_ausgabe = 1.0  # die Ausgabe ist seit langem still

        l._schlafen = schlafen
        return l, s, geschrieben, uhr

    def test_ein_vertrauensdialog_bekommt_keinen_text_und_kein_enter(self):
        l, s, geschrieben, uhr = self.maschine(self.DIALOG)
        l._startnachricht_senden(s, "Hallo Agent")
        self.assertEqual(geschrieben, [], "in den Dialog wird nichts getippt: ein Enter dort hieße „Nein, beenden“")
        log = (l.runtime_dir / "startnachricht.log").read_text()
        self.assertIn("wartet: das Programm fragt nach einer Bestätigung", log)
        self.assertIn("nicht getippt", log)
        self.assertGreater(uhr[0], 500, "es hat auf Daniel gewartet, nicht sofort aufgegeben")

    def test_gibt_daniel_die_bestaetigung_wird_danach_getippt(self):
        l, s, geschrieben, uhr = self.maschine(self.DIALOG)
        originale = l._schlafen

        def schlafen(sek):
            originale(sek)
            if uhr[0] > 30 and bytes(s.replay) == self.DIALOG:
                s.replay += b"\x1b[2J" + ("Willkommen bei Claude Code. Wie kann ich helfen?\r\n" * 80).encode()  # neue Oberfläche, der Dialog liegt weit zurück

        l._schlafen = schlafen
        l._startnachricht_senden(s, "Hallo Agent")
        self.assertEqual([g for g in geschrieben if g != b"\r"], [b"Hallo Agent"])
        self.assertEqual(geschrieben[-1], b"\r")

    def test_ohne_dialog_wird_wie_bisher_getippt(self):
        l, s, geschrieben, _ = self.maschine(b"Willkommen\r\n> ")
        l._startnachricht_senden(s, "Hallo Agent")
        self.assertEqual(geschrieben, [b"Hallo Agent", b"\r"])

    def test_die_erkennung_findet_die_texte_trotz_steuerzeichen_und_ohne_leerzeichen(self):
        l, s, _, _ = self.maschine(b"Is\x1b[0m this a\x1b[1m project you created or one you trust?")
        self.assertTrue(l._wartet_auf_bestaetigung(s))
        s.replay = bytearray(b"Ein ganz normaler Bildschirm mit Text")
        self.assertFalse(l._wartet_auf_bestaetigung(s))


if __name__ == "__main__":
    unittest.main()
