from __future__ import annotations

import gzip
import json
import os
import re
import shutil
import sqlite3
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from common import OUTPUT_ROOT, load_json, redact, sha256_file, stable_id, utcnow, write_jsonl

PROVIDERS = {
    'claude': {'root': Path('/root/.claude/projects/-root'), 'format': 'claude_jsonl'},
    'codex': {'root': Path('/root/.codex/sessions'), 'format': 'codex_rollout_jsonl'},
    'gemini': {'root': Path('/root/.gemini/antigravity-cli/brain'), 'format': 'gemini_document_bundle'},
    'kimi': {'root': Path('/root/.kimi'), 'format': 'unknown_native'},
    'glm': {'root': Path('/root/.glm'), 'format': 'unknown_native'},
}
CACHE = OUTPUT_ROOT / 'cache' / 'terminal'
CAPTURE_ROOT = Path('/root/werkraum/_gpt/terminal_capture')

DECISION_RULE = re.compile(r'(?i)\b(ich entscheide|wir nehmen|entscheidung|ab jetzt|gewählt|verwenden wir|festgelegt)\b')
CORRECTION_RULE = re.compile(r'(?i)\b(korrektur|nein|nicht so|falsch|zurück|missverstanden|doch nicht)\b')
ERROR_RULE = re.compile(r'(?i)\b(error|fehler|failed|traceback|timeout|scheitert|kaputt|returncode[^0])\b')
IMPULSE_RULE = re.compile(r'(?i)\b(ich möchte|ich will|bitte|mach|baue|prüfe|suche|idee|vorschlag|nächster schritt)\b')


def _event(provider: str, session_id: str, seq: int, role: str, kind: str, text: str, timestamp: str | None, source: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    clean, redactions = redact(text)
    row = {
        'event_id': stable_id('terminal-event', f'{provider}:{session_id}:{seq}:{role}:{kind}:{clean[:200]}'),
        'provider': provider,
        'session_id': session_id,
        'sequence': seq,
        'role': role,
        'kind': kind,
        'text': clean,
        'timestamp': timestamp,
        'source_path': source,
        'redactions': redactions,
    }
    if extra:
        row.update(extra)
    return row


def _claude_events(path: Path, session_id: str) -> Iterator[dict[str, Any]]:
    seq = 0
    with path.open('r', encoding='utf-8', errors='replace') as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except Exception:
                continue
            row_type = row.get('type')
            if row_type not in ('user', 'assistant'):
                continue
            message = row.get('message') or {}
            role = message.get('role') or row_type
            content = message.get('content')
            timestamp = row.get('timestamp') or row.get('created_at')
            if isinstance(content, str):
                seq += 1
                yield _event('claude', session_id, seq, role, 'message', content, timestamp, str(path), {'source_line': line_number})
                continue
            if not isinstance(content, list):
                continue
            text_parts = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                kind = block.get('type')
                if kind == 'text':
                    text_parts.append(str(block.get('text') or ''))
                elif kind == 'tool_use':
                    if text_parts:
                        seq += 1
                        yield _event('claude', session_id, seq, role, 'message', '\n'.join(text_parts), timestamp, str(path), {'source_line': line_number})
                        text_parts.clear()
                    seq += 1
                    payload = {'name': block.get('name'), 'input': block.get('input') or {}, 'tool_use_id': block.get('id')}
                    yield _event('claude', session_id, seq, 'tool', 'tool_call', json.dumps(payload, ensure_ascii=False, indent=2), timestamp, str(path), {'source_line': line_number, 'tool_name': block.get('name'), 'tool_use_id': block.get('id')})
                elif kind == 'tool_result':
                    if text_parts:
                        seq += 1
                        yield _event('claude', session_id, seq, role, 'message', '\n'.join(text_parts), timestamp, str(path), {'source_line': line_number})
                        text_parts.clear()
                    seq += 1
                    result = block.get('content')
                    if not isinstance(result, str):
                        result = json.dumps(result, ensure_ascii=False, default=str)
                    yield _event('claude', session_id, seq, 'tool', 'tool_result', result, timestamp, str(path), {'source_line': line_number, 'tool_use_id': block.get('tool_use_id'), 'is_error': bool(block.get('is_error'))})
            if text_parts:
                seq += 1
                yield _event('claude', session_id, seq, role, 'message', '\n'.join(text_parts), timestamp, str(path), {'source_line': line_number})


def _codex_events(path: Path, session_id: str) -> Iterator[dict[str, Any]]:
    seq = 0
    with path.open('r', encoding='utf-8', errors='replace') as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except Exception:
                continue
            timestamp = row.get('timestamp')
            row_type = row.get('type')
            payload = row.get('payload') or {}
            if row_type == 'response_item':
                kind = payload.get('type')
                if kind == 'message':
                    role = payload.get('role') or 'assistant'
                    if role in ('developer', 'system'):
                        continue
                    parts = []
                    for block in payload.get('content') or []:
                        if isinstance(block, dict) and block.get('type') in ('input_text', 'output_text', 'text'):
                            parts.append(str(block.get('text') or ''))
                    if parts:
                        seq += 1
                        yield _event('codex', session_id, seq, role, 'message', '\n'.join(parts), timestamp, str(path), {'source_line': line_number})
                elif kind in ('function_call', 'custom_tool_call'):
                    seq += 1
                    name = payload.get('name') or payload.get('tool_name') or 'tool'
                    args = payload.get('arguments') or payload.get('input') or payload
                    text = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False, indent=2, default=str)
                    yield _event('codex', session_id, seq, 'tool', 'tool_call', f'{name}\n{text}', timestamp, str(path), {'source_line': line_number, 'tool_name': name, 'tool_use_id': payload.get('call_id')})
                elif kind in ('function_call_output', 'custom_tool_call_output'):
                    seq += 1
                    output = payload.get('output') or payload
                    text = output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, default=str)
                    yield _event('codex', session_id, seq, 'tool', 'tool_result', text, timestamp, str(path), {'source_line': line_number, 'tool_use_id': payload.get('call_id')})
            elif row_type in ('event_msg', 'message'):
                text = payload.get('message') or payload.get('text') or row.get('message')
                if text:
                    seq += 1
                    yield _event('codex', session_id, seq, payload.get('role') or 'assistant', 'status', str(text), timestamp, str(path), {'source_line': line_number})


