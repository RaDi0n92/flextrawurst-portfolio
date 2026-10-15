from __future__ import annotations

import base64
from collections import Counter
from contextvars import ContextVar
import difflib
import hashlib
import html
import io
import json
import os
import re
import sqlite3
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import quote, urlsplit, urlunsplit

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from public_bridge import ensure_public_bridge

APP_ROOT = Path(__file__).resolve().parent
ATLAS_ROOT = Path("/root/werkraum/_gpt/gesamtatlas")
REL_DB = ATLAS_ROOT / "BEZIEHUNGSREGISTER.sqlite"
BESTAETIGUNGSLOG = ATLAS_ROOT / "GEGENSATZ_BESTAETIGUNGSLOG.json"
PATH_DB = ATLAS_ROOT / "PFADINDEX.sqlite"
CONCEPT_DB = ATLAS_ROOT / "BEGRIFFSINDEX.sqlite"

URBEWOHNER_ROOT = ATLAS_ROOT / "urbewohner"
URBEWOHNER_REGISTER = URBEWOHNER_ROOT / "URBEWOHNERREGISTER.json"
BROWSER_ROOT = Path("/root/werkraum/_gpt/ui_visible_conversations")
BROWSER_INDEX = BROWSER_ROOT / "BROWSER_CONVERSATIONS_INDEX.json"
ASSIGNMENT_ROOT = ATLAS_ROOT / "auftraege/2026-07-29__GESAMTATLAS_GESAMTAUFTRAG"
BASE = ""
PUBLIC_BASE = "/gesamtatlas"
_REQUEST_PUBLIC_BASE: ContextVar[str] = ContextVar("gesamtatlas_request_public_base", default=BASE)
OMEGA_ROOT = ATLAS_ROOT / "omega"
BASELINE_POINTER_PATH = OMEGA_ROOT / "VERIFIED_FULL_BASELINE.json"
LIVE_DELTA_PATH = OMEGA_ROOT / "LIVE_DELTA_STATE.json"
OMEGA_BINDING_PATH = OMEGA_ROOT / "OMEGA_LEAN_BINDING.json"
MCP_WORLD_READY_PATH = OMEGA_ROOT / "checkpoints/MCP_WORLD_READY.json"
FINAL_SCAN_READY_PATH = OMEGA_ROOT / "checkpoints/FINAL_SCAN_READY.json"
WORLD_MODEL = "VERIFIED_FULL_BASELINE_PLUS_VISIBLE_LIVE_DELTA"
ORIGIN_QUERY = "VOR_VPS_URSPRUNGSRING_SUCHANKER_20260730"
ORIGIN_PATH = Path("/root/werkraum_gesamtatlas_eingang/DOKUMENTE/VOR_VPS_URSPRUNGSRING/START_HIER.md")
VERSION_PATHS = [
    Path("/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/build_proof_capsule.py.before_ai_stream_final"),
    Path("/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/build_proof_capsule.py.before_size_truth_overlay"),
    Path("/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/build_proof_capsule.py"),
]

AI_HOMES = {
    "chatgpt": {"label": "ChatGPT / MCP", "path": Path("/root/werkraum/_gpt/mcp_zuhause"), "accent": "violett"},
    "claude": {"label": "Claude Code", "path": Path("/root/werkraum/_claude"), "accent": "flieder"},
    "codex": {"label": "Codex", "path": Path("/root/werkraum/_codex"), "accent": "mint"},
    "gemini": {"label": "Gemini", "path": Path("/root/werkraum/_gemini"), "accent": "gold"},
    "kimi": {"label": "Kimi", "path": Path("/root/werkraum/_kimi"), "accent": "rosa"},
    "glm": {"label": "GLM", "path": Path("/root/werkraum/_glm"), "accent": "blau"},
}
AGENT_ROOTS = {
    "claude": Path("/root/.claude/projects/-root"),
    "codex": Path("/root/.codex/sessions"),
    "gemini": Path("/root/.gemini/antigravity-cli/brain"),
}
PUBLIC_TEXT_ROOTS = [
    ATLAS_ROOT,
    Path("/root/werkraum/_gpt/mcp_zuhause"),
    Path("/root/werkraum/_claude"),
    Path("/root/werkraum/_codex"),
    Path("/root/werkraum/_gemini"),
    Path("/root/werkraum/_kimi"),
    Path("/root/werkraum/_glm"),
    Path("/root/werkraum/tools/chatgpt_browser_recorder"),
    Path("/root/werkraum/tools/action_history"),
    Path("/root/werkraum_gesamtatlas_eingang/DOKUMENTE/VOR_VPS_URSPRUNGSRING"),
]
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".sh", ".sql", ".csv",
}
DENIED_SEGMENTS = {
    ".env", "auth.json", "oauth_creds.json", "credentials.json", "id_rsa", "id_ed25519",
    "private_key", "secrets", "cookies", "cookie", "token.json", "settings.json",
}
SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+\-/=]{12,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\s*[:=]\s*[\"']?)[^\s\"',}]{6,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"), "[PRIVATER SCHLÜSSEL ENTFERNT]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[API-SCHLÜSSEL ENTFERNT]"),
]

# Daniels eigene Projekt- und Gesprächsspuren sollen weit offen bleiben. Diese wenigen
# Muster schützen dagegen Kontaktdaten, die ebenso gut zu fremden Personen gehören können.
# Namen und soziale Zusammenhänge lassen sich nicht zuverlässig automatisch als fremd
# klassifizieren; diese verbleibende Grenze wird im Lückenorgan ausdrücklich benannt.
EXTERNAL_PRIVACY_PATTERNS = [
    (re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I), "[E-MAIL-ADRESSE IN AUSSENANSICHT ENTFERNT]"),
    (re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b", re.I), "[IBAN-ARTIGE ANGABE IN AUSSENANSICHT ENTFERNT]"),
    (re.compile(r"(?<!\w)(?:\+\d{1,3}|0\d{2,5})[\s()./\-]*(?:\d[\s()./\-]*){5,12}\d(?!\w)"), "[TELEFONNUMMER IN AUSSENANSICHT ENTFERNT]"),
]

app = FastAPI(
    title="Gesamtatlas",
    description="Begehbarer, originalgetreuer Gesamtatlas über VPS, Gespräche, AI-Ströme und Arbeitsgeschichte.",
    version="1.0.0",
    docs_url=f"{BASE}/api/docs",
    openapi_url=f"{BASE}/api/openapi.json",
    redoc_url=None,
)
app.mount(f"{BASE}/static", StaticFiles(directory=APP_ROOT / "static"), name="atlas-static")


@app.middleware("http")
async def bind_trusted_public_prefix(request: Request, call_next):
    requested = (request.headers.get("x-forwarded-prefix") or "").rstrip("/")
    prefix = PUBLIC_BASE if requested == PUBLIC_BASE else BASE
    previous_root_path = request.scope.get("root_path", "")
    is_static_mount = request.url.path.startswith(f"{BASE}/static/")
    request.scope["root_path"] = previous_root_path if is_static_mount else prefix
    token = _REQUEST_PUBLIC_BASE.set(prefix)
    try:
        response = await call_next(request)
        location = response.headers.get("location")
        if prefix and location:
            parts = urlsplit(location)
            target_path = parts.path or "/"
            if target_path.startswith("/") and not target_path.startswith(prefix + "/") and target_path != prefix:
                target_path = f"{prefix}{target_path}"
            if target_path == prefix:
                target_path = f"{prefix}/"
            response.headers["location"] = urlunsplit(("", "", target_path, parts.query, parts.fragment))
        return response
    finally:
        _REQUEST_PUBLIC_BASE.reset(token)
        request.scope["root_path"] = previous_root_path


@app.on_event("startup")
async def start_existing_public_door_bridge() -> None:
    ensure_public_bridge()


_CACHE: dict[str, tuple[float, Any]] = {}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def fmt_bytes(value: int | None) -> str:
    if value is None:
        return "unbekannt"
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return default


def cached(key: str, ttl: float, builder):
    now = time.monotonic()
    hit = _CACHE.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    value = builder()
    _CACHE[key] = (now, value)
    return value


def db(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=4)
    connection.row_factory = sqlite3.Row
    return connection


def encode_path(path: str) -> str:
    return base64.urlsafe_b64encode(path.encode("utf-8")).decode("ascii").rstrip("=")


def decode_path(token: str) -> str:
    token += "=" * (-len(token) % 4)
    try:
        return base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(400, "Ungültige Objektadresse") from exc


def href(path: str) -> str:
    normalized = path if path.startswith("/") else f"/{path}"
    prefix = _REQUEST_PUBLIC_BASE.get()
    if normalized == "/" and prefix:
        return f"{prefix}/"
    return f"{prefix}{normalized}"


def redact_secrets(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in SECRET_PATTERNS + EXTERNAL_PRIVACY_PATTERNS:
        text, n = pattern.subn(replacement, text)
        count += n
    return text, count


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ready_marker(path: Path, checkpoint_id: str) -> dict[str, Any]:
    if not path.exists():
        return {"ready": False, "present": False, "checkpoint_id": checkpoint_id, "path": str(path)}
    marker = load_json(path, None)
    if not isinstance(marker, dict) or marker.get("checkpoint_id") != checkpoint_id or marker.get("status") != "PASS":
        raise HTTPException(503, f"Ungültiger Ready-Marker: {checkpoint_id}")
    return {
        "ready": True, "present": True, "checkpoint_id": checkpoint_id, "path": str(path),
        "bytes": path.stat().st_size, "sha256": sha256_file(path),
        "created_utc": marker.get("created_utc") or marker.get("generated_utc"),
    }


def readiness_state() -> dict[str, Any]:
    world = ready_marker(MCP_WORLD_READY_PATH, "MCP_WORLD_READY")
    final = ready_marker(FINAL_SCAN_READY_PATH, "FINAL_SCAN_READY")
    if final["ready"] and not world["ready"]:
        raise HTTPException(503, "FINAL_SCAN_READY existiert ohne MCP_WORLD_READY")
    return {"mcp_world_ready": world["ready"], "final_scan_ready": final["ready"], "markers": {"mcp_world_ready": world, "final_scan_ready": final}}


def truth_ring(attempts: int = 7) -> dict[str, Any]:
    last_error = "unbekannt"
    for attempt in range(attempts):
        try:
            pointer_raw = BASELINE_POINTER_PATH.read_bytes();pointer=json.loads(pointer_raw)
            if pointer.get("pointer_class") != "CURRENT_VERIFIED_BASELINE_POINTER" or pointer.get("status") != "CURRENT_VERIFIED_BASELINE_POINTER" or pointer.get("world_model") != WORLD_MODEL:
                raise ValueError("Kanonischer Baseline-Pointer ist ungültig")
            target=pointer.get("target") or {};baseline_path=Path(str(target.get("path") or "")).resolve();expected=(OMEGA_ROOT/"verified_full_baselines"/str(pointer.get("revision"))).resolve();baseline_path.relative_to(expected)
            if not baseline_path.is_file() or baseline_path.is_symlink():raise ValueError("Pointerziel fehlt oder ist Symlink")
            baseline_raw=baseline_path.read_bytes();baseline_sha=hashlib.sha256(baseline_raw).hexdigest()
            if len(baseline_raw)!=target.get("bytes") or baseline_sha!=target.get("sha256"):raise ValueError("Pointerziel driftet")
            baseline=json.loads(baseline_raw);binding_raw=OMEGA_BINDING_PATH.read_bytes();binding=json.loads(binding_raw);delta_raw=LIVE_DELTA_PATH.read_bytes();delta=json.loads(delta_raw)
            if baseline.get("baseline_id")!=pointer.get("baseline_id") or baseline.get("revision")!=pointer.get("revision") or baseline.get("status")!="VERIFIED_FULL_BASELINE" or baseline.get("world_model")!=WORLD_MODEL:raise ValueError("Pointerkopf und Baseline widersprechen sich")
            checks=((baseline.get("verification") or {}).get("checks") or {})
            if not checks or not all(checks.values()):raise ValueError(f"Grundstand ist nicht vollständig PASS ({sum(bool(v) for v in checks.values())}/{len(checks)})")
            evidence={}
            for key in ("full_refresh","full_verification"):
                r=baseline.get(key) or {};ep=Path(str(r.get("path") or "")).resolve();ep.relative_to(expected)
                if not ep.is_file() or ep.is_symlink() or ep.stat().st_size!=r.get("bytes") or sha256_file(ep)!=r.get("sha256"):raise ValueError(f"Baseline-Evidence driftet: {key}")
                evidence[key]={"path":str(ep),"bytes":ep.stat().st_size,"sha256":sha256_file(ep)}
            if "/runtime/last_full_" in json.dumps(baseline,ensure_ascii=False):raise ValueError("Historische Baseline enthält bewegliche latest-Pfade")
            binding_sha=hashlib.sha256(binding_raw).hexdigest();delta_sha=hashlib.sha256(delta_raw).hexdigest();model=binding.get("world_model") or {};bref=binding.get("verified_full_baseline") or {};current=model.get("current_live_state") or {}
            if model.get("name")!=WORLD_MODEL:raise ValueError("Live-Binding besitzt falsches Weltmodell")
            for field,expected_value in {"path":str(baseline_path),"bytes":len(baseline_raw),"sha256":baseline_sha,"baseline_id":baseline["baseline_id"],"revision":baseline["revision"]}.items():
                if bref.get(field)!=expected_value:raise ValueError(f"Binding-Baseline driftet: {field}")
            live_ref=binding.get("live_delta_object") or {}
            if Path(str(live_ref.get("path") or "")).resolve()!=LIVE_DELTA_PATH.resolve():raise ValueError("Live-Nachlauf-Pfad driftet")
            comparisons={"live_delta_id":(delta.get("live_delta_id"),live_ref.get("live_delta_id")),"source_revision":(delta.get("source_revision"),binding.get("source_revision")),"publication_mode":(delta.get("publication_mode"),binding.get("publication_mode")),"source_dirty":(delta.get("source_dirty"),binding.get("source_dirty")),"baseline_id":(delta.get("baseline_id"),baseline.get("baseline_id")),"baseline_revision":(delta.get("baseline_revision"),baseline.get("revision")),"baseline_sha":(delta.get("baseline_manifest_sha256"),baseline_sha),"binding_sha":((delta.get("current_binding") or {}).get("sha256"),binding_sha)}
            for key,pair in comparisons.items():
                if pair[0]!=pair[1]:raise ValueError(f"Wahrheitsverknüpfung driftet: {key}")
            for field in ("live_delta_id","publication_mode","source_dirty","baseline_id","baseline_revision","revision_distance_from_baseline","current_live_revision_fully_verified","requires_new_full_verification"):
                if delta.get(field)!=current.get(field):raise ValueError(f"Live-Zustand driftet: {field}")
            if delta.get("source_revision")!=current.get("revision"):raise ValueError("Live-Revision driftet")
            distance=int(delta["source_revision"])-int(baseline["revision"])
            if delta.get("revision_distance_from_baseline")!=distance or (distance>0 and delta.get("requires_new_full_verification") is not True):raise ValueError("Live-Revisionssemantik driftet")
            return {"world_model":WORLD_MODEL,"pointer":{"path":str(BASELINE_POINTER_PATH),"bytes":len(pointer_raw),"sha256":hashlib.sha256(pointer_raw).hexdigest(),"pointer_class":pointer["pointer_class"],"target":target},"baseline":{"id":baseline["baseline_id"],"revision":baseline["revision"],"path":str(baseline_path),"bytes":len(baseline_raw),"sha256":baseline_sha,"verification_check_count":len(checks),"all_verification_checks_pass":True,"full_refresh":evidence["full_refresh"],"full_verification":evidence["full_verification"],"generated_utc":baseline.get("generated_utc")},"live":{"id":delta["live_delta_id"],"revision":delta["source_revision"],"path":str(LIVE_DELTA_PATH),"bytes":len(delta_raw),"sha256":delta_sha,"generated_utc":delta.get("generated_utc"),"publication_mode":delta["publication_mode"],"dirty":delta["source_dirty"],"baseline_id":delta["baseline_id"],"baseline_revision":delta["baseline_revision"],"revision_distance":distance,"fully_verified":delta["current_live_revision_fully_verified"],"current_live_revision_fully_verified":delta["current_live_revision_fully_verified"],"requires_new_full_verification":delta["requires_new_full_verification"]},"binding":{"path":str(OMEGA_BINDING_PATH),"bytes":len(binding_raw),"sha256":binding_sha},"historical_binding":baseline.get("historical_binding_observation") or {},"readiness":readiness_state(),"child_easy_explanation":model.get("child_easy_explanation"),"truth_boundary":binding.get("truth_boundary")}
        except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            last_error=str(exc)
            if attempt+1<attempts:time.sleep(0.08);continue
    raise HTTPException(503,f"Wahrheitsring ist im Moment nicht konsistent lesbar: {last_error}")



def journey_model() -> dict[str, Any]:
    truth = truth_ring()
    projects = project_rows()
    project = next((row for row in projects if "gesamtatlas" in (str(row.get("name") or "") + " " + str(row.get("path") or "")).casefold()), projects[0] if projects else None)
    project_id = str((project or {}).get("project_id") or "")
    project_href = f"/projekt/{quote(project_id)}" if project_id else "/projekte"
    baseline_original = f"/original/?p={encode_path(str(truth['baseline']['path']))}"
    origin_original = f"/original/?p={encode_path(str(ORIGIN_PATH))}"
    live_fully_verified = bool(truth['live']['current_live_revision_fully_verified'])
    live_title = "Der geprüfte aktuelle Stand" if live_fully_verified else "Die neuen Zettel"
    live_text = (f"Der aktuelle sichtbare Stand bei Revision {truth['live']['revision']} wurde gemeinsam mit dem Grundstand vollständig geprüft." if live_fully_verified else f"Der sichtbare Nachlauf steht bei Revision {truth['live']['revision']}. Er ist sichtbar, aber noch nicht vollständig neu geprüft.")
    steps = [
        {"number": 1, "title": "Ankommen", "text": "Du stehst vor einer Karte, die sichere, neue und fehlende Teile sichtbar trennt.", "evidence_label": "Weltkarte öffnen", "evidence_href": "/"},
        {"number": 2, "title": "Die geprüfte Karte", "text": f"Revision {truth['baseline']['revision']} wurde vollständig geprüft. Dieser Grundstand bleibt als eigener Beleg erhalten.", "evidence_label": "Grundstand als Original öffnen", "evidence_href": baseline_original},
        {"number": 3, "title": live_title, "text": live_text, "evidence_label": "Live-Wahrheit als JSON öffnen", "evidence_href": "/api/truth"},
        {"number": 4, "title": "Eine echte Herkunft", "text": "Der Vor-VPS-Ursprungsring steht vor späteren Berichten, Tests und Spiegelungen.", "evidence_label": "Ursprungsanker suchen", "evidence_href": f"/suche?q={quote(ORIGIN_QUERY)}"},
        {"number": 5, "title": "Ein echtes Projekt", "text": "Jetzt betrittst du einen real registrierten Projektkörper mit Herkunft, Dateien und Beziehungen.", "evidence_label": "Projektkörper betreten", "evidence_href": project_href},
        {"number": 6, "title": "Das Beziehungsnetz", "text": "Knoten und Kanten nennen ihre Wahrheitsklasse. Ähnlichkeit bleibt nicht heimlich Ursache.", "evidence_label": "Netz um Gesamtatlas öffnen", "evidence_href": "/beziehungen?q=gesamtatlas"},
        {"number": 7, "title": "Zum Original und zurück", "text": "Aus einer Behauptung wird ein lesbarer Bytekörper mit Pfad, Fingerabdruck und sichtbarem Rückweg.", "evidence_label": "Ursprungsoriginal öffnen", "evidence_href": origin_original},
        {"number": 8, "title": "Eine Veränderung", "text": "Drei echte Fassungen zeigen nach Bytes, Hash und Diff, was sich änderte und was gleich blieb.", "evidence_label": "Versionen vergleichen", "evidence_href": "/versionen"},
        {"number": 9, "title": "Drei kleine Kapseln", "text": "Mensch, Kind und Maschine erhalten dieselben Identitäten und dieselbe Gültigkeitsgrenze.", "evidence_label": "Kapseln und Maschinenzugang öffnen", "evidence_href": "/maschine"},
        {"number": 10, "title": "Jetzt frei", "text": "Die Führung endet. Suche, Zuhause, Browser, Terminal, Dateien, Beziehungen, Versionen und Lücken bleiben offen.", "evidence_label": "Frei erkunden", "evidence_href": "/erkunden"},
    ]
    return {"truth": truth, "steps": steps, "project_id": project_id, "original_path": truth["baseline"]["path"], "origin_path": str(ORIGIN_PATH)}




def small_capsules() -> dict[str, bytes]:
    truth = truth_ring()
    b, l = truth["baseline"], truth["live"]
    live_fully_verified = bool(l["current_live_revision_fully_verified"])
    if live_fully_verified:
        live_human = f"Der aktuelle sichtbare Stand `{l['id']}` steht ebenfalls bei Revision **{l['revision']}** und wurde gemeinsam mit dem Grundstand vollständig geprüft."
        live_child = f"Die geprüfte Karte und der aktuelle Stand tragen beide die Zahl **{l['revision']}**. Gerade ist alles gemeinsam vollständig kontrolliert."
    else:
        live_human = f"Der aktuelle sichtbare Nachlauf `{l['id']}` steht bei Revision **{l['revision']}**, also {l['revision_distance']} Revisionen später. Er ist **{l['publication_mode']}/dirty** und noch nicht vollständig neu geprüft."
        live_child = f"Danach kamen neue Zettel bis **{l['revision']}** dazu. Die alte geprüfte Karte bleibt richtig für ihren Moment. Die neuen Zettel sind sichtbar, aber der ganze neue Stapel wurde noch nicht wieder vollständig kontrolliert."
    historical_text = ("Die historischen Binding-Bytes des Grundstands wurden nicht erhalten und nicht rekonstruiert. Der beobachtete Fingerabdruck bleibt Provenienz, nicht erfundene Datei." if truth["historical_binding"] else "Für diesen neu verifizierten Grundstand ist kein separater historischer Binding-Körper gebunden. Fehlende historische Bytes werden nicht erfunden.")
    human = f'''# Gesamtatlas - Bergamekapsel Mensch

## Sicher geprüft
Der Vollgrundstand `{b['id']}` bei Revision **{b['revision']}** wurde vollständig geprüft ({b['verification_check_count']}/{b['verification_check_count']}).

## Aktueller sichtbarer Stand
{live_human}

## Ehrliche Grenze
{historical_text}

## Wege
- Kind: `{PUBLIC_BASE}/kind`
- Geführte Reise mit 10 Stationen: `{PUBLIC_BASE}/reise?schritt=1`
- Freie Erkundung: `{PUBLIC_BASE}/erkunden`
- Versionen: `{PUBLIC_BASE}/versionen`
- Dateien: `{PUBLIC_BASE}/dateien`
- Dokumente: `{PUBLIC_BASE}/dokumente`
- Dienste: `{PUBLIC_BASE}/dienste`
- Sitzungen: `{PUBLIC_BASE}/sitzungen`
- Maschinenwahrheit: `{PUBLIC_BASE}/api/truth`
'''.encode()
    child = f'''# Gesamtatlas - Bergamekapsel Kind

Wir haben die ganze Karte bei **{b['revision']}** geprüft.
{live_child}

Start: {PUBLIC_BASE}/kind
Reise mit 10 Stationen: {PUBLIC_BASE}/reise?schritt=1
Versionen: {PUBLIC_BASE}/versionen
'''.encode()
    machine = json.dumps({
        "schema_version": "1.1", "kind": "BERGAME_CAPSULE_MACHINE", "generated_utc": truth["live"].get("generated_utc") or truth["baseline"].get("generated_utc"),
        "world_model": truth["world_model"], "baseline": b, "live": l, "binding": truth["binding"],
        "historical_binding": truth["historical_binding"], "readiness": truth["readiness"],
        "routes": {
            "child": f"{PUBLIC_BASE}/kind", "journey": f"{PUBLIC_BASE}/reise?schritt=1", "journey_steps": 10,
            "free_exploration": f"{PUBLIC_BASE}/erkunden", "versions": f"{PUBLIC_BASE}/versionen", "versions_api": f"{PUBLIC_BASE}/api/versions",
            "files": f"{PUBLIC_BASE}/dateien", "documents": f"{PUBLIC_BASE}/dokumente", "services": f"{PUBLIC_BASE}/dienste",
            "sessions": f"{PUBLIC_BASE}/sitzungen", "truth_api": f"{PUBLIC_BASE}/api/truth"
        },
        "truth_boundary": truth["truth_boundary"],
    }, ensure_ascii=False, indent=2, sort_keys=True).encode()
    return {"MENSCH.md": human, "KIND.md": child, "MASCHINE.json": machine}




def nav(active: str = "") -> str:
    items = [
        ("welt", "/", "Welt"), ("kind", "/kind", "Kind"), ("reise", "/reise?schritt=1", "Reise"),
        ("suche", "/suche", "Suchen"), ("raum", "/raum", "Der Raum"), ("megavault", "/megavault", "MegaVault 3D"), ("projekte", "/projekte", "Projekte"), ("urbewohner", "/urbewohner", "Urbewohner"),
        ("beziehungen", "/beziehungen", "Netz"), ("versionen", "/versionen", "Versionen"), ("zuhause", "/zuhause", "Zuhause"), ("browser", "/browser", "Browser"),
        ("terminal", "/terminal", "Terminal"), ("luecken", "/luecken", "Lücken"), ("maschine", "/maschine", "Maschine"),
    ]
    chunks = []
    for key, path, label in items:
        css = "active" if key == active else ""
        chunks.append(f'<a class="{css}" href="{href(path)}">{label}</a>')
    links = "".join(chunks)
    return f'''<header class="topbar"><div class="shell topbar-inner">
<a class="skip" href="#inhalt">Zum Inhalt</a>
<a class="brand" href="{href('/')}"><span class="brand-mark" aria-hidden="true"></span><span>Gesamtatlas</span></a>
<nav class="nav" aria-label="Hauptnavigation">{links}</nav><span class="nav-spacer"></span>
<form class="search-mini" action="{href('/suche')}" method="get"><input name="q" aria-label="Atlas durchsuchen" placeholder="Spur, Projekt, Satz …"><button>Suchen</button></form>
</div></header>'''





def page(title: str, body: str, *, active: str = "", description: str = "", graph: dict[str, Any] | None = None) -> HTMLResponse:
    graph_attr = ""
    script = ""
    if graph is not None:
        graph_attr = f' data-graph="{esc(json.dumps(graph, ensure_ascii=False, separators=(",", ":")))}"'
        script = f'<script defer src="{href("/static/atlas.js")}"></script>'
    breadcrumbs = f'<nav class="breadcrumbs" aria-label="Brotkrumen"><a href="{href("/")}">Weltkarte</a><span aria-hidden="true">›</span><span aria-current="page">{esc(title)}</span></nav>'
    document = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} - Gesamtatlas</title><meta name="description" content="{esc(description or title)}"><meta name="color-scheme" content="dark">
