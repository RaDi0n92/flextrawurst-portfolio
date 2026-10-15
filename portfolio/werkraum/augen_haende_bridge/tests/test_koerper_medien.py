import threading
import time
import unittest

from augen_haende_bridge.koerper.kamera import Kamera
from augen_haende_bridge.koerper.medien import Medien
from augen_haende_bridge.koerper.mikrofon import Mikrofon
from augen_haende_bridge.koerper.notaus import NotAus


class KameraQuelleFake:
    def __init__(self, vorhanden=True):
        self.vorhanden, self.offen = vorhanden, False

    def oeffnen(self, index):
        self.offen = self.vorhanden
        return self.vorhanden

    def lesen(self):
        return (2, 1, b"\x00" * 6)

    def schliessen(self):
        self.offen = False


class MikrofonQuelleFake:
    def __init__(self):
        self.eingang, self.offen, self.geraet = None, False, "unberührt"

    def oeffnen(self, geraet, abtastrate, kanaele, eingang):
        self.eingang, self.offen, self.geraet = eingang, True, geraet

    def schliessen(self):
        self.offen = False


def bauen(vorhanden=True, takt=0.01, **extra):
    frames, quellen = [], {}
    notaus = NotAus()

    def kamera():
        quellen["k"] = KameraQuelleFake(vorhanden)
        return Kamera(quelle=quellen["k"])

    def mikrofon(**kw):
        quellen["m"] = MikrofonQuelleFake()
        return Mikrofon(quelle=quellen["m"], **kw)

    medien = Medien(frame_weitergeben=lambda a, f: frames.append((a, f.sequenz)), not_aus=notaus, takt_s=takt,
                    kamera_bauen=kamera, mikrofon_bauen=mikrofon, **extra)
    return medien, frames, quellen, notaus


def warte_zustand(medien, agent, zustand, sekunden=3.0):
    ende = time.monotonic() + sekunden
    while time.monotonic() < ende and medien.kamera_zustand(agent) != zustand:
        time.sleep(0.005)
    return medien.kamera_zustand(agent)


class MedienTest(unittest.TestCase):
    def test_kamera_liefert_echte_frames_und_stoppt(self):
        medien, frames, quellen, _ = bauen()
        medien.kamera_umschalten("a")
        self.assertEqual(warte_zustand(medien, "a", "ein"), "ein")
        deadline = time.monotonic() + 3
        while len(frames) < 2 and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertGreaterEqual(len(frames), 2)
        self.assertEqual(medien.kamera_umschalten("a"), "aus")
        self.assertFalse(quellen["k"].offen)
        n = len(frames)
        time.sleep(0.05)
        self.assertEqual(len(frames), n)

    def test_fehlende_kamera_bleibt_fehler(self):
        medien, frames, _, _ = bauen(vorhanden=False)
        medien.kamera_umschalten("a")
        self.assertEqual(warte_zustand(medien, "a", "fehler"), "fehler")
        self.assertIn("kamera_nicht_gefunden", medien.fehlertext("a"))
        self.assertEqual(frames, [])

    def test_mikrofon_zaehlt_bloecke_nur_offen_und_sendet_nie(self):
        medien, _, quellen, _ = bauen()
        self.assertEqual(medien.mikrofon_umschalten("a"), "ein")
        quellen["m"].eingang(b"\x00\x00", None)
        self.assertEqual(medien.fuer("a").bloecke, 1)
        self.assertFalse(medien.audio_uebertragung)
        self.assertEqual(medien.mikrofon_umschalten("a"), "aus")
        self.assertFalse(quellen["m"].offen)

    def test_not_aus_stoppt_beides_und_sperrt_einschalten(self):
        medien, _, quellen, notaus = bauen()
        medien.kamera_umschalten("a")
        warte_zustand(medien, "a", "ein")
        medien.mikrofon_umschalten("a")
        notaus.ausloesen("test")
        self.assertEqual(medien.kamera_zustand("a"), "aus")
        self.assertEqual(medien.mikrofon_zustand("a"), "aus")
        self.assertEqual(medien.kamera_umschalten("a"), "aus")
        self.assertEqual(medien.mikrofon_umschalten("a"), "aus")

    def test_agenten_getrennt(self):
        medien, _, _, _ = bauen()
        medien.mikrofon_umschalten("a")
        self.assertEqual(medien.mikrofon_zustand("b"), "aus")


