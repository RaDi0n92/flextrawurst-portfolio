"""Tests für koerper/menue.py unter Linux.

Popup-Menüs und Zwischenablage sind reine Win32-Aufrufe ohne injizierbare Fake-API (anders als der Fensterscanner);
ein ehrlicher Test unter Linux kann nur die dokumentierte Weiche selbst prüfen: jede Funktion meldet sich sofort über
`require_windows()`, bevor sie irgendeinen `user32`/`kernel32`-Aufruf versucht. Echtes Verhalten bleibt Wine-/Windows-Beleg.
"""

from __future__ import annotations

import unittest

from augen_haende_bridge.koerper import menue


class GatingTests(unittest.TestCase):
    def test_zeige_menue_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            menue.zeige_menue(1, [(1, "Eins", 0)], 0, 0)

    def test_text_aus_zwischenablage_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            menue.text_aus_zwischenablage(1)

    def test_text_in_zwischenablage_verlangt_windows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "win32_required"):
            menue.text_in_zwischenablage(1, "hallo")


class KonstantenTests(unittest.TestCase):
    def test_abgeblendet_und_gehakt_spiegeln_die_win32_flags(self) -> None:
        from augen_haende_bridge.koerper import win32 as w

        self.assertEqual(menue.ABGEBLENDET, w.MF_GRAYED)
        self.assertEqual(menue.GEHAKT, w.MF_CHECKED)


if __name__ == "__main__":
    unittest.main()
