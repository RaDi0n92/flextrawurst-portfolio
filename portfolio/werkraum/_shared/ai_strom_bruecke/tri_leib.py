#!/usr/bin/env python3
"""Dreileibiger Wahrnehmungsvertrag for platform objects."""

from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from typing import Any

from .contracts import TriViewObject


DEFAULT_ROT_BLOCK = [
    "alte_falsche_aliasverknuepfung",
    "nicht_aus_beobachtung_als_wesenwunsch_lesen",
    "nicht_aus_beobachtung_als_adminpflicht_lesen",
]


class TriViewValidationError(ValueError):
    pass


def _required(mapping: Mapping[str, Any], fields: tuple[str, ...], name: str) -> None:
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise TriViewValidationError(f"{name} fehlen: {', '.join(missing)}")


def validate_tri_view_object(obj: TriViewObject | Mapping[str, Any]) -> None:
    value = obj.to_dict() if isinstance(obj, TriViewObject) else obj
    _required(
        value,
        ("object_id", "object_type", "version", "identity", "provenance",
         "codewesen_leib", "menschen_leib", "organ_leib", "rot_block"),
        "Objektvertrag",
    )
    if not value["object_id"] or not value["object_type"]:
        raise TriViewValidationError("Objektidentität darf nicht leer sein")
    if not isinstance(value["rot_block"], list):
        raise TriViewValidationError("rot_block muss eine Liste sein")
    _required(
        value["codewesen_leib"],
        ("dom_kind", "dom_path", "html_fragment", "css_states", "ids", "classes",
         "actions", "order", "freshness", "changed_since", "forbidden_context", "confidence"),
        "Codewesen-Leib",
    )
    _required(
        value["menschen_leib"],
        ("scene", "motion", "depth", "visual_weight", "animation", "interaction", "render_metrics"),
        "Menschen-Leib",
    )
    _required(
        value["organ_leib"],
        ("linked_organs", "kompoase_effect", "splitter_effect", "groups_effect",
         "shadow_effect", "resonance_effect", "profile_effect", "counter_effect",
         "provenance_effect", "rot_guard"),
        "Organ-Leib",
    )
    if value["codewesen_leib"]["dom_kind"] not in {"real", "semantic-proxy"}:
        raise TriViewValidationError("dom_kind muss real oder semantic-proxy sein")
    if value["codewesen_leib"]["dom_kind"] == "semantic-proxy" and not value["codewesen_leib"].get("confidence"):
        raise TriViewValidationError("semantic-proxy braucht eine positive Konfidenz")


def build_tri_view_capsule(
    source: Mapping[str, Any],
    *,
    context: Mapping[str, Any] | None = None,
    now: float | None = None,
    dom_kind: str = "real",
    dom_path: str = "",
    html_fragment: str = "",
    css_states: list[str] | None = None,
    actions: list[str] | None = None,
    forbidden_context: list[str] | None = None,
    organ_overrides: Mapping[str, Any] | None = None,
) -> TriViewObject:
    """Atomically create all three leiber from one canonical object.

    ``source`` remains provenance material; no LLM or hidden enrichment is
    performed.  Callers may provide a native semantic proxy by setting
    ``dom_kind`` and its evidence/confidence in ``context``.
    """
    timestamp = now if now is not None else time.time()
    object_id = str(source.get("object_id") or source.get("id") or f"object-{uuid.uuid4().hex}")
    object_type = str(source.get("object_type") or source.get("type") or "world-object")
    identity = {
        "deep_link": source.get("deep_link") or f"/objects/{object_id}",
        "share": source.get("share") or f"/share/{object_id}",
        "avatar": source.get("avatar") or f"/avatar/{object_id}",
        "counter": source.get("counter", 0),
    }
    provenance = list(source.get("provenance", []))
    rot_block = list(forbidden_context or source.get("rot_block", []) or DEFAULT_ROT_BLOCK)
    context = context or {}
    code_confidence = float(context.get("dom_confidence", 1.0 if dom_kind == "real" else 0.0))
    code_leib = {
        "dom_kind": dom_kind,
        "dom_path": dom_path or str(source.get("dom_path", "")),
        "html_fragment": html_fragment or str(source.get("html_fragment", "")),
        "css_states": list(css_states or source.get("css_states", [])),
        "ids": list(source.get("ids", [object_id])),
        "classes": list(source.get("classes", [])),
        "actions": list(actions or source.get("actions", [])),
        "order": int(source.get("order", 0)),
        "freshness": dict(source.get("freshness", {"status": "now"})),
        "changed_since": source.get("changed_since"),
        "forbidden_context": rot_block,
        "confidence": code_confidence,
        "source": context.get("dom_source", "canonical-object"),
    }
    human_leib = {
        "scene": source.get("scene", f"wahrnehmbares Objekt {object_id}"),
        "motion": source.get("motion", "stabil"),
        "depth": source.get("depth", "nah"),
        "visual_weight": source.get("visual_weight", "mittel"),
        "animation": dict(source.get("animation", {})),
        "interaction": list(source.get("interaction", [])),
        "render_metrics": dict(source.get("render_metrics", {})),
    }
    organ_leib = {
        "linked_organs": list(source.get("linked_organs", [])),
        "kompoase_effect": dict(source.get("kompoase_effect", {})),
        "splitter_effect": dict(source.get("splitter_effect", {})),
        "groups_effect": dict(source.get("groups_effect", {})),
        "shadow_effect": dict(source.get("shadow_effect", {})),
        "resonance_effect": dict(source.get("resonance_effect", {})),
        "profile_effect": dict(source.get("profile_effect", {})),
        "counter_effect": dict(source.get("counter_effect", {})),
        "provenance_effect": {"sources": provenance},
        "rot_guard": rot_block,
    }
    if organ_overrides is None and isinstance(source.get("organ_overrides"), Mapping):
        organ_overrides = source.get("organ_overrides")
    if organ_overrides:
        for key, value in organ_overrides.items():
            if key not in organ_leib:
                raise TriViewValidationError(f"unbekannter Organ-Leib: {key}")
            organ_leib[key] = value
    result = TriViewObject(
        object_id=object_id,
        object_type=object_type,
        version=int(source.get("version", 1)),
        identity=identity,
        provenance=provenance,
        codewesen_leib=code_leib,
        menschen_leib=human_leib,
        organ_leib=organ_leib,
        rot_block=rot_block,
        created_at=float(source.get("created_at", timestamp)),
        changed_at=float(source.get("changed_at", timestamp)),
    )
    validate_tri_view_object(result)
    return result
