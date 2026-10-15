"""Linux-Fensterschicht: gleiche Schnittstelle wie Windows (Parität), echte Darstellung der Körperfenster, Backend-Wahl."""

from __future__ import annotations

import inspect
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
KOERPER = WURZEL / "src" / "augen_haende_bridge" / "koerper"


def _python(code: str, **umgebung) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "BRIDGE_BACKEND"}
    env.update({"PYTHONPATH": str(WURZEL / "src")})
    env.update(umgebung)
    return subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=120)


def _oeffentlich(klasse) -> dict[str, list[str]]:
    namen = {}
    for name, wert in inspect.getmembers(klasse):
        if name.startswith("_") or not callable(wert) or name in ("fehler",):
            continue
        try:
            namen[name] = [p for p in inspect.signature(wert).parameters if p not in ("self", "cls")]
        except (TypeError, ValueError):
            namen[name] = []
    return namen


class ParitaetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from augen_haende_bridge.koerper import fenster as windows
        from augen_haende_bridge.koerper import fenster_linux as linux

        cls.windows, cls.linux = windows, linux

    def test_klassen_haben_dieselben_oeffentlichen_methoden_mit_denselben_parametern(self):
        for name in ("Schrift", "Leinwand", "Fenster", "Anwendung"):
            win, lin = _oeffentlich(getattr(self.windows, name)), _oeffentlich(getattr(self.linux, name))
            fehlend = sorted(set(win) - set(lin))
            self.assertEqual(fehlend, [], f"{name}: unter Linux fehlen {fehlend}")
            for methode in win:
                self.assertEqual(win[methode], lin[methode], f"{name}.{methode}: Parameter weichen ab")

    def test_modulfunktion_und_konstruktoren(self):
        self.assertEqual(list(inspect.signature(self.windows.bild_ausnahme_setzen).parameters),
                         list(inspect.signature(self.linux.bild_ausnahme_setzen).parameters))
        for name in ("Schrift", "Leinwand", "Fenster", "Anwendung"):
            self.assertEqual(list(inspect.signature(getattr(self.windows, name).__init__).parameters),
                             list(inspect.signature(getattr(self.linux, name).__init__).parameters), f"Konstruktor {name}")

    def test_pixel_fenster_hat_dieselbe_schnittstelle(self):
        from augen_haende_bridge.koerper import pixel_fenster as windows
        win, lin = _oeffentlich(windows.PixelFenster), _oeffentlich(self.linux.PixelFenster)
        self.assertEqual(sorted(set(win) - set(lin)), [])
        for methode in ("setze_rgba", "verschiebe"):
            self.assertEqual(win[methode], lin[methode])

    def test_alle_direkten_windows_aufrufe_der_fenster_haben_eine_linux_entsprechung(self):
        from augen_haende_bridge.koerper import win32_linux

        nur_windows = {"notaus.py", "selbsttest_windows.py", "fenster.py", "win32.py", "pixel_fenster.py", "win32_linux.py", "fenster_linux.py"}
        # Funktionen, die der Körper nur in Windows-eigenen Teilen ruft (globaler Tastaturhaken, Zwischenablage-Speicher, Menü, Aufnahme-Selbsttest)
        ausnahmen = {"menue.py"}
        fehlend = []
        for datei in KOERPER.glob("*.py"):
            if datei.name in nur_windows or datei.name in ausnahmen:
                continue
            for tabelle, name in re.findall(r"\bw\.(user32|gdi32|kernel32)\.([A-Za-z0-9_]+)", datei.read_text(encoding="utf-8")):
                if getattr(getattr(win32_linux, tabelle), name) is None:
                    fehlend.append(f"{datei.name}: {tabelle}.{name}")
        self.assertEqual(sorted(set(fehlend)), [], "Diese Windows-Aufrufe der Körperfenster fehlen in win32_linux.py")

    def test_menue_hat_die_gleichen_funktionen(self):
        from augen_haende_bridge.koerper import menue, menue_linux

        for name in ("zeige_menue", "text_aus_zwischenablage", "text_in_zwischenablage"):
            self.assertEqual(list(inspect.signature(getattr(menue, name)).parameters)[:5],
                             list(inspect.signature(getattr(menue_linux, name)).parameters)[:5], name)