class VorschauTests(unittest.TestCase):
    def test_vorschau_bekommt_viele_bilder_der_agent_weiterhin_nur_im_takt(self):
        medien, frames, _, _ = bauen(takt=0.6)
        gesehen = []
        medien._vorschau = lambda agent, frame: gesehen.append(agent)
        medien.kamera_umschalten("a")
        warte_zustand(medien, "a", "ein")
        ende = time.monotonic() + 3
        while time.monotonic() < ende and len(gesehen) < 3:
            time.sleep(0.01)
        medien.kamera_umschalten("a")
        self.assertGreaterEqual(len(gesehen), 3)
        self.assertLess(len(frames), len(gesehen))  # der Strom zum Agenten bleibt sparsam
        self.assertGreaterEqual(len(frames), 1)  # das erste Bild geht sofort

    def test_ohne_vorschau_bleibt_alles_wie_vorher(self):
        medien, frames, _, _ = bauen(takt=0.01)
        medien.kamera_umschalten("a")
        warte_zustand(medien, "a", "ein")
        ende = time.monotonic() + 3
        while time.monotonic() < ende and len(frames) < 3:
            time.sleep(0.01)
        medien.kamera_umschalten("a")
        self.assertGreaterEqual(len(frames), 3)


class LangsameKameraTests(unittest.TestCase):
    def test_oeffnen_blockiert_den_aufrufer_nicht_und_der_zustand_ist_startet(self):
        frei = threading.Event()

        class Langsam(KameraQuelleFake):
            def oeffnen(self, index):
                frei.wait(5)
                return super().oeffnen(index)

        notaus = NotAus()
        medien = Medien(frame_weitergeben=lambda a, f: None, not_aus=notaus, takt_s=0.01,
                        kamera_bauen=lambda: Kamera(quelle=Langsam()), mikrofon_bauen=lambda **kw: Mikrofon(quelle=MikrofonQuelleFake(), **kw))
        start = time.monotonic()
        zustand = medien.kamera_umschalten("a")
        self.assertLess(time.monotonic() - start, 1.0)  # kehrt sofort zurück, obwohl das Öffnen noch hängt
        self.assertEqual(zustand, "startet")
        frei.set()
        self.assertEqual(warte_zustand(medien, "a", "ein"), "ein")
        medien.kamera_umschalten("a")

    def test_ausschalten_waehrend_des_oeffnens_schliesst_das_geraet_danach_gleich_wieder(self):
        frei = threading.Event()
        quellen = {}

        class Langsam(KameraQuelleFake):
            def oeffnen(self, index):
                frei.wait(5)
                return super().oeffnen(index)

        def kamera():
            quellen["k"] = Langsam()
            return Kamera(quelle=quellen["k"])

        medien = Medien(frame_weitergeben=lambda a, f: None, not_aus=NotAus(), takt_s=0.01, kamera_bauen=kamera,
                        mikrofon_bauen=lambda **kw: Mikrofon(quelle=MikrofonQuelleFake(), **kw))
        medien.kamera_umschalten("a")
        threading.Timer(0.2, frei.set).start()  # das Öffnen hängt noch, wenn der zweite Klick kommt
        medien.kamera_umschalten("a")  # zweiter Klick: abbrechen
        self.assertEqual(warte_zustand(medien, "a", "aus"), "aus")
        self.assertFalse(quellen["k"].offen)

    def test_not_aus_waehrend_des_oeffnens_laesst_die_kamera_zu(self):
        frei = threading.Event()
        quellen = {}
        notaus = NotAus()

        class Langsam(KameraQuelleFake):
            def oeffnen(self, index):
                frei.wait(5)
                return super().oeffnen(index)

        def kamera():
            quellen["k"] = Langsam()
            return Kamera(quelle=quellen["k"])

        medien = Medien(frame_weitergeben=lambda a, f: None, not_aus=notaus, takt_s=0.01, kamera_bauen=kamera,
                        mikrofon_bauen=lambda **kw: Mikrofon(quelle=MikrofonQuelleFake(), **kw))
        medien.kamera_umschalten("a")
        notaus.ausloesen("x")
        frei.set()
        ende = time.monotonic() + 3
        while time.monotonic() < ende and (quellen["k"].offen or medien.kamera_zustand("a") == "startet"):
            time.sleep(0.01)
        self.assertFalse(quellen["k"].offen)


