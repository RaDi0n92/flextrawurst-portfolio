"""G13: die Kapsel holt Zeichnungen, Bindung und WorldDOM-Knoten vom Körper (über den bestehenden WorldDOM-Befehl); antwortet er nicht, steht der Grund als Lücke da."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from client_vps.kapsel_dienst import KapselDienst


def launcher(antwort):
    aufrufe = []

    def weltdom_befehl(tid, request):
        aufrufe.append((tid, request))
        return antwort(request)

    a = SimpleNamespace(name="Codex", terminal_id="t-1", zu_dict=lambda: {"terminal_id": "t-1", "name": "Codex"}, faehigkeiten=lambda: [])
    reg = SimpleNamespace(agenten={"t-1": a}, auftraege_an=lambda t: [], finde=lambda n: a if n == "Codex" else None)
    return SimpleNamespace(register=reg, agenten_liste=lambda: [{"terminal_id": "t-1", "name": "Codex", "ziel_info": {}}], ziel_info={"t-1": {"target_id": "kde1:window:42", "zustand": "da"}},
                           anzeige={"t-1": "kde1"}, ziel={"t-1": "kde1"}, frames_dir=Path(tempfile.mkdtemp()), ablauf=SimpleNamespace(laeufe={}), weltdom_befehl=weltdom_befehl), aufrufe


def knoten(herkunft):
    return {"ok": True, "knoten": [{"id": f"n-{herkunft}", "herkunft": herkunft, "name": herkunft}]}


class KapselDienstTests(unittest.TestCase):
    def test_antwortet_der_koerper_sind_beide_luecken_zu_und_der_stand_steht_in_der_kapsel(self):
        l, aufrufe = launcher(lambda r: knoten(r["args"].get("herkunft", "real")))
        d = KapselDienst(l, Path(tempfile.mkdtemp()))
        r = d.moment("Test", "agent", "g", agenten=["t-1"])
        self.assertTrue(r["ok"], r)
        k = d.store.laden(r["kapsel"])
        self.assertEqual([x["feld"] for x in k["luecken"] if x["feld"].startswith(("koerper", "weltdom"))], [])
        self.assertEqual([n["id"] for n in k["koerper"]["t-1"]["anker"]], ["n-authored"])
        self.assertEqual([n["id"] for n in k["koerper"]["t-1"]["projiziert"]], ["n-projected"])
        self.assertEqual(k["koerper"]["t-1"]["bindung"]["target_id"], "kde1:window:42")
        self.assertEqual(k["weltdom"]["kde1:window:42"][0]["id"], "n-real")
        self.assertTrue(all(a[1]["args"]["neu_messen"] is False for a in aufrufe), "eine Kapsel misst nie selbst neu, sie hält den Stand fest")

    def test_antwortet_er_nicht_steht_der_grund_da_und_die_kapsel_entsteht_trotzdem(self):
        l, _ = launcher(lambda r: {"ok": False, "reason": "keine_antwort"})
        d = KapselDienst(l, Path(tempfile.mkdtemp()))
        r = d.moment("Test", "agent", "g", agenten=["t-1"])
        self.assertTrue(r["ok"])
        gruende = {}
        for x in r["luecken"]:
            gruende.setdefault(x["feld"], []).append(x["grund"])
        self.assertTrue(any("keine_antwort" in g for g in gruende["koerper.t-1"]), gruende)
        self.assertTrue(any("keine_antwort" in g for g in gruende["weltdom.kde1:window:42"]), gruende)

    def test_ein_ziel_ohne_agent_wird_als_luecke_gemeldet(self):
        l, _ = launcher(lambda r: knoten("real"))
        l.ziel_info = {"t-1": {"target_id": "kde1:window:42"}}
        q = KapselDienst(l, Path(tempfile.mkdtemp())).quellen()
        l.ziel_info = {}
        with self.assertRaises(LookupError):
            q.weltdom("kde1:window:42")


class ZweigTests(unittest.TestCase):
    def aufbau(self, messen_ok=True):
        l, _ = launcher(lambda r: knoten("real") if messen_ok else {"ok": False, "reason": "keine_antwort"})
        l.ablauf = SimpleNamespace(laeufe={"l-1": SimpleNamespace(id="l-1", agent="t-1")}, befehl=lambda agent, req: {"ok": True, "lauf": "l-2", "hinweis": "neuer Lauf"})
        d = KapselDienst(l, Path(tempfile.mkdtemp()))
        r = d.moment("Test", "agent", "g", agenten=["t-1"])
        return l, d, r["kapsel"]

    def test_ein_zweig_aus_einer_kapsel_darf_erst_nach_frischer_messung_starten(self):
        from client_vps.ablauf_dienst import AblaufDienst

        l, d, kid = self.aufbau()
        l.kapseln = d
        r = d.zweig_aus_kapsel("t-1", kid, "l-1", "cp")
        self.assertTrue(r["ok"], r)
        self.assertIn("frisch gemessen", r["hinweis"])
        self.assertFalse(d.zweig_darf_starten("l-2"))
        a = AblaufDienst.__new__(AblaufDienst)
        a.l, a.ausf, a._laufen = l, SimpleNamespace(fortsetzen=lambda lauf: True), lambda lauf: None
        lauf = SimpleNamespace(id="l-2", agent="t-1", status="paused")
        gesperrt = a._steuern_lauf(lauf, "weiter", {})
        self.assertEqual((gesperrt["ok"], gesperrt["reason"]), (False, "frische_messung_fehlt"))
        self.assertEqual(d.zweig_messen("t-1", "l-2")["ok"], True)
        self.assertTrue(d.zweig_darf_starten("l-2"))
        self.assertTrue(a._steuern_lauf(lauf, "weiter", {})["ok"])

    def test_misslingt_die_messung_bleibt_der_zweig_gesperrt(self):
        l, d, kid = self.aufbau()
        d.zweig_aus_kapsel("t-1", kid, "l-1", "cp")
        l.weltdom_befehl = lambda tid, req: {"ok": False, "reason": "keine_antwort"}
        r = d.zweig_messen("t-1", "l-2")
        self.assertEqual((r["ok"], r["frisch"]), (False, False))
        self.assertFalse(d.zweig_darf_starten("l-2"))

    def test_fremde_und_unbekannte_laeufe_und_kapseln(self):
        l, d, kid = self.aufbau()
        self.assertEqual(d.zweig_aus_kapsel("t-1", "k-gibtsnicht", "l-1", "cp")["ok"], False)
        self.assertEqual(d.zweig_aus_kapsel("t-1", kid, "l-99", "cp")["reason"], "lauf_nicht_mehr_vorhanden")
        l.ablauf.laeufe["l-1"].agent = "t-anderer"
        self.assertEqual(d.zweig_aus_kapsel("t-1", kid, "l-1", "cp")["reason"], "lauf_nicht_mehr_vorhanden")
        self.assertEqual(d.zweig_messen("t-1", "l-1")["reason"], "kein_kapselzweig")


class GespraechTests(unittest.TestCase):
    def test_das_modellgespraech_wird_festgehalten_wiedergegeben_und_ins_pult_geladen_ohne_modell(self):
        l, _ = launcher(lambda r: knoten("real"))
        d = KapselDienst(l, Path(tempfile.mkdtemp()))
        d.pult.hinzufuegen("user", "Wie spät ist es?", "daniel")
        d.pult.hinzufuegen("assistant", "Kurz nach drei.", "hauhaucs")
        kid = d.moment("Test", "agent", "g", agenten=["t-1"])["kapsel"]
        d.pult.leeren()
        d.pult.hinzufuegen("user", "Etwas ganz anderes", "daniel")
        w = d.befehl("t-1", {"befehl": "wiedergabe", "kapsel": kid})
        self.assertEqual([(n["rolle"], n["text"]) for n in w["nachrichten"]], [("user", "Wie spät ist es?"), ("assistant", "Kurz nach drei.")])
        self.assertIn("kein Modell gerufen", w["hinweis"])
        geladen = d.befehl("t-1", {"befehl": "gespraech_laden", "kapsel": kid})
        self.assertEqual((geladen["ok"], geladen["nachrichten"]), (True, 2))
        self.assertEqual([n.text for n in d.pult.nachrichten], ["Wie spät ist es?", "Kurz nach drei."])
        self.assertTrue(d.pult.zurueck(), "das Laden ist rückgängig zu machen")
        self.assertEqual([n.text for n in d.pult.nachrichten], ["Etwas ganz anderes"])
        self.assertEqual(d.store.laden(kid)["unveraendert"], True, "die Kapsel selbst bleibt unberührt")

    def test_ohne_gespraech_steht_das_da_und_laden_wird_abgelehnt(self):
        l, _ = launcher(lambda r: knoten("real"))
        d = KapselDienst(l, Path(tempfile.mkdtemp()))
        kid = d.moment("Test", "agent", "g", agenten=["t-1"])["kapsel"]
        self.assertIsNone(d.befehl("t-1", {"befehl": "wiedergabe", "kapsel": kid})["gespraech"])
        self.assertEqual(d.befehl("t-1", {"befehl": "gespraech_laden", "kapsel": kid})["reason"], "kein_gespraech_in_kapsel")
        self.assertFalse(d.befehl("t-1", {"befehl": "wiedergabe", "kapsel": "k-gibtsnicht"})["ok"])

    def test_ersetzen_durch_ungueltiges_aendert_nichts(self):
        from augen_haende_bridge.kontextmischpult import Mischpult, PultFehler

        p = Mischpult()
        p.hinzufuegen("user", "bleibt")
        with self.assertRaises(PultFehler):
            p.ersetzen_durch({"schema": 2})
        self.assertEqual([n.text for n in p.nachrichten], ["bleibt"])


if __name__ == "__main__":
    unittest.main()
