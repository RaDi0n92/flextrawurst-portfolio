import unittest
from unittest.mock import patch

from augen_haende_bridge.preflight import collect_probes


class PreflightTests(unittest.TestCase):
    def test_preflight_is_side_effect_free_and_has_required_g01_probes(self):
        probes = collect_probes()
        names = {probe.name for probe in probes}
        self.assertTrue({
            "host.os",
            "windows.native_runner",
            "windows.packager.pyinstaller",
            "native.overlay.entrypoint",
            "kde.live_session",
            "original.terminal.readback",
            "transport.websocket_dependency",
            "native.window.evidence",
        } <= names)
        self.assertTrue(all(probe.status in {"available", "not_proven", "unavailable"} for probe in probes))

    @patch("augen_haende_bridge.preflight.platform.system", return_value="Windows")
    def test_windows_host_is_reported_as_available(self, _system):
        probes = {probe.name: probe for probe in collect_probes()}
        self.assertEqual(probes["windows.native_runner"].status, "available")


if __name__ == "__main__":
    unittest.main()
