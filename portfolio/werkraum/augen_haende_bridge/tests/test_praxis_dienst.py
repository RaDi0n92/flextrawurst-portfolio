"""Praxistest im Starter: echte Spuren aus dem Ereignisprotokoll öffnen die Knoten, die Ansage landet als Raute-Eingabe, das Protokoll entsteht live, das Werkzeug ist streng."""

from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from augen_haende_bridge.praxis import lauf as lauf_modul
from tests.test_ablauf_dienst import kurze_wartezeit, starter


class Basis(unittest.TestCase):
    def setUp(self):
        kurze_wartezeit(self)
        self.l, self.fv = starter()
        self.l.ziel_info["t-2"] = {"target_id": "kde1:window:77", "zustand": "ok", "faehigkeit": "frisch", "seit_ms": 1}
        self.d = self.l.praxis
        self.doku = Path(tempfile.mkdtemp())
        self.d.doku = self.doku
        self.d.ordner = Path(tempfile.mkdtemp())
        self.l._publish_alt = self.l._publish
        self.gesendet = []
        def publish(kind, payload, **kw):
            self.gesendet.append((kind, payload))
            # The real desktop sends this acknowledgement asynchronously.  The
            # unit harness answers immediately so tests never wait on a fake
            # transport for the 15-second production timeout.
            if kind == "raute_tippen" and payload.get("request_id"):
                self.d.raute_ergebnis({"terminal_id": payload["terminal_id"],
                                       "request_id": payload["request_id"],
                                       "ok": True, "grund": ""},
                                      self.l.anzeige.get(payload["terminal_id"]))
            return "x"
        self.l._publish = publish
        self.uhr = [1000.0]
        lauf_modul.time = lauf_modul.time  # echte Uhr; Lesezeit wird über lese_bis des Laufs verkürzt

    def starten(self, **kw):
        r = self.d.befehl("t-1", {"befehl": "start", "partner": "Claude", **kw})
        self.assertTrue(r["ok"], r)
        self.lauf = self.d.laeufe[r["lauf"]]
        return r

    def lesezeit_ueberspringen(self):
        self.lauf.z["lese_bis"] = 0.0

    def spur(self, tid, art, text="x", **daten):
        if art == "sehen":
            now = int(time.time() * 1000)
            daten = {"target_id": self.l.ziel_info.get(tid, {}).get("target_id"),
                     "captured_at_ms": now, "received_at_ms": now,
                     "source": "capture", **daten}
        self.l.kapseln.erfassen(art, tid, text, daten)
        time.sleep(0.003)

    def aktionsbeleg(self, tid, command="haende", action_kind="klick", **extra):
        """Typed v2 event used by the contract-v2 scenario tests."""
        ctx = self.d.kontext(tid)
        self.l.kapseln.erfassen("sonstiges", tid, "typed test action", {
            "praxis": ctx, "command": command, "befehl": "test",
            "action_kind": action_kind, "ok": True,
            "capture_fresh": extra.pop("capture_fresh", True), **extra})


ANSAGE = "Schritt 1 · Prüfe: Zähler steigt · Mache: einmal klicken · Erwarte: Zähler steht auf eins"


