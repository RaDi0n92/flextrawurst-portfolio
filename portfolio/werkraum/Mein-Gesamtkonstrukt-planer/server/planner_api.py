from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
APP_HTML = ROOT / "app" / "index.html"
SYNC_JS = ROOT / "server" / "sync.js"
WORKSPACE_JS = ROOT / "server" / "workspace.js"
STREAMS_JS = ROOT / "server" / "streams.js"
NOTES_JS = ROOT / "server" / "universal_notes.js"
DOM_CONTRACT_JS = ROOT / "server" / "dom_contract.js"
REPLICA_REGISTRY_JS = ROOT / "server" / "replica_registry.js"
OPERATING_SHELL_JS = ROOT / "server" / "operating_shell.js"
HUMAN_START_JS = ROOT / "server" / "human_start.js"
HUMAN_REDESIGN_JS = ROOT / "server" / "human_redesign.js"
LIVE_STREAM_JS = ROOT / "server" / "live_stream.js"
REAL_FS_UI_JS = ROOT / "server" / "real_fs_ui.js"
BABYLON_VENDOR_JS = ROOT / "static" / "vendor" / "babylon.js"
BABYLON_PROC_TEX_JS = ROOT / "static" / "vendor" / "babylon.proceduralTextures.min.js"
BABYLON_LOADERS_JS = ROOT / "static" / "vendor" / "babylon.loaders.min.js"
SCHROTTPLATZ_BABYLON_JS = ROOT / "server" / "schrottplatz_babylon.js"
DATA_DIR = ROOT / "data"
CURRENT = DATA_DIR / "current.json"
LOCK = DATA_DIR / ".state.lock"
EVENTS = DATA_DIR / "events"
HISTORY = DATA_DIR / "history"
MAX_BODY_BYTES = 6_000_000
TREE = DATA_DIR / "tree"
TRASH = TREE / ".papierkorb"
# Arbeitsorte sind ausdrücklich begrenzt: kein freies Dateisystem, sondern der echte Werkraum
# und der bisherige Gesamtkonstrukt-Bestand. Weitere Wurzeln können später bewusst ergänzt werden.
WORKSPACE_ROOTS = {
    "gesamtkonstrukt": {"label": "Arbeitsraum", "path": TREE, "sourcePrefix": "werkraum://"},
}
STREAMS = DATA_DIR / "ai_spuren.json"
REPLICA_CONTAINERS = DATA_DIR / "replica_containers.json"
BUILD_LOG = TREE / "ChatGPT_Work" / "03_Gemeinsame_Arbeit" / "BAULOG.ndjson"
MAX_FILE_BYTES = 1_000_000

WORKSPACE_SEED = {
    "00_Start/README.md": "# Mein Gesamtkonstrukt\n\nDies ist dein echter Arbeitsbestand. Dateien hier können geöffnet, bearbeitet, umbenannt, verschoben und in den Papierkorb gelegt werden. Mit **Als Arbeitsobjekt übernehmen** wird eine Datei bewusst zu einem realen Knoten im Planer.\n",
    "02_Ideen/erste-idee.md": "# Erste Idee\n\nWas soll aus dem Gesamtkonstrukt entstehen? Schreibe roh, skizzenhaft oder konkret.\n",
    "06_Redteam-Umbau/STATUS.md": "# Redteam-Umbau\n\n- [x] VPS ist die einzige Wahrheit fuer alle Browser\n- [x] Echter, geschuetzter Arbeitsordner statt lokaler Scheinablage\n- [x] Ordner und Unterordner anlegen, umbenennen, verschieben, oeffnen, bearbeiten\n- [x] Papierkorb statt sofortigem Loeschen\n- [x] Arbeitsdatei bewusst als reales Arbeitsobjekt in den Planer uebernehmen\n- [ ] Bild- und Dateiupload mit Herkunft und Vorschau\n- [ ] Mehr echte Werkzeuge pro Replica, nicht nur andere Ansicht\n\nDieser Ordner dokumentiert die Abarbeitung. Nur Dinge mit Haken sind bereits gebaut und pruefbar.\n",
    "03_Gemeinsame_Arbeit/README.md": "# Gemeinsame Arbeit\n\nHier bleibt nachvollziehbar, was Menschen und Agenten tatsächlich getan, geprüft, entschieden oder offen gelassen haben. Jede Notiz soll echte Planer-Objekte und Werkraum-Dateien referenzieren.\n",
    "03_Gemeinsame_Arbeit/PROTOKOLL.md": "# Protokoll\n\nDieser Ordner bleibt menschenlesbar. Die strukturierte, maschinenlesbare Fassung liegt daneben in `data/ai_spuren.json` und erscheint im Planer unter **Spurenraum**.\n",
}


