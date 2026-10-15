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

import goal_api
from world_state import WorldStateStore


PROJECT_ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
REAL_CURRENT = PROJECT_ROOT / "data" / "current.json"
PROJECT_OBJECT = "object-80b6d904-3571-4697-bced-12888febce15"


class GoalApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gkos-goal-api-")
        self.root = Path(self.tmp.name)
        self.current = self.root / "current.json"
        shutil.copy2(REAL_CURRENT, self.current)
        self.store = WorldStateStore(
            self.current,
            self.root / ".state.lock",
            self.root / "world_events",
        )
        self.old_store = goal_api.STORE
        goal_api.STORE = self.store
        self.rf = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_staff=True, username="goal-test")

    def tearDown(self):
        goal_api.STORE = self.old_store
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

    def create_goal(self, goal_id="goal-api-test"):
        base = self.store.read_wrapper()["serverRevision"]
        response = goal_api.goal_list_create(
            self.request(
                "POST",
                "/goals/",
                {
                    "goalId": goal_id,
                    "constructRef": PROJECT_OBJECT,
                    "title": "Lebender Draht ist belegbar",
                    "desiredState": "Ein echter Lauf kann Wirkung und Review belegt durchlaufen.",
                    "scopeRefs": ["haufen-planer", "haufen-realfs"],
                    "criteria": [
                        {"id": "c-run", "statement": "Run bleibt nach Reload erhalten."},
                        {"id": "c-effect", "statement": "Eine Wirkung besitzt einen realen Beleg."},
                    ],
                    "expectedServerRevision": base,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 201, data)
        self.assertEqual(data["serverRevision"], base + 1)
        return data["goal"]

    def test_goal_requires_evidence_before_achievement(self):
        goal = self.create_goal()
        self.assertEqual(goal["status"], "active")
        self.assertEqual(goal["version"], 1)

        # Cannot declare achieved while criteria are unknown.
        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "achieved",
                    "expectedGoalVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 409, data)
        self.assertEqual(data["error"], "achieved_requires_all_criteria_met")

        # Marking met without evidence is also rejected.
        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "criterionId": "c-run",
                    "criterionStatus": "met",
                    "expectedGoalVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 400, data)
        self.assertEqual(data["error"], "met_criterion_requires_evidence")

        # Evidence-bound criteria can be satisfied explicitly.
        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "criterionId": "c-run",
                    "criterionStatus": "met",
                    "criterionEvidenceRef": "reload:run-visible",
                    "expectedGoalVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["goal"]["version"], 2)

        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "criterionId": "c-effect",
                    "criterionStatus": "met",
                    "criterionEvidenceRef": "sha256:effect-proof",
                    "expectedGoalVersion": 2,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["goal"]["version"], 3)

        # Now and only now can the durable Goal become achieved.
        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "achieved",
                    "evidenceRef": "review:accepted",
                    "expectedGoalVersion": 3,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["goal"]["status"], "achieved")
        self.assertEqual(data["goal"]["version"], 4)
        self.assertEqual(data["goal"]["evidenceRefs"], ["review:accepted"])
        self.assertIsNotNone(data["goal"]["achievedAt"])

        wrapper = self.store.read_wrapper()
        self.assertEqual(
            [event["type"] for event in wrapper["state"]["worldEvents"][-4:]],
            ["goal.created", "goal.updated", "goal.updated", "goal.updated"],
        )

    def test_stale_goal_version_preserves_state(self):
        goal = self.create_goal("goal-stale")
        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "paused",
                    "expectedGoalVersion": 1,
                },
            )
        )
        self.assertEqual(response.status_code, 200, self.body(response))
        before = self.current.read_bytes()

        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "active",
                    "expectedGoalVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 409, data)
        self.assertEqual(data["error"], "goal_version_conflict")
        self.assertEqual(data["actualGoalVersion"], 2)
        self.assertEqual(self.current.read_bytes(), before)

    def test_achieved_goal_reopens_only_as_needs_revision(self):
        base = self.store.read_wrapper()["serverRevision"]
        response = goal_api.goal_list_create(
            self.request(
                "POST",
                "/goals/",
                {
                    "goalId": "goal-achieved",
                    "constructRef": PROJECT_OBJECT,
                    "desiredState": "Belegter Zustand",
                    "status": "achieved",
                    "criteria": [
                        {
                            "id": "c1",
                            "statement": "Beleg liegt vor.",
                            "status": "met",
                            "evidenceRefs": ["proof:1"],
                        }
                    ],
                    "expectedServerRevision": base,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 201, data)
        goal = data["goal"]

        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "active",
                    "expectedGoalVersion": 1,
                },
            )
        )
        self.assertEqual(response.status_code, 409, self.body(response))

        response = goal_api.goal_update(
            self.request(
                "POST",
                "/goals/update/",
                {
                    "goalId": goal["id"],
                    "status": "needs_revision",
                    "expectedGoalVersion": 1,
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["goal"]["status"], "needs_revision")
        self.assertIsNone(data["goal"]["achievedAt"])

    def test_filters_by_construct_and_status(self):
        self.create_goal("g-filter-a")
        base = self.store.read_wrapper()["serverRevision"]
        response = goal_api.goal_list_create(
            self.request(
                "POST",
                "/goals/",
                {
                    "goalId": "g-filter-b",
                    "constructRef": "other-construct",
                    "desiredState": "anderes Ziel",
                    "status": "paused",
                    "expectedServerRevision": base,
                },
            )
        )
        self.assertEqual(response.status_code, 201, self.body(response))

        response = goal_api.goal_list_create(
            self.request("GET", "/goals/", {"constructRef": PROJECT_OBJECT, "status": "active"})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual([g["id"] for g in data["goals"]], ["g-filter-a"])


if __name__ == "__main__":
    unittest.main()
