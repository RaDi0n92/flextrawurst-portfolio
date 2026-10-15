"""Spracherkennung auf dem VPS: Transkriber (mit Attrappe des Modells), Launcher-Anbindung, `hoere`."""
import base64
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from client_vps import sprache
from client_vps.sprache import WhisperTranskriber, bereinigen, ist_phantom
from client_vps.terminal_launcher import Launcher, MAX_AUDIO_WARTESCHLANGE, Ort, StartEntry


class Segment(SimpleNamespace):
    pass


class FakeModell:
    def __init__(self, segmente=None, fehler=None):
        self.segmente, self.fehler, self.aufrufe = segmente or [], fehler, []

    def transcribe(self, datei, **optionen):
        self.aufrufe.append((datei.read(4), optionen))
        if self.fehler:
            raise self.fehler
        return iter(self.segmente), SimpleNamespace()


def seg(text, no_speech=0.0, logprob=-0.2):
    return Segment(text=text, no_speech_prob=no_speech, avg_logprob=logprob)


class TranskriberTests(unittest.TestCase):
    def transkriber(self, modell):
        return WhisperTranskriber(modell="klein", sprache="de", threads=2, vokabular="Claude, Codex", faktor=lambda n, t: modell)

    def test_text_aus_den_segmenten_wird_zusammengesetzt_und_bereinigt(self):
        m = FakeModell([seg(" Hallo  Claude,"), seg(" schau mal.\n")])
        self.assertEqual(self.transkriber(m).transkribiere(b"RIFFxxxx"), "Hallo Claude, schau mal.")

    def test_optionen_sprache_vad_und_vokabular(self):
        m = FakeModell([seg("x")])
        self.transkriber(m).transkribiere(b"RIFFxxxx")
        _kopf, optionen = m.aufrufe[0]
        self.assertEqual((optionen["language"], optionen["vad_filter"], optionen["initial_prompt"]), ("de", True, "Claude, Codex"))
        self.assertFalse(optionen["condition_on_previous_text"])

    def test_stille_segmente_und_phantomsaetze_werden_verworfen(self):
        m = FakeModell([seg("Rauschen", no_speech=0.9, logprob=-2.0)])
        self.assertEqual(self.transkriber(m).transkribiere(b"RIFF"), "")
        m = FakeModell([seg("Untertitel der Amara.org-Community")])
        self.assertEqual(self.transkriber(m).transkribiere(b"RIFF"), "")

    def test_leises_aber_sicheres_segment_bleibt(self):
        m = FakeModell([seg("ja", no_speech=0.9, logprob=-0.3)])
        self.assertEqual(self.transkriber(m).transkribiere(b"RIFF"), "ja")

    def test_modell_wird_nur_einmal_geladen(self):
        geladen = []
        t = WhisperTranskriber(modell="m", faktor=lambda n, th: geladen.append(n) or FakeModell([seg("a")]))
        t.transkribiere(b"RIFF")
        t.transkribiere(b"RIFF")
        self.assertEqual(geladen, ["m"])

    def test_fehlendes_modell_ist_ein_klarer_fehler(self):
        def faktor(n, t):
            raise FileNotFoundError("kein modell")
        t = WhisperTranskriber(modell="m", faktor=faktor)
        with self.assertRaisesRegex(RuntimeError, "whisper_nicht_verfuegbar"):
            t.transkribiere(b"RIFF")
        self.assertIn("kein modell", t.fehler)

    def test_hilfsfunktionen(self):
        self.assertEqual(bereinigen("  a \n  b\t c "), "a b c")
        self.assertTrue(ist_phantom("Vielen Dank fürs Zuschauen!"))
        self.assertFalse(ist_phantom("Öffne das Terminal"))

    def test_standardwerte_aus_der_umgebung(self):
        import os
        os.environ["BRIDGE_WHISPER_MODELL"] = "tiny"
        try:
            self.assertEqual(WhisperTranskriber(faktor=lambda n, t: None).modell, "tiny")
        finally:
            del os.environ["BRIDGE_WHISPER_MODELL"]
        self.assertEqual(WhisperTranskriber(faktor=lambda n, t: None).modell, sprache.STANDARD_MODELL)


class Runtime:
    def __init__(self):
        self.sent = []

    def publish(self, kind, payload, *, message_id=None):
        self.sent.append((kind, payload))
        return message_id or "x"


class FakeTranskriber:
    modell = "fake-modell"

    def __init__(self, text="Schau mal links", fehler=None):
        self.text, self.fehler, self.aufrufe = text, fehler, []
        self.vorgeladen = False

    def vorladen(self):
        self.vorgeladen = True

    def transkribiere(self, wav):
        self.aufrufe.append(wav)
        if self.fehler:
            raise self.fehler
        return self.text


