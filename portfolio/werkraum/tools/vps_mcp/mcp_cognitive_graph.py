from __future__ import annotations

from pathlib import Path
import json
import os
import selectors
import shlex
import subprocess
import threading
import time
import uuid
from typing import Any, Callable, TypedDict

import psycopg2
from psycopg2.extras import execute_values
from langgraph.graph import END, START, StateGraph
from mcp_atlas_hybrid_search import hybrid_suche, manual_read_index_aktualisieren

from mcp_workflow_graph import (
    MODE_CONTROL_PLANE,
    MODE_DISCOVER,
    MODE_SURGICAL,
    STATE_CHANGE_READY,
    STATE_VERIFY,
    graph_snapshot as workflow_snapshot,
)

_RUNTIME_PATH = Path("/run/flextrawurst-vps-mcp-cognitive-graph.json")
_SCHEMA = 1
_LOCK = threading.RLock()
_MAX_NODES = 220
_MAX_EDGES = 500
_MEMORY_ENV_PATH = Path("/root/werkraum/.agent/flextrawurst-db.env")
_MEMORY_SCHEMA = "portfolio_memory"


def _memory_db_uri() -> str | None:
    if _MEMORY_ENV_PATH.is_file():
        for raw in _MEMORY_ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("FLEXTRAWURST_DB_URI="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _memory_connection():
    uri = _memory_db_uri()
    if not uri:
        return None
    conn = psycopg2.connect(uri, connect_timeout=5)
    conn.autocommit = True
    return conn


def _memory_record_event(event: str, target_key: str | None = None, payload: dict[str, Any] | None = None) -> None:
    """Best-effort Langzeitspur. Sie darf niemals den eigentlichen Lese-/Toollauf blockieren."""
    conn = None
    try:
        conn = _memory_connection()
        if conn is None:
            return
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {_MEMORY_SCHEMA}.events(event,target_key,payload) VALUES (%s,%s,%s::jsonb)",
                (str(event), target_key, json.dumps(payload or {}, ensure_ascii=False)),
            )
    except Exception:
        pass
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _memory_mark_source(path: str, *, state: str, note: str = "", data: dict[str, Any] | None = None) -> None:
    """Merkt einen Fundort, ohne suggested und read miteinander zu verwechseln."""
    conn = None
    try:
        conn = _memory_connection()
        if conn is None:
            return
        payload = json.dumps(data or {}, ensure_ascii=False)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.nodes AS n(key,kind,label,state,note,data)
                VALUES (%s,'source',%s,%s,%s,%s::jsonb)
                ON CONFLICT (key) DO UPDATE SET
                    label=COALESCE(EXCLUDED.label,n.label),
                    state=CASE
                        WHEN n.state='read' THEN 'read'
                        WHEN n.state='read_partial' AND EXCLUDED.state='suggested' THEN 'read_partial'
                        ELSE EXCLUDED.state
                    END,
                    note=CASE WHEN EXCLUDED.note<>'' THEN EXCLUDED.note ELSE n.note END,
                    data=n.data || EXCLUDED.data,
                    updated_at=now()
                """,
                (path, Path(path).name, state, note, payload),
            )
    except Exception:
        pass
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _memory_source_states(paths: list[str]) -> dict[str, str]:
    unique = [path for path in dict.fromkeys(str(p) for p in paths if str(p).strip())]
    if not unique:
        return {}
    conn = None
    try:
        conn = _memory_connection()
        if conn is None:
            return {}
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT key,state FROM {_MEMORY_SCHEMA}.nodes WHERE kind='source' AND key = ANY(%s)",
                (unique,),
            )
            return {str(key): str(state) for key, state in cur.fetchall()}
    except Exception:
        return {}
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass



_PATH_SCAN_VIRTUAL_ROOTS = frozenset({"/proc", "/sys", "/dev", "/run"})


def _ensure_path_scan_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_scans (
                scan_id text PRIMARY KEY,
                status text NOT NULL DEFAULT 'running',
                roots jsonb NOT NULL DEFAULT '[]'::jsonb,
                started_at timestamptz NOT NULL DEFAULT now(),
                updated_at timestamptz NOT NULL DEFAULT now(),
                completed_at timestamptz,
                directories_scanned bigint NOT NULL DEFAULT 0,
                directories_seen bigint NOT NULL DEFAULT 0,
                files_seen bigint NOT NULL DEFAULT 0,
                symlinks_seen bigint NOT NULL DEFAULT 0,
                other_seen bigint NOT NULL DEFAULT 0,
                errors bigint NOT NULL DEFAULT 0,
                secret_paths_omitted bigint NOT NULL DEFAULT 0,
                virtual_roots_skipped bigint NOT NULL DEFAULT 0
            )
            """
        )
        cur.execute(
            f"ALTER TABLE {_MEMORY_SCHEMA}.path_scans ADD COLUMN IF NOT EXISTS secret_paths_omitted bigint NOT NULL DEFAULT 0"
        )
        cur.execute(
            f"ALTER TABLE {_MEMORY_SCHEMA}.path_scans ADD COLUMN IF NOT EXISTS virtual_roots_skipped bigint NOT NULL DEFAULT 0"
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_inventory (
                scan_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.path_scans(scan_id) ON DELETE CASCADE,
                path text NOT NULL,
                parent_path text,
                entry_type text NOT NULL,
                state text NOT NULL DEFAULT 'seen',
                first_seen_at timestamptz NOT NULL DEFAULT now(),
                checked_at timestamptz,
                check_session text,
                data jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                PRIMARY KEY (scan_id, path)
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_scan_queue (
                scan_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.path_scans(scan_id) ON DELETE CASCADE,
                path text NOT NULL,
                depth integer NOT NULL DEFAULT 0,
                status text NOT NULL DEFAULT 'pending',
                error text,
                claimed_at timestamptz,
                PRIMARY KEY (scan_id, path)
            )
            """
        )
        cur.execute(
            f"ALTER TABLE {_MEMORY_SCHEMA}.path_scan_queue ADD COLUMN IF NOT EXISTS claimed_at timestamptz"
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_funds (
                scan_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.path_scans(scan_id) ON DELETE CASCADE,
                path text NOT NULL,
                what_is text NOT NULL,
                origin text NOT NULL,
                why_include text NOT NULL,
                recorded_at timestamptz NOT NULL DEFAULT now(),
                recorded_session text,
                PRIMARY KEY (scan_id, path)
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_directory_visits (
                scan_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.path_scans(scan_id) ON DELETE CASCADE,
                path text NOT NULL,
                session_id text NOT NULL,
                visited_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (scan_id, path, session_id)
            )
            """
        )
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_MEMORY_SCHEMA}.path_item_evidence (
                scan_id text NOT NULL REFERENCES {_MEMORY_SCHEMA}.path_scans(scan_id) ON DELETE CASCADE,
                path text NOT NULL,
                session_id text NOT NULL,
                evidence_type text NOT NULL,
                observed_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (scan_id, path, session_id, evidence_type)
            )
            """
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS path_inventory_parent_idx ON {_MEMORY_SCHEMA}.path_inventory(scan_id,parent_path)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS path_inventory_state_idx ON {_MEMORY_SCHEMA}.path_inventory(scan_id,state,entry_type)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS path_scan_queue_status_idx ON {_MEMORY_SCHEMA}.path_scan_queue(scan_id,status,depth)"
        )


def _normalize_scan_roots(roots: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in roots:
        try:
            path = str(Path(raw).resolve(strict=False))
        except Exception:
            continue
        if not Path(path).is_dir():
            continue
        if path not in normalized:
            normalized.append(path)
    if "/" in normalized:
        return ["/"]
    compact: list[str] = []
    for path in sorted(normalized, key=len):
        p = Path(path)
        if any(p == Path(parent) or Path(parent) in p.parents for parent in compact):
            continue
        compact.append(path)
    return compact


def _flush_path_scan_rows(conn, inventory_rows: list[tuple[Any, ...]], queue_rows: list[tuple[Any, ...]]) -> None:
    """Schreibt Scanpfade in begrenzten Bloecken nach Postgres und leert die RAM-Listen."""
    if not inventory_rows and not queue_rows:
        return
    with conn.cursor() as cur:
        if inventory_rows:
            execute_values(
                cur,
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.path_inventory(scan_id,path,parent_path,entry_type,state,data)
                VALUES %s
                ON CONFLICT (scan_id,path) DO UPDATE SET
                    parent_path=EXCLUDED.parent_path,
                    entry_type=EXCLUDED.entry_type
                """,
                inventory_rows,
                template="(%s,%s,%s,%s,%s,%s::jsonb)",
                page_size=5000,
            )
        if queue_rows:
            execute_values(
                cur,
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.path_scan_queue(scan_id,path,depth,status)
                VALUES %s
                ON CONFLICT (scan_id,path) DO NOTHING
                """,
                queue_rows,
                page_size=5000,
            )
    inventory_rows.clear()
    queue_rows.clear()


class _DirectoryScanTimeout(RuntimeError):
    pass


def _iter_directory_entries(directory: str, timeout_seconds: float = 30.0):
    """Listet genau eine Verzeichnisebene in einem killbaren Kindprozess, ohne Dateiinhalte."""
    proc = subprocess.Popen(
        [
            "find",
            directory,
            "-mindepth",
            "1",
            "-maxdepth",
            "1",
            "-printf",
            "%y\\0%p\\0%T@\\0%s\\0%i\\0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,
    )
    if proc.stdout is None:
        proc.kill()
        raise OSError("find-stdout konnte nicht geoeffnet werden")

    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + max(1.0, float(timeout_seconds))
    buffer = b""
    fields: list[bytes] = []
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise _DirectoryScanTimeout(f"Verzeichnis-Scan nach {timeout_seconds:.0f}s abgebrochen: {directory}")

            events = selector.select(timeout=min(0.5, remaining))
            for key, _mask in events:
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    try:
                        selector.unregister(key.fileobj)
                    except Exception:
                        pass
                    continue
                buffer += chunk
                while b"\0" in buffer:
                    field, buffer = buffer.split(b"\0", 1)
                    fields.append(field)
                    if len(fields) == 5:
                        entry_type_code = fields[0].decode("ascii", errors="replace")[:1]
                        child = os.fsdecode(fields[1])
                        fingerprint = {
                            "mtime": fields[2].decode("ascii", errors="replace"),
                            "size": fields[3].decode("ascii", errors="replace"),
                            "inode": fields[4].decode("ascii", errors="replace"),
                        }
                        fields.clear()
                        yield child, entry_type_code, fingerprint

            if proc.poll() is not None and not selector.get_map():
                break

        returncode = proc.wait(timeout=1)
        if returncode != 0:
            raise OSError(f"Verzeichnis-Scan endete mit Rueckgabecode {returncode}: {directory}")
        if fields or buffer:
            raise OSError(f"Unvollstaendige Pfadausgabe beim Verzeichnis-Scan: {directory}")
    finally:
        selector.close()
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=2)
            except Exception:
                pass


def _path_fingerprint_now(path: str, timeout_seconds: float = 5.0) -> dict[str, str]:
    """Liest nur Typ/mtime/Groesse/Inode eines Pfads; keine Dateiinhalte."""
    proc = subprocess.run(
        ["find", path, "-maxdepth", "0", "-printf", "%y\\0%T@\\0%s\\0%i\\0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=max(1.0, float(timeout_seconds)),
        check=False,
    )
    if proc.returncode != 0:
        raise CognitiveGraphError(f"Pfad ist seit dem Scan nicht mehr stabil erreichbar: {path}")
    fields = proc.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) != 4:
        raise CognitiveGraphError(f"Metadaten-Fingerabdruck unvollstaendig: {path}")
    return {
        "type": fields[0].decode("ascii", errors="replace")[:1],
        "mtime": fields[1].decode("ascii", errors="replace"),
        "size": fields[2].decode("ascii", errors="replace"),
        "inode": fields[3].decode("ascii", errors="replace"),
    }


def _require_no_path_drift(cur, scan_id: str, path: str) -> None:
    cur.execute(
        f"SELECT data FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND path=%s",
        (scan_id, path),
    )
    row = cur.fetchone()
    scanned = (row[0] if row and isinstance(row[0], dict) else {}).get("scan_fingerprint")
    if not isinstance(scanned, dict):
        raise CognitiveGraphError("Pfad hat keinen Scan-Fingerabdruck; ein neuer Pfadscan ist noetig.")
    current = _path_fingerprint_now(path)
    keys = ("mtime", "size", "inode")
    if tuple(str(scanned.get(k, "")) for k in keys) != tuple(str(current.get(k, "")) for k in keys):
        raise CognitiveGraphError("Pfad hat sich seit der Pfadinventur veraendert; Haken/Fund bleibt bis zum erneuerten Inventurstand blockiert.")


def path_scan_step(
    *,
    roots: list[str],
    secret_predicate: Callable[[Path], bool] | None = None,
    max_directories: int = 1000,
    reset: bool = False,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Pfad-only BFS ueber den VPS. Liest niemals Dateiinhalte."""
    max_directories = max(1, min(int(max_directories), 20000))
    normalized_roots = _normalize_scan_roots(roots)
    if not normalized_roots:
        raise CognitiveGraphError("Keine scanbaren Wurzeln vorhanden.")

    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar; Pfadinventur wird nicht fluechtig weitergefuehrt.")

    scan_id = f"vps-paths::{_session_key(session_id)}"
    processed = 0
    new_dirs_seen = 0
    new_files_seen = 0
    new_symlinks_seen = 0
    new_other_seen = 0
    errors = 0
    secret_skips = 0
    virtual_skips = 0

    try:
        _ensure_path_scan_tables(conn)
        with conn.cursor() as cur:
            if reset:
                cur.execute(
                    f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND state='checked'",
                    (scan_id,),
                )
                checked_count = int(cur.fetchone()[0])
                cur.execute(
                    f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_funds WHERE scan_id=%s",
                    (scan_id,),
                )
                fund_count = int(cur.fetchone()[0])
                if checked_count or fund_count:
                    raise CognitiveGraphError(
                        "Reset abgelehnt: Dieser Scan enthaelt bereits gepruefte Ordner oder Funde und darf nicht kaskadierend geloescht werden."
                    )
                cur.execute(f"DELETE FROM {_MEMORY_SCHEMA}.path_scans WHERE scan_id=%s", (scan_id,))

            cur.execute(
                f"SELECT status,roots FROM {_MEMORY_SCHEMA}.path_scans WHERE scan_id=%s",
                (scan_id,),
            )
            existing = cur.fetchone()
            if existing is None:
                cur.execute(
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.path_scans(scan_id,status,roots)
                    VALUES (%s,'running',%s::jsonb)
                    """,
                    (scan_id, json.dumps(normalized_roots, ensure_ascii=False)),
                )
                root_rows = [
                    (
                        scan_id,
                        root,
                        str(Path(root).parent) if root != "/" else None,
                        "dir",
                        "seen",
                        json.dumps({"root": True, "scan_fingerprint": _path_fingerprint_now(root)}),
                    )
                    for root in normalized_roots
                ]
                execute_values(
                    cur,
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.path_inventory(scan_id,path,parent_path,entry_type,state,data)
                    VALUES %s
                    ON CONFLICT (scan_id,path) DO NOTHING
                    """,
                    root_rows,
                    template="(%s,%s,%s,%s,%s,%s::jsonb)",
                )
                queue_rows = [(scan_id, root, 0, "pending") for root in normalized_roots]
                execute_values(
                    cur,
                    f"""
                    INSERT INTO {_MEMORY_SCHEMA}.path_scan_queue(scan_id,path,depth,status)
                    VALUES %s
                    ON CONFLICT (scan_id,path) DO NOTHING
                    """,
                    queue_rows,
                )
            else:
                stored_roots = existing[1] if isinstance(existing[1], list) else normalized_roots
                if list(stored_roots) != normalized_roots and not reset:
                    raise CognitiveGraphError("Laufende Pfadinventur hat andere Wurzeln; reset=true ist fuer einen neuen Scan erforderlich.")

            cur.execute(
                f"""
                UPDATE {_MEMORY_SCHEMA}.path_scan_queue
                SET status='error',
                    error=COALESCE(error,'stale in_progress claim reclaimed'),
                    claimed_at=NULL
                WHERE scan_id=%s
                  AND status='in_progress'
                  AND claimed_at < now() - interval '15 minutes'
                """,
                (scan_id,),
            )
            cur.execute(
                f"""
                WITH picked AS (
                    SELECT path
                    FROM {_MEMORY_SCHEMA}.path_scan_queue
                    WHERE scan_id=%s AND status IN ('pending','error')
                    ORDER BY CASE WHEN status='pending' THEN 0 ELSE 1 END,depth,path
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE {_MEMORY_SCHEMA}.path_scan_queue AS q
                SET status='in_progress',claimed_at=now(),error=NULL
                FROM picked
                WHERE q.scan_id=%s AND q.path=picked.path
                RETURNING q.path,q.depth
                """,
                (scan_id, max_directories, scan_id),
            )
            pending = [(str(path), int(depth)) for path, depth in cur.fetchall()]

        inventory_rows: list[tuple[Any, ...]] = []
        queue_rows: list[tuple[Any, ...]] = []
        done_paths: list[str] = []
        error_rows: list[tuple[str, str]] = []
        secret_omissions_by_parent: dict[str, int] = {}

        for directory, depth in pending:
            processed += 1
            if directory in _PATH_SCAN_VIRTUAL_ROOTS:
                done_paths.append(directory)
                virtual_skips += 1
                continue

            local_secret_skips = 0
            try:
                for child, entry_type_code, fingerprint in _iter_directory_entries(directory):
                    child_path = Path(child)
                    if secret_predicate is not None:
                        try:
                            if secret_predicate(child_path):
                                secret_skips += 1
                                local_secret_skips += 1
                                continue
                        except Exception:
                            secret_skips += 1
                            local_secret_skips += 1
                            continue

                    is_symlink = entry_type_code == "l"
                    is_dir = entry_type_code == "d"
                    is_file = entry_type_code == "f"

                    if is_symlink:
                        entry_type = "symlink"
                        new_symlinks_seen += 1
                    elif is_dir:
                        entry_type = "dir"
                        new_dirs_seen += 1
                    elif is_file:
                        entry_type = "file"
                        new_files_seen += 1
                    else:
                        entry_type = "other"
                        new_other_seen += 1

                    inventory_rows.append(
                        (scan_id, child, directory, entry_type, "seen", json.dumps(dict(scan_fingerprint=fingerprint)))
                    )
                    if is_dir and not is_symlink and child not in _PATH_SCAN_VIRTUAL_ROOTS:
                        queue_rows.append((scan_id, child, depth + 1, "pending"))
                    if len(inventory_rows) >= 5000 or len(queue_rows) >= 5000:
                        _flush_path_scan_rows(conn, inventory_rows, queue_rows)
                done_paths.append(directory)
                secret_omissions_by_parent[directory] = local_secret_skips
            except Exception as exc:
                errors += 1
                error_rows.append((directory, f"{type(exc).__name__}: {exc}"[:1000]))

        _flush_path_scan_rows(conn, inventory_rows, queue_rows)

        with conn.cursor() as cur:
            if done_paths:
                cur.execute(
                    f"""
                    UPDATE {_MEMORY_SCHEMA}.path_scan_queue
                    SET status='done',error=NULL,claimed_at=NULL
                    WHERE scan_id=%s AND path = ANY(%s)
                    """,
                    (scan_id, done_paths),
                )
            for parent_path, omitted_count in secret_omissions_by_parent.items():
                cur.execute(
                    f"""
                    UPDATE {_MEMORY_SCHEMA}.path_inventory
                    SET data=jsonb_set(data,'{{secret_children_omitted}}',to_jsonb(CAST(%s AS integer)),true)
                    WHERE scan_id=%s AND path=%s
                    """,
                    (omitted_count, scan_id, parent_path),
                )
            for path, error in error_rows:
                cur.execute(
                    f"""
                    UPDATE {_MEMORY_SCHEMA}.path_scan_queue
                    SET status='error',error=%s,claimed_at=NULL
                    WHERE scan_id=%s AND path=%s
                    """,
                    (error, scan_id, path),
                )

            cur.execute(
                f"""
                UPDATE {_MEMORY_SCHEMA}.path_scans
                SET updated_at=now(),
                    directories_scanned=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_scan_queue
                        WHERE scan_id=%s AND status IN ('done','error','in_progress')
                    ),
                    directories_seen=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND entry_type='dir'
                    ),
                    files_seen=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND entry_type='file'
                    ),
                    symlinks_seen=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND entry_type='symlink'
                    ),
                    other_seen=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND entry_type='other'
                    ),
                    errors=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_scan_queue
                        WHERE scan_id=%s AND status='error'
                    ),
                    secret_paths_omitted=(
                        SELECT COALESCE(sum((data->>'secret_children_omitted')::bigint),0)
                        FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND data ? 'secret_children_omitted'
                    ),
                    virtual_roots_skipped=(
                        SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory
                        WHERE scan_id=%s AND path = ANY(%s)
                    )
                WHERE scan_id=%s
                """,
                (
                    scan_id,
                    scan_id,
                    scan_id,
                    scan_id,
                    scan_id,
                    scan_id,
                    scan_id,
                    scan_id,
                    list(_PATH_SCAN_VIRTUAL_ROOTS),
                    scan_id,
                ),
            )
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_scan_queue WHERE scan_id=%s AND status IN ('pending','in_progress')",
                (scan_id,),
            )
            pending_count = int(cur.fetchone()[0])
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_scan_queue WHERE scan_id=%s AND status='error'",
                (scan_id,),
            )
            error_count = int(cur.fetchone()[0])
            complete = pending_count == 0 and error_count == 0
            if complete:
                final_status = "complete_with_declared_exclusions" if "/" in normalized_roots else "complete"
                cur.execute(
                    f"""
                    UPDATE {_MEMORY_SCHEMA}.path_scans
                    SET status=%s,completed_at=COALESCE(completed_at,now()),updated_at=now()
                    WHERE scan_id=%s
                    """,
                    (final_status, scan_id),
                )
            elif pending_count == 0 and error_count > 0:
                cur.execute(
                    f"""
                    UPDATE {_MEMORY_SCHEMA}.path_scans
                    SET status='incomplete_errors',completed_at=NULL,updated_at=now()
                    WHERE scan_id=%s
                    """,
                    (scan_id,),
                )
            cur.execute(
                f"""
                SELECT status,directories_scanned,directories_seen,files_seen,symlinks_seen,other_seen,errors,
                       secret_paths_omitted,virtual_roots_skipped
                FROM {_MEMORY_SCHEMA}.path_scans
                WHERE scan_id=%s
                """,
                (scan_id,),
            )
            (
                status,
                dirs_scanned,
                dirs_seen,
                files_seen,
                symlinks_seen,
                other_seen,
                total_errors,
                total_secret_omitted,
                total_virtual_skipped,
            ) = cur.fetchone()

        _memory_record_event(
            "path_scan_step",
            target_key=scan_id,
            payload={
                "session": _session_key(session_id),
                "processed_directories": processed,
                "pending_directories": pending_count,
                "complete": complete,
                "secret_skips": secret_skips,
                "virtual_skips": virtual_skips,
            },
        )
        return {
            "scan_id": scan_id,
            "status": str(status),
            "complete": complete,
            "processed_directories": processed,
            "pending_directories": pending_count,
            "counts": {
                "directories_scanned": int(dirs_scanned),
                "directories_seen": int(dirs_seen),
                "files_seen": int(files_seen),
                "symlinks_seen": int(symlinks_seen),
                "other_seen": int(other_seen),
                "errors": int(total_errors),
                "secret_paths_omitted": int(total_secret_omitted),
                "virtual_roots_skipped": int(total_virtual_skipped),
            },
            "secret_paths_omitted_this_step": secret_skips,
            "virtual_roots_not_descended_this_step": virtual_skips,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def path_inventory_page(
    *,
    session_id: str | None = None,
    prefix: str | None = None,
    entry_type: str | None = None,
    state: str | None = None,
    limit: int = 200,
    cursor: int = 0,
) -> dict[str, Any]:
    """Liest ausschliesslich gespeicherte Pfade aus der Postgres-Inventur."""
    limit = max(1, min(int(limit), 2000))
    cursor = max(0, int(cursor))
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        clauses = ["scan_id=%s"]
        params: list[Any] = [scan_id]
        if prefix:
            clauses.append("path LIKE %s")
            params.append(str(prefix).rstrip("/") + "/%")
        if entry_type:
            clauses.append("entry_type=%s")
            params.append(str(entry_type))
        if state:
            clauses.append("state=%s")
            params.append(str(state))
        where = " AND ".join(clauses)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT path FROM {_MEMORY_SCHEMA}.path_inventory WHERE {where} ORDER BY path LIMIT %s OFFSET %s",
                (*params, limit, cursor),
            )
            paths = [str(row[0]) for row in cur.fetchall()]
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory WHERE {where}",
                tuple(params),
            )
            total = int(cur.fetchone()[0])
        return {
            "scan_id": scan_id,
            "paths": paths,
            "cursor": cursor,
            "next_cursor": cursor + len(paths) if cursor + len(paths) < total else None,
            "total": total,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _require_complete_path_scan(conn, scan_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT status FROM {_MEMORY_SCHEMA}.path_scans WHERE scan_id=%s",
            (scan_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise CognitiveGraphError("Noch keine Pfadinventur vorhanden.")
    if str(row[0]) not in {"complete", "complete_with_declared_exclusions"}:
        raise CognitiveGraphError("Die Pfadinventur ist noch nicht vollstaendig.")


def path_record_directory_visit(path: str, *, session_id: str | None = None) -> bool:
    """Merkt einen echten Einzelbesuch eines inventarisierten Ordners nach abgeschlossenem Scan."""
    if not session_id:
        return False
    target = str(Path(path).resolve(strict=False))
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        return False
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_type FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND path=%s",
                (scan_id, target),
            )
            row = cur.fetchone()
            if row is None or str(row[0]) != "dir":
                return False
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.path_directory_visits(scan_id,path,session_id,visited_at)
                VALUES (%s,%s,%s,now())
                ON CONFLICT (scan_id,path,session_id) DO UPDATE SET visited_at=now()
                """,
                (scan_id, target, _session_key(session_id)),
            )
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass




def path_record_item_evidence(
    path: str,
    *,
    evidence_type: str,
    session_id: str | None = None,
) -> bool:
    """Merkt eine echte Lese-/Inspektionsbeobachtung fuer einen inventarisierten Nicht-Ordner."""
    if not session_id:
        return False
    target = str(Path(path).expanduser().absolute())
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        return False
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_type FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND path=%s",
                (scan_id, target),
            )
            row = cur.fetchone()
            if row is None or str(row[0]) == "dir":
                return False
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.path_item_evidence(scan_id,path,session_id,evidence_type,observed_at)
                VALUES (%s,%s,%s,%s,now())
                ON CONFLICT (scan_id,path,session_id,evidence_type) DO UPDATE SET observed_at=now()
                """,
                (scan_id, target, _session_key(session_id), str(evidence_type)),
            )
        return True
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def path_check_directory(path: str, *, session_id: str | None = None) -> dict[str, Any]:
    """Hakt genau einen inventarisierten Ordner als wirklich geprueft ab."""
    path = str(Path(path).resolve(strict=False))
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_type,state FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND path=%s",
                (scan_id, path),
            )
            row = cur.fetchone()
            if row is None:
                raise CognitiveGraphError("Ordner steht nicht in der abgeschlossenen Pfadinventur.")
            if str(row[0]) != "dir":
                raise CognitiveGraphError("Abhaken gilt hier nur fuer Ordner.")
            _require_no_path_drift(cur, scan_id, path)
            cur.execute(
                f"""
                SELECT 1
                FROM {_MEMORY_SCHEMA}.path_directory_visits
                WHERE scan_id=%s AND path=%s AND session_id=%s
                """,
                (scan_id, path, _session_key(session_id)),
            )
            if cur.fetchone() is None:
                raise CognitiveGraphError("Ordner wurde nach Abschluss der Pfadinventur noch nicht einzeln mit vps.list_files besucht.")
            cur.execute(
                f"""
                SELECT count(*)
                FROM {_MEMORY_SCHEMA}.path_inventory
                WHERE scan_id=%s
                  AND parent_path=%s
                  AND entry_type='dir'
                  AND state<>'checked'
                  AND NOT (path = ANY(%s))
                """,
                (scan_id, path, list(_PATH_SCAN_VIRTUAL_ROOTS)),
            )
            unchecked_children = int(cur.fetchone()[0])
            if unchecked_children:
                raise CognitiveGraphError(
                    f"Ordner hat noch {unchecked_children} ungepruefte direkte Unterordner; erst unten abhaken, dann den Elternordner."
                )
            cur.execute(
                f"""
                UPDATE {_MEMORY_SCHEMA}.path_inventory
                SET state='checked',checked_at=now(),check_session=%s
                WHERE scan_id=%s AND path=%s
                """,
                (_session_key(session_id), scan_id, path),
            )
        _memory_record_event(
            "path_directory_checked",
            target_key=path,
            payload={"scan_id": scan_id, "session": _session_key(session_id)},
        )
        return {"scan_id": scan_id, "path": path, "checked": True}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def path_checklist_page(
    *,
    session_id: str | None = None,
    prefix: str | None = None,
    limit: int = 200,
    cursor: int = 0,
) -> dict[str, Any]:
    """Liefert die Ordner-Hakenliste der abgeschlossenen Pfadinventur."""
    limit = max(1, min(int(limit), 2000))
    cursor = max(0, int(cursor))
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        clauses = ["scan_id=%s", "entry_type='dir'"]
        params: list[Any] = [scan_id]
        if prefix:
            clauses.append("(path=%s OR path LIKE %s)")
            clean = str(prefix).rstrip("/") or "/"
            params.extend([clean, clean.rstrip("/") + "/%"])
        where = " AND ".join(clauses)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT path,state
                FROM {_MEMORY_SCHEMA}.path_inventory
                WHERE {where}
                ORDER BY path
                LIMIT %s OFFSET %s
                """,
                (*params, limit, cursor),
            )
            items = [{"path": str(path), "checked": str(state) == "checked"} for path, state in cur.fetchall()]
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory WHERE {where}",
                tuple(params),
            )
            total = int(cur.fetchone()[0])
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_inventory WHERE {where} AND state='checked'",
                tuple(params),
            )
            checked = int(cur.fetchone()[0])
        return {
            "scan_id": scan_id,
            "items": items,
            "checked": checked,
            "unchecked": total - checked,
            "total": total,
            "cursor": cursor,
            "next_cursor": cursor + len(items) if cursor + len(items) < total else None,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def path_record_fund(
    path: str,
    *,
    what_is: str,
    origin: str,
    why_include: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Speichert einen Fund mit exakt den drei von Daniel verlangten Angaben."""
    path = str(Path(path).expanduser().absolute())
    what_is = str(what_is or "").strip()
    origin = str(origin or "").strip()
    why_include = str(why_include or "").strip()
    if not what_is or not origin or not why_include:
        raise CognitiveGraphError("Fund braucht exakt: Was ist das? / Wo kam es her? / Warum soll es mit?")
    if max(len(what_is), len(origin), len(why_include)) > 240:
        raise CognitiveGraphError("Jedes der drei Fundfelder darf hoechstens 240 Zeichen lang sein.")
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT entry_type FROM {_MEMORY_SCHEMA}.path_inventory WHERE scan_id=%s AND path=%s",
                (scan_id, path),
            )
            row = cur.fetchone()
            if row is None:
                raise CognitiveGraphError("Fundpfad steht nicht in der abgeschlossenen Pfadinventur.")
            entry_type = str(row[0])
            _require_no_path_drift(cur, scan_id, path)
            if entry_type == "dir":
                cur.execute(
                    f"""
                    SELECT 1 FROM {_MEMORY_SCHEMA}.path_directory_visits
                    WHERE scan_id=%s AND path=%s AND session_id=%s
                    """,
                    (scan_id, path, _session_key(session_id)),
                )
                if cur.fetchone() is None:
                    raise CognitiveGraphError("Fundordner wurde in dieser Reise noch nicht einzeln besucht.")
            else:
                cur.execute(
                    f"""
                    SELECT 1 FROM {_MEMORY_SCHEMA}.path_item_evidence
                    WHERE scan_id=%s AND path=%s AND session_id=%s
                    """,
                    (scan_id, path, _session_key(session_id)),
                )
                if cur.fetchone() is None:
                    raise CognitiveGraphError("Funddatei wurde in dieser Reise noch nicht vollstaendig gelesen oder als Asset inspiziert.")
            cur.execute(
                f"""
                INSERT INTO {_MEMORY_SCHEMA}.path_funds
                    (scan_id,path,what_is,origin,why_include,recorded_session)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (scan_id,path) DO UPDATE SET
                    what_is=EXCLUDED.what_is,
                    origin=EXCLUDED.origin,
                    why_include=EXCLUDED.why_include,
                    recorded_at=now(),
                    recorded_session=EXCLUDED.recorded_session
                """,
                (scan_id, path, what_is, origin, why_include, _session_key(session_id)),
            )
        _memory_record_event(
            "path_fund_recorded",
            target_key=path,
            payload={
                "scan_id": scan_id,
                "session": _session_key(session_id),
                "what_is": what_is,
                "origin": origin,
                "why_include": why_include,
            },
        )
        return {
            "scan_id": scan_id,
            "path": path,
            "what_is": what_is,
            "origin": origin,
            "why_include": why_include,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def path_funds_page(
    *,
    session_id: str | None = None,
    limit: int = 200,
    cursor: int = 0,
) -> dict[str, Any]:
    """Liest das persistente Fundregister dieser VPS-Reise."""
    limit = max(1, min(int(limit), 2000))
    cursor = max(0, int(cursor))
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        _require_complete_path_scan(conn, scan_id)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT path,what_is,origin,why_include
                FROM {_MEMORY_SCHEMA}.path_funds
                WHERE scan_id=%s
                ORDER BY recorded_at,path
                LIMIT %s OFFSET %s
                """,
                (scan_id, limit, cursor),
            )
            items = [
                {
                    "path": str(path),
                    "what_is": str(what_is),
                    "origin": str(origin),
                    "why_include": str(why_include),
                }
                for path, what_is, origin, why_include in cur.fetchall()
            ]
            cur.execute(
                f"SELECT count(*) FROM {_MEMORY_SCHEMA}.path_funds WHERE scan_id=%s",
                (scan_id,),
            )
            total = int(cur.fetchone()[0])
        return {
            "scan_id": scan_id,
            "items": items,
            "total": total,
            "cursor": cursor,
            "next_cursor": cursor + len(items) if cursor + len(items) < total else None,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


class PathJourneyState(TypedDict, total=False):
    operation: str
    session_id: str
    arguments: dict[str, Any]
    phase: str
    output: dict[str, Any]


def _path_journey_gate(state: PathJourneyState) -> dict[str, Any]:
    operation = str(state.get("operation") or "").strip()
    session_id = _session_key(state.get("session_id"))
    if operation not in {"scan", "inventory", "check", "checklist", "fund", "funds"}:
        raise CognitiveGraphError(f"Unbekannte VPS-Reiseaktion: {operation}")

    if operation == "scan":
        return {"phase": "PATH_INVENTORY"}

    scan_id = f"vps-paths::{session_id}"
    conn = _memory_connection()
    if conn is None:
        raise CognitiveGraphError("Postgres-Gedaechtnis ist nicht erreichbar.")
    try:
        _ensure_path_scan_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT status FROM {_MEMORY_SCHEMA}.path_scans WHERE scan_id=%s",
                (scan_id,),
            )
            row = cur.fetchone()
        status = str(row[0]) if row else "missing"
    finally:
        conn.close()

    complete = status in {"complete", "complete_with_declared_exclusions"}
    if operation not in {"inventory"} and not complete:
        raise CognitiveGraphError("Diese VPS-Reiseaktion ist erst nach abgeschlossener Pfadinventur erlaubt.")
    return {"phase": "MANUAL_DISCOVERY" if complete else "PATH_INVENTORY"}


def _path_journey_execute(state: PathJourneyState) -> dict[str, Any]:
    operation = str(state.get("operation") or "")
    session_id = state.get("session_id")
    args = dict(state.get("arguments") or {})

    if operation == "scan":
        output = path_scan_step(
            roots=list(args.get("roots") or []),
            secret_predicate=args.get("secret_predicate"),
            max_directories=int(args.get("max_directories", 1000)),
            reset=bool(args.get("reset", False)),
            session_id=session_id,
        )
    elif operation == "inventory":
        output = path_inventory_page(
            session_id=session_id,
            prefix=args.get("prefix"),
            entry_type=args.get("entry_type"),
            state=args.get("state"),
            limit=int(args.get("limit", 200)),
            cursor=int(args.get("cursor", 0)),
        )
    elif operation == "check":
        output = path_check_directory(str(args.get("path") or ""), session_id=session_id)
    elif operation == "checklist":
        output = path_checklist_page(
            session_id=session_id,
            prefix=args.get("prefix"),
            limit=int(args.get("limit", 200)),
            cursor=int(args.get("cursor", 0)),
        )
    elif operation == "fund":
        output = path_record_fund(
            str(args.get("path") or ""),
            what_is=str(args.get("what_is") or ""),
            origin=str(args.get("origin") or ""),
            why_include=str(args.get("why_include") or ""),
            session_id=session_id,
        )
    else:
        output = path_funds_page(
            session_id=session_id,
            limit=int(args.get("limit", 200)),
            cursor=int(args.get("cursor", 0)),
        )
    return {"output": output}


def _path_journey_remember(state: PathJourneyState) -> dict[str, Any]:
    output = dict(state.get("output") or {})
    _memory_record_event(
        "path_journey_step",
        target_key=str(output.get("path") or output.get("scan_id") or "") or None,
        payload={
            "session": _session_key(state.get("session_id")),
            "operation": str(state.get("operation") or ""),
            "phase": str(state.get("phase") or ""),
        },
    )
    return {}


def _build_path_journey_graph():
    graph = StateGraph(PathJourneyState)
    graph.add_node("gate", _path_journey_gate)
    graph.add_node("execute", _path_journey_execute)
    graph.add_node("remember", _path_journey_remember)
    graph.add_edge(START, "gate")
    graph.add_edge("gate", "execute")
    graph.add_edge("execute", "remember")
    graph.add_edge("remember", END)
    return graph.compile()


_PATH_JOURNEY_GRAPH = _build_path_journey_graph()


def path_journey_run(
    operation: str,
    *,
    arguments: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    result = _PATH_JOURNEY_GRAPH.invoke(
        {
            "operation": str(operation),
            "arguments": dict(arguments or {}),
            "session_id": _session_key(session_id),
        }
    )
    return dict(result.get("output") or {})


NODE_TYPES = {
    "USER_DIRECTIVE",
    "SOURCE_READ",
    "OBSERVATION",
    "QUESTION",
    "HYPOTHESIS",
    "CONTRADICTION",
    "DECISION",
    "ACTION",
    "VERIFICATION",
    "BLOCK",
    "LESSON",
}
EDGE_TYPES = {
    "LEADS_TO",
    "SUPPORTS",
    "CONTRADICTS",
    "ANSWERS",
    "DEPENDS_ON",
    "SUPERSEDES",
    "VERIFIED_BY",
    "BLOCKED_BY",
    "DERIVED_FROM",
    "REQUESTS",
}
CONFIDENCE = {"unknown", "low", "medium", "high"}
STATUSES = {"open", "resolved", "superseded"}


class CognitiveGraphError(RuntimeError):
    pass


def _session_key(session_id: str | None) -> str:
    raw = str(session_id or "default")
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in "._-")[:100]
    return safe or "default"


def _empty_store() -> dict[str, Any]:
    return {"schema": _SCHEMA, "sessions": {}}


def _empty_session() -> dict[str, Any]:
    return {
        "nodes": [],
        "edges": [],
        "last_action_node": None,
        "last_updated": None,
    }


def _load() -> dict[str, Any]:
    try:
        data = json.loads(_RUNTIME_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("schema") == _SCHEMA:
            return data
    except Exception:
        pass
    return _empty_store()


def _save(data: dict[str, Any]) -> None:
    try:
        tmp = _RUNTIME_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(_RUNTIME_PATH)
    except Exception:
        # Das kognitive Zusatznetz darf nie den Werkzeugkoerper lahmlegen.
        pass


def _get_session(store: dict[str, Any], key: str) -> dict[str, Any]:
    sessions = store.setdefault("sessions", {})
    session = sessions.get(key)
    if not isinstance(session, dict):
        session = _empty_session()
        sessions[key] = session
    base = _empty_session()
    base.update(session)
    sessions[key] = base
    return base


def _new_id(prefix: str = "n") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _normalize_refs(source_refs: list[str] | None) -> list[str]:
    refs: list[str] = []
    for ref in source_refs or []:
        value = str(ref).strip()
        if value and value not in refs:
            refs.append(value)
    return refs[:30]


def _validate_semantics(
    node_type: str,
    text: str,
    source_refs: list[str],
    confidence: str,
) -> str:
    if node_type not in NODE_TYPES:
        raise CognitiveGraphError(f"Unbekannter node_type: {node_type}")
    if not text.strip():
        raise CognitiveGraphError("text fehlt")
    if confidence not in CONFIDENCE:
        raise CognitiveGraphError(f"confidence muss eines von {sorted(CONFIDENCE)} sein")

    if node_type == "OBSERVATION" and not source_refs:
        raise CognitiveGraphError(
            "OBSERVATION braucht mindestens eine source_ref. Ohne Beleg ist es QUESTION oder HYPOTHESIS."
        )
    if node_type == "CONTRADICTION" and len(source_refs) < 2:
        raise CognitiveGraphError(
            "CONTRADICTION braucht mindestens zwei getrennte source_refs."
        )
    if node_type == "USER_DIRECTIVE":
        return "EXPLICIT_USER_INPUT"
    if node_type in {"QUESTION", "HYPOTHESIS"} and not source_refs:
        return "UNVERIFIED"
    if source_refs:
        return "GROUNDED"
    return "WORKING_NOTE"


def add_node(
    node_type: str,
    text: str,
    source_refs: list[str] | None = None,
    confidence: str = "unknown",
    status: str = "open",
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node_type = str(node_type or "").strip().upper()
    text = str(text or "").strip()
    confidence = str(confidence or "unknown").strip().lower()
    status = str(status or "open").strip().lower()
    refs = _normalize_refs(source_refs)
    epistemic_status = _validate_semantics(node_type, text, refs, confidence)
    if status not in STATUSES:
        raise CognitiveGraphError(f"status muss eines von {sorted(STATUSES)} sein")

    node = {
        "id": _new_id(),
        "type": node_type,
        "text": text[:4000],
        "confidence": confidence,
        "status": status,
        "epistemic_status": epistemic_status,
        "source_refs": refs,
        "metadata": metadata if isinstance(metadata, dict) else {},
        "created_at": time.time(),
        "updated_at": time.time(),
    }

    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        nodes = list(session.get("nodes") or [])
        nodes.append(node)
        session["nodes"] = nodes[-_MAX_NODES:]
        session["last_updated"] = time.time()
        _save(store)
    return node


def add_edge(
    from_id: str,
    to_id: str,
    edge_type: str,
    reason: str = "",
    session_id: str | None = None,
) -> dict[str, Any]:
    edge_type = str(edge_type or "").strip().upper()
    if edge_type not in EDGE_TYPES:
        raise CognitiveGraphError(f"Unbekannter edge_type: {edge_type}")

    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        node_ids = {node.get("id") for node in session.get("nodes") or []}
        if from_id not in node_ids or to_id not in node_ids:
            raise CognitiveGraphError("from_id und to_id muessen existierende Knoten derselben Session sein")
        edge = {
            "id": _new_id("e"),
            "from": from_id,
            "to": to_id,
            "type": edge_type,
            "reason": str(reason or "")[:2000],
            "created_at": time.time(),
        }
        edges = list(session.get("edges") or [])
        edges.append(edge)
        session["edges"] = edges[-_MAX_EDGES:]
        session["last_updated"] = time.time()
        _save(store)
        return edge


def resolve_node(
    node_id: str,
    status: str = "resolved",
    session_id: str | None = None,
) -> dict[str, Any]:
    status = str(status or "").strip().lower()
    if status not in STATUSES:
        raise CognitiveGraphError(f"status muss eines von {sorted(STATUSES)} sein")
    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        for node in session.get("nodes") or []:
            if node.get("id") == node_id:
                node["status"] = status
                node["updated_at"] = time.time()
                session["last_updated"] = time.time()
                _save(store)
                return node
    raise CognitiveGraphError(f"Knoten nicht gefunden: {node_id}")


def _extract_paths(args: dict[str, Any] | None, tool_name: str | None = None) -> list[str]:
    args = args if isinstance(args, dict) else {}
    paths: list[str] = []

    def add_path(raw: str) -> None:
        try:
            path = str(Path(raw).resolve(strict=False))
        except Exception:
            return
        if path not in paths:
            paths.append(path)

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if value.startswith("/"):
                add_path(value)
            return
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    walk(args)

    if tool_name == "vps.shell":
        cwd_raw = args.get("cwd")
        command = args.get("command", args.get("cmd", ""))
        try:
            cwd = Path(str(cwd_raw)).resolve(strict=False)
        except Exception:
            cwd = None
        if cwd is not None and isinstance(command, str):
            try:
                tokens = shlex.split(command)
            except Exception:
                tokens = command.split()
            for token in tokens:
                token = token.strip()
                if not token or token.startswith("-") or token in {"|", "&&", ";"}:
                    continue
                candidate = Path(token)
                if not candidate.is_absolute():
                    candidate = cwd / candidate
                try:
                    resolved = candidate.resolve(strict=False)
                except Exception:
                    continue
                if resolved.exists():
                    add_path(str(resolved))

        root = str(cwd) if cwd is not None else None
        if root and len(paths) > 1 and root in paths:
            paths = [path for path in paths if path != root]

    return paths[:12]


def _upsert_source_read(session: dict[str, Any], path: str, tool_name: str) -> dict[str, Any]:
    nodes = list(session.get("nodes") or [])
    for node in reversed(nodes):
        if (
            node.get("type") == "SOURCE_READ"
            and (node.get("metadata") or {}).get("path") == path
        ):
            meta = node.setdefault("metadata", {})
            meta["read_count"] = int(meta.get("read_count") or 1) + 1
            meta["last_tool"] = tool_name
            node["updated_at"] = time.time()
            return node
    node = {
        "id": _new_id(),
        "type": "SOURCE_READ",
        "text": f"Gelesene Quelle: {path}",
        "confidence": "high",
        "status": "open",
        "epistemic_status": "GROUNDED",
        "source_refs": [path],
        "metadata": {
            "path": path,
            "read_count": 1,
            "last_tool": tool_name,
        },
        "created_at": time.time(),
        "updated_at": time.time(),
    }
    nodes.append(node)
    session["nodes"] = nodes[-_MAX_NODES:]
    return node


def _path_journey_annotations(paths: list[str], session_id: str | None) -> dict[str, dict[str, Any]]:
    clean = [str(path) for path in dict.fromkeys(paths) if str(path).strip()]
    if not clean:
        return {}
    scan_id = f"vps-paths::{_session_key(session_id)}"
    conn = _memory_connection()
    if conn is None:
        return {}
    try:
        _ensure_path_scan_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT path,state
                FROM {_MEMORY_SCHEMA}.path_inventory
                WHERE scan_id=%s AND path = ANY(%s)
                """,
                (scan_id, clean),
            )
            info = {
                str(path): {
                    "inventoried": True,
                    "checked": str(state) == "checked",
                    "fund": False,
                }
                for path, state in cur.fetchall()
            }
            cur.execute(
                f"""
                SELECT path
                FROM {_MEMORY_SCHEMA}.path_funds
                WHERE scan_id=%s AND path = ANY(%s)
                """,
                (scan_id, clean),
            )
            for (path,) in cur.fetchall():
                item = info.setdefault(
                    str(path),
                    {"inventoried": True, "checked": False, "fund": False},
                )
                item["fund"] = True
        return info
    except Exception:
        return {}
    finally:
        try:
            conn.close()
        except Exception:
            pass


