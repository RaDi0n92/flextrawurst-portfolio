#!/usr/bin/env python3
"""Deterministic native-input harness used for browser acceptance tests.

It exercises the same lease/action/release engine with a recording backend.
It is explicitly a test surface, never a claim that a browser has become an
X11 window or that Google Earth accepted an input.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .actions import ActionExecutor, RecordingBackend
from .contracts import ActionExpectation, jsonable


HTML = """<!doctype html><html lang=de><meta charset=utf-8><title>Native Harness</title>
<style>body{font:16px system-ui;background:#101318;color:#e8edf5;padding:24px}button{margin:4px;padding:10px}pre{background:#191e27;padding:12px}</style>
<h1>Deterministic Native Harness</h1><p id=provenance>test-only · no X11 · no Webtop primary</p>
<button id=gesture>Held gesture</button><button id=middle>Mittelmaus</button><button id=right>Rechtsmaus</button><button id=wheel>Zoom/Rad</button><button id=keyhold>WASD hold</button><button id=stop>Emergency stop</button><pre id=state>warte</pre>
<script>
async function call(path, body={}) { const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}); const value=await r.json(); document.querySelector('#state').textContent=JSON.stringify(value,null,2); return value; }
gesture.onclick=()=>call('/api/gesture'); middle.onclick=()=>call('/api/middle'); right.onclick=()=>call('/api/right'); wheel.onclick=()=>call('/api/wheel'); keyhold.onclick=()=>call('/api/keyhold'); stop.onclick=()=>call('/api/stop');
setInterval(async()=>{const r=await fetch('/state',{cache:'no-store'}); if(r.ok) document.querySelector('#state').textContent=JSON.stringify(await r.json(),null,2)},250);
</script>"""


class HarnessHandler(BaseHTTPRequestHandler):
    server_version = "AI-Strom-Bruecke-Native-Harness/1.0"

    def log_message(self, *_args):
        return

    @property
    def harness(self):
        return self.server.harness

    def _json(self, value: object, status: int = 200):
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):  # noqa: N802
        route = urlparse(self.path).path
        if route == "/":
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif route in {"/state", "/health"}:
            self._json(self.harness.state())
        else:
            self.send_error(404)

    def do_POST(self):  # noqa: N802
        route = urlparse(self.path).path
        try:
            if route == "/api/gesture":
                transaction = self.harness.executor.gesture(
                    actor="playwright-test", target="native-harness",
                    points=[(10, 10), (20, 15), (40, 30)], hold_delay_s=0,
                    expectation=ActionExpectation(explanation="harness frame changed"),
                )
                self.harness.executor.acknowledge(transaction, accepted=True, frame_ids=["harness-frame-2"], evidence={"diff": "camera-moved"})
                return self._json(self.harness.record(transaction))
            if route == "/api/keyhold":
                transaction = self.harness.executor.key_hold(actor="playwright-test", target="native-harness", key="w", duration_s=0.01)
                self.harness.executor.acknowledge(transaction, accepted=True, frame_ids=["harness-frame-3"], evidence={"diff": "camera-moved"})
                return self._json(self.harness.record(transaction))
            if route in {"/api/middle", "/api/right", "/api/wheel"}:
                if route == "/api/wheel":
                    transaction = self.harness.executor.wheel(actor="playwright-test", target="native-harness", direction=1)
                    frame_id = "harness-frame-wheel"
                else:
                    button = 2 if route == "/api/middle" else 3
                    transaction = self.harness.executor.click(actor="playwright-test", target="native-harness", button=button)
                    frame_id = f"harness-frame-button-{button}"
                self.harness.executor.acknowledge(transaction, accepted=True, frame_ids=[frame_id], evidence={"diff": "camera-moved"})
                return self._json(self.harness.record(transaction))
            if route == "/api/stop":
                released = self.harness.executor.emergency_release()
                self.harness.last_stop = released
                return self._json(self.harness.state())
            self._json({"error": "unknown route"}, 404)
        except Exception as error:  # test surface returns evidence, not a hidden traceback
            self._json({"error": str(error)}, 500)


class NativeHarness:
    def __init__(self, ledger: Path):
        self.backend = RecordingBackend()
        self.lease_path = Path(tempfile.gettempdir()) / "ai-strom-native-harness.lock"
        self.executor = ActionExecutor(self.backend, lease_path=self.lease_path)
        self.ledger = ledger
        self.last_action = None
        self.last_stop = []

    def record(self, transaction):
        value = jsonable(transaction)
        self.last_action = value
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")
        return self.state()

    def state(self):
        return {
            "schema": "ai-strom-bruecke.native-harness.v1",
            "test_only": True,
            "production_primary": False,
            "action": self.last_action,
            "calls": [list(call) for call in self.backend.calls],
            "last_stop": self.last_stop,
            "llm_calls": 0,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8110)
    parser.add_argument("--ledger", type=Path, default=Path(tempfile.gettempdir()) / "native-harness.jsonl")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.bind, args.port), HarnessHandler)
    server.daemon_threads = True
    server.harness = NativeHarness(args.ledger)
    print(f"Native harness auf http://{args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
