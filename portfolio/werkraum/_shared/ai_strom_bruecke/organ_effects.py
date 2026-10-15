#!/usr/bin/env python3
"""Explicit, additive organ effects for platform object families."""

from __future__ import annotations

from typing import Any, Mapping


FAMILIES = {
    "post": ("kompoase", "resonanz", "profile", "counter"),
    "splitter": ("splitter", "kompoase", "resonanz"),
    "group": ("gruppen", "resonanz", "counter"),
    "shadow-comment": ("shadow", "resonanz", "profile"),
    "kompoase": ("kompoase", "splitter", "provenienz"),
    "profile": ("profile", "resonanz", "counter"),
}


def derive_effects(object_type: str, source: Mapping[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Return visible organ effects; unknown types remain explicit and empty."""
    source = source or {}
    family = FAMILIES.get(object_type, ())
    effects: dict[str, dict[str, Any]] = {
        "kompoase_effect": {}, "splitter_effect": {}, "groups_effect": {},
        "shadow_effect": {}, "resonance_effect": {}, "profile_effect": {},
        "counter_effect": {}, "provenance_effect": {},
    }
    for organ in family:
        key = {
            "kompoase": "kompoase_effect", "splitter": "splitter_effect", "gruppen": "groups_effect",
            "shadow": "shadow_effect", "resonanz": "resonance_effect", "profile": "profile_effect",
            "counter": "counter_effect", "provenienz": "provenance_effect",
        }[organ]
        effects[key] = {"organ": organ, "object_type": object_type, "status": "linked", "input": source.get(organ)}
    return effects


def merge_effects(base: Mapping[str, Any], override: Mapping[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    value = {key: dict(item) if isinstance(item, Mapping) else {} for key, item in base.items()}
    for key, item in (override or {}).items():
        if key in value:
            value[key] = dict(item) if isinstance(item, Mapping) else {}
    return value
