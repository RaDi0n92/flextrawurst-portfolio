"""G06.7: Bedienungshilfen — AT-SPI gegen ein echtes GTK-Programm, UI Automation gegen ein nachgebautes Objektmodell."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from augen_haende_bridge.koerper import uia

WURZEL = Path(__file__).resolve().parent.parent
DISPLAY = bool(os.environ.get("DISPLAY")) and os.environ.get("BRIDGE_TEST_XVFB") == "1"
BRAUCHBAR = DISPLAY and shutil.which("dbus-run-session") and Path("/usr/libexec/at-spi-bus-launcher").exists()
_zwischen: dict[str, dict] = {}


def lauf(fall: str) -> dict:
    """Ein Fall im eigenen D-Bus (die Sitzung des Tests bleibt unberührt); das Ergebnis wird je Fall nur einmal geholt."""
    if fall not in _zwischen:
        ergebnis = subprocess.run(["dbus-run-session", "--", sys.executable, str(WURZEL / "tests" / "helfer_atspi_lauf.py"), fall], capture_output=True, text=True, timeout=120)
        zeilen = [z for z in ergebnis.stdout.splitlines() if z.startswith("{")]
        if not zeilen:
            raise AssertionError(ergebnis.stdout[-800:] + ergebnis.stderr[-800:])
        _zwischen[fall] = json.loads(zeilen[-1])
    return _zwischen[fall]


@unittest.skipUnless(BRAUCHBAR, "kein privater Xvfb (BRIDGE_TEST_XVFB=1), dbus-run-session oder AT-SPI fehlt")
class AtspiLesenTests(unittest.TestCase):
    def test_der_baum_nennt_schaltflaeche_feld_und_beschriftung_mit_rolle_name_und_lage(self):
        r = lauf("lesen")
        self.assertTrue(r["verfuegbar"] and r["anwendung_gefunden"])
        self.assertEqual(r["status"], "ok")
        self.assertGreaterEqual(r["anzahl"], 5)
        self.assertTrue({"button", "text", "label", "frame"} <= set(r["rollen"]), r["rollen"])
        for name in ("knopf", "feld", "etikett"):
            links, oben, rechts, unten = r[name]["rect"]
            self.assertTrue(rechts > links and unten > oben, f"{name}: echte Lage")
        self.assertLess(r["etikett"]["rect"][1], r["knopf"]["rect"][1], "die Beschriftung steht über dem Knopf (Reihenfolge der Lage stimmt)")
        self.assertLess(r["knopf"]["rect"][1], r["feld"]["rect"][1])


@unittest.skipUnless(BRAUCHBAR, "kein privater Xvfb (BRIDGE_TEST_XVFB=1), dbus-run-session oder AT-SPI fehlt")
class AtspiBedienenTests(unittest.TestCase):
    def test_knopf_ausloesen_und_feld_setzen_mit_ruecklese(self):
        r = lauf("bedienen")
        self.assertEqual(r["klick_knopf"], [True, True])
        self.assertTrue(r["nach_klick"].startswith("2|"), "das Programm hat zweimal gezählt (Rücklese aus dem Programm selbst)")
        self.assertTrue(r["text_setzen"])
        self.assertEqual(r["nach_text"], "2|Grüße 🌍")
        self.assertIn("klick", r["knopf"]["faehig"])
        self.assertIn("text_setzen", r["feld"]["faehig"])

    def test_ein_knoten_ohne_die_faehigkeit_loest_nichts_aus(self):
        r = lauf("bedienen")
        self.assertEqual(r["etikett"]["faehig"], [])
        self.assertFalse(r["klick_etikett"])
        self.assertFalse(r["text_etikett"])
        self.assertEqual(r["nach_verweigert"], "2|Grüße 🌍", "nach den verweigerten Aktionen ist der Stand unverändert")


@unittest.skipUnless(BRAUCHBAR, "kein privater Xvfb (BRIDGE_TEST_XVFB=1), dbus-run-session oder AT-SPI fehlt")
class OhneBaumTests(unittest.TestCase):
    def test_ein_programm_ohne_bedienungshilfen_ist_kein_baum_und_kein_leerer_erfolg(self):
        r = lauf("ohne_baum")
        self.assertNotIn("NurFlaeche", r["anwendungen"])
        self.assertEqual(r["baum"]["status"], "kein_baum")
        self.assertFalse(r["baum"]["wurzel"])
        self.assertTrue(r["baum"]["grund"])

    def test_ohne_atspi_bus_ist_es_nicht_verfuegbar(self):
        q = uia.AtspiQuelle()
        q._atspi = None
        self.assertFalse(q.verfuegbar())
        self.assertEqual(q.baum("x").status, "nicht_verfuegbar")


# ---- Windows: nachgebautes Objektmodell mit denselben Eigenschaften wie _ComElement ------------------------------------------
class Falsch:
    def __init__(self, name, rolle="window", pid=1, wert="", invoke=False, value=False, kinder=(), rect=(0, 0, 100, 40), zustaende=("enabled",)):
        self.name, self.rolle, self.process_id, self.wert, self.rect, self.zustaende = name, rolle, pid, wert, rect, zustaende
        self.hat_invoke, self.hat_value, self._kinder = invoke, value, list(kinder)
        self.aufgerufen = 0

    def kinder(self):
        return list(self._kinder)

    def invoke(self):
        self.aufgerufen += 1
        return True

    def wert_setzen(self, text):
        self.wert = text
        return True


class FalschesModell:
    def __init__(self, *apps):
        self.apps = apps

    def GetRootElement(self):
        return Falsch("Desktop", "pane", 0, kinder=self.apps)


class WindowsUiaTests(unittest.TestCase):
    def setUp(self):
        self.knopf = Falsch("Speichern", "button", 7, invoke=True, rect=(10, 10, 90, 30))
        self.feld = Falsch("Name", "edit", 7, wert="alt", value=True, rect=(10, 40, 200, 60))
        self.etikett = Falsch("Hinweis", "text", 7, rect=(10, 70, 200, 90))
        self.app = Falsch("Editor", "window", 7, kinder=[Falsch("Fenster", "pane", 7, kinder=[self.knopf, self.feld, self.etikett])])
        self.q = uia.WindowsUiaQuelle(FalschesModell(self.app, Falsch("Leer", "window", 9)))

    def test_der_baum_hat_dieselbe_form_wie_unter_linux(self):
        self.assertTrue(self.q.verfuegbar())
        self.assertEqual(self.q.anwendungen(), [("Editor", 7), ("Leer", 9)])
        b = self.q.baum("Editor")
        self.assertEqual((b.status, b.anzahl), ("ok", 5))
        knopf, feld, etikett = (b.wurzel.finde(n) for n in ("button", "edit", "text"))
        self.assertEqual((knopf.name, knopf.rect, knopf.faehigkeiten, knopf.quelle), ("Speichern", (10, 10, 90, 30), ("klick",), "uia"))
        self.assertEqual((feld.wert, feld.faehigkeiten), ("alt", ("text_setzen",)))
        self.assertEqual(etikett.faehigkeiten, ())
        self.assertEqual(knopf.pfad, (0, 0))

    def test_aktionen_nur_mit_faehigkeit_und_mit_ruecklese(self):
        b = self.q.baum(7)
        knopf, feld, etikett = (b.wurzel.finde(n) for n in ("button", "edit", "text"))
        self.assertTrue(self.q.klick(knopf))
        self.assertEqual(self.knopf.aufgerufen, 1)
        self.assertTrue(self.q.text_setzen(feld, "neu"))
        self.assertEqual(self.feld.wert, "neu")
        self.assertFalse(self.q.klick(etikett))
        self.assertFalse(self.q.text_setzen(etikett, "x"))
        self.assertFalse(self.q.klick(feld), "ein Feld ohne Invoke-Muster wird nicht angeklickt")
        self.assertEqual((self.etikett.wert, self.etikett.aufgerufen), ("", 0))

    def test_ein_programm_ohne_elemente_ist_kein_baum(self):
        b = self.q.baum("Leer")
        self.assertEqual((b.status, b.wurzel is not None), ("kein_baum", True))
        self.assertEqual(self.q.baum("Gibt es nicht").status, "kein_baum")

    def test_ohne_die_bibliothek_ist_es_nicht_verfuegbar(self):
        q = uia.WindowsUiaQuelle()  # hier gibt es kein comtypes/UIAutomationCore
        self.assertFalse(q.verfuegbar())
        b = q.baum("x")
        self.assertEqual(b.status, "nicht_verfuegbar")
        self.assertIn("nicht verfügbar", b.grund)

    def test_die_grenzen_gelten(self):
        tief = Falsch("blatt", "text", 7)
        for i in range(uia.MAX_TIEFE + 10):
            tief = Falsch(f"ebene{i}", "pane", 7, kinder=[tief])
        b = uia.WindowsUiaQuelle(FalschesModell(tief)).baum(7)
        self.assertEqual(b.status, "ok")
        self.assertLessEqual(max(len(k.pfad) for k in b.wurzel.alle()), uia.MAX_TIEFE + 1)


if __name__ == "__main__":
    unittest.main()
