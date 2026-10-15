"""Ereignisspeicher, Graph und RAG gegen eine eingebettete, private PostgreSQL (pgserver) — nie gegen Daniels Server.

Läuft nur, wenn `pgserver`, `psycopg`, `langgraph` und `onnxruntime` da sind; sonst werden die Tests übersprungen.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

try:
    import langgraph  # noqa: F401
    import pixeltable_pgserver as pgserver
    import psycopg  # noqa: F401
    FEHLT = ""
except ImportError as f:
    FEHLT = str(f)

if not FEHLT:
    from augen_haende_bridge.speicher.ereignisspeicher import Ereignisspeicher
    from augen_haende_bridge.speicher.infragraph import KNOTEN, Infragraph

_server = _ordner = None
_zaehler = 0


def setUpModule():
    global _server, _ordner
    if FEHLT:
        return
    _ordner = tempfile.mkdtemp(prefix="bridge_pg_")
    _server = pgserver.get_server(_ordner, cleanup_mode="stop")


def tearDownModule():
    if _server is not None:
        _server.cleanup()
    if _ordner:
        shutil.rmtree(_ordner, ignore_errors=True)


def neue_datenbank() -> str:
    global _zaehler
    _zaehler += 1
    name = f"t{_zaehler}"
    _server.psql(f"CREATE DATABASE {name}")
    return f"postgresql://postgres:@/{name}?host={_ordner}"


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class SpeicherTests(unittest.TestCase):
    def setUp(self):
        self.s = Ereignisspeicher(neue_datenbank())
        self.s.schema_anlegen()
        self.addCleanup(self.s.schliessen)

    def test_nur_anhaengen(self):
        i = self.s.schreiben("graph", "x", text="eins")
        for sql in ("UPDATE ereignis SET text='zwei'", "DELETE FROM ereignis", "TRUNCATE ereignis, einbettung", "TRUNCATE einbettung"):
            with self.assertRaises(Exception) as f:
                self.s.abfrage(sql)
            self.assertIn("append-only", str(f.exception))
        with self.assertRaises(Exception):
            self.s.abfrage("TRUNCATE ereignis")  # scheitert schon am Fremdschlüssel der Einbettungen
        self.assertEqual(self.s.abfrage("SELECT text FROM ereignis WHERE id=%s", (i,))[0]["text"], "eins")

    def test_einlesen_ist_wiederholbar(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "p.jsonl").write_text("\n".join(json.dumps(e) for e in (
            {"id": "e-1", "zeit_ms": 1, "art": "state", "agent": "a", "ziel": "", "text": "läuft", "daten": {}},
            {"id": "e-2", "zeit_ms": 2, "art": "haende", "agent": "a", "ziel": "z", "text": "klick", "daten": {"ok": True}})) + "\nkaputt\n", encoding="utf-8")
        self.assertEqual(self.s.einlesen_protokoll(d / "p.jsonl"), (2, 0))
        self.assertEqual(self.s.einlesen_protokoll(d / "p.jsonl"), (0, 2))
        self.assertEqual(self.s.zaehlen("protokoll"), 2)
        (d / "l.jsonl").write_text(json.dumps({"zeit_ms": 3, "lauf_id": "p-1", "versuch_id": "v", "nr": 2, "status": "entdeckung", "von": "b", "text": "Befund"}) + "\n", encoding="utf-8")
        self.assertEqual(self.s.einlesen_ledger(d / "l.jsonl"), (1, 0))
        self.assertEqual(self.s.einlesen_ledger(d / "l.jsonl"), (0, 1))
        self.assertEqual(self.s.lauf("p-1")[0]["knoten"], "s2")

    def test_echte_daten_einlesbar(self):
        wurzel = Path(__file__).resolve().parents[1] / "runtime"
        protokoll = wurzel / "g13/protokoll/ereignisse.jsonl"
        if not protokoll.is_file():
            self.skipTest("kein Ereignisprotokoll im Repo")
        neu, _ = self.s.einlesen_protokoll(protokoll)
        self.assertGreater(neu, 100)
        self.assertEqual(self.s.zaehlen("protokoll"), neu)


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class FolgerTests(unittest.TestCase):
    def setUp(self):
        from augen_haende_bridge.speicher.folgen import Folger

        self.s = Ereignisspeicher(neue_datenbank())
        self.s.schema_anlegen()
        self.addCleanup(self.s.schliessen)
        self.w = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.w, ignore_errors=True)
        (self.w / "g13/protokoll").mkdir(parents=True)
        (self.w / "praxis").mkdir()
        self.datei = self.w / "g13/protokoll/ereignisse.jsonl"
        self.f = Folger(self.s, self.w)

    def zeile(self, i, art="nachricht"):
        return json.dumps({"id": f"e-{i}", "zeit_ms": 1000 + i, "art": art, "agent": "a", "ziel": "", "text": f"text {i}", "daten": {}}) + "\n"

    def test_neue_zeilen_kommen_einmal_an(self):
        self.datei.write_text(self.zeile(1) + self.zeile(2), encoding="utf-8")
        self.assertEqual(self.f.runde(), 2)
        self.assertEqual(self.f.runde(), 0)
        with open(self.datei, "a", encoding="utf-8") as f:
            f.write(self.zeile(3))
        self.assertEqual(self.f.runde(), 1)
        self.assertEqual(self.s.zaehlen("protokoll"), 3)

    def test_eine_halb_geschriebene_zeile_wartet_auf_ihr_ende(self):
        ganz = self.zeile(1)
        halb = self.zeile(2)
        self.datei.write_text(ganz + halb[:20], encoding="utf-8")
        self.assertEqual(self.f.runde(), 1)
        with open(self.datei, "a", encoding="utf-8") as f:
            f.write(halb[20:])
        self.assertEqual(self.f.runde(), 1)
        self.assertEqual(self.s.zaehlen("protokoll"), 2)

    def test_kaputte_zeile_haelt_nichts_an_und_rotation_liest_von_vorn(self):
        self.datei.write_text(self.zeile(1) + "kaputt\n" + self.zeile(2), encoding="utf-8")
        self.assertEqual(self.f.runde(), 2)
        self.datei.write_text(self.zeile(3), encoding="utf-8")  # kleiner als zuvor: Rotation
        self.assertEqual(self.f.runde(), 1)
        self.assertEqual(self.s.zaehlen("protokoll"), 3)

    def test_ledger_und_bekanntes_aus_dem_nachholen_werden_nicht_doppelt(self):
        z = {"zeit_ms": 5, "lauf_id": "p-1", "versuch_id": "v", "nr": 1, "status": "entdeckung", "von": "A", "text": "Befund"}
        (self.w / "praxis/p-1.jsonl").write_text(json.dumps(z) + "\n", encoding="utf-8")
        self.datei.write_text(self.zeile(1), encoding="utf-8")
        self.s.einlesen_protokoll(self.datei)  # schon bekannt
        self.assertEqual(self.f.runde(), 1, "nur die Ledger-Zeile ist neu")
        self.assertEqual(self.s.zaehlen("ledger"), 1)
        self.assertEqual(self.s.zaehlen("protokoll"), 1)


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class SpiegelTests(unittest.TestCase):
    def warte(self, bedingung, s=15.0):
        ende = time.time() + s
        while time.time() < ende and not bedingung():
            time.sleep(0.05)
        return bedingung()

    def test_neue_ereignisse_landen_in_der_datenbank(self):
        from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
        from augen_haende_bridge.speicher.spiegel import Spiegel

        dsn = neue_datenbank()
        s = Ereignisspeicher(dsn)
        s.schema_anlegen()
        self.addCleanup(s.schliessen)
        p = Ereignisprotokoll()
        sp = Spiegel(p, dsn)
        self.addCleanup(sp.beenden)
        p.erfassen("haende", "A", "haende", {"ok": False, "reason": "frame_unbekannt"})
        p.erfassen("nachricht", "B", "Hallo zusammen")
        self.assertTrue(self.warte(lambda: s.zaehlen("protokoll") == 2))
        self.assertEqual(s.abfrage("SELECT grund FROM ereignis WHERE art='haende'")[0]["grund"], "frame_unbekannt")

    def test_ledgerzeile_live_und_spaeter_aus_datei_ergibt_keine_doppelte(self):
        from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
        from augen_haende_bridge.speicher.spiegel import Spiegel

        dsn = neue_datenbank()
        s = Ereignisspeicher(dsn)
        s.schema_anlegen()
        self.addCleanup(s.schliessen)
        sp = Spiegel(Ereignisprotokoll(), dsn)
        self.addCleanup(sp.beenden)
        z = {"zeit_ms": 5, "lauf_id": "p-9", "versuch_id": "v", "nr": 3, "status": "entdeckung", "von": "A", "text": "Befund"}
        sp.ledger(z)
        self.assertTrue(self.warte(lambda: s.zaehlen("ledger") == 1))
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "p-9.jsonl").write_text(json.dumps(z, ensure_ascii=False) + "\n", encoding="utf-8")
        self.assertEqual(s.einlesen_ledger(d / "p-9.jsonl"), (0, 1))

    def test_datenbank_weg_haelt_das_protokoll_nicht_an_und_holt_nach(self):
        from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
        from augen_haende_bridge.speicher import spiegel as modul

        dsn = neue_datenbank()
        s = Ereignisspeicher(dsn)
        s.schema_anlegen()
        self.addCleanup(s.schliessen)
        da = {"ja": False}

        def fabrik():
            if not da["ja"]:
                raise ConnectionError("Datenbank nicht erreichbar")
            return Ereignisspeicher(dsn)
        p = Ereignisprotokoll()
        sp = modul.Spiegel(p, speicher_fabrik=fabrik)
        self.addCleanup(sp.beenden)
        t0 = time.time()
        p.erfassen("nachricht", "A", "während die Datenbank fehlt")
        self.assertLess(time.time() - t0, 0.5)  # Aufzeichnen wartet nie
        self.assertTrue(self.warte(lambda: "ConnectionError" in sp.fehler))
        da["ja"] = True
        self.assertTrue(self.warte(lambda: s.zaehlen("protokoll") == 1, 20))
        self.assertEqual(sp.fehler, "")

    def test_ueberlauf_wird_gezaehlt(self):
        from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
        from augen_haende_bridge.speicher import spiegel as modul

        modul_max = modul.MAX_WARTEND
        modul.MAX_WARTEND = 2
        self.addCleanup(setattr, modul, "MAX_WARTEND", modul_max)
        p = Ereignisprotokoll()
        sp = modul.Spiegel(p, speicher_fabrik=lambda: (_ for _ in ()).throw(ConnectionError("weg")))
        self.addCleanup(sp.beenden)
        for i in range(6):
            p.erfassen("nachricht", "A", f"n{i}")
        self.assertGreaterEqual(sp.verworfen, 3)


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class GraphTests(unittest.TestCase):
    def setUp(self):
        self.s = Ereignisspeicher(neue_datenbank())
        self.s.schema_anlegen()
        self.addCleanup(self.s.schliessen)
        self.ok = {k: True for k in KNOTEN}
        self.grund = {k: "" for k in KNOTEN}
        self.pruefer = {k: (lambda lauf, agent, k=k: (self.ok[k], self.grund[k])) for k in KNOTEN}
        self.g = Infragraph(self.s, self.pruefer)

    def arten(self, lauf="L"):
        return [e["art"] for e in self.s.lauf(lauf)]

    def test_alles_erfuellt_laeuft_bis_zum_ende(self):
        k = self.g.weiter("L", "A")
        self.assertEqual(k["zustand"], "fertig")
        betreten = [e["knoten"] for e in self.s.lauf("L") if e["art"] == "knoten_betreten"]
        self.assertEqual(betreten, list(KNOTEN))
        self.assertIn("lauf_fertig", self.arten())

    def test_fehlender_knoten_wartet_und_ist_sichtbar(self):
        self.ok["strom_frisch"], self.grund["strom_frisch"] = False, "kein_bild"
        k = self.g.weiter("L", "A")
        self.assertEqual((k["zustand"], k["knoten"], k["wartet_auf"], k["position"]), ("wartet", "strom_frisch", "kein_bild", "2 von 6"))
        self.assertIn("kein_bild", k["satz"])
        self.assertEqual(self.s.wartet_agent("A")["knoten"], "strom_frisch")
        self.ok["strom_frisch"] = True
        k = self.g.weiter("L", "A")
        self.assertEqual(k["zustand"], "fertig")
        self.assertIsNone(self.s.wartet_agent("A"))

    def test_dritter_fehlversuch_haelt_statt_zu_ueberspringen(self):
        self.ok["lease"], self.grund["lease"] = False, "lease_fehlt"
        self.assertEqual(self.g.weiter("L", "A")["versuche"], 1)
        self.assertEqual(self.g.weiter("L", "A")["versuche"], 2)
        k = self.g.weiter("L", "A")
        self.assertEqual((k["zustand"], k["knoten"]), ("halt", "lease"))
        self.assertIn("halt", self.arten())
        self.assertIn("diagnose", self.arten())
        self.assertNotIn("hand", [e["knoten"] for e in self.s.lauf("L") if e["art"] == "knoten_betreten"])
        # auch wenn der Zustand inzwischen stimmt: ohne Entsperren geht der Halt nicht weg
        self.ok["lease"] = True
        self.assertEqual(self.g.weiter("L", "A")["zustand"], "halt")
        self.assertEqual(self.s.position("L")["knoten"], "lease")

    def test_entsperren_braucht_benannte_ursache_und_bleibt_am_knoten(self):
        self.ok["hand"], self.grund["hand"] = False, "kein_ziel"
        for _ in range(3):
            self.g.weiter("L", "A")
        self.assertFalse(self.g.entsperren("L", "A", "kurz"))
        self.assertEqual(self.g.karte("L", "A")["zustand"], "halt")
        self.ok["hand"] = True
        self.assertTrue(self.g.entsperren("L", "A", "Ziel war nach Neustart nicht gebunden; Desktop gebunden"))
        k = self.g.weiter("L", "A")
        self.assertEqual(k["zustand"], "fertig")
        self.assertEqual(self.s.fehlversuche("L", "hand"), 0)

    def test_kaputter_pruefer_zaehlt_nie_als_erfolg(self):
        def kaputt(lauf, agent):
            raise RuntimeError("x")
        pruefer = dict(self.pruefer, ziel_gebunden=kaputt)
        k = Infragraph(self.s, pruefer).weiter("K", "A")
        self.assertEqual(k["zustand"], "wartet")
        self.assertEqual(k["wartet_auf"], "pruefer_fehler:RuntimeError")

    def test_zwei_agenten_sehen_wer_sonst_wartet(self):
        self.ok["beleg"], self.grund["beleg"] = False, "kein_beleg"
        self.g.weiter("L1", "A")
        k = self.g.weiter("L2", "B")
        self.assertEqual(k["andere_wartende"], ["A"])
        self.assertEqual([w["agent"] for w in self.s.wartezustand()], ["A", "B"])

    def test_prueferliste_muss_vollstaendig_sein(self):
        with self.assertRaises(ValueError):
            Infragraph(self.s, {"lease": lambda l, a: (True, "")})

    def test_jeder_lauf_hat_eigene_position(self):
        self.ok["urteil"], self.grund["urteil"] = False, "kein_eigenes_bild"
        self.g.weiter("L1", "A")
        self.ok["urteil"] = True
        self.g.weiter("L2", "B")
        self.assertEqual(self.s.position("L1")["knoten"], "urteil")
        self.assertEqual(self.s.position("L2")["knoten"], "ende")


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class EchtePrueferTests(unittest.TestCase):
    def setUp(self):
        from augen_haende_bridge.speicher.pruefer import ereignis_pruefer

        self.s = Ereignisspeicher(neue_datenbank())
        self.s.schema_anlegen()
        self.addCleanup(self.s.schliessen)
        self.t = {"ms": 1_000_000}
        self.g = Infragraph(self.s, ereignis_pruefer(self.s, jetzt_ms=lambda: self.t["ms"]))

    def ev(self, art, vor_s=0, **daten):
        self.s.schreiben("protokoll", art, agent="t-a", text=art, zeit_ms=self.t["ms"] - vor_s * 1000, grund=str(daten.get("reason", "")), daten=daten)

    def test_ohne_spuren_wartet_der_erste_knoten(self):
        k = self.g.weiter("L", "t-a")
        self.assertEqual((k["zustand"], k["knoten"], k["wartet_auf"]), ("wartet", "ziel_gebunden", "kein_bild_gebunden"))

    def test_nur_echte_spuren_bringen_den_lauf_weiter(self):
        self.ev("frame", 5, seq=1)
        k = self.g.weiter("L", "t-a")
        self.assertEqual((k["knoten"], k["wartet_auf"]), ("lease", "keine_lease"))
        self.ev("lease", 3, ok=False, reason="kein_fenster_ziel")
        self.assertEqual(self.g.weiter("L", "t-a")["wartet_auf"], "kein_fenster_ziel")
        self.ev("lease", 2, ok=True)
        self.assertEqual((self.g.weiter("L", "t-a")["knoten"], self.g.karte("L", "t-a")["wartet_auf"]), ("hand", "keine_aktion"))
        self.ev("haende", 1, ok=True)
        self.assertEqual(self.g.weiter("L", "t-a")["wartet_auf"], "kein_eigenes_bild_nach_der_aktion")
        self.ev("sehen", 0, seq=2)
        self.assertEqual(self.g.weiter("L", "t-a")["wartet_auf"], "kein_urteil")
        self.s.schreiben("ledger", "ok", agent="Gutachter", lauf="L", knoten="s1", text="stimmt", zeit_ms=self.t["ms"])
        self.assertEqual(self.g.weiter("L", "t-a")["zustand"], "fertig")

    def test_altes_bild_ist_nicht_frisch(self):
        self.ev("frame", 60)
        k = self.g.weiter("L", "t-a")
        self.assertEqual((k["knoten"], k["wartet_auf"]), ("strom_frisch", "bild_60_s_alt"))


@unittest.skipIf(FEHLT, f"Abhängigkeiten fehlen: {FEHLT}")
class RagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from augen_haende_bridge.speicher import rag
            cls.rag = rag
            cls.einbetter = rag.Einbetter()
        except (ImportError, FileNotFoundError) as f:
            raise unittest.SkipTest(f"Einbettung nicht verfügbar: {f}")

    def setUp(self):
        self.s = Ereignisspeicher(neue_datenbank())
        self.s.schema_anlegen()
        self.addCleanup(self.s.schliessen)

    def test_vektor_hat_384_dimensionen_und_laenge_eins(self):
        v = self.einbetter.einbetten(["Der Bilderstrom liefert kein Bild"])[0]
        self.assertEqual(len(v), 384)
        self.assertAlmostEqual(sum(x * x for x in v), 1.0, places=3)

    def test_bedeutungssuche_findet_ohne_gleiches_wort(self):
        self.s.schreiben("ledger", "entdeckung", agent="Gutachter", lauf="p-1", text="Der Gutachter hatte zwei Stunden kein frisches Fensterbild und konnte nicht urteilen")
        self.s.schreiben("ledger", "entdeckung", agent="Nutzerin", lauf="p-1", text="Die Kaffeemaschine in der Küche ist leer und niemand hat Milch gekauft")
        self.s.schreiben("protokoll", "haende", agent="Nutzerin", text="Klick abgelehnt weil Daniel gerade die Maus bedient")
        self.assertEqual(self.rag.einbetten_neue(self.s, self.einbetter), 3)
        self.assertEqual(self.rag.einbetten_neue(self.s, self.einbetter), 0)  # nachholbar, nichts doppelt
        treffer = self.rag.suche(self.s, self.einbetter, "Urteil ohne aktuelles Bild", 3)
        self.assertEqual(treffer[0]["agent"], "Gutachter")
        treffer = self.rag.suche(self.s, self.einbetter, "Mensch benutzt Mauszeiger, Aktion verweigert", 3)
        self.assertEqual(treffer[0]["art"], "haende")
        gefiltert = self.rag.suche(self.s, self.einbetter, "Urteil ohne aktuelles Bild", 3, quelle="protokoll")
        self.assertEqual({t["quelle"] for t in gefiltert}, {"protokoll"})

    def test_frames_werden_nicht_eingebettet_und_grund_zaehlt(self):
        for i in range(5):
            self.s.schreiben("protokoll", "frame", agent="a", text="Bild 1632×800 (capture)")
        self.s.schreiben("protokoll", "haende", agent="a", text="haende", grund="kein_fenster_ziel")
        self.s.schreiben("protokoll", "haende", agent="a", text="haende")  # zu kurz ohne Grund
        self.assertEqual(self.rag.einbetten_neue(self.s, self.einbetter), 1)
        self.assertEqual(self.rag.suche(self.s, self.einbetter, "kein Fenster als Ziel", 1)[0]["grund"], "kein_fenster_ziel")

    def test_hybrid_vereint_fachwort_und_umschreibung(self):
        self.s.schreiben("ledger", "entdeckung", agent="O", lauf="p-1", text="Beleg-Stau: Tastendruck strg+s wurde zugestellt, der Harness zählt aber keinen Beleg")
        self.s.schreiben("protokoll", "raute", agent="O", text="Körperquittung: Schritt 2 Mache: Zeiger auf die Schaltfläche, einmal klicken")
        self.s.schreiben("protokoll", "nachricht", agent="G", text="Kaffeepause, in zehn Minuten geht es weiter")
        self.rag.einbetten_neue(self.s, self.einbetter)
        self.assertEqual(self.rag.hybrid(self.s, self.einbetter, "Tastendruck ohne Beleg strg+s", 2)[0]["art"], "entdeckung")
        self.assertEqual(self.rag.hybrid(self.s, self.einbetter, "Tastendruck ohne Beleg", 3, quelle="protokoll")[0]["quelle"], "protokoll")

    def test_volltext_zwischenweg(self):
        self.s.schreiben("graph", "halt", text="Halt an lease: Ursache suchen")
        self.assertEqual(len(self.rag.volltext(self.s, "lease")), 1)
        self.assertEqual(self.rag.volltext(self.s, "gibtesnicht"), [])
        self.assertEqual(len(self.rag.volltext(self.s, "Halt vor lease!")), 1)  # ein Treffer-Wort genügt, Satzzeichen stören nicht


if __name__ == "__main__":
    unittest.main()
