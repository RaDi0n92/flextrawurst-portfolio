#!/usr/bin/env python3
"""Append-only store for canonical three-bodied perception objects."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from .tri_leib import build_tri_view_capsule, validate_tri_view_object


class TriViewObjectStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._objects: dict[str, dict[str, Any]] = {}
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
            obj = event.get("object")
            if isinstance(obj, dict) and obj.get("object_id"):
                self._objects[obj["object_id"]] = obj

    def _append(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")

    def create(self, source: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
        obj = build_tri_view_capsule(source, **kwargs)
        validate_tri_view_object(obj)
        value = obj.to_dict()
        if value["object_id"] in self._objects:
            raise ValueError(f"Objekt existiert bereits: {value['object_id']}")
        event = {
            "schema": "ai-strom-bruecke.triview-object-event.v1",
            "event_id": f"object-event-{uuid.uuid4().hex}",
            "event_type": "object.created",
            "created_at": time.time(),
            "object": value,
        }
        self._append(event)
        self._objects[value["object_id"]] = value
        return value

    def update(self, object_id: str, source: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
        previous = self._objects.get(object_id)
        if previous is None:
            raise KeyError(object_id)
        merged = dict(source)
        merged["object_id"] = object_id
        merged["version"] = int(previous.get("version", 1)) + 1
        merged["provenance"] = list(previous.get("provenance", [])) + list(source.get("provenance", []))
        organ_overrides = merged.pop("organ_overrides", None)
        obj = build_tri_view_capsule(merged, organ_overrides=organ_overrides, **kwargs)
        validate_tri_view_object(obj)
        value = obj.to_dict()
        event = {
            "schema": "ai-strom-bruecke.triview-object-event.v1",
            "event_id": f"object-event-{uuid.uuid4().hex}",
            "event_type": "object.updated",
            "created_at": time.time(),
            "before_version": previous.get("version"),
            "object": value,
        }
        self._append(event)
        self._objects[object_id] = value
        return value

    def get(self, object_id: str) -> dict[str, Any] | None:
        value = self._objects.get(object_id)
        return dict(value) if value else None

    def all(self) -> list[dict[str, Any]]:
        return [dict(value) for value in self._objects.values()]