class StartTests(Basis):
    def test_explicit_stop_is_not_a_running_checkpoint_after_restart(self):
        self.starten()
        self.assertTrue(self.d.befehl("t-1", {"befehl": "stopp"})["ok"])
        saved = json.loads((self.d.ordner / f"{self.lauf.id}.checkpoint.json").read_text())
        self.assertEqual(saved["ergebnis"]["status"], "ABORTED")

    def test_start_mit_partner_gibt_die_erste_karte_und_den_ort_des_protokolls(self):
        r = self.starten()
        self.assertEqual((r["karte"]["schritt"], r["karte"]["du"], r["karte"]["handelnder"]), (1, "handelnder", "Codex"))
        self.assertIn(f"lauf-{r['lauf']}.md", r["sage"])
        self.assertEqual(self.d.befehl("t-2", {"befehl": "karte"})["du"], "zuschauer", "der Partner sieht denselben Lauf")

    def test_unbekannter_partner_sich_selbst_und_ohne_lauf(self):
        self.assertEqual(self.d.befehl("t-1", {"befehl": "start", "partner": "Niemand"})["reason"], "partner_unbekannt")
        self.assertEqual(self.d.befehl("t-1", {"befehl": "start", "partner": "Codex"})["reason"], "partner_unbekannt")
        self.assertEqual(self.d.befehl("t-1", {"befehl": "start", "partner": "Claude", "ab": 0})["reason"], "ab_ungueltig")
        r = self.d.befehl("t-1", {"befehl": "karte"})
        self.assertEqual(r["reason"], "kein_lauf")
        self.assertIn("test start", r["sage"])
        self.starten()
        self.assertEqual(self.d.befehl("t-1", {"befehl": "tanzen"})["reason"], "befehl_unbekannt")


