from __future__ import annotations

import hashlib
import os
import unittest

from augen_haende_bridge.windows_capture import WindowsScreenCapture


class FakeCaptureApi:
    def virtual_screen_rect(self):
        return (-2, 3, 2, 5)

    def capture_bgra(self, rect):
        self.last_rect = rect
        return bytes(range(32))


class WindowsCaptureTests(unittest.TestCase):
    def test_capture_pairs_hash_reference_and_exact_dimensions(self):
        api = FakeCaptureApi()
        frame = WindowsScreenCapture(api).capture(captured_at_ms=123)
        digest = hashlib.sha256(bytes(range(32))).hexdigest()
        self.assertEqual(frame.frame_hash, f"sha256:{digest}")
        self.assertEqual(frame.frame_ref, f"windows://desktop/123-{digest[:16]}")
        self.assertEqual((frame.width, frame.height), (4, 2))
        self.assertEqual(api.last_rect, (-2, 3, 2, 5))

    @unittest.skipUnless(os.name != "nt", "Linux-only unavailable-platform assertion")
    def test_linux_default_is_unavailable(self):
        capture = WindowsScreenCapture()
        self.assertFalse(capture.available)
        with self.assertRaisesRegex(RuntimeError, "windows_capture_unavailable"):
            capture.capture(captured_at_ms=1)


if __name__ == "__main__":
    unittest.main()
