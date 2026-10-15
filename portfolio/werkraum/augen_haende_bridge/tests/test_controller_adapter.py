"""G10: virtuelle Controller — strenge Aktionen, dieselben Sperren wie die Hände, nach jedem Auftrag alles losgelassen, Not-Aus und Übernahme brechen ab; echtes uinput-Gerät (Linux) wird angelegt und wieder entfernt."""

from __future__ import annotations

import glob
import os
import threading
import time
import unittest

from augen_haende_bridge.koerper import steuerprofil
from augen_haende_bridge.koerper.controller_adapter import (MAX_HALTEN_MS, AttrappenBackend, ControllerAktion, ControllerEngine, UinputBackend, VigemBackend)

FREI = dict(lease_grund="", haende_erlaubt=True, profil_erlaubt=True)


def knopf(name="a", dauer=40, index=0):
    return ControllerAktion("knopf", index, name, dauer_ms=dauer)


class AktionTests(unittest.TestCase):
    def test_gueltige_aktionen_und_umlauf(self):
        for d in ({"art": "controller", "befehl": "knopf", "name": "a"}, {"art": "controller", "befehl": "stick", "name": "links", "wert": [0.5, -1]}, {"art": "controller", "befehl": "trigger", "name": "rechts", "wert": [1, 0]},
                  {"art": "controller", "befehl": "loslassen", "index": 3}, {"art": "controller", "befehl": "knopf", "name": "hoch", "index": 2, "dauer_ms": MAX_HALTEN_MS}):
            a = ControllerAktion.aus_dict(d)
            self.assertIsNotNone(a, d)
            self.assertEqual(ControllerAktion.aus_dict(a.zu_dict()), a)

    def test_ungueltiges_wird_abgelehnt(self):
        schlecht = [None, [], {}, {"art": "klick"}, {"art": "controller"}, {"art": "controller", "befehl": "knopf"}, {"art": "controller", "befehl": "knopf", "name": "z"}, {"art": "controller", "befehl": "knopf", "name": "a", "index": 4},
                    {"art": "controller", "befehl": "knopf", "name": "a", "index": -1}, {"art": "controller", "befehl": "knopf", "name": "a", "index": True}, {"art": "controller", "befehl": "knopf", "name": "a", "dauer_ms": 10},
                    {"art": "controller", "befehl": "knopf", "name": "a", "dauer_ms": MAX_HALTEN_MS + 1}, {"art": "controller", "befehl": "knopf", "name": "a", "extra": 1},
                    {"art": "controller", "befehl": "stick", "name": "mitte", "wert": [0, 0]}, {"art": "controller", "befehl": "stick", "name": "links", "wert": [2, 0]}, {"art": "controller", "befehl": "stick", "name": "links", "wert": [0]},
                    {"art": "controller", "befehl": "stick", "name": "links", "wert": ["a", 0]}, {"art": "controller", "befehl": "stick", "name": "links", "wert": [True, 0]},
                    {"art": "controller", "befehl": "trigger", "name": "links", "wert": [-0.1, 0]}, {"art": "controller", "befehl": "trigger", "name": "links", "wert": [1.1, 0]}, {"art": "controller", "befehl": "wild", "name": "a"}]
        for d in schlecht:
            self.assertIsNone(ControllerAktion.aus_dict(d), d)


