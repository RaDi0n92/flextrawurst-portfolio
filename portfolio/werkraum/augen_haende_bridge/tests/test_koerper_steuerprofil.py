"""G10: Steuerprofile und die Erkennung virtueller Controller (nur erkennen, nie installieren)."""

import unittest
from unittest import mock

from augen_haende_bridge.koerper import eingabe_adapter as ea
from augen_haende_bridge.koerper import steuerprofil as sp


class ProfilTests(unittest.TestCase):
    def test_hintergrund_und_geteilte_maus_sind_unterscheidbar(self):
        h, g = sp.profil("hintergrund"), sp.profil("geteilte_maus")
        self.assertEqual((h.zeiger_geteilt, h.tastatur_geteilt, g.zeiger_geteilt, g.tastatur_geteilt), (False, False, True, True))
        for art in sorted(sp.KOORDINATEN_AKTIONEN):
            self.assertFalse(h.erlaubt(art), art)
            self.assertTrue(g.erlaubt(art), art)
        self.assertFalse(g.erlaubt("controller"))
        self.assertTrue(sp.profil("hybrid").erlaubt("controller") and sp.profil("hybrid").erlaubt("klick"))
        self.assertTrue(sp.profil("controller").erlaubt("controller"))
        self.assertFalse(sp.profil("controller").erlaubt("klick"))

    def test_unbekannte_namen_ergeben_das_vorsichtigste_profil(self):
        for name in (None, 5, "", "alles", "GETEILTE_MAUS"):
            self.assertEqual(sp.profil(name).name, "hintergrund", name)
        self.assertEqual({sp.profil(n).name for n in sp.PROFILE}, set(sp.PROFILE))

    def test_das_profil_wirkt_im_kaefig(self):
        a = ea.Aktion("klick", punkt=(1, 1))
        ziel, rect = "kde1:window:5", (0, 0, 100, 100)
        bezug = ea.Bildbezug(ziel, 1, 1000, 100, 100, rect, "g", 1.0)
        stand = ea.ZielStand(True, rect, False, "g", 1.0)
        for profilname, erwartet in (("hintergrund", "profil_erlaubt_nicht"), ("geteilte_maus", ""), ("hybrid", "")):
            e = ea.pruefe(a, ziel=ziel, bezug=bezug, stand=stand, lease_grund="", not_aus=False, haende_erlaubt=True, profil_erlaubt=sp.profil(profilname).erlaubt(a.art), jetzt_ms=1500)
            self.assertEqual(e.grund, erwartet, profilname)


class ControllerTests(unittest.TestCase):
    def test_linux_ohne_uinput(self):
        z = sp.controller_zustand(plattform="linux", existiert=lambda p: False, joysticks=lambda: [])
        self.assertEqual((z["treiber"], z["treiber_vorhanden"], z["nutzbar"], z["ziel"], z["freigabe_noetig"]), ("uinput", False, False, 4, True))
        self.assertIn("nicht vorhanden", z["text"])

    def test_linux_uinput_da_aber_nicht_beschreibbar(self):
        z = sp.controller_zustand(plattform="linux", existiert=lambda p: p == "/dev/uinput", schreibbar=lambda p: False, joysticks=lambda: [])
        self.assertEqual((z["treiber_vorhanden"], z["nutzbar"]), (True, False))
        self.assertIn("Daniels Wort", z["text"])

    def test_linux_uinput_beschreibbar_und_geraete_gedeckelt(self):
        z = sp.controller_zustand(plattform="linux", existiert=lambda p: p == "/dev/uinput", schreibbar=lambda p: True, joysticks=lambda: [f"/dev/input/js{i}" for i in range(7)])
        self.assertEqual((z["nutzbar"], len(z["erkannte_geraete"])), (True, sp.MAX_CONTROLLER))

    def test_windows_mit_und_ohne_treiber(self):
        self.assertEqual(sp.controller_zustand(plattform="windows", vigem=False, joysticks=lambda: [])["nutzbar"], False)
        z = sp.controller_zustand(plattform="windows", vigem=True, joysticks=lambda: [])
        self.assertEqual((z["treiber"], z["nutzbar"]), ("ViGEmBus", True))
        self.assertIn("nicht installiert", sp.controller_zustand(plattform="windows", vigem=False, joysticks=lambda: [])["text"])

    def test_zustand_meldet_controller_nur_wenn_profil_und_treiber_passen(self):
        kw = dict(plattform="linux", existiert=lambda p: p == "/dev/uinput", schreibbar=lambda p: True, joysticks=lambda: [])
        self.assertTrue(sp.zustand("hybrid", **kw)["controller_nutzbar"])
        self.assertFalse(sp.zustand("geteilte_maus", **kw)["controller_nutzbar"], "Treiber da, aber das Profil sieht keinen Controller vor")
        self.assertFalse(sp.zustand("hybrid", plattform="linux", existiert=lambda p: False, joysticks=lambda: [])["controller_nutzbar"])

    def test_erkennen_installiert_und_oeffnet_nichts(self):
        with mock.patch("builtins.open", side_effect=AssertionError("nichts öffnen")), mock.patch("subprocess.run", side_effect=AssertionError("nichts starten")):
            sp.controller_zustand(plattform="linux", existiert=lambda p: True, schreibbar=lambda p: True, joysticks=lambda: [])
            sp.controller_zustand(plattform="windows", vigem=False, joysticks=lambda: [])

    def test_die_echte_maschine_wird_ehrlich_beschrieben(self):
        z = sp.controller_zustand()
        self.assertIn(z["plattform"], ("linux", "windows"))
        self.assertTrue(z["text"])
        self.assertIsInstance(z["nutzbar"], bool)


if __name__ == "__main__":
    unittest.main()
