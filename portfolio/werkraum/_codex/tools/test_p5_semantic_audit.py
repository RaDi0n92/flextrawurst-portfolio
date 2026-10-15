#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("p5_semantic_audit.py")
spec = importlib.util.spec_from_file_location("p5_semantic_audit", SOURCE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class P5GateTests(unittest.TestCase):
    def test_changed_character_stays_ambiguous_without_raw_p4_text(self):
        status, reason = module.classify_structural(
            role="user",
            p4_roles=["user"],
            normalized_length=11,
            p4_text_lengths=[11],
            candidate_variant_count=1,
        )
        self.assertEqual(status, "ambiguous")
        self.assertIn("raw_text", reason)

    def test_role_change_is_red(self):
        status, _ = module.classify_structural(
            role="assistant",
            p4_roles=["user"],
            normalized_length=11,
            p4_text_lengths=[11],
            candidate_variant_count=1,
        )
        self.assertEqual(status, "role-mismatch")

    def test_swapped_order_is_red(self):
        self.assertEqual(
            module.classify_order(p4_order=["a", "c", "b"], vps_order=["a", "b", "c"], duplicate_ids=[]),
            "order-mismatch",
        )

    def test_missing_message_is_red(self):
        self.assertEqual(
            module.classify_presence(stable_id_in_vps=True, stable_id_in_p4=False),
            "missing-live",
        )
        self.assertEqual(
            module.classify_presence(stable_id_in_vps=False, stable_id_in_p4=True),
            "missing-vps",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
