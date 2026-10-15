#!/usr/bin/env python3
"""Durable evidence-bound Goals for the Gesamtkonstrukt world state.

Goals are a facet in current.json, not a new planner object kind. A Goal describes
a desired world state and explicit criteria. This module never infers success from
LLM prose or a completed Run: achieved is only valid when every criterion is
explicitly marked met and each met criterion carries at least one evidence ref.
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

from world_state import DEFAULT_STORE, WorldStateStore, now_iso


GOAL_SCHEMA = "gkos.goal.v0"
GOAL_STATUSES = {"active", "paused", "achieved", "abandoned", "needs_revision"}
CRITERION_STATUSES = {"unknown", "met", "unmet"}
GOAL_TRANSITIONS = {
    "active": {"active", "paused", "achieved", "abandoned", "needs_revision"},
    "paused": {"paused", "active", "abandoned", "needs_revision"},
    "needs_revision": {"needs_revision", "active", "paused", "abandoned"},
    # An achieved goal may be reopened only as needs_revision when later evidence
    # invalidates the contract. It does not silently become active again.
    "achieved": {"achieved", "needs_revision"},
    "abandoned": {"abandoned", "needs_revision"},
}


class GoalStateError(RuntimeError):
    pass


class GoalNotFound(GoalStateError):
    pass


class GoalVersionConflict(GoalStateError):
    def __init__(self, goal_id: str, expected: int, actual: int):
        super().__init__(
            f"goal_version_conflict: goal={goal_id} expected={expected} actual={actual}"
        )
        self.goal_id = goal_id
        self.expected = expected
        self.actual = actual


class InvalidGoalTransition(GoalStateError):
    pass


def _goals(state: dict[str, Any]) -> list[dict[str, Any]]:
    goals = state.setdefault("goals", [])
    if not isinstance(goals, list):
        raise GoalStateError("goals_must_be_list")
    return goals


def _find_goal(state: dict[str, Any], goal_id: str) -> dict[str, Any]:
    for goal in _goals(state):
        if isinstance(goal, dict) and goal.get("id") == goal_id:
            return goal
    raise GoalNotFound(goal_id)


def _clean_refs(values: list[str] | tuple[str, ...] | None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _clean_status(value: str, allowed: set[str], label: str) -> str:
    status = str(value or "").strip()
    if status not in allowed:
        raise GoalStateError(f"invalid_{label}_status: {status}")
    return status


def _normalize_criteria(criteria: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    for raw in criteria or []:
        if not isinstance(raw, dict):
            raise GoalStateError("criterion_must_be_object")
        statement = str(raw.get("statement") or "").strip()
        if not statement:
            raise GoalStateError("criterion_statement_required")
        criterion_id = str(raw.get("id") or f"criterion-{uuid.uuid4()}").strip()
        if not criterion_id or criterion_id in ids:
            raise GoalStateError("criterion_id_duplicate_or_empty")
        ids.add(criterion_id)
        status = _clean_status(str(raw.get("status") or "unknown"), CRITERION_STATUSES, "criterion")
        evidence = _clean_refs(raw.get("evidenceRefs") if isinstance(raw.get("evidenceRefs"), list) else None)
        if status == "met" and not evidence:
            raise GoalStateError("met_criterion_requires_evidence")
        normalized.append(
            {
                "id": criterion_id,
                "statement": statement,
                "status": status,
                "evidenceRefs": evidence,
                "note": str(raw.get("note") or "").strip() or None,
            }
        )
    return normalized


def _assert_achievable(goal: dict[str, Any]) -> None:
    criteria = goal.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise InvalidGoalTransition("achieved_requires_criteria")
    for criterion in criteria:
        if criterion.get("status") != "met":
            raise InvalidGoalTransition("achieved_requires_all_criteria_met")
        if not _clean_refs(criterion.get("evidenceRefs") if isinstance(criterion.get("evidenceRefs"), list) else None):
            raise InvalidGoalTransition("achieved_requires_evidence_for_every_criterion")


def read_goals(store: WorldStateStore = DEFAULT_STORE) -> list[dict[str, Any]]:
    return copy.deepcopy(_goals(store.read_wrapper()["state"]))


def read_goal(goal_id: str, store: WorldStateStore = DEFAULT_STORE) -> dict[str, Any]:
    return copy.deepcopy(_find_goal(store.read_wrapper()["state"], goal_id))


def create_goal(
    *,
    construct_ref: str,
    desired_state: str,
    title: str | None = None,
    scope_refs: list[str] | tuple[str, ...] | None = None,
    criteria: list[dict[str, Any]] | None = None,
    status: str = "active",
    goal_id: str | None = None,
    store: WorldStateStore = DEFAULT_STORE,
    expected_server_revision: int | None = None,
) -> dict[str, Any]:
    construct_ref = str(construct_ref or "").strip()
    desired_state = str(desired_state or "").strip()
    if not construct_ref:
        raise GoalStateError("construct_ref_required")
    if not desired_state:
        raise GoalStateError("desired_state_required")
    status = _clean_status(status, GOAL_STATUSES, "goal")
    normalized_criteria = _normalize_criteria(criteria)
    if status == "achieved":
        probe = {"criteria": normalized_criteria}
        _assert_achievable(probe)

    at = now_iso()
    gid = str(goal_id or f"goal-{uuid.uuid4()}")
    goal = {
        "schema": GOAL_SCHEMA,
        "id": gid,
        "version": 1,
        "constructRef": construct_ref,
        "title": str(title or "").strip() or None,
        "desiredState": desired_state,
        "scopeRefs": _clean_refs(scope_refs),
        "status": status,
        "criteria": normalized_criteria,
        "evidenceRefs": [],
        "createdAt": at,
        "updatedAt": at,
        "achievedAt": at if status == "achieved" else None,
    }

    def mutate(state: dict[str, Any]):
        goals = _goals(state)
        if any(isinstance(item, dict) and item.get("id") == gid for item in goals):
            raise GoalStateError(f"goal_already_exists: {gid}")
        goals.append(copy.deepcopy(goal))
        return {
            "goalRef": gid,
            "constructRef": construct_ref,
            "status": status,
            "goalVersion": 1,
        }

    result = store.commit(
        mutate,
        event_type="goal.created",
        event_data={
            "goalRef": gid,
            "constructRef": construct_ref,
            "status": status,
        },
        expected_server_revision=expected_server_revision,
    )
    return copy.deepcopy(_find_goal(result.wrapper["state"], gid))


def update_goal(
    goal_id: str,
    *,
    status: str | None = None,
    title: str | None | object = ...,
    desired_state: str | None = None,
    scope_refs: list[str] | tuple[str, ...] | None | object = ...,
    evidence_ref: str | None = None,
    criterion_id: str | None = None,
    criterion_status: str | None = None,
    criterion_evidence_ref: str | None = None,
    criterion_note: str | None | object = ...,
    expected_goal_version: int | None = None,
    expected_server_revision: int | None = None,
    store: WorldStateStore = DEFAULT_STORE,
) -> dict[str, Any]:
    gid = str(goal_id or "").strip()
    if not gid:
        raise GoalStateError("goal_id_required")

    change_summary: dict[str, Any] = {}

    def mutate(state: dict[str, Any]):
        goal = _find_goal(state, gid)
        actual_version = int(goal.get("version") or 0)
        if expected_goal_version is not None and int(expected_goal_version) != actual_version:
            raise GoalVersionConflict(gid, int(expected_goal_version), actual_version)

        old_status = _clean_status(str(goal.get("status") or ""), GOAL_STATUSES, "goal")
        new_status = _clean_status(status, GOAL_STATUSES, "goal") if status is not None else old_status
        if new_status not in GOAL_TRANSITIONS[old_status]:
            raise InvalidGoalTransition(f"invalid_goal_transition: {old_status}->{new_status}")

        if title is not ...:
            goal["title"] = str(title or "").strip() or None
        if desired_state is not None:
            text = str(desired_state or "").strip()
            if not text:
                raise GoalStateError("desired_state_required")
            goal["desiredState"] = text
        if scope_refs is not ...:
            goal["scopeRefs"] = _clean_refs(scope_refs if scope_refs is not None else None)
        if evidence_ref:
            goal["evidenceRefs"] = _clean_refs([*goal.get("evidenceRefs", []), evidence_ref])

        criterion_change = None
        if criterion_id:
            criteria = goal.get("criteria")
            if not isinstance(criteria, list):
                raise GoalStateError("criteria_must_be_list")
            criterion = next((c for c in criteria if isinstance(c, dict) and c.get("id") == criterion_id), None)
            if criterion is None:
                raise GoalStateError("criterion_not_found")
            next_status = (
                _clean_status(criterion_status, CRITERION_STATUSES, "criterion")
                if criterion_status is not None
                else str(criterion.get("status") or "unknown")
            )
            refs = _clean_refs(criterion.get("evidenceRefs") if isinstance(criterion.get("evidenceRefs"), list) else None)
            if criterion_evidence_ref:
                refs = _clean_refs([*refs, criterion_evidence_ref])
            if next_status == "met" and not refs:
                raise GoalStateError("met_criterion_requires_evidence")
            criterion["status"] = next_status
            criterion["evidenceRefs"] = refs
            if criterion_note is not ...:
                criterion["note"] = str(criterion_note or "").strip() or None
            criterion_change = {
                "criterionId": criterion_id,
                "status": next_status,
                "evidenceRefs": copy.deepcopy(refs),
            }

        # Check achievement only after all same-request criterion changes are applied.
        if new_status == "achieved":
            _assert_achievable(goal)

        at = now_iso()
        goal["status"] = new_status
        if new_status == "achieved" and old_status != "achieved":
            goal["achievedAt"] = at
        elif new_status != "achieved":
            goal["achievedAt"] = None
        goal["updatedAt"] = at
        goal["version"] = actual_version + 1

        change_summary.update(
            {
                "goalRef": gid,
                "beforeStatus": old_status,
                "afterStatus": new_status,
                "goalVersion": goal["version"],
            }
        )
        if criterion_change:
            change_summary["criterion"] = criterion_change
        if evidence_ref:
            change_summary["evidenceRef"] = evidence_ref
        return copy.deepcopy(change_summary)

    result = store.commit(
        mutate,
        event_type="goal.updated",
        event_data={"goalRef": gid},
        expected_server_revision=expected_server_revision,
    )
    return copy.deepcopy(_find_goal(result.wrapper["state"], gid))
