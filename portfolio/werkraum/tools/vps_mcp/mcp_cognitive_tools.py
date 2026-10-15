from __future__ import annotations

from typing import Any

from mcp_cognitive_graph import (
    CognitiveGraphError,
    add_edge,
    add_node,
    next_moves,
    resolve_node,
    snapshot,
    wander,
)


def _result(ok: bool, data: Any = None, error: str | None = None) -> dict:
    return {
        "ok": ok,
        "data": data,
        "source_refs": [],
        "warnings": [],
        "truncated": False,
        "next_cursor": None,
        "error": error,
    }


def tool_note(args: dict) -> dict:
    try:
        node = add_node(
            node_type=str(args.get("node_type") or ""),
            text=str(args.get("text") or ""),
            source_refs=args.get("source_refs") or [],
            confidence=str(args.get("confidence") or "unknown"),
            status=str(args.get("status") or "open"),
            session_id=args.get("session_id"),
            metadata=args.get("metadata") if isinstance(args.get("metadata"), dict) else {},
        )
        return _result(True, node)
    except CognitiveGraphError as exc:
        return _result(False, error=str(exc))
    except Exception as exc:
        return _result(False, error=f"Kognitiver Graphfehler: {exc}")


def tool_link(args: dict) -> dict:
    try:
        edge = add_edge(
            from_id=str(args.get("from_id") or ""),
            to_id=str(args.get("to_id") or ""),
            edge_type=str(args.get("edge_type") or ""),
            reason=str(args.get("reason") or ""),
            session_id=args.get("session_id"),
        )
        return _result(True, edge)
    except CognitiveGraphError as exc:
        return _result(False, error=str(exc))
    except Exception as exc:
        return _result(False, error=f"Kognitiver Graphfehler: {exc}")


def tool_resolve(args: dict) -> dict:
    try:
        node = resolve_node(
            node_id=str(args.get("node_id") or ""),
            status=str(args.get("status") or "resolved"),
            session_id=args.get("session_id"),
        )
        return _result(True, node)
    except CognitiveGraphError as exc:
        return _result(False, error=str(exc))
    except Exception as exc:
        return _result(False, error=f"Kognitiver Graphfehler: {exc}")


def tool_next(args: dict) -> dict:
    try:
        return _result(
            True,
            {"moves": next_moves(args.get("session_id"), int(args.get("limit", 5)))},
        )
    except Exception as exc:
        return _result(False, error=f"Kognitiver Graphfehler: {exc}")


def tool_wander(args: dict) -> dict:
    try:
        trail = args.get("trail") or []
        if not isinstance(trail, list):
            return _result(False, error="trail muss eine Liste von bereits bereisten Pfaden sein")
        data = wander(
            seed=str(args.get("seed") or ""),
            trail=[str(item) for item in trail],
            limit=int(args.get("limit", 6)),
            session_id=args.get("session_id"),
        )
        return _result(True, data)
    except CognitiveGraphError as exc:
        return _result(False, error=str(exc))
    except Exception as exc:
        return _result(False, error=f"Wander-RAG-Fehler: {exc}")


def tool_snapshot(args: dict) -> dict:
    try:
        return _result(True, snapshot(args.get("session_id")))
    except Exception as exc:
        return _result(False, error=f"Kognitiver Graphfehler: {exc}")
