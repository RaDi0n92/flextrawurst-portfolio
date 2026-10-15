#!/usr/bin/env python3
"""Deterministic attacks against the integrated evidence and safety core."""

from __future__ import annotations

import argparse
import json
import tempfile
import io
from pathlib import Path

from PIL import Image

from .actions import ActionExecutor, InputBackend, RecordingBackend
from .contracts import ActionExpectation, ActionPhase, DiffKind
from .network_guard import runtime_status, scan_sources
from .object_store import TriViewObjectStore
from .timeline import FrameTimeline, compare_frames
from .tri_leib import TriViewValidationError, build_tri_view_capsule, validate_tri_view_object


class ExplodingBackend(RecordingBackend):
    def move(self, x: int, y: int) -> None:
        super().move(x, y)
        if len([call for call in self.calls if call[0] == "move"]) > 1:
            raise RuntimeError("injected backend crash")


def run() -> dict:
    root = Path(tempfile.mkdtemp(prefix="ai-strom-redteam-"))
    cases = []

    unchanged = compare_frames(b"not-a-frame", b"not-a-frame")
    cases.append({"id": "stale-frame-not-accepted", "passed": unchanged.kind == DiffKind.UNCHANGED, "evidence": unchanged.to_dict()})

    backend = ExplodingBackend()
    executor = ActionExecutor(backend, lease_path=root / "lease.lock")
    transaction = executor.gesture(actor="redteam", target="native", points=[(1, 1), (2, 2), (3, 3)], hold_delay_s=0)
    calls = [call[0] for call in backend.calls]
    cases.append({"id": "crash-releases-button", "passed": transaction.phase == ActionPhase.ABORTED and calls[-1] == "mouseup", "evidence": {"phase": transaction.phase.value, "calls": calls}})

    first = build_tri_view_capsule({"object_id": "red-1", "type": "post", "provenance": ["redteam"]})
    try:
        bad = first.to_dict()
        bad.pop("organ_leib")
        validate_tri_view_object(bad)
        atomic = False
    except (TriViewValidationError, ValueError, TypeError):
        atomic = True
    cases.append({"id": "no-two-of-three-object", "passed": atomic, "evidence": {"three_leiber": True}})

    timeline = FrameTimeline(retention_seconds=60, fps=10, frame_dir=root / "frames")
    image = Image.new("RGB", (4, 4), "black")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    frame = buffer.getvalue()
    timeline.ingest(frame)
    timeline.ingest(frame)
    metadata = timeline.metadata()
    cases.append({"id": "duplicate-is-visible", "passed": metadata[1]["duplicate_of"] == metadata[0]["frame_id"], "evidence": metadata})

    sources = [Path(__file__).with_name(name) for name in ("bridge.py", "cockpit_server.py", "vision_runner.py", "stream_server.py")]
    findings = scan_sources(sources)
    cases.append({"id": "model-free-runtime", "passed": not findings and runtime_status()["llm_calls"] == 0, "evidence": {"findings": findings, "runtime": runtime_status()}})

    return {"schema": "ai-strom-bruecke.redteam.v1", "passed": all(case["passed"] for case in cases), "cases": cases, "cleanup_root": str(root)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
