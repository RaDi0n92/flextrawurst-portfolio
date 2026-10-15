import os
import unittest
from unittest.mock import patch

from client_vps.bridge_server import (
    DEFAULT_PORT,
    build_principals,
    _token,
)


class BridgeServerContractTests(unittest.TestCase):
    def test_default_port_is_new_and_loopback_handoff_port(self):
        self.assertEqual(DEFAULT_PORT, 19880)

    def test_fixed_principals_are_separate_and_readback_only_on_agent(self):
        desktop, agent = build_principals(
            desktop_token="d" * 40,
            agent_token="a" * 40,
        )
        self.assertEqual((desktop.session_id, desktop.peer_id, desktop.target_id),
                         ("desktop", "agent", "desktop-main"))
        self.assertTrue(desktop.can_publish_frames)
        self.assertTrue(desktop.can_request_inventory)
        self.assertFalse(desktop.can_publish_inventory)
        self.assertTrue(desktop.can_control_terminals)
        self.assertFalse(desktop.can_serve_terminals)
        self.assertTrue(agent.can_serve_terminals)
        self.assertFalse(agent.can_control_terminals)
        self.assertEqual((agent.session_id, agent.peer_id, agent.target_id),
                         ("agent", "desktop", "desktop-main"))
        self.assertTrue(agent.can_publish_inventory)
        self.assertFalse(agent.can_publish_frames)
        self.assertFalse(agent.can_request_inventory)

    def test_tokens_are_required_and_never_fallback_to_old_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "BRIDGE_DESKTOP_TOKEN"):
                _token("BRIDGE_DESKTOP_TOKEN")

    def test_tokens_must_be_distinct(self):
        with self.assertRaisesRegex(ValueError, "distinct_tokens_required"):
            build_principals(desktop_token="x" * 40, agent_token="x" * 40)

    def test_short_tokens_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "strong_tokens_required"):
            build_principals(desktop_token="d" * 31, agent_token="a" * 40)


if __name__ == "__main__":
    unittest.main()
