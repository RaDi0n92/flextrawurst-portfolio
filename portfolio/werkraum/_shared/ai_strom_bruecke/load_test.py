#!/usr/bin/env python3
"""Bounded, model-free 100-ms timeline load measurement."""

from __future__ import annotations

import io
import json
import os
import time
from dataclasses import dataclass

from PIL import Image

from .timeline import FrameTimeline


@dataclass(slots=True)
class LoadReport:
    duration_s: float
    frames: int
    measured_interval_ms: float
    max_interval_ms: float
    ring_records: int
    max_ring_records: int
    passed: bool

    def to_dict(self):
        return {
            "schema": "ai-strom-bruecke.load-report.v1", "duration_s": round(self.duration_s, 3),
            "frames": self.frames, "measured_interval_ms": round(self.measured_interval_ms, 2),
            "max_interval_ms": round(self.max_interval_ms, 2), "ring_records": self.ring_records,
            "max_ring_records": self.max_ring_records, "passed": self.passed,
        }


def run(duration_s: float = 1.2, fps: float = 10.0) -> LoadReport:
    timeline = FrameTimeline(retention_seconds=60, fps=fps)
    image = Image.new("RGB", (64, 48), "black")
    payload = io.BytesIO()
    image.save(payload, format="PNG")
    frame = payload.getvalue()
    started = time.monotonic()
    stamps = []
    while time.monotonic() - started < duration_s:
        stamps.append(time.monotonic())
        timeline.ingest(frame, target="load-test")
        time.sleep(1 / fps)
    intervals = [(b - a) * 1000 for a, b in zip(stamps, stamps[1:])]
    measured = sum(intervals) / len(intervals) if intervals else 0.0
    maximum = max(intervals, default=0.0)
    max_records = round(60 * fps * 1.25)
    return LoadReport(duration_s, len(stamps), measured, maximum, len(timeline.records), max_records, bool(stamps) and measured <= 150 and maximum <= 250 and len(timeline.records) <= max_records)


if __name__ == "__main__":
    duration = float(os.environ.get("AI_STROM_BRUECKE_LOAD_DURATION_S", "1.2"))
    fps = float(os.environ.get("AI_STROM_BRUECKE_LOAD_FPS", "10"))
    report = run(duration_s=duration, fps=fps)
    print(json.dumps(report.to_dict(), indent=2))
    raise SystemExit(0 if report.passed else 1)