class WanderState(TypedDict, total=False):
    session_id: str
    seed: str
    trail: list[str]
    limit: int
    retrieved: list[dict[str, Any]]
    route: list[dict[str, Any]]
    output: dict[str, Any]


def _wander_retrieve(state: WanderState) -> dict[str, Any]:
    seed = str(state.get("seed") or "").strip()
    limit = max(3, min(int(state.get("limit") or 6), 12))
    result = hybrid_suche(seed, limit=max(12, limit * 3)) if seed else {"ergebnisse": []}
    return {"retrieved": list(result.get("ergebnisse") or [])}


def _wander_shape(state: WanderState) -> dict[str, Any]:
    raw = list(state.get("retrieved") or [])
    trail = [str(p) for p in (state.get("trail") or []) if str(p).strip()]
    visited = set(trail)
    limit = max(3, min(int(state.get("limit") or 6), 12))
    route: list[dict[str, Any]] = []
    seen: set[str] = set()
    candidate_paths = [str(entry.get("pfad") or "") for entry in raw]
    memory_states = _memory_source_states(candidate_paths)
    journey_states = _path_journey_annotations(candidate_paths, state.get("session_id"))

    def add(entry: dict[str, Any], pull: str) -> None:
        path = str(entry.get("pfad") or "").strip()
        if not path or path in seen or len(route) >= limit:
            return
        item = dict(entry)
        exists_now = Path(path).exists()
        remembered = memory_states.get(path)
        item["pull"] = ("historische/stale Spur: " + pull) if not exists_now else pull
        item["exists_now"] = exists_now
        item["visited_before"] = path in visited
        item["read_status"] = remembered or entry.get("read_state") or ("read_partial" if bool(entry.get("manual_read")) else "unread_or_unknown")
        item["journey"] = journey_states.get(
            path,
            {"inventoried": False, "checked": False, "fund": False},
        )
        item["authority"] = "INVITATION_ONLY"
        route.append(item)
        seen.add(path)

    # Erst der offensichtliche Zug, damit Wandern nicht mit absichtlicher Blindheit verwechselt wird.
    for entry in raw[:2]:
        add(entry, "starker Zug aus der aktuellen Suche")

    # Ein Echo aus bereits wirklich gelesener Landschaft, falls vorhanden.
    for entry in raw:
        path = str(entry.get("pfad") or "")
        if (memory_states.get(path) == "read" or entry.get("read_state") == "read") and path not in seen:
            add(entry, "Echo aus bereits bereister Landschaft")
            break

    # Ein bewusster Seitensprung aus der hinteren Haelfte der Trefferliste.
    if raw:
        start = max(2, len(raw) // 2)
        for entry in raw[start:]:
            if str(entry.get("pfad") or "") not in seen:
                add(entry, "Seitenpfad: nicht der naheliegendste Treffer")
                break

    # Rueckkehr ist ein eigener Wert: Bekanntes kann spaeter etwas anderes bedeuten.
    for entry in raw:
        if str(entry.get("pfad") or "") in visited and str(entry.get("pfad") or "") not in seen:
            add(entry, "Rueckkehr: dieser Ort taucht auf der neuen Spur wieder auf")
            break

    # Restliche Plaetze ohne weitere Theorie fuellen.
    for entry in raw:
        add(entry, "weitere moegliche Abzweigung")

    return {"route": route}


def _wander_remember(state: WanderState) -> dict[str, Any]:
    seed = str(state.get("seed") or "").strip()
    session_id = _session_key(state.get("session_id"))
    trail = [str(p) for p in (state.get("trail") or []) if str(p).strip()]
    route = list(state.get("route") or [])

    for item in route:
        path = str(item.get("pfad") or "").strip()
        if not path:
            continue
        _memory_mark_source(
            path,
            state="read" if item.get("read_status") == "read" else "suggested",
            note="Vom Wander-RAG als moeglicher Weg gesehen; kein Lesebeweis.",
            data={
                "last_seed": seed,
                "last_pull": item.get("pull"),
                "retrieval_sources": item.get("gefunden_ueber") or [],
                "session": session_id,
            },
        )

    _memory_record_event(
        "wander",
        target_key=trail[-1] if trail else None,
        payload={
            "session": session_id,
            "seed": seed,
            "trail": trail[-20:],
            "candidates": [
                {
                    "path": item.get("pfad"),
                    "pull": item.get("pull"),
                    "read_status": item.get("read_status"),
                    "journey": item.get("journey") or {},
                    "authority": "INVITATION_ONLY",
                }
                for item in route
            ],
        },
    )

    output = {
        "seed": seed,
        "session": session_id,
        "trail": trail,
        "paths": route,
        "contract": [
            "RAG zeigt Wege, es entscheidet keine Wahrheit.",
            "Treffer bedeutet nicht gelesen.",
            "Originalquelle gewinnt gegen Index, Zusammenfassung, DB und frueheren AI-Output.",
            "Kein Pfad wird automatisch verfolgt; der naechste echte Schritt bleibt sichtbar und einzeln.",
        ],
    }
    return {"output": output}


def _build_wander_graph():
    graph = StateGraph(WanderState)
    graph.add_node("retrieve", _wander_retrieve)
    graph.add_node("shape", _wander_shape)
    graph.add_node("remember", _wander_remember)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "shape")
    graph.add_edge("shape", "remember")
    graph.add_edge("remember", END)
    return graph.compile()


