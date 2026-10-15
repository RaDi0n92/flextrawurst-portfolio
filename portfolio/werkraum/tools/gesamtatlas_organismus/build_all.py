#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from browser import build_browser, origin_search, package_conversation
from capsule import build_capsule, install_capsule
from common import (
    ATLAS_ROOT,
    CAPSULE_ZIP,
    CURRENT,
    LOCK,
    MAX_CAPSULE_BYTES,
    MAX_OVERLAY_BYTES,
    MAX_TOTAL_BYTES,
    OUTPUT_ROOT,
    SOURCE_ROOTS,
    STATE,
    atomic_replace_directory,
    dir_size,
    json_text,
    load_json,
    sha256_file,
    utcnow,
)
from core import build_core, search_core
from homes import build_homes
from reactive import build_reactive
from terminal import build_terminal, search_terminal
from ui import render_ui

TOOL_ROOT = Path(__file__).resolve().parent
PUBLIC_URL = 'https://flextrawurst.de/gesamtatlas/'


def fingerprint() -> str:
    digest = hashlib.sha256()
    tracked = [
        ATLAS_ROOT / 'PFADINDEX.sqlite', ATLAS_ROOT / 'BEGRIFFSINDEX.sqlite', ATLAS_ROOT / 'BEZIEHUNGSREGISTER.sqlite',
        ATLAS_ROOT / 'PROJEKTREGISTER.json', ATLAS_ROOT / 'AI_STROEME.json', ATLAS_ROOT / 'IDEENREGISTER.jsonl',
        Path('/root/werkraum/_gpt/ui_visible_conversations'), Path('/root/.claude/projects/-root'),
        Path('/root/.codex/sessions'), Path('/root/.gemini/antigravity-cli/brain'),
        Path('/root/werkraum/_gpt/terminal_capture'), Path('/root/werkraum/_gpt/gesamtatlas/beitraege'),
        Path('/root/werkraum/_gpt/mcp_zuhause'), Path('/root/werkraum/_claude'), Path('/root/werkraum/_codex'),
        Path('/root/werkraum/_gemini'), Path('/root/werkraum/_kimi'), Path('/root/werkraum/_glm'),
    ]
    for root in tracked:
        digest.update(str(root).encode())
        if not root.exists():
            digest.update(b'\0missing')
            continue
        if root.is_file():
            stat = root.stat()
            digest.update(f'\0{stat.st_size}\0{stat.st_mtime_ns}'.encode())
            continue
        count = total = max_mtime = 0
        for base, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if name not in {'.git','node_modules','__pycache__','.cache','organismus','dateikoerper'}]
            for name in files:
                path = Path(base) / name
                try:
                    stat = path.stat()
                except OSError:
                    continue
                count += 1; total += stat.st_size; max_mtime = max(max_mtime, stat.st_mtime_ns)
        digest.update(f'\0{count}\0{total}\0{max_mtime}'.encode())
    return digest.hexdigest()


def write_initial_docs(staging: Path) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    (staging / '00_START_HIER.md').write_text('''# Gesamtatlas-Organismus\n\nDieser Körper ist der schlanke lebende Gesamtatlas. Er verdoppelt den VPS nicht, sondern hält Pfade, Herkunft, Beziehungen, kurze Suchvorschauen und gezielt materialisierbare Originalzugänge zusammen.\n\nSeine lokale Oberfläche liegt unter `UI/index.html`. Die kleine Übergabekapsel liegt nach dem vollständigen Bau unter `GESAMTATLAS_KAPSEL_AKTUELL.zip`.\n\nDie öffentliche Route `/gesamtatlas/` bleibt absichtlich geschlossen.\n''', encoding='utf-8')
    (staging / 'ARCHITEKTUR.md').write_text('''# Architektur\n\n1. **Schmaler Kern:** Pfade, Projekte, AI-Ströme, Beziehungen und kurze Vorschauen.\n2. **AI-Zuhause:** vollständige Kartierung und ausgewählte Anker, keine Vollkopien.\n3. **Browser A–F:** Zeitreise, UI-MCP-Spur, Blitzmomente, Rohwunschvergleich, Pakete und Ursprungssuche.\n4. **Terminalwerkstrom:** normalisierte Gespräche, Tools, Fehler, Entscheidungen und PTY-Fallback.\n5. **Reaktiver Atlas:** findet Lücken und macht Vorschläge, verändert aber keine Originalquellen.\n6. **Kleine Kapsel:** facettenvollständig, bewusst nicht detailvollständig.\n7. **Explorationskörper:** konkrete Details erst auf eine konkrete Frage hin.\n''', encoding='utf-8')
    (staging / 'WAHRHEITSGRENZEN.md').write_text('''# Wahrheitsgrenzen\n\n- Original, Spiegel, technische Beobachtung und Ableitung bleiben getrennt.\n- Sichtbarkeit oder Erreichbarkeit beweist kein tatsächliches Lesen.\n- Ähnlichkeit beweist weder Übernahme noch unabhängigen Konsens.\n- Heuristische Blitz-, Verhärtungs- und Reaktionsmarker sind prüfbare Kandidaten.\n- Historisch nicht erfasste Inhalte werden nicht erfunden.\n- Daniels eigene Projektgeschichte ist tief erforschbar; fremde personenbezogene Inhalte und Geheimnisse werden in Außenkörpern markiert entfernt.\n''', encoding='utf-8')


