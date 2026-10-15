#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

BASE_CAPSULE = Path(os.environ.get('GA_BASE_CAPSULE', '/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip'))
PROOF_ROOT = Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis')
SOURCE_ROOT = Path('/root/werkraum/_gpt/gesamtatlas/originalquellen/nachgereichter_verlauf_2026-07-29')
TOOL_ROOT = Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis')
OUTPUT_ROOT = PROOF_ROOT / 'KAPSEL'
CURRENT = OUTPUT_ROOT / 'AKTUELL'
OUTPUT_ZIP = OUTPUT_ROOT / 'GESAMTATLAS_KAPSEL_MIT_ENDPRODUKTBEWEIS.zip'
STATUS_PATH = OUTPUT_ROOT / 'STATUS.json'
MAX_ZIP_BYTES = 25_000_000
MAX_UNPACKED_BYTES = 80_000_000
PROOF_SOURCE_FINGERPRINT = os.environ.get('GA_PROOF_SOURCE_FINGERPRINT')

HIGH_CONFIDENCE_SECRET_PATTERNS = [
    ('private_key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('openai_key', re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b')),
    ('bearer_token', re.compile(r'(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9._~+\-/=]{16,}')),
    ('assigned_secret', re.compile(r'(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*["\']?(?!\[|<|REDACTED|ENTFERNT|PLACEHOLDER|EXAMPLE)[^\s"\',}]{12,}')),
]
TEXT_SUFFIXES = {'.md','.txt','.json','.jsonl','.py','.html','.css','.js','.sql','.yaml','.yml','.toml','.ini','.csv'}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def safe_member(info: zipfile.ZipInfo) -> PurePosixPath:
    name = info.filename.replace('\\', '/')
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise RuntimeError(f'Unsicherer ZIP-Pfad: {info.filename!r}')
    mode = (info.external_attr >> 16) & 0o170000
    if mode == stat.S_IFLNK:
        raise RuntimeError(f'Symlink im Ausgangs-ZIP: {info.filename!r}')
    return path