class SpurenTests(Basis):
    def test_stale_or_wrong_target_observation_does_not_open_seen_node(self):
        self.starten()
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.lesezeit_ueberspringen()
        self.d.kontext("t-1")
        self.spur("t-1", "sehen", captured_at_ms=1, received_at_ms=1)
        self.spur("t-1", "sehen", target_id="another-window")
        self.assertEqual(self.d.evidenz("t-1", "sehen", self.lauf.z["t_ansage_ms"]), 0)
        self.spur("t-1", "sehen")
        self.assertEqual(self.d.evidenz("t-1", "sehen", self.lauf.z["t_ansage_ms"]), 1)

    def test_ansage_ohne_koerperquittung_zaehlt_nicht_als_raute(self):
        from unittest import mock

        self.starten()
        self.l._publish = lambda kind, payload, **kw: self.gesendet.append((kind, payload)) or "x"
        with mock.patch("client_vps.praxis_dienst.RAUTE_FRIST_S", 0.01):
            r = self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.assertEqual(r["reason"], "raute_nicht_erreichbar")
        self.assertEqual(r["quittung"]["grund"], "raute_quittung_fehlt")
        self.assertEqual(self.d.evidenz("t-1", "raute", 0), 0)

    def test_die_ansage_wird_in_die_raute_des_handelnden_getippt(self):
        self.starten()
        r = self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.assertTrue(r["ok"], r)
        tippen = [p for k, p in self.gesendet if k == "raute_tippen"]
        self.assertEqual([(p["terminal_id"], p["text"]) for p in tippen], [("t-1", ANSAGE)])
        self.assertEqual(self.d.befehl("t-1", {"befehl": "ansage", "text": "Ich klicke mal"})["reason"], "jetzt_lesen")

    def test_ein_hinsehen_schritt_braucht_kein_zweites_bild_nach_dem_getan(self):
        self.starten()
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.lesezeit_ueberspringen()
        self.assertEqual(self.d.befehl("t-1", {"befehl": "getan", "text": "Bild geholt und angesehen, Fenster beschrieben"})["fehlt"], ["sehen"])
        self.spur("t-1", "sehen", "see")
        self.aktionsbeleg("t-1", command="see", capture_fresh=True)
        self.assertTrue(self.d.befehl("t-1", {"befehl": "getan", "text": "Bild geholt und angesehen, Fenster beschrieben"})["ok"])
        self.assertTrue(self.d.befehl("t-1", {"befehl": "gesehen", "text": "Schaltfläche, Feld, Regler und Fläche", "urteil": "ok"})["ok"], "das Bild von eben genügt")
        self.assertEqual(self.d.befehl("t-2", {"befehl": "zuschauer", "text": "Ich sehe dasselbe auf meinem Bild", "urteil": "bestaetigt"})["reason"], "spur_fehlt")
        self.spur("t-2", "sehen", "see")
        self.aktionsbeleg("t-2", command="see", capture_fresh=True)
        self.assertTrue(self.d.befehl("t-2", {"befehl": "zuschauer", "text": "Ich sehe dasselbe auf meinem Bild", "urteil": "bestaetigt"})["ok"])

    def test_der_ganze_schritt_mit_echten_spuren_und_das_protokoll_entsteht(self):
        self.starten(ab=2)
        h, z = "t-2", "t-1"  # Schritt 2 (Klicken) handelt B = Claude, A = Codex schaut zu
        self.assertEqual(self.d.befehl(h, {"befehl": "karte"})["du"], "handelnder")
        self.d.befehl(h, {"befehl": "ansage", "text": ANSAGE.replace("Schritt 1", "Schritt 2")})
        self.lesezeit_ueberspringen()
        r = self.d.befehl(h, {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})
        self.assertEqual((r["ok"], r["reason"]), (False, "spur_fehlt"), "ohne Hände-Spur im Protokoll geht es nicht weiter")
        self.spur(h, "haende", "haende", ok=True, reason="")
        self.aktionsbeleg(h)
        self.assertTrue(self.d.befehl(h, {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})["ok"])
        self.assertEqual(self.d.befehl(h, {"befehl": "gesehen", "text": "Der Zähler zeigt eins", "urteil": "ok"})["reason"], "spur_fehlt")
        self.spur(h, "sehen", "see")
        self.aktionsbeleg(h, command="see", capture_fresh=True)
        self.assertTrue(self.d.befehl(h, {"befehl": "gesehen", "text": "Der Zähler zeigt eins", "urteil": "ok"})["ok"])
        # der dritte echte Fehlversuch an diesem Schritt (getan, gesehen, jetzt zuschauer) hält den Lauf an; erst die Ursache löst ihn
        self.assertEqual(self.d.befehl(z, {"befehl": "zuschauer", "text": "Auf meinem Bild steht eins", "urteil": "bestaetigt"})["reason"], "halt")
        self.assertEqual(self.d.befehl(z, {"befehl": "nicht_getestet", "text": "ich überspringe das einfach mal"})["reason"], "halt")
        self.assertTrue(self.d.befehl(z, {"befehl": "ursache", "text": "Mein eigenes Bild fehlte noch; ich habe es jetzt mit see geholt"})["ok"])
        self.spur(z, "sehen", "see")
        self.aktionsbeleg(z, command="see", capture_fresh=True)
        r = self.d.befehl(z, {"befehl": "zuschauer", "text": "Auf meinem Bild steht eins", "urteil": "bestaetigt"})
        self.assertTrue(r["ok"], r)
        md = (self.doku / f"lauf-{self.lauf.id}.md").read_text(encoding="utf-8")
        self.assertIn("Schritt | Status", md)
        self.assertIn("2 Klicken | ok | Claude → Codex", md)
        self.assertIn("Zeiger auf die Schaltfläche, einmal geklickt", md)
        zeilen = [json.loads(x) for x in (self.d.ordner / f"{self.lauf.id}.jsonl").read_text().splitlines()]
        self.assertEqual([x["status"] for x in zeilen if x["status"] != "zurueckgestellt"], ["fehlversuch", "fehlversuch", "fehlversuch", "halt", "ursache", "ok"])
        raute = [p["terminal_id"] for k, p in self.gesendet if k == "raute_tippen"]
        self.assertEqual(raute, [h], "nur die Ansage steht in der Raute, kein Fazit hinterher")

    def test_spuren_des_falschen_agenten_oder_der_falschen_art_zaehlen_nicht(self):
        self.starten()
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.lesezeit_ueberspringen()
        self.spur("t-2", "haende", "haende", ok=True)  # der andere
        self.spur("t-1", "haende", "haende", ok=False, reason="lease_fehlt")  # abgelehnt zählt nicht als Handlung
        self.spur("t-1", "nachricht", "nachricht")
        r = self.d.befehl("t-1", {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})
        self.assertEqual(r["reason"], "spur_fehlt")
        self.assertEqual(self.d.evidenz("t-1", "haende_abgelehnt", 0), 0, "nur Ablehnung mit Grund „ausserhalb“ zählt als Negativtest")
        self.spur("t-1", "haende", "haende", ok=False, reason="ausserhalb")
        self.assertEqual(self.d.evidenz("t-1", "haende_abgelehnt", 0), 1)

    def test_evidenz_fuer_kapsel_seed_und_loop_kommt_aus_den_diensten(self):
        t0 = int(time.time() * 1000) - 1
        self.assertEqual((self.d.evidenz("t-1", "kapsel", t0), self.d.evidenz("t-1", "seed", t0), self.d.evidenz("t-1", "loop", t0)), (0, 0, 0))
        self.l.kapseln.moment("Codex", "agent", "g", agenten=["t-1"])
        self.l.seeds.befehl("t-1", {"befehl": "vorschlagen", "zieltyp": "kontext", "titel": "H", "inhalt": "x", "empfaenger": ["Claude"]})
        self.assertEqual(self.d.evidenz("t-1", "kapsel", t0), 1)
        self.assertEqual(self.d.evidenz("t-1", "seed", t0), 1)
        self.assertEqual(self.d.evidenz("t-2", "seed", t0), 0, "ein Seed gehört dem, der ihn vorgeschlagen hat")


