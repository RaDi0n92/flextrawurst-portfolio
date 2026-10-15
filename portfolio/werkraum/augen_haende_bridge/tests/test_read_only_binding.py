import unittest

from augen_haende_bridge.contracts import Capability, TargetKind, TargetScanItem, TargetScanSnapshot
from augen_haende_bridge.read_only_binding import (
    BindingError,
    BindingStatus,
    create_read_only_binding,
    read_back_binding,
)


def snapshot(*, generation="hwnd:7:generation:1", frame_hash="sha256:frame-1", available="available"):
    return TargetScanSnapshot(
        scan_id="scan-1",
        captured_at_ms=100,
        source="win32.window-enum",
        frame_ref="frame://desktop/1",
        frame_hash=frame_hash,
        default_target_id="windows:desktop",
        items=(TargetScanItem(
            target_id="windows:window:7",
            generation=generation,
            kind=TargetKind.WINDOWS_WINDOW,
            label="Browser",
            host="thinkpad",
            rect=(0, 0, 800, 600),
            visible=True,
            source="win32.window-enum",
            availability=available,
            capabilities=frozenset({"inventory", "capture"}),
        ),),
    )


class ReadOnlyBindingTests(unittest.TestCase):
    def test_selection_carries_scan_witness_and_observe_only(self):
        binding = create_read_only_binding(
            snapshot(), binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
        )
        self.assertEqual(binding.target_generation, "hwnd:7:generation:1")
        self.assertEqual(binding.frame_hash, "sha256:frame-1")
        self.assertEqual(binding.capabilities, frozenset({Capability.OBSERVE}))

    def test_matching_fresh_scan_reads_binding_back(self):
        binding = create_read_only_binding(
            snapshot(), binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
        )
        readback = read_back_binding(binding, snapshot())
        self.assertEqual(readback.status, BindingStatus.MATCHED)
        self.assertTrue(readback.valid)

    def test_reused_window_identity_is_stale(self):
        binding = create_read_only_binding(
            snapshot(), binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
        )
        readback = read_back_binding(binding, snapshot(generation="hwnd:7:generation:2"))
        self.assertEqual(readback.status, BindingStatus.STALE)
        self.assertEqual(readback.reason, "target_generation_changed")

    def test_new_frame_is_stale_even_when_target_identity_survives(self):
        binding = create_read_only_binding(
            snapshot(), binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
        )
        readback = read_back_binding(binding, snapshot(frame_hash="sha256:frame-2"))
        self.assertEqual(readback.reason, "paired_frame_changed")

    def test_unavailable_or_unobservable_target_cannot_be_bound(self):
        with self.assertRaisesRegex(BindingError, "target_unavailable"):
            create_read_only_binding(
                snapshot(available="unavailable"),
                binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
            )

        no_capability = snapshot()
        item = no_capability.items[0]
        no_capability = TargetScanSnapshot(
            **{**no_capability.__dict__, "items": (TargetScanItem(**{**item.__dict__, "capabilities": frozenset()}),)}
        )
        with self.assertRaisesRegex(BindingError, "observation_capability_missing"):
            create_read_only_binding(
                no_capability,
                binding_id="binding-1", agent_id="codex", target_id="windows:window:7"
            )


if __name__ == "__main__":
    unittest.main()
