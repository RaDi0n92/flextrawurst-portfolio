"""Ein echtes Ampel-Fenster in einem privaten Xvfb: Klick auf eine Lampe, Ziehen, Rechtsklick (BRIDGE_TEST_XVFB=1, nie auf Daniels Desktop)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
LAUF = os.environ.get("BRIDGE_TEST_XVFB") == "1"
DISPLAY = ":87"


def xdo(*args) -> str:
    env = {**os.environ, "DISPLAY": DISPLAY}
    return subprocess.run(["xdotool", *map(str, args)], env=env, capture_output=True, text=True, timeout=10).stdout


@unittest.skipUnless(LAUF, "kein privater Xvfb (BRIDGE_TEST_XVFB=1 fehlt)")
class BedienungTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xvfb = subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", "800x600x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)
        cls.ordner = tempfile.TemporaryDirectory()
        cls.stand_datei = Path(cls.ordner.name) / "stand.json"
        env = {**os.environ, "DISPLAY": DISPLAY, "BRIDGE_BACKEND": "linux", "PYTHONPATH": f"{WURZEL / 'src'}:{WURZEL}"}
        cls.taste_datei = Path(cls.ordner.name) / "taste.txt"
        cls.taste_datei.write_text("1", encoding="utf-8")  # Bedientaste gehalten: das Fenster nimmt Klicks an
        cls.kind = subprocess.Popen([sys.executable, str(WURZEL / "tests" / "helfer_gtk_ampel.py"), str(cls.stand_datei), str(cls.taste_datei)], env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cls.stand = cls._warte(lambda s: s.get("rechteck") and s.get("lampen") == 3, 10)  # erst wenn die drei Lampen berechnet sind
        assert cls.stand, "das Ampel-Fenster ist nicht gestartet: " + (cls.kind.stdout.read(2000).decode("utf-8", "replace") if cls.kind.poll() is not None else "")

    @classmethod
    def tearDownClass(cls):
        cls.kind.terminate()
        cls.xvfb.terminate()
        cls.ordner.cleanup()

    @classmethod
    def _stand(cls) -> dict:
        try:
            return json.loads(cls.stand_datei.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    @classmethod
    def _warte(cls, bedingung, sekunden: float = 4.0):
        ende = time.time() + sekunden
        while time.time() < ende:
            s = cls._stand()
            if bedingung(s):
                return s
            time.sleep(0.15)
        return None

    def lampe(self, i: int) -> tuple[int, int]:
        l, o, r, u = self._stand()["rechteck"]
        b, h = r - l, u - o
        return l + (2 * i + 1) * b // 6, o + h // 2

    def test_klick_auf_die_rote_lampe_loest_ihre_behebung_aus(self):
        x, y = self.lampe(0)
        xdo("mousemove", x, y)
        xdo("click", 1)
        s = self._warte(lambda s: ["Testagent", "strom_neu"] in s["aktionen"])
        self.assertIsNotNone(s, f"der Klick kam nicht an: {self._stand()}")

    def test_klick_auf_eine_gruene_lampe_erklaert_die_gruppe(self):
        x, y = self.lampe(1)
        xdo("mousemove", x, y)
        xdo("click", 1)
        s = self._warte(lambda s: ["Testagent", "gruppe:haende"] in s["aktionen"])
        self.assertIsNotNone(s, f"der Klick kam nicht an: {self._stand()}")

    def test_ziehen_verschiebt_das_fenster_und_loest_keine_aktion_aus(self):
        vorher = self._stand()
        aktionen_vorher = len(vorher["aktionen"])
        l, o, r, u = vorher["rechteck"]
        x, y = l + 20, o + 10
        xdo("mousemove", x, y)
        xdo("mousedown", 1)
        for schritt in range(1, 9):
            xdo("mousemove", x + schritt * 15, y + schritt * 10)
            time.sleep(0.03)
        xdo("mouseup", 1)
        s = self._warte(lambda s: s["rechteck"][0] != l or s["rechteck"][1] != o)
        self.assertIsNotNone(s, "das Fenster hat sich nicht bewegt")
        self.assertGreater(s["rechteck"][0] - l, 40)
        self.assertEqual(len(s["aktionen"]), aktionen_vorher, "ein Zug darf keine Lampe auslösen")

    def test_rechtsklick_ruft_das_menue_auf(self):
        x, y = self.lampe(2)
        xdo("mousemove", x, y)
        xdo("click", 3)
        s = self._warte(lambda s: s["menues"])
        self.assertIsNotNone(s, "kein Menü")
        self.assertEqual(s["menues"][-1][0], "Testagent")


    def taste(self, gehalten: bool) -> None:
        self.taste_datei.write_text("1" if gehalten else "0", encoding="utf-8")
        time.sleep(0.5)  # der Durchklick-Verwalter schaltet im 50-ms-Takt

    def test_ohne_bedientaste_geht_der_klick_durch_das_fenster_und_mit_bedientaste_wirkt_er(self):
        x, y = self.lampe(0)
        vorher = len(self._stand()["aktionen"])
        self.taste(False)
        try:
            xdo("mousemove", x, y)
            xdo("click", 1)
            time.sleep(0.8)
            self.assertEqual(len(self._stand()["aktionen"]), vorher, "ohne Bedientaste muss der Klick durchgehen")
            self.taste(True)
            xdo("mousemove", x + 1, y)
            xdo("click", 1)
            s = self._warte(lambda s: len(s["aktionen"]) > vorher)
            self.assertIsNotNone(s, "mit Bedientaste muss der Klick wirken")
        finally:
            self.taste(True)

    def test_menueauswahl_ist_vom_menue_aufruf_getrennt_der_rechtsklick_liefert_die_bildschirmposition(self):
        x, y = self.lampe(2)
        xdo("mousemove", x, y)
        xdo("click", 3)
        s = self._warte(lambda s: s["menues"])
        _agent, mx, my = s["menues"][-1]
        self.assertAlmostEqual(mx, x, delta=3)
        self.assertAlmostEqual(my, y, delta=3)


if __name__ == "__main__":
    unittest.main()
