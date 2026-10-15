#!/usr/bin/env python3
"""Deterministic camera/focus claims derived from observed evidence."""

from __future__ import annotations

import time
import uuid
from typing import Any, Mapping

from .contracts import CameraState, CoordinateClaim, CoordinateKind
from .earth_perception import coordinate_plausible, local_pixel_rate


def build_camera_state(
    *,
    frame_id: str,
    target: str,
    pointer_claim: CoordinateClaim | None = None,
    center_claim: CoordinateClaim | None = None,
    zoom: float | None = None,
    eye_altitude_m: float | None = None,
    heading: float | None = None,
    tilt: float | None = None,
    loading: bool = False,
    popup: str | None = None,
    street_view: bool = False,
    focus: bool = True,
    calibration: Mapping[str, Any] | None = None,
) -> CameraState:
    confidence = 0.0
    if pointer_claim and coordinate_plausible(pointer_claim):
        confidence = max(confidence, pointer_claim.confidence)
    if center_claim and coordinate_plausible(center_claim):
        confidence = max(confidence, center_claim.confidence)
    return CameraState(
        state_id=f"camera-{uuid.uuid4().hex}", frame_id=frame_id,
        pointer_anchor=pointer_claim, map_center=center_claim, zoom=zoom,
        eye_altitude_m=eye_altitude_m, heading=heading, tilt=tilt,
        loading=loading, popup=popup, street_view=street_view, focus=focus,
        target=target, calibration=dict(calibration or {}), confidence=confidence,
        updated_at=time.time(),
    )


def center_claim_from_pointer(claim: CoordinateClaim, *, frame_id: str) -> CoordinateClaim:
    """Make the distinction explicit; no pointer claim is silently relabelled."""
    return CoordinateClaim(
        claim_id=f"claim-{uuid.uuid4().hex}", frame_id=frame_id,
        pointer_xy=claim.pointer_xy, coordinate_kind=CoordinateKind.CENTER,
        latitude=claim.latitude, longitude=claim.longitude,
        elevation_m=claim.elevation_m, eye_altitude_m=claim.eye_altitude_m,
        raw_text=claim.raw_text, normalized_text=claim.normalized_text,
        confidence=claim.confidence * 0.8, source="derived-center-from-pointer",
        observed_at=time.time(), metadata={"derived_from": claim.claim_id},
    )


def calibrate_pointer(first: CoordinateClaim, second: CoordinateClaim) -> dict[str, float]:
    return local_pixel_rate(first, second)


def classify_camera(*, focus: bool, popup: str | None, loading: bool, frame_available: bool) -> dict[str, Any]:
    if not frame_available:
        return {"state": "window-closed", "focus": False, "popup": popup, "loading": False}
    if not focus:
        return {"state": "focus-lost", "focus": False, "popup": popup, "loading": loading}
    if popup:
        return {"state": "popup", "focus": True, "popup": popup, "loading": loading}
    if loading:
        return {"state": "loading", "focus": True, "popup": None, "loading": True}
    return {"state": "ready", "focus": True, "popup": None, "loading": False}
