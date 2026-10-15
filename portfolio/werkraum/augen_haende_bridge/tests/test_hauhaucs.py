"""G14: Hauhaucs als Beobachter — aufgezeichnet/zugestellt/verarbeitet getrennt, kein Modellaufruf ohne Auftrag, Bilder getrennt, Budget/Stop, Quellenprüfung.

Das Modell ist ein lokaler Fake-Server im OpenAI-Format auf einem freien Port. Port 11436 (Hintergrundinstanz) wird nie angesprochen;
ein Live-Test gegen den Chat-Server 11435 läuft nur mit BRIDGE_LIVE_CHAT=1.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from augen_haende_bridge import hauhaucs
from augen_haende_bridge.ereignisprotokoll import Ereignisprotokoll
from augen_haende_bridge.hauhaucs import Beobachtung, BeobachterFehler, Budget, ModellClient
from augen_haende_bridge.kontextmischpult import Mischpult


class FakeServer:
    def __init__(self, antwort="Codex schrieb hallo [e-1]. Außerdem [e-999] und [k-nix].", usage=None, status=200, rohantwort=None):
        self.anfragen: list[dict] = []
        außen = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                außen.anfragen.append(json.loads(self.rfile.read(n)))
                if rohantwort is not None:
                    daten = rohantwort.encode()
                else:
                    daten = json.dumps({"choices": [{"message": {"content": antwort}}], "usage": usage or {"prompt_tokens": 50, "completion_tokens": 10, "total_tokens": 60}}).encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(daten)))
                self.end_headers()
                self.wfile.write(daten)

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1/chat/completions"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def schliessen(self):
        self.server.shutdown()
        self.server.server_close()


def bauen(server=None, **kw):
    protokoll = Ereignisprotokoll(Path(tempfile.mkdtemp()))
    client = ModellClient(server.url, timeout_s=5) if server else None
    return protokoll, Beobachtung(protokoll, client=client, **kw)


class SteuernTests(unittest.TestCase):
    def test_nichts_wird_vor_dem_start_aufgezeichnet_und_nach_stop_nicht_mehr(self):
        p, b = bauen()
        p.erfassen("nachricht", "codex", "vorher")
        self.assertEqual(b.status()["wartend"], 0)
        b.starten(["codex"])
        p.erfassen("nachricht", "codex", "waehrend")
        p.erfassen("nachricht", "gemini", "fremder agent")
        self.assertEqual((b.status()["wartend"], b.status()["agenten"][0]["aufgezeichnet"]), (1, 1))
        b.stop()
        p.erfassen("nachricht", "codex", "nachher")
        self.assertEqual((b.status()["wartend"], b.status()["aktiv"]), (1, False))

    def test_eins_bis_drei_agenten(self):
        _, b = bauen()
        for kaputt in ([], ["a", "b", "c", "d"]):
            with self.assertRaises(BeobachterFehler):
                b.starten(kaputt)
        b.starten(["a", "a", "b"])
        self.assertEqual(b.agenten, ("a", "b"))

    def test_bilder_nur_wenn_zugeschaltet(self):
        p, b = bauen()
        b.starten(["codex"])
        p.erfassen("frame", "codex", "bild")
        self.assertEqual(b.status()["wartend"], 0)
        b.bilder_schalten(True)
        p.erfassen("frame", "codex", "bild")
        self.assertEqual(b.status()["wartend"], 1)


class ZaehlerTests(unittest.TestCase):
    def test_aufgezeichnet_zugestellt_verarbeitet_sind_drei_getrennte_zahlen(self):
        s = FakeServer()
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            for t in ("eins", "zwei", "drei"):
                p.erfassen("nachricht", "codex", t)
            z = b.status()["agenten"][0]
            self.assertEqual((z["aufgezeichnet"], z["zugestellt"], z["verarbeitet"]), (3, 0, 0))
            self.assertEqual(b.zustellen(), 3)
            z = b.status()["agenten"][0]
            self.assertEqual((z["aufgezeichnet"], z["zugestellt"], z["verarbeitet"]), (3, 3, 0))
            self.assertEqual(s.anfragen, [], "bis hierhin kein einziger Modellaufruf")
            self.assertTrue(b.jetzt_dokumentieren()["ok"])
            z = b.status()["agenten"][0]
            self.assertEqual((z["aufgezeichnet"], z["zugestellt"], z["verarbeitet"]), (3, 3, 3))
            self.assertEqual(len(s.anfragen), 1)
        finally:
            s.schliessen()

    def test_zugestellte_sind_im_pult_lesbar_mit_kennung_und_name(self):
        p, b = bauen(namen=lambda t: {"codex": "Codex"}.get(t, t))
        b.starten(["codex"])
        p.erfassen("nachricht", "codex", "hallo welt")
        b.zustellen()
        text = b.pult.vorschau()[0]["content"]
        self.assertRegex(text, r"^\[e-\d+\] \d\d:\d\d:\d\d Codex · nachricht: hallo welt$")
        self.assertIn("hallo welt", b.lesbar("codex"))

    def test_reine_aufnahme_braucht_kein_modell(self):
        p, b = bauen()
        b.starten(["codex"])
        p.erfassen("nachricht", "codex", "x")
        self.assertEqual(b.zustellen(), 1)
        self.assertEqual(b.jetzt_dokumentieren(), {"ok": False, "reason": "kein_modell_angebunden"})


class DokumentierenTests(unittest.TestCase):
    def test_quellen_werden_gegen_das_protokoll_geprueft(self):
        s = FakeServer()
        try:
            p, b = bauen(s, kapsel_existiert=lambda k: k == "k-ok")
            b.starten(["codex"])
            eid = p.erfassen("nachricht", "codex", "hallo")
            s.server.RequestHandlerClass  # Fake kennt die ID nicht vorab: Antwort mit echter ID bauen
            s.schliessen()
            s2 = FakeServer(antwort=f"Codex sagte hallo [{eid}]. Dazu [e-999] und [k-ok] und [k-nix].")
            b.client = ModellClient(s2.url, timeout_s=5)
            try:
                r = b.jetzt_dokumentieren("Fasse zusammen", kapseln=["k-ok"])
            finally:
                s2.schliessen()
            self.assertTrue(r["ok"])
            self.assertEqual((r["quellen"], r["unbekannte_quellen"], r["ohne_quellenbezug"]), ([eid, "k-ok"], ["e-999", "k-nix"], False))
            gesendet = json.dumps(s2.anfragen[0]["messages"])
            self.assertIn("Fasse zusammen", gesendet)
            self.assertIn("hallo", gesendet)
            self.assertEqual(b.pult.nachrichten[-1].quelle, "hauhaucs")
        finally:
            pass

    def test_antwort_ohne_quellen_wird_so_gekennzeichnet(self):
        s = FakeServer(antwort="Alles war ruhig.")
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            r = b.jetzt_dokumentieren()
            self.assertEqual((r["ok"], r["quellen"], r["ohne_quellenbezug"]), (True, [], True))
        finally:
            s.schliessen()

    def test_grenzen_aus_dem_pult_gelten_fuer_anfrage_und_antwort(self):
        s = FakeServer(antwort="x" * 500)
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            b.pult.grenzen_setzen(100, 64)
            r = b.jetzt_dokumentieren()
            self.assertEqual((len(r["text"]), s.anfragen[0]["max_tokens"]), (100, 64))
        finally:
            s.schliessen()

    def test_serverkuerzung_wird_angezeigt(self):
        s = FakeServer(usage={"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4})
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            for i in range(20):
                p.erfassen("nachricht", "codex", f"ereignis nummer {i} mit etwas Text")
            r = b.jetzt_dokumentieren()
            self.assertEqual(r["kontext"]["serverkuerzung"], "vermutet")
        finally:
            s.schliessen()

    def test_bilder_nur_mit_schalter_und_dann_als_image_url(self):
        s = FakeServer()
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            self.assertEqual(b.jetzt_dokumentieren(bilder=["QUJD"])["reason"], "bilder_nicht_zugeschaltet")
            self.assertEqual(s.anfragen, [])
            b.bilder_schalten(True)
            self.assertTrue(b.jetzt_dokumentieren(bilder=["QUJD"])["ok"])
            inhalt = s.anfragen[0]["messages"][-1]["content"]
            self.assertEqual(inhalt[1]["image_url"]["url"], "data:image/jpeg;base64,QUJD")
        finally:
            s.schliessen()


class ChatTests(unittest.TestCase):
    def test_freies_gespraech_haelt_den_verlauf_im_pult_und_schickt_ihn_mit(self):
        s = FakeServer(antwort="Hallo Daniel.")
        try:
            _, b = bauen(s)
            r1 = b.chatten("Hallo Hauhaucs")
            r2 = b.chatten("Und noch eine Frage")
            self.assertEqual((r1["ok"], r1["text"], r2["ok"]), (True, "Hallo Daniel.", True))
            self.assertEqual([n.rolle for n in b.pult.nachrichten], ["user", "assistant", "user", "assistant"])
            zweite = s.anfragen[1]["messages"]
            self.assertEqual([m["content"] for m in zweite], ["Hallo Hauhaucs", "Hallo Daniel.", "Und noch eine Frage"], "der erste Austausch geht beim zweiten Mal mit")
            self.assertEqual(b.status()["chat_aufrufe"], 2)
            self.assertEqual(b.budget.aufrufe, 0, "ein Gespräch verbraucht das Beobachtungsbudget nicht")
        finally:
            s.schliessen()

    def test_chat_geht_auch_nach_stop_der_beobachtung_und_ohne_start(self):
        s = FakeServer()
        try:
            _, b = bauen(s)
            b.stop()
            self.assertTrue(b.chatten("Hallo")["ok"])
        finally:
            s.schliessen()

    def test_gekuerzter_verlauf_wirkt_auf_das_naechste_gespraech(self):
        s = FakeServer()
        try:
            _, b = bauen(s)
            b.chatten("Eins")
            b.pult.leeren()
            b.chatten("Zwei")
            self.assertEqual([m["content"] for m in s.anfragen[1]["messages"]], ["Zwei"])
        finally:
            s.schliessen()

    def test_leerer_text_unerreichbares_modell_und_fehlendes_modell(self):
        s = FakeServer()
        try:
            _, b = bauen(s)
            self.assertEqual(b.chatten("   ")["reason"], "text_leer")
            self.assertEqual(s.anfragen, [])
        finally:
            s.schliessen()
        _, ohne = bauen()
        self.assertEqual(ohne.chatten("x")["reason"], "kein_modell_angebunden")
        p = Ereignisprotokoll(Path(tempfile.mkdtemp()))
        b = Beobachtung(p, client=ModellClient("http://127.0.0.1:1/v1/chat/completions", timeout_s=2))
        r = b.chatten("Hallo")
        self.assertTrue(r["reason"].startswith("modell_nicht_erreichbar"))
        self.assertEqual(b.pult.nachrichten, [], "die unbeantwortete Frage bleibt nicht im Verlauf")

    def test_ausgabegrenzen_gelten_im_gespraech(self):
        s = FakeServer(antwort="x" * 500)
        try:
            _, b = bauen(s)
            b.pult.grenzen_setzen(100, 32)
            r = b.chatten("Hallo")
            self.assertEqual((len(r["text"]), s.anfragen[0]["max_tokens"]), (100, 32))
        finally:
            s.schliessen()


class BudgetTests(unittest.TestCase):
    def test_aufrufbudget_erschoepft_und_wird_beim_neustart_nicht_umgangen(self):
        s = FakeServer()
        try:
            p, b = bauen(s, budget=Budget(max_aufrufe=2))
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            self.assertTrue(b.jetzt_dokumentieren()["ok"])
            self.assertTrue(b.jetzt_dokumentieren()["ok"])
            r = b.jetzt_dokumentieren()
            self.assertEqual((r["ok"], r["reason"]), (False, "budget_aufrufe_erschoepft"))
            self.assertEqual(len(s.anfragen), 2)
            b.starten(["codex"])
            self.assertEqual(b.jetzt_dokumentieren()["reason"], "budget_aufrufe_erschoepft")
        finally:
            s.schliessen()

    def test_tokenbudget_verweigert_vor_dem_aufruf(self):
        s = FakeServer()
        try:
            p, b = bauen(s, budget=Budget(max_tokens=5))
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "ein längerer Text " * 10)
            r = b.jetzt_dokumentieren()
            self.assertEqual(r["reason"], "budget_tokens_erschoepft")
            self.assertEqual(s.anfragen, [])
        finally:
            s.schliessen()

    def test_stop_verweigert_sofort_jeden_aufruf(self):
        s = FakeServer()
        try:
            p, b = bauen(s)
            b.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            b.stop()
            self.assertEqual(b.jetzt_dokumentieren()["reason"], "gestoppt")
            self.assertEqual(s.anfragen, [])
        finally:
            s.schliessen()


class ServerFehlerTests(unittest.TestCase):
    def test_zu_grosser_prompt_ist_ein_eigener_grund_mit_zahlen(self):
        s = FakeServer(status=400, rohantwort=json.dumps({"error": {"code": 400, "type": "exceed_context_size_error", "n_prompt_tokens": 9000, "n_ctx": 8192}}))
        try:
            _, b = bauen(s)
            self.assertEqual(b.chatten("Hallo")["reason"], "kontext_zu_gross:9000_von_8192")
            self.assertEqual(b.pult.nachrichten, [], "die abgelehnte Frage bleibt nicht im Verlauf")
            p, b2 = bauen(s)
            b2.starten(["codex"])
            p.erfassen("nachricht", "codex", "x")
            self.assertEqual(b2.jetzt_dokumentieren()["reason"], "kontext_zu_gross:9000_von_8192")
            self.assertEqual(b2.budget.aufrufe, 0)
        finally:
            s.schliessen()

    def test_andere_fehlercodes_sind_nicht_unerreichbar(self):
        for status, roh, erwartet in ((500, "{}", "modell_antwortet_mit_fehler:500"), (400, "kein json", "modell_antwortet_mit_fehler:400"), (400, json.dumps({"error": {"message": "Context length exceeded"}}), "kontext_zu_gross"),
                                       (503, json.dumps({"error": {"message": "loading"}}), "modell_antwortet_mit_fehler:503")):
            s = FakeServer(status=status, rohantwort=roh)
            try:
                _, b = bauen(s)
                self.assertEqual(b.chatten("x")["reason"], erwartet, (status, roh))
            finally:
                s.schliessen()


class FehlerTests(unittest.TestCase):
    def test_unerreichbares_modell_ist_ein_grund_kein_absturz_und_zaehlt_nicht_als_aufruf(self):
        p = Ereignisprotokoll(Path(tempfile.mkdtemp()))
        b = Beobachtung(p, client=ModellClient("http://127.0.0.1:1/v1/chat/completions", timeout_s=2))
        b.starten(["codex"])
        p.erfassen("nachricht", "codex", "x")
        r = b.jetzt_dokumentieren()
        self.assertEqual(r["ok"], False)
        self.assertTrue(r["reason"].startswith("modell_nicht_erreichbar"))
        self.assertEqual(b.budget.aufrufe, 0)
        self.assertEqual(b.status()["agenten"][0]["verarbeitet"], 0)

    def test_kaputte_antworten(self):
        for roh in ("kein json", "{}", '{"choices": []}'):
            s = FakeServer(rohantwort=roh)
            try:
                p, b = bauen(s)
                b.starten(["codex"])
                p.erfassen("nachricht", "codex", "x")
                self.assertFalse(b.jetzt_dokumentieren()["ok"], roh)
            finally:
                s.schliessen()

    def test_die_hintergrundinstanz_wird_nie_angesprochen(self):
        quelle = Path(hauhaucs.__file__).read_text(encoding="utf-8")
        code = "\n".join(z for z in quelle.splitlines() if not z.lstrip().startswith(("#", '"""')))
        self.assertEqual(hauhaucs.CHAT_URL, "http://localhost:11435/v1/chat/completions")
        self.assertNotIn("import hauhau", code.lower())


@unittest.skipUnless(os.environ.get("BRIDGE_LIVE_CHAT") == "1", "Live-Test gegen den Chat-Server 11435 nur auf Wunsch")
class LiveTests(unittest.TestCase):
    def test_echtes_modell_antwortet_auf_eine_kleine_dokumentation(self):
        p = Ereignisprotokoll(Path(tempfile.mkdtemp()))
        b = Beobachtung(p, client=ModellClient(timeout_s=300), budget=Budget(max_aufrufe=1, max_tokens=4000))
        b.pult.grenzen_setzen(None, 120)
        b.starten(["codex"])
        p.erfassen("nachricht", "codex", "Test: Codex hat die Datei a.txt angelegt.")
        r = b.jetzt_dokumentieren()
        self.assertTrue(r["ok"], r)
        self.assertTrue(r["text"].strip())


if __name__ == "__main__":
    unittest.main()
