from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path

import mcp_atlas_stream_log as stream_log


class StreamLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.previous_root = stream_log.ROOT
        stream_log.ROOT = Path(self.temp.name) / "strom_mitschriften"

    def tearDown(self) -> None:
        stream_log.ROOT = self.previous_root
        self.temp.cleanup()

    def test_all_known_streams_connect_and_write(self) -> None:
        aliases = {
            "claude-code": "claude",
            "claudeweb": "claudeweb",
            "chatgpt": "chatgpt",
            "codex": "codex",
            "gemini": "gemini",
            "kimi": "kimi",
            "glm": "glm",
        }
        for supplied, expected in aliases.items():
            session_id = f"session-{expected}"
            connected = stream_log.connect_stream(stream_id=supplied, session_id=session_id)
            self.assertTrue(connected["connected"])
            self.assertEqual(connected["connection"]["stream_id"], expected)
            written = stream_log.append_entry(
                session_id=session_id,
                content=f"Omega-Mitschrift von {expected}",
                kind="decision",
                title="Verbindungstest",
                idempotency_key="write-1",
            )
            self.assertTrue(written["write_verified"])
            duplicate = stream_log.append_entry(
                session_id=session_id,
                content=f"Omega-Mitschrift von {expected}",
                kind="decision",
                title="Verbindungstest",
                idempotency_key="write-1",
            )
            self.assertTrue(duplicate["duplicate"])
            chain = stream_log.validate_chain(stream_id=expected)
            self.assertEqual(chain["event_count"], 1)

        status = stream_log.stream_status()
        self.assertEqual(status["event_count"], 7)
        self.assertEqual(set(status["streams"]), set(stream_log.STREAM_IDS))

    def test_connection_is_idempotent_and_cannot_be_relabelled(self) -> None:
        first = stream_log.connect_stream(stream_id="claudecode", session_id="same-session")
        second = stream_log.connect_stream(stream_id="claude", session_id="same-session")
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])
        with self.assertRaises(stream_log.StreamLogError):
            stream_log.connect_stream(stream_id="gemini", session_id="same-session")

    def test_search_and_automatic_tool_event(self) -> None:
        stream_log.connect_stream(stream_id="chatgpt", session_id="s-chatgpt")
        result = stream_log.record_tool_event(
            session_id="s-chatgpt",
            tool_name="vps.read_file",
            history_event={"event_id": "evt-1", "event_hash": "abc"},
            target="/root/werkraum/Flextrawurst.md",
            status="success",
            completeness="complete",
        )
        self.assertIsNotNone(result)
        found = stream_log.search_entries(query="Flextrawurst", stream_id="chatgpt")
        self.assertEqual(found["count"], 1)
        self.assertEqual(found["results"][0]["kind"], "mcp_tool_action")
        duplicate = stream_log.record_tool_event(
            session_id="s-chatgpt",
            tool_name="vps.read_file",
            history_event={"event_id": "evt-1", "event_hash": "abc"},
            target="/root/werkraum/Flextrawurst.md",
            status="success",
            completeness="complete",
        )
        self.assertTrue(duplicate["duplicate"])

    def test_concurrent_append_keeps_hash_chain_valid(self) -> None:
        stream_log.connect_stream(stream_id="gemini", session_id="s-gemini")
        errors: list[Exception] = []

        def worker(index: int) -> None:
            try:
                stream_log.append_entry(
                    session_id="s-gemini",
                    content=f"Parallelspur {index}",
                    kind="parallel-test",
                    idempotency_key=f"parallel-{index}",
                )
            except Exception as exc:  # pragma: no cover - only used for thread collection
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        chain = stream_log.validate_chain(stream_id="gemini")
        self.assertEqual(chain["event_count"], 20)

    def test_unknown_stream_and_unconnected_write_are_blocked(self) -> None:
        with self.assertRaises(stream_log.StreamLogError):
            stream_log.connect_stream(stream_id="grok", session_id="s-grok")
        with self.assertRaises(stream_log.StreamLogError):
            stream_log.append_entry(session_id="not-connected", content="Nein")

    def test_files_are_plain_searchable_primary_sources(self) -> None:
        stream_log.connect_stream(stream_id="kimi", session_id="s-kimi")
        written = stream_log.append_entry(
            session_id="s-kimi",
            content="Ein einzigartiger Suchbegriff namens Zimtzunge-4488.",
            source_refs=["file:/root/KIMI.md"],
        )
        log_path = Path(written["log_path"])
        self.assertTrue(log_path.is_file())
        raw = log_path.read_text(encoding="utf-8")
        self.assertIn("Zimtzunge-4488", raw)
        parsed = json.loads(raw.splitlines()[-1])
        self.assertEqual(parsed["content_sha256"], written["record"]["content_sha256"])
        self.assertTrue((stream_log.ROOT / "START_HIER.md").is_file())


if __name__ == "__main__":
    unittest.main()