def launcher(transkriber):
    start = StartEntry("x", "X", "Host", "/tmp", "cat")
    l = Launcher(Runtime(), {"x": start}, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()), transkriber=transkriber)
    l.sessions["t-1"] = SimpleNamespace(state="running", terminal_id="t-1", token="tok", entry=start, close=lambda: None)
    return l


def audio(tid="t-1", dauer=1500):
    return {"terminal_id": tid, "mime": "audio/wav", "data": base64.b64encode(b"RIFFwavdaten").decode(), "dauer_ms": dauer}


def warte(bedingung, sekunden=3.0):
    ende = time.monotonic() + sekunden
    while time.monotonic() < ende:
        if bedingung():
            return True
        time.sleep(0.01)
    return bedingung()


class LauncherSpracheTests(unittest.TestCase):
    def starten(self, transkriber):
        l = launcher(transkriber)
        l.start()
        self.addCleanup(l.shutdown)
        return l

    def test_aeusserung_wird_erkannt_und_als_sprache_text_gemeldet(self):
        t = FakeTranskriber()
        l = self.starten(t)
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        self.assertTrue(warte(lambda: l.runtime.sent))
        art, nutzlast = l.runtime.sent[0]
        self.assertEqual(art, "sprache_text")
        self.assertEqual((nutzlast["terminal_id"], nutzlast["text"], nutzlast["dauer_ms"], nutzlast["modell"]),
                         ("t-1", "Schau mal links", 1500, "fake-modell"))
        self.assertEqual(t.aufrufe, [b"RIFFwavdaten"])
        self.assertTrue(t.vorgeladen)

    def test_hoere_liefert_nur_neue_saetze_einmal(self):
        l = self.starten(FakeTranskriber("eins"))
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        warte(lambda: l.saetze.get("t-1"))
        antwort = l.agent_request({"terminal_id": "t-1", "token": "tok", "cmd": "hoere"})
        self.assertTrue(antwort["ok"] and antwort["spracherkennung"])
        self.assertEqual([s["text"] for s in antwort["saetze"]], ["eins"])
        self.assertEqual(l.agent_request({"terminal_id": "t-1", "token": "tok", "cmd": "hoere"})["saetze"], [])

    def test_hoere_ohne_spracherkennung_sagt_es(self):
        l = launcher(None)
        antwort = l.agent_request({"terminal_id": "t-1", "token": "tok", "cmd": "hoere"})
        self.assertEqual((antwort["ok"], antwort["spracherkennung"], antwort["saetze"]), (True, False, []))

    def test_hoere_mit_falschem_token_wird_abgelehnt(self):
        l = launcher(FakeTranskriber())
        self.assertEqual(l.agent_request({"terminal_id": "t-1", "token": "falsch", "cmd": "hoere"})["reason"],
                         "unknown_terminal_or_token")

    def test_leerer_text_wird_nicht_gemeldet(self):
        l = self.starten(FakeTranskriber(text=""))
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        time.sleep(0.3)
        self.assertEqual(l.runtime.sent, [])

    def test_fehler_der_erkennung_stoppt_die_warteschlange_nicht(self):
        t = FakeTranskriber(fehler=RuntimeError("kaputt"))
        l = self.starten(t)
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        self.assertTrue(warte(lambda: l.transkription_fehler))
        t.fehler = None
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        self.assertTrue(warte(lambda: l.runtime.sent))
        self.assertIsNone(l.transkription_fehler)

    def test_unbekanntes_oder_beendetes_terminal_wird_ignoriert(self):
        t = FakeTranskriber()
        l = self.starten(t)
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio("t-99")})
        l.sessions["t-1"].state = "exited"
        l.handle({"kind": "event", "event_kind": "terminal_audio", "payload": audio()})
        time.sleep(0.2)
        self.assertEqual(t.aufrufe, [])

    def test_zu_viele_wartende_aeusserungen_werden_verworfen(self):
        frei = threading.Event()

        class Langsam(FakeTranskriber):
            def transkribiere(self, wav):
                frei.wait(3)
                return super().transkribiere(wav)

        l = launcher(Langsam())
        l.start()
        self.addCleanup(l.shutdown)
        self.addCleanup(frei.set)
        for _ in range(MAX_AUDIO_WARTESCHLANGE + 4):
            l._audio_annehmen(audio())
        self.assertGreaterEqual(l.audio_verworfen, 1)

    def test_ohne_transkriber_wird_audio_verworfen(self):
        l = launcher(None)
        l._audio_annehmen(audio())
        self.assertTrue(l._audio_schlange.empty())


if __name__ == "__main__":
    unittest.main()
