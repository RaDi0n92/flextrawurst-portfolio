"""G15 im Starter: Vorschläge, Daniels Ja über die offenen Fragen, Auslieferung (Ablauf, Kontext, Datei, Loop), Rücknahme, Eigentumsregeln, Werkzeug."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from tests.test_ablauf_dienst import kurze_wartezeit, starter


def flow(i="meinfluss"):
    return {"id": i, "start": "z", "knoten": {"z": {"art": "zustand", "setze": {"fertig": True, "n": 1}}}, "kanten": []}


class Basis(unittest.TestCase):
    def setUp(self):
        kurze_wartezeit(self)
        self.l, self.fv = starter()
        self.s = self.l.seeds
        self.s.frist_s = 3.0
        self.ordner = Path(tempfile.mkdtemp())
        self.addCleanup(self.s.stoppen)

    def freigaben(self, **d):
        (self.s.store.ordner / "freigaben.json").write_text(json.dumps(d))

    def vorschlag(self, agent="t-1", **r):
        return self.s.befehl(agent, {"befehl": "vorschlagen", **r})

    def daniel_sagt(self, ja: bool, warten_s=3.0):
        """Daniel beantwortet die erste offene Frage — über denselben Weg wie seine Oberfläche."""
        ende = time.monotonic() + warten_s
        while time.monotonic() < ende:
            offen = self.l.ablauf.genehmigungen.offen()
            if offen:
                return self.l.ablauf.steuern({"aktion": "freigeben" if ja else "verweigern", "frage_id": offen[0]["id"]}), offen[0]
            time.sleep(0.01)
        self.fail("keine offene Frage")

    def ausliefern_im_faden(self, agent, **r):
        ergebnis = {}
        t = threading.Thread(target=lambda: ergebnis.update(r=self.s.befehl(agent, {"befehl": "ausliefern", **r})))
        t.start()
        return t, ergebnis


class VorschlagTests(Basis):
    def test_vorschlag_prueft_form_ablauf_empfaenger_und_loopbudget(self):
        r = self.vorschlag(zieltyp="kontext", titel="Hinweis", inhalt="Bitte zuerst messen.", empfaenger=["Claude"])
        self.assertEqual((r["ok"], r["status"], r["version"]), (True, "vorschlag", 1))
        self.assertIn("nur vorgeschlagen", r["hinweis"])
        self.assertEqual(self.vorschlag(zieltyp="kontext", titel="x", inhalt="x", empfaenger=["Niemand"])["reason"], "empfaenger_unbekannt")
        self.assertTrue(self.vorschlag(zieltyp="ablauf", titel="Fluss", inhalt={"id": "x"})["reason"].startswith("ablauf_ungueltig"))
        self.assertEqual(self.vorschlag(zieltyp="loop", titel="L", inhalt="gibtsnicht", budget={"max_laeufe": 2})["reason"], "ablauf_unbekannt")
        self.s.l.ablauf.speicher.speichere(flow(), "t")
        for budget, grund in ((None, "budget_ungueltig"), ({"max_laeufe": 0}, "budget_ungueltig"), ({"max_laeufe": 2, "intervall_s": -1}, "intervall_ungueltig"), ({"max_laeufe": 2, "abschluss": {"pfad": "a", "gleich": 1}}, "abschluss_nur_bei_goal")):
            self.assertEqual(self.vorschlag(zieltyp="loop", titel="L", inhalt="meinfluss", budget=budget)["reason"], grund, budget)
        self.assertEqual(self.vorschlag(zieltyp="goal", titel="G", inhalt="meinfluss", budget={"max_laeufe": 2})["reason"], "abschluss_fehlt")
        self.assertEqual(self.vorschlag(zieltyp="wild", titel="x", inhalt="x")["ok"], False)

    def test_auch_eine_neue_version_bleibt_ein_vorschlag(self):
        a = self.vorschlag(zieltyp="kontext", titel="H", inhalt="eins", empfaenger=["Claude"])
        b = self.vorschlag(zieltyp="kontext", titel="H2", inhalt="zwei", empfaenger=["Claude"], seed=a["seed"])
        self.assertEqual((b["seed"], b["version"], b["status"]), (a["seed"], 2, "vorschlag"))


class FreigabeTests(Basis):
    def test_ohne_freiheit_nur_vorschlag_wird_nichts_ausgeliefert(self):
        self.freigaben(freiheit="vorschlag")
        a = self.vorschlag(zieltyp="kontext", titel="H", inhalt="x", empfaenger=["Claude"])
        self.assertEqual(self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})["reason"], "freiheit_nur_vorschlag")
        self.assertEqual(self.l.ablauf.genehmigungen.offen(), [])

    def test_standard_braucht_daniels_ja_ein_nein_oder_schweigen_liefert_nichts(self):
        a = self.vorschlag(zieltyp="kontext", titel="H", inhalt="Hallo Claude", empfaenger=["Claude"])
        t, erg = self.ausliefern_im_faden("t-1", seed=a["seed"])
        ok, frage = self.daniel_sagt(False)
        t.join(5)
        self.assertEqual((erg["r"]["ok"], erg["r"]["reason"]), (False, "nicht_freigegeben"))
        self.assertIn(a["seed"], frage["beschreibung"])
        self.assertEqual(self.s.store.hole(a["seed"])["status"], "vorschlag")
        self.s.frist_s = 0.2
        self.assertEqual(self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})["reason"], "keine_antwort")
        self.assertEqual(self.s.store.hole(a["seed"])["status"], "vorschlag")

    def test_mit_daniels_ja_wird_zugestellt_und_der_verlauf_nennt_ihn(self):
        a = self.vorschlag(zieltyp="kontext", titel="H", inhalt="Hallo Claude", empfaenger=["Claude"])
        t, erg = self.ausliefern_im_faden("t-1", seed=a["seed"])
        self.daniel_sagt(True)
        t.join(5)
        self.assertEqual((erg["r"]["ok"], erg["r"]["zugestellt"]), (True, ["Claude"]))
        self.assertIn("zugestellt, nicht „verstanden“", erg["r"]["hinweis"])
        v = self.s.store.hole(a["seed"])
        self.assertEqual(v["status"], "aktiv")
        self.assertIn(("freigegeben", "Daniel"), [(e["was"], e["von"]) for e in v["ereignisse"]])
        ende = time.monotonic() + 3
        while time.monotonic() < ende and not self.s.l.sessions["t-2"].geschrieben:
            time.sleep(0.01)
        gesamt = b"".join(self.s.l.sessions["t-2"].geschrieben).decode()
        self.assertIn(f"[Bridge · Seed {a['seed']} v1 von Codex] Hallo Claude", gesamt)
        self.assertEqual(self.s.l.sessions["t-1"].geschrieben, [], "der Vorschlagende selbst bekommt nichts")

    def test_selbststaendig_darf_nicht_datei_seeds_aber_ablauf_und_kontext(self):
        self.freigaben(freiheit="selbststaendig")
        k = self.vorschlag(zieltyp="kontext", titel="H", inhalt="x", empfaenger=["Claude"])
        self.assertTrue(self.s.befehl("t-1", {"befehl": "ausliefern", "seed": k["seed"]})["ok"], "kein Daniel nötig")
        a = self.vorschlag(zieltyp="ablauf", titel="Fluss", inhalt=flow("neufluss"))
        r = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})
        self.assertEqual((r["ok"], r["ablauf"], r["ablauf_version"]), (True, "neufluss", 1))
        self.assertIn("nie gelöscht", r["hinweis"])
        self.assertEqual(self.l.ablauf.speicher.versionen("neufluss"), [1])
        datei = self.ordner / "SKILL.md"
        self.freigaben(freiheit="selbststaendig", ziele=[{"pfad": str(self.ordner), "arten": ["skill"]}])
        d = self.vorschlag(zieltyp="skill", titel="S", inhalt="Regel", ziel_pfad=str(datei))
        self.assertTrue(self.s.befehl("t-1", {"befehl": "pruefen", "seed": d["seed"]})["pruefung"]["braucht_daniel"], "Dateien brauchen auch hier Daniels Ja")
        self.s.frist_s = 0.2
        self.assertEqual(self.s.befehl("t-1", {"befehl": "ausliefern", "seed": d["seed"]})["reason"], "keine_antwort")
        self.assertFalse(datei.exists())


class DateiTests(Basis):
    def test_datei_nur_im_zielumfang_mit_ja_und_rueckgaengig(self):
        datei = self.ordner / "skills" / "SKILL.md"
        datei.parent.mkdir()
        datei.write_text("# Vorhanden\n")
        kid = self.l.kapseln.moment("Test", "agent", "Umweg", agenten=["t-1"])["kapsel"]
        a = self.vorschlag(zieltyp="skill", titel="S", inhalt="Neue Regel", ziel_pfad=str(datei), kapseln=[kid])
        r = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})
        self.assertEqual((r["ok"], r["reason"]), (False, "ziel_nicht_freigegeben"))
        self.assertEqual(datei.read_text(), "# Vorhanden\n")
        self.freigaben(ziele=[{"pfad": str(self.ordner / "skills"), "arten": ["skill"]}])
        t, erg = self.ausliefern_im_faden("t-1", seed=a["seed"])
        self.daniel_sagt(True)
        t.join(5)
        self.assertTrue(erg["r"]["ok"], erg["r"])
        self.assertIn("Neue Regel", datei.read_text())
        fremd = self.s.befehl("t-2", {"befehl": "zurueckziehen", "seed": a["seed"]})
        self.assertEqual(fremd["reason"], "nicht_dein_seed", "ein anderer Agent kann ihn nicht zurückziehen")
        self.assertIn("Neue Regel", datei.read_text())
        z = self.s.befehl("t-1", {"befehl": "zurueckziehen", "seed": a["seed"]})
        self.assertTrue(z["ok"], z)
        self.assertEqual(datei.read_text(), "# Vorhanden\n")
        self.assertTrue(self.s.zurueckziehen(None, {"seed": a["seed"]}, daniel=True)["ok"] is False, "schon zurückgezogen")


class LoopTests(Basis):
    def test_goal_laeuft_mit_budget_endet_mit_grund_und_zieht_den_seed_zurueck(self):
        self.freigaben(freiheit="selbststaendig")
        self.l.ablauf.speicher.speichere(flow(), "t")
        a = self.vorschlag(zieltyp="goal", titel="Fertig werden", inhalt="meinfluss", budget={"max_laeufe": 5, "intervall_s": 0.01, "abschluss": {"pfad": "zustand.fertig", "gleich": True}})
        r = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})
        self.assertTrue(r["ok"], r)
        lid = r["loop"]
        ende = time.monotonic() + 8
        while time.monotonic() < ende and self.s.loops.hole(lid).zustand != "beendet":
            time.sleep(0.02)
        st = self.s.befehl("t-1", {"befehl": "loop", "aktion": "status", "loop": lid})["loop"]
        self.assertEqual((st["zustand"], st["grund"], st["art"]), ("beendet", "abgeschlossen", "goal"), st)
        self.assertEqual(st["laeufe"], 1)
        time.sleep(0.3)
        self.assertEqual(self.s.store.hole(a["seed"])["status"], "zurueckgezogen", "mit dem Ende des Loops ist der Seed nicht mehr aktiv")
        self.assertIn("loop beendet: abgeschlossen", json.dumps(self.s.store.hole(a["seed"])["ereignisse"]))

    def test_stop_beendet_und_nur_der_eigner_darf_steuern(self):
        self.freigaben(freiheit="selbststaendig")
        self.l.ablauf.speicher.speichere(flow(), "t")
        a = self.vorschlag(zieltyp="loop", titel="Dauer", inhalt="meinfluss", budget={"max_laeufe": 1000, "intervall_s": 0.05})
        lid = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})["loop"]
        self.assertEqual(self.s.befehl("t-2", {"befehl": "loop", "aktion": "stopp", "loop": lid})["reason"], "nicht_dein_loop")
        self.assertEqual(self.s.befehl("t-2", {"befehl": "loop", "aktion": "liste"})["loops"], [])
        self.assertEqual([x["id"] for x in self.s.befehl("t-1", {"befehl": "loop", "aktion": "liste"})["loops"]], [lid])
        time.sleep(0.2)
        self.assertTrue(self.s.befehl("t-1", {"befehl": "loop", "aktion": "pause", "loop": lid})["ok"])
        self.assertTrue(self.s.befehl("t-1", {"befehl": "loop", "aktion": "weiter", "loop": lid})["ok"])
        st = self.s.befehl("t-1", {"befehl": "loop", "aktion": "stopp", "loop": lid})["loop"]
        self.assertEqual((st["zustand"], st["grund"]), ("beendet", "gestoppt"))
        n = st["laeufe"]
        time.sleep(0.4)
        self.assertEqual(self.s.loops.hole(lid).laeufe, n, "nach dem Stop läuft nichts heimlich weiter")
        self.assertEqual(self.s.befehl("t-1", {"befehl": "loop", "aktion": "tanzen", "loop": lid})["reason"], "aktion_unbekannt")

    def test_zurueckziehen_eines_aktiven_loop_seeds_stoppt_den_loop(self):
        self.freigaben(freiheit="selbststaendig")
        self.l.ablauf.speicher.speichere(flow(), "t")
        a = self.vorschlag(zieltyp="loop", titel="Dauer", inhalt="meinfluss", budget={"max_laeufe": 1000, "intervall_s": 0.05})
        lid = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})["loop"]
        self.assertTrue(self.s.befehl("t-1", {"befehl": "zurueckziehen", "seed": a["seed"]})["ok"])
        self.assertEqual(self.s.loops.hole(lid).zustand, "beendet")
        self.assertEqual(self.s.store.hole(a["seed"])["status"], "zurueckgezogen")


class DanielTests(Basis):
    def test_daniel_zieht_einen_datei_seed_ueber_die_oberflaeche_zurueck_und_sieht_ihn_im_stand(self):
        datei = self.ordner / "DOK.md"
        datei.write_text("Original\n")
        self.freigaben(ziele=[{"pfad": str(self.ordner), "arten": ["dokument"]}])
        a = self.vorschlag(zieltyp="dokument", titel="Doku", inhalt="Zusatz", ziel_pfad=str(datei))
        t, erg = self.ausliefern_im_faden("t-1", seed=a["seed"])
        self.daniel_sagt(True)
        t.join(5)
        self.assertIn("Zusatz", datei.read_text())
        stand = self.l.ablauf.stand()
        self.assertEqual([(x["art"], x["id"], x["zieltyp"]) for x in stand["seeds"]], [("seed", a["seed"], "dokument")])
        r = self.l.ablauf.steuern({"aktion": "seed_zurueckziehen", "seed_id": a["seed"]})
        self.assertTrue(r["ok"], r)
        self.assertEqual(datei.read_text(), "Original\n")
        self.assertNotIn("seeds", self.l.ablauf.stand(), "ohne aktive Seeds bleibt der Stand wie bisher")

    def test_daniel_stoppt_einen_loop_ueber_die_oberflaeche(self):
        self.freigaben(freiheit="selbststaendig")
        self.l.ablauf.speicher.speichere(flow(), "t")
        a = self.vorschlag(zieltyp="loop", titel="Dauer", inhalt="meinfluss", budget={"max_laeufe": 1000, "intervall_s": 0.05})
        lid = self.s.befehl("t-1", {"befehl": "ausliefern", "seed": a["seed"]})["loop"]
        self.assertIn(("loop", lid), [(x["art"], x["id"]) for x in self.l.ablauf.stand()["seeds"]])
        self.assertTrue(self.l.ablauf.steuern({"aktion": "loop_stoppen", "loop_id": lid})["ok"])
        self.assertEqual(self.s.loops.hole(lid).grund, "gestoppt")
        self.assertEqual(self.l.ablauf.steuern({"aktion": "loop_stoppen", "loop_id": "l-gibtsnicht"})["reason"], "loop_unbekannt")
        self.assertEqual(self.l.ablauf.steuern({"aktion": "seed_zurueckziehen", "seed_id": "s-00000000"})["reason"], "seed_unbekannt")

    def test_der_relay_kennt_die_neuen_aktionen_streng_und_den_stand_mit_seeds(self):
        from types import SimpleNamespace

        from augen_haende_bridge import transport as tr
        from client_vps import anzeigeorte as ao
        from tests.test_ablauf_dienst import Path as _P  # noqa: F401

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        relay = tr.Relay(ao.baue_principals(d), tr.Journal(tmp / "j.sqlite3"))
        desktop = SimpleNamespace(principal=next(p for p in relay.principals if p.can_control_terminals))
        starter = SimpleNamespace(principal=next(p for p in relay.principals if p.can_serve_terminals))
        self.assertEqual(relay.payload(desktop, "ablauf_steuern", {"aktion": "seed_zurueckziehen", "seed_id": "s-1a2b3c4d"})["seed_id"], "s-1a2b3c4d")
        self.assertEqual(relay.payload(desktop, "ablauf_steuern", {"aktion": "loop_stoppen", "loop_id": "l-1a2b3c4d"})["aktion"], "loop_stoppen")
        for kaputt in ({"aktion": "seed_zurueckziehen", "seed_id": "a b"}, {"aktion": "seed_zurueckziehen", "seed_id": 5}, {"aktion": "loop_stoppen", "loop_id": ""}, {"aktion": "seed_loeschen", "seed_id": "s-1"}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                relay.payload(desktop, "ablauf_steuern", kaputt)
        with self.assertRaises(tr.ProtocolError):
            relay.payload(starter, "ablauf_steuern", {"aktion": "seed_zurueckziehen", "seed_id": "s-1a2b3c4d"})
        stand = {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": []}
        self.assertEqual(relay.payload(starter, "ablauf_stand", dict(stand))["lernen"], False, "der alte Stand ohne Seeds geht weiter")
        self.assertEqual(len(relay.payload(starter, "ablauf_stand", {**stand, "seeds": [{"art": "seed", "id": "s-1", "titel": "T", "zieltyp": "skill"}]})["seeds"]), 1)
        for kaputt in ({**stand, "seeds": "x"}, {**stand, "seeds": [{}] * 21}, {**stand, "fremd": 1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)[:40]):
                relay.payload(starter, "ablauf_stand", kaputt)

    def test_die_oberflaeche_bietet_zurueckziehen_und_stoppen_an(self):
        from tests.test_koerper_anwendung import _gestartet

        app, gui, gebaut = _gestartet()
        app.anzeigeorte.unterstuetzt = True
        app.ablauf_stand = {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": [], "seeds": [{"art": "seed", "id": "s-1a2b3c4d", "titel": "Doku", "zieltyp": "dokument"},
                                                                                                      {"art": "loop", "id": "l-1a2b3c4d", "titel": "Dauer", "zieltyp": "loop"}]}
        texte = [e[1] for e in app._ablauf_menueeintraege() if e]
        self.assertIn("Seed zurückziehen: Doku (dokument)", texte)
        self.assertIn("Loop stoppen: Dauer (loop)", texte)
        self.assertIn({"aktion": "seed_zurueckziehen", "seed_id": "s-1a2b3c4d"}, app._ablauf_aktionen.values())
        self.assertIn({"aktion": "loop_stoppen", "loop_id": "l-1a2b3c4d"}, app._ablauf_aktionen.values())


class HerkunftTests(Basis):
    def test_eine_genannte_kapsel_muss_es_geben(self):
        kid = self.l.kapseln.moment("Test", "agent", "g", agenten=["t-1"])["kapsel"]
        self.assertTrue(self.vorschlag(zieltyp="kontext", titel="H", inhalt="x", empfaenger=["Claude"], kapseln=[kid])["ok"])
        r = self.vorschlag(zieltyp="kontext", titel="H", inhalt="x", empfaenger=["Claude"], kapseln=["k-gibtsnicht"])
        self.assertEqual((r["ok"], r["reason"]), (False, "kapsel_unbekannt"))


class SonstigesTests(Basis):
    def test_liste_zeige_exportieren_und_unbekanntes(self):
        a = self.vorschlag(zieltyp="kontext", titel="H", inhalt="x", empfaenger=["Claude"])
        self.assertEqual([x["id"] for x in self.s.befehl("t-1", {"befehl": "liste"})["seeds"]], [a["seed"]])
        self.assertEqual(self.s.befehl("t-1", {"befehl": "liste"})["freiheit"], "nach_freigabe")
        self.assertEqual(self.s.befehl("t-1", {"befehl": "zeige", "seed": a["seed"]})["seed"]["titel"], "H")
        self.assertIn("kein Modellgewicht", self.s.befehl("t-1", {"befehl": "exportieren", "seed": a["seed"]})["export"]["hinweis"])
        for b in ("zeige", "pruefen", "exportieren", "ausliefern", "zurueckziehen"):
            self.assertFalse(self.s.befehl("t-1", {"befehl": b, "seed": "s-00000000"})["ok"], b)
        self.assertEqual(self.s.befehl("t-1", {"befehl": "tanzen"})["reason"], "befehl_unbekannt")

    def test_das_werkzeug_kennt_die_befehle_und_sendet_streng(self):
        from unittest import mock

        from client_vps import bridge_cli

        def anfrage(*argv):
            with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
                code = bridge_cli.main(list(argv))
            return code, ask.call_args.args[0] if ask.call_args else None

        self.assertEqual(anfrage("seed", "vorschlagen", "kontext", "Titel", "--inhalt=Text", "--an=Claude,Gemgem"),
                         (0, {"cmd": "seed", "befehl": "vorschlagen", "zieltyp": "kontext", "titel": "Titel", "inhalt": "Text", "empfaenger": ["Claude", "Gemgem"]}))
        self.assertEqual(anfrage("seed", "vorschlagen", "goal", "G", "--inhalt=fluss", "--budget={\"max_laeufe\":3}")[1]["budget"], {"max_laeufe": 3})
        self.assertEqual(anfrage("seed", "ausliefern", "s-1", "2"), (0, {"cmd": "seed", "befehl": "ausliefern", "seed": "s-1", "version": 2}))
        self.assertEqual(anfrage("loop", "stopp", "l-1"), (0, {"cmd": "seed", "befehl": "loop", "aktion": "stopp", "loop": "l-1"}))
        self.assertEqual(anfrage("seed", "liste", "--status=aktiv")[1], {"cmd": "seed", "befehl": "liste", "status": "aktiv"})
        datei = self.ordner / "f.json"
        datei.write_text(json.dumps(flow()))
        self.assertEqual(anfrage("seed", "vorschlagen", "ablauf", "F", f"--datei={datei}")[1]["inhalt"]["id"], "meinfluss")
        for schlecht in (("seed",), ("seed", "vorschlagen", "kontext"), ("seed", "vorschlagen", "kontext", "T"), ("seed", "vorschlagen", "kontext", "T", "--inhalt=a", "--datei=b"), ("seed", "ausliefern"),
                         ("seed", "ausliefern", "s-1", "x"), ("seed", "tanzen", "s-1"), ("loop", "stopp"), ("loop", "tanzen", "l-1"), ("seed", "vorschlagen", "kontext", "T", "--quatsch=1", "--inhalt=a")):
            self.assertEqual(anfrage(*schlecht), (2, None), schlecht)
        code, _ = anfrage("seed", "vorschlagen", "goal", "G", "--inhalt=f", "--budget=kein json")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
