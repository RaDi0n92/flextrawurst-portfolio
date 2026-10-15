"""Das Lagebild eines Agenten: vollständig, mit Alter, „unbekannt“ als eigener Zustand, Pflicht zum Mitteilen."""

from __future__ import annotations

import unittest

from augen_haende_bridge import lage
from augen_haende_bridge.koerper import ampel
from augen_haende_bridge.koerper.ampel import Lampe
from augen_haende_bridge.transport import ProtocolError, Relay


def lampen(*teile):
    return [Lampe(k, n, f, w, behebe=b) for k, n, f, w, b in teile]


GRUEN = lampen(("bild", "Bilder kommen frisch an", "gruen", "Bild 2 s", None), ("hand", "Hände insgesamt", "gruen", "läuft", None),
               ("zustand", "Zustand des Ziel-Fensters", "gruen", "sichtbar", None))


class LageTests(unittest.TestCase):
    def nutz(self, liste):
        return lage.nutzlast("t-1", liste, ampel.gruppe_von)

    def test_alles_gruen_sagt_es_ausdruecklich(self):
        b = lage.bewerte(self.nutz(GRUEN), 1.0)
        self.assertTrue(b["bekannt"])
        self.assertEqual({g["zustand"] for g in b["gruppen"].values()}, {"läuft"})
        self.assertEqual(b["probleme"], [])
        self.assertIn("Alles, was gemessen wird, läuft", lage.satz(b))
        self.assertEqual(lage.kurz(b), "Lage: alles läuft.")

    def test_probleme_stehen_mit_funktion_zustand_grund_und_behebung_da(self):
        liste = GRUEN + lampen(("strom", "Bilderstrom", "rot", "KEIN BILD seit 4 min", "strom_neu"), ("sicht", "Ziel ist sichtbar", "gelb", "verdeckt", "fenster_vor"))
        b = lage.bewerte(self.nutz(liste), 2.0)
        self.assertEqual(b["gruppen"]["augen"]["zustand"], "kaputt")
        self.assertEqual([p["zustand"] for p in b["probleme"]], ["kaputt", "Achtung"], "das Schlimmste zuerst")
        self.assertEqual(b["probleme"][0]["behebe"], "strom_neu")
        s = lage.satz(b)
        self.assertIn("Augen: kaputt (KEIN BILD seit 4 min)", s)
        self.assertIn("Bilderstrom — kaputt: KEIN BILD seit 4 min", s)
        self.assertIn("bridge_cli.py say", s, "wer nicht selbst beheben kann, teilt es mit")

    def test_ohne_meldung_oder_zu_alt_ist_die_lage_unbekannt_nie_gruen(self):
        for b in (lage.bewerte(None, None), lage.bewerte(self.nutz(GRUEN), lage.ALTER_UNBEKANNT_S + 1)):
            self.assertFalse(b["bekannt"])
            self.assertIn("Lage unbekannt", lage.satz(b))
            self.assertIn("Lage unbekannt", lage.kurz(b))
            self.assertIn("bridge_cli.py say", lage.satz(b))
        self.assertIn("alt", lage.bewerte(self.nutz(GRUEN), 40)["grund"])

    def test_eine_gruppe_ohne_messung_heisst_unbekannt(self):
        b = lage.bewerte(self.nutz(lampen(("bild", "Bilder", "gruen", "ok", None))), 1.0)
        self.assertEqual((b["gruppen"]["haende"]["zustand"], b["gruppen"]["ziel"]["zustand"]), ("unbekannt", "unbekannt"))

    def test_die_echten_44_lampen_passen_in_die_nutzlast(self):
        z = ampel.Zustand(name="X", an=True, haende_an=True, strom_vorhanden=True, alter_s=1.0, gebunden=True, ziel_text="Ziel: Test", verbunden=True, ziel_zustand="ok")
        liste = ampel.lampen(z)
        n = self.nutz(liste)
        self.assertTrue(lage.gueltig(n))
        self.assertEqual(len(n["lampen"]), min(len(liste), lage.MAX_LAMPEN))
        self.assertTrue(lage.bewerte(n, 1.0)["bekannt"])

    def test_ungueltige_meldungen_werden_abgewiesen(self):
        for schlecht in (None, {}, {"terminal_id": "t", "lampen": "x"}, {"terminal_id": "t", "lampen": [{"f": "lila", "n": "a", "w": "b", "g": "augen"}]},
                         {"terminal_id": "t", "lampen": [{"f": "rot", "n": "a", "w": "b", "g": "unbekannt"}]}):
            self.assertFalse(lage.gueltig(schlecht))

    def test_der_transport_kennt_die_nachricht_und_prueft_sie(self):
        relay = Relay.__new__(Relay)
        gut = self.nutz(GRUEN)
        self.assertEqual(relay.terminal_payload("lage", gut), gut)
        for schlecht in ({**gut, "zusatz": 1}, {"terminal_id": "t-1", "lampen": [{"f": "lila"}]}, {"terminal_id": "t-1"}):
            with self.assertRaises(ProtocolError):
                relay.terminal_payload("lage", schlecht)


class KoerperSendetTests(unittest.TestCase):
    def setUp(self):
        from augen_haende_bridge.koerper.anwendung import KoerperAnwendung

        self.app = KoerperAnwendung.__new__(KoerperAnwendung)
        self.app._lage_zeit = {}
        self.gesendet = []
        self.app._senden = lambda kind, payload: self.gesendet.append((kind, payload)) or True
        self.liste = ampel.lampen(ampel.Zustand(name="X", an=True, haende_an=True, strom_vorhanden=True, alter_s=1.0, gebunden=True, ziel_text="Ziel: T", verbunden=True, ziel_zustand="ok"))

    def test_alle_fuenf_sekunden_und_gueltig_fuer_den_transport(self):
        relay = Relay.__new__(Relay)
        self.app._lage_senden("t-1", self.liste, 100.0)
        self.app._lage_senden("t-1", self.liste, 101.0)  # zu früh
        self.app._lage_senden("t-1", self.liste, 105.0)
        self.assertEqual([k for k, _ in self.gesendet], ["lage", "lage"])
        self.assertEqual(relay.terminal_payload("lage", self.gesendet[0][1]), self.gesendet[0][1])

    def test_jeder_agent_hat_seinen_eigenen_takt(self):
        self.app._lage_senden("t-1", self.liste, 100.0)
        self.app._lage_senden("t-2", self.liste, 100.5)
        self.assertEqual([p["terminal_id"] for _, p in self.gesendet], ["t-1", "t-2"])

    def test_nicht_gesendet_wird_nicht_als_gesendet_gemerkt_und_ein_fehler_haelt_nichts_an(self):
        self.app._senden = lambda kind, payload: False  # nicht verbunden
        self.app._lage_senden("t-1", self.liste, 100.0)
        self.assertEqual(self.app._lage_zeit, {})
        def kaputt(kind, payload):
            raise RuntimeError("weg")
        self.app._senden = kaputt
        self.app._lage_senden("t-1", self.liste, 101.0)  # wirft nicht


if __name__ == "__main__":
    unittest.main()
