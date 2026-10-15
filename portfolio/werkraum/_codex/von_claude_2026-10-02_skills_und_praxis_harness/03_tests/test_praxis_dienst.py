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
        self.d = self.l.praxis
        self.doku = Path(tempfile.mkdtemp())
        self.d.doku = self.doku
        self.d.ordner = Path(tempfile.mkdtemp())
        self.l._publish_alt = self.l._publish
        self.gesendet = []
        self.l._publish = lambda kind, payload, **kw: self.gesendet.append((kind, payload)) or "x"
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
        self.l.kapseln.erfassen(art, tid, text, daten)
        time.sleep(0.003)


ANSAGE = "Schritt 1 · Prüfe: Zähler steigt · Mache: einmal klicken · Erwarte: Zähler steht auf eins"


class StartTests(Basis):
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
        self.assertTrue(self.d.befehl("t-1", {"befehl": "getan", "text": "Bild geholt und angesehen, Fenster beschrieben"})["ok"])
        self.assertTrue(self.d.befehl("t-1", {"befehl": "gesehen", "text": "Schaltfläche, Feld, Regler und Fläche", "urteil": "ok"})["ok"], "das Bild von eben genügt")
        self.assertEqual(self.d.befehl("t-2", {"befehl": "zuschauer", "text": "Ich sehe dasselbe auf meinem Bild", "urteil": "bestaetigt"})["reason"], "spur_fehlt")
        self.spur("t-2", "sehen", "see")
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
        self.assertTrue(self.d.befehl(h, {"befehl": "getan", "text": "Zeiger auf die Schaltfläche, einmal geklickt"})["ok"])
        self.assertEqual(self.d.befehl(h, {"befehl": "gesehen", "text": "Der Zähler zeigt eins", "urteil": "ok"})["reason"], "spur_fehlt")
        self.spur(h, "sehen", "see")
        self.assertTrue(self.d.befehl(h, {"befehl": "gesehen", "text": "Der Zähler zeigt eins", "urteil": "ok"})["ok"])
        self.assertEqual(self.d.befehl(z, {"befehl": "zuschauer", "text": "Auf meinem Bild steht eins", "urteil": "bestaetigt"})["reason"], "spur_fehlt")
        self.spur(z, "sehen", "see")
        r = self.d.befehl(z, {"befehl": "zuschauer", "text": "Auf meinem Bild steht eins", "urteil": "bestaetigt"})
        self.assertTrue(r["ok"], r)
        md = (self.doku / f"lauf-{self.lauf.id}.md").read_text(encoding="utf-8")
        self.assertIn("Schritt | Status", md)
        self.assertIn("2 Klicken | ok | Claude → Codex", md)
        self.assertIn("Zeiger auf die Schaltfläche, einmal geklickt", md)
        zeilen = [json.loads(x) for x in (self.d.ordner / f"{self.lauf.id}.jsonl").read_text().splitlines()]
        self.assertEqual([x["status"] for x in zeilen if x["status"] != "zurueckgestellt"], ["ok"])
        raute = [p["terminal_id"] for k, p in self.gesendet if k == "raute_tippen"]
        self.assertEqual(raute, [h, h, z], "Ansage, Gesehen und Bestätigung stehen je in der Raute des Sprechenden")

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
        self.assertEqual([x["name"] for x in r["szenarien"]], ["menschlich"])
        self.starten(szenario="menschlich")
        for schlecht in ("../x", "gibtsnicht"):
            self.assertFalse(self.d.befehl("t-1", {"befehl": "start", "partner": "Claude", "szenario": schlecht})["ok"], schlecht)


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


if __name__ == "__main__":
    unittest.main()
