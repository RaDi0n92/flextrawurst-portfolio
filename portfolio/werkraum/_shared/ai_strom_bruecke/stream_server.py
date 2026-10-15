#!/usr/bin/env python3
"""Local push feed for the AI-Strom-Brücke.

The server deliberately uses only the Python standard library. It binds to
loopback and publishes the newest X11 frame as a multipart PNG stream plus the
append-only Selkies event ledger as Server-Sent Events.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_FRAME = Path(__file__).resolve().parent / "latest.png"
DEFAULT_LEDGER = Path(__file__).resolve().parent / "events.jsonl"
DEFAULT_STATE = Path(__file__).resolve().parent / "state.json"


class PushHandler(BaseHTTPRequestHandler):
    server_version = "AI-Strom-Bruecke-Push/1.0"

    def log_message(self, *_args):
        return

    @property
    def config(self):
        return self.server.push_config

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        route = urlparse(self.path).path
        if route == "/health":
            self._json({"ok": True, "schema": "ai-strom-bruecke.push.v2", "state": self._state()})
        elif route == "/state":
            self._json(self._state())
        elif route == "/latest.png":
            self._latest()
        elif route == "/stream":
            self._stream()
        elif route == "/events":
            self._events()
        else:
            self.send_error(404, "Use /health, /state, /latest.png, /stream or /events")

    def _state(self) -> dict:
        path = self.config["state"]
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                value = {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            value = {}
        frame = self.config["frame"]
        try:
            value["source_frame_age_ms"] = round(max(0.0, time.time() - frame.stat().st_mtime) * 1000, 1)
        except FileNotFoundError:
            value["source_frame_age_ms"] = None
        value.update({"stream_schema": "ai-strom-bruecke.push.v2", "llm_calls": 0, "model_network": "blocked-by-architecture"})
        return value

    def _json(self, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _latest(self):
        frame = self.config["frame"]
        try:
            data = frame.read_bytes()
        except FileNotFoundError:
            self.send_error(503, "No frame has been generated yet")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _stream(self):
        boundary = b"ai_strom_frame"
        self.send_response(200)
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={boundary.decode()}")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last_stamp = None
        try:
            while True:
                frame = self.config["frame"]
                try:
                    stamp = frame.stat().st_mtime_ns
                except FileNotFoundError:
                    time.sleep(0.05)
                    continue
                if stamp != last_stamp:
                    data = frame.read_bytes()
                    state = self._state()
                    header = (
                        b"--" + boundary + b"\r\n"
                        b"Content-Type: image/png\r\n"
                        + f"Content-Length: {len(data)}\r\n".encode()
                        + f"X-Frame-Time: {time.time():.6f}\r\n".encode()
                        + f"X-Frame-Sequence: {state.get('frame_sequence', '')}\r\n".encode()
                        + f"X-Frame-Digest: {state.get('frame_digest', '')}\r\n\r\n".encode()
                    )
                    self.wfile.write(header + data + b"\r\n")
                    self.wfile.flush()
                    last_stamp = stamp
                time.sleep(0.03)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return

    def _events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        position = 0
        try:
            while True:
                ledger = self.config["ledger"]
                if ledger.exists():
                    with ledger.open(encoding="utf-8") as stream:
                        stream.seek(position)
                        for line in stream:
                            self.wfile.write(b"event: input\ndata: " + line.rstrip().encode() + b"\n\n")
                            self.wfile.flush()
                        position = stream.tell()
                time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return


def main():
    parser = argparse.ArgumentParser(description="AI-Strom-Brücke local push feed")
    parser.add_argument("--bind", default=os.environ.get("AI_STROM_BRUECKE_PUSH_BIND", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AI_STROM_BRUECKE_PUSH_PORT", "8098")))
    parser.add_argument("--frame", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_FRAME", DEFAULT_FRAME)))
    parser.add_argument("--ledger", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_LEDGER", DEFAULT_LEDGER)))
    parser.add_argument("--state", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_STATE", DEFAULT_STATE)))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.bind, args.port), PushHandler)
    server.daemon_threads = True
    server.push_config = {"frame": args.frame, "ledger": args.ledger, "state": args.state}
    print(f"AI-Strom-Brücke push feed listening on http://{args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
