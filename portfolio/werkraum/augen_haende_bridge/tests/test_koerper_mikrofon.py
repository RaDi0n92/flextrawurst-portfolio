"""Tests für koerper/mikrofon.py: Zustand, Stummschaltung, Push-to-talk und Sequenzierung — mit einer injizierten
Fake-Quelle für die Logik, und einem echten `SounddeviceMikrofonQuelle`-Lauf gegen diesen Container, der ohne die
native PortAudio-Bibliothek auskommen muss, um zu belegen, dass das kontrolliert als benannter Fehlschlag zurückkommt
statt als unbehandelte Ausnahme (G07: "Gerätefehler ... zurückgelesen"; `pruefe_koerper.py` V04 verbietet eine bloße
Boolean-Attrappe)."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper.mikrofon import Mikrofon, MikrofonFehler, SounddeviceMikrofonQuelle


class FakeMikrofonQuelle:
    def __init__(self, *, wirft: Exception | None = None):
        self.wirft = wirft
        self.eingang = None
        self.oeffnen_aufrufe: list[tuple] = []
        self.geschlossen = False

    def oeffnen(self, geraet, abtastrate, kanaele, eingang) -> None:
        self.oeffnen_aufrufe.append((geraet, abtastrate, kanaele))
        if self.wirft is not None:
            raise self.wirft
        self.eingang = eingang

    def schliessen(self) -> None:
        self.geschlossen = True

    def sende(self, pcm: bytes, status=None) -> None:
        self.eingang(pcm, status)


class EinschaltenTests(unittest.TestCase):
    def test_erfolgreiches_einschalten_setzt_aktiv_und_loescht_den_fehler(self) -> None:
        mikrofon = Mikrofon(quelle=FakeMikrofonQuelle())
        self.assertTrue(mikrofon.einschalten())
        self.assertTrue(mikrofon.aktiv)
        self.assertIsNone(mikrofon.letzter_fehler)

    def test_fehlgeschlagenes_oeffnen_meldet_sich_statt_zu_taeuschen(self) -> None:
        mikrofon = Mikrofon(quelle=FakeMikrofonQuelle(wirft=MikrofonFehler("mikrofon_geraet_fehlgeschlagen:kaputt")))
        self.assertFalse(mikrofon.einschalten())
        self.assertFalse(mikrofon.aktiv)
        self.assertEqual(mikrofon.letzter_fehler, "mikrofon_geraet_fehlgeschlagen:kaputt")

    def test_zweimaliges_einschalten_oeffnet_die_quelle_nur_einmal(self) -> None:
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle)
        mikrofon.einschalten(3, abtastrate=48000, kanaele=2)
        mikrofon.einschalten(3, abtastrate=48000, kanaele=2)
        self.assertEqual(quelle.oeffnen_aufrufe, [(3, 48000, 2)])


class PushToTalkTests(unittest.TestCase):
    def test_ohne_gedrueckte_sprechtaste_kommt_im_push_to_talk_modus_kein_block_durch(self) -> None:
        empfangen = []
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle, block_empfangen=empfangen.append)
        mikrofon.einschalten()
        quelle.sende(b"\x00\x01")
        self.assertEqual(empfangen, [])

    def test_gedrueckte_sprechtaste_laesst_bloecke_mit_sequenz_und_herkunft_durch(self) -> None:
        empfangen = []
        zeiten = iter([500, 516])
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle, jetzt_ms=lambda: next(zeiten), block_empfangen=empfangen.append)
        mikrofon.einschalten("usb-mic", abtastrate=16000, kanaele=1)
        mikrofon.sprechtaste(True)
        quelle.sende(b"\x00\x01")
        quelle.sende(b"\x02\x03")
        self.assertEqual([b.sequenz for b in empfangen], [1, 2])
        self.assertEqual(empfangen[0].aufgenommen_ms, 500)
        self.assertEqual(empfangen[0].abtastrate, 16000)
        self.assertEqual(empfangen[0].kanaele, 1)
        self.assertEqual(empfangen[0].quelle, "sounddevice:usb-mic")

    def test_loslassen_der_sprechtaste_stoppt_die_weitergabe_sofort(self) -> None:
        empfangen = []
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle, block_empfangen=empfangen.append)
        mikrofon.einschalten()
        mikrofon.sprechtaste(True)
        quelle.sende(b"\x00")
        mikrofon.sprechtaste(False)
        quelle.sende(b"\x01")
        self.assertEqual(len(empfangen), 1)

    def test_offener_modus_sendet_ohne_gedrueckte_sprechtaste(self) -> None:
        empfangen = []
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle, block_empfangen=empfangen.append)
        mikrofon.einschalten()
        mikrofon.modus_setzen("offen")
        quelle.sende(b"\x00")
        self.assertEqual(len(empfangen), 1)

    def test_stummschaltung_gewinnt_auch_bei_gedrueckter_sprechtaste(self) -> None:
        empfangen = []
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle, block_empfangen=empfangen.append)
        mikrofon.einschalten()
        mikrofon.sprechtaste(True)
        mikrofon.stummschalten(True)
        quelle.sende(b"\x00")
        self.assertEqual(empfangen, [])

    def test_ein_statusfehler_wird_gemeldet_auch_wenn_der_block_nicht_weitergegeben_wird(self) -> None:
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle)
        mikrofon.einschalten()
        quelle.sende(b"\x00", status="input overflow")
        self.assertEqual(mikrofon.letzter_fehler, "input overflow")


class AusschaltenTests(unittest.TestCase):
    def test_ausschalten_gibt_das_geraet_frei(self) -> None:
        quelle = FakeMikrofonQuelle()
        mikrofon = Mikrofon(quelle=quelle)
        mikrofon.einschalten()
        mikrofon.ausschalten()
        self.assertFalse(mikrofon.aktiv)
        self.assertTrue(quelle.geschlossen)

    def test_ausschalten_ohne_vorheriges_einschalten_fasst_die_quelle_nicht_an(self) -> None:
        quelle = FakeMikrofonQuelle()
        Mikrofon(quelle=quelle).ausschalten()
        self.assertFalse(quelle.geschlossen)


class SounddeviceMikrofonQuelleTests(unittest.TestCase):
    """Echter Lauf gegen diesen Container: PortAudio ist hier nicht installiert, `sounddevice` scheitert schon beim
    Import mit `OSError`. Belegt, dass das als `MikrofonFehler` durchgereicht wird statt als unbehandelte Ausnahme."""

    def test_fehlende_portaudio_bibliothek_wird_zu_einem_benannten_fehlschlag(self) -> None:
        with self.assertRaises(MikrofonFehler):
            SounddeviceMikrofonQuelle().oeffnen(None, 16000, 1, lambda pcm, status: None)


class FakeSd:
    def __init__(self, geraete, schnittstellen):
        self._g, self._h = geraete, schnittstellen

    def query_devices(self):
        return self._g

    def query_hostapis(self):
        return self._h


SCHNITTSTELLEN = [{"name": "MME"}, {"name": "Windows WASAPI"}]
GERAETE = [
    {"name": "Mikrofon A", "max_input_channels": 2, "hostapi": 0},
    {"name": "Lautsprecher", "max_input_channels": 0, "hostapi": 0},
    {"name": "Mikrofon B", "max_input_channels": 1, "hostapi": 0},
    {"name": "Mikrofon A", "max_input_channels": 2, "hostapi": 1},  # dasselbe Gerät über WASAPI
    {"name": "Mikrofon C", "max_input_channels": 1, "hostapi": 1},  # nur über WASAPI
]


class GeraeteTests(unittest.TestCase):
    def test_eingabegeraete_je_name_einmal_ueber_mme_und_ohne_ausgaenge(self) -> None:
        from augen_haende_bridge.koerper.mikrofon import eingabegeraete
        self.assertEqual(eingabegeraete(FakeSd(GERAETE, SCHNITTSTELLEN)), [(0, "Mikrofon A"), (2, "Mikrofon B")])

    def test_ohne_mme_werden_alle_schnittstellen_entdoppelt(self) -> None:
        from augen_haende_bridge.koerper.mikrofon import eingabegeraete
        namen = [n for _, n in eingabegeraete(FakeSd(GERAETE, [{"name": "ALSA"}, {"name": "JACK"}]))]
        self.assertEqual(namen, ["Mikrofon A", "Mikrofon B", "Mikrofon C"])

    def test_fehler_ergeben_eine_leere_liste(self) -> None:
        from augen_haende_bridge.koerper.mikrofon import eingabegeraete

        class Kaputt:
            def query_devices(self):
                raise OSError("portaudio")

        self.assertEqual(eingabegeraete(Kaputt()), [])

    def test_geraet_index_loest_den_namen_auf(self) -> None:
        from augen_haende_bridge.koerper.mikrofon import geraet_index
        sd = FakeSd(GERAETE, SCHNITTSTELLEN)
        self.assertIsNone(geraet_index(None, sd))
        self.assertIsNone(geraet_index("", sd))
        self.assertEqual(geraet_index("Mikrofon B", sd), 2)

    def test_verschwundenes_geraet_bleibt_als_name_stehen_statt_ein_anderes_zu_nehmen(self) -> None:
        from augen_haende_bridge.koerper.mikrofon import geraet_index
        self.assertEqual(geraet_index("Weg", FakeSd(GERAETE, SCHNITTSTELLEN)), "Weg")


if __name__ == "__main__":
    unittest.main()
