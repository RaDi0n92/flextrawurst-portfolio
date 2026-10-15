from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
from typing import Any

from common import SOURCE_ROOTS, TEXT_SUFFIXES, excluded, preview_text, redact, sha256_file, stable_id, utcnow, write_jsonl

STREAM_ROOTS = {
    'chatgpt': Path('/root/werkraum/_gpt/mcp_zuhause'),
    'claude': Path('/root/werkraum/_claude'),
    'codex': Path('/root/werkraum/_codex'),
    'gemini': Path('/root/werkraum/_gemini'),
    'kimi': Path('/root/werkraum/_kimi'),
    'glm': Path('/root/werkraum/_glm'),
    'grok': Path('/root/werkraum/_grok'),
}


def _iter_home_files(root: Path):
    if not root.exists():
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        dirs[:] = [name for name in sorted(dirs) if excluded(base_path / name) is None and not name.startswith('_import_')]
        for name in sorted(files):
            path = base_path / name
            if excluded(path) is None:
                yield path


def build_homes(output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    streams = {}
    total_files = total_bytes = total_previews = 0
    for stream, root in STREAM_ROOTS.items():
        rows = []
        if root.exists():
            for path in _iter_home_files(root):
                try:
                    stat = path.stat()
                except OSError:
                    continue
                preview = ''
                redactions = replacements = 0
                if path.suffix.lower() in TEXT_SUFFIXES and stat.st_size <= 5_000_000:
                    preview, redactions, replacements = preview_text(path, 1200)
                    total_previews += int(bool(preview))
                rows.append({
                    'object_id': stable_id('home-file', f'{stream}:{path.relative_to(root)}'),
                    'stream_id': stream,
                    'relative_path': path.relative_to(root).as_posix(),
                    'source_path': str(path),
                    'bytes': stat.st_size,
                    'mtime_ns': stat.st_mtime_ns,
                    'suffix': path.suffix.lower(),
                    'sha256': sha256_file(path) if stat.st_size <= 20_000_000 else None,
                    'preview': preview,
                    'preview_redactions': redactions,
                    'decode_replacements': replacements,
                    'copy_policy': 'reference_only',
                })
                total_files += 1
                total_bytes += stat.st_size
        target = output / stream
        target.mkdir(parents=True, exist_ok=True)
        write_jsonl(target / 'INDEX.jsonl.gz', rows, gzip_output=True)
        anchor_names = ['ZUHAUSE.md', 'RESONANZFELD.md', 'WERKRAUM_KARTE.md', 'SUBCONSCIOUS.md', 'FRAGEN.md']
        anchors = []
        for name in anchor_names:
            source = root / name
            if not source.exists() or not source.is_file():
                continue
            text = source.read_text('utf-8', errors='replace')
            clean, redactions = redact(text)
            anchor = target / name
            anchor.write_text(clean, encoding='utf-8')
            anchors.append({
                'name': name,
                'source_path': str(source),
                'source_sha256': sha256_file(source),
                'atlas_path': str(anchor),
                'atlas_sha256': sha256_file(anchor),
                'copy_class': 'exact_text_copy' if redactions == 0 and '\ufffd' not in text else 'marked_external_copy',
                'redactions': redactions,
            })
        status = {
            'stream_id': stream,
            'source_root': str(root),
            'source_exists': root.exists(),
            'file_count': len(rows),
            'source_bytes': sum(row['bytes'] for row in rows),
            'anchors': anchors,
            'exploration': {
                'search': f'gesamtatlas --stream {stream} search "BEGRIFF"',
                'read': 'gesamtatlas read "/absolute/source/path"',
                'note': f'gesamtatlas --stream {stream} note --subject "THEMA" "TEXT"',
                'challenge': f'gesamtatlas --stream {stream} challenge --subject "THEMA" "WIDERSPRUCH"',
            },
            'identity_boundary': 'Imported house plans and mirrors remain references and are not treated as this stream’s own memory.',
        }
        (target / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        streams[stream] = status
    summary = {
        'ok': True,
        'generated_utc': utcnow(),
        'streams': streams,
        'stream_count': len(streams),
        'homes_present': sum(1 for item in streams.values() if item['source_exists']),
        'files_indexed': total_files,
        'source_bytes_referenced_not_copied': total_bytes,
        'preview_count': total_previews,
        'copy_policy': 'home files remain at source; only compact indices and selected anchors are carried',
    }
    (output / 'STATUS.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return summary
