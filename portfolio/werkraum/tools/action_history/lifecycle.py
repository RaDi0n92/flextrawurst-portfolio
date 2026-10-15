from __future__ import annotations

import contextlib
import datetime as dt
import fcntl
import hashlib
import os
import uuid
from collections.abc import Iterator
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from .file_work import ensure_file_work_constitution
from .history import ActionHistory, acquire_flock
from .startklarheit import startup_view
from .session_continuity import (
    SessionContinuityError,
    continuity_marker,
    load_session_continuity_protocol,
    normalize_session_intent,
    require_new_session_reason,
)
from .time_stream import ensure_temporal_trace
from .ui_visible import ensure_ui_visible_session

_HELD_LOCKS: ContextVar[frozenset[str]] = ContextVar(
    "action_history_held_locks",
    default=frozenset(),
)


class SessionClosedError(RuntimeError):
    pass


def _lock_path(history: ActionHistory, session_id: str | None = None) -> Path:
    if session_id is None:
        return Path(f"{history.path}.lifecycle.lock")
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    return Path(f"{history.path}.session-{digest}.lock")


@contextlib.contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    key = str(path)
    held = _HELD_LOCKS.get()
    if key in held:
        yield
        return

    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("a+", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        acquire_flock(handle, f"lifecycle:{path.name}", fcntl.LOCK_EX)
        token = _HELD_LOCKS.set(held | {key})
        try:
            yield
        finally:
            _HELD_LOCKS.reset(token)
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def _lifecycle_lock(history: ActionHistory) -> Iterator[None]:
    with _file_lock(_lock_path(history)):
        yield


@contextlib.contextmanager
def _session_lock(history: ActionHistory, session_id: str) -> Iterator[None]:
    with _file_lock(_lock_path(history, session_id)):
        yield


def generate_session_id(prefix: str = "chatgpt") -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{timestamp}-{uuid.uuid4().hex[:12]}"


def _actor_session_prefix(actor: str) -> str:
    """2026-07-31 gefunden: generate_session_id() hatte 'chatgpt' hartkodiert als
    Default-Praefix -- betraf automatisch generierte IDs fuer ALLE Stroeme (Claude Code,
    Codex, Gemini, Claude Web), nicht nur ChatGPT selbst. Sogar ChatGPTs eigener Dienst
    setzt FLEXTRAWURST_ACTION_ACTOR gar nicht explizit (Code-Default dort ist
    'GPT-5.6-sol-hoch', nicht 'chatgpt') -- der alte Default war also nie an einen
    echten Strom gebunden, reiner Zufallswert aus der fruehen Bauphase. Rein kosmetisch
    (das actor-Feld war die ganze Zeit korrekt und ist die einzige echte Routing-
    Grundlage), aber irrefuehrend beim Lesen. Fix: den tatsaechlichen actor-Namen der
    aufrufenden ActionHistory als Praefix verwenden, keine neue Konstante."""
    slug = "".join(c if c.isalnum() else "-" for c in actor.lower())
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "session"


def _require_real_session_id(session_id: str | None) -> str:
    if not session_id or session_id == "unknown-session":
        raise ValueError("Eine echte session_id ist erforderlich")
    return session_id


def _session_is_closed(history: ActionHistory, session_id: str) -> bool:
    return bool(history.list_events(session_id=session_id, action="session.end", limit=1))


def _session_exists(history: ActionHistory, session_id: str) -> bool:
    return bool(history.list_events(session_id=session_id, action="session.begin", limit=1))


def _real_session_ids(history: ActionHistory) -> list[str]:
    sessions: list[str] = []
    for event in history.list_events(limit=5000):
        if event.get("action") != "session.begin":
            continue
        session_id = str(event.get("session_id") or "")
        if session_id and session_id not in sessions:
            sessions.append(session_id)
    return sessions


def _previous_real_session_id(history: ActionHistory, current_session_id: str) -> str | None:
    candidates = [
        session_id
        for session_id in _real_session_ids(history)
        if session_id != current_session_id
    ]
    return candidates[-1] if candidates else None


def _record_closed_attempt(
    history: ActionHistory,
    session_id: str,
    *,
    action: str,
    target: str | None,
) -> None:
    history.append(
        action="session.closed_action_blocked",
        target=session_id,
        status="blocked",
        session_id="system-audit",
        completeness="aborted",
        details={
            "attempted_action": action,
            "attempted_target": target,
            "closed_session_id": session_id,
        },
    )


@contextlib.contextmanager
def session_action(
    history: ActionHistory,
    session_id: str,
    *,
    action: str,
    target: str | None = None,
) -> Iterator[str]:
    """Verhindert Rennen zwischen laufender Arbeit und Sessionabschluss."""
    active_session_id = _require_real_session_id(session_id)
    with _session_lock(history, active_session_id):
        if _session_is_closed(history, active_session_id):
            _record_closed_attempt(
                history,
                active_session_id,
                action=action,
                target=target,
            )
            raise SessionClosedError(
                f"Session ist bereits geschlossen: {active_session_id}"
            )
        yield active_session_id


def begin_session_once(
    history: ActionHistory,
    session_id: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_session_id = _require_real_session_id(session_id)
    with _lifecycle_lock(history), _session_lock(history, active_session_id):
        return history.begin_session(active_session_id, details=details)


def end_session_once(
    history: ActionHistory,
    session_id: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_session_id = _require_real_session_id(session_id)
    with _lifecycle_lock(history), _session_lock(history, active_session_id):
        return history.end_session(active_session_id, details=details)


def _startup_context(
    history: ActionHistory,
    session_id: str,
    recent_limit: int,
) -> dict[str, Any]:
    current = history.list_events(session_id=session_id, limit=recent_limit)
    previous_session_id = _previous_real_session_id(history, session_id)
    previous = (
        history.list_events(session_id=previous_session_id, limit=recent_limit)
        if previous_session_id
        else []
    )
    global_recent = history.list_events(limit=recent_limit)
    relevant = previous + current + [
        event
        for event in global_recent
        if event.get("session_id") in {"system-audit", "unassigned"}
    ]
    return {
        "actor": history.actor,
        "history_path": str(history.path),
        "checkpoint_path": str(history.checkpoint_path),
        "session_id": session_id,
        "current_session_actions": current,
        "previous_session_id": previous_session_id,
        "previous_session_actions": previous,
        "global_recent_actions": global_recent,
        "failed_or_blocked": [
            event for event in relevant if event.get("status") != "success"
        ],
        "partial_or_unknown": [
            event
            for event in relevant
            if event.get("completeness") in {"partial", "unknown", "aborted"}
        ],
        "integrity": history.verify(),
    }


def startup_session(
    history: ActionHistory,
    *,
    session_id: str | None = None,
    recent_limit: int = 30,
    details: dict[str, Any] | None = None,
    session_intent: str = "resume",
    new_session_reason: str | None = None,
    supersedes_session_id: str | None = None,
) -> dict[str, Any]:
    startklarheit = startup_view()
    protocol = load_session_continuity_protocol()
    intent = normalize_session_intent(session_intent)
    requested_session_id = (
        None if not session_id or session_id == "unknown-session" else str(session_id)
    )
    supersedes = (
        None
        if not supersedes_session_id or supersedes_session_id == "unknown-session"
        else str(supersedes_session_id)
    )
    generated = False
    replaced_closed_session_id: str | None = None
    reason: str | None = None

    with _lifecycle_lock(history):
        if intent == "resume":
            if not requested_session_id:
                raise SessionContinuityError(
                    "Fortsetzung ist Standard, benötigt aber die kanonische session_id "
                    "dieses UI- oder Arbeitsfadens. Für eine wirklich neue Arbeitslinie "
                    "session_intent='new' und new_session_reason angeben."
                )
            if not _session_exists(history, requested_session_id):
                raise SessionContinuityError(
                    f"Unbekannte Session kann nicht fortgesetzt werden: {requested_session_id}. "
                    "Der Server wählt nicht ersatzweise eine andere oder die global letzte Session."
                )
            if _session_is_closed(history, requested_session_id):
                raise SessionClosedError(
                    f"Geschlossene Session wird nicht still ersetzt: {requested_session_id}. "
                    "Für eine neue Arbeitslinie session_intent='new', new_session_reason und "
                    "supersedes_session_id angeben."
                )
            resolved_session_id = requested_session_id
            decision = "resumed_existing"
            session_begin = begin_session_once(
                history,
                resolved_session_id,
                details={"source": "history_startup", "continuity_decision": decision},
            )
            continuity_event = history.append(
                action="session.resume",
                target=resolved_session_id,
                status="success",
                session_id=resolved_session_id,
                completeness="complete",
                details={
                    "source": "history_startup",
                    "session_intent": intent,
                    "canonical_session_id": resolved_session_id,
                    **(details or {}),
                },
            )
        else:
            reason = require_new_session_reason(new_session_reason)
            if supersedes and not _session_exists(history, supersedes):
                raise SessionContinuityError(
                    f"supersedes_session_id ist unbekannt: {supersedes}"
                )
            if requested_session_id and _session_exists(history, requested_session_id):
                if _session_is_closed(history, requested_session_id):
                    supersedes = supersedes or requested_session_id
                    replaced_closed_session_id = requested_session_id
                    resolved_session_id = generate_session_id(_actor_session_prefix(history.actor))
                    generated = True
                else:
                    raise SessionContinuityError(
                        f"Session existiert bereits und ist offen: {requested_session_id}. "
                        "Sie muss mit session_intent='resume' fortgesetzt werden."
                    )
            else:
                resolved_session_id = requested_session_id or generate_session_id(_actor_session_prefix(history.actor))
                generated = requested_session_id is None
            decision = "created_new"
            session_begin = begin_session_once(
                history,
                resolved_session_id,
                details={
                    "source": "history_startup",
                    "continuity_decision": decision,
                    "generated_session_id": generated,
                    "requested_session_id": requested_session_id,
                    "new_session_reason": reason,
                    "supersedes_session_id": supersedes,
                    "replaced_closed_session_id": replaced_closed_session_id,
                    **(details or {}),
                },
            )
            continuity_event = history.append(
                action="session.continuity_new",
                target=resolved_session_id,
                status="success",
                session_id=resolved_session_id,
                completeness="complete",
                details={
                    "source": "history_startup",
                    "session_intent": intent,
                    "canonical_session_id": resolved_session_id,
                    "new_session_reason": reason,
                    "supersedes_session_id": supersedes,
                    **(details or {}),
                },
            )

    marker = continuity_marker(
        decision=decision,
        session_id=resolved_session_id,
        reason=reason,
        supersedes_session_id=supersedes,
    )
    ui_visible = ensure_ui_visible_session(history, resolved_session_id)
    temporal_trace = ensure_temporal_trace(history)
    file_work_constitution = ensure_file_work_constitution()
    context = _startup_context(history, resolved_session_id, recent_limit)
    continuity = {
        "protocol": protocol,
        "decision": decision,
        "intent": intent,
        "marker": marker,
        "canonical_session_id": resolved_session_id,
        "requested_session_id": requested_session_id,
        "generated_session_id": generated,
        "new_session_reason": reason,
        "supersedes_session_id": supersedes,
        "replaced_closed_session_id": replaced_closed_session_id,
        "continuity_event_id": continuity_event.get("event_id"),
        "truth_boundary": (
            "Jeder UI- oder Arbeitsfaden behält seine eigene kanonische Session. "
            "Der Server hat keine globale Fremdsession als Ersatz gewählt."
        ),
    }
    return {
        "startklarheit": startklarheit,
        "session_begin": session_begin,
        "session_continuity_event": continuity_event,
        "generated_session_id": generated,
        "replaced_closed_session_id": replaced_closed_session_id,
        "global_session_continuity": continuity,
        "session_continuity_marker": marker,
        "global_ui_visible_protocol": ui_visible,
        "startup_temporal_trace": temporal_trace,
        "global_file_work_constitution": file_work_constitution,
        **context,
    }
