"""Dialoge im Terminal der Agenten: erkannt mit den echten Texten vom 2026-10-03, nicht erkannt bei normalem Text, als Lampe und im Chat sichtbar."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from augen_haende_bridge.koerper import ampel
from augen_haende_bridge.koerper.dialog_erkennung import erkenne

CLAUDE_VERTRAUEN = """Accessing workspace:
/root/werkraum/augen_haende_bridge

Quick safety check: Is this a project you created or one you trust?
If not, we recommend reviewing the contents first.

Claude Code'll be able to read, edit, and execute files here.

Security guide

> No, exit
  Yes, I trust this folder

Enter to confirm · Esc to cancel""".splitlines()

OPENCODE_BERECHTIGUNG = """Permission required
  - /root/werkraum/augen_haende_bridge/skills/bridge-praxistest/*

  Allow once      Allow always      Reject

trl+f   fullscreen""".splitlines()


class ErkennungTests(unittest.TestCase):
    def test_vertrauensfrage_von_claude_code(self):
        d = erkenne(CLAUDE_VERTRAUEN)
        self.assertEqual(d.art, "vertrauen")
        self.assertTrue(any("Yes, I trust" in a for a in d.antworten))

    def test_berechtigung_von_opencode(self):
        d = erkenne(OPENCODE_BERECHTIGUNG)
        self.assertEqual(d.art, "berechtigung")
        self.assertIn("Allow once", d.antworten[0])

    def test_berechtigung_von_opencode_ohne_fragezeile(self):
        """So sah der Dialog am 2026-10-03 aus: nur der Pfad und die Wahlzeile, ohne das Wort Permission auf dem Bildschirm."""
        d = erkenne(["  - /root/werkraum/augen_haende_bridge/*", "", "  Allow once      Allow always      Reject", "trl+f   fullscreen"])
        self.assertEqual(d.art, "berechtigung")
        self.assertIn("/root/werkraum/augen_haende_bridge/*", d.frage)

    def test_ein_einzelnes_wahlwort_im_text_ist_kein_dialog(self):
        self.assertIsNone(erkenne(["Die Option Reject wird in der Doku erklaert.", "Allow once steht im Handbuch."]))

    def test_ja_nein(self):
        d = erkenne(["Das Skript löscht 3 Dateien.", "Proceed? (y/n)"])
        self.assertEqual(d.art, "ja_nein")

    def test_normaler_text_ist_kein_dialog(self):
        for zeilen in (["Ich erlaube mir einen Hinweis zur Berechtigung der Datei."], ["Wir sagen Yes oder No in der Doku."], ["permission denied: /root/x"],
                       ["", "   "], [], ["Allow once ist ein Beispiel ohne Frage"]):
            self.assertIsNone(erkenne(zeilen), zeilen)

    def test_nur_das_ende_des_bildschirms_zaehlt(self):
        alt = CLAUDE_VERTRAUEN + ["x"] * 40  # der Dialog scrollte weit nach oben, danach kam normale Ausgabe
        self.assertIsNone(erkenne(alt))


class LampeTests(unittest.TestCase):
    def test_kein_dialog_ist_gruen(self):
        l = ampel.dialog_lampe(None)
        self.assertEqual((l.kennung, l.farbe, l.wort), ("dialog", ampel.GRUEN, "kein Dialog offen"))

    def test_dialog_ist_orange_und_nach_drei_minuten_rot_und_blinkend(self):
        l = ampel.dialog_lampe(("berechtigung", "Permission required", 40.0))
        self.assertEqual(l.farbe, ampel.GELB)
        self.assertIn("40 s", l.wort)
        self.assertIn("eine Berechtigung", l.wort)
        l = ampel.dialog_lampe(("berechtigung", "Permission required", 200.0))
        self.assertEqual((l.farbe, l.blinkt, l.piepen), (ampel.ROT, True, True))

    def test_die_lampe_gehoert_zu_den_haenden_und_steht_im_katalog(self):
        self.assertEqual(ampel.gruppe_von("dialog"), "haende")
        self.assertIn("dialog", ampel.KATALOG)
        z = ampel.Zustand(name="X", dialog=("vertrauen", "Do you trust this folder", 5.0))
        drei = ampel.drei_lampen(ampel.lampen(z))
        haende = next(l for l in drei if l.kennung == "haende")
        self.assertEqual(haende.farbe, ampel.GELB)


class AnwendungTests(unittest.TestCase):
    def setUp(self):
        from augen_haende_bridge.koerper.anwendung import KoerperAnwendung

        self.app = KoerperAnwendung.__new__(KoerperAnwendung)
        self.app._dialog_seit, self.app._dialog_gemeldet = {}, {}
        self.zeilen = list(CLAUDE_VERTRAUEN)
        zeilen = self.zeilen

        class Modell:
            @property
            def zeilen(self):
                return len(zeilen)

            def zeile_text(self, i):
                return zeilen[i]

        self.modell = Modell()
        self.agent = SimpleNamespace(name="Claude-Host", koerper=SimpleNamespace(terminal=SimpleNamespace(modell=self.modell)))
        self.chat = Mock()
        self.app.chat = self.chat
        self.app.agenten = {}  # die Meldung fragt nach den Gate-Nachbarn; hier gibt es keine
        self.app.bilderstrom = None
        self.logzeilen = []
        self.app.log = self.logzeilen.append

    def test_zeit_zaehlt_ab_der_ersten_sichtung_und_endet_mit_dem_dialog(self):
        a = self.app._dialog_von("t", self.agent, 100.0)
        b = self.app._dialog_von("t", self.agent, 130.0)
        self.assertEqual((a[0], round(a[2]), round(b[2])), ("vertrauen", 0, 30))
        self.zeilen[:] = ["normale Ausgabe"]
        self.assertIsNone(self.app._dialog_von("t", self.agent, 140.0))
        c = self.app._dialog_von("t", self.agent, 150.0) if self.zeilen == ["normale Ausgabe"] else None
        self.assertIsNone(c)

    def test_der_chat_meldet_jeden_dialog_genau_einmal(self):
        self.app._dialog_von("t", self.agent, 100.0)
        for _ in range(3):
            self.app._dialog_melden("t", self.agent, [])
        self.assertEqual(self.chat.empfangen.call_count, 1)
        text = self.chat.empfangen.call_args.args[1]
        self.assertIn("Claude-Host wartet auf eine Vertrauensfrage", text)
        self.assertIn("Beantworte ihn im Terminal", text)
        self.assertEqual(len(self.logzeilen), 1)
        self.assertIn("Dialog: Claude-Host wartet auf eine Vertrauensfrage", self.logzeilen[0], "auch im Körper-Log, damit Beobachter es sehen")
        self.zeilen[:] = OPENCODE_BERECHTIGUNG  # ein neuer Dialog wird wieder gemeldet
        self.app._dialog_von("t", self.agent, 200.0)
        self.app._dialog_melden("t", self.agent, [])
        self.assertEqual(self.chat.empfangen.call_count, 2)


if __name__ == "__main__":
    unittest.main()
