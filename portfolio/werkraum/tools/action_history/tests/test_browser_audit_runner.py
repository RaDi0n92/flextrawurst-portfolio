from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.action_history import browser_audit_runner as runner


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class BrowserAuditRunnerTests(unittest.TestCase):
    def make_chat(self, root: Path, *, complete: int = 1, turns: int = 2, gaps: int = 1) -> Path:
        chat = root / "2026-08-03__Test__abcdef123456"
        chat.mkdir()
        (chat / "MANIFEST.json").write_text(json.dumps({
            "conversation_id": "abcdef12-3456-7890-abcd-ef1234567890",
            "complete_turn_count": complete,
            "turn_count": turns,
            "gap_count": gaps,
        }), encoding="utf-8")
        write_jsonl(chat / "messages.jsonl", [
            {"event_type": "message_final", "message_id": "m1", "role": "user", "content": "Hallo"},
            {"event_type": "message_final", "message_id": "m2", "role": "assistant", "content": "Welt"},
        ])
        write_jsonl(chat / "visible_stream.jsonl", [{"event_type": "visible_update", "content": "Welt"}])
        write_jsonl(chat / "capture_gaps.jsonl", [{"event_type": "capture_gap", "reason": "fixture"}] if gaps else [])
        return chat

    def test_compare_keeps_role_and_text_failures_distinct(self) -> None:
        vps = [
            {"event_type": "message_final", "message_id": "m1", "role": "user", "content": "Hallo"},
            {"event_type": "message_final", "message_id": "m2", "role": "assistant", "content": "Welt"},
        ]
        live = [
            {"key": "wrapper:1", "role": "user", "text": "Hallo"},
            {"key": "wrapper:2", "role": "thinking", "text": "Welt"},
            {"key": "wrapper:3", "role": "assistant", "text": "Extra"},
        ]
        result = runner.compare_messages(vps, live)
        self.assertEqual(result["exact_matches"], 1)
        self.assertEqual(result["role_mismatches"], 1)
        self.assertEqual(result["missing_vps"], 1)

    def test_p1_and_p2_preserve_known_gap_as_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "store"
            store.mkdir()
            self.make_chat(store)
            audits = Path(tmp) / "audits"
            inventory_dir = runner.create_inventory(store, audits, "audit-fixture")
            runner.create_audit(inventory_dir)
            report = json.loads((inventory_dir / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["partial"], 1)
            self.assertEqual(report["summary"]["complete"], 0)
            self.assertTrue(report["acceptance"]["no_false_all_green"])
            self.assertTrue((inventory_dir / "checksums.sha256").exists())
            self.assertTrue((inventory_dir / "vps-files.jsonl").exists())

    def test_matching_live_snapshot_does_not_hide_existing_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "store"
            store.mkdir()
            self.make_chat(store)
            audits = Path(tmp) / "audits"
            inventory_dir = runner.create_inventory(store, audits, "audit-fixture-live")
            snapshot = Path(tmp) / "browser.json"
            snapshot.write_text(json.dumps({"status": "ok", "tabs": [{
                "conversation_id": "abcdef12-3456-7890-abcd-ef1234567890",
                "snapshot": {"messages": [
                    {"key": "provider:m1", "role": "user", "text": "Hallo"},
                    {"key": "provider:m2", "role": "assistant", "text": "Welt"},
                ]},
            }]}), encoding="utf-8")
            runner.create_audit(inventory_dir, browser_snapshot=snapshot)
            report = json.loads((inventory_dir / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(report["results"][0]["status"], "partial")
            self.assertEqual(report["results"][0]["comparison"]["exact_matches"], 2)
            self.assertIn("manifest gap_count=1", report["results"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
