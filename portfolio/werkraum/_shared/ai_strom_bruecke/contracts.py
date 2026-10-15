#!/usr/bin/env python3
"""Versioned, serialisable contracts for the complete AI-Strom-Brücke.

The bridge has to carry evidence, not just convenient values.  These small
dataclasses are deliberately independent of FastAPI, Playwright and X11 so
the same objects can be used by the native adapter, the browser adapter, the
local cockpit and deterministic tests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class CoordinateKind(StrEnum):
    POINTER = "pointer"
    CENTER = "center"
    UNKNOWN = "unknown"


class ActionPhase(StrEnum):
    PLANNED = "planned"
    DISPATCHED = "dispatched"
    OBSERVED = "observed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ABORTED = "aborted"
    TIMED_OUT = "timed_out"
    STALE = "stale"
    UNSAFE = "unsafe"


class DiffKind(StrEnum):
    UNCHANGED = "unchanged"
    MINOR_CHANGE = "minor-change"
    CAMERA_MOVED = "camera-moved"
    TARGET_CHANGED = "target-changed"
    POPUP_APPEARED = "popup-appeared"
    POPUP_CLOSED = "popup-closed"
    LOADING = "loading"
    WINDOW_CLOSED = "window-closed"
    CAPTURE_ERROR = "capture-error"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class FrameEnvelope:
    frame_id: str
    sequence: int
    source: str
    target: str
    window_id: str | None
    captured_at: float
    monotonic_at: float
    width: int
    height: int
    digest: str
    byte_length: int
    stream_ref: str | None = None
    capture_latency_ms: float | None = None
    age_ms: float = 0.0
    duplicate_of: str | None = None
    freshness: str = "fresh"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CoordinateClaim:
    claim_id: str
    frame_id: str
    pointer_xy: dict[str, int] | None
    coordinate_kind: CoordinateKind
    latitude: float | None
    longitude: float | None
    elevation_m: float | None
    eye_altitude_m: float | None
    raw_text: str
    normalized_text: str
    confidence: float
    source: str
    observed_at: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["coordinate_kind"] = self.coordinate_kind.value
        return result


@dataclass(slots=True)
class CameraState:
    state_id: str
    frame_id: str | None
    pointer_anchor: CoordinateClaim | None
    map_center: CoordinateClaim | None
    zoom: float | None
    eye_altitude_m: float | None
    heading: float | None
    tilt: float | None
    loading: bool
    popup: str | None
    street_view: bool
    focus: bool
    target: str
    calibration: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    updated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["pointer_anchor"] = self.pointer_anchor.to_dict() if self.pointer_anchor else None
        result["map_center"] = self.map_center.to_dict() if self.map_center else None
        return result


@dataclass(slots=True)
class ActionExpectation:
    expected_diff: list[DiffKind] = field(default_factory=list)
    expected_coordinate_delta: dict[str, float] = field(default_factory=dict)
    expected_target: str | None = None
    timeout_ms: int = 1500
    minimum_confidence: float = 0.6
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["expected_diff"] = [item.value for item in self.expected_diff]
        return result


@dataclass(slots=True)
class ActionTransaction:
    action_id: str
    actor: str
    lease_id: str | None
    target: str
    action_type: str
    phase: ActionPhase
    planned_at: float
    dispatched_at: float | None = None
    observed_at: float | None = None
    released_at: float | None = None
    pointer_start: dict[str, int] | None = None
    pointer_end: dict[str, int] | None = None
    button: int | None = None
    key: str | None = None
    held_buttons: list[int] = field(default_factory=list)
    held_keys: list[str] = field(default_factory=list)
    input_sequence: list[dict[str, Any]] = field(default_factory=list)
    expectation: ActionExpectation = field(default_factory=ActionExpectation)
    observed_frames: list[str] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    rejection_reason: str | None = None
    provenance: list[str] = field(default_factory=list)

    def transition(self, phase: ActionPhase, **result: Any) -> None:
        self.phase = phase
        self.result.update(result)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["phase"] = self.phase.value
        result["expectation"] = self.expectation.to_dict()
        return result


@dataclass(slots=True)
class TriViewObject:
    object_id: str
    object_type: str
    version: int
    identity: dict[str, Any]
    provenance: list[str]
    codewesen_leib: dict[str, Any]
    menschen_leib: dict[str, Any]
    organ_leib: dict[str, Any]
    rot_block: list[str]
    created_at: float
    changed_at: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WorldCausalEvent:
    event_id: str
    object_id: str
    action_id: str | None
    source: str
    before_state: dict[str, Any]
    after_state: dict[str, Any]
    human_effect: dict[str, Any]
    organ_effect: dict[str, Any]
    codewesen_effect: dict[str, Any]
    created_at: float
    visibility: str = "public"
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def jsonable(value: Any) -> Any:
    """Convert nested contract values without losing enum evidence."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value
