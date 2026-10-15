from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TOOL_ROOT = Path(__file__).resolve().parent
ATLAS_ROOT = Path('/root/werkraum/_gpt/gesamtatlas')
OUTPUT_ROOT = ATLAS_ROOT / 'dateikoerper'
CURRENT_DIR = OUTPUT_ROOT / 'AKTUELL'
ZIP_PATH = OUTPUT_ROOT / 'GESAMTATLAS_DATEIKOERPER_AKTUELL.zip'
STABLE_ZIP = ATLAS_ROOT / 'GESAMTATLAS_DATEIKOERPER_AKTUELL.zip'
STATE_PATH = OUTPUT_ROOT / 'LETZTER_BAU.json'
LOCK_PATH = OUTPUT_ROOT / '.build.lock'
MAX_TEXT_BYTES = 120_000_000
TEXT_SUFFIXES = {
    '.md', '.txt', '.json', '.jsonl', '.yaml', '.yml', '.toml', '.ini', '.cfg',
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.sh', '.sql', '.csv',
    '.xml', '.log', '.ndjson', '.rst', '.conf', '.service', '.timer', '.path',
}
EXCLUDE_PARTS = {
    '.git', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'venv', '.venv', 'site-packages', 'dist', '.cache', 'cache', 'tmp', '.tmp',
}
DENIED_NAMES = {
    '.env', 'auth.json', 'oauth_creds.json', 'credentials.json', 'id_rsa', 'id_ed25519',
    'private_key', 'secrets.json', 'cookies.json', 'cookie.json', 'token.json',
}
DENIED_FRAGMENTS = ('credential', 'secret', 'private-key', 'private_key', 'oauth', 'cookie')

