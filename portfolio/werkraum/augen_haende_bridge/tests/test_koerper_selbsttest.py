"""Selbsttest-Gerüst: Ausführung, Bericht, Kindprozess für Kamera/Mikrofon (Absturz, Hänger, Erfolg)."""

from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from augen_haende_bridge.koerper import selbsttest as st


class AusfuehrenTests(unittest.TestCase):
    def test_ergebnisse_in_reihenfolge_mit_dauer(self):
        zeit = iter([0.0, 0.5, 1.0, 1.25])
        e = st.ausfuehren([("a", lambda: (st.OK, "gut")), ("b", lambda: (st.WARNUNG, "na ja"))], uhr=lambda: next(zeit))
        self.assertEqual([(x.name, x.status, x.dauer_ms) for x in e], [("a", "ok", 500), ("b", "warnung", 250)])

    def test_ausnahme_ist_ein_befund_und_bricht_nicht_ab(self):
        def kaputt():
            raise RuntimeError("boom")

        e = st.ausfuehren([("x", kaputt), ("y", lambda: (st.OK, "ok"))])
        self.assertEqual((e[0].status, e[1].status), ("fehler", "ok"))
        self.assertIn("boom", e[0].detail)

    def test_zusammenfassung_zaehlt_alle_arten(self):
        e = st.ausfuehren([("a", lambda: (st.OK, "")), ("b", lambda: (st.OK, "")), ("c", lambda: (st.FEHLER, "")), ("d", lambda: (st.UNBEKANNT, ""))])
        self.assertEqual(st.zusammenfassung(e), {"ok": 2, "warnung": 0, "fehler": 1, "unbekannt": 1})


class BerichtTests(unittest.TestCase):
    def test_text_und_json_bericht(self):
        e = st.ausfuehren([("Durchklicken", lambda: (st.OK, "alles gut")), ("Kamera", lambda: (st.FEHLER, "abgestürzt"))])
        kopf = {"version": "1.2.3", "system": "Windows 11", "zeit": "2026-09-30 12:00:00"}
        text = st.als_text(e, kopf)
        self.assertIn("[ OK ] Durchklicken", text)
        self.assertIn("[FEHL] Kamera", text)
        self.assertIn("Zusammenfassung: 1 ok, 0 Warnung(en), 1 Fehler, 0 unbekannt", text)
        with tempfile.TemporaryDirectory() as temp:
            json_pfad, text_pfad = st.bericht_schreiben(e, kopf, Path(temp) / "unter")
            daten = json.loads(json_pfad.read_text(encoding="utf-8"))
            self.assertEqual(daten["zusammenfassung"]["fehler"], 1)
            self.assertEqual(daten["ergebnisse"][1]["name"], "Kamera")
            self.assertEqual(text_pfad.read_text(encoding="utf-8"), text)

    def test_kopf(self):
        k = st.kopf_bauen("9.9")
        self.assertEqual(k["version"], "9.9")
        self.assertIn("python", k)


