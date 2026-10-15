#!/usr/bin/env python3
"""HTTP skin for durable gkos.goal.v0 contracts.

These endpoints only persist/read explicit Goal contracts and evidence-bound
criterion updates. They never ask an LLM whether a Goal is achieved and never
infer Goal success from a completed Run.
"""
from __future__ import annotations

import json
from typing import Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from goal_state import (
    GoalNotFound,
    GoalStateError,
    GoalVersionConflict,
    InvalidGoalTransition,
    create_goal,
    read_goal,
    read_goals,
    update_goal,
)
from planner_api import MAX_BODY_BYTES, _require_staff, _same_origin
from world_state import DEFAULT_STORE, RevisionConflict, WorldStateError


STORE = DEFAULT_STORE


def _body(request) -> dict[str, Any]:
    if len(request.body) > MAX_BODY_BYTES:
        raise ValueError("body_too_large")
    value = json.loads(request.body.decode("utf-8") or "{}")
    if not isinstance(value, dict):
        raise ValueError("invalid_json")
    return value


def _server_revision() -> int:
    return int(STORE.read_wrapper().get("serverRevision") or 0)


def _error_response(exc: Exception) -> JsonResponse:
    if isinstance(exc, GoalNotFound):
        return JsonResponse({"ok": False, "error": "goal_not_found"}, status=404)
    if isinstance(exc, GoalVersionConflict):
        return JsonResponse(
            {
                "ok": False,
                "error": "goal_version_conflict",
                "goalId": exc.goal_id,
                "expectedGoalVersion": exc.expected,
                "actualGoalVersion": exc.actual,
            },
            status=409,
        )
    if isinstance(exc, RevisionConflict):
        return JsonResponse(
            {
                "ok": False,
                "error": "server_revision_conflict",
                "expectedServerRevision": exc.expected,
                "actualServerRevision": exc.actual,
            },
            status=409,
        )
    if isinstance(exc, InvalidGoalTransition):
        return JsonResponse({"ok": False, "error": str(exc)}, status=409)
    if isinstance(exc, (GoalStateError, WorldStateError, ValueError)):
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return JsonResponse({"ok": False, "error": f"goal_api_failed: {exc}"}, status=500)


@csrf_exempt
def goal_list_create(request):
    denied = _require_staff(request)
    if denied:
        return denied

    if request.method == "GET":
        try:
            goal_id = str(request.GET.get("id") or "").strip()
            if goal_id:
                goal = read_goal(goal_id, store=STORE)
                return JsonResponse(
                    {"ok": True, "serverRevision": _server_revision(), "goal": goal},
                    json_dumps_params={"ensure_ascii": False},
                )
            goals = read_goals(store=STORE)
            status = str(request.GET.get("status") or "").strip()
            construct_ref = str(request.GET.get("constructRef") or "").strip()
            if status:
                goals = [goal for goal in goals if goal.get("status") == status]
            if construct_ref:
                goals = [goal for goal in goals if goal.get("constructRef") == construct_ref]
            return JsonResponse(
                {"ok": True, "serverRevision": _server_revision(), "goals": goals},
                json_dumps_params={"ensure_ascii": False},
            )
        except Exception as exc:
            return _error_response(exc)

    if request.method != "POST" or not _same_origin(request):
        return JsonResponse(
            {"ok": False, "error": "method_or_origin_not_allowed"}, status=405
        )

    try:
        body = _body(request)
        goal = create_goal(
            construct_ref=str(body.get("constructRef") or ""),
            desired_state=str(body.get("desiredState") or ""),
            title=body.get("title"),
            scope_refs=body.get("scopeRefs") if isinstance(body.get("scopeRefs"), list) else None,
            criteria=body.get("criteria") if isinstance(body.get("criteria"), list) else None,
            status=str(body.get("status") or "active"),
            goal_id=str(body.get("goalId") or "").strip() or None,
            store=STORE,
            expected_server_revision=(
                int(body["expectedServerRevision"])
                if body.get("expectedServerRevision") is not None
                else None
            ),
        )
        return JsonResponse(
            {"ok": True, "serverRevision": _server_revision(), "goal": goal},
            status=201,
            json_dumps_params={"ensure_ascii": False},
        )
    except Exception as exc:
        return _error_response(exc)


@csrf_exempt
def goal_update(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse(
            {"ok": False, "error": "method_or_origin_not_allowed"}, status=405
        )

    try:
        body = _body(request)
        goal_id = str(body.get("goalId") or "").strip()
        if not goal_id:
            raise ValueError("goal_id_required")

        kwargs: dict[str, Any] = {
            "status": body.get("status"),
            "desired_state": body.get("desiredState"),
            "evidence_ref": str(body.get("evidenceRef") or "").strip() or None,
            "criterion_id": str(body.get("criterionId") or "").strip() or None,
            "criterion_status": body.get("criterionStatus"),
            "criterion_evidence_ref": str(body.get("criterionEvidenceRef") or "").strip() or None,
            "expected_goal_version": (
                int(body["expectedGoalVersion"])
                if body.get("expectedGoalVersion") is not None
                else None
            ),
            "expected_server_revision": (
                int(body["expectedServerRevision"])
                if body.get("expectedServerRevision") is not None
                else None
            ),
            "store": STORE,
        }
        # Missing means unchanged. Explicit null can clear title/scope/note.
        if "title" in body:
            kwargs["title"] = body.get("title")
        if "scopeRefs" in body:
            kwargs["scope_refs"] = body.get("scopeRefs") if isinstance(body.get("scopeRefs"), list) else None
        if "criterionNote" in body:
            kwargs["criterion_note"] = body.get("criterionNote")

        goal = update_goal(goal_id, **kwargs)
        return JsonResponse(
            {"ok": True, "serverRevision": _server_revision(), "goal": goal},
            json_dumps_params={"ensure_ascii": False},
        )
    except Exception as exc:
        return _error_response(exc)