def _gemini_events(path: Path, session_id: str) -> Iterator[dict[str, Any]]:
    seq = 0
    files = sorted((file for file in path.rglob('*') if file.is_file() and file.suffix.lower() in {'.md', '.txt', '.json', '.jsonl'}), key=lambda p: (p.stat().st_mtime_ns, str(p)))
    for file in files:
        try:
            text = file.read_text('utf-8', errors='replace')
        except Exception:
            continue
        name = file.name.lower()
        role = 'user' if any(term in name for term in ('prompt', 'user', 'request', 'input')) else 'assistant'
        kind = 'message' if role == 'user' else 'document'
        timestamp = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).isoformat()
        seq += 1
        yield _event('gemini', session_id, seq, role, kind, text, timestamp, str(file), {'source_file': file.name})


def _generic_events(provider: str, root: Path, session_id: str) -> Iterator[dict[str, Any]]:
    seq = 0
    path = root / session_id
    files = [path] if path.is_file() else sorted((p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in {'.md', '.txt', '.json', '.jsonl'}), key=lambda p: (p.stat().st_mtime_ns, str(p)))
    for file in files:
        try:
            text = file.read_text('utf-8', errors='replace')
        except Exception:
            continue
        seq += 1
        yield _event(provider, session_id, seq, 'unknown', 'document', text, datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).isoformat(), str(file), {'source_file': file.name})




def _capture_events(provider: str, session_id: str, path: Path) -> Iterator[dict[str, Any]]:
    log = path / 'terminal.log'
    if not log.exists():
        return
    text = log.read_text('utf-8', errors='replace')
    manifest = load_json(path / 'MANIFEST.json', {}) or {}
    yield _event(provider, session_id, 1, 'unknown', 'terminal_visible_stream', text, manifest.get('started_utc'), str(log), {'capture_manifest': str(path / 'MANIFEST.json')})

