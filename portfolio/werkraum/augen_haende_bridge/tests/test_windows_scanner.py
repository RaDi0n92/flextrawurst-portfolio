from __future__ import annotations

import unittest

from augen_haende_bridge import TargetKind
from augen_haende_bridge.windows_scanner import WindowInfo, WindowsWindowScanner


class FakeWindowApi:
    def __init__(self) -> None:
        self.windows = [
            WindowInfo(
                hwnd=101,
                title="Firefox",
                class_name="MozillaWindowClass",
                rect=(10, 20, 810, 620),
                process_id=501,
                process_path="C:\\Program Files\\Firefox\\firefox.exe",
            ),
            WindowInfo(
                hwnd=202,
                title="Bridge",
                class_name="TkTopLevel",
                rect=(40, 50, 400, 300),
                process_id=502,
                process_path="C:\\Bridge\\bridge.exe",
            ),
        ]

    def virtual_screen_rect(self) -> tuple[int, int, int, int]:
        return (0, 0, 1920, 1080)

    def enumerate_windows(self) -> list[WindowInfo]:
        return list(self.windows)


class WindowsScannerTests(unittest.TestCase):
    def test_default_is_complete_desktop_then_visible_windows(self) -> None:
        scanner = WindowsWindowScanner(FakeWindowApi())
        snapshot = scanner.scan(frame_ref="frame://desktop/1", frame_hash="sha256:frame", captured_at_ms=100)

        self.assertEqual(snapshot.default_target_id, "windows:desktop")
        self.assertEqual(snapshot.source, "win32.window-enum")
        self.assertEqual(snapshot.items[0].kind, TargetKind.WINDOWS_DESKTOP)
        self.assertEqual(snapshot.items[0].rect, (0, 0, 1920, 1080))
        self.assertEqual([item.target_id for item in snapshot.items[1:]], ["windows:window:101", "windows:window:202"])
        self.assertEqual(snapshot.items[1].z_order, 1)
        self.assertEqual(snapshot.items[1].capabilities, frozenset({"inventory"}))

    def test_same_window_keeps_generation_when_title_or_rect_changes(self) -> None:
        api = FakeWindowApi()
        scanner = WindowsWindowScanner(api)
        first = scanner.scan(frame_ref="frame://1", frame_hash="sha256:1", captured_at_ms=1)
        api.windows[0] = WindowInfo(101, "Firefox — moved", "MozillaWindowClass", (20, 30, 820, 630), 501, api.windows[0].process_path)
        second = scanner.scan(frame_ref="frame://2", frame_hash="sha256:2", captured_at_ms=2)
        self.assertEqual(first.items[1].generation, second.items[1].generation)

    def test_reused_handle_with_new_process_gets_new_generation(self) -> None:
        api = FakeWindowApi()
        scanner = WindowsWindowScanner(api)
        first = scanner.scan(frame_ref="frame://1", frame_hash="sha256:1", captured_at_ms=1)
        api.windows[0] = WindowInfo(101, "Other", "OtherClass", (10, 20, 810, 620), 999, "C:\\Other\\other.exe")
        second = scanner.scan(frame_ref="frame://2", frame_hash="sha256:2", captured_at_ms=2)
        self.assertNotEqual(first.items[1].generation, second.items[1].generation)

    def test_missing_frame_witness_blocks_scan(self) -> None:
        with self.assertRaisesRegex(ValueError, "paired_frame_reference_and_hash_required"):
            WindowsWindowScanner(FakeWindowApi()).scan(frame_ref="", frame_hash="sha256:missing")
