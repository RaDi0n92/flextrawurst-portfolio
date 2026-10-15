"""Tests für die reine Logik in koerper/win32.py — Farben, Wort-Zerlegung und die Linux/Windows-Weiche.

Die eigentlichen DLL-Aufrufe (user32, gdi32, kernel32) brauchen einen echten oder Wine-Windows-Host und werden hier nicht
gefaked; unter Linux ist das Vertragsversprechen des Moduls nur: importierbar, Konstanten korrekt, reine Helfer korrekt,
und jeder Versuch einer echten Win32-Aktion scheitert kontrolliert über `require_windows()`.
"""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import win32 as w


class PlattformWeicheTests(unittest.TestCase):
    def test_unter_linux_ist_windows_falsch_und_tabellen_sind_leer(self) -> None:
        self.assertFalse(w.WINDOWS)
        self.assertIsNone(w.user32)
        self.assertIsNone(w.gdi32)
        self.assertIsNone(w.kernel32)

    def test_require_windows_meldet_sich_unter_linux(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            w.require_windows()

    def test_last_error_ist_unter_linux_immer_null(self) -> None:
        self.assertEqual(w.last_error(), 0)


class FarbenTests(unittest.TestCase):
    def test_rgb_baut_colorref_als_0x00bbggrr(self) -> None:
        self.assertEqual(w.rgb(0x11, 0x22, 0x33), 0x00332211)

    def test_rgb_kappt_werte_ausserhalb_eines_bytes(self) -> None:
        self.assertEqual(w.rgb(256 + 0x11, -1, 0x33), w.rgb(0x11, 0xFF, 0x33))

    def test_rgb_hex_liest_ein_websicheres_hexformat(self) -> None:
        self.assertEqual(w.rgb_hex("#00E5FF"), w.rgb(0x00, 0xE5, 0xFF))

    def test_rgb_hex_kommt_auch_ohne_raute_aus(self) -> None:
        self.assertEqual(w.rgb_hex("FFD600"), w.rgb_hex("#FFD600"))


class WortZerlegungTests(unittest.TestCase):
    def test_loword_und_hiword(self) -> None:
        wert = (0x1234 << 16) | 0x5678
        self.assertEqual(w.loword(wert), 0x5678)
        self.assertEqual(w.hiword(wert), 0x1234)

    def test_signed_loword_liest_negative_x_koordinate(self) -> None:
        # lParam einer Mausnachricht mit x = -5, y = 10
        lparam = w.make_lparam(-5, 10)
        self.assertEqual(w.signed_loword(lparam), -5)
        self.assertEqual(w.signed_hiword(lparam), 10)

    def test_signed_hiword_liest_negative_y_koordinate(self) -> None:
        lparam = w.make_lparam(3, -7)
        self.assertEqual(w.signed_loword(lparam), 3)
        self.assertEqual(w.signed_hiword(lparam), -7)

    def test_make_lparam_ist_zu_loword_hiword_umgekehrt(self) -> None:
        lparam = w.make_lparam(0x12, 0x34)
        self.assertEqual(w.loword(lparam), 0x12)
        self.assertEqual(w.hiword(lparam), 0x34)


if __name__ == "__main__":
    unittest.main()
