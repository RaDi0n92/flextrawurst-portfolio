from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import difflib
import fcntl
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import tempfile
import threading
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator

from mcp_atlas_relations import (
    build_relational_layer,
    event_project_ids as relational_event_project_ids,
    handoff_state as relational_handoff_state,
    observe_project_event,
    project_match as relational_project_match,
    query_relationships as relational_query_relationships,
)


ATLAS_ROOT = Path(
    os.environ.get("FLEXTRAWURST_MCP_ATLAS_ROOT", "/root/werkraum/_gpt/gesamtatlas")
)
HISTORY_PATH = Path(
    os.environ.get("FLEXTRAWURST_ACTION_HISTORY", "/root/werkraum/_gpt/session_history.jsonl")
)
STATUS_PATH = ATLAS_ROOT / "ATLAS_STATUS.json"
PATH_DB = ATLAS_ROOT / "PFADINDEX.sqlite"
CONCEPT_DB = ATLAS_ROOT / "BEGRIFFSINDEX.sqlite"
CHANGE_LOG = ATLAS_ROOT / "AENDERUNGSSTROM.jsonl"
CONSENSUS_LOG = ATLAS_ROOT / "KONSENSREGISTER.jsonl"
CONFLICT_LOG = ATLAS_ROOT / "KONFLIKTREGISTER.jsonl"
IDEA_LOG = ATLAS_ROOT / "EINGEBUNGSPROVENIENZ.jsonl"
PROJECT_REVISION_PATH = ATLAS_ROOT / "PROJEKTREVISIONEN.json"
CLAIM_REGISTER_PATH = ATLAS_ROOT / "CLAIMREGISTER.json"
VALIDATION_REGISTER_PATH = ATLAS_ROOT / "VALIDIERUNGSREGISTER.json"
HANDOFF_REGISTER_PATH = ATLAS_ROOT / "UEBERGABEREGISTER.json"
HANDOFF_ROOT = ATLAS_ROOT / "uebergaben"
AI_BRIDGE_PATH = ATLAS_ROOT / "AI_STROM_BRUECKEN.json"
RELATION_DB = ATLAS_ROOT / "BEZIEHUNGSREGISTER.sqlite"
RELATION_JSON = ATLAS_ROOT / "BEZIEHUNGSREGISTER.json"
CURSOR_ROOT = ATLAS_ROOT / "session_cursors"
LOCK_PATH = ATLAS_ROOT / ".atlas.lock"

SCAN_ROOTS: tuple[dict[str, Any], ...] = (
    {"name": "werkraum", "path": "/root/werkraum", "kind": "arbeitsraum"},
    {"name": "flextrawurst-live", "path": "/root/flextrawurst", "kind": "live_system"},
    {"name": "gemini-brain", "path": "/root/.gemini/antigravity-cli/brain", "kind": "agent_sessions"},
    {"name": "glm-home", "path": "/root/werkraum/_glm", "kind": "ai_stream_home"},
    {"name": "bilder", "path": "/root/werkraum_bilder", "kind": "assets"},
    {"name": "geni", "path": "/root/werkraum_geni", "kind": "geni"},
    {"name": "codewesen", "path": "/root/werkraum_codewesen", "kind": "codewesen"},
    {"name": "agentenmaterial", "path": "/root/werkraum_agent", "kind": "agentenmaterial"},
    {"name": "erkenntnis", "path": "/root/werkraum_erkenntnis", "kind": "erkenntnis"},
    {"name": "flarum", "path": "/root/werkraum_flarum", "kind": "forum"},
    {"name": "logs", "path": "/root/werkraum_logs", "kind": "logs"},
    {"name": "claude-sessions", "path": "/root/.claude/projects", "kind": "agent_sessions"},
    {"name": "codex-sessions", "path": "/root/.codex/sessions", "kind": "agent_sessions"},
    {
        "name": "gesamtatlas-eingang",
        "path": "/root/werkraum_gesamtatlas_eingang",
        "kind": "curated_manual_intake",
        "scope_role": "curated_manual",
    },
    {
        "name": "zensi",
        "path": "/root/zensi",
        "kind": "zensi",
        "scan_mode": "federated",
        "scope_role": "federated_external",
        "federated_search_tool": "zensi.vault_search",
        "federated_tree_tool": "zensi.vault_tree",
    },
)

ROOT_LETTERS: tuple[dict[str, Any], ...] = (
    {
        "path": "/root/GEMINI.md",
        "filename_label": "gemini",
        "declared_author": "Gemini bei Daniels VPS",
        "declared_targets": ["gemini"],
        "excluded_targets": [],
        "identity_status": "filename_and_content_aligned",
    },
    {
        "path": "/root/CLAUDE.md",
        "filename_label": "claude",
        "declared_author": "glm-code bei Daniels VPS",
        "declared_targets": ["glm"],
        "excluded_targets": [],
        "identity_status": "filename_content_identity_mismatch",
    },
    {
        "path": "/root/KIMI.md",
        "filename_label": "kimi",
        "declared_author": "kimi bei Daniels VPS",
        "declared_targets": ["kimi"],
        "excluded_targets": [],
        "identity_status": "filename_and_content_aligned",
    },
    {
        "path": "/root/grok.md",
        "filename_label": "grok",
        "declared_author": "Daniel / nicht formal ausgewiesen",
        "declared_targets": ["glm"],
        "excluded_targets": [],
        "identity_status": "filename_content_identity_mismatch",
    },
    {
        "path": "/root/AGENTS.md",
        "filename_label": "agents",
        "declared_author": "codex bei Daniels VPS",
        "declared_targets": ["codex", "kimi"],
        "excluded_targets": ["glm"],
        "identity_status": "multi_stream_root_contract",
    },
)

AI_STREAMS: tuple[dict[str, Any], ...] = (
    {
        "id": "chatgpt",
        "home": "/root/werkraum/_gpt/mcp_zuhause",
        "workspace": "/root/werkraum/_gpt/mcp_arbeitskoerper",
        "sessions": "/root/werkraum/_gpt/session_history.jsonl",
        "root_letter_paths": [],
    },
    {
        "id": "claudeweb",
        "home": "/root/werkraum/_claudeweb",
        "workspace": "/root/werkraum/_claudeweb",
        "sessions": "/root/werkraum/_claudeweb/verlauf",
        "root_letter_paths": [],
        "entry_paths": [
            "/root/werkraum/_claudeweb/ZUHAUSE.md",
            "/root/werkraum/_claudeweb/MANIFEST.json",
            "/root/werkraum/_claudeweb/protokoll/claudeweb_zuhause_v1.json",
        ],
        "identity_boundary": "Claude Web ist ein eigener Browser-/App-Chatstrom über Daniels MCP-Konnektor, nicht Claude Code und nicht ChatGPT. Kontinuität entsteht nur durch explizit gelesene Dateien oder Plattform-Memory.",
        "note": "Achter AI-Strom mit eigenem Zuhause und sichtbarer Verlaufsquelle; keine erfundene Hintergrundinstanz oder gemeinsame Erinnerung.",
    },
    {
        "id": "claude",
        "home": "/root/werkraum/_claude",
        "workspace": "/root/werkraum/_claude",
        "sessions": "/root/.claude/projects",
        "root_letter_paths": [],
        "note": "Der Dateiname /root/CLAUDE.md wird nicht automatisch Claude zugerechnet; sein eigener Inhalt erklärt GLM-Herkunft und GLM-Ziel.",
    },
    {
        "id": "codex",
        "home": "/root/werkraum/_codex",
        "workspace": "/root/werkraum/_codex",
        "sessions": "/root/.codex/sessions",
        "root_letter_paths": ["/root/AGENTS.md"],
    },
    {
        "id": "kimi",
        "home": "/root/werkraum/_kimi",
        "workspace": "/root/werkraum/_kimi",
        "sessions": "/root/werkraum/_kimi",
        "root_letter_paths": ["/root/KIMI.md", "/root/AGENTS.md"],
    },
    {
        "id": "gemini",
        "home": "/root/werkraum/_gemini",
        "workspace": "/root/werkraum/_gemini",
        "sessions": "/root/.gemini/antigravity-cli/brain",
        "root_letter_paths": ["/root/GEMINI.md"],
    },
    {
        "id": "glm",
        "home": "/root/werkraum/_glm",
        "workspace": "/root/werkraum/_glm",
        "sessions": None,
        "root_letter_paths": ["/root/CLAUDE.md", "/root/grok.md"],
        "note": "GLM-Körper und GLM-adressierte Wurzelbriefe; Dateinamen bleiben als separate Provenienz erhalten.",
    },
    {
        "id": "grok",
        "home": None,
        "workspace": None,
        "sessions": None,
        "root_letter_paths": ["/root/grok.md"],
        "status": "root_letter_filename_only_no_confirmed_home",
        "note": "Aus dem Dateinamen grok.md wird kein Grok-Haus abgeleitet; der Inhalt adressiert GLM.",
    },
)

SKIP_DIRECTORY_NAMES = frozenset(
    {
        ".cache",
        ".npm",
        ".pnpm-store",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "watchdog_venv",
        "site-packages",
        "chromium",
        "chrome-cache",
        "playwright-browsers",
    }
)
TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".txt",
        ".json",
        ".jsonl",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".conf",
        ".service",
        ".timer",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".sql",
        ".sh",
    }
)
MUTATING_TOOL_PREFIXES = (
    "vps.shell",
    "vps.exec_allowlisted",
    "vps.write",
    "vps.edit",
    "vps.move",
    "vps.delete",
    "tracked_write",
    "git.commit",
    "services.start",
    "services.stop",
    "services.restart",
    "services.enable",
    "services.disable",
    "services.install",
    "database.execute",
)
LOW_SIGNAL_ACTION_PREFIXES = (
    "vps.list",
    "vps.read",
    "vps.search",
    "vps.file_metadata",
    "git.status",
    "git.log",
    "git.show",
    "services.status",
    "services.logs",
    "assets.list",
    "assets.search",
    "agents.list",
    "agents.read",
    "agents.search",
    "ui_visible.protocol_bound",
)
CONSENSUS_CLASSES = frozenset(
    {
        "DANIEL_EXPLIZIT_GESETZT",
        "TECHNISCH_VALIDIERT",
        "MEHRFACH_BESTAETIGT",
        "ARBEITSHYPOTHESE",
        "VORSCHLAG",
        "WIDERSPRUCH",
        "VERALTET",
        "UNBEKANNT",
    }
)
IDEA_AWARENESS = frozenset({"none", "partial", "direct", "unknown"})
IDEA_PROVENANCE_CLASSES = frozenset(
    {
        "UEBERNOMMEN_ODER_DIREKT_ANGESTOSSEN",
        "ANGESTOSSEN_ODER_TEILBEWUSST",
        "KONVERGENT_MIT_AUFFINDBARER_VORSPUR",
        "OHNE_GEFUNDENE_VORSPUR",
        "HERKUNFT_UNKLAR_MIT_AEHNLICHKEIT",
        "HERKUNFT_UNKLAR",
        "CROSS_SESSION_EINGEBUNG_MIT_NACHGELAGERTER_LOKALER_FREIGABE",
    }
)


class AtlasError(RuntimeError):
    pass


def _utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def _atomic_write_json(path: Path, value: Any) -> None:
    _atomic_write_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _atomic_write_text(path: Path, value: str) -> None:
    _atomic_write_bytes(path, value.encode("utf-8"))


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        raise AtlasError(f"Ungültiges JSON in {path}: {exc}") from exc