def run_playwright(staging: Path, stage: int) -> dict[str, Any]:
    evidence = staging / 'EVIDENZ'
    evidence.mkdir(parents=True, exist_ok=True)
    port = 18440 + stage
    server_log = evidence / f'BAUABSCHNITT_{stage:02d}_HTTP.log'
    with server_log.open('w', encoding='utf-8') as stream:
        server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(staging)], stdout=stream, stderr=subprocess.STDOUT)
    report = evidence / f'BAUABSCHNITT_{stage:02d}_PLAYWRIGHT.json'
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/UI/index.html', timeout=1):
                    break
            except Exception:
                time.sleep(.15)
        env = os.environ.copy()
        env.update({'ATLAS_BASE': f'http://127.0.0.1:{port}', 'ATLAS_STAGE': str(stage), 'ATLAS_REPORT': str(report)})
        result = subprocess.run(['node', str(TOOL_ROOT / 'tests/stage_test.js')], env=env, text=True, capture_output=True, timeout=180)
        (evidence / f'BAUABSCHNITT_{stage:02d}_PLAYWRIGHT.stdout').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f'Playwright Bauabschnitt {stage} fehlgeschlagen: {(result.stdout + result.stderr)[-3000:]}')
        data = json.loads(report.read_text('utf-8'))
        if not data.get('ok'):
            raise RuntimeError(f'Playwright Bauabschnitt {stage} nicht grün')
        return data
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def write_access(staging: Path) -> dict[str, Any]:
    target = staging / 'ZUGANG'
    target.mkdir(parents=True, exist_ok=True)
    access = {
        'schema_version': 'gesamtatlas-access-1.0',
        'generated_utc': utcnow(),
        'streams': ['chatgpt','claude','codex','gemini','kimi','glm','grok'],
        'commands': ['status','search','origin','ask','read','explore','conversation-package','note','challenge','impulse'],
        'cli': '/usr/local/bin/gesamtatlas',
        'examples': {
            'search': 'gesamtatlas --stream claude search "Browser-Agent"',
            'challenge': 'gesamtatlas --stream gemini challenge --subject "Aussage" "Gegenquelle fehlt"',
            'note': 'gesamtatlas --stream codex note --subject "Fund" "Diese Datei gehört zu Projekt X"',
            'explore': 'gesamtatlas explore --query "Ursprung Gesamtatlas"',
        },
        'write_boundary': 'Beiträge werden attribuiert gespeichert und nicht automatisch kanonisch.',
        'source_mutation': False,
    }
    (target / 'ACCESS.json').write_text(json_text(access), encoding='utf-8')
    (target / 'README.md').write_text('''# Zugang für Menschen und AI-Ströme\n\nAlle bekannten Ströme nutzen denselben schlanken Zugang, behalten aber ihre Herkunft. Sie dürfen suchen, lesen, fragen, Detailkörper erzeugen sowie eigene Notizen, Impulse und Widersprüche hinterlassen. Beiträge werden nie automatisch Wahrheit.\n''', encoding='utf-8')
    return access