SECRET_PATTERNS = [
    (re.compile(r'(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+\-/=]{12,}'), r'\1[GEHEIMNIS ENTFERNT]'),
    (re.compile(r'(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\s*[:=]\s*["\']?)[^\s"\',}]{6,}'), r'\1[GEHEIMNIS ENTFERNT]'),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'), '[PRIVATER SCHLÜSSEL ENTFERNT]'),
    (re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'), '[API-SCHLÜSSEL ENTFERNT]'),
    (re.compile(r'(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])', re.I), '[E-MAIL-ADRESSE IN AUSSENKOPIE ENTFERNT]'),
    (re.compile(r'\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b', re.I), '[IBAN-ARTIGE ANGABE IN AUSSENKOPIE ENTFERNT]'),
    (re.compile(r'(?<!\w)(?:\+\d{1,3}|0\d{2,5})[\s()./\-]*(?:\d[\s()./\-]*){5,12}\d(?!\w)'), '[TELEFONNUMMER IN AUSSENKOPIE ENTFERNT]'),
]

@dataclass(frozen=True)
class RootSpec:
    root_id: str
    title: str
    path: Path
    section: str
    description: str

ROOTS = [
    RootSpec('atlas', 'Gesamtatlas-Kern', ATLAS_ROOT, '02_ATLAS_UND_MASCHINENKOERPER', 'Register, Aufträge, Übergaben, Status- und Beziehungskörper.'),
    RootSpec('ui_chats', 'Browser-Gesprächskörper', Path('/root/werkraum/_gpt/ui_visible_conversations'), '04_BROWSER_GESPRAECHE', 'Aufgenommene und importierte UI-Gespräche mit Lücken- und Herkunftsmarkern.'),
    RootSpec('home_chatgpt', 'ChatGPT/MCP-Zuhause', Path('/root/werkraum/_gpt/mcp_zuhause'), '03_AI_ZUHAUSE', 'Orientierungs-, Arbeits- und Kontinuitätskörper des MCP-Zugangs.'),
    RootSpec('home_claude', 'Claude-Zuhause', Path('/root/werkraum/_claude'), '03_AI_ZUHAUSE', 'Claudes Zuhause, Notizen, Karten und Resonanzfelder.'),
    RootSpec('home_codex', 'Codex-Zuhause', Path('/root/werkraum/_codex'), '03_AI_ZUHAUSE', 'Codex-Zuhause und importierte Referenzkörper mit eigener Herkunft.'),
    RootSpec('home_gemini', 'Gemini-Zuhause', Path('/root/werkraum/_gemini'), '03_AI_ZUHAUSE', 'Gemini-Zuhause und zugeordnete Gedächtnis- und Arbeitskörper.'),
    RootSpec('home_kimi', 'Kimi-Zuhause', Path('/root/werkraum/_kimi'), '03_AI_ZUHAUSE', 'Kimi-Zuhause und zugeordnete Notizen und Karten.'),
    RootSpec('home_glm', 'GLM-Zuhause', Path('/root/werkraum/_glm'), '03_AI_ZUHAUSE', 'GLM-Zuhause und vorhandene Arbeitsnotizen.'),
    RootSpec('terminal_claude', 'Claude-Terminalwerkstrom', Path('/root/.claude/projects/-root'), '05_TERMINAL_WERKSTROEME', 'Native Claude-Code-Sitzungen und sichtbare Tool- und Gesprächsspuren.'),
    RootSpec('terminal_codex', 'Codex-Terminalwerkstrom', Path('/root/.codex/sessions'), '05_TERMINAL_WERKSTROEME', 'Native Codex-Rollouts und chronologische Arbeitsspuren.'),
    RootSpec('terminal_gemini', 'Gemini-Terminalwerkstrom', Path('/root/.gemini/antigravity-cli/brain'), '05_TERMINAL_WERKSTROEME', 'Native Gemini-CLI-Transkripte und Arbeitskörper.'),
    RootSpec('browser_recorder', 'Browser-Recorder', Path('/root/werkraum/tools/chatgpt_browser_recorder'), '06_WERKZEUGE_DOKUMENTATION_UND_FEHLSPUREN', 'Recorder-Code, Tests, Exportformate und Experimentkörper.'),
    RootSpec('action_history', 'Action-History', Path('/root/werkraum/tools/action_history'), '06_WERKZEUGE_DOKUMENTATION_UND_FEHLSPUREN', 'Technische Sitzungs-, Zeit- und Provenienzwerkzeuge.'),
    RootSpec('public_web_historical', 'Historische Webfehlrichtung', Path('/root/werkraum/tools/gesamtatlas_world'), '06_WERKZEUGE_DOKUMENTATION_UND_FEHLSPUREN', 'Erhaltene, aber deaktivierte Website-Umsetzung als nachvollziehbare Fehlspur.'),
]

STAGE_ROOTS = {
    2: {'atlas'},
    3: {'home_chatgpt', 'home_claude', 'home_codex', 'home_gemini', 'home_kimi', 'home_glm'},
    4: {'ui_chats'},
    5: {'terminal_claude', 'terminal_codex', 'terminal_gemini'},
    6: {'browser_recorder', 'action_history', 'public_web_historical'},
}

CSS = '''
:root{color-scheme:dark;--bg:#0c0912;--panel:#171120;--ink:#f3eafa;--muted:#beaecd;--line:#4b3b5c;--accent:#c89cff;--soft:#2a1d38;--ok:#9de3bd;--warn:#ffd38b}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 15% 0,#251536 0,#0c0912 45%);color:var(--ink);font:17px/1.55 system-ui,sans-serif}main,header,footer{max-width:1180px;margin:auto;padding:1.2rem}nav{display:flex;gap:.6rem;flex-wrap:wrap}a{color:#dfbdff}nav a,.button{border:1px solid var(--line);padding:.55rem .8rem;border-radius:999px;text-decoration:none;background:#171120}.hero{padding:3rem 0 2rem}.hero h1{font-size:clamp(2.4rem,7vw,5.5rem);line-height:.96;margin:.2rem 0 1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}.card{background:linear-gradient(145deg,#1b1325,#120d19);border:1px solid var(--line);border-radius:18px;padding:1rem;overflow-wrap:anywhere}.number{font-size:2rem;font-weight:800;color:var(--accent)}.muted{color:var(--muted)}.path{font-family:ui-monospace,monospace;font-size:.84rem;overflow-wrap:anywhere}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.15rem .5rem;margin:.15rem;color:var(--muted)}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid var(--line);padding:.55rem;vertical-align:top}input{width:100%;padding:.8rem;border-radius:12px;border:1px solid var(--line);background:#0f0b15;color:var(--ink)}pre{white-space:pre-wrap;overflow-wrap:anywhere}.notice{border-left:4px solid var(--warn);padding:1rem;background:#241b1c;border-radius:10px}@media(max-width:520px){body{font-size:15px}main,header,footer{padding:.85rem}th:nth-child(3),td:nth-child(3){display:none}}
'''


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def redact(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in SECRET_PATTERNS:
        text, found = pattern.subn(replacement, text)
        count += found
    return text, count


def denied(path: Path) -> str | None:
    parts = {part.lower() for part in path.parts}
    if parts & EXCLUDE_PARTS:
        return 'excluded_directory_class'
    name = path.name.lower()
    if name in DENIED_NAMES or any(fragment in name for fragment in DENIED_FRAGMENTS):
        return 'possible_secret_or_credential_file'
    if path == OUTPUT_ROOT or OUTPUT_ROOT in path.parents:
        return 'self_generated_output'
    if path.name.endswith(('.tmp', '.swp', '~')):
        return 'temporary_file'
    return None


def iter_entries(spec: RootSpec) -> Iterable[Path]:
    if not spec.path.exists():
        return
    for base, directories, files in os.walk(spec.path, followlinks=False):
        base_path = Path(base)
        directories[:] = [name for name in sorted(directories) if denied(base_path / name) is None]
        for name in sorted(files):
            yield base_path / name
        for name in sorted(directories):
            candidate = base_path / name
            if candidate.is_symlink():
                yield candidate


def rel_export_path(spec: RootSpec, source: Path) -> Path:
    relative = source.relative_to(spec.path)
    return Path(spec.section) / 'QUELLKOERPER' / spec.root_id / relative


def file_object_id(spec: RootSpec, relative: str) -> str:
    return 'file:' + hashlib.sha256(f'{spec.root_id}:{relative}'.encode()).hexdigest()[:24]


def copy_source(spec: RootSpec, source: Path, staging: Path) -> dict[str, Any]:
    relative = source.relative_to(spec.path).as_posix()
    before = source.lstat()
    record: dict[str, Any] = {
        'schema_version': '1.0',
        'object_id': file_object_id(spec, relative),
        'root_id': spec.root_id,
        'root_title': spec.title,
        'source_path': str(source),
        'relative_path': relative,
        'source_size': before.st_size,
        'source_mtime_ns': before.st_mtime_ns,
        'source_kind': 'symlink' if source.is_symlink() else 'file',
        'section': spec.section,
        'exported_path': None,
        'copy_class': None,
        'read_status': 'not_read',
        'redactions': 0,
        'omission_reason': None,
    }
    if source.is_symlink():
        record['symlink_target'] = os.readlink(source)
        record['copy_class'] = 'metadata_only'
        record['omission_reason'] = 'symlink_not_followed'
        return record
    reason = denied(source)
    if reason:
        record['copy_class'] = 'metadata_only'
        record['omission_reason'] = reason
        return record
    suffix = source.suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        record['copy_class'] = 'metadata_only'
        record['omission_reason'] = 'binary_or_unsupported_format'
        try:
            record['source_sha256'] = sha_file(source)
        except OSError as exc:
            record['read_error'] = str(exc)
        return record
    if before.st_size > MAX_TEXT_BYTES:
        record['copy_class'] = 'metadata_only'
        record['omission_reason'] = f'text_file_over_{MAX_TEXT_BYTES}_bytes'
        try:
            record['source_sha256'] = sha_file(source)
        except OSError as exc:
            record['read_error'] = str(exc)
        return record
    try:
        payload = source.read_bytes()
        record['source_sha256'] = sha_bytes(payload)
        text = payload.decode('utf-8', errors='replace')
        decode_replacements = text.count('\ufffd')
        redacted, redactions = redact(text)
        target_rel = rel_export_path(spec, source)
        target = staging / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if redactions == 0 and decode_replacements == 0:
            target.write_bytes(payload)
            copy_class = 'exact_byte_copy'
        else:
            target.write_text(redacted, encoding='utf-8')
            copy_class = 'external_copy_with_marked_omissions' if redactions else 'utf8_replacement_copy'
        record.update({
            'exported_path': target_rel.as_posix(),
            'exported_sha256': sha_file(target),
            'exported_size': target.stat().st_size,
            'copy_class': copy_class,
            'read_status': 'fully_read_for_export',
            'redactions': redactions,
            'decode_replacements': decode_replacements,
        })
        after = source.stat()
        record['changed_during_read'] = before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns
        return record
    except Exception as exc:
        record['copy_class'] = 'metadata_only'
        record['omission_reason'] = 'read_or_export_error'
        record['read_error'] = f'{type(exc).__name__}: {exc}'
        return record


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')


def export_sqlite_metadata(staging: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    db_specs = [
        ('PFADINDEX', ATLAS_ROOT / 'PFADINDEX.sqlite'),
        ('BEGRIFFSINDEX', ATLAS_ROOT / 'BEGRIFFSINDEX.sqlite'),
        ('BEZIEHUNGSREGISTER', ATLAS_ROOT / 'BEZIEHUNGSREGISTER.sqlite'),
    ]
    reports: list[dict[str, Any]] = []
    target_root = staging / '02_ATLAS_UND_MASCHINENKOERPER' / 'SQLITE_EXPORT'
    target_root.mkdir(parents=True, exist_ok=True)
    for label, source in db_specs:
        report: dict[str, Any] = {'database': label, 'source_path': str(source), 'tables': [], 'ok': False}
        if not source.exists():
            report['error'] = 'missing'
            reports.append(report)
            continue
        report['source_size'] = source.stat().st_size
        report['source_sha256'] = sha_file(source)
        try:
            connection = sqlite3.connect(f'file:{source}?mode=ro', uri=True, timeout=20)
            connection.row_factory = sqlite3.Row
            tables = [row[0] for row in connection.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
            for table in tables:
                columns = [row[1] for row in connection.execute(f'pragma table_info("{table}")')]
                selected = [column for column in columns if not any(term in column.lower() for term in ('content', 'body', 'fulltext', 'raw_text'))]
                if not selected:
                    selected = columns[:8]
                count = int(connection.execute(f'select count(*) from "{table}"').fetchone()[0])
                out = target_root / label / f'{table}.jsonl'
                out.parent.mkdir(parents=True, exist_ok=True)
                with out.open('w', encoding='utf-8') as stream:
                    query = 'select ' + ','.join(f'"{column}"' for column in selected) + f' from "{table}"'
                    for row in connection.execute(query):
                        item = {}
                        redactions = 0
                        for column in selected:
                            value = row[column]
                            if isinstance(value, str):
                                value, found = redact(value)
                                redactions += found
                            elif isinstance(value, bytes):
                                value = {'bytes': len(value), 'sha256': sha_bytes(value)}
                            item[column] = value
                        if redactions:
                            item['_redactions'] = redactions
                        stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')
                report['tables'].append({'name': table, 'rows': count, 'exported_columns': selected, 'exported_path': out.relative_to(staging).as_posix(), 'bytes': out.stat().st_size})
            connection.close()
            report['ok'] = True
        except Exception as exc:
            report['error'] = f'{type(exc).__name__}: {exc}'
        reports.append(report)
    (target_root / 'SQLITE_EXPORT_STATUS.json').write_text(safe_json({'generated_utc': utcnow(), 'databases': reports}), encoding='utf-8')
    return reports


def write_docs(staging: Path) -> None:
    docs = staging / '00_START_HIER'
    docs.mkdir(parents=True, exist_ok=True)
    correction = '''# Daniel-Korrektur: Kein öffentlicher Gesamtatlas\n\n**Status:** direkte Nutzerkorrektur aus der aktuellen ChatGPT-Sitzung; noch kein vollständiger Browserexport dieser Sitzung.\n\n> ja es gab wider probleme bei openai und zeitüberschreitung und so und etwas hier von chatverlauf in ui wurde entfernt du hast abgeblic auch schon\n>\n> https://flextrawurst.de/gesamtatlas/\n>\n> eröffnet das wollte ich nie ich wollte nur einenfür externe menschen und llms komplett durchdringbaren dateikörperim besten fall den ich mir dann schnell zippe und runterladen kann der immer aktuell ist\n\nDie öffentliche Route wurde am 29. Juli 2026 entfernt. Der Gesamtatlas wird als lokaler, automatisch aktualisierter Dateikörper erzeugt.\n'''
    (docs / '00_DANIEL_KORREKTUR.md').write_text(correction, encoding='utf-8')
    (docs / '01_START_HIER.md').write_text('''# Gesamtatlas-Dateikörper\n\nDies ist kein öffentliches Webangebot. Dies ist ein tragbarer, durchsuchbarer und regelmäßig erneuerter Dateikörper für Menschen und fremde LLMs.\n\nDu darfst überall beginnen:\n\n- `01_VERSTAENDNIS/` erklärt das Ganze in mehreren Tiefen.\n- `02_ATLAS_UND_MASCHINENKOERPER/` enthält Register, JSONL-Indizes und SQLite-Exporte.\n- `03_AI_ZUHAUSE/` spiegelt die getrennten Häuser der AI-Ströme.\n- `04_BROWSER_GESPRAECHE/` enthält Browser-Gesprächskörper und Lückenmarker.\n- `05_TERMINAL_WERKSTROEME/` enthält native Coding-Agenten-Verläufe.\n- `06_WERKZEUGE_DOKUMENTATION_UND_FEHLSPUREN/` zeigt Recorder, Action-History und die deaktivierte Webfehlrichtung.\n- `07_LUECKEN_UND_ABDECKUNG/` zeigt Auslassungen, Fehler und nicht vollständig erfassbare Bereiche.\n- `OFFLINE/index.html` ist eine lokale, nicht öffentliche Erkundungsoberfläche.\n\nJede Quellkopie besitzt im `QUELLENMANIFEST.jsonl` ihren Ursprungspfad, Ursprungshash, Exporthash und ihre Kopierklasse. Markierte Auslassungen werden nicht als unveränderte Originale ausgegeben.\n''', encoding='utf-8')
    understanding = staging / '01_VERSTAENDNIS'
    understanding.mkdir(parents=True, exist_ok=True)
    (understanding / 'ELI10.md').write_text('''# ELI10\n\nStell dir den VPS als riesige Stadt vor. Projekte sind Gebäude, Dateien sind Fundstücke, Chats sind Räume und jede AI hat ein eigenes Zuhause. Dieser ZIP-Körper packt eine erforschbare Kopie der Stadt in einen Koffer. Zu jedem Fundstück steht dabei, woher es kam, ob es exakt kopiert wurde und ob etwas für die Außenweitergabe sichtbar entfernt werden musste.\n''', encoding='utf-8')
    (understanding / 'WAS_ES_IST.md').write_text('''# Was dieser Körper ist\n\n**[ABLEITUNG]** Eine portable, selbstbeschreibende Außenkopie des Gesamtatlas. Sie verbindet Erklärung, Quellkopien, Herkunftsmanifest, Projekte, AI-Zuhause, Browsergespräche, Terminalwerkströme, Beziehungen und Lücken. Sie ist für Menschen lesbar und für LLMs über Markdown, JSON, JSONL und stabile Pfade vollständig maschinell durchsuchbar.\n''', encoding='utf-8')
    (understanding / 'WAS_ES_KANN.md').write_text('''# Was er kann\n\n- Inhalte und Pfade ohne Server durchsuchen.\n- Zu jeder eingebetteten Datei Ursprung, Hash, Kopierklasse und Auslassungen zeigen.\n- Browser- und Terminalarbeit chronologisch zugänglich machen.\n- Getrennte AI-Zuhause gemeinsam erforschbar machen.\n- Lücken und nicht eingebettete Binärkörper ausdrücklich benennen.\n- Nach dem Entpacken lokal über `OFFLINE/index.html` erkundet werden.\n''', encoding='utf-8')
    (understanding / 'WAS_ES_NICHT_KANN.md').write_text('''# Was er nicht kann\n\n- Historisch nie aufgenommene Inhalte nachträglich als Original erfinden.\n- Vollständig automatisch erkennen, welche Namen oder indirekten sozialen Zusammenhänge zu fremden Personen gehören.\n- Aus Erreichbarkeit tatsächliches Lesen ableiten.\n- Aus mehreren Kopien derselben Quelle unabhängigen Konsens machen.\n- Jede Binärdatei sinnvoll in einem kompakten Außen-ZIP wiedergeben. Solche Körper bleiben im Manifest sichtbar.\n''', encoding='utf-8')
    (understanding / 'ERKUNDEN_STATT_REGELKOFFFER.md').write_text('''# Erkunden statt Regelkoffer\n\nEs gibt keine vorgeschriebene Lesereihenfolge. Beginne bei einer AI, einem Gespräch, einer Datei, einem Fehler, einem Projekt oder einer offenen Lücke. Die technischen Constraints arbeiten als Tragwerk im Hintergrund; die sichtbare Gestalt bleibt einladend, offen und ergebnisorientiert.\n''', encoding='utf-8')


def root_info(spec: RootSpec, rows: list[dict[str, Any]], staging: Path) -> None:
    root_dir = staging / spec.section / 'QUELLKOERPER' / spec.root_id
    root_dir.mkdir(parents=True, exist_ok=True)
    included = sum(1 for row in rows if row['root_id'] == spec.root_id and row.get('exported_path'))
    omitted = sum(1 for row in rows if row['root_id'] == spec.root_id and not row.get('exported_path'))
    exact = sum(1 for row in rows if row['root_id'] == spec.root_id and row.get('copy_class') == 'exact_byte_copy')
    redacted = sum(1 for row in rows if row['root_id'] == spec.root_id and row.get('redactions'))
    info = {
        'root_id': spec.root_id,
        'title': spec.title,
        'source_path': str(spec.path),
        'section': spec.section,
        'description': spec.description,
        'source_exists': spec.path.exists(),
        'included_files': included,
        'omitted_or_metadata_only': omitted,
        'exact_byte_copies': exact,
        'files_with_marked_redactions': redacted,
    }
    (root_dir / '_ROOT_INFO.json').write_text(safe_json(info), encoding='utf-8')


def build_luecken(staging: Path, records: list[dict[str, Any]], root_specs: list[RootSpec], sqlite_reports: list[dict[str, Any]]) -> dict[str, Any]:
    missing_roots = [str(spec.path) for spec in root_specs if not spec.path.exists()]
    omitted = [row for row in records if not row.get('exported_path')]
    redacted = [row for row in records if row.get('redactions')]
    raced = [row for row in records if row.get('changed_during_read')]
    errors = [row for row in records if row.get('read_error')]
    report = {
        'generated_utc': utcnow(),
        'missing_roots': missing_roots,
        'source_objects_seen': len(records),
        'content_copies_embedded': len(records) - len(omitted),
        'metadata_only_or_omitted': len(omitted),
        'files_with_marked_redactions': len(redacted),
        'files_changed_during_read': len(raced),
        'read_or_export_errors': len(errors),
        'sqlite_exports': sqlite_reports,
        'known_boundary': 'Namen, Rollen und indirekte soziale Zusammenhänge fremder Personen können nicht vollständig automatisch erkannt werden. Der Körper ist deshalb tief prüfbar, aber eine externe Veröffentlichung bleibt menschlich hinterfragbar.',
        'omission_reasons': {},
    }
    for row in omitted:
        key = row.get('omission_reason') or 'unknown'
        report['omission_reasons'][key] = report['omission_reasons'].get(key, 0) + 1
    target = staging / '07_LUECKEN_UND_ABDECKUNG'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'LUECKENREGISTER.json').write_text(safe_json(report), encoding='utf-8')
    md = ['# Lücken- und Abdeckungsregister', '', f"- Gesehene Quellobjekte: **{len(records):,}**", f"- Eingebettete Inhaltskopien: **{report['content_copies_embedded']:,}**", f"- Nur Metadaten oder ausgelassen: **{len(omitted):,}**", f"- Dateien mit markierten Auslassungen: **{len(redacted):,}**", f"- Während der Aufnahme verändert: **{len(raced):,}**", f"- Lese- oder Exportfehler: **{len(errors):,}**", '', '## Bekannte Grenze', '', report['known_boundary'], '', '## Auslassungsgründe', '']
    for key, count in sorted(report['omission_reasons'].items()):
        md.append(f'- `{key}`: {count:,}')
    (target / 'LUECKENREGISTER.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    write_jsonl(target / 'AUSGELASSENE_ODER_NUR_KARTIERTE_KOERPER.jsonl', omitted)
    write_jsonl(target / 'MARKIERTE_AUSLASSUNGEN.jsonl', redacted)
    write_jsonl(target / 'WAEREND_AUFNAHME_VERAENDERT.jsonl', raced)
    write_jsonl(target / 'LESEFEHLER.jsonl', errors)
    return report


def make_search_index(records: list[dict[str, Any]], staging: Path) -> list[dict[str, Any]]:
    rows = []
    for row in records:
        if not row.get('exported_path'):
            continue
        preview = ''
        target = staging / row['exported_path']
        try:
            preview = target.read_text('utf-8', errors='replace')[:700].replace('\n', ' ')
        except Exception:
            pass
        rows.append({
            'object_id': row['object_id'],
            'root_id': row['root_id'],
            'title': Path(row['relative_path']).name,
            'relative_path': row['relative_path'],
            'exported_path': row['exported_path'],
            'copy_class': row['copy_class'],
            'preview': preview,
        })
    machine = staging / '02_ATLAS_UND_MASCHINENKOERPER'
    machine.mkdir(parents=True, exist_ok=True)
    write_jsonl(machine / 'SUCHINDEX.jsonl', rows)
    return rows


def page(title: str, body: str, nav_links: str = '') -> str:
    return f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · Gesamtatlas-Dateikörper</title><style>{CSS}</style></head><body><header><nav><a href="index.html">Start</a><a href="suche.html">Suche</a><a href="luecken.html">Lücken</a>{nav_links}</nav></header><main>{body}</main><footer><p class="muted">Lokale Offline-Erkundung. Keine öffentliche Website.</p></footer></body></html>'''


def render_offline(staging: Path, stage: int, records: list[dict[str, Any]], search_rows: list[dict[str, Any]] | None = None, gap_report: dict[str, Any] | None = None) -> None:
    offline = staging / 'OFFLINE'
    sections = offline / 'sektionen'
    offline.mkdir(parents=True, exist_ok=True)
    sections.mkdir(parents=True, exist_ok=True)
    summaries = []
    for spec in ROOTS:
        seen = [row for row in records if row['root_id'] == spec.root_id]
        if not seen and stage < min((key for key, ids in STAGE_ROOTS.items() if spec.root_id in ids), default=7):
            continue
        included = [row for row in seen if row.get('exported_path')]
        summaries.append({'spec': spec, 'seen': len(seen), 'included': len(included), 'omitted': len(seen) - len(included)})
        items = []
        for row in seen:
            if row.get('exported_path'):
                href = '../../' + row['exported_path']
                link = f'<a href="{html.escape(href, quote=True)}">{html.escape(row["relative_path"])}</a>'
            else:
                link = html.escape(row['relative_path'])
            items.append(f'<tr><td>{link}</td><td>{html.escape(str(row.get("copy_class")))}</td><td>{html.escape(str(row.get("omission_reason") or ""))}</td></tr>')
        body = f'<section class="hero"><p class="muted">{html.escape(spec.section)}</p><h1>{html.escape(spec.title)}</h1><p>{html.escape(spec.description)}</p><div class="grid"><div class="card"><div class="number">{len(seen):,}</div><p>kartierte Körper</p></div><div class="card"><div class="number">{len(included):,}</div><p>eingebettete Inhaltskopien</p></div></div></section><section><table><thead><tr><th>Pfad</th><th>Kopierklasse</th><th>Auslassung</th></tr></thead><tbody>{"".join(items)}</tbody></table></section>'
        (sections / f'{spec.root_id}.html').write_text(page(spec.title, body), encoding='utf-8')
    cards = []
    for summary in summaries:
        spec = summary['spec']
        cards.append(f'<a class="card" href="sektionen/{spec.root_id}.html"><h2>{html.escape(spec.title)}</h2><div class="number">{summary["included"]:,}</div><p>{html.escape(spec.description)}</p><span class="pill">{summary["omitted"]:,} nur kartiert</span></a>')
    body = f'''<section class="hero"><p class="muted">Bauabschnitt {stage} von 7</p><h1>Gesamtatlas als <span style="color:var(--accent)">Dateikörper.</span></h1><p>Offen, explorativ, originalgebunden und lokal durchsuchbar. Keine öffentliche Webroute.</p><div class="grid"><div class="card"><div class="number">{len(records):,}</div><p>kartierte Quellobjekte</p></div><div class="card"><div class="number">{sum(1 for row in records if row.get('exported_path')):,}</div><p>eingebettete Inhaltskopien</p></div></div></section><section class="grid">{''.join(cards)}</section><section class="notice"><strong>Originaltreue:</strong> Exakte Kopien und markiert redigierte Außenkopien bleiben über das Quellenmanifest unterscheidbar.</section>'''
    (offline / 'index.html').write_text(page('Start', body), encoding='utf-8')
    if search_rows is not None:
        search_payload = json.dumps(search_rows, ensure_ascii=False).replace('</', '<\\/')
        search_body = f'''<section class="hero"><h1>Lokale Suche</h1><p>Die Suche arbeitet nur im entpackten Dateikörper.</p><input id="q" placeholder="Begriff, Pfad, Datei oder AI-Strom" autocomplete="off"><p id="count" class="muted"></p><div id="results" class="grid"></div></section><script>const DATA={search_payload};const q=document.getElementById('q'),out=document.getElementById('results'),count=document.getElementById('count');function esc(s){{return String(s).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}function run(){{const n=q.value.trim().toLowerCase();const rows=n?DATA.filter(x=>(x.title+' '+x.relative_path+' '+x.preview+' '+x.root_id).toLowerCase().includes(n)).slice(0,200):[];count.textContent=rows.length+' Treffer sichtbar';out.innerHTML=rows.map(x=>'<a class="card" href="../'+encodeURI(x.exported_path)+'"><h2>'+esc(x.title)+'</h2><p class="path">'+esc(x.relative_path)+'</p><p>'+esc(x.preview.slice(0,300))+'</p><span class="pill">'+esc(x.copy_class)+'</span></a>').join('')}}q.addEventListener('input',run);</script>'''
        (offline / 'suche.html').write_text(page('Suche', search_body), encoding='utf-8')
    else:
        (offline / 'suche.html').write_text(page('Suche', '<section class="hero"><h1>Suche entsteht im letzten Bauabschnitt</h1></section>'), encoding='utf-8')
    if gap_report is not None:
        gap_body = f'''<section class="hero"><h1>Lücken und Abdeckung</h1><div class="grid"><div class="card"><div class="number">{gap_report['content_copies_embedded']:,}</div><p>eingebettet</p></div><div class="card"><div class="number">{gap_report['metadata_only_or_omitted']:,}</div><p>nur kartiert oder ausgelassen</p></div><div class="card"><div class="number">{gap_report['files_with_marked_redactions']:,}</div><p>mit markierten Auslassungen</p></div></div><div class="notice">{html.escape(gap_report['known_boundary'])}</div></section>'''
        (offline / 'luecken.html').write_text(page('Lücken', gap_body), encoding='utf-8')
    else:
        (offline / 'luecken.html').write_text(page('Lücken', '<section class="hero"><h1>Lückenregister entsteht im letzten Bauabschnitt</h1></section>'), encoding='utf-8')


def run_playwright(staging: Path, stage: int) -> dict[str, Any]:
    report = staging / 'EVIDENZ' / f'BAUABSCHNITT_{stage:02d}_PLAYWRIGHT.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    port = 18220 + stage
    server_log = staging / 'EVIDENZ' / f'BAUABSCHNITT_{stage:02d}_HTTP.log'
    with server_log.open('w', encoding='utf-8') as log:
        server = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(staging)], stdout=log, stderr=subprocess.STDOUT)
    try:
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                import urllib.request
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/OFFLINE/index.html', timeout=1):
                    break
            except Exception:
                time.sleep(.15)
        env = os.environ.copy()
        env.update({'ATLAS_BASE': f'http://127.0.0.1:{port}', 'ATLAS_STAGE': str(stage), 'ATLAS_REPORT': str(report)})
        result = subprocess.run(['node', str(TOOL_ROOT / 'tests/stage_test.js')], env=env, capture_output=True, text=True, timeout=90)
        (staging / 'EVIDENZ' / f'BAUABSCHNITT_{stage:02d}_PLAYWRIGHT.stdout').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode != 0:
            raise RuntimeError(f'Playwright stage {stage} failed: {result.stdout[-1000:]} {result.stderr[-1000:]}')
        data = json.loads(report.read_text('utf-8'))
        if not data.get('ok'):
            raise RuntimeError(f'Playwright stage {stage} not green')
        return data
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


def source_fingerprint() -> str:
    h = hashlib.sha256()
    for spec in ROOTS:
        h.update(f'ROOT\0{spec.root_id}\0{spec.path}\0'.encode())
        if not spec.path.exists():
            h.update(b'MISSING\0')
            continue
        for source in iter_entries(spec):
            try:
                stat = source.lstat()
                relative = source.relative_to(spec.path).as_posix()
                h.update(f'{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\0'.encode())
            except OSError:
                continue
    return h.hexdigest()


def build(*, verify_sections: bool, force: bool, final_playwright: bool) -> dict[str, Any]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    fingerprint = source_fingerprint()
    previous = {}
    if STATE_PATH.exists():
        try:
            previous = json.loads(STATE_PATH.read_text('utf-8'))
        except Exception:
            previous = {}
    if not force and previous.get('source_fingerprint') == fingerprint and ZIP_PATH.exists() and CURRENT_DIR.exists():
        return {'ok': True, 'skipped': True, 'reason': 'source_fingerprint_unchanged', 'zip': str(ZIP_PATH), 'source_fingerprint': fingerprint}
    staging = Path(tempfile.mkdtemp(prefix='.gesamtatlas-dateikoerper-', dir=OUTPUT_ROOT))
    records: list[dict[str, Any]] = []
    playwright_reports = []
    started = utcnow()
    try:
        write_docs(staging)
        render_offline(staging, 1, records)
        if verify_sections:
            playwright_reports.append(run_playwright(staging, 1))
        sqlite_reports: list[dict[str, Any]] = []
        for stage in range(2, 7):
            for spec in ROOTS:
                if spec.root_id not in STAGE_ROOTS[stage]:
                    continue
                if spec.path.exists():
                    for source in iter_entries(spec):
                        records.append(copy_source(spec, source, staging))
                root_info(spec, records, staging)
            if stage == 2:
                sqlite_reports = export_sqlite_metadata(staging, records)
            write_jsonl(staging / '02_ATLAS_UND_MASCHINENKOERPER' / 'QUELLENMANIFEST_TEILSTAND.jsonl', records)
            render_offline(staging, stage, records)
            if verify_sections:
                playwright_reports.append(run_playwright(staging, stage))
        search_rows = make_search_index(records, staging)
        gap_report = build_luecken(staging, records, ROOTS, sqlite_reports)
        machine = staging / '02_ATLAS_UND_MASCHINENKOERPER'
        write_jsonl(machine / 'QUELLENMANIFEST.jsonl', records)
        objects = [{key: row.get(key) for key in ('object_id', 'root_id', 'relative_path', 'exported_path', 'copy_class', 'source_sha256', 'exported_sha256')} for row in records]
        write_jsonl(machine / 'OBJECTS.jsonl', objects)
        roots_json = [{'root_id': spec.root_id, 'title': spec.title, 'source_path': str(spec.path), 'section': spec.section, 'description': spec.description, 'exists': spec.path.exists()} for spec in ROOTS]
        (machine / 'ROOTS.json').write_text(safe_json({'generated_utc': utcnow(), 'roots': roots_json}), encoding='utf-8')
        render_offline(staging, 7, records, search_rows, gap_report)
        if verify_sections or final_playwright:
            playwright_reports.append(run_playwright(staging, 7))
        manifest_rows = []
        for path in sorted(staging.rglob('*')):
            if not path.is_file() or path.name in {'MANIFEST.json', 'SHA256SUMS.txt'}:
                continue
            manifest_rows.append({'path': path.relative_to(staging).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha_file(path)})
        final_manifest = {
            'schema_version': '1.0',
            'kind': 'external_human_and_llm_traversable_file_body',
            'generated_utc': utcnow(),
            'build_started_utc': started,
            'source_fingerprint': fingerprint,
            'public_website': False,
            'source_objects_seen': len(records),
            'embedded_content_copies': sum(1 for row in records if row.get('exported_path')),
            'exact_byte_copies': sum(1 for row in records if row.get('copy_class') == 'exact_byte_copy'),
            'copies_with_marked_omissions': sum(1 for row in records if row.get('redactions')),
            'metadata_only_or_omitted': sum(1 for row in records if not row.get('exported_path')),
            'playwright_sections': playwright_reports,
            'files': manifest_rows,
            'truth_boundary': [
                'Der Dateikörper enthält tief eingebettete Textquellen und vollständige Metadaten über ausgelassene oder binäre Körper.',
                'Markierte Außenkopien sind keine unveränderten Originale; Ursprungshash und Exporthash bleiben getrennt.',
                'Fremde Namen und indirekte soziale Beziehungen können nicht vollständig automatisch erkannt werden.',
                'Historisch nie erfasste Inhalte werden nicht nachträglich erfunden.',
            ],
        }
        (staging / 'MANIFEST.json').write_text(safe_json(final_manifest), encoding='utf-8')
        checks = []
        for path in sorted(staging.rglob('*')):
            if path.is_file() and path.name != 'SHA256SUMS.txt':
                checks.append(f'{sha_file(path)}  {path.relative_to(staging).as_posix()}')
        (staging / 'SHA256SUMS.txt').write_text('\n'.join(checks) + '\n', encoding='utf-8')
        temp_zip = OUTPUT_ROOT / '.GESAMTATLAS_DATEIKOERPER_AKTUELL.zip.tmp'
        if temp_zip.exists():
            temp_zip.unlink()
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path in sorted(staging.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(staging).as_posix())
        with zipfile.ZipFile(temp_zip) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f'ZIP integrity failure: {bad}')
            zip_entries = len(archive.infolist())
        old = OUTPUT_ROOT / '.AKTUELL.previous'
        if old.exists():
            shutil.rmtree(old)
        if CURRENT_DIR.exists():
            CURRENT_DIR.rename(old)
        staging.rename(CURRENT_DIR)
        temp_zip.replace(ZIP_PATH)
        if old.exists():
            shutil.rmtree(old)
        if STABLE_ZIP.exists() or STABLE_ZIP.is_symlink():
            STABLE_ZIP.unlink()
        STABLE_ZIP.symlink_to(ZIP_PATH)
        state = {
            'schema_version': '1.0',
            'ok': True,
            'generated_utc': utcnow(),
            'source_fingerprint': fingerprint,
            'current_directory': str(CURRENT_DIR),
            'zip_path': str(ZIP_PATH),
            'stable_zip_path': str(STABLE_ZIP),
            'zip_bytes': ZIP_PATH.stat().st_size,
            'zip_sha256': sha_file(ZIP_PATH),
            'zip_entries': zip_entries,
            'source_objects_seen': len(records),
            'embedded_content_copies': final_manifest['embedded_content_copies'],
            'playwright_sections_green': len(playwright_reports),
        }
        STATE_PATH.write_text(safe_json(state), encoding='utf-8')
        return state
    except Exception:
        if staging.exists():
            failure = OUTPUT_ROOT / f'FEHLGESCHLAGENER_BAU_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}'
            staging.rename(failure)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-sections', action='store_true')
    parser.add_argument('--final-playwright', action='store_true')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(json.dumps({'ok': False, 'skipped': True, 'reason': 'build_lock_exists'}, ensure_ascii=False))
        return 0
    try:
        os.write(fd, f'{os.getpid()} {utcnow()}\n'.encode())
        os.close(fd)
        result = build(verify_sections=args.verify_sections, force=args.force, final_playwright=args.final_playwright)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    finally:
        LOCK_PATH.unlink(missing_ok=True)


if __name__ == '__main__':
    raise SystemExit(main())
