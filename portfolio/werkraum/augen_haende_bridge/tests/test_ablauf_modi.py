"""G12: Modi — free, shadow, witness, daniel_gate, learning, delegated_learning einzeln und kombiniert; Lernen anfangs aus."""

from __future__ import annotations

import threading
import time
import unittest

from augen_haende_bridge import ablauf as ab
from augen_haende_bridge import ablauf_modi as am
from tests.test_ablauf import Handler, fluss


def aufbau(modi=("free",), bereich=lambda l: True, frist=1.0, lernen_aktiv=False, h=None, d=None):
    h = h or Handler()
    ereignisse, lernen = [], []
    m = am.Modi(am.Genehmigungen(), aufgabenbereich=bereich, ereignis=ereignisse.append, lernen=lernen.append, frist_s=frist, lernen_aktiv=lernen_aktiv)
    a = ab.Ablauf.aus_dict(d or fluss(), version=1)
    ausf = ab.Ausfuehrer(h.alle(), modi=m, schlafen=lambda s: None)
    lauf = ab.neuer_lauf(a, "t-1", frozenset(h.alle()), m.normalisieren(modi))
    return ausf, lauf, m, h, ereignisse, lernen


def handelnde_aufrufe(h):
    return [a for a in h.aufrufe if a["args"]["befehl"] == "aktion"]


class NormalisierenTests(unittest.TestCase):
    def test_standard_ist_free_und_unbekanntes_wird_abgelehnt(self):
        self.assertEqual(am.normalisieren(None), ("free",))
        self.assertEqual(am.normalisieren(()), ("free",))
        self.assertEqual(am.normalisieren("shadow"), ("shadow",))
        self.assertEqual(am.normalisieren(["witness", "free", "witness"]), ("witness", "free"))
        with self.assertRaises(am.ModiFehler) as c:
            am.normalisieren(["free", "wild"])
        self.assertEqual(str(c.exception), "modus_unbekannt:wild")

    def test_lernen_ist_anfangs_aus_und_muss_ausdruecklich_eingeschaltet_werden(self):
        for m in ("learning", "delegated_learning"):
            with self.assertRaises(am.ModiFehler) as c:
                am.normalisieren([m])
            self.assertEqual(str(c.exception), "lernen_ist_aus")
        self.assertEqual(am.normalisieren(["free", "learning"], lernen_aktiv=True), ("free", "learning"))
        self.assertFalse(am.Modi().lernen_aktiv)


class FreeTests(unittest.TestCase):
    def test_free_arbeitet_im_aufgabenbereich_ohne_einzelbestaetigung(self):
        ausf, lauf, m, h, _, _ = aufbau()
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, len(handelnde_aufrufe(h))), ("completed", 1))
        self.assertEqual(m.genehmigungen.offen(), [], "keine Frage an Daniel")

    def test_ausserhalb_des_aufgabenbereichs_geschieht_nichts(self):
        ausf, lauf, m, h, _, _ = aufbau(bereich=lambda l: False)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual(lauf.status, "blocked")
        self.assertIn("Freigabe verweigert", lauf.grund)
        self.assertEqual(handelnde_aufrufe(h), [])
        self.assertEqual([a["args"]["befehl"] for a in h.aufrufe], ["liste"], "Beobachten ist erlaubt, Handeln nicht")


class ShadowTests(unittest.TestCase):
    def test_shadow_fuehrt_nichts_aus_und_kennzeichnet_alles_als_simuliert(self):
        ausf, lauf, m, h, _, _ = aufbau(("shadow",))
        ausf.starten(lauf)
        ausf.laufen(lauf)
        klick = next(e for e in lauf.verlauf if e.knoten == "klicken")
        self.assertEqual((klick.simuliert, klick.status, handelnde_aufrufe(h)), (True, "simuliert", []))
        self.assertEqual(lauf.ctx["klicken"], {"ok": None, "simuliert": True})
        self.assertEqual(m.genehmigungen.offen(), [])

    def test_shadow_gewinnt_gegen_daniel_gate_und_free(self):
        ausf, lauf, m, h, _, _ = aufbau(("free", "daniel_gate", "shadow"), frist=0.2)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, handelnde_aufrufe(h), m.genehmigungen.offen()), ("completed", [], []), "Shadow fragt Daniel nicht: es geschieht ja nichts")

    def test_ein_tor_ist_unter_shadow_offen(self):
        d = fluss()
        d["knoten"]["tor"] = {"art": "tor", "name": "Freigabe"}
        d["kanten"] = [{"von": "messen", "nach": "tor", "wenn": "ok"}, {"von": "tor", "nach": "fertig", "wenn": "ok"}]
        ausf, lauf, m, h, _, _ = aufbau(("shadow",), d=d)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "fertig"}))


