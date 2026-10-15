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

import real_fs_api
from run_state import create_run, read_run
from world_state import WorldStateStore


PROJECT_ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
REAL_CURRENT = PROJECT_ROOT / "data" / "current.json"


class RealFsApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gkos-realfs-api-")
        self.root = Path(self.tmp.name).resolve()
        self.data = self.root / "data"
        self.data.mkdir(parents=True)
        self.current = self.data / "current.json"
        shutil.copy2(REAL_CURRENT, self.current)
        self.base_revision = json.loads(self.current.read_text(encoding="utf-8"))["serverRevision"]
        self.workspace = self.root / "allowed"
        self.workspace.mkdir()

        self.old = {
            name: getattr(real_fs_api, name)
            for name in [
                "ROOT",
                "ALLOWLIST_FILE",
                "ALLOWLIST_LOCK",
                "PENDING_FILE",
                "PENDING_LOCK",
                "BACKUPS_DIR",
                "ALLOWED_ROOT",
                "DEFAULT_STORE",
            ]
        }
        real_fs_api.ROOT = self.root
        real_fs_api.ALLOWLIST_FILE = self.data / "allowlist.json"
        real_fs_api.ALLOWLIST_LOCK = self.data / ".allowlist.lock"
        real_fs_api.PENDING_FILE = self.data / "pending.json"
        real_fs_api.PENDING_LOCK = self.data / ".pending.lock"
        real_fs_api.BACKUPS_DIR = self.data / "backups"
        real_fs_api.ALLOWED_ROOT = self.root
        real_fs_api.DEFAULT_STORE = WorldStateStore(
            self.current,
            self.data / ".state.lock",
            self.data / "world_events",
        )
        self.rf = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True, is_staff=True)

    def tearDown(self):
        for name, value in self.old.items():
            setattr(real_fs_api, name, value)
        self.tmp.cleanup()

    def request(self, method: str, path: str, payload: dict | None = None):
        if method == "GET":
            request = self.rf.get(path, data=payload or {})
        else:
            request = self.rf.post(
                path,
                data=json.dumps(payload or {}),
                content_type="application/json",
            )
        request.user = self.user
        return request

    @staticmethod
    def body(response):
        return json.loads(response.content.decode("utf-8"))

    def add_allowed_workspace(self):
        response = real_fs_api.real_fs_add(
            self.request("POST", "/add", {"path": str(self.workspace), "label": "Temp"})
        )
        self.assertEqual(response.status_code, 200, self.body(response))
        data = self.body(response)
        self.assertTrue(data["worldSignal"]["ok"])
        return data["entry"]["id"]

    def propose(self, entry_id: str, content: str, path: str = "target.txt", extra: dict | None = None):
        payload = {
            "id": entry_id,
            "path": path,
            "content": content,
            "proposedBy": "GPT Endpoint-Test",
        }
        payload.update(extra or {})
        response = real_fs_api.real_fs_propose_write(
            self.request(
                "POST",
                "/propose",
                payload,
            )
        )
        self.assertEqual(response.status_code, 200, self.body(response))
        data = self.body(response)
        self.assertTrue(data["worldSignal"]["ok"])
        return data["changeId"]

    def test_full_stale_then_reproposal_then_confirmed_effect(self):
        entry_id = self.add_allowed_workspace()
        target = self.workspace / "target.txt"

        stale_change = self.propose(entry_id, "B")
        pending = json.loads(real_fs_api.PENDING_FILE.read_text(encoding="utf-8"))
        proposal = next(item for item in pending if item["id"] == stale_change)
        self.assertFalse(proposal["expectedTarget"]["exists"])
        self.assertEqual(proposal["approvalStatus"], "pending")
        self.assertEqual(proposal["effectStatus"], "not_started")

        # Another actor changes the world after proposal creation.
        target.write_text("C", encoding="utf-8")
        response = real_fs_api.real_fs_approve(
            self.request("POST", "/approve", {"id": stale_change})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 409, data)
        self.assertEqual(data["error"], "stale_target")
        self.assertEqual(target.read_text(encoding="utf-8"), "C")
        stale_saved = next(
            item
            for item in json.loads(real_fs_api.PENDING_FILE.read_text(encoding="utf-8"))
            if item["id"] == stale_change
        )
        self.assertEqual(stale_saved["status"], "pending")
        self.assertEqual(stale_saved["effectStatus"], "stale")
        self.assertTrue(data["worldSignal"]["ok"])

        # Re-propose against the new real target and approve that exact basis.
        fresh_change = self.propose(entry_id, "D")
        response = real_fs_api.real_fs_approve(
            self.request("POST", "/approve", {"id": fresh_change})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertEqual(data["effectStatus"], "confirmed")
        self.assertEqual(target.read_text(encoding="utf-8"), "D")
        self.assertTrue(data["worldSignal"]["approval"]["ok"])
        self.assertTrue(data["worldSignal"]["effect"]["ok"])
        self.assertTrue(Path(data["backup"]).is_file())
        self.assertEqual(Path(data["backup"]).read_text(encoding="utf-8"), "C")

        saved = next(
            item
            for item in json.loads(real_fs_api.PENDING_FILE.read_text(encoding="utf-8"))
            if item["id"] == fresh_change
        )
        self.assertEqual(saved["status"], "approved")
        self.assertEqual(saved["approvalStatus"], "approved")
        self.assertEqual(saved["effectStatus"], "confirmed")
        self.assertEqual(saved["effect"]["target"]["sha256"], data["sha256"])

        wrapper = json.loads(self.current.read_text(encoding="utf-8"))
        # add + stale proposal + stale approval + fresh proposal + approval + effect
        self.assertEqual(wrapper["serverRevision"], self.base_revision + 6)
        self.assertEqual(
            [event["type"] for event in wrapper["state"]["worldEvents"][-6:]],
            [
                "world.connection.added",
                "approval.requested",
                "approval.stale",
                "approval.requested",
                "approval.approved",
                "effect.confirmed",
            ],
        )

    def test_proposal_correlates_to_run_without_freezing_whole_run(self):
        entry_id = self.add_allowed_workspace()
        run = create_run(
            koerper_ref="koerper-correlation-test",
            goal_ref="goal-correlation-test",
            phase="running",
            current_node_ref="n1",
            run_id="run-correlation-test",
            store=real_fs_api.DEFAULT_STORE,
        )
        self.assertEqual(run["version"], 1)

        change_id = self.propose(
            entry_id,
            "correlated write",
            "correlated.txt",
            {
                "runRef": run["id"],
                "expectedRunVersion": 1,
                "nodeRef": "n1",
                "goalRef": "goal-correlation-test",
            },
        )
        pending = json.loads(real_fs_api.PENDING_FILE.read_text(encoding="utf-8"))
        change = next(item for item in pending if item["id"] == change_id)
        self.assertEqual(
            change["correlation"],
            {
                "runRef": "run-correlation-test",
                "runVersionAtProposal": 1,
                "nodeRef": "n1",
                "goalRef": "goal-correlation-test",
            },
        )

        # Action-level approval wait does NOT silently freeze the whole Run.
        still_running = read_run(run["id"], store=real_fs_api.DEFAULT_STORE)
        self.assertEqual(still_running["phase"], "running")
        self.assertIsNone(still_running["wait"])
        self.assertEqual(still_running["version"], 1)

        wrapper = json.loads(self.current.read_text(encoding="utf-8"))
        event = wrapper["state"]["worldEvents"][-1]
        self.assertEqual(event["type"], "approval.requested")
        self.assertEqual(event["data"]["correlation"]["runRef"], run["id"])

        before_pending = real_fs_api.PENDING_FILE.read_bytes()
        response = real_fs_api.real_fs_propose_write(
            self.request(
                "POST",
                "/propose",
                {
                    "id": entry_id,
                    "path": "too-old.txt",
                    "content": "must not become a proposal",
                    "proposedBy": "GPT Endpoint-Test",
                    "runRef": run["id"],
                    "expectedRunVersion": 0,
                    "nodeRef": "n1",
                },
            )
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 409, data)
        self.assertEqual(data["error"], "run_version_conflict")
        self.assertEqual(data["actualRunVersion"], 1)
        self.assertEqual(real_fs_api.PENDING_FILE.read_bytes(), before_pending)

    def test_reject_is_durable_world_transition_without_effect(self):
        entry_id = self.add_allowed_workspace()
        change_id = self.propose(entry_id, "never written", "reject.txt")
        response = real_fs_api.real_fs_reject(
            self.request("POST", "/reject", {"id": change_id})
        )
        data = self.body(response)
        self.assertEqual(response.status_code, 200, data)
        self.assertTrue(data["worldSignal"]["ok"])
        self.assertFalse((self.workspace / "reject.txt").exists())
        saved = next(
            item
            for item in json.loads(real_fs_api.PENDING_FILE.read_text(encoding="utf-8"))
            if item["id"] == change_id
        )
        self.assertEqual(saved["status"], "rejected")
        self.assertEqual(saved["approvalStatus"], "rejected")
        self.assertEqual(saved["effectStatus"], "not_started")


if __name__ == "__main__":
    unittest.main()