_WANDER_GRAPH = _build_wander_graph()


def wander(seed: str, trail: list[str] | None = None, limit: int = 6, session_id: str | None = None) -> dict[str, Any]:
    seed = str(seed or "").strip()
    if not seed:
        raise CognitiveGraphError("wander braucht einen seed / eine Spur, von der aus wir losgehen")
    state: WanderState = {
        "seed": seed,
        "trail": list(trail or []),
        "limit": max(3, min(int(limit), 12)),
        "session_id": _session_key(session_id),
    }
    result = _WANDER_GRAPH.invoke(state)
    return dict(result.get("output") or {})


def record_tool_event(
    tool_name: str,
    args: dict[str, Any] | None,
    decision: Any,
    result: dict[str, Any] | None,
) -> None:
    result = result if isinstance(result, dict) else {}
    ok = bool(result.get("ok"))
    key = _session_key((args or {}).get("session_id") if isinstance(args, dict) else None)
    paths = _extract_paths(args, tool_name)

    if ok and tool_name == "vps.list_files" and paths:
        for path in paths:
            path_record_directory_visit(
                path,
                session_id=(args or {}).get("session_id") if isinstance(args, dict) else None,
            )

    # Nur vps.read_file ist fuer diese Reise ein echter Inhalts-Lesezugriff.
    # Ein Zeilenbereich ist bewusst nur read_partial; assets.get_file, Suche und RAG
    # duerfen niemals stillschweigend zu "gelesen" hochstufen.
    start_line = (args or {}).get("start_line") if isinstance(args, dict) else None
    end_line = (args or {}).get("end_line") if isinstance(args, dict) else None
    is_partial_read = tool_name == "vps.read_file" and (start_line is not None or end_line is not None)

    evidence_type = None
    if ok and tool_name == "vps.read_file" and paths and not is_partial_read:
        evidence_type = "read"
    elif ok and tool_name in {"assets.inspect", "assets.inspect_image", "assets.inspect_audio"} and paths:
        evidence_type = "inspect"
    if evidence_type:
        for path in paths:
            path_record_item_evidence(
                path,
                evidence_type=evidence_type,
                session_id=(args or {}).get("session_id") if isinstance(args, dict) else None,
            )

    if ok and tool_name == "vps.read_file" and paths:
        body = result.get("data")
        memory_state = "read_partial" if is_partial_read else "read"
        event_name = "source_read_partial" if is_partial_read else "source_read"
        for path in paths:
            _memory_mark_source(
                path,
                state=memory_state,
                note="Direkt teilweise mit vps.read_file gelesen." if is_partial_read else "Direkt vollstaendig mit vps.read_file gelesen.",
                data={"last_tool": tool_name, "session": key, "read_at": time.time(), "read_state": memory_state},
            )
            _memory_record_event(
                event_name,
                target_key=path,
                payload={"session": key, "tool": tool_name, "read_state": memory_state},
            )
        if isinstance(body, str) and body.strip():
            read_range = f"L{start_line or 1}-L{end_line or 'EOF'}"
            chunk_id = f"{paths[0]}::{read_range}"
            manual_read_index_aktualisieren(
                pfad=chunk_id,
                text=body,
                metadaten={
                    "session": key,
                    "source": tool_name,
                    "source_path": paths[0],
                    "read_range": read_range,
                    "read_state": memory_state,
                    "titel": Path(paths[0]).name,
                },
            )

    if not bool(getattr(decision, "project_scoped", False)):
        return

    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        action_node = str(getattr(decision, "action_node", ""))
        before_state = str(getattr(decision, "state", ""))

        if action_node == "READ" and ok and tool_name == "vps.read_file" and not is_partial_read:
            for path in paths:
                _upsert_source_read(session, path, tool_name)
            if before_state == STATE_VERIFY:
                node = {
                    "id": _new_id(),
                    "type": "VERIFICATION",
                    "text": f"Verifikation nach Eingriff via {tool_name}",
                    "confidence": "high",
                    "status": "open",
                    "epistemic_status": "GROUNDED",
                    "source_refs": paths,
                    "metadata": {"tool": tool_name},
                    "created_at": time.time(),
                    "updated_at": time.time(),
                }
                nodes = list(session.get("nodes") or [])
                nodes.append(node)
                session["nodes"] = nodes[-_MAX_NODES:]
                previous = session.get("last_action_node")
                if previous:
                    edges = list(session.get("edges") or [])
                    edges.append({
                        "id": _new_id("e"),
                        "from": previous,
                        "to": node["id"],
                        "type": "VERIFIED_BY",
                        "reason": "Workflow-State verlangte Gegenlesen nach Mutation.",
                        "created_at": time.time(),
                    })
                    session["edges"] = edges[-_MAX_EDGES:]

        elif not bool(getattr(decision, "allowed", False)):
            node = {
                "id": _new_id(),
                "type": "BLOCK",
                "text": str(getattr(decision, "reason", "Aktion blockiert")),
                "confidence": "high",
                "status": "open",
                "epistemic_status": "WORKING_NOTE",
                "source_refs": paths,
                "metadata": {
                    "tool": tool_name,
                    "action_node": action_node,
                },
                "created_at": time.time(),
                "updated_at": time.time(),
            }
            nodes = list(session.get("nodes") or [])
            nodes.append(node)
            session["nodes"] = nodes[-_MAX_NODES:]

        elif ok and action_node in {
            "SINGLE_EDIT",
            "SINGLE_WRITE",
            "SINGLE_DELETE",
            "SINGLE_MOVE",
            "CREATE_SCRIPT",
            "META_GENERATION",
        }:
            node = {
                "id": _new_id(),
                "type": "ACTION",
                "text": f"Ausgefuehrte Aktion: {tool_name} ({action_node})",
                "confidence": "high",
                "status": "open",
                "epistemic_status": "GROUNDED",
                "source_refs": paths,
                "metadata": {
                    "tool": tool_name,
                    "action_node": action_node,
                },
                "created_at": time.time(),
                "updated_at": time.time(),
            }
            nodes = list(session.get("nodes") or [])
            nodes.append(node)
            session["nodes"] = nodes[-_MAX_NODES:]
            session["last_action_node"] = node["id"]

        session["last_updated"] = time.time()
        _save(store)


