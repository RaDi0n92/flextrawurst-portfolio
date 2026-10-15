from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "client_windows" / "start_with_ssh_tunnel.ps1"


class SshTunnelContractTests(unittest.TestCase):
    def test_launcher_keeps_both_ends_on_loopback(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"127.0.0.1:{0}:127.0.0.1:{0}"', text)
        self.assertIn('"-o", "ExitOnForwardFailure=yes"', text)
        self.assertIn('"-o", "BatchMode=yes"', text)

    def test_launcher_does_not_disable_host_key_verification_or_leak_token(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("StrictHostKeyChecking=no", text)
        self.assertNotIn('"-DesktopToken"', text)
        self.assertIn('$env:BRIDGE_TOKEN = $DesktopToken', text)

    def test_launcher_stops_only_its_child_tunnel(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("Stop-Process -Id $tunnel.Id -Force", text)
        self.assertNotIn("Stop-Process -Name ssh", text)

    def test_launcher_has_explicit_native_scan_test_hook(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[switch]$NativeScanOnStart", text)
        self.assertIn("BRIDGE_NATIVE_SCAN_ON_START", text)

    def test_launcher_resolves_repository_and_handoff_archive_layouts(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("if ([string]::IsNullOrWhiteSpace($ExePath))", text)
        self.assertIn("..\\AugenUndHaendeBridge\\AugenUndHaendeBridge.exe", text)

    def test_native_witness_is_read_only_and_writes_json_plus_png(self):
        witness = SCRIPT.with_name("native_acceptance_witness.ps1").read_text(encoding="utf-8")
        self.assertIn("GetWindowText", witness)
        self.assertIn("GetWindowRect", witness)
        self.assertIn("Save-NativeScreenEvidence", witness)
        self.assertIn('status = "PASS"', witness)
        self.assertIn("input_exercised = $false", witness)
        self.assertNotIn("ExecutionPolicy", witness)
        self.assertNotIn("SendInput", witness)
        self.assertNotIn("PostMessage", witness)

    def test_native_witness_resolves_handoff_archive_layout(self):
        witness = SCRIPT.with_name("native_acceptance_witness.ps1").read_text(encoding="utf-8")
        self.assertIn("if ([string]::IsNullOrWhiteSpace($ExePath))", witness)
        self.assertIn("..\\AugenUndHaendeBridge\\AugenUndHaendeBridge.exe", witness)

    def test_native_witness_can_wait_for_a_human_binding_click(self):
        witness = SCRIPT.with_name("native_acceptance_witness.ps1").read_text(encoding="utf-8")
        self.assertIn("[switch]$WaitForManualBinding", witness)
        self.assertIn("Bitte jetzt im Bridge-Zielrail", witness)
        self.assertIn('"binding-readback"', witness)
        self.assertIn('target_selection = if ($manualBindingObserved)', witness)


if __name__ == "__main__":
    unittest.main()
