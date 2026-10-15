"""G15: Loops und Goals — Budget, Fortschritt, Pause, Stop ohne heimliche Wiederholung, echter Abschlussgrund."""

from __future__ import annotations

import threading
import time
import unittest

from augen_haende_bridge.loops import LoopFehler, LoopVerwaltung, Loop, MAX_GLEICHZEITIG


def warte(bedingung, s=5.0):
    ende = time.monotonic() + s
    while time.monotonic() < ende:
        if bedingung():
            return True
        time.sleep(0.005)
    return False


def ok(nr):
    return {"ok": True, "status": "fertig", "kurz": f"durchlauf {nr}", "ctx": {"wert": nr}}


class BudgetTests(unittest.TestCase):
    def test_laeufe_budget_beendet_mit_echtem_grund(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 3, "max_s": 60}, intervall_s=0)
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        s = l.stand()
        self.assertEqual((s["laeufe"], s["grund"], s["art"]), (3, "budget_laeufe_erschoepft", "loop"))
        self.assertEqual([f["nr"] for f in s["fortschritt"]], [1, 2, 3])

    def test_zeitbudget(self):
        t = [0.0]
        l = Loop("l-1", "t", lambda nr: (t.__setitem__(0, t[0] + 10) or ok(nr)), budget={"max_laeufe": 100, "max_s": 25}, intervall_s=0, uhr=lambda: t[0])
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual((l.grund, l.laeufe), ("budget_zeit_erschoepft", 3))

    def test_ungueltiges_budget_und_abschluss(self):
        for b in (None, {}, {"max_laeufe": 0}, {"max_laeufe": 1001}, {"max_laeufe": True}, {"max_s": 0}, {"max_s": 86_401}, {"x": 1}, {"max_laeufe": 1.5}):
            if b == {}:
                continue  # leer = Standardwerte
            with self.assertRaises(LoopFehler, msg=str(b)):
                Loop("l", "t", ok, budget=b)
        with self.assertRaises(LoopFehler):
            Loop("l", "t", ok, budget={"max_laeufe": 2}, abschluss={"pfad": "x", "wild": 1})


class GoalTests(unittest.TestCase):
    def test_goal_endet_wenn_die_bedingung_stimmt(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 50}, intervall_s=0, abschluss={"pfad": "wert", "mindestens": 4})
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual((l.art, l.grund, l.laeufe), ("goal", "abgeschlossen", 4))

    def test_goal_ohne_erreichen_endet_am_budget_nicht_als_abgeschlossen(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 3}, intervall_s=0, abschluss={"pfad": "wert", "mindestens": 99})
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual(l.grund, "budget_laeufe_erschoepft")

    def test_ein_fehlgeschlagener_durchlauf_zaehlt_nie_als_erreicht(self):
        l = Loop("l-1", "t", lambda nr: {"ok": False, "ctx": {"wert": 100}}, budget={"max_laeufe": 10}, intervall_s=0, abschluss={"pfad": "wert", "mindestens": 1})
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual((l.grund, l.laeufe), ("fehler", 3), "drei Fehlschläge in Folge beenden den Loop")


class FehlerTests(unittest.TestCase):
    def test_ausnahmen_werden_gezaehlt_und_beenden_mit_fehler(self):
        def kaputt(nr):
            raise RuntimeError("boom")

        l = Loop("l-1", "t", kaputt, budget={"max_laeufe": 10}, intervall_s=0)
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual((l.grund, l.fortschritt[0]["status"], l.fortschritt[0]["kurz"]), ("fehler", "ausnahme", "RuntimeError"))

    def test_ein_erfolg_setzt_die_fehlerreihe_zurueck(self):
        l = Loop("l-1", "t", lambda nr: {"ok": nr % 3 == 0}, budget={"max_laeufe": 9}, intervall_s=0)
        l.starten()
        self.assertTrue(warte(lambda: l.zustand == "beendet"))
        self.assertEqual((l.grund, l.laeufe), ("budget_laeufe_erschoepft", 9))


