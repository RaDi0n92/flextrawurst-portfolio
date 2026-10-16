#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

DEFAULT = Path('/root/flextrawurst/out/process_camera/flextrawurst_surface_public.html')
path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
raw = path.read_text(encoding='utf-8', errors='replace')
soup = BeautifulSoup(raw, 'html.parser')


def norm_text(node) -> str:
    if node is None:
        return ''
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip()


def logical_view_id(dom_id: str) -> str:
    if dom_id.startswith('view-'):
        return dom_id[5:]
    if dom_id.startswith('v-'):
        return dom_id[2:]
    return dom_id

# Exact DOM elements only. No regex span leakage into following global scripts.
views: dict[str, dict] = {}
for node in soup.find_all(id=re.compile(r'^(?:view|v)-')):
    dom_id = node.get('id', '')
    view_id = logical_view_id(dom_id)
    fragment = str(node)
    plain = norm_text(node)
    api_urls = sorted(set(re.findall(r"fetch\s*\(\s*['\"]([^'\"]+)['\"]", fragment)))
    views[view_id] = {
        'dom_id': dom_id,
        'bytes': len(fragment.encode('utf-8')),
        'static_text_chars': len(plain),
        'loading_markers': len(re.findall(r'(?i)\b(?:lädt|laedt)\s*(?:\.\.\.|…)?', plain)),
        'fetch_calls': len(re.findall(r'\bfetch\s*\(', fragment)),
        'api_urls': api_urls,
        'iframes': len(node.find_all('iframe')),
        'forms': len(node.find_all('form')),
        'buttons': len(node.find_all('button')),
        'links': len(node.find_all('a')),
        'static_text_preview': plain[:180],
    }

tabs = []
for a in soup.select('a.v-tab'):
    view_id = a.get('data-view', '')
    style = (a.get('style') or '').replace(' ', '').lower()
    info = views.get(view_id, {})
    tabs.append({
        'label': norm_text(a),
        'view': view_id,
        'href': a.get('href', ''),
        'hidden_default': 'display:none' in style,
        'live_badge': a.get('data-live') == '1',
        'has_view': view_id in views,
        'static_text_chars': info.get('static_text_chars', 0),
        'loading_markers': info.get('loading_markers', 0),
        'fetch_calls': info.get('fetch_calls', 0),
        'iframes': info.get('iframes', 0),
        'forms': info.get('forms', 0),
        'buttons': info.get('buttons', 0),
        'links': info.get('links', 0),
    })

counts: dict[str, int] = {}
for t in tabs:
    counts[t['view']] = counts.get(t['view'], 0) + 1

report = {
    'file': str(path),
    'bytes': len(raw.encode('utf-8')),
    'tab_count': len(tabs),
    'unique_tab_views': len({t['view'] for t in tabs if t['view']}),
    'view_count': len(views),
    'duplicate_tab_targets': {k: v for k, v in counts.items() if v > 1},
    'missing_view_targets': [t for t in tabs if t['view'] and not t['has_view']],
    'unlinked_views': sorted(set(views) - {t['view'] for t in tabs}),
    'tabs': tabs,
    'views': views,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