def _open_nodes(nodes: list[dict[str, Any]], node_type: str) -> list[dict[str, Any]]:
    return [
        node for node in nodes
        if node.get("type") == node_type and node.get("status") == "open"
    ]


def next_moves(session_id: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 10))
    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        nodes = list(session.get("nodes") or [])

    workflow = workflow_snapshot(session_id)
    runtime = workflow.get("runtime") or {}
    state = runtime.get("state")
    mode = runtime.get("mode", MODE_DISCOVER)

    suggestions: list[dict[str, Any]] = []

    if state == STATE_VERIFY:
        suggestions.append({
            "move": "VERIFY_PENDING_ACTION",
            "why": "Der Workflow hat eine offene VERIFY-Schuld. Erst das betroffene Ziel oder git.diff/show pruefen.",
            "node_ids": [session.get("last_action_node")] if session.get("last_action_node") else [],
        })

    contradictions = _open_nodes(nodes, "CONTRADICTION")
    if contradictions:
        suggestions.append({
            "move": "COMPARE_CONFLICTING_EVIDENCE",
            "why": "Mindestens ein offener Widerspruch existiert. Nicht glattbuegeln; Quellen getrennt vergleichen.",
            "node_ids": [n["id"] for n in contradictions[-3:]],
        })

    hypotheses = [
        n for n in _open_nodes(nodes, "HYPOTHESIS")
        if n.get("epistemic_status") == "UNVERIFIED"
    ]
    if hypotheses:
        suggestions.append({
            "move": "SEEK_EVIDENCE_FOR_HYPOTHESIS",
            "why": "Eine Hypothese ist explizit unbestaetigt. Suche Belege oder Gegenbelege statt sie zur Tatsache hochzustufen.",
            "node_ids": [n["id"] for n in hypotheses[-3:]],
        })

    questions = _open_nodes(nodes, "QUESTION")
    if questions:
        suggestions.append({
            "move": "EXPLORE_OPEN_QUESTION",
            "why": "Offene Frage vorhanden. Folge einer Quelle, die sie wirklich beantworten koennte.",
            "node_ids": [n["id"] for n in questions[-3:]],
        })

    source_reads = _open_nodes(nodes, "SOURCE_READ")
    if len(source_reads) < 2:
        suggestions.append({
            "move": "READ_DIVERSE_SOURCE",
            "why": "Noch zu wenig unabhaengige gelesene Quellen im Arbeitsnetz.",
            "node_ids": [n["id"] for n in source_reads[-2:]],
        })
    elif not contradictions and not hypotheses and not questions:
        suggestions.append({
            "move": "COMPARE_OR_FORM_QUESTION",
            "why": "Mehrere Quellen sind vorhanden, aber kein offener Widerspruch/Hypothese/Frage. Jetzt querlesen statt nur weiter sammeln.",
            "node_ids": [n["id"] for n in source_reads[-3:]],
        })

    if mode in {MODE_SURGICAL, MODE_CONTROL_PLANE} and state == STATE_CHANGE_READY:
        suggestions.append({
            "move": "DECIDE_TARGETED_ACTION",
            "why": "Intent erlaubt Eingriff und der Workflow hat genug gelesenen Kontext. Vor Aktion Ziel und Zweck benennen.",
            "node_ids": [],
        })

    return suggestions[:limit]


