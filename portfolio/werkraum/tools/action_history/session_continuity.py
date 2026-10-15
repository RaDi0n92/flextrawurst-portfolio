from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .startklarheit import DEFAULT_STARTKLARHEIT_PATH, load_technical_section


DEFAULT_PROTOCOL_PATH = DEFAULT_STARTKLARHEIT_PATH
ALLOWED_INTENTS = frozenset({"resume", "new"})


class SessionContinuityError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_session_continuity_protocol(
    path: str | Path | None = None,
) -> dict[str, Any]:
    try:
        return load_technical_section(
            "session_continuity",
            {
                "protocol_id",
                "protocol_version",
                "status",
                "default_intent",
                "allowed_intents",
                "hard_rules",
                "failure_policy",
            },
            path or DEFAULT_PROTOCOL_PATH,
        )
    except Exception as exc:
        if isinstance(exc, SessionContinuityError):
            raise
        raise SessionContinuityError(str(exc)) from exc


def normalize_session_intent(value: str | None) -> str:
    intent = str(value or "resume").strip().lower()
    if intent not in ALLOWED_INTENTS:
        raise SessionContinuityError(
            f"session_intent muss eines von {sorted(ALLOWED_INTENTS)} sein"
        )
    return intent


def require_new_session_reason(value: str | None) -> str:
    reason = " ".join(str(value or "").split())
    if len(reason) < 8:
        raise SessionContinuityError(
            "Eine neue Session verlangt einen konkreten new_session_reason "
            "mit mindestens 8 Zeichen"
        )
    if len(reason) > 1000:
        raise SessionContinuityError("new_session_reason ist zu lang")
    return reason


def continuity_marker(
    *,
    decision: str,
    session_id: str,
    reason: str | None = None,
    supersedes_session_id: str | None = None,
) -> str:
    if decision == "resumed_existing":
        return f"[SESSION-KONTINUITAET: FORTGESETZT {session_id}]"
    return (
        f"[SESSION-KONTINUITAET: NEU {session_id} | "
        f"GRUND={reason} | HERKUNFT={supersedes_session_id or 'keine'}]"
    )
