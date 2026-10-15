"""G12: Abläufe — Sprache, Speicher mit Versionen, Ausführung mit Prüfungen und Fallbacks, Pause/Fortsetzen/Abbruch, Zweige, Delegation, Replay."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path

from augen_haende_bridge import ablauf as ab
from augen_haende_bridge.harness import RunStatus


def fluss(**kw):
    d = {"id": "demo", "name": "Demo", "start": "messen", "knoten": {
        "messen": {"art": "beobachten", "aktion": "weltdom", "args": {"befehl": "liste"}, "speichere": "liste"},
        "klicken": {"art": "handeln", "aktion": "weltdom", "args": {"befehl": "aktion", "args": {"knoten": {"$suche": {"pfad": "liste.knoten", "wo": {"name": "OK"}, "feld": "id"}}, "aktion": "klick"}},
                    "vorher": [{"pfad": "liste.knoten", "enthaelt": {"name": "OK"}}], "nachher": [{"pfad": "klicken.ruecklese.bestaetigt", "gleich": True}], "fallback": "plan_b",
                    "unsicherheit": "der Knopf könnte schon gedrückt sein"},
        "fertig": {"art": "zustand", "setze": {"phase": "fertig"}},
        "plan_b": {"art": "zustand", "setze": {"phase": "plan_b"}}},
        "kanten": [{"von": "messen", "nach": "klicken", "wenn": "ok"}, {"von": "klicken", "nach": "fertig", "wenn": "ok"}]}
    d.update(kw)
    return d


class Handler:
    def __init__(self):
        self.aufrufe = []
        self.liste = {"ok": True, "knoten": [{"id": "k1", "name": "OK", "rolle": "button"}, {"id": "k2", "name": "Abbrechen", "rolle": "button"}]}
        self.klick = {"ok": True, "status": "ausgefuehrt", "ruecklese": {"bestaetigt": True}}

    def weltdom(self, spec, ctx):
        self.aufrufe.append(spec)
        return dict(self.liste) if spec["args"]["befehl"] == "liste" else dict(self.klick)

    def alle(self):
        return {"weltdom": self.weltdom, "haende": lambda s, c: {"ok": True}, "lease": lambda s, c: {"ok": True}, "nachricht": lambda s, c: {"ok": True}, "auftrag": lambda s, c: {"ok": True}}


def lauf_von(d, h=None, modi=("free",), **kw):
    h = h or Handler()
    a = ab.Ablauf.aus_dict(d, version=1)
    ausf = ab.Ausfuehrer(h.alle(), schlafen=lambda s: None, **kw)
    lauf = ab.neuer_lauf(a, "t-1", frozenset(h.alle()), modi)
    return ausf, lauf, h


class SpracheTests(unittest.TestCase):
    def test_bedingungen(self):
        ctx = {"a": {"liste": [{"n": 1, "name": "x"}, {"n": 2, "name": "y"}], "wert": 5, "text": "Hallo Welt", "leer": []}}
        wahr = [{"pfad": "a.wert", "gleich": 5}, {"pfad": "a.wert", "ungleich": 4}, {"pfad": "a.liste", "enthaelt": {"name": "y"}}, {"pfad": "a.text", "enthaelt": "Welt"}, {"pfad": "a.wert", "mindestens": 5},
                {"pfad": "a.wert", "hoechstens": 5}, {"pfad": "a.liste.1.n", "gleich": 2}, {"pfad": "a.gibtsnicht", "vorhanden": False}, {"pfad": "a.wert", "vorhanden": True}, {"pfad": "a.liste", "nicht_leer": True},
                {"pfad": "a.leer", "nicht_leer": False}]
        falsch = [{"pfad": "a.wert", "gleich": 6}, {"pfad": "a.liste", "enthaelt": {"name": "z"}}, {"pfad": "a.gibtsnicht", "gleich": None}, {"pfad": "a.gibtsnicht", "mindestens": 0}, {"pfad": "a.text", "mindestens": 1},
                  {"pfad": "a.wert", "vorhanden": False}, {"pfad": "a.liste.9", "vorhanden": True}]
        for b in wahr:
            self.assertTrue(ab.bedingung(b, ctx), b)
        for b in falsch:
            self.assertFalse(ab.bedingung(b, ctx), b)
        for kaputt in (None, {}, {"pfad": 5}, {"pfad": "a", "gleich": 1, "ungleich": 2}, {"pfad": "a", "wuerfeln": 1}, {"pfad": "a", "gleich": 1, "extra": 1}):
            with self.assertRaises(ab.AblaufFehler, msg=str(kaputt)):
                ab.bedingung(kaputt, ctx)

    def test_referenzen_und_suchen_raten_nie(self):
        ctx = {"l": {"knoten": [{"id": "k1", "name": "OK"}, {"id": "k2", "name": "Abbrechen"}, {"id": "k3", "name": "OK"}]}, "x": {"y": [7]}}
        self.assertEqual(ab.aufloesen({"a": {"$ref": "x.y.0"}, "b": [1, {"$ref": "x.y"}]}, ctx), {"a": 7, "b": [1, [7]]})
        self.assertEqual(ab.aufloesen({"$suche": {"pfad": "l.knoten", "wo": {"name": "Abbrechen"}, "feld": "id"}}, ctx), "k2")
        for kaputt, grund in (({"$ref": "x.gibts.nicht"}, "ref_fehlt"), ({"$suche": {"pfad": "l.knoten", "wo": {"name": "OK"}, "feld": "id"}}, "suche_mehrdeutig"),
                              ({"$suche": {"pfad": "l.knoten", "wo": {"name": "Nix"}, "feld": "id"}}, "suche_leer"), ({"$suche": {"pfad": "l.knoten"}}, "suche_ungueltig")):
            with self.assertRaises(ab.AblaufFehler) as c:
                ab.aufloesen(kaputt, ctx)
            self.assertTrue(str(c.exception).startswith(grund), (kaputt, str(c.exception)))
        tief = {}
        for _ in range(12):
            tief = {"a": tief}
        with self.assertRaises(ab.AblaufFehler):
            ab.aufloesen(tief, ctx)

    def test_ein_gueltiger_ablauf_und_die_kurzschreibweise_fallback(self):
        a = ab.Ablauf.aus_dict(fluss(), version=3, urheber="codex", jetzt_ms=5)
        self.assertEqual((a.id, a.version, a.start, a.urheber), ("demo", 3, "messen", "codex"))
        self.assertIn({"von": "klicken", "nach": "plan_b", "wenn": "abweichung"}, a.kanten)
        self.assertEqual(ab.Ablauf.aus_dict(a.zu_dict()), a, "Hin und zurück über JSON")
        g = a.graph()
        self.assertEqual((g.id, g.start_node_id, len(g.nodes)), ("demo@3", "messen", 4))

    def test_ungueltige_ablaeufe_werden_mit_festem_code_abgelehnt(self):
        def mit(**ersatz):
            d = fluss()
            d.update(ersatz)
            return d

        faelle = {"unbekannte_felder": mit(extra=1), "id_ungueltig": mit(id="a b"), "start_unbekannt": mit(start="x"), "knoten_ungueltig": mit(knoten={}), "kante_ungueltig": mit(kanten=[{"von": "messen", "nach": "x"}]),
                  "max_schritte_ungueltig": mit(max_schritte=0), "schema_unbekannt": mit(schema=9), "version_ungueltig": mit(version=0), "name_ungueltig": mit(name="")}
        for code, d in faelle.items():
            with self.assertRaises(ab.AblaufFehler, msg=code) as c:
                ab.Ablauf.aus_dict(d)
            self.assertEqual(str(c.exception), code)
        for kaputt in ({"art": "magie"}, {"art": "handeln", "aktion": "shell", "args": {}}, {"art": "handeln", "aktion": "weltdom", "args": []}, {"art": "warten", "sekunden": 99999}, {"art": "zustand", "setze": []},
                       {"art": "pruefen", "pruefe": [{"pfad": "a", "wuerfeln": 1}]}, {"art": "delegieren", "an": "x"}, {"art": "beobachten", "aktion": "weltdom", "extra": 1}, {"art": "beobachten", "aktion": "weltdom", "speichere": "a b"},
                       {"art": "handeln", "aktion": "weltdom", "fallback": "gibt-es-nicht"}):
            d = fluss()
            d["knoten"]["x"] = kaputt
            with self.assertRaises(ab.AblaufFehler, msg=str(kaputt)):
                ab.Ablauf.aus_dict(d)
        with self.assertRaises(ab.AblaufFehler):
            ab.Ablauf.aus_dict("kein dict")
        zu_gross = fluss(knoten={f"n{i}": {"art": "zustand", "setze": {"a": 1}} for i in range(ab.MAX_KNOTEN + 1)}, start="n0", kanten=[])
        with self.assertRaises(ab.AblaufFehler):
            ab.Ablauf.aus_dict(zu_gross)

    def test_ein_tor_oeffnet_mit_pass_auch_wenn_ok_geschrieben_wurde(self):
        d = fluss()
        d["knoten"]["tor"] = {"art": "tor", "name": "Freigabe"}
        d["kanten"].append({"von": "tor", "nach": "fertig", "wenn": "ok"})
        self.assertIn({"von": "tor", "nach": "fertig", "wenn": "pass"}, ab.Ablauf.aus_dict(d).kanten)


class SpeicherTests(unittest.TestCase):
    def test_versionen_ueberschreiben_nie_und_ueberleben_den_neustart(self):
        ordner = Path(tempfile.mkdtemp())
        s = ab.AblaufSpeicher(ordner, uhr=lambda: 123)
        v1 = s.speichere(fluss(), "codex")
        v2 = s.speichere(fluss(name="Demo neu"), "claude")
        self.assertEqual((v1.version, v2.version, v1.name, v2.name), (1, 2, "Demo", "Demo neu"))
        self.assertEqual((s.ablauf("demo").version, s.ablauf("demo", 1).name, s.versionen("demo")), (2, "Demo", [1, 2]))
        neu = ab.AblaufSpeicher(ordner)
        self.assertEqual((neu.versionen("demo"), neu.ablauf("demo", 2).urheber), ([1, 2], "claude"))
        self.assertEqual(neu.liste(), [{"id": "demo", "name": "Demo neu", "version": 2, "versionen": [1, 2], "urheber": "claude"}])
        with self.assertRaises(ab.AblaufFehler):
            s.speichere({"id": "kaputt"}, "x")
        self.assertEqual(s.versionen("kaputt"), [])

    def test_kaputte_dateien_werden_uebersprungen(self):
        ordner = Path(tempfile.mkdtemp())
        s = ab.AblaufSpeicher(ordner)
        s.speichere(fluss(), "x")
        (ordner / "ablaeufe" / "boese@9.json").write_text("{kaputt")
        (ordner / "laeufe").mkdir(exist_ok=True)
        (ordner / "laeufe" / "x.json").write_text("5")
        neu = ab.AblaufSpeicher(ordner)
        self.assertEqual(neu.versionen("demo"), [1])
        self.assertTrue(neu.fehler)

    def test_ein_neuer_ablauf_aus_einer_datei_laeuft_ohne_neuen_code(self):
        """R078: derselbe Ausführer, derselbe Handler-Satz — nur eine neue JSON-Datei."""
        ordner = Path(tempfile.mkdtemp())
        datei = ordner / "neu.json"
        datei.write_text(json.dumps({"id": "ganz-neu", "start": "a", "knoten": {"a": {"art": "zustand", "setze": {"x": 1}}, "b": {"art": "pruefen", "pruefe": [{"pfad": "liste", "vorhanden": False}]}},
                                     "kanten": [{"von": "a", "nach": "b", "wenn": "ok"}]}))
        a = ab.AblaufSpeicher(ordner / "speicher").speichere(json.loads(datei.read_text()), "agent")
        ausf = ab.Ausfuehrer({}, schlafen=lambda t: None)
        lauf = ab.neuer_lauf(a, "t-1", frozenset())
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"x": 1}))


class LaufTests(unittest.TestCase):
    def test_ein_ablauf_laeuft_mit_kontext_vorher_nachher_und_unsicherheit(self):
        ausf, lauf, h = lauf_von(fluss())
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "fertig"}), lauf.grund)
        self.assertEqual([e.knoten for e in lauf.verlauf], ["messen", "klicken", "fertig"])
        self.assertEqual(h.aufrufe[1]["args"]["args"]["knoten"], "k1", "$suche hat den Knoten über den Namen gefunden")
        self.assertEqual(lauf.unsicherheit, [{"knoten": "klicken", "text": "der Knopf könnte schon gedrückt sein"}])
        self.assertTrue(all(e.signal == "ok" for e in lauf.verlauf))

    def test_geaenderter_zustand_loest_den_fallback_aus(self):
        for aenderung, grund in (({"liste": {"ok": True, "knoten": [{"id": "k2", "name": "Abbrechen"}]}}, "vorher_nicht_erfuellt"), ({"klick": {"ok": True, "ruecklese": {"bestaetigt": False}}}, "nachher_nicht_erfuellt"),
                                 ({"klick": {"ok": False, "reason": "lease_fehlt"}}, "handler_meldet_nicht_ok")):
            h = Handler()
            for k, v in aenderung.items():
                setattr(h, k, v)
            ausf, lauf, _ = lauf_von(fluss(), h)
            ausf.starten(lauf)
            ausf.laufen(lauf)
            self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "plan_b"}), grund)
            klick = next(e for e in lauf.verlauf if e.knoten == "klicken")
            self.assertEqual((klick.signal, klick.status), ("abweichung", grund))

    def test_ohne_fallback_haelt_der_lauf_ehrlich_an(self):
        d = fluss()
        del d["knoten"]["klicken"]["fallback"]
        h = Handler()
        h.klick = {"ok": False, "reason": "geometrie_geaendert"}
        ausf, lauf, _ = lauf_von(d, h)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual(lauf.status, "blocked")
        self.assertIn("abweichung ohne Fallback an klicken", lauf.grund)
        self.assertIn("geometrie_geaendert", lauf.grund)
        self.assertEqual(lauf.zustand, {})

    def test_eine_ausnahme_ist_ein_fehlersignal_nicht_ein_absturz(self):
        h = Handler()
        d = fluss()
        d["kanten"].append({"von": "klicken", "nach": "plan_b", "wenn": "fehler"})
        ausf, lauf, _ = lauf_von(d, h)
        ausf.handler["weltdom"] = lambda s, c: (_ for _ in ()).throw(RuntimeError("boom")) if s["args"]["befehl"] == "aktion" else {"ok": True, "knoten": [{"id": "k1", "name": "OK"}]}
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "plan_b"}))
        self.assertEqual([e.status for e in lauf.verlauf if e.knoten == "klicken"], ["ausnahme"])

    def test_fehlende_argumente_und_fehlender_handler_halten_an_statt_zu_raten(self):
        h = Handler()
        h.liste = {"ok": True, "knoten": []}
        d = fluss()
        del d["knoten"]["klicken"]["vorher"]
        ausf, lauf, _ = lauf_von(d, h)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual(lauf.status, "blocked")
        self.assertIn("suche_leer", lauf.grund)
        ausf2 = ab.Ausfuehrer({}, schlafen=lambda s: None)
        lauf2 = ab.neuer_lauf(ab.Ablauf.aus_dict(fluss()), "t-1", frozenset())
        ausf2.starten(lauf2)
        ausf2.laufen(lauf2)
        self.assertEqual(lauf2.status, "blocked")
        self.assertIn("handler_fehlt", lauf2.grund)

    def test_schleifen_enden_an_max_schritte(self):
        d = {"id": "schleife", "start": "a", "max_schritte": 7, "knoten": {"a": {"art": "zustand", "setze": {"x": 1}}}, "kanten": [{"von": "a", "nach": "a", "wenn": "ok"}]}
        ausf, lauf, _ = lauf_von(d)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.schritte, lauf.grund), ("blocked", 7, "max_schritte_erreicht:7"))

    def test_pause_fortsetzen_und_abbruch_halten_weitere_knoten_an(self):
        langsam, freigabe = threading.Event(), threading.Event()

        def weltdom(spec, ctx):
            if spec["args"]["befehl"] == "liste":
                langsam.set()
                freigabe.wait(5)
                return {"ok": True, "knoten": [{"id": "k1", "name": "OK"}]}
            return {"ok": True, "ruecklese": {"bestaetigt": True}}

        ausf, lauf, _ = lauf_von(fluss())
        ausf.handler["weltdom"] = weltdom
        ausf.starten(lauf)
        t = threading.Thread(target=ausf.laufen, args=(lauf,))
        t.start()
        self.assertTrue(langsam.wait(3))
        self.assertTrue(ausf.pausieren(lauf))
        freigabe.set()
        t.join(5)
        self.assertEqual((lauf.status, lauf.grund, [e.knoten for e in lauf.verlauf]), ("paused", "pausiert", ["messen"]))
        self.assertFalse(ausf.pausieren(lauf))
        self.assertTrue(ausf.fortsetzen(lauf))
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand), ("completed", {"phase": "fertig"}))
        self.assertFalse(ausf.fortsetzen(lauf))
        ausf2, lauf2, _ = lauf_von(fluss())
        ausf2.starten(lauf2)
        ausf2.abbrechen(lauf2, "daniel")
        ausf2.laufen(lauf2)
        self.assertEqual((lauf2.status, lauf2.verlauf, lauf2.grund), ("aborted", [], "abgebrochen: daniel"))

    def test_checkpoint_und_zweig_der_alte_lauf_bleibt_unveraendert(self):
        d = fluss()
        d["knoten"]["messen"]["unsicherheit"] = "Liste könnte unvollständig sein"
        ausf, lauf, _ = lauf_von(d)
        ausf.starten(lauf)
        ausf.schritt(lauf)
        ausf.checkpoint(lauf, "nach_messen")
        ausf.laufen(lauf)
        original = json.dumps(lauf.zu_dict(), sort_keys=True)
        h2 = Handler()
        h2.klick = {"ok": False, "reason": "anderer Weg"}
        ausf_z = ab.Ausfuehrer(h2.alle(), schlafen=lambda s: None)
        zweig = ausf_z.zweig(lauf, "nach_messen", "l-zweig")
        self.assertEqual((zweig.eltern, zweig.zweig_von, zweig.status, zweig.run.current_node_id), (lauf.id, "nach_messen", "ready", "klicken"))
        self.assertEqual([e.knoten for e in zweig.verlauf], ["messen"])
        self.assertEqual(zweig.unsicherheit, [{"knoten": "messen", "text": "Liste könnte unvollständig sein"}])
        ausf_z.starten(zweig)
        ausf_z.laufen(zweig)
        self.assertEqual((zweig.status, zweig.zustand), ("completed", {"phase": "plan_b"}))
        self.assertEqual(json.dumps(lauf.zu_dict(), sort_keys=True), original)
        self.assertEqual(lauf.zustand, {"phase": "fertig"})

    def test_delegation_uebergibt_zustand_und_unsicherheit_und_wartet_auf_das_ergebnis(self):
        d = {"id": "teilen", "start": "z", "knoten": {"z": {"art": "zustand", "setze": {"phase": "vorbereitet"}},
                                                       "d": {"art": "delegieren", "an": "Claude", "text": "Prüfe die Tests", "warte_s": 5, "nachher": [{"pfad": "d.auftrag.status", "gleich": "fertig"}]},
                                                       "ende": {"art": "zustand", "setze": {"ok": True}}},
             "kanten": [{"von": "z", "nach": "d", "wenn": "ok"}, {"von": "d", "nach": "ende", "wenn": "ok"}]}
        gesehen = []

        def auftrag(spec, ctx):
            gesehen.append(spec)
            return {"ok": True, "auftrag": {"status": "fertig", "ergebnis": "12 grün"}}

        ausf, lauf, _ = lauf_von(d)
        ausf.handler["auftrag"] = auftrag
        lauf.unsicherheit.append({"knoten": "start", "text": "unklar, ob die Tests laufen"})
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertEqual((lauf.status, lauf.zustand["ok"]), ("completed", True), lauf.grund)
        a = gesehen[0]["args"]
        self.assertEqual(a["an"], "Claude")
        for teil in ("Prüfe die Tests", "vorbereitet", "unklar, ob die Tests laufen", "Lauf " + lauf.id):
            self.assertIn(teil, a["text"])

    def test_replay_fuehrt_nichts_aus(self):
        s = ab.AblaufSpeicher(Path(tempfile.mkdtemp()))
        h = Handler()
        ausf, lauf, _ = lauf_von(fluss(), h, speicher=s)
        ausf.starten(lauf)
        ausf.laufen(lauf)
        n = len(h.aufrufe)
        spur = ab.wiedergeben(s, lauf.id)
        self.assertEqual([e["knoten"] for e in spur], ["messen", "klicken", "fertig"])
        self.assertTrue(all(e["replay"] for e in spur))
        self.assertEqual(len(h.aufrufe), n)
        self.assertEqual(ab.wiedergeben(s, "gibt-es-nicht"), [])

    def test_durchlaeufe_bleiben_erhalten_und_ein_unterbrochener_wird_so_benannt(self):
        ordner = Path(tempfile.mkdtemp())
        s = ab.AblaufSpeicher(ordner)
        a = s.speichere(fluss(), "codex")
        for i in range(2):
            ausf = ab.Ausfuehrer(Handler().alle(), speicher=s, schlafen=lambda t: None)
            lauf = ab.neuer_lauf(a, "t-1", frozenset(Handler().alle()), lauf_id=f"l-{i}")
            ausf.starten(lauf)
            ausf.laufen(lauf)
        laufend = ab.neuer_lauf(a, "t-1", frozenset(Handler().alle()), lauf_id="l-laufend")
        ab.Ausfuehrer(Handler().alle(), speicher=s).starten(laufend)
        neu = ab.AblaufSpeicher(ordner)
        self.assertEqual({d["id"]: d["status"] for d in neu.laeufe("demo")}, {"l-0": "completed", "l-1": "completed", "l-laufend": "unterbrochen"})
        s.speichere(fluss(name="geaendert"), "claude")
        self.assertEqual(ab.AblaufSpeicher(ordner).lauf("l-0")["ablauf_version"], 1)

    def test_die_harness_liefert_zustand_und_spur(self):
        ausf, lauf, _ = lauf_von(fluss())
        ausf.starten(lauf)
        ausf.laufen(lauf)
        self.assertIsInstance(lauf.run.status, RunStatus)
        self.assertIn("completed", [t.event for t in lauf.run.trace])


if __name__ == "__main__":
    unittest.main()
