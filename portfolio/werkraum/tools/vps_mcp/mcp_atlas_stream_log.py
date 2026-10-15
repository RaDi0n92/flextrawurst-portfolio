from __future__ import annotations

import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(
    os.environ.get(
        "FLEXTRAWURST_ATLAS_STREAM_LOG_ROOT",
        "/root/werkraum_gesamtatlas_eingang/AI_UEBERGABEN/STROM_MITSCHRIFTEN",
    )
)

STREAM_IDS = ("claude", "claudeweb", "chatgpt", "codex", "gemini", "kimi", "glm")
STREAM_ALIASES = {
    "claude": "claude",
    "claudecode": "claude",
    "claude-code": "claude",
    "claude_code": "claude",
    "claudeweb": "claudeweb",
    "claude-web": "claudeweb",
    "claude_web": "claudeweb",
    "chatgpt": "chatgpt",
    "gpt": "chatgpt",
    "codex": "codex",
    "gemini": "gemini",
    "kimi": "kimi",
    "glm": "glm",
}
MAX_CONTENT_BYTES = max(
    4096,
    int(os.environ.get("FLEXTRAWURST_ATLAS_STREAM_MAX_CONTENT_BYTES", str(2 * 1024 * 1024))),
)


class StreamLogError(RuntimeError):
    pass


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _safe_text(value: Any, *, maximum: int = 512) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text[:maximum]


def _normalise_string_list(value: Any, *, maximum_items: int = 64) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        raise StreamLogError("Listenfeld muss Text oder eine Liste aus Texten sein")
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        text = _safe_text(item, maximum=4096)
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= maximum_items:
            break
    return result


def canonical_stream_id(stream_id: str) -> str:
    raw = re.sub(r"\s+", "", str(stream_id or "").strip().lower())
    canonical = STREAM_ALIASES.get(raw)
    if canonical is None:
        raise StreamLogError(
            "Unbekannter AI-Strom. Erlaubt sind Claude Code, Claude Web, ChatGPT, "
            "Codex, Gemini, Kimi und GLM."
        )
    return canonical


def _connections_path() -> Path:
    return ROOT / "VERBINDUNGEN.jsonl"


def _status_path() -> Path:
    return ROOT / "STATUS.json"


def _lock_path() -> Path:
    return ROOT / ".mitschrift.lock"


def _stream_root(stream_id: str) -> Path:
    return ROOT / stream_id