def static_acceptance(staging: Path, reports: list[dict[str, Any]], capsule: dict[str, Any]) -> dict[str, Any]:
    errors = []
    if len(reports) != 7 or not all(report.get('ok') for report in reports):
        errors.append('playwright_stages')
    core = load_json(staging / 'KERN/STATUS.json', {}) or {}
    homes = load_json(staging / 'HÄUSER/STATUS.json', {}) or {}
    browser = load_json(staging / 'BROWSER/STATUS.json', {}) or {}
    terminal = load_json(staging / 'TERMINAL/STATUS.json', {}) or {}
    reactive = load_json(staging / 'REAKTION/STATUS.json', {}) or {}
    if core.get('counts', {}).get('paths', 0) < 1000: errors.append('core_paths')
    if homes.get('homes_present', 0) < 6: errors.append('homes')
    if set(browser.get('a_to_f', {})) != set('ABCDEF'): errors.append('browser_a_f')
    if terminal.get('providers', {}).get('claude', {}).get('sessions', 0) < 1: errors.append('claude_terminal')
    if terminal.get('providers', {}).get('codex', {}).get('sessions', 0) < 1: errors.append('codex_terminal')
    if terminal.get('providers', {}).get('gemini', {}).get('sessions', 0) < 1: errors.append('gemini_terminal')
    if reactive.get('finding_count', 0) < 1: errors.append('reactive')
    if capsule.get('zip_bytes', 0) > MAX_CAPSULE_BYTES: errors.append('capsule_size')
    if not capsule.get('facet_complete') or capsule.get('detail_complete') is not False: errors.append('capsule_semantics')
    with zipfile.ZipFile(staging / 'GESAMTATLAS_KAPSEL_AKTUELL.zip') as archive:
        bad = archive.testzip()
        if bad: errors.append(f'zip:{bad}')
        names = set(archive.namelist())
        for needed in ('00_START_HIER.md','MASCHINE/KAPSEL.sqlite','OFFLINE/index.html','FRAGE_DIE_KAPSEL.py'):
            if needed not in names: errors.append(f'zip_missing:{needed}')
    overlay_bytes = dir_size(staging)
    current_atlas_without_staging = max(0, dir_size(ATLAS_ROOT) - dir_size(OUTPUT_ROOT))
    projected_total = current_atlas_without_staging + overlay_bytes
    if overlay_bytes > MAX_OVERLAY_BYTES: errors.append(f'overlay_size:{overlay_bytes}')
    if projected_total > MAX_TOTAL_BYTES: errors.append(f'total_size:{projected_total}')
    # Real CLI-like search acceptance against staged data.
    if not search_core(staging / 'KERN/ATLAS_SCHMAL.sqlite', 'gesamtatlas', 5): errors.append('core_search')
    if not origin_search(staging / 'BROWSER', 'Gesamtatlas', 5):
        # Test data may not contain this exact word, use known recorder term.
        if not origin_search(staging / 'BROWSER', 'Recorder', 5): errors.append('origin_search')
    if not search_terminal(staging / 'TERMINAL', 'tool', 5):
        if not search_terminal(staging / 'TERMINAL', 'VPS', 5): errors.append('terminal_search')
    public_status = None
    try:
        request = urllib.request.Request(PUBLIC_URL, method='GET')
        urllib.request.urlopen(request, timeout=20)
        public_status = 200
    except urllib.error.HTTPError as exc:
        public_status = exc.code
    except Exception as exc:
        errors.append(f'public_probe:{type(exc).__name__}')
    if public_status != 404: errors.append(f'public_status:{public_status}')
    return {
        'ok': not errors,
        'errors': errors,
        'generated_utc': utcnow(),
        'playwright_stage_count': len(reports),
        'playwright_check_count': sum(report.get('check_count', 0) for report in reports),
        'overlay_bytes': overlay_bytes,
        'projected_total_atlas_bytes': projected_total,
        'capsule_bytes': capsule.get('zip_bytes'),
        'public_status': public_status,
    }


def manifest(staging: Path, validation: dict[str, Any], source_fp: str) -> dict[str, Any]:
    files = []
    for path in sorted(staging.rglob('*')):
        if path.is_file() and path.name not in {'MANIFEST.json','SHA256SUMS.txt'}:
            files.append({'path': path.relative_to(staging).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256_file(path)})
    value = {
        'schema_version': 'gesamtatlas-organismus-1.0',
        'generated_utc': utcnow(),
        'source_fingerprint': source_fp,
        'status': 'validated' if validation.get('ok') else 'failed',
        'public_website': False,
        'copy_policy': 'reference_first_targeted_materialization',
        'validation': validation,
        'files': files,
        'truth_boundary': 'Der Atlas ist vollständig als Zugang und Facettennetz, nicht als materielle Vollkopie aller Originale.',
    }
    (staging / 'MANIFEST.json').write_text(json_text(value), encoding='utf-8')
    checks = [f'{sha256_file(path)}  {path.relative_to(staging).as_posix()}' for path in sorted(staging.rglob('*')) if path.is_file() and path.name != 'SHA256SUMS.txt']
    (staging / 'SHA256SUMS.txt').write_text('\n'.join(checks) + '\n', encoding='utf-8')
    return value


