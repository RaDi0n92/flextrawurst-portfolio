import unittest

from augen_haende_bridge.bridge_runtime import BridgeRuntime
from client_vps.bridge_agent import build_inventory_agent
from augen_haende_bridge.target_registry import PlatformUnavailableAdapter, TargetRegistry


class BridgeAgentTests(unittest.TestCase):
    def test_inventory_agent_is_explicit_and_does_not_connect_on_build(self):
        registry = TargetRegistry(PlatformUnavailableAdapter())
        runtime, returned_registry = build_inventory_agent(
            "ws://127.0.0.1:9880",
            "a" * 32,
            registry=registry,
        )

        self.assertIs(returned_registry, registry)
        self.assertIsInstance(runtime, BridgeRuntime)
        self.assertFalse(runtime.connected)
        self.assertIs(getattr(runtime.inventory_provider, "__self__", None), registry)
        self.assertEqual(getattr(runtime.inventory_provider, "__name__", None), "bridge_inventory")


if __name__ == "__main__":
    unittest.main()