def _read_jsonl(path: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    if limit is not None:
        return rows[-max(0, int(limit)) :]
    return rows


def _append_jsonl(path: Path, value: dict[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    with path.open("ab") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            offset = handle.tell()
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            return offset + len(payload)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextlib.contextmanager
def _atlas_lock() -> Iterator[None]:
    ATLAS_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    with LOCK_PATH.open("a+", encoding="utf-8") as handle:
        os.chmod(LOCK_PATH, 0o600)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _ensure_layout() -> None:
    for path in (
        ATLAS_ROOT,
        CURSOR_ROOT,
        ATLAS_ROOT / "karten" / "projekte",
        ATLAS_ROOT / "karten" / "systeme",
        ATLAS_ROOT / "karten" / "vaults",
        ATLAS_ROOT / "karten" / "ai-stroeme",
        ATLAS_ROOT / "karten" / "sessions",
        ATLAS_ROOT / "karten" / "begriffe",
        ATLAS_ROOT / "karten" / "pfade",
        ATLAS_ROOT / "runtime",
        ATLAS_ROOT / "validation",
        ATLAS_ROOT / "systemd",
        HANDOFF_ROOT,
    ):
        path.mkdir(parents=True, exist_ok=True, mode=0o700)


def _path_kind(path: Path, is_dir: bool, is_symlink: bool) -> str:
    if is_symlink:
        return "symlink"
    if is_dir:
        return "directory"
    suffix = path.suffix.lower()
    if suffix in {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}:
        return "archive"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        return "image"
    if suffix in {".glb", ".gltf", ".blend", ".obj", ".fbx", ".stl"}:
        return "3d"
    if suffix in {".mp3", ".wav", ".ogg", ".flac", ".m4a"}:
        return "audio"
    if suffix in TEXT_SUFFIXES:
        return "text"
    return "file"


def _markers_for(path: Path, is_dir: bool) -> list[str]:
    markers: list[str] = []
    name = path.name.lower()
    if is_dir and name == ".obsidian":
        markers.append("obsidian_config")
    if is_dir and name in {"verweise", "moc", "zeitstrom", "coordination", "sessions", "validation"}:
        markers.append(name)
    if name in {
        "start_hier.md",
        "home.md",
        "zuhause.md",
        "werkraum_karte.md",
        "manifest.json",
        "aktuelle_wahrheit.md",
        "aktuelle_wahrheit.json",
        "zeitstrom.md",
        "uhrzeitenerlebnis.md",
        "gespraechsnetz.md",
        "agents.md",
        "claude.md",
        "gemini.md",
        "kimi.md",
        "grok.md",
    }:
        markers.append("entry_or_manifest")
    if name == "build_obsidian_vault.py":
        markers.append("vault_builder")
    if name.endswith("validierungsbericht.md") or name.endswith("result.json"):
        markers.append("validation_artifact")
    return markers


def _safe_stat(path: Path, *, follow_symlinks: bool = False) -> os.stat_result | None:
    try:
        return path.stat(follow_symlinks=follow_symlinks)
    except (FileNotFoundError, PermissionError, OSError):
        return None


def _scan_paths(
    database_path: Path,
    concept_database_path: Path,
    *,
    max_paths: int,
    max_text_documents: int,
    text_bytes_per_file: int,
) -> dict[str, Any]:
    temp_db = database_path.with_name(f".{database_path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    temp_concept = concept_database_path.with_name(
        f".{concept_database_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    for path in (temp_db, temp_concept):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    connection = sqlite3.connect(temp_db)
    concept = sqlite3.connect(temp_concept)
    concept_fts = True
    try:
        connection.execute("PRAGMA journal_mode=OFF")
        connection.execute("PRAGMA synchronous=OFF")
        connection.execute(
            """
            CREATE TABLE paths (
                path TEXT PRIMARY KEY,
                root_name TEXT NOT NULL,
                root_path TEXT NOT NULL,
                kind TEXT NOT NULL,
                is_dir INTEGER NOT NULL,
                is_symlink INTEGER NOT NULL,
                size INTEGER,
                mtime_ns INTEGER,
                suffix TEXT,
                depth INTEGER NOT NULL,
                basename TEXT NOT NULL,
                parent TEXT,
                markers_json TEXT NOT NULL,
                excluded_reason TEXT
            )
            """
        )
        connection.execute("CREATE INDEX idx_paths_basename ON paths(basename)")
        connection.execute("CREATE INDEX idx_paths_root ON paths(root_name)")
        connection.execute("CREATE INDEX idx_paths_kind ON paths(kind)")
        connection.execute("CREATE INDEX idx_paths_mtime ON paths(mtime_ns)")
        connection.execute(
            "CREATE TABLE root_summary (root_name TEXT PRIMARY KEY, root_path TEXT, kind TEXT, exists_flag INTEGER, file_count INTEGER, directory_count INTEGER, byte_count INTEGER, excluded_directory_count INTEGER, error_count INTEGER)"
        )
        try:
            concept.execute(
                "CREATE VIRTUAL TABLE documents USING fts5(path UNINDEXED, title, headings, body, tokenize='unicode61 remove_diacritics 2')"
            )
        except sqlite3.OperationalError:
            concept_fts = False
            concept.execute(
                "CREATE TABLE documents(path TEXT PRIMARY KEY, title TEXT, headings TEXT, body TEXT)"
            )
            concept.execute("CREATE INDEX idx_documents_title ON documents(title)")

        total_paths = 0
        observed_paths = 0
        total_text_documents = 0
        text_content_candidate_count = 0
        empty_text_path_count = 0
        text_read_error_count = 0
        broken_text_symlink_count = 0
        text_empty_after_decode_count = 0
        total_bytes = 0
        errors: list[dict[str, str]] = []
        vault_candidates: dict[str, set[str]] = defaultdict(set)
        root_rows: list[dict[str, Any]] = []
        path_batch: list[tuple[Any, ...]] = []
        doc_batch: list[tuple[str, str, str, str]] = []
        fully_covered_roots: list[tuple[Path, str]] = []

        def flush() -> None:
            nonlocal path_batch, doc_batch
            if path_batch:
                connection.executemany(
                    "INSERT OR REPLACE INTO paths VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    path_batch,
                )
                path_batch = []
            if doc_batch:
                if concept_fts:
                    concept.executemany(
                        "INSERT INTO documents(path,title,headings,body) VALUES (?,?,?,?)",
                        doc_batch,
                    )
                else:
                    concept.executemany(
                        "INSERT OR REPLACE INTO documents(path,title,headings,body) VALUES (?,?,?,?)",
                        doc_batch,
                    )
                doc_batch = []

        for root_spec in SCAN_ROOTS:
            root = Path(root_spec["path"])
            root_name = root_spec["name"]
            root_kind = root_spec["kind"]
            root_scan_mode = root_spec.get("scan_mode", "full")
            root_files = 0
            root_indexed = 0
            root_dirs = 0
            root_bytes = 0
            root_excluded = 0
            root_errors = 0
            exists = root.exists()
            if not exists:
                root_rows.append(
                    {
                        "name": root_name,
                        "path": str(root),
                        "kind": root_kind,
                        "exists": False,
                        "file_count": 0,
                        "directory_count": 0,
                        "observed_path_count": 0,
                        "indexed_path_count": 0,
                        "coverage_class": "missing",
                        "scope_role": root_spec.get(
                            "scope_role",
                            "federated_external" if root_scan_mode == "federated" else "direct_source",
                        ),
                        "federated_search_tool": root_spec.get("federated_search_tool"),
                        "federated_tree_tool": root_spec.get("federated_tree_tool"),
                        "byte_count": 0,
                        "excluded_directory_count": 0,
                        "error_count": 0,
                    }
                )
                continue

            covering = next(
                (item for item in fully_covered_roots if root != item[0] and root.is_relative_to(item[0])),
                None,
            )
            if covering is not None:
                # Die Unterwurzel bleibt als eigener Navigations- und Herkunftsknoten
                # sichtbar, wird aber nicht ein zweites Mal gezählt oder volltextindiziert.
                flush()
                prefix = str(root).rstrip("/") + "/%"
                covered_files, covered_dirs, covered_bytes = connection.execute(
                    "SELECT "
                    "sum(CASE WHEN is_dir=0 THEN 1 ELSE 0 END), "
                    "sum(CASE WHEN is_dir=1 THEN 1 ELSE 0 END), "
                    "coalesce(sum(CASE WHEN is_dir=0 THEN size ELSE 0 END),0) "
                    "FROM paths WHERE path LIKE ?",
                    (prefix,),
                ).fetchone()
                covered_files = int(covered_files or 0)
                covered_dirs = int(covered_dirs or 0)
                covered_count = covered_files + covered_dirs
                root_rows.append(
                    {
                        "name": root_name,
                        "path": str(root),
                        "kind": root_kind,
                        "exists": True,
                        "file_count": covered_files,
                        "directory_count": covered_dirs,
                        "observed_path_count": covered_count,
                        "indexed_path_count": covered_count,
                        "coverage_class": "covered_by_parent_root",
                        "scope_role": "covered_alias",
                        "covered_by_root_name": covering[1],
                        "covered_by_root_path": str(covering[0]),
                        "federated_search_tool": root_spec.get("federated_search_tool"),
                        "federated_tree_tool": root_spec.get("federated_tree_tool"),
                        "byte_count": int(covered_bytes or 0),
                        "excluded_directory_count": 0,
                        "error_count": 0,
                    }
                )
                continue

            stack: list[tuple[Path, int]] = [(root, 0)]
            while stack:
                current, depth = stack.pop()
                try:
                    entries = list(os.scandir(current))
                except (PermissionError, FileNotFoundError, OSError) as exc:
                    root_errors += 1
                    if len(errors) < 250:
                        errors.append({"path": str(current), "error": repr(exc)})
                    continue
                entries.sort(key=lambda entry: entry.name.lower(), reverse=True)
                for entry in entries:
                    path = Path(entry.path)
                    if path == ATLAS_ROOT or ATLAS_ROOT in path.parents:
                        continue
                    try:
                        is_symlink = entry.is_symlink()
                        is_dir = entry.is_dir(follow_symlinks=False)
                        stat = entry.stat(follow_symlinks=False)
                    except (PermissionError, FileNotFoundError, OSError) as exc:
                        root_errors += 1
                        if len(errors) < 250:
                            errors.append({"path": str(path), "error": repr(exc)})
                        continue
                    excluded_reason = None
                    if is_dir and entry.name in SKIP_DIRECTORY_NAMES:
                        excluded_reason = "dependency_or_cache_subtree"
                        root_excluded += 1
                    elif is_symlink and not path.exists():
                        excluded_reason = "broken_symlink_target_missing"
                    kind = _path_kind(path, is_dir, is_symlink)
                    markers = _markers_for(path, is_dir)
                    if excluded_reason == "broken_symlink_target_missing":
                        markers.append("broken_symlink")
                    size = int(stat.st_size) if not is_dir else 0
                    observed_paths += 1
                    total_bytes += size
                    if is_dir:
                        root_dirs += 1
                    else:
                        root_files += 1
                        root_bytes += size
                    # Große Spezialkörper dürfen den globalen Atlas nicht aushungern.
                    # Föderierte Wurzeln werden vollständig gezählt, ihre Ordnerstruktur
                    # und kanonischen Einstiegspfade werden lokal indexiert; die Millionen
                    # Einzeldateien bleiben über das spezialisierte Suchorgan erreichbar.
                    should_index = total_paths < max_paths and (
                        root_scan_mode != "federated"
                        or is_dir
                        or depth == 0
                        or bool(markers)
                    )
                    if should_index:
                        total_paths += 1
                        root_indexed += 1
                        path_batch.append(
                            (
                                str(path),
                                root_name,
                                str(root),
                                kind,
                                int(is_dir),
                                int(is_symlink),
                                size,
                                int(stat.st_mtime_ns),
                                path.suffix.lower(),
                                depth + 1,
                                path.name,
                                str(path.parent),
                                json.dumps(markers, ensure_ascii=False),
                                excluded_reason,
                            )
                        )
                    if "obsidian_config" in markers:
                        vault_candidates[str(path.parent)].add(".obsidian")
                    if is_dir and entry.name in {"Verweise", "MOC"}:
                        vault_candidates[str(path.parent)].add(entry.name)
                    if "vault_builder" in markers:
                        vault_candidates[str(path.parent.parent)].add("build_obsidian_vault.py")
                    if "entry_or_manifest" in markers:
                        vault_candidates[str(path.parent)].add(path.name)
                    if (
                        should_index
                        and not is_dir
                        and path.suffix.lower() in TEXT_SUFFIXES
                        and size <= 2 * 1024 * 1024
                    ):
                        if size == 0:
                            empty_text_path_count += 1
                        elif excluded_reason == "broken_symlink_target_missing":
                            broken_text_symlink_count += 1
                        else:
                            text_content_candidate_count += 1
                            if total_text_documents < max_text_documents:
                                read_failed = False
                                try:
                                    raw = path.read_bytes()[:text_bytes_per_file]
                                    text = raw.decode("utf-8", errors="replace")
                                except (PermissionError, FileNotFoundError, OSError):
                                    text_read_error_count += 1
                                    read_failed = True
                                    text = ""
                                if text:
                                    headings = "\n".join(
                                        line.strip("# ")
                                        for line in text.splitlines()
                                        if line.lstrip().startswith("#")
                                    )[:12000]
                                    doc_batch.append((str(path), path.name, headings, text))
                                    total_text_documents += 1
                                elif not read_failed:
                                    text_empty_after_decode_count += 1
                    if is_dir and not is_symlink and excluded_reason is None:
                        stack.append((path, depth + 1))
                    if len(path_batch) >= 2000 or len(doc_batch) >= 250:
                        flush()
            observed_for_root = root_files + root_dirs
            root_rows.append(
                {
                    "name": root_name,
                    "path": str(root),
                    "kind": root_kind,
                    "exists": True,
                    "file_count": root_files,
                    "directory_count": root_dirs,
                    "observed_path_count": observed_for_root,
                    "indexed_path_count": root_indexed,
                    "coverage_class": (
                        "federated_complete" if root_scan_mode == "federated"
                        else "full_metadata" if root_indexed == observed_for_root
                        else "partial_due_global_limit"
                    ),
                    "scope_role": root_spec.get(
                        "scope_role",
                        "federated_external" if root_scan_mode == "federated" else "direct_source",
                    ),
                    "federated_search_tool": root_spec.get("federated_search_tool"),
                    "federated_tree_tool": root_spec.get("federated_tree_tool"),
                    "byte_count": root_bytes,
                    "excluded_directory_count": root_excluded,
                    "error_count": root_errors,
                }
            )
            flush()
            if root_scan_mode == "full":
                fully_covered_roots.append((root, root_name))
        root_letter_rows: list[dict[str, Any]] = []
        root_letter_files = 0
        root_letter_bytes = 0
        root_letter_errors = 0
        for letter_spec in ROOT_LETTERS:
            path = Path(str(letter_spec["path"]))
            stat = _safe_stat(path, follow_symlinks=False)
            exists = bool(stat and path.is_file())
            row = dict(letter_spec)
            row.update(
                {
                    "exists": exists,
                    "size": int(stat.st_size) if stat else None,
                    "mtime_ns": int(stat.st_mtime_ns) if stat else None,
                    "sha256": _sha256_file(path) if exists else None,
                    "coverage_class": "deep_read_and_indexed" if exists else "missing",
                    "source_type": "root_letter",
                }
            )
            root_letter_rows.append(row)
            if not exists:
                root_letter_errors += 1
                continue
            size = int(stat.st_size)
            observed_paths += 1
            total_bytes += size
            root_letter_files += 1
            root_letter_bytes += size
            if total_paths < max_paths:
                total_paths += 1
                markers = [
                    "root_letter",
                    str(letter_spec.get("identity_status") or "unknown_identity"),
                    *[f"target:{target}" for target in letter_spec.get("declared_targets", [])],
                ]
                path_batch.append(
                    (
                        str(path),
                        "root-letters",
                        "/root",
                        "text",
                        0,
                        int(path.is_symlink()),
                        size,
                        int(stat.st_mtime_ns),
                        path.suffix.lower(),
                        1,
                        path.name,
                        str(path.parent),
                        json.dumps(markers, ensure_ascii=False),
                        None,
                    )
                )
                if size == 0:
                    empty_text_path_count += 1
                else:
                    text_content_candidate_count += 1
                    if total_text_documents < max_text_documents:
                        read_failed = False
                        try:
                            raw = path.read_bytes()[:text_bytes_per_file]
                            letter_text = raw.decode("utf-8", errors="replace")
                        except (PermissionError, FileNotFoundError, OSError):
                            text_read_error_count += 1
                            read_failed = True
                            letter_text = ""
                        if letter_text:
                            headings = "\n".join(
                                line.strip("# ")
                                for line in letter_text.splitlines()
                                if line.lstrip().startswith("#")
                            )[:12000]
                            doc_batch.append((str(path), path.name, headings, letter_text))
                            total_text_documents += 1
                        elif not read_failed:
                            text_empty_after_decode_count += 1
        root_rows.append(
            {
                "name": "root-letters",
                "path": "/root",
                "kind": "explicit_root_letters",
                "exists": root_letter_files > 0,
                "file_count": root_letter_files,
                "directory_count": 0,
                "observed_path_count": root_letter_files,
                "indexed_path_count": root_letter_files,
                "coverage_class": "explicit_files_deep_read",
                "scope_role": "explicit_root_letters",
                "federated_search_tool": None,
                "federated_tree_tool": None,
                "byte_count": root_letter_bytes,
                "excluded_directory_count": 0,
                "error_count": root_letter_errors,
            }
        )
        flush()
        federated_source_bytes = sum(
            int(row.get("byte_count") or 0)
            for row in root_rows
            if row.get("scope_role") == "federated_external"
        )
        direct_source_bytes = sum(
            int(row.get("byte_count") or 0)
            for row in root_rows
            if row.get("scope_role") in {"direct_source", "curated_manual", "explicit_root_letters"}
        )
        curated_intake_bytes = sum(
            int(row.get("byte_count") or 0)
            for row in root_rows
            if row.get("scope_role") == "curated_manual"
        )
        federated_observed_paths = sum(
            int(row.get("observed_path_count") or 0)
            for row in root_rows
            if row.get("scope_role") == "federated_external"
        )
        direct_observed_paths = sum(
            int(row.get("observed_path_count") or 0)
            for row in root_rows
            if row.get("scope_role") in {"direct_source", "curated_manual", "explicit_root_letters"}
        )
        source_landscape_bytes = direct_source_bytes + federated_source_bytes
        connection.executemany(
            "INSERT OR REPLACE INTO root_summary VALUES (?,?,?,?,?,?,?,?,?)",
            [
                (
                    row["name"],
                    row["path"],
                    row["kind"],
                    int(row["exists"]),
                    row["file_count"],
                    row["directory_count"],
                    row["byte_count"],
                    row["excluded_directory_count"],
                    row["error_count"],
                )
                for row in root_rows
            ],
        )
        connection.commit()
        concept.commit()
        connection.execute("PRAGMA integrity_check").fetchone()
        concept.execute("PRAGMA integrity_check").fetchone()
    finally:
        connection.close()
        concept.close()
    os.replace(temp_db, database_path)
    os.replace(temp_concept, concept_database_path)
    return {
        "path_count": total_paths,
        "observed_path_count": observed_paths,
        "text_document_count": total_text_documents,
        "text_content_candidate_count": text_content_candidate_count,
        "empty_text_path_count": empty_text_path_count,
        "text_read_error_count": text_read_error_count,
        "broken_text_symlink_count": broken_text_symlink_count,
        "text_empty_after_decode_count": text_empty_after_decode_count,
        "byte_count": total_bytes,
        "byte_count_semantics": "source_landscape_logical_bytes_referenced_not_copied",
        "source_landscape_bytes": source_landscape_bytes,
        "direct_source_bytes": direct_source_bytes,
        "federated_source_bytes": federated_source_bytes,
        "curated_intake_bytes": curated_intake_bytes,
        "direct_observed_path_count": direct_observed_paths,
        "federated_observed_path_count": federated_observed_paths,
        "path_limit": max_paths,
        "text_document_limit": max_text_documents,
        "text_bytes_per_file": text_bytes_per_file,
        "path_limit_reached": total_paths >= max_paths,
        "text_document_limit_reached": (
            text_content_candidate_count
            - text_read_error_count
            - text_empty_after_decode_count
            > total_text_documents
        ),
        "concept_index_mode": "fts5" if concept_fts else "plain_sqlite",
        "roots": root_rows,
        "root_letters": root_letter_rows,
        "vault_candidates": [
            {
                "path": path,
                "markers": sorted(markers),
                "origin_class": (
                    "generated_snapshot"
                    if "/truth_engine/generations/" in path
                    else "backup_or_import"
                    if any(token in path for token in ("/backups/", "/_import_", "/audit/", "/_gpt/tests/"))
                    else "canonical_or_live"
                ),
            }
            for path, markers in sorted(vault_candidates.items())
            if (
                ".obsidian" in markers
                or "build_obsidian_vault.py" in markers
                or ({"Verweise", "MOC"} <= markers)
            )
        ],
        "errors": errors,
    }


def _history_snapshot() -> dict[str, Any]:
    sessions: dict[str, dict[str, Any]] = {}
    event_count = 0
    last_event_id = None
    last_event_hash = None
    last_timestamp = None
    if HISTORY_PATH.exists():
        with HISTORY_PATH.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                event_count += 1
                sid = str(event.get("session_id") or "unknown")
                row = sessions.setdefault(
                    sid,
                    {
                        "session_id": sid,
                        "actor": event.get("actor"),
                        "started_utc": None,
                        "ended_utc": None,
                        "last_timestamp_utc": None,
                        "last_action": None,
                        "last_status": None,
                        "event_count": 0,
                        "mutation_count": 0,
                        "failure_count": 0,
                        "targets": Counter(),
                    },
                )
                action = str(event.get("action") or "")
                row["event_count"] += 1
                row["last_timestamp_utc"] = event.get("timestamp_utc")
                row["last_action"] = action
                row["last_status"] = event.get("status")
                if action == "session.begin":
                    row["started_utc"] = event.get("timestamp_utc")
                if action == "session.end":
                    row["ended_utc"] = event.get("timestamp_utc")
                if action.startswith(MUTATING_TOOL_PREFIXES) or any(
                    token in action for token in ("completed", "marker", "commit", "write", "edit", "move", "delete")
                ):
                    row["mutation_count"] += 1
                if event.get("status") in {"failed", "blocked"}:
                    row["failure_count"] += 1
                target = event.get("target")
                if isinstance(target, str) and target and len(target) < 600:
                    row["targets"][target] += 1
                last_event_id = event.get("event_id")
                last_event_hash = event.get("event_hash")
                last_timestamp = event.get("timestamp_utc")
    rows = []
    for row in sessions.values():
        row = dict(row)
        row["open"] = bool(row.get("started_utc") and not row.get("ended_utc"))
        row["targets"] = [target for target, _count in row["targets"].most_common(12)]
        rows.append(row)
    rows.sort(key=lambda value: value.get("last_timestamp_utc") or "", reverse=True)
    return {
        "event_count": event_count,
        "session_count": len(rows),
        "open_session_count": sum(1 for row in rows if row["open"]),
        "last_event_id": last_event_id,
        "last_event_hash": last_event_hash,
        "last_timestamp_utc": last_timestamp,
        "sessions": rows,
    }


def _directory_stats(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "file_count": 0, "latest_modified_utc": None}
    file_count = 0
    latest_ns = 0
    try:
        for child in path.rglob("*"):
            if not child.is_file():
                continue
            file_count += 1
            stat = _safe_stat(child)
            if stat:
                latest_ns = max(latest_ns, stat.st_mtime_ns)
    except (PermissionError, OSError):
        pass
    latest = None
    if latest_ns:
        latest = dt.datetime.fromtimestamp(latest_ns / 1_000_000_000, tz=dt.timezone.utc).isoformat()
    return {"exists": True, "file_count": file_count, "latest_modified_utc": latest}


def _root_letter_registry() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in ROOT_LETTERS:
        path = Path(str(spec["path"]))
        stat = _safe_stat(path, follow_symlinks=False)
        exists = bool(stat and path.is_file())
        row = dict(spec)
        row.update(
            {
                "exists": exists,
                "size": int(stat.st_size) if stat else None,
                "mtime_ns": int(stat.st_mtime_ns) if stat else None,
                "sha256": _sha256_file(path) if exists else None,
                "coverage_class": "deep_read_and_indexed" if exists else "missing",
                "source_type": "root_letter",
            }
        )
        rows.append(row)
    return rows


def _ai_stream_registry(
    history: dict[str, Any],
    root_letters: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    letter_by_path = {row.get("path"): row for row in (root_letters or _root_letter_registry())}
    rows = []
    for spec in AI_STREAMS:
        home_raw = spec.get("home")
        sessions_raw = spec.get("sessions")
        home = Path(str(home_raw)) if home_raw else None
        session_source = Path(str(sessions_raw)) if sessions_raw else None
        if session_source is None:
            session_stats = {
                "exists": False,
                "file_count": 0,
                "latest_modified_utc": None,
                "classification": "no_confirmed_session_store",
            }
        elif session_source.is_dir():
            session_stats = _directory_stats(session_source)
            session_stats["classification"] = "directory_session_store"
        else:
            session_stats = {
                "exists": session_source.exists(),
                "file_count": history.get("session_count", 0) if session_source == HISTORY_PATH else int(session_source.exists()),
                "latest_modified_utc": history.get("last_timestamp_utc") if session_source == HISTORY_PATH else (
                    dt.datetime.fromtimestamp(session_source.stat().st_mtime, tz=dt.timezone.utc).isoformat()
                    if session_source.exists() else None
                ),
                "classification": "file_session_store",
            }
        entry_files = []
        for declared_path in spec.get("entry_paths", []):
            candidate = Path(str(declared_path))
            if candidate.exists() and candidate.is_file():
                entry_files.append(str(candidate))
        if home and home.is_dir():
            for name in (
                "START_HIER.md",
                "ZUHAUSE.md",
                "WERKRAUM_KARTE.md",
                "RESONANZFELD.md",
                "brief_an_mich.md",
                "BRIEF_AN_NAECHSTE_SESSION.md",
                "README.md",
            ):
                candidate = home / name
                if candidate.exists() and str(candidate) not in entry_files:
                    entry_files.append(str(candidate))
        linked_letters = [
            letter_by_path[path]
            for path in spec.get("root_letter_paths", [])
            if path in letter_by_path
        ]
        rows.append(
            {
                **spec,
                "home_exists": bool(home and home.exists()),
                "entry_files": entry_files,
                "root_letters": linked_letters,
                "session_source_stats": session_stats,
            }
        )
    return rows


def _service_registry() -> list[dict[str, Any]]:
    try:
        raw = subprocess.check_output(
            [
                "systemctl",
                "list-units",
                "--all",
                "--type=service",
                "--no-legend",
                "--no-pager",
                "--plain",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
    except (subprocess.SubprocessError, OSError):
        return []
    wanted = re.compile(
        r"(flextrawurst|mcp|browser-agent|codewesen|geni|zensi|llama|ollama|postgres|nginx|flarum|godot|tts)",
        re.I,
    )
    rows = []
    for line in raw.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 4:
            continue
        unit, load, active, sub = parts[:4]
        description = parts[4] if len(parts) > 4 else ""
        if not wanted.search(unit + " " + description):
            continue
        rows.append(
            {
                "unit": unit,
                "load": load,
                "active": active,
                "sub": sub,
                "description": description,
            }
        )
    return sorted(rows, key=lambda row: row["unit"])


def _project_classification(row: dict[str, Any]) -> dict[str, Any]:
    path = Path(str(row.get("path") or ""))
    raw_path = str(path)
    name = path.name
    markers = set(row.get("markers") or [])
    if "/_gpt/tests/" in raw_path or "/tests/fixtures/" in raw_path:
        project_class = "test_fixture"
    elif raw_path in {"/root", "/root/werkraum"}:
        project_class = "container_root"
    elif re.search(r"(?:\.backup[-_]|/backups?/|/_backups(?:/|$))", raw_path, re.I):
        project_class = "backup_snapshot"
    elif name.lower() in {"verweise", "zeitstrom", "moc"} or markers.intersection({"verweise", "zeitstrom", "moc"}):
        project_class = "structural_view"
    elif name in {"_archive", "_exports", "_quarantaene"}:
        project_class = "storage_area"
    elif name in {"_ops", "_ordnung"}:
        project_class = "operations_area"
    elif raw_path.startswith("/root/werkraum/_gpt/") or name in {"_claude", "_claudeweb", "_codex", "_kimi", "_gemini", "_glm"}:
        project_class = "system_component"
    elif "registered_scan_root" in markers and (
        row.get("git")
        or row.get("truth_engine")
        or row.get("coordination")
        or "README.md" in markers
        or "START_HIER.md" in markers
        or "MANIFEST.json" in markers
    ):
        project_class = "canonical_project"
    elif path.parent == Path("/root/werkraum") and (
        row.get("git")
        or row.get("truth_engine")
        or row.get("coordination")
        or "README.md" in markers
        or "MANIFEST.json" in markers
    ):
        project_class = "canonical_project"
    elif "/engine/" in raw_path or name in {"datei_wandler"}:
        project_class = "project_component"
    else:
        project_class = "project_component"
    priority = {
        "canonical_project": 100,
        "project_component": 80,
        "system_component": 75,
        "operations_area": 55,
        "structural_view": 45,
        "storage_area": 25,
        "backup_snapshot": 15,
        "container_root": 10,
        "test_fixture": 0,
    }[project_class]
    return {
        "project_class": project_class,
        "primary_project": project_class == "canonical_project",
        "bridge_eligible": project_class in {"canonical_project", "project_component", "system_component"},
        "revision_eligible": project_class != "test_fixture",
        "navigational_priority": priority,
    }


def _finalize_project_registry(candidates: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in candidates.values():
        row = dict(row)
        row.update(_project_classification(row))
        if row["project_class"] == "test_fixture":
            continue
        rows.append(row)
    canonical = [row for row in rows if row["project_class"] == "canonical_project"]
    by_path = {str(row["path"]): row for row in rows}
    for row in rows:
        path = str(row["path"])
        ancestors = [
            parent
            for parent in canonical
            if str(parent["path"]) != path and path.startswith(str(parent["path"]).rstrip("/") + "/")
        ]
        parent = max(ancestors, key=lambda item: len(str(item["path"])), default=None)
        row["canonical_parent_project_id"] = parent.get("project_id") if parent else None
        row["canonical_parent_path"] = parent.get("path") if parent else None
        if row["project_class"] == "backup_snapshot":
            base = re.split(r"\.backup[-_]", path, maxsplit=1, flags=re.I)[0]
            source = by_path.get(base)
            row["backup_of_project_id"] = source.get("project_id") if source else None
            row["backup_of_path"] = source.get("path") if source else base
        else:
            row["backup_of_project_id"] = None
            row["backup_of_path"] = None
    return sorted(
        rows,
        key=lambda row: (
            -int(row.get("navigational_priority") or 0),
            -int(row.get("score") or 0),
            str(row.get("path") or ""),
        ),
    )


def _project_registry(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    rows = connection.execute(
        "SELECT path,root_name,kind,depth,markers_json,excluded_reason FROM paths WHERE is_dir=1 AND (depth<=2 OR markers_json!='[]')"
    ).fetchall()
    for path, root_name, kind, depth, markers_json, excluded_reason in rows:
        if excluded_reason:
            continue
        p = Path(path)
        markers = set(json.loads(markers_json or "[]"))
        score = 0
        reasons: list[str] = []
        for marker in ("coordination", "sessions", "validation", "verweise", "moc", "zeitstrom"):
            if marker in markers:
                score += 2
                reasons.append(marker)
        if depth <= 1 and root_name == "werkraum":
            score += 1
            reasons.append("werkraum_top_level")
        for child_name, weight in (
            (".git", 3),
            ("README.md", 2),
            ("START_HIER.md", 3),
            ("truth_engine", 3),
            ("coordination", 2),
            ("tools", 1),
            ("MANIFEST.json", 2),
        ):
            if (p / child_name).exists():
                score += weight
                reasons.append(child_name)
        if score < 3:
            continue
        candidates[path] = {
            "project_id": hashlib.sha256(path.encode("utf-8")).hexdigest()[:16],
            "name": p.name,
            "path": path,
            "root_name": root_name,
            "score": score,
            "markers": sorted(set(reasons)),
            "git": (p / ".git").exists(),
            "truth_engine": (p / "truth_engine").exists(),
            "coordination": (p / "coordination").exists(),
            "generated_views": [
                str(candidate)
                for candidate in (
                    p / "HOME.md",
                    p / "GESPRAECHSNETZ.md",
                    p / "ZEITSTROM.md",
                    p / "UHRZEITENERLEBNIS.md",
                    p / "AKTUELLE_WAHRHEIT.md",
                )
                if candidate.exists()
            ],
        }
    # Die Scanwurzel selbst steht nicht in der paths-Tabelle, weil dort ihre
    # Kinder beginnen. Sie muss dennoch als möglicher Projektkörper bewertet
    # werden, sonst kennt der Atlas jedes Haus, aber nicht die Stadt.
    for root_name, root_path, _kind, exists_flag, *_rest in connection.execute(
        "SELECT root_name,root_path,kind,exists_flag,file_count,directory_count,byte_count,excluded_directory_count,error_count FROM root_summary"
    ):
        if not exists_flag or root_path in candidates:
            continue
        p = Path(root_path)
        score = 0
        reasons: list[str] = ["registered_scan_root"]
        for child_name, weight in (
            (".git", 3),
            ("README.md", 2),
            ("START_HIER.md", 3),
            ("truth_engine", 3),
            ("coordination", 2),
            ("tools", 1),
            ("MANIFEST.json", 2),
        ):
            if (p / child_name).exists():
                score += weight
                reasons.append(child_name)
        if score < 3:
            continue
        candidates[root_path] = {
            "project_id": hashlib.sha256(root_path.encode("utf-8")).hexdigest()[:16],
            "name": p.name,
            "path": root_path,
            "root_name": root_name,
            "score": score,
            "markers": sorted(set(reasons)),
            "git": (p / ".git").exists(),
            "truth_engine": (p / "truth_engine").exists(),
            "coordination": (p / "coordination").exists(),
            "generated_views": [
                str(candidate)
                for candidate in (
                    p / "HOME.md",
                    p / "GESPRAECHSNETZ.md",
                    p / "ZEITSTROM.md",
                    p / "UHRZEITENERLEBNIS.md",
                    p / "AKTUELLE_WAHRHEIT.md",
                )
                if candidate.exists()
            ],
        }
    return _finalize_project_registry(candidates)


def _format_bytes(value: int | None) -> str:
    number = float(value or 0)
    units = ("B", "KB", "MB", "GB", "TB")
    unit = units[0]
    for candidate in units:
        unit = candidate
        if abs(number) < 1000.0 or candidate == units[-1]:
            break
        number /= 1000.0
    return f"{number:.2f} {unit}".replace(".", ",")


def _size_truth(scan: dict[str, Any]) -> dict[str, Any]:
    excluded = {
        ATLAS_ROOT / "GROESSENWAHRHEIT.json",
        STATUS_PATH,
        ATLAS_ROOT / "GESAMTKARTE.md",
        ATLAS_ROOT / "HEUTE.md",
    }
    logical = 0
    allocated = 0
    file_count = 0
    if ATLAS_ROOT.exists():
        for path in ATLAS_ROOT.rglob("*"):
            if not path.is_file() or path in excluded:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            logical += int(stat.st_size)
            allocated += int(getattr(stat, "st_blocks", 0)) * 512
            file_count += 1
    index_paths = [PATH_DB, CONCEPT_DB, RELATION_DB]
    index_bytes = sum(path.stat().st_size for path in index_paths if path.exists())
    capsule = ATLAS_ROOT / "GESAMTATLAS_KAPSEL_AKTUELL.zip"
    return {
        "schema_version": "1.0",
        "measurement_semantics": "separate_source_landscape_from_generated_atlas",
        "source_landscape_logical_bytes": int(scan.get("source_landscape_bytes") or scan.get("byte_count") or 0),
        "direct_source_logical_bytes": int(scan.get("direct_source_bytes") or 0),
        "federated_external_logical_bytes": int(scan.get("federated_source_bytes") or 0),
        "curated_intake_logical_bytes": int(scan.get("curated_intake_bytes") or 0),
        "local_index_bytes": int(index_bytes),
        "atlas_workspace_logical_bytes_excluding_self_reports": int(logical),
        "atlas_workspace_allocated_bytes_excluding_self_reports": int(allocated),
        "atlas_workspace_file_count_excluding_self_reports": int(file_count),
        "portable_capsule_bytes": capsule.stat().st_size if capsule.exists() else 0,
        "portable_capsule_path": str(capsule),
        "manual_intake_path": "/root/werkraum_gesamtatlas_eingang",
        "measurement_excludes": [str(path) for path in sorted(excluded, key=str)],
        "einschraenkung": (
            "Die Quelllandschaft ist referenziertes Ausgangsmaterial und keine Atlas-Dateigröße. "
            "Föderierte Außenkörper wie Zensi werden nicht in den lokalen Volltextindex kopiert."
        ),
    }


def _write_human_maps(
    *,
    status: dict[str, Any],
    projects: list[dict[str, Any]],
    vaults: list[dict[str, Any]],
    services: list[dict[str, Any]],
    streams: list[dict[str, Any]],
    root_letters: list[dict[str, Any]],
    sessions: dict[str, Any],
) -> None:
    generated = status["generated_utc"]
    lines = [
        "# Gesamtkarte",
        "",
        f"> Regenerierbare Übersicht. Revision `{status['revision']}`, erzeugt `{generated}`.",
        "> Primärquellen bleiben an ihren Ursprungsorten; diese Karte ersetzt sie nicht.",
        "",
        "## Soforteinstiege",
        "",
        f"- Atlasstatus: `{STATUS_PATH}`",
        f"- Größenwahrheit: `{ATLAS_ROOT / 'GROESSENWAHRHEIT.json'}`",
        "- Kuratierter manueller Eingang: `/root/werkraum_gesamtatlas_eingang/START_HIER.md`",
        f"- Pfadindex: `{PATH_DB}`",
        f"- Volltext-/Begriffsindex: `{CONCEPT_DB}`",
        f"- Änderungen: `{CHANGE_LOG}`",
        f"- Konsens: `{CONSENSUS_LOG}`",
        f"- Konflikte: `{CONFLICT_LOG}`",
        f"- Eingebungsprovenienz: `{IDEA_LOG}`",
        "",
        "## Umfang",
        "",
        f"- beobachtete Pfade: **{status['scan'].get('observed_path_count', status['scan']['path_count']):,}**".replace(",", "."),
        f"- lokal indexierte Pfade: **{status['scan']['path_count']:,}**".replace(",", "."),
        f"- volltextindizierte Dokumente: **{status['scan']['text_document_count']:,}**".replace(",", "."),
        f"- referenzierte Quelllandschaft, **nicht Atlasgröße**: **{_format_bytes(status.get('sizes', {}).get('source_landscape_logical_bytes', status['scan'].get('source_landscape_bytes')))}**",
        f"- direkte, lokal erschlossene Quellen: **{_format_bytes(status.get('sizes', {}).get('direct_source_logical_bytes', status['scan'].get('direct_source_bytes')))}**",
        f"- föderierte Außenkörper, nicht lokal kopiert: **{_format_bytes(status.get('sizes', {}).get('federated_external_logical_bytes', status['scan'].get('federated_source_bytes')))}**",
        f"- erzeugter Atlas-Arbeitskörper: **{_format_bytes(status.get('sizes', {}).get('atlas_workspace_logical_bytes_excluding_self_reports'))}**",
        f"- tragbare private Kapsel: **{_format_bytes(status.get('sizes', {}).get('portable_capsule_bytes'))}**",
        f"- kanonische Projekte: **{sum(1 for row in projects if row.get('primary_project'))}**",
        f"- Projekt-/Komponenten-/Strukturknoten: **{len(projects)}**",
        f"- Vault-/Bedeutungsnetzkandidaten: **{len(vaults)}**",
        f"- relevante Dienste: **{len(services)}**",
        f"- technische History-Sessions: **{sessions['session_count']}**",
        f"- technisch offene Sessionhüllen: **{sessions['open_session_count']}**",
        "",
        "## Projekte",
        "",
    ]
    for project_class in (
        "canonical_project",
        "project_component",
        "system_component",
        "operations_area",
        "structural_view",
        "storage_area",
        "backup_snapshot",
        "container_root",
    ):
        class_rows = [row for row in projects if row.get("project_class") == project_class]
        if not class_rows:
            continue
        lines.extend(["", f"### {project_class}", ""])
        for row in class_rows[:120]:
            lines.append(
                f"- **{row['name']}** · `{row['path']}` · r{row.get('project_revision', 0)} · Beziehungen {sum((row.get('relationship_counts') or {}).values())} · Marker: {', '.join(row['markers'][:8]) or 'keine'}"
            )
    lines.extend(["", "## Vaults und Bedeutungsnetze", ""])
    for row in vaults[:150]:
        lines.append(f"- `{row['path']}` · {', '.join(row['markers'])}")
    lines.extend(["", "## Wurzelbriefe", ""])
    for row in root_letters:
        lines.append(
            f"- `{row['path']}` · Datei-Label **{row.get('filename_label')}** · erklärte Ziele {', '.join(row.get('declared_targets', [])) or 'keine'} · `{row.get('identity_status')}`"
        )
    lines.extend(["", "## AI-Ströme", ""])
    for row in streams:
        home = row.get("home") or "kein bestätigtes Zuhause"
        sessions_source = row.get("sessions") or "kein bestätigter Session-Store"
        letters = ", ".join(letter.get("path", "") for letter in row.get("root_letters", [])) or "keine"
        lines.append(
            f"- **{row['id']}** · Zuhause `{home}` · Sitzungsquelle `{sessions_source}` · Wurzelbriefe {letters} · Dateien {row['session_source_stats']['file_count']}"
        )
    lines.extend(["", "## Dienste", ""])
    for row in services:
        lines.append(f"- `{row['unit']}` · {row['active']}/{row['sub']} · {row['description']}")
    lines.extend(
        [
            "",
            "## Einschraenkung",
            "",
            "- Ein Pfadfund beweist Existenz, nicht fachliche Gültigkeit.",
            "- Volltextähnlichkeit ist kein Konsensbeweis.",
            "- Zwei ähnliche Ideen werden nicht automatisch als unabhängig oder übernommen bezeichnet.",
            "- Konsens, Konflikt und Eingebungsprovenienz besitzen eigene append-only Register.",
            "",
        ]
    )
    _atomic_write_text(ATLAS_ROOT / "GESAMTKARTE.md", "\n".join(lines))

    today = dt.datetime.now().astimezone().date().isoformat()
    changes = _read_jsonl(CHANGE_LOG, limit=80)
    day_lines = ["# Heute im Gesamtatlas", "", f"Datum: `{today}`", "", "## Letzte Änderungen", ""]
    for row in reversed(changes):
        day_lines.append(
            f"- `{row.get('timestamp_utc')}` · r{row.get('revision')} · **{row.get('kind')}** · {row.get('summary')}"
        )
    _atomic_write_text(ATLAS_ROOT / "HEUTE.md", "\n".join(day_lines) + "\n")


def stable_change_id(payload: dict[str, Any], revision: int, generated_utc: str) -> str:
    return hashlib.sha256(
        json.dumps(
            {"payload": payload, "revision": revision, "generated_utc": generated_utc},
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()[:24]


def refresh_atlas(
    *,
    mode: str = "full",
    reason: str = "manual",
    session_id: str | None = None,
    max_paths: int | None = None,
    max_text_documents: int | None = None,
) -> dict[str, Any]:
    if mode not in {"full", "light"}:
        raise AtlasError("mode muss 'full' oder 'light' sein")
    _ensure_layout()
    with _atlas_lock():
        old_status = _read_json(STATUS_PATH, {}) or {}
        old_revision = int(old_status.get("revision") or 0)
        history = _history_snapshot()
        root_letters = _root_letter_registry()
        streams = _ai_stream_registry(history, root_letters)
        services = _service_registry()
        if mode == "full" or not PATH_DB.exists() or not CONCEPT_DB.exists():
            scan = _scan_paths(
                PATH_DB,
                CONCEPT_DB,
                max_paths=max_paths
                or int(os.environ.get("FLEXTRAWURST_ATLAS_MAX_PATHS", "350000")),
                max_text_documents=max_text_documents
                or int(os.environ.get("FLEXTRAWURST_ATLAS_MAX_TEXT_DOCUMENTS", "150000")),
                text_bytes_per_file=int(
                    os.environ.get("FLEXTRAWURST_ATLAS_TEXT_BYTES_PER_FILE", "49152")
                ),
            )
        else:
            scan = dict(old_status.get("scan") or {})
            scan["reused_from_revision"] = old_revision
        root_letters = list(scan.get("root_letters") or root_letters)
        streams = _ai_stream_registry(history, root_letters)
        connection = sqlite3.connect(PATH_DB)
        try:
            projects = _project_registry(connection)
        finally:
            connection.close()
        vaults = list(scan.get("vault_candidates") or _read_json(ATLAS_ROOT / "VAULTREGISTER.json", []))
        generated = _utcnow()
        relational = build_relational_layer(
            atlas_root=ATLAS_ROOT,
            path_db=PATH_DB,
            concept_db=CONCEPT_DB,
            history_path=HISTORY_PATH,
            projects=projects,
            vaults=vaults,
            services=services,
            streams=streams,
            history_snapshot=history,
            consensus_rows=_read_jsonl(CONSENSUS_LOG),
            conflict_rows=_read_jsonl(CONFLICT_LOG),
            generated_utc=generated,
            refresh_mode=mode,
        )
        projects = relational["projects"]
        services = relational["services"]
        streams = relational["streams"]
        history = relational["history"]
        revision = old_revision + 1
        status = {
            "schema_version": "1.0",
            "atlas_id": "mcp-gesamtatlas",
            "revision": revision,
            "generated_utc": generated,
            "mode": mode,
            "reason": reason,
            "session_id": session_id,
            "history": {key: history.get(key) for key in history if key != "sessions"},
            "scan": scan,
            "counts": {
                "projects": len(projects),
                "vaults": len(vaults),
                "services": len(services),
                "ai_streams": len(streams),
                "root_letters": len(root_letters),
                "sessions": history["session_count"],
                "claims": len((relational.get("claims") or {}).get("claims") or []),
                "handoffs": len((relational.get("handoffs") or {}).get("handoffs") or []),
                "relationship_nodes": int((relational.get("relationships") or {}).get("node_count") or 0),
                "relationship_edges": int((relational.get("relationships") or {}).get("edge_count") or 0),
                "urbewohner": int((((relational.get("relationships") or {}).get("urbewohner") or {}).get("canonical_entities")) or 0),
                "urbewohner_facets": int((((relational.get("relationships") or {}).get("urbewohner") or {}).get("source_facets")) or 0),
                "urbewohner_gedanken": int((((relational.get("relationships") or {}).get("urbewohner") or {}).get("thought_nodes")) or 0),
                "geni_knoten": int((((relational.get("relationships") or {}).get("urbewohner") or {}).get("geni_nodes")) or 0),
            },
            "relational_paths": relational.get("paths", {}),
            "dirty": (
                False if mode == "full" else bool(old_status.get("dirty", False))
            ),
            "full_refresh_recommended": (
                False
                if mode == "full"
                else bool(old_status.get("full_refresh_recommended", False))
            ),
            "datenstand": (
                "LIVE_VALIDATED_PROVISIONAL"
                if mode == "full" or not bool(old_status.get("dirty", False))
                else "STALE_METADATA_PROVISIONAL"
            ),
        }
        _atomic_write_json(ATLAS_ROOT / "WURZELREGISTER.json", scan.get("roots", []))
        _atomic_write_json(ATLAS_ROOT / "WURZELBRIEFE.json", root_letters)
        _atomic_write_json(ATLAS_ROOT / "PROJEKTREGISTER.json", projects)
        _atomic_write_json(ATLAS_ROOT / "SYSTEMREGISTER.json", services)
        _atomic_write_json(ATLAS_ROOT / "DIENSTREGISTER.json", services)
        _atomic_write_json(ATLAS_ROOT / "VAULTREGISTER.json", vaults)
        _atomic_write_json(ATLAS_ROOT / "AI_STROEME.json", streams)
        _atomic_write_json(ATLAS_ROOT / "SESSIONREGISTER.json", history)
        _atomic_write_json(STATUS_PATH, status)
        change = {
            "schema_version": "1.0",
            "change_id": hashlib.sha256(
                f"{revision}|{generated}|{reason}|{session_id}".encode("utf-8")
            ).hexdigest()[:24],
            "timestamp_utc": generated,
            "revision": revision,
            "kind": "atlas_refresh",
            "summary": f"Gesamtatlas {mode} aktualisiert: {scan.get('path_count', 0)} Pfade, {len(projects)} Projekte, {len(vaults)} Vaults.",
            "session_id": session_id,
            "reason": reason,
            "source_history_event_id": history.get("last_event_id"),
            "source_history_event_hash": history.get("last_event_hash"),
            "relationship_nodes": int((relational.get("relationships") or {}).get("node_count") or 0),
            "relationship_edges": int((relational.get("relationships") or {}).get("edge_count") or 0),
            "handoff_count": len((relational.get("handoffs") or {}).get("handoffs") or []),
        }
        _append_jsonl(CHANGE_LOG, change)
        for derived in list(relational.get("project_changes") or []) + list(relational.get("stream_changes") or []):
            derived = dict(derived)
            derived.update(
                {
                    "schema_version": "1.0",
                    "change_id": stable_change_id(derived, revision, generated),
                    "timestamp_utc": generated,
                    "revision": revision,
                    "session_id": session_id,
                }
            )
            _append_jsonl(CHANGE_LOG, derived)
        _write_human_maps(
            status=status,
            projects=projects,
            vaults=vaults,
            services=services,
            streams=streams,
            root_letters=root_letters,
            sessions=history,
        )
        if mode == "full":
            sizes = _size_truth(scan)
            sizes["measured_utc"] = generated
            sizes["atlas_revision"] = revision
            _atomic_write_json(ATLAS_ROOT / "GROESSENWAHRHEIT.json", sizes)
        else:
            sizes = dict(old_status.get("sizes") or {})
            if sizes:
                sizes["reused_from_revision"] = old_revision
        status["sizes"] = sizes
        _atomic_write_json(STATUS_PATH, status)
        _write_human_maps(
            status=status,
            projects=projects,
            vaults=vaults,
            services=services,
            streams=streams,
            root_letters=root_letters,
            sessions=history,
        )
        return {
            "ok": True,
            "status": status,
            "paths": {
                "root": str(ATLAS_ROOT),
                "map": str(ATLAS_ROOT / "GESAMTKARTE.md"),
                "today": str(ATLAS_ROOT / "HEUTE.md"),
                "path_index": str(PATH_DB),
                "concept_index": str(CONCEPT_DB),
                **relational.get("paths", {}),
            },
            "relationships": relational.get("relationships", {}),
            "handoff_count": len((relational.get("handoffs") or {}).get("handoffs") or []),
        }


def atlas_snapshot() -> dict[str, Any]:
    _ensure_layout()
    status = _read_json(STATUS_PATH, {}) or {}
    return {
        "ok": bool(status),
        "atlas_root": str(ATLAS_ROOT),
        "status_path": str(STATUS_PATH),
        "map_path": str(ATLAS_ROOT / "GESAMTKARTE.md"),
        "today_path": str(ATLAS_ROOT / "HEUTE.md"),
        "revision": status.get("revision"),
        "generated_utc": status.get("generated_utc"),
        "datenstand": status.get("datenstand"),
        "dirty": status.get("dirty"),
        "full_refresh_recommended": status.get("full_refresh_recommended"),
        "counts": status.get("counts", {}),
        "scan": {
            key: (status.get("scan") or {}).get(key)
            for key in (
                "path_count",
                "observed_path_count",
                "text_document_count",
                "text_content_candidate_count",
                "empty_text_path_count",
                "text_read_error_count",
                "broken_text_symlink_count",
                "text_empty_after_decode_count",
                "path_limit_reached",
                "text_document_limit_reached",
                "concept_index_mode",
            )
        },
    }


def _cursor_path(session_id: str) -> Path:
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    return CURSOR_ROOT / f"{digest}.json"


def _cursor_lock_path(session_id: str) -> Path:
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    return CURSOR_ROOT / f"{digest}.lock"


@contextlib.contextmanager
def _session_cursor_lock(session_id: str) -> Iterator[None]:
    _ensure_layout()
    path = _cursor_lock_path(session_id)
    with path.open("a+", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _history_delta(offset: int, *, initial_limit: int = 400) -> tuple[list[dict[str, Any]], int]:
    if not HISTORY_PATH.exists():
        return [], 0
    size = HISTORY_PATH.stat().st_size
    if offset < 0 or offset > size:
        offset = 0
    events: list[dict[str, Any]] = []
    with HISTORY_PATH.open("rb") as handle:
        if offset:
            handle.seek(offset)
        raw = handle.read()
        new_offset = handle.tell()
    for line in raw.splitlines():
        try:
            event = json.loads(line.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    if offset == 0 and len(events) > initial_limit:
        events = events[-initial_limit:]
    return events, new_offset


def _jsonl_delta(path: Path, offset: int, *, initial_limit: int = 200) -> tuple[list[dict[str, Any]], int]:
    if not path.exists():
        return [], 0
    size = path.stat().st_size
    if offset < 0 or offset > size:
        offset = 0
    rows = []
    with path.open("rb") as handle:
        if offset:
            handle.seek(offset)
        raw = handle.read()
        new_offset = handle.tell()
    for line in raw.splitlines():
        try:
            value = json.loads(line.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    if offset == 0 and len(rows) > initial_limit:
        rows = rows[-initial_limit:]
    return rows, new_offset


def _event_significance(event: dict[str, Any]) -> str:
    action = str(event.get("action") or "")
    status = str(event.get("status") or "")
    if status in {"failed", "blocked"}:
        return "failure_or_blocker"
    if action == "session.end":
        return "session_completed"
    if action == "session.begin":
        return "session_started"
    if action.startswith(MUTATING_TOOL_PREFIXES):
        return "mutation"
    if any(token in action for token in ("completed", "marker", "commit", "validated", "consensus", "conflict")):
        return "meaningful_marker"
    if action.startswith(LOW_SIGNAL_ACTION_PREFIXES):
        return "read_or_orientation"
    return "other"


def _compact_event(event: dict[str, Any]) -> dict[str, Any]:
    details = event.get("details") if isinstance(event.get("details"), dict) else {}
    summary = None
    for key in ("summary", "result", "reason", "task", "title"):
        value = details.get(key)
        if isinstance(value, str) and value.strip():
            summary = value.strip()[:420]
            break
    target = event.get("target")
    if not summary and isinstance(target, str):
        summary = target.splitlines()[0][:420]
    return {
        "event_id": event.get("event_id"),
        "timestamp_utc": event.get("timestamp_utc"),
        "timestamp_berlin": event.get("timestamp_berlin"),
        "session_id": event.get("session_id"),
        "actor": event.get("actor"),
        "action": event.get("action"),
        "status": event.get("status"),
        "significance": _event_significance(event),
        "target": target if isinstance(target, str) and len(target) < 700 else None,
        "summary": summary,
        "event_hash": event.get("event_hash"),
    }


def _compact_handoff_for_pulse(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_id": row.get("handoff_id"),
        "source_session_id": row.get("source_session_id"),
        "actor": row.get("actor"),
        "ended_utc": row.get("ended_utc"),
        "completion_summary": row.get("completion_summary"),
        "mutation_count": row.get("mutation_count"),
        "verification_count": row.get("verification_count"),
        "failure_count": row.get("failure_count"),
        "partial_count": row.get("partial_count"),
        "related_projects": [
            {
                "project_id": item.get("project_id"),
                "name": item.get("name"),
                "path": item.get("path"),
            }
            for item in (row.get("related_projects") or [])[:8]
        ],
        "markdown_path": row.get("markdown_path"),
        "datenstand": row.get("datenstand"),
    }


def pulse(
    *,
    session_id: str,
    current_project: str | None = None,
    consume: bool = True,
    max_items: int = 12,
    include_current_session: bool = False,
    level: str = "whisper",
) -> dict[str, Any]:
    if not session_id:
        raise AtlasError("session_id ist für atlas.pulse erforderlich")
    if level not in {"whisper", "project", "stream", "full"}:
        raise AtlasError("level muss whisper, project, stream oder full sein")
    _ensure_layout()
    cursor_path = _cursor_path(session_id)
    cursor_context = _session_cursor_lock(session_id) if consume else contextlib.nullcontext()
    with cursor_context:
        cursor = _read_json(cursor_path, {}) or {}
        events, history_offset = _history_delta(int(cursor.get("history_offset") or 0))
        changes, change_offset = _jsonl_delta(CHANGE_LOG, int(cursor.get("change_offset") or 0))
        ideas, idea_offset = _jsonl_delta(IDEA_LOG, int(cursor.get("idea_offset") or 0))
        projects = _read_json(ATLAS_ROOT / "PROJEKTREGISTER.json", []) or []
        project_revisions_payload = _read_json(PROJECT_REVISION_PATH, {"projects": {}}) or {"projects": {}}
        project_revisions = project_revisions_payload.get("projects") or {}
        handoff_payload = _read_json(HANDOFF_REGISTER_PATH, {"handoffs": []}) or {"handoffs": []}
        handoffs = handoff_payload.get("handoffs") or []
        bridge_payload = _read_json(AI_BRIDGE_PATH, {"streams": {}}) or {"streams": {}}
        bridges = bridge_payload.get("streams") or {}
        conflicts = [
            row for row in _read_jsonl(CONFLICT_LOG)
            if row.get("status", "open") == "open"
        ]
        current_project_row = None
        if current_project:
            if str(current_project).startswith("/"):
                current_project_row = relational_project_match(projects, [str(current_project)])
            if current_project_row is None:
                needle = str(current_project).lower()
                current_project_row = next(
                    (
                        row for row in projects
                        if needle in str(row.get("name") or "").lower()
                        or needle in str(row.get("path") or "").lower()
                    ),
                    None,
                )
        current_project_id = str((current_project_row or {}).get("project_id") or "")
        current_project_path = str((current_project_row or {}).get("path") or current_project or "")
        foreign = [
            event
            for event in events
            if include_current_session or event.get("session_id") != session_id
        ]
        if level == "project" and current_project_id:
            foreign = [
                event
                for event in foreign
                if current_project_id in relational_event_project_ids(event, projects)
            ]
        changes = [row for row in changes if row.get("session_id") != session_id]
        if level == "project" and current_project_id:
            changes = [
                row
                for row in changes
                if row.get("project_id") == current_project_id
                or current_project_path in json.dumps(row, ensure_ascii=False)
                or row.get("kind") == "atlas_refresh"
            ]
        by_session: dict[str, dict[str, Any]] = {}
        for event in foreign:
            sid = str(event.get("session_id") or "unknown")
            row = by_session.setdefault(
                sid,
                {
                    "session_id": sid,
                    "actor": event.get("actor"),
                    "event_count": 0,
                    "classes": Counter(),
                    "first_utc": event.get("timestamp_utc"),
                    "last_utc": event.get("timestamp_utc"),
                    "important_events": [],
                    "related_project_ids": set(),
                },
            )
            row["event_count"] += 1
            significance = _event_significance(event)
            row["classes"][significance] += 1
            row["last_utc"] = event.get("timestamp_utc")
            row["related_project_ids"].update(relational_event_project_ids(event, projects))
            if significance not in {"read_or_orientation", "other"}:
                row["important_events"].append(_compact_event(event))
        effective_max = min(max(1, int(max_items)), 4 if level == "whisper" else 100)
        session_summaries = []
        for row in by_session.values():
            row = dict(row)
            row["classes"] = dict(row["classes"])
            row["related_project_ids"] = sorted(row["related_project_ids"])
            row["important_events"] = row["important_events"][-effective_max:]
            row["activity_class"] = (
                "failed_or_blocked"
                if row["classes"].get("failure_or_blocker")
                else "mutation_or_completion"
                if row["classes"].get("mutation")
                or row["classes"].get("meaningful_marker")
                or row["classes"].get("session_completed")
                else "orientation_only"
            )
            session_summaries.append(row)
        session_summaries.sort(key=lambda row: row.get("last_utc") or "", reverse=True)
        relevant_changes = changes[-effective_max:]
        foreign_ideas = [row for row in ideas if row.get("session_id") != session_id]
        if level == "project" and current_project_path:
            foreign_ideas = [
                row for row in foreign_ideas
                if current_project_path in json.dumps(row, ensure_ascii=False)
            ]
        known_handoff_ids = set(cursor.get("known_handoff_ids") or [])
        new_handoffs = [
            row
            for row in handoffs
            if row.get("handoff_id") not in known_handoff_ids
            and row.get("source_session_id") != session_id
        ]
        if level == "project" and current_project_id:
            new_handoffs = [
                row
                for row in new_handoffs
                if any(related.get("project_id") == current_project_id for related in row.get("related_projects") or [])
            ]
        seen_project_revisions = cursor.get("project_revisions_seen") or {}
        project_revision_deltas = []
        for project_id, state in project_revisions.items():
            if level == "project" and current_project_id and project_id != current_project_id:
                continue
            revision = int((state or {}).get("revision") or 0)
            previous = int(seen_project_revisions.get(project_id) or 0)
            if revision > previous:
                project = next((row for row in projects if row.get("project_id") == project_id), {})
                project_revision_deltas.append(
                    {
                        "project_id": project_id,
                        "name": project.get("name"),
                        "path": (state or {}).get("path") or project.get("path"),
                        "previous_revision": previous,
                        "revision": revision,
                        "last_event_id": (state or {}).get("last_event_id"),
                        "last_event_session_id": (state or {}).get("last_event_session_id"),
                    }
                )
        seen_conflicts = set(cursor.get("known_open_conflict_ids") or [])
        new_conflicts = [
            row for row in conflicts
            if row.get("conflict_id") and row.get("conflict_id") not in seen_conflicts
        ]
        seen_stream_revisions = cursor.get("ai_stream_revisions_seen") or {}
        stream_deltas = []
        if level in {"stream", "full"}:
            for stream_id, bridge in bridges.items():
                revision = int((bridge or {}).get("revision") or 0)
                previous = int(seen_stream_revisions.get(stream_id) or 0)
                if revision > previous:
                    stream_deltas.append(
                        {
                            "stream_id": stream_id,
                            "previous_revision": previous,
                            "revision": revision,
                            "related_projects": (bridge or {}).get("related_projects") or [],
                            "session_source_stats": (bridge or {}).get("session_source_stats") or {},
                        }
                    )
        status = _read_json(STATUS_PATH, {}) or {}
        changed = bool(
            session_summaries
            or relevant_changes
            or foreign_ideas
            or new_handoffs
            or project_revision_deltas
            or new_conflicts
            or stream_deltas
        )
        marker = (
            f"[ATLAS-PULS {level} r{status.get('revision', 0)} | "
            f"{len(session_summaries)} fremde Sitzungen | "
            f"{len(project_revision_deltas)} Projektdeltas | "
            f"{len(new_handoffs)} Übergaben | "
            f"{len(stream_deltas)} Stromdeltas | "
            f"{len(foreign_ideas)} Eingebungsspuren | "
            f"{len(new_conflicts)} neue Konflikte]"
        )
        result = {
            "ok": True,
            "changed": changed,
            "marker": marker,
            "level": level,
            "session_id": session_id,
            "current_project": current_project,
            "current_project_state": (
                {
                    "project_id": current_project_id,
                    "name": (current_project_row or {}).get("name"),
                    "path": current_project_path,
                    "revision": int((project_revisions.get(current_project_id) or {}).get("revision") or 0),
                }
                if current_project_id
                else None
            ),
            "atlas_revision": status.get("revision"),
            "foreign_sessions": session_summaries[:effective_max],
            "atlas_changes": relevant_changes,
            "project_revision_deltas": project_revision_deltas[:effective_max],
            "new_handoffs": [
                _compact_handoff_for_pulse(row)
                for row in new_handoffs[:effective_max]
            ],
            "ai_stream_deltas": stream_deltas[:effective_max],
            "foreign_idea_markers": foreign_ideas[-effective_max:],
            "new_conflicts": new_conflicts[:effective_max],
            "open_conflict_count": len(conflicts),
            "refresh_recommended": bool(status.get("dirty") or status.get("full_refresh_recommended")),
            "cursor_was_new": not bool(cursor),
            "lease": {
                "atlas_revision_seen_before": cursor.get("atlas_revision"),
                "project_revisions_seen_before": seen_project_revisions,
                "known_completed_sessions_before": cursor.get("known_completed_sessions") or [],
            },
        }
        if consume:
            _atomic_write_json(
                cursor_path,
                {
                    "schema_version": "2.0",
                    "session_id": session_id,
                    "updated_utc": _utcnow(),
                    "history_offset": history_offset,
                    "change_offset": change_offset,
                    "idea_offset": idea_offset,
                    "atlas_revision": status.get("revision"),
                    "current_project": current_project,
                    "current_project_id": current_project_id or None,
                    "project_revisions_seen": {
                        project_id: int((state or {}).get("revision") or 0)
                        for project_id, state in project_revisions.items()
                    },
                    "known_handoff_ids": [row.get("handoff_id") for row in handoffs if row.get("handoff_id")],
                    "known_completed_sessions": [row.get("source_session_id") for row in handoffs if row.get("source_session_id")],
                    "known_open_conflict_ids": [row.get("conflict_id") for row in conflicts if row.get("conflict_id")],
                    "ai_stream_revisions_seen": {
                        stream_id: int((bridge or {}).get("revision") or 0)
                        for stream_id, bridge in bridges.items()
                    },
                },
            )
        return result


def observe_tool_event(
    *,
    tool_name: str,
    session_id: str,
    event: dict[str, Any],
    result: Any,
    target: str | None,
    context_paths: Iterable[str] | None = None,
) -> dict[str, Any] | None:
    if tool_name.startswith("atlas."):
        return None
    mutating = tool_name.startswith(MUTATING_TOOL_PREFIXES)
    failed = event.get("status") in {"failed", "blocked"}
    if not mutating and not failed:
        return None
    _ensure_layout()
    with _atlas_lock():
        status = _read_json(STATUS_PATH, {}) or {}
        revision = int(status.get("revision") or 0) + 1
        status["revision"] = revision
        status["generated_utc"] = _utcnow()
        status["dirty"] = bool(mutating)
        status["full_refresh_recommended"] = bool(mutating)
        status["last_observed_event_id"] = event.get("event_id")
        status["last_observed_tool"] = tool_name
        _atomic_write_json(STATUS_PATH, status)
        project_observation = (
            observe_project_event(
                projects_path=ATLAS_ROOT / "PROJEKTREGISTER.json",
                revision_path=PROJECT_REVISION_PATH,
                event=event,
                tool_name=tool_name,
                target=target,
                context_paths=context_paths or [],
            )
            if mutating
            else None
        )
        record = {
            "schema_version": "1.0",
            "change_id": hashlib.sha256(
                f"{event.get('event_id')}|{tool_name}|{revision}".encode("utf-8")
            ).hexdigest()[:24],
            "timestamp_utc": event.get("timestamp_utc") or _utcnow(),
            "revision": revision,
            "kind": "tool_mutation" if mutating else "tool_failure",
            "summary": f"{tool_name}: {target or 'ohne Ziel'}",
            "session_id": session_id,
            "tool_name": tool_name,
            "target": target,
            "history_event_id": event.get("event_id"),
            "history_event_hash": event.get("event_hash"),
            "result_ok": result.get("ok") if isinstance(result, dict) else None,
            "project_id": (project_observation or {}).get("project_id"),
            "project_path": (project_observation or {}).get("project_path"),
            "project_revision": (project_observation or {}).get("project_revision"),
        }
        _append_jsonl(CHANGE_LOG, record)
        return record


def _tokenize(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\wäöüßÄÖÜ-]{3,}", value.lower(), flags=re.UNICODE)
        if token not in {"dass", "eine", "einer", "eines", "oder", "aber", "auch", "nicht", "noch", "wird", "sind", "sein", "haben", "hier", "dort"}
    }


def _idea_similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 0.0
    sequence = difflib.SequenceMatcher(None, left.lower(), right.lower()).ratio()
    return round((0.7 * jaccard) + (0.3 * sequence), 4)


def _recent_history_idea_candidates(limit: int = 500) -> list[dict[str, Any]]:
    rows = _read_jsonl(HISTORY_PATH, limit=limit)
    candidates = []
    for event in rows:
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        fragments = []
        for key in ("summary", "reason", "result", "task", "title"):
            value = details.get(key)
            if isinstance(value, str):
                fragments.append(value)
        action = str(event.get("action") or "")
        if any(token in action for token in ("marker", "completed", "architecture", "konzept", "idea", "atlas")):
            fragments.append(action)
        if not fragments:
            continue
        candidates.append(
            {
                "source_type": "history_event",
                "source_id": event.get("event_id"),
                "session_id": event.get("session_id"),
                "timestamp_utc": event.get("timestamp_utc"),
                "text": " | ".join(fragments)[:4000],
                "action": action,
            }
        )
    return candidates


def idea_probe(*, text: str, session_id: str | None = None, limit: int = 8) -> dict[str, Any]:
    if not text.strip():
        raise AtlasError("text darf nicht leer sein")
    candidates = []
    for row in _read_jsonl(IDEA_LOG, limit=1000):
        candidates.append(
            {
                "source_type": "idea_marker",
                "source_id": row.get("idea_id"),
                "session_id": row.get("session_id"),
                "timestamp_utc": row.get("timestamp_utc"),
                "text": str(row.get("text") or ""),
                "classification": row.get("classification"),
            }
        )
    candidates.extend(_recent_history_idea_candidates())
    matches = []
    for candidate in candidates:
        if session_id and candidate.get("session_id") == session_id:
            continue
        score = _idea_similarity(text, candidate.get("text") or "")
        if score < 0.18:
            continue
        row = dict(candidate)
        row["similarity"] = score
        row.pop("text", None)
        matches.append(row)
    matches.sort(key=lambda row: row["similarity"], reverse=True)
    return {
        "ok": True,
        "query_sha256": _sha256_bytes(text.encode("utf-8")),
        "matches": matches[:limit],
        "highest_similarity": matches[0]["similarity"] if matches else 0.0,
        "einschraenkung": "Ähnlichkeit beweist weder Übernahme noch Unabhängigkeit. Sie markiert nur eine auffindbare Vor- oder Parallelspur.",
    }


def record_idea(
    *,
    text: str,
    session_id: str,
    prior_awareness: str = "unknown",
    classification_override: str | None = None,
    trigger: str | None = None,
    related_paths: Iterable[str] | None = None,
    explicit_source_refs: Iterable[str] | None = None,
    supersedes_idea_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    if prior_awareness not in IDEA_AWARENESS:
        raise AtlasError(f"prior_awareness muss eines von {sorted(IDEA_AWARENESS)} sein")
    if classification_override and classification_override not in IDEA_PROVENANCE_CLASSES:
        raise AtlasError(
            f"classification_override muss eines von {sorted(IDEA_PROVENANCE_CLASSES)} sein"
        )
    probe = idea_probe(text=text, session_id=session_id)
    highest = float(probe["highest_similarity"])
    top = probe["matches"][0] if probe["matches"] else None
    if classification_override:
        classification = classification_override
    elif prior_awareness == "direct":
        classification = "UEBERNOMMEN_ODER_DIREKT_ANGESTOSSEN"
    elif prior_awareness == "partial":
        classification = "ANGESTOSSEN_ODER_TEILBEWUSST"
    elif prior_awareness == "none" and highest >= 0.42:
        classification = "KONVERGENT_MIT_AUFFINDBARER_VORSPUR"
    elif prior_awareness == "none":
        classification = "OHNE_GEFUNDENE_VORSPUR"
    else:
        classification = "HERKUNFT_UNKLAR_MIT_AEHNLICHKEIT" if top else "HERKUNFT_UNKLAR"
    source_refs = list(explicit_source_refs or [])
    now = _utcnow()
    idea_id = hashlib.sha256(f"{session_id}|{now}|{text}".encode("utf-8")).hexdigest()[:24]
    if source_refs:
        source_display = "ExpliziteQuelle=" + ",".join(str(ref) for ref in source_refs[:3])
    elif top:
        source_display = f"Aehnlichkeitsspur={top.get('session_id')}/{top.get('source_id')}"
    else:
        source_display = "Spur=keine gefunden"
    marker = (
        f"[EINGEBUNGSPROVENIENZ: {classification} | "
        f"Vorwissen={prior_awareness} | Ähnlichkeit={highest:.2f} | {source_display}]"
    )
    record = {
        "schema_version": "1.0",
        "idea_id": idea_id,
        "timestamp_utc": now,
        "session_id": session_id,
        "text": text,
        "text_sha256": _sha256_bytes(text.encode("utf-8")),
        "prior_awareness": prior_awareness,
        "classification_override": classification_override,
        "trigger": trigger,
        "classification": classification,
        "marker": marker,
        "highest_similarity": highest,
        "similar_traces": probe["matches"],
        "related_paths": list(related_paths or []),
        "explicit_source_refs": source_refs,
        "supersedes_idea_ids": list(supersedes_idea_ids or []),
        "einschraenkung": "Der Marker beschreibt den belegbaren Herkunftsstand, nicht ein unbeweisbares inneres Entstehungsereignis.",
    }
    _append_jsonl(IDEA_LOG, record)
    _append_jsonl(
        CHANGE_LOG,
        {
            "schema_version": "1.0",
            "change_id": idea_id,
            "timestamp_utc": now,
            "revision": (_read_json(STATUS_PATH, {}) or {}).get("revision", 0),
            "kind": "idea_provenance",
            "summary": marker,
            "session_id": session_id,
            "idea_id": idea_id,
        },
    )
    return {"ok": True, "record": record, "display_marker": marker}


def record_consensus(
    *,
    statement: str,
    consensus_class: str,
    session_id: str,
    scope: str = "global",
    source_refs: Iterable[str] | None = None,
    supersedes: Iterable[str] | None = None,
) -> dict[str, Any]:
    if consensus_class not in CONSENSUS_CLASSES:
        raise AtlasError(f"Unbekannte Konsensklasse: {consensus_class}")
    now = _utcnow()
    consensus_id = hashlib.sha256(
        f"{statement}|{consensus_class}|{scope}|{now}".encode("utf-8")
    ).hexdigest()[:24]
    record = {
        "schema_version": "1.0",
        "consensus_id": consensus_id,
        "timestamp_utc": now,
        "session_id": session_id,
        "scope": scope,
        "class": consensus_class,
        "statement": statement,
        "statement_sha256": _sha256_bytes(statement.encode("utf-8")),
        "source_refs": list(source_refs or []),
        "supersedes": list(supersedes or []),
        "status": "active" if consensus_class != "VERALTET" else "obsolete",
    }
    _append_jsonl(CONSENSUS_LOG, record)
    return {"ok": True, "record": record}


def record_conflict(
    *,
    statement_a: str,
    statement_b: str,
    session_id: str,
    scope: str = "global",
    source_refs_a: Iterable[str] | None = None,
    source_refs_b: Iterable[str] | None = None,
) -> dict[str, Any]:
    now = _utcnow()
    conflict_id = hashlib.sha256(
        f"{statement_a}|{statement_b}|{scope}|{now}".encode("utf-8")
    ).hexdigest()[:24]
    record = {
        "schema_version": "1.0",
        "conflict_id": conflict_id,
        "timestamp_utc": now,
        "session_id": session_id,
        "scope": scope,
        "statement_a": statement_a,
        "statement_b": statement_b,
        "source_refs_a": list(source_refs_a or []),
        "source_refs_b": list(source_refs_b or []),
        "status": "open",
    }
    _append_jsonl(CONFLICT_LOG, record)
    return {"ok": True, "record": record}


def list_consensus(*, query: str | None = None, limit: int = 100) -> dict[str, Any]:
    rows = _read_jsonl(CONSENSUS_LOG)
    if query:
        needle = query.lower()
        rows = [row for row in rows if needle in json.dumps(row, ensure_ascii=False).lower()]
    return {"ok": True, "count": len(rows), "rows": rows[-limit:]}


def list_conflicts(*, query: str | None = None, status: str = "open", limit: int = 100) -> dict[str, Any]:
    rows = _read_jsonl(CONFLICT_LOG)
    if status != "all":
        rows = [row for row in rows if row.get("status", "open") == status]
    if query:
        needle = query.lower()
        rows = [row for row in rows if needle in json.dumps(row, ensure_ascii=False).lower()]
    return {"ok": True, "count": len(rows), "rows": rows[-limit:]}


def find(
    *,
    query: str,
    limit: int = 40,
    root_name: str | None = None,
    kind: str | None = None,
    include_content: bool = True,
) -> dict[str, Any]:
    if not PATH_DB.exists():
        raise AtlasError("Pfadindex fehlt; atlas.refresh full ausführen")
    limit = max(1, min(int(limit), 200))
    path_rows: list[dict[str, Any]] = []
    connection = sqlite3.connect(PATH_DB)
    connection.row_factory = sqlite3.Row
    try:
        clauses = ["(path LIKE ? OR basename LIKE ?)"]
        params: list[Any] = [f"%{query}%", f"%{query}%"]
        if root_name:
            clauses.append("root_name=?")
            params.append(root_name)
        if kind:
            clauses.append("kind=?")
            params.append(kind)
        params.append(limit)
        sql = "SELECT * FROM paths WHERE " + " AND ".join(clauses) + " ORDER BY CASE WHEN basename=? THEN 0 ELSE 1 END, length(path), mtime_ns DESC LIMIT ?"
        exact_params = params[:-1] + [query, params[-1]]
        for row in connection.execute(sql, exact_params):
            value = dict(row)
            value["markers"] = json.loads(value.pop("markers_json") or "[]")
            path_rows.append(value)
    finally:
        connection.close()
    content_rows: list[dict[str, Any]] = []
    if include_content and CONCEPT_DB.exists():
        concept = sqlite3.connect(CONCEPT_DB)
        concept.row_factory = sqlite3.Row
        try:
            table_sql = concept.execute(
                "SELECT sql FROM sqlite_master WHERE name='documents'"
            ).fetchone()
            is_fts = bool(table_sql and "VIRTUAL TABLE" in str(table_sql[0]).upper())
            if is_fts:
                terms = [term for term in re.findall(r"[\wäöüßÄÖÜ-]+", query) if len(term) >= 2]
                match = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms[:12])
                if match:
                    for row in concept.execute(
                        "SELECT path,title,headings,snippet(documents,3,'[',']',' … ',24) AS snippet,bm25(documents) AS rank FROM documents WHERE documents MATCH ? ORDER BY rank LIMIT ?",
                        (match, limit),
                    ):
                        content_rows.append(dict(row))
            else:
                for row in concept.execute(
                    "SELECT path,title,headings,substr(body,1,500) AS snippet FROM documents WHERE title LIKE ? OR headings LIKE ? OR body LIKE ? LIMIT ?",
                    (f"%{query}%", f"%{query}%", f"%{query}%", limit),
                ):
                    content_rows.append(dict(row))
        except sqlite3.OperationalError:
            content_rows = []
        finally:
            concept.close()
    return {
        "ok": True,
        "query": query,
        "path_match_count": len(path_rows),
        "content_match_count": len(content_rows),
        "path_matches": path_rows,
        "content_matches": content_rows,
        "einschraenkung": "Volltext- und Pfadtreffer sind Fundstellen. Gültigkeit und Konsens müssen separat geprüft werden.",
    }


def where_is(*, name_or_path: str, limit: int = 80) -> dict[str, Any]:
    result = find(query=name_or_path, limit=limit, include_content=False)
    exact = [
        row
        for row in result["path_matches"]
        if row["path"] == name_or_path or row["basename"].lower() == name_or_path.lower()
    ]
    result["exact_matches"] = exact
    return result


def map_view(*, section: str = "summary", limit: int = 150) -> dict[str, Any]:
    allowed = {
        "summary": STATUS_PATH,
        "roots": ATLAS_ROOT / "WURZELREGISTER.json",
        "root_letters": ATLAS_ROOT / "WURZELBRIEFE.json",
        "projects": ATLAS_ROOT / "PROJEKTREGISTER.json",
        "vaults": ATLAS_ROOT / "VAULTREGISTER.json",
        "systems": ATLAS_ROOT / "SYSTEMREGISTER.json",
        "ai_streams": ATLAS_ROOT / "AI_STROEME.json",
        "sessions": ATLAS_ROOT / "SESSIONREGISTER.json",
        "consensus": CONSENSUS_LOG,
        "conflicts": CONFLICT_LOG,
        "ideas": IDEA_LOG,
        "project_revisions": PROJECT_REVISION_PATH,
        "claims": CLAIM_REGISTER_PATH,
        "validations": VALIDATION_REGISTER_PATH,
        "handoffs": HANDOFF_REGISTER_PATH,
        "relationships": RELATION_JSON,
        "ai_bridges": AI_BRIDGE_PATH,
    }
    if section == "all":
        return {
            "ok": True,
            "summary": atlas_snapshot(),
            "roots": _read_json(allowed["roots"], []),
            "root_letters": _read_json(allowed["root_letters"], []),
            "projects": _read_json(allowed["projects"], [])[:limit],
            "vaults": _read_json(allowed["vaults"], [])[:limit],
            "systems": _read_json(allowed["systems"], [])[:limit],
            "ai_streams": _read_json(allowed["ai_streams"], []),
            "sessions": (_read_json(allowed["sessions"], {}) or {}).get("sessions", [])[:limit],
            "consensus": _read_jsonl(CONSENSUS_LOG, limit=limit),
            "conflicts": _read_jsonl(CONFLICT_LOG, limit=limit),
            "ideas": _read_jsonl(IDEA_LOG, limit=limit),
            "project_revisions": _read_json(PROJECT_REVISION_PATH, {}),
            "claims": _read_json(CLAIM_REGISTER_PATH, {}),
            "validations": _read_json(VALIDATION_REGISTER_PATH, {}),
            "handoffs": _read_json(HANDOFF_REGISTER_PATH, {}),
            "relationships": _read_json(RELATION_JSON, {}),
            "ai_bridges": _read_json(AI_BRIDGE_PATH, {}),
        }
    if section not in allowed:
        raise AtlasError(f"Unbekannte Kartensektion: {section}")
    if section == "summary":
        return atlas_snapshot()
    path = allowed[section]
    if path.suffix == ".jsonl":
        data: Any = _read_jsonl(path, limit=limit)
    else:
        data = _read_json(path, [] if section != "sessions" else {})
        if isinstance(data, list):
            data = data[:limit]
    return {"ok": True, "section": section, "path": str(path), "data": data}


def changed_since(*, revision: int = 0, limit: int = 200) -> dict[str, Any]:
    rows = [row for row in _read_jsonl(CHANGE_LOG) if int(row.get("revision") or 0) > int(revision)]
    return {"ok": True, "since_revision": revision, "count": len(rows), "rows": rows[-limit:]}


def relationships(
    *,
    query: str | None = None,
    node_type: str | None = None,
    relation: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    return relational_query_relationships(
        relation_db=RELATION_DB,
        query=query,
        node_type=node_type,
        relation=relation,
        limit=limit,
    )


def handoffs(*, session_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    return relational_handoff_state(HANDOFF_REGISTER_PATH, session_id=session_id, limit=limit)


def project_state(*, query: str) -> dict[str, Any]:
    projects = _read_json(ATLAS_ROOT / "PROJEKTREGISTER.json", []) or []
    needle = query.lower()
    matches = [
        dict(row)
        for row in projects
        if needle in row.get("name", "").lower() or needle in row.get("path", "").lower()
    ]
    for row in matches:
        path = row.get("path")
        row["consensus"] = [
            item
            for item in _read_jsonl(CONSENSUS_LOG)
            if path and path in json.dumps(item, ensure_ascii=False)
        ][-30:]
        row["conflicts"] = [
            item
            for item in _read_jsonl(CONFLICT_LOG)
            if path and path in json.dumps(item, ensure_ascii=False)
        ][-30:]
        relation_result = relationships(query=str(row.get("project_id") or path), node_type="project", limit=20)
        row["relationship_query"] = relation_result
    return {"ok": True, "query": query, "count": len(matches), "projects": matches}


def session_state(*, session_id: str) -> dict[str, Any]:
    sessions = (_read_json(ATLAS_ROOT / "SESSIONREGISTER.json", {}) or {}).get("sessions", [])
    matches = [row for row in sessions if row.get("session_id") == session_id]
    cursor = _read_json(_cursor_path(session_id), {}) or {}
    handoff = handoffs(session_id=session_id, limit=10)
    relation_result = relationships(query=session_id, node_type="session", limit=20)
    return {
        "ok": True,
        "session_id": session_id,
        "matches": matches,
        "atlas_cursor": cursor,
        "handoff": handoff,
        "relationships": relation_result,
    }


def ai_stream_state(*, stream_id: str) -> dict[str, Any]:
    streams = _read_json(ATLAS_ROOT / "AI_STROEME.json", []) or []
    matches = [row for row in streams if row.get("id", "").lower() == stream_id.lower()]
    bridge = (_read_json(AI_BRIDGE_PATH, {"streams": {}}) or {}).get("streams", {}).get(stream_id)
    relation_result = relationships(query=stream_id, node_type="ai_stream", limit=30)
    return {
        "ok": True,
        "stream_id": stream_id,
        "matches": matches,
        "bridge": bridge,
        "relationships": relation_result,
    }


def provenance(*, path_or_query: str, limit: int = 60) -> dict[str, Any]:
    found = where_is(name_or_path=path_or_query, limit=limit)
    history_mentions = []
    needle = path_or_query.lower()
    for event in _read_jsonl(HISTORY_PATH, limit=2000):
        target = str(event.get("target") or "")
        details = json.dumps(event.get("details") or {}, ensure_ascii=False)
        if needle in target.lower() or needle in details.lower():
            history_mentions.append(_compact_event(event))
    linked_consensus = [
        row for row in _read_jsonl(CONSENSUS_LOG) if needle in json.dumps(row, ensure_ascii=False).lower()
    ]
    linked_conflicts = [
        row for row in _read_jsonl(CONFLICT_LOG) if needle in json.dumps(row, ensure_ascii=False).lower()
    ]
    linked_ideas = [
        row for row in _read_jsonl(IDEA_LOG) if needle in json.dumps(row, ensure_ascii=False).lower()
    ]
    return {
        "ok": True,
        "query": path_or_query,
        "index": found,
        "history_mentions": history_mentions[-limit:],
        "consensus": linked_consensus[-limit:],
        "conflicts": linked_conflicts[-limit:],
        "idea_provenance": linked_ideas[-limit:],
        "relationships": relationships(query=path_or_query, limit=limit),
        "handoffs": [
            row
            for row in ((_read_json(HANDOFF_REGISTER_PATH, {"handoffs": []}) or {}).get("handoffs") or [])
            if needle in json.dumps(row, ensure_ascii=False).lower()
        ][-limit:],
    }


def health() -> dict[str, Any]:
    status = _read_json(STATUS_PATH, {}) or {}
    checks: dict[str, Any] = {
        "status_exists": STATUS_PATH.exists(),
        "map_exists": (ATLAS_ROOT / "GESAMTKARTE.md").exists(),
        "path_index_exists": PATH_DB.exists(),
        "concept_index_exists": CONCEPT_DB.exists(),
        "relationship_index_exists": RELATION_DB.exists(),
        "project_revisions_exist": PROJECT_REVISION_PATH.exists(),
        "validation_register_exists": VALIDATION_REGISTER_PATH.exists(),
        "handoff_register_exists": HANDOFF_REGISTER_PATH.exists(),
        "ai_bridge_register_exists": AI_BRIDGE_PATH.exists(),
    }
    for key, path in (
        ("path_index_integrity", PATH_DB),
        ("concept_index_integrity", CONCEPT_DB),
        ("relationship_index_integrity", RELATION_DB),
    ):
        if not path.exists():
            checks[key] = None
            continue
        connection = sqlite3.connect(path)
        try:
            checks[key] = connection.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            connection.close()
    history_size = HISTORY_PATH.stat().st_size if HISTORY_PATH.exists() else 0
    cursor_files = len(list(CURSOR_ROOT.glob("*.json"))) if CURSOR_ROOT.exists() else 0
    ok = all(
        checks.get(key) in {True, "ok"}
        for key in (
            "status_exists",
            "map_exists",
            "path_index_exists",
            "concept_index_exists",
            "protocol_exists",
            "relationship_index_exists",
            "project_revisions_exist",
            "validation_register_exists",
            "handoff_register_exists",
            "ai_bridge_register_exists",
            "path_index_integrity",
            "concept_index_integrity",
            "relationship_index_integrity",
        )
    )
    return {
        "ok": ok,
        "checks": checks,
        "status": status,
        "history_bytes": history_size,
        "session_cursor_count": cursor_files,
        "open_conflict_count": len(
            [row for row in _read_jsonl(CONFLICT_LOG) if row.get("status", "open") == "open"]
        ),
        "handoff_count": len(((_read_json(HANDOFF_REGISTER_PATH, {"handoffs": []}) or {}).get("handoffs") or [])),
        "relationship_summary": _read_json(RELATION_JSON, {}),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="MCP-Gesamtatlas")
    sub = parser.add_subparsers(dest="command", required=True)
    refresh_parser = sub.add_parser("refresh")
    refresh_parser.add_argument("--mode", choices=("full", "light"), default="light")
    refresh_parser.add_argument("--reason", default="cli")
    refresh_parser.add_argument("--session-id")
    sub.add_parser("health")
    args = parser.parse_args()
    if args.command == "refresh":
        result = refresh_atlas(mode=args.mode, reason=args.reason, session_id=args.session_id)
    else:
        result = health()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
