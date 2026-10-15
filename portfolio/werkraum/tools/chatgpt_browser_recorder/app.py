from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT.parent))

from tools.action_history.browser_capture import (  # noqa: E402
    BrowserCaptureError,
    browser_chat_export_data,
    browser_chat_office_export,
    browser_chat_client_artifact_export,
    list_collection_artifact_manifests,
    record_collection_artifact_manifest,
    browser_chat_recorded_segment_export_data,
    browser_web_export_data,
    browser_web_office_export,
    browser_chat_status,
    list_browser_chats,
    record_browser_events,
    read_browser_timeline,
    set_browser_chat_alias,
    verify_browser_capture,
)
from tools.action_history.browser_experiments import (  # noqa: E402
    BrowserExperimentError,
    apply_browser_experiment_action,
    browser_experiment_status,
    build_browser_experiment_timeline,
    create_browser_experiment,
    export_browser_experiment,
    list_browser_experiments,
)

TOKEN = os.environ.get("CHATGPT_BROWSER_RECORDER_TOKEN", "")
if not TOKEN:
    raise RuntimeError("CHATGPT_BROWSER_RECORDER_TOKEN fehlt")

app = FastAPI(title="ChatGPT Browser Recorder", version="1.3.3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Recorder-Token"],
)


def require_token(value: str | None) -> None:
    if not value or value != TOKEN:
        raise HTTPException(status_code=401, detail="Ungültiger Recorder-Token")


@app.exception_handler(BrowserCaptureError)
async def capture_error_handler(_request: Request, exc: BrowserCaptureError):
    return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    listing = list_browser_chats(limit=1)
    verification = verify_browser_capture()
    return {
        "ok": True,
        "service": "chatgpt-browser-recorder",
        "version": "1.3.3",
        "b_shared_timeline": True,
        "multisession_experiments": True,
        "chat_count": listing["count"],
        "storage_ok": verification["ok"],
    }