class DanielGateTests(unittest.TestCase):
    def antworte(self, m, ja, verzoegerung=0.1):
        def lauf():
            ende = time.monotonic() + 3
            while time.monotonic() < ende:
                offen = m.genehmigungen.offen()
                if offen:
                    time.sleep(verzoegerung)
                    m.genehmigungen.entscheiden(offen[0]["id"], ja)
                    return
                time.sleep(0.01)

        t = threading.Thread(target=lauf)
        t.start()
        return t

    def test_vor_jeder_handelnden_aktion_wird_gefragt_ja_fuehrt_aus(self):
        ausf, lauf, m, h, _, _ = aufbau(("daniel_gate",), frist=3)
        t = self.antworte(m, True)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        t.join(5)
        self.assertEqual((lauf.status, len(handelnde_aufrufe(h))), ("completed", 1))

    def test_nein_und_keine_antwort_fuehren_nichts_aus(self):
        ausf, lauf, m, h, _, _ = aufbau(("daniel_gate",), frist=3)
        t = self.antworte(m, False)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        t.join(5)
        self.assertEqual((lauf.status, handelnde_aufrufe(h)), ("blocked", []))
        self.assertIn("freigabe", lauf.grund.lower())
        ausf2, lauf2, m2, h2, _, _ = aufbau(("daniel_gate",), frist=0.2)
        ausf2.starten(lauf2)
        ausf2.laufen(lauf2)
        self.assertEqual((lauf2.status, handelnde_aufrufe(h2)), ("blocked", []))
        self.assertIn("zeitablauf", lauf2.grund)

    def test_die_frage_nennt_was_gleich_geschieht_und_pause_bricht_das_warten_ab(self):
        ausf, lauf, m, h, _, _ = aufbau(("daniel_gate",), frist=5)
        ausf.starten(lauf)
        t = threading.Thread(target=ausf.laufen, args=(lauf,))
        t.start()
        ende = time.monotonic() + 3
        while time.monotonic() < ende and not m.genehmigungen.offen():
            time.sleep(0.01)
        frage = m.genehmigungen.offen()[0]
        self.assertEqual((frage["lauf"], frage["knoten"]), (lauf.id, "klicken"))
        self.assertIn("weltdom", frage["beschreibung"])
        ausf.pausieren(lauf)
        t.join(5)
        self.assertEqual(handelnde_aufrufe(h), [], "nach der Pause wurde nichts mehr getan")
        self.assertFalse(m.genehmigungen.entscheiden("g-gibts-nicht", True))

    def test_ein_tor_knoten_fragt_immer_auch_unter_free(self):
        d = fluss()
        d["knoten"]["tor"] = {"art": "tor", "name": "Freigabe"}
        d["kanten"] = [{"von": "messen", "nach": "tor", "wenn": "ok"}, {"von": "tor", "nach": "fertig", "wenn": "ok"}]
        ausf, lauf, m, h, _, _ = aufbau(("free",), frist=3, d=d)
        t = self.antworte(m, True)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        t.join(5)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "fertig"}))
        ausf2, lauf2, m2, _, _, _ = aufbau(("free",), frist=0.2, d=d)
        ausf2.starten(lauf2)
        ausf2.laufen(lauf2)
        self.assertEqual(lauf2.status, "blocked")


class WitnessLernenTests(unittest.TestCase):
    def test_witness_meldet_jeden_schritt_ohne_den_lauf_aufzuhalten_und_ein_kaputter_beobachter_stoert_nicht(self):
        ausf, lauf, m, h, ereignisse, _ = aufbau(("witness",))
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual([e["knoten"] for e in ereignisse], ["messen", "klicken", "fertig"])
        self.assertEqual(lauf.status, "completed")
        m._ereignis = lambda e: (_ for _ in ()).throw(RuntimeError("kaputt"))
        ausf2, lauf2, m2, _, _, _ = aufbau(("witness",))
        m2._ereignis = m._ereignis
        ausf2.starten(lauf2)
        ausf2.laufen(lauf2)
        self.assertEqual(lauf2.status, "completed")

    def test_ohne_witness_keine_meldungen(self):
        ausf, lauf, m, h, ereignisse, _ = aufbau(("free",))
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual(ereignisse, [])

    def test_lernen_zeichnet_auf_wenn_eingeschaltet_und_nie_simuliertes(self):
        ausf, lauf, m, h, _, lernen = aufbau(("learning",), lernen_aktiv=True)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual([e["knoten"] for e in lernen], ["messen", "klicken", "fertig"])
        self.assertEqual(lernen[1]["ergebnis"]["ruecklese"]["bestaetigt"], True)
        self.assertEqual(lernen[1]["ablauf"], "demo@1")
        self.assertFalse(lernen[1]["delegiert"])
        ausf2, lauf2, m2, _, _, lernen2 = aufbau(("shadow", "learning"), lernen_aktiv=True)
        ausf2.starten(lauf2)
        ausf2.laufen(lauf2)
        self.assertTrue(all(e["status"] != "simuliert" for e in lernen2), "Simuliertes wird nie als Erfahrung gelernt")

    def test_delegiertes_lernen_nennt_den_auswerter(self):
        d = fluss()
        ausf, lauf, m, h, _, lernen = aufbau(("delegated_learning",), lernen_aktiv=True, d=d)
        lauf.zustand["auswerter"] = "Claude"
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertTrue(lernen and all(e["delegiert"] and e["auswerter"] == "Claude" for e in lernen))

    def test_ist_das_lernen_ausgeschaltet_zeichnet_ein_gesetzter_modus_nichts_auf(self):
        ausf, lauf, m, h, _, lernen = aufbau(("free",), lernen_aktiv=True)
        lauf.modi = ("free", "learning")
        m.lernen_aktiv = False
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual(lernen, [])

    def test_kombination_witness_daniel_gate_learning(self):
        ausf, lauf, m, h, ereignisse, lernen = aufbau(("witness", "daniel_gate", "learning"), lernen_aktiv=True, frist=3)
        t = DanielGateTests().antworte(m, True)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        t.join(5)
        self.assertEqual((lauf.status, len(ereignisse), len(lernen), len(handelnde_aufrufe(h))), ("completed", 3, 3, 1))


if __name__ == "__main__":
    unittest.main()
