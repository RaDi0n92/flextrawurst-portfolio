"""Nachprüfung (Netzrecherche 2026-10-02): Wayland wird erkannt und ehrlich als Grenze benannt; der Windows-Fokuswechsel läuft über den AttachThreadInput-Weg und ist unter Wine geprüft."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"


@unittest.skipUnless(DISPLAY, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class SitzungTests(unittest.TestCase):
    def zeile(self, **umgebung):
        from augen_haende_bridge.koerper import selbsttest_linux as st

        with mock.patch.dict(os.environ, umgebung, clear=False):
            for k in ("XDG_SESSION_TYPE", "WAYLAND_DISPLAY"):
                if k not in umgebung:
                    os.environ.pop(k, None)
            zeilen = st.pruefungen("kde1", "ws://127.0.0.1:1", None)
        return next(z for z in zeilen if z[1] == "Sitzung")

    def test_x11_ist_ok(self):
        self.assertEqual(self.zeile(XDG_SESSION_TYPE="x11")[0], "ok")
        self.assertEqual(self.zeile()[0], "ok")

    def test_wayland_mit_xwayland_ist_ein_hinweis_mit_grenze(self):
        z = self.zeile(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0")
        self.assertEqual(z[0], "Hinweis")
        self.assertIn("nur X11-Fenster", z[2])

    def test_reines_wayland_ist_fehlt_mit_dem_ausweg_im_text(self):
        with mock.patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"}):
            display = os.environ.pop("DISPLAY")
            try:
                from augen_haende_bridge.koerper import selbsttest_linux as st

                # ohne DISPLAY schlagen die X11-Prüfungen selbst fehl; die Sitzungszeile muss trotzdem erklären
                zeilen = st.pruefungen("kde1", "ws://127.0.0.1:1", None)
            finally:
                os.environ["DISPLAY"] = display
        z = next(z for z in zeilen if z[1] == "Sitzung")
        self.assertEqual(z[0], "fehlt")
        self.assertIn("libei", z[2])
        self.assertIn("PipeWire", z[2])


@unittest.skipUnless(shutil.which("wine") and Path("/config/wine-bridge-build/prefix").exists(), "Wine fehlt")
class FokusTests(unittest.TestCase):
    def test_fokus_geben_bringt_das_fenster_nach_vorn_unter_wine(self):
        env = {**os.environ, "PYTHONPATH": str(WURZEL / "src"), "WINEPREFIX": "/config/wine-bridge-build/prefix", "WINEARCH": "win64", "WINEDEBUG": "-all", "WINEDLLOVERRIDES": "mscoree,mshtml="}
        lauf = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1280x800x24", "wine", "C:\\Python313\\python.exe", str(WURZEL / "probes" / "haende_wine.py")], env=env, capture_output=True, text=True, timeout=240)
        zeile = next(z for z in lauf.stdout.splitlines() if z.startswith("{"))
        r = json.loads(zeile)
        self.assertTrue(r["fokus"]["ergebnis"] and r["fokus"]["vorn_ist_ziel"], r["fokus"])

    def test_der_attach_weg_ist_im_code_und_loest_immer_wieder(self):
        quelle = (WURZEL / "src/augen_haende_bridge/koerper/eingabe_adapter.py").read_text(encoding="utf-8")
        a = quelle.index("def fokus_geben(self, kennung: int) -> bool:\n        \"\"\"Windows verweigert")
        block = quelle[a:a + 2200]
        self.assertIn("AttachThreadInput(eigener, fremder, 1)", block)
        self.assertIn("finally:", block)
        self.assertIn("AttachThreadInput(eigener, fremder, 0)", block, "die Warteschlange wird in jedem Fall wieder gelöst")


if __name__ == "__main__":
    unittest.main()
