#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from browser import origin_search, package_conversation
from capsule import build_detail_package
from common import ATLAS_ROOT, CONTRIBUTION_ROOT, CURRENT, STATE, append_jsonl, load_json, redact, stable_id, utcnow
from core import search_core
from terminal import materialize_terminal_session, search_terminal

KNOWN_STREAMS = {'chatgpt', 'claude', 'codex', 'gemini', 'kimi', 'glm', 'grok', 'daniel', 'unknown'}
READ_ROOTS = [Path('/root/werkraum'), Path('/root/.claude'), Path('/root/.codex'), Path('/root/.gemini'), Path('/root/.kimi'), Path('/root/.glm')]


def current_paths() -> tuple[Path, Path, Path]:
    if not CURRENT.exists():
        raise RuntimeError('Gesamtatlas-Organismus wurde noch nicht gebaut.')
    return CURRENT / 'KERN' / 'ATLAS_SCHMAL.sqlite', CURRENT / 'BROWSER', CURRENT / 'TERMINAL'


def output(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str))


def combined_search(query: str, limit: int) -> dict[str, Any]:
    core_db, browser_dir, terminal_dir = current_paths()
    return {
        'query': query,
        'core': search_core(core_db, query, limit),
        'browser': origin_search(browser_dir, query, limit),
        'terminal': search_terminal(terminal_dir, query, limit),
    }


def safe_path(value: str) -> Path:
    path = Path(value).resolve()
    if not any(path == root or root in path.parents for root in READ_ROOTS):
        raise PermissionError('Pfad liegt außerhalb der lesbaren Atlaswurzeln.')
    return path


def contribution(args: argparse.Namespace, kind: str) -> dict[str, Any]:
    stream = (args.stream or os.environ.get('GESAMTATLAS_STREAM') or 'unknown').lower()
    if stream not in KNOWN_STREAMS:
        raise ValueError(f'Unbekannter AI-Strom: {stream}')
    text, redactions = redact(args.text)
    subject, subject_redactions = redact(args.subject or '')
    row = {
        'schema_version': 'atlas-contribution-1.0',
        'contribution_id': stable_id('contribution', f'{stream}:{kind}:{utcnow()}:{subject}:{text}'),
        'stream_id': stream,
        'kind': kind,
        'subject': subject,
        'text': text,
        'redactions': redactions + subject_redactions,
        'created_utc': utcnow(),
        'source_interface': 'gesamtatlas-cli',
        'status': 'attributed_not_canonical',
        'truth_boundary': 'Ein Beitrag ist die zugeschriebene Stimme seines Stroms, nicht automatische Atlaswahrheit.',
    }
    path = CONTRIBUTION_ROOT / stream / f'{kind}.jsonl'
    append_jsonl(path, row)
    return {'ok': True, 'path': str(path), 'contribution': row}


def main() -> int:
    parser = argparse.ArgumentParser(prog='gesamtatlas', description='Schmaler explorativer Gesamtatlas-Zugang für Menschen und AI-Ströme.')
    parser.add_argument('--stream', help='chatgpt/claude/codex/gemini/kimi/glm/grok/daniel')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('status')
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--limit', type=int, default=30)
    origin = sub.add_parser('origin')
    origin.add_argument('query')
    origin.add_argument('--limit', type=int, default=50)
    ask = sub.add_parser('ask')
    ask.add_argument('question')
    ask.add_argument('--limit', type=int, default=20)
    read = sub.add_parser('read')
    read.add_argument('path')
    read.add_argument('--start-line', type=int, default=1)
    read.add_argument('--max-lines', type=int, default=300)
    explore = sub.add_parser('explore')
    explore.add_argument('--query', required=True)
    explore.add_argument('--destination')
    conversation = sub.add_parser('conversation-package')
    conversation.add_argument('conversation_id')
    conversation.add_argument('--destination')
    terminal_package = sub.add_parser('terminal-package')
    terminal_package.add_argument('provider')
    terminal_package.add_argument('session_id')
    terminal_package.add_argument('--destination')
    for name in ('note', 'challenge', 'impulse'):
        command = sub.add_parser(name)
        command.add_argument('--subject', default='')
        command.add_argument('text')

    args = parser.parse_args()
    if args.command == 'status':
        state = load_json(STATE, {}) or {}
        state['current_exists'] = CURRENT.exists()
        state['capsule_path'] = str(ATLAS_ROOT / 'GESAMTATLAS_KAPSEL_AKTUELL.zip')
        output(state)
        return 0
    if args.command == 'search':
        output(combined_search(args.query, args.limit))
        return 0
    if args.command == 'origin':
        core_db, browser_dir, terminal_dir = current_paths()
        output({
            'query': args.query,
            'browser_origins': origin_search(browser_dir, args.query, args.limit),
            'terminal_origins': search_terminal(terminal_dir, args.query, args.limit),
            'file_and_document_origins': search_core(core_db, args.query, args.limit),
            'truth_boundary': 'Treffer zeigen Fundstellen und Ähnlichkeit. Sie beweisen nicht automatisch den allerersten historischen Ursprung.',
        })
        return 0
    if args.command == 'ask':
        result = combined_search(args.question, args.limit)
        result['question'] = args.question
        result['reading_contract'] = [
            'Original, Spiegel und Ableitung getrennt halten.',
            'Erreichbarkeit nicht als tatsächliches Lesen ausgeben.',
            'Gegenbelege und Lücken benennen.',
            'Für Details einen Explorationskörper erzeugen.',
        ]
        output(result)
        return 0
    if args.command == 'read':
        path = safe_path(args.path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(path)
        text = path.read_text('utf-8', errors='replace')
        clean, redactions = redact(text)
        lines = clean.splitlines()
        start = max(1, args.start_line)
        selected = lines[start - 1:start - 1 + max(1, args.max_lines)]
        output({
            'path': str(path),
            'start_line': start,
            'returned_lines': len(selected),
            'total_lines': len(lines),
            'complete': start == 1 and len(selected) == len(lines),
            'redactions': redactions,
            'text': '\n'.join(selected),
        })
        return 0
    if args.command == 'explore':
        destination = Path(args.destination) if args.destination else None
        path = build_detail_package(args.query, CURRENT, destination)
        output({'ok': True, 'query': args.query, 'path': str(path), 'bytes': path.stat().st_size})
        return 0
    if args.command == 'conversation-package':
        _, browser_dir, _ = current_paths()
        destination = Path(args.destination) if args.destination else None
        path = package_conversation(browser_dir, args.conversation_id, destination)
        output({'ok': True, 'conversation_id': args.conversation_id, 'path': str(path), 'bytes': path.stat().st_size})
        return 0
    if args.command == 'terminal-package':
        _, _, terminal_dir = current_paths()
        destination = Path(args.destination) if args.destination else (ATLAS_ROOT / 'organismus/EXPLORATIONSKOERPER' / f'TERMINAL_{args.provider}_{stable_id("terminal-session", args.session_id).split(":",1)[1]}.zip')
        path = materialize_terminal_session(terminal_dir, args.provider, args.session_id, destination)
        output({'ok': True, 'provider': args.provider, 'session_id': args.session_id, 'path': str(path), 'bytes': path.stat().st_size})
        return 0
    if args.command in ('note', 'challenge', 'impulse'):
        output(contribution(args, args.command))
        return 0
    return 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        output({'ok': False, 'error': f'{type(exc).__name__}: {exc}'})
        raise SystemExit(1)
