from __future__ import annotations

import unittest

from augen_haende_bridge import VTScreenState


class VTRendererTests(unittest.TestCase):
    def test_reads_text_cursor_and_sgr_without_losing_raw_byte_count(self) -> None:
        screen = VTScreenState(rows=3, cols=12)
        screen.feed(b"hello\x1b[2;3H\x1b[31mred")

        self.assertEqual(screen.text().splitlines(), ["hello", "  red"])
        self.assertEqual(screen.cursor_row, 1)
        self.assertEqual(screen.cursor_col, 5)
        self.assertEqual(screen.sgr, (31,))
        self.assertEqual(screen.bytes_received, len(b"hello\x1b[2;3H\x1b[31mred"))

    def test_tracks_alternate_screen_and_restores_primary_screen(self) -> None:
        screen = VTScreenState(rows=3, cols=12)
        screen.feed("main\n")
        screen.feed("\x1b[?1049halt\x1b[2Jalt")
        self.assertTrue(screen.alternate_screen)
        self.assertIn("alt", screen.text())
        screen.feed("\x1b[?1049l")
        self.assertFalse(screen.alternate_screen)
        self.assertIn("main", screen.text())

    def test_unsupported_sequences_are_visible_in_state(self) -> None:
        screen = VTScreenState(rows=2, cols=8)
        screen.feed("\x1b[6n")
        self.assertEqual(screen.unsupported_sequences, ["\x1b[6n"])

    def test_resize_preserves_visible_cells_and_cursor_bounds(self) -> None:
        screen = VTScreenState(rows=2, cols=5)
        screen.feed("abc")
        screen.resize(4, 8)
        self.assertEqual(screen.text().splitlines()[0], "abc")
        self.assertLess(screen.cursor_row, 4)
        self.assertLess(screen.cursor_col, 8)
