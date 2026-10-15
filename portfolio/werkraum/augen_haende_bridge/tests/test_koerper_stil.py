"""Tests für koerper/stil.py — Deckkraft, Kürzel und Farbrechnung. Reine Logik, kein Windows nötig."""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import stil


class DeckkraftTests(unittest.TestCase):
    def test_r031_start_ist_34_prozent_deckkraft_gleich_66_prozent_transparent(self) -> None:
        self.assertEqual(stil.DECKKRAFT_START_PROZENT, 34)
        self.assertEqual(100 - stil.DECKKRAFT_START_PROZENT, 66)

    def test_deckkraft_alpha_rechnet_prozent_in_ein_byte_um(self) -> None:
        self.assertEqual(stil.deckkraft_alpha(0), 0)
        self.assertEqual(stil.deckkraft_alpha(100), 255)
        self.assertEqual(stil.deckkraft_alpha(34), round(34 * 255 / 100))

    def test_deckkraft_alpha_kappt_ausserhalb_von_0_bis_100(self) -> None:
        self.assertEqual(stil.deckkraft_alpha(-10), 0)
        self.assertEqual(stil.deckkraft_alpha(150), 255)

    def test_alpha_prozent_ist_die_umkehrung_von_deckkraft_alpha(self) -> None:
        for prozent in stil.DECKKRAFT_STUFEN_PROZENT:
            self.assertEqual(stil.alpha_prozent(stil.deckkraft_alpha(prozent)), prozent)

    def test_naechste_stufe_geht_die_stufenliste_aufwaerts(self) -> None:
        self.assertEqual(stil.naechste_stufe(34), 50)
        self.assertEqual(stil.naechste_stufe(40), 50)
        self.assertEqual(stil.naechste_stufe(50), 75)
        self.assertEqual(stil.naechste_stufe(75), 100)

    def test_naechste_stufe_hat_eine_ein_prozent_toleranz_um_eine_stufe(self) -> None:
        # "stufe > prozent + 1": ein Wert direkt auf einer Stufe (z.B. durch Rundung) überspringt sie
        # und springt zur übernächsten, statt an Ort und Stelle stehen zu bleiben.
        self.assertEqual(stil.naechste_stufe(49), 75)

    def test_naechste_stufe_springt_von_der_letzten_stufe_zurueck_zur_ersten(self) -> None:
        self.assertEqual(stil.naechste_stufe(100), stil.DECKKRAFT_STUFEN_PROZENT[0])


class KuerzelTests(unittest.TestCase):
    def test_kuerzel_nimmt_die_ersten_beiden_buchstaben_grossgeschrieben(self) -> None:
        self.assertEqual(stil.kuerzel_aus_name("codex"), "CO")

    def test_kuerzel_ueberspringt_leerzeichen_und_sonderzeichen(self) -> None:
        self.assertEqual(stil.kuerzel_aus_name("· gemini ·"), "GE")

    def test_kuerzel_fuer_leeren_namen_ist_ein_fragezeichen(self) -> None:
        self.assertEqual(stil.kuerzel_aus_name("···"), "?")


class FarbrechnungTests(unittest.TestCase):
    def test_farbe_hell_skaliert_jeden_kanal(self) -> None:
        grundfarbe = stil.w.rgb(40, 60, 80)
        aufgehellt = stil.farbe_hell(grundfarbe, 2.0)
        self.assertEqual(aufgehellt, stil.w.rgb(80, 120, 160))

    def test_farbe_hell_kappt_bei_255(self) -> None:
        grundfarbe = stil.w.rgb(200, 200, 200)
        aufgehellt = stil.farbe_hell(grundfarbe, 2.0)
        self.assertEqual(aufgehellt, stil.w.rgb(255, 255, 255))

    def test_skaliert_rundet_und_bleibt_mindestens_bei_eins(self) -> None:
        self.assertEqual(stil.skaliert(16, 1.5), 24)
        self.assertEqual(stil.skaliert(1, 0.01), 1)

    def test_agentenfarben_sind_websichere_hexcodes(self) -> None:
        for farbe in stil.AGENTENFARBEN:
            self.assertRegex(farbe, r"^#[0-9A-Fa-f]{6}$")

    def test_agentenfarben_sind_alle_verschieden(self) -> None:
        self.assertEqual(len(set(stil.AGENTENFARBEN)), len(stil.AGENTENFARBEN))

class AgentenfarbeTests(unittest.TestCase):
    def test_farbe_ist_stabil_und_aus_der_liste(self) -> None:
        from augen_haende_bridge.koerper import stil as s
        for name in ("Claude", "Codex-Host", "Gemgem", "GLM", ""):
            self.assertIn(s.agentenfarbe(name), s.AGENTENFARBEN)
            self.assertEqual(s.agentenfarbe(name), s.agentenfarbe(name))

    def test_farbe_ist_ueber_prozesse_hinweg_gleich(self) -> None:
        import subprocess
        import sys
        code = "from augen_haende_bridge.koerper import stil; print(stil.agentenfarbe('Claude'))"
        laeufe = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                 env={"PYTHONPATH": "src", "PYTHONHASHSEED": str(seed), "PATH": "/usr/bin:/bin"}).stdout
                  for seed in (1, 2, 3, 99)}
        self.assertEqual(len(laeufe), 1)


if __name__ == "__main__":
    unittest.main()

