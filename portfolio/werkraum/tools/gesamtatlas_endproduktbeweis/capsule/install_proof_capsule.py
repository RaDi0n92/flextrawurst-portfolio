#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PROOF_ROOT = Path(os.environ.get('GA_PROOF_ROOT', '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis'))
CANONICAL = Path(os.environ.get('GA_CANONICAL_CAPSULE', '/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip'))
BASE_STORE = Path(os.environ.get('GA_BASE_STORE', str(PROOF_ROOT / 'KAPSEL/BASE_AKTUELL.zip')))
CANDIDATE = Path(os.environ.get('GA_CANDIDATE_CAPSULE', str(PROOF_ROOT / 'KAPSEL/GESAMTATLAS_KAPSEL_MIT_ENDPRODUKTBEWEIS.zip')))
BUILDER = Path(os.environ.get('GA_PROOF_BUILDER', '/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/build_proof_capsule.py'))
INSTALL_STATUS = Path(os.environ.get('GA_INSTALL_STATUS', str(PROOF_ROOT / 'KAPSEL/INSTALL_STATUS.json')))
BACKUP_ROOT = Path(os.environ.get('GA_INSTALL_BACKUP_ROOT', str(PROOF_ROOT / 'KAPSEL/INSTALL_BACKUPS')))
LOCK_PATH = Path(os.environ.get('GA_INSTALL_LOCK', str(PROOF_ROOT / 'KAPSEL/.install.lock')))
MAX_ZIP_BYTES = 25_000_000
REQUIRED = {
    '00_START_HIER.md',
    '01_ENDPRODUKTBEWEIS_START.md',
    'ENDPRODUKTBEWEIS/MANIFEST.json',
    'ENDPRODUKTBEWEIS/SHA256SUMS.txt',
    'ENDPRODUKTBEWEIS/ANFORDERUNGEN/ANFORDERUNGSREGISTER.jsonl',
    'ENDPRODUKTBEWEIS/MASCHINE/ANFORDERUNGSREGISTER.sqlite',
    'ENDPRODUKTBEWEIS/INTEGRATION/LLM_ABNAHME_AUFGABEN.json',
    'ENDPRODUKTBEWEIS/UI/index.html',
    'ENDPRODUKTBEWEIS/UI/ai-stroeme.html',
    'ENDPRODUKTBEWEIS/AI_STROEME/STATUS.json',
    'ENDPRODUKTBEWEIS/AI_STROEME/AI_STROEME.json',
    'ENDPRODUKTBEWEIS/AI_STROEME/AI_STROM_BRUECKEN.json',
    'ENDPRODUKTBEWEIS/UI/groessenwahrheit.html',
    'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/STATUS.json',
    'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/GROESSENWAHRHEIT.json',
    'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_START_HIER.md',
    'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_MANIFEST.json',
    'ENDPRODUKTBEWEIS/ERGAENZUNGEN/GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.json',
    'ENDPRODUKTBEWEIS/SCHLANKHEIT/SCHLANKHEITSAUDIT.json',
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{target.name}.', dir=target.parent)
    try:
        with source.open('rb') as src, os.fdopen(fd, 'wb') as dst:
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if sha256(source) != sha256(Path(temp_name)):
            raise RuntimeError(f'Kopierhash weicht ab: {source} -> {target}')
        os.replace(temp_name, target)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def zip_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f'ZIP beschädigt: {path}')
        name = 'ENDPRODUKTBEWEIS/MANIFEST.json'
        if name not in archive.namelist():
            return None
        return json.loads(archive.read(name))


