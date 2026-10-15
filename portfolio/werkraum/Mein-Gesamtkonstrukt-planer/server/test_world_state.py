#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from run_state import (
    InvalidRunTransition,
    RunVersionConflict,
    create_run,
    read_run,
    transition_run,
)
from world_state import RevisionConflict, WorldStateStore, atomic_json, state_hash


PROJECT_ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
REAL_CURRENT = PROJECT_ROOT / "data" / "current.json"
LOOP_KOERPER = "koerper-726ca2ff-86b0-4aef-ae39-9dd3c79b2406"


class WorldStateRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gkos-world-state-")
        self.root = Path(self.tmp.name)
        self.current = self.root / "current.json"
        self.lock = self.root / ".state.lock"
        self.events = self.root / "world_events"
        shutil.copy2(REAL_CURRENT, self.current)

        # Add a synthetic future field to the COPY only. This proves the helper
        # preserves unknown top-level state instead of reconstructing a whitelist.
        wrapper = json.loads(self.current.read_text(encoding="utf-8"))
        wrapper["state"]["futureUnknownFacet"] = {
            "mustSurvive": True,
            "nested": [1, 2, 3],
        }
        wrapper["sha256"] = state_hash(wrapper["state"])
        atomic_json(self.current, wrapper)
        self.base_revision = int(wrapper["serverRevision"])
        self.store = WorldStateStore(self.current, self.lock, self.events)

    def tearDown(self):
        self.tmp.cleanup()

    def test_world_commit_preserves_unknown_state_and_bumps_once(self):
        before = self.store.read_wrapper()

        def mutate(state):
            state["probeFacet"] = {"alive": True}
            return {"probe": "ok"}

        result = self.store.commit(
            mutate,
            event_type="probe.changed",
            event_data={"target": "copy-only"},
            actor={"stream": "gpt", "role": "tester"},
            expected_server_revision=self.base_revision,
        )

        after = result.wrapper
        self.assertEqual(after["serverRevision"], self.base_revision + 1)
        self.assertTrue(after["state"]["futureUnknownFacet"]["mustSurvive"])
        self.assertEqual(after["state"]["probeFacet"], {"alive": True})
        self.assertEqual(after["sha256"], state_hash(after["state"]))
        self.assertEqual(after["state"]["worldEvents"][-1]["type"], "probe.changed")
        self.assertTrue(result.event_log_written)
        self.assertNotEqual(before["sha256"], after["sha256"])

    def test_run_lives_separately_from_koerper_and_wait_has_scope(self):
        run = create_run(
            koerper_ref=LOOP_KOERPER,
            goal_ref="object-80b6d904-3571-4697-bced-12888febce15",
            actor={"stream": "claude", "instance": "test-session", "role": "worker"},
            phase="prepared",
            current_node_ref="n1",
            run_id="run-copy-loop-test",
            store=self.store,
            expected_server_revision=self.base_revision,
        )
        self.assertEqual(run["phase"], "prepared")
        self.assertEqual(run["version"], 1)
        self.assertEqual(run["koerperRef"], LOOP_KOERPER)

        run = transition_run(
            run["id"],
            phase="running",
            current_node_ref="n1",
            native_event_ref="claude:test:tool_use:1",
            expected_run_version=1,
            store=self.store,
        )
        self.assertEqual(run["phase"], "running")
        self.assertEqual(run["version"], 2)

        run = transition_run(
            run["id"],
            phase="waiting",
            wait={
                "reason": "human_approval",
                "on": "rfsc-copy-test",
                "resolvableBy": "daniel",
                "scope": "action",
            },
            expected_run_version=2,
            store=self.store,
        )
        self.assertEqual(run["phase"], "waiting")
        self.assertEqual(run["version"], 3)
        self.assertEqual(run["wait"]["scope"], "action")
        self.assertEqual(run["currentNodeRef"], "n1")

        wrapper = self.store.read_wrapper()
        self.assertEqual(wrapper["serverRevision"], self.base_revision + 3)
        self.assertTrue(wrapper["state"]["futureUnknownFacet"]["mustSurvive"])
        self.assertEqual(len(wrapper["state"]["runs"]), 1)
        self.assertEqual(
            [e["type"] for e in wrapper["state"]["worldEvents"][-3:]],
            ["run.created", "run.transitioned", "run.transitioned"],
        )

        log = self.events / wrapper["updatedAt"][:10]
        # Filename has .ndjson; keep assertion explicit instead of relying on glob order.
        log = log.with_suffix(".ndjson")
        self.assertTrue(log.exists())
        self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 3)

    def test_stale_run_version_is_rejected_without_mutation(self):
        run = create_run(
            koerper_ref=LOOP_KOERPER,
            phase="prepared",
            current_node_ref="n1",
            run_id="run-stale-test",
            store=self.store,
        )
        run = transition_run(
            run["id"],
            phase="running",
            expected_run_version=1,
            store=self.store,
        )
        before = self.current.read_bytes()
        with self.assertRaises(RunVersionConflict):
            transition_run(
                run["id"],
                phase="waiting",
                wait={"reason": "human_approval"},
                expected_run_version=1,
                store=self.store,
            )
        self.assertEqual(self.current.read_bytes(), before)
        self.assertEqual(read_run(run["id"], self.store)["version"], 2)

    def test_terminal_run_cannot_silently_restart(self):
        run = create_run(
            koerper_ref=LOOP_KOERPER,
            phase="prepared",
            run_id="run-terminal-test",
            store=self.store,
        )
        run = transition_run(
            run["id"],
            phase="running",
            expected_run_version=1,
            store=self.store,
        )
        run = transition_run(
            run["id"],
            phase="completed",
            expected_run_version=2,
            evidence_ref="sha256:copy-proof",
            store=self.store,
        )
        self.assertEqual(run["phase"], "completed")
        self.assertIsNotNone(run["completedAt"])
        before = self.current.read_bytes()
        with self.assertRaises(InvalidRunTransition):
            transition_run(
                run["id"],
                phase="running",
                expected_run_version=3,
                store=self.store,
            )
        self.assertEqual(self.current.read_bytes(), before)

    def test_waiting_requires_reason(self):
        with self.assertRaises(InvalidRunTransition):
            create_run(
                koerper_ref=LOOP_KOERPER,
                phase="waiting",
                wait={},
                store=self.store,
            )

    def test_server_revision_conflict_rejects_copy_mutation(self):
        before = self.current.read_bytes()
        with self.assertRaises(RevisionConflict):
            self.store.commit(
                lambda state: state.update({"shouldNotExist": True}),
                event_type="probe.conflict",
                expected_server_revision=self.base_revision - 1,
            )
        self.assertEqual(self.current.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
