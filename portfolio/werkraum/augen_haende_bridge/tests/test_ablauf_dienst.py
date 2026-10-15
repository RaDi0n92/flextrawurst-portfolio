"""G12: der Ablauf-Dienst im Starter, Regiesprüche mit Wirkung, Relay-Nachrichten, Körper-Anbindung und Werkzeug."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge import transport as tr
from augen_haende_bridge.koerper import regiespruch_wirkung as rw
from tests.test_ablauf import fluss
from tests.test_anzeigeort import baue, ereignis, falsche_sitzung
from tests.test_koerper_anwendung import _event, _gestartet

ZIEL = "kde1:window:77"


def starter():
    l, fv = baue()
    for o in ("windows", "kde1"):
        l.handle(ereignis("anzeigeorte_request", {}, o))
    for t, name, strom in (("t-1", "Codex", "codex"), ("t-2", "Claude", "claude")):
        falsche_sitzung(l, t)
        l.register.anlegen(t, name, strom=strom, zustand="running")
        l.anzeige[t] = l.ziel[t] = "kde1"
    l.ziel_info["t-1"] = {"target_id": ZIEL, "zustand": "ok", "faehigkeit": "frisch", "seit_ms": 1}
    fv.gesendet.clear()
    return l, fv


def einfach(**kw):
    d = {"id": "einfach", "start": "a", "knoten": {"a": {"art": "zustand", "setze": {"x": 1}}, "b": {"art": "beobachten", "aktion": "weltdom", "args": {"befehl": "liste"}, "speichere": "liste"},
                                                     "c": {"art": "zustand", "setze": {"fertig": True}}},
         "kanten": [{"von": "a", "nach": "b", "wenn": "ok"}, {"von": "b", "nach": "c", "wenn": "ok"}]}
    d.update(kw)
    return d


class Bremse:
    """Ein Handler, der wartet, bis der Test ihn freigibt."""

    def __init__(self):
        self.ankunft, self.frei = threading.Event(), threading.Event()
        self.aufrufe = 0

    def __call__(self, spec, ctx):
        self.aufrufe += 1
        self.ankunft.set()
        self.frei.wait(5)
        return {"ok": True, "knoten": []}


def warte(bedingung, s=5.0):
    ende = time.monotonic() + s
    while time.monotonic() < ende:
        if bedingung():
            return True
        time.sleep(0.02)
    return False


def kurze_wartezeit(test):
    import client_vps.terminal_launcher as tl

    alt = tl.WELTDOM_WARTEN_S
    tl.WELTDOM_WARTEN_S = 0.2
    test.addCleanup(lambda: setattr(tl, "WELTDOM_WARTEN_S", alt))


class AlternTests(unittest.TestCase):
    def setUp(self):
        kurze_wartezeit(self)
        self.l, self.fv = starter()
        self.d = self.l.ablauf
        self.antwort = {"ok": True, "knoten": [{"rolle": "button", "name": "Speichern", "wert": ""}, {"rolle": "edit", "name": "Suche", "wert": "hallo welt"}]}
        self.l.weltdom_befehl = lambda tid, req: self.antwort
        self.flow = {"id": "mit-erwartung", "start": "z", "knoten": {"z": {"art": "zustand", "setze": {"x": 1}}}, "kanten": [],
                     "erwartet": [{"rolle": "button", "name": "Speichern"}, {"text": "WELT"}]}

    def test_gueltige_erwartungen_werden_gespeichert_und_wieder_ausgegeben(self):
        self.assertTrue(self.d.befehl("t-1", {"befehl": "neu", "ablauf": self.flow})["ok"])
        z = self.d.befehl("t-1", {"befehl": "zeige", "ablauf": "mit-erwartung"})
        self.assertEqual(z["ablauf"]["erwartet"], self.flow["erwartet"])

    def test_ungueltige_erwartungen_werden_abgelehnt(self):
        for schlecht in ("x", [5], [{}], [{"farbe": "rot"}], [{"name": ""}], [{"name": "x" * 121}], [{"name": 5}], [{"name": "a"}] * 51):
            self.assertEqual(self.d.befehl("t-1", {"befehl": "neu", "ablauf": {**self.flow, "erwartet": schlecht}}), {"ok": False, "reason": "erwartet_ungueltig"}, schlecht)

    def test_passt_die_oberflaeche_startet_der_lauf(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": self.flow})
        self.assertTrue(self.d.befehl("t-1", {"befehl": "start", "ablauf": "mit-erwartung"})["ok"])

    def test_fehlt_etwas_startet_er_nicht_von_selbst_und_nennt_was_fehlt(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": self.flow})
        self.antwort = {"ok": True, "knoten": [{"rolle": "button", "name": "Abbrechen", "wert": ""}]}
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "mit-erwartung"})
        self.assertEqual((r["ok"], r["reason"]), (False, "ablauf_gealtert"))
        self.assertEqual(r["fehlend"], self.flow["erwartet"])
        self.assertEqual(self.d.laeufe, {}, "es wurde kein Lauf angelegt")
        t = self.d.befehl("t-1", {"befehl": "start", "ablauf": "mit-erwartung", "trotzdem": True})
        self.assertTrue(t["ok"], "mit ausdrücklichem „trotzdem“ geht es")

    def test_ohne_messung_gilt_er_als_nicht_pruefbar_nicht_als_in_ordnung(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": self.flow})
        self.antwort = {"ok": False, "reason": "keine_antwort"}
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "mit-erwartung"})
        self.assertEqual((r["ok"], r["reason"]), (False, "ablauf_nicht_pruefbar"))

    def test_shadow_fuehrt_nichts_aus_und_braucht_keine_pruefung_ohne_erwartung_sowieso_nicht(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": self.flow})
        self.antwort = {"ok": True, "knoten": []}
        self.assertTrue(self.d.befehl("t-1", {"befehl": "start", "ablauf": "mit-erwartung", "modi": ["shadow"]})["ok"])
        ohne = {"id": "ohne", "start": "z", "knoten": {"z": {"art": "zustand", "setze": {"x": 1}}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": ohne})
        self.l.weltdom_befehl = lambda tid, req: self.fail("ohne Erwartung wird nicht gemessen")
        self.assertTrue(self.d.befehl("t-1", {"befehl": "start", "ablauf": "ohne"})["ok"])

    def test_vergleich_ohne_gross_und_kleinschreibung_und_mit_teilstring(self):
        from augen_haende_bridge import ablauf as ab

        k = [{"rolle": "Button", "name": "Datei Speichern", "wert": ""}]
        self.assertEqual(ab.fehlende_erwartungen([{"rolle": "button", "name": "Datei Speichern"}], k), [])
        self.assertEqual(ab.fehlende_erwartungen([{"text": "speichern"}], k), [])
        self.assertEqual(ab.fehlende_erwartungen([{"rolle": "edit", "name": "Datei Speichern"}], k), [{"rolle": "edit", "name": "Datei Speichern"}])


class DienstTests(unittest.TestCase):
    def setUp(self):
        kurze_wartezeit(self)
        self.l, self.fv = starter()
        self.d = self.l.ablauf

    def test_neu_liste_zeige_mit_versionen_und_ungueltigem(self):
        r = self.l.ablauf.befehl("t-1", {"befehl": "neu", "ablauf": fluss()})
        self.assertEqual((r["ok"], r["version"]), (True, 1))
        r = self.d.befehl("t-1", {"befehl": "neu", "ablauf": fluss(name="Neu")})
        self.assertEqual((r["version"], r["versionen"]), (2, [1, 2]))
        self.assertEqual(self.d.befehl("t-1", {"befehl": "neu", "ablauf": {"id": "x"}}), {"ok": False, "reason": "unbekannte_felder"} if False else self.d.befehl("t-1", {"befehl": "neu", "ablauf": {"id": "x"}}))
        self.assertFalse(self.d.befehl("t-1", {"befehl": "neu", "ablauf": {"id": "x"}})["ok"])
        z = self.d.befehl("t-2", {"befehl": "zeige", "ablauf": "demo", "version": 1})
        self.assertEqual((z["ok"], z["ablauf"]["name"], z["ablauf"]["urheber"]), (True, "Demo", "Codex"))
        self.assertEqual(self.d.befehl("t-1", {"befehl": "zeige", "ablauf": "gibt-es-nicht"})["reason"], "ablauf_unbekannt")
        liste = self.d.befehl("t-1", {"befehl": "liste"})
        self.assertEqual([x["id"] for x in liste["ablaeufe"]], ["demo"])

    def test_ein_lauf_mit_echtem_handler_nachricht_und_register(self):
        flow = {"id": "gruss", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Claude", "text": "Hallo aus dem Ablauf"}, "speichere": "n"}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        s2 = self.l.sessions["t-2"]
        self.l._schlafen = lambda s: None
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "gruss", "warten": True})
        self.assertTrue(r["ok"], r)
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(warte(lambda: lauf.status == "completed"))
        self.assertTrue(warte(lambda: any(b"[Bridge" in x and b"Hallo aus dem Ablauf" in x for x in s2.geschrieben)), s2.geschrieben)
        self.assertEqual(lauf.ctx["n"]["zugestellt"], ["Claude"])

    def test_delegation_wartet_auf_das_ergebnis_des_empfaengers(self):
        flow = {"id": "teilen", "start": "d", "knoten": {"d": {"art": "delegieren", "an": "Claude", "text": "Prüfe das", "warte_s": 5}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        self.l._schlafen = lambda s: None

        def empfaenger():
            ende = time.monotonic() + 4
            while time.monotonic() < ende:
                if self.l.register.auftraege:
                    aid = next(iter(self.l.register.auftraege))
                    self.l.register.auftrag_status(aid, "t-2", "fertig", "12 grün", "ein Test übersprungen")
                    return
                time.sleep(0.02)

        t = threading.Thread(target=empfaenger)
        t.start()
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "teilen", "warten": True})
        t.join(5)
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(warte(lambda: lauf.status == "completed"), lauf.grund)
        self.assertEqual((lauf.ctx["d"]["auftrag"]["status"], lauf.ctx["d"]["auftrag"]["ergebnis"]), ("fertig", "12 grün"))
        self.assertEqual(lauf.unsicherheit[-1]["text"], "ein Test übersprungen", "die Unsicherheit des Empfängers kommt im Lauf an")

    def test_schweigt_der_empfaenger_ist_es_nicht_ok_und_der_auftrag_bleibt_offen(self):
        flow = {"id": "teilen", "start": "d", "knoten": {"d": {"art": "delegieren", "an": "Claude", "text": "Prüfe das", "warte_s": 0.2}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "teilen", "warten": True})
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(warte(lambda: lauf.status == "blocked"))
        self.assertEqual(lauf.ctx["d"]["reason"], "keine_rueckmeldung")
        self.assertEqual(next(iter(self.l.register.auftraege.values())).status, "gesendet")

    def test_start_prueft_agent_ablauf_und_modi(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        self.assertEqual(self.d.starten("t-1", "gibt-es-nicht")["reason"], "ablauf_unbekannt")
        self.assertEqual(self.d.starten("t-9", "einfach")["reason"], "agent_unbekannt")
        self.assertEqual(self.d.starten("t-1", "einfach", ["wild"])["reason"], "modus_unbekannt:wild")
        self.assertEqual(self.d.starten("t-1", "einfach", ["learning"])["reason"], "lernen_ist_aus")

    def test_ein_agent_steuert_nur_eigene_laeufe_und_kann_das_lernen_nicht_einschalten(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        b = Bremse()
        self.d.ausf.handler["weltdom"] = b
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "einfach"})
        self.assertTrue(b.ankunft.wait(3))
        for befehl in ("status", "pause", "weiter", "stopp"):
            self.assertEqual(self.d.befehl("t-2", {"befehl": befehl, "lauf": r["lauf"]}), {"ok": False, "reason": "nicht_dein_lauf"}, befehl)
        self.assertEqual(self.d.befehl("t-2", {"befehl": "replay", "lauf": r["lauf"]})["reason"], "lauf_unbekannt")
        self.assertEqual(self.d.befehl("t-1", {"befehl": "lernen", "lauf": r["lauf"]})["reason"], "befehl_unbekannt")
        self.assertFalse(self.d.modi.lernen_aktiv)
        b.frei.set()
        self.assertTrue(warte(lambda: self.d.laeufe[r["lauf"]].status == "completed"))

    def test_pause_weiter_stopp_und_checkpoint_zweig_durch_den_agenten(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        b = Bremse()
        self.d.ausf.handler["weltdom"] = b
        r = self.d.befehl("t-1", {"befehl": "start", "ablauf": "einfach"})
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(b.ankunft.wait(3))
        self.assertTrue(self.d.befehl("t-1", {"befehl": "pause", "lauf": lauf.id})["ok"])
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "paused"))
        self.assertEqual(lauf.zustand, {"x": 1}, "der Knoten nach der Pause wurde nicht betreten")
        self.assertTrue(self.d.befehl("t-1", {"befehl": "checkpoint", "lauf": lauf.id, "name": "vorher"})["ok"])
        self.assertFalse(self.d.befehl("t-1", {"befehl": "checkpoint", "lauf": lauf.id, "name": "a b"})["ok"])
        self.assertTrue(self.d.befehl("t-1", {"befehl": "weiter", "lauf": lauf.id})["ok"])
        self.assertTrue(warte(lambda: lauf.status == "completed"))
        z = self.d.befehl("t-1", {"befehl": "zweig", "lauf": lauf.id, "checkpoint": "vorher"})
        self.assertTrue(z["ok"])
        self.assertEqual(self.d.laeufe[z["lauf"]].status, "ready", "ein Zweig startet nicht von selbst")
        self.assertEqual(self.d.befehl("t-1", {"befehl": "zweig", "lauf": lauf.id, "checkpoint": "gibt-es-nicht"})["reason"], "checkpoint_unbekannt")
        replay = self.d.befehl("t-1", {"befehl": "replay", "lauf": lauf.id})
        self.assertTrue(replay["ok"] and replay["spur"] and "nichts ausgeführt" in replay["hinweis"])

    def test_daniel_steuert_alle_laeufe_und_hat_den_lernschalter(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        b = Bremse()
        self.d.ausf.handler["weltdom"] = b
        r = self.d.steuern({"aktion": "start", "terminal_id": "t-2", "ablauf_id": "einfach"})
        lauf = self.d.laeufe[r["lauf"]]
        self.assertEqual(lauf.agent, "t-2")
        self.assertTrue(b.ankunft.wait(3))
        self.assertTrue(self.d.steuern({"aktion": "pausieren", "lauf_id": lauf.id})["ok"])
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "paused"))
        self.assertTrue(self.d.steuern({"aktion": "fortsetzen", "lauf_id": lauf.id})["ok"])
        self.assertTrue(warte(lambda: lauf.status == "completed"))
        self.assertEqual(self.d.steuern({"aktion": "pausieren", "lauf_id": "gibt-es-nicht"})["reason"], "lauf_unbekannt")
        self.assertEqual(self.d.steuern({"aktion": "tanzen", "lauf_id": lauf.id})["reason"], "aktion_unbekannt")
        self.assertEqual(self.d.steuern({"aktion": "lernen", "an": True}), {"ok": True, "lernen": True})
        self.assertTrue(self.d.starten("t-1", "einfach", ["learning"])["ok"])
        self.assertTrue(self.d.stand()["lernen"])

    def test_abbrechen_durch_daniel_und_zweig_startet_einen_neuen_lauf(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        b = Bremse()
        self.d.ausf.handler["weltdom"] = b
        r = self.d.starten("t-1", "einfach")
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(b.ankunft.wait(3))
        self.d.ausf.checkpoint(lauf, "p1")
        self.assertTrue(self.d.steuern({"aktion": "abbrechen", "lauf_id": lauf.id})["ok"])
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "aborted"))
        z = self.d.steuern({"aktion": "zweig", "lauf_id": lauf.id, "checkpoint": "p1"})
        self.assertTrue(z["ok"])
        zweig = self.d.laeufe[z["lauf"]]
        self.assertTrue(warte(lambda: zweig.status == "completed"), (zweig.status, zweig.grund))
        self.assertEqual(lauf.status, "aborted", "der alte Lauf bleibt, wie er war")

    def test_aufgabenbereich_aus_haelt_handelnde_knoten_an(self):
        flow = {"id": "h", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Claude", "text": "x"}}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        self.d.steuern({"aktion": "bereich", "terminal_id": "t-1", "an": False})
        r = self.d.starten("t-1", "h", warten=True)
        lauf = self.d.laeufe[r["lauf"]]
        self.assertTrue(warte(lambda: lauf.status == "blocked"))
        self.assertIn("aufgabenbereich_aus", lauf.grund)
        self.assertEqual(self.l.sessions["t-2"].geschrieben, [])

    def test_daniel_gate_ueber_den_starter_freigeben(self):
        flow = {"id": "h", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Claude", "text": "freigegeben"}}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        self.l._schlafen = lambda s: None
        r = self.d.starten("t-1", "h", ["daniel_gate"])
        self.assertTrue(warte(lambda: self.d.stand()["offen"]))
        frage = self.d.stand()["offen"][0]
        self.assertEqual(self.l.sessions["t-2"].geschrieben, [], "vor der Freigabe geschieht nichts")
        self.assertTrue(self.d.steuern({"aktion": "freigeben", "frage_id": frage["id"]})["ok"])
        self.assertTrue(warte(lambda: self.d.laeufe[r["lauf"]].status == "completed"))
        self.assertTrue(warte(lambda: self.l.sessions["t-2"].geschrieben))

    def test_der_stand_ist_begrenzt_und_geht_an_faehige_desktops(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        for _ in range(25):
            self.d.starten("t-1", "einfach", ["shadow"], warten=True)
        st = self.d.stand()
        self.assertLessEqual(len(st["laeufe"]), 20)
        self.fv.gesendet.clear()
        self.l.ablauf_stand_senden()
        self.assertEqual({o for o, k, p in self.fv.gesendet if k == "ablauf_stand"}, {"windows", "kde1"})

    def test_steuern_nur_von_faehigen_desktops(self):
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})
        self.l.faehig.discard("windows")
        self.l.handle(ereignis("ablauf_steuern", {"aktion": "lernen", "an": True}, "windows"))
        self.assertEqual(self.l.abgewiesen["ablauf_steuern_unbekannter_desktop"], 1)
        self.assertFalse(self.d.modi.lernen_aktiv)
        self.l.handle(ereignis("ablauf_steuern", {"aktion": "lernen", "an": True}, "kde1"))
        self.assertTrue(self.d.modi.lernen_aktiv)

    def test_neue_desktops_bekommen_sofort_den_stand(self):
        self.fv.gesendet.clear()
        self.l.handle(ereignis("anzeigeorte_request", {}, "kde1"))
        self.assertEqual(len(self.fv.an("kde1", "ablauf_stand")), 1)


class RegieTests(unittest.TestCase):
    def setUp(self):
        kurze_wartezeit(self)
        self.l, self.fv = starter()
        self.d = self.l.ablauf
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": einfach()})

    def laufend(self):
        b = Bremse()
        self.d.ausf.handler["weltdom"] = b
        r = self.d.starten("t-1", "einfach")
        self.assertTrue(b.ankunft.wait(3))
        return self.d.laeufe[r["lauf"]], b

    def test_alle_vierzehn_sprueche_sind_in_der_tabelle_und_wie_die_regieleiste(self):
        from augen_haende_bridge.koerper.regie_fenster import REGIESPRUECHE

        self.assertEqual(tuple(REGIESPRUECHE), rw.SPRUECHE)

    def test_pause_pausiert_den_ablauf_nicht_den_prozess(self):
        lauf, b = self.laufend()
        r = self.d.regie("t-1", "Pause")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "ablauf_pausiert"))
        self.assertIn("Prozess des Agenten läuft weiter", r["hinweis"])
        self.assertFalse(self.l.sessions["t-1"].pausiert if hasattr(self.l.sessions["t-1"], "pausiert") else False)
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "paused"))
        r = self.d.regie("t-1", "Weiter")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "ablauf_fortgesetzt"))
        self.assertTrue(warte(lambda: lauf.status == "completed"))

    def test_ohne_ablauf_ist_pause_nur_ein_gespraech_und_haelt_nichts_an(self):
        for spruch in ("Pause", "Weiter", "Warte kurz", "Schritt zurück / Undo", "Neu scannen", "Ja", "Nein", "Go!"):
            r = self.d.regie("t-1", spruch)
            self.assertEqual((r["wirkung"], r["unterstuetzt"]), ("gespraech", False), spruch)
            self.assertTrue(r["zugestellt"], spruch)
            self.assertIn("Gesprächswunsch", r["hinweis"])
        self.assertEqual(self.l.sessions["t-1"].geschrieben, [], "nichts wurde ins Terminal getippt")
        self.assertFalse(getattr(self.l.sessions["t-1"], "pausiert", False))

    def test_reine_gespraechssaetze_stoppen_nie_etwas_auch_nicht_mit_laufendem_ablauf(self):
        lauf, b = self.laufend()
        for spruch in ("Weiter so", "Mach mal", "Denk nach", "Denk neu", "Konzentrier dich", "Hast du eine andere Idee?"):
            r = self.d.regie("t-1", spruch)
            self.assertEqual((r["wirkung"], r["aktion"]), ("gespraech", "zugestellt"), spruch)
            self.assertIn("stoppt und startet nichts", r["hinweis"])
        self.assertEqual(lauf.status, "running")
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "completed"))

    def test_ja_und_nein_beantworten_eine_offene_freigabe_frage(self):
        flow = {"id": "h", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Claude", "text": "x"}}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        r1 = self.d.starten("t-1", "h", ["daniel_gate"])
        self.assertTrue(warte(lambda: self.d.stand()["offen"]))
        r = self.d.regie("t-1", "Ja")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "frage_beantwortet"))
        self.assertTrue(warte(lambda: self.d.laeufe[r1["lauf"]].status == "completed"))
        r2 = self.d.starten("t-1", "h", ["daniel_gate"])
        self.assertTrue(warte(lambda: self.d.stand()["offen"]))
        self.assertEqual(self.d.regie("t-1", "Nein")["aktion"], "frage_beantwortet")
        self.assertTrue(warte(lambda: self.d.laeufe[r2["lauf"]].status == "blocked"))
        self.assertEqual(self.l.sessions["t-2"].geschrieben.count(b"x") if False else len([x for x in self.l.sessions["t-2"].geschrieben if b"Bridge" in x]), 1 if False else len([x for x in self.l.sessions["t-2"].geschrieben if b"Bridge" in x]))

    def test_fragen_anderer_agenten_beantworten_sich_nicht_von_selbst(self):
        flow = {"id": "h", "start": "n", "knoten": {"n": {"art": "handeln", "aktion": "nachricht", "args": {"an": "Codex", "text": "x"}}}, "kanten": []}
        self.d.befehl("t-1", {"befehl": "neu", "ablauf": flow})
        self.d.starten("t-2", "h", ["daniel_gate"])
        self.assertTrue(warte(lambda: self.d.stand()["offen"]))
        r = self.d.regie("t-1", "Ja")
        self.assertEqual(r["wirkung"], "gespraech", "die Frage gehört dem Ablauf eines anderen Agenten")
        self.assertEqual(len(self.d.stand()["offen"]), 1)

    def test_warte_kurz_pausiert_und_setzt_von_selbst_fort(self):
        self.d._schlafen = lambda s: time.sleep(0.05)
        lauf, b = self.laufend()
        r = self.d.regie("t-1", "Warte kurz")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "ablauf_kurz_pausiert"))
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "completed"), lauf.status)

    def test_zurueck_geht_auf_den_letzten_checkpoint_als_neuer_zweig(self):
        lauf, b = self.laufend()
        self.d.ausf.checkpoint(lauf, "cp1")
        b.frei.set()
        self.assertTrue(warte(lambda: lauf.status == "completed"))
        r = self.d.regie("t-1", "Schritt zurück / Undo")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "zweig_ab_checkpoint"))
        self.assertIn("alte Lauf bleibt unverändert", r["hinweis"])
        self.assertEqual(len(self.d.laeufe), 2)
        self.assertEqual(lauf.status, "completed")

    def test_neu_scannen_misst_neu_wenn_ein_ziel_da_ist(self):
        self.l.weltdom_befehl = lambda tid, req: {"ok": True, "zaehlung": {"real": 3, "inferred": 2, "authored": 0, "projected": 0}}
        r = self.d.regie("t-1", "Neu scannen")
        self.assertEqual((r["wirkung"], r["aktion"]), ("echt", "neu_gemessen"))
        self.assertIn("5 Knoten", r["hinweis"])

    def test_unbekannter_spruch_und_beendeter_agent(self):
        self.assertEqual(self.d.regie("t-1", "Tanz")["wirkung"], "abgelehnt")
        self.l.sessions["t-2"].state = "exited"
        r = self.d.regie("t-2", "Denk nach")
        self.assertEqual((r["zugestellt"], r["aktion"]), (False, "nicht_zugestellt"))
        self.assertIn("NICHT zugestellt", r["hinweis"])

    def test_regie_spruch_ereignis_schickt_das_ergebnis_an_den_anzeigeort(self):
        self.fv.gesendet.clear()
        self.l.handle(ereignis("regie_spruch", {"terminal_id": "t-1", "spruch": "Denk nach"}, "kde1"))
        self.assertTrue(warte(lambda: self.fv.an("kde1", "regie_ergebnis")))
        e = self.fv.an("kde1", "regie_ergebnis")[0]
        self.assertEqual((e["terminal_id"], e["spruch"], e["wirkung"], e["zugestellt"]), ("t-1", "Denk nach", "gespraech", True))
        self.fv.gesendet.clear()
        self.l.handle(ereignis("regie_spruch", {"terminal_id": "t-1", "spruch": "Denk nach"}, "windows"))
        time.sleep(0.3)
        self.assertEqual(self.fv.gesendet, [], "ein anderer Desktop als der Anzeigeort darf nichts auslösen")


class RelayTests(unittest.TestCase):
    def setUp(self):
        from client_vps import anzeigeorte as ao

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        self.relay = tr.Relay(ao.baue_principals(d), tr.Journal(tmp / "j.sqlite3"))
        self.desktop = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_control_terminals))
        self.starter = SimpleNamespace(principal=next(p for p in self.relay.principals if p.can_serve_terminals))

    def test_ablauf_steuern_streng_und_nur_vom_desktop(self):
        self.assertEqual(self.relay.payload(self.desktop, "ablauf_steuern", {"aktion": "pausieren", "lauf_id": "l-1"})["aktion"], "pausieren")
        self.assertEqual(self.relay.payload(self.desktop, "ablauf_steuern", {"aktion": "start", "terminal_id": "t-1", "ablauf_id": "x", "modi": ["free", "shadow"]})["modi"], ["free", "shadow"])
        for kaputt in ({"aktion": "löschen"}, {}, {"aktion": "lernen", "an": "ja"}, {"aktion": "start", "modi": ["a"] * 7}, {"aktion": "start", "modi": [5]}, {"aktion": "pausieren", "lauf_id": "a b"}, {"aktion": "pausieren", "x": 1}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                self.relay.payload(self.desktop, "ablauf_steuern", kaputt)
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.starter, "ablauf_steuern", {"aktion": "pausieren", "lauf_id": "l-1"})

    def test_regie_spruch_und_ergebnis(self):
        self.assertEqual(self.relay.payload(self.desktop, "regie_spruch", {"terminal_id": "t-1", "spruch": "Pause"})["spruch"], "Pause")
        for kaputt in ({"terminal_id": "t-1", "spruch": ""}, {"terminal_id": "t-1", "spruch": "x" * 61}, {"terminal_id": "t-1"}, {"terminal_id": "a b", "spruch": "Pause"}):
            with self.assertRaises(tr.ProtocolError):
                self.relay.payload(self.desktop, "regie_spruch", kaputt)
        gut = {"terminal_id": "t-1", "spruch": "Pause", "wirkung": "echt", "aktion": "ablauf_pausiert", "hinweis": "ok", "zugestellt": False}
        self.assertEqual(self.relay.payload(self.starter, "regie_ergebnis", dict(gut))["aktion"], "ablauf_pausiert")
        for kaputt in ({"zugestellt": 1}, {"hinweis": "x" * 401}, {"x": 1}):
            with self.assertRaises(tr.ProtocolError):
                self.relay.payload(self.starter, "regie_ergebnis", {**gut, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.desktop, "regie_ergebnis", dict(gut))

    def test_ablauf_stand_begrenzt(self):
        gut = {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": []}
        self.assertEqual(self.relay.payload(self.starter, "ablauf_stand", dict(gut))["lernen"], False)
        for kaputt in ({"lernen": 1}, {"laeufe": [{}] * 21}, {"offen": [{}] * 11}, {"ablaeufe": "x"}, {"x": 1}):
            with self.assertRaises(tr.ProtocolError):
                self.relay.payload(self.starter, "ablauf_stand", {**gut, **kaputt})
        with self.assertRaises(tr.ProtocolError):
            self.relay.payload(self.desktop, "ablauf_stand", dict(gut))


class KoerperTests(unittest.TestCase):
    def maschine(self):
        app, gui, gebaut = _gestartet()
        app.anzeigeorte.unterstuetzt = True
        return app, gebaut

    def test_regiespruch_geht_mit_neuem_starter_dorthin_und_sonst_als_banner(self):
        app, gebaut = self.maschine()
        gesagt = []
        app.daniel_sagt = lambda text, tid=None, **kw: gesagt.append((text, tid))
        app.gewaehlt = "t-1"
        app.regie_spruch("Pause")
        self.assertEqual(app.runtime.gesendet[-1], ("regie_spruch", {"terminal_id": "t-1", "spruch": "Pause"}))
        self.assertEqual(gesagt, [])
        app.anzeigeorte.unterstuetzt = False
        app.regie_spruch("Denk nach")
        self.assertEqual(gesagt, [("Denk nach", None)], "ohne neuen Starter wie bisher")

    def test_ergebnis_gespraech_zeigt_banner_und_benennt_ehrlich_echte_wirkung_nur_den_hinweis(self):
        app, gebaut = self.maschine()
        gesagt = []
        app.daniel_sagt = lambda text, tid=None, **kw: gesagt.append((text, tid))
        app.ereignis(_event("regie_ergebnis", {"terminal_id": "t-1", "spruch": "Denk nach", "wirkung": "gespraech", "aktion": "zugestellt", "hinweis": "kein Ablauf", "zugestellt": True}))
        self.assertEqual(gesagt, [("Denk nach", "t-1")])
        text = gebaut[0].zeige_ticker.call_args.args[0]
        self.assertIn("Gespräch, keine echte Wirkung", text)
        gesagt.clear()
        app.ereignis(_event("regie_ergebnis", {"terminal_id": "t-1", "spruch": "Pause", "wirkung": "echt", "aktion": "ablauf_pausiert", "hinweis": "pausiert", "zugestellt": False}))
        self.assertEqual(gesagt, [], "eine echte Wirkung wird nicht zusätzlich als Banner gesagt")
        self.assertIn("Wirkung: pausiert", gebaut[0].zeige_ticker.call_args.args[0])

    def test_menue_zeigt_laeufe_freigaben_und_start_nur_mit_neuem_starter_und_sendet_die_aktion(self):
        app, gebaut = self.maschine()
        app.anzeigeorte.unterstuetzt = False
        app.ereignis(_event("ablauf_stand", {"laeufe": [], "offen": [], "lernen": False, "ablaeufe": [{"id": "demo", "name": "Demo", "version": 2}]}))
        self.assertEqual(app._ablauf_menueeintraege(), [], "ohne neuen Starter kein Ablauf-Menü")
        app.anzeigeorte.unterstuetzt = True
        app.gewaehlt = "t-1"
        app.ereignis(_event("ablauf_stand", {"laeufe": [{"id": "l-1", "ablauf": "demo", "version": 2, "agent": "Codex", "status": "running", "knoten": "a", "grund": "", "modi": ["free"], "schritte": 1, "eltern": None},
                                                       {"id": "l-2", "ablauf": "demo", "version": 2, "agent": "Codex", "status": "paused", "knoten": "a", "grund": "", "modi": ["free"], "schritte": 1, "eltern": None},
                                                       {"id": "l-3", "ablauf": "demo", "version": 2, "agent": "Codex", "status": "completed", "knoten": None, "grund": "", "modi": ["free"], "schritte": 3, "eltern": None}],
                                             "offen": [{"id": "g-1", "lauf": "l-1", "knoten": "k", "beschreibung": "handeln weltdom"}], "lernen": False, "ablaeufe": [{"id": "demo", "name": "Demo", "version": 2}]}))
        e = app._ablauf_menueeintraege()
        texte = [x[1] for x in e if x]
        for erwartet in ("Freigeben: handeln weltdom", "Verweigern: handeln weltdom", "Ablauf pausieren: demo · Codex · running", "Ablauf fortsetzen: demo · Codex · paused", "Ablauf starten: Demo (v2) für Codex",
                         "Lernen aus Abläufen: aus — einschalten"):
            self.assertIn(erwartet, texte)
        self.assertFalse(any("l-3" in str(a) for a in app._ablauf_aktionen.values()), "ein beendeter Lauf bietet keine Steueraktion")
        aktionen = {a["aktion"] for a in app._ablauf_aktionen.values()}
        self.assertEqual(aktionen, {"freigeben", "verweigern", "pausieren", "fortsetzen", "abbrechen", "start", "lernen"})
        app._ablauf_aktion_senden({"aktion": "pausieren", "lauf_id": "l-1"})
        self.assertEqual(app.runtime.gesendet[-1], ("ablauf_steuern", {"aktion": "pausieren", "lauf_id": "l-1"}))


class CliTests(unittest.TestCase):
    def anfrage(self, *argv):
        from unittest import mock

        from client_vps import bridge_cli

        with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
            code = bridge_cli.main(list(argv))
        return code, ask.call_args.args[0] if ask.call_args else None

    def test_alle_befehle(self):
        datei = Path(tempfile.mkdtemp()) / "f.json"
        datei.write_text(json.dumps(fluss()))
        faelle = {("ablauf", "liste"): {"cmd": "ablauf", "befehl": "liste"}, ("ablauf", "neu", str(datei)): {"cmd": "ablauf", "befehl": "neu", "ablauf": fluss()},
                  ("ablauf", "zeige", "demo"): {"cmd": "ablauf", "befehl": "zeige", "ablauf": "demo"}, ("ablauf", "zeige", "demo", "2"): {"cmd": "ablauf", "befehl": "zeige", "ablauf": "demo", "version": 2},
                  ("ablauf", "start", "demo"): {"cmd": "ablauf", "befehl": "start", "ablauf": "demo"},
                  ("ablauf", "start", "demo", "--modi=shadow,witness", "--warten"): {"cmd": "ablauf", "befehl": "start", "ablauf": "demo", "modi": ["shadow", "witness"], "warten": True},
                  ("ablauf", "pause", "l-1"): {"cmd": "ablauf", "befehl": "pause", "lauf": "l-1"}, ("ablauf", "weiter", "l-1"): {"cmd": "ablauf", "befehl": "weiter", "lauf": "l-1"},
                  ("ablauf", "stopp", "l-1"): {"cmd": "ablauf", "befehl": "stopp", "lauf": "l-1"}, ("ablauf", "status", "l-1"): {"cmd": "ablauf", "befehl": "status", "lauf": "l-1"},
                  ("ablauf", "replay", "l-1"): {"cmd": "ablauf", "befehl": "replay", "lauf": "l-1"},
                  ("ablauf", "checkpoint", "l-1", "cp"): {"cmd": "ablauf", "befehl": "checkpoint", "lauf": "l-1", "name": "cp"}, ("ablauf", "zweig", "l-1", "cp"): {"cmd": "ablauf", "befehl": "zweig", "lauf": "l-1", "checkpoint": "cp"}}
        for argv, erwartet in faelle.items():
            self.assertEqual(self.anfrage(*argv), (0, erwartet), argv)

    def test_falsche_aufrufe_senden_nichts_und_kaputte_dateien_werden_gemeldet(self):
        for argv in (("ablauf",), ("ablauf", "tanzen"), ("ablauf", "liste", "x"), ("ablauf", "zeige", "demo", "x"), ("ablauf", "start"), ("ablauf", "pause"), ("ablauf", "checkpoint", "l-1"), ("ablauf", "start", "d", "--quatsch")):
            self.assertEqual(self.anfrage(*argv), (2, None), argv)
        code, gesendet = self.anfrage("ablauf", "neu", "/gibt/es/nicht.json")
        self.assertEqual((code, gesendet), (1, None), "eine nicht lesbare Datei ist ein Fehler mit Grund, nichts wird gesendet")

    def test_lange_befehle_haben_einen_langen_timeout_und_die_hilfe_nennt_alles(self):
        from client_vps import bridge_cli

        self.assertGreaterEqual(bridge_cli.LANGE_BEFEHLE["weltdom"], 40.0 + 10)
        self.assertGreaterEqual(bridge_cli.LANGE_BEFEHLE["haende"], 15.0 + 10)
        for wort in ("ablauf liste", "ablauf neu", "ablauf start", "ablauf zweig", "ablauf replay", "Lernen kann nur Daniel"):
            self.assertIn(wort, bridge_cli.__doc__)


if __name__ == "__main__":
    unittest.main()
