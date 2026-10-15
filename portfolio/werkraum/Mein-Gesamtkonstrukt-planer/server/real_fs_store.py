#!/usr/bin/env python3
"""Concurrency-safe persistence primitives for real_fs approval/write flows.

This module is deliberately Django-free so proposal/fingerprint/effect semantics can
be tested in isolation before wiring them into the live HTTP endpoints.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class RealFsStoreError(RuntimeError):
    pass


class ChangeNotFound(RealFsStoreError):
    pass


class ChangeAlreadyResolved(RealFsStoreError):
    pass


class StaleTarget(RealFsStoreError):
    def __init__(self, expected: dict[str, Any], actual: dict[str, Any]):
        super().__init__("stale_target")
        self.expected = expected
        self.actual = actual


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(content: str) -> str:
    return sha256_bytes(content.encode("utf-8"))


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def target_fingerprint(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {"exists": False, "kind": "missing", "sha256": None, "size": None}
    if path.is_file():
        stat = path.stat()
        return {
            "exists": True,
            "kind": "file",
            "sha256": sha256_file(path),
            "size": stat.st_size,
        }
    if path.is_dir():
        return {"exists": True, "kind": "folder", "sha256": None, "size": None}
    return {"exists": True, "kind": "other", "sha256": None, "size": None}


def same_target(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return False
    if bool(expected.get("exists")) != bool(actual.get("exists")):
        return False
    if expected.get("kind") != actual.get("kind"):
        return False
    if expected.get("kind") == "file":
        return expected.get("sha256") == actual.get("sha256")
    return True


def atomic_json_list(path: Path, entries: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{uuid.uuid4().hex}")
    payload = json.dumps(entries, ensure_ascii=False, indent=2) + "\n"
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_text_write(path: Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{uuid.uuid4().hex}")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass


class JsonListStore:
    def __init__(self, path: Path, lock_path: Path | None = None):
        self.path = Path(path)
        self.lock_path = Path(lock_path or self.path.with_name(self.path.name + ".lock"))

    @contextmanager
    def locked(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _read_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise RealFsStoreError(f"invalid_json_list: {self.path}: {exc}") from exc
        if not isinstance(value, list):
            raise RealFsStoreError(f"json_root_not_list: {self.path}")
        return value

    def read(self) -> list[dict[str, Any]]:
        with self.locked():
            return copy.deepcopy(self._read_unlocked())

    def mutate(self, fn: Callable[[list[dict[str, Any]]], Any]) -> Any:
        with self.locked():
            entries = self._read_unlocked()
            result = fn(entries)
            atomic_json_list(self.path, entries)
            return copy.deepcopy(result)


class RealFsChangeStore:
    """Atomic lifecycle for proposal/approval/effect metadata.

    The real target file is intentionally not locked by this store because other
    CLI tools do not share our advisory lock. Stale-target checking therefore
    protects against ordinary delayed approvals but cannot provide mathematical
    CAS against an uncooperative writer racing in the tiny check->replace window.
    """

    def __init__(self, pending_file: Path, lock_file: Path | None = None):
        self.store = JsonListStore(pending_file, lock_file)

    @staticmethod
    def _find(entries: list[dict[str, Any]], change_id: str) -> dict[str, Any]:
        for change in entries:
            if isinstance(change, dict) and change.get("id") == change_id:
                return change
        raise ChangeNotFound(change_id)

    def read_all(self) -> list[dict[str, Any]]:
        return self.store.read()

    def get(self, change_id: str) -> dict[str, Any]:
        entries = self.store.read()
        return copy.deepcopy(self._find(entries, change_id))

    def add(self, change: dict[str, Any]) -> dict[str, Any]:
        change = copy.deepcopy(change)
        change_id = str(change.get("id") or "").strip()
        if not change_id:
            raise RealFsStoreError("change_id_required")

        def mutate(entries):
            if any(isinstance(item, dict) and item.get("id") == change_id for item in entries):
                raise RealFsStoreError(f"change_already_exists: {change_id}")
            entries.append(change)
            return change

        return self.store.mutate(mutate)

    def mark_stale(
        self,
        change_id: str,
        *,
        actual_target: dict[str, Any],
        checked_at: str | None = None,
    ) -> dict[str, Any]:
        def mutate(entries):
            change = self._find(entries, change_id)
            if change.get("status") != "pending":
                raise ChangeAlreadyResolved(change_id)
            change["effectStatus"] = "stale"
            change["staleCheckedAt"] = checked_at or now_iso()
            change["staleActualTarget"] = copy.deepcopy(actual_target)
            return change

        return self.store.mutate(mutate)

    def claim_approval(
        self,
        change_id: str,
        *,
        actual_target: dict[str, Any],
        resolved_at: str | None = None,
    ) -> dict[str, Any]:
        """Mark human approval and claim the effect execution.

        Requires a proposal-time expectedTarget fingerprint. Legacy pending changes
        without it must be re-proposed instead of being approved unsafely.
        """

        stale_payload: dict[str, Any] = {}

        def mutate(entries):
            change = self._find(entries, change_id)
            if change.get("status") != "pending":
                raise ChangeAlreadyResolved(change_id)
            expected = change.get("expectedTarget")
            if not isinstance(expected, dict):
                raise RealFsStoreError("proposal_missing_expected_target")
            if not same_target(expected, actual_target):
                change["effectStatus"] = "stale"
                change["staleCheckedAt"] = resolved_at or now_iso()
                change["staleActualTarget"] = copy.deepcopy(actual_target)
                stale_payload.update(
                    {
                        "expected": copy.deepcopy(expected),
                        "actual": copy.deepcopy(actual_target),
                    }
                )
                return change

            at = resolved_at or now_iso()
            change["status"] = "approved"
            change["approvalStatus"] = "approved"
            change["resolvedAt"] = at
            change["effectStatus"] = "running"
            change["effectStartedAt"] = at
            change.pop("staleActualTarget", None)
            change.pop("staleCheckedAt", None)
            return change

        result = self.store.mutate(mutate)
        if stale_payload:
            raise StaleTarget(stale_payload["expected"], stale_payload["actual"])
        return result

    def finish_effect(
        self,
        change_id: str,
        *,
        effect_status: str,
        effect: dict[str, Any] | None = None,
        backup: str | None = None,
        finished_at: str | None = None,
    ) -> dict[str, Any]:
        if effect_status not in {"confirmed", "failed", "unknown"}:
            raise RealFsStoreError(f"invalid_effect_status: {effect_status}")

        def mutate(entries):
            change = self._find(entries, change_id)
            if change.get("status") != "approved":
                raise RealFsStoreError("effect_requires_approved_change")
            change["effectStatus"] = effect_status
            change["effectFinishedAt"] = finished_at or now_iso()
            if effect is not None:
                change["effect"] = copy.deepcopy(effect)
            change["backup"] = backup
            return change

        return self.store.mutate(mutate)

    def reject(self, change_id: str, *, resolved_at: str | None = None) -> dict[str, Any]:
        def mutate(entries):
            change = self._find(entries, change_id)
            if change.get("status") != "pending":
                raise ChangeAlreadyResolved(change_id)
            change["status"] = "rejected"
            change["approvalStatus"] = "rejected"
            change["effectStatus"] = "not_started"
            change["resolvedAt"] = resolved_at or now_iso()
            return change

        return self.store.mutate(mutate)
