from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

ATLAS_ROOT = Path('/root/werkraum/_gpt/gesamtatlas')
TOOL_ROOT = Path('/root/werkraum/tools/gesamtatlas_organismus')
OUTPUT_ROOT = ATLAS_ROOT / 'organismus'
CURRENT = OUTPUT_ROOT / 'AKTUELL'
CAPSULE_ZIP = ATLAS_ROOT / 'GESAMTATLAS_KAPSEL_AKTUELL.zip'
CAPSULE_DIR = OUTPUT_ROOT / 'KAPSEL_AKTUELL'
DETAIL_ROOT = OUTPUT_ROOT / 'EXPLORATIONSKOERPER'
CONTRIBUTION_ROOT = ATLAS_ROOT / 'beitraege'
STATE = OUTPUT_ROOT / 'BAUZUSTAND.json'
LOCK = OUTPUT_ROOT / '.build.lock'

MAX_TOTAL_BYTES = 1_500_000_000
MAX_OVERLAY_BYTES = 650_000_000
MAX_CAPSULE_BYTES = 25_000_000
MAX_DETAIL_BYTES = 250_000_000
PREVIEW_CHARS = 900
TEXT_SUFFIXES = {
    '.md', '.txt', '.json', '.jsonl', '.ndjson', '.yaml', '.yml', '.toml', '.ini',
    '.cfg', '.conf', '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.sh',
    '.sql', '.csv', '.xml', '.log', '.service', '.timer', '.path', '.rst',
}
EXCLUDE_PARTS = {
    '.git', 'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.venv', 'venv', 'site-packages', '.cache', 'cache', 'tmp', '.tmp', 'dateikoerper',
    'organismus', 'endprodukt_v1_backup_20260729T153325Z',
}
SECRET_NAME_FRAGMENTS = ('secret', 'credential', 'cookie', 'oauth', 'private_key', 'private-key')
SECRET_NAMES = {'.env', 'auth.json', 'credentials.json', 'cookies.json', 'token.json', 'id_rsa', 'id_ed25519'}