def _stream_log_path(stream_id: str) -> Path:
    return _stream_root(stream_id) / "MITSCHRIFTEN.jsonl"


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _atomic_write_json(path: Path, value: Any) -> None:
    _atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _append_jsonl_unlocked(path: Path, value: dict[str, Any]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
    with path.open("r", encoding="utf-8", errors="strict") as read_handle:
        line_number = sum(1 for _ in read_handle)
    reread = path.read_text(encoding="utf-8", errors="strict").splitlines()[-1]
    parsed = json.loads(reread)
    if parsed.get("event_hash") != value.get("event_hash"):
        raise StreamLogError("Rückleseprüfung der Mitschrift ist fehlgeschlagen")
    return line_number, _sha256_text(reread)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    result: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StreamLogError(f"Ungültiges JSONL in {path}:{line_number}: {exc}") from exc
            if isinstance(value, dict):
                result.append(value)
    return result


@contextlib.contextmanager
def _locked() -> Iterator[None]:
    ROOT.mkdir(parents=True, exist_ok=True)
    with _lock_path().open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _layout_text() -> str:
    return """# Gemeinsamer Gesamtatlas-Mitschreibanschluss

Dieser Eingang gehört Daniels vorhandenen AI-Strömen: Claude Code, Claude Web, ChatGPT, Codex, Gemini, Kimi und GLM.

Jeder Strom behält seine eigene Herkunft und seine eigene append-only Mitschrift. Eine Verbindung verschmilzt keine Erinnerungen und erklärt keine Aussage automatisch für wahr. Nach erfolgreicher Verbindung werden nachfolgende MCP-Aktionen dieser Sitzung automatisch an die Stromspur gebunden. Vollständige Gedanken, Antworten, Entscheidungen und Übergaben können zusätzlich über `atlas.stream_write` hinterlassen werden.

Alle Mitschriften sind beim nächsten Gesamtatlas-Vollrefresh als Primärquellen volltextsuchbar. Schon vorher können sie direkt über `atlas.stream_search` durchsucht werden.
"""


def _ensure_layout_unlocked() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    start = ROOT / "START_HIER.md"
    if not start.exists():
        _atomic_write(start, _layout_text().encode("utf-8"))
    for stream_id in STREAM_IDS:
        stream_root = _stream_root(stream_id)
        stream_root.mkdir(parents=True, exist_ok=True)
        readme = stream_root / "START_HIER.md"
        if not readme.exists():
            _atomic_write(
                readme,
                (
                    f"# Mitschrift: {stream_id}\n\n"
                    "Dieser Ordner enthält die append-only Herkunftsspur dieses AI-Stroms. "
                    "Die kanonischen Einträge liegen in `MITSCHRIFTEN.jsonl`.\n"
                ).encode("utf-8"),
            )


def _latest_connections_unlocked() -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for record in _read_jsonl(_connections_path()):
        session_id = str(record.get("session_id") or "")
        if session_id:
            latest[session_id] = record
    return latest


def _last_event_hash(path: Path) -> str | None:
    records = _read_jsonl(path)
    if not records:
        return None
    return _safe_text(records[-1].get("event_hash"), maximum=128)


def _event_hash(record_without_hash: dict[str, Any]) -> str:
    return _sha256_bytes(_canonical_json(record_without_hash))


def _write_status_unlocked() -> dict[str, Any]:
    connections = _read_jsonl(_connections_path())
    streams: dict[str, Any] = {}
    total_events = 0
    for stream_id in STREAM_IDS:
        records = _read_jsonl(_stream_log_path(stream_id))
        total_events += len(records)
        streams[stream_id] = {
            "event_count": len(records),
            "latest_event_id": records[-1].get("event_id") if records else None,
            "latest_timestamp_utc": records[-1].get("timestamp_utc") if records else None,
            "log_path": str(_stream_log_path(stream_id)),
            "log_sha256": _sha256_bytes(_stream_log_path(stream_id).read_bytes()) if _stream_log_path(stream_id).is_file() else None,
        }
    latest_connections = _latest_connections_unlocked()
    status = {
        "schema_version": "1.0",
        "generated_utc": _utc_now(),
        "ok": True,
        "root": str(ROOT),
        "entry_path": str(ROOT / "START_HIER.md"),
        "connection_count": len(connections),
        "active_session_connection_count": len(latest_connections),
        "event_count": total_events,
        "streams": streams,
        "einschraenkung": (
            "Die Mitschrift beweist, welcher verbundene Strom welchen Inhalt oder welche MCP-Aktion "
            "unter welcher Session hinterlassen hat. Sie beweist nicht automatisch Wahrheit, Konsens, "
            "wortgetreue UI-Vollständigkeit oder gemeinsame Erinnerung."
        ),
    }
    _atomic_write_json(_status_path(), status)
    return status


def _find_idempotent_unlocked(stream_id: str, session_id: str, idempotency_key: str) -> dict[str, Any] | None:
    for record in reversed(_read_jsonl(_stream_log_path(stream_id))):
        if record.get("session_id") == session_id and record.get("idempotency_key") == idempotency_key:
            return record
    return None


def connect_stream(
    *,
    stream_id: str,
    session_id: str,
    client_label: str | None = None,
    source_surface: str | None = None,
) -> dict[str, Any]:
    canonical = canonical_stream_id(stream_id)
    session = _safe_text(session_id, maximum=512)
    if not session:
        raise StreamLogError("Eine reale History-session_id ist für die Stromverbindung erforderlich")
    with _locked():
        _ensure_layout_unlocked()
        latest = _latest_connections_unlocked()
        existing = latest.get(session)
        if existing:
            if existing.get("stream_id") != canonical:
                raise StreamLogError(
                    f"Diese Session ist bereits mit {existing.get('stream_id')} verbunden und darf nicht still umetikettiert werden"
                )
            status = _write_status_unlocked()
            return {
                "ok": True,
                "connected": True,
                "duplicate": True,
                "connection": existing,
                "status": status,
                "search_tools": ["atlas.find", "atlas.where_is", "atlas.relationships", "atlas.provenance", "atlas.stream_search"],
                "write_tool": "atlas.stream_write",
            }
        previous_hash = _last_event_hash(_connections_path())
        record: dict[str, Any] = {
            "schema_version": "1.0",
            "event_type": "stream_connected",
            "timestamp_utc": _utc_now(),
            "stream_id": canonical,
            "session_id": session,
            "client_label": _safe_text(client_label, maximum=512),
            "source_surface": _safe_text(source_surface, maximum=512),
            "previous_hash": previous_hash,
            "identity_status": "DECLARED_BY_CALLER_AND_BOUND_TO_HISTORY_SESSION",
        }
        record["event_id"] = _sha256_bytes(
            _canonical_json({"stream_id": canonical, "session_id": session, "timestamp_utc": record["timestamp_utc"]})
        )[:24]
        record["event_hash"] = _event_hash(record)
        line_number, line_sha256 = _append_jsonl_unlocked(_connections_path(), record)
        status = _write_status_unlocked()
        return {
            "ok": True,
            "connected": True,
            "duplicate": False,
            "connection": record,
            "connection_log_path": str(_connections_path()),
            "connection_line": line_number,
            "connection_line_sha256": line_sha256,
            "status": status,
            "entry_path": str(ROOT / "START_HIER.md"),
            "search_tools": ["atlas.find", "atlas.where_is", "atlas.relationships", "atlas.provenance", "atlas.stream_search"],
            "write_tool": "atlas.stream_write",
            "message": (
                f"{canonical} ist mit dieser History-Session verbunden. Nachfolgende MCP-Aktionen werden automatisch "
                "an die Stromspur gebunden; vollständige Texte und Entscheidungen können über atlas.stream_write eingehen."
            ),
        }


def connection_for_session(session_id: str) -> dict[str, Any] | None:
    session = _safe_text(session_id, maximum=512)
    if not session:
        return None
    with _locked():
        _ensure_layout_unlocked()
        return _latest_connections_unlocked().get(session)


def append_entry(
    *,
    session_id: str,
    content: str,
    stream_id: str | None = None,
    kind: str = "note",
    role: str | None = None,
    title: str | None = None,
    source_refs: Any = None,
    project_paths: Any = None,
    external_session_id: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    session = _safe_text(session_id, maximum=512)
    if not session:
        raise StreamLogError("Eine reale History-session_id ist für die Mitschrift erforderlich")
    text = str(content or "")
    if not text.strip():
        raise StreamLogError("content darf nicht leer sein")
    content_bytes = text.encode("utf-8")
    if len(content_bytes) > MAX_CONTENT_BYTES:
        raise StreamLogError(f"content überschreitet das Limit von {MAX_CONTENT_BYTES} Bytes")
    safe_kind = _safe_text(kind, maximum=128) or "note"
    safe_idempotency = _safe_text(idempotency_key, maximum=512)
    with _locked():
        _ensure_layout_unlocked()
        connection = _latest_connections_unlocked().get(session)
        if stream_id is None:
            if not connection:
                raise StreamLogError("Session ist noch mit keinem AI-Strom verbunden")
            canonical = str(connection["stream_id"])
        else:
            canonical = canonical_stream_id(stream_id)
            if connection and connection.get("stream_id") != canonical:
                raise StreamLogError(
                    f"Session ist mit {connection.get('stream_id')} verbunden, nicht mit {canonical}"
                )
            if not connection:
                raise StreamLogError("Zuerst atlas.stream_connect oder history_startup mit ai_stream_id verwenden")
        if safe_idempotency:
            duplicate = _find_idempotent_unlocked(canonical, session, safe_idempotency)
            if duplicate:
                return {
                    "ok": True,
                    "written": False,
                    "duplicate": True,
                    "record": duplicate,
                    "log_path": str(_stream_log_path(canonical)),
                }
        log_path = _stream_log_path(canonical)
        previous_hash = _last_event_hash(log_path)
        timestamp = _utc_now()
        record: dict[str, Any] = {
            "schema_version": "1.0",
            "event_type": "stream_mitschrift",
            "timestamp_utc": timestamp,
            "stream_id": canonical,
            "session_id": session,
            "external_session_id": _safe_text(external_session_id, maximum=1024),
            "kind": safe_kind,
            "role": _safe_text(role, maximum=128),
            "title": _safe_text(title, maximum=2048),
            "content": text,
            "content_sha256": _sha256_bytes(content_bytes),
            "source_refs": _normalise_string_list(source_refs),
            "project_paths": _normalise_string_list(project_paths),
            "idempotency_key": safe_idempotency,
            "previous_stream_hash": previous_hash,
            "datenstand": "DECLARED_BY_CONNECTED_STREAM",
        }
        record["event_id"] = _sha256_bytes(
            _canonical_json(
                {
                    "stream_id": canonical,
                    "session_id": session,
                    "timestamp_utc": timestamp,
                    "content_sha256": record["content_sha256"],
                    "idempotency_key": safe_idempotency,
                }
            )
        )[:24]
        record["event_hash"] = _event_hash(record)
        line_number, line_sha256 = _append_jsonl_unlocked(log_path, record)
        status = _write_status_unlocked()
        return {
            "ok": True,
            "written": True,
            "duplicate": False,
            "record": record,
            "log_path": str(log_path),
            "line": line_number,
            "line_sha256": line_sha256,
            "write_verified": True,
            "status": status,
            "atlas_full_refresh_required_for_global_fts": True,
        }


def record_tool_event(
    *,
    session_id: str,
    tool_name: str,
    history_event: dict[str, Any],
    target: str | None,
    status: str,
    completeness: str,
) -> dict[str, Any] | None:
    connection = connection_for_session(session_id)
    if not connection:
        return None
    if tool_name.startswith("atlas.stream_") or tool_name in {"atlas.pulse"}:
        return None
    history_event_id = _safe_text(history_event.get("event_id"), maximum=512)
    history_event_hash = _safe_text(history_event.get("event_hash"), maximum=512)
    summary = f"{tool_name}"
    if target:
        summary += f" → {target}"
    summary += f" [{status}/{completeness}]"
    return append_entry(
        session_id=session_id,
        stream_id=str(connection["stream_id"]),
        content=summary,
        kind="mcp_tool_action",
        title=tool_name,
        source_refs=[
            item
            for item in (
                f"history_event:{history_event_id}" if history_event_id else None,
                f"history_hash:{history_event_hash}" if history_event_hash else None,
            )
            if item
        ],
        idempotency_key=f"history-event:{history_event_id}" if history_event_id else None,
    )


def search_entries(
    *,
    query: str,
    stream_id: str | None = None,
    kind: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    needle = str(query or "").strip().casefold()
    if not needle:
        raise StreamLogError("query darf nicht leer sein")
    requested_streams = [canonical_stream_id(stream_id)] if stream_id else list(STREAM_IDS)
    safe_kind = _safe_text(kind, maximum=128)
    safe_limit = max(1, min(int(limit), 200))
    matches: list[dict[str, Any]] = []
    with _locked():
        _ensure_layout_unlocked()
        for current_stream in requested_streams:
            for record in reversed(_read_jsonl(_stream_log_path(current_stream))):
                if safe_kind and record.get("kind") != safe_kind:
                    continue
                haystack = "\n".join(
                    str(record.get(field) or "")
                    for field in ("title", "content", "kind", "role", "session_id", "external_session_id")
                ).casefold()
                if needle in haystack:
                    matches.append(record)
                    if len(matches) >= safe_limit:
                        break
            if len(matches) >= safe_limit:
                break
    matches.sort(key=lambda item: str(item.get("timestamp_utc") or ""), reverse=True)
    return {
        "ok": True,
        "query": query,
        "stream_id": canonical_stream_id(stream_id) if stream_id else None,
        "kind": safe_kind,
        "count": len(matches[:safe_limit]),
        "results": matches[:safe_limit],
        "searched_logs": [str(_stream_log_path(item)) for item in requested_streams],
    }


def stream_status(*, stream_id: str | None = None, session_id: str | None = None) -> dict[str, Any]:
    canonical = canonical_stream_id(stream_id) if stream_id else None
    with _locked():
        _ensure_layout_unlocked()
        status = _write_status_unlocked()
        connection = _latest_connections_unlocked().get(str(session_id)) if session_id else None
        if canonical:
            status = dict(status)
            status["streams"] = {canonical: status["streams"][canonical]}
        status["current_session_connection"] = connection
        status["search_tools"] = ["atlas.find", "atlas.where_is", "atlas.relationships", "atlas.provenance", "atlas.stream_search"]
        status["write_tool"] = "atlas.stream_write"
        return status


def startup_projection(*, session_id: str) -> dict[str, Any]:
    return stream_status(session_id=session_id)


def validate_chain(*, stream_id: str) -> dict[str, Any]:
    canonical = canonical_stream_id(stream_id)
    with _locked():
        _ensure_layout_unlocked()
        records = _read_jsonl(_stream_log_path(canonical))
        previous: str | None = None
        for index, record in enumerate(records, 1):
            if record.get("previous_stream_hash") != previous:
                raise StreamLogError(f"Hash-Kettenbruch in {canonical}, Zeile {index}")
            claimed = record.get("event_hash")
            body = dict(record)
            body.pop("event_hash", None)
            calculated = _event_hash(body)
            if claimed != calculated:
                raise StreamLogError(f"Event-Hash ungültig in {canonical}, Zeile {index}")
            previous = str(claimed)
        return {
            "ok": True,
            "stream_id": canonical,
            "event_count": len(records),
            "last_hash": previous,
            "log_path": str(_stream_log_path(canonical)),
        }