def extract_base(destination: Path) -> dict[str, Any]:
    if not BASE_CAPSULE.exists():
        raise FileNotFoundError(BASE_CAPSULE)
    count = 0
    with zipfile.ZipFile(BASE_CAPSULE) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'Ausgangskapsel beschädigt bei {bad}')
        for info in archive.infolist():
            rel = safe_member(info)
            target = destination.joinpath(*rel.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open('wb') as out:
                shutil.copyfileobj(source, out)
            count += 1
    return {'path': str(BASE_CAPSULE), 'bytes': BASE_CAPSULE.stat().st_size, 'sha256': sha256(BASE_CAPSULE), 'entries': count}


def copy_file(source: Path, target: Path) -> dict[str, Any]:
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if sha256(source) != sha256(target):
        raise RuntimeError(f'Kopierhash weicht ab: {source}')
    return {'source_path': str(source), 'capsule_path': target.as_posix(), 'bytes': target.stat().st_size, 'sha256': sha256(target)}


def sqlite_backup(source: Path, target: Path) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    src = sqlite3.connect(f'file:{source}?mode=ro', uri=True, timeout=30)
    dst = sqlite3.connect(target, timeout=30)
    try:
        src.backup(dst)
        dst.execute('pragma journal_mode=DELETE')
        dst.execute('pragma optimize')
        dst.commit()
        integrity = dst.execute('pragma integrity_check').fetchone()[0]
        if integrity != 'ok':
            raise RuntimeError(f'SQLite-Kopie beschädigt: {source}: {integrity}')
        dst.execute('vacuum')
    finally:
        src.close(); dst.close()
    return {'source_path': str(source), 'capsule_path': target.as_posix(), 'bytes': target.stat().st_size, 'sha256': sha256(target), 'sqlite_integrity': 'ok'}


def added_sources() -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = [
        (PROOF_ROOT / '00_BEWEIS_START.md', 'ENDPRODUKTBEWEIS/00_START_HIER.md'),
        (PROOF_ROOT / 'QUELLENMANIFEST.json', 'ENDPRODUKTBEWEIS/QUELLEN/BEWEIS_QUELLENMANIFEST.json'),
        (PROOF_ROOT / 'ABHAENGIGKEITEN/BROWSER_EXTENSION_REALABNAHME_OFFEN.json', 'ENDPRODUKTBEWEIS/ABHAENGIGKEITEN/BROWSER_EXTENSION_REALABNAHME_OFFEN.json'),
        (PROOF_ROOT / 'ANFORDERUNGEN/ANFORDERUNGSMATRIX.md', 'ENDPRODUKTBEWEIS/ANFORDERUNGEN/ANFORDERUNGSMATRIX.md'),
        (PROOF_ROOT / 'ANFORDERUNGEN/ANFORDERUNGSREGISTER.jsonl', 'ENDPRODUKTBEWEIS/ANFORDERUNGEN/ANFORDERUNGSREGISTER.jsonl'),
        (PROOF_ROOT / 'ANFORDERUNGEN/UEBERHOLTE_ANFORDERUNGEN.md', 'ENDPRODUKTBEWEIS/ANFORDERUNGEN/UEBERHOLTE_ANFORDERUNGEN.md'),
        (SOURCE_ROOT / 'QUELLENMANIFEST.json', 'ENDPRODUKTBEWEIS/QUELLEN/ORIGINALVERLAUF_MANIFEST.json'),
        (SOURCE_ROOT / 'LUECKEN_UND_DUPLIKATE.json', 'ENDPRODUKTBEWEIS/QUELLEN/LUECKEN_UND_DUPLIKATE.json'),
        (SOURCE_ROOT / 'LUECKEN_UND_DUPLIKATE.md', 'ENDPRODUKTBEWEIS/QUELLEN/LUECKEN_UND_DUPLIKATE.md'),
        (SOURCE_ROOT / 'NACHGEREICHTER_SICHTBARER_VERLAUF.txt.gz', 'ENDPRODUKTBEWEIS/QUELLEN/NACHGEREICHTER_SICHTBARER_VERLAUF.txt.gz'),
        (SOURCE_ROOT / 'KANONISCHE_LESEFASSUNG.md', 'ENDPRODUKTBEWEIS/QUELLEN/KANONISCHE_LESEFASSUNG.md'),
        (PROOF_ROOT / 'INTEGRATION/LLM_LESEN_VERSTEHEN_VORSCHLAGEN_INTEGRIEREN.md', 'ENDPRODUKTBEWEIS/INTEGRATION/VERTRAG.md'),
        (PROOF_ROOT / 'INTEGRATION/LLM_ABNAHME_AUFGABEN.json', 'ENDPRODUKTBEWEIS/INTEGRATION/LLM_ABNAHME_AUFGABEN.json'),
        (PROOF_ROOT / 'INTEGRATION/RAW_RESPONSE_SCHEMA.json', 'ENDPRODUKTBEWEIS/INTEGRATION/RAW_RESPONSE_SCHEMA.json'),
        (PROOF_ROOT / 'INTEGRATION/INTEGRATION_FREIGABE_SCHEMA.json', 'ENDPRODUKTBEWEIS/INTEGRATION/INTEGRATION_FREIGABE_SCHEMA.json'),
        (PROOF_ROOT / 'INTEGRATION/STATUS.json', 'ENDPRODUKTBEWEIS/INTEGRATION/STATUS.json'),
        (PROOF_ROOT / 'WIRKUNG/README.md', 'ENDPRODUKTBEWEIS/WIRKUNG/README.md'),
        (PROOF_ROOT / 'WIRKUNG/STATUS.json', 'ENDPRODUKTBEWEIS/WIRKUNG/STATUS.json'),
        (PROOF_ROOT / 'WIRKUNG/BEISPIEL_ORIGINALVERLAUF.json', 'ENDPRODUKTBEWEIS/WIRKUNG/BEISPIEL_ORIGINALVERLAUF.json'),
        (PROOF_ROOT / 'TERMINALWIRKUNG/STATUS.json', 'ENDPRODUKTBEWEIS/TERMINALWIRKUNG/STATUS.json'),
        (PROOF_ROOT / 'TERMINALWIRKUNG/HISTORY_IMPORT_STATUS.json', 'ENDPRODUKTBEWEIS/TERMINALWIRKUNG/HISTORY_IMPORT_STATUS.json'),
        (PROOF_ROOT / 'TERMINALWIRKUNG/BEISPIEL_PLAYWRIGHT_KORREKTUR.json', 'ENDPRODUKTBEWEIS/TERMINALWIRKUNG/BEISPIEL_PLAYWRIGHT_KORREKTUR.json'),
        (PROOF_ROOT / 'TERMINALWIRKUNG/SPEZIFIKATIONEN/GA-TERMINAL-034__PLAYWRIGHT_KORREKTUR.json', 'ENDPRODUKTBEWEIS/TERMINALWIRKUNG/SPEZIFIKATION.json'),
        (PROOF_ROOT / 'ZEITREISE/STATUS.json', 'ENDPRODUKTBEWEIS/ZEITREISE/STATUS.json'),
        (PROOF_ROOT / 'ZEITREISE/HISTORY_IMPORT_STATUS.json', 'ENDPRODUKTBEWEIS/ZEITREISE/HISTORY_IMPORT_STATUS.json'),
        (PROOF_ROOT / 'ZEITREISE/BEISPIEL_MOMENT_203015.json', 'ENDPRODUKTBEWEIS/ZEITREISE/BEISPIEL_MOMENT_203015.json'),
        (PROOF_ROOT / 'ZEITREISE/SPEZIFIKATIONEN/GA-TIME-011__MOMENT_203015.json', 'ENDPRODUKTBEWEIS/ZEITREISE/SPEZIFIKATION.json'),
        (TOOL_ROOT / 'llm_abnahme.py', 'ENDPRODUKTBEWEIS/MASCHINE/llm_abnahme.py'),
        (TOOL_ROOT / 'evidence/evidence_ladder.py', 'ENDPRODUKTBEWEIS/MASCHINE/evidence_ladder.py'),
        (TOOL_ROOT / 'terminal/terminal_effects.py', 'ENDPRODUKTBEWEIS/MASCHINE/terminal_effects.py'),
        (TOOL_ROOT / 'time/epistemic_time.py', 'ENDPRODUKTBEWEIS/MASCHINE/epistemic_time.py'),
        (TOOL_ROOT / 'ai_streams/build_ai_streams_ui.py', 'ENDPRODUKTBEWEIS/MASCHINE/build_ai_streams_ui.py'),
        (TOOL_ROOT / 'size_truth/build_size_truth_ui.py', 'ENDPRODUKTBEWEIS/MASCHINE/build_size_truth_ui.py'),
        (TOOL_ROOT / 'capsule/build_proof_capsule.py', 'ENDPRODUKTBEWEIS/MASCHINE/build_proof_capsule.py'),
        (TOOL_ROOT / 'capsule/install_proof_capsule.py', 'ENDPRODUKTBEWEIS/MASCHINE/install_proof_capsule.py'),
        (TOOL_ROOT / 'systemd/gesamtatlas-proof-capsule.service', 'ENDPRODUKTBEWEIS/MASCHINE/systemd/gesamtatlas-proof-capsule.service'),
        (TOOL_ROOT / 'systemd/gesamtatlas-proof-capsule.path', 'ENDPRODUKTBEWEIS/MASCHINE/systemd/gesamtatlas-proof-capsule.path'),
        (TOOL_ROOT / 'systemd/gesamtatlas-proof-capsule.timer', 'ENDPRODUKTBEWEIS/MASCHINE/systemd/gesamtatlas-proof-capsule.timer'),
        (PROOF_ROOT / 'UI/index.html', 'ENDPRODUKTBEWEIS/UI/index.html'),
        (PROOF_ROOT / 'UI/wirkung.html', 'ENDPRODUKTBEWEIS/UI/wirkung.html'),
        (PROOF_ROOT / 'UI/terminalwirkung.html', 'ENDPRODUKTBEWEIS/UI/terminalwirkung.html'),
        (PROOF_ROOT / 'UI/zeitreise.html', 'ENDPRODUKTBEWEIS/UI/zeitreise.html'),
        (PROOF_ROOT / 'UI/ai-stroeme.html', 'ENDPRODUKTBEWEIS/UI/ai-stroeme.html'),
        (PROOF_ROOT / 'AI_STROEME/STATUS.json', 'ENDPRODUKTBEWEIS/AI_STROEME/STATUS.json'),
        (PROOF_ROOT / 'AI_STROEME/AI_STROEME.json', 'ENDPRODUKTBEWEIS/AI_STROEME/AI_STROEME.json'),
        (PROOF_ROOT / 'AI_STROEME/AI_STROM_BRUECKEN.json', 'ENDPRODUKTBEWEIS/AI_STROEME/AI_STROM_BRUECKEN.json'),
        (PROOF_ROOT / 'UI/groessenwahrheit.html', 'ENDPRODUKTBEWEIS/UI/groessenwahrheit.html'),
        (PROOF_ROOT / 'GROESSENWAHRHEIT/STATUS.json', 'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/STATUS.json'),
        (PROOF_ROOT / 'GROESSENWAHRHEIT/GROESSENWAHRHEIT.json', 'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/GROESSENWAHRHEIT.json'),
        (PROOF_ROOT / 'GROESSENWAHRHEIT/WURZEL_AUSSCHNITT.json', 'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/WURZEL_AUSSCHNITT.json'),
        (PROOF_ROOT / 'GROESSENWAHRHEIT/EINGANG_START_HIER.md', 'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_START_HIER.md'),
        (PROOF_ROOT / 'GROESSENWAHRHEIT/EINGANG_MANIFEST.json', 'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_MANIFEST.json'),
        (PROOF_ROOT / 'ERGAENZUNGEN/2026-07-30__GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.json', 'ENDPRODUKTBEWEIS/ERGAENZUNGEN/GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.json'),
        (PROOF_ROOT / 'ERGAENZUNGEN/2026-07-30__GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.md', 'ENDPRODUKTBEWEIS/ERGAENZUNGEN/GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.md'),
        (PROOF_ROOT / 'SCHLANKHEITSAUDIT.json', 'ENDPRODUKTBEWEIS/SCHLANKHEIT/SCHLANKHEITSAUDIT.json'),
        (PROOF_ROOT / 'SCHLANKHEITSAUDIT.md', 'ENDPRODUKTBEWEIS/SCHLANKHEIT/SCHLANKHEITSAUDIT.md'),
        (Path('/root/werkraum/_gpt/mcp_global_protocols/gesamtatlas_v1.json'), 'ENDPRODUKTBEWEIS/VERTRAEGE/gesamtatlas_v1.json'),
        (PROOF_ROOT / 'UI/DATA.json', 'ENDPRODUKTBEWEIS/UI/DATA.json'),
        (PROOF_ROOT / 'UI/STATUS.json', 'ENDPRODUKTBEWEIS/UI/STATUS.json'),
    ]
    for report in sorted((PROOF_ROOT / 'EVIDENZ').glob('*.json')):
        # Kapsel-, Installations- und kanonische Abnahmeberichte bleiben außen.
        # Sonst würde eine ZIP ihre eigene Vorgängerversion als Innenbeweis tragen.
        if report.name.startswith('GA-CAPSULE'):
            continue
        files.append((report, f'ENDPRODUKTBEWEIS/EVIDENZ/{report.name}'))
    return files


def privacy_scan(root: Path, added_relpaths: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel in added_relpaths:
        path = root / rel
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 5_000_000:
            continue
        text = path.read_text('utf-8', errors='replace')
        for name, pattern in HIGH_CONFIDENCE_SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append({'capsule_path': rel, 'pattern': name, 'excerpt': match.group(0)[:120]})
    return findings


def dir_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob('*') if path.is_file() and not path.is_symlink())


def build() -> dict[str, Any]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.proof-capsule-', dir=OUTPUT_ROOT))
    content = staging / 'content'
    content.mkdir()
    try:
        base = extract_base(content)
        records: list[dict[str, Any]] = []
        added_relpaths: list[str] = []
        for source, rel in added_sources():
            target = content / rel
            record = copy_file(source, target)
            record['capsule_path'] = rel
            records.append(record); added_relpaths.append(rel)
        for source, rel in [
            (PROOF_ROOT / 'ANFORDERUNGEN/ANFORDERUNGSREGISTER.sqlite', 'ENDPRODUKTBEWEIS/MASCHINE/ANFORDERUNGSREGISTER.sqlite'),
            (PROOF_ROOT / 'WIRKUNG/WIRKUNGSSTUFEN.sqlite', 'ENDPRODUKTBEWEIS/MASCHINE/WIRKUNGSSTUFEN.sqlite'),
        ]:
            target = content / rel
            record = sqlite_backup(source, target)
            record['capsule_path'] = rel
            records.append(record); added_relpaths.append(rel)
        # Kapselspezifische Offline-Verweise: kleine Datenbanken lokal, große Tiefenkörper nur als VPS-Referenz.
        ui_replacements = {
            'ENDPRODUKTBEWEIS/UI/index.html': {
                '../00_BEWEIS_START.md': '../00_START_HIER.md',
                '../ANFORDERUNGEN/ANFORDERUNGSREGISTER.sqlite': '../MASCHINE/ANFORDERUNGSREGISTER.sqlite',
            },
            'ENDPRODUKTBEWEIS/UI/wirkung.html': {
                '../WIRKUNG/WIRKUNGSSTUFEN.sqlite': '../MASCHINE/WIRKUNGSSTUFEN.sqlite',
            },
            'ENDPRODUKTBEWEIS/UI/terminalwirkung.html': {
                '<a href="../TERMINALWIRKUNG/WIRKUNGSKETTEN.sqlite">SQLite-Datenbank</a>': '<a href="../TERMINALWIRKUNG/STATUS.json">Kompakter Maschinenstatus; vollständige SQLite bleibt auf dem VPS</a>',
            },
            'ENDPRODUKTBEWEIS/UI/zeitreise.html': {
                '<a href="../ZEITREISE/EPISTEMISCHE_MOMENTE.sqlite">SQLite-Datenbank</a>': '<a href="../ZEITREISE/STATUS.json">Kompakter Maschinenstatus; vollständige SQLite bleibt auf dem VPS</a>',
            },
        }
        for rel, replacements in ui_replacements.items():
            path = content / rel
            text = path.read_text('utf-8')
            for old, new in replacements.items():
                if old not in text:
                    raise RuntimeError(f'Kapsel-UI-Verweis nicht gefunden: {rel}: {old}')
                text = text.replace(old, new)
            atomic_write(path, text)
            for record in records:
                if record['capsule_path'] == rel:
                    record['bytes'] = path.stat().st_size
                    record['sha256'] = sha256(path)
                    record['copy_class'] = 'capsule_specific_offline_projection'
                    break

        pointer = '''# Erweiterter Endproduktbeweis\n\nDiese private Kapsel ergänzt die bestehende Gesamtatlas-Kapsel um den quellengebundenen Erfüllungsvertrag.\n\nEinstieg: `ENDPRODUKTBEWEIS/00_START_HIER.md`\n\nWichtig:\n\n- Die Browser-Erweiterung ist noch nicht real abgenommen.\n- Fremd-LLM-Antworten sind noch nicht vorhanden.\n- Lesen, Verstehen, Vorschlagen und kanonische Integration bleiben getrennt.\n- Daniel entscheidet jede kanonische Integration.\n- Vollständige Terminal- und Zeitreise-Datenbanken bleiben auf dem VPS und werden gezielt materialisiert; die Kapsel enthält reale Beispiele, Schemata und Testbeweise.\n'''
        atomic_write(content / '01_ENDPRODUKTBEWEIS_START.md', pointer)
        added_relpaths.append('01_ENDPRODUKTBEWEIS_START.md')
        privacy = privacy_scan(content, added_relpaths)
        if privacy:
            raise RuntimeError('Hochkonfidente Geheimnisfunde in Zusatzkörpern: ' + json.dumps(privacy, ensure_ascii=False))
        unpacked = dir_size(content)
        if unpacked > MAX_UNPACKED_BYTES:
            raise RuntimeError(f'Ungepackte Kapsel zu groß: {unpacked} > {MAX_UNPACKED_BYTES}')
        manifest = {
            'schema_version': 'gesamtatlas-proof-capsule-1.0',
            'generated_utc': utcnow(),
            'purpose': 'private_selective_handoff_with_requirement_bound_endproduct_evidence',
            'base_capsule': base,
            'proof_source_fingerprint': PROOF_SOURCE_FINGERPRINT,
            'public_delivery': False,
            'distribution': 'Daniel downloads via WinSCP and distributes selectively.',
            'canonical_installation': False,
            'candidate_only': True,
            'requirement_count': 21,
            'clean_room_task_count': 10,
            'external_response_count': 0,
            'browser_real_acceptance': 'OPEN_BLOCKED_EXTERNAL',
            'included_full_databases': ['ANFORDERUNGSREGISTER.sqlite', 'WIRKUNGSSTUFEN.sqlite'],
            'reference_only_large_databases': [
                '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/TERMINALWIRKUNG/WIRKUNGSKETTEN.sqlite',
                '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/ZEITREISE/EPISTEMISCHE_MOMENTE.sqlite',
            ],
            'added_files': records,
            'privacy_scan': {'high_confidence_secret_findings': 0, 'scope': 'added textual proof files'},
            'truth_boundary': 'Die Kapsel beweist vorhandene Quellen, Modelle und Testläufe. Sie behauptet weder aktive Browser-Integration noch abgeschlossene Fremd-LLM- oder menschliche Endabnahme.',
        }
        atomic_write(content / 'ENDPRODUKTBEWEIS/MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
        manifest_rel = 'ENDPRODUKTBEWEIS/MANIFEST.json'; added_relpaths.append(manifest_rel)
        sums = []
        for rel in sorted(added_relpaths):
            path = content / rel
            sums.append(f'{sha256(path)}  {rel}')
        atomic_write(content / 'ENDPRODUKTBEWEIS/SHA256SUMS.txt', '\n'.join(sums) + '\n')
        added_relpaths.append('ENDPRODUKTBEWEIS/SHA256SUMS.txt')
        zip_temp = staging / 'candidate.zip'
        with zipfile.ZipFile(zip_temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            for path in sorted(content.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(content).as_posix())
        with zipfile.ZipFile(zip_temp) as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError(f'Kandidaten-ZIP beschädigt bei {bad}')
            entries = len(archive.infolist())
            for info in archive.infolist():
                safe_member(info)
        if zip_temp.stat().st_size > MAX_ZIP_BYTES:
            raise RuntimeError(f'ZIP zu groß: {zip_temp.stat().st_size} > {MAX_ZIP_BYTES}')
        candidate_status = {
            'ok': True,
            'generated_utc': utcnow(),
            'candidate_zip': str(OUTPUT_ZIP),
            'candidate_zip_bytes': zip_temp.stat().st_size,
            'candidate_zip_sha256': sha256(zip_temp),
            'entry_count': entries,
            'unpacked_bytes': unpacked,
            'max_zip_bytes': MAX_ZIP_BYTES,
            'canonical_installed': False,
            'base_capsule_sha256': base['sha256'],
            'proof_source_fingerprint': PROOF_SOURCE_FINGERPRINT,
            'browser_real_acceptance': 'OPEN_BLOCKED_EXTERNAL',
            'external_response_count': 0,
            'privacy_high_confidence_findings': 0,
            'truth_boundary': manifest['truth_boundary'],
        }
        previous = CURRENT.with_name('AKTUELL.previous')
        if previous.exists(): shutil.rmtree(previous)
        if CURRENT.exists(): CURRENT.rename(previous)
        content.rename(CURRENT)
        if previous.exists(): shutil.rmtree(previous)
        zip_stage = OUTPUT_ZIP.with_suffix('.tmp')
        shutil.copy2(zip_temp, zip_stage)
        os.replace(zip_stage, OUTPUT_ZIP)
        atomic_write(STATUS_PATH, json.dumps(candidate_status, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
        return candidate_status
    except Exception:
        failed = OUTPUT_ROOT / f'FEHLGESCHLAGENER_KAPSELBAU_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}'
        if staging.exists(): staging.rename(failed)
        raise
    finally:
        if staging.exists(): shutil.rmtree(staging, ignore_errors=True)


if __name__ == '__main__':
    try:
        print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': f'{type(exc).__name__}: {exc}'}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
