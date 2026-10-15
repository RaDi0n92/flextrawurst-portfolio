#!/usr/bin/env python3
"""Capture a 10 Hz Blender viewport/state trajectory through the live bridge.

The script is observational only. It never calls execute_code and never starts
or stops Blender. Each command uses its own short-lived TCP connection so a
large JSON response cannot be mixed with another command's response.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def receive_json(sock: socket.socket, timeout: float) -> dict[str, Any]:
    sock.settimeout(timeout)
    chunks: list[bytes] = []
    while True:
        chunk = sock.recv(64 * 1024)
        if not chunk:
            if not chunks:
                raise ConnectionError("Blender bridge closed before sending a response")
            break
        chunks.append(chunk)
        raw = b"".join(chunks)
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict):
            raise ValueError("Blender bridge returned a non-object JSON response")
        return value
    raise ValueError("Incomplete JSON response from Blender bridge")


def call_bridge(host: str, port: int, command: str, params: dict[str, Any] | None,
                timeout: float) -> dict[str, Any]:
    payload = {"type": command, "params": params or {}}
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        response = receive_json(sock, timeout)
    if response.get("status") == "error":
        raise RuntimeError(response.get("message", "Blender bridge returned an error"))
    return response.get("result", {})


def capture_sample(args: argparse.Namespace, output: Path, index: int,
                   scheduled_at: float, previous_started: float | None) -> tuple[dict[str, Any], float]:
    started_at = time.monotonic()
    filename = output / f"sample-{index:06d}.png"
    screenshot = call_bridge(
        args.host,
        args.port,
        "get_viewport_screenshot",
        {"max_size": args.max_size, "filepath": str(filename), "format": "png"},
        args.timeout,
    )
    if not filename.is_file() or filename.stat().st_size == 0:
        raise RuntimeError(f"Blender reported a screenshot but no file was created: {filename}")

    world_state = call_bridge(args.host, args.port, "get_world_state_snapshot", {}, args.timeout)
    finished_at = time.monotonic()
    interval_ms = None if previous_started is None else (started_at - previous_started) * 1000.0
    scheduled_lateness_ms = (started_at - scheduled_at) * 1000.0
    sample = {
        "sample": index,
        "label": args.label,
        "captured_at": utc_now(),
        "elapsed_ms": (started_at - args.started_monotonic) * 1000.0,
        "interval_ms": interval_ms,
        "target_interval_ms": args.interval * 1000.0,
        "scheduled_lateness_ms": round(scheduled_lateness_ms, 3),
        "capture_duration_ms": round((finished_at - started_at) * 1000.0, 3),
        "screenshot": {
            "path": str(filename),
            "sha256": sha256_file(filename),
            "bytes": filename.stat().st_size,
            "width": screenshot.get("width"),
            "height": screenshot.get("height"),
            "method": screenshot.get("method"),
        },
        "world_state": world_state,
    }
    return sample, started_at


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="Directory for PNG samples and trajectory.jsonl")
    parser.add_argument("--duration", type=float, default=1.0,
                        help="Capture duration in seconds (default: 1.0)")
    parser.add_argument("--interval", type=float, default=0.1,
                        help="Target interval in seconds (default: 0.1)")
    parser.add_argument("--cadence-tolerance-ms", type=float, default=25.0,
                        help="Allowed absolute interval drift in milliseconds (default: 25)")
    parser.add_argument("--max-size", type=int, default=1000,
                        help="Largest screenshot dimension (default: 1000)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9876)
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="Per-command bridge timeout in seconds")
    parser.add_argument("--label", default="observation")
    args = parser.parse_args()
    if (args.duration <= 0 or args.interval <= 0 or args.max_size <= 0
            or args.cadence_tolerance_ms < 0):
        parser.error("duration, interval, and max-size must be positive; cadence tolerance cannot be negative")
    return args


def main() -> int:
    args = parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)

    try:
        addon = call_bridge(args.host, args.port, "get_addon_info", {}, args.timeout)
        ping = call_bridge(args.host, args.port, "ping", {}, args.timeout)
    except Exception as exc:
        print(f"ERROR: Blender bridge preflight failed: {exc}", file=sys.stderr)
        return 2

    manifest = {
        "trajectory_version": 1,
        "label": args.label,
        "created_at": utc_now(),
        "host": args.host,
        "port": args.port,
        "duration_s": args.duration,
        "target_interval_s": args.interval,
        "max_size": args.max_size,
        "connection": {"ping": ping, "addon": addon},
    }
    (args.output / "trajectory-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    trajectory_path = args.output / "trajectory.jsonl"
    args.started_monotonic = time.monotonic()
    start = args.started_monotonic
    next_tick = start
    previous_started: float | None = None
    index = 0
    errors = 0
    successful_samples = 0
    intervals_ms: list[float] = []

    with trajectory_path.open("w", encoding="utf-8") as trajectory:
        while True:
            now = time.monotonic()
            if index and now - start >= args.duration:
                break
            if now < next_tick:
                time.sleep(next_tick - now)
            scheduled_at = next_tick
            try:
                sample, sample_started = capture_sample(
                    args, args.output, index, scheduled_at, previous_started
                )
                trajectory.write(json.dumps(sample, ensure_ascii=False) + "\n")
                trajectory.flush()
                successful_samples += 1
                if sample["interval_ms"] is not None:
                    intervals_ms.append(float(sample["interval_ms"]))
                print(
                    f"sample={index} elapsed={sample['elapsed_ms']:.1f}ms "
                    f"interval={sample['interval_ms'] if sample['interval_ms'] is not None else 'n/a'}ms "
                    f"late={sample['scheduled_lateness_ms']:.1f}ms"
                )
            except Exception as exc:
                errors += 1
                event = {
                    "sample": index,
                    "label": args.label,
                    "captured_at": utc_now(),
                    "error": str(exc),
                    "scheduled_lateness_ms": round((time.monotonic() - scheduled_at) * 1000.0, 3),
                }
                trajectory.write(json.dumps(event, ensure_ascii=False) + "\n")
                trajectory.flush()
                print(f"sample={index} ERROR: {exc}", file=sys.stderr)
                previous_started = time.monotonic()
            index += 1
            next_tick += args.interval

    target_interval_ms = args.interval * 1000.0
    expected_samples = max(2, math.ceil(args.duration / args.interval))
    cadence_intervals = [
        value for value in intervals_ms
        if abs(value - target_interval_ms) <= args.cadence_tolerance_ms
    ]
    cadence_met = (
        successful_samples >= expected_samples
        and len(intervals_ms) == successful_samples - 1
        and len(cadence_intervals) == len(intervals_ms)
    )
    summary = {
        "trajectory_version": 1,
        "completed_at": utc_now(),
        "samples_attempted": index,
        "successful_samples": successful_samples,
        "samples_with_errors": errors,
        "target_interval_s": args.interval,
        "target_interval_ms": target_interval_ms,
        "cadence_tolerance_ms": args.cadence_tolerance_ms,
        "expected_samples": expected_samples,
        "cadence_intervals": len(cadence_intervals),
        "measured_intervals_ms": [round(value, 3) for value in intervals_ms],
        "max_interval_ms": round(max(intervals_ms), 3) if intervals_ms else None,
        "capture_mode": "mcp-viewport-and-world-state",
        "cadence_met": cadence_met,
        "cadence_status": "PASS" if cadence_met else "FAIL",
        "duration_s": args.duration,
        "trajectory": str(trajectory_path),
    }
    (args.output / "trajectory-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if errors:
        return 1
    return 0 if cadence_met else 3


if __name__ == "__main__":
    raise SystemExit(main())