class SpracheTests(unittest.TestCase):
    BLOCK = b"\x10\x27" * 1600  # 0,1 s, Amplitude 10000

    def baue(self, **extra):
        self.aeusserungen = []
        self.taste = {"an": False}
        medien, _f, quellen, notaus = bauen(audio_weitergeben=lambda a, wav, d: self.aeusserungen.append((a, wav, d)),
                                            taste=lambda vk: self.taste["an"] and vk == medien.sprechtaste_vk, **extra)
        return medien, quellen, notaus

    def sprechen(self, quellen, bloecke=10):
        for _ in range(bloecke):
            quellen["m"].eingang(self.BLOCK, None)

    def test_ohne_rueckruf_verlaesst_nichts_den_rechner(self):
        medien, _, quellen, _ = bauen()
        self.assertFalse(medien.audio_uebertragung)
        medien.mikrofon_umschalten("a")
        quellen["m"].eingang(self.BLOCK, None)
        self.assertEqual(medien.fuer("a").bloecke, 1)

    def test_standard_ist_sprechtaste_und_ohne_taste_wird_nichts_gesendet(self):
        medien, quellen, _ = self.baue()
        self.assertEqual(medien.modus, "sprechtaste")
        medien.mikrofon_umschalten("a")
        self.sprechen(quellen)
        self.assertEqual(self.aeusserungen, [])

    def test_gehaltene_sprechtaste_sendet_eine_aeusserung_als_wav(self):
        medien, quellen, _ = self.baue()
        medien.mikrofon_umschalten("a")
        self.taste["an"] = True
        self.sprechen(quellen, 10)
        self.taste["an"] = False
        quellen["m"].eingang(self.BLOCK, None)
        (agent, wav, dauer), = self.aeusserungen
        self.assertEqual((agent, dauer), ("a", 1000))
        self.assertTrue(wav.startswith(b"RIFF") and len(wav) == 44 + 32000)
        self.assertEqual(medien.fuer("a").aeusserungen, 1)

    def test_offener_modus_schneidet_aus_dem_strom(self):
        medien, quellen, _ = self.baue()
        medien.modus = "offen"
        medien.mikrofon_umschalten("a")
        self.sprechen(quellen, 6)
        for _ in range(12):
            quellen["m"].eingang(b"\x00\x00" * 1600, None)
        self.assertEqual(len(self.aeusserungen), 1)

    def test_not_aus_verwirft_die_fertige_aeusserung(self):
        medien, quellen, notaus = self.baue()
        medien.mikrofon_umschalten("a")
        self.taste["an"] = True
        self.sprechen(quellen, 10)
        notaus.ausloesen("x")
        self.taste["an"] = False
        quellen["m"].eingang(self.BLOCK, None)
        self.assertEqual(self.aeusserungen, [])

    def test_mikrofon_aus_verwirft_angefangenes(self):
        medien, quellen, _ = self.baue()
        medien.mikrofon_umschalten("a")
        self.taste["an"] = True
        self.sprechen(quellen, 5)
        medien.mikrofon_umschalten("a")  # aus
        medien.mikrofon_umschalten("a")  # wieder an
        self.taste["an"] = False
        quellen["m"].eingang(self.BLOCK, None)
        self.assertEqual(self.aeusserungen, [])

    def test_standardgeraet_und_gewaehltes_geraet_werden_an_das_oeffnen_gegeben(self):
        medien, quellen, _ = self.baue()
        medien.mikrofon_umschalten("a")
        self.assertIsNone(quellen["m"].geraet)  # Standard von Windows
        medien.mikrofon_umschalten("a")
        medien.mik_geraet = "Gibt es nicht"  # ohne sounddevice nicht auflösbar: bleibt als Name stehen statt ein anderes Gerät zu nehmen
        medien.mikrofon_umschalten("a")
        self.assertEqual(quellen["m"].geraet, "Gibt es nicht")

    def test_rueckruf_kann_nachtraeglich_verbunden_werden(self):
        medien, _, quellen, _ = bauen()
        medien.audio_verbinden(lambda *a: None)
        self.assertTrue(medien.audio_uebertragung)


if __name__ == "__main__":
    unittest.main()
