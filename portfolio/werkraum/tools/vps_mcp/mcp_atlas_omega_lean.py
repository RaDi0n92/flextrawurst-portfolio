from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

ATLAS_ROOT = Path('/root/werkraum/_gpt/gesamtatlas')
DEFAULT_BINDING = ATLAS_ROOT / 'omega/OMEGA_LEAN_BINDING.json'
DEFAULT_BASELINE_POINTER = ATLAS_ROOT / 'omega/VERIFIED_FULL_BASELINE.json'
WORLD_MODEL = 'VERIFIED_FULL_BASELINE_PLUS_VISIBLE_LIVE_DELTA'
MAX_EXACT_FILE_BYTES = 64 * 1024 * 1024
MAX_EXACT_TOTAL_BYTES = 128 * 1024 * 1024
MAX_FULL_HASH_BYTES = 64 * 1024 * 1024
OBJECT_PREFIX = 'leanpath:'
_HASH_CACHE: dict[tuple[str, int, int, int, str], bool] = {}
_HASH_LOCK = threading.RLock()
T = TypeVar('T')


class LeanOmegaError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _signature(path: Path) -> dict[str, int]:
    st = path.stat()
    return {'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns, 'inode': st.st_ino}


def _binding_path() -> Path:
    return Path(os.environ.get('GESAMTATLAS_OMEGA_LEAN_BINDING', str(DEFAULT_BINDING))).resolve()


def _load_binding() -> tuple[dict[str, Any], str, Path]:
    path = _binding_path()
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode('utf-8'))
    except FileNotFoundError as exc:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Lean-Bindung fehlt: {path}') from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Lean-Bindung unlesbar: {path}: {exc}') from exc
    if not isinstance(value, dict) or value.get('backend') != 'OMEGA_LEAN_REFERENCE' or value.get('status') != 'PASS':
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Ungültige Lean-Bindung: {path}')
    return value, _sha256_bytes(raw), path


def _verify_source(key: str, item: dict[str, Any], *, verify_hashes: bool) -> dict[str, Any]:
    path = Path(str(item.get('path') or '')).resolve()
    if not path.is_file() or path.is_symlink():
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Gebundene Quelle fehlt/ist Symlink: {key}: {path}')
    expected = {name: int(item.get(name, -1)) for name in ('bytes', 'mtime_ns', 'inode')}
    before = _signature(path)
    if before != expected:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Quellenstat driftet: {key}: erwartet={expected}, aktuell={before}')
    expected_sha = str(item.get('sha256') or '')
    verification = 'STAT_ONLY'
    if verify_hashes:
        if len(expected_sha) != 64:
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: SHA-256 fehlt: {key}')
        cache_key = (str(path), before['inode'], before['bytes'], before['mtime_ns'], expected_sha)
        with _HASH_LOCK:
            cached = _HASH_CACHE.get(cache_key, False)
        if not cached:
            actual_sha = _sha256_file(path)
            after_hash = _signature(path)
            if after_hash != before:
                raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Quelle änderte sich während Hashprüfung: {key}')
            if actual_sha != expected_sha:
                raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: SHA-256 driftet: {key}')
            with _HASH_LOCK:
                _HASH_CACHE[cache_key] = True
            verification = 'SHA256_VERIFIED_NOW'
        else:
            verification = 'SHA256_VERIFIED_CACHED_FOR_IDENTICAL_STAT'
    after = _signature(path)
    if after != before:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Quelle änderte sich während Gate: {key}')
    return {
        'path': str(path),
        'original_path': item.get('original_path'),
        **after,
        'sha256': expected_sha,
        'hash_verification': verification,
        'storage_mode': item.get('storage_mode'),
    }


def _load_json_object(path: Path, *, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode('utf-8'))
    except FileNotFoundError as exc:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: {label} fehlt: {path}') from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: {label} unlesbar: {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: {label} ist kein JSON-Objekt: {path}')
    return value, raw