class GeraetTests(unittest.TestCase):
    def skript(self, inhalt: str) -> list[str]:
        pfad = Path(tempfile.mkdtemp()) / "kind.py"
        pfad.write_text(textwrap.dedent(inhalt), encoding="utf-8")
        return [sys.executable, str(pfad)]

    def test_erfolg_des_kindes_wird_uebernommen(self):
        basis = self.skript('''
            import json, sys
            open(sys.argv[3], "w").write(json.dumps({"status": "ok", "detail": "1 Kamera"}))
        ''')
        self.assertEqual(st.geraet_im_kindprozess("kamera", basis), ("ok", "1 Kamera"))

    def test_absturz_des_kindes_ist_ein_befund_mit_exitcode(self):
        basis = self.skript("import os; os._exit(3)")
        status, detail = st.geraet_im_kindprozess("mikrofon", basis)
        self.assertEqual(status, "fehler")
        self.assertIn("Exitcode 3", detail)

    def test_haengendes_kind_wird_abgebrochen(self):
        basis = self.skript("import time; time.sleep(30)")
        status, detail = st.geraet_im_kindprozess("kamera", basis, timeout_s=0.5)
        self.assertEqual(status, "fehler")
        self.assertIn("Zeitüberschreitung", detail)

    def test_zeitueberschreitung_nennt_den_zwischenstand(self):
        basis = self.skript('''
            import json, sys, time
            open(sys.argv[3], "w").write(json.dumps({"status": "teil", "detail": "Mikro A: 12"}))
            time.sleep(30)
        ''')
        status, detail = st.geraet_im_kindprozess("mikrofon", basis, timeout_s=1.5)
        self.assertEqual(status, "fehler")
        self.assertIn("Zeitüberschreitung", detail)
        self.assertIn("Zwischenstand: Mikro A: 12", detail)

    def test_abgebrochenes_kind_mit_zwischenstand_ist_ein_fehler_mit_zwischenstand(self):
        basis = self.skript('''
            import json, os, sys
            open(sys.argv[3], "w").write(json.dumps({"status": "teil", "detail": "Mikro A: 12"}))
            os._exit(1)
        ''')
        status, detail = st.geraet_im_kindprozess("mikrofon", basis)
        self.assertEqual(status, "fehler")
        self.assertIn("Mikro A: 12", detail)

    def test_standard_timeouts_reichen_fuer_langsame_geraete(self):
        self.assertGreaterEqual(st.GERAET_TIMEOUT_S["kamera"], 90)
        self.assertGreaterEqual(st.GERAET_TIMEOUT_S["mikrofon"], 90)

    def test_nicht_startbares_kind_ist_unbekannt(self):
        status, detail = st.geraet_im_kindprozess("kamera", ["/gibt/es/nicht"])
        self.assertEqual(status, "unbekannt")

    def test_kaputte_ergebnisdatei_zaehlt_als_ohne_ergebnis(self):
        basis = self.skript('import sys; open(sys.argv[3], "w").write("{kaputt")')
        self.assertEqual(st.geraet_im_kindprozess("kamera", basis)[0], "fehler")

    def test_geraet_pruefen_schreibt_einen_fehler_statt_zu_werfen(self):
        with tempfile.TemporaryDirectory() as temp:
            ziel = Path(temp) / "k.json"
            st.geraet_pruefen("unsinn", ziel)
            self.assertEqual(json.loads(ziel.read_text())["status"], "fehler")


class KandidatenTests(unittest.TestCase):
    def test_erste_freie_kombination_wird_genommen_die_belegten_werden_aufgezaehlt(self):
        from augen_haende_bridge.koerper.selbsttest_windows import erste_anmeldbare
        from augen_haende_bridge.koerper.tastenkombi import Kombination

        belegt = {(0, 0x7C), (0, 0x7D)}
        gui = type("G", (), {"hotkey_setzen": lambda self, n, m, v, a: (m, v) not in belegt})()
        kombi, liste = erste_anmeldbare(gui, "x", [Kombination(0, 0x7C), Kombination(0, 0x7D), Kombination(0, 0x7E)], lambda: None)
        self.assertEqual((kombi.text(), liste), ("F15", ["F13", "F14"]))

    def test_sind_alle_belegt_kommt_none(self):
        from augen_haende_bridge.koerper.selbsttest_windows import erste_anmeldbare
        from augen_haende_bridge.koerper.tastenkombi import Kombination

        gui = type("G", (), {"hotkey_setzen": lambda self, n, m, v, a: False})()
        kombi, liste = erste_anmeldbare(gui, "x", [Kombination(0, 0x7C)], lambda: None)
        self.assertIsNone(kombi)
        self.assertEqual(liste, ["F13"])


class AuswahlTests(unittest.TestCase):
    LISTE = [("Durchklicken: Klicks", lambda: None), ("Kamera (eigener Prozess)", lambda: None),
             ("Mikrofon (eigener Prozess)", lambda: None), ("Aufräumen", lambda: None)]

    def namen(self, nur, ohne):
        from augen_haende_bridge.koerper.selbsttest_windows import auswaehlen
        return [n for n, _ in auswaehlen(self.LISTE, nur, ohne)]

    def test_ohne_angabe_laufen_alle(self):
        self.assertEqual(len(self.namen([], [])), 4)

    def test_nur_grenzt_ein_und_aufraeumen_bleibt(self):
        self.assertEqual(self.namen(["kamera"], []), ["Kamera (eigener Prozess)", "Aufräumen"])

    def test_ohne_schliesst_aus_und_aufraeumen_bleibt(self):
        self.assertEqual(self.namen([], ["Kamera", "mikro"]), ["Durchklicken: Klicks", "Aufräumen"])

    def test_aufraeumen_laesst_sich_nicht_abwaehlen(self):
        self.assertIn("Aufräumen", self.namen([], ["Aufräumen"]))


if __name__ == "__main__":
    unittest.main()
