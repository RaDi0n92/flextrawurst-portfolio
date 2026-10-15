#!/usr/bin/env python3
from __future__ import annotations

import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path

from real_fs_store import (
    JsonListStore,
    RealFsChangeStore,
    RealFsStoreError,
    StaleTarget,
    atomic_text_write,
    sha256_text,
    target_fingerprint,
)


def _concurrent_append_worker(path: str, lock_path: str, prefix: str, count: int) -> None:
    store = JsonListStore(Path(path), Path(lock_path))
    for index in range(count):
        item = {"id": f"{prefix}-{index}"}

        def mutate(entries, item=item):
            entries.append(item)

        store.mutate(mutate)


class RealFsStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gkos-realfs-")
        self.root = Path(self.tmp.name)
        self.pending = self.root / "pending.json"
        self.pending_lock = self.root / "pending.lock"
        self.changes = RealFsChangeStore(self.pending, self.pending_lock)
        self.target = self.root / "target.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def _proposal(self, change_id: str, expected_target: dict | None):
        change = {
            "id": change_id,
            "status": "pending",
            "approvalStatus": "pending",
            "effectStatus": "not_started",
            "targetPath": str(self.target),
            "proposedContent": "B",
            "proposedContentSha256": sha256_text("B"),
        }
        if expected_target is not None:
            change["expectedTarget"] = expected_target
        return self.changes.add(change)

    def test_fingerprint_detects_changed_existing_file(self):
        self.target.write_text("A", encoding="utf-8")
        before = target_fingerprint(self.target)
        self.assertEqual(before["sha256"], sha256_text("A"))
        self.target.write_text("C", encoding="utf-8")
        after = target_fingerprint(self.target)
        self.assertNotEqual(before["sha256"], after["sha256"])

    def test_stale_approval_is_persisted_and_does_not_claim_effect(self):
        self.target.write_text("A", encoding="utf-8")
        self._proposal("change-stale", target_fingerprint(self.target))
        self.target.write_text("C", encoding="utf-8")

        with self.assertRaises(StaleTarget):
            self.changes.claim_approval(
                "change-stale",
                actual_target=target_fingerprint(self.target),
            )

        saved = self.changes.get("change-stale")
        self.assertEqual(saved["status"], "pending")
        self.assertEqual(saved["approvalStatus"], "pending")
        self.assertEqual(saved["effectStatus"], "stale")
        self.assertEqual(saved["staleActualTarget"]["sha256"], sha256_text("C"))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "C")

    def test_missing_target_becoming_file_is_stale(self):
        expected = target_fingerprint(self.target)
        self.assertFalse(expected["exists"])
        self._proposal("change-created-elsewhere", expected)
        self.target.write_text("someone else", encoding="utf-8")

        with self.assertRaises(StaleTarget):
            self.changes.claim_approval(
                "change-created-elsewhere",
                actual_target=target_fingerprint(self.target),
            )

        saved = self.changes.get("change-created-elsewhere")
        self.assertEqual(saved["effectStatus"], "stale")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "someone else")

    def test_approval_and_effect_are_distinct_states(self):
        self.target.write_text("A", encoding="utf-8")
        self._proposal("change-ok", target_fingerprint(self.target))

        claimed = self.changes.claim_approval(
            "change-ok",
            actual_target=target_fingerprint(self.target),
        )
        self.assertEqual(claimed["status"], "approved")
        self.assertEqual(claimed["approvalStatus"], "approved")
        self.assertEqual(claimed["effectStatus"], "running")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "A")

        atomic_text_write(self.target, "B")
        effect = target_fingerprint(self.target)
        finished = self.changes.finish_effect(
            "change-ok",
            effect_status="confirmed",
            effect={"target": effect},
            backup="copy-only-backup",
        )
        self.assertEqual(finished["effectStatus"], "confirmed")
        self.assertEqual(finished["effect"]["target"]["sha256"], sha256_text("B"))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "B")

    def test_legacy_pending_change_without_expected_target_must_be_reproposed(self):
        self.target.write_text("A", encoding="utf-8")
        self._proposal("legacy", None)
        before = self.pending.read_bytes()
        with self.assertRaisesRegex(RealFsStoreError, "proposal_missing_expected_target"):
            self.changes.claim_approval(
                "legacy",
                actual_target=target_fingerprint(self.target),
            )
        self.assertEqual(self.pending.read_bytes(), before)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "A")

    def test_json_list_lock_prevents_lost_updates_between_processes(self):
        path = self.root / "concurrent.json"
        lock = self.root / "concurrent.lock"
        path.write_text("[]\n", encoding="utf-8")

        ctx = multiprocessing.get_context("fork")
        processes = [
            ctx.Process(
                target=_concurrent_append_worker,
                args=(str(path), str(lock), f"p{index}", 35),
            )
            for index in range(4)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(15)
            self.assertEqual(process.exitcode, 0)

        entries = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 140)
        self.assertEqual(len({entry["id"] for entry in entries}), 140)


if __name__ == "__main__":
    unittest.main()
