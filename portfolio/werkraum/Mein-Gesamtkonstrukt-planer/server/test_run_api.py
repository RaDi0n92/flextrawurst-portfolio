#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import django
from django.test import RequestFactory

django.setup()

import run_api
from world_state import WorldStateStore


PROJECT_ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
REAL_CURRENT = PROJECT_ROOT / "data" / "current.json"
LOOP_KOERPER = "koerper-726ca2ff-86b0-4aef-ae39-9dd3c79b2406"


class RunApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gkos-run-api-")
        self.root = Path(self.tmp.name)
        self.current = self.root / "current.json"
        shutil.copy2(REAL_CURRENT, self.current)
        self.store = WorldStateStore(
            self.current,
            self.root / ".state.lock",
            self.root / "world_events",
        )
        self.old_store = run_api.STORE
        run_api.STORE = self.store
        self.rf = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_staff=True)

    def tearDown(self):
        run_api.STORE = self.old_store
        self.tmp.cleanup()

    def request(self, method: str, path: str, payload: dict | None = None):
        if method == "GET":
            req = self.rf.get(path, data=payload or {})
        else:
            req = self.rf.post(
                path,
                data=json.dumps(payload or {}),
                content_type="application/json",
            )
        req.user = self.user
        return req

    @staticmethod
    def body(response):
        return json.loads(response.content.decode("utf-8"))

    def test_create_read_wait_resume_review_complete(self):
        base_revision = self.store.read_wrapper()["serverRevision"]
        response = run_api.run_list_create(
            self.request(
                "POST",
                "/runs/",
                {
                    "runId": "run-api-loop",
                    "koerperRef": LOOP_KOERPER,
                    "goalRef": "goal-api-test",
                    "scopeRefs": ["haufen-planer", "haufen-realfs"],
                    "actor": {"stream": "gpt", "instance": "api-test", "role": "worker"},
                    "phase": "prepared",
                    "currentNodeRef": "n1",
                    "expectedServerRevision": base_revision,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 201, data)
        self.assertEqual(data["run"]["version"], 1)
        self.assertEqual(data["serverRevision"], base_revision + 1)

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-loop",
                    "phase": "running",
                    "currentNodeRef": "n2",
                    "nativeEventRef": "tool:gpt:1",
                    "expectedRunVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["run"]["phase"], "running")
        self.assertEqual(data["run"]["currentNodeRef"], "n2")
        self.assertEqual(data["run"]["version"], 2)

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-loop",
                    "phase": "waiting",
                    "wait": {
                        "reason": "human_approval",
                        "on": "rfsc-test",
                        "resolvableBy": "daniel",
                        "scope": "action",
                    },
                    "expectedRunVersion": 2,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["run"]["phase"], "waiting")
        self.assertEqual(data["run"]["wait"]["scope"], "action")
        self.assertEqual(data["run"]["version"], 3)

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-loop",
                    "phase": "running",
                    "wait": None,
                    "expectedRunVersion": 3,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertIsNone(data["run"]["wait"])
        self.assertEqual(data["run"]["version"], 4)

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-loop",
                    "phase": "review",
                    "currentNodeRef": "n-review",
                    "expectedRunVersion": 4,
                },
            )
        )
        self.assertEqual(response.status_code, 200, self.body(response))

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-loop",
                    "phase": "completed",
                    "evidenceRef": "sha256:api-proof",
                    "expectedRunVersion": 5,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["run"]["phase"], "completed")
        self.assertIn("sha256:api-proof", data["run"]["evidenceRefs"])
        self.assertEqual(data["serverRevision"], base_revision + 6)

        response = run_api.run_list_create(
            self.request("GET", "/runs/", {"id": "run-api-loop"})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["run"]["version"], 6)

    def test_stale_run_version_returns_409_and_preserves_state(self):
        response = run_api.run_list_create(
            self.request(
                "POST",
                "/runs/",
                {"runId": "run-api-stale", "koerperRef": LOOP_KOERPER},
            )
        )
        self.assertEqual(response.status_code, 201, self.body(response))

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-stale",
                    "phase": "running",
                    "expectedRunVersion": 1,
                },
            )
        )
        self.assertEqual(response.status_code, 200, self.body(response))
        before = self.current.read_bytes()

        response = run_api.run_transition(
            self.request(
                "POST",
                "/runs/transition/",
                {
                    "runId": "run-api-stale",
                    "phase": "waiting",
                    "wait": {"reason": "approval"},
                    "expectedRunVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 409, data)
        self.assertEqual(data["error"], "run_version_conflict")
        self.assertEqual(data["actualRunVersion"], 2)
        self.assertEqual(self.current.read_bytes(), before)

    def test_phase_filter_lists_only_matching_runs(self):
        for run_id, phase in [("r-prepared", "prepared"), ("r-running", "running")]:
            response = run_api.run_list_create(
                self.request(
                    "POST",
                    "/runs/",
                    {"runId": run_id, "koerperRef": LOOP_KOERPER, "phase": phase},
                )
            )
            self.assertEqual(response.status_code, 201, self.body(response))

        response = run_api.run_list_create(
            self.request("GET", "/runs/", {"phase": "running"})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual([run["id"] for run in data["runs"]], ["r-running"])


if __name__ == "__main__":
    unittest.main()
