#!/usr/bin/env python3
"""Explicit inventory of the v1 bridge surface and additive v2 paths."""

from __future__ import annotations

from pathlib import Path


V1_PATHS = ("bridge.py", "events.jsonl", "state.json", "latest.png", "stream_server.py", "vision_runner.py")
V2_PATHS = ("contracts.py", "timeline.py", "earth_perception.py", "camera_analysis.py", "analysis_overlay.py", "actions.py", "cockpit_server.py", "web_dom_adapter.py", "web_session.py", "native_proxy.py", "native_harness.py", "tri_leib.py", "object_store.py", "organ_effects.py", "world_flow.py", "anchors.py", "render_surface.py", "requirements.py", "inventory.py")
V1_ROUTES = ("/stream", "/latest.png", "/events", "/health", "/state")
V2_ROUTES = ("/state-stream", "/timeline", "/objects", "/anchors", "/world-events", "/requirements", "/metrics", "/inventory")


def build_inventory(root: Path) -> dict:
    return {
        "schema": "ai-strom-bruecke.inventory.v1",
        "v1": {"paths": [{"path": path, "present": (root / path).exists()} for path in V1_PATHS], "routes": list(V1_ROUTES)},
        "v2": {"paths": [{"path": path, "present": (root / path).exists()} for path in V2_PATHS], "routes": list(V2_ROUTES)},
        "compatibility": "additive-v2-no-v1-removal",
    }
