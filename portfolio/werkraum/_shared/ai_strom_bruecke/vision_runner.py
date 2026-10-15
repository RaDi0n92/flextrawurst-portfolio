#!/usr/bin/env python3
"""Frame subscriber and safety bus for the AI-Strom-Brücke.

The existing push server publishes frames, but publishing is not the same as
having a consumer.  This process is that consumer: it keeps a live connection
to the upstream multipart stream, writes a small observable state, republishes
frames for a real vision client, and closes the input gate when the stream
stops producing frames.

It intentionally does not pretend to be a language model.  A model/runner can
subscribe to this process at /stream and receives each frame plus sequence and
timing headers.  The current chat transport still needs an actual vision
client to consume that local feed.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import urlunparse


ROOT = Path(__file__).resolve().parent
DEFAULT_UPSTREAM = "http://127.0.0.1:8098/stream"
DEFAULT_STATE = ROOT / "vision_state.json"
DEFAULT_GATE = Path("/tmp/ai-strom-bruecke-input-gate.json")
DEFAULT_FRAME = ROOT / "vision_latest.png"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def parse_url(value: str) -> tuple[str, int, str]:
    parsed = urlparse(value)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError(f"Nur http-URLs werden unterstützt: {value}")
    port = parsed.port or 80
    path = urlunparse(("", "", parsed.path or "/", "", parsed.query, ""))
    return parsed.hostname, port, path


class VisionRunner:
    def __init__(self, args: argparse.Namespace):
        self.upstream = args.upstream
        self.upstream_host, self.upstream_port, self.upstream_path = parse_url(args.upstream)
        self.state_path = args.state
        self.gate_path = args.gate
        self.frame_path = args.frame
        self.stale_after = max(0.25, args.stale_after)
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.generation = 0
        self.frame = None
        self.state = {
            "name": "AI-Strom-Brücke Vision-Runner",
            "schema": "ai-strom-bruecke.vision-state.v1",
            "runner": "starting",
            "upstream": self.upstream,
            "connected": False,
            "frame_count": 0,
            "last_frame_at": None,
            "last_frame_age_s": None,
            "last_frame_digest": None,
            "last_source_sequence": None,
            "last_frame_age_ms": None,
            "capture_latency_ms": None,
            "duplicate_frame_count": 0,
            "gate": {"allow_input": False, "reason": "runner-starting"},
        }
        self._publish_state()

    def _snapshot(self) -> dict:
        with self.lock:
            state = dict(self.state)
            state["gate"] = dict(self.state["gate"])
            if state["last_frame_at"] is not None:
                state["last_frame_age_s"] = round(max(0.0, time.time() - state["last_frame_at"]), 3)
                state["last_frame_age_ms"] = round(state["last_frame_age_s"] * 1000, 1)
            state["llm_calls"] = 0
            state["model_network"] = "blocked-by-architecture"
            return state

    def _publish_state(self) -> None:
        state = self._snapshot()
        atomic_json(self.state_path, state)
        atomic_json(self.gate_path, {
            "schema": "ai-strom-bruecke.input-gate.v1",
            "allow_input": state["gate"]["allow_input"],
            "reason": state["gate"]["reason"],
            "updated_at": time.time(),
            "last_frame_at": state["last_frame_at"],
            "last_frame_age_s": state["last_frame_age_s"],
            "frame_count": state["frame_count"],
        })

    def _set_status(self, **changes) -> None:
        with self.lock:
            self.state.update(changes)
        self._publish_state()

    def _set_gate(self, allow: bool, reason: str) -> None:
        with self.lock:
            self.state["gate"] = {"allow_input": bool(allow), "reason": reason}
        self._publish_state()

    def _record_frame(self, frame: bytes, headers: dict[str, str]) -> None:
        now = time.time()
        digest = hashlib.sha256(frame).hexdigest()
        with self.condition:
            previous = self.state["last_frame_digest"]
            duplicate_count = self.state["duplicate_frame_count"] + 1 if digest == previous else 0
            self.frame = frame
            self.generation += 1
            self.state.update({
                "runner": "running",
                "connected": True,
                "frame_count": self.state["frame_count"] + 1,
                "last_frame_at": now,
                "last_frame_age_s": 0.0,
                "last_frame_digest": digest,
                "last_source_sequence": headers.get("x-frame-sequence") or None,
                "capture_latency_ms": round(max(0.0, (now - float(headers["x-frame-time"])) * 1000), 1) if headers.get("x-frame-time") else None,
                "duplicate_frame_count": duplicate_count,
                "upstream_frame_time": headers.get("x-frame-time"),
                "generation": self.generation,
            })
            self.state["gate"] = {"allow_input": True, "reason": "fresh-frame"}
            generation = self.generation
            self.condition.notify_all()
        atomic_bytes(self.frame_path, frame)
        self._publish_state()
        _ = generation

    def _disconnect(self, reason: str) -> None:
        self._set_status(connected=False, runner="disconnected", disconnect_reason=reason)
        self._set_gate(False, reason)

    @staticmethod
    def _read_exact(response, size: int) -> bytes:
        chunks = []
        remaining = size
        while remaining:
            chunk = response.read(remaining)
            if not chunk:
                raise ConnectionError("Upstream-Stream endete mitten im Frame")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def _read_part(self, response, boundary: bytes):
        marker = b"--" + boundary
        line = response.readline()
        while line and not line.startswith(marker):
            line = response.readline()
        if not line or line.startswith(marker + b"--"):
            return None
        headers = {}
        line = response.readline()
        while line not in (b"\r\n", b"\n", b""):
            name, _, value = line.decode("latin-1").partition(":")
            if name and value:
                headers[name.strip().lower()] = value.strip()
            line = response.readline()
        length = int(headers.get("content-length", "0"))
        if length <= 0:
            raise ValueError("Upstream-Frame ohne Content-Length")
        frame = self._read_exact(response, length)
        response.read(2)
        return frame, headers

    def _consume_once(self) -> None:
        connection = http.client.HTTPConnection(self.upstream_host, self.upstream_port, timeout=8)
        connection.request("GET", self.upstream_path, headers={"Accept": "multipart/x-mixed-replace"})
        response = connection.getresponse()
        if response.status != 200:
            raise ConnectionError(f"Upstream antwortete mit HTTP {response.status}")
        content_type = response.getheader("Content-Type", "")
        boundary_value = next((part.strip() for part in content_type.split(";") if "boundary=" in part), "")
        boundary_value = boundary_value.split("=", 1)[-1].strip().strip('"')
        if not boundary_value:
            raise ValueError("Upstream-Stream hat keine Multipart-Grenze")
        boundary = boundary_value.encode("ascii")
        self._set_status(connected=True, runner="running", disconnect_reason=None)
        while True:
            part = self._read_part(response, boundary)
            if part is None:
                raise ConnectionError("Upstream-Stream wurde beendet")
            frame, headers = part
            self._record_frame(frame, headers)

    def run(self) -> None:
        while True:
            try:
                self._consume_once()
            except Exception as error:  # the runner must recover forever
                self._disconnect(f"upstream-error: {error}")
                time.sleep(1.0)

    def watchdog(self) -> None:
        """Close the gate even when the process is alive but frames stop."""
        while True:
            time.sleep(0.1)
            with self.lock:
                last_frame_at = self.state["last_frame_at"]
                gate_open = self.state["gate"]["allow_input"]
            if (
                gate_open
                and last_frame_at is not None
                and time.time() - last_frame_at > self.stale_after
            ):
                self._set_gate(False, "frame-stale")

    def status(self) -> dict:
        state = self._snapshot()
        if state["last_frame_age_s"] is None or state["last_frame_age_s"] > self.stale_after:
            state["gate"] = {"allow_input": False, "reason": "frame-stale"}
            state["connected"] = False
        return state

    def wait_for_frame(self, after_generation: int, timeout: float):
        deadline = time.monotonic() + timeout
        with self.condition:
            while self.generation <= after_generation:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self.condition.wait(remaining)
            return self.frame, self.generation, self.state["last_frame_digest"]


class PushHandler(BaseHTTPRequestHandler):
    server_version = "AI-Strom-Bruecke-Vision/1.0"

    def log_message(self, *_args):
        return

    @property
    def runner(self) -> VisionRunner:
        return self.server.runner

    def _json(self, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        route = urlparse(self.path).path
        if route in {"/health", "/state"}:
            self._json(self.runner.status())
        elif route == "/latest.png":
            frame = self.runner.frame
            if not frame:
                self.send_error(503, "No vision frame available")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(frame)))
            self.end_headers()
            self.wfile.write(frame)
        elif route == "/stream":
            self._stream()
        else:
            self.send_error(404, "Use /health, /state, /latest.png or /stream")

    def _stream(self) -> None:
        boundary = b"ai_strom_vision_frame"
        self.send_response(200)
        self.send_header("Content-Type", f"multipart/x-mixed-replace; boundary={boundary.decode()}")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        generation = 0
        try:
            while True:
                result = self.runner.wait_for_frame(generation, timeout=15)
                if result is None:
                    continue
                frame, generation, digest = result
                header = (
                    b"--" + boundary + b"\r\n"
                    b"Content-Type: image/png\r\n"
                    + f"Content-Length: {len(frame)}\r\n".encode()
                    + f"X-Vision-Sequence: {generation}\r\n".encode()
                    + f"X-Vision-Digest: {digest}\r\n".encode()
                    + f"X-Vision-Source-Sequence: {self.runner.state.get('last_source_sequence') or ''}\r\n\r\n".encode()
                )
                self.wfile.write(header + frame + b"\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Consumes and republishes AI-Strom-Brücke frames")
    parser.add_argument("--upstream", default=os.environ.get("AI_STROM_BRUECKE_VISION_UPSTREAM", DEFAULT_UPSTREAM))
    parser.add_argument("--bind", default=os.environ.get("AI_STROM_BRUECKE_VISION_BIND", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AI_STROM_BRUECKE_VISION_PORT", "8099")))
    parser.add_argument("--state", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_VISION_STATE", DEFAULT_STATE)))
    parser.add_argument("--gate", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_INPUT_GATE", DEFAULT_GATE)))
    parser.add_argument("--frame", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_VISION_FRAME", DEFAULT_FRAME)))
    parser.add_argument("--stale-after", type=float, default=float(os.environ.get("AI_STROM_BRUECKE_VISION_STALE_AFTER", "1.0")))
    args = parser.parse_args()
    runner = VisionRunner(args)
    server = ThreadingHTTPServer((args.bind, args.port), PushHandler)
    server.daemon_threads = True
    server.runner = runner
    threading.Thread(target=server.serve_forever, name="vision-http", daemon=True).start()
    threading.Thread(target=runner.watchdog, name="vision-watchdog", daemon=True).start()
    runner.run()


if __name__ == "__main__":
    main()