def sessions_for(provider: str) -> list[tuple[str, Path]]:
    spec = PROVIDERS[provider]
    root = spec['root']
    candidates: list[tuple[str, Path]] = []
    if root.exists():
        if provider == 'claude':
            candidates.extend((path.stem, path) for path in sorted(root.glob('*.jsonl')))
        elif provider == 'codex':
            candidates.extend((path.stem, path) for path in sorted(root.rglob('rollout-*.jsonl')))
        elif provider == 'gemini':
            candidates.extend((path.name, path) for path in sorted(root.iterdir()) if path.is_dir())
        else:
            for path in sorted(root.iterdir()):
                if path.is_dir() or path.suffix.lower() in {'.jsonl', '.json', '.md', '.txt'}:
                    candidates.append((path.stem if path.is_file() else path.name, path))
    capture = CAPTURE_ROOT / provider
    if capture.exists():
        candidates.extend((f'pty-{path.name}', path) for path in sorted(capture.iterdir()) if path.is_dir() and (path / 'terminal.log').exists())
    return candidates


def events_for(provider: str, session_id: str, path: Path) -> Iterator[dict[str, Any]]:
    if path.is_dir() and (path / 'terminal.log').exists():
        yield from _capture_events(provider, session_id, path)
    elif provider == 'claude':
        yield from _claude_events(path, session_id)
    elif provider == 'codex':
        yield from _codex_events(path, session_id)
    elif provider == 'gemini':
        yield from _gemini_events(path, session_id)
    else:
        yield from _generic_events(provider, PROVIDERS[provider]['root'], session_id)


def classify_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marks = []
    for event in events:
        text = event.get('text') or ''
        classes = []
        if event.get('role') == 'user' and IMPULSE_RULE.search(text):
            classes.append('daniel_impulse')
        if event.get('role') == 'assistant' and IMPULSE_RULE.search(text):
            classes.append('agent_impulse')
        if DECISION_RULE.search(text):
            classes.append('decision_candidate')
        if CORRECTION_RULE.search(text):
            classes.append('correction_candidate')
        if ERROR_RULE.search(text) or event.get('is_error'):
            classes.append('error_or_failed_path')
        for classification in classes:
            marks.append({
                'marker_id': stable_id('terminal-marker', f"{event['event_id']}:{classification}"),
                'event_id': event['event_id'],
                'provider': event['provider'],
                'session_id': event['session_id'],
                'classification': classification,
                'excerpt': text[:1600],
                'truth_class': 'HEURISTIC_DERIVATION',
                'review_status': 'unreviewed',
            })
    return marks


def _conversation_text(events: list[dict[str, Any]]) -> str:
    parts = []
    for event in events:
        if event.get('kind') != 'message' or event.get('role') not in ('user', 'assistant'):
            continue
        role = 'Daniel' if event['role'] == 'user' else event['provider'].capitalize()
        parts.append(f'{role}:\n{event.get("text") or ""}')
    return '\n\n'.join(parts).rstrip() + '\n'


def _source_fingerprint(path: Path) -> str:
    if path.is_file():
        stat = path.stat()
        return stable_id('source-state', f'{path}:{stat.st_size}:{stat.st_mtime_ns}', 40)
    pieces = []
    for file in sorted(p for p in path.rglob('*') if p.is_file()):
        try:
            stat = file.stat()
        except OSError:
            continue
        pieces.append(f'{file.relative_to(path)}:{stat.st_size}:{stat.st_mtime_ns}')
    return stable_id('source-state', '\n'.join(pieces), 40)


def _source_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob('*') if file.is_file())


def _source_modified(path: Path) -> str:
    if path.is_file():
        stamp = path.stat().st_mtime
    else:
        stamps = [file.stat().st_mtime for file in path.rglob('*') if file.is_file()]
        stamp = max(stamps) if stamps else path.stat().st_mtime
    return datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat()


