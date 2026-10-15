#!/usr/bin/env python3
"""Append-only, evidence-backed confirmed places and camera anchors."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from .contracts import CameraState, CoordinateClaim
from .earth_perception import coordinate_plausible


_SCENE_CONTEXTS_REQUIRING_LABEL = {
    "water", "lake", "see", "forest", "wood", "woods", "wald",
}


def _claim_value(claim: CoordinateClaim | Mapping[str, Any]) -> dict[str, Any]:
    return claim.to_dict() if isinstance(claim, CoordinateClaim) else dict(claim)


def _map_bounds(camera: Mapping[str, Any]) -> tuple[float, float, float, float] | None:
    raw = camera.get("map_bounds")
    if not isinstance(raw, Mapping):
        return None
    if all(key in raw for key in ("left", "top", "right", "bottom")):
        return tuple(float(raw[key]) for key in ("left", "top", "right", "bottom"))
    if all(key in raw for key in ("x", "y", "width", "height")):
        left, top = float(raw["x"]), float(raw["y"])
        return left, top, left + float(raw["width"]), top + float(raw["height"])
    return None


def validate_anchor_candidate(
    claim: CoordinateClaim | Mapping[str, Any],
    camera: CameraState | Mapping[str, Any],
    *,
    frame_id: str,
    minimum_confidence: float = 0.6,
) -> dict[str, Any]:
    """Return an explicit, deterministic acceptance decision for an Earth anchor.

    Optional camera evidence is additive: old callers without map/scene fields
    retain the FW-26 contract, while richer Earth frames get the FW-27 guard.
    """
    claim_value = _claim_value(claim)
    camera_value = camera.to_dict() if isinstance(camera, CameraState) else dict(camera)
    reasons: list[str] = []
    latitude = claim_value.get("latitude")
    longitude = claim_value.get("longitude")
    try:
        plausible = latitude is not None and longitude is not None and -90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180
    except (TypeError, ValueError):
        plausible = False
    if not plausible:
        reasons.append("coordinate-invalid-or-unparsed")
    if claim_value.get("coordinate_kind") != "pointer":
        reasons.append("coordinate-is-not-pointer-claim")
    if claim_value.get("confidence", 0) < minimum_confidence:
        reasons.append("coordinate-confidence-too-low")
    if claim_value.get("frame_id") and claim_value.get("frame_id") != frame_id:
        reasons.append("claim-frame-mismatch")
    pointer = claim_value.get("pointer_xy")
    if not isinstance(pointer, Mapping) or pointer.get("x") is None or pointer.get("y") is None:
        reasons.append("pointer-position-missing")

    bounds = _map_bounds(camera_value)
    if bounds and isinstance(pointer, Mapping):
        left, top, right, bottom = bounds
        margin = float(camera_value.get("anchor_safe_margin_px", 16))
        x, y = float(pointer["x"]), float(pointer["y"])
        if not (left + margin <= x <= right - margin and top + margin <= y <= bottom - margin):
            reasons.append("pointer-at-map-edge-or-outside-safe-rect")

    scene = str(camera_value.get("scene_context", "")).strip().lower()
    if scene in _SCENE_CONTEXTS_REQUIRING_LABEL and camera_value.get("target_label_visible") is not True:
        reasons.append("scene-needs-visible-target-label")

    diff = camera_value.get("frame_diff") or camera_value.get("diff")
    diff_kind = diff.get("kind") if isinstance(diff, Mapping) else diff
    if diff_kind == "unchanged" or camera_value.get("frame_changed") is False:
        reasons.append("evidence-frame-unchanged")
    if camera_value.get("focus") is False:
        reasons.append("earth-focus-not-confirmed")
    if camera_value.get("popup"):
        reasons.append("popup-covers-map")

    return {
        "accepted": not reasons,
        "reasons": reasons,
        "checks": {
            "coordinate_plausible": plausible,
            "pointer_claim": claim_value.get("coordinate_kind") == "pointer",
            "confidence": claim_value.get("confidence", 0),
            "safe_map_rect": bounds is None or "pointer-at-map-edge-or-outside-safe-rect" not in reasons,
            "scene_context": scene or None,
            "frame_changed": "evidence-frame-unchanged" not in reasons,
        },
    }


class AnchorStore:
    """Keep a reusable location only together with its proof frame and claim."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._anchors: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            anchor = event.get("anchor")
            if isinstance(anchor, dict) and anchor.get("anchor_id"):
                self._anchors[anchor["anchor_id"]] = anchor

    def _append(self, event: Mapping[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(dict(event), ensure_ascii=False, separators=(",", ":")) + "\n")

    def create(
        self,
        *,
        label: str,
        claim: CoordinateClaim | Mapping[str, Any],
        camera: CameraState | Mapping[str, Any],
        frame_id: str,
        frame_digest: str,
        frame_path: str | None = None,
        provenance: list[str] | None = None,
    ) -> dict[str, Any]:
        claim_value = claim.to_dict() if isinstance(claim, CoordinateClaim) else dict(claim)
        camera_value = camera.to_dict() if isinstance(camera, CameraState) else dict(camera)
        if not frame_id or not frame_digest:
            raise ValueError("Anker braucht Belegframe und Digest")
        validation = validate_anchor_candidate(claim_value, camera_value, frame_id=frame_id)
        if not validation["accepted"]:
            raise ValueError("Anker abgelehnt: " + ", ".join(validation["reasons"]))
        anchor = {
            "anchor_id": f"anchor-{uuid.uuid4().hex}",
            "label": label,
            "claim": claim_value,
            "camera": camera_value,
            "frame_id": frame_id,
            "frame_digest": frame_digest,
            "frame_path": frame_path,
            "provenance": list(provenance or []) + [frame_id, claim_value.get("claim_id", "")],
            "confirmed_at": time.time(),
            "status": "confirmed",
        }
        self._append({
            "schema": "ai-strom-bruecke.anchor-event.v1",
            "event_id": f"anchor-event-{uuid.uuid4().hex}",
            "event_type": "anchor.confirmed",
            "created_at": time.time(),
            "anchor": anchor,
        })
        self._anchors[anchor["anchor_id"]] = anchor
        return dict(anchor)

    def get(self, anchor_id: str) -> dict[str, Any] | None:
        anchor = self._anchors.get(anchor_id)
        return dict(anchor) if anchor else None

    def all(self) -> list[dict[str, Any]]:
        return [dict(anchor) for anchor in self._anchors.values()]
