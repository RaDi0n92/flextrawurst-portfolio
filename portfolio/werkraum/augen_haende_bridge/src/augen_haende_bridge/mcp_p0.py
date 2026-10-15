"""Provider-neutral, read-only MCP-P0 transport probe.

This module is deliberately smaller than an MCP client library.  It performs
the five facts the bridge is allowed to claim at the first gate:

``configured -> reachable -> handshake_succeeded -> tools_list_received
-> atlas_read_verified``

The last step is opt-in and needs a bearer token supplied by the caller.  A
missing token, missing ``Mcp-Session-Id`` or an OAuth error remains visible as
BLOCKED; no response is promoted to a PASS by inference.
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.client import HTTPMessage
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .harness import MCPPreflightRun, RunStatus


@dataclass(frozen=True)
class MCPProbeConfig:
    """The non-secret identity and endpoint inputs for one provider probe."""

    ai_stream_id: str
    access_path: str
    server_id: str
    endpoint: str
    tool_profile: str = "atlas"
    atlas_tool_name: str = "atlas_hybrid_search"
    session_mode: str = "unknown"
    bearer_token: str | None = None
    timeout_s: float = 15.0


@dataclass(frozen=True)
class MCPProviderProfile:
    """Non-secret connection identity for one known AI-stream clone."""

    ai_stream_id: str
    endpoint: str
    server_id: str
    access_path: str
    session_mode: str = "stateless"


MCP_PROVIDER_PROFILES: dict[str, MCPProviderProfile] = {
    "chatgpt": MCPProviderProfile(
        "chatgpt",
        "https://flextrawurst.de/werkzeugkoerper-[PFAD-GESCHWAERZT]",
        "vps-mcp-chatgpt",
        "mcp_chatgpt_web",
    ),
    "codex": MCPProviderProfile(
        "codex",
        "https://flextrawurst.de/werkzeugkoerper-codex-[REDACTED]",
        "vps-mcp-codex",
        "mcp_provider",
    ),
    "claude": MCPProviderProfile(
        "claude",
        "https://flextrawurst.de/werkzeugkoerper-geteilt-[REDACTED]",
        "vps-mcp-claude",
        "mcp_provider",
    ),
    "gemini": MCPProviderProfile(
        "gemini",
        "https://flextrawurst.de/werkzeugkoerper-gemini-[REDACTED]",
        "vps-mcp-gemini",
        "mcp_provider",
    ),
}


def known_provider_profile(ai_stream_id: str) -> MCPProviderProfile:
    try:
        return MCP_PROVIDER_PROFILES[ai_stream_id]
    except KeyError as exc:
        raise ValueError(f"unknown MCP provider profile: {ai_stream_id}") from exc


def run_known_provider_p0(ai_stream_id: str, *, bearer_token: str | None = None) -> MCPProbeResult:
    """Run P0 using a checked-in non-secret provider profile."""

    profile = known_provider_profile(ai_stream_id)
    return run_mcp_p0(
        MCPProbeConfig(
            ai_stream_id=profile.ai_stream_id,
            access_path=profile.access_path,
            server_id=profile.server_id,
            endpoint=profile.endpoint,
            session_mode=profile.session_mode,
            bearer_token=bearer_token,
        )
    )


@dataclass(frozen=True)
class HTTPObservation:
    status: int | None
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    error: str | None = None


@dataclass
class MCPProbeResult:
    """Redacted, serialisable result of one P0 probe."""

    run: MCPPreflightRun
    endpoint: str
    server_info: dict[str, Any] | None = None
    protocol_version: str | None = None
    session_id: str | None = None
    session_mode: str = "unknown"
    tool_names: list[str] = field(default_factory=list)
    reachable_status: int | None = None
    last_http_error: str | None = None
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    atlas_content_observed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = self.run.to_dict()
        payload.update(
            {
                "endpoint": self.endpoint,
                "server_info": self.server_info,
                "protocol_version": self.protocol_version,
                "session_id": self.session_id,
                "session_mode": self.session_mode,
                "tool_count_observed": self.run.tool_count,
                "reachable_status": self.reachable_status,
                "last_http_error": self.last_http_error,
                "checked_at": self.checked_at,
                "atlas_content_observed": self.atlas_content_observed,
            }
        )
        return payload


def _headers(message: HTTPMessage) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in message.items()}


def _request(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    bearer_token: str | None = None,
    timeout_s: float,
) -> HTTPObservation:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache",
    }
    data: bytes | None = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return HTTPObservation(
                status=response.status,
                headers=_headers(response.headers),
                body=response.read().decode("utf-8", errors="replace"),
            )
    except HTTPError as exc:
        # An HTTP 401/403 is still a reachability observation.  The caller
        # decides whether it is an expected auth gate or a failed P0 stage.
        try:
            response_body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            response_body = ""
        observation = HTTPObservation(
            status=exc.code,
            headers=_headers(exc.headers),
            body=response_body,
            error=f"http_{exc.code}",
        )
        exc.close()
        return observation
    except (TimeoutError, URLError, OSError) as exc:
        return HTTPObservation(status=None, error=f"transport:{type(exc).__name__}")


def _json_body(observation: HTTPObservation) -> dict[str, Any] | list[Any] | None:
    if not observation.body:
        return None
    try:
        value = json.loads(observation.body)
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, (dict, list)) else None


def _rpc_with_session(
    endpoint: str,
    *,
    request_id: int,
    method: str,
    params: dict[str, Any] | None,
    bearer_token: str | None,
    timeout_s: float,
    session_id: str | None,
) -> HTTPObservation:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = Request(
        endpoint,
        data=json.dumps(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            },
            ensure_ascii=False,
        ).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            return HTTPObservation(
                status=response.status,
                headers=_headers(response.headers),
                body=response.read().decode("utf-8", errors="replace"),
            )
    except HTTPError as exc:
        try:
            response_body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            response_body = ""
        observation = HTTPObservation(
            status=exc.code,
            headers=_headers(exc.headers),
            body=response_body,
            error=f"http_{exc.code}",
        )
        exc.close()
        return observation
    except (TimeoutError, URLError, OSError) as exc:
        return HTTPObservation(status=None, error=f"transport:{type(exc).__name__}")


def _first_rpc_response(value: dict[str, Any] | list[Any] | None) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and "id" in item:
                return item
    return None


def _normalize_endpoint(endpoint: str) -> str:
    """Accept either a public MCP base URL or its explicit ``/mcp`` URL."""

    normalized = endpoint.rstrip("/")
    if normalized.endswith("/mcp") or normalized.endswith("/rpc"):
        return normalized
    return f"{normalized}/mcp"


def _block(result: MCPProbeResult, reason: str) -> MCPProbeResult:
    result.run._block(reason)  # noqa: SLF001 — package-local gate transition
    return result


def run_mcp_p0(config: MCPProbeConfig) -> MCPProbeResult:
    """Run one strictly ordered, read-only MCP-P0 probe."""

    run = MCPPreflightRun(
        id=f"mcp-p0-{config.ai_stream_id}-{uuid.uuid4().hex[:12]}",
        ai_stream_id=config.ai_stream_id,
        access_path=config.access_path,
        server_id=config.server_id,
        tool_profile=config.tool_profile,
    )
    endpoint = _normalize_endpoint(config.endpoint)
    result = MCPProbeResult(run=run, endpoint=endpoint)
    try:
        run.start()
        run.attest("configured")
    except RuntimeError:
        return result

    discovery = _request("GET", endpoint, timeout_s=config.timeout_s)
    result.reachable_status = discovery.status
    if discovery.status is None:
        return _block(result, discovery.error or "mcp_unreachable")
    try:
        run.attest("reachable")
    except RuntimeError:
        return result

    initialize = _rpc_with_session(
        endpoint,
        request_id=1,
        method="initialize",
        params={
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "augen-haende-mcp-p0", "version": "0.1"},
        },
        bearer_token=config.bearer_token,
        timeout_s=config.timeout_s,
        session_id=None,
    )
    result.last_http_error = initialize.error
    init_payload = _first_rpc_response(_json_body(initialize))
    init_result = init_payload.get("result") if init_payload else None
    if initialize.status != 200 or not isinstance(init_result, dict):
        return _block(result, "initialize_failed")
    result.server_info = init_result.get("serverInfo") if isinstance(init_result.get("serverInfo"), dict) else None
    result.protocol_version = init_result.get("protocolVersion") if isinstance(init_result.get("protocolVersion"), str) else None
    result.session_id = initialize.headers.get("mcp-session-id")
    observed_session_mode = config.session_mode
    if result.session_id and observed_session_mode == "unknown":
        observed_session_mode = "stateful"
    result.session_mode = observed_session_mode
    if result.session_id and observed_session_mode == "stateless":
        return _block(result, "stateless_handshake_with_session_id")
    if not result.session_id and observed_session_mode != "stateless":
        return _block(result, "session_mode_unattested")
    try:
        run.attest(
            "handshake_succeeded",
            session_id=result.session_id,
            session_mode=observed_session_mode,
        )
    except RuntimeError:
        return result

    tools_response = _rpc_with_session(
        endpoint,
        request_id=2,
        method="tools/list",
        params={},
        bearer_token=config.bearer_token,
        timeout_s=config.timeout_s,
        session_id=result.session_id,
    )
    tools_payload = _first_rpc_response(_json_body(tools_response))
    tools_result = tools_payload.get("result") if tools_payload else None
    tools = tools_result.get("tools") if isinstance(tools_result, dict) else None
    if tools_response.status != 200 or not isinstance(tools, list):
        return _block(result, "tools_list_failed")
    result.tool_names = [item.get("name", "") for item in tools if isinstance(item, dict) and isinstance(item.get("name"), str)]
    try:
        run.attest("tools_list_received", tool_count=len(result.tool_names))
    except RuntimeError:
        return result

    if not config.bearer_token:
        return _block(result, "atlas_read_requires_bearer_token")
    if config.atlas_tool_name not in result.tool_names:
        return _block(result, f"atlas_tool_not_listed:{config.atlas_tool_name}")

    atlas_response = _rpc_with_session(
        endpoint,
        request_id=3,
        method="tools/call",
        params={
            "name": config.atlas_tool_name,
            "arguments": {"query": "augen haende bridge MCP P0", "limit": 1},
        },
        bearer_token=config.bearer_token,
        timeout_s=config.timeout_s,
        session_id=result.session_id,
    )
    atlas_payload = _first_rpc_response(_json_body(atlas_response))
    atlas_result = atlas_payload.get("result") if atlas_payload else None
    content = atlas_result.get("content") if isinstance(atlas_result, dict) else None
    if (
        atlas_response.status != 200
        or not isinstance(atlas_result, dict)
        or atlas_result.get("isError")
        or not isinstance(content, list)
        or not any(
            isinstance(item, dict)
            and isinstance(item.get("text"), str)
            and item["text"]
            for item in content
        )
    ):
        return _block(result, "atlas_read_failed")
    result.atlas_content_observed = True
    try:
        run.attest("atlas_read_verified", tool_name=config.atlas_tool_name)
    except RuntimeError:
        return result
    return result


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Read-only Augen-und-Haende MCP-P0 probe")
    parser.add_argument("--stream", choices=("chatgpt", "codex", "claude", "gemini"))
    parser.add_argument("--provider", choices=("chatgpt", "codex", "claude", "gemini"))
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--server-id", default="vps-mcp")
    parser.add_argument("--access-path", default="mcp_provider")
    parser.add_argument("--bearer-env", default="")
    args = parser.parse_args()
    stream = args.stream or args.provider
    if not stream:
        parser.error("--stream oder --provider ist erforderlich")
    token = os.environ.get(args.bearer_env) if args.bearer_env else None
    if args.endpoint:
        result = run_mcp_p0(
            MCPProbeConfig(
                ai_stream_id=stream,
                access_path=args.access_path,
                server_id=args.server_id,
                endpoint=args.endpoint,
                bearer_token=token,
            )
        )
    else:
        result = run_known_provider_p0(stream, bearer_token=token)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.run.status is RunStatus.COMPLETED else 2


if __name__ == "__main__":
    raise SystemExit(_cli())