class SteuerungTests(unittest.TestCase):
    def test_pause_haelt_an_fortsetzen_geht_weiter(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 1000}, intervall_s=0.01)
        l.starten()
        self.assertTrue(warte(lambda: l.laeufe >= 2))
        self.assertTrue(l.pausieren())
        time.sleep(0.1)
        n = l.laeufe
        time.sleep(0.2)
        self.assertEqual(l.laeufe, n, "in der Pause beginnt nichts Neues")
        self.assertEqual(l.zustand, "pausiert")
        self.assertTrue(l.fortsetzen())
        self.assertTrue(warte(lambda: l.laeufe > n + 1))
        l.stoppen()

    def test_nach_dem_stop_beginnt_nie_ein_neuer_durchlauf(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 1000}, intervall_s=0.01)
        l.starten()
        self.assertTrue(warte(lambda: l.laeufe >= 2))
        self.assertTrue(l.stoppen())
        n = l.laeufe
        time.sleep(0.3)
        self.assertEqual((l.laeufe, l.zustand, l.grund), (n, "beendet", "gestoppt"))
        self.assertFalse(l.stoppen(), "ein zweiter Stop ändert nichts")
        self.assertFalse(l.pausieren())
        self.assertFalse(l.fortsetzen())
        with self.assertRaises(LoopFehler):
            l.starten()

    def test_stop_waehrend_ein_durchlauf_laeuft_wartet_auf_dessen_ende_und_startet_keinen_weiteren(self):
        drin, frei = threading.Event(), threading.Event()

        def langsam(nr):
            drin.set()
            frei.wait(5)
            return ok(nr)

        l = Loop("l-1", "t", langsam, budget={"max_laeufe": 1000}, intervall_s=0)
        l.starten()
        self.assertTrue(drin.wait(2))
        threading.Timer(0.1, frei.set).start()
        l.stoppen()
        self.assertEqual((l.laeufe, l.zustand, l.grund), (1, "beendet", "gestoppt"))
        time.sleep(0.2)
        self.assertEqual(l.laeufe, 1)

    def test_stop_in_der_pause_beendet_sofort(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 1000}, intervall_s=0.5)
        l.starten()
        self.assertTrue(warte(lambda: l.laeufe >= 1))
        l.pausieren()
        t0 = time.monotonic()
        l.stoppen()
        self.assertLess(time.monotonic() - t0, 1.0)
        self.assertEqual(l.zustand, "beendet")

    def test_ein_nie_gestarteter_loop_laesst_sich_stoppen(self):
        l = Loop("l-1", "t", ok, budget={"max_laeufe": 3})
        self.assertTrue(l.stoppen())
        self.assertEqual((l.zustand, l.grund), ("beendet", "gestoppt"))


class VerwaltungTests(unittest.TestCase):
    def test_begrenzt_gleichzeitige_loops_und_stoppt_alle(self):
        v = LoopVerwaltung()
        loops = []
        for i in range(MAX_GLEICHZEITIG):
            l = v.neu(f"t{i}", ok, budget={"max_laeufe": 1000}, intervall_s=0.05)
            l.starten()
            loops.append(l)
        with self.assertRaises(LoopFehler) as c:
            v.neu("zu viel", ok, budget={"max_laeufe": 1})
        self.assertEqual(str(c.exception), "zu_viele_loops")
        self.assertEqual(len(v.liste()), MAX_GLEICHZEITIG)
        self.assertEqual(v.alle_stoppen(), MAX_GLEICHZEITIG)
        self.assertTrue(all(l.zustand == "beendet" for l in loops))
        self.assertIsNone(v.hole("l-gibtsnicht"))
        v.neu("jetzt wieder", ok, budget={"max_laeufe": 1})  # Platz ist wieder frei


if __name__ == "__main__":
    unittest.main()
