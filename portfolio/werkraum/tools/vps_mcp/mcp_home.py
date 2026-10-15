from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


HOME_ROOT = Path(
    os.environ.get("FLEXTRAWURST_MCP_HOME_ROOT", "/root/werkraum/_gpt/mcp_zuhause")
)
PROTOCOL_PATH = Path(
    os.environ.get(
        "FLEXTRAWURST_MCP_HOME_PROTOCOL_PATH",
        "/root/werkraum/_gpt/mcp_global_protocols/mcp_zuhause_v1.json",
    )
)
MANIFEST_PATH = HOME_ROOT / "MANIFEST.json"


class MCPHomeError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MCPHomeError(f"MCP-Zuhause-Datei fehlt: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MCPHomeError(f"Ungültiges JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MCPHomeError(f"JSON-Wurzel muss ein Objekt sein: {path}")
    return value


def load_protocol() -> dict[str, Any]:
    protocol = _read_json(PROTOCOL_PATH)
    protocol["protocol_path"] = str(PROTOCOL_PATH)
    protocol["protocol_sha256"] = _sha256(PROTOCOL_PATH)
    return protocol


def load_manifest() -> dict[str, Any]:
    manifest = _read_json(MANIFEST_PATH)
    manifest["manifest_path"] = str(MANIFEST_PATH)
    manifest["manifest_sha256"] = _sha256(MANIFEST_PATH)
    return manifest


def read_section(section: str) -> dict[str, Any]:
    manifest = load_manifest()
    sections = manifest.get("sections") or {}
    if section not in sections:
        raise MCPHomeError(
            f"Unbekannter MCP-Zuhause-Abschnitt: {section}; "
            f"erlaubt={sorted(sections)}"
        )
    path = Path(str(sections[section]))
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise MCPHomeError(f"MCP-Zuhause-Abschnitt fehlt: {path}") from exc
    return {
        "section": section,
        "path": str(path),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "content": content,
    }


def home_snapshot(
    *,
    section: str = "summary",
    active_operations: list[dict[str, Any]] | None = None,
    shared_read_tools: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict[str, Any]:
    protocol = load_protocol()
    manifest = load_manifest()
    sections = manifest.get("sections") or {}
    active = list(active_operations or [])
    shared = sorted(shared_read_tools or [])

    result: dict[str, Any] = {
        "ok": True,
        "home_id": protocol.get("home_id"),
        "protocol_id": protocol.get("protocol_id"),
        "protocol_version": protocol.get("protocol_version"),
        "status": protocol.get("status"),
        "purpose": protocol.get("purpose"),
        "identity_boundary": protocol.get("identity_boundary"),
        "home_root": str(HOME_ROOT),
        "start_here": sections.get("start"),
        "map": sections.get("map"),
        "work_contract": sections.get("work"),
        "patterns": sections.get("patterns"),
        "questions": sections.get("questions"),
        "handoff": sections.get("handoff"),
        "manifest_path": manifest.get("manifest_path"),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "protocol_path": protocol.get("protocol_path"),
        "protocol_sha256": protocol.get("protocol_sha256"),
        "startup_sequence": protocol.get("startup_sequence", []),
        "concurrency": {
            "contract": protocol.get("concurrency_contract", {}),
            "shared_read_tool_count": len(shared),
            "active_operation_count": len(active),
            "active_operations": active,
        },
        "einschraenkung": protocol.get("einschraenkung", []),
    }

    if section == "summary":
        return result
    if section == "all":
        result["documents"] = {
            name: read_section(name) for name in sorted(sections)
        }
        return result

    result["document"] = read_section(section)
    return result
