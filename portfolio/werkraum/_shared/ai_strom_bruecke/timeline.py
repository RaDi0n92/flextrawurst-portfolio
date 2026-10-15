#!/usr/bin/env python3
"""Evidence-preserving frame timeline and deterministic image comparison."""

from __future__ import annotations

import hashlib
import io
import time
import uuid
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from .contracts import DiffKind, FrameEnvelope


@dataclass(slots=True)
class FrameRecord:
    envelope: FrameEnvelope
    payload: bytes


@dataclass(slots=True)
class DiffResult:
    kind: DiffKind
    changed_ratio: float
    mean_difference: float
    digest_changed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "changed_ratio": round(self.changed_ratio, 6),
            "mean_difference": round(self.mean_difference, 6),
            "digest_changed": self.digest_changed,
            "reason": self.reason,
        }


class FrameTimeline:
    """Ring buffer retaining real frames for a bounded 30–60 second view.

    The class never turns a repeated digest into a fake movement.  It stores
    repeated frames as evidence and marks the envelope with ``duplicate_of``.
    """

    def __init__(
        self,
        retention_seconds: float = 60.0,
        fps: float = 10.0,
        max_frames: int | None = None,
        frame_dir: Path | None = None,
    ) -> None:
        if retention_seconds <= 0 or fps <= 0:
            raise ValueError("retention_seconds und fps müssen positiv sein")
        self.retention_seconds = retention_seconds
        self.fps = fps
        self.max_frames = max_frames or max(1, round(retention_seconds * fps * 1.25))
        self.records: deque[FrameRecord] = deque(maxlen=self.max_frames)
        self._sequence = 0
        self.frame_dir = frame_dir
        if frame_dir:
            frame_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def digest(payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def dimensions(payload: bytes) -> tuple[int, int]:
        with Image.open(io.BytesIO(payload)) as image:
            return image.size

    def ingest(
        self,
        payload: bytes,
        *,
        source: str = "x11",
        target: str = "active",
        window_id: str | None = None,
        captured_at: float | None = None,
        capture_latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FrameRecord:
        if not payload:
            raise ValueError("leerer Frame ist kein gültiger Beobachtungsframe")
        now = captured_at if captured_at is not None else time.time()
        digest = self.digest(payload)
        width, height = self.dimensions(payload)
        duplicate_of = None
        for previous in reversed(self.records):
            if previous.envelope.digest == digest:
                duplicate_of = previous.envelope.frame_id
                break
        self._sequence += 1
        frame_id = f"frame-{self._sequence:08d}-{uuid.uuid4().hex[:8]}"
        envelope = FrameEnvelope(
            frame_id=frame_id,
            sequence=self._sequence,
            source=source,
            target=target,
            window_id=window_id,
            captured_at=now,
            monotonic_at=time.monotonic(),
            width=width,
            height=height,
            digest=digest,
            byte_length=len(payload),
            capture_latency_ms=capture_latency_ms,
            duplicate_of=duplicate_of,
            freshness="duplicate" if duplicate_of else "fresh",
            metadata=metadata or {},
        )
        record = FrameRecord(envelope, payload)
        self.records.append(record)
        self._prune(now)
        if self.frame_dir:
            path = self.frame_dir / f"{frame_id}.png"
            temporary = path.with_suffix(".png.tmp")
            temporary.write_bytes(payload)
            temporary.replace(path)
            envelope.stream_ref = str(path)
        return record

    def _prune(self, now: float) -> None:
        cutoff = now - self.retention_seconds
        while self.records and self.records[0].envelope.captured_at < cutoff:
            old = self.records.popleft()
            if self.frame_dir and old.envelope.stream_ref:
                try:
                    Path(old.envelope.stream_ref).unlink()
                except FileNotFoundError:
                    pass

    def latest(self) -> FrameRecord | None:
        return self.records[-1] if self.records else None

    def by_id(self, frame_id: str) -> FrameRecord | None:
        return next((record for record in self.records if record.envelope.frame_id == frame_id), None)

    def since(self, sequence: int = 0) -> list[FrameRecord]:
        return [record for record in self.records if record.envelope.sequence > sequence]

    def metadata(self) -> list[dict[str, Any]]:
        return [record.envelope.to_dict() for record in self.records]

    def age_ms(self, now: float | None = None) -> float | None:
        latest = self.latest()
        if latest is None:
            return None
        return max(0.0, ((now if now is not None else time.time()) - latest.envelope.captured_at) * 1000)


def compare_frames(
    previous: bytes | None,
    current: bytes | None,
    *,
    popup_before: bool = False,
    popup_after: bool = False,
    loading_after: bool = False,
    closed_after: bool = False,
    minor_threshold: float = 0.002,
    changed_threshold: float = 0.02,
) -> DiffResult:
    if closed_after or current is None:
        return DiffResult(DiffKind.WINDOW_CLOSED, 1.0, 1.0, True, "kein aktueller Frame")
    if popup_after and not popup_before:
        return DiffResult(DiffKind.POPUP_APPEARED, 1.0, 1.0, True, "Popup erschien")
    if popup_before and not popup_after:
        return DiffResult(DiffKind.POPUP_CLOSED, 1.0, 1.0, True, "Popup verschwand")
    if previous is None:
        return DiffResult(DiffKind.UNKNOWN, 1.0, 1.0, True, "kein Vergleichsframe")
    if previous == current:
        return DiffResult(DiffKind.UNCHANGED, 0.0, 0.0, False, "Bytefolge unverändert")
    try:
        with Image.open(io.BytesIO(previous)).convert("RGB") as old_image:
            with Image.open(io.BytesIO(current)).convert("RGB") as new_image:
                if old_image.size != new_image.size:
                    return DiffResult(DiffKind.CAMERA_MOVED, 1.0, 1.0, True, "Framegröße änderte sich")
                # Downsampling keeps the 100-ms loop bounded while the full
                # frames remain available in the timeline as evidence.
                old_small = old_image.resize((min(256, old_image.width), min(256, old_image.height)))
                new_small = new_image.resize(old_small.size)
                diff = ImageChops.difference(old_small, new_small)
                stat = ImageStat.Stat(diff)
                mean = sum(stat.mean) / (len(stat.mean) * 255.0)
                changed = sum(1 for pixel in diff.convert("L").getdata() if pixel > 12)
                ratio = changed / max(1, diff.width * diff.height)
        if mean < minor_threshold and ratio < minor_threshold:
            return DiffResult(DiffKind.MINOR_CHANGE, ratio, mean, True, "nur geringe Bildänderung")
        kind = DiffKind.LOADING if loading_after else DiffKind.CAMERA_MOVED
        if ratio < changed_threshold:
            kind = DiffKind.MINOR_CHANGE
        return DiffResult(kind, ratio, mean, True, "signifikante Bildänderung")
    except Exception as error:
        return DiffResult(DiffKind.UNKNOWN, 1.0, 1.0, True, f"Vergleich nicht möglich: {error}")