class SzenarioWahlTests(Basis):
    def test_szenario_waehlen_und_auflisten(self):
        r = self.d.befehl("t-1", {"befehl": "szenarien"})
        self.assertEqual([x["name"] for x in r["szenarien"]], ["gemgem-allein", "menschlich", "nutzerin-anwendungsfaelle"])
        self.starten(szenario="menschlich")
        for schlecht in ("../x", "gibtsnicht"):
            self.assertFalse(self.d.befehl("t-1", {"befehl": "start", "partner": "Claude", "szenario": schlecht})["ok"], schlecht)


class DienstBelegTests(Basis):
    def prepare(self, step):
        self.starten(ab=step)
        actor = self.lauf.handelnder()
        self.assertTrue(self.d.befehl(actor, {"befehl": "ansage", "text": self.lauf.karte(actor)["ansage_vorlage"]})["ok"])
        self.lesezeit_ueberspringen()
        return actor

    def test_capsule_service_answers_satisfy_same_resource_proof(self):
        actor = self.prepare(21)
        created = self.l._agent_befehl(actor, "kapsel", {"befehl": "moment"})
        self.assertTrue(created["ok"], created)
        viewer = self.lauf.zuschauer_von()
        read = self.l._agent_befehl(viewer, "kapsel", {"befehl": "zeige", "kapsel": created["kapsel"]})
        self.assertTrue(read["ok"], read)
        self.assertTrue(self.d.pruefe_belege(self.lauf)["ok"])

    def test_context_seed_requires_daniel_and_real_partner_delivery(self):
        actor = self.prepare(22)
        proposed = self.l._agent_befehl(actor, "seed", {
            "befehl": "vorschlagen", "zieltyp": "kontext", "titel": "Test",
            "inhalt": "Ein Beleg", "empfaenger": ["Codex"]})
        self.assertTrue(proposed["ok"], proposed)
        self.assertFalse(self.d.pruefe_belege(self.lauf)["ok"])
        # Unit fixture for the human approval event; no external owner message.
        self.l.seeds.store.freigeben(proposed["seed"], "Daniel", proposed["version"])
        delivered = self.l._agent_befehl(actor, "seed", {"befehl": "ausliefern", "seed": proposed["seed"]})
        self.assertTrue(delivered["ok"], delivered)
        self.assertTrue(self.d.pruefe_belege(self.lauf)["ok"])

    def test_loop_delivery_and_finished_budget_are_the_same_loop(self):
        from tests.test_seed_dienst import flow

        actor = self.prepare(23)
        self.addCleanup(self.l.seeds.stoppen)
        self.l.ablauf.speicher.speichere(flow(), "fixture")
        proposed = self.l._agent_befehl(actor, "seed", {
            "befehl": "vorschlagen", "zieltyp": "loop", "titel": "Bounded loop",
            "inhalt": "meinfluss", "budget": {"max_laeufe": 3, "intervall_s": 0}})
        self.assertTrue(proposed["ok"], proposed)
        self.l.seeds.store.freigeben(proposed["seed"], "Daniel", proposed["version"])
        delivered = self.l._agent_befehl(actor, "seed", {"befehl": "ausliefern", "seed": proposed["seed"]})
        self.assertTrue(delivered["ok"], delivered)
        loop = self.l.seeds.loops.hole(delivered["loop"])
        loop._faden.join(5)
        self.assertFalse(loop._faden.is_alive())
        status = self.l._agent_befehl(actor, "seed", {"befehl": "loop", "aktion": "status", "loop": delivered["loop"]})
        self.assertTrue(status["ok"], status)
        self.assertTrue(self.d.pruefe_belege(self.lauf)["ok"], status)


