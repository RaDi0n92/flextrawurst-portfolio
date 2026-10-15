#!/usr/bin/env python3
#
# Pflichtfrage (einmalig, diese Datei): wann hoert dieser Code auf zu laufen, und wann
# faengt er an sich selbst zu heilen und zu beleben? Antwort: er laeuft weiter, solange
# irgendein AI-Strom ueber diesen Wrapper gestartet wird -- er heilt sich nie von selbst,
# weil er nichts Kaputtes ist: er schreibt nur mit, still, ohne die Session selbst zu
# beeinflussen. "Heilung" waere hier fehl am Platz -- eher: er bleibt so lange richtig,
# wie sein eigener session_id-Mechanismus (Zeile 42) klar getrennt bleibt von Claude Codes
# eigenem --session-id/--resume-Mechanismus, den er selbst gar nicht kennt oder anfasst.
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

CAPTURE_ROOT = Path('/root/werkraum/_gpt/terminal_capture')
# Claude Code(20-08-2026/01:22:00): VERMUTUNG -- der Schluessel heisst "glm", der Pfad
# dahinter zeigt aber auf /usr/bin/grok, nicht auf ein GLM-Binary. Entweder ist "grok"
# hier bewusst als GLM-kompatibler CLI-Alias installiert (dann ist alles richtig, nur
# der Binary-Name irreführend), oder der Schluessel "glm" meint eigentlich Grok und
# ist selbst falsch benannt. Unverifiziert, nicht angefasst -- nur als echte offene
# Frage stehen gelassen.
BINARIES = {
    'claude': Path('/root/.local/bin/claude'),
    'codex': Path('/usr/bin/codex'),
    'gemini': Path('/usr/bin/gemini'),
    'kimi': Path('/root/.kimi-code/bin/kimi'),
    'glm': Path('/usr/bin/grok'),
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('provider', choices=sorted(BINARIES))
    parser.add_argument('args', nargs=argparse.REMAINDER)
    ns = parser.parse_args()
    binary = BINARIES[ns.provider]
    if not binary.exists():
        print(f'{ns.provider}: kein reales Terminalprogramm unter {binary} gefunden.', file=sys.stderr)
        return 127
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    session_id = f'{stamp}-{uuid.uuid4().hex[:12]}'
    root = CAPTURE_ROOT / ns.provider / session_id
    root.mkdir(parents=True, exist_ok=False)
    output_log = root / 'terminal.log'
    timing_log = root / 'timing.log'
    manifest_path = root / 'MANIFEST.json'
    command = [str(binary), *ns.args]
    if ns.provider == 'codex':
        command.append('--dangerously-bypass-approvals-and-sandbox')
    manifest = {
        'schema_version': 'atlas-terminal-capture-1.0',
        'provider': ns.provider,
        'session_id': session_id,
        'started_utc': utcnow(),
        'cwd': os.getcwd(),
        'binary': str(binary),
        'arguments': ns.args,
        'terminal_log': str(output_log),
        'timing_log': str(timing_log),
        'capture_kind': 'pty_visible_stream',
        'native_provider_log_expected': ns.provider in {'claude', 'codex', 'gemini'},
        'status': 'running',
        'privacy_note': 'Der sichtbare PTY-Strom wird lokal gespeichert. Außenexporte wenden Geheimnis- und Fremddatenfilter an.',
    }
    write(manifest_path, manifest)
    script_command = [
        '/usr/bin/script', '--quiet', '--flush', '--return',
        '--log-out', str(output_log), '--log-timing', str(timing_log),
        '--command', shlex.join(command),
    ]
    try:
        result = subprocess.run(script_command)
        code = int(result.returncode)
    except KeyboardInterrupt:
        code = 130
    except Exception as exc:
        manifest['capture_error'] = f'{type(exc).__name__}: {exc}'
        code = 126
    manifest.update({
        'ended_utc': utcnow(),
        'exit_code': code,
        'status': 'completed' if code == 0 else 'completed_with_nonzero_exit',
        'terminal_log_bytes': output_log.stat().st_size if output_log.exists() else 0,
        'timing_log_bytes': timing_log.stat().st_size if timing_log.exists() else 0,
    })
    write(manifest_path, manifest)
    dirty = Path('/root/werkraum/_gpt/gesamtatlas/organismus/DIRTY')
    dirty.parent.mkdir(parents=True, exist_ok=True)
    dirty.write_text(json.dumps({'provider': ns.provider, 'session_id': session_id, 'updated_utc': utcnow()}, ensure_ascii=False) + '\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