def load_builder_module():
    spec = importlib.util.spec_from_file_location('ga_build_proof_capsule', BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Builder nicht importierbar: {BUILDER}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def proof_input_paths() -> list[Path]:
    module = load_builder_module()
    paths: list[Path] = [BUILDER, Path(__file__).resolve()]
    for source, _ in module.added_sources():
        paths.append(Path(source))
    paths.extend([
        PROOF_ROOT / 'ANFORDERUNGEN/ANFORDERUNGSREGISTER.sqlite',
        PROOF_ROOT / 'WIRKUNG/WIRKUNGSSTUFEN.sqlite',
    ])
    # Kapsel-/Installationsbeweise triggern keinen endlosen Selbstneubau.
    excluded_names = {
        'GA-CAPSULE-002-TECHNICAL.json',
        'GA-CAPSULE-002-PLAYWRIGHT.json',
        'FINAL_VALIDATION.json',
        'INSTALL_STATUS.json',
    }
    unique: dict[str, Path] = {}
    for path in paths:
        if path.name in excluded_names:
            continue
        unique[str(path.resolve())] = path.resolve()
    return [unique[key] for key in sorted(unique)]


def proof_fingerprint(base_path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(b'gesamtatlas-proof-inputs-v1\0')
    digest.update(str(base_path).encode()); digest.update(b'\0'); digest.update(sha256(base_path).encode()); digest.update(b'\0')
    for path in proof_input_paths():
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(path)
        digest.update(str(path).encode('utf-8')); digest.update(b'\0')
        digest.update(str(path.stat().st_size).encode()); digest.update(b'\0')
        digest.update(sha256(path).encode()); digest.update(b'\0')
    return digest.hexdigest()


def validate_candidate(path: Path, base: Path, fingerprint: str) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_ZIP_BYTES:
        raise RuntimeError(f'Kandidat zu groß: {path.stat().st_size}')
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'Kandidat beschädigt bei {bad}')
        names = set(archive.namelist())
        missing = sorted(REQUIRED - names)
        if missing:
            raise RuntimeError(f'Kandidat vermisst Pflichtkörper: {missing}')
        manifest = json.loads(archive.read('ENDPRODUKTBEWEIS/MANIFEST.json'))
    if manifest.get('base_capsule', {}).get('sha256') != sha256(base):
        raise RuntimeError('Manifest-Basishash stimmt nicht')
    if manifest.get('proof_source_fingerprint') != fingerprint:
        raise RuntimeError('Manifest-Fingerprint stimmt nicht')
    if manifest.get('public_delivery') is not False:
        raise RuntimeError('Kandidat behauptet öffentliche Auslieferung')
    if manifest.get('browser_real_acceptance') != 'OPEN_BLOCKED_EXTERNAL':
        raise RuntimeError('Browserblocker ging verloren')
    if manifest.get('external_response_count') != 0:
        raise RuntimeError('Kandidat behauptet Fremdantworten')
    return {
        'path': str(path),
        'bytes': path.stat().st_size,
        'sha256': sha256(path),
        'entry_count': len(names),
        'base_sha256': sha256(base),
        'proof_source_fingerprint': fingerprint,
    }


def save_base(source: Path) -> dict[str, Any]:
    if zip_manifest(source) is not None:
        raise RuntimeError('Eine bereits überlagerte Kapsel darf nicht als neue Basis gespeichert werden')
    atomic_copy(source, BASE_STORE)
    if zip_manifest(BASE_STORE) is not None:
        raise RuntimeError('Gespeicherte Basis enthält unerwartet den Endproduktbeweis')
    return {'path': str(BASE_STORE), 'bytes': BASE_STORE.stat().st_size, 'sha256': sha256(BASE_STORE)}


def prune_backups(keep: int = 3) -> None:
    if not BACKUP_ROOT.exists():
        return
    files = sorted((p for p in BACKUP_ROOT.glob('*.zip') if p.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files[keep:]:
        path.unlink(missing_ok=True)


def backup_canonical() -> Path:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    target = BACKUP_ROOT / f'{stamp}__{sha256(CANONICAL)[:16]}.zip'
    atomic_copy(CANONICAL, target)
    prune_backups()
    return target


def build_candidate(base: Path, fingerprint: str) -> dict[str, Any]:
    env = os.environ.copy()
    env['GA_BASE_CAPSULE'] = str(base)
    env['GA_PROOF_SOURCE_FINGERPRINT'] = fingerprint
    result = subprocess.run([sys.executable, str(BUILDER)], env=env, text=True, capture_output=True, timeout=900)
    if result.returncode != 0:
        raise RuntimeError(f'Beweiskapselbau fehlgeschlagen: {(result.stdout + result.stderr)[-5000:]}')
    return validate_candidate(CANDIDATE, base, fingerprint)


def install(force: bool = False) -> dict[str, Any]:
    if not CANONICAL.exists():
        raise FileNotFoundError(CANONICAL)
    CANONICAL.parent.mkdir(parents=True, exist_ok=True)
    current_manifest = zip_manifest(CANONICAL)
    action: list[str] = []
    if current_manifest is None:
        base = save_base(CANONICAL)
        action.append('new_base_saved')
    else:
        if not BASE_STORE.exists():
            raise RuntimeError('Kanonische Kapsel ist bereits überlagert, aber BASE_AKTUELL.zip fehlt. Rekursive Überlagerung wird verweigert.')
        if zip_manifest(BASE_STORE) is not None:
            raise RuntimeError('BASE_AKTUELL.zip ist selbst überlagert. Rekursive Überlagerung wird verweigert.')
        base = {'path': str(BASE_STORE), 'bytes': BASE_STORE.stat().st_size, 'sha256': sha256(BASE_STORE)}
    fingerprint = proof_fingerprint(BASE_STORE)
    if current_manifest is not None and not force:
        same_base = current_manifest.get('base_capsule', {}).get('sha256') == base['sha256']
        same_proof = current_manifest.get('proof_source_fingerprint') == fingerprint
        if same_base and same_proof:
            status = {
                'ok': True,
                'state': 'CURRENT_PROOF_CAPSULE_ALREADY_INSTALLED',
                'changed': False,
                'checked_utc': utcnow(),
                'canonical_path': str(CANONICAL),
                'canonical_bytes': CANONICAL.stat().st_size,
                'canonical_sha256': sha256(CANONICAL),
                'base': base,
                'proof_source_fingerprint': fingerprint,
            }
            atomic_json(INSTALL_STATUS, status)
            return status
    candidate = build_candidate(BASE_STORE, fingerprint)
    backup = backup_canonical()
    atomic_copy(CANDIDATE, CANONICAL)
    installed = validate_candidate(CANONICAL, BASE_STORE, fingerprint)
    if installed['sha256'] != candidate['sha256']:
        raise RuntimeError('Installierte Kapsel weicht vom geprüften Kandidaten ab')
    status = {
        'ok': True,
        'state': 'PROOF_CAPSULE_INSTALLED',
        'changed': True,
        'installed_utc': utcnow(),
        'canonical_path': str(CANONICAL),
        'canonical_bytes': CANONICAL.stat().st_size,
        'canonical_sha256': sha256(CANONICAL),
        'base': base,
        'candidate': candidate,
        'backup_path': str(backup),
        'proof_source_fingerprint': fingerprint,
        'actions': action + ['candidate_built', 'canonical_backed_up', 'candidate_installed', 'installed_zip_revalidated'],
        'truth_boundary': 'Installiert den geprüften privaten Beweiskörper. Browser-, Fremd-LLM- und menschliche Endabnahmen bleiben offen.',
    }
    atomic_json(INSTALL_STATUS, status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(prog='gesamtatlas-proof-capsule-install')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with LOCK_PATH.open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            value = install(force=args.force)
        print(json.dumps({'ok': True, 'result': value}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        error = {'ok': False, 'error': f'{type(exc).__name__}: {exc}', 'failed_utc': utcnow(), 'canonical_path': str(CANONICAL)}
        atomic_json(INSTALL_STATUS.with_name('INSTALL_FAILURE.json'), error)
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