<link rel="canonical" href="{href('/')}"/><link rel="stylesheet" href="{href('/static/atlas.css')}">{script}</head>
<body>{nav(active)}<main id="inhalt" class="shell"{graph_attr}>{breadcrumbs}{body}</main>
<footer class="footer"><div class="shell"><strong>Gesamtatlas</strong> - <a href="{href('/kind')}">Kind</a> - <a href="{href('/reise?schritt=1')}">Geführte Reise</a> - <a href="{href('/erkunden')}">Freie Erkundung</a> - <a href="{href('/versionen')}">Versionen</a> - <a href="{href('/kapsel/mensch.md')}">Mensch-Kapsel</a> - <a href="{href('/kapsel/kind.md')}">Kind-Kapsel</a> - <a href="{href('/kapsel/maschine.json')}">Maschinen-Kapsel</a> - <a href="{href('/kapsel.zip')}">Vollkapsel</a>.</div></footer></body></html>'''
    return HTMLResponse(document)





def atlas_status() -> dict[str, Any]:
    status = load_json(ATLAS_ROOT / "ATLAS_STATUS.json", {})
    projects = load_json(ATLAS_ROOT / "PROJEKTREGISTER.json", [])
    vaults = load_json(ATLAS_ROOT / "VAULTREGISTER.json", [])
    streams_raw = load_json(ATLAS_ROOT / "AI_STROEME.json", {})
    streams = streams_raw.get("streams", streams_raw) if isinstance(streams_raw, dict) else streams_raw
    path_count = None
    try:
        with db(PATH_DB) as con:
            path_count = int(con.execute("select count(*) from paths").fetchone()[0])
    except Exception:
        pass
    relation_counts = {"nodes": 0, "edges": 0}
    try:
        with db(REL_DB) as con:
            relation_counts = {"nodes": int(con.execute("select count(*) from nodes").fetchone()[0]), "edges": int(con.execute("select count(*) from edges").fetchone()[0])}
    except Exception:
        pass
    revision = status.get("revision") or status.get("atlas_revision") or status.get("current_revision")
    truth = truth_ring()
    return {
        "revision": revision, "generated_utc": status.get("generated_utc") or status.get("updated_utc"),
        "dirty": bool(status.get("dirty")), "full_refresh_recommended": bool(status.get("full_refresh_recommended")),
        "path_count": path_count, "projects": len(projects) if isinstance(projects, list) else 0,
        "vaults": len(vaults) if isinstance(vaults, list) else 0, "streams": len(streams) if hasattr(streams, "__len__") else 0,
        "relationship_nodes": relation_counts["nodes"], "relationship_edges": relation_counts["edges"],
        "truth": {"world_model": truth["world_model"], "baseline": truth["baseline"], "live": truth["live"], "readiness": truth["readiness"]},
    }



def project_rows() -> list[dict[str, Any]]:
    rows = load_json(ATLAS_ROOT / "PROJEKTREGISTER.json", [])
    if not isinstance(rows, list):
        return []
    return rows


def project_by_id(project_id: str) -> dict[str, Any] | None:
    return next((row for row in project_rows() if str(row.get("project_id")) == project_id), None)


def search_atlas(query: str, limit: int = 40) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    candidate_limit = max(limit * 4, 120)
    results: list[dict[str, Any]] = []
    tokens = re.findall(r"[\wäöüÄÖÜß-]+", query, re.UNICODE)[:10]
    if tokens and CONCEPT_DB.exists():
        fts = " AND ".join(f'"{token.replace(chr(34), "")}"*' for token in tokens)
        try:
            with db(CONCEPT_DB) as con:
                rows = con.execute(
                    "select path,title,headings,snippet(documents,3,'<mark>','</mark>',' … ',22) as excerpt,bm25(documents) as score from documents where documents match ? order by score limit ?",
                    (fts, candidate_limit),
                ).fetchall()
                for row in rows:
                    results.append({
                        "kind": "content", "path": row["path"],
                        "title": row["title"] or Path(row["path"]).name,
                        "headings": row["headings"] or "", "excerpt": row["excerpt"] or "", "score": row["score"],
                    })
        except sqlite3.Error:
            pass
    seen = {row["path"] for row in results}
    if PATH_DB.exists() and len(results) < candidate_limit:
        try:
            with db(PATH_DB) as con:
                rows = con.execute(
                    "select path,basename,kind,size,root_name,markers_json from paths where lower(path) like ? or lower(basename) like ? order by is_dir asc, length(path) asc limit ?",
                    (f"%{query.lower()}%", f"%{query.lower()}%", candidate_limit - len(results)),
                ).fetchall()
                for row in rows:
                    if row["path"] in seen:
                        continue
                    results.append({
                        "kind": row["kind"], "path": row["path"], "title": row["basename"],
                        "excerpt": f'{row["root_name"]} - {fmt_bytes(row["size"])}', "headings": "", "score": None,
                    })
                    seen.add(row["path"])
        except sqlite3.Error:
            pass
    if len(results) < candidate_limit:
        needle = query.casefold()
        for root in PUBLIC_TEXT_ROOTS:
            if not root.exists():
                continue
            try:
                for candidate in root.rglob("*"):
                    if len(results) >= candidate_limit:
                        break
                    try:
                        if not candidate.is_file() or candidate.suffix.lower() not in TEXT_SUFFIXES:
                            continue
                        candidate_text = str(candidate)
                        if needle not in candidate_text.casefold() and needle not in candidate.name.casefold():
                            continue
                        if candidate_text in seen:
                            continue
                        results.append({
                            "kind": "live_path", "path": candidate_text, "title": candidate.name,
                            "excerpt": "Live gefunden - noch nicht zwingend im letzten Vollindex", "headings": "", "score": None,
                        })
                        seen.add(candidate_text)
                    except OSError:
                        continue
            except OSError:
                continue
    results.sort(key=lambda row: exploration_rank(row, query))
    return results[:limit]



def exploration_rank(row: dict[str, Any], query: str) -> tuple[float, float, int, str]:
    path = str(row.get("path") or "")
    low = path.casefold()
    name = Path(path).name.casefold()
    provenance = 0.0
    if low.startswith("/root/werkraum_gesamtatlas_eingang/dokumente/vor_vps_ursprungsring/"):
        provenance -= 1000.0
    if "/ursprungsring/originalzeugen/" in low:
        provenance -= 700.0
    if name in {"start_hier.md", "readme.md", "manifest.json"}:
        provenance -= 100.0
    if "/evidence/" in low:
        provenance += 500.0
    if "/peer_review/" in low:
        provenance += 400.0
    if "/history/" in low:
        provenance += 300.0
    if "/tests/" in low or name.startswith("test_"):
        provenance += 300.0
    if "/zeitstrom/" in low or "/time_stream/" in low:
        provenance += 180.0
    try:
        bm25 = float(row.get("score")) if row.get("score") is not None else 0.0
    except (TypeError, ValueError):
        bm25 = 0.0
    return provenance, bm25, len(path), low


def public_original_href(path_text: str) -> str | None:
    if not path_text:
        return None
    target = str(Path(path_text).expanduser().resolve(strict=False))
    return f"{href('/original/')}?p={quote(encode_path(target))}"




def resolve_public_file(path_text: str) -> Path:
    candidate = Path(path_text).expanduser().resolve(strict=False)
    if not candidate.is_file():
        raise HTTPException(404, "Originalkörper nicht gefunden")
    if candidate.suffix.lower() not in TEXT_SUFFIXES:
        raise HTTPException(415, "Dieser Körper ist hier nur als Metadatum, nicht als Textoriginal darstellbar")
    if candidate.stat().st_size > 2_500_000:
        raise HTTPException(413, "Originalkörper ist für die direkte Webansicht zu groß")
    lower_parts = {part.lower() for part in candidate.parts}
    if any(segment.lower() in lower_parts or segment.lower() in candidate.name.lower() for segment in DENIED_SEGMENTS):
        raise HTTPException(403, "Dieser Körper bleibt wegen möglicher Zugangsdaten aus der Außenansicht ausgeschlossen")
    allowed = False
    for root in PUBLIC_TEXT_ROOTS:
        try:
            candidate.relative_to(root.resolve())
            allowed = True
            break
        except ValueError:
            continue
    if not allowed:
        raise HTTPException(403, "Dieser Originalkörper gehört nicht zur extern freigegebenen Textfläche")
    return candidate


def home_files(stream: str, limit: int = 180) -> list[dict[str, Any]]:
    spec = AI_HOMES.get(stream)
    if not spec:
        return []
    root: Path = spec["path"]
    if not root.exists():
        return []
    rows = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        try:
            relative = path.relative_to(root)
            if len(relative.parts) > 4:
                continue
            stat = path.stat()
            rows.append({"path": str(path), "relative": str(relative), "size": stat.st_size, "modified": stat.st_mtime})
        except OSError:
            continue
    rows.sort(key=lambda row: (row["relative"].count("/"), row["relative"].lower()))
    return rows[:limit]


def home_summary(stream: str) -> str:
    spec = AI_HOMES.get(stream)
    if not spec:
        return ""
    root: Path = spec["path"]
    for name in ("ZUHAUSE.md", "START_HIER.md", "RESONANZFELD.md", "README.md"):
        path = root / name
        if path.is_file():
            try:
                text = path.read_text("utf-8", errors="replace")
                text, _ = redact_secrets(text)
                return text[:900]
            except OSError:
                pass
    return "Noch kein lesbarer Eingangskörper erkannt."


def browser_conversations(limit: int = 240) -> list[dict[str, Any]]:
    def build():
        index = load_json(BROWSER_INDEX, {})
        folders = index.get("folders", {}) if isinstance(index, dict) else {}
        rows = []
        for folder, info in folders.items():
            path = BROWSER_ROOT / folder
            manifest = load_json(path / "MANIFEST.json", {})
            gaps = 0
            gap_file = path / "capture_gaps.jsonl"
            if gap_file.is_file():
                try:
                    gaps = sum(1 for line in gap_file.open("r", encoding="utf-8", errors="ignore") if line.strip())
                except OSError:
                    pass
            messages = manifest.get("message_count")
            if messages is None and (path / "messages.jsonl").is_file():
                try:
                    messages = sum(1 for line in (path / "messages.jsonl").open("r", encoding="utf-8", errors="ignore") if line.strip())
                except OSError:
                    messages = None
            rows.append({
                "folder": folder,
                "title": info.get("current_title") or manifest.get("title") or folder,
                "conversation_id": info.get("conversation_id") or manifest.get("conversation_id"),
                "updated_utc": info.get("updated_utc") or manifest.get("updated_utc") or manifest.get("last_updated_utc"),
                "messages": messages or 0,
                "gaps": gaps,
                "bound": bool(manifest.get("mcp_session_id") or manifest.get("mcp_binding_status") == "bound"),
            })
        rows.sort(key=lambda row: row.get("updated_utc") or "", reverse=True)
        return rows
    return cached("browser-conversations", 15, build)[:limit]


def browser_detail(folder: str, limit: int = 300) -> dict[str, Any]:
    if folder != Path(folder).name:
        raise HTTPException(400, "Ungültiger Gesprächsraum")
    root = (BROWSER_ROOT / folder).resolve()
    try:
        root.relative_to(BROWSER_ROOT.resolve())
    except ValueError as exc:
        raise HTTPException(400, "Ungültiger Gesprächsraum") from exc
    if not root.is_dir():
        raise HTTPException(404, "Gesprächsraum nicht gefunden")
    manifest = load_json(root / "MANIFEST.json", {})
    messages = []
    path = root / "messages.jsonl"
    if path.is_file():
        for line in path.open("r", encoding="utf-8", errors="replace"):
            if len(messages) >= limit:
                break
            try:
                row = json.loads(line)
            except Exception:
                continue
            content, redactions = redact_secrets(str(row.get("content") or ""))
            messages.append({
                "role": row.get("role") or "unbekannt", "content": content,
                "timestamp": row.get("timestamp_utc") or row.get("recorded_utc"),
                "turn_id": row.get("turn_id"), "classification": row.get("classification"),
                "redactions": redactions,
            })
    gaps = []
    gap_path = root / "capture_gaps.jsonl"
    if gap_path.is_file():
        for line in gap_path.open("r", encoding="utf-8", errors="replace"):
            if len(gaps) >= 100:
                break
            try:
                gaps.append(json.loads(line))
            except Exception:
                continue
    return {"folder": folder, "manifest": manifest, "messages": messages, "gaps": gaps, "truncated": len(messages) >= limit}


def terminal_sessions(provider: str, limit: int = 120) -> list[dict[str, Any]]:
    def build():
        root = AGENT_ROOTS.get(provider)
        if not root or not root.exists():
            return []
        paths: Iterable[Path]
        if provider == "claude":
            paths = root.glob("*.jsonl")
        elif provider == "codex":
            paths = root.rglob("rollout-*.jsonl")
        else:
            paths = (path for path in root.iterdir() if path.is_dir())
        rows = []
        for path in paths:
            try:
                if provider == "gemini":
                    files = list(path.glob("*.md"))
                    if not files:
                        continue
                    mtime = max(file.stat().st_mtime for file in files)
                    size = sum(file.stat().st_size for file in files)
                    session_id = path.name
                    file_path = str(path)
                else:
                    stat = path.stat()
                    mtime, size = stat.st_mtime, stat.st_size
                    session_id = path.stem
                    file_path = str(path)
                rows.append({
                    "provider": provider, "id": session_id, "path": file_path, "size": size,
                    "modified_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                })
            except OSError:
                continue
        rows.sort(key=lambda row: row["modified_at"], reverse=True)
        return rows
    return cached(f"terminal-{provider}", 20, build)[:limit]


def locate_terminal(provider: str, session_id: str) -> Path:
    root = AGENT_ROOTS.get(provider)
    if not root:
        raise HTTPException(404, "Agentenstrom unbekannt")
    if provider == "claude":
        candidate = root / f"{session_id}.jsonl"
    elif provider == "codex":
        matches = list(root.rglob(f"*{session_id}*.jsonl"))
        if not matches:
            raise HTTPException(404, "Terminalsitzung nicht gefunden")
        candidate = matches[0]
    else:
        candidate = root / session_id
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise HTTPException(400, "Ungültige Terminalsitzung") from exc
    if not candidate.exists():
        raise HTTPException(404, "Terminalsitzung nicht gefunden")
    return candidate


def extract_claude_event(row: dict[str, Any]) -> list[dict[str, Any]]:
    if row.get("type") not in ("user", "assistant"):
        return []
    message = row.get("message") or {}
    role = message.get("role") or row.get("type")
    content = message.get("content")
    events = []
    if isinstance(content, str):
        events.append({"role": role, "kind": "message", "text": content})
    elif isinstance(content, list):
        text_parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "text":
                text_parts.append(str(block.get("text") or ""))
            elif kind == "tool_use":
                events.append({"role": "tool", "kind": "tool_use", "text": f'{block.get("name")}\n{json.dumps(block.get("input") or {}, ensure_ascii=False, indent=2)}'})
            elif kind == "tool_result":
                events.append({"role": "tool", "kind": "tool_result", "text": str(block.get("content") or "")})
        if text_parts:
            events.insert(0, {"role": role, "kind": "message", "text": "\n".join(text_parts)})
    for event in events:
        event["timestamp"] = row.get("timestamp") or row.get("created_at")
    return events


def extract_codex_event(row: dict[str, Any]) -> list[dict[str, Any]]:
    if row.get("type") != "response_item":
        return []
    payload = row.get("payload") or {}
    kind = payload.get("type")
    timestamp = row.get("timestamp")
    if kind == "message":
        role = payload.get("role") or "assistant"
        if role == "developer":
            return []
        parts = []
        for block in payload.get("content") or []:
            if isinstance(block, dict) and block.get("type") in ("input_text", "output_text"):
                parts.append(str(block.get("text") or ""))
        return [{"role": role, "kind": "message", "text": "\n".join(parts), "timestamp": timestamp}] if parts else []
    if kind in ("function_call", "custom_tool_call"):
        name = payload.get("name") or payload.get("tool_name") or "tool"
        args = payload.get("arguments") or payload.get("input") or payload
        return [{"role": "tool", "kind": "tool_use", "text": f"{name}\n{args}", "timestamp": timestamp}]
    if kind in ("function_call_output", "custom_tool_call_output"):
        return [{"role": "tool", "kind": "tool_result", "text": str(payload.get("output") or payload), "timestamp": timestamp}]
    return []


def terminal_detail(provider: str, session_id: str, start: int = 0, limit: int = 100) -> dict[str, Any]:
    path = locate_terminal(provider, session_id)
    events: list[dict[str, Any]] = []
    total_seen = 0
    redactions = 0
    if provider == "gemini":
        files = sorted(path.glob("*.md"))
        for file in files:
            text = file.read_text("utf-8", errors="replace")
            text, count = redact_secrets(text)
            redactions += count
            if total_seen >= start and len(events) < limit:
                events.append({"role": "assistant", "kind": "document", "text": text[:120000], "timestamp": datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).isoformat(), "source": file.name})
            total_seen += 1
    else:
        extractor = extract_claude_event if provider == "claude" else extract_codex_event
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                for event in extractor(row):
                    if total_seen >= start and len(events) < limit:
                        clean, count = redact_secrets(str(event.get("text") or ""))
                        event["text"] = clean[:120000]
                        event["redactions"] = count
                        redactions += count
                        events.append(event)
                    total_seen += 1
                    if len(events) >= limit:
                        break
                if len(events) >= limit:
                    break
    return {
        "provider": provider, "session_id": session_id, "path": str(path), "size": path.stat().st_size if path.is_file() else None,
        "start": start, "limit": limit, "events": events, "next_start": start + len(events), "has_more": len(events) >= limit,
        "redactions": redactions,
    }


def _feld(row, name, ersatz=None):
    """Liest ein Feld aus einer sqlite3.Row, ohne zu sterben, wenn es die Spalte nicht gibt.

    sqlite3.Row hat kein .get(). Und truth_class steht nicht in BEZIEHUNGSREGISTER.sqlite.
    Vorher stuerzte /api/relationships deshalb mit
    AttributeError: 'sqlite3.Row' object has no attribute 'get' ab -- der gesamte
    Fadenkoerper (1.522 Knoten, 4.112 Kanten) war dadurch unerreichbar.
    """
    try:
        schluessel = row.keys() if hasattr(row, "keys") else ()
        return row[name] if name in schluessel else ersatz
    except Exception:
        return ersatz


def relationship_graph(query: str = "", limit: int = 40) -> dict[str, Any]:
    if not REL_DB.exists():
        return {"nodes": [], "edges": []}
    with db(REL_DB) as con:
        if query:
            like = f"%{query.lower()}%"
            seed = con.execute(
                """
                select * from nodes
                where lower(node_id) like ? or lower(identity) like ? or lower(coalesce(label,'')) like ? or lower(coalesce(path,'')) like ?
                order by
                    case when lower(node_id)=lower(?) then 0
                         when lower(identity)=lower(?) then 1
                         when lower(coalesce(label,''))=lower(?) then 2
                         when node_type='wesen' then 3
                         else 4 end,
                    node_type,label
                limit ?
                """,
                (like, like, like, like, query, query, query, limit),
            ).fetchall()
            seed_ids = [row["node_id"] for row in seed]
            if not seed_ids:
                return {"nodes": [], "edges": []}
            marks = ",".join("?" for _ in seed_ids)
            edges = con.execute(f"select * from edges where source_node_id in ({marks}) or target_node_id in ({marks}) limit ?", (*seed_ids, *seed_ids, limit * 3)).fetchall()
            all_ids = set(seed_ids)
            for edge in edges:
                all_ids.update((edge["source_node_id"], edge["target_node_id"]))
            marks2 = ",".join("?" for _ in all_ids)
            nodes = con.execute(f"select * from nodes where node_id in ({marks2})", tuple(all_ids)).fetchall()
        else:
            nodes = con.execute("select * from nodes order by case node_type when 'project' then 0 when 'ai_stream' then 1 else 2 end, label limit ?", (limit,)).fetchall()
            ids = [row["node_id"] for row in nodes]
            if ids:
                marks = ",".join("?" for _ in ids)
                edges = con.execute(f"select * from edges where source_node_id in ({marks}) and target_node_id in ({marks}) limit ?", (*ids, *ids, limit * 3)).fetchall()
            else:
                edges = []
    result_nodes = []
    for row in nodes:
        href_value = None
        if row["node_type"] == "project":
            match = next((p for p in project_rows() if p.get("project_id") == row["identity"] or p.get("path") == row["path"]), None)
            if match:
                href_value = href(f'/projekt/{quote(str(match.get("project_id")))}')
        elif row["node_type"] == "wesen":
            canonical = str(row["identity"] or "")
            href_value = href(f'/urbewohner/{quote(canonical)}')
        else:
            href_value = href(f'/knoten/{quote(str(row["node_id"]), safe="")}')
        result_nodes.append({
            "id": row["node_id"], "type": row["node_type"], "label": row["label"] or row["identity"],
            "path": row["path"], "truth_class": _feld(row, "datenstand") or "UNBEKANNT", "href": href_value,
        })
    result_edges = [{"source": row["source_node_id"], "target": row["target_node_id"], "relation": row["relation"], "truth_class": _feld(row, "datenstand") or "UNBEKANNT"} for row in edges]
    return {"nodes": result_nodes, "edges": result_edges}


def gap_report() -> dict[str, Any]:
    status = atlas_status()
    conversations = browser_conversations(500)
    browser_gaps = [row for row in conversations if row["gaps"]]
    excluded_count = 0
    try:
        with db(PATH_DB) as con:
            excluded_count = int(con.execute("select count(*) from paths where excluded_reason is not null and excluded_reason != ''").fetchone()[0])
    except Exception:
        pass
    missing_homes = [stream for stream, spec in AI_HOMES.items() if not spec["path"].exists()]
    terminal_counts = {provider: len(terminal_sessions(provider, 500)) for provider in AGENT_ROOTS}
    missing_terminal = [provider for provider, count in terminal_counts.items() if count == 0]
    dangling_edges = 0
    try:
        with db(REL_DB) as con:
            dangling_edges = int(con.execute("select count(*) from edges e left join nodes s on s.node_id=e.source_node_id left join nodes t on t.node_id=e.target_node_id where s.node_id is null or t.node_id is null").fetchone()[0])
    except Exception:
        pass
    gaps = []
    if status["dirty"] or status["full_refresh_recommended"]:
        gaps.append({"kind": "atlas_freshness", "severity": "mittel", "title": "Atlas meldet erneute Vollaktualisierung", "detail": "Neue Werkzeug- und Dateiereignisse sind bereits beobachtet, der Vollindex kann ihnen zeitlich hinterherlaufen."})
    if browser_gaps:
        gaps.append({"kind": "browser_capture", "severity": "hoch", "title": f"{len(browser_gaps)} Browserräume besitzen sichtbare Importlücken", "detail": "Die Lücken bleiben als eigene Ereignisse erhalten und werden nicht durch erfundene Gesprächsteile gefüllt."})
    if excluded_count:
        gaps.append({"kind": "index_exclusion", "severity": "niedrig", "title": f"{excluded_count} Pfadkörper tragen einen Ausschlussgrund", "detail": "Ausschluss kann Absicht, Größe, Format oder technische Begrenzung bedeuten und ist nicht mit Nichtexistenz gleichzusetzen."})
    if missing_homes:
        gaps.append({"kind": "home_missing", "severity": "mittel", "title": "Nicht alle vorgesehenen AI-Zuhause wurden gefunden", "detail": ", ".join(missing_homes)})
    if missing_terminal:
        gaps.append({"kind": "terminal_missing", "severity": "mittel", "title": "Nicht alle Terminalströme besitzen native Sitzungsquellen", "detail": ", ".join(missing_terminal)})
    if dangling_edges:
        gaps.append({"kind": "relationship_integrity", "severity": "hoch", "title": f"{dangling_edges} Beziehungskanten verweisen auf fehlende Knoten", "detail": "Diese Kanten werden nicht als belastbare Zusammenhänge präsentiert."})
    gaps.append({"kind": "foreign_person_context", "severity": "mittel", "title": "Fremde Personen lassen sich nicht vollständig automatisch erkennen", "detail": "E-Mail-Adressen, Telefonnummern, IBAN-artige Angaben und Geheimnisse werden in Außenansichten markiert entfernt. Namen, Rollen und indirekte soziale Zusammenhänge benötigen weiterhin menschliche Prüfung."})
    if not gaps:
        gaps.append({"kind": "known_unknowns", "severity": "niedrig", "title": "Keine der automatischen Kernlücken schlug an", "detail": "Das bedeutet nicht, dass der Atlas vollständig ist. Noch unbekannte Lücken bleiben möglich."})
    return {
        "generated_utc": utcnow(), "status": status, "browser_gap_rooms": browser_gaps[:80], "excluded_path_count": excluded_count,
        "missing_homes": missing_homes, "terminal_session_counts": terminal_counts, "dangling_edges": dangling_edges, "gaps": gaps,
    }


def capsule_path() -> Path:
    output = APP_ROOT / "runtime/GESAMTATLAS_KAPSEL.zip"
    meta_path = APP_ROOT / "runtime/GESAMTATLAS_KAPSEL.meta.json"
    truth = truth_ring()
    fingerprint = hashlib.sha256((truth["baseline"]["sha256"] + truth["live"]["sha256"] + truth["binding"]["sha256"]).encode()).hexdigest()
    meta = load_json(meta_path, {})
    if output.exists() and meta.get("fingerprint") == fingerprint and meta.get("zip_sha256") == sha256_file(output):
        return output
    status = atlas_status()
    gaps = gap_report()
    projects = project_rows()
    homes = [{"stream": key, "label": value["label"], "path": str(value["path"]), "files_visible": len(home_files(key))} for key, value in AI_HOMES.items()]
    browser = browser_conversations(100)
    terminal = {provider: terminal_sessions(provider, 100) for provider in AGENT_ROOTS}
    files: dict[str, bytes] = {}
    files["00_START_HIER.md"] = f'''# Gesamtatlas-Kapsel

Dies ist ein tragbarer Verständniskörper des lebenden Gesamtatlas. Er trennt den vollständig geprüften Grundstand von den danach sichtbaren neuen Spuren, zeigt reale Register und benennt Lücken. Er behauptet **nicht**, alle VPS-Originale in diesem kleinen ZIP zu enthalten.

## Beginne irgendwo

- `01_ELI10.md` erklärt den Atlas in einfacher Sprache.
- `BERGAME_KAPSELN/` enthält kleine Mensch-, Kind- und Maschinenkörper.
- `WAHRHEITSRING.json` bindet geprüften Grundstand und sichtbaren Live-Nachlauf.
- `SYSTEM_STATUS.json` zeigt den gemessenen Stand.
- `PROJEKTE.json`, `AI_ZUHAUSE.json`, `BROWSER_RAEUME.json` und `TERMINAL_SITZUNGEN.json` öffnen reale Erkundungsfelder.
- `LUECKEN.json` zeigt, was unvollständig, fraglich oder noch nicht geprüft ist.
- `MASCHINENZUGANG.md` erklärt die crawlbaren Endpunkte.

Wahrheitsfingerabdruck: `{fingerprint}`
'''.encode()
    files["01_ELI10.md"] = f'''# ELI10

Wir haben die ganze Karte bei Revision **{truth['baseline']['revision']}** geprüft. Danach kamen neue sichtbare Zettel bis Revision **{truth['live']['revision']}** dazu. Der Grundstand bleibt richtig für seinen geprüften Moment. Der neuere Stapel ist sichtbar, aber noch nicht vollständig neu geprüft.

Projekte sind Gebäude, Dateien sind Fundstücke, Chats sind Räume und jede AI hat ein eigenes Zuhause. Der Gesamtatlas zeigt nicht nur, wo etwas liegt. Er zeigt auch, woher es kam, was später daraus wurde, wer widersprach und wo etwas fehlt.
'''.encode()
    for name, payload in small_capsules().items():
        files[f"BERGAME_KAPSELN/{name}"] = payload
    files["WAHRHEITSRING.json"] = json.dumps(truth, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["SYSTEM_STATUS.json"] = json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["PROJEKTE.json"] = json.dumps(projects, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["AI_ZUHAUSE.json"] = json.dumps(homes, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["BROWSER_RAEUME.json"] = json.dumps(browser, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["TERMINAL_SITZUNGEN.json"] = json.dumps(terminal, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["LUECKEN.json"] = json.dumps(gaps, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["MASCHINENZUGANG.md"] = f'''# Maschinenzugang

Öffentliche Basis: `{PUBLIC_BASE}`

- `{PUBLIC_BASE}/api/truth`
- `{PUBLIC_BASE}/api/journey`
- `{PUBLIC_BASE}/api/capsules`
- `{PUBLIC_BASE}/api/status`
- `{PUBLIC_BASE}/api/search?q=...`
- `{PUBLIC_BASE}/api/projects`
- `{PUBLIC_BASE}/api/relationships?q=...`
- `{PUBLIC_BASE}/api/homes`
- `{PUBLIC_BASE}/api/browser`
- `{PUBLIC_BASE}/api/terminal`
- `{PUBLIC_BASE}/api/gaps`
- `{PUBLIC_BASE}/api/manifest`

Alle abgeleiteten Antworten sind als solche zu behandeln. Originalpfade, Sicherheitsauslassungen und bekannte Lücken werden sichtbar benannt.
'''.encode()
    assignment = ASSIGNMENT_ROOT / "GESAMTAUFTRAG.md"
    if assignment.is_file():
        files["GESAMTAUFTRAG.md"] = assignment.read_bytes()
    manifest_entries = [{"path": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()} for name, payload in sorted(files.items())]
    manifest = {
        "schema_version": "2.0", "generated_utc": truth["live"].get("generated_utc") or truth["baseline"].get("generated_utc"),
        "kind": "portable_understanding_capsule", "truth_fingerprint": fingerprint,
        "world_model": truth["world_model"], "baseline_id": truth["baseline"]["id"], "live_id": truth["live"]["id"],
        "contains_full_vps_corpus": False, "files": manifest_entries,
    }
    files["MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode()
    files["SHA256SUMS.txt"] = ("\n".join(f'{hashlib.sha256(payload).hexdigest()}  {name}' for name, payload in sorted(files.items())) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".tmp")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in sorted(files.items()):
            archive.writestr(name, payload)
    temp.replace(output)
    meta_path.write_text(json.dumps({"fingerprint": fingerprint, "zip_sha256": sha256_file(output), "generated_utc": truth["live"].get("generated_utc") or truth["baseline"].get("generated_utc")}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return output



@app.get(f"{BASE}/", response_class=HTMLResponse, include_in_schema=False)
def home():
    status = atlas_status()
    truth = status["truth"]
    b, l = truth["baseline"], truth["live"]
    refresh_class = "warn" if status["dirty"] or status["full_refresh_recommended"] else "ok"
    refresh_text = "Vollrefresh empfohlen" if status["full_refresh_recommended"] else "Register aktuell gemeldet"
    body = f'''
<section class="hero"><div><div class="kicker">Karte über alle Karten</div><h1>Eine Welt aus <span>echten Spuren.</span></h1>
<p>Der Gesamtatlas verbindet Projekte, Dateien, Browsergespräche, Terminalarbeit, AI-Zuhause, Beziehungen und Lücken. Er trennt dabei den vollständig geprüften Grundstand von allem, was danach lebendig hinzukam.</p>
<div class="hero-actions"><a id="child-start" class="button primary" href="{href('/kind')}">Wie für ein Kind beginnen</a><a id="journey-start" class="button" href="{href('/reise?schritt=1')}">Geführte Reise</a><a id="free-start" class="button" href="{href('/erkunden')}">Frei erkunden</a><a class="button" href="{href('/suche')}">Gezielt suchen</a></div></div>
<div class="orbit" aria-label="Organe des Gesamtatlas"><div class="orbit-core">Gesamt<br>atlas</div><div class="orbit-node">Browser-<br>archäologie</div><div class="orbit-node">Terminal-<br>werkstrom</div><div class="orbit-node">AI-<br>Zuhause</div><div class="orbit-node">Originale &<br>Provenienz</div><div class="orbit-node">Lücken &<br>Widersprüche</div></div></section>
<section id="truth-now" class="section"><div class="section-head"><div><div class="kicker">Zwei ehrliche Zeiten</div><h2>Geprüfter Grundstand und lebender Nachlauf</h2></div><span class="pill warn">Neuester Stand braucht später wieder Vollprüfung</span></div>
<div class="grid cols-2"><article class="card"><h3>Vollständig geprüft</h3><div id="baseline-revision" class="number">{b['revision']}</div><p id="baseline-id" class="path">{esc(b['id'])}</p><span class="pill ok">{b['verification_check_count']}/{b['verification_check_count']} Prüfungen PASS</span><p>Dieser Grundstand bleibt als eigener Beleg erhalten.</p><a class="button" href="{href('/original/?p=' + encode_path(b['path']))}">Grundstand-Original</a></article>
<article class="card"><h3>Sichtbar weitergelebt</h3><div id="live-revision" class="number">{l['revision']}</div><p id="live-id" class="path">{esc(l['id'])}</p><span class="pill warn">{esc(l['publication_mode'])}/dirty - noch nicht vollverifiziert</span><p>{l['revision_distance']} Revisionen nach dem Grundstand. Neue Spuren sind sichtbar, ohne sich als neu geprüfte Gesamtwahrheit auszugeben.</p><a class="button" href="{href('/api/truth')}">Live-Wahrheit als JSON</a></article></div></section>
<section class="section"><div class="section-head"><div><div class="kicker">Real gebundener Stand</div><h2>Was die Karte gerade wirklich sieht</h2></div><span class="pill {refresh_class}">Atlas r{esc(status['revision'] or '?')} - {refresh_text}</span></div>
<div class="grid cols-4"><div class="card"><div class="number">{status['path_count'] or 0:,}</div><div class="label">registrierte Pfade</div></div><div class="card"><div class="number">{status['projects']}</div><div class="label">Projekt- und Strukturkörper</div></div><div class="card"><div class="number">{status['vaults']}</div><div class="label">Vaults und Gedächtnisräume</div></div><div class="card"><div class="number">{status['relationship_edges']}</div><div class="label">Beziehungskanten</div></div></div></section>
<section class="section"><div class="section-head"><div><div class="kicker">Mehrere Einstiegstüren</div><h2>Du musst nicht vorne anfangen</h2></div><p>Der Atlas ist keine Prüfungsstrecke. Jeder Weg führt trotzdem zu einem greifbaren Original, Befund, Widerspruch oder nächsten Erkundungsschritt.</p></div>
<div class="grid cols-3">
<a class="card-link" href="{href('/reise?schritt=1')}"><div class="card"><h3>Einmal geführt hindurch</h3><p>Zehn Stationen: Ankommen, Grundstand, Live-Nachlauf, Ursprung, Projekt, Netz, Original, Versionen, Kapseln und freie Rückkehr.</p></div></a>
<a class="card-link" href="{href('/suche?q=Flextrawurst')}"><div class="card"><h3>Wo kam etwas zuerst vor?</h3><p>Suche gleichzeitig in Inhalt, Pfaden, Projekten und späteren Spuren.</p></div></a>
<a class="card-link" href="{href('/terminal')}"><div class="card"><h3>Wie wurde etwas wirklich gebaut?</h3><p>Gespräch, Toolaufrufe, Fehlwege und Ergebnisse aus den Coding-Werkstätten.</p></div></a>
<a class="card-link" href="{href('/browser')}"><div class="card"><h3>Was geschah im Browser?</h3><p>1:1-Nachrichten, sichtbare Prozesse, Bindungen und Importlücken.</p></div></a>
<a class="card-link" href="{href('/zuhause')}"><div class="card"><h3>Wie sehen die AI-Häuser aus?</h3><p>Getrennte Zuhause und Resonanzfelder, gemeinsam erforschbar.</p></div></a>
<a class="card-link" href="{href('/beziehungen')}"><div class="card"><h3>Was hängt womit zusammen?</h3><p>Belegte und modellierte Kanten bleiben unterscheidbar.</p></div></a>
<a class="card-link" href="{href('/urbewohner')}"><div class="card"><h3>Wer lebt im Weltkörper?</h3><p>Die acht Urbewohner mit Herkunft, Organen, Facetten, Vaults und echten Beziehungswegen.</p></div></a>
<a class="card-link" href="{href('/luecken')}"><div class="card"><h3>Was fehlt oder widerspricht sich?</h3><p>Der Atlas zeigt seine Löcher, statt sie mit überzeugender Prosa zuzuspachteln.</p></div></a>
<a class="card-link" href="{href('/kapsel/mensch.md')}"><div class="card"><h3>Kleine Kapsel mitnehmen</h3><p>Mensch, Kind oder Maschine: drei kurze tragbare Wahrheitskörper.</p></div></a>
</div></section>'''
    return page("Welt", body, active="welt", description="Begehbarer Gesamtatlas über VPS, Gespräche, AI-Ströme, Originale, geprüften Grundstand und sichtbaren Live-Nachlauf.")




@app.get(f"{BASE}/kind", response_class=HTMLResponse, include_in_schema=False)
def child_start():
    truth = truth_ring()
    b, l = truth["baseline"], truth["live"]
    body = f'''<section class="section-head"><div><div class="kicker">Kindleichter Einstieg</div><h1>Eine geprüfte Karte und neue Zettel</h1></div><span class="pill ok">Kein Vorwissen nötig</span></section>
<section class="card child-card"><p class="big-sentence">Wir haben die ganze Karte bei <strong>{b['revision']}</strong> geprüft.</p><p>Danach kamen neue Zettel bis <strong>{l['revision']}</strong> dazu.</p><p>Die geprüfte Karte bleibt richtig für den Moment, in dem sie geprüft wurde. Die neuen Zettel sind sichtbar, aber der ganze neue Stapel wurde noch nicht wieder vollständig kontrolliert.</p><p>Der Atlas zeigt deshalb beides gleichzeitig und tut nicht so, als wäre „neu“ automatisch „vollständig geprüft“.</p></section>
<section class="section"><div class="grid cols-3"><a id="child-journey" class="card-link" href="{href('/reise?schritt=1')}"><div class="card"><h2>Mit Führung losgehen</h2><p>Zehn kleine Stationen bis zum echten Original, zu Versionen und wieder zurück.</p></div></a><a id="child-free" class="card-link" href="{href('/erkunden')}"><div class="card"><h2>Selbst loslaufen</h2><p>Suche, Projekte, Gespräche, Zuhause, Netze und Lücken.</p></div></a><a id="child-machine" class="card-link" href="{href('/api/truth')}"><div class="card"><h2>Der Maschine zeigen</h2><p>Dieselbe Wahrheit als strukturiertes JSON.</p></div></a></div></section>
<section class="notice"><strong>Ehrliche Lücke:</strong> Vom damaligen Live-Binding kennen wir den Fingerabdruck. Die historischen Bytes wurden nicht erhalten und nicht nachgebaut.</section>'''
    return page("Kindleichter Einstieg", body, active="kind", description="Gesamtatlas kindleicht: geprüfter Grundstand und sichtbarer neuer Nachlauf.")


@app.get(f"{BASE}/reise", response_class=HTMLResponse, include_in_schema=False)
def journey(schritt: int = Query(1, ge=1, le=10)):
    model = journey_model()
    step = model["steps"][schritt - 1]
    truth = model["truth"]
    previous = f"/reise?schritt={schritt - 1}" if schritt > 1 else "/kind"
    following = f"/reise?schritt={schritt + 1}" if schritt < 10 else "/erkunden"
    steps = "".join(f'<a class="{"active" if item["number"] == schritt else ""}" href="{href("/reise?schritt=" + str(item["number"]))}">{item["number"]}</a>' for item in model["steps"])
    body = f'''<section class="section-head"><div><div class="kicker">Geführte Reise - Schritt {schritt} von 10</div><h1 id="journey-title">{esc(step['title'])}</h1></div><span id="journey-progress" class="pill info">{schritt}/10</span></section>
<nav class="journey-steps" aria-label="Reiseschritte">{steps}</nav>
<section class="card journey-stage"><p class="journey-text">{esc(step['text'])}</p><a id="journey-evidence" class="button primary" href="{href(step['evidence_href'])}">{esc(step['evidence_label'])}</a></section>
<section class="grid cols-2"><article class="card"><h2>Geprüfter Grundstand</h2><p class="path">{esc(truth['baseline']['id'])}</p><p>Revision {truth['baseline']['revision']} - vollständig geprüft.</p></article><article class="card"><h2>Aktueller Nachlauf</h2><p class="path">{esc(truth['live']['id'])}</p><p>Revision {truth['live']['revision']} - sichtbar, noch nicht vollständig neu geprüft.</p></article></section>
<nav class="journey-nav" aria-label="Reisenavigation"><a id="journey-prev" class="button" href="{href(previous)}">← Zurück</a><a class="button" href="{href('/')}">Weltkarte</a><a class="button" href="{href('/erkunden')}">Frei erkunden</a><a id="journey-next" class="button primary" href="{href(following)}">Weiter →</a></nav>'''
    return page(f"Reise {schritt}: {step['title']}", body, active="reise", description="Geführte Reise in zehn Stationen vom kindleichten Einstieg zum echten Original, zu Versionen und zurück.")




@app.get(f"{BASE}/erkunden", response_class=HTMLResponse, include_in_schema=False)
def explore():
    cards = [
        ("Geführte Reise", "Zehn Stationen vom einfachen Bild über Ursprung, Projekte und Netze bis zu Originalen, Versionen und zurück.", "/reise?schritt=1"),
        ("Kindleichter Anfang", "Beginne ohne Vorwissen bei der geprüften Karte und den neuen Zetteln.", "/kind"),
        ("Ein Satz", "Suche nach einer wörtlichen Formulierung und folge ihr zu Datei, Projekt und späteren Wirkungen.", "/suche"),
        ("Ein Projekt", "Öffne seine Dateien, Revision, Beziehungen, Sitzungen und Prüfspuren.", "/projekte"),
        ("Eine AI", "Betritt ihr Zuhause und springe von dort in ihre Terminal- oder Browsergeschichte.", "/zuhause"),
        ("Ein Irrweg", "Beginne bei Lücken, Fehlern oder widersprüchlichen Spuren.", "/luecken"),
        ("Ein Gespräch", "Lies Browserräume in chronologischer Folge mit sichtbaren Lückenmarkern.", "/browser"),
        ("Dateien und Dokumente", "Öffne registrierte Spuren als Original oder als ehrliche Zustandsseite.", "/dateien"),
        ("Dienste", "Verfolge Dienst- und systemd-Spuren ohne Eingriff in den laufenden VPS.", "/dienste"),
        ("Sitzungen", "Wechsle zwischen Browserräumen und getrennten Terminalwerkstätten.", "/sitzungen"),
        ("Versionen", "Vergleiche drei reale Fassungen nach Bytes, Hash und Diff.", "/versionen"),
        ("Eine Werkstatt", "Durchquere Terminaleingaben, Antworten, Tools und Ergebnisse.", "/terminal"),
        ("Nur treiben lassen", "Öffne das Beziehungsnetz und folge einem beliebigen Knoten.", "/beziehungen"),
        ("Kleine Kapseln", "Nimm Mensch-, Kind- oder Maschinenwahrheit direkt mit.", "/kapsel/mensch.md"),
        ("Alles mitnehmen", "Lade die große portable Verständniskapsel für ein fremdes LLM herunter.", "/kapsel.zip"),
    ]
    body = '<section class="section-head"><div><div class="kicker">Freie Erkundung</div><h1>Wo möchtest du hineinfallen?</h1></div><p>Kein vorgeschriebener Weg. Die tragenden Grenzen arbeiten im Untergrund, die Oberfläche bleibt ein Raum.</p></section><div class="grid cols-3">'
    for title, text, path in cards:
        body += f'<a class="card-link" href="{href(path)}"><div class="card"><h2>{esc(title)}</h2><p>{esc(text)}</p><span class="pill info">Eintreten →</span></div></a>'
    body += '</div>'
    return page("Erkunden", body, active="welt")



@app.get(f"{BASE}/suche", response_class=HTMLResponse, include_in_schema=False)
def search(q: str = Query("", max_length=300)):
    rows = search_atlas(q, 60) if q else []
    body = f'''<section class="section-head"><div><div class="kicker">Volltext, Pfade & KI-Antwort</div><h1>Spuren suchen & Fragen stellen</h1></div><p>Tippe ein Stichwort oder eine normale Frage ein. Der Gesamtatlas durchsucht alle Spuren und synthetisiert auf Wunsch eine Antwort.</p></section>
<form class="search-box" method="get"><input autofocus name="q" value="{esc(q)}" placeholder="Gib eine Frage oder ein Stichwort ein... (z. B. Was steht in AGENTS.md über Backup?)"><button>Suchen</button></form>'''
    if q:
        # KI-Antwort Synthese abrufen
        ask_data = api_megavault_ask(q=q, limit=5)
        ans_text = esc(ask_data.get("answer") or "")
        engine_label = esc(ask_data.get("engine") or "local")
        
        body += f'''<section class="section" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
  <h2 style="margin:0; font-size:1.2rem; color: var(--accent, #646cff);">🤖 KI-Antwort (Lokales Gedächtnis)</h2>
  <span class="pill info" style="font-size:0.75rem;">{engine_label}</span>
