#!/usr/bin/env python3
"""Small append-only causal flow connecting the three object bodies."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from .contracts import WorldCausalEvent
from .object_store import TriViewObjectStore
from .organ_effects import derive_effects, merge_effects
from .tri_leib import validate_tri_view_object


class WorldFlow:
    def __init__(self, objects: TriViewObjectStore, events_path: Path) -> None:
        self.objects = objects
        self.events_path = events_path
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, event: WorldCausalEvent) -> None:
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({
                "schema": "ai-strom-bruecke.world-causal-event.v1",
                "event_type": "world.causal",
                "event": event.to_dict(),
            }, ensure_ascii=False, separators=(",", ":")) + "\n")

    def create(self, source: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        canonical = dict(source)
        canonical.setdefault("organ_overrides", derive_effects(str(canonical.get("object_type", canonical.get("type", "world-object")))))
        obj = self.objects.create(canonical)
        validate_tri_view_object(obj)
        event = WorldCausalEvent(
            event_id=f"world-event-{uuid.uuid4().hex}", object_id=obj["object_id"], action_id=None,
            source="world.create", before_state={}, after_state={"version": obj["version"]},
            human_effect={"surface": "created"}, organ_effect={"provenance": obj["provenance"]},
            codewesen_effect={"fresh_capsule": True}, created_at=time.time(),
            provenance=list(obj["provenance"]),
        )
        self._append(event)
        return obj, event.to_dict()

    def apply(self, object_id: str, *, source: str, action_id: str | None = None, human_effect: Mapping[str, Any] | None = None, organ_effect: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
        before = self.objects.get(object_id)
        if before is None:
            raise KeyError(object_id)
        human = dict(human_effect or {})
        organs = merge_effects(derive_effects(str(before.get("object_type", "world-object"))), organ_effect)
        update = {
            "scene": human.get("scene", before["menschen_leib"].get("scene")),
            "motion": human.get("motion", "aktualisiert"),
            "interaction": human.get("interaction", before["menschen_leib"].get("interaction", [])),
            "provenance": [f"world-event:{uuid.uuid4().hex}"],
            "linked_organs": before["organ_leib"].get("linked_organs", []),
            "organ_overrides": merge_effects({
                "kompoase_effect": before["organ_leib"].get("kompoase_effect", {}),
                "splitter_effect": before["organ_leib"].get("splitter_effect", {}),
                "groups_effect": before["organ_leib"].get("groups_effect", {}),
                "shadow_effect": before["organ_leib"].get("shadow_effect", {}),
                "resonance_effect": before["organ_leib"].get("resonance_effect", {}),
                "profile_effect": before["organ_leib"].get("profile_effect", {}),
                "counter_effect": before["organ_leib"].get("counter_effect", {}),
                "provenance_effect": {"sources": before["provenance"]},
            }, organs),
        }
        # Keep the generated provenance stable in the object and event.
        update["organ_overrides"]["provenance_effect"] = {"sources": before["provenance"] + update["provenance"]}
        after = self.objects.update(object_id, update)
        validate_tri_view_object(after)
        event = WorldCausalEvent(
            event_id=f"world-event-{uuid.uuid4().hex}", object_id=object_id, action_id=action_id,
            source=source, before_state={"version": before["version"], "object": before},
            after_state={"version": after["version"], "object": after},
            human_effect=human, organ_effect=organs,
            codewesen_effect={"fresh_capsule": True, "rot_block": after["rot_block"]},
            created_at=time.time(), provenance=list(after["provenance"]),
        )
        self._append(event)
        return after, event.to_dict()

    def all_events(self) -> list[dict[str, Any]]:
        try:
            lines = self.events_path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        result = []
        for line in lines:
            try:
                event = json.loads(line).get("event")
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                result.append(event)
        return result
