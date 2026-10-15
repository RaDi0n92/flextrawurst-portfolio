from __future__ import annotations

import unittest

from augen_haende_bridge import (
    TERMINAL_CHANNEL_PROOF_SEQUENCE,
    TerminalChannel,
    TerminalChannelStatus,
)


def evidence(state: str) -> dict[str, object]:
    return {
        "session_owned": {"owner": "test"},
        "pty_connected": {"transport": "test-pty"},
        "vt_output_received": {"byte_count": 4},
        "rendered": {"render_source": "test-native-terminal"},
        "input_accepted": {"request_id": "req-1"},
        "input_delivered": {"delivery_method": "test-pty"},
        "input_echoed": {"marker": "AUGEN_HAENDE_PROBE_TEST"},
        "state_observed": {"capture_method": "test-readback"},
        "audited": {"audit_sequence": 9},
    }[state]


class TerminalChannelTests(unittest.TestCase):
    def test_requires_exact_order_and_evidence(self) -> None:
        channel = TerminalChannel("channel-1", "terminal-1")
        for state in TERMINAL_CHANNEL_PROOF_SEQUENCE:
            event = channel.advance(state, evidence(state))
            self.assertEqual(event.state, state)
        self.assertEqual(channel.status, TerminalChannelStatus.COMPLETED)
        self.assertEqual(channel.next_state, None)
        self.assertEqual(channel.to_dict()["proofs"], list(TERMINAL_CHANNEL_PROOF_SEQUENCE))

    def test_wrong_order_blocks_fail_closed(self) -> None:
        channel = TerminalChannel("channel-2", "terminal-2")
        with self.assertRaisesRegex(RuntimeError, "expected:session_owned"):
            channel.advance("pty_connected", evidence("pty_connected"))
        self.assertEqual(channel.status, TerminalChannelStatus.BLOCKED)
        self.assertEqual(channel.last_error, "expected:session_owned:received:pty_connected")

    def test_missing_render_proof_does_not_become_terminal_pass(self) -> None:
        channel = TerminalChannel("channel-3", "terminal-3")
        channel.advance("session_owned", evidence("session_owned"))
        channel.advance("pty_connected", evidence("pty_connected"))
        channel.advance("vt_output_received", evidence("vt_output_received"))
        with self.assertRaisesRegex(RuntimeError, "missing_evidence:rendered:render_source"):
            channel.advance("rendered")
        self.assertEqual(channel.status, TerminalChannelStatus.BLOCKED)
