#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Any

ATLAS = Path('/root/werkraum/_gpt/gesamtatlas')
OMEGA = ATLAS / 'omega'
SOURCE_ROOT = OMEGA / 'lean_sources'
BINDING = OMEGA / 'OMEGA_LEAN_BINDING.json'
BASELINE = OMEGA / 'VERIFIED_FULL_BASELINE.json'
VERIFIED_BASELINES_ROOT = OMEGA / 'verified_full_baselines'
LIVE_DELTA = OMEGA / 'LIVE_DELTA_STATE.json'
PATH_INDEX = ATLAS / 'PFADINDEX.sqlite'
TERM_INDEX = ATLAS / 'BEGRIFFSINDEX.sqlite'
RELATION_LIVE = ATLAS / 'BEZIEHUNGSREGISTER.sqlite'
CHANGE_LIVE = ATLAS / 'AENDERUNGSSTROM.jsonl'
RELATION_SNAPSHOT = SOURCE_ROOT / 'BEZIEHUNGSREGISTER.snapshot.sqlite'
CHANGE_SNAPSHOT = SOURCE_ROOT / 'AENDERUNGSSTROM.snapshot.jsonl'
FULL_REFRESH = ATLAS / 'runtime/last_full_refresh.json'
FULL_VERIFICATION = ATLAS / 'runtime/last_full_verification.json'
MAX_NEW_ARTIFACT_BYTES = 128 * 1024 * 1024
WORLD_MODEL = 'VERIFIED_FULL_BASELINE_PLUS_VISIBLE_LIVE_DELTA'
HISTORICAL_BINDING_SHA_BY_REVISION = {
    3710: '432a5efac99b75612371f7008020d7ce4e5529412b06c1f2c9c9b610c5ad19f6',
}


class PublishError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def file_ref(path: Path, **extra: Any) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise PublishError(f'Beleg fehlt oder ist Symlink: {path}')
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path), **extra}