@app.post("/api/v1/events")
async def events(request: Request, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    payload = await request.json()
    if isinstance(payload, list):
        batch = payload
    elif isinstance(payload, dict) and isinstance(payload.get("events"), list):
        batch = payload["events"]
    elif isinstance(payload, dict):
        batch = [payload]
    else:
        raise HTTPException(status_code=400, detail="JSON-Ereignis oder events-Liste erforderlich")
    return record_browser_events(batch)


@app.exception_handler(BrowserExperimentError)
async def experiment_error_handler(_request: Request, exc: BrowserExperimentError):
    return JSONResponse(status_code=400, content={"ok": False, "error": str(exc), "experiment_layer_only": True})


@app.get("/api/v1/experiments")
def experiments(limit: int = 100, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    return list_browser_experiments(limit=max(1, min(limit, 1000)))


@app.post("/api/v1/experiments")
async def create_experiment(request: Request, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    return create_browser_experiment(
        str(payload.get("name") or ""),
        str(payload.get("description") or "") or None,
        software_versions=payload.get("software_versions") if isinstance(payload.get("software_versions"), dict) else None,
    )


@app.get("/api/v1/experiments/{experiment_id}")
def experiment_status(
    experiment_id: str,
    refresh_participants: bool = True,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_recorder_token)
    return browser_experiment_status(experiment_id, refresh_participants=refresh_participants)


@app.post("/api/v1/experiments/{experiment_id}/actions")
async def experiment_action(
    experiment_id: str,
    request: Request,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    action = str(payload.get("action") or "")
    action_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    return apply_browser_experiment_action(experiment_id, action, action_payload, source="daniel_manual_via_extension_or_api")


@app.get("/api/v1/experiments/{experiment_id}/timeline")
def experiment_timeline(
    experiment_id: str,
    participant_id: str | None = None,
    phase_id: str | None = None,
    source: str | None = None,
    event_type: str | None = None,
    influence_class: str | None = None,
    include_derived: bool = True,
    limit: int = 20000,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_recorder_token)
    return build_browser_experiment_timeline(
        experiment_id,
        participant_id=participant_id,
        phase_id=phase_id,
        source=source,
        event_type=event_type,
        influence_class=influence_class,
        include_derived=include_derived,
        limit=max(1, min(limit, 50000)),
        write_projection=True,
    )


@app.post("/api/v1/experiments/{experiment_id}/export")
def experiment_export(experiment_id: str, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    return export_browser_experiment(experiment_id)


@app.post("/api/v1/alias")
async def alias(request: Request, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    return set_browser_chat_alias(str(payload.get("identifier") or ""), str(payload.get("alias") or ""))


@app.get("/api/v1/chats")
def chats(limit: int = 100, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    return list_browser_chats(limit=max(1, min(limit, 500)))


@app.get("/api/v1/chats/{identifier}/export-data")
def chat_export_data(identifier: str, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    return browser_chat_export_data(identifier)


@app.get("/api/v1/chats/{identifier}/recorded-segment-export-data")
def chat_recorded_segment_export_data(
    identifier: str,
    import_id: str | None = None,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """Return the explicitly requested recording, never an accidental later one."""
    require_token(x_recorder_token)
    return browser_chat_recorded_segment_export_data(identifier, import_id=import_id)


@app.post("/api/v1/chats/{identifier}/office-export")
async def chat_office_export(
    identifier: str,
    request: Request,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """Persist a rich VPS artifact first, then return exactly those bytes to the browser."""
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    return browser_chat_office_export(
        identifier,
        scope=str(payload.get("scope") or ""),
        variant=str(payload.get("variant") or ""),
        format_name=str(payload.get("format") or ""),
    )


@app.post("/api/v1/chats/{identifier}/client-artifact-export")
async def chat_client_artifact_export(
    identifier: str,
    request: Request,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """Persist browser-generated HTML/MD after exact VPS turn-count verification."""
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    return browser_chat_client_artifact_export(
        identifier,
        scope=str(payload.get("scope") or ""),
        artifact_kind=str(payload.get("artifact_kind") or ""),
        filename=str(payload.get("filename") or ""),
        content_base64=str(payload.get("content_base64") or ""),
        content_sha256=str(payload.get("content_sha256") or ""),
        turn_count=payload.get("turn_count"),
        input_count=payload.get("input_count"),
        output_count=payload.get("output_count"),
        semantic_verification=payload.get("semantic_verification") if isinstance(payload.get("semantic_verification"), dict) else None,
    )


@app.post("/api/v1/collections/{identifier}/artifact-manifests")
async def collection_artifact_manifest(
    identifier: str,
    request: Request,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """Store one bounded manifest; export bytes stay in the browser/local collection store."""
    require_token(x_recorder_token)
    payload = await request.json()
    artifact = payload.get("artifact") if isinstance(payload, dict) else None
    if not isinstance(artifact, dict):
        raise HTTPException(status_code=400, detail="artifact-Manifest-Objekt erforderlich")
    return record_collection_artifact_manifest(identifier, artifact)


@app.get("/api/v1/collections/{identifier}/artifact-manifests")
def collection_artifact_manifest_list(
    identifier: str,
    limit: int = 100,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_recorder_token)
    return list_collection_artifact_manifests(identifier, limit=max(1, min(limit, 100)))


@app.get("/api/v1/web-pages/{identifier}/export-data")
def web_page_export_data(identifier: str, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    """Generate script-free PAGE.md/PAGE.html and preserve external links."""
    require_token(x_recorder_token)
    return browser_web_export_data(identifier)


@app.post("/api/v1/web-pages/{identifier}/office-export")
async def web_page_office_export(identifier: str, request: Request, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erforderlich")
    return browser_web_office_export(identifier, format_name=str(payload.get("format") or ""))


@app.get("/api/v1/chats/{identifier}")
def chat(identifier: str, x_recorder_token: str | None = Header(default=None)) -> dict[str, Any]:
    require_token(x_recorder_token)
    return browser_chat_status(identifier)


@app.get("/api/v1/chats/{identifier}/timeline")
def chat_timeline(
    identifier: str,
    provider_id: str | None = None,
    turn_id: str | None = None,
    mcp_session_id: str | None = None,
    event_type: str | None = None,
    binding_status: str | None = None,
    from_utc: str | None = None,
    to_utc: str | None = None,
    include_derived: bool = True,
    limit: int = 5000,
    x_recorder_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_token(x_recorder_token)
    return read_browser_timeline(
        identifier,
        provider_id=provider_id,
        turn_id=turn_id,
        mcp_session_id=mcp_session_id,
        event_type=event_type,
        binding_status=binding_status,
        from_utc=from_utc,
        to_utc=to_utc,
        include_derived=include_derived,
        limit=max(1, min(limit, 20000)),
        refresh_projection=True,
    )
