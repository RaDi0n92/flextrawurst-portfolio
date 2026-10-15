from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path

from tests.validate_native_binding_evidence import validate_native_binding


def _payload() -> dict:
    return {
        "status": "PASS",
        "native_windows": True,
        "input_exercised": False,
        "scanner_marker": "Augen & Hände Bridge · scan-received:2",
        "binding_marker": "Augen & Hände Bridge · scan-received:2 · binding-readback",
        "target_selection": "manual_click",
        "binding_readback": "native_marker",
        "transport": "ssh-local-forward",
        "window": {
            "hwnd": 123,
            "process_id": 456,
            "visible": True,
            "rect": {"width": 800, "height": 600},
        },
    }


class NativeBindingEvidenceTests(unittest.TestCase):
    def _png(self, directory: Path) -> Path:
        path = directory / "native.png"
        ihdr = struct.pack(">IIBBBBB", 800, 600, 8, 6, 0, 0, 0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr)
        return path

    def test_complete_manual_witness_is_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = validate_native_binding(_payload(), self._png(Path(directory)))
        self.assertEqual(report.status, "PASS")

    def test_missing_png_is_unknown_not_pass(self) -> None:
        report = validate_native_binding(_payload(), None)
        self.assertEqual(report.status, "UNKNOWN")

    def test_missing_manual_marker_fails_closed(self) -> None:
        payload = _payload()
        payload["target_selection"] = "not_exercised"
        with tempfile.TemporaryDirectory() as directory:
            report = validate_native_binding(payload, self._png(Path(directory)))
        self.assertEqual(report.status, "FAIL")

    def test_invalid_png_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.png"
            path.write_bytes(b"not a png")
            report = validate_native_binding(_payload(), path)
        self.assertEqual(report.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