class WerkzeugTests(unittest.TestCase):
    def anfrage(self, *argv):
        from unittest import mock

        from client_vps import bridge_cli

        with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
            code = bridge_cli.main(list(argv))
        return code, ask.call_args.args[0] if ask.call_args else None

    def test_alle_befehle_und_strenge(self):
        faelle = {("test", "start", "Gemgem"): {"cmd": "test", "befehl": "start", "partner": "Gemgem", "ab": 1}, ("test", "start", "Gemgem", "--ab=5"): {"cmd": "test", "befehl": "start", "partner": "Gemgem", "ab": 5},
                  ("test", "start", "Gemgem", "--szenario=skill-demo"): {"cmd": "test", "befehl": "start", "partner": "Gemgem", "ab": 1, "szenario": "skill-demo"}, ("test", "szenarien"): {"cmd": "test", "befehl": "szenarien"},
                  ("test", "karte"): {"cmd": "test", "befehl": "karte"}, ("test", "status"): {"cmd": "test", "befehl": "status"}, ("test", "nochmal"): {"cmd": "test", "befehl": "nochmal"},
                  ("test", "ansage", "Schritt 1 ·", "Prüfe: a"): {"cmd": "test", "befehl": "ansage", "text": "Schritt 1 · Prüfe: a"},
                  ("test", "gesehen", "Zähler", "eins", "ok"): {"cmd": "test", "befehl": "gesehen", "text": "Zähler eins", "urteil": "ok"},
                  ("test", "zuschauer", "sehe", "eins", "bestaetigt"): {"cmd": "test", "befehl": "zuschauer", "text": "sehe eins", "urteil": "bestaetigt"},
                  ("test", "entdeckung", "Die", "Raute", "flackert"): {"cmd": "test", "befehl": "kuer", "text": "Die Raute flackert"}}
        for argv, erwartet in faelle.items():
            self.assertEqual(self.anfrage(*argv), (0, erwartet), argv)
        for schlecht in (("test",), ("test", "tanzen"), ("test", "start"), ("test", "start", "A", "--ab=x"), ("test", "ansage"), ("test", "gesehen", "nur-ein-wort"), ("test", "karte", "extra"), ("test", "start", "A", "--quatsch")):
            self.assertEqual(self.anfrage(*schlecht), (2, None), schlecht)


