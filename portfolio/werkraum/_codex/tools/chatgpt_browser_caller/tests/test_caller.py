from __future__ import annotations

import json
import unittest

from chatgpt_browser_caller.caller import (
    CallerError,
    ChatGPTBrowserCaller,
    SlotStore,
    parse_targets,
)


class CallerTests(unittest.TestCase):
    def test_parse_targets_keeps_only_explicit_chatgpt_conversation_pages(self):
        targets = parse_targets(
            [
                {
                    "id": "chat-2",
                    "type": "page",
                    "title": "Chat B",
                    "url": "https://chatgpt.com/c/bbbbbbbb-2222",
                },
                {
                    "id": "other-page",
                    "type": "page",
                    "title": "Other site",
                    "url": "https://example.com/",
                },
                {
                    "id": "chat-not-page",
                    "type": "background_page",
                    "title": "Chat background",
                    "url": "https://chatgpt.com/c/cccccccc-3333",
                },
                {
                    "id": "chat-1",
                    "type": "page",
                    "title": "Chat A",
                    "url": "https://chatgpt.com/c/aaaaaaaa-1111",
                },
            ]
        )

        self.assertEqual([target.target_id for target in targets], ["chat-1", "chat-2"])
        self.assertEqual(targets[0].conversation_id, "aaaaaaaa-1111")

    def test_bind_requires_exact_selector_and_never_auto_binds(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            state_path = __import__("pathlib").Path(directory) / "slots.json"
            caller = ChatGPTBrowserCaller(state_path=state_path)
            caller.discover = lambda: parse_targets(
                [
                    {
                        "id": "target-1",
                        "type": "page",
                        "title": "Dedicated test chat",
                        "url": "https://chatgpt.com/c/test-1",
                    }
                ]
            )

            self.assertEqual(caller.slots(), [])
            with self.assertRaises(CallerError):
                caller.bind("chatgpt-1", "not-a-target")
            self.assertEqual(caller.slots(), [])

            bound = caller.bind("chatgpt-1", "target-1")
            self.assertTrue(bound.bound_explicitly)
            self.assertEqual(caller.slots()[0].target_id, "target-1")

    def test_store_round_trip(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "slots.json"
            store = SlotStore(path)
            self.assertEqual(store.load(), {})
            store.save({})
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["version"], 1)
            self.assertEqual(payload["slots"], {})

    def test_non_chatgpt_slot_is_rejected(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "slots.json"
            caller = ChatGPTBrowserCaller(state_path=path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "slots": {
                            "bad": {
                                "target_id": "x",
                                "url": "https://example.com/",
                                "title": "wrong",
                                "conversation_id": None,
                                "bound_explicitly": True,
                                "created_at": "now",
                                "last_seen_at": "now",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(CallerError):
                caller._bound_slot("bad")


if __name__ == "__main__":
    unittest.main()
