#!/usr/bin/env python3
"""Nicht-destruktive Regression fuer Browser-Agent-Shutdown.

Kein systemd-Restart, kein echter LLM-/HTTP-Aufruf, keine echte PostgreSQL-Warteschlange.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
import threading

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/welt")

import llm_scheduler as sched
import hauhau_client
import browser_agent


def test_scheduler_cancel_before_db():
    old_conn = sched._conn
    called = []
    sched._conn = lambda: called.append(True)
    try:
        slot = sched.LLMSlot(rufer="audit:pre", cancel_check=lambda: True)
        try:
            slot.__enter__()
            raise AssertionError("cancel before DB wurde nicht ausgeloest")
        except sched.LLMSlotCancelled:
            pass
        assert called == [], "DB wurde trotz bereits gesetztem Cancel geoeffnet"
    finally:
        sched._conn = old_conn


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self.last_sql = ""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.last_sql = " ".join(sql.split())
        if self.last_sql.startswith("DELETE FROM llm_warteschlange WHERE id"):
            self.conn.deleted = True

    def fetchone(self):
        sql = self.last_sql
        if sql.startswith("INSERT INTO llm_warteschlange"):
            return {"id": 123, "angefragt_um": datetime.now(timezone.utc)}
        if sql.startswith("UPDATE llm_warteschlange"):
            return None
        if sql.startswith("SELECT NOW() -"):
            return {"gewartet": timedelta(seconds=0)}
        return None

    def fetchall(self):
        return []


class FakeConn:
    def __init__(self):
        self.autocommit = False
        self.closed = False
        self.deleted = False

    def cursor(self):
        return FakeCursor(self)

    def close(self):
        self.closed = True


def test_scheduler_cancel_while_waiting_cleanup():
    old_conn = sched._conn
    old_sleep = sched.time.sleep
    fake = FakeConn()
    cancelled = {"v": False}
    sched._conn = lambda: fake
    sched.time.sleep = lambda _s: cancelled.__setitem__("v", True)
    try:
        slot = sched.LLMSlot(
            rufer="audit:wait",
            max_wartezeit=150,
            cancel_check=lambda: cancelled["v"],
        )
        try:
            slot.__enter__()
            raise AssertionError("cancel waehrend Wait wurde nicht ausgeloest")
        except sched.LLMSlotCancelled:
            pass
        assert fake.deleted, "Warteschlangen-Zeile wurde bei Cancel nicht geloescht"
        assert fake.closed, "Scheduler-DB-Verbindung wurde bei Cancel nicht geschlossen"
    finally:
        sched._conn = old_conn
        sched.time.sleep = old_sleep


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": "nie erreicht"}}]}


class FakeHttpClient:
    last = None

    def __init__(self, *args, **kwargs):
        self.closed = False
        FakeHttpClient.last = self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False

    def close(self):
        self.closed = True

    def post(self, url, json=None):
        tid = threading.get_ident()
        assert hauhau_client._AKTIVE_STREAMS.get(tid) is self, "chat() registrierte Client nicht"
        assert hauhau_client.abbreche_stream(tid), "abbreche_stream fand registrierten chat()-Client nicht"
        assert self.closed, "abbreche_stream schloss chat()-Client nicht"
        raise RuntimeError("simulierter Abbruch")


def test_chat_request_is_abortable():
    old_client = hauhau_client.httpx.Client
    hauhau_client.httpx.Client = FakeHttpClient
    tid = threading.get_ident()
    try:
        try:
            hauhau_client.chat("audit", timeout=120.0)
            raise AssertionError("simulierter HTTP-Abbruch wurde nicht sichtbar")
        except RuntimeError as e:
            assert "simulierter Abbruch" in str(e)
        assert tid not in hauhau_client._AKTIVE_STREAMS, "Client-Registry wurde nach Abbruch nicht bereinigt"
    finally:
        hauhau_client.httpx.Client = old_client
        hauhau_client._AKTIVE_STREAMS.pop(tid, None)


def test_browser_signal_handler_sets_cancel_and_aborts_request():
    old_abort = browser_agent.hauhau_client.abbreche_stream
    old_running = browser_agent._laufend
    calls = []
    browser_agent.hauhau_client.abbreche_stream = lambda tid: calls.append(tid) or True
    browser_agent._laufend = True
    try:
        browser_agent._signal_handler(15, None)
        assert browser_agent._laufend is False, "SIGTERM setzte _laufend nicht auf False"
        assert calls == [threading.get_ident()], "SIGTERM brach den Request des Hauptthreads nicht ab"
    finally:
        browser_agent.hauhau_client.abbreche_stream = old_abort
        browser_agent._laufend = old_running


def test_all_browser_agent_slots_are_cancelable():
    text = Path("/root/werkraum/welt/browser_agent.py").read_text(encoding="utf-8")
    slot_calls = text.count("with sched.LLMSlot(")
    cancel_hooks = text.count("cancel_check=lambda: not _laufend")
    assert slot_calls == 4, f"unerwartete LLMSlot-Aufruferzahl: {slot_calls}"
    assert cancel_hooks == slot_calls, f"nur {cancel_hooks}/{slot_calls} Slot-Aufrufer cancelbar"


def main():
    tests = [
        test_scheduler_cancel_before_db,
        test_scheduler_cancel_while_waiting_cleanup,
        test_chat_request_is_abortable,
        test_browser_signal_handler_sets_cancel_and_aborts_request,
        test_all_browser_agent_slots_are_cancelable,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS total={len(tests)}/{len(tests)}")


if __name__ == "__main__":
    main()