def _ensure_workspace_tree() -> None:
    TREE.mkdir(parents=True, exist_ok=True)
    TRASH.mkdir(parents=True, exist_ok=True)
    # Sobald ein benannter Arbeitskörper den bisherigen Startbaum aufgenommen hat,
    # darf der Server keine alten Startordner und Seed-Dateien daneben neu erzeugen.
    if (TREE / "ChatGPT_Work").is_dir():
        return
    for folder in ("00_Start", "01_Material", "02_Ideen", "03_Abläufe", "04_Automationen", "05_Übergaben", "06_Redteam-Umbau", "03_Gemeinsame_Arbeit"):
        (TREE / folder).mkdir(parents=True, exist_ok=True)
    for relative, content in WORKSPACE_SEED.items():
        path = TREE / relative
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_state_bytes(state: dict) -> bytes:
    return json.dumps(
        state, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _state_hash(state: dict) -> str:
    return hashlib.sha256(_canonical_state_bytes(state)).hexdigest()


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@contextmanager
def _locked():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read_current() -> dict:
    with CURRENT.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _valid_state(state: object) -> bool:
    return (
        isinstance(state, dict)
        and isinstance(state.get("title"), str)
        and isinstance(state.get("objects"), list)
        and isinstance(state.get("edges"), list)
        and isinstance(state.get("feedback"), list)
    )


def _same_origin(request) -> bool:
    origin = request.headers.get("Origin")
    if not origin:
        return True
    parsed = urlparse(origin)
    return parsed.scheme in {"http", "https"} and parsed.netloc == request.get_host()


def _require_staff(request):
    """Diese API-Endpunkte sitzen unauthentifiziert auf einer echten, oeffentlich
    erreichbaren Website (kein login_required, der Origin-Check greift nicht ohne
    Origin-Header). Reused Django-eigenes is_staff-Muster (wie lexicon/views.py
    curator_required) statt einer neuen Auth zu bauen - Daniels User ist schon
    is_staff/is_superuser."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or not user.is_staff:
        return JsonResponse({"ok": False, "error": "auth_required"}, status=401)
    return None


def _append_event(wrapper: dict, previous: dict) -> None:
    EVENTS.mkdir(parents=True, exist_ok=True)
    state = wrapper["state"]
    feedback = state.get("feedback", [])
    event = {
        "at": wrapper["updatedAt"],
        "type": "planner.state.saved",
        "serverRevision": wrapper["serverRevision"],
        "previousServerRevision": previous.get("serverRevision", 0),
        "stateRevision": state.get("revision"),
        "sha256": wrapper["sha256"],
        "objects": len(state.get("objects", [])),
        "edges": len(state.get("edges", [])),
        "feedbackOpen": sum(1 for item in feedback if item.get("status") == "open"),
        "feedbackResolved": sum(
            1 for item in feedback if item.get("status") == "resolved"
        ),
    }
    event_path = EVENTS / f"{wrapper['updatedAt'][:10]}.ndjson"
    with event_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _append_build_log(wrapper: dict, action: str, details: dict | None = None) -> None:
    _ensure_workspace_tree()
    record = {
        "at": wrapper["updatedAt"],
        "serverRevision": wrapper["serverRevision"],
        "action": action,
        "details": details or {},
    }
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BUILD_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _snapshot_explicit_revision(wrapper: dict, previous: dict) -> None:
    current_revision = wrapper["state"].get("revision")
    previous_revision = previous.get("state", {}).get("revision")
    if current_revision == previous_revision:
        return
    HISTORY.mkdir(parents=True, exist_ok=True)
    name = (
        f"arbeitsrevision-{str(current_revision).zfill(4)}-"
        f"server-{str(wrapper['serverRevision']).zfill(6)}.json"
    )
    _atomic_json(HISTORY / name, wrapper)


def _relative(value: object, allow_root: bool = True) -> PurePosixPath:
    raw = str(value or "").strip().replace("\\\\", "/")
    if not raw and allow_root:
        return PurePosixPath(".")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("invalid_path")
    return path


def _safe_name(value: object) -> str:
    name = str(value or "").strip()
    if not name or len(name) > 120 or name in {".", ".."} or "/" in name or "\\\\" in name:
        raise ValueError("invalid_name")
    return name


def _read_replica_containers() -> dict:
    if not REPLICA_CONTAINERS.exists():
        return {"schemaVersion": 1, "updatedAt": _now(), "containers": []}
    try:
        payload = json.loads(REPLICA_CONTAINERS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"schemaVersion": 1, "updatedAt": _now(), "containers": []}
    if not isinstance(payload, dict) or not isinstance(payload.get("containers"), list):
        return {"schemaVersion": 1, "updatedAt": _now(), "containers": []}
    return payload


def _validate_koerper_sequence(nodes: list, edges: list, sequence_type: str, start_node_id: str) -> tuple[list[str], str | None]:
    # Reihenfolge wird IMMER hier aus dem Kantengraphen hergeleitet, nie vom Client
    # uebernommen - ein client-gesetzter Index waere bei einer Schleife irrefuehrend
    # (welcher Knoten ist "0"? die Ruecklaufkante verschwindet). sequence_type ist ein
    # echter Struktur-Check, keine Deko: "loop" nur bei echtem, alle Knoten umfassendem
    # Zyklus; "linear" nur bei einem einzigen Pfad ohne Verzweigung; "freeform"
    # ueberspringt die Reihenfolge-Pruefung komplett (bewusst - z.B. fuer eine reine
    # Momentaufnahme ohne Ablaufsinn).
    node_ids = []
    seen = set()
    for node in nodes:
        node_id = str(node.get("id") or "").strip() if isinstance(node, dict) else ""
        if not node_id or node_id in seen:
            return [], "invalid_koerper_nodes"
        seen.add(node_id)
        node_ids.append(node_id)
    node_id_set = set(node_ids)
    for edge in edges:
        if not isinstance(edge, dict):
            return [], "invalid_koerper_edges"
        if str(edge.get("from") or "") not in node_id_set or str(edge.get("to") or "") not in node_id_set:
            return [], "koerper_edge_unknown_node"
    if sequence_type == "freeform":
        return node_ids, None
    if sequence_type not in {"linear", "loop"}:
        return [], "invalid_sequence_type"
    if start_node_id not in node_id_set:
        return [], "invalid_start_node"
    out_map: dict[str, list[str]] = {}
    for edge in edges:
        out_map.setdefault(str(edge.get("from")), []).append(str(edge.get("to")))
    for targets in out_map.values():
        if len(targets) > 1:
            return [], "koerper_sequence_branches"
    visited = [start_node_id]
    visited_set = {start_node_id}
    current = start_node_id
    for _ in range(len(node_ids) + 1):
        nexts = out_map.get(current, [])
        if not nexts:
            if sequence_type == "linear" and len(visited) == len(node_ids):
                return visited, None
            if sequence_type == "loop":
                return [], "koerper_sequence_missing_loop_closure"
            return [], "koerper_sequence_incomplete_chain"
        nxt = nexts[0]
        if nxt == start_node_id:
            if sequence_type != "loop":
                return [], "koerper_sequence_not_linear"
            if len(visited) == len(node_ids):
                return visited, None
            return [], "koerper_sequence_incomplete_loop"
        if nxt in visited_set:
            return [], "koerper_sequence_cycle_not_closed"
        visited.append(nxt)
        visited_set.add(nxt)
        current = nxt
    return [], "koerper_sequence_too_long"


def _koerper_container(body_or_query, base: Path) -> dict:
    container_id = _safe_name(str(body_or_query.get("containerId") or "")).lower().replace(" ", "-")[:80]
    container = next((item for item in _read_replica_containers().get("containers", []) if item.get("id") == container_id), None)
    if not container:
        raise ValueError("koerper_container_not_found")
    return container


def _koerper_folder(container: dict, base: Path) -> Path:
    return _tree_path(str(container.get("path") or ""), base=base) / "Koerper"


def _workspace_root(value: object) -> tuple[str, dict]:
    root_id = str(value or "gesamtkonstrukt").strip()
    config = WORKSPACE_ROOTS.get(root_id)
    if not config:
        raise ValueError("unknown_workspace_root")
    return root_id, config


def _tree_path(relative: object, allow_root: bool = True, base: Path | None = None) -> Path:
    root = (base or TREE).resolve()
    target = (root / _relative(relative, allow_root)).resolve()
    if target != root and root not in target.parents:
        raise ValueError("path_outside_workspace")
    return target


def _node(path: Path, base: Path = TREE, root_label: str = "Mein Gesamtkonstrukt") -> dict:
    relative = path.relative_to(base).as_posix() if path != base else ""
    stat = path.stat()
    node = {
        "path": relative,
        "name": root_label if path == base else path.name,
        "kind": "folder" if path.is_dir() else "file",
        "modifiedAt": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if path.is_file():
        node["size"] = stat.st_size
        node["extension"] = path.suffix.lower()
    else:
        children = []
        for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.casefold())):
            if child.name == ".papierkorb":
                continue
            children.append(_node(child, base, root_label))
        node["children"] = children
    return node


def _atomic_text(path: Path, content: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _store_workspace_state(previous: dict, state: dict, action: str, details: dict | None = None) -> dict:
    events = state.setdefault("events", [])
    event = {
        "id": f"workspace-{uuid.uuid4()}",
        "at": _now(),
        "type": "workspace.file",
        "title": action,
        "source": "werkraum",
    }
    if details:
        event["details"] = details
    events.append(event)
    state["events"] = events[-120:]
    wrapper = {
        "schemaVersion": 1,
        "serverRevision": int(previous.get("serverRevision", 0)) + 1,
        "updatedAt": _now(),
        "sha256": _state_hash(state),
        "state": state,
    }
    _atomic_json(CURRENT, wrapper)
    _append_event(wrapper, previous)
    _append_build_log(wrapper, action, details)
    return wrapper


def _json_body(request) -> dict:
    if len(request.body) > MAX_BODY_BYTES:
        raise ValueError("body_too_large")
    body = json.loads(request.body.decode("utf-8"))
    if not isinstance(body, dict):
        raise ValueError("invalid_json")
    return body


def _read_streams() -> dict:
    if not STREAMS.exists():
        return {"schemaVersion": 1, "updatedAt": _now(), "entries": []}
    with STREAMS.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) and isinstance(value.get("entries"), list) else {"schemaVersion": 1, "updatedAt": _now(), "entries": []}


def _save_streams(value: dict) -> None:
    value["updatedAt"] = _now()
    _atomic_json(STREAMS, value)


def _rewrite_workspace_sources(state: dict, old_relative: str, new_relative: str, source_prefix: str = "werkraum://") -> None:
    old_prefix = f"{source_prefix}{old_relative}"
    new_prefix = f"{source_prefix}{new_relative}"
    for item in state.get("objects", []):
        source = item.get("sourcePath")
        if source == old_prefix or (isinstance(source, str) and source.startswith(old_prefix + "/")):
            item["sourcePath"] = new_prefix + source[len(old_prefix):]
            item["updatedAt"] = _now()


def planner_page(request):
    _ensure_workspace_tree()
    wrapper = _read_current()
    state = wrapper["state"]
    embedded = {
        "embeddedId": (
            f"server-r{wrapper['serverRevision']}-{wrapper['sha256'][:12]}"
        ),
        "exportedAt": wrapper["updatedAt"],
        "state": state,
    }
    embedded_json = json.dumps(embedded, ensure_ascii=False).replace("</", "<\\/")
    html = APP_HTML.read_text(encoding="utf-8")
    html = re.sub(
        r'(<script id="embedded-workspace" type="application/json">).*?(</script>)',
        lambda match: match.group(1) + embedded_json + match.group(2),
        html,
        count=1,
        flags=re.S,
    )
    bootstrap = (
        "<script>window.__PLANNER_SERVER_MODE__=true;"
        f"window.__PLANNER_SERVER_REVISION__={int(wrapper['serverRevision'])};"
        f"window.__PLANNER_SERVER_SHA__={json.dumps(wrapper['sha256'])};"
        "try{window.localStorage.setItem('arbeitskoerper.offline.workspace.v1',"
        + json.dumps(json.dumps(wrapper["state"], ensure_ascii=False))
        + ");}catch(_){}</script><script>"
        + SYNC_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + WORKSPACE_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + STREAMS_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + NOTES_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + DOM_CONTRACT_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + REPLICA_REGISTRY_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + OPERATING_SHELL_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + HUMAN_START_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + HUMAN_REDESIGN_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + LIVE_STREAM_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
        + "</script><script>"
        + REAL_FS_UI_JS.read_text(encoding="utf-8").replace("</script", "<\/script")
        + "</script><script>"
        + BABYLON_VENDOR_JS.read_text(encoding="utf-8").replace("</script", "<\/script")
        + "</script><script>"
        + BABYLON_PROC_TEX_JS.read_text(encoding="utf-8").replace("</script", "<\/script")
        + "</script><script>"
        + BABYLON_LOADERS_JS.read_text(encoding="utf-8").replace("</script", "<\/script")
        + "</script><script>"
        + SCHROTTPLATZ_BABYLON_JS.read_text(encoding="utf-8").replace("</script", "<\/script")
        + "</script>"
    )
    html = html.replace("</head>", bootstrap + "</head>", 1)
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "no-store, max-age=0"
    response["Pragma"] = "no-cache"
    response["X-Planner-Server-Revision"] = str(wrapper["serverRevision"])
    response["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'unsafe-inline' blob:; "
        "style-src 'unsafe-inline'; img-src data: blob:; font-src data:; "
        "connect-src 'self'; worker-src blob:; frame-ancestors 'self'; "
        "base-uri 'self'; form-action 'self'"
    )
    return response


def planner_auth_check(request):
    """Nur fuer nginx auth_request (Stage 3 / SSE): der Events-Stream laeuft als
    eigener kleiner Prozess ohne Django-Session-Handling, also spiegelt nginx jede
    Verbindung an diesen winzigen, schnellen Endpunkt statt Django-Sessions dort
    nachzubauen. Login-Pflicht auf Daniels ausdruecklichen Wunsch (05.09.) entfernt -
    siehe Revert von feaf7fe486 im selben Commit."""
    return HttpResponse(status=204)


@csrf_exempt
def planner_state_api(request):
    if request.method == "GET":
        wrapper = _read_current()
        response = JsonResponse(wrapper, json_dumps_params={"ensure_ascii": False})
        response["Cache-Control"] = "no-store, max-age=0"
        response["ETag"] = f'"{wrapper["sha256"]}"'
        return response

    if request.method not in {"PUT", "POST"}:
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    if not _same_origin(request):
        return JsonResponse({"ok": False, "error": "origin_not_allowed"}, status=403)
    if len(request.body) > MAX_BODY_BYTES:
        return JsonResponse({"ok": False, "error": "body_too_large"}, status=413)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    state = body.get("state") if isinstance(body, dict) else None
    base_revision = body.get("baseRevision") if isinstance(body, dict) else None
    if not _valid_state(state):
        return JsonResponse({"ok": False, "error": "invalid_state"}, status=400)

    with _locked():
        previous = _read_current()
        current_revision = int(previous.get("serverRevision", 0))
        if base_revision is not None and int(base_revision) != current_revision:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "server_revision_conflict",
                    "serverRevision": current_revision,
                    "sha256": previous.get("sha256"),
                    "updatedAt": previous.get("updatedAt"),
                },
                status=409,
            )

        new_hash = _state_hash(state)
        if new_hash == previous.get("sha256"):
            return JsonResponse(
                {
                    "ok": True,
                    "unchanged": True,
                    "serverRevision": current_revision,
                    "sha256": new_hash,
                    "updatedAt": previous.get("updatedAt"),
                }
            )

        wrapper = {
            "schemaVersion": 1,
            "serverRevision": current_revision + 1,
            "updatedAt": _now(),
            "sha256": new_hash,
            "state": state,
        }
        _atomic_json(CURRENT, wrapper)
        _append_event(wrapper, previous)
        _snapshot_explicit_revision(wrapper, previous)

    return JsonResponse(
        {
            "ok": True,
            "unchanged": False,
            "serverRevision": wrapper["serverRevision"],
            "sha256": wrapper["sha256"],
            "updatedAt": wrapper["updatedAt"],
        }
    )


@csrf_exempt
def planner_files_api(request):
    _ensure_workspace_tree()
    if request.method == "GET":
        try:
            if request.GET.get("roots") == "1":
                return JsonResponse({"ok": True, "roots": [{"id": root_id, "label": item["label"]} for root_id, item in WORKSPACE_ROOTS.items()]}, json_dumps_params={"ensure_ascii": False})
            root_id, config = _workspace_root(request.GET.get("root"))
            base = config["path"]
            if request.GET.get("op") == "replica-containers":
                return JsonResponse({"ok": True, "containers": _read_replica_containers().get("containers", [])}, json_dumps_params={"ensure_ascii": False})
            if request.GET.get("op") == "koerper-list":
                container = _koerper_container(request.GET, base)
                folder = _koerper_folder(container, base)
                items = []
                if folder.is_dir():
                    for entry in sorted(folder.glob("*.json")):
                        try:
                            record = json.loads(entry.read_text(encoding="utf-8"))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                        if record.get("schema") != "gkos.koerper.v1":
                            continue
                        items.append({
                            "id": record.get("id"), "title": record.get("title"),
                            "replicaId": record.get("replicaId"), "updatedAt": record.get("updatedAt"),
                            "nodeCount": len(record.get("sequence", {}).get("nodes", [])),
                            "sequenceType": record.get("sequence", {}).get("type"),
                            "startNodeId": record.get("sequence", {}).get("startNodeId") or "",
                        })
                return JsonResponse({"ok": True, "containerId": container.get("id"), "koerper": items}, json_dumps_params={"ensure_ascii": False})
            if request.GET.get("op") == "koerper-load":
                container = _koerper_container(request.GET, base)
                koerper_id = _safe_name(str(request.GET.get("id") or ""))
                target = _koerper_folder(container, base) / f"{koerper_id}.json"
                if not target.is_file():
                    return JsonResponse({"ok": False, "error": "koerper_not_found"}, status=404)
                record = json.loads(target.read_text(encoding="utf-8"))
                if record.get("schema") != "gkos.koerper.v1":
                    return JsonResponse({"ok": False, "error": "not_a_koerper"}, status=400)
                return JsonResponse({"ok": True, "koerper": record}, json_dumps_params={"ensure_ascii": False})
            if request.GET.get("op") == "read":
                path = _tree_path(request.GET.get("path"), allow_root=False, base=base)
                if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
                    return JsonResponse({"ok": False, "error": "file_not_readable"}, status=400)
                return JsonResponse({"ok": True, "root": root_id, "path": path.relative_to(base).as_posix(), "content": path.read_text(encoding="utf-8")}, json_dumps_params={"ensure_ascii": False})
            return JsonResponse({"ok": True, "root": root_id, "rootLabel": config["label"], "tree": _node(base, base, config["label"])}, json_dumps_params={"ensure_ascii": False})
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "error": "invalid_path"}, status=400)

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    if not _same_origin(request):
        return JsonResponse({"ok": False, "error": "origin_not_allowed"}, status=403)
    try:
        body = _json_body(request)
        operation = body.get("op")
        root_id, config = _workspace_root(body.get("root"))
        base = config["path"]
        source_prefix = config["sourcePrefix"]
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return JsonResponse({"ok": False, "error": str(error)}, status=400)

    try:
        with _locked():
            previous = _read_current()
            state = json.loads(json.dumps(previous["state"], ensure_ascii=False))
            result = {"ok": True}
            if operation == "replica-container":
                container_id = _safe_name(str(body.get("id") or "")).lower().replace(" ", "-")[:80]
                label = str(body.get("label") or container_id).strip()[:160] or container_id
                replica_ids = body.get("replicaIds") if isinstance(body.get("replicaIds"), list) else []
                replica_ids = sorted({str(item).strip()[:80] for item in replica_ids if str(item).strip()})[:17]
                if not container_id or not replica_ids:
                    raise ValueError("invalid_replica_container")
                metadata = _read_replica_containers()
                existing = next((item for item in metadata["containers"] if item.get("id") == container_id), None)
                relative = (PurePosixPath("01_Material") / "Replica-Container" / container_id).as_posix()
                folder = _tree_path(relative, base=base)
                folder.mkdir(parents=True, exist_ok=True)
                container_config = {
                    "id": container_id, "label": label, "path": relative,
                    "replicaIds": replica_ids, "format": {
                        "schemaVersion": 1,
                        "records": ["asset", "reference", "operation", "output", "link"],
                        "provenanceRequired": True,
                    },
                    "updatedAt": _now(),
                }
                if existing:
                    metadata["containers"][metadata["containers"].index(existing)] = container_config
                else:
                    metadata["containers"].append(container_config)
                metadata["updatedAt"] = _now()
                _atomic_json(REPLICA_CONTAINERS, metadata)
                readme = folder / "README.md"
                _atomic_text(readme, "# " + label + "\n\n" + "Gemeinsamer Container für: " + ", ".join(replica_ids) + "\n\n" + "Dieses Verzeichnis ist real auf Platte und in data/replica_containers.json verankert. Dateien behalten Herkunft; Werkstätten dürfen diesen Container nur benutzen, wenn sie in replicaIds stehen.\n")
                action = f"Werkstattcontainer: {container_id} für {', '.join(replica_ids)}"
                result.update({"container": container_config, "path": relative})
            elif operation == "create":
                parent = _tree_path(body.get("parent"), base=base)
                name = _safe_name(body.get("name"))
                kind = body.get("kind")
                if not parent.is_dir() or kind not in {"folder", "file"}:
                    raise ValueError("invalid_create")
                if kind == "file" and "." not in name:
                    name += ".md"
                target = parent / name
                if target.exists():
                    raise ValueError("already_exists")
                if kind == "folder":
                    target.mkdir()
                else:
                    content = str(body.get("content") or "")
                    if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                        raise ValueError("file_too_large")
                    _atomic_text(target, content)
                action = f"Werkraum: {'Ordner' if kind == 'folder' else 'Datei'} angelegt: {target.relative_to(base).as_posix()}"
                result["path"] = target.relative_to(base).as_posix()
            elif operation == "save":
                target = _tree_path(body.get("path"), allow_root=False, base=base)
                content = str(body.get("content") or "")
                if not target.is_file() or len(content.encode("utf-8")) > MAX_FILE_BYTES:
                    raise ValueError("file_not_writable")
                _atomic_text(target, content)
                action = f"Werkraum: Datei bearbeitet: {target.relative_to(base).as_posix()}"
                result["path"] = target.relative_to(base).as_posix()
            elif operation in {"rename", "move"}:
                source = _tree_path(body.get("path"), allow_root=False, base=base)
                if not source.exists():
                    raise ValueError("not_found")
                parent = source.parent if operation == "rename" else _tree_path(body.get("parent"), base=base)
                name = _safe_name(body.get("name")) if operation == "rename" else source.name
                target = parent / name
                if target.exists() or (source.is_dir() and source in parent.parents):
                    raise ValueError("invalid_destination")
                old_relative = source.relative_to(base).as_posix()
                new_relative = target.relative_to(base).as_posix()
                old_prefix = f"{source_prefix}{old_relative}"
                affected_object_ids = [
                    item.get("id") for item in state.get("objects", [])
                    if item.get("sourcePath") == old_prefix
                    or (isinstance(item.get("sourcePath"), str) and item["sourcePath"].startswith(old_prefix + "/"))
                ]
                os.replace(source, target)
                _rewrite_workspace_sources(state, old_relative, new_relative, source_prefix)
                action = f"Werkraum: {'umbenannt' if operation == 'rename' else 'verschoben'}: {new_relative}"
                result["path"] = new_relative
                result["eventDetails"] = {
                    "operation": operation,
                    "oldPath": old_relative,
                    "newPath": new_relative,
                    "affectedObjectIds": affected_object_ids,
                }
            elif operation == "trash":
                source = _tree_path(body.get("path"), allow_root=False, base=base)
                if not source.exists():
                    raise ValueError("not_found")
                trash = TRASH if base == TREE else base / ".papierkorb"
                trash.mkdir(parents=True, exist_ok=True)
                target = trash / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}--{source.name}"
                shutil.move(str(source), str(target))
                action = f"Werkraum: in Papierkorb gelegt: {source.relative_to(base).as_posix()}"
                result["trashed"] = source.relative_to(base).as_posix()
            elif operation == "object":
                source = _tree_path(body.get("path"), allow_root=False, base=base)
                if not source.is_file() or source.stat().st_size > MAX_FILE_BYTES:
                    raise ValueError("file_not_readable")
                relative = source.relative_to(base).as_posix()
                source_path = f"{source_prefix}{relative}"
                existing = next((item for item in state.get("objects", []) if item.get("sourcePath") == source_path), None)
                if existing:
                    return JsonResponse({"ok": True, "unchanged": True, "objectId": existing.get("id"), "serverRevision": previous.get("serverRevision")})
                object_id = f"object-{uuid.uuid4()}"
                title = source.stem.replace("-", " ").replace("_", " ").strip().title() or source.name
                content = source.read_text(encoding="utf-8")
                state.setdefault("objects", []).append({
                    "id": object_id, "title": title, "kind": "document", "truth": "real", "work": "roh",
                    "summary": f"Echte Arbeitsdatei: {relative}", "body": content,
                    "sourceName": "Werkraum-Datei", "sourcePath": source_path,
                    "humanInstruction": "Diese Datei ist bewusst als reales Arbeitsobjekt übernommen.",
                    "tags": ["werkraum", "datei"], "createdAt": _now(), "updatedAt": _now(),
                })
                roots = [item for item in state.get("objects", []) if item.get("kind") == "project"]
                if roots:
                    state.setdefault("edges", []).append({
                        "id": f"edge-{uuid.uuid4()}", "from": roots[0].get("id"), "to": object_id,
                        "type": "enthält", "reason": "Bewusst aus echter Werkraum-Datei übernommen.",
                        "provenance": "werkraum-datei", "createdAt": _now(),
                    })
                action = f"Werkraum: Datei als reales Arbeitsobjekt übernommen: {relative}"
                result["objectId"] = object_id
            elif operation == "refresh-object":
                source = _tree_path(body.get("path"), allow_root=False, base=base)
                if not source.is_file() or source.stat().st_size > MAX_FILE_BYTES:
                    raise ValueError("file_not_readable")
                relative = source.relative_to(base).as_posix()
                source_path = f"{source_prefix}{relative}"
                existing = next((item for item in state.get("objects", []) if item.get("sourcePath") == source_path), None)
                action = f"Werkraum: Aktualisierung eines Arbeitsobjekts geprüft: {relative}"
                if not existing:
                    result["unchanged"] = True
                else:
                    content = source.read_text(encoding="utf-8")
                    existing["body"] = content
                    existing["summary"] = f"Echte Arbeitsdatei: {relative}"
                    existing["updatedAt"] = _now()
                    action = f"Werkraum: Arbeitsobjekt aus Datei aktualisiert: {relative}"
                    result["objectId"] = existing.get("id")
            elif operation == "sketch-element":
                replica_id = "sketch"
                element_type = _safe_name(str(body.get("elementType") or "shape")).lower()[:40]
                label = str(body.get("label") or element_type).strip()[:160] or element_type
                container_id = _safe_name(str(body.get("containerId") or "")).lower().replace(" ", "-")[:80]
                available = [item for item in _read_replica_containers().get("containers", []) if replica_id in item.get("replicaIds", [])]
                container = next((item for item in available if item.get("id") == container_id), None)
                if not container:
                    raise ValueError("sketch_container_not_allowed")
                container_relative = str(container.get("path") or "")
                elements = _tree_path(container_relative, base=base) / "Inhalte" / "sketch"
                elements.mkdir(parents=True, exist_ok=True)
                record_id = f"sketch-{uuid.uuid4()}"
                relative = (PurePosixPath(container_relative) / "Inhalte" / "sketch" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{element_type}.json").as_posix()
                source = base / relative
                geometry = body.get("geometry")
                geometry = geometry if isinstance(geometry, dict) else None
                group_id = str(body.get("groupId") or "").strip()[:80] or None
                record = {
                    "schema": "gkos.sketch.element.v1", "id": record_id, "replica": replica_id,
                    "elementType": element_type, "label": label, "containerId": container.get("id"),
                    "contextPath": str(body.get("contextPath") or "")[:300],
                    "targetObjectId": str(body.get("targetObjectId") or "")[:120],
                    "geometry": geometry, "groupId": group_id,
                    "createdAt": _now(), "createdBy": "Werkstatt · Skizze",
                }
                _atomic_json(source, record)
                object_id = f"object-{uuid.uuid4()}"
                source_path = f"{source_prefix}{relative}"
                state.setdefault("objects", []).append({
                    "id": object_id, "title": f"Skizze · {label}", "kind": "artifact", "truth": "real", "work": "roh",
                    "summary": f"Strukturiertes Skizzenelement: {element_type} in {container_relative}",
                    "body": json.dumps(record, ensure_ascii=False, indent=2),
                    "sourceName": "Skizzen-Element", "sourcePath": source_path,
                    "humanInstruction": "Dieses Element ist eine echte Skizzendatei. Öffne die Quelle oder verknüpfe es bewusst.",
                    "tags": ["replica", "sketch", "element", element_type, f"container:{container.get('id')}"],
                    "createdAt": _now(), "updatedAt": _now(),
                })
                target_id = str(body.get("targetObjectId") or "").strip()
                targets = {item.get("id") for item in state.get("objects", [])}
                linked_to = target_id if target_id in targets and target_id != object_id else next((item.get("id") for item in state.get("objects", []) if item.get("kind") == "project"), None)
                if linked_to:
                    state.setdefault("edges", []).append({
                        "id": f"edge-{uuid.uuid4()}", "from": linked_to, "to": object_id,
                        "type": "hat Skizzenelement", "reason": f"Skizze: {element_type} · {label}.",
                        "provenance": "sketch-element", "createdAt": _now(),
                    })
                action = f"Skizze: {element_type} in Container {container.get('id')}: {relative}"
                result.update({"path": relative, "objectId": object_id, "linkedTo": linked_to, "containerId": container.get("id"), "record": record})
            elif operation == "sketch-element-update":
                element_path = _tree_path(body.get("path"), allow_root=False, base=base)
                if not element_path.is_file():
                    raise ValueError("sketch_element_not_found")
                record = json.loads(element_path.read_text(encoding="utf-8"))
                if record.get("schema") != "gkos.sketch.element.v1":
                    raise ValueError("not_a_sketch_element")
                geometry = body.get("geometry")
                if isinstance(geometry, dict):
                    record["geometry"] = geometry
                if "groupId" in body:
                    group_id = str(body.get("groupId") or "").strip()[:80]
                    record["groupId"] = group_id or None
                record["updatedAt"] = _now()
                _atomic_json(element_path, record)
                relative = element_path.relative_to(base).as_posix()
                source_path = f"{source_prefix}{relative}"
                existing_obj = next((item for item in state.get("objects", []) if item.get("sourcePath") == source_path), None)
                if existing_obj:
                    existing_obj["body"] = json.dumps(record, ensure_ascii=False, indent=2)
                    existing_obj["updatedAt"] = _now()
                action = f"Skizze: Element aktualisiert: {relative}"
                result.update({"path": relative, "record": record})
            elif operation == "koerper-save":
                # Bewusst NICHT in state.objects/edges gespiegelt (anders als sketch-element/
                # replica-action/note): Koerper sind ein eigenstaendiges Format mit eigener
                # Logik, kein Alias fuer das bestehende Objekt-Modell (explizite Entscheidung,
                # siehe Plan "Gemeinsame Arbeit & Betriebssystem"). Ueberschreibt bei bekannter
                # id dieselbe Datei statt (wie replica-action) bei jedem Aufruf eine neue
                # anzulegen - das ist die eigentliche "gleicher Koerper nach Neuladen"-Eigenschaft.
                container_id = _safe_name(str(body.get("containerId") or "")).lower().replace(" ", "-")[:80]
                replica_id = _safe_name(str(body.get("replicaId") or "")).lower()[:80]
                containers = _read_replica_containers().get("containers", [])
                container = next((item for item in containers if item.get("id") == container_id), None)
                if not container or replica_id not in container.get("replicaIds", []):
                    raise ValueError("koerper_container_not_allowed")
                koerper_id = str(body.get("id") or "").strip()
                is_new = not koerper_id
                if is_new:
                    koerper_id = f"koerper-{uuid.uuid4()}"
                elif not re.fullmatch(r"koerper-[0-9a-f-]{36}", koerper_id):
                    raise ValueError("invalid_koerper_id")
                title = str(body.get("title") or "Ohne Titel").strip()[:200] or "Ohne Titel"
                sequence_in = body.get("sequence") if isinstance(body.get("sequence"), dict) else {}
                nodes_in = sequence_in.get("nodes") if isinstance(sequence_in.get("nodes"), list) else []
                edges_in = sequence_in.get("edges") if isinstance(sequence_in.get("edges"), list) else []
                sequence_type = str(sequence_in.get("type") or "freeform")
                start_node_id = str(sequence_in.get("startNodeId") or "")
                ordered_ids, order_error = _validate_koerper_sequence(nodes_in, edges_in, sequence_type, start_node_id)
                if order_error:
                    raise ValueError(order_error)
                index_by_id = {node_id: position for position, node_id in enumerate(ordered_ids)}
                clean_nodes = [{
                    "id": str(node.get("id") or "").strip(),
                    "kind": str(node.get("kind") or "")[:80],
                    "title": str(node.get("title") or "")[:200],
                    "body": str(node.get("body") or "")[:MAX_FILE_BYTES],
                    "data": node.get("data") if isinstance(node.get("data"), dict) else {},
                    "index": index_by_id.get(str(node.get("id") or "").strip()),
                } for node in nodes_in]
                clean_edges = [{
                    "from": str(edge.get("from") or ""), "to": str(edge.get("to") or ""),
                    "type": str(edge.get("type") or "")[:80],
                } for edge in edges_in]
                folder = _koerper_folder(container, base)
                folder.mkdir(parents=True, exist_ok=True)
                target = folder / f"{koerper_id}.json"
                created_at = _now()
                if target.is_file():
                    try:
                        created_at = json.loads(target.read_text(encoding="utf-8")).get("createdAt") or created_at
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
                record = {
                    "schema": "gkos.koerper.v1", "id": koerper_id, "title": title,
                    "containerId": container.get("id"), "replicaId": replica_id,
                    "createdAt": created_at, "updatedAt": _now(),
                    "sequence": {
                        "type": sequence_type,
                        "startNodeId": start_node_id or (ordered_ids[0] if ordered_ids else ""),
                        "nodes": clean_nodes, "edges": clean_edges,
                    },
                }
                _atomic_json(target, record)
                relative = target.relative_to(base).as_posix()
                action = f"Betriebssystem: Koerper {'angelegt' if is_new else 'gespeichert'}: {koerper_id} in {container.get('id')}"
                result.update({"path": relative, "koerper": record, "containerId": container.get("id"), "isNew": is_new})
            elif operation == "replica-action":
                replica_id = _safe_name(str(body.get("replicaId") or "werkstatt"))[:80]
                action_name = str(body.get("action") or "Aktion").strip()[:160] or "Aktion"
                context_path = str(body.get("contextPath") or "").strip()[:300]
                target_id = str(body.get("targetObjectId") or "").strip()
                target_source_path = str(body.get("targetSourcePath") or "").strip()[:500]
                if not target_id and target_source_path:
                    target_id = next((item.get("id") for item in state.get("objects", []) if item.get("sourcePath") == target_source_path), "")
                requested_container_id = _safe_name(str(body.get("containerId") or "")).lower().replace(" ", "-")[:80]
                available_containers = [item for item in _read_replica_containers().get("containers", []) if replica_id in item.get("replicaIds", [])]
                container = next((item for item in available_containers if item.get("id") == requested_container_id), None) if requested_container_id else next((item for item in available_containers if item.get("id") == f"{replica_id}-eigen"), None)
                container = container or (available_containers[0] if available_containers else None)
                if not container:
                    raise ValueError("no_replica_container")
                container_relative = str(container.get("path") or "")
                container_folder = _tree_path(container_relative, base=base)
                operations = container_folder / "Operationen" / replica_id
                operations.mkdir(parents=True, exist_ok=True)
                action_stem = _safe_name(action_name).rsplit(".", 1)[0] or "Aktion"
                relative = (PurePosixPath(container_relative) / "Operationen" / replica_id / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{action_stem}.md").as_posix()
                source = base / relative
                header = f"# {replica_id} · {action_name}\n\n"
                links = f"- Arbeitskontext: `{context_path or 'root'}`\n- Verknüpftes Objekt: `{target_id or 'offen'}`\n- Verknüpfte Quelle: `{target_source_path or 'offen'}`\n- Zustand: `ausgeführt`\n\n"
                links = f"- Container: `{container.get('id')}` · `{container_relative}`\n" + links
                body_text = str(body.get("note") or "Die Aktion wurde in der Werkstatt bewusst ausgelöst. Ergebnis und weitere Semantik werden von dieser Werkstatt schrittweise konkretisiert.").strip()
                _atomic_text(source, header + links + body_text + "\n")
                object_id = f"object-{uuid.uuid4()}"
                source_path = f"{source_prefix}{relative}"
                state.setdefault("objects", []).append({
                    "id": object_id, "title": f"{replica_id} · {action_name}", "kind": "document", "truth": "real", "work": "roh",
                    "summary": f"Werkstattoperation: {relative}", "body": header + links + body_text,
                    "sourceName": "Replica-Operation", "sourcePath": source_path,
                    "humanInstruction": "Diese Operation entstand bewusst in einer Werkstatt. Öffne Quelle, Ergebnis und Verbindung.",
                    "tags": ["replica", replica_id, "operation", f"container:{container.get('id')}"], "createdAt": _now(), "updatedAt": _now(),
                })
                targets = {item.get("id") for item in state.get("objects", [])}
                linked_to = target_id if target_id in targets and target_id != object_id else next((item.get("id") for item in state.get("objects", []) if item.get("kind") == "project"), None)
                if linked_to:
                    state.setdefault("edges", []).append({
                        "id": f"edge-{uuid.uuid4()}", "from": linked_to, "to": object_id,
                        "type": "hat Werkstattoperation", "reason": f"{replica_id}: {action_name} im Kontext {context_path or 'root'}.",
                        "provenance": "replica-operation", "createdAt": _now(),
                    })
                action = f"Werkstatt: {replica_id} · {action_name}: {relative}"
                result.update({"path": relative, "objectId": object_id, "linkedTo": linked_to, "containerId": container.get("id"), "containerPath": container_relative})
            elif operation == "note":
                title = str(body.get("title") or "Notiz").strip()[:160] or "Notiz"
                content = str(body.get("content") or "").strip()
                if not content or len(content.encode("utf-8")) > MAX_FILE_BYTES:
                    raise ValueError("invalid_note")
                context_path = str(body.get("contextPath") or "").strip()[:300]
                target_id = str(body.get("targetObjectId") or "").strip()
                target_source_path = str(body.get("targetSourcePath") or "").strip()[:500]
                if not target_id and target_source_path:
                    target_id = next((item.get("id") for item in state.get("objects", []) if item.get("sourcePath") == target_source_path), "")
                notes = base / "03_Gemeinsame_Arbeit" / "Notizen"
                notes.mkdir(parents=True, exist_ok=True)
                stem = _safe_name(title).rsplit(".", 1)[0] or "Notiz"
                relative = (PurePosixPath("03_Gemeinsame_Arbeit") / "Notizen" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{stem}.md").as_posix()
                source = base / relative
                header = f"# {title}\n\n"
                links = f"- Arbeitskontext: `{context_path or 'root'}`\n- Verknüpftes Objekt: `{target_id or 'offen'}`\n- Verknüpfte Quelle: `{target_source_path or 'offen'}`\n\n"
                _atomic_text(source, header + links + content + "\n")
                object_id = f"object-{uuid.uuid4()}"
                source_path = f"{source_prefix}{relative}"
                state.setdefault("objects", []).append({
                    "id": object_id, "title": title, "kind": "document", "truth": "real", "work": "roh",
                    "summary": f"Verknüpfte Notiz: {relative}", "body": header + links + content,
                    "sourceName": "Verknüpfte Notiz", "sourcePath": source_path,
                    "humanInstruction": "Diese Notiz ist an ihrem Kontext entstanden; prüfe ihre Verbindung bewusst.",
                    "tags": ["notiz", "werkraum", "verknuepft"], "createdAt": _now(), "updatedAt": _now(),
                })
                targets = {item.get("id") for item in state.get("objects", [])}
                linked_to = target_id if target_id in targets and target_id != object_id else next((item.get("id") for item in state.get("objects", []) if item.get("kind") == "project"), None)
                if linked_to:
                    state.setdefault("edges", []).append({
                        "id": f"edge-{uuid.uuid4()}", "from": linked_to, "to": object_id,
                        "type": "hat Notiz", "reason": f"Notiz im Kontext {context_path or 'root'} bewusst angelegt.",
                        "provenance": "universelle-notiz", "createdAt": _now(),
                    })
                action = f"Werkraum: verknüpfte Notiz angelegt: {relative}"
                result.update({"path": relative, "objectId": object_id, "linkedTo": linked_to})
            else:
                raise ValueError("unknown_operation")
            wrapper = _store_workspace_state(previous, state, action, result.get("eventDetails"))
            result["serverRevision"] = wrapper["serverRevision"]
            result["root"] = root_id
            result["tree"] = _node(base, base, config["label"])
        return JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    except (ValueError, UnicodeDecodeError) as error:
        return JsonResponse({"ok": False, "error": str(error)}, status=400)


@csrf_exempt
def planner_streams_api(request):
    if request.method == "GET":
        return JsonResponse({"ok": True, "streams": _read_streams()}, json_dumps_params={"ensure_ascii": False})
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = _json_body(request)
        author = str(body.get("author") or "Unbenannt").strip()[:100]
        kind = str(body.get("kind") or "notiz").strip()[:40]
        title = str(body.get("title") or "Ohne Titel").strip()[:180]
        note = str(body.get("note") or "").strip()
        object_ids = body.get("objectIds") if isinstance(body.get("objectIds"), list) else []
        file_paths = body.get("filePaths") if isinstance(body.get("filePaths"), list) else []
        if not author or not note or len(note.encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError("invalid_stream_entry")
        with _locked():
            previous = _read_current()
            state = json.loads(json.dumps(previous["state"], ensure_ascii=False))
            valid_ids = {item.get("id") for item in state.get("objects", [])}
            entry = {"id": f"spur-{uuid.uuid4()}", "at": _now(), "author": author, "kind": kind, "title": title, "note": note, "objectIds": [item for item in object_ids if item in valid_ids], "filePaths": [str(item)[:300] for item in file_paths], "status": "offen"}
            streams = _read_streams(); streams["entries"].append(entry); streams["entries"] = streams["entries"][-500:]; _save_streams(streams)
            wrapper = _store_workspace_state(previous, state, f"Gemeinsame Arbeit: {kind} von {author}: {title}")
        return JsonResponse({"ok": True, "entry": entry, "serverRevision": wrapper["serverRevision"]}, json_dumps_params={"ensure_ascii": False})
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return JsonResponse({"ok": False, "error": str(error)}, status=400)



CHARACTER_GLB_DIR = ROOT / "static" / "models"
CHARACTER_GLB_ALLOWED = {
    "daniel_char_rigged.glb",
    "daniel_char_opa.glb",
    "daniel_char_frau_v1_static.glb",
    "daniel_char_frau_v2_rigged.glb",
    "daniel_char_maennlich_v1_rigged.glb",
    "daniel_char_savage_codex.glb",
}


def schrottplatz_character_glb(request, filename):
    """Liefert eines der freigegebenen Charakter-Modelle als GLB-Binaerdatei aus."""
    if filename not in CHARACTER_GLB_ALLOWED:
        return HttpResponse(status=404)
    path = CHARACTER_GLB_DIR / filename
    if not path.exists():
        return HttpResponse(status=404)
    data = path.read_bytes()
    response = HttpResponse(data, content_type="model/gltf-binary")
    response["Cache-Control"] = "public, max-age=3600"
    return response
