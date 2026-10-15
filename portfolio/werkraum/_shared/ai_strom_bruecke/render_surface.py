#!/usr/bin/env python3
"""Measured human-surface render metadata, separate from experience claims."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RenderMetrics:
    mode: str = "dom-derived"
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    frame_time_ms: float | None = None
    dropped_frames: int = 0
    target_fps: int = 66
    target_resolution: str = "8K"
    target_status: str = "planned"

    def record(self, *, now: float, previous_at: float | None, width: int | None, height: int | None) -> float:
        self.width, self.height = width, height
        if previous_at is not None and now > previous_at:
            self.frame_time_ms = (now - previous_at) * 1000
            self.fps = 1000 / self.frame_time_ms if self.frame_time_ms else None
        if self.width is not None and self.height is not None and self.fps is not None:
            self.target_status = "verified" if self.meets_target() else "measured-below-target"
        return self.frame_time_ms or 0.0

    def meets_target(self) -> bool:
        return bool(
            self.width is not None and self.height is not None
            and self.width >= 7680 and self.height >= 4320
            and self.fps is not None and self.fps >= self.target_fps
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode, "width": self.width, "height": self.height,
            "fps": round(self.fps, 2) if self.fps is not None else None,
            "frame_time_ms": round(self.frame_time_ms, 2) if self.frame_time_ms is not None else None,
            "dropped_frames": self.dropped_frames, "target_fps": self.target_fps,
            "target_resolution": self.target_resolution, "target_status": self.target_status,
            "target_met": self.meets_target(),
            "measured_at": time.time(),
        }


def human_surface_from_object(obj: dict[str, Any], *, width: int | None = None, height: int | None = None) -> dict[str, Any]:
    human = obj.get("menschen_leib", {})
    metrics = dict(human.get("render_metrics", {}))
    if width is not None:
        metrics.setdefault("width", width)
    if height is not None:
        metrics.setdefault("height", height)
    metrics.setdefault("target_fps", 66)
    metrics.setdefault("target_resolution", "8K")
    metrics.setdefault("target_status", "planned")
    return {"object_id": obj.get("object_id"), "scene": human.get("scene"), "animation": human.get("animation", {}), "depth": human.get("depth"), "render_metrics": metrics}
