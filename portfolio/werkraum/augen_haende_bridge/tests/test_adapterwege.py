"""G09: Adapterwege je Strom — die Tabelle ist vollständig, ehrlich und gegen die echten Programme geprüft, soweit sie hier liegen."""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from types import SimpleNamespace

from augen_haende_bridge import adapterwege as aw
from augen_haende_bridge.koerper.agentenregister import STROEME, strom_von

STARTS = Path(__file__).resolve().parent.parent / "client_vps" / "starts.json"


class TabelleTests(unittest.TestCase):
    def test_jeder_start_der_liste_hat_einen_strom_mit_weg(self):
        starts = json.loads(STARTS.read_text(encoding="utf-8"))["starts"]
        for s in starts:
            strom = strom_von(s["programm"])
            gemeint = "gemini" if strom == "gemini" else strom
            self.assertIn(gemeint, aw.WEGE, f"{s['start_id']}: kein Eintrag für Strom {gemeint}")
            self.assertIn(s["start_id"], aw.WEGE[gemeint].orte, f"{s['start_id']} fehlt in den Orten von {gemeint}")

    def test_die_gewuenschten_stroeme_sind_alle_da(self):
        for strom in ("codex", "gemini", "claude", "kimi", "opencode"):
            self.assertIn(strom, aw.WEGE)

    def test_nichts_gilt_als_belegt_ohne_bemerkung_und_ungemessene_sind_offen_benannt(self):
        for strom, weg in aw.WEGE.items():
            self.assertIn(weg.pty_tippen, (aw.BELEGT, aw.ZERSTUECKELT, aw.DIALOG, aw.OFFEN), strom)
            self.assertTrue(weg.pty_bemerkung, f"{strom}: jedes Ergebnis hat eine Bemerkung (Messweise oder Grund)")
            self.assertFalse(weg.kopflos_ausgefuehrt, f"{strom}: ein kopfloser Lauf wäre eine echte Modell-Anfrage und wurde nicht gemacht")
        self.assertEqual(aw.WEGE["kimi"].pty_tippen, aw.OFFEN)

    def test_stromerkennung_und_tabelle_passen_zusammen(self):
        for programm, strom in STROEME.items():
            if strom in ("gpt", "haiku"):
                continue
            self.assertIn(strom, aw.WEGE | {"gpt": None}, programm)


class PruefTests(unittest.TestCase):
    def test_fehlendes_programm_ist_nicht_installiert_statt_erfundener_version(self):
        r = aw.pruefe("kimi", suchen=lambda n: None)
        self.assertEqual((r["status"], r["installiert"], r["version"]), (aw.FEHLT, False, None))

    def test_version_wird_aus_der_echten_ausgabe_gelesen(self):
        r = aw.pruefe("codex", suchen=lambda n: "/x/codex", ausfuehren=lambda *a, **k: SimpleNamespace(stdout="codex-cli 0.159.2\n", stderr=""))
        self.assertEqual((r["version"], r["status"]), ("0.159.2", aw.BELEGT))
        r = aw.pruefe("codex", suchen=lambda n: "/x/codex", ausfuehren=lambda *a, **k: SimpleNamespace(stdout="Unsinn", stderr=""))
        self.assertIsNone(r["version"])

    def test_ein_haengendes_programm_bringt_keinen_absturz(self):
        import subprocess

        def haengt(*a, **k):
            raise subprocess.TimeoutExpired("x", 25)

        self.assertIsNone(aw.pruefe("codex", suchen=lambda n: "/x/codex", ausfuehren=haengt)["version"])

    def test_die_echten_programme_dieses_rechners_nennen_eine_version(self):
        gefunden = 0
        for strom in ("claude", "codex", "opencode", "gemini"):
            weg = aw.WEGE[strom]
            if shutil.which(weg.programm) is None:
                continue
            r = aw.pruefe(strom)
            gefunden += 1
            self.assertTrue(r["installiert"], strom)
            self.assertIsNotNone(r["version"], f"{strom}: {weg.programm} {weg.version_argumente} nennt keine Version")
        if gefunden == 0:
            self.skipTest("keiner der Agenten liegt auf diesem Rechner")


if __name__ == "__main__":
    unittest.main()