def stat_signature(path: Path) -> dict[str, int]:
    st = path.stat()
    return {'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns, 'inode': st.st_ino}


def stable_sha256(path: Path, *, attempts: int = 4) -> tuple[str, dict[str, int]]:
    for _ in range(attempts):
        before = stat_signature(path)
        digest = sha256(path)
        after = stat_signature(path)
        if before == after:
            return digest, after
        time.sleep(0.15)
    raise PublishError(f'Quelle änderte sich während SHA-256-Lesung: {path}')


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    raw = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_copy_exact(source: Path, target: Path) -> None:
    raw = source.read_bytes()
    if target.exists():
        if target.is_symlink() or target.read_bytes() != raw:
            raise PublishError(f'Versiegelter Evidence-Körper driftet: {target}')
        return
    atomic_write_bytes(target, raw)
    if target.read_bytes() != raw:
        raise PublishError(f'Atomare Evidence-Kopie ist nicht bytegleich: {source} -> {target}')


def baseline_paths(revision: int) -> dict[str, Path]:
    root = VERIFIED_BASELINES_ROOT / str(revision)
    evidence = root / 'evidence'
    return {
        'root': root,
        'baseline': root / f'FULL_BASELINE_{revision}.json',
        'refresh': evidence / f'FULL_REFRESH_{revision}.json',
        'verification': evidence / f'FULL_VERIFICATION_{revision}.json',
    }


def write_baseline_pointer(baseline: dict[str, Any], baseline_path: Path) -> dict[str, Any]:
    pointer = {
        'schema_version': '1.0',
        'pointer_class': 'CURRENT_VERIFIED_BASELINE_POINTER',
        'status': 'CURRENT_VERIFIED_BASELINE_POINTER',
        'world_model': WORLD_MODEL,
        'baseline_id': baseline['baseline_id'],
        'revision': baseline['revision'],
        'target': file_ref(
            baseline_path,
            baseline_id=baseline['baseline_id'],
            revision=baseline['revision'],
            status=baseline['status'],
        ),
        'einschraenkung': 'Kleiner kanonischer Zeiger. Der vollständige Grundstand und seine unveränderlichen Belege liegen ausschließlich im revisionsgebundenen Zielordner.',
    }
    atomic_json(BASELINE, pointer)
    return pointer


def resolve_baseline_pointer() -> tuple[dict[str, Any], Path, dict[str, Any]]:
    pointer = read_json(BASELINE)
    if pointer.get('pointer_class') != 'CURRENT_VERIFIED_BASELINE_POINTER' or pointer.get('status') != 'CURRENT_VERIFIED_BASELINE_POINTER':
        raise PublishError('VERIFIED_FULL_BASELINE.json ist kein gültiger kleiner Pointer')
    target = pointer.get('target') or {}
    path = Path(str(target.get('path') or '')).resolve()
    expected_root = (VERIFIED_BASELINES_ROOT / str(pointer.get('revision'))).resolve()
    try:
        path.relative_to(expected_root)
    except ValueError as exc:
        raise PublishError(f'Baseline-Pointer verlässt revisionsgebundenen Ordner: {path}') from exc
    if not path.is_file() or path.is_symlink():
        raise PublishError(f'Baseline-Pointerziel fehlt oder ist Symlink: {path}')
    if path.stat().st_size != target.get('bytes') or sha256(path) != target.get('sha256'):
        raise PublishError('Baseline-Pointerziel driftet in Bytezahl oder SHA-256')
    baseline = read_json(path)
    if baseline.get('baseline_id') != pointer.get('baseline_id') or baseline.get('revision') != pointer.get('revision'):
        raise PublishError('Baseline-Pointer und Ziel widersprechen sich')
    return baseline, path, pointer


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise PublishError(f'JSON ist kein Objekt: {path}')
    return value


def snapshot_sqlite_relation_projection(source: Path, target: Path, *, attempts: int = 4) -> dict[str, Any]:
    """Baut den pfadzentrierten Lean-Ring aus dem vollständigen Beziehungsgraphen.

    Vollständige Live-Wahrheit bleibt `source`. Die kleine Momentaufnahme enthält
    alle pfadtragenden Knoten außer dem Wesen-Hauptknoten, ihre direkten Nachbarn
    und alle Kanten innerhalb dieses einen Rings. So bleiben Datei-, Projekt-,
    Vault- und Zielgedankenbeziehungen nutzbar, ohne pfadlose Massenspeicher wie
    alle GENI-Knoten ein zweites Mal zu kopieren.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    for _attempt in range(attempts):
        before = stat_signature(source)
        fd, tmp_name = tempfile.mkstemp(prefix=f'.{target.name}.', dir=target.parent)
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            tmp.unlink(missing_ok=True)
            src = sqlite3.connect(f'file:{source.as_posix()}?mode=ro', uri=True, timeout=120)
            dst = sqlite3.connect(tmp, timeout=120)
            try:
                dst.execute('PRAGMA journal_mode=OFF')
                dst.execute('PRAGMA synchronous=OFF')
                for table in ('nodes', 'edges'):
                    schema = src.execute(
                        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                        (table,),
                    ).fetchone()
                    if not schema or not schema[0]:
                        raise PublishError(f'Relationsquelle besitzt Tabelle nicht: {table}')
                    dst.execute(schema[0])

                src.execute('CREATE TEMP TABLE keep_nodes(node_id TEXT PRIMARY KEY) WITHOUT ROWID')
                src.execute(
                    "INSERT INTO keep_nodes "
                    "SELECT node_id FROM nodes "
                    "WHERE path IS NOT NULL AND path<>'' AND node_type<>'wesen'"
                )
                src.execute(
                    """
                    INSERT OR IGNORE INTO keep_nodes
                    SELECT CASE
                        WHEN e.source_node_id IN (SELECT node_id FROM keep_nodes)
                        THEN e.target_node_id ELSE e.source_node_id END
                    FROM edges e
                    WHERE e.source_node_id IN (SELECT node_id FROM keep_nodes)
                       OR e.target_node_id IN (SELECT node_id FROM keep_nodes)
                    """
                )
                kept_nodes = int(src.execute('SELECT count(*) FROM keep_nodes').fetchone()[0])

                node_columns = int(src.execute("PRAGMA table_info('nodes')").fetchall().__len__())
                edge_columns = int(src.execute("PRAGMA table_info('edges')").fetchall().__len__())
                node_marks = ','.join('?' for _ in range(node_columns))
                edge_marks = ','.join('?' for _ in range(edge_columns))

                cursor = src.execute(
                    'SELECT n.* FROM nodes n JOIN keep_nodes k ON k.node_id=n.node_id ORDER BY n.node_id'
                )
                while True:
                    rows = cursor.fetchmany(5000)
                    if not rows:
                        break
                    dst.executemany(f'INSERT INTO nodes VALUES({node_marks})', rows)

                cursor = src.execute(
                    """
                    SELECT e.* FROM edges e
                    JOIN keep_nodes s ON s.node_id=e.source_node_id
                    JOIN keep_nodes t ON t.node_id=e.target_node_id
                    ORDER BY e.edge_id
                    """
                )
                kept_edges = 0
                while True:
                    rows = cursor.fetchmany(5000)
                    if not rows:
                        break
                    dst.executemany(f'INSERT INTO edges VALUES({edge_marks})', rows)
                    kept_edges += len(rows)

                for (index_sql,) in src.execute(
                    "SELECT sql FROM sqlite_master "
                    "WHERE type='index' AND sql IS NOT NULL AND tbl_name IN ('nodes','edges') "
                    "ORDER BY name"
                ):
                    dst.execute(index_sql)
                dst.commit()
                check = dst.execute('PRAGMA quick_check').fetchone()[0]
                if check != 'ok':
                    raise PublishError(f'Lean-Relationsprojektion nicht intakt: {check}')
                node_types = {
                    str(row[0]): int(row[1])
                    for row in dst.execute('SELECT node_type,count(*) FROM nodes GROUP BY node_type')
                }
                relation_types = {
                    str(row[0]): int(row[1])
                    for row in dst.execute('SELECT relation,count(*) FROM edges GROUP BY relation')
                }
            finally:
                dst.close()
                src.close()

            after = stat_signature(source)
            if before != after:
                tmp.unlink(missing_ok=True)
                time.sleep(0.15)
                continue
            with tmp.open('rb') as handle:
                os.fsync(handle.fileno())
            os.replace(tmp, target)
            return {
                'projection_class': 'PATH_CENTRIC_ONE_HOP',
                'source_bytes': before['bytes'],
                'projected_bytes': target.stat().st_size,
                'projected_nodes': kept_nodes,
                'projected_edges': kept_edges,
                'node_type_counts': node_types,
                'relation_counts': relation_types,
                'excluded_mass_node_types': ['geni_knoten', 'gedanke_ohne_pfadnachbarschaft'],
                'truth_boundary': 'Vollständiger Graph bleibt Live-Quelle. Lean enthält den Pfad-Nachbarschaftsring, nicht alle pfadlosen Lebensereignisse.',
            }
        finally:
            tmp.unlink(missing_ok=True)
    raise PublishError(f'Beziehungsquelle blieb während Lean-Projektion nicht stabil: {source}')


def snapshot_append_only(source: Path, target: Path, *, attempts: int = 6) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(attempts):
        before = stat_signature(source)
        fd, tmp_name = tempfile.mkstemp(prefix=f'.{target.name}.', dir=target.parent)
        tmp = Path(tmp_name)
        try:
            remaining = before['bytes']
            with source.open('rb') as src, os.fdopen(fd, 'wb') as dst:
                while remaining:
                    block = src.read(min(1024 * 1024, remaining))
                    if not block:
                        raise PublishError(f'Änderungsstrom vor erwarteter Größe beendet: {source}')
                    dst.write(block)
                    remaining -= len(block)
                dst.flush()
                os.fsync(dst.fileno())
            after = stat_signature(source)
            if before == after and tmp.stat().st_size == before['bytes']:
                os.replace(tmp, target)
                return
        finally:
            tmp.unlink(missing_ok=True)
        time.sleep(0.1)
    raise PublishError(f'Änderungsstrom blieb während Momentaufnahme nicht stabil: {source}')


def previous_source(key: str) -> dict[str, Any] | None:
    if not BINDING.is_file():
        return None
    try:
        previous = read_json(BINDING)
        item = (previous.get('sources') or {}).get(key)
        return item if isinstance(item, dict) else None
    except Exception:
        return None


def source_entry(key: str, path: Path, *, original_path: Path | None = None, permit_reuse: bool = False) -> dict[str, Any]:
    signature = stat_signature(path)
    digest: str | None = None
    reused = False
    if permit_reuse:
        previous = previous_source(key)
        if previous:
            comparable = {name: int(previous.get(name, -1)) for name in ('bytes', 'mtime_ns', 'inode')}
            if comparable == signature and str(previous.get('path')) == str(path) and previous.get('sha256'):
                digest = str(previous['sha256'])
                reused = True
    if digest is None:
        digest, signature = stable_sha256(path)
    return {
        'key': key,
        'path': str(path),
        'original_path': str(original_path or path),
        **signature,
        'sha256': digest,
        'hash_reused_from_previous_binding': reused,
        'storage_mode': 'LIVE_REFERENCE' if original_path is None else 'ATOMIC_SMALL_SNAPSHOT',
    }


def _full_pair() -> tuple[Path, dict[str, Any], Path, dict[str, Any]]:
    refresh = read_json(FULL_REFRESH)
    verification = read_json(FULL_VERIFICATION)
    status = refresh.get('status') or {}
    revision = status.get('revision')
    checks = verification.get('checks') or {}
    if not (
        refresh.get('ok') is True
        and status.get('mode') == 'full'
        and status.get('dirty') is False
        and verification.get('ok') is True
        and verification.get('verified_revision') == revision
        and checks
        and all(checks.values())
    ):
        raise PublishError('Letzter Full-Grundstand ist nicht vollständig verifiziert')
    return FULL_REFRESH, refresh, FULL_VERIFICATION, verification


def build_baseline() -> tuple[dict[str, Any], Path]:
    refresh_path, refresh, verification_path, verification = _full_pair()
    status = refresh.get('status') or {}
    revision = int(status['revision'])
    baseline_id = f'omega-verified-full-r{revision}'
    checks = verification.get('checks') or {}
    paths = baseline_paths(revision)
    paths['root'].mkdir(parents=True, exist_ok=True)
    atomic_copy_exact(refresh_path, paths['refresh'])
    atomic_copy_exact(verification_path, paths['verification'])
    immutable_refresh = read_json(paths['refresh'])
    immutable_verification = read_json(paths['verification'])
    immutable_status = immutable_refresh.get('status') or {}
    if not (
        immutable_refresh.get('ok') is True
        and immutable_status.get('revision') == revision
        and immutable_status.get('mode') == 'full'
        and immutable_status.get('dirty') is False
        and immutable_verification.get('ok') is True
        and immutable_verification.get('verified_revision') == revision
        and len(immutable_verification.get('checks') or {}) == len(checks)
        and all((immutable_verification.get('checks') or {}).values())
    ):
        raise PublishError('Revisionsgebundene Full-Evidence ist nicht vollständig verifiziert')
    historical_sha = HISTORICAL_BINDING_SHA_BY_REVISION.get(revision)
    historical = None
    if historical_sha:
        historical = {
            'observed_sha256': historical_sha,
            'bytes_retained': False,
            'byte_artifact_preserved': False,
            'byte_identity_reconstructed': False,
            'classification': 'PROVENANCE_ONLY_OBSERVATION',
            'einschraenkung': 'Der Hash wurde am damaligen Full/clean-Livebinding beobachtet. Die historischen Binding-Bytes wurden nicht erhalten und werden nicht rekonstruiert.',
        }
    existing = read_json(paths['baseline']) if paths['baseline'].is_file() else None
    created_utc = existing.get('created_utc') if existing else utc_now()
    baseline = {
        'schema_version': '3.1-owner',
        'world_model': WORLD_MODEL,
        'baseline_id': baseline_id,
        'status': 'VERIFIED_FULL_BASELINE',
        'revision': revision,
        'generated_utc': immutable_status.get('generated_utc'),
        'created_utc': created_utc,
        'mode': 'full',
        'dirty': False,
        'datenstand': immutable_status.get('datenstand'),
        'full_refresh': file_ref(paths['refresh'], role='immutable_primary_evidence', revision=revision),
        'full_verification': file_ref(paths['verification'], role='immutable_primary_evidence', verified_revision=revision),
        'verification': {
            'check_count': len(immutable_verification.get('checks') or {}),
            'passed': sum(bool(value) for value in (immutable_verification.get('checks') or {}).values()),
            'failed': [key for key, value in (immutable_verification.get('checks') or {}).items() if not value],
            'checks': immutable_verification.get('checks') or {},
            'counts': immutable_verification.get('counts') or {},
            'source_hashes': immutable_verification.get('hashes') or {},
            'post_snapshot_changes_present_at_verification': bool(immutable_verification.get('post_snapshot_changes_present')),
        },
        'mutable_latest_aliases': {
            'authoritative_for_baseline_3710': False if revision == 3710 else False,
            'authoritative_for_this_baseline': False,
            'paths_embedded_in_immutable_baseline': False,
            'classification': 'NON_AUTHORITATIVE_MOVING_LATEST_ALIASES',
            'einschraenkung': 'Bewegliche latest-Aliase existieren außerhalb dieses historischen Körpers. Ihre Pfade werden absichtlich nicht in die unveränderliche Baseline eingebettet.',
        },
        'historical_binding_observation': historical,
        'validity': {
            'kind': 'POINT_IN_TIME_VERIFIED_BASELINE',
            'remains_valid_after_later_deltas': True,
            'superseded_only_by_newer_verified_full_baseline': True,
            'current_live_state_may_be_newer': True,
        },
        'child_easy_explanation': 'Wir haben die ganze Karte bei diesem Stand vollständig geprüft. Spätere neue Zettel machen diese geprüfte Karte nicht rückwirkend falsch.',
        'einschraenkung': 'Owner-Grundstand mit revisionsgebundenen unveränderlichen Evidence-Bytes. Bewegliche runtime/last_full_*-Aliase bleiben sichtbar, sind aber für diesen Grundstand ausdrücklich nicht autoritativ.',
    }
    raw = (json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if paths['baseline'].exists():
        if paths['baseline'].read_bytes() != raw:
            raise PublishError(f'Versiegelter Full-Grundstand driftet: {paths["baseline"]}')
    else:
        atomic_write_bytes(paths['baseline'], raw)
    baseline = read_json(paths['baseline'])
    write_baseline_pointer(baseline, paths['baseline'])
    return baseline, paths['baseline']



def validate_baseline() -> tuple[dict[str, Any], Path]:
    if not BASELINE.is_file():
        return build_baseline()
    baseline, immutable, pointer = resolve_baseline_pointer()
    revision = int(baseline.get('revision'))
    expected = baseline_paths(revision)
    if immutable != expected['baseline'].resolve():
        raise PublishError('Pointer zeigt nicht auf den kanonischen revisionsgebundenen Grundstand')
    if baseline.get('world_model') != WORLD_MODEL or baseline.get('status') != 'VERIFIED_FULL_BASELINE':
        raise PublishError('Full-Grundstand besitzt falschen Weltvertrag')
    checks = ((baseline.get('verification') or {}).get('checks') or {})
    if not checks or not all(checks.values()):
        raise PublishError('Full-Grundstand enthält keine vollständige PASS-Verifikation')
    if (baseline.get('mutable_latest_aliases') or {}).get('authoritative_for_this_baseline') is not False:
        raise PublishError('Bewegliche latest-Aliase sind nicht ausdrücklich nicht-autoritativ')
    for key, expected_path in (('full_refresh', expected['refresh']), ('full_verification', expected['verification'])):
        ref = baseline.get(key) or {}
        path = Path(str(ref.get('path') or '')).resolve()
        if path != expected_path.resolve():
            raise PublishError(f'Full-Grundstand-Beleg ist nicht revisionsgebunden: {key}')
        if not path.is_file() or path.is_symlink() or path.stat().st_size != ref.get('bytes') or sha256(path) != ref.get('sha256'):
            raise PublishError(f'Full-Grundstand-Beleg driftet: {key}')
    return baseline, immutable



def live_state(revision: int, mode: str, dirty: bool, baseline: dict[str, Any]) -> dict[str, Any]:
    baseline_revision = int(baseline['revision'])
    distance = revision - baseline_revision
    current_verified = revision == baseline_revision and mode == 'full' and dirty is False
    return {
        'live_delta_id': f'omega-live-r{revision}',
        'revision': revision,
        'publication_mode': mode,
        'source_dirty': dirty,
        'baseline_id': baseline['baseline_id'],
        'baseline_revision': baseline_revision,
        'revision_distance_from_baseline': distance,
        'is_newer_than_verified_baseline': distance > 0,
        'current_live_revision_fully_verified': current_verified,
        'requires_new_full_verification': not current_verified,
        'meaning': 'NEWER_VISIBLE_LIVE_DELTA' if distance > 0 else 'CURRENT_STATE_EQUALS_VERIFIED_BASELINE',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Atomare Quellenbindung für Omega Lean Reference')
    parser.add_argument('--mode', choices=('light', 'full'), required=True)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--refresh-json', required=True)
    args = parser.parse_args()

    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    refresh_path = Path(args.refresh_json).resolve()
    refresh = read_json(refresh_path)
    status = refresh.get('status') or {}
    if refresh.get('ok') is not True:
        raise PublishError('Atlasrefresh ist nicht ok')
    if status.get('mode') != args.mode:
        raise PublishError(f'Refreshmodus driftet: {status.get("mode")} != {args.mode}')
    revision = status.get('revision')
    if revision is None:
        raise PublishError('Atlasrevision fehlt')
    revision = int(revision)

    verification_path = FULL_VERIFICATION
    verification: dict[str, Any] | None = read_json(verification_path) if verification_path.is_file() else None
    if args.mode == 'full':
        if status.get('dirty') is not False:
            raise PublishError('Vollsnapshot ist nicht sauber')
        if not verification or verification.get('ok') is not True:
            raise PublishError('Vollverifikation ist nicht PASS')
        if verification.get('verified_revision') != revision:
            raise PublishError('Vollverifikation gehört nicht zur Refreshrevision')
        baseline, baseline_path = build_baseline()
    else:
        baseline, baseline_path = validate_baseline()

    for source in (PATH_INDEX, TERM_INDEX, RELATION_LIVE, CHANGE_LIVE):
        if not source.is_file():
            raise PublishError(f'Lean-Quelle fehlt: {source}')

    relation_projection = snapshot_sqlite_relation_projection(RELATION_LIVE, RELATION_SNAPSHOT)
    snapshot_append_only(CHANGE_LIVE, CHANGE_SNAPSHOT)

    relation_source = source_entry('relation_index', RELATION_SNAPSHOT, original_path=RELATION_LIVE)
    relation_source['projection'] = relation_projection
    sources = {
        'path_index': source_entry('path_index', PATH_INDEX, permit_reuse=True),
        'term_index': source_entry('term_index', TERM_INDEX, permit_reuse=True),
        'relation_index': relation_source,
        'change_stream': source_entry('change_stream', CHANGE_SNAPSHOT, original_path=CHANGE_LIVE),
    }
    lean_artifact_bytes = RELATION_SNAPSHOT.stat().st_size + CHANGE_SNAPSHOT.stat().st_size
    if lean_artifact_bytes > MAX_NEW_ARTIFACT_BYTES:
        raise PublishError(f'Lean-Größenbudget überschritten: {lean_artifact_bytes} > {MAX_NEW_ARTIFACT_BYTES}')

    verification_ref = dict(baseline.get('full_verification') or {})

    baseline_ref = file_ref(
        baseline_path,
        baseline_id=baseline['baseline_id'],
        revision=baseline['revision'],
        status=baseline['status'],
    )
    current = live_state(revision, args.mode, bool(status.get('dirty')), baseline)
    if current['current_live_revision_fully_verified']:
        child_explanation = 'Die ganze Karte und der aktuelle sichtbare Stand wurden gemeinsam vollständig geprüft. Gerade liegt kein ungeprüfter Zettelstapel daneben.'
        delta_boundary = 'Dieser Körper beschreibt den aktuellen vollständig verifizierten Live-Stand. Er ist mit dem verifizierten Grundstand revisionsgleich und öffnet keine Ready-Freigabe.'
    else:
        child_explanation = 'Die ganze Karte wurde beim Grundstand vollständig geprüft. Danach kamen neue sichtbare Zettel dazu. Die Zettel brauchen später wieder eine neue Gesamtprüfung.'
        delta_boundary = 'Dieser Körper beschreibt den aktuellen Live-Nachlauf. Er ersetzt den verifizierten Grundstand nicht und behauptet bei light/dirty ausdrücklich keine vollständige Neuverifikation.'
    manifest = {
        'schema_version': '3.0',
        'backend': 'OMEGA_LEAN_REFERENCE',
        'status': 'PASS',
        'published_utc': utc_now(),
        'publication_mode': args.mode,
        'publication_reason': args.reason,
        'source_revision': revision,
        'source_generated_utc': status.get('generated_utc'),
        'source_datenstand': status.get('datenstand'),
        'source_dirty': bool(status.get('dirty')),
        'refresh': file_ref(refresh_path),
        'last_full_verification': verification_ref,
        'world_model': {
            'name': WORLD_MODEL,
            'verified_full_baseline': baseline_ref,
            'current_live_state': current,
            'readiness_semantics': {
                'verified_full_baseline_valid': True,
                'live_delta_mechanism_active': True,
                'current_live_revision_fully_verified': current['current_live_revision_fully_verified'],
                'new_full_verification_recommended': current['requires_new_full_verification'],
                'mcp_world_ready_may_bind_baseline_plus_delta': True,
            },
            'child_easy_explanation': child_explanation,
        },
        'verified_full_baseline': baseline_ref,
        'current_live_state': current,
        'live_delta_object': {'path': str(LIVE_DELTA), 'live_delta_id': current['live_delta_id']},
        'sources': sources,
        'raw_duplicate_bytes': 0,
        'small_snapshot_bytes': lean_artifact_bytes,
        'max_new_artifact_bytes': MAX_NEW_ARTIFACT_BYTES,
        'budget_ok': lean_artifact_bytes <= MAX_NEW_ARTIFACT_BYTES,
        'einschraenkung': 'Pfad- und Volltextindex bleiben Live-Referenzen. Das Beziehungsregister wird als pfadzentrierter Ein-Hop-Ring atomar projiziert; der vollständige Lebensgraph bleibt ausschließlich in der autoritativen Live-Quelle. Der Änderungsstrom bleibt eine atomare Momentaufnahme. Ein verifizierter Full-Grundstand bleibt als eigener Beleg erhalten; spätere Light-Revisionen werden getrennt als sichtbare Deltas ausgewiesen und niemals als vollständig verifiziert ausgegeben.',
    }
    atomic_json(BINDING, manifest)
    reread = read_json(BINDING)
    if reread.get('source_revision') != revision or reread.get('status') != 'PASS':
        raise PublishError('Atomare Bindungsrücklesung abweichend')

    delta = {
        'schema_version': '1.0',
        'world_model': WORLD_MODEL,
        'status': 'VISIBLE_LIVE_STATE',
        'generated_utc': utc_now(),
        **current,
        'live_revision': revision,
        'source_revision': revision,
        'baseline_manifest_sha256': baseline_ref['sha256'],
        'baseline_manifest_path': baseline_ref['path'],
        'verified_full_baseline': baseline_ref,
        'current_binding': file_ref(BINDING, source_revision=revision, publication_mode=args.mode),
        'latest_refresh': file_ref(refresh_path, revision=revision, mode=args.mode, dirty=bool(status.get('dirty'))),
        'child_easy_explanation': manifest['world_model']['child_easy_explanation'],
        'einschraenkung': delta_boundary,
    }
    atomic_json(LIVE_DELTA, delta)

    result = {
        'ok': True,
        'binding': file_ref(BINDING),
        'verified_full_baseline': file_ref(baseline_path, baseline_id=baseline['baseline_id'], revision=baseline['revision']),
        'live_delta': file_ref(LIVE_DELTA, live_delta_id=current['live_delta_id'], revision=revision),
        'source_revision': revision,
        'publication_mode': args.mode,
        'source_dirty': bool(status.get('dirty')),
        'current_live_revision_fully_verified': current['current_live_revision_fully_verified'],
        'requires_new_full_verification': current['requires_new_full_verification'],
        'small_snapshot_bytes': lean_artifact_bytes,
        'max_new_artifact_bytes': MAX_NEW_ARTIFACT_BYTES,
        'raw_duplicate_bytes': 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
