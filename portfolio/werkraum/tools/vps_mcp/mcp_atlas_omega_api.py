from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import mcp_atlas_omega as omega
import mcp_atlas_omega_lean as lean

CORE_READY_DEFAULT = Path('/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/CORE_READY.json')
MONSTERLAB_READY_DEFAULT = Path('/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/MONSTERLABOR_DYNAMIC_READY.json')
MCP_WORLD_READY_DEFAULT = Path('/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/MCP_WORLD_READY.json')
FINAL_SCAN_READY_DEFAULT = Path('/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/FINAL_SCAN_READY.json')


class OmegaAPIError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _json_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise OmegaAPIError(f'Pflichtmarker fehlt: {path}') from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise OmegaAPIError(f'Pflichtmarker unlesbar: {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise OmegaAPIError(f'Pflichtmarker ist kein Objekt: {path}')
    return value


def _checkpoint_contract() -> dict[str, Any]:
    core_path = Path(omega.__file__).resolve()
    core_ready_path = Path(os.environ.get('GESAMTATLAS_OMEGA_CORE_READY', str(CORE_READY_DEFAULT))).resolve()
    monsterlab_path = Path(os.environ.get('GESAMTATLAS_OMEGA_MONSTERLAB_READY', str(MONSTERLAB_READY_DEFAULT))).resolve()
    core_sha = _sha256_file(core_path)
    core_ready = _json_file(core_ready_path)
    monsterlab = _json_file(monsterlab_path)
    if core_ready.get('checkpoint_id') != 'CORE_READY' or core_ready.get('status') != 'PASS':
        raise OmegaAPIError('CORE_READY ist nicht PASS')
    if monsterlab.get('checkpoint_id') != 'MONSTERLABOR_DYNAMIC_READY' or monsterlab.get('status') != 'PASS':
        raise OmegaAPIError('MONSTERLABOR_DYNAMIC_READY ist nicht PASS')
    ready_core_sha = str((core_ready.get('core') or {}).get('sha256') or '')
    lab_core_sha = str((monsterlab.get('core') or {}).get('sha256') or '')
    if not ready_core_sha or core_sha != ready_core_sha or core_sha != lab_core_sha:
        raise OmegaAPIError(
            f'Omega-Core-Hashbindung verletzt: live={core_sha}, core_ready={ready_core_sha}, monsterlabor={lab_core_sha}'
        )
    core_ready_sha = _sha256_file(core_ready_path)
    expected_core_ready_sha = str((monsterlab.get('core_ready') or {}).get('sha256') or '')
    if not expected_core_ready_sha or core_ready_sha != expected_core_ready_sha:
        raise OmegaAPIError('CORE_READY-Hashbindung verletzt')
    return {
        'core': {'path': str(core_path), 'sha256': core_sha},
        'core_ready': {'path': str(core_ready_path), 'sha256': core_ready_sha},
        'monsterlabor_ready': {'path': str(monsterlab_path), 'sha256': _sha256_file(monsterlab_path)},
    }


def _optional_ready(path: Path, checkpoint_id: str) -> dict[str, Any]:
    path = path.resolve()
    if not path.exists():
        return {'ready': False, 'present': False, 'path': str(path), 'checkpoint_id': checkpoint_id}
    marker = _json_file(path)
    if marker.get('checkpoint_id') != checkpoint_id or marker.get('status') != 'PASS':
        raise OmegaAPIError(f'Ungültiger Ready-Marker: {checkpoint_id}: {path}')
    return {
        'ready': True, 'present': True, 'path': str(path), 'checkpoint_id': checkpoint_id,
        'bytes': path.stat().st_size, 'sha256': _sha256_file(path),
        'created_utc': marker.get('created_utc') or marker.get('generated_utc'),
    }


def _readiness_contract() -> dict[str, Any]:
    world = _optional_ready(
        Path(os.environ.get('GESAMTATLAS_OMEGA_MCP_WORLD_READY', str(MCP_WORLD_READY_DEFAULT))),
        'MCP_WORLD_READY',
    )
    final = _optional_ready(
        Path(os.environ.get('GESAMTATLAS_OMEGA_FINAL_SCAN_READY', str(FINAL_SCAN_READY_DEFAULT))),
        'FINAL_SCAN_READY',
    )
    if final['ready'] and not world['ready']:
        raise OmegaAPIError('FINAL_SCAN_READY darf nicht ohne MCP_WORLD_READY gelten')
    return {
        'mcp_world_ready': world['ready'], 'final_scan_ready': final['ready'],
        'ready_markers': {'mcp_world_ready': world, 'final_scan_ready': final},
    }


def _full_backend_requested() -> bool:
    return bool(str(os.environ.get('GESAMTATLAS_OMEGA_DB') or '').strip())


def _full_contract() -> dict[str, Any]:
    checkpoints = _checkpoint_contract()
    db_path = Path(str(os.environ.get('GESAMTATLAS_OMEGA_DB') or '')).resolve()
    if not db_path.is_file():
        raise OmegaAPIError(f'Omega-Datenbank fehlt: {db_path}')
    return {
        'ok': True,
        'backend': 'OMEGA_FULL_COPY_TEST_BACKEND',
        'scope': 'OMEGA_READ_ONLY_MCP',
        **checkpoints,
        'database': {'path': str(db_path), 'bytes': db_path.stat().st_size},
        'read_only': True,
        **_readiness_contract(),
        'einschraenkung': (
            'Expliziter GESAMTATLAS_OMEGA_DB-Pfad aktiviert ausschließlich '
            'den bestehenden Monsterlabor-/Kompatibilitätsbackend.'
        ),
    }


def _lean_contract_for_result(result: dict[str, Any]) -> dict[str, Any]:
    try:
        current = lean.gate_contract(verify_hashes=True)
    except lean.LeanOmegaError as exc:
        raise OmegaAPIError(str(exc)) from exc
    result_manifest = str(result.get('source_manifest_sha256') or '')
    result_revision = result.get('source_revision')
    if not result_manifest or result_manifest != current.get('source_manifest_sha256'):
        raise OmegaAPIError('UNKNOWN_SOURCE_DRIFT: API-Vertrag und Lean-Ergebnis gehören nicht zum selben Quellenmanifest')
    if result_revision != current.get('source_revision'):
        raise OmegaAPIError('UNKNOWN_SOURCE_DRIFT: API-Vertrag und Lean-Ergebnis gehören nicht zur selben Atlasrevision')
    return {
        **current,
        **_checkpoint_contract(),
        **_readiness_contract(),
    }


def gate() -> dict[str, Any]:
    if _full_backend_requested():
        return _full_contract()
    try:
        current = lean.gate_contract(verify_hashes=True)
    except lean.LeanOmegaError as exc:
        raise OmegaAPIError(str(exc)) from exc
    return {
        **current,
        **_checkpoint_contract(),
        **_readiness_contract(),
    }


def _with_contract(payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result['omega_contract'] = contract
    return result


def search(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get('query') or '').strip()
    if not query:
        raise OmegaAPIError('query darf nicht leer sein')
    if len(query) > 4096:
        raise OmegaAPIError('query ist zu lang')
    limit = max(1, min(int(args.get('limit', 40)), 100))
    historic = bool(args.get('include_historic', False))
    try:
        if _full_backend_requested():
            contract = _full_contract()
            result = omega.search_full(query, db_path=contract['database']['path'], limit=limit, include_historic=historic)
        else:
            result = lean.search_full(query, limit=limit, include_historic=historic)
            contract = _lean_contract_for_result(result)
    except (omega.OmegaError, lean.LeanOmegaError) as exc:
        raise OmegaAPIError(str(exc)) from exc
    return _with_contract(result, contract)


def object_view(args: dict[str, Any]) -> dict[str, Any]:
    value = str(args.get('path_or_object') or '').strip()
    if not value:
        raise OmegaAPIError('path_or_object darf nicht leer sein')
    edge_limit = max(1, min(int(args.get('edge_limit', 100)), 500))
    version_limit = max(1, min(int(args.get('version_limit', 100)), 500))
    try:
        if _full_backend_requested():
            contract = _full_contract()
            result = omega.object_view(
                value,
                db_path=contract['database']['path'],
                edge_limit=edge_limit,
                version_limit=version_limit,
            )
        else:
            result = lean.object_view(value, edge_limit=edge_limit, version_limit=version_limit)
            contract = _lean_contract_for_result(result)
    except (omega.OmegaError, lean.LeanOmegaError) as exc:
        raise OmegaAPIError(str(exc)) from exc
    return _with_contract(result, contract)


def read_original(args: dict[str, Any]) -> dict[str, Any]:
    value = str(args.get('path_or_object') or '').strip()
    if not value:
        raise OmegaAPIError('path_or_object darf nicht leer sein')
    version = str(args.get('version_id')) if args.get('version_id') else None
    start = max(0, int(args.get('start_byte', 0)))
    amount = max(1, min(int(args.get('max_bytes', 65536)), 262144))
    try:
        if _full_backend_requested():
            contract = _full_contract()
            result = omega.read_original(
                value,
                db_path=contract['database']['path'],
                version_id=version,
                start_byte=start,
                max_bytes=amount,
            )
        else:
            result = lean.read_original(value, version_id=version, start_byte=start, max_bytes=amount)
            contract = _lean_contract_for_result(result)
    except (omega.OmegaError, lean.LeanOmegaError) as exc:
        raise OmegaAPIError(str(exc)) from exc
    return _with_contract(result, contract)


def timeline(args: dict[str, Any]) -> dict[str, Any]:
    value = str(args.get('path_or_object') or '').strip()
    if not value:
        raise OmegaAPIError('path_or_object darf nicht leer sein')
    limit = max(1, min(int(args.get('limit', 200)), 1000))
    try:
        if _full_backend_requested():
            contract = _full_contract()
            result = omega.timeline(value, db_path=contract['database']['path'], limit=limit)
        else:
            result = lean.timeline(value, limit=limit)
            contract = _lean_contract_for_result(result)
    except (omega.OmegaError, lean.LeanOmegaError) as exc:
        raise OmegaAPIError(str(exc)) from exc
    return _with_contract(result, contract)


def health(args: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        if _full_backend_requested():
            contract = _full_contract()
            result = omega.health(db_path=contract['database']['path'])
        else:
            result = lean.health()
            contract = _lean_contract_for_result(result)
    except (omega.OmegaError, lean.LeanOmegaError) as exc:
        raise OmegaAPIError(str(exc)) from exc
    return _with_contract(result, contract)


__all__ = ['OmegaAPIError', 'gate', 'search', 'object_view', 'read_original', 'timeline', 'health']