def _verify_artifact_ref(key: str, item: dict[str, Any], *, verify_hashes: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    path = Path(str(item.get('path') or '')).resolve()
    if not path.is_file() or path.is_symlink():
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Wahrheitskörper fehlt/ist Symlink: {key}: {path}')
    raw_size = path.stat().st_size
    expected_bytes = int(item.get('bytes', -1))
    if raw_size != expected_bytes:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Wahrheitskörpergröße driftet: {key}: {raw_size} != {expected_bytes}')
    expected_sha = str(item.get('sha256') or '')
    verification = 'SIZE_ONLY'
    if verify_hashes:
        if len(expected_sha) != 64:
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: SHA-256 fehlt für Wahrheitskörper: {key}')
        actual_sha = _sha256_file(path)
        if actual_sha != expected_sha:
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Wahrheitskörper-Hash driftet: {key}')
        verification = 'SHA256_VERIFIED_NOW'
    value, raw = _load_json_object(path, label=key)
    if len(raw) != raw_size:
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Wahrheitskörper änderte sich während Prüfung: {key}')
    return value, {
        'path': str(path), 'bytes': raw_size, 'sha256': expected_sha,
        'hash_verification': verification,
    }


def _verify_baseline_pointer(baseline_ref: dict[str, Any], *, verify_hashes: bool) -> dict[str, Any]:
    pointer_path = Path(os.environ.get('GESAMTATLAS_OMEGA_BASELINE_POINTER', str(DEFAULT_BASELINE_POINTER))).resolve()
    pointer, raw = _load_json_object(pointer_path, label='verified_full_baseline_pointer')
    if pointer_path.is_symlink() or pointer.get('pointer_class') != 'CURRENT_VERIFIED_BASELINE_POINTER' or pointer.get('status') != 'CURRENT_VERIFIED_BASELINE_POINTER':
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Ungültiger aktueller Baseline-Pointer')
    if pointer.get('world_model') != WORLD_MODEL:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Baseline-Pointer besitzt falsches Weltmodell')
    target = pointer.get('target') or {}
    for field in ('path', 'bytes', 'sha256', 'baseline_id', 'revision'):
        if target.get(field) != baseline_ref.get(field):
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Pointerziel und Binding-Baseline driften: {field}')
    if pointer.get('baseline_id') != baseline_ref.get('baseline_id') or pointer.get('revision') != baseline_ref.get('revision'):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Pointerkopf und Binding-Baseline driften')
    target_path = Path(str(target.get('path') or '')).resolve()
    expected_root = (ATLAS_ROOT / 'omega/verified_full_baselines' / str(pointer.get('revision'))).resolve()
    try: target_path.relative_to(expected_root)
    except ValueError as exc: raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Pointerziel ist nicht revisionsgebunden') from exc
    if verify_hashes and _sha256_bytes(raw) != _sha256_file(pointer_path):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Pointer änderte sich während Prüfung')
    return {'path':str(pointer_path),'bytes':len(raw),'sha256':_sha256_bytes(raw),'pointer_class':pointer['pointer_class'],'baseline_id':pointer['baseline_id'],'revision':pointer['revision'],'target':target}


def _world_contract(binding: dict[str, Any], manifest_sha: str, manifest_path: Path, *, verify_hashes: bool) -> dict[str, Any]:
    model = binding.get('world_model') or {}
    if model.get('name') != WORLD_MODEL:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Unbekanntes Grundstand-/Live-Nachlauf-Weltmodell')
    baseline_ref = binding.get('verified_full_baseline')
    if not isinstance(baseline_ref, dict):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Verifizierter Full-Grundstand fehlt in Bindung')
    pointer_artifact = _verify_baseline_pointer(baseline_ref, verify_hashes=verify_hashes)
    baseline, baseline_artifact = _verify_artifact_ref('verified_full_baseline', baseline_ref, verify_hashes=verify_hashes)
    world_baseline = model.get('verified_full_baseline') or {}
    for field in ('path', 'bytes', 'sha256', 'baseline_id', 'revision'):
        if baseline_ref.get(field) != world_baseline.get(field):
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Grundstand-Referenz driftet im Weltmodell: {field}')
    if baseline.get('status') != 'VERIFIED_FULL_BASELINE' or baseline.get('world_model') != WORLD_MODEL:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Grundstand besitzt falschen Status oder Weltvertrag')
    if baseline.get('baseline_id') != baseline_ref.get('baseline_id') or baseline.get('revision') != baseline_ref.get('revision'):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Grundstand-ID oder Revision driftet')
    checks = ((baseline.get('verification') or {}).get('checks') or {})
    if not checks or not all(checks.values()):
        passed = sum(bool(value) for value in checks.values())
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Grundstand ist nicht vollständig PASS-verifiziert ({passed}/{len(checks)})')
    evidence = {}
    for key in ('full_refresh', 'full_verification'):
        item = baseline.get(key) or {}
        _, evidence[key] = _verify_artifact_ref(f'baseline_{key}', item, verify_hashes=verify_hashes)
        expected_root = (ATLAS_ROOT / 'omega/verified_full_baselines' / str(baseline.get('revision'))).resolve()
        try: Path(evidence[key]['path']).resolve().relative_to(expected_root)
        except ValueError as exc: raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Baseline-Evidence nicht revisionsgebunden: {key}') from exc
    if '/runtime/last_full_' in json.dumps(baseline, ensure_ascii=False):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Historische Baseline enthält bewegliche latest-Pfade')

    live_ref = binding.get('live_delta_object') or {}
    live_path = Path(str(live_ref.get('path') or '')).resolve()
    live, live_raw = _load_json_object(live_path, label='live_delta_state')
    if live_path.is_symlink():
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Live-Nachlauf darf kein Symlink sein')
    live_sha = _sha256_bytes(live_raw)
    current = model.get('current_live_state') or {}
    if live.get('status') != 'VISIBLE_LIVE_STATE' or live.get('world_model') != WORLD_MODEL:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Live-Nachlauf besitzt falschen Status oder Weltvertrag')
    comparisons = {
        'live_delta_id': (live.get('live_delta_id'), live_ref.get('live_delta_id')),
        'source_revision': (live.get('source_revision'), binding.get('source_revision')),
        'publication_mode': (live.get('publication_mode'), binding.get('publication_mode')),
        'source_dirty': (live.get('source_dirty'), binding.get('source_dirty')),
        'baseline_id': (live.get('baseline_id'), baseline.get('baseline_id')),
        'baseline_revision': (live.get('baseline_revision'), baseline.get('revision')),
        'current_binding_sha256': ((live.get('current_binding') or {}).get('sha256'), manifest_sha),
        'current_binding_path': (str(Path(str((live.get('current_binding') or {}).get('path') or '')).resolve()), str(manifest_path)),
    }
    for field, pair in comparisons.items():
        if pair[0] != pair[1]:
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Grundstand-/Live-Verknüpfung driftet: {field}: {pair[0]!r} != {pair[1]!r}')
    for field in ('live_delta_id', 'revision', 'publication_mode', 'source_dirty', 'baseline_id', 'baseline_revision',
                  'revision_distance_from_baseline', 'current_live_revision_fully_verified', 'requires_new_full_verification'):
        live_field = 'source_revision' if field == 'revision' else field
        if live.get(live_field) != current.get(field):
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Live-Zustand driftet im Weltmodell: {field}')
    distance = int(binding.get('source_revision')) - int(baseline.get('revision'))
    if live.get('revision_distance_from_baseline') != distance:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Live-Revisionsabstand ist falsch')
    if distance > 0 and live.get('requires_new_full_verification') is not True:
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Neuerer Live-Nachlauf verlangt keine neue Vollverifikation')
    return {
        'name': WORLD_MODEL,
        'verified_full_baseline_pointer': pointer_artifact,
        'verified_full_baseline': {
            **baseline_artifact,
            'baseline_id': baseline.get('baseline_id'),
            'revision': baseline.get('revision'),
            'verification_check_count': len(checks),
            'all_verification_checks_pass': True,
            'full_refresh': evidence['full_refresh'],
            'full_verification': evidence['full_verification'],
            'mutable_latest_aliases': baseline.get('mutable_latest_aliases'),
            'historical_binding_observation': baseline.get('historical_binding_observation'),
        },
        'current_live_state': current,
        'live_delta': {
            'path': str(live_path), 'bytes': len(live_raw), 'sha256': live_sha,
            'live_delta_id': live.get('live_delta_id'), 'revision': live.get('source_revision'),
            'baseline_id': live.get('baseline_id'), 'baseline_revision': live.get('baseline_revision'),
        },
        'readiness_semantics': model.get('readiness_semantics') or {},
        'child_easy_explanation': model.get('child_easy_explanation'),
    }


def gate_contract(*, verify_hashes: bool = True) -> dict[str, Any]:
    binding, manifest_sha, path = _load_binding()
    sources: dict[str, Any] = {}
    for key in ('path_index', 'term_index', 'relation_index', 'change_stream'):
        item = (binding.get('sources') or {}).get(key)
        if not isinstance(item, dict):
            raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Quelle fehlt in Bindung: {key}')
        sources[key] = _verify_source(key, item, verify_hashes=verify_hashes)
    world = _world_contract(binding, manifest_sha, path, verify_hashes=verify_hashes)
    return {
        'ok': True,
        'backend': 'OMEGA_LEAN_REFERENCE',
        'scope': 'OMEGA_READ_ONLY_MCP',
        'source_manifest': {'path': str(path), 'bytes': path.stat().st_size, 'sha256': manifest_sha},
        'source_manifest_sha256': manifest_sha,
        'source_revision': binding.get('source_revision'),
        'source_generated_utc': binding.get('source_generated_utc'),
        'source_datenstand': binding.get('source_datenstand'),
        'source_dirty': binding.get('source_dirty'),
        'publication_mode': binding.get('publication_mode'),
        'world_model': world['name'],
        'verified_full_baseline_pointer': world['verified_full_baseline_pointer'],
        'verified_full_baseline': world['verified_full_baseline'],
        'current_live_state': world['current_live_state'],
        'live_delta': world['live_delta'],
        'readiness_semantics': world['readiness_semantics'],
        'child_easy_explanation': world['child_easy_explanation'],
        'sources': sources,
        'read_only': True,
        'raw_duplicate_bytes': 0,
        'small_snapshot_bytes': binding.get('small_snapshot_bytes'),
        'max_new_artifact_bytes': binding.get('max_new_artifact_bytes'),
        'einschraenkung': binding.get('einschraenkung'),
    }


def _same_generation(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if before['source_manifest_sha256'] != after['source_manifest_sha256']:
        return False
    if before['source_revision'] != after['source_revision']:
        return False
    for key in before['sources']:
        for field in ('path', 'bytes', 'mtime_ns', 'inode', 'sha256'):
            if before['sources'][key].get(field) != after['sources'][key].get(field):
                return False
    return True


def _with_generation(operation: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    before = gate_contract(verify_hashes=True)
    result = operation(before)
    after = gate_contract(verify_hashes=True)
    if not _same_generation(before, after):
        raise LeanOmegaError('UNKNOWN_SOURCE_DRIFT: Quellenmanifest oder Quellgeneration änderte sich während der Operation')
    result = dict(result)
    result.update({
        'backend': 'OMEGA_LEAN_REFERENCE',
        'source_manifest_sha256': before['source_manifest_sha256'],
        'source_revision': before['source_revision'],
        'source_generated_utc': before['source_generated_utc'],
        'source_datenstand': before['source_datenstand'],
        'source_dirty': before['source_dirty'],
        'publication_mode': before['publication_mode'],
        'world_model': before['world_model'],
        'verified_full_baseline': before['verified_full_baseline'],
        'current_live_state': before['current_live_state'],
        'live_delta': before['live_delta'],
        'readiness_semantics': before['readiness_semantics'],
        'child_easy_explanation': before['child_easy_explanation'],
        'source_hash_verification': {key: value['hash_verification'] for key, value in before['sources'].items()},
        'raw_duplicate_bytes': 0,
    })
    return result


def _connect_ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA query_only=ON')
    return con


def _encode_object_id(path: str) -> str:
    return OBJECT_PREFIX + base64.urlsafe_b64encode(path.encode('utf-8')).decode('ascii').rstrip('=')


def _decode_object_id(value: str) -> str:
    if not value.startswith(OBJECT_PREFIX):
        return value
    token = value[len(OBJECT_PREFIX):] + '=' * ((4 - len(value[len(OBJECT_PREFIX):]) % 4) % 4)
    try:
        return base64.urlsafe_b64decode(token.encode('ascii')).decode('utf-8')
    except Exception as exc:
        raise LeanOmegaError('Ungültige Lean-Objekt-ID') from exc


def _path_row(path_or_object: str, contract: dict[str, Any]) -> sqlite3.Row:
    path = str(Path(_decode_object_id(path_or_object)))
    with _connect_ro(Path(contract['sources']['path_index']['path'])) as con:
        row = con.execute('SELECT * FROM paths WHERE path=? LIMIT 1', (path,)).fetchone()
    if not row:
        raise LeanOmegaError(f'object/path not found: {path_or_object}')
    if row['excluded_reason']:
        raise LeanOmegaError(f'Pfad ist bewusst ausgeschlossen: {path}: {row["excluded_reason"]}')
    return row


def _current_stat(row: sqlite3.Row) -> tuple[Path, os.stat_result]:
    path = Path(str(row['path']))
    if not path.exists() or not path.is_file():
        raise LeanOmegaError(f'Original fehlt aktuell oder ist keine Datei: {path}')
    if path.is_symlink() or int(row['is_symlink']):
        raise LeanOmegaError(f'Symlink-Originalzugriff ist gesperrt: {path}')
    st = path.stat()
    if st.st_size != int(row['size'] or 0) or st.st_mtime_ns != int(row['mtime_ns'] or 0):
        raise LeanOmegaError(f'UNKNOWN_SOURCE_DRIFT: Original driftet seit Atlasindex: {path}')
    return path, st


def _version_id(path: str, size: int, mtime_ns: int) -> str:
    return 'leanver_' + hashlib.sha256(f'{path}\0{size}\0{mtime_ns}'.encode('utf-8')).hexdigest()[:40]


def _iso_from_ns(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1_000_000_000, tz=dt.timezone.utc).isoformat()


def _decode_bytes(raw: bytes) -> tuple[str, str, int]:
    try:
        return raw.decode('utf-8'), 'utf-8', 0
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='replace')
        return text, 'utf-8-replacement', text.count('\ufffd')


def _find_offsets(path: Path, needle: bytes, *, max_offsets: int = 64) -> list[int]:
    if not needle:
        return []
    offsets: list[int] = []
    overlap = max(0, len(needle) - 1)
    absolute = 0
    previous = b''
    with path.open('rb') as handle:
        while len(offsets) < max_offsets:
            block = handle.read(1024 * 1024)
            if not block:
                break
            data = previous + block
            base = absolute - len(previous)
            pos = 0
            while len(offsets) < max_offsets:
                found = data.find(needle, pos)
                if found < 0:
                    break
                value = base + found
                if value >= 0 and (not offsets or value != offsets[-1]):
                    offsets.append(value)
                pos = found + 1
            absolute += len(block)
            previous = data[-overlap:] if overlap else b''
    return offsets


def _fts_candidates(query: str, contract: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    phrase = '"' + query.replace('"', '""') + '"'
    sql = """SELECT rowid,path,title,headings,snippet(documents,3,'⟦','⟧',' … ',32) AS snippet,bm25(documents) AS score
             FROM documents WHERE documents MATCH ? ORDER BY score LIMIT ?"""
    with _connect_ro(Path(contract['sources']['term_index']['path'])) as con:
        try:
            rows = con.execute(sql, (phrase, limit)).fetchall()
        except sqlite3.Error:
            rows = con.execute(sql, (query, limit)).fetchall()
    return [dict(row) for row in rows]


def _metadata_rows(paths: Iterable[str], contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    unique = list(dict.fromkeys(paths))
    result: dict[str, dict[str, Any]] = {}
    if not unique:
        return result
    with _connect_ro(Path(contract['sources']['path_index']['path'])) as con:
        for start in range(0, len(unique), 400):
            part = unique[start:start + 400]
            placeholders = ','.join('?' for _ in part)
            for row in con.execute(f'SELECT * FROM paths WHERE path IN ({placeholders})', part):
                result[str(row['path'])] = dict(row)
    return result


def _path_name_candidates(query: str, contract: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    escaped = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    with _connect_ro(Path(contract['sources']['path_index']['path'])) as con:
        rows = con.execute(
            """SELECT path,basename,root_name,root_path,kind,is_dir,is_symlink,size,mtime_ns,suffix,parent,markers_json,excluded_reason
               FROM paths WHERE excluded_reason IS NULL AND (basename LIKE ? ESCAPE '\\' OR path LIKE ? ESCAPE '\\')
               ORDER BY is_dir,length(path),path LIMIT ?""",
            (f'%{escaped}%', f'%{escaped}%', limit),
        ).fetchall()
    return [dict(row) for row in rows]


def search_full(query: str, *, limit: int = 40, include_historic: bool = False) -> dict[str, Any]:
    query = str(query).strip()
    if not query:
        raise LeanOmegaError('query darf nicht leer sein')
    limit = max(1, min(int(limit), 100))
    def operation(contract: dict[str, Any]) -> dict[str, Any]:
        candidates = _fts_candidates(query, contract, min(limit * 8, 800))
        metadata = _metadata_rows((str(item['path']) for item in candidates), contract)
        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        needle = query.encode('utf-8')
        budget = MAX_EXACT_TOTAL_BYTES
        for candidate in candidates:
            path_text = str(candidate['path'])
            row = metadata.get(path_text)
            if not row or row.get('excluded_reason') or row.get('is_dir') or row.get('is_symlink'):
                continue
            path = Path(path_text)
            if not path.is_file():
                continue
            size = int(row.get('size') or 0)
            offsets: list[int] = []
            scan_status = 'SKIPPED_SIZE_GUARD'
            if size <= MAX_EXACT_FILE_BYTES and size <= budget:
                offsets = _find_offsets(path, needle)
                budget -= size
                scan_status = 'EXACT_UTF8_BYTES_SCANNED'
            results.append({
                'score': candidate.get('score'), 'snippet': candidate.get('snippet'), 'title': candidate.get('title'),
                'headings': candidate.get('headings'), 'path': path_text, 'source_path': path_text,
                'object_id': _encode_object_id(path_text), 'root_name': row.get('root_name'), 'root_path': row.get('root_path'),
                'kind': row.get('kind'), 'size': size, 'mtime_ns': row.get('mtime_ns'),
                'match_byte_offsets': offsets, 'first_match_byte': offsets[0] if offsets else None,
                'exact_literal_match_count': len(offsets), 'exact_scan_status': scan_status, 'storage_mode': 'REFERENCE_ONLY',
            })
            seen.add(path_text)
            if len(results) >= limit:
                break
        if len(results) < limit:
            for row in _path_name_candidates(query, contract, limit * 2):
                path_text = str(row['path'])
                if path_text in seen:
                    continue
                results.append({
                    'score': None, 'snippet': f'Pfadtreffer: {path_text}', 'title': row.get('basename'), 'headings': '',
                    'path': path_text, 'source_path': path_text, 'object_id': _encode_object_id(path_text),
                    'root_name': row.get('root_name'), 'root_path': row.get('root_path'), 'kind': row.get('kind'),
                    'size': row.get('size'), 'mtime_ns': row.get('mtime_ns'), 'match_byte_offsets': [],
                    'first_match_byte': None, 'exact_literal_match_count': 0, 'exact_scan_status': 'PATH_NAME_MATCH',
                    'storage_mode': 'REFERENCE_ONLY',
                })
                if len(results) >= limit:
                    break
        return {'ok': True, 'query': query, 'include_historic': bool(include_historic), 'historic_supported': False,
                'result_count': len(results), 'results': results, 'exact_scan_total_budget_bytes': MAX_EXACT_TOTAL_BYTES}
    return _with_generation(operation)


def _current_version(row: sqlite3.Row, st: os.stat_result) -> dict[str, Any]:
    path = str(row['path'])
    return {
        'version_id': _version_id(path, st.st_size, st.st_mtime_ns), 'object_id': _encode_object_id(path), 'epoch': 1,
        'created_utc': _iso_from_ns(st.st_mtime_ns), 'source_path': path, 'size': st.st_size, 'mtime_ns': st.st_mtime_ns,
        'file_sha256': None, 'content_fingerprint': hashlib.sha256(f'{st.st_size}:{st.st_mtime_ns}'.encode()).hexdigest(),
        'encoding': 'ON_DEMAND', 'decode_errors': 0, 'chunk_count': 0, 'complete': 1,
        'change_kind': 'CURRENT_REFERENCE', 'storage_mode': 'REFERENCE_ONLY',
    }


def _relations_for_path(path: str, contract: dict[str, Any], limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with _connect_ro(Path(contract['sources']['relation_index']['path'])) as con:
        nodes = con.execute('SELECT * FROM nodes WHERE path=?', (path,)).fetchall()
        if not nodes:
            return [], []
        ids = [str(row['node_id']) for row in nodes]
        placeholders = ','.join('?' for _ in ids)
        out_rows = con.execute(f'SELECT * FROM edges WHERE source_node_id IN ({placeholders}) LIMIT ?', (*ids, limit)).fetchall()
        in_rows = con.execute(f'SELECT * FROM edges WHERE target_node_id IN ({placeholders}) LIMIT ?', (*ids, limit)).fetchall()
    return [dict(row) for row in out_rows], [dict(row) for row in in_rows]


def _events_for_path(path: str, contract: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with Path(contract['sources']['change_stream']['path']).open('r', encoding='utf-8', errors='replace') as handle:
        for line_number, line in enumerate(handle, 1):
            if path not in line:
                continue
            try: value = json.loads(line)
            except json.JSONDecodeError: value = {'raw_line': line.rstrip('\n')}
            events.append({'line_number': line_number, 'event': value})
            if len(events) > limit:
                events.pop(0)
    return events


def object_view(path_or_object: str, *, edge_limit: int = 100, version_limit: int = 100) -> dict[str, Any]:
    def operation(contract: dict[str, Any]) -> dict[str, Any]:
        row = _path_row(path_or_object, contract)
        path, st = _current_stat(row)
        version = _current_version(row, st)
        edges_out, edges_in = _relations_for_path(str(path), contract, max(1, min(edge_limit, 500)))
        object_id = _encode_object_id(str(path))
        obj = {'object_id': object_id, 'identity_kind': 'PATH_REFERENCE', 'device': st.st_dev, 'inode': st.st_ino,
               'first_seen_utc': None, 'last_seen_utc': _iso_from_ns(st.st_mtime_ns), 'current_primary_path': str(path),
               'current_version_id': version['version_id'], 'deleted': 0, 'storage_mode': 'REFERENCE_ONLY'}
        record = dict(row)
        record.update({'object_id': object_id, 'exists_flag': 1, 'last_seen_utc': _iso_from_ns(st.st_mtime_ns), 'storage_mode': 'REFERENCE_ONLY'})
        return {'ok': True, 'object': obj, 'paths': [record], 'versions': [version][:max(1, min(version_limit, 500))],
                'edges_out': edges_out, 'edges_in': edges_in, 'events': _events_for_path(str(path), contract, 100)}
    return _with_generation(operation)


def read_original(path_or_object: str, *, version_id: str | None = None, start_byte: int = 0, max_bytes: int = 65536) -> dict[str, Any]:
    def operation(contract: dict[str, Any]) -> dict[str, Any]:
        row = _path_row(path_or_object, contract)
        path, st = _current_stat(row)
        version = _current_version(row, st)
        if version_id and version_id != version['version_id']:
            raise LeanOmegaError('Lean-Backend besitzt nur die aktuell gebundene Version')
        start = max(0, int(start_byte)); amount = max(1, min(int(max_bytes), 1024 * 1024))
        with path.open('rb') as handle:
            handle.seek(start); raw = handle.read(amount)
        text, encoding, errors = _decode_bytes(raw)
        file_sha = _sha256_file(path) if st.st_size <= MAX_FULL_HASH_BYTES else None
        return {'ok': True, 'object_id': _encode_object_id(str(path)), 'version_id': version['version_id'], 'epoch': 1,
                'source_path': str(path), 'total_bytes': st.st_size, 'start_byte': start, 'end_byte': start + len(raw),
                'returned_bytes': len(raw), 'has_more': start + len(raw) < st.st_size,
                'next_start_byte': start + len(raw) if start + len(raw) < st.st_size else None,
                'range_sha256': _sha256_bytes(raw), 'content_fingerprint': version['content_fingerprint'],
                'file_sha256': file_sha, 'file_sha256_status': 'COMPUTED_ON_DEMAND' if file_sha else 'NOT_COMPUTED_SIZE_GUARD',
                'stored_encoding': None, 'encoding': encoding, 'decode_error_count': errors,
                'raw_base64': base64.b64encode(raw).decode('ascii'), 'text': text,
                'direct_source_read': True, 'stored_copy': False}
    return _with_generation(operation)


def timeline(path_or_object: str, *, limit: int = 200) -> dict[str, Any]:
    def operation(contract: dict[str, Any]) -> dict[str, Any]:
        row = _path_row(path_or_object, contract)
        path, st = _current_stat(row)
        version = _current_version(row, st)
        amount = max(1, min(int(limit), 1000))
        return {'ok': True, 'object_id': _encode_object_id(str(path)), 'versions': [version],
                'path_history': [{'path': str(path), 'first_seen_utc': None, 'last_seen_utc': _iso_from_ns(st.st_mtime_ns),
                                  'exists_flag': 1, 'last_scan_id': 'CURRENT_GESAMTATLAS_REFERENCE'}],
                'events': _events_for_path(str(path), contract, amount),
                'timeline_scope': 'CURRENT_INDEX_PLUS_BOUND_CHANGE_STREAM_SNAPSHOT', 'historic_raw_versions_stored': False}
    return _with_generation(operation)


def health(*, verify_hashes: bool = True) -> dict[str, Any]:
    def operation(contract: dict[str, Any]) -> dict[str, Any]:
        counts: dict[str, int] = {}; checks: dict[str, str] = {}
        for key, tables in (('path_index', ('paths', 'root_summary')), ('term_index', ('documents',)), ('relation_index', ('nodes', 'edges'))):
            with _connect_ro(Path(contract['sources'][key]['path'])) as con:
                checks[key] = str(con.execute('PRAGMA quick_check').fetchone()[0])
                for table in tables:
                    counts[f'{key}.{table}'] = int(con.execute(f'SELECT count(*) FROM {table}').fetchone()[0])
        with _connect_ro(Path(contract['sources']['path_index']['path'])) as con:
            summary = con.execute('SELECT count(*) roots,sum(file_count) files,sum(directory_count) directories,sum(byte_count) bytes,sum(error_count) errors FROM root_summary').fetchone()
            root_summary = dict(summary) if summary else {}
            excluded = int(con.execute("SELECT count(*) FROM paths WHERE excluded_reason IS NOT NULL AND excluded_reason<>''").fetchone()[0])
        all_ok = all(value == 'ok' for value in checks.values()) and int(root_summary.get('errors') or 0) == 0
        return {'ok': all_ok, 'status': 'READY' if all_ok else 'DEGRADED', 'integrity': 'ok' if all_ok else 'error',
                'checks': checks, 'counts': counts, 'root_summary': root_summary, 'excluded_paths': excluded,
                'database': {'path': contract['sources']['path_index']['path'], 'bytes': contract['sources']['path_index']['bytes'],
                             'backend': 'REFERENCE_SET', 'sources': contract['sources']},
                'binding_hash_verified_now': bool(verify_hashes), 'read_only': True, 'einschraenkung': contract['einschraenkung']}
    return _with_generation(operation)


__all__ = ['LeanOmegaError', 'gate_contract', 'search_full', 'object_view', 'read_original', 'timeline', 'health']