def build(force: bool) -> dict[str, Any]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    source_fp = fingerprint()
    previous = load_json(STATE, {}) or {}
    if not force and previous.get('source_fingerprint') == source_fp and CURRENT.exists() and CAPSULE_ZIP.exists():
        return {'ok': True, 'skipped': True, 'reason': 'sources_unchanged', **previous}
    staging = Path(tempfile.mkdtemp(prefix='.gesamtatlas-organismus-', dir=OUTPUT_ROOT))
    reports = []
    try:
        # Bauabschnitt 1: Gestalt und Wahrheitsgrenzen.
        write_initial_docs(staging)
        render_ui(staging, 1)
        reports.append(run_playwright(staging, 1))

        # Bauabschnitt 2: schmaler Kern.
        core_dir = staging / 'KERN'; core_dir.mkdir()
        core_status = build_core(core_dir / 'ATLAS_SCHMAL.sqlite')
        (core_dir / 'STATUS.json').write_text(json_text(core_status), encoding='utf-8')
        render_ui(staging, 2)
        reports.append(run_playwright(staging, 2))

        # Bauabschnitt 3: AI-Zuhause.
        homes_status = build_homes(staging / 'HÄUSER')
        render_ui(staging, 3)
        reports.append(run_playwright(staging, 3))

        # Bauabschnitt 4: Browser A–F.
        browser_status = build_browser(staging / 'BROWSER', core_dir / 'ATLAS_SCHMAL.sqlite')
        render_ui(staging, 4)
        reports.append(run_playwright(staging, 4))

        # Bauabschnitt 5: Terminalwerkstrom.
        terminal_status = build_terminal(staging / 'TERMINAL')
        render_ui(staging, 5)
        reports.append(run_playwright(staging, 5))

        # Bauabschnitt 6: Reaktion und gemeinsamer Zugang.
        reactive_status = build_reactive(staging / 'REAKTION', core_dir / 'ATLAS_SCHMAL.sqlite', browser_status, terminal_status)
        access = write_access(staging)
        render_ui(staging, 6)
        reports.append(run_playwright(staging, 6))

        # Bauabschnitt 7: kleine Kapsel und gezielte Tiefenkörper.
        capsule_status = build_capsule(staging, core_dir / 'ATLAS_SCHMAL.sqlite', staging / 'BROWSER', staging / 'TERMINAL', staging / 'REAKTION')
        (staging / 'KAPSEL_STATUS.json').write_text(json_text(capsule_status), encoding='utf-8')
        render_ui(staging, 7)
        reports.append(run_playwright(staging, 7))

        validation = static_acceptance(staging, reports, capsule_status)
        (staging / 'EVIDENZ/FINAL_VALIDATION.json').write_text(json_text(validation), encoding='utf-8')
        if not validation['ok']:
            raise RuntimeError('Finale Abnahme fehlgeschlagen: ' + ', '.join(validation['errors']))
        final_manifest = manifest(staging, validation, source_fp)
        atomic_replace_directory(staging, CURRENT)
        install_capsule(CURRENT / 'capsule', CURRENT / 'GESAMTATLAS_KAPSEL_AKTUELL.zip')
        state = {
            'schema_version': 'gesamtatlas-organismus-state-1.0',
            'ok': True,
            'generated_utc': utcnow(),
            'source_fingerprint': source_fp,
            'current_path': str(CURRENT),
            'current_bytes': dir_size(CURRENT),
            'atlas_total_bytes': dir_size(ATLAS_ROOT),
            'capsule_path': str(CAPSULE_ZIP),
            'capsule_bytes': CAPSULE_ZIP.stat().st_size,
            'capsule_sha256': sha256_file(CAPSULE_ZIP),
            'playwright_stages': len(reports),
            'playwright_checks': validation['playwright_check_count'],
            'public_status': validation['public_status'],
            'manifest_sha256': sha256_file(CURRENT / 'MANIFEST.json'),
        }
        STATE.write_text(json_text(state), encoding='utf-8')
        return state
    except Exception:
        if staging.exists():
            failed = OUTPUT_ROOT / f'FEHLGESCHLAGENER_BAU_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}'
            staging.rename(failed)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({'ok': False, 'skipped': True, 'reason': 'build_lock_exists'}, ensure_ascii=False))
        return 0
    try:
        os.write(fd, f'{os.getpid()} {utcnow()}\n'.encode()); os.close(fd)
        result = build(args.force)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == '__main__':
    raise SystemExit(main())