def _source_format(provider: str, source: Path) -> str:
    if source.is_dir() and (source / 'terminal.log').exists():
        return 'script_terminal_output'
    return PROVIDERS[provider]['format']


def _session_summary(provider: str, session_id: str, source: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    events = list(events_for(provider, session_id, source))
    markers = classify_events(events)
    counts = defaultdict(int)
    redactions = 0
    for event in events:
        counts[event.get('kind') or 'unknown'] += 1
        counts[event.get('role') or 'unknown'] += 1
        redactions += int(event.get('redactions') or 0)
    summary = {
        'schema_version': 'terminalwerkstrom-2.0',
        'provider': provider,
        'session_id': session_id,
        'source_path': str(source),
        'source_format': _source_format(provider, source),
        'source_fingerprint': _source_fingerprint(source),
        'source_bytes': _source_bytes(source),
        'modified_utc': _source_modified(source),
        'event_count': len(events),
        'message_count': counts['message'],
        'tool_call_count': counts['tool_call'],
        'tool_result_count': counts['tool_result'],
        'marker_count': len(markers),
        'redactions': redactions,
        'storage_policy': 'compact_index_only_full_normalization_on_demand',
        'truth_boundary': 'Messages and tools are normalized from visible/native records. Markers are heuristic derivations. Full normalized bodies are generated on demand.',
    }
    return events, markers, summary


def build_terminal(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    sessions_root = output / 'sessions'
    sessions_root.mkdir(parents=True, exist_ok=True)
    index_db = output / 'TERMINAL_INDEX.sqlite'
    if index_db.exists():
        index_db.unlink()
    connection = sqlite3.connect(index_db)
    connection.execute('pragma journal_mode=OFF')
    connection.execute('pragma synchronous=OFF')
    connection.execute('pragma temp_store=MEMORY')
    connection.execute('create table providers(provider text primary key, source_root text, source_format text, source_exists integer, session_count integer, status text)')
    connection.execute('create table sessions(provider text, session_id text, source_path text, source_format text, modified_utc text, source_bytes integer, event_count integer, message_count integer, tool_call_count integer, tool_result_count integer, marker_count integer, atlas_path text, primary key(provider,session_id))')
    connection.execute("create virtual table event_search using fts5(event_id unindexed, provider unindexed, session_id unindexed, sequence unindexed, role unindexed, kind unindexed, timestamp unindexed, text, tokenize='unicode61 remove_diacritics 2')")
    connection.execute('create table markers(marker_id text primary key, provider text, session_id text, event_id text, classification text, excerpt text, truth_class text, review_status text)')
    totals = defaultdict(int)
    provider_status: dict[str, Any] = {}
    register = []
    for provider, spec in PROVIDERS.items():
        found = sessions_for(provider)
        root_or_capture_exists = spec['root'].exists() or (CAPTURE_ROOT / provider).exists()
        status = 'available' if found else ('source_root_missing' if not root_or_capture_exists else 'no_supported_sessions_found')
        connection.execute('insert into providers values (?,?,?,?,?,?)', (provider, str(spec['root']), spec['format'], int(root_or_capture_exists), len(found), status))
        provider_status[provider] = {'source_root': str(spec['root']), 'capture_root': str(CAPTURE_ROOT / provider), 'format': spec['format'], 'exists': root_or_capture_exists, 'sessions': len(found), 'status': status}
        for session_id, source in found:
            events, markers, summary = _session_summary(provider, session_id, source)
            target = sessions_root / provider / stable_id('session', session_id).split(':', 1)[1]
            target.mkdir(parents=True, exist_ok=True)
            (target / 'MANIFEST.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            row = {
                'provider': provider,
                'session_id': session_id,
                'source_path': str(source),
                'source_format': summary['source_format'],
                'modified_utc': summary['modified_utc'],
                'source_bytes': summary['source_bytes'],
                'event_count': summary['event_count'],
                'message_count': summary['message_count'],
                'tool_call_count': summary['tool_call_count'],
                'tool_result_count': summary['tool_result_count'],
                'marker_count': summary['marker_count'],
                'atlas_path': str(target),
            }
            connection.execute('insert into sessions values (?,?,?,?,?,?,?,?,?,?,?,?)', tuple(row.values()))
            batch = []
            for event in events:
                text = (event.get('text') or '')[:1400]
                batch.append((event['event_id'], provider, session_id, event.get('sequence'), event.get('role'), event.get('kind'), event.get('timestamp'), text))
                if len(batch) >= 1500:
                    connection.executemany('insert into event_search values (?,?,?,?,?,?,?,?)', batch)
                    batch.clear()
            if batch:
                connection.executemany('insert into event_search values (?,?,?,?,?,?,?,?)', batch)
            mark_rows = [(mark['marker_id'], provider, session_id, mark['event_id'], mark['classification'], (mark['excerpt'] or '')[:900], mark['truth_class'], mark['review_status']) for mark in markers]
            if mark_rows:
                connection.executemany('insert into markers values (?,?,?,?,?,?,?,?)', mark_rows)
            register.append(row)
            totals['sessions'] += 1
            totals['events'] += row['event_count']
            totals['messages'] += row['message_count']
            totals['tool_calls'] += row['tool_call_count']
            totals['tool_results'] += row['tool_result_count']
            totals['markers'] += row['marker_count']
    connection.commit()
    connection.execute('insert into event_search(event_search) values (\'optimize\')')
    connection.commit()
    connection.execute('vacuum')
    connection.close()
    write_jsonl(output / 'SITZUNGSREGISTER.jsonl.gz', register, gzip_output=True)
    result = {
        'ok': True,
        'generated_utc': utcnow(),
        'providers': provider_status,
        'totals': dict(totals),
        'index_path': str(index_db),
        'index_bytes': index_db.stat().st_size,
        'capture_policy': 'native originals remain in place; compact excerpts and session manifests are indexed; complete normalized streams are generated on demand',
        'full_stream_storage': False,
    }
    (output / 'STATUS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return result


def materialize_terminal_session(terminal_dir: Path, provider: str, session_id: str, destination: Path) -> Path:
    db = terminal_dir / 'TERMINAL_INDEX.sqlite'
    connection = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    row = connection.execute('select * from sessions where provider=? and session_id=?', (provider, session_id)).fetchone()
    connection.close()
    if row is None:
        raise FileNotFoundError(f'{provider}:{session_id}')
    source = Path(row['source_path'])
    events, markers, summary = _session_summary(provider, session_id, source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix('.tmp')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=7, allowZip64=True) as archive:
        event_lines = ''.join(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n' for event in events)
        marker_lines = ''.join(json.dumps(marker, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n' for marker in markers)
        archive.writestr('00_START_HIER.md', f'# Terminalwerkstrom\n\nProvider: {provider}\nSitzung: {session_id}\nQuelle: {source}\n\nNachrichten, Toolaufrufe, Ergebnisse und markierte Ableitungen bleiben getrennt.\n')
        archive.writestr('EREIGNISSE.jsonl', event_lines)
        archive.writestr('GESPRAECH_1ZU1.md', _conversation_text(events))
        archive.writestr('MARKER.jsonl', marker_lines)
        archive.writestr('MANIFEST.json', json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    with zipfile.ZipFile(temp) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'bad terminal package member: {bad}')
    temp.replace(destination)
    return destination


def search_terminal(terminal_dir: Path, query: str, limit: int = 50) -> list[dict[str, Any]]:
    db = terminal_dir / 'TERMINAL_INDEX.sqlite'
    if not db.exists() or not query.strip():
        return []
    connection = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in connection.execute(
            'select event_id,provider,session_id,sequence,role,kind,timestamp,text,bm25(event_search) as rank from event_search where event_search match ? order by rank limit ?',
            (' '.join(query.split()), limit),
        )]
    except sqlite3.OperationalError:
        rows = []
    connection.close()
    return rows