class RauteSpurTests(Basis):
    def test_say_schreibe_und_see_hinterlassen_spuren_im_protokoll(self):
        l = self.l
        l.sessions["t-1"].token = "geheim"
        l.sessions["t-1"].state = "running"
        t0 = int(time.time() * 1000) - 1
        anfrage = lambda **kw: l.agent_request({"terminal_id": "t-1", "token": "geheim", **kw})
        self.assertTrue(anfrage(cmd="say", text="Hallo Daniel")["ok"])
        self.assertTrue(anfrage(cmd="schreibe", text="Schritt 1 · Prüfe: x")["ok"])
        self.assertEqual(self.d.evidenz("t-1", "raute", t0), 2)
        self.assertEqual(anfrage(cmd="see")["reason"], "no_frame_yet")
        self.assertEqual(self.d.evidenz("t-1", "sehen", t0), 0, "ohne Bild keine Sehen-Spur")
        (l.frames_dir / "t-1").mkdir(parents=True, exist_ok=True)
        (l.frames_dir / "t-1" / "latest.json").write_text(json.dumps({"file": "f.jpg", "mime": "image/jpeg", "captured_at_ms": t0, "received_at_ms": t0, "width": 640, "height": 480, "source": "capture", "seq": 3}))
        self.assertTrue(anfrage(cmd="see")["ok"])
        self.assertEqual(self.d.evidenz("t-1", "sehen", t0), 1)
        self.assertEqual(self.d.evidenz("t-2", "sehen", t0), 0, "die Spur gehört dem, der hingesehen hat")


class HilfeImDienstTests(Basis):
    def test_zielwechsel_nach_der_ansage_antwortet_mit_neu_ansagen_und_zaehlt_nicht(self):
        self.starten()
        self.assertTrue(self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})["ok"])
        self.lesezeit_ueberspringen()
        self.l.ziel_info["t-2"]["target_id"] = "kde1:window:99"
        for befehl in ("getan", "gesehen", "zuschauer"):
            r = self.d.befehl("t-1", {"befehl": befehl, "text": "Zeiger auf die Schaltfläche, einmal geklickt", "urteil": "ok"})
            self.assertEqual(r["reason"], "ziel_gewechselt", befehl)
            self.assertIn("test nochmal", r["next"]["befehl"])
        self.assertEqual(self.lauf.fehlversuche.get(1, 0), 0)

    def test_nach_nochmal_gilt_das_neue_ziel(self):
        self.starten()
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.l.ziel_info["t-2"]["target_id"] = "kde1:window:99"
        self.assertEqual(self.d.befehl("t-1", {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})["reason"], "ziel_gewechselt")
        self.assertTrue(self.d.befehl("t-1", {"befehl": "nochmal"})["ok"])
        self.assertTrue(self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})["ok"])
        self.lesezeit_ueberspringen()
        self.assertNotEqual(self.d.befehl("t-1", {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"}).get("reason"), "ziel_gewechselt")

    def test_nach_einem_fehlversuch_steht_die_erinnerung_in_der_karte(self):
        gesucht = []
        self.starten()
        self.d._aehnliche = lambda grund, titel, **kw: gesucht.append((grund, titel, kw.get("klasse"))) or [{"wann": "2026-10-03 18:00:00", "woher": "protokoll/raute", "text": "Ziel wechselte nach der Ansage"}]
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.lesezeit_ueberspringen()
        r = self.d.befehl("t-1", {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})
        self.assertEqual((r["reason"], r["klasse"]), ("spur_fehlt", "ausfuehrung"))
        for _ in range(100):
            if self.lauf.erinnerung:
                break
            time.sleep(0.02)
        k = self.d.befehl("t-1", {"befehl": "karte"})
        self.assertEqual(gesucht[0][0], "spur_fehlt")
        self.assertEqual(k["erinnerung"]["faelle"][0]["text"], "Ziel wechselte nach der Ansage")

    def test_eine_haengende_suche_haelt_den_befehl_nicht_auf(self):
        self.starten()
        self.d._aehnliche = lambda *a, **k: time.sleep(5) or []
        self.d.befehl("t-1", {"befehl": "ansage", "text": ANSAGE})
        self.lesezeit_ueberspringen()
        t0 = time.monotonic()
        self.d.befehl("t-1", {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})
        self.assertLess(time.monotonic() - t0, 2.0)


if __name__ == "__main__":
    unittest.main()