@unittest.skipUnless(shutil.which("xvfb-run"), "xvfb-run fehlt")
class DarstellungTests(unittest.TestCase):
    def test_alle_koerperfenster_bauen_zeichnen_und_lassen_sich_bedienen(self):
        env = {**os.environ, "PYTHONPATH": str(WURZEL / "src"), "BRIDGE_TEST_XVFB": "1"}
        env.pop("BRIDGE_BACKEND", None)
        lauf = subprocess.run(["xvfb-run", "-a", "-s", "-screen 0 1280x800x24", sys.executable, "-u",
                               str(WURZEL / "probes" / "linux_koerper_zeichnen.py")], env=env, capture_output=True, text=True, timeout=150)
        self.assertIn("linux koerper probe ok", lauf.stdout, lauf.stdout[-1500:] + lauf.stderr[-1500:])
        for fenster in ("raute", "terminal", "chat", "regie", "kamera", "bild_element", "eingabe", "banner", "ticker", "zeichenflaeche", "werkzeugleiste"):
            self.assertIn(fenster, lauf.stdout)

    def test_gleiche_zeichenlogik_gleiche_masse_wie_unter_windows(self):
        """Die Regie-Leiste und die Werkzeugleiste haben unter Linux dieselbe Größe, weil Layout und Schriftmaße aus demselben Code kommen (die Werkzeugleiste
        misst die Schrift; Liberation/Noto haben ähnliche, nicht gleiche Breiten wie Segoe UI — deshalb Spielraum)."""
        from augen_haende_bridge.koerper import regie_fenster

        env = {**os.environ, "PYTHONPATH": str(WURZEL / "src")}
        env.pop("BRIDGE_BACKEND", None)
        lauf = subprocess.run(["xvfb-run", "-a", sys.executable, "-c",
                               "import os; os.environ['BRIDGE_BACKEND']='linux'\n"
                               "from augen_haende_bridge.koerper.fenster import Anwendung\n"
                               "from augen_haende_bridge.koerper.regie_fenster import RegieFenster\n"
                               "a=Anwendung(); a.starten(); r=RegieFenster(10,10); a.pumpen(100); print(r.clientgroesse())"],
                              env=env, capture_output=True, text=True, timeout=60)
        self.assertIn(f"({regie_fenster.BREITE}, {regie_fenster.HOEHE})", lauf.stdout, lauf.stderr[-800:])


class BackendWahlTests(unittest.TestCase):
    PRUEFUNG = "from augen_haende_bridge.koerper import fenster; import sys; print(fenster.Fenster.__module__.rsplit('.',1)[-1], 'gi' in sys.modules)"

    def test_ohne_variable_bleibt_es_windows_und_gtk_wird_nicht_geladen(self):
        lauf = _python(self.PRUEFUNG)
        self.assertEqual(lauf.stdout.split(), ["fenster", "False"], lauf.stderr[-500:])

    def test_windows_ausdruecklich(self):
        self.assertEqual(_python(self.PRUEFUNG, BRIDGE_BACKEND="windows").stdout.split()[0], "fenster")

    def test_linux_waehlt_die_gtk_fassung(self):
        lauf = _python(self.PRUEFUNG, BRIDGE_BACKEND="linux")
        self.assertEqual(lauf.stdout.split(), ["fenster_linux", "True"], lauf.stderr[-500:])

    def test_unbekannter_wert_faellt_auf_windows_zurueck(self):
        self.assertEqual(_python(self.PRUEFUNG, BRIDGE_BACKEND="beos").stdout.split()[0], "fenster")

    def test_linux_ersetzt_auch_pixel_fenster_und_menues(self):
        lauf = _python("from augen_haende_bridge.koerper import pixel_fenster, menue; print(pixel_fenster.PixelFenster.__module__.rsplit('.',1)[-1], menue.zeige_menue.__module__.rsplit('.',1)[-1])",
                       BRIDGE_BACKEND="linux")
        self.assertEqual(lauf.stdout.split(), ["fenster_linux", "menue_linux"], lauf.stderr[-500:])

    def test_linux_ohne_anzeige_laesst_sich_importieren_aber_nicht_bauen(self):
        env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY")}
        lauf = subprocess.run([sys.executable, "-c",
                               "import os; os.environ['BRIDGE_BACKEND']='linux'\nfrom augen_haende_bridge.koerper.fenster import Fenster\nprint('import ok')"],
                              env={**env, "PYTHONPATH": str(WURZEL / "src")}, capture_output=True, text=True, timeout=60)
        self.assertIn("import ok", lauf.stdout, lauf.stderr[-500:])


if __name__ == "__main__":
    unittest.main()