class EngineTests(unittest.TestCase):
    def engine(self, **kw):
        b = AttrappenBackend()
        return b, ControllerEngine(b, schlafen=lambda s: time.sleep(min(s, 0.005)), **kw)

    def test_knopf_wird_gedrueckt_und_danach_losgelassen(self):
        b, e = self.engine()
        r = e.ausfuehren("c-1", knopf("a"), **FREI)
        self.assertEqual((r.status, r.delivered), ("ausgefuehrt", 1))
        self.assertEqual(b.ereignisse, [("knopf", 0, "a", True), ("knopf", 0, "a", False)])
        self.assertEqual(b.zustand[0]["knoepfe"], set())

    def test_stick_und_trigger_kehren_in_die_mitte_zurueck(self):
        b, e = self.engine()
        e.ausfuehren("c-2", ControllerAktion("stick", 1, "links", (1.0, -0.5), 40), **FREI)
        e.ausfuehren("c-3", ControllerAktion("trigger", 1, "rechts", (0.8, 0.0), 40), **FREI)
        self.assertEqual((b.zustand[1]["sticks"]["links"], b.zustand[1]["trigger"]["rechts"]), ((0.0, 0.0), 0.0))
        self.assertIn(("stick", 1, "links", 1.0, -0.5), b.ereignisse)
        self.assertIn(("trigger", 1, "rechts", 0.8), b.ereignisse)

    def test_jede_sperre_verhindert_alles_und_nennt_den_grund(self):
        b, e = self.engine(not_aus=lambda: True)
        self.assertEqual(e.ausfuehren("c", knopf(), **FREI).grund, "not_aus")
        b2, e2 = self.engine(daniel_uebernimmt=lambda: True)
        self.assertEqual(e2.ausfuehren("c", knopf(), **FREI).grund, "daniel_uebernimmt")
        b3, e3 = self.engine(verbindung=lambda: False)
        self.assertEqual(e3.ausfuehren("c", knopf(), **FREI).grund, "verbindung_weg")
        b4, e4 = self.engine()
        self.assertEqual(e4.ausfuehren("c", knopf(), lease_grund="", haende_erlaubt=False, profil_erlaubt=True).grund, "haende_aus")
        self.assertEqual(e4.ausfuehren("c", knopf(), lease_grund="", haende_erlaubt=True, profil_erlaubt=False).grund, "profil_erlaubt_nicht")
        self.assertEqual(e4.ausfuehren("c", knopf(), lease_grund="lease_fehlt", haende_erlaubt=True, profil_erlaubt=True).grund, "lease_fehlt")
        for backend in (b, b2, b3, b4):
            self.assertEqual(backend.ereignisse, [], "bei einer Sperre erreicht nichts das Gerät")
            self.assertEqual(backend.offen, set(), "nicht einmal ein Gerät wird angelegt")

    def test_profile_der_bridge_erlauben_controller_nur_bei_controller_und_hybrid(self):
        self.assertEqual([n for n in steuerprofil.PROFILE if steuerprofil.profil(n).erlaubt("controller")], ["controller", "hybrid"])

    def test_not_aus_waehrend_des_haltens_bricht_ab_und_laesst_los(self):
        b = AttrappenBackend()
        e = ControllerEngine(b)
        ergebnis = []
        t = threading.Thread(target=lambda: ergebnis.append(e.ausfuehren("c", knopf("b", 3000), **FREI)))
        t.start()
        for _ in range(100):
            if ("knopf", 0, "b", True) in b.ereignisse:
                break
            time.sleep(0.01)
        t0 = time.monotonic()
        e.abbrechen()
        t.join(2)
        self.assertLess(time.monotonic() - t0, 1.0, "der Abbruch wirkt sofort, nicht erst nach drei Sekunden")
        self.assertEqual((ergebnis[0].status, b.zustand[0]["knoepfe"]), ("abgebrochen", set()))

    def test_uebernimmt_daniel_waehrend_des_haltens_wird_abgebrochen(self):
        daniel = [False]
        b = AttrappenBackend()
        e = ControllerEngine(b, daniel_uebernimmt=lambda: daniel[0])
        ergebnis = []
        t = threading.Thread(target=lambda: ergebnis.append(e.ausfuehren("c", knopf("x", 3000), **FREI)))
        t.start()
        time.sleep(0.1)
        daniel[0] = True
        t.join(2)
        self.assertEqual((ergebnis[0].status, ergebnis[0].grund), ("abgebrochen", "daniel_uebernimmt"))
        self.assertEqual(b.zustand[0]["knoepfe"], set())

    def test_backendfehler_laesst_trotzdem_alles_los(self):
        class Kaputt(AttrappenBackend):
            def stick(self, *a):
                raise OSError("weg")

        b = Kaputt()
        e = ControllerEngine(b, schlafen=lambda s: None)
        r = e.ausfuehren("c", ControllerAktion("stick", 0, "links", (1.0, 0.0), 40), **FREI)
        self.assertEqual((r.status, r.grund), ("fehler", "backend_fehler"))
        e.ausfuehren("c2", knopf("a"), **FREI)
        self.assertEqual(b.zustand[0]["knoepfe"], set())

    def test_loslassen_und_schliessen(self):
        b, e = self.engine()
        e.ausfuehren("c", knopf("a"), **FREI)
        self.assertEqual(e.ausfuehren("c", ControllerAktion("loslassen", 0), **FREI).status, "ausgefuehrt")
        e.schliessen()
        self.assertEqual(b.offen, set())
        self.assertEqual(e.zustand()["geraete"], [])

    def test_zustand_nennt_die_grenze(self):
        _, e = self.engine()
        self.assertIn("nicht: im Spiel angekommen", e.zustand()["hinweis"])

    def test_nicht_verfuegbares_backend_ist_eine_ablehnung_mit_grund(self):
        class Weg(AttrappenBackend):
            def verfuegbar(self):
                return False, "treiber_vigembus_fehlt"

        r = ControllerEngine(Weg()).ausfuehren("c", knopf(), **FREI)
        self.assertEqual((r.status, r.grund), ("abgelehnt", "controller_treiber_vigembus_fehlt"))