SECRET_PATTERNS = [
    (re.compile(r'(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+\-/=]{12,}'), r'\1[GEHEIMNIS ENTFERNT]'),
    (re.compile(r'(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\s*[:=]\s*["\']?)[^\s"\',}]{6,}'), r'\1[GEHEIMNIS ENTFERNT]'),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'), '[PRIVATER SCHLÜSSEL ENTFERNT]'),
    (re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'), '[API-SCHLÜSSEL ENTFERNT]'),
    (re.compile(r'(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])', re.I), '[E-MAIL-ADRESSE ENTFERNT]'),
    (re.compile(r'\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b', re.I), '[IBAN-ARTIGE ANGABE ENTFERNT]'),
    (re.compile(r'(?<!\w)(?:\+\d{1,3}|0\d{2,5})[\s()./\-]*(?:\d[\s()./\-]*){5,12}\d(?!\w)'), '[TELEFONNUMMER ENTFERNT]'),
]

@dataclass(frozen=True)
class SourceRoot:
    root_id: str
    title: str
    path: Path
    kind: str
    description: str

SOURCE_ROOTS = [
    SourceRoot('atlas', 'Gesamtatlas-Kern', ATLAS_ROOT, 'atlas', 'Register, Indizes, Beziehungen, Übergaben und Aufgaben.'),
    SourceRoot('ui_chats', 'Browser-Gesprächskörper', Path('/root/werkraum/_gpt/ui_visible_conversations'), 'browser', 'Live- und Altchat-Aufnahmen, Experimente und Exporte.'),
    SourceRoot('home_chatgpt', 'ChatGPT/MCP-Zuhause', Path('/root/werkraum/_gpt/mcp_zuhause'), 'home', 'ChatGPT/MCP-Orientierung und Kontinuitätskörper.'),
    SourceRoot('home_claude', 'Claude-Zuhause', Path('/root/werkraum/_claude'), 'home', 'Claudes Zuhause und Resonanzfelder.'),
    SourceRoot('home_codex', 'Codex-Zuhause', Path('/root/werkraum/_codex'), 'home', 'Codex-Zuhause und Resonanzfelder.'),
    SourceRoot('home_gemini', 'Gemini-Zuhause', Path('/root/werkraum/_gemini'), 'home', 'Gemini-Zuhause und Resonanzfelder.'),
    SourceRoot('home_kimi', 'Kimi-Zuhause', Path('/root/werkraum/_kimi'), 'home', 'Kimi-Zuhause und Resonanzfelder.'),
    SourceRoot('home_glm', 'GLM-Zuhause', Path('/root/werkraum/_glm'), 'home', 'GLM-Zuhause und Resonanzfelder.'),
    SourceRoot('terminal_claude', 'Claude-Terminal', Path('/root/.claude/projects/-root'), 'terminal', 'Native Claude-Code-Sitzungen.'),
    SourceRoot('terminal_codex', 'Codex-Terminal', Path('/root/.codex/sessions'), 'terminal', 'Native Codex-Rollouts.'),
    SourceRoot('terminal_gemini', 'Gemini-Terminal', Path('/root/.gemini/antigravity-cli/brain'), 'terminal', 'Native Gemini-CLI-Transkripte.'),
    SourceRoot('terminal_kimi', 'Kimi-Terminal', Path('/root/.kimi'), 'terminal', 'Native Kimi-Sitzungen, sofern vorhanden.'),
    SourceRoot('terminal_glm', 'GLM-Terminal', Path('/root/.glm'), 'terminal', 'Native GLM-Sitzungen, sofern vorhanden.'),
    SourceRoot('recorder', 'Browser-Recorder', Path('/root/werkraum/tools/chatgpt_browser_recorder'), 'tool', 'Recorder, Tests, Formate und A–F-Ausbaukörper.'),
    SourceRoot('action_history', 'Action-History', Path('/root/werkraum/tools/action_history'), 'tool', 'VPS-/MCP-Zeit- und Provenienzspuren.'),
]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(namespace: str, value: str, length: int = 24) -> str:
    return f'{namespace}:' + hashlib.sha256(value.encode('utf-8', errors='replace')).hexdigest()[:length]


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]], *, gzip_output: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if gzip_output or path.suffix == '.gz' else open
    with opener(path, 'wt', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')


def read_jsonl(path: Path, limit: int | None = None) -> Iterator[dict[str, Any]]:
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as stream:
        for index, line in enumerate(stream):
            if limit is not None and index >= limit:
                break
            try:
                value = json.loads(line)
            except Exception:
                continue
            if isinstance(value, dict):
                yield value


def redact(text: str) -> tuple[str, int]:
    count = 0
    for pattern, replacement in SECRET_PATTERNS:
        text, found = pattern.subn(replacement, text)
        count += found
    return text, count


def excluded(path: Path) -> str | None:
    lowered = {part.lower() for part in path.parts}
    if lowered & EXCLUDE_PARTS:
        return 'excluded_directory'
    name = path.name.lower()
    if name in SECRET_NAMES or any(fragment in name for fragment in SECRET_NAME_FRAGMENTS):
        return 'possible_secret_file'
    if path.is_symlink():
        return 'symlink_not_followed'
    return None


def iter_files(root: Path) -> Iterator[Path]:
    if not root.exists():
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        dirs[:] = [name for name in sorted(dirs) if excluded(base_path / name) is None]
        for name in sorted(files):
            path = base_path / name
            if excluded(path) is None:
                yield path


def preview_text(path: Path, chars: int = PREVIEW_CHARS) -> tuple[str, int, int]:
    try:
        data = path.read_bytes()
    except Exception:
        return '', 0, 0
    text = data[: min(len(data), 2_000_000)].decode('utf-8', errors='replace')
    clean, redactions = redact(text)
    return clean[:chars].replace('\x00', ''), redactions, text.count('\ufffd')


def dir_size(root: Path) -> int:
    total = 0
    if not root.exists():
        return 0
    for path in root.rglob('*'):
        try:
            if path.is_file() and not path.is_symlink():
                total += path.stat().st_size
        except OSError:
            continue
    return total


def atomic_replace_directory(staging: Path, target: Path) -> None:
    previous = target.with_name(target.name + '.previous')
    if previous.exists():
        import shutil
        shutil.rmtree(previous)
    if target.exists():
        target.rename(previous)
    staging.rename(target)
    if previous.exists():
        import shutil
        shutil.rmtree(previous)


@contextmanager
def sqlite(path: Path, *, readonly: bool = False) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if readonly:
        connection = sqlite3.connect(f'file:{path}?mode=ro', uri=True, timeout=30)
    else:
        connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute('pragma journal_mode=WAL')
    connection.execute('pragma synchronous=NORMAL')
    connection.execute('pragma foreign_keys=ON')
    try:
        yield connection
        if not readonly:
            connection.commit()
    finally:
        connection.close()


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text('utf-8'))
    except Exception:
        return default


def temporary_directory(prefix: str) -> Path:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=OUTPUT_ROOT))
