"""Äußerungen schneiden: Sprechtaste, offenes Mikrofon mit Energieerkennung, WAV-Verpackung."""

from __future__ import annotations

import array
import struct
import unittest

from augen_haende_bridge.koerper.sprachaufnahme import (
    MAX_S,
    MODUS_OFFEN,
    MODUS_SPRECHTASTE,
    RATE,
    Segmentierer,
    mittlere_amplitude,
    wav_bytes,
)

BLOCK = RATE // 10  # 0,1 s


def pcm(amplitude: int, bloecke: int = 1) -> bytes:
    return struct.pack("<h", amplitude) * BLOCK * bloecke


class WavTests(unittest.TestCase):
    def test_kopf_stimmt(self):
        daten = pcm(100, 3)
        wav = wav_bytes(daten)
        self.assertEqual(wav[:4], b"RIFF")
        self.assertEqual(struct.unpack("<I", wav[4:8])[0], 36 + len(daten))
        self.assertEqual(wav[8:16], b"WAVEfmt ")
        fmt = struct.unpack("<IHHIIHH", wav[16:36])
        self.assertEqual(fmt, (16, 1, 1, RATE, RATE * 2, 2, 16))
        self.assertEqual(wav[36:40], b"data")
        self.assertEqual(struct.unpack("<I", wav[40:44])[0], len(daten))
        self.assertEqual(wav[44:], daten)

    def test_amplitude(self):
        self.assertEqual(mittlere_amplitude(pcm(1000)), 1000)
        self.assertEqual(mittlere_amplitude(pcm(-1000)), 1000)
        self.assertEqual(mittlere_amplitude(b""), 0.0)
        self.assertEqual(mittlere_amplitude(b"\x01"), 0.0)


class SprechtasteTests(unittest.TestCase):
    def baue(self):
        self.ergebnisse = []
        self.taste = {"an": False}
        return Segmentierer(lambda p, d: self.ergebnisse.append((p, d)), modus=lambda: MODUS_SPRECHTASTE,
                            sprechtaste_gehalten=lambda: self.taste["an"])

    def test_ohne_taste_wird_nichts_aufgenommen(self):
        s = self.baue()
        for _ in range(20):
            s.block(pcm(9000))
        self.assertEqual(self.ergebnisse, [])

    def test_taste_halten_und_loslassen_gibt_eine_aeusserung(self):
        s = self.baue()
        self.taste["an"] = True
        for _ in range(10):
            s.block(pcm(3000))
        self.taste["an"] = False
        s.block(pcm(0))
        self.assertEqual(len(self.ergebnisse), 1)
        self.assertEqual(self.ergebnisse[0][1], 1000)
        self.assertEqual(len(self.ergebnisse[0][0]), BLOCK * 10 * 2)

    def test_zu_kurzes_tippen_wird_verworfen(self):
        s = self.baue()
        self.taste["an"] = True
        s.block(pcm(3000))
        self.taste["an"] = False
        s.block(pcm(0))
        self.assertEqual(self.ergebnisse, [])

    def test_sehr_lange_aeusserung_wird_geteilt_und_die_taste_bleibt_aktiv(self):
        s = self.baue()
        self.taste["an"] = True
        for _ in range(int(MAX_S * 10) + 30):
            s.block(pcm(3000))
        self.taste["an"] = False
        s.block(pcm(0))
        self.assertEqual(len(self.ergebnisse), 2)
        self.assertLessEqual(self.ergebnisse[0][1], int(MAX_S * 1000) + 100)

    def test_andere_abtastrate_wird_ignoriert(self):
        s = self.baue()
        self.taste["an"] = True
        for _ in range(10):
            s.block(pcm(3000), rate=44100)
        self.taste["an"] = False
        s.block(pcm(0), rate=44100)
        self.assertEqual(self.ergebnisse, [])


class OffenTests(unittest.TestCase):
    def baue(self):
        self.ergebnisse = []
        return Segmentierer(lambda p, d: self.ergebnisse.append((p, d)), modus=lambda: MODUS_OFFEN)

    def test_stille_bleibt_still(self):
        s = self.baue()
        for _ in range(100):
            s.block(pcm(20))
        self.assertEqual(self.ergebnisse, [])

    def test_sprache_mit_vorlauf_und_nachlauf_wird_ausgeschnitten(self):
        s = self.baue()
        for _ in range(10):
            s.block(pcm(20))
        for _ in range(10):
            s.block(pcm(4000))
        for _ in range(12):
            s.block(pcm(20))
        self.assertEqual(len(self.ergebnisse), 1)
        _daten, dauer_ms = self.ergebnisse[0]
        self.assertGreaterEqual(dauer_ms, 1000 + 300)  # Sprache plus Vorlauf plus Nachlauf

    def test_einzelner_knall_ist_keine_sprache(self):
        s = self.baue()
        s.block(pcm(20))
        s.block(pcm(9000))
        for _ in range(20):
            s.block(pcm(20))
        self.assertEqual(self.ergebnisse, [])

    def test_kurze_pause_mitten_im_satz_trennt_nicht(self):
        s = self.baue()
        for _ in range(5):
            s.block(pcm(4000))
        for _ in range(4):
            s.block(pcm(20))  # 0,4 s Pause, kürzer als der Nachlauf
        for _ in range(5):
            s.block(pcm(4000))
        for _ in range(12):
            s.block(pcm(20))
        self.assertEqual(len(self.ergebnisse), 1)

    def test_zwei_saetze_mit_langer_pause_sind_zwei_aeusserungen(self):
        s = self.baue()
        for _ in range(2):
            for _ in range(6):
                s.block(pcm(4000))
            for _ in range(12):
                s.block(pcm(20))
        self.assertEqual(len(self.ergebnisse), 2)

    def test_zuruecksetzen_verwirft_angefangenes(self):
        s = self.baue()
        for _ in range(6):
            s.block(pcm(4000))
        s.zuruecksetzen()
        for _ in range(12):
            s.block(pcm(20))
        self.assertEqual(self.ergebnisse, [])


if __name__ == "__main__":
    unittest.main()
