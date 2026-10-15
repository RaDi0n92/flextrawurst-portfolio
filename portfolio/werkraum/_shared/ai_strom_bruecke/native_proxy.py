#!/usr/bin/env python3
"""Build honest semantic-proxy objects for native/OpenGL observations."""

from __future__ import annotations

from typing import Any

from .contracts import CoordinateClaim
from .tri_leib import build_tri_view_capsule


def native_claim_to_capsule(
    *,
    object_id: str,
    object_type: str,
    label: str,
    window_id: str,
    frame_id: str,
    claim: CoordinateClaim,
    actions: list[str] | None = None,
    provenance: list[str] | None = None,
) -> dict[str, Any]:
    confidence = claim.confidence
    return build_tri_view_capsule(
        {
            "object_id": object_id,
            "object_type": object_type,
            "provenance": list(provenance or []) + [frame_id, claim.claim_id],
            "scene": label,
            "actions": list(actions or []),
            "linked_organs": ["provenance", "resonanz"],
            "deep_link": f"native://{window_id}/{object_id}",
            "share": f"/share/{object_id}",
            "rot_block": ["nicht_als_html_dom_behaupten", "nicht_als_sichere_ocr_ohne_beleg_lesen"],
            "dom_path": f"x11://{window_id}/frame/{frame_id}/label/{object_id}",
            "html_fragment": "",
            "ids": [object_id],
            "classes": ["native-proxy", object_type],
            "freshness": {"status": "frame-bound", "frame_id": frame_id},
        },
        context={"dom_kind": "semantic-proxy", "dom_confidence": confidence, "dom_source": claim.source},
        dom_kind="semantic-proxy",
        dom_path=f"x11://{window_id}/frame/{frame_id}/label/{object_id}",
        html_fragment="",
        actions=list(actions or []),
        forbidden_context=["nicht_als_html_dom_behaupten", "nicht_als_sichere_ocr_ohne_beleg_lesen"],
    ).to_dict()