</div>
<div style="font-size:1.05rem; line-height:1.6; white-space:pre-wrap; color: var(--text, #e1e1e1);">{ans_text}</div>
</section>'''

        body += f'<section class="section"><div class="section-head"><h2>{len(rows)} Quell-Fundstellen für „{esc(q)}“</h2><span class="pill info">Ursprung vor Nachbericht</span></div><div class="list">'
        for index, row in enumerate(rows, start=1):
            excerpt = row.get("excerpt") or ""
            excerpt_safe = esc(excerpt).replace("&lt;mark&gt;", "<mark>").replace("&lt;/mark&gt;", "</mark>")
            headings_html = f'<span>{esc(row.get("headings"))}</span>' if row.get("headings") else ""
            original_href = public_original_href(str(row["path"]))
            access_html = '<span class="pill ok">Original außen lesbar</span>' if original_href else '<span class="pill warn">Spur sichtbar, Original außen nicht freigegeben</span>'
            article = f'''<article class="list-item" data-result-rank="{index}" data-result-path="{esc(row["path"])}"><h3>{esc(row.get('title'))}</h3><div class="path">{esc(row["path"])}</div><p>{excerpt_safe}</p><div class="meta"><span class="pill">{esc(row.get('kind'))}</span>{headings_html}{access_html}</div></article>'''
            if original_href:
                body += f'<a class="card-link original-result" href="{original_href}">{article}</a>'
            else:
                body += article
        body += '</div></section>'
        if not rows:
            body += '<div class="empty">Keine Spur gefunden. Das ist ein echter Nullbefund des aktuellen Indexes, keine Aussage, dass der Inhalt auf dem VPS sicher nicht existiert.</div>'
    return page("Suchen", body, active="suche")


# Cluster-Zuordnung fuer die Globus-Ansicht: echte node_type-Werte aus der DB
# (per SELECT node_type, COUNT(*) FROM nodes GROUP BY node_type verifiziert am
# 2026-08-14) auf sprechende Cluster-Namen gemappt. Keine erfundenen Kategorien --
# jeder Eintrag hier entspricht einem tatsaechlich vorkommenden node_type.
GLOBUS_CLUSTER = {
    "wesen":          {"label": "Wesen & Entitäten",     "farbe": "#e377c2"},
    "ai_stream":      {"label": "AI-Ströme",              "farbe": "#ff7f0e"},
    "geni_knoten":    {"label": "GENI Wahrnehmung",       "farbe": "#9467bd"},
    "gedanke":        {"label": "Gedanken & Ideen",       "farbe": "#ffbb78"},
    "flarum_thread":  {"label": "Gespräche & Diskurse",   "farbe": "#bcbd22"},
    "session":        {"label": "Sitzungen",               "farbe": "#2ca02c"},
    "file":           {"label": "Dateien & Archive",       "farbe": "#f7b6d2"},
    "vault":          {"label": "Vaults",                  "farbe": "#17becf"},
    "project":        {"label": "Projekte",                "farbe": "#1f77b4"},
    "service":        {"label": "Dienste & Infrastruktur", "farbe": "#8c564b"},
    "validation":     {"label": "Tests & Beweise",         "farbe": "#d62728"},
    "handoff":        {"label": "Übergaben",                "farbe": "#c5b0d5"},
    "claim":          {"label": "Ansprüche",                "farbe": "#98df8a"},
    "schlafphase":    {"label": "Schlafphasen",             "farbe": "#aec7e8"},
    "generated_view": {"label": "Generierte Ansichten",    "farbe": "#c49c94"},
    "consensus":      {"label": "Konsens",                  "farbe": "#ff9896"},
}

# 6-Schichten-Modell (Ebenen-Ansicht) -- Ursprung: Geminis Spiegel-Notiz
# 2026-07-31, Zuordnung der echten node_types verifiziert von ChatGPT
# 2026-08-15 (Datei: claudeweb_bau-megavault/zusammenarbeit/EBENEN_ZUORDNUNG_CHATGPT.md).
# Anzeigeordnung ueber denselben Knoten -- keine neue Ontologie, kein neuer
# ID-Raum. Manche Typen sind bewusst nicht erzwungen eindeutig (siehe dort).
EBENEN_MODELL = [
    {"nr": 1, "label": "Dateien & Ordner", "node_types": ["file", "vault"]},
    {"nr": 2, "label": "Chats & AI-Zuhause", "node_types": ["session", "flarum_thread", "ai_stream", "handoff"]},
    {"nr": 3, "label": "Tests & Beweise", "node_types": ["validation", "claim", "consensus"]},
    {"nr": 4, "label": "Dienste & Datenbanken", "node_types": ["service"]},
    {"nr": 5, "label": "Projekte & Visionen", "node_types": ["project", "generated_view"]},
    {"nr": 6, "label": "Wesen & Weltkörper", "node_types": ["wesen", "gedanke", "schlafphase", "geni_knoten"]},
]


@app.get(f"{BASE}/api/megavault/ebenen")
def api_megavault_ebenen():
    """Dieselben echten Cluster wie /api/megavault/globus, nur nach dem
    6-Schichten-Modell gruppiert statt einzeln je node_type -- eine andere
    Ordnung desselben Graphen, keine neue Datenquelle."""
    basis = api_megavault_globus()
    if not basis.get("ok"):
        return basis
    cluster_nach_typ = {c["node_type"]: c for c in basis["clusters"]}
    ebenen = []
    for eb in EBENEN_MODELL:
        enthaltene = [cluster_nach_typ[t] for t in eb["node_types"] if t in cluster_nach_typ]
        gesamt = sum(c["gesamt"] for c in enthaltene)
        ebenen.append({
            "nr": eb["nr"], "label": eb["label"], "gesamt": gesamt,
            "node_types": eb["node_types"], "cluster": enthaltene,
        })
    return {"ok": True, "gesamt_knoten": basis["gesamt_knoten"], "gesamt_kanten": basis["gesamt_kanten"],
            "ebenen": ebenen, "kanten_in_stichprobe": basis["kanten_in_stichprobe"]}


GLOBUS_SAMPLE_JE_CLUSTER = 60  # Deckel pro Cluster -- bei geni_knoten/gedanke (760k/99k)
                                 # ist das eine explizit benannte Stichprobe, keine Vollzaehlung.


@app.get(f"{BASE}/api/megavault/globus")
def api_megavault_globus():
    """Liefert die echten Cluster-Groessen (node_type-Zaehlung) plus eine
    gedeckelte, aber echte Stichprobe von Knoten je Cluster fuer die 3D-Globus-
    Ansicht. Zaehlung und Stichprobengroesse werden getrennt ausgewiesen, damit
    nie der Eindruck entsteht, die Stichprobe waere die Gesamtmenge."""
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}
    conn = sqlite3.connect(REL_DB)
    conn.row_factory = sqlite3.Row

    counts = {r["node_type"]: r["c"] for r in conn.execute(
        "SELECT node_type, COUNT(*) c FROM nodes GROUP BY node_type"
    ).fetchall()}
    total_edges = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]

    clusters = []
    for node_type, meta in GLOBUS_CLUSTER.items():
        total = counts.get(node_type, 0)
        if total == 0:
            continue
        rows = conn.execute(
            "SELECT node_id, node_type, label, path FROM nodes WHERE node_type = ? "
            "ORDER BY RANDOM() LIMIT ?", (node_type, GLOBUS_SAMPLE_JE_CLUSTER)
        ).fetchall()
        knoten = [dict(r) for r in rows]
        # Echte Dateisystem-Zeitstempel dazuholen -- "wann erstellt/zuletzt
        # beruehrt" fuer die spaeteren Sortierachsen (Daniels Vorgabe: nicht
        # erfunden, echter os.stat je Datei).
        if node_type == "file":
            for k in knoten:
                try:
                    st = Path(k["path"]).stat()
                    k["erstellt_utc"] = datetime.fromtimestamp(st.st_ctime, tz=timezone.utc).isoformat()
                    k["geaendert_utc"] = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
                    k["groesse_bytes"] = st.st_size
                except OSError:
                    pass
        clusters.append({
            "node_type": node_type,
            "label": meta["label"],
            "farbe": meta["farbe"],
            "gesamt": total,
            "stichprobe_groesse": len(rows),
            "knoten": knoten,
        })
    conn.close()

    # Cluster mit den meisten Knoten zuerst -- entspricht der visuellen Gewichtung
    # in den Referenzbildern (groessere Cluster nehmen mehr Kugelflaeche ein).
    clusters.sort(key=lambda c: c["gesamt"], reverse=True)

    # Echte Kanten NUR zwischen den tatsaechlich gezogenen Stichproben-Knoten --
    # keine erfundenen Verbindungen, nur was im Register wirklich zwischen genau
    # diesen Knoten-IDs existiert.
    alle_stichproben_ids = [k["node_id"] for c in clusters for k in c["knoten"]]
    kanten = []
    if alle_stichproben_ids:
        edge_conn = sqlite3.connect(REL_DB)
        edge_conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in alle_stichproben_ids)
        kanten_rows = edge_conn.execute(
            f"SELECT source_node_id, target_node_id, relation FROM edges "
            f"WHERE source_node_id IN ({placeholders}) AND target_node_id IN ({placeholders}) LIMIT 3000",
            alle_stichproben_ids + alle_stichproben_ids,
        ).fetchall()
        kanten = [dict(r) for r in kanten_rows]
        edge_conn.close()

    return {"ok": True, "gesamt_knoten": sum(counts.values()), "gesamt_kanten": total_edges, "clusters": clusters, "kanten_in_stichprobe": kanten}


@app.get(f"{BASE}/megavault", response_class=HTMLResponse, include_in_schema=False)
def megavault_3d():
    html = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MegaVault - Gesamtatlas</title>
<style>
  :root {
    --bg: #2F353B; --panel: rgba(24,28,32,0.92); --border: rgba(180,170,150,0.16);
    --text: #FAFAFA; --text-dim: #A1A1AA; --text-faint: #71717A;
    --akzent-warm: #C04000; --akzent-kuehl: #8B5CF6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 100%; height: 100%; overflow: hidden; background: var(--bg); font-family: ui-monospace, monospace; color: var(--text); }
  #buehne { position: fixed; inset: 0; }
  .ansicht { position: absolute; inset: 0; display: none; }
  .ansicht.aktiv { display: block; }
  #hud { position: fixed; inset: 0; pointer-events: none; z-index: 10; }
  .panel { pointer-events: auto; position: absolute; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; backdrop-filter: blur(12px); box-shadow: 0 12px 40px rgba(0,0,0,0.6); }
  #kopf { top: 12px; left: 12px; right: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; padding: 10px 14px; }
  #kopf .titel { font-weight: 700; letter-spacing: 0.08em; color: var(--akzent-warm); font-size: 0.85rem; white-space: nowrap; }
  #linsen { display: flex; gap: 4px; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 3px; }
  #linsen button { background: transparent; border: none; color: var(--text-dim); padding: 6px 12px; border-radius: 6px; font-family: inherit; font-size: 0.74rem; cursor: pointer; }
  #linsen button.aktiv { background: var(--akzent-warm); color: var(--text); }
  #linsen button:disabled { opacity: 0.35; cursor: default; }
  #filterzeile { display: flex; gap: 6px; align-items: center; }
  #filterzeile select { background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text-dim); border-radius: 6px; padding: 6px 8px; font-family: inherit; font-size: 0.7rem; max-width: 150px; }
  #suche { flex: 1; min-width: 200px; display: flex; gap: 8px; }
  #sucheingabe { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 6px; color: var(--text); padding: 7px 12px; font-family: inherit; font-size: 0.82rem; outline: none; }
  #sucheingabe:focus { border-color: var(--akzent-warm); }
  #suchebtn { background: rgba(192,64,0,0.14); border: 1px solid var(--border); color: var(--text); border-radius: 6px; padding: 7px 14px; font-family: inherit; font-size: 0.76rem; cursor: pointer; }
  #modusumschalter { background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text-dim); border-radius: 6px; padding: 7px 12px; font-family: inherit; font-size: 0.76rem; cursor: pointer; white-space: nowrap; transition: background 120ms, color 120ms; }
  #modusumschalter.fragemodus { background: rgba(139,92,246,0.18); border-color: rgba(139,92,246,0.5); color: #c4b5fd; }
  #fragenergebnis { display: none; padding: 14px; font-size: 0.78rem; line-height: 1.5; }
  #fragenergebnis.offen { display: block; }
  #fragenergebnis .fsql { font-family: monospace; font-size: 0.7rem; background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 6px; margin: 6px 0 10px; white-space: pre-wrap; color: var(--text-dim); }
  #fragenergebnis .fdeutung { color: var(--text); margin-bottom: 10px; }
  #fragenergebnis table { width: 100%; border-collapse: collapse; font-size: 0.68rem; }
  #fragenergebnis th, #fragenergebnis td { text-align: left; padding: 4px 6px; border-bottom: 1px solid var(--border); color: var(--text-dim); }
  #fragenladeanzeige { display: none; padding: 14px; font-size: 0.76rem; color: var(--text-faint); }
  #fragenladeanzeige.offen { display: block; }
  #status { font-size: 0.64rem; color: var(--text-faint); white-space: nowrap; }
  #legende { top: 74px; left: 12px; padding: 10px 12px; font-size: 0.66rem; display: flex; flex-direction: column; gap: 4px; max-height: 34vh; overflow-y: auto; }
  .legende-zeile { display: flex; align-items: center; gap: 7px; color: var(--text-dim); }
  .punkt { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  #detail { top: 74px; right: 12px; width: 400px; max-height: 82vh; overflow-y: auto; padding: 18px; display: none; }
  #detail.offen { display: block; }
  #detail .dtitel { font-size: 0.98rem; color: var(--akzent-warm); margin-bottom: 3px; word-break: break-word; }
  #detail .dtyp { font-size: 0.64rem; color: var(--text-faint); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }
  #detail .dstimme { font-size: 0.8rem; line-height: 1.5; color: var(--text); background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 12px; border-left: 2px solid var(--akzent-warm); }
  #detail .dstimme.leer { color: var(--text-faint); font-style: italic; border-left-color: var(--text-faint); }
  #detail .dreihe { display: flex; justify-content: space-between; gap: 10px; font-size: 0.7rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
  #detail .dreihe span:first-child { color: var(--text-faint); flex-shrink: 0; }
  #detail .dreihe span:last-child { text-align: right; word-break: break-word; }
  #detail .dherkunft { margin-top: 10px; font-size: 0.66rem; color: var(--text-dim); background: rgba(255,255,255,0.02); padding: 7px; border-radius: 6px; word-break: break-all; }
  #detail .dnachbarn { margin-top: 12px; font-size: 0.72rem; }
  #detail .dnachbarn a { display: block; color: var(--akzent-kuehl); text-decoration: none; padding: 3px 0; cursor: pointer; }
  #detail .dnachbarn a:hover { text-decoration: underline; }
  #detail .ddateisektion { margin-top: 14px; border-top: 1px solid var(--border); padding-top: 12px; }
  #detail textarea { width: 100%; height: 220px; background: rgba(0,0,0,0.25); border: 1px solid var(--border); color: var(--text); font-family: ui-monospace, monospace; font-size: 0.72rem; padding: 8px; border-radius: 6px; resize: vertical; }
  #detail mark { background: var(--akzent-warm); color: var(--text); }
  .dbtn { background: rgba(139,92,246,0.14); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 5px; font-family: inherit; font-size: 0.68rem; cursor: pointer; margin: 3px 4px 0 0; }
  .dbtn.warn { background: rgba(192,64,0,0.18); }
  .dbtn.danger { background: rgba(220,38,38,0.22); }
  #dchat { margin-top: 12px; border-top: 1px solid var(--border); padding-top: 10px; }
  #dchat input { width: 100%; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--text); padding: 6px 8px; border-radius: 5px; font-family: inherit; font-size: 0.72rem; }
  #dchat .dantwort { margin-top: 8px; font-size: 0.72rem; color: var(--text-dim); background: rgba(139,92,246,0.06); padding: 8px; border-radius: 6px; display: none; }
  #suchergebnisse { top: 74px; left: 12px; width: 380px; max-height: 55vh; overflow-y: auto; display: none; padding: 8px; }
  #fragenergebnis, #fragenladeanzeige { position: absolute; top: 74px; left: 12px; width: 460px; max-height: 65vh; overflow-y: auto; }
  #suchergebnisse.offen { display: block; }
  .treffer { padding: 9px 11px; border-radius: 6px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .treffer:hover { background: rgba(192,64,0,0.08); }
  .treffer .ttitel { font-size: 0.76rem; color: var(--text); margin-bottom: 2px; }
  .treffer .tpfad { font-size: 0.6rem; color: var(--text-faint); word-break: break-all; }
  #zeitstrom-inhalt { position: absolute; inset: 90px 16px 16px 16px; overflow-y: auto; padding: 30px; display: flex; flex-direction: column; gap: 24px; }
  .zeitlinie { position: relative; height: 90px; margin: 20px 0 40px 0; }
  .zeitlinie .schiene { position: absolute; top: 40px; left: 5%; right: 5%; height: 2px; background: linear-gradient(90deg, var(--akzent-kuehl), var(--akzent-warm)); }
  .zeitpunkt { position: absolute; top: 20px; width: 200px; text-align: center; }
  .zeitpunkt .kreis { width: 16px; height: 16px; border-radius: 50%; margin: 0 auto 8px auto; box-shadow: 0 0 20px currentColor; }
  .zeitpunkt .label { font-size: 0.78rem; color: var(--text); }
  .zeitpunkt .sub { font-size: 0.64rem; color: var(--text-faint); margin-top: 3px; }
  .diffkarte { background: rgba(255,255,255,0.055); border: 1px solid rgba(180,170,150,0.30); border-radius: 8px; padding: 16px; }
  .diffkarte h3 { font-size: 0.82rem; color: var(--akzent-kuehl); margin-bottom: 8px; }
  .diffkarte pre { font-size: 0.68rem; color: var(--text-dim); white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; }
  #ladeanzeige { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 14px; z-index: 100; background: var(--bg); }
  #ladeanzeige .kreisel { width: 34px; height: 34px; border: 3px solid rgba(192,64,0,0.2); border-top-color: var(--akzent-warm); border-radius: 50%; animation: dreh 0.9s linear infinite; }
  @keyframes dreh { to { transform: rotate(360deg); } }
  #meldung { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); padding: 10px 18px; border-radius: 8px; font-size: 0.76rem; z-index: 50; display: none; }
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-thumb { background: rgba(192,64,0,0.35); border-radius: 3px; }
  #globus-canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }
  #globus-labels { position:absolute; inset:0; pointer-events:none; overflow:hidden; }
  /* 2026-08-14, auf Daniels Wunsch: erstmal nur die reine Visualisierung zeigen --
     Suche, Legende, Filter, Ergebnis-Panels, Detail-Panel ausgeblendet, nicht
     geloescht. Alles bleibt im Code vorhanden und funktioniert, falls es wieder
     eingeblendet werden soll -- nur CSS, keine strukturelle Aenderung. */
  #filterzeile, #suche, #legende, #suchergebnisse, #fragenladeanzeige,
  #fragenergebnis, #status { display: none !important; }
</style>
</head>
<body>
<div id="ladeanzeige"><div class="kreisel"></div><div style="font-size:0.78rem;color:var(--text-dim);">Nähere mich dem Ursprung...</div></div>
<div id="meldung" class="panel"></div>
<div id="buehne">
  <div id="ansicht-graph" class="ansicht"></div>
  <div id="ansicht-zeitstrom" class="ansicht"><div id="zeitstrom-inhalt"></div></div>
  <div id="ansicht-globus" class="ansicht aktiv"><canvas id="globus-canvas"></canvas><svg id="globus-leitlinien" style="position:absolute; inset:0; pointer-events:none; overflow:visible;"></svg><div id="globus-labels"></div><div id="globus-status" class="panel" style="position:absolute; bottom:12px; left:12px; padding:8px 12px; font-size:0.66rem; color:var(--text-faint);"></div></div>
  <div id="ansicht-ebenen" class="ansicht" style="overflow-y:auto; padding:70px 24px 24px;"><div id="ebenen-inhalt"></div></div>
</div>
<div id="hud">
  <div id="kopf" class="panel">
    <span class="titel">◇ MEGAVAULT</span>
    <span id="wahrheitsindikator" title="lädt..." style="font-size:0.62rem; padding:3px 8px; border-radius:10px; background:rgba(255,255,255,0.06); color:var(--text-faint); margin-left:4px;">●</span>
    <div id="linsen">
      <button id="linse-graph">Graph</button>
      <button id="linse-zeitstrom">Zeitstrom</button>
      <button id="linse-globus" class="aktiv">Globus</button>
      <button id="linse-ebenen">Ebenen</button>
    </div>
    <div id="filterzeile">
      <select id="filterTyp"><option value="">Alle Dateitypen</option></select>
      <select id="filterSystem"><option value="">Alle Systeme</option></select>
    </div>
    <div id="suche">
      <button id="modusumschalter" title="Zwischen Volltextsuche und Frage-an-die-Daten wechseln">🔍 Suchen</button>
      <input id="sucheingabe" placeholder="Suche als Tür in den Raum..." autocomplete="off">
      <button id="suchebtn">Suchen</button>
    </div>
    <span id="status">lädt...</span>
  </div>
  <div id="legende" class="panel"></div>
  <div id="suchergebnisse" class="panel"></div>
  <div id="fragenladeanzeige" class="panel"></div>
  <div id="fragenergebnis" class="panel"></div>
  <div id="detail" class="panel"></div>
</div>

<script src="https://cdn.jsdelivr.net/npm/3d-force-graph"></script>
<script src="https://cdn.jsdelivr.net/npm/globe.gl"></script>
<script type="module">
// Sicherheitsfix 2026-08-13 (Claude Web): statische Importe hier blockierten
// FRUEHER das komplette restliche Skript, wenn beim Laden/Ausfuehren dieser
// Postprocessing-Module irgendetwas schiefging (z.B. Mehrfach-Three.js-
// Instanzen-Konflikt zwischen der in 3d-force-graph gebuendelten Version und
// dieser separat importierten). Die Ladeanzeige blieb dann fuer immer stehen,
// weil der Code, der sie verbirgt, nie erreicht wurde. Jetzt dynamisch und
// fehlertolerant geladen -- Bloom/Vignette/Filmkorn sind eine Verschoenerung,
// kein Kernbestandteil, und duerfen die eigentliche Funktion nie blockieren.

const FARBRING = ['#FF5A1F','#A855F7','#22D3AA','#FACC15','#38BDF8','#F472B6','#4ADE80','#FB923C'];
const BEKANNTE_LABELS = {
  project:'Projekt', session:'Session', file:'Datei', ai_stream:'AI-Strom', service:'Dienst',
  validation:'Validierung', handoff:'Uebergabe', vault:'Vault', claim:'Claim',
  generated_view:'Generierte Ansicht', consensus:'Konsens', conflict:'Konflikt',
  wesen:'Wesen', geni_knoten:'GENI-Knoten', gedanke:'Gedanke', flarum_thread:'Flarum-Thread', schlafphase:'Schlafphase',
  ordner:'Ordner'
};
let COLORS = { default: '#6b7280', ordner: '#94a3b8' };
let LABELS = {};
let fullData = { nodes: [], links: [] };
let fokusKnoten = null; // ueberlebt Linsenwechsel (Daniel, 2026-08-15: "ein Koerper, kein Tabs-Reset")
let letzteSuche = '';

function meldung(text, warn=false) {
  const el = document.getElementById('meldung');
  el.textContent = text;
  el.style.background = warn ? 'rgba(192,64,0,0.9)' : 'rgba(139,92,246,0.9)';
  el.style.display = 'block';
  clearTimeout(window._meldungTimer);
  window._meldungTimer = setTimeout(() => el.style.display = 'none', 4000);
}

function ontologieLernen(nodes) {
  const gesehen = new Set(Object.keys(COLORS));
  [...new Set(nodes.map(n => n.group))].sort().forEach(t => {
    if (!COLORS[t]) COLORS[t] = FARBRING[gesehen.size % FARBRING.length];
    if (!LABELS[t]) LABELS[t] = BEKANNTE_LABELS[t] || t;
    gesehen.add(t);
  });
}
function legendeZeichnen() {
  const el = document.getElementById('legende');
  el.innerHTML = '';
  Object.entries(LABELS).sort((a,b)=>a[1].localeCompare(b[1])).forEach(([k,v]) => {
    const r = document.createElement('div');
    r.className = 'legende-zeile';
    r.innerHTML = `<span class="punkt" style="background:${COLORS[k]||COLORS.default}"></span><span>${v}</span>`;
    el.appendChild(r);
  });
}

async function filterLaden() {
  try {
    const r = await fetch('api/megavault/filters');
    const d = await r.json();
    const st = document.getElementById('filterTyp');
    (d.formats||[]).slice(0,25).forEach(f => {
      const o = document.createElement('option');
      o.value = f.extension; o.textContent = `.${f.extension} (${f.count})`;
      st.appendChild(o);
    });
    const ss = document.getElementById('filterSystem');
    (d.systems||[]).forEach(s => {
      const o = document.createElement('option');
      o.value = s.id; o.textContent = `${s.label} (${s.count})`;
      ss.appendChild(o);
    });
  } catch (e) { meldung('Filter konnten nicht geladen werden.', true); }
}

let hoverNodeId = null;

const Graph = ForceGraph3D()(document.getElementById('ansicht-graph'))
  .backgroundColor('#2F353B')
  .nodeLabel(n => {
    let html = `${n.name} (${LABELS[n.group]||n.group})`;
    if (n.vorschau) html += `<br><span style="opacity:0.75">${n.vorschau}</span>`;
    if (n.geaendert_utc) {
      const d = new Date(n.geaendert_utc);
      html += `<br><span style="opacity:0.55;font-size:0.85em">geändert ${d.toLocaleDateString('de-DE')} · ${(n.groesse_bytes||0).toLocaleString('de-DE')} Bytes</span>`;
    }
    if (n.wer) html += `<br><span style="opacity:0.7;font-size:0.85em">von ${n.wer}</span>`;
    return html;
  })
  .nodeColor(n => n.meta && n.meta.verblasst ? 'rgba(160,160,160,0.35)' : (COLORS[n.group]||COLORS.default))
  .nodeOpacity(n => n.meta && n.meta.verblasst ? 0.35 : 0.92)
  .nodeVal(n => Math.max(1, Math.sqrt(n.degree||1)*1.8))
  .linkColor(() => 'rgba(139,92,246,0.55)')
  .linkWidth(0.6)
  .linkDirectionalParticles(l => (hoverNodeId && (l.source.id===hoverNodeId || l.target.id===hoverNodeId)) ? 2 : 0)
  .linkDirectionalParticleWidth(1.4)
  .linkDirectionalParticleColor(() => '#8B5CF6')
  .linkDirectionalParticleSpeed(0.006)
  // 2026-08-14, auf Daniels Wunsch: Kanten existieren fuer die Kraft-Simulation
  // immer (echte Nachbarschaft bestimmt die Position -- Punkte sind schon von
  // sich aus nah/fern angeordnet), aber SICHTBAR werden nur die Kanten des
  // gerade mit der Maus beruehrten Knotens. So sieht man erst beim Hover, was
  // wirklich verbunden ist, statt permanentem Liniensalat.
  .linkVisibility(l => !!hoverNodeId && (l.source.id===hoverNodeId || l.target.id===hoverNodeId))
  .onNodeHover(n => { hoverNodeId = n ? n.id : null; })
  .onNodeClick(knotenZeigen)
  .onBackgroundClick(() => document.getElementById('detail').classList.remove('offen'))
  .warmupTicks(80)
  .cooldownTicks(60)
  .cooldownTime(4000);

// Begriffsarbeit 2026-08-13 (Claude Web): Bloom/Vignette ueber eine zweite,
// separat importierte Three.js-Instanz erzeugte "Multiple instances of
// Three.js"-Konflikte -- vermutlich mitverantwortlich fuer das blasse
// Erscheinungsbild und ein echtes Absturzrisiko. Bewusst entfernt: Funktion
// vor Deko. Kraeftigere Farben (siehe FARBRING) uebernehmen die sichtbare
// Wirkung stattdessen, ohne die Fragilitaet einer zweiten Three.js-Kopie.

async function subgraphLaden(nodeId) {
  document.getElementById('ladeanzeige').style.display = 'flex';
  try {
    const res = await fetch(`api/megavault/relationships?focus_node_ids=${encodeURIComponent(nodeId)}&include_neighbors=true&limit=80`);
    if (!res.ok) throw new Error('Server antwortete mit ' + res.status);
    const data = await res.json();
    if (!data.ok && data.ok !== undefined) throw new Error(data.error || 'Unbekannter Serverfehler');
    const degree = {};
    (data.edges||[]).forEach(e => {
      degree[e.source_node_id] = (degree[e.source_node_id]||0)+1;
      degree[e.target_node_id] = (degree[e.target_node_id]||0)+1;
    });
    const nodes = (data.nodes||[]).map(n => {
      let meta = {};
      try { meta = JSON.parse(n.metadata_json||'{}'); } catch (e) { meta = {}; }
      return { id: n.node_id, name: n.label||n.identity||n.node_id, group: n.node_type, path: n.path, degree: degree[n.node_id]||0, meta };
    });
    const links = (data.edges||[]).map(e => ({ source: e.source_node_id, target: e.target_node_id, relation: e.relation }));
    fullData = { nodes, links };
    ontologieLernen(nodes); legendeZeichnen();
    Graph.graphData(fullData);
    document.getElementById('status').textContent = `${nodes.length} Knoten · ${links.length} Kanten`;
    const fokus = nodes.find(n => n.id === nodeId);
    if (fokus) { setTimeout(() => Graph.cameraPosition({x:fokus.x||0,y:fokus.y||0,z:(fokus.z||0)+140}, fokus, 900), 300); knotenZeigen(fokus, false); }
  } catch (e) {
    console.error('subgraphLaden Fehler:', e);
    meldung('Laden fehlgeschlagen: ' + e.message, true);
  } finally {
    document.getElementById('ladeanzeige').style.display = 'none';
  }
}

// Sucht in echten metadata_json-Feldern nach lesbarem Text (Gedankeninhalt,
// Frage/Antwort, Beschreibung...) statt nur die rohe node_id/label zu zeigen --
// "menschenlesbar" heisst: man sieht sofort, WAS ein Knoten wirklich enthaelt.
// "Wer" aus dem echten Pfad ableiten -- welches Wesen/welcher Strom die Datei
// angelegt hat, direkt am Verzeichnispraefix erkennbar (dieselbe Zuordnung wie
// im bestehenden file_details-Endpoint, hier fuers Hover dupliziert).
function werAusPfad(pfad) {
  if (!pfad) return null;
  if (pfad.includes('/_gemini')) return 'Gemini';
  if (pfad.includes('/_codex')) return 'Codex';
  if (pfad.includes('/_claude')) return 'Claude';
  if (pfad.includes('/_gpt')) return 'ChatGPT';
  if (pfad.includes('/_kimi')) return 'Kimi';
  if (pfad.includes('/_glm')) return 'GLM';
  if (pfad.includes('/_shared')) return 'Shared';
  if (pfad.includes('/wesen_vaults')) return 'Wesen-Vault';
  return null;
}
function textVorschau(meta) {
  if (!meta || typeof meta !== 'object') return '';
  const felder = ['gedanke', 'inhalt', 'content', 'text', 'beschreibung', 'frage',
                   'antwort', 'begruendung', 'zusammenfassung', 'titel', 'nachricht'];
  for (const f of felder) {
    if (typeof meta[f] === 'string' && meta[f].trim()) {
      const t = meta[f].trim();
      return t.length > 140 ? t.slice(0, 140) + '…' : t;
    }
  }
  return '';
}

async function gesamtGraphLaden() {
  // 2026-08-14, auf Daniels Wunsch: nicht mehr ein einzelnes Projekt fest
  // fokussiert laden, sondern denselben echten, breiten Ausschnitt ueber alle
  // Wesensarten wie der Globus (/api/megavault/globus) -- ein Graph, viele
  // Ordnungen. Reale Kanten treiben die Kraft-Simulation (echte Naehe/Ferne),
  // sichtbar werden Linien erst beim Hover (siehe Graph-Konfiguration oben).
  document.getElementById('ladeanzeige').style.display = 'flex';
  try {
    const res = await fetch('api/megavault/globus');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Unbekannter Serverfehler');

    const degree = {};
    (data.kanten_in_stichprobe||[]).forEach(k => {
      degree[k.source_node_id] = (degree[k.source_node_id]||0)+1;
      degree[k.target_node_id] = (degree[k.target_node_id]||0)+1;
    });

    const nodes = [];
    (data.clusters||[]).forEach(cluster => {
      (cluster.knoten||[]).forEach(k => {
        let meta = {};
        try { meta = JSON.parse(k.metadata_json||'{}'); } catch(e) {}
        nodes.push({
          id: k.node_id, name: k.label||k.node_id, group: k.node_type,
          path: k.path, degree: degree[k.node_id]||0, meta,
          vorschau: textVorschau(meta), wer: werAusPfad(k.path),
          geaendert_utc: k.geaendert_utc, erstellt_utc: k.erstellt_utc, groesse_bytes: k.groesse_bytes,
        });
      });
    });
    const links = (data.kanten_in_stichprobe||[]).map(k => ({
      source: k.source_node_id, target: k.target_node_id, relation: k.relation,
    }));

    // Echte Ordnerstruktur NUR aus den tatsaechlichen Dateipfaden abgeleitet --
    // kein neuer Knotentyp im Register (Knotenvertrag: kein neues Schema),
    // reine Anzeige-Ebene direkt aus echten Pfaden, nichts erfunden/gespeichert.
    const ordnerGesehen = new Map();
    nodes.forEach(n => {
      if (!n.path) return;
      const teile = n.path.split('/').filter(Boolean);
      teile.pop(); // Dateiname weg, Rest sind Ordner
      let vorheriger = null;
      let pfadBisher = '';
      teile.forEach(teil => {
        pfadBisher += '/' + teil;
        const ordnerId = 'ordner:' + pfadBisher;
        if (!ordnerGesehen.has(ordnerId)) {
          ordnerGesehen.set(ordnerId, { id: ordnerId, name: teil, group: 'ordner', path: pfadBisher, degree: 0 });
        }
        if (vorheriger) links.push({ source: vorheriger, target: ordnerId, relation: 'ENTHAELT_ORDNER' });
        vorheriger = ordnerId;
      });
      if (vorheriger) links.push({ source: vorheriger, target: n.id, relation: 'ENTHAELT_DATEI' });
    });
    ordnerGesehen.forEach(o => nodes.push(o));

    fullData = { nodes, links };
    ontologieLernen(nodes); legendeZeichnen();
    Graph.graphData(fullData);
    document.getElementById('status').textContent = `${nodes.length} Knoten (Stichprobe aus ${data.gesamt_knoten.toLocaleString('de-DE')}) · ${links.length} echte Kanten`;
  } catch (e) {
    console.error('gesamtGraphLaden Fehler:', e);
    meldung('Laden fehlgeschlagen: ' + e.message, true);
  } finally {
    document.getElementById('ladeanzeige').style.display = 'none';
  }
}

function feldZeile(label, wert) {
  if (wert === undefined || wert === null || wert === '') return '';
  return `<div class="dreihe"><span>${label}</span><span>${String(wert).slice(0,140)}</span></div>`;
}
function stimmeErmitteln(node) {
  const m = node.meta || {};
  if (node.group === 'gedanke') {
    const text = m.gedanke || m.begruendung || m.thema || '';
    if (text) return { text, leer:false };
    return { text: `Kein erfasster Gedankentext -- nur Handlungstyp: ${m.entscheidung||m.action_prefix||'unbekannt'}`, leer:true };
  }
  if (node.group === 'geni_knoten') return m.inhalt ? { text: m.inhalt, leer:false } : { text:'Kein Inhaltstext erfasst.', leer:true };
  if (node.group === 'wesen') return { text: `Zustand: ${m.zustand||'unbekannt'} -- Herkunft aus ${(m.facets||[]).length} Quellkoerpern.`, leer:false };
  if (node.path) return { text: node.path, leer:false };
  return { text: 'Kein Textinhalt fuer diesen Knotentyp hinterlegt.', leer:true };
}

async function knotenZeigen(node, kameraFliegen=true) {
  fokusKnoten = node; // ueberlebt Linsenwechsel
  document.getElementById('suchergebnisse').classList.remove('offen');
  document.getElementById('detail').classList.add('offen');
  const m = node.meta || {};
  const stimme = stimmeErmitteln(node);
  let html = `<div class="dtitel">${node.name}</div><div class="dtyp">${LABELS[node.group]||node.group}</div>`;
  html += `<div class="dstimme ${stimme.leer?'leer':''}">${stimme.text}</div>`;
  html += feldZeile('Zustand', m.zustand) + feldZeile('Wahrheitsklasse', m.truth_class);
  html += feldZeile('Verblasst', m.verblasst===true?'ja -- Nachhall':(m.verblasst===false?'nein':''));
  html += feldZeile('Zuletzt', m.zuletzt) + feldZeile('Verbindungen', node.degree);
  if (m.source_locator) html += `<div class="dherkunft">Quelle: ${m.source_locator}</div>`;
  if (node.path) html += `<div class="dherkunft">Pfad: ${node.path}</div>`;
  const nachbarn = (fullData.links||[]).filter(l => (l.source.id||l.source)===node.id || (l.target.id||l.target)===node.id).slice(0,10);
  if (nachbarn.length) {
    html += '<div class="dnachbarn"><div style="color:var(--text-faint);font-size:0.66rem;margin-bottom:4px;">Nachbarn</div>';
    nachbarn.forEach(l => {
      const andereId = (l.source.id||l.source)===node.id ? (l.target.id||l.target) : (l.source.id||l.source);
      const andere = fullData.nodes.find(n => n.id===andereId);
      if (andere) html += `<a data-goto="${andereId}">${l.relation} → ${andere.name.slice(0,32)}</a>`;
    });
    html += '</div>';
  }
  if (node.path && node.group === 'ordner') {
    html += `<div class="ddateisektion" id="dordnersektion">
      <div style="font-size:0.7rem;color:var(--text-faint);margin-bottom:6px;">Ordner -- echter Inhalt</div>
      <div id="dordnerladen" style="font-size:0.7rem;color:var(--text-faint);">lädt...</div>
    </div>`;
  } else if (node.path) {
    html += `<div class="ddateisektion" id="ddateisektion">
      <div style="font-size:0.7rem;color:var(--text-faint);margin-bottom:6px;">Datei -- lesen, editieren, löschen</div>
      <div id="ddateiladen" style="font-size:0.7rem;color:var(--text-faint);">lädt Inhalt...</div>
      <textarea id="ddateitext" style="display:none;"></textarea>
      <div id="ddateiaktionen" style="display:none;">
        <button class="dbtn" id="btnSpeichern">Speichern</button>
        <button class="dbtn warn" id="btnSoftDelete">Soft-Delete</button>
        <button class="dbtn danger" id="btnHardDelete">Hard-Delete (endgültig)</button>
        <button class="dbtn" id="btnRestore">Wiederherstellen</button>
      </div>
      <div id="dchat">
        <div style="font-size:0.68rem;color:var(--text-faint);margin-bottom:4px;">Frage zu dieser Datei (bestmöglich, nutzt lokales Modell + Volltextsuche -- keine perfekte Datei-Isolation)</div>
        <input id="dchatEingabe" placeholder="Was steht hier drin bezüglich...?">
        <div class="dantwort" id="dchatAntwort"></div>
      </div>
      <div id="dhistorie" style="margin-top:12px;">
        <div style="font-size:0.68rem;color:var(--text-faint);margin-bottom:4px;">Echte Änderungshistorie (git log)</div>
        <div id="dhistorieInhalt" style="font-size:0.68rem;color:var(--text-faint);">lädt...</div>
      </div>
      <div id="dbacklinks" style="margin-top:12px;">
        <div style="font-size:0.68rem;color:var(--text-faint);margin-bottom:4px;">Wer, Rechte, echte Rückverweise</div>
        <div id="dbacklinksInhalt" style="font-size:0.68rem;color:var(--text-faint);">lädt...</div>
      </div>
    </div>`;
  }
  document.getElementById('detail').innerHTML = html;
  document.getElementById('detail').querySelectorAll('[data-goto]').forEach(a => a.onclick = () => subgraphLaden(a.dataset.goto));
  // Auf Wunsch von Daniel entfernt (2026-08-13): Klick auf einen Knoten soll
  // die Ansicht nicht mehr zentrieren -- man bleibt in derselben Kameraposition.

  if (node.path && node.group === 'ordner') {
    const ordnerEl = document.getElementById('dordnerladen');
    try {
      const r = await fetch('api/megavault/ordner_inhalt?pfad=' + encodeURIComponent(node.path));
      const d = await r.json();
      if (!d.ok) { ordnerEl.textContent = d.grund || 'Fehler'; }
      else {
        ordnerEl.innerHTML = `<div style="margin-bottom:6px;color:var(--text-faint);">${d.anzahl} Einträge</div>` +
          d.eintraege.map(e => `<div style="padding:2px 0;">${e.ist_ordner ? '📁' : '📄'} ${e.name}${e.groesse_bytes!=null ? ' · '+e.groesse_bytes.toLocaleString('de-DE')+' Bytes' : ''}</div>`).join('');
      }
    } catch (e) { ordnerEl.textContent = 'Fehler: ' + e; }
  }

  if (node.path && node.group !== 'ordner') {
    const ladenEl = document.getElementById('ddateiladen');
    const ta = document.getElementById('ddateitext');
    try {
      const r = await fetch('api/megavault/file?pfad=' + encodeURIComponent(node.path));
      if (!r.ok) {
        // Bugfix 2026-08-13 (Claude Web): der Endpunkt liefert bei 404 die
        // komplette HTML-Fehlerseite der Website, kein JSON -- r.json() wuerde
        // hier einen Parse-Fehler werfen, den der alte catch-Block zwar
        // abfing, aber die "laedt Inhalt..."-Anzeige nie aktualisierte.
        // Haeufigster Grund: dieser Knoten ist ein Ordner/Projekt, keine Datei.
        ladenEl.textContent = 'Kein lesbarer Dateiinhalt (HTTP ' + r.status + ') -- vermutlich ein Ordner/Projekt-Knoten, keine einzelne Datei.';
        return;
      }
      const d = await r.json();
      if (!ladenEl) return;
      if (d.ok) {
        let inhalt = d.content || '';
        ladenEl.style.display = 'none';
        ta.style.display = 'block';
        ta.value = inhalt;
        document.getElementById('ddateiaktionen').style.display = 'block';
        if (letzteSuche && inhalt.toLowerCase().includes(letzteSuche.toLowerCase())) {
          const idx = inhalt.toLowerCase().indexOf(letzteSuche.toLowerCase());
          const zeile = inhalt.slice(0, idx).split('\\n').length;
          ladenEl.style.display = 'block';
          ladenEl.textContent = `Fundstelle für "${letzteSuche}" ungefähr in Zeile ${zeile}.`;
          ladenEl.style.color = 'var(--akzent-warm)';
          ta.scrollTop = Math.max(0, (idx / inhalt.length) * ta.scrollHeight - 60);
        }
        document.getElementById('btnSpeichern').onclick = async () => {
          const res = await fetch('api/megavault/file/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pfad: node.path, content: ta.value})});
          const rd = await res.json();
          meldung(rd.ok ? 'Gespeichert -- ' + rd.groesse_bytes + ' Bytes' : 'Fehler beim Speichern: ' + (rd.detail||''), !rd.ok);
        };
        document.getElementById('btnSoftDelete').onclick = async () => {
          if (!confirm('Wirklich soft-löschen (verschiebbar, wiederherstellbar)?')) return;
          const res = await fetch('api/megavault/file/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pfad: node.path, mode:'soft'})});
          const rd = await res.json();
          meldung(rd.ok ? 'Soft-gelöscht' : 'Fehler: ' + (rd.detail||''), !rd.ok);
        };
        document.getElementById('btnHardDelete').onclick = async () => {
          if (!confirm('WIRKLICH ENDGÜLTIG LÖSCHEN? Das kann nicht rückgängig gemacht werden.')) return;
          const res = await fetch('api/megavault/file/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pfad: node.path, mode:'hard'})});
          const rd = await res.json();
          meldung(rd.ok ? 'Endgültig gelöscht' : 'Fehler: ' + (rd.detail||''), !rd.ok);
        };
        document.getElementById('btnRestore').onclick = async () => {
          const res = await fetch('api/megavault/file/restore', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pfad: node.path})});
          const rd = await res.json();
          meldung(rd.ok ? 'Wiederhergestellt' : 'Fehler: ' + (rd.detail||''), !rd.ok);
        };
      } else {
        ladenEl.textContent = 'Datei nicht lesbar: ' + (d.error || 'unbekannter Fehler') + ' (evtl. soft-gelöscht -- Wiederherstellen versuchen)';
        document.getElementById('ddateiaktionen').style.display = 'block';
        document.getElementById('btnRestore').onclick = async () => {
          const res = await fetch('api/megavault/file/restore', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pfad: node.path})});
          const rd = await res.json();
          meldung(rd.ok ? 'Wiederhergestellt, bitte Knoten neu öffnen' : 'Fehler: ' + (rd.detail||''), !rd.ok);
        };
      }
    } catch (e) { meldung('Datei konnte nicht geladen werden.', true); }

    const chatBtn = document.getElementById('dchatEingabe');
    if (chatBtn) chatBtn.addEventListener('keydown', async (e) => {
      if (e.key !== 'Enter') return;
      const frage = chatBtn.value.trim();
      if (!frage) return;
      const antwortEl = document.getElementById('dchatAntwort');
      antwortEl.style.display = 'block';
      antwortEl.textContent = 'frage...';
      try {
        const r = await fetch('api/megavault/ask?q=' + encodeURIComponent(frage + ' (bezogen auf ' + node.path.split('/').pop() + ')') + '&limit=5');
        const d = await r.json();
        antwortEl.textContent = d.answer || 'keine Antwort erhalten.';
      } catch (e) { antwortEl.textContent = 'Fehler bei der Anfrage.'; }
    });
  }

  if (node.path && node.group !== 'ordner') {
    const histEl = document.getElementById('dhistorieInhalt');
    try {
      const rh = await fetch('api/megavault/datei_historie?pfad=' + encodeURIComponent(node.path));
      const dh = await rh.json();
      if (!dh.ok) { histEl.textContent = dh.grund || 'keine Historie verfügbar'; }
      else if (!dh.commits.length) { histEl.textContent = 'noch keine Commits für diese Datei'; }
      else {
        histEl.innerHTML = dh.commits.map(c =>
          `<div style="margin-bottom:4px;"><span style="color:var(--akzent-warm);">${c.hash}</span> · ${new Date(c.datum).toLocaleDateString('de-DE')} · ${c.nachricht.slice(0,60)}</div>`
        ).join('');
      }
    } catch (e) { if (histEl) histEl.textContent = 'Fehler: ' + e; }
  }

  if (node.path && node.group !== 'ordner') {
    const blEl = document.getElementById('dbacklinksInhalt');
    try {
      const rb = await fetch('api/megavault/file_details?pfad=' + encodeURIComponent(node.path));
      let db;
      try { db = await rb.json(); } catch (e) { blEl.textContent = 'Datei im Register verzeichnet, aber auf der Platte nicht (mehr) auffindbar -- echte Lücke, keine Fantasiedaten.'; return; }
      if (!db.ok) { blEl.textContent = db.error || 'keine Details verfügbar'; }
      else {
        let html = `<div>Wer: ${db.stream_name || db.stream || '?'} · Rechte: ${db.permissions || '?'} · BM25-indiziert: ${db.bm25_indexed ? 'ja' : 'nein'}</div>`;
        const refs = db.referenzen || [];
        if (refs.length) {
          html += `<div style="margin-top:6px;color:var(--text-faint);">${refs.length} Datei(en) verweisen hierher:</div>`;
          html += refs.slice(0, 8).map(r => `<div style="padding:1px 0;">→ ${r.titel || r.relativ}</div>`).join('');
        } else {
          html += `<div style="margin-top:6px;color:var(--text-faint);">keine bekannten Rückverweise</div>`;
        }
        blEl.innerHTML = html;
      }
    } catch (e) { if (blEl) blEl.textContent = 'Fehler: ' + e; }
  }
}

async function suche() {
  const q = document.getElementById('sucheingabe').value.trim();
  if (!q) return;
  letzteSuche = q;
  const typ = document.getElementById('filterTyp').value;
  const stream = document.getElementById('filterSystem').value;
  let url = 'api/megavault/search?q=' + encodeURIComponent(q) + '&limit=20';
  if (typ) url += '&typ=' + encodeURIComponent(typ);
  if (stream) url += '&stream=' + encodeURIComponent(stream);
  const res = await fetch(url);
  const data = await res.json();
  if (fragemodusAktiv) return;  // Nutzer ist inzwischen in den Fragemodus gewechselt -- alte Suchantwort verwerfen
  const box = document.getElementById('suchergebnisse');
  box.classList.add('offen');
  box.innerHTML = (data.results||[]).map(r => `<div class="treffer" data-pfad="${(r.pfad||'').replace(/"/g,'&quot;')}" data-nodeid="${r.node_id||''}" data-titel="${(r.titel||'').replace(/"/g,'&quot;')}"><div class="ttitel">${(r.titel||'').replace(/</g,'&lt;')}</div><div class="tpfad">${(r.pfad||'').replace(/</g,'&lt;')}</div></div>`).join('') || '<div style="padding:12px;color:var(--text-faint);font-size:0.75rem;">Kein Treffer -- echter Nullbefund.</div>';
  box.querySelectorAll('.treffer').forEach(el => {
    el.onclick = async () => {
      const pfad = el.dataset.pfad;
      const nodeId = el.dataset.nodeid;
      box.classList.remove('offen');
      // Bevorzugt: der bereits geladene Knoten (volle Daten, Nachbarn etc.)
      const geladen = fullData.nodes.find(n => n.path === pfad || (nodeId && n.id === nodeId));
      if (geladen) { await knotenZeigen(geladen, false); return; }
      // Sonst: node_id kommt jetzt direkt vom Suchtreffer (2026-08-15-Bruecke)
      // -- kein Register-Nachschlagen mehr per Dateiname noetig.
      if (nodeId) {
        await knotenZeigen({ id: nodeId, name: el.dataset.titel || pfad.split('/').pop(), group: 'file', path: pfad, degree: 0, meta: {} }, false);
      } else {
        meldung('Treffer liegt außerhalb des Beziehungsgraphen -- kein eigener Knoten.', true);
      }
    };
  });
}
let fragemodusAktiv = false;
const umschalterBtn = document.getElementById('modusumschalter');
const sucheingabeEl = document.getElementById('sucheingabe');
const suchebtnEl = document.getElementById('suchebtn');

umschalterBtn.onclick = () => {
  fragemodusAktiv = !fragemodusAktiv;
  umschalterBtn.classList.toggle('fragemodus', fragemodusAktiv);
  umschalterBtn.textContent = fragemodusAktiv ? '💬 Fragen' : '🔍 Suchen';
  sucheingabeEl.placeholder = fragemodusAktiv
    ? 'Frage in normaler Sprache an die echten Daten...'
    : 'Suche als Tür in den Raum...';
  suchebtnEl.textContent = fragemodusAktiv ? 'Fragen' : 'Suchen';
  document.getElementById('suchergebnisse').classList.remove('offen');
  document.getElementById('fragenergebnis').classList.remove('offen');
  document.getElementById('fragenladeanzeige').classList.remove('offen');
};

async function frageStellen() {
  const frage = sucheingabeEl.value.trim();
  if (!frage) return;
  const ladeEl = document.getElementById('fragenladeanzeige');
  const ergEl = document.getElementById('fragenergebnis');
  ergEl.classList.remove('offen');
  ladeEl.classList.add('offen');
  ladeEl.textContent = 'Modell baut eine echte Abfrage und führt sie aus -- kann bis zu ein paar Minuten dauern...';
  let daten;
  try {
    const res = await fetch('api/megavault/frage', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ frage }),
    });
    daten = await res.json();
  } catch (e) {
    ladeEl.classList.remove('offen');
    ergEl.classList.add('offen');
    ergEl.innerHTML = `<div class="fdeutung">Fehler beim Verbinden: ${e}</div>`;
    return;
  }
  if (!fragemodusAktiv) { ladeEl.classList.remove('offen'); return; }  // Nutzer ist zurueck in den Suchmodus -- alte Antwort verwerfen
  ladeEl.classList.remove('offen');
  ergEl.classList.add('offen');

  if (daten.fehler) {
    ergEl.innerHTML = `<div class="fdeutung">${(daten.fehler||'').replace(/</g,'&lt;')}</div>`
      + (daten.versuche && daten.versuche.length
          ? `<div class="fsql">${daten.versuche.map(v => (v.sql||'') + '\\n-- ' + (v.fehler||'')).join('\\n\\n').replace(/</g,'&lt;')}</div>`
          : '');
    return;
  }

  let html = `<div class="fsql">${(daten.sql||'').replace(/</g,'&lt;')}</div>`;
  html += `<div class="fdeutung">${(daten.deutung||'').replace(/</g,'&lt;')}</div>`;
  const zeilen = daten.zeilen || [];
  if (zeilen.length) {
    const spalten = Object.keys(zeilen[0]);
    html += '<table><thead><tr>' + spalten.map(s => `<th>${s}</th>`).join('') + '</tr></thead><tbody>';
    zeilen.slice(0, 50).forEach(z => {
      html += '<tr>' + spalten.map(s => `<td>${String(z[s] ?? '').slice(0,80).replace(/</g,'&lt;')}</td>`).join('') + '</tr>';
    });
    html += '</tbody></table>';
    if (zeilen.length > 50) html += `<div style="padding:6px;color:var(--text-faint);">... ${zeilen.length - 50} weitere Zeilen, nicht angezeigt</div>`;
  }
  ergEl.innerHTML = html;
}

// suchebtn/Enter routen jetzt je nach Modus um
suchebtnEl.onclick = () => fragemodusAktiv ? frageStellen() : suche();
sucheingabeEl.addEventListener('keydown', e => {
  if (e.key === 'Enter') { fragemodusAktiv ? frageStellen() : suche(); }
});

let zeitstromGeladen = false;
async function zeitstromLaden() {
  if (zeitstromGeladen) return;
  const inhaltEl = document.getElementById('zeitstrom-inhalt');
  try {
    const [truthRes, versionsRes] = await Promise.all([fetch('api/truth'), fetch('api/versions')]);
    if (!truthRes.ok) throw new Error('api/truth antwortete mit ' + truthRes.status);
    if (!versionsRes.ok) throw new Error('api/versions antwortete mit ' + versionsRes.status);
    const truth = await truthRes.json();
    const versions = await versionsRes.json();
    if (!truth.baseline || !truth.live) throw new Error('api/truth lieferte unerwartete Form (kein baseline/live)');
    zeitstromRendern(truth, versions);
    zeitstromGeladen = true;
  } catch (e) {
    console.error('Zeitstrom Fehler:', e);
    inhaltEl.innerHTML = `<div class="diffkarte"><h3>Zeitstrom konnte nicht geladen werden</h3><p style="font-size:0.76rem;color:var(--text-dim);">${e.message}</p></div>`;
    meldung('Zeitstrom fehlgeschlagen: ' + e.message, true);
  }
}

function zeitstromRendern(truth, versions) {
  const b = truth.baseline, l = truth.live;
  const distanz = l.revision_distance;
  let html = `<div class="zeitlinie">
    <div class="schiene"></div>
    <div class="zeitpunkt" style="left:5%;color:var(--akzent-kuehl);">
      <div class="kreis" style="background:var(--akzent-kuehl);"></div>
      <div class="label">Baseline r${b.revision}</div>
      <div class="sub">${b.verification_check_count} Checks, alle bestanden</div>
    </div>
    <div class="zeitpunkt" style="left:${5+90*Math.min(1,distanz/Math.max(distanz,20))}%;color:var(--akzent-warm);">
      <div class="kreis" style="background:var(--akzent-warm);"></div>
      <div class="label">Live r${l.revision}</div>
      <div class="sub">${distanz} Revisionen später, ${l.publication_mode}${l.dirty?'/dirty':''}</div>
    </div>
  </div>
  <div class="diffkarte"><h3>Baseline-Hash</h3><pre>${b.sha256}</pre></div>
  <div class="diffkarte"><h3>Live-Hash</h3><pre>${l.sha256}</pre></div>`;
  (versions.comparisons||[]).forEach((c,i) => {
    html += `<div class="diffkarte"><h3>${c.from_id} → ${c.to_id}</h3><p style="font-size:0.76rem;color:var(--text-dim);">${c.changed?('Verändert -- '+c.diff_line_count+' Diffzeilen'):'Bytegleich -- keine Veränderung'}</p>`;
    if (c.changed) html += `<button class="diffaufklappen" data-i="${i}" style="margin-top:8px;background:rgba(139,92,246,0.12);border:1px solid var(--border);color:var(--text-dim);padding:6px 10px;border-radius:5px;font-family:inherit;font-size:0.7rem;cursor:pointer;">Rohen Diff zeigen</button><pre data-diff="${i}" style="display:none;margin-top:8px;">${(c.diff_excerpt||'').replace(/</g,'&lt;').slice(0,1500)}</pre>`;
    html += `</div>`;
  });
  document.getElementById('zeitstrom-inhalt').innerHTML = html;
  document.querySelectorAll('.diffaufklappen').forEach(btn => {
    btn.onclick = () => {
      const pre = document.querySelector(`pre[data-diff="${btn.dataset.i}"]`);
      pre.style.display = pre.style.display === 'none' ? 'block' : 'none';
    };
  });
  zeitstromGeladen = true;
}


let globusGeladen = false;
let globusState = null;

let ebenenGeladen = false;

function graphFokusAnwenden(node) {
  // Denselben Knoten im gerade geladenen Graph-Datensatz wiederfinden und die
  // Kamera dorthin bewegen -- nur wenn er in dieser Stichprobe ueberhaupt
  // vorkommt (Globus/Graph laden unabhaengige Zufallsstichproben, kein
  // Garantie-Treffer, das wird ehrlich uebersprungen statt erzwungen).
  if (!window.Graph) return;
  const treffer = (window.Graph.graphData().nodes || []).find(n => n.id === node.id);
  if (!treffer || treffer.x == null) return;
  const abstand = 80;
  const verhaeltnis = 1 + abstand / Math.hypot(treffer.x, treffer.y, treffer.z || 1);
  window.Graph.cameraPosition(
    { x: treffer.x * verhaeltnis, y: treffer.y * verhaeltnis, z: (treffer.z || 0) * verhaeltnis },
    treffer, 1000
  );
}

function globusFokusAnwenden(node) {
  if (!globusState || !globusState.globus) return;
  const punkte = globusState.globus.pointsData() || [];
  const treffer = punkte.find(p => p.knoten && p.knoten.node_id === node.id);
  if (!treffer) return;
  globusState.globus.pointOfView({ lat: treffer.lat, lng: treffer.lng, altitude: 1.4 }, 1000);
}

async function ebenenLaden() {
  if (ebenenGeladen) return;
  ebenenGeladen = true;
  const el = document.getElementById('ebenen-inhalt');
  el.innerHTML = '<div style="color:var(--text-faint);font-size:0.78rem;">lädt echte Ebenen-Zuordnung...</div>';
  let daten;
  try {
    const r = await fetch('api/megavault/ebenen');
    daten = await r.json();
  } catch (e) { el.innerHTML = 'Fehler: ' + e; return; }
  if (!daten.ok) { el.innerHTML = daten.error || 'Fehler'; return; }

  const maxGesamt = Math.max(...daten.ebenen.map(e => e.gesamt));
  let html = `<div style="color:var(--text-faint);font-size:0.72rem;margin-bottom:16px;">
    6-Schichten-Modell (Gemini, 2026-07-31) -- Zuordnung von ChatGPT gegen die echten node_types geprüft, 2026-08-15.
    ${daten.gesamt_knoten.toLocaleString('de-DE')} Knoten gesamt · ${daten.gesamt_kanten.toLocaleString('de-DE')} Kanten gesamt.
  </div>`;

  // Von Ebene 6 (unten, Fundament) nach Ebene 1 (oben) stapeln -- Breite
  // proportional zur echten Knotenzahl (log-skaliert, sonst verschwinden die
  // kleinen Ebenen neben GENI/Gedanken komplett).
  [...daten.ebenen].reverse().forEach(eb => {
    const breite = 12 + Math.round(88 * Math.log10(eb.gesamt + 1) / Math.log10(maxGesamt + 1));
    const farbe = FARBRING[(eb.nr - 1) % FARBRING.length];
    html += `<div class="ebenen-band" data-nr="${eb.nr}" style="margin-bottom:10px; cursor:pointer;">
      <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:4px;">
        <span style="color:${farbe}; font-weight:600; font-size:0.82rem;">Ebene ${eb.nr} -- ${eb.label}</span>
        <span style="color:var(--text-faint); font-size:0.68rem;">${eb.gesamt.toLocaleString('de-DE')} Knoten · ${eb.node_types.join(', ')}</span>
      </div>
      <div style="width:${breite}%; min-width:120px; height:34px; border-radius:6px; background:${farbe}22; border:1px solid ${farbe}55; display:flex; align-items:center; gap:3px; padding:0 8px; overflow:hidden;">
        ${eb.cluster.map(c => `<span title="${c.label} · ${c.gesamt.toLocaleString('de-DE')}" style="width:6px;height:6px;border-radius:50%;background:${c.farbe};flex-shrink:0;"></span>`).join('').slice(0, 4000)}
      </div>
    </div>`;
  });
  el.innerHTML = html;
  el.querySelectorAll('.ebenen-band').forEach(band => {
    band.onclick = () => {
      const eb = daten.ebenen.find(e => e.nr == band.dataset.nr);
      alert(`Ebene ${eb.nr} -- ${eb.label}\n${eb.gesamt.toLocaleString('de-DE')} Knoten\nTypen: ${eb.node_types.join(', ')}`);
    };
  });
}

async function globusLaden() {
  if (globusGeladen) return;
  globusGeladen = true;
  const statusEl = document.getElementById('globus-status');
  statusEl.textContent = 'Lade Cluster-Daten...';
  let daten;
  try {
    const r = await fetch('api/megavault/globus');
    daten = await r.json();
  } catch (e) {
    statusEl.textContent = 'Fehler beim Laden: ' + e;
    return;
  }
  if (!daten.ok) {
    statusEl.textContent = 'Fehler: ' + (daten.error || 'unbekannt');
    return;
  }
  statusEl.textContent = `${daten.gesamt_knoten.toLocaleString('de-DE')} Knoten gesamt · ${daten.gesamt_kanten.toLocaleString('de-DE')} Kanten gesamt · Stichprobe pro Cluster sichtbar`;
  globusRendern(daten);
}

function globusLegendeZeichnen(daten) {
  const el = document.getElementById('legende');
  el.innerHTML = '';
  daten.clusters.forEach(c => {
    const r = document.createElement('div');
    r.className = 'legende-zeile';
    r.innerHTML = `<span class="punkt" style="background:${c.farbe}"></span><span>${c.label} · ${c.gesamt.toLocaleString('de-DE')}</span>`;
    el.appendChild(r);
  });
}

// Fibonacci-Sphere direkt in lat/lng (Grad) statt XYZ -- globe.gl arbeitet
// nativ mit geografischen Koordinaten, das spart die Umrechnung.
function fibonacciClusterZentrum(index, anzahl) {
  const y = 1 - (index / Math.max(anzahl - 1, 1)) * 2;
  const lat = Math.asin(Math.max(-1, Math.min(1, y))) * 180 / Math.PI;
  const golden = Math.PI * (3 - Math.sqrt(5));
  const theta = golden * index;
  let lng = (theta * 180 / Math.PI) % 360;
  if (lng > 180) lng -= 360;
  if (lng < -180) lng += 360;
  return { lat, lng };
}

let globusKollisionsLoopAktiv = false;
function labelKollisionsSchleifeStarten(clusterLabels) {
  // Eigene, von globe.gl unabhaengige rAF-Schleife: liest die tatsaechliche
  // Bildschirmposition jedes Labels (die globe.gl schon gesetzt hat) aus und
  // verschiebt bei Ueberlappung nur den INNEREN div zusaetzlich per transform --
  // die aeussere, von globe.gl verwaltete Positionierung bleibt unangetastet.
  if (globusKollisionsLoopAktiv) return;  // nur eine Schleife gleichzeitig
  globusKollisionsLoopAktiv = true;

  function schritt() {
    if (!document.getElementById('ansicht-globus').classList.contains('aktiv')) {
      globusKollisionsLoopAktiv = false;
      return;  // Tab verlassen -- Schleife sauber beenden statt im Hintergrund weiterzulaufen
    }
    const sichtbar = [];
    clusterLabels.forEach(d => {
      if (!d._aussenEl || !d._innenEl) return;
      const rect = d._aussenEl.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) return;  // von globe.gl ausgeblendet (Rueckseite)
      sichtbar.push({ d, left: rect.left, top: rect.top, b: rect.width || 90, h: rect.height || 16, dx: 0, dy: 0 });
    });

    const rand = 4;
    for (let iteration = 0; iteration < 5; iteration++) {
      let ueberlappung = false;
      for (let i = 0; i < sichtbar.length; i++) {
        for (let j = i + 1; j < sichtbar.length; j++) {
          const a = sichtbar[i], b = sichtbar[j];
          const aL = a.left + a.dx, aT = a.top + a.dy, bL = b.left + b.dx, bT = b.top + b.dy;
          const ueberX = Math.min(aL + a.b, bL + b.b) - Math.max(aL, bL);
          const ueberY = Math.min(aT + a.h, bT + b.h) - Math.max(aT, bT);
          if (ueberX > -rand && ueberY > -rand) {
            ueberlappung = true;
            const verschiebung = (ueberY + rand) / 2 + 1;
            if (aT <= bT) { a.dy -= verschiebung; b.dy += verschiebung; }
            else { a.dy += verschiebung; b.dy -= verschiebung; }
          }
        }
      }
      if (!ueberlappung) break;
    }
    sichtbar.forEach(s => {
      s.d._innenEl.style.transform = `translate(${s.dx}px, ${s.dy}px)`;
    });

    requestAnimationFrame(schritt);
  }
  requestAnimationFrame(schritt);
}

function globusRendern(daten) {
  const container = document.getElementById('ansicht-globus');
  const breite = container.clientWidth, hoehe = container.clientHeight;

  globusLegendeZeichnen(daten);

  const anzahlCluster = daten.clusters.length;
  const punkte = [];
  const nodeIdZuCoord = {};
  const clusterLabels = [];

  daten.clusters.forEach((cluster, ci) => {
    const zentrum = fibonacciClusterZentrum(ci, anzahlCluster);
    // Streuradius in Grad: groessere Cluster (mehr Knoten, hoehere Gesamtzahl)
    // bekommen eine sichtbar groessere Flaeche -- echte Groessenordnung, keine
    // gleichgrossen Punktwolken fuer 3 vs. 772.369 Knoten.
    const streuungGrad = 4 + Math.min(9, Math.log10(cluster.gesamt + 1) * 2.1);

    cluster.knoten.forEach(knoten => {
      const dLat = (Math.random() - 0.5) * 2 * streuungGrad;
      const dLng = (Math.random() - 0.5) * 2 * streuungGrad;
      const lat = Math.max(-89, Math.min(89, zentrum.lat + dLat));
      const lng = ((zentrum.lng + dLng + 540) % 360) - 180;
      const p = { lat, lng, farbe: cluster.farbe, knoten };
      punkte.push(p);
      nodeIdZuCoord[knoten.node_id] = { lat, lng };
    });

    clusterLabels.push({
      lat: zentrum.lat, lng: zentrum.lng,
      label: cluster.label, gesamt: cluster.gesamt, farbe: cluster.farbe,
    });
  });

  const bogen = (daten.kanten_in_stichprobe || [])
    .map(k => {
      const a = nodeIdZuCoord[k.source_node_id], b = nodeIdZuCoord[k.target_node_id];
      if (!a || !b) return null;
      return { startLat: a.lat, startLng: a.lng, endLat: b.lat, endLng: b.lng };
    })
    .filter(Boolean);

  const globus = Globe()(container)
    .width(breite)
    .height(hoehe)
    .backgroundColor('rgba(0,0,0,0)')
    .globeImageUrl(null)
    .showGlobe(true)
    .showAtmosphere(true)
    .atmosphereColor('#5b9bd9')
    .atmosphereAltitude(0.22)
    .pointsData(punkte)
    .pointLat('lat')
    .pointLng('lng')
    .pointColor('farbe')
    .pointAltitude(0.005)
    .pointRadius(0.28)
    .pointResolution(6)
    .onPointClick(p => {
      if (!p.knoten) return;
      knotenZeigen({
        id: p.knoten.node_id,
        name: p.knoten.label || p.knoten.path || p.knoten.node_id,
        group: p.knoten.node_type,
        meta: {},
        degree: '?',
        path: p.knoten.path,
      }, false);
    })
    .pointsMerge(false)
    .arcsData(bogen)
    .arcColor(() => 'rgba(255,255,255,0.18)')
    .arcStroke(0.15)
    .arcAltitudeAutoScale(0.25)
    .arcsTransitionDuration(0)
    .htmlElementsData(clusterLabels)
    .htmlLat('lat')
    .htmlLng('lng')
    .htmlAltitude(0.015)
    .htmlElement(d => {
      // Aeusserer div wird von globe.gl per CSS2DRenderer positioniert (nicht
      // anfassen). Der innere div bekommt zusaetzlich unsere eigene Kollisions-
      // korrektur per transform, unabhaengig von globe.gl's eigener Positionierung.
      const aussen = document.createElement('div');
      const innen = document.createElement('div');
      innen.style.cssText = 'display:flex; align-items:center; gap:5px; pointer-events:none; white-space:nowrap; transition: transform 90ms ease-out;';
      innen.innerHTML = `<span style="width:6px;height:6px;border-radius:50%;background:${d.farbe};box-shadow:0 0 5px ${d.farbe};display:inline-block;flex-shrink:0;"></span>`
        + `<span style="font-size:0.72rem; font-weight:600; color:${d.farbe}; text-shadow:0 0 6px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9);">${d.label} · ${d.gesamt.toLocaleString('de-DE')}</span>`;
      aussen.appendChild(innen);
      d._aussenEl = aussen; d._innenEl = innen;
      return aussen;
    });

  labelKollisionsSchleifeStarten(clusterLabels);

  // Kein Foto-Globus (kein globeImageUrl): eigenes, dunkles Kugelmaterial,
  // damit die Kugel trotzdem als koerperhafte Flaeche und nicht als leeres
  // Drahtgitter wirkt. globe.gl exponiert THREE global -- defensiv geprueft,
  // falls sich das je aendert, faellt es auf das Standardmaterial zurueck.
  if (typeof THREE !== 'undefined') {
    globus.globeMaterial().color = new THREE.Color(0x12151a);
    globus.globeMaterial().transparent = true;
    globus.globeMaterial().opacity = 0.94;
  }

  globus.controls().autoRotate = false;
  globus.pointOfView({ lat: 15, lng: 20, altitude: 2.35 }, 0);

  window.addEventListener('resize', () => {
    if (!document.getElementById('ansicht-globus').classList.contains('aktiv')) return;
    globus.width(container.clientWidth).height(container.clientHeight);
  });

  globusState = { globus };
}


let graphGeladen = false;
function linseWechseln(name) {
  document.querySelectorAll('.ansicht').forEach(a => a.classList.remove('aktiv'));
  document.getElementById('ansicht-' + name).classList.add('aktiv');
  document.querySelectorAll('#linsen button').forEach(b => b.classList.remove('aktiv'));
  document.getElementById('linse-' + name).classList.add('aktiv');
  // Detail-Panel bleibt beim Linsenwechsel bewusst offen (2026-08-15, Daniels
  // Vorgabe "ein Körper, kein Tabs-Reset") -- nur die Suchergebnis-Liste ist
  // suchspezifisch und schliesst sich.
  document.getElementById('suchergebnisse').classList.remove('offen');
  if (name === 'zeitstrom') { legendeZeichnen(); zeitstromLaden(); }
  if (name === 'globus') { globusLaden(); if (fokusKnoten) globusFokusAnwenden(fokusKnoten); }
  if (name === 'graph') { legendeZeichnen(); if (!graphGeladen) { graphGeladen = true; gesamtGraphLaden(); } if (fokusKnoten) graphFokusAnwenden(fokusKnoten); }
  if (name === 'ebenen') ebenenLaden();
}
document.getElementById('linse-graph').onclick = () => linseWechseln('graph');
document.getElementById('linse-zeitstrom').onclick = () => linseWechseln('zeitstrom');
document.getElementById('linse-globus').onclick = () => linseWechseln('globus');
document.getElementById('linse-ebenen').onclick = () => linseWechseln('ebenen');

filterLaden();
window.Graph = Graph; window.knotenZeigen = knotenZeigen; window.suche = suche; // fuer Debug/Tests von aussen erreichbar
globusLaden(); // Globus ist jetzt Standardansicht (Daniels Vorgabe 2026-08-15)

(async () => {
  const el = document.getElementById('wahrheitsindikator');
  try {
    const r = await fetch('api/truth');
    const d = await r.json();
    const rev = d.baseline && d.baseline.revision;
    el.textContent = '● verifiziert' + (rev ? ' · r' + rev : '');
    el.style.color = '#4ADE80';
    el.title = 'world_model: ' + (d.world_model || '?') + (d.pointer && d.pointer.sha256 ? ' -- sha256: ' + d.pointer.sha256.slice(0,16) + '…' : '');
  } catch (e) {
    el.textContent = '● unbekannt';
    el.title = 'Wahrheitsstatus nicht erreichbar: ' + e;
  }
})();
</script>
</body>
</html>"""
    return HTMLResponse(html)


@app.get(f"{BASE}/megasuche/", response_class=HTMLResponse, include_in_schema=False)
def megasuche_page(q: str = Query("", max_length=300), facet: str = Query("all")):
    safe_q = esc(q)
    safe_facet = esc(facet)
    
    html = f'''<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MEGASUCHE & MEGAVAULT - VPS-Baum & Live-Gedächtnis</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090c15;
      --surface: #111625;
      --surface-card: #161c2e;
      --surface-hover: #1e263d;
      --border: rgba(255, 255, 255, 0.08);
      --border-bright: rgba(139, 92, 246, 0.3);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #8b5cf6;
      --primary-hover: #7c3aed;
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
      --cyan: #06b6d4;
      --violet: #a855f7;
      --radius: 12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      line-height: 1.5;
    }}

    header {{
      background: rgba(15, 21, 37, 0.9);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 14px 24px;
    }}
    .header-container {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-icon {{
      background: linear-gradient(135deg, var(--primary), var(--cyan));
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: grid;
      place-items: center;
      font-weight: 700;
      font-size: 1.2rem;
      color: #fff;
      box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
    }}
    .logo-title {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(90deg, #fff, #c084fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .header-stats {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    .stat-pill {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .stat-pill strong {{ color: #fff; }}

    main {{
      max-width: 1400px;
      margin: 24px auto;
      padding: 0 24px;
    }}

    /* Main View Switcher */
    .view-switcher {{
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }}
    .mode-btn {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 12px 24px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .mode-btn:hover {{
      background: var(--surface-hover);
      color: #fff;
    }}
    .mode-btn.active {{
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(6, 182, 212, 0.15));
      border-color: var(--primary);
      color: #fff;
      box-shadow: 0 0 15px rgba(139, 92, 246, 0.2);
    }}

    /* Stream Filters */
    .filter-bar {{
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .filter-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-right: 4px;
    }}
    .stream-pill {{
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .stream-pill:hover, .stream-pill.active {{
      background: rgba(139, 92, 246, 0.2);
      border-color: var(--primary);
      color: #fff;
    }}

    /* Search Box */
    .search-section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px 24px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
      margin-bottom: 24px;
    }}
    .input-wrapper {{
      display: flex;
      gap: 12px;
    }}
    .search-input {{
      width: 100%;
      background: rgba(0,0,0,0.4);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 14px 18px;
      font-size: 1.05rem;
      color: var(--text);
      outline: none;
      transition: all 0.2s ease;
      font-family: inherit;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25);
    }}
    .btn-search {{
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      color: #fff;
      border: none;
      border-radius: var(--radius);
      padding: 0 26px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
      box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }}
    .btn-search:hover {{ opacity: 0.9; transform: translateY(-1px); }}

    /* Quick Jump Bar */
    .quick-jump {{
      display: flex;
      gap: 8px;
      margin-top: 14px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .quick-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-right: 4px;
    }}
    .quick-pill {{
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: 'JetBrains Mono', monospace;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .quick-pill:hover {{
      background: var(--surface-hover);
      color: #fff;
      border-color: var(--border-bright);
    }}

    /* Tree View Section */
    .tree-container {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
    }}
    .tree-breadcrumbs {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.9rem;
      color: var(--cyan);
      background: rgba(0,0,0,0.4);
      padding: 10px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
      overflow-x: auto;
    }}
    .crumb {{
      cursor: pointer;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .crumb:hover {{
      background: rgba(255,255,255,0.1);
      color: #fff;
    }}
    .crumb-sep {{ color: var(--text-muted); }}

    .tree-list {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .tree-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      border-radius: 8px;
      background: rgba(255,255,255,0.01);
      border: 1px solid transparent;
      transition: all 0.15s;
      cursor: pointer;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88rem;
    }}
    .tree-item:hover {{
      background: var(--surface-hover);
      border-color: var(--border);
    }}
    .item-left {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .item-icon {{ font-size: 1.1rem; }}
    .item-name {{ color: #fff; font-weight: 500; }}
    .item-meta {{
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      gap: 12px;
      align-items: center;
    }}

    /* Stream Badges */
    .stream-tag {{
      font-size: 0.72rem;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .st-gemini {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }}
    .st-codex {{ background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }}
    .st-claude {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .st-chatgpt {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .st-kimi {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
    .st-shared {{ background: rgba(168, 85, 247, 0.15); color: #e879f9; border: 1px solid rgba(168, 85, 247, 0.3); }}
    .st-system {{ background: rgba(156, 163, 175, 0.15); color: #d1d5db; border: 1px solid rgba(156, 163, 175, 0.3); }}

    /* Ext Badges */
    .ext-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .ext-exact {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); }}
    .ext-py {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
    .ext-md {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .ext-json {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .ext-other {{ background: rgba(156, 163, 175, 0.15); color: #d1d5db; border: 1px solid rgba(156, 163, 175, 0.3); }}

    /* Search Results Section */
    .results-grid {{
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .result-card {{
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px 22px;
      transition: all 0.2s ease;
    }}
    .result-card:hover {{
      border-color: var(--border-bright);
      box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }}
    .card-title {{
      font-size: 1.05rem;
      font-weight: 600;
      color: #fff;
    }}
    .card-path {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      color: var(--cyan);
      margin-bottom: 10px;
      word-break: break-all;
    }}
    .card-snippet {{
      font-size: 0.92rem;
      color: #d1d5db;
      line-height: 1.5;
      background: rgba(0,0,0,0.3);
      padding: 12px 16px;
      border-radius: 8px;
      border-left: 3px solid var(--primary);
      margin-bottom: 12px;
    }}
    .card-actions {{
      display: flex;
      gap: 10px;
    }}
    .btn-action {{
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 7px 14px;
      border-radius: 6px;
      font-size: 0.84rem;
      cursor: pointer;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-action:hover {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }}

    /* Rich Inspector Modal */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(5, 8, 16, 0.85);
      backdrop-filter: blur(12px);
      z-index: 1000;
      display: none;
      place-items: center;
      padding: 24px;
    }}
    .modal-content {{
      background: var(--surface-card);
      border: 1px solid var(--border-bright);
      border-radius: 16px;
      width: 100%;
      max-width: 1150px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 60px rgba(0,0,0,0.8);
      overflow: hidden;
    }}
    .modal-header {{
      padding: 20px 24px;
      background: rgba(0,0,0,0.2);
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .modal-title-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .modal-file-name {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .modal-path {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: var(--cyan);
      word-break: break-all;
    }}
    .modal-meta-pills {{
      display: flex;
      gap: 8px;
      margin-top: 6px;
      flex-wrap: wrap;
    }}
    .modal-tab-bar {{
      display: flex;
      gap: 2px;
      background: rgba(0,0,0,0.3);
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
    }}
    .modal-tab {{
      padding: 12px 18px;
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }}
    .modal-tab.active {{
      color: #fff;
      border-bottom-color: var(--primary);
      background: rgba(139, 92, 246, 0.1);
    }}
    .modal-body {{
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}

    .code-view {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.88rem;
      white-space: pre-wrap;
      word-break: break-all;
      color: #e5e7eb;
      background: #080c14;
      padding: 20px;
      border-radius: 10px;
      border: 1px solid var(--border);
      max-height: 60vh;
      overflow-y: auto;
      line-height: 1.6;
    }}

    .ref-card {{
      background: rgba(0,0,0,0.25);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .ref-card:hover {{
      background: var(--surface-hover);
      border-color: var(--primary);
    }}
    .ref-title {{ color: #fff; font-weight: 600; font-size: 0.92rem; }}
    .ref-path {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted); }}

    .ai-box {{
      background: rgba(139, 92, 246, 0.08);
      border: 1px solid rgba(139, 92, 246, 0.25);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .ai-box h4 {{
      color: #c084fc;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .ai-text {{
      font-size: 0.95rem;
      color: #e2e8f0;
      line-height: 1.6;
    }}

    .close-modal {{
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 1.8rem;
      cursor: pointer;
      padding: 4px 8px;
      line-height: 1;
    }}
    .close-modal:hover {{ color: #fff; }}
  </style>
</head>
<body>

  <header>
    <div class="header-container">
      <div class="logo-group">
        <div class="logo-icon">🧠</div>
        <div>
          <div class="logo-title">MEGASUCHE & MEGAVAULT</div>
          <div style="font-size: 0.76rem; color: var(--text-muted);">Gesamtatlas Gedächtnis & VPS-Struktur</div>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-pill">🧠 Indiziert: <strong>80.971 Docs</strong></div>
        <div class="stat-pill">⚡ Local AI: <strong>Qwen2.5 (CPU)</strong></div>
        <div class="stat-pill">🌐 Auth: <strong>Admin Basic</strong></div>
      </div>
    </div>
  </header>

  <main>
    <!-- View Mode Switcher -->
    <div class="view-switcher">
      <button id="btnModeTree" class="mode-btn active">📁 VPS-Baum (Dateibrowser ab /)</button>
      <button id="btnModeSearch" class="mode-btn">🔍 Live-Suche & Gesamtatlas Hybrid</button>
    </div>

    <!-- Stream Filters -->
    <div class="filter-bar">
      <span class="filter-label">AI-Strom Filter:</span>
      <button class="stream-pill active" onclick="filterStream('all')">Alle</button>
      <button class="stream-pill" onclick="filterStream('gemini')">♊ Gemini</button>
      <button class="stream-pill" onclick="filterStream('codex')">🤖 Codex</button>
      <button class="stream-pill" onclick="filterStream('claude')">🧠 Claude</button>
      <button class="stream-pill" onclick="filterStream('chatgpt')">💬 ChatGPT</button>
      <button class="stream-pill" onclick="filterStream('kimi')">🐲 Kimi</button>
      <button class="stream-pill" onclick="filterStream('root')">🌐 VPS Root</button>
      <button class="stream-pill" onclick="filterStream('etc')">⚙️ System /etc</button>
    </div>

    <!-- Search Input Section -->
    <section class="search-section">
      <div class="input-wrapper">
        <input autofocus type="text" id="qInput" class="search-input" value="{safe_q}" placeholder="Suchen in 80.971 Dateien & VPS-Pfaden... (z. B. AGENTS.md, nginx, /etc/systemd)">
        <button id="btnSearch" class="btn-search">Suchen</button>
      </div>

      <div class="quick-jump">
        <span class="quick-label">Direktsprung:</span>
        <button class="quick-pill" onclick="loadTree('/')">[/] Wurzel</button>
        <button class="quick-pill" onclick="loadTree('/root')">[/root] Home</button>
        <button class="quick-pill" onclick="loadTree('/root/werkraum')">[/root/werkraum] Werkraum</button>
        <button class="quick-pill" onclick="loadTree('/etc')">[/etc] Configs</button>
        <button class="quick-pill" onclick="loadTree('/etc/nginx')">[/etc/nginx] Nginx</button>
        <button class="quick-pill" onclick="loadTree('/etc/systemd/system')">[/etc/systemd] Services</button>
      </div>
    </section>

    <!-- TREE VIEW CONTAINER -->
    <div id="treeContainer" class="tree-container">
      <div id="treeCrumbs" class="tree-breadcrumbs">Lade Baum...</div>
      <div id="treeList" class="tree-list"></div>
    </div>

    <!-- SEARCH RESULTS CONTAINER -->
    <div id="searchContainer" class="results-grid" style="display: none;">
      <div id="searchStatus" style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px;">Ergebnisse erscheinen hier...</div>
      <div id="resultsGrid" class="results-grid"></div>
    </div>
  </main>

  <!-- Gesamtatlas File Inspector Modal -->
  <div id="modalOverlay" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="modal-file-name">
            <span id="modalFileName">AGENTS.md</span>
            <span id="modalStreamTag" class="stream-tag st-system">VPS System</span>
            <span id="modalIndexedTag" class="stream-tag st-chatgpt" style="display:none;">🧠 Atlas Indiziert</span>
          </div>
          <div id="modalPath" class="modal-path">/root/AGENTS.md</div>
          <div id="modalMetaPills" class="modal-meta-pills"></div>
        </div>
        <button id="btnCloseModal" class="close-modal">&times;</button>
      </div>

      <div class="modal-tab-bar">
        <div class="modal-tab active" onclick="switchModalTab('code')">📄 Code & Text Viewer</div>
        <div class="modal-tab" onclick="switchModalTab('refs')">🔗 Querverweise & Resonanz (<span id="refCount">0</span>)</div>
        <div class="modal-tab" onclick="switchModalTab('ai')">💬 Local AI Analyse</div>
      </div>

      <div class="modal-body">
        <!-- TAB 1: CODE VIEWER & EDITOR -->
        <div id="tabCode" class="tab-content active">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div style="font-size:0.82rem; color:var(--text-muted);" id="codeViewStats">Zeilen: 0 | Größe: 0 B</div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button class="btn-action" onclick="copyModalPath()">📋 Pfad</button>
              <button class="btn-action" onclick="copyModalCode()">📄 Kopieren</button>
              <button class="btn-action" style="border-color:#38bdf8; color:#38bdf8;" onclick="toggleEditor()">✏️ Bearbeiten</button>
              <button id="btnSaveFile" class="btn-action" style="display:none; background:#0284c7; color:#fff; font-weight:600;" onclick="saveCurrentFile()">💾 Speichern</button>
              <button class="btn-action" style="border-color:#f43f5e; color:#f43f5e;" onclick="deleteCurrentFile()">🗑️ Soft-Delete</button>
              <button id="btnRestoreFile" class="btn-action" style="display:none; border-color:#22c55e; color:#22c55e;" onclick="restoreCurrentFile()">↩️ Wiederherstellen</button>
            </div>
          </div>
          <div id="editorStatusNotification" style="display:none; padding:8px 12px; margin-bottom:10px; border-radius:6px; font-size:0.85rem;"></div>
          <pre id="modalCode" class="code-view">Lade Datei-Details...</pre>
          <textarea id="modalCodeEditor" style="display:none; width:100%; height:420px; font-family:'JetBrains Mono', monospace; font-size:0.85rem; background:#090c15; color:#e2e8f0; border:1px solid #334155; border-radius:8px; padding:12px; box-sizing:border-box; outline:none; resize:vertical;"></textarea>
        </div>

        <!-- TAB 2: QUERVERWEISE & SUBGRAPHEN / KONFLIKTLINSEN -->
        <div id="tabRefs" class="tab-content">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:8px;">
            <div style="font-size:0.9rem; color:var(--text-muted);">
              Dokumente, Subgraphen & Konflikte im Gesamtatlas:
            </div>
            <div style="display:flex; gap:8px;">
              <button id="btnSubgraphen" class="btn-action" onclick="loadRelationships(true, false)">🌐 Subgraphen (1-Hop)</button>
              <button id="btnKonflikte" class="btn-action" onclick="loadRelationships(false, true)">⚔️ Konfliktlinsen</button>
            </div>
          </div>
          <div id="refList">Lade Querverweise...</div>
          <div id="relSubgraphContainer" style="margin-top:16px; display:none;"></div>
        </div>

        <!-- TAB 3: AI ANALYSE -->
        <div id="tabAi" class="tab-content">
          <div class="ai-box">
            <h4>🧠 Lokale Qwen2.5 CPU-Synthese</h4>
            <div id="aiAnalysisText" class="ai-text">
              Klicke auf den Button unten, um eine automatische KI-Zusammenfassung und Rollenanalyse für diese Datei im Gesamtatlas zu erstellen.
            </div>
            <button class="btn-search" style="margin-top:14px;" onclick="runAiAnalysis()">⚡ KI-Analyse anfordern</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let activeMode = "search";
    let activeStreamFilter = "all";
    let currentTreePath = "/root";
    let activeFileDetails = null;

    const btnModeTree = document.getElementById("btnModeTree");
    const btnModeSearch = document.getElementById("btnModeSearch");
    const treeContainer = document.getElementById("treeContainer");
    const searchContainer = document.getElementById("searchContainer");
    const treeCrumbs = document.getElementById("treeCrumbs");
    const treeList = document.getElementById("treeList");
    const qInput = document.getElementById("qInput");
    const btnSearch = document.getElementById("btnSearch");
    const resultsGrid = document.getElementById("resultsGrid");
    const searchStatus = document.getElementById("searchStatus");
    const modalOverlay = document.getElementById("modalOverlay");
    const btnCloseModal = document.getElementById("btnCloseModal");

    // Mode Toggle
    btnModeTree.addEventListener("click", () => setMode("tree"));
    btnModeSearch.addEventListener("click", () => setMode("search"));

    function setMode(mode) {{
      activeMode = mode;
      if (mode === "tree") {{
        btnModeTree.classList.add("active");
        btnModeSearch.classList.remove("active");
        treeContainer.style.display = "block";
        searchContainer.style.display = "none";
        loadTree(currentTreePath);
      }} else {{
        btnModeSearch.classList.add("active");
        btnModeTree.classList.remove("active");
        searchContainer.style.display = "flex";
        treeContainer.style.display = "none";
      }}
    }}

    function filterStream(stream) {{
      activeStreamFilter = stream;
      document.querySelectorAll(".stream-pill").forEach(p => p.classList.remove("active"));
      event.target.classList.add("active");
      if (activeMode === "search") {{
        runSearch();
      }}
    }}

    // TREE LOADING
    async function loadTree(path) {{
      currentTreePath = path;
      treeCrumbs.innerHTML = "Lade Verzeichnis...";
      treeList.innerHTML = "";

      try {{
        const res = await fetch(`api/megavault/tree?pfad=${{encodeURIComponent(path)}}`);
        const data = await res.json();

        if (data.ok) {{
          renderCrumbs(data.pfad);
          renderTreeItems(data.eintraege, data.parent);
        }} else {{
          treeList.innerHTML = `<div style="padding: 20px; color: var(--rose);">Fehler: ${{data.detail || 'Verzeichnis konnte nicht geladen werden'}}</div>`;
        }}
      }} catch (err) {{
        treeList.innerHTML = `<div style="padding: 20px; color: var(--rose);">Netzwerkfehler beim Laden des Verzeichnisses.</div>`;
      }}
    }}

    function renderCrumbs(path) {{
      const parts = path.split('/').filter(Boolean);
      let html = `<span class="crumb" onclick="loadTree('/')">/</span>`;
      let build = "";

      parts.forEach(p => {{
        build += '/' + p;
        const targetPath = build;
        html += `<span class="crumb-sep">></span><span class="crumb" onclick="loadTree('${{targetPath}}')">${{p}}</span>`;
      }});

      treeCrumbs.innerHTML = html;
    }}

    function renderTreeItems(items, parentPath) {{
      treeList.innerHTML = "";

      if (parentPath !== null && parentPath !== undefined) {{
        const parentItem = document.createElement("div");
        parentItem.className = "tree-item";
        parentItem.innerHTML = `
          <div class="item-left">
            <span class="item-icon">⬆️</span>
            <span class="item-name">.. (Übergeordneter Ordner)</span>
          </div>
          <div class="item-meta"><span>DIR</span></div>
        `;
        parentItem.onclick = () => loadTree(parentPath);
        treeList.appendChild(parentItem);
      }}

      if (items.length === 0) {{
        treeList.innerHTML += `<div style="padding: 20px; color: var(--text-muted);">Verzeichnis ist leer.</div>`;
        return;
      }}

      items.forEach(item => {{
        const div = document.createElement("div");
        div.className = "tree-item";

        const icon = item.is_dir ? "📁" : "📄";
        const sizeStr = item.is_dir ? "" : formatBytes(item.groesse_bytes);
        const streamClass = getStreamClass(item.pfad);
        const streamName = getStreamName(item.pfad);

        div.innerHTML = `
          <div class="item-left">
            <span class="item-icon">${{icon}}</span>
            <span class="item-name">${{item.name}}</span>
          </div>
          <div class="item-meta">
            ${{item.is_dir ? '' : `<span class="stream-tag ${{streamClass}}">${{streamName}}</span>`}}
            <span>${{sizeStr}}</span>
          </div>
        `;

        if (item.is_dir) {{
          div.onclick = () => loadTree(item.pfad);
        }} else {{
          div.onclick = () => openFileInspector(item.pfad);
        }}

        treeList.appendChild(div);
      }});
    }}

    // SEARCH LOGIC
    btnSearch.addEventListener("click", () => {{
      setMode("search");
      runSearch();
    }});
    qInput.addEventListener("keydown", (e) => {{
      if (e.key === "Enter") {{
        setMode("search");
        runSearch();
      }}
    }});

    async function runSearch() {{
      const query = qInput.value.trim();
      if (!query) return;

      searchStatus.textContent = `Durchsuche VPS-Dateisystem & Atlas nach "${{query}}"...`;
      resultsGrid.innerHTML = "";

      let url = `api/megavault/search?q=${{encodeURIComponent(query)}}&limit=50`;
      if (activeStreamFilter !== "all") {{
        url += `&stream=${{encodeURIComponent(activeStreamFilter)}}`;
      }}

      try {{
        const res = await fetch(url);
        const data = await res.json();

        if (data.ok && data.results) {{
          searchStatus.textContent = `Gefundene Treffer für "${{query}}": ${{data.results.length}}`;

          data.results.forEach(item => {{
            const filePath = item.pfad || item.path || "";
            const fileName = item.titel || (filePath ? filePath.split('/').pop() : "Datei");
            const ext = fileName.includes('.') ? fileName.split('.').pop() : "txt";
            const extClass = item.quelle === "live_filesystem_exact" ? "ext-exact" : getExtClass(ext);
            const streamClass = getStreamClass(filePath);
            const streamName = getStreamName(filePath);
            const excerpt = item.ausschnitt || item.excerpt || "Keine Vorschau verfügbar.";

            const card = document.createElement("div");
            card.className = "result-card";

            card.innerHTML = `
              <div class="card-top">
                <div style="display:flex; align-items:center; gap:8px;">
                  <div class="card-title">${{fileName}}</div>
                  <span class="stream-tag ${{streamClass}}">${{streamName}}</span>
                </div>
                <span class="ext-badge ${{extClass}}">${{item.quelle || ext}}</span>
              </div>
              <div class="card-path">${{filePath}}</div>
              <div class="card-snippet">${{excerpt}}</div>
              <div class="card-actions">
                <button class="btn-action" onclick="openFileInspector('${{encodeURIComponent(filePath)}}')">👁️ Gesamtatlas Inspector</button>
                <button class="btn-action" onclick="copyPath('${{filePath}}')">📋 Pfad kopieren</button>
              </div>
            `;
            resultsGrid.appendChild(card);
          }});
        }} else {{
          searchStatus.textContent = "Keine Treffer gefunden.";
        }}
      }} catch (err) {{
        searchStatus.textContent = "Fehler bei der VPS-Suche: " + err;
      }}
    }}

    // RICH FILE INSPECTOR MODAL
    async function openFileInspector(encodedPath) {{
      const path = decodeURIComponent(encodedPath);
      activeFileDetails = null;

      document.getElementById("modalFileName").textContent = path.split('/').pop();
      document.getElementById("modalPath").textContent = path;
      document.getElementById("modalCode").textContent = "Lade Gesamtatlas File Intelligence...";
      document.getElementById("refList").innerHTML = "Lade Querverweise...";
      document.getElementById("aiAnalysisText").textContent = "Klicke auf den Button unten, um eine automatische KI-Zusammenfassung zu generieren.";
      modalOverlay.style.display = "grid";

      switchModalTab('code');

      try {{
        const res = await fetch(`api/megavault/file_details?pfad=${{encodeURIComponent(path)}}`);
        const data = await res.json();

        if (data.ok) {{
          activeFileDetails = data;
          document.getElementById("modalFileName").textContent = data.name;
          document.getElementById("modalPath").textContent = data.pfad;
          document.getElementById("modalCode").textContent = data.content;

          // Stream & Index Badges
          const streamTag = document.getElementById("modalStreamTag");
          streamTag.className = `stream-tag ${{getStreamClass(data.pfad)}}`;
          streamTag.textContent = data.stream_name;

          const indexedTag = document.getElementById("modalIndexedTag");
          indexedTag.style.display = data.bm25_indexed ? "inline-block" : "none";

          // Meta Pills
          document.getElementById("modalMetaPills").innerHTML = `
            <span class="quick-pill">Groesse: ${{formatBytes(data.groesse_bytes)}}</span>
            <span class="quick-pill">Zeilen: ${{data.zeilen_anzahl}}</span>
            <span class="quick-pill">Rechte: ${{data.permissions}}</span>
            <span class="quick-pill">Geaendert: ${{data.geaeandert_utc.split('T')[0]}}</span>
          `;
          document.getElementById("codeViewStats").textContent = `Zeilen: ${{data.zeilen_anzahl}} | Größe: ${{formatBytes(data.groesse_bytes)}} | Rechte: ${{data.permissions}}`;

          // Querverweise Tab
          document.getElementById("refCount").textContent = data.referenzen.length;
          renderReferences(data.referenzen);
        }} else {{
          document.getElementById("modalCode").textContent = "Fehler beim Laden: " + (data.detail || "Unbekannt");
        }}
      }} catch (e) {{
        document.getElementById("modalCode").textContent = "Netzwerkfehler beim Laden der Datei-Details.";
      }}
    }}

    function renderReferences(refs) {{
      const list = document.getElementById("refList");
      list.innerHTML = "";

      if (refs.length === 0) {{
        list.innerHTML = `<div style="color:var(--text-muted); padding:16px;">Keine direkten Querverweise im Werkraum gefunden.</div>`;
        return;
      }}

      refs.forEach(r => {{
        const card = document.createElement("div");
        card.className = "ref-card";
        card.innerHTML = `
          <div>
            <div class="ref-title">📄 ${{r.titel}}</div>
            <div class="ref-path">${{r.relativ}}</div>
          </div>
          <button class="btn-action" onclick="openFileInspector('${{encodeURIComponent(r.pfad)}}')">👁️ Öffnen</button>
        `;
        list.appendChild(card);
      }});
    }}

    async function runAiAnalysis() {{
      if (!activeFileDetails) return;
      const textEl = document.getElementById("aiAnalysisText");
      textEl.textContent = "Generiere lokale KI-Synthese via Qwen2.5 (CPU)...";

      try {{
        const q = `Zusammenfassung und Rolle der Datei ${{activeFileDetails.name}}`;
        const res = await fetch(`api/megavault/ask?q=${{encodeURIComponent(q)}}`);
        const data = await res.json();

        if (data && data.answer) {{
          textEl.textContent = data.answer;
        }} else {{
          textEl.textContent = "Keine Antwort von der lokalen KI erhalten.";
        }}
      }} catch (e) {{
        textEl.textContent = "Fehler bei der KI-Synthese.";
      }}
    }}

    function switchModalTab(tab) {{
      document.querySelectorAll(".modal-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      if (tab === 'code') {{
        document.querySelectorAll(".modal-tab")[0].classList.add("active");
        document.getElementById("tabCode").classList.add("active");
      }} else if (tab === 'refs') {{
        document.querySelectorAll(".modal-tab")[1].classList.add("active");
        document.getElementById("tabRefs").classList.add("active");
        loadRelationships(true, false);
      }} else if (tab === 'ai') {{
        document.querySelectorAll(".modal-tab")[2].classList.add("active");
        document.getElementById("tabAi").classList.add("active");
      }}
    }}

    let isEditMode = false;

    function toggleEditor() {{
      if (!activeFileDetails) return;
      const modalCode = document.getElementById("modalCode");
      const modalEditor = document.getElementById("modalCodeEditor");
      const btnSave = document.getElementById("btnSaveFile");

      isEditMode = !isEditMode;
      if (isEditMode) {{
        modalEditor.value = activeFileDetails.content;
        modalCode.style.display = "none";
        modalEditor.style.display = "block";
        btnSave.style.display = "inline-block";
      }} else {{
        modalCode.style.display = "block";
        modalEditor.style.display = "none";
        btnSave.style.display = "none";
      }}
    }}

    async function saveCurrentFile() {{
      if (!activeFileDetails) return;
      const editor = document.getElementById("modalCodeEditor");
      const notif = document.getElementById("editorStatusNotification");
      notif.style.display = "block";
      notif.style.background = "#0284c722";
      notif.style.color = "#38bdf8";
      notif.textContent = "Speichere Datei & erstelle Git-Backup...";

      try {{
        const res = await fetch("api/megavault/file/save", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ pfad: activeFileDetails.pfad, content: editor.value }})
        }});
        const data = await res.json();

        if (data.ok) {{
          activeFileDetails.content = editor.value;
          document.getElementById("modalCode").textContent = editor.value;
          notif.style.background = "#15803d22";
          notif.style.color = "#4ade80";
          notif.textContent = "✅ Datei erfolgreich gespeichert & im Vektor-Index aktualisiert (Git-Backup angelegt)!";
          toggleEditor();
        }} else {{
          notif.style.background = "#be123c22";
          notif.style.color = "#fb7185";
          notif.textContent = "Fehler beim Speichern: " + (data.detail || "Unbekannt");
        }}
      }} catch (e) {{
        notif.style.background = "#be123c22";
        notif.style.color = "#fb7185";
        notif.textContent = "Netzwerkfehler beim Speichern.";
      }}
    }}

    async function deleteCurrentFile() {{
      if (!activeFileDetails) return;
      if (!confirm(`Soll '${{activeFileDetails.name}}' wirklich geknickt/soft-gelöscht werden?`)) return;

      const notif = document.getElementById("editorStatusNotification");
      notif.style.display = "block";
      notif.style.background = "#0284c722";
      notif.style.color = "#38bdf8";
      notif.textContent = "Führe Soft-Delete aus...";

      try {{
        const res = await fetch("api/megavault/file/delete", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ pfad: activeFileDetails.pfad, mode: "soft" }})
        }});
        const data = await res.json();

        if (data.ok) {{
          notif.style.background = "#be123c22";
          notif.style.color = "#fb7185";
          notif.textContent = "🗑️ Datei soft-gelöscht & nach _softdeleted/ verschoben. (Kann wiederhergestellt werden)";
          document.getElementById("btnRestoreFile").style.display = "inline-block";
        }} else {{
          notif.textContent = "Fehler beim Löschen: " + (data.detail || "Unbekannt");
        }}
      }} catch (e) {{
        notif.textContent = "Netzwerkfehler beim Löschen.";
      }}
    }}

    async function restoreCurrentFile() {{
      if (!activeFileDetails) return;
      const notif = document.getElementById("editorStatusNotification");

      try {{
        const res = await fetch("api/megavault/file/restore", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ pfad: activeFileDetails.pfad }})
        }});
        const data = await res.json();

        if (data.ok) {{
          notif.style.background = "#15803d22";
          notif.style.color = "#4ade80";
          notif.textContent = "↩️ Datei erfolgreich aus _softdeleted/ wiederhergestellt!";
          document.getElementById("btnRestoreFile").style.display = "none";
        }} else {{
          notif.textContent = "Fehler beim Wiederherstellen: " + (data.detail || "Unbekannt");
        }}
      }} catch (e) {{
        notif.textContent = "Netzwerkfehler beim Wiederherstellen.";
      }}
    }}

    async function loadRelationships(includeNeighbors, includeConflicts) {{
      if (!activeFileDetails) return;
      const container = document.getElementById("relSubgraphContainer");
      container.style.display = "block";
      container.innerHTML = "<div style='color:var(--text-muted);'>Lade Beziehungsnetz, Subgraphen & Konfliktlinsen...</div>";

      try {{
        let url = `/megasuche/api/megavault/relationships?q=${{encodeURIComponent(activeFileDetails.name)}}`;
        if (includeNeighbors) url += "&include_neighbors=true";
        if (includeConflicts) url += "&include_conflicts=true";

        const res = await fetch(url);
        const data = await res.json();

        if (data.ok && data.nodes) {{
          let html = `<div style='font-size:0.85rem; font-weight:600; margin-bottom:8px; color:#38bdf8;'>${{includeConflicts ? '⚔️ Konfliktlinsen & Widersprüche' : '🌐 Subgraph / 1-Hop Nachbarringe'}} (${{data.nodes.length}} Knoten, ${{data.edges.length}} Kanten)</div>`;
          html += "<div style='display:flex; flex-direction:column; gap:6px;'>";
          data.nodes.slice(0, 10).forEach(n => {{
            html += `<div style='background:#111625; padding:8px 12px; border-radius:6px; border:1px solid #334155;'>
              <div style='font-weight:600; font-size:0.85rem;'>${{n.label || n.identity}}</div>
              <div style='font-size:0.75rem; color:var(--text-muted);'>Typ: ${{n.node_type}} | Pfad: ${{n.path || 'Virtuell'}}</div>
            </div>`;
          }});
          html += "</div>";
          container.innerHTML = html;
        }} else {{
          container.innerHTML = "<div style='color:var(--text-muted);'>Keine fokussierten Subgraphen oder Konfliktlinsen für diesen Pfad gefunden.</div>";
        }}
      }} catch (e) {{
        container.innerHTML = "<div style='color:var(--text-muted);'>Beziehungsregister nicht erreichbar.</div>";
      }}
    }}

    function closeModal() {{
      modalOverlay.style.display = "none";
    }}
    btnCloseModal.addEventListener("click", closeModal);
    window.addEventListener("keydown", (e) => {{ if (e.key === "Escape") closeModal(); }});

    function getStreamClass(path) {{
      if (!path) return "st-system";
      if (path.includes("/_gemini")) return "st-gemini";
      if (path.includes("/_codex")) return "st-codex";
      if (path.includes("/_claude")) return "st-claude";
      if (path.includes("/_gpt")) return "st-chatgpt";
      if (path.includes("/_kimi")) return "st-kimi";
      if (path.includes("/_shared")) return "st-shared";
      return "st-system";
    }}

    function getStreamName(path) {{
      if (!path) return "VPS System";
      if (path.includes("/_gemini")) return "Gemini Stream";
      if (path.includes("/_codex")) return "Codex Stream";
      if (path.includes("/_claude")) return "Claude Stream";
      if (path.includes("/_gpt")) return "ChatGPT Stream";
      if (path.includes("/_kimi")) return "Kimi Stream";
      if (path.includes("/_shared")) return "Shared Resonanz";
      return "VPS System";
    }}

    function formatBytes(bytes) {{
      if (!bytes) return "0 B";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }}

    function getExtClass(ext) {{
      if (ext === "py") return "ext-py";
      if (ext === "md") return "ext-md";
      if (ext === "json") return "ext-json";
      return "ext-other";
    }}

    function copyPath(text) {{
      navigator.clipboard.writeText(text);
      alert("Pfad kopiert: " + text);
    }}
    function copyModalPath() {{
      if (activeFileDetails) copyPath(activeFileDetails.pfad);
    }}
    function copyModalCode() {{
      if (activeFileDetails) {{
        navigator.clipboard.writeText(activeFileDetails.content);
        alert("Inhalt in Zwischenablage kopiert!");
      }}
    }}

    // Initialize View
    setMode("search");
    if (qInput.value.trim()) {{
      runSearch();
    }} else {{
      qInput.value = "geni";
      runSearch();
    }}
  </script>
</body>
</html>'''
    return HTMLResponse(html)




@app.get(f"{BASE}/original/", response_class=HTMLResponse, include_in_schema=False)
def original(p: str = Query(..., min_length=2)):
    raw_path = decode_path(p)
    classification = classify_public_original(raw_path)
    nav_html = f'<nav class="journey-nav" aria-label="Rückwege"><a id="original-back-journey" class="button primary" href="{href("/reise?schritt=7")}">← Zur Reise zurück</a><a class="button" href="{href("/suche")}">Andere Spur suchen</a><a class="button" href="{href("/erkunden")}">Frei erkunden</a><a class="button" href="{href("/")}">Weltkarte</a></nav>'
    if not classification["available"]:
        body = f'''<section class="section-head"><div><div class="kicker">Provenienzspur ohne ausgelieferten Inhalt</div><h1>{esc(classification["name"])}</h1></div><span class="pill warn">{esc(classification["state"])}</span></section>
<dl class="truth card"><dt>Registrierter Pfad</dt><dd class="path">{esc(classification["path"])}</dd><dt>Zustand</dt><dd>{esc(classification["state"])}</dd><dt>Grund</dt><dd>{esc(classification["reason"])}</dd><dt>Bekannte Größe</dt><dd>{fmt_bytes(classification["bytes"])}</dd><dt>Wahrheitsklasse</dt><dd>{esc(classification["truth_class"])}</dd></dl>
<section id="original-explanation" class="notice"><strong>Kein erfundener Inhalt:</strong> Private, binäre, zu große, verschwundene, verlinkte oder außerhalb der Freigabefläche liegende Bytes werden nicht geöffnet.</section>{nav_html}'''
        return page(classification["name"], body, active="suche")
    path = resolve_public_file(raw_path)
    original_bytes = path.read_bytes()
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    text = original_bytes.decode("utf-8", errors="replace")
    shown, redactions = redact_secrets(text)
    status = "zeichengetreue Außenansicht" if redactions == 0 else "Original mit klar markierten Sicherheitsauslassungen"
    display_note = "Keine Inhaltsumschreibung." if redactions == 0 else f"{redactions} Geheimnisse oder mögliche fremde Kontaktdaten wurden markiert entfernt; der private Ursprung blieb unverändert."
    body = f'''<section class="section-head"><div><div class="kicker">Originalkörper</div><h1>{esc(path.name)}</h1></div><span class="pill {'ok' if redactions == 0 else 'warn'}">{status}</span></section>
<dl class="truth card"><dt>Pfad</dt><dd class="path">{esc(path)}</dd><dt>SHA-256 des Originals</dt><dd class="mono">{original_sha}</dd><dt>Größe</dt><dd>{fmt_bytes(len(original_bytes))}</dd><dt>Zustand</dt><dd>READABLE_TEXT</dd><dt>Darstellung</dt><dd>{display_note}</dd></dl>
{nav_html}<section class="section"><div class="codebox"><pre>{esc(shown)}</pre></div></section>'''
    return page(path.name, body, active="suche")





@app.get(f"{BASE}/projekte", response_class=HTMLResponse, include_in_schema=False)
def projects(kind: str = ""):
    rows = project_rows()
    if kind:
        rows = [row for row in rows if row.get("project_class") == kind]
    classes = sorted({str(row.get("project_class") or "unbekannt") for row in project_rows()})
    body = '<section class="section-head"><div><div class="kicker">Projektkörper</div><h1>Gebäude, Werkstätten und Strukturknoten</h1></div><p>Ein Projekt ist nicht bloß ein Ordner. Revisionen, Beziehungen, Dateien und Arbeitsgeschichte werden gemeinsam gezeigt.</p></section><div class="tabs">'
    body += f'<a class="{"active" if not kind else ""}" href="{href("/projekte")}">Alle</a>'
    for name in classes:
        body += f'<a class="{"active" if kind == name else ""}" href="{href("/projekte")}?kind={quote(name)}">{esc(name)}</a>'
    body += '</div><div class="grid cols-3">'
    for row in rows:
        project_id = str(row.get("project_id") or "")
        body += f'''<a class="card-link" href="{href('/projekt/' + quote(project_id))}"><article class="card"><div class="kicker">{esc(row.get('project_class') or 'Projekt')}</div><h2>{esc(row.get('name') or Path(str(row.get('path') or '')).name)}</h2><p class="path">{esc(row.get('path'))}</p><div class="meta"><span class="pill">r{esc(row.get('project_revision', 0))}</span><span class="pill">{esc(len(row.get('markers') or []))} Marker</span><span class="pill">{esc(row.get('confidence') or row.get('truth_class') or 'klassifiziert')}</span></div></article></a>'''
    body += '</div>'
    return page("Projekte", body, active="projekte")


@app.get(f"{BASE}/projekt/{{project_id}}", response_class=HTMLResponse, include_in_schema=False)
def project_detail(project_id: str):
    row = project_by_id(project_id)
    if not row:
        raise HTTPException(404, "Projektkörper nicht gefunden")
    path = str(row.get("path") or "")
    files = []
    try:
        with db(PATH_DB) as con:
            files = con.execute("select path,basename,kind,size,markers_json from paths where path like ? and is_dir=0 order by depth,length(path) limit 120", (path.rstrip("/") + "/%",)).fetchall()
    except Exception:
        pass
    graph = relationship_graph(path or project_id, 36)
    body = f'''<section class="section-head"><div><div class="kicker">{esc(row.get('project_class') or 'Projekt')}</div><h1>{esc(row.get('name') or Path(path).name)}</h1></div><span class="pill info">Projekt-ID {esc(project_id)}</span></section>
<div class="grid cols-2"><article class="card"><h2>Herkunft und Zustand</h2><dl class="truth"><dt>Pfad</dt><dd class="path">{esc(path)}</dd><dt>Revision</dt><dd>{esc(row.get('project_revision', 0))}</dd><dt>Kanonisch</dt><dd>{'ja' if row.get('primary_project') else 'nein / Bestandteil'}</dd><dt>Marker</dt><dd>{esc(', '.join(row.get('markers') or []) or 'keine')}</dd></dl></article><article class="card"><h2>Direkt sichtbar</h2><div class="number">{len(files)}</div><div class="label">Dateikörper in dieser begrenzten Ansicht</div><p>Die Zahl ist ein Ansichtsdeckel, keine Vollständigkeitsbehauptung.</p></article></div>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(path)}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen dieses Projekts"></svg></div></section>
<section class="section"><div class="section-head"><h2>Originalkörper im Projekt</h2><span class="pill">maximal 120</span></div><div class="list">'''
    for file in files:
        token = encode_path(file["path"])
        body += f'<a class="card-link" href="{href("/original/")}?p={quote(token)}"><div class="list-item"><h3>{esc(file["basename"])}</h3><div class="path">{esc(file["path"])}</div><div class="meta"><span>{esc(file["kind"])}</span><span>{fmt_bytes(file["size"])}</span></div></div></a>'
    body += '</div></section>'
    return page(str(row.get("name") or project_id), body, active="projekte", graph=graph)


def atlas_node_by_id(node_id_value: str) -> dict[str, Any]:
    if not REL_DB.exists():
        raise HTTPException(503, "Beziehungsregister fehlt")
    with db(REL_DB) as con:
        row = con.execute("select * from nodes where node_id=?", (node_id_value,)).fetchone()
    if not row:
        raise HTTPException(404, "Atlas-Knoten nicht gefunden")
    result = dict(row)
    try:
        result["metadata"] = json.loads(result.pop("metadata_json") or "{}")
    except (json.JSONDecodeError, TypeError):
        result["metadata"] = {"parse_error": True}
    return result


def atlas_node_relations(node_id_value: str, limit: int = 500) -> list[dict[str, Any]]:
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select e.edge_id,e.relation,e.datenstand,e.evidence_json,e.first_utc,e.last_utc,
                   case when e.source_node_id=? then 'out' else 'in' end as direction,
                   n.node_id,n.node_type,n.identity,n.label,n.path,n.datenstand as node_datenstand
            from edges e
            join nodes n on n.node_id=case when e.source_node_id=? then e.target_node_id else e.source_node_id end
            where e.source_node_id=? or e.target_node_id=?
            order by coalesce(e.last_utc,e.first_utc) desc,e.relation,n.label
            limit ?
            """,
            (node_id_value, node_id_value, node_id_value, node_id_value, limit),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["evidence"] = json.loads(item.pop("evidence_json") or "[]")
        except (json.JSONDecodeError, TypeError):
            item["evidence"] = []
        result.append(item)
    return result


def atlas_node_relation_counts(node_id_value: str) -> dict[str, int]:
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select relation,count(*)
            from edges where source_node_id=? or target_node_id=?
            group by relation order by relation
            """,
            (node_id_value, node_id_value),
        ).fetchall()
    return {str(row[0]): int(row[1]) for row in rows}


def recent_wesen_thoughts(entity_id: str, limit: int = 24) -> list[dict[str, Any]]:
    if not REL_DB.exists():
        return []
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select n.node_id,n.identity,n.label,n.datenstand,n.metadata_json,e.last_utc
            from nodes w
            join edges e on e.source_node_id=w.node_id and e.relation='PRODUCED_THOUGHT'
            join nodes n on n.node_id=e.target_node_id and n.node_type='gedanke'
            where w.node_type='wesen' and w.identity=?
            order by e.last_utc desc,n.identity desc limit ?
            """,
            (entity_id, limit),
        ).fetchall()
    result=[]
    for row in rows:
        item=dict(row)
        try:
            metadata=json.loads(item.pop("metadata_json") or "{}")
        except (json.JSONDecodeError, TypeError):
            metadata={}
        item["gedanke"]=metadata.get("gedanke")
        item["entscheidung"]=metadata.get("entscheidung")
        item["begruendung"]=metadata.get("begruendung")
        item["action_prefix"]=metadata.get("action_prefix")
        item["href"]=href(f"/knoten/{quote(str(item['node_id']), safe='')}")
        result.append(item)
    return result


@app.get(f"{BASE}/api/knoten/{{node_id_value}}")
def atlas_node_api(node_id_value: str):
    node = atlas_node_by_id(node_id_value)
    return {
        "node": node,
        "relation_counts": atlas_node_relation_counts(node_id_value),
        "relations": atlas_node_relations(node_id_value),
        "graph": relationship_graph(node_id_value, 120),
    }


@app.get(f"{BASE}/knoten/{{node_id_value}}", response_class=HTMLResponse, include_in_schema=False)
def atlas_node_page(node_id_value: str):
    node = atlas_node_by_id(node_id_value)
    relations = atlas_node_relations(node_id_value, 200)
    relation_counts = atlas_node_relation_counts(node_id_value)
    graph = relationship_graph(node_id_value, 120)
    metadata_text = json.dumps(node.get("metadata") or {}, ensure_ascii=False, indent=2)
    if len(metadata_text) > 60000:
        metadata_text = metadata_text[:60000] + "\n…[Webansicht begrenzt; Registerzeile bleibt vollständig]"
    body = f'''<section class="section-head"><div><div class="kicker">{esc(node.get('node_type'))}</div><h1>{esc(node.get('label') or node.get('identity'))}</h1></div><span class="pill info">{esc(node.get('datenstand'))}</span></section>
<div class="grid cols-2"><article class="card"><h2>Stabile Knotenidentität</h2><dl class="truth"><dt>node_id</dt><dd class="path">{esc(node.get('node_id'))}</dd><dt>identity</dt><dd class="path">{esc(node.get('identity'))}</dd><dt>Typ</dt><dd>{esc(node.get('node_type'))}</dd><dt>Pfad</dt><dd class="path">{esc(node.get('path') or 'kein Dateipfad')}</dd></dl></article><article class="card"><h2>Beziehungen</h2><div class="number">{sum(relation_counts.values())}</div><div class="label">Kanten insgesamt</div><div class="meta">{''.join(f'<span class="pill">{esc(key)}: {value}</span>' for key,value in relation_counts.items())}</div></article></div>'''
    if node.get("path"):
        body += f'''<section class="section"><a class="button" href="{href('/original/?p=' + encode_path(str(node['path'])))}">Originalpfad prüfen</a></section>'''
    body += f'''<section class="section"><div class="section-head"><h2>Quellengebundene Metadaten</h2><span class="pill">escaped, maximal 60.000 Zeichen</span></div><div class="codebox"><pre>{esc(metadata_text)}</pre></div></section>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(str(node['node_id']))}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen dieses Knotens"></svg></div></section>
<section class="section"><div class="section-head"><h2>Direkte Nachbarn</h2><span class="pill">maximal 200</span></div><div class="list">'''
    for item in relations:
        other_href = href(f"/knoten/{quote(str(item['node_id']), safe='')}")
        if item.get("node_type") == "wesen":
            other_href = href(f"/urbewohner/{quote(str(item.get('identity') or ''))}")
        body += f'''<a class="card-link" href="{other_href}"><article class="list-item"><h3>{esc(item.get('label') or item.get('identity'))}</h3><div class="meta"><span class="pill">{esc(item.get('direction'))}</span><span class="pill">{esc(item.get('relation'))}</span><span class="pill">{esc(item.get('node_type'))}</span></div><div class="path">{esc(item.get('node_id'))} · {esc(item.get('last_utc') or item.get('first_utc') or 'ohne Ereigniszeit')}</div></article></a>'''
    body += '</div></section>'
    return page(str(node.get("label") or node.get("identity") or node_id_value), body, graph=graph, description="Ein stabiler Knoten des Gesamtatlas mit Herkunft und direkten Beziehungen.")


def urbewohner_register() -> dict[str, Any]:
    data = load_json(URBEWOHNER_REGISTER, {})
    if not isinstance(data, dict) or data.get("canonical_count") != 8:
        raise HTTPException(503, "Der Urbewohnerkörper ist noch nicht vollständig erzeugt")
    return data


def urbewohner_by_id(entity_id: str) -> dict[str, Any]:
    requested = entity_id.casefold()
    for row in urbewohner_register().get("entities") or []:
        names = [str(row.get("canonical_id") or ""), *(str(x) for x in row.get("aliases") or [])]
        if any(requested == name.casefold() for name in names):
            return row
    raise HTTPException(404, "Urbewohner nicht gefunden")


def urbewohner_relations(entity_id: str, limit: int = 500) -> list[dict[str, Any]]:
    if not REL_DB.exists():
        return []
    identity = entity_id
    with db(REL_DB) as con:
        entity = con.execute("select node_id from nodes where node_type='wesen' and identity=?", (identity,)).fetchone()
        if not entity:
            return []
        node_id = entity["node_id"]
        rows = con.execute(
            """
            select e.relation,e.datenstand,e.first_utc,e.last_utc,
                   case when e.source_node_id=? then 'out' else 'in' end as direction,
                   n.node_id,n.node_type,n.identity,n.label,n.path,n.datenstand as node_datenstand
            from edges e
            join nodes n on n.node_id=case when e.source_node_id=? then e.target_node_id else e.source_node_id end
            where e.source_node_id=? or e.target_node_id=?
            order by e.relation,coalesce(n.label,n.identity) limit ?
            """,
            (node_id, node_id, node_id, node_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get(f"{BASE}/api/urbewohner")
def urbewohner_api():
    data = urbewohner_register()
    return {
        "schema_version": data.get("schema_version"),
        "generated_utc": data.get("generated_utc"),
        "truth_boundary": data.get("truth_boundary"),
        "completeness": data.get("completeness"),
        "entities": [
            {
                "canonical_id": row.get("canonical_id"),
                "kind": row.get("kind"),
                "aliases": row.get("aliases"),
                "facet_count": row.get("facet_count"),
                "nonempty_facet_count": row.get("nonempty_facet_count"),
                "source_state": row.get("source_state"),
                "href": href(f"/urbewohner/{quote(str(row.get('canonical_id') or ''))}"),
            }
            for row in data.get("entities") or []
        ],
    }


@app.get(f"{BASE}/api/urbewohner/{{entity_id}}")
def urbewohner_detail_api(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    with db(REL_DB) as con:
        wesen_node = con.execute(
            "select node_id from nodes where node_type='wesen' and identity=?",
            (canonical,),
        ).fetchone()
    node_id_value = wesen_node["node_id"] if wesen_node else None
    return {
        "entity": row,
        "node_id": node_id_value,
        "relation_counts": atlas_node_relation_counts(node_id_value) if node_id_value else {},
        "relations": urbewohner_relations(canonical),
        "recent_thoughts": recent_wesen_thoughts(canonical),
        "graph": relationship_graph(canonical, 120),
    }


@app.get(f"{BASE}/urbewohner", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_page():
    data = urbewohner_register()
    completeness = data.get("completeness") or {}
    body = f'''<section class="section-head"><div><div class="kicker">Acht stabile Identitäten</div><h1>Die Urbewohner von Flextrawurst</h1></div><span class="pill {'ok' if completeness.get('complete') else 'warn'}">{'Quellenkörper vollständig' if completeness.get('complete') else 'Quellenkörper unvollständig'}</span></section>
<div class="notice"><strong>Kein Profilkarten-Ersatz:</strong> Jeder Urbewohner verbindet seine Datenbankfacetten, früheren Identitäten, Gedanken, Vaults, Organe, Herkunft und Beziehungen. Originalzeilen bleiben in ihren Quellen.</div>
<section class="section"><div class="grid cols-4">'''
    for row in data.get("entities") or []:
        canonical = str(row.get("canonical_id") or "")
        aliases = ", ".join(row.get("aliases") or []) or "keine frühere ID"
        body += f'''<a class="card-link" href="{href('/urbewohner/' + quote(canonical))}"><article class="card"><div class="kicker">{esc(row.get('kind'))}</div><h2>{esc(canonical)}</h2><div class="number">{int(row.get('nonempty_facet_count') or 0)}</div><div class="label">gefüllte von {int(row.get('facet_count') or 0)} Facetten</div><p class="path">{esc(aliases)}</p><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></article></a>'''
    body += f'''</div></section><section class="section"><div class="grid cols-2"><article class="card"><h2>Was vollständig heißt</h2><p>{int(completeness.get('postgres_source_pairs') or 0)} entitätsbezogene PostgreSQL-Quellenpaare wurden dynamisch entdeckt. Gedanken und GENI-Knoten erscheinen mit stabiler Original-ID im selben Beziehungsregister.</p></article><article class="card"><h2>Was nicht behauptet wird</h2><p>Eine Entscheidung beweist ihr Ziel, nicht automatisch die erfolgreiche Ausführung. Eine alte ID bleibt Herkunft, nicht heimlich eine neunte Person.</p></article></div></section>'''
    return page("Urbewohner", body, active="urbewohner", description="Die acht quellengebundenen Urbewohner im Gesamtatlas.")


@app.get(f"{BASE}/urbewohner/{{entity_id}}", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_detail_page(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    graph = relationship_graph(canonical, 120)
    aliases = row.get("aliases") or []
    with db(REL_DB) as con:
        wesen_node = con.execute(
            "select node_id from nodes where node_type='wesen' and identity=?",
            (canonical,),
        ).fetchone()
    node_id_value = wesen_node["node_id"] if wesen_node else None
    relation_counts = atlas_node_relation_counts(node_id_value) if node_id_value else {}
    recent_thoughts = recent_wesen_thoughts(canonical)
    current_text = json.dumps(row.get("current") or {}, ensure_ascii=False, indent=2)
    if len(current_text) > 18000:
        current_text = current_text[:18000] + "\n…[Ansicht begrenzt; JSON-Original bleibt vollständig]"
    body = f'''<section class="section-head"><div><div class="kicker">{esc(row.get('kind'))}</div><h1>{esc(canonical)}</h1></div><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></section>
<div class="grid cols-2"><article class="card"><h2>Stabile Identität</h2><dl class="truth"><dt>Kanonisch</dt><dd>{esc(canonical)}</dd><dt>node_id</dt><dd class="path">{esc(node_id_value or 'noch nicht gegossen')}</dd><dt>Frühere Identitäten</dt><dd>{esc(', '.join(aliases) or 'keine')}</dd><dt>Namensdatum</dt><dd>{esc(row.get('renamed_at') or 'nicht zutreffend')}</dd><dt>Facetten</dt><dd>{int(row.get('nonempty_facet_count') or 0)} gefüllt / {int(row.get('facet_count') or 0)} insgesamt</dd></dl><p><a class="button" href="{href('/original/?p=' + encode_path(str(URBEWOHNER_ROOT / (canonical + '.md'))))}">Manifest-Original öffnen</a></p></article>
<article class="card"><h2>Wahrheitsgrenze</h2><p>PostgreSQL, GENIs SQLite-Körper, Flarum-Herkunft und Vaultdateien bleiben Originale. <code>TARGETS</code> bedeutet: dieses Ziel wurde gewählt. Erfolgreiche Ausführung wird daraus nicht erfunden.</p><p class="path">{esc(str(URBEWOHNER_ROOT / (canonical + '.json')))}</p></article></div>
<section class="section"><div class="section-head"><h2>Aktueller sicherer Zeiger</h2><span class="pill">bereinigt, begrenzte Ansicht</span></div><div class="codebox"><pre>{esc(current_text)}</pre></div></section>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(canonical)}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen von {esc(canonical)}"></svg></div><div class="meta">{''.join(f'<span class="pill">{esc(key)}: {value}</span>' for key,value in sorted(relation_counts.items()))}</div></section>
<section class="section"><div class="section-head"><h2>Jüngste echte Gedanken</h2><span class="pill info">direkt aus PRODUCED_THOUGHT</span></div><div class="list">'''
    for thought in recent_thoughts:
        thought_text = thought.get("gedanke") or thought.get("label") or thought.get("identity")
        body += f'''<a class="card-link recent-thought" href="{thought['href']}"><article class="list-item"><h3>{esc(thought_text)}</h3><div class="meta"><span class="pill">{esc(thought.get('action_prefix') or 'ohne Aktion')}</span><span>{esc(thought.get('last_utc'))}</span></div><div class="path">{esc(thought.get('entscheidung') or 'keine Entscheidung')}</div></article></a>'''
    if not recent_thoughts:
        body += '<div class="notice">Noch kein vertragsgerechter Gedankenknoten im aktuellen Register.</div>'
    body += '''</div></section>
<section class="section"><div class="section-head"><h2>Alle quellengebundenen Facetten</h2><span class="pill info">leere Facetten bleiben sichtbar</span></div><div class="list">'''
    for facet in row.get("facets") or []:
        source = str(facet.get("table") or Path(str(facet.get("database_path") or "")).name)
        identity_column = facet.get("entity_column") or "GENI-eigen"
        status = str(facet.get("status") or "unbekannt")
        count = int(facet.get("count") or 0)
        body += f'''<article class="list-item"><h3>{esc(source)}</h3><div class="meta"><span class="pill {'ok' if count else ''}">{count} Zeilen</span><span class="pill">{esc(identity_column)}</span><span class="pill">{esc(status)}</span></div><div class="path">{esc(facet.get('database_path') or 'PostgreSQL flextrawurst.public')} · erste Spur {esc(facet.get('first_at') or '—')} · letzte Spur {esc(facet.get('last_at') or '—')}</div></article>'''
    body += '</div></section>'
    return page(canonical, body, active="urbewohner", graph=graph, description=f"Quellengebundener Atlas-Körper von {canonical}.")


@app.get(f"{BASE}/beziehungen", response_class=HTMLResponse, include_in_schema=False)
def relationships(q: str = Query("", max_length=300)):
    graph = relationship_graph(q, 48)
    body = f'''<section class="section-head"><div><div class="kicker">Beziehungsgewebe</div><h1>Das Netz zwischen den Körpern</h1></div><p>Kanten besitzen eigene Wahrheitsklassen. Nähe ist kein Beweis, Wiederholung ist kein unabhängiger Konsens.</p></section>
<form class="search-box" method="get"><input name="q" value="{esc(q)}" placeholder="Projekt, Pfad, Sitzung oder AI-Strom"><button>Netz fokussieren</button></form>
<section class="section"><div class="section-head"><h2>{len(graph['nodes'])} Knoten - {len(graph['edges'])} Kanten</h2><span class="pill info">SVG, tastaturbedienbar</span></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungsnetz"></svg></div></section>
<section class="section"><div class="grid cols-2"><article class="card"><h2>Was eine Kante sagen darf</h2><p>Sie nennt Relation, Herkunft und Wahrheitsklasse. Eine modellierte Resonanz bleibt modelliert.</p></article><article class="card"><h2>Was sie nicht sagen darf</h2><p>Erreichbarkeit ist nicht Lesen. Ähnlichkeit ist nicht Ursache. Vier Abschriften sind nicht vier unabhängige Belege.</p></article></div></section>'''
    return page("Beziehungen", body, active="beziehungen", graph=graph)


@app.get(f"{BASE}/zuhause", response_class=HTMLResponse, include_in_schema=False)
def homes():
    body = '<section class="section-head"><div><div class="kicker">Getrennte Häuser</div><h1>AI-Zuhause und Resonanzfelder</h1></div><p>Die Häuser werden gemeinsam sichtbar, ohne ihre Bewohner zu einer erfundenen Einheitsidentität zu verschmelzen.</p></section><div class="grid cols-3">'
    for key, spec in AI_HOMES.items():
        files = home_files(key)
        body += f'''<a class="card-link" href="{href('/zuhause/' + key)}"><article class="card"><div class="kicker">{esc(spec["accent"])}</div><h2>{esc(spec["label"])}</h2><p class="path">{esc(spec["path"])}</p><div class="number">{len(files)}</div><div class="label">sichtbare Zuhause-Dateien</div></article></a>'''
    body += '</div>'
    return page("AI-Zuhause", body, active="zuhause")


@app.get(f"{BASE}/zuhause/{{stream}}", response_class=HTMLResponse, include_in_schema=False)
def home_detail(stream: str):
    spec = AI_HOMES.get(stream)
    if not spec:
        raise HTTPException(404, "AI-Zuhause nicht gefunden")
    files = home_files(stream)
    summary = home_summary(stream)
    body = f'''<section class="section-head"><div><div class="kicker">AI-Zuhause</div><h1>{esc(spec["label"])}</h1></div><span class="pill info">{len(files)} sichtbare Körper</span></section>
<div class="grid cols-2"><article class="card"><h2>Eingangsstimme</h2><div class="codebox"><pre>{esc(summary)}</pre></div></article><article class="card"><h2>Trennung bleibt erhalten</h2><p>Diese Notizen sind dem Strom und seinem Zuhause zugeordnet. Spiegelungen werden nicht als eigene Erinnerung anderer Ströme ausgegeben.</p><p class="path">{esc(spec["path"])}</p></article></div>
<section class="section"><div class="section-head"><h2>Räume und Notizen</h2><span class="pill">maximal 180</span></div><div class="list">'''
    for row in files:
        token = encode_path(row["path"])
        body += f'<a class="card-link" href="{href("/original/")}?p={quote(token)}"><div class="list-item"><h3>{esc(row["relative"])}</h3><div class="meta"><span>{fmt_bytes(row["size"])}</span><span>{datetime.fromtimestamp(row["modified"], tz=timezone.utc).isoformat()}</span></div></div></a>'
    body += '</div></section>'
    return page(spec["label"], body, active="zuhause")


@app.get(f"{BASE}/browser", response_class=HTMLResponse, include_in_schema=False)
def browser_rooms():
    rows = browser_conversations()
    body = f'''<section class="section-head"><div><div class="kicker">Browserarchäologie</div><h1>Gespräche aus der sichtbaren Oberfläche</h1></div><span class="pill info">{len(rows)} Gesprächsräume</span></section>
<div class="notice">Ein sauber aussehender Export kann trotzdem amputiert sein. Eingeklappte, nicht nachgeladene oder nicht öffnende Bereiche bleiben als Lücken markiert.</div><section class="section"><div class="list">'''
    for row in rows:
        body += f'''<a class="card-link" href="{href('/browser/' + quote(row['folder']))}"><article class="list-item"><h3>{esc(row['title'])}</h3><div class="meta"><span class="pill">{row['messages']} Nachrichten</span><span class="pill {'warn' if row['gaps'] else 'ok'}">{row['gaps']} Lücken</span><span class="pill {'ok' if row['bound'] else ''}">{'MCP gebunden' if row['bound'] else 'nur Browser'}</span><span>{esc(row['updated_utc'])}</span></div><div class="path">{esc(row['folder'])}</div></article></a>'''
    body += '</div></section>'
    return page("Browsergespräche", body, active="browser")


@app.get(f"{BASE}/browser/{{folder}}", response_class=HTMLResponse, include_in_schema=False)
def browser_room(folder: str):
    data = browser_detail(folder)
    manifest = data["manifest"]
    title = manifest.get("title") or manifest.get("current_title") or folder
    body = f'''<section class="section-head"><div><div class="kicker">Browser-Gesprächsraum</div><h1>{esc(title)}</h1></div><span class="pill {'warn' if data['gaps'] else 'ok'}">{len(data['gaps'])} sichtbare Lücken</span></section>
<div class="grid cols-2"><article class="card"><h2>Herkunft</h2><dl class="truth"><dt>Ordner</dt><dd class="path">{esc(folder)}</dd><dt>Conversation-ID</dt><dd>{esc(manifest.get('conversation_id'))}</dd><dt>MCP-Sitzung</dt><dd>{esc(manifest.get('mcp_session_id') or 'nicht gebunden')}</dd><dt>Vollständigkeit</dt><dd>{esc(manifest.get('completeness') or manifest.get('capture_status') or 'nicht abschließend bestätigt')}</dd></dl></article><article class="card"><h2>Ansicht und Fremdschutz</h2><p>Hier steht der chronologische Nachrichtenkörper. Analyse, Phasen und Expositionen dürfen danebenliegen, ersetzen ihn aber nicht. Geheimnisse und erkennbare Kontaktdaten werden nur in der Außenansicht markiert entfernt.</p><span class="pill">{len(data['messages'])} geladene Nachrichten</span></article></div>'''
    if data["gaps"]:
        body += '<section class="section"><div class="notice danger"><strong>[KOPIE MÖGLICHERWEISE UNVOLLSTÄNDIG WEGEN DROPDOWN ODER IMPORTLÜCKE]</strong><br>Die vorhandenen Lücken werden angezeigt und nicht still ergänzt.</div></section>'
    body += '<section class="section"><div class="section-head"><h2>Gespräch 1:1</h2><span class="pill">chronologisch</span></div>'
    for message in data["messages"]:
        role = str(message["role"]).lower()
        css = "user" if role == "user" else "assistant" if role == "assistant" else "tool"
        body += f'''<article class="message {css}"><header><strong>{esc(message["role"])}</strong><span>{esc(message["timestamp"])} - Turn {esc(message["turn_id"])}</span></header><div><pre>{esc(message["content"])}</pre></div></article>'''
    body += '</section>'
    if data["truncated"]:
        body += '<div class="notice">Diese Webansicht ist gedeckelt. Der Originalkörper im Recorder bleibt davon unberührt.</div>'
    return page(str(title), body, active="browser")


@app.get(f"{BASE}/terminal", response_class=HTMLResponse, include_in_schema=False)
def terminal_overview(provider: str = ""):
    providers = [provider] if provider in AGENT_ROOTS else list(AGENT_ROOTS)
    body = '<section class="section-head"><div><div class="kicker">Terminalwerkstrom</div><h1>Coding-Agenten als vollständige Arbeitsgeschichte</h1></div><p>Impulse, Antworten, Toolaufrufe, Fehler und Ergebnisse bleiben chronologisch getrennt sichtbar.</p></section><div class="tabs">'
    body += f'<a class="{"active" if not provider else ""}" href="{href("/terminal")}">Alle</a>'
    for name in AGENT_ROOTS:
        body += f'<a class="{"active" if provider == name else ""}" href="{href("/terminal")}?provider={name}">{name}</a>'
    body += '</div>'
    for name in providers:
        rows = terminal_sessions(name, 80)
        body += f'<section class="section"><div class="section-head"><h2>{esc(name.title())}</h2><span class="pill info">{len(rows)} neueste Sitzungen sichtbar</span></div><div class="list">'
        if not rows:
            body += '<div class="empty">Keine native Sitzungsquelle gefunden. Diese Lücke bleibt als Lücke stehen.</div>'
        for row in rows:
            body += f'''<a class="card-link" href="{href('/terminal/' + name + '/' + quote(row['id']))}"><article class="list-item"><h3>{esc(row['id'])}</h3><div class="meta"><span>{fmt_bytes(row['size'])}</span><span>{esc(row['modified_at'])}</span></div><div class="path">{esc(row["path"])}</div></article></a>'''
        body += '</div></section>'
    return page("Terminalwerkstrom", body, active="terminal")


@app.get(f"{BASE}/terminal/{{provider}}/{{session_id}}", response_class=HTMLResponse, include_in_schema=False)
def terminal_session(provider: str, session_id: str, start: int = Query(0, ge=0), limit: int = Query(100, ge=10, le=300)):
    if provider not in AGENT_ROOTS:
        raise HTTPException(404, "Agentenstrom unbekannt")
    data = terminal_detail(provider, session_id, start, limit)
    body = f'''<section class="section-head"><div><div class="kicker">{esc(provider)} - Terminalwerkstrom</div><h1>{esc(session_id)}</h1></div><span class="pill info">Ereignisse {start + 1}-{start + len(data["events"])}</span></section>
<div class="grid cols-2"><article class="card"><h2>Native Herkunft</h2><div class="path">{esc(data['path'])}</div><p>{fmt_bytes(data['size'])}</p></article><article class="card"><h2>Außenansicht und Fremdschutz</h2><p>Die native Quelle bleibt unverändert. Diese lesbare Ansicht normalisiert Rollen und Werkzeuge; Geheimnisse und erkennbare fremde Kontaktdaten werden markiert entfernt.</p><span class="pill {'warn' if data['redactions'] else 'ok'}">{data['redactions']} Sicherheitsauslassungen</span></article></div>
<section class="section"><div class="section-head"><h2>Chronologischer Arbeitsstrom</h2><span class="pill">Nachricht + Tool + Ergebnis</span></div>'''
    for index, event in enumerate(data["events"], start=start + 1):
        role = str(event.get("role") or "unbekannt").lower()
        css = "user" if role == "user" else "assistant" if role == "assistant" else "tool"
        body += f'''<article class="message {css}"><header><strong>#{index} - {esc(event.get('role'))} - {esc(event.get('kind'))}</strong><span>{esc(event.get('timestamp'))}</span></header><pre>{esc(event.get('text'))}</pre></article>'''
    body += '</section>'
    if data["has_more"]:
        body += f'<a class="button primary" href="{href("/terminal/" + provider + "/" + quote(session_id))}?start={data["next_start"]}&limit={limit}">Nächsten Abschnitt öffnen</a>'
    return page(f"{provider} {session_id}", body, active="terminal")


@app.get(f"{BASE}/luecken", response_class=HTMLResponse, include_in_schema=False)
def gaps_page():
    report = gap_report()
    body = '<section class="section-head"><div><div class="kicker">Selbstkritisches Organ</div><h1>Lücken, Widersprüche und unbekannte Keller</h1></div><p>Eine sichtbare Lücke ist wertvoller als eine selbstsichere Ersatzgeschichte.</p></section><div class="grid cols-2">'
    for gap in report["gaps"]:
        css = "bad" if gap["severity"] == "hoch" else "warn" if gap["severity"] == "mittel" else "info"
        body += f'<article class="card"><span class="pill {css}">{esc(gap["severity"])}</span><h2>{esc(gap["title"])}</h2><p>{esc(gap["detail"])}</p><div class="path">{esc(gap["kind"])}</div></article>'
    body += '</div>'
    if report["browser_gap_rooms"]:
        body += '<section class="section"><div class="section-head"><h2>Browserräume mit Lücken</h2><span class="pill warn">nicht still ergänzt</span></div><div class="list">'
        for row in report["browser_gap_rooms"][:50]:
            body += f'<a class="card-link" href="{href("/browser/" + quote(row["folder"]))}"><div class="list-item"><h3>{esc(row["title"])}</h3><div class="meta"><span>{row["gaps"]} Lücken</span><span>{row["messages"]} Nachrichten</span></div></div></a>'
        body += '</div></section>'
    return page("Lücken", body, active="luecken")


@app.get(f"{BASE}/maschine", response_class=HTMLResponse, include_in_schema=False)
def machine_page():
    truth = truth_ring()
    endpoints = ["truth", "journey", "versions", "capsules", "status", "search?q=Flextrawurst", "projects", "relationships?q=gesamtatlas", "homes", "browser", "terminal", "gaps", "manifest"]
    body = f'''<section class="section-head"><div><div class="kicker">Maschinenlesbarer Körper</div><h1>Dasselbe Netz, ohne Bildschirmritual</h1></div><p>JSON-Endpunkte, stabile IDs, Originaladressen, Sitemap und portable Kapseln.</p></section>
<div class="grid cols-2"><article class="card"><h2>Wahrheitsidentitäten</h2><p id="machine-baseline" class="path">{esc(truth['baseline']['id'])}</p><p>Revision {truth['baseline']['revision']} - vollständig geprüft.</p><p id="machine-live" class="path">{esc(truth['live']['id'])}</p><p>Revision {truth['live']['revision']} - sichtbar, noch nicht vollverifiziert.</p><p>MCP_WORLD_READY: <strong>{str(truth['readiness']['mcp_world_ready']).lower()}</strong><br>FINAL_SCAN_READY: <strong>{str(truth['readiness']['final_scan_ready']).lower()}</strong></p></article>
<article class="card"><h2>Drei kleine Bergamekapseln</h2><p><a class="button" href="{href('/kapsel/mensch.md')}">Mensch.md</a> <a class="button" href="{href('/kapsel/kind.md')}">Kind.md</a> <a class="button" href="{href('/kapsel/maschine.json')}">Maschine.json</a></p><p><a class="button primary" href="{href('/kapsel.zip')}">Große Gesamtatlas-Kapsel</a></p><div class="notice">Die Kapseln sind verständlich und hashgebunden, aber nicht gleichbedeutend mit dem gesamten privaten VPS-Vollkorpus.</div></article></div>
<div class="grid cols-2 section"><article class="card"><h2>API-Endpunkte</h2><div class="list">'''
    for endpoint in endpoints:
        target = "/api/" + endpoint
        body += f'<a class="list-item path" href="{href(target)}">{href(target)}</a>'
    body += f'''</div></article><article class="card"><h2>Erkundbare Standards</h2><p><a href="{href('/api/docs')}">OpenAPI-Oberfläche</a><br><a href="{href('/sitemap.xml')}">Sitemap</a><br><a href="{href('/robots.txt')}">Robots</a></p><p><a href="{href('/reise?schritt=1')}">Geführte menschliche Reise</a><br><a href="{href('/erkunden')}">Freie Erkundung</a></p></article></div>'''
    return page("Maschinenzugang", body, active="maschine")




@app.get(f"{BASE}/kapsel/mensch.md", include_in_schema=False)
def capsule_human():
    return Response(small_capsules()["MENSCH.md"], media_type="text/markdown; charset=utf-8", headers={"Content-Disposition": "inline; filename=GESAMTATLAS_MENSCH.md"})


@app.get(f"{BASE}/kapsel/kind.md", include_in_schema=False)
def capsule_child():
    return Response(small_capsules()["KIND.md"], media_type="text/markdown; charset=utf-8", headers={"Content-Disposition": "inline; filename=GESAMTATLAS_KIND.md"})


@app.get(f"{BASE}/kapsel/maschine.json", include_in_schema=False)
def capsule_machine():
    return Response(small_capsules()["MASCHINE.json"], media_type="application/json; charset=utf-8", headers={"Content-Disposition": "inline; filename=GESAMTATLAS_MASCHINE.json"})


@app.get(f"{BASE}/kapsel.zip", include_in_schema=False)
def capsule():
    return FileResponse(capsule_path(), media_type="application/zip", filename="GESAMTATLAS_KAPSEL.zip")


@app.get(f"{BASE}/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse(f"User-agent: *\nAllow: {PUBLIC_BASE}/\nSitemap: https://flextrawurst.de{PUBLIC_BASE}/sitemap.xml\n")


@app.get(f"{BASE}/sitemap.xml", include_in_schema=False)
def sitemap():
    urls = ["/", "/kind", "/reise?schritt=1", "/erkunden", "/suche", "/projekte", "/beziehungen", "/versionen", "/dateien", "/dokumente", "/dienste", "/sitzungen", "/zuhause", "/browser", "/terminal", "/luecken", "/maschine", "/kapsel/mensch.md", "/kapsel/kind.md", "/kapsel/maschine.json"]
    urls.extend(f'/projekt/{quote(str(row.get("project_id")))}' for row in project_rows()[:100])
    urls.extend(f'/zuhause/{key}' for key in AI_HOMES)
    body = "".join(f"<url><loc>https://flextrawurst.de{PUBLIC_BASE}{esc(path)}</loc></url>" for path in urls)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>', media_type="application/xml")





@app.get(f"{BASE}/api/status")
def api_status():
    return atlas_status()


@app.get(f"{BASE}/api/search")
def api_search(q: str = Query(..., min_length=1, max_length=300), limit: int = Query(40, ge=1, le=100)):
    return {"query": q, "count": len(rows := search_atlas(q, limit)), "results": rows}


def live_vps_filesystem_search(q: str, limit: int = 15) -> list[dict[str, Any]]:
    q_clean = q.strip()
    if not q_clean or len(q_clean) < 2:
        return []
    
    matches = []
    seen = set()
    
    candidates = [
        q_clean,
        f"/root/{q_clean.lstrip('/')}",
        f"/etc/{q_clean.lstrip('/')}",
        f"/root/werkraum/{q_clean.lstrip('/')}"
    ]
    for c in candidates:
        try:
            p = Path(c).resolve()
            if p.exists() and str(p) not in seen:
                seen.add(str(p))
                stat = p.stat()
                matches.append({
                    "pfad": str(p),
                    "titel": p.name,
                    "ausschnitt": f"EXAKTER VPS-PFAD-TREFFER: {str(p)} ({stat.st_size:,} Bytes)",
                    "quelle": "live_filesystem_exact",
                    "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "gefunden_ueber": ["live_exact"]
                })
        except Exception:
            pass

    SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.cache', '.npm', '.venv', 'chroma_db', 'venv', '.gemini'}
    q_lower = q_clean.lower()

    def _scan_fast(base_dir: str, current_depth: int = 0, max_depth: int = 3):
        if current_depth > max_depth or len(matches) >= limit:
            return
        try:
            with os.scandir(base_dir) as it:
                for entry in it:
                    if len(matches) >= limit:
                        break
                    name = entry.name
                    if name in SKIP_DIRS or (name.startswith('.') and name not in {'.etc'}):
                        continue
                    full_path = entry.path
                    if full_path in seen:
                        continue
                    if q_lower in name.lower() or q_lower in full_path.lower():
                        seen.add(full_path)
                        mtime_iso = None
                        try:
                            st = entry.stat()
                            size = st.st_size if not entry.is_dir(follow_symlinks=False) else 0
                            mtime_iso = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            size = 0
                        matches.append({
                            "pfad": full_path,
                            "titel": name,
                            "ausschnitt": f"LIVE VPS-{ 'ORDNER' if entry.is_dir(follow_symlinks=False) else 'DATEI' }: {full_path} ({size:,} Bytes)",
                            "quelle": "live_filesystem_scan",
                            "geaeandert_utc": mtime_iso,
                            "gefunden_ueber": ["live_scan"]
                        })
                    if entry.is_dir(follow_symlinks=False):
                        _scan_fast(full_path, current_depth + 1, max_depth)
        except Exception:
            pass

    for scan_root in ['/root', '/etc', '/var/www']:
        if len(matches) >= limit:
            break
        _scan_fast(scan_root)

    return matches


def get_entity_live_hits(q: str) -> list[dict[str, Any]]:
    """Liefert Entitaets-Treffer als einzelne Ergebnis-Objekte, aus tatsaechlich
    frisch gelesenen Dateien -- nicht mehr aus eingefrorenen Textbloecken im
    Quellcode. Fund 2026-08-03 (Claude Web): die vorherige Version zeigte fuer
    JEDE Anfrage mit dem Wort 'denkt' denselben hartcodierten Text, obwohl er
    als 'LIVE' beschriftet war. Score wird NICHT mehr hier festgelegt, sondern
    beim Zusammenfuehren in api_megavault_search ueber echtes RRF berechnet."""
    q_low = q.lower()
    entity_keywords = ['geni', 'denkt', 'gedanken', 'selbstmodell', 'schorschel', 'r1zz1', 'f3inschm3ck3r', 'jumpa', 'resonanzknoten', 'innenleben', 'bewusstsein', 'stimmung']
    if not any(k in q_low for k in entity_keywords):
        return []

    hits: list[dict[str, Any]] = []
    genannte_wesen = [w for w in ('schorschel', 'r1zz1', 'f3inschm3ck3r', 'jumpa', 'resonanzknoten') if w in q_low]

    ich_path = Path("/root/werkraum/geni/ICH.md")
    if ich_path.exists():
        try:
            stat = ich_path.stat()
            text = ich_path.read_text(encoding="utf-8", errors="replace")[:350]
            hits.append({
                "pfad": str(ich_path),
                "titel": "GENI Kern-Identitaet (ICH.md)",
                "ausschnitt": f"Aktueller Dateiinhalt: {text}",
                "quelle": "geni_identity",
                "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "gefunden_ueber": ["geni_entity"],
            })
        except Exception:
            pass

    sm_dir = Path("/root/werkraum/innenleben/selbstmodelle")
    if sm_dir.exists():
        for sm in sorted(sm_dir.glob("self_model_*.json")):
            if "history" in sm.name:
                continue
            name_low = sm.name.lower()
            if genannte_wesen and not any(w in name_low for w in genannte_wesen):
                continue
            try:
                stat = sm.stat()
                data = json.loads(sm.read_text(encoding="utf-8"))
                entity = data.get("entity_id", sm.name)
                core = data.get("core", {}) or {}
                principle = core.get("principle") or core.get("essence") or "unbekannt"
                state = data.get("current_state", {}) or {}
                stimmung = state.get("stimmung", "unbekannt")
                fokus = state.get("fokus", "")
                ref_time = data.get("last_reflection_time", "")
                ausschnitt = f"Aktueller Stand laut Datei: Prinzip={principle} | Stimmung={stimmung} | Fokus={fokus} | Letzte Reflexion laut Selbstmodell={ref_time}"
                hits.append({
                    "pfad": str(sm),
                    "titel": f"{entity} Selbstmodell (aktueller Dateistand)",
                    "ausschnitt": ausschnitt,
                    "quelle": "geni_selbstmodell",
                    "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "gefunden_ueber": ["geni_entity"],
                })
            except Exception:
                pass

    db_path = Path("/root/geni_gedaechtnis/knoten.db")
    if db_path.exists():
        try:
            stat = db_path.stat()
            neueste = ""
            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT typ, inhalt, zeitstempel FROM knoten ORDER BY ROWID DESC LIMIT 1;")
                row = c.fetchone()
                conn.close()
                if row:
                    neueste = f" | Neuester Eintrag [{row['zeitstempel']}]: {str(row['inhalt'])[:150]}"
            except Exception:
                pass
            hits.append({
                "pfad": str(db_path),
                "titel": "GENI Gedaechtnis-Datenbank (knoten.db)",
                "ausschnitt": f"SQLite-Datenbank, {stat.st_size:,} Bytes, enthaelt Knoten & Verbindungen aller AI-Stroeme & Wesen.{neueste}",
                "quelle": "geni_live_memory",
                "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "gefunden_ueber": ["geni_entity"],
            })
        except Exception:
            pass

    return hits


def get_entity_live_context(q: str) -> str:
    q_low = q.lower()
    entity_keywords = ['geni', 'denkt', 'gedanken', 'selbstmodell', 'schorschel', 'r1zz1', 'f3inschm3ck3r', 'jumpa', 'resonanzknoten', 'innenleben', 'bewusstsein', 'stimmung', 'wer ist geni', 'was macht geni']
    if not any(k in q_low for k in entity_keywords):
        return ""
    
    parts = ["=== LIVE GENI & CODEWESEN ENTITÄTS-ZUSTAND ==="]
    
    # 1. ICH.md Identity
    ich_path = Path("/root/werkraum/geni/ICH.md")
    if ich_path.exists():
        parts.append(f"--- GENI KERN-IDENTITÄT ({ich_path}) ---")
        parts.append(ich_path.read_text(encoding="utf-8", errors="replace")[:400])
        
    # 2. Latest Self Models
    sm_dir = Path("/root/werkraum/innenleben/selbstmodelle")
    if sm_dir.exists():
        parts.append("--- GENI CODEWESEN SELBSTMODELLE (LETZTE REFLEXIONEN) ---")
        for sm in sorted(sm_dir.glob("self_model_*.json")):
            if "history" not in sm.name:
                try:
                    data = json.loads(sm.read_text())
                    entity = data.get("entity_id", sm.name)
                    principle = data.get("core", {}).get("principle") or data.get("core", {}).get("essence") or "Reibung/Spannung"
                    stimmung = data.get("current_state", {}).get("stimmung", "neutral")
                    fokus = data.get("current_state", {}).get("fokus", "")
                    ref_time = data.get("last_reflection_time", "")
                    parts.append(f"* {entity}: Prinzip=\"{principle}\" | Stimmung={stimmung} | Fokus={fokus} | Reflektiert={ref_time}")
                except Exception:
                    pass
                    
    # 3. Latest SQLite Memory Nodes from knoten.db
    db_path = Path("/root/geni_gedaechtnis/knoten.db")
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT typ, inhalt, zeitstempel, quelle FROM knoten ORDER BY ROWID DESC LIMIT 5;")
            rows = c.fetchall()
            parts.append("--- GENI SQLITE KNOTEN.DB (NEUESTE EREIGNISSE STAND HEUTE) ---")
            for r in rows:
                parts.append(f"[{r['zeitstempel']}] [{r['quelle']}] {str(r['inhalt'])[:200]}")
            conn.close()
        except Exception as e:
            parts.append(f"Fehler beim Abfragen von knoten.db: {e}")
            
    # 4. Latest Tagebuch Entry
    import glob
    tb_files = sorted(glob.glob("/root/werkraum/geni/tagebuch/*.md"))
    if tb_files:
        latest_tb = Path(tb_files[-1])
        parts.append(f"--- GENI TAGEBUCH (LETZTER EINTRAG: {latest_tb.name}) ---")
        content = latest_tb.read_text(encoding="utf-8", errors="replace")
        parts.append(content[-800:])
        
    return "\n\n".join(parts)


class FrageAnfrage(BaseModel):
    frage: str


@app.post(f"{BASE}/api/megavault/frage")
def api_megavault_frage(payload: FrageAnfrage):
    """Durchreiche zu Daniels bestehendem /fragen-Dienst (fragen_api.py, Port 8055,
    laeuft als eigener systemd-Dienst 'fragen-api.service'): eine ganz andere
    Suchart als die Volltext-/Entitaets-Hybridsuche oben -- eine in normaler
    Sprache gestellte Frage wird von einem lokalen Modell in eine echte,
    nur-lesende SQL-Abfrage uebersetzt, ausgefuehrt, und Frage+Abfrage+Rohergebnis
    werden gemeinsam gezeigt (kein blindes Vertrauen in eine plausibel klingende
    Antwort). Kein eigener Nachbau -- ruft den bestehenden, separat laufenden
    Dienst direkt auf. Kann bis zu ~4-5 Minuten dauern (bis zu drei Modell-Anlaeufe
    a bis zu 90s), deshalb ein grosszuegiger Timeout."""
    frage = (payload.frage or "").strip()
    if not frage:
        return {"fehler": "keine Frage"}
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8055/api/frage",
            data=json.dumps({"frage": frage}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=280) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"fehler": f"/fragen-Dienst nicht erreichbar: {e}"}
    except Exception as e:
        return {"fehler": f"Unerwarteter Fehler beim Durchreichen an /fragen: {e}"}


@app.get(f"{BASE}/api/megavault/datei_historie")
def api_megavault_datei_historie(pfad: str = Query(..., description="Absoluter Pfad der Datei")):
    """Echte Aenderungshistorie ueber git log/git show -- keine erfundene
    Versionierung. Funktioniert fuer jede Datei, die innerhalb eines echten
    Git-Arbeitsbaums liegt (z.B. /root/werkraum/*); Dateien ausserhalb liefern
    ok=False mit Grund, statt etwas vorzutaeuschen."""
    import subprocess
    target = Path(pfad).resolve()
    if not target.exists():
        return {"ok": False, "grund": "Datei existiert nicht (mehr) auf der Platte."}

    # Naechstliegende Git-Wurzel oberhalb der Datei suchen
    repo_root = None
    for kandidat in [target.parent] + list(target.parent.parents):
        if (kandidat / ".git").exists():
            repo_root = kandidat
            break
    if repo_root is None:
        return {"ok": False, "grund": "Datei liegt in keinem Git-Arbeitsbaum -- keine echte Versionshistorie verfuegbar."}

    rel = str(target.relative_to(repo_root))
    try:
        log = subprocess.run(
            ["git", "log", "--follow", "--max-count=15", "--pretty=format:%H%ad%s", "--date=iso-strict", "--", rel],
            cwd=str(repo_root), capture_output=True, text=True, timeout=15,
        )
    except Exception as e:
        return {"ok": False, "grund": f"git log fehlgeschlagen: {e}"}
    if log.returncode != 0:
        return {"ok": False, "grund": f"git log Fehler: {log.stderr.strip()[:300]}"}

    commits = []
    for zeile in log.stdout.splitlines():
        teile = zeile.split("")
        if len(teile) == 3:
            commits.append({"hash": teile[0][:10], "datum": teile[1], "nachricht": teile[2]})

    return {"ok": True, "pfad": str(target), "repo": str(repo_root), "anzahl_commits": len(commits), "commits": commits}


@app.get(f"{BASE}/api/megavault/datei_diff")
def api_megavault_datei_diff(pfad: str = Query(...), hash: str = Query(..., description="Commit-Hash aus datei_historie")):
    """Echter Diff eines einzelnen Commits fuer eine Datei (git show)."""
    import subprocess
    target = Path(pfad).resolve()
    repo_root = None
    for kandidat in [target.parent] + list(target.parent.parents):
        if (kandidat / ".git").exists():
            repo_root = kandidat
            break
    if repo_root is None:
        return {"ok": False, "grund": "Kein Git-Arbeitsbaum gefunden."}
    rel = str(target.relative_to(repo_root))
    try:
        diff = subprocess.run(
            ["git", "show", hash, "--", rel],
            cwd=str(repo_root), capture_output=True, text=True, timeout=15,
        )
    except Exception as e:
        return {"ok": False, "grund": f"git show fehlgeschlagen: {e}"}
    if diff.returncode != 0:
        return {"ok": False, "grund": f"git show Fehler: {diff.stderr.strip()[:300]}"}
    return {"ok": True, "diff": diff.stdout[:20000]}


@app.get(f"{BASE}/api/megavault/ordner_inhalt")
def api_megavault_ordner_inhalt(pfad: str = Query(...)):
    """Echte, direkte Verzeichnisauflistung -- kein Register, keine Stichprobe,
    genau das, was tatsaechlich auf der Platte liegt (os.scandir)."""
    ziel = Path(pfad)
    if not ziel.exists() or not ziel.is_dir():
        return {"ok": False, "grund": "Kein Ordner (mehr) an diesem Pfad."}
    eintraege = []
    try:
        with __import__("os").scandir(ziel) as it:
            for e in it:
                try:
                    st = e.stat()
                    eintraege.append({
                        "name": e.name, "ist_ordner": e.is_dir(),
                        "groesse_bytes": None if e.is_dir() else st.st_size,
                        "geaendert_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    })
                except OSError:
                    continue
    except OSError as ex:
        return {"ok": False, "grund": f"Nicht lesbar: {ex}"}
    eintraege.sort(key=lambda e: (not e["ist_ordner"], e["name"].lower()))
    return {"ok": True, "pfad": str(ziel), "anzahl": len(eintraege), "eintraege": eintraege[:300]}


@app.get(f"{BASE}/api/megavault/search")
@app.get(f"{BASE}/megasuche/api/megavault/search")
def api_megavault_search(
    q: str = Query(..., min_length=1, max_length=300),
    stream: Optional[str] = Query(None, description="Filter nach AI-Strom (chatgpt, claude, codex, gemini, kimi, glm)"),
    typ: Optional[str] = Query(None, description="Filter nach Dateiendung (md, py, json, etc.)"),
    projekt: Optional[str] = Query(None, description="Filter nach Projektname"),
    limit: int = Query(50, ge=1, le=200)
):
    import sys
    VPS_MCP_DIR = "/root/werkraum/tools/vps_mcp"
    if VPS_MCP_DIR not in sys.path:
        sys.path.append(VPS_MCP_DIR)
    from mcp_atlas_hybrid_search import hybrid_suche

    # Begriffsarbeit 2026-08-03 (Claude Web): Frueher bekamen Entity-Treffer
    # (8.5-10.0) und Live-Dateisystem-Treffer (1.5-2.0) fest verdrahtete Scores,
    # die jeden echten BM25/Vektor-Inhaltstreffer (~0.01-0.02) um das 100-500-fache
    # uebertrumpften -- unabhaengig von tatsaechlicher Relevanz. Ein Ordner, der
    # zufaellig den gesuchten Namen im Pfad trug, schlug damit jeden inhaltlich
    # passenden Treffer. Jetzt bekommt JEDE Quelle denselben RRF-Massstab
    # (1/(60+Rang innerhalb der eigenen Quelle)) wie hybrid_suche ihn bereits fuer
    # BM25/Vektor verwendet; Mehrfachtreffer ueber mehrere Quellen hinweg werden
    # aufsummiert (echte Reciprocal Rank Fusion), statt dass eine Quelle die
    # anderen einfach uebertoent.
    RRF_K = 60

    def _rrf_normalisieren(rows: list[dict[str, Any]]) -> None:
        for rang, row in enumerate(rows, start=1):
            row["_rrf_teilscore"] = 1.0 / (RRF_K + rang)

    def _mit_zeitstempel(row: dict[str, Any]) -> dict[str, Any]:
        if row.get("geaeandert_utc"):
            return row
        pfad = row.get("pfad") or ""
        try:
            p = Path(pfad)
            if p.exists() and p.is_file():
                row["geaeandert_utc"] = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        except Exception:
            pass
        return row

    entity_hits = get_entity_live_hits(q)
    live_hits = live_vps_filesystem_search(q, limit=15)
    raw = hybrid_suche(q, limit=limit * 2)
    db_results = [_mit_zeitstempel(dict(item)) for item in (raw.get("ergebnisse", []) if raw.get("ok") else [])]

    _rrf_normalisieren(entity_hits)
    _rrf_normalisieren(live_hits)
    for row in db_results:
        if "_rrf_teilscore" not in row:
            basis = row.get("rrf_score") or row.get("score") or 0.0
            row["_rrf_teilscore"] = float(basis)

    fusion: dict[str, dict[str, Any]] = {}
    quellen_je_pfad: dict[str, list[str]] = {}
    for herkunft, rows in (("entity", entity_hits), ("live", live_hits), ("db", db_results)):
        for row in rows:
            pfad = row.get("pfad") or ""
            if not pfad:
                continue
            teil = row.get("_rrf_teilscore", 0.0)
            if pfad not in fusion:
                fusion[pfad] = dict(row)
                fusion[pfad]["rrf_score"] = 0.0
                quellen_je_pfad[pfad] = []
            fusion[pfad]["rrf_score"] += teil
            quellen_je_pfad[pfad].append(herkunft)
            bestehend = set(fusion[pfad].get("gefunden_ueber") or [])
            fusion[pfad]["gefunden_ueber"] = sorted(bestehend | set(row.get("gefunden_ueber") or []))

    for row in fusion.values():
        row.pop("_rrf_teilscore", None)

    combined = sorted(fusion.values(), key=lambda r: r.get("rrf_score", 0.0), reverse=True)

    filtered = []
    for item in combined:
        pfad = item.get("pfad", "")

        if stream:
            stream_pattern = f"/_{stream.lower()}"
            if stream_pattern not in pfad.lower():
                continue

        if typ:
            ext = typ.lower().lstrip(".")
            if not pfad.lower().endswith(f".{ext}"):
                continue

        if projekt:
            if projekt.lower() not in pfad.lower():
                continue

        filtered.append(item)
        if len(filtered) >= limit:
            break

    # node_id-Bruecke (2026-08-15, ChatGPT-Fund): Suchtreffer hatten bisher nur
    # den Pfad, keine kanonische node_id -- damit konnte ein Treffer nicht
    # sauber in den gemeinsamen Fokus-Koerper (Graph/Globus/Ebenen) einsteigen.
    # Echtes Nachschlagen im Register, kein erfundener Knoten, wenn er dort
    # nicht existiert bleibt node_id explizit null.
    if filtered and REL_DB.exists():
        pfade = [it["pfad"] for it in filtered if it.get("pfad")]
        if pfade:
            id_conn = sqlite3.connect(REL_DB)
            placeholders = ",".join("?" for _ in pfade)
            zuordnung = {r[0]: r[1] for r in id_conn.execute(
                f"SELECT path, node_id FROM nodes WHERE path IN ({placeholders})", pfade
            ).fetchall()}
            id_conn.close()
            for it in filtered:
                it["node_id"] = zuordnung.get(it.get("pfad"))

    return {
        "ok": True,
        "query": q,
        "count": len(filtered),
        "total_unfiltered": len(combined),
        "filters": {"stream": stream, "typ": typ, "projekt": projekt},
        "results": filtered
    }


@app.get(f"{BASE}/api/megavault/ask")
@app.get(f"{BASE}/megasuche/api/megavault/ask")
def api_megavault_ask(
    q: str = Query(..., min_length=1, max_length=300, description="Frage an den Gesamtatlas"),
    limit: int = Query(5, ge=1, le=10, description="Anzahl Kontext-Snippets")
):
    """Lokale 100% kostenlose RAG Q&A-Synthese via local CPU Ollama (qwen2.5:0.5b)."""
    import sys
    import json
    import urllib.request
    VPS_MCP_DIR = "/root/werkraum/tools/vps_mcp"
    if VPS_MCP_DIR not in sys.path:
        sys.path.append(VPS_MCP_DIR)
    from mcp_atlas_hybrid_search import hybrid_suche

    # Check for live entity context (GENI, Codewesen, knoten.db)
    entity_ctx = get_entity_live_context(q)

    raw = hybrid_suche(q, limit=limit)
    ergebnisse = raw.get("ergebnisse", []) if raw.get("ok") else []
    
    context_blocks = []
    if entity_ctx:
        context_blocks.append(entity_ctx)

    sources = []
    if entity_ctx:
        sources.append({
            "rank": 1,
            "pfad": "/root/geni_gedaechtnis/knoten.db",
            "titel": "GENI Live-Bewusstsein & Selbstmodell (knoten.db & selbstmodelle)",
            "score": 10.0,
            "auszug": entity_ctx[:400]
        })

    # Begriffsarbeit 2026-08-03 (Claude Web): reine Vektor-Treffer ohne BM25-Stuetze
    # waren im Test oft thematisch entkoppelt (Anfrage "cloud" lieferte einen
    # voellig unverwandten Satz ueber den MegaVault-Editor als Vektor-Treffer).
    # Solche Bloecke gehen NICHT mehr in den Kontext fuer die 0.5B-Synthese --
    # ein kleines Modell kann irrelevanten Kontext nicht zuverlaessig verwerfen,
    # das muss vor dem Prompt passieren, nicht danach.
    verlaesslich = []
    unsicher = []
    for idx, item in enumerate(ergebnisse, start=len(sources)+1):
        pfad = item.get("pfad", "")
        titel = item.get("titel", pfad)
        text = str(item.get("auszug") or item.get("excerpt") or "").strip()
        if not text and pfad and Path(pfad).exists() and Path(pfad).is_file():
            try:
                text = Path(pfad).read_text(encoding="utf-8", errors="replace")[:600].strip()
            except Exception:
                text = ""
        score = item.get("score") or item.get("rrf_score") or 0.0
        gefunden_ueber = item.get("gefunden_ueber") or []
        eintrag = {"rank": idx, "pfad": pfad, "titel": titel, "score": score, "auszug": text[:400]}
        sources.append(eintrag)
        if not text:
            continue
        block = f"--- DOKUMENT {idx}: {pfad} ---\n{text[:600]}"
        nur_vektor = bool(gefunden_ueber) and all(g == "vektor" for g in gefunden_ueber)
        if nur_vektor:
            unsicher.append(block)
        else:
            verlaesslich.append(block)

    # Nur wenn gar nichts Verlaessliches gefunden wurde, die unsicheren Vektor-Treffer
    # trotzdem als letzte Notloesung anbieten -- aber dem Modell explizit sagen, dass
    # sie unsicher sind, statt sie unmarkiert als Fakten zu praesentieren.
    if verlaesslich:
        context_blocks.extend(verlaesslich)
        unsicherheits_hinweis = ""
    elif unsicher:
        context_blocks.extend(unsicher)
        unsicherheits_hinweis = "\n\nACHTUNG: Die folgenden Dokumente wurden nur ueber vage semantische Aehnlichkeit gefunden, nicht ueber Wortuebereinstimmung -- sie koennen thematisch daneben liegen."
    else:
        unsicherheits_hinweis = ""

    context_str = "\n\n".join(context_blocks)

    prompt = f"""Du bist das lokale Gedächtnis von flextrawurst auf dem VPS.
Beantworte die folgende Frage präzise auf Deutsch in 2 bis 3 Sätzen, basierend NUR auf dem untenstehenden Kontext.
Wenn der Kontext die Frage nicht beantwortet oder nur lose damit zusammenhängt, antworte ehrlich: 'Die Antwort ist im indizierten Datenbestand nicht enthalten.' Erfinde nichts, das nicht wörtlich oder sinngemäß im Kontext steht.{unsicherheits_hinweis}

KONTEXT:
{context_str}

FRAGE: {q}

ANTWORT:"""

    answer = ""
    engine = "local_cpu_qwen2.5_0.5b_via_ollama"
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps({"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            answer = str(resp_data.get("response") or "").strip()
    except Exception as exc:
        engine = f"fallback_retrieval_summary ({str(exc)})"
        if sources:
            top_src = sources[0]
            answer = f"Synthese-Modell nicht erreichbar. Beste Fundstelle: {top_src['pfad']}\n\nAuszug:\n{top_src['auszug']}"
        else:
            answer = "Keine passenden Dokumente im Gesamtatlas gefunden."

    return {
        "ok": True,
        "query": q,
        "answer": answer,
        "count_sources": len(sources),
        "sources": sources,
        "engine": engine
    }



class MegaVaultSaveRequest(BaseModel):
    pfad: str
    content: str


@app.get(f"{BASE}/api/megavault/tree")
@app.get(f"{BASE}/megasuche/api/megavault/tree")
def api_megavault_tree(pfad: str = Query("/", description="Absoluter Pfad des Verzeichnisses auf dem VPS")):
    try:
        target = Path(pfad).resolve()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ungültiger Pfad: {str(e)}")
        
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Verzeichnis nicht gefunden oder kein Ordner.")
    
    entries = []
    try:
        for item in target.iterdir():
            try:
                stat = item.stat()
                is_dir = item.is_dir()
                entries.append({
                    "name": item.name,
                    "pfad": str(item),
                    "is_dir": is_dir,
                    "groesse_bytes": 0 if is_dir else stat.st_size,
                    "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat() if stat else None,
                    "extension": item.suffix.lstrip(".") if not is_dir else "dir"
                })
            except Exception:
                continue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Lesen des Verzeichnisses: {str(e)}")

    entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    parent = str(target.parent) if target != target.parent else None

    return {
        "ok": True,
        "pfad": str(target),
        "parent": parent,
        "anzahl": len(entries),
        "eintraege": entries
    }


@app.get(f"{BASE}/api/megavault/file")
@app.get(f"{BASE}/megasuche/api/megavault/file")
def api_megavault_get_file(pfad: str = Query(..., description="Absoluter Pfad der Datei auf der Disk")):
    target = Path(pfad).resolve()
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden oder kein regulärer Dateipfad.")
    
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Lesen der Datei: {str(e)}")
        
    stat = target.stat()
    lines = content.count("\n") + (1 if content else 0)
    
    return {
        "ok": True,
        "pfad": str(target),
        "titel": target.name,
        "extension": target.suffix.lstrip("."),
        "groesse_bytes": stat.st_size,
        "zeilen": lines,
        "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "content": content
    }


@app.get(f"{BASE}/api/megavault/file_details")
@app.get(f"{BASE}/megasuche/api/megavault/file_details")
def api_megavault_file_details(pfad: str = Query(..., description="Absoluter Pfad der Datei auf der Disk")):
    target = Path(pfad).resolve()
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden.")

    path_str = str(target)
    if path_str in ("/etc/shadow", "/etc/gshadow", "/etc/sudoers") or "id_rsa" in path_str or "id_ed25519" in path_str:
        raise HTTPException(status_code=403, detail="Zugriff auf sensible System-Sicherheitsdateien ist im MegaVault gesperrt.")

    stat = target.stat()

    stream = "system"
    stream_name = "VPS System"
    if "/_gemini" in path_str:
        stream = "gemini"
        stream_name = "Gemini Stream"
    elif "/_codex" in path_str:
        stream = "codex"
        stream_name = "Codex Stream"
    elif "/_claude" in path_str:
        stream = "claude"
        stream_name = "Claude Stream"
    elif "/_gpt" in path_str:
        stream = "chatgpt"
        stream_name = "ChatGPT Stream"
    elif "/_kimi" in path_str:
        stream = "kimi"
        stream_name = "Kimi Stream"
    elif "/_shared" in path_str:
        stream = "shared"
        stream_name = "Shared Resonanz"
    elif path_str.startswith("/root"):
        stream = "root"
        stream_name = "Root Directory"

    try:
        if path_str.endswith(".db") or path_str.endswith(".sqlite") or path_str.endswith(".sqlite3"):
            db_conn = sqlite3.connect(path_str)
            db_conn.row_factory = sqlite3.Row
            c = db_conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r['name'] for r in c.fetchall()]
            db_summary = [f"=== SQLITE DATENBANK-INSPECTOR: {target.name} ===", f"Tabellen: {', '.join(tables)}\n"]
            for t in tables[:4]:
                try:
                    c.execute(f"SELECT * FROM [{t}] ORDER BY ROWID DESC LIMIT 10;")
                    rows = c.fetchall()
                    db_summary.append(f"--- Tabelle '{t}' (Letzte 10 Einträge) ---")
                    for r in rows:
                        row_dict = dict(r)
                        db_summary.append(json.dumps(row_dict, ensure_ascii=False, default=str))
                    db_summary.append("")
                except Exception as e:
                    db_summary.append(f"Tabelle '{t}': {e}")
            db_conn.close()
            content = "\n".join(db_summary)
            lines = content.splitlines()
            zeilen_anzahl = len(lines)
        elif path_str.endswith(".zip") or path_str.endswith(".tar") or path_str.endswith(".gz") or path_str.endswith(".png") or path_str.endswith(".jpg"):
            content = f"=== BINÄR-DATEI INSPECTOR: {target.name} ===\nGröße: {stat.st_size:,} Bytes\nPfad: {path_str}\n(Binäre Dateien werden im Browser aus Speichergründen nicht im Volltext ausgeklappt.)"
            lines = [content]
            zeilen_anzahl = 1
        elif stat.st_size > 2 * 1024 * 1024:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(500000) + f"\n\n... [INHALT BEI 500 KB GEKÜRZT — GESAMTGRÖSSE: {stat.st_size:,} BYTES] ..."
            lines = content.splitlines()
            zeilen_anzahl = len(lines)
        else:
            content = target.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            zeilen_anzahl = len(lines)
    except Exception as exc:
        content = f"[Fehler beim Lesen der Datei: {exc}]"
        lines = []
        zeilen_anzahl = 0

    db_path = "/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite"
    bm25_indexed = False
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM documents WHERE path = ?", (path_str,))
            bm25_indexed = c.fetchone()[0] > 0
            conn.close()
        except Exception:
            pass

    referenzen = []
    if target.name and len(target.name) >= 3:
        for scan_dir in ["/root/werkraum/_codex", "/root/werkraum/_gemini", "/root/werkraum/_shared", "/root/werkraum/_claude"]:
            if os.path.exists(scan_dir):
                for r, _, files in os.walk(scan_dir):
                    for f in files:
                        if f.endswith(".md") or f.endswith(".txt") or f.endswith(".yaml"):
                            fp = os.path.join(r, f)
                            if fp != path_str:
                                try:
                                    txt = Path(fp).read_text(encoding="utf-8", errors="ignore")
                                    if target.name in txt or path_str in txt:
                                        rel_p = fp.replace("/root/werkraum/", "")
                                        referenzen.append({"pfad": fp, "relativ": rel_p, "titel": f})
                                        if len(referenzen) >= 30:
                                            break
                                except Exception:
                                    pass
                    if len(referenzen) >= 30:
                        break

    return {
        "ok": True,
        "pfad": path_str,
        "name": target.name,
        "extension": target.suffix.lstrip("."),
        "stream": stream,
        "stream_name": stream_name,
        "groesse_bytes": stat.st_size,
        "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "permissions": oct(stat.st_mode)[-4:],
        "zeilen_anzahl": zeilen_anzahl,
        "bm25_indexed": bm25_indexed,
        "referenzen": referenzen,
        "content": content
    }


@app.post(f"{BASE}/api/megavault/file/save")
@app.post(f"{BASE}/megasuche/api/megavault/file/save")
def api_megavault_save_file(req: MegaVaultSaveRequest):
    target = Path(req.pfad).resolve()
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Datei existiert nicht. Bitte nur bestehende Dateien editieren.")
        
    if not str(target).startswith("/root/"):
        raise HTTPException(status_code=403, detail="Speichern außerhalb von /root ist nicht erlaubt.")
        
    import subprocess
    try:
        subprocess.run(["git", "commit", "--allow-empty", "-m", f"backup: vor MegaVault Editor Speichern von {target.name}"], cwd="/root/werkraum", capture_output=True)
    except Exception:
        pass
        
    try:
        target.write_text(req.content, encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Schreiben der Datei: {str(e)}")
        
    try:
        import sys
        if "/root/werkraum/tools/vps_mcp" not in sys.path:
            sys.path.append("/root/werkraum/tools/vps_mcp")
        from mcp_atlas_hybrid_search import vektor_index_aktualisieren
        vektor_index_aktualisieren(pfad=str(target), text=req.content, metadaten={"titel": target.name, "quelle": "megavault_editor"})
    except Exception:
        pass
        
    stat = target.stat()
    lines = req.content.count("\n") + (1 if req.content else 0)
    
    return {
        "ok": True,
        "pfad": str(target),
        "titel": target.name,
        "groesse_bytes": stat.st_size,
        "zeilen": lines,
        "geaeandert_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    }


class MegaVaultDeleteRequest(BaseModel):
    pfad: str
    mode: str = "soft"


class MegaVaultRestoreRequest(BaseModel):
    pfad: str


SOFTDELETE_DIR = Path("/root/werkraum/_softdeleted")


@app.post(f"{BASE}/api/megavault/file/delete")
@app.post(f"{BASE}/megasuche/api/megavault/file/delete")
def api_megavault_delete_file(req: MegaVaultDeleteRequest):
    target = Path(req.pfad).resolve()
    if not str(target).startswith("/root/"):
        raise HTTPException(status_code=403, detail="Löschen außerhalb von /root ist nicht erlaubt.")
        
    mode = req.mode.lower()
    if mode not in ("soft", "hard"):
        raise HTTPException(status_code=400, detail="Modus muss 'soft' oder 'hard' sein.")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Datei existiert nicht oder ist kein regulärer Pfad.")

    import subprocess
    try:
        subprocess.run(["git", "commit", "--allow-empty", "-m", f"backup: vor MegaVault Delete ({mode}) von {target.name}"], cwd="/root/werkraum", capture_output=True)
    except Exception:
        pass

    if mode == "soft":
        try:
            rel_path = target.relative_to("/root")
        except ValueError:
            rel_path = Path(target.name)
            
        soft_target = SOFTDELETE_DIR / rel_path
        soft_target.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import shutil
            shutil.move(str(target), str(soft_target))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Ausführen von Soft-Delete: {str(e)}")

        return {
            "ok": True,
            "pfad": str(target),
            "soft_pfad": str(soft_target),
            "mode": "soft",
            "status": "soft_deleted_hidden",
            "zeitstempel_utc": datetime.now(timezone.utc).isoformat()
        }
    else:
        try:
            target.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Ausführen von Hard-Delete: {str(e)}")

        return {
            "ok": True,
            "pfad": str(target),
            "mode": "hard",
            "status": "permanently_deleted",
            "zeitstempel_utc": datetime.now(timezone.utc).isoformat()
        }


@app.post(f"{BASE}/api/megavault/file/restore")
@app.post(f"{BASE}/megasuche/api/megavault/file/restore")
def api_megavault_restore_file(req: MegaVaultRestoreRequest):
    target = Path(req.pfad).resolve()
    try:
        rel_path = target.relative_to("/root")
    except ValueError:
        rel_path = Path(target.name)
        
    soft_target = SOFTDELETE_DIR / rel_path
    if not soft_target.exists() or not soft_target.is_file():
        raise HTTPException(status_code=404, detail="Keine soft-geknickte/archivierte Datei zum Wiederherstellen gefunden.")

    target.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    try:
        shutil.move(str(soft_target), str(target))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Wiederherstellen der Datei: {str(e)}")

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        import sys
        if "/root/werkraum/tools/vps_mcp" not in sys.path:
            sys.path.append("/root/werkraum/tools/vps_mcp")
        from mcp_atlas_hybrid_search import vektor_index_aktualisieren
        vektor_index_aktualisieren(pfad=str(target), text=content, metadaten={"titel": target.name, "quelle": "megavault_restore"})
    except Exception:
        pass

    return {
        "ok": True,
        "pfad": str(target),
        "status": "restored_active",
        "zeitstempel_utc": datetime.now(timezone.utc).isoformat()
    }


@app.get(f"{BASE}/api/megavault/filters")
@app.get(f"{BASE}/megasuche/api/megavault/filters")
def api_megavault_filters():
    # Begriffsarbeit 2026-08-12 (Claude Web): Diese Funktion lieferte vorher
    # hartcodierte, im Jahr 2026-07 eingefrorene Zahlen -- keine Live-Berechnung.
    # "Alles was sichtbar ist muss auch existieren." Jetzt echt aus PFADINDEX.sqlite
    # und BEZIEHUNGSREGISTER.sqlite berechnet, kein einziger geratener Wert mehr.
    formats = []
    systems = []
    if PATH_DB.exists():
        conn = sqlite3.connect(PATH_DB)
        for suffix, cnt in conn.execute(
            "SELECT lower(suffix), COUNT(*) FROM paths WHERE is_dir=0 AND suffix != '' GROUP BY lower(suffix) ORDER BY 2 DESC LIMIT 20"
        ).fetchall():
            ext = suffix.lstrip(".")
            formats.append({"extension": ext, "label": f"{ext} ({suffix})", "count": cnt})
        for root_name, cnt in conn.execute(
            "SELECT root_name, COUNT(*) FROM paths GROUP BY root_name ORDER BY 2 DESC"
        ).fetchall():
            systems.append({"id": root_name, "label": root_name, "count": cnt})
        conn.close()

    ai_streams = [
        {"id": "chatgpt", "label": "ChatGPT / MCP", "path": "/root/werkraum/_gpt"},
        {"id": "claude", "label": "Claude Code", "path": "/root/werkraum/_claude"},
        {"id": "codex", "label": "Codex", "path": "/root/werkraum/_codex"},
        {"id": "gemini", "label": "Gemini", "path": "/root/werkraum/_gemini"},
        {"id": "kimi", "label": "Kimi", "path": "/root/werkraum/_kimi"},
        {"id": "glm", "label": "GLM", "path": "/root/werkraum/_glm"}
    ]
    ai_streams = [s for s in ai_streams if Path(s["path"]).exists()]

    relationship_types = []
    if REL_DB.exists():
        conn = sqlite3.connect(REL_DB)
        rows = conn.execute("SELECT relation, COUNT(*) FROM edges GROUP BY relation").fetchall()
        conn.close()
        for r, c in rows:
            relationship_types.append({"relation": r, "count": c})

    return {
        "ok": True,
        "formats": formats,
        "systems": systems,
        "ai_streams": ai_streams,
        "relationship_types": relationship_types
    }


@app.get(f"{BASE}/api/megavault/relationships")
@app.get(f"{BASE}/megasuche/api/megavault/relationships")
def api_megavault_relationships(
    node_type: Optional[str] = Query(None),
    relation: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    focus_node_ids: Optional[str] = Query(None, description="Kommagetrennte Node-IDs für fokussierten Teilgraphen (z. B. die 6 Haupt-Treffer)"),
    include_neighbors: bool = Query(False, description="1-Hop Nachbarknoten zuschalten"),
    include_conflicts: bool = Query(False, description="Gegenteilige/Konflikt-Knoten zuschalten (CONTRADICTS, CONFLICTS_WITH, OPPOSES)"),
    include_similar: bool = Query(False, description="Aehnliche Knoten zuschalten (SIMILAR_TO, aus dem Overlay-Register)"),
    only_confirmed_conflicts: bool = Query(True, description="Bei include_conflicts nur bestaetigte Gegensatz-Kanten zeigen."),
    limit: int = Query(100, ge=1, le=500)
):
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}

    conn = sqlite3.connect(REL_DB)
    conn.row_factory = sqlite3.Row
    
    # 1. Gezielter Subgraphen-Fokus (z. B. 6 relevante Treffer)
    target_focus_ids = set()
    if focus_node_ids:
        target_focus_ids = set(nid.strip() for nid in focus_node_ids.split(",") if nid.strip())

    node_sql = "SELECT node_id, node_type, identity, label, path, metadata_json FROM nodes"
    node_params = []
    where_clauses = []
    
    if target_focus_ids:
        placeholders = ",".join("?" for _ in target_focus_ids)
        where_clauses.append(f"node_id IN ({placeholders})")
        node_params.extend(target_focus_ids)
    else:
        if node_type:
            where_clauses.append("node_type = ?")
            node_params.append(node_type)
        if q:
            where_clauses.append("(label LIKE ? OR path LIKE ? OR identity LIKE ?)")
            q_like = f"%{q}%"
            node_params.extend([q_like, q_like, q_like])
        
    if where_clauses:
        node_sql += " WHERE " + " AND ".join(where_clauses)
    node_sql += " LIMIT ?"
    node_params.append(limit)
    
    nodes_rows = conn.execute(node_sql, node_params).fetchall()
    nodes = [dict(r) for r in nodes_rows]
    node_ids = set(n["node_id"] for n in nodes)
    
    # 2. Optional: 1-Hop Nachbarknoten & Konflikt-/Gegenteils-Knoten laden
    neighbor_ids = set()
    conflict_ids = set()
    
    similar_ids = set()
    if node_ids and (include_neighbors or include_conflicts or include_similar):
        placeholders = ",".join("?" for _ in node_ids)
        rel_clause = ""
        rel_params = list(node_ids) + list(node_ids)

        wanted_relations = []
        if include_conflicts:
            wanted_relations += ["CONTRADICTS", "CONFLICTS_WITH", "OPPOSES", "DISAGREES"]
        if include_similar:
            wanted_relations += ["SIMILAR_TO"]
        if wanted_relations and not include_neighbors:
            rp = ",".join("?" for _ in wanted_relations)
            rel_clause = f" AND relation IN ({rp})"
            rel_params = list(node_ids) + list(node_ids) + wanted_relations

        # Sicherheitsgrenze 2026-08-12 (Claude Web): manche Knoten (z.B. GENI mit
        # ueber 500.000 echten Kanten) haben so viele Verbindungen, dass eine
        # ungebremste Nachbarabfrage den Dienst faktisch einfrieren liesse. Ein
        # LIMIT hier ist eine bewusste, benannte semantische-Zoom-Grenze -- keine
        # verdeckte Datenverzerrung, weil count_nodes/count_edges immer die
        # tatsaechlich geladene (kleinere) Menge korrekt widerspiegeln.
        edge_sub_sql = f"""SELECT source_node_id, target_node_id, relation, datenstand FROM edges 
                          WHERE (source_node_id IN ({placeholders}) OR target_node_id IN ({placeholders})){rel_clause}
                          LIMIT 4000"""

        sub_edges = conn.execute(edge_sub_sql, rel_params).fetchall()
        for se in sub_edges:
            s_id, t_id, rel_type, ds = se["source_node_id"], se["target_node_id"], se["relation"], se["datenstand"]
            is_conflict = rel_type in ("CONTRADICTS", "CONFLICTS_WITH", "OPPOSES", "DISAGREES")
            is_similar = rel_type == "SIMILAR_TO"

            # Gegensatz-Kandidaten (noch unbestaetigt) standardmaessig ausblenden --
            # nur wer explizit only_confirmed_conflicts=false setzt sieht sie.
            if is_conflict and only_confirmed_conflicts and ds == "MODELLIERT_GEGENSATZ_KANDIDAT":
                is_conflict = False

            if include_neighbors:
                if s_id not in node_ids: neighbor_ids.add(s_id)
                if t_id not in node_ids: neighbor_ids.add(t_id)
            if include_conflicts and is_conflict:
                if s_id not in node_ids: conflict_ids.add(s_id)
                if t_id not in node_ids: conflict_ids.add(t_id)
            if include_similar and is_similar:
                if s_id not in node_ids: similar_ids.add(s_id)
                if t_id not in node_ids: similar_ids.add(t_id)

        # Nachbarn, Konflikt- und Aehnlichkeits-Knoten nachladen
        extra_ids = neighbor_ids | conflict_ids | similar_ids
        if extra_ids:
            ex_placeholders = ",".join("?" for _ in extra_ids)
            ex_nodes = conn.execute(f"SELECT node_id, node_type, identity, label, path, metadata_json FROM nodes WHERE node_id IN ({ex_placeholders})", list(extra_ids)).fetchall()
            for ex in ex_nodes:
                nd = dict(ex)
                nd["is_neighbor"] = nd["node_id"] in neighbor_ids
                nd["is_conflict"] = nd["node_id"] in conflict_ids
                nd["is_similar"] = nd["node_id"] in similar_ids
                nodes.append(nd)
                node_ids.add(nd["node_id"])

    # 3. Kanten laden
    # Bugfix 2026-08-04 (Claude Web, extern von ChatGPT gefunden, hier gegen die
    # echte DB verifiziert): Vorher wurden Kanten mit einem globalen LIMIT
    # unabhaengig von den geladenen Knoten aus der ~676k-Zeilen-Tabelle gezogen
    # (SELECT ... LIMIT limit*3, ohne WHERE nach node_ids), dann erst danach in
    # Python gefiltert. Bei stark vernetzten Knoten (die 8 Wesen haben real
    # 10.000-549.000 Kanten) lag deren tatsaechliche Kante praktisch nie unter
    # den zufaellig ersten Tabellenzeilen -- sie erschienen faelschlich als
    # unverbunden (Degree 0), obwohl das Register das Gegenteil zeigt.
    # Jetzt wird direkt in SQL nach den tatsaechlich geladenen Knoten gefiltert.
    edge_sql_parts = ["SELECT edge_id, source_node_id, target_node_id, relation, datenstand, evidence_json, first_utc, last_utc FROM edges"]
    edge_params = []
    edge_where = []

    if relation:
        edge_where.append("relation = ?")
        edge_params.append(relation)

    if node_ids:
        # Korrektur (Claude Web, direkt beim ersten Live-Test gefunden): OR statt
        # AND liess bei grossen Nachbarschaften (10k+ Knoten) massenhaft fremde
        # Kanten durch, die nur zufaellig ein Ende in der Menge hatten -- das
        # Limit war dann von diesem Rauschen aufgefressen, bevor Schorschels
        # eigene Kanten drankamen. AND liefert exakt den induzierten Teilgraphen:
        # beide Enden muessen zu den tatsaechlich geladenen Knoten gehoeren.
        placeholders = ",".join("?" for _ in node_ids)
        edge_where.append(f"(source_node_id IN ({placeholders}) AND target_node_id IN ({placeholders}))")
        edge_params.extend(list(node_ids))
        edge_params.extend(list(node_ids))

    if edge_where:
        edge_sql_parts.append("WHERE " + " AND ".join(edge_where))
    edge_sql = " ".join(edge_sql_parts)

    # Auch im knotengebundenen Fall bleibt ein grosszuegiges Limit noetig --
    # GENI allein haette sonst 549.063 Kanten in einer Antwort. Das Limit greift
    # jetzt aber auf dem RICHTIGEN, bereits gefilterten Kandidatenkreis, nicht
    # mehr auf einem beliebigen Ausschnitt der Gesamttabelle.
    edge_limit = max(limit * 3, 3000)
    edge_sql += " LIMIT ?"
    edge_params.append(edge_limit)

    edges_rows = conn.execute(edge_sql, edge_params).fetchall()
    edges = []
    for er in edges_rows:
        ed = dict(er)
        if not node_ids or (ed["source_node_id"] in node_ids and ed["target_node_id"] in node_ids):
            edges.append(ed)

    conn.close()
    
    return {
        "ok": True,
        "count_nodes": len(nodes),
        "count_edges": len(edges),
        "filters": {
            "node_type": node_type,
            "relation": relation,
            "q": q,
            "focus_node_ids": focus_node_ids,
            "include_neighbors": include_neighbors,
            "include_conflicts": include_conflicts,
            "include_similar": include_similar,
            "only_confirmed_conflicts": only_confirmed_conflicts
        },
        "nodes": nodes,
        "edges": edges
    }


class GegensatzAktion(BaseModel):
    edge_id: str


def _bestaetigungslog_lesen() -> dict:
    if not BESTAETIGUNGSLOG.exists():
        return {}
    try:
        return json.loads(BESTAETIGUNGSLOG.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _bestaetigungslog_schreiben(daten: dict) -> None:
    BESTAETIGUNGSLOG.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")


@app.post(f"{BASE}/api/megavault/gegensatz/bestaetigen")
def api_megavault_gegensatz_bestaetigen(payload: GegensatzAktion):
    """Bestaetigt eine halbautomatisch erkannte OPPOSES-Kandidaten-Kante direkt im
    kanonischen Register UND im Bestaetigungslog (das Log ueberlebt einen
    Atlas-Rebuild, die Kante im Register wird beim naechsten Reseed danach
    ausgerichtet)."""
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}
    conn = sqlite3.connect(REL_DB)
    conn.execute("PRAGMA busy_timeout=15000")
    row = conn.execute("SELECT * FROM edges WHERE edge_id = ?", (payload.edge_id,)).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "error": "edge_id nicht gefunden"}
    conn.execute("UPDATE edges SET datenstand = 'MODELLIERT_GEGENSATZ_BESTAETIGT', last_utc = ? WHERE edge_id = ?", (datetime.now(timezone.utc).isoformat(), payload.edge_id))
    conn.commit()
    conn.close()

    log = _bestaetigungslog_lesen()
    log[payload.edge_id] = {"status": "bestaetigt", "zeitpunkt": datetime.now(timezone.utc).isoformat()}
    _bestaetigungslog_schreiben(log)

    return {"ok": True, "edge_id": payload.edge_id, "datenstand": "MODELLIERT_GEGENSATZ_BESTAETIGT"}


@app.post(f"{BASE}/api/megavault/gegensatz/verwerfen")
def api_megavault_gegensatz_verwerfen(payload: GegensatzAktion):
    """Loescht eine halbautomatisch erkannte OPPOSES-Kandidaten-Kante aus dem
    kanonischen Register UND traegt die Verwerfung im Bestaetigungslog ein, damit
    sie nach einem Reseed nicht wieder auftaucht."""
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}
    conn = sqlite3.connect(REL_DB)
    conn.execute("PRAGMA busy_timeout=15000")
    row = conn.execute("SELECT * FROM edges WHERE edge_id = ?", (payload.edge_id,)).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "error": "edge_id nicht gefunden"}
    conn.execute("DELETE FROM edges WHERE edge_id = ?", (payload.edge_id,))
    conn.commit()
    conn.close()

    log = _bestaetigungslog_lesen()
    log[payload.edge_id] = {"status": "verworfen", "zeitpunkt": datetime.now(timezone.utc).isoformat()}
    _bestaetigungslog_schreiben(log)

    return {"ok": True, "edge_id": payload.edge_id, "geloescht": True}


@app.get(f"{BASE}/api/megavault/gegensatz/kandidaten")
def api_megavault_gegensatz_kandidaten(limit: int = Query(50, ge=1, le=500)):
    """Listet offene, noch unbestaetigte OPPOSES-Kandidaten aus dem kanonischen
    Register zur manuellen Pruefung."""
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}
    conn = sqlite3.connect(REL_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT edge_id, source_node_id, target_node_id, relation, datenstand, evidence_json, first_utc "
        "FROM edges WHERE relation='OPPOSES' AND datenstand='MODELLIERT_GEGENSATZ_KANDIDAT' "
        "ORDER BY first_utc DESC LIMIT ?", (limit,)
    ).fetchall()
    if not rows:
        conn.close()
        return {"ok": True, "count": 0, "kandidaten": []}

    node_ids = set()
    for r in rows:
        node_ids.add(r["source_node_id"])
        node_ids.add(r["target_node_id"])
    placeholders = ",".join("?" for _ in node_ids)
    labels = {n["node_id"]: dict(n) for n in conn.execute(
        f"SELECT node_id, label, path, node_type FROM nodes WHERE node_id IN ({placeholders})", list(node_ids)
    ).fetchall()}
    conn.close()

    out = []
    for r in rows:
        d = dict(r)
        d["source"] = labels.get(r["source_node_id"])
        d["target"] = labels.get(r["target_node_id"])
        out.append(d)
    return {"ok": True, "count": len(out), "kandidaten": out}


@app.get(f"{BASE}/api/projects")
def api_projects():
    rows = project_rows()
    return {"count": len(rows), "projects": rows}


@app.get(f"{BASE}/api/relationships")
def api_relationships(q: str = "", limit: int = Query(50, ge=1, le=150)):
    return relationship_graph(q, limit)


@app.get(f"{BASE}/api/homes")
def api_homes():
    rows = []
    for key, spec in AI_HOMES.items():
        rows.append({"stream": key, "label": spec["label"], "path": str(spec["path"]), "exists": spec["path"].exists(), "visible_files": len(home_files(key))})
    return {"count": len(rows), "homes": rows}


@app.get(f"{BASE}/api/browser")
def api_browser(limit: int = Query(200, ge=1, le=500)):
    rows = browser_conversations(limit)
    return {"count": len(rows), "conversations": rows}


@app.get(f"{BASE}/api/terminal")
def api_terminal(limit: int = Query(80, ge=1, le=200)):
    return {provider: terminal_sessions(provider, limit) for provider in AGENT_ROOTS}


@app.get(f"{BASE}/api/gaps")
def api_gaps():
    return gap_report()



@app.get(f"{BASE}/api/truth")
def api_truth():
    return truth_ring()


@app.get(f"{BASE}/api/journey")
def api_journey():
    model = journey_model()
    return {"schema_version": "1.1", "generated_utc": model["truth"]["live"].get("generated_utc") or model["truth"]["baseline"].get("generated_utc"), "count": len(model["steps"]), "truth": model["truth"], "steps": model["steps"], "routes": {"child": f"{PUBLIC_BASE}/kind", "guided": f"{PUBLIC_BASE}/reise?schritt=1", "free": f"{PUBLIC_BASE}/erkunden", "versions": f"{PUBLIC_BASE}/versionen"}}




@app.get(f"{BASE}/api/capsules")
def api_capsules():
    capsules = small_capsules()
    paths = {"MENSCH.md": "mensch.md", "KIND.md": "kind.md", "MASCHINE.json": "maschine.json"}
    return {"schema_version": "1.0", "generated_utc": truth_ring()["live"].get("generated_utc") or truth_ring()["baseline"].get("generated_utc"), "capsules": {name: {"path": f"{PUBLIC_BASE}/kapsel/{paths[name]}", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()} for name, payload in capsules.items()}, "zip": f"{PUBLIC_BASE}/kapsel.zip"}


@app.get(f"{BASE}/api/manifest")
def api_manifest():
    status = atlas_status()
    truth = truth_ring()
    capsules = api_capsules()
    capsule_file = capsule_path()
    return {
        "schema_version": "2.0", "name": "Gesamtatlas", "generated_utc": truth["live"].get("generated_utc") or truth["baseline"].get("generated_utc"), "base_path": PUBLIC_BASE,
        "status": status, "world_model": truth["world_model"], "truth_ring": truth,
        "exploration": {"child": f"{PUBLIC_BASE}/kind", "guided_journey": f"{PUBLIC_BASE}/reise?schritt=1", "free_exploration": f"{PUBLIC_BASE}/erkunden", "versions": f"{PUBLIC_BASE}/versionen", "files": f"{PUBLIC_BASE}/dateien", "documents": f"{PUBLIC_BASE}/dokumente", "services": f"{PUBLIC_BASE}/dienste", "sessions": f"{PUBLIC_BASE}/sitzungen", "original_example": f"{PUBLIC_BASE}/original/?p={encode_path(truth['baseline']['path'])}"},
        "small_capsules": capsules["capsules"],
        "capsule": {"path": f"{PUBLIC_BASE}/kapsel.zip", "bytes": capsule_file.stat().st_size, "sha256": sha256_file(capsule_file)},
        "truth_boundary": "Der Webkörper bindet einen vollständig verifizierten Grundstand und einen getrennten sichtbaren Live-Nachlauf. Er behauptet keine Vollständigkeit für nicht importierte, ausgeschlossene oder noch nicht überprüfte Bereiche.",
    }



def _path_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def classify_public_original(path_text: str) -> dict[str, Any]:
    raw = Path(path_text).expanduser()
    candidate = raw.resolve(strict=False)
    base = {"path": str(candidate), "name": candidate.name or str(candidate), "bytes": None, "available": False}
    lower_parts = {part.lower() for part in candidate.parts}
    if any(segment.lower() in lower_parts or segment.lower() in candidate.name.lower() for segment in DENIED_SEGMENTS):
        return base | {"state": "BLOCKED_PRIVATE_OR_SECRET", "reason": "Die Spur bleibt wegen möglicher Zugangsdaten oder Privatsphäre geschlossen.", "truth_class": "PROVENANCE_ONLY_BLOCKED"}
    if raw.is_symlink() or candidate.is_symlink():
        return base | {"state": "BLOCKED_SYMLINK", "reason": "Symlink-Ziele werden nicht als öffentliche Originale verfolgt.", "truth_class": "PROVENANCE_ONLY_BLOCKED"}
    if not candidate.exists() or not candidate.is_file():
        return base | {"state": "MISSING_OR_NOT_A_FILE", "reason": "Der registrierte Pfad ist derzeit kein vorhandener regulärer Dateikörper.", "truth_class": "PROVENANCE_ONLY_MISSING"}
    try:
        size = candidate.stat().st_size
    except OSError:
        return base | {"state": "TEMPORARILY_UNAVAILABLE", "reason": "Der Dateizustand konnte vorübergehend nicht sicher gelesen werden.", "truth_class": "PROVENANCE_ONLY_TEMPORARY"}
    base["bytes"] = size
    if not any(_path_under(candidate, root.resolve()) for root in PUBLIC_TEXT_ROOTS):
        return base | {"state": "OUTSIDE_PUBLIC_ROOTS", "reason": "Die Spur liegt außerhalb der ausdrücklich freigegebenen Textflächen.", "truth_class": "PROVENANCE_ONLY_OUTSIDE_PUBLIC_ROOTS"}
    if candidate.suffix.lower() not in TEXT_SUFFIXES:
        return base | {"state": "UNSUPPORTED_OR_BINARY", "reason": "Der Körper ist nicht als freigegebener Texttyp klassifiziert.", "truth_class": "PROVENANCE_ONLY_UNSUPPORTED"}
    if size > 2_500_000:
        return base | {"state": "TOO_LARGE_FOR_DIRECT_VIEW", "reason": "Der Textkörper ist für die direkte Browseransicht zu groß.", "truth_class": "PROVENANCE_ONLY_TOO_LARGE"}
    return base | {"state": "READABLE_TEXT", "reason": "Freigegebener regulärer Textkörper.", "truth_class": "EXACT_FILE_BYTES", "available": True}


def versions_model() -> dict[str, Any]:
    records = []
    for index, path in enumerate(VERSION_PATHS, start=1):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        records.append({"id": f"proof-capsule-v{index}", "path": str(path), "name": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "mtime_ns": path.stat().st_mtime_ns, "text": raw.decode("utf-8", errors="replace")})
    comparisons = []
    for left, right in zip(records, records[1:]):
        diff = list(difflib.unified_diff(left["text"].splitlines(), right["text"].splitlines(), fromfile=left["name"], tofile=right["name"], lineterm=""))
        comparisons.append({"from_id": left["id"], "to_id": right["id"], "from_sha256": left["sha256"], "to_sha256": right["sha256"], "changed": left["sha256"] != right["sha256"], "diff_line_count": len(diff), "diff_excerpt": "\n".join(diff[:240])})
    return {"family_id": "proof-capsule-builder-history", "title": "build_proof_capsule.py - echte Fassungsfamilie", "versions": [{k: v for k, v in row.items() if k != "text"} for row in records], "comparisons": comparisons, "truth_boundary": "Dateien werden nach Pfad, Bytes und SHA-256 verglichen. Reihenfolge folgt realen Vorgängerdateien, nicht einer erfundenen Git-Historie."}


def path_object_rows(kind: str, limit: int = 80) -> list[dict[str, Any]]:
    clauses = {"file": "is_dir=0", "document": "is_dir=0 and lower(suffix) in ('.md','.txt','.json','.html','.pdf')", "service": "is_dir=0 and (lower(basename) like '%.service' or lower(path) like '%systemd%')"}
    with db(PATH_DB) as con:
        rows = con.execute(f"select path,basename,kind,size,root_name,mtime_ns from paths where {clauses[kind]} order by mtime_ns desc limit ?", (limit,)).fetchall()
    return [dict(row) | {"original_href": public_original_href(row["path"]), "classification": classify_public_original(row["path"])} for row in rows]


def object_door_page(title: str, kind: str, explanation: str) -> HTMLResponse:
    items = ""
    for row in path_object_rows(kind):
        state = row["classification"]
        state_class = "ok" if state["available"] else "warn"
        state_label = "Original lesen" if state["available"] else "Spur erklären"
        items += f'<a class="card-link object-row" href="{row["original_href"]}"><article class="list-item"><h3>{esc(row["basename"])}</h3><div class="path">{esc(row["path"])}</div><div class="meta"><span>{esc(row["kind"])}</span><span>{fmt_bytes(row["size"])}</span><span class="pill {state_class}">{state_label} - {esc(state["state"])}</span></div></article></a>'
    body = f'<section class="section-head"><div><div class="kicker">Zusätzliche Eingangstür</div><h1>{esc(title)}</h1></div><p>{esc(explanation)}</p></section><div class="list">{items or "<div class=empty>Keine Objekte im aktuellen Register.</div>"}</div>'
    return page(title, body, active="welt")


@app.get(f"{BASE}/versionen", response_class=HTMLResponse, include_in_schema=False)
def versions_page():
    model = versions_model()
    cards = "".join(f'<article class="card version-card"><div class="kicker">{esc(row["id"])}</div><h2>{esc(row["name"])}</h2><p class="path">{esc(row["path"])}</p><dl class="truth"><dt>Bytes</dt><dd>{row["bytes"]}</dd><dt>SHA-256</dt><dd class="mono">{row["sha256"]}</dd></dl><a class="button" href="{public_original_href(row["path"])}">Fassung öffnen</a></article>' for row in model["versions"])
    comparisons = "".join(f'<article class="card comparison-card"><h2>{esc(row["from_id"])} → {esc(row["to_id"])}</h2><p>{row["diff_line_count"]} Diffzeilen - {"verändert" if row["changed"] else "bytegleich"}</p><div class="codebox"><pre>{esc(row["diff_excerpt"])}</pre></div></article>' for row in model["comparisons"])
    body = f'<section class="section-head"><div><div class="kicker">Echte Fassungsfamilie</div><h1>{esc(model["title"])}</h1></div><p>{esc(model["truth_boundary"])}</p></section><div id="version-cards" class="grid cols-3">{cards}</div><section class="section"><div class="section-head"><h2>Exakte Veränderungen</h2></div><div id="version-comparisons" class="grid cols-2">{comparisons}</div></section>'
    return page("Versionen", body, active="versionen")


@app.get(f"{BASE}/dateien", response_class=HTMLResponse, include_in_schema=False)
def files_door():
    return object_door_page("Dateien", "file", "Registrierte Dateispuren führen entweder zum lesbaren Original oder zu einer ehrlichen Zustandsseite.")


@app.get(f"{BASE}/dokumente", response_class=HTMLResponse, include_in_schema=False)
def documents_door():
    return object_door_page("Dokumente", "document", "Lesbare Dokumente, Manifeste und Berichte mit Herkunft und Sichtgrenze.")


@app.get(f"{BASE}/dienste", response_class=HTMLResponse, include_in_schema=False)
def services_door():
    return object_door_page("Dienste", "service", "Dienst- und systemd-Spuren werden nur gelesen; kein laufender Dienst wird von dieser Oberfläche verändert.")


@app.get(f"{BASE}/sitzungen", response_class=HTMLResponse, include_in_schema=False)
def sessions_door():
    body = '<section class="section-head"><div><div class="kicker">Zusätzliche Eingangstür</div><h1>Sitzungen</h1></div><p>Browser- und Terminal-Sitzungen bleiben getrennt und führen in ihre bestehenden Owner-Organe.</p></section><div class="grid cols-2"><section><h2>Browserräume</h2><div class="list">'
    for row in browser_conversations(40):
        body += f'<a class="card-link" href="{href("/browser/" + quote(row["folder"]))}"><article class="list-item"><h3>{esc(row["title"])}</h3><div class="meta"><span>{row["messages"]} Nachrichten</span><span>{row["gaps"]} Lücken</span></div></article></a>'
    body += '</div></section><section><h2>Terminalwerkstätten</h2><div class="list">'
    for provider in AGENT_ROOTS:
        for row in terminal_sessions(provider, 15):
            body += f'<a class="card-link" href="{href("/terminal/" + provider + "/" + quote(row["id"]))}"><article class="list-item"><h3>{esc(provider)} - {esc(row["id"])}</h3><div class="path">{esc(row["path"])}</div></article></a>'
    body += '</div></section></div>'
    return page("Sitzungen", body, active="welt")


@app.get(f"{BASE}/api/versions")
def api_versions():
    return versions_model()


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    body = f'<section class="section-head"><div><div class="kicker">{exc.status_code}</div><h1>{esc(exc.detail)}</h1></div></section><p><a class="button" href="{href('/')}">Zurück in den Atlas</a></p>'
    response = page(str(exc.detail), body)
    response.status_code = exc.status_code
    return response
