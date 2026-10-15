"""G14: das Kontext-Mischpult — effektiv leere Sitzung, ID-genaue Auswahl, Bearbeiten, Leeren, Halbieren, Zurückspringen, Einspeisen ohne Antwort, Felder, Vorschau, Export/Import, Einmalfeedback, Grenzen, Modi, getrennte Schätzung/Messung."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from augen_haende_bridge.kontextmischpult import Mischpult, PultFehler


def gefuellt():
    p = Mischpult("Test")
    ids = [p.hinzufuegen("user", "Erster Satz. Zweiter Satz! Dritter Satz?", "daniel"), p.hinzufuegen("assistant", "Antwort eins.", "modell"), p.hinzufuegen("user", "Noch eine Frage.", "daniel"),
           p.hinzufuegen("assistant", "Antwort zwei.", "modell")]
    return p, ids


class LeereSitzungTests(unittest.TestCase):
    def test_eine_neue_sitzung_ist_effektiv_leer_keine_versteckten_prompts(self):
        p = Mischpult()
        self.assertEqual((p.vorschau(), p.basis_prompt, p.felder, p.nachrichten, p.einmalfeedback), ([], "", [], [], None))
        self.assertEqual(p.anfrage_bauen(), {"messages": [], "einmal_verbraucht": False, "gesendete_zeichen": 0})
        self.assertEqual(p.schaetzung()["tokens"], 0)
        self.assertEqual(p.anzeige()["nachrichten"], 0)

    def test_nach_leeren_ist_der_kontext_leer_bis_auf_aktive_felder(self):
        p, _ = gefuellt()
        p.feld_setzen("Rolle", "Du beobachtest.", True)
        self.assertEqual(p.leeren(), 4)
        self.assertEqual(p.vorschau(), [{"role": "system", "content": "Du beobachtest."}])
        p.feld_setzen("Rolle", "Du beobachtest.", False)
        self.assertEqual(p.vorschau(), [])

    def test_der_basisprompt_ist_nur_da_wenn_ausdruecklich_gesetzt_und_dann_sichtbar(self):
        p = Mischpult()
        p.basis_setzen("Sei knapp.")
        self.assertEqual(p.vorschau(), [{"role": "system", "content": "Sei knapp."}])
        p.basis_setzen("   ")
        self.assertEqual(p.vorschau(), [])


class AuswahlTests(unittest.TestCase):
    def test_vorschau_enthaelt_genau_die_ausgewaehlten_nachrichten_in_reihenfolge(self):
        p, ids = gefuellt()
        self.assertEqual([m["content"] for m in p.vorschau()][:2], ["Erster Satz. Zweiter Satz! Dritter Satz?", "Antwort eins."])
        self.assertEqual(p.nur_auswaehlen([ids[0], ids[3]]), 2)
        self.assertEqual([m["content"] for m in p.vorschau()], ["Erster Satz. Zweiter Satz! Dritter Satz?", "Antwort zwei."])
        p.auswaehlen([ids[1]], True)
        self.assertEqual(len(p.vorschau()), 3)
        p.auswaehlen(None, False)
        self.assertEqual(p.vorschau(), [])
        p.auswaehlen(None, True)
        self.assertEqual(len(p.vorschau()), 4)
        with self.assertRaises(PultFehler):
            p.auswaehlen(["m-99"])
        with self.assertRaises(PultFehler):
            p.nur_auswaehlen(["m-99"])

    def test_ereignisse_gehen_als_nutzernachricht_hinaus_und_bleiben_im_pult_als_ereignis_erkennbar(self):
        p = Mischpult()
        p.einspeisen_text("[e-1] 12:00 Codex · nachricht: hallo", rolle="ereignis")
        self.assertEqual(p.vorschau()[0]["role"], "user")
        self.assertEqual(p.nachrichten[0].rolle, "ereignis")


class BearbeitenTests(unittest.TestCase):
    def test_saetze_bearbeiten_und_entfernen(self):
        p, ids = gefuellt()
        self.assertEqual(p.saetze(p.nachrichten[0].text), ["Erster Satz.", "Zweiter Satz!", "Dritter Satz?"])
        p.satz_bearbeiten(ids[0], 1, "Neuer zweiter Satz.")
        self.assertEqual(p.nachrichten[0].text, "Erster Satz. Neuer zweiter Satz. Dritter Satz?")
        p.satz_entfernen(ids[0], 0)
        self.assertEqual(p.nachrichten[0].text, "Neuer zweiter Satz. Dritter Satz?")
        for aufruf in (lambda: p.satz_entfernen(ids[1], 0), lambda: p.satz_bearbeiten(ids[0], 9, "x"), lambda: p.satz_bearbeiten(ids[0], 0, " "), lambda: p.satz_bearbeiten("m-99", 0, "x")):
            with self.assertRaises(PultFehler):
                aufruf()

    def test_text_ersetzen_entfernen_und_validierung(self):
        p, ids = gefuellt()
        p.text_ersetzen(ids[1], "Ganz anders.")
        self.assertEqual(p.nachrichten[1].text, "Ganz anders.")
        self.assertEqual(p.entfernen([ids[1], ids[2]]), 2)
        self.assertEqual([n.id for n in p.nachrichten], [ids[0], ids[3]])
        for aufruf in (lambda: p.text_ersetzen(ids[0], ""), lambda: p.hinzufuegen("wild", "x"), lambda: p.hinzufuegen("user", ""), lambda: p.hinzufuegen("user", "a\x00b"), lambda: p.hinzufuegen("user", "x" * 200_001)):
            with self.assertRaises(PultFehler):
                aufruf()

    def test_halbieren_entfernt_die_aeltere_haelfte(self):
        p, ids = gefuellt()
        self.assertEqual(p.halbieren(), 2)
        self.assertEqual([n.id for n in p.nachrichten], ids[2:])
        self.assertEqual(p.halbieren(), 1)
        self.assertEqual(p.halbieren(), 0, "mit einer Nachricht gibt es nichts zu halbieren")
        self.assertEqual(len(p.nachrichten), 1)

    def test_jede_aenderung_ist_rueckgaengig_und_wiederholbar_und_zurueckspringen_geht_mehrere_schritte(self):
        p, ids = gefuellt()
        stand = [n.zu_dict() for n in p.nachrichten]
        p.halbieren()
        p.satz_bearbeiten(ids[2], 0, "Frage neu.") if False else p.text_ersetzen(ids[2], "Frage neu.")
        p.leeren()
        self.assertEqual(len(p.nachrichten), 0)
        self.assertTrue(p.zurueck())
        self.assertEqual(p.nachrichten[0].text, "Frage neu.")
        self.assertTrue(p.vor())
        self.assertEqual(len(p.nachrichten), 0)
        self.assertEqual(p.zurueckspringen(3), 3)
        self.assertEqual([n.zu_dict() for n in p.nachrichten], stand, "nach drei Schritten zurück ist der Anfangsstand wieder da")
        self.assertEqual(p.zurueckspringen(50), 4, "nur die vorhandenen Schritte (die vier Hinzufügungen)")
        self.assertFalse(p.zurueck())
        p.hinzufuegen("user", "neu")
        self.assertFalse(p.vor(), "nach einer neuen Änderung gibt es kein Vor mehr")

    def test_zurueck_stellt_auch_felder_feedback_und_grenzen_wieder_her(self):
        p = Mischpult()
        p.feld_setzen("A", "text", True)
        p.einmalfeedback_setzen("kurz")
        p.grenzen_setzen(100, 50)
        p.zurueck()
        self.assertEqual((p.max_zeichen, p.max_tokens), (None, None))
        p.zurueck()
        self.assertIsNone(p.einmalfeedback)
        p.zurueck()
        self.assertEqual(p.felder, [])


class EinspeisenTests(unittest.TestCase):
    def test_text_einspeisen_ohne_antwort_loest_keinen_aufruf_aus(self):
        p = Mischpult()
        mid = p.einspeisen_text("Hintergrundwissen: der Bus fährt um acht.")
        self.assertTrue(p.nachrichten[0].ohne_antwort)
        self.assertEqual(p.vorschau()[0]["content"], "Hintergrundwissen: der Bus fährt um acht.")
        self.assertEqual(mid, "m-1")

    def test_mehrere_dateien_alles_oder_nichts(self):
        p = Mischpult()
        ids = p.einspeisen_dateien([("notiz.md", "# Titel\nInhalt"), ("liste.txt", "eins\nzwei")])
        self.assertEqual(len(ids), 2)
        self.assertTrue(p.nachrichten[0].text.startswith("[Datei: notiz.md]\n# Titel"))
        self.assertTrue(all(n.ohne_antwort and n.quelle.startswith("datei:") for n in p.nachrichten))
        vorher = len(p.nachrichten)
        for kaputt in ([("bild.png", "x")], [("a.md", "ok"), ("../b.md", "x")], [("a.md", "")], [("a.md", "x" * 400_001)], [("a.md", "a\x00b")], [("a.md", "gut"), ("b.exe", "x")]):
            with self.assertRaises(PultFehler, msg=str(kaputt)[:40]):
                p.einspeisen_dateien(kaputt)
        self.assertEqual(len(p.nachrichten), vorher, "nichts wurde halb eingespeist")


class FelderFeedbackGrenzenTests(unittest.TestCase):
    def test_promptfelder_sind_sichtbar_ein_und_ausschaltbar_in_der_vorschau(self):
        p, _ = gefuellt()
        p.feld_setzen("Stil", "Antworte kurz.", True)
        p.feld_setzen("Rolle", "Du bist Prüfer.", False)
        v = p.vorschau()
        self.assertEqual((v[0], len(v)), ({"role": "system", "content": "Antworte kurz."}, 5))
        p.feld_setzen("Rolle", "Du bist Prüfer.", True)
        self.assertEqual([m["content"] for m in p.vorschau()[:2]], ["Antworte kurz.", "Du bist Prüfer."])
        self.assertTrue(p.feld_entfernen("Stil"))
        self.assertFalse(p.feld_entfernen("Stil"))
        for kaputt in (("", "x"), ("x" * 41, "x"), ("ok", 5)):
            with self.assertRaises(PultFehler):
                p.feld_setzen(*kaputt)
        for i in range(25):
            try:
                p.feld_setzen(f"f{i}", "x")
            except PultFehler as f:
                self.assertEqual(str(f), "zu_viele_felder")
                break
        else:
            self.fail("die Felder sind nicht begrenzt")

    def test_einmalfeedback_gilt_fuer_genau_eine_ausgabe(self):
        p, _ = gefuellt()
        p.einmalfeedback_setzen("Fasse dich kürzer.")
        self.assertIn("Fasse dich kürzer.", p.vorschau()[-1]["content"], "die Vorschau zeigt es, ohne es zu verbrauchen")
        self.assertIsNotNone(p.einmalfeedback)
        a1 = p.anfrage_bauen()
        self.assertTrue(a1["einmal_verbraucht"])
        self.assertIn("Fasse dich kürzer.", a1["messages"][-1]["content"])
        a2 = p.anfrage_bauen()
        self.assertFalse(a2["einmal_verbraucht"])
        self.assertNotIn("Fasse dich kürzer.", json.dumps(a2["messages"]))
        for kaputt in ("", " ", "x" * 4001, 5):
            with self.assertRaises(PultFehler):
                p.einmalfeedback_setzen(kaputt)
        p.einmalfeedback_setzen(None)

    def test_ausgabegrenzen(self):
        p = Mischpult()
        p.grenzen_setzen(500, 128)
        a = p.anfrage_bauen()
        self.assertEqual((a["max_tokens"], a["max_zeichen"]), (128, 500))
        p.grenzen_setzen(None, None)
        self.assertNotIn("max_tokens", p.anfrage_bauen())
        for kaputt in ((0, None), (None, -1), (1.5, None), (None, 2_000_000), ("5", None)):
            with self.assertRaises(PultFehler):
                p.grenzen_setzen(*kaputt)


class AnzeigeTests(unittest.TestCase):
    def test_schaetzung_und_messung_sind_getrennt_und_beschriftet(self):
        p, _ = gefuellt()
        a = p.anzeige()
        self.assertEqual((a["geschaetzt"]["art"], a["gemessen"]), ("geschaetzt", None))
        self.assertIn("nur geschätzt", a["hinweis"])
        zeichen = p.schaetzung()["zeichen"]
        p.server_gemessen({"prompt_tokens": p.schaetzung()["tokens"], "completion_tokens": 12}, zeichen)
        a = p.anzeige()
        self.assertEqual((a["gemessen"]["art"], a["serverkuerzung"], a["abweichung_prozent"]), ("gemessen", "nein", 0.0))
        self.assertIn("nahe beieinander", a["hinweis"])

    def test_eine_serverkuerzung_wird_nicht_hinter_der_anzeige_versteckt(self):
        p, _ = gefuellt()
        zeichen = p.schaetzung()["zeichen"]
        p.server_gemessen({"prompt_tokens": 5, "completion_tokens": 1}, zeichen)
        a = p.anzeige()
        self.assertEqual(a["serverkuerzung"], "vermutet")
        self.assertIn("nicht alles gesehen", a["hinweis"])
        self.assertLess(a["abweichung_prozent"], -40)
        p.server_gemessen({"prompt_tokens": p.schaetzung()["tokens"]}, zeichen, gekuerzt=True)
        a = p.anzeige()
        self.assertEqual(a["serverkuerzung"], "gemeldet")
        self.assertIn("NICHT alles gesehen", a["hinweis"])
        self.assertEqual(a["geschaetzt"]["art"], "geschaetzt")
        self.assertEqual(a["gemessen"]["art"], "gemessen", "beide Zahlen bleiben nebeneinander stehen")

    def test_unbrauchbare_serverangaben_werden_ignoriert(self):
        p, _ = gefuellt()
        for usage in (None, {}, {"prompt_tokens": "viele"}, {"prompt_tokens": True}, []):
            p.server_gemessen(usage, 100)
            self.assertIsNone(p.gemessen, usage)


class ExportTests(unittest.TestCase):
    def test_export_import_haelt_auswahl_kennungen_felder_und_grenzen_exakt(self):
        p, ids = gefuellt()
        p.nur_auswaehlen([ids[0], ids[2]])
        p.feld_setzen("Stil", "kurz", False)
        p.grenzen_setzen(300, 64)
        p.einmalfeedback_setzen("nur einmal")
        q = Mischpult.aus_export(json.loads(json.dumps(p.export())))
        self.assertEqual([(n.id, n.ausgewaehlt, n.text, n.rolle, n.quelle) for n in q.nachrichten], [(n.id, n.ausgewaehlt, n.text, n.rolle, n.quelle) for n in p.nachrichten])
        self.assertEqual(q.vorschau(), p.vorschau())
        self.assertEqual((q.felder[0].aktiv, q.max_zeichen, q.max_tokens, q.einmalfeedback), (False, 300, 64, "nur einmal"))
        neu = q.hinzufuegen("user", "danach")
        self.assertEqual(neu, "m-5", "die Zählung läuft ohne Kollision weiter")

    def test_speichern_und_neu_laden_im_sitzungsmodus_nicht_im_geistermodus(self):
        ordner = Path(tempfile.mkdtemp())
        p, ids = gefuellt()
        p.nur_auswaehlen([ids[3]])
        pfad = p.speichern(ordner)
        self.assertEqual([m["content"] for m in Mischpult.laden(pfad).vorschau()], ["Antwort zwei."], "nach dem Neuladen sind exakt die ausgewählten Inhalte aktiv")
        g = Mischpult("Geist", "geist")
        g.hinzufuegen("user", "flüchtig")
        with self.assertRaises(PultFehler) as c:
            g.speichern(ordner)
        self.assertEqual(str(c.exception), "geistermodus_speichert_nicht")
        self.assertEqual(sorted(x.name for x in ordner.iterdir()), ["Test.json"])
        with self.assertRaises(PultFehler):
            Mischpult("../boese").speichern(ordner)
        with self.assertRaises(PultFehler):
            Mischpult.laden(ordner / "gibtsnicht.json")
        with self.assertRaises(PultFehler):
            Mischpult("x", "wild")

    def test_kaputte_exporte_werden_abgelehnt_nicht_halb_geladen(self):
        gut = gefuellt()[0].export()
        for kaputt in (None, [], {}, {**gut, "schema": 2}, {**gut, "modus": "wild"}, {**gut, "nachrichten": [{"id": "m-1", "rolle": "wild", "text": "x"}]}, {**gut, "nachrichten": [{"id": "m-1", "rolle": "user", "text": ""}]},
                       {**gut, "nachrichten": [{"id": "m-1", "rolle": "user", "text": "a"}, {"id": "m-1", "rolle": "user", "text": "b"}]}, {**gut, "nachrichten": [{"rolle": "user", "text": "a"}]}):
            with self.assertRaises(PultFehler, msg=str(kaputt)[:60]):
                Mischpult.aus_export(kaputt)


if __name__ == "__main__":
    unittest.main()