def snapshot(session_id: str | None = None) -> dict[str, Any]:
    key = _session_key(session_id)
    with _LOCK:
        store = _load()
        session = _get_session(store, key)
        nodes = list(session.get("nodes") or [])
        edges = list(session.get("edges") or [])

    counts: dict[str, int] = {}
    for node in nodes:
        counts[node.get("type", "UNKNOWN")] = counts.get(node.get("type", "UNKNOWN"), 0) + 1

    return {
        "active": True,
        "session": key,
        "node_types": sorted(NODE_TYPES),
        "edge_types": sorted(EDGE_TYPES),
        "counts": counts,
        "nodes": nodes,
        "edges": edges,
        "next_moves": next_moves(session_id, limit=5),
        "rules": [
            "OBSERVATION braucht source_ref; unbelegte Einfaelle sind HYPOTHESIS/QUESTION.",
            "CONTRADICTION braucht mindestens zwei getrennte source_refs.",
            "Hypothesen duerfen kreativ sein, bleiben ohne Beleg explizit UNVERIFIED.",
            "USER_DIRECTIVE ist eigener Knotentyp und wird nicht als Beobachtung ausgegeben.",
            "Tool-Laufspur speichert nur Metadaten/Pfade, keine gelesenen Inhalte.",
        ],
    }
