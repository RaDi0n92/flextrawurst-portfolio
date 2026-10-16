#!/usr/bin/env python3
"""Nicht-destruktive Regression fuer Innenleben-LLM-Ausfall/Retry.

Schreibt weder PostgreSQL noch echte Chroma-Collections. Alle mutierenden Pfade
werden durch Fakes ersetzt.
"""
import sys
sys.path.insert(0, "/root/werkraum/innenleben")

import nodes
import flarum_feeder as feeder


class FakeCol:
    def __init__(self):
        self.upserts = []

    def count(self):
        return 1

    def query(self, **kwargs):
        return {"documents": [["alte erinnerung"]]}

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)


def test_llm_wrapper_propagiert():
    original = nodes.sched.LLMSlot

    class FailSlot:
        def __enter__(self):
            raise RuntimeError("simulierter scheduler-ausfall")

        def __exit__(self, *args):
            return False

    nodes.sched.LLMSlot = lambda **kwargs: FailSlot()
    try:
        try:
            nodes._llm("x")
        except nodes.ReflectionLLMUnavailable:
            return
        raise AssertionError("_llm hat Scheduler-Ausfall verschluckt")
    finally:
        nodes.sched.LLMSlot = original


def test_reflection_keine_fake_und_retry_idempotent():
    original_collection = nodes._collection
    original_llm = nodes._llm
    state = {
        "entity_id": "TEST_WESEN",
        "current_event": "Testereignis",
        "event_id": "flarum:post_7778:TEST_WESEN",
        "self_model": {"x": 1},
        "emotions": {"valence": 5.0, "arousal": 5.0, "dominance": 5.0},
    }
    try:
        fail_col = FakeCol()
        nodes._collection = lambda _eid: fail_col
        nodes._llm = lambda *a, **k: (_ for _ in ()).throw(
            nodes.ReflectionLLMUnavailable("simulierter slotfehler")
        )
        try:
            nodes.reflection_node(state)
            raise AssertionError("Slotfehler wurde verschluckt")
        except nodes.ReflectionLLMUnavailable:
            pass
        assert fail_col.upserts == [], "Slotfehler hat Fake-Reflexion gespeichert"

        retry_col = FakeCol()
        nodes._collection = lambda _eid: retry_col
        nodes._llm = lambda *a, **k: (
            '{"reflection":"echte reflexion","insight":"kleine erkenntnis"}'
        )
        nodes.reflection_node(state)
        nodes.reflection_node(state)
        ids = [x["ids"][0] for x in retry_col.upserts]
        assert len(ids) == 2 and ids[0] == ids[1], f"Retry-IDs nicht identisch: {ids}"
    finally:
        nodes._collection = original_collection
        nodes._llm = original_llm


def test_feeder_cursor_bleibt_vor_fehlerpost():
    original_names = feeder.WESEN_USERNAMES
    original_load = feeder._lade_cursor_state
    original_posts = feeder._neue_posts_laden
    original_author = feeder._kanonischer_autor
    original_flag = feeder.CHAT_FLAG
    original_graph = feeder.innenleben_graph
    original_save = feeder._speichere_cursor_state

    wesen = "traeumerlie"
    saved = []

    class Flag:
        def exists(self):
            return False

    class Graph:
        @staticmethod
        def verarbeite_ereignis(**kwargs):
            raise RuntimeError("simulierter LLM-Slot-Ausfall")

    try:
        feeder.WESEN_USERNAMES = [wesen]
        feeder._lade_cursor_state = lambda: {wesen: 7777}
        feeder._neue_posts_laden = lambda _id: [{
            "id": 7778,
            "content": "audit test",
            "created_at": None,
            "autor": "daniel",
            "diskussion_titel": "x",
            "diskussion_id": 1,
        }]
        feeder._kanonischer_autor = lambda _a: None
        feeder.CHAT_FLAG = Flag()
        feeder.innenleben_graph = Graph
        feeder._speichere_cursor_state = lambda state: saved.append(dict(state))
        feeder.verarbeite_neue_posts(max_pro_wesen=3)
        assert saved == [], f"Cursor wurde trotz Fehler fortgeschrieben: {saved}"
    finally:
        feeder.WESEN_USERNAMES = original_names
        feeder._lade_cursor_state = original_load
        feeder._neue_posts_laden = original_posts
        feeder._kanonischer_autor = original_author
        feeder.CHAT_FLAG = original_flag
        feeder.innenleben_graph = original_graph
        feeder._speichere_cursor_state = original_save


def main():
    tests = [
        test_llm_wrapper_propagiert,
        test_reflection_keine_fake_und_retry_idempotent,
        test_feeder_cursor_bleibt_vor_fehlerpost,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS total={len(tests)}/{len(tests)}")


if __name__ == "__main__":
    main()