class VigemTests(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "nur dort, wo ViGEm nicht läuft")
    def test_ohne_windows_meldet_vigem_einen_grund_statt_abzustuerzen(self):
        ok, grund = VigemBackend().verfuegbar()
        self.assertFalse(ok)
        self.assertIn(grund, ("paket_vgamepad_fehlt", "treiber_vigembus_fehlt"))


@unittest.skipUnless(UinputBackend().verfuegbar()[0], "kein beschreibbares /dev/uinput oder kein evdev")
class UinputEchtTests(unittest.TestCase):
    @staticmethod
    def lies(pfad):
        with open(pfad) as f:
            return f.read().strip()

    def namen(self):
        return [self.lies(n) for n in glob.glob("/sys/devices/virtual/input/input*/name") if os.path.exists(n)]

    def test_ein_echtes_geraet_entsteht_mit_den_faehigkeiten_eines_controllers_und_verschwindet_wieder(self):
        b = UinputBackend()
        e = ControllerEngine(b, schlafen=lambda s: time.sleep(min(s, 0.005)))
        name = "Bridge virtueller Controller 3"
        self.assertNotIn(name, self.namen())
        r = e.ausfuehren("c", knopf("a", 40, index=2), **FREI)
        self.assertEqual(r.status, "ausgefuehrt", r)
        for _ in range(50):
            if name in self.namen():
                break
            time.sleep(0.05)
        verz = next(os.path.dirname(n) for n in glob.glob("/sys/devices/virtual/input/input*/name") if self.lies(n) == name)

        def bit(datei, n):
            worte = self.lies(verz + "/capabilities/" + datei).split()
            return bool(int(worte[-1 - n // 64], 16) >> (n % 64) & 1) if n // 64 < len(worte) else False

        for n in (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x10, 0x11):  # ABS_X, Y, Z, RX, RY, RZ, HAT0X, HAT0Y
            self.assertTrue(bit("abs", n), f"Achse {n:#x} fehlt")
        for n in (0x130, 0x131, 0x133, 0x134, 0x136, 0x137, 0x13A, 0x13B, 0x13C, 0x13D, 0x13E):  # BTN_SOUTH, EAST, NORTH, WEST, TL, TR, SELECT, START, MODE, THUMBL, THUMBR
            self.assertTrue(bit("key", n), f"Knopf {n:#x} fehlt")
        self.assertFalse(bit("key", 0x138), "ein Knopf, den ein Xbox-Controller nicht hat, ist nicht angelegt")
        e.schliessen()
        for _ in range(50):
            if name not in self.namen():
                break
            time.sleep(0.05)
        self.assertNotIn(name, self.namen())


if __name__ == "__main__":
    unittest.main()
