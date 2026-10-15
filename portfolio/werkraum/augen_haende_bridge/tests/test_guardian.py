from __future__ import annotations

import unittest

from augen_haende_bridge import (
    GuardianObservation,
    GuardianStatus,
    GuardianStep,
    PlaywrightGuardian,
)


class PlaywrightGuardianTests(unittest.TestCase):
    def test_pass_requires_dom_core_audit_and_fresh_target(self) -> None:
        guardian = PlaywrightGuardian()
        step = GuardianStep(
            step_id="inspect-kde-1",
            action="inspect-selected",
            expected_dom={"selected-target": "kde-1", "selected-availability": "available"},
            expected_core={"status": "observed"},
            required_audit_suffix=("action.requested", "action.accepted", "action.observed"),
            target_id="kde-1",
        )
        verdict = guardian.verify(
            step,
            GuardianObservation(
                step_id="inspect-kde-1",
                action="inspect-selected",
                dom={"selected-target": "kde-1", "selected-availability": "available"},
                core={"status": "observed"},
                audit_types=("action.requested", "action.accepted", "action.observed"),
                target_id="kde-1",
                scan_id="scan-17",
                frame_hash="sha256:frame-17",
            ),
        )
        self.assertEqual(verdict.status, GuardianStatus.PASS)
        self.assertTrue(verdict.passed)

    def test_dom_success_without_audit_is_blocked(self) -> None:
        guardian = PlaywrightGuardian()
        step = GuardianStep(
            step_id="input",
            action="input-inside",
            expected_dom={"last-result": "accepted"},
            required_audit_suffix=("action.requested", "action.accepted"),
            target_id="win-desktop",
        )
        verdict = guardian.verify(
            step,
            GuardianObservation(
                step_id="input",
                action="input-inside",
                dom={"last-result": "accepted"},
                core={"status": "accepted"},
                audit_types=(),
                target_id="win-desktop",
                scan_id="scan-1",
                frame_hash="sha256:frame-1",
            ),
        )
        self.assertEqual(verdict.status, GuardianStatus.BLOCKED)
        self.assertIn("audit suffix mismatch", " ".join(verdict.reasons))

    def test_missing_native_witness_stays_unknown(self) -> None:
        guardian = PlaywrightGuardian()
        step = GuardianStep(
            step_id="native-overlay",
            action="show-overlay",
            target_id="win-desktop",
            requires_native=True,
        )
        verdict = guardian.verify(
            step,
            GuardianObservation(
                step_id="native-overlay",
                action="show-overlay",
                dom={},
                core={},
                audit_types=(),
                target_id="win-desktop",
                scan_id="scan-1",
                frame_hash="sha256:frame-1",
            ),
        )
        self.assertEqual(verdict.status, GuardianStatus.UNKNOWN)
        self.assertIn("native platform witness", " ".join(verdict.reasons))

