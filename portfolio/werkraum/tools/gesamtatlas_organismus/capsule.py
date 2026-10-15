from __future__ import annotations

import gzip
import html
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from browser import origin_search, package_conversation
from common import (
    ATLAS_ROOT,
    CAPSULE_DIR,
    CAPSULE_ZIP,
    DETAIL_ROOT,
    MAX_CAPSULE_BYTES,
    MAX_DETAIL_BYTES,
    TEXT_SUFFIXES,
    json_text,
    load_json,
    redact,
    sha256_file,
    stable_id,
    utcnow,
)
from core import search_core
from terminal import search_terminal

CSS = '''
:root{color-scheme:dark;--bg:#100b17;--panel:#1b1326;--ink:#f4eafa;--muted:#c9b3d9;--line:#4d3a60;--accent:#d3a5ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0,#2c1841,#100b17 52%);color:var(--ink);font:17px/1.55 system-ui,sans-serif}main,header,footer{max-width:1040px;margin:auto;padding:1rem}a{color:#e1c1ff}.hero{padding:3rem 0}.hero h1{font-size:clamp(2.4rem,7vw,5rem);line-height:.98;margin:.3rem 0 1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem}.card{display:block;color:inherit;text-decoration:none;border:1px solid var(--line);border-radius:18px;padding:1rem;background:linear-gradient(145deg,#1e152a,#130e1b)}.muted{color:var(--muted)}code{overflow-wrap:anywhere}input{width:100%;padding:.8rem;border:1px solid var(--line);border-radius:12px;background:#0d0912;color:var(--ink)}@media(max-width:420px){body{font-size:15px}}
'''


def _page(title: str, body: str) -> str:
    return f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · Gesamtatlas-Kapsel</title><style>{CSS}</style></head><body><header><a href="index.html">Start</a> · <a href="facetten.html">Facetten</a> · <a href="fragen.html">Fragen</a></header><main>{body}</main><footer><p class="muted">Lokale portable Kapsel. Kein öffentlicher Gesamtatlas.</p></footer></body></html>'


def _capsule_db(path: Path, core_db: Path, browser_dir: Path, terminal_dir: Path, reactive_dir: Path) -> dict[str, int]:
    if path.exists():
        path.unlink()
    out = sqlite3.connect(path)
    out.execute('pragma journal_mode=OFF')
    out.execute('pragma synchronous=OFF')
    out.execute('create table meta(key text primary key,value_json text not null)')
    out.execute('create table facets(facet_id text primary key,facet_type text,title text,description text,source_path text,item_count integer,status text,metadata_json text)')
    out.execute('create table paths(path text primary key,root_name text,kind text,size integer,mtime_ns integer,suffix text,basename text,parent text,excluded_reason text)')
    out.execute('create index idx_paths_basename on paths(basename)')
    out.execute('create table projects(project_id text primary key,name text,path text,project_class text,status text,summary text)')
    out.execute('create table streams(stream_id text primary key,title text,home_path text,home_exists integer,session_source text)')
    out.execute('create table browser_conversations(conversation_id text primary key,title text,provider text,message_count integer,turn_count integer,gap_count integer,completeness text,source_path text)')
    out.execute('create table terminal_sessions(provider text,session_id text,modified_utc text,event_count integer,message_count integer,tool_call_count integer,tool_result_count integer,source_path text,primary key(provider,session_id))')
    out.execute('create table findings(finding_id text primary key,kind text,subject text,summary text,severity text,truth_class text)')
    counts = {'paths': 0, 'projects': 0, 'streams': 0, 'browser_conversations': 0, 'terminal_sessions': 0, 'findings': 0}
    core = sqlite3.connect(f'file:{core_db}?mode=ro', uri=True)
    core.row_factory = sqlite3.Row
    batch = []
    for row in core.execute('select path,root_name,kind,size,mtime_ns,suffix,basename,parent,excluded_reason from paths'):
        batch.append(tuple(row))
        if len(batch) >= 5000:
            out.executemany('insert into paths values (?,?,?,?,?,?,?,?,?)', batch)
            counts['paths'] += len(batch)
            batch.clear()
    if batch:
        out.executemany('insert into paths values (?,?,?,?,?,?,?,?,?)', batch)
        counts['paths'] += len(batch)
    for row in core.execute('select project_id,name,path,project_class,status,summary from projects'):
        out.execute('insert into projects values (?,?,?,?,?,?)', tuple(row))
        counts['projects'] += 1
    for row in core.execute('select stream_id,title,home_path,home_exists,session_source from streams'):
        out.execute('insert into streams values (?,?,?,?,?)', tuple(row))
        counts['streams'] += 1
    roots = [dict(row) for row in core.execute('select * from roots')]
    core.close()

    browser_db = browser_dir / 'URSPRUNGSSUCHE.sqlite'
    if browser_db.exists():
        source = sqlite3.connect(f'file:{browser_db}?mode=ro', uri=True)
        source.row_factory = sqlite3.Row
        for row in source.execute('select conversation_id,title,provider,message_count,turn_count,gap_count,completeness,source_path from conversations'):
            out.execute('insert into browser_conversations values (?,?,?,?,?,?,?,?)', tuple(row))
            counts['browser_conversations'] += 1
        source.close()
    terminal_db = terminal_dir / 'TERMINAL_INDEX.sqlite'
    if terminal_db.exists():
        source = sqlite3.connect(f'file:{terminal_db}?mode=ro', uri=True)
        source.row_factory = sqlite3.Row
        for row in source.execute('select provider,session_id,modified_utc,event_count,message_count,tool_call_count,tool_result_count,source_path from sessions'):
            out.execute('insert into terminal_sessions values (?,?,?,?,?,?,?,?)', tuple(row))
            counts['terminal_sessions'] += 1
        source.close()
    findings_path = reactive_dir / 'REAKTIONSREGISTER.jsonl.gz'
    if findings_path.exists():
        with gzip.open(findings_path, 'rt', encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                out.execute('insert or replace into findings values (?,?,?,?,?,?)', (
                    row['finding_id'], row.get('kind'), row.get('subject'), row.get('summary'), row.get('severity'), row.get('truth_class'),
                ))
                counts['findings'] += 1
    facets = [
        ('facet:core', 'organ', 'Schmaler Atlas-Kern', 'Pfade, Projekte, AI-Ströme und Beziehungen ohne Originalverdopplung.', str(core_db), counts['paths'], 'available', {}),
        ('facet:browser', 'organ', 'Browserarchäologie A–F', 'Zeitreise, UI-MCP-Verwebung, Blitzmomente, Rohwunsch-Vergleich, Gesprächspakete und Ursprungssuche.', str(browser_dir), counts['browser_conversations'], 'available', {}),
        ('facet:terminal', 'organ', 'Terminalwerkstrom', 'Vollständige normalisierte Gespräche, Toolspuren, Marker und native Quellverweise.', str(terminal_dir), counts['terminal_sessions'], 'available', {}),
        ('facet:reactive', 'organ', 'Reaktiver Atlas', 'Lücken, Waisen, Behauptungsprüfung, Wiederentdeckungen und AI-Beiträge.', str(reactive_dir), counts['findings'], 'available', {}),
    ]
    for root in roots:
        facets.append((f"facet:root:{root['root_id']}", 'source_root', root['title'], root['description'], root['path'], root['source_file_count'], 'available' if root['exists_flag'] else 'missing', root))
    out.executemany('insert into facets values (?,?,?,?,?,?,?,?)', [(a,b,c,d,e,f,g,json.dumps(h, ensure_ascii=False, sort_keys=True)) for a,b,c,d,e,f,g,h in facets])
    out.execute('insert into meta values (?,?)', ('generated_utc', json.dumps(utcnow())))
    out.execute('insert into meta values (?,?)', ('counts', json.dumps(counts, ensure_ascii=False)))
    out.execute('insert into meta values (?,?)', ('purpose', json.dumps('Small fast explorative handoff; complete facet map, details on demand.')))
    out.commit()
    out.execute('vacuum')
    out.close()
    return counts


def _copy_anchor_sources(root: Path) -> list[dict[str, Any]]:
    anchors = [
        ATLAS_ROOT / 'README.md',
        ATLAS_ROOT / 'ATLAS_STATUS.json',
        ATLAS_ROOT / 'GESAMTKARTE.md',
        ATLAS_ROOT / 'GROESSENWAHRHEIT.json',
        ATLAS_ROOT / 'AI_STROEME.json',
        ATLAS_ROOT / 'AI_STROM_BRUECKEN.json',
        ATLAS_ROOT / 'KONSENSREGISTER.jsonl',
        ATLAS_ROOT / 'KONFLIKTREGISTER.jsonl',
        ATLAS_ROOT / 'auftraege/2026-07-29__GESAMTATLAS_GESAMTAUFTRAG/GESAMTAUFTRAG.md',
        ATLAS_ROOT / 'auftraege/2026-07-29__GESAMTATLAS_GESAMTAUFTRAG/sources/SICHTBARE_NUTZERSETZUNGEN.md',
        Path('/root/werkraum_gesamtatlas_eingang/START_HIER.md'),
        Path('/root/werkraum_gesamtatlas_eingang/MANIFEST.json'),
        Path('/root/werkraum/_gpt/mcp_global_protocols/gesamtatlas_v1.json'),
        Path('/root/werkraum/tools/chatgpt_browser_recorder/NAECHSTER_AUSBAUKOERPER_A_BIS_F.md'),
    ]
    for home in ('_gpt/mcp_zuhause', '_claudeweb', '_claude', '_codex', '_gemini', '_kimi', '_glm'):
        base = Path('/root/werkraum') / home
        anchors.extend([base / 'ZUHAUSE.md', base / 'RESONANZFELD.md'])
    records = []
    target_root = root / 'ORIGINALANKER'
    target_root.mkdir(parents=True, exist_ok=True)
    for source in anchors:
        if not source.exists() or not source.is_file():
            continue
        text = source.read_text('utf-8', errors='replace')
        clean, redactions = redact(text)
        name = stable_id('anchor', str(source)).split(':', 1)[1] + '__' + source.name
        target = target_root / name
        target.write_text(clean, encoding='utf-8')
        records.append({
            'source_path': str(source),
            'source_sha256': sha256_file(source),
            'capsule_path': str(target.relative_to(root)),
            'capsule_sha256': sha256_file(target),
            'copy_class': 'exact_text_copy' if redactions == 0 and '\ufffd' not in text else 'marked_external_copy',
            'redactions': redactions,
        })
    (target_root / 'ANKER_MANIFEST.json').write_text(json_text({'generated_utc': utcnow(), 'anchors': records}), encoding='utf-8')
    return records


def _write_query_script(root: Path) -> None:
    script = r'''#!/usr/bin/env python3
import argparse, json, sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parent/'MASCHINE'/'KAPSEL.sqlite'
p=argparse.ArgumentParser(description='Durchsuche die kleine Gesamtatlas-Kapsel.')
p.add_argument('query', nargs='?')
p.add_argument('--facets', action='store_true')
p.add_argument('--projects', action='store_true')
p.add_argument('--streams', action='store_true')
p.add_argument('--limit', type=int, default=50)
a=p.parse_args(); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
if a.facets:
 rows=c.execute('select * from facets order by facet_type,title limit ?', (a.limit,))
elif a.projects:
 rows=c.execute('select * from projects order by name limit ?', (a.limit,))
elif a.streams:
 rows=c.execute('select * from streams order by title limit ?', (a.limit,))
elif a.query:
 q='%'+a.query.lower()+'%'; rows=c.execute('select path,root_name,kind,size,mtime_ns,suffix from paths where lower(path) like ? or lower(basename) like ? limit ?', (q,q,a.limit))
else:
 rows=c.execute('select * from facets order by facet_type,title limit ?', (a.limit,))
print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)); c.close()
'''
    path = root / 'FRAGE_DIE_KAPSEL.py'
    path.write_text(script, encoding='utf-8')
    path.chmod(0o755)


def _write_docs(root: Path, counts: dict[str, int], anchors: list[dict[str, Any]]) -> None:
    (root / '00_START_HIER.md').write_text(f'''# Gesamtatlas-Kapsel\n\nDies ist ein **kleiner, schneller Arbeitskörper**, kein vollständiger VPS-Abguss. Er macht jede erfasste Facette auffindbar und erfragbar, ohne jedes Detail zu vervielfältigen.\n\n## Direkt beginnen\n\n- Öffne `OFFLINE/index.html` für eine lokale Erkundung.\n- Starte `python3 FRAGE_DIE_KAPSEL.py --facets`.\n- Suche mit `python3 FRAGE_DIE_KAPSEL.py "Browser-Agent"`.\n- Lies `WIE_DETAILKOERPER_ANGEFORDERT_WERDEN.md`, wenn du Originale zu einer konkreten Frage brauchst.\n\n## Umfang\n\n- {counts['paths']:,} Pfade als schlanke Referenzen\n- {counts['projects']:,} Projekte\n- {counts['streams']:,} AI-Ströme\n- {counts['browser_conversations']:,} Browsergesprächsräume\n- {counts['terminal_sessions']:,} Terminalsitzungen\n- {counts['findings']:,} offene Atlasbefunde\n- {len(anchors):,} ausgewählte Originalanker\n\nOriginale bleiben grundsätzlich an ihren Quellorten. Die Kapsel enthält Facettenkarte, Herkunft, Zustände, ausgewählte Ursprungskörper und Werkzeuge zum gezielten Weiterfragen.\n''', encoding='utf-8')
    (root / 'WAS_DAS_SYSTEM_IST.md').write_text('''# Was das System ist\n\nDer Gesamtatlas ist ein lebendes Herkunfts-, Gesprächs-, Arbeits- und Erkenntnisnetz über Daniels VPS und die daran beteiligten AI-Ströme. Er verbindet Projekte, Dateien, Zuhause, Browsergespräche, Terminalarbeit, Entscheidungen, Fehler, Korrekturen, Tests, Beziehungen und Lücken.\n\nEr ist kein Autor über den Originalen. Er hält Ursprünge, Spiegel und Ableitungen auseinander.\n''', encoding='utf-8')
    (root / 'WAS_ES_KANN_UND_NICHT_KANN.md').write_text('''# Was er kann und nicht kann\n\n## Kann\n\n- Pfade, Projekte, Begriffe, AI-Ströme, Gespräche und Terminalarbeit auffinden.\n- Ursprünge, Widersprüche, Fehlerwege und spätere Wirkungen getrennt zeigen.\n- Browsergespräche über A–F-Ansichten erforschen.\n- Terminalverläufe mit Nachrichten, Toolaufrufen und Ergebnissen normalisieren.\n- kleine, gezielte Explorationskörper erzeugen.\n- AI-Ströme eigene Notizen, Widersprüche und Impulse mit Herkunft hinterlassen lassen.\n\n## Kann nicht\n\n- nie aufgezeichnete Originale erfinden.\n- Erreichbarkeit mit tatsächlichem Lesen gleichsetzen.\n- heuristische Ähnlichkeit als bewiesene Kausalität ausgeben.\n- fremde personenbezogene Zusammenhänge vollständig automatisch erkennen.\n- in dieser kleinen Kapsel jedes Detail des VPS materiell enthalten.\n''', encoding='utf-8')
    (root / 'WIE_DETAILKOERPER_ANGEFORDERT_WERDEN.md').write_text('''# Details gezielt anfordern\n\nEin fremder Mensch oder ein LLM kann eine konkrete Frage formulieren, zum Beispiel:\n\n- „Zeige alle Ursprungsmomente des Gesamtatlas.“\n- „Erzeuge einen vollständigen Körper zu Claude Codes Arbeit am Browser-Agenten.“\n- „Zeige Rohwunsch, spätere Regelbildung und Gegenkorrekturen zum Thema X.“\n- „Gib mir Gespräch, Toolspur, Dateiwirkung und Tests zu Sitzung Y.“\n\nAuf dem VPS erzeugt dann:\n\n```bash\ngesamtatlas explore --query "THEMA"\n```\n\neinen begrenzten ZIP-Körper mit Suchtreffern, Quellverweisen, ausgewählten Originalen und sichtbaren Auslassungen.\n''', encoding='utf-8')
    (root / 'ANFRAGEVORLAGE.json').write_text(json_text({
        'query': 'Welche Facette soll vertieft werden?',
        'desired_original_depth': 'relevant_originals',
        'include_browser_history': True,
        'include_terminal_history': True,
        'include_counterevidence': True,
        'maximum_package_bytes': MAX_DETAIL_BYTES,
        'note': 'Die Kapsel ist ein Einstieg. Details werden gezielt und nachvollziehbar materialisiert.',
    }), encoding='utf-8')


def _write_offline(root: Path, counts: dict[str, int]) -> None:
    offline = root / 'OFFLINE'
    offline.mkdir(parents=True, exist_ok=True)
    cards = [
        ('Schmaler Kern', f"{counts['paths']:,} Pfade und {counts['projects']:,} Projekte", 'Keine Originalverdopplung, sondern Herkunft und gezielte Zugänge.'),
        ('Browser A–F', f"{counts['browser_conversations']:,} Gesprächsräume", 'Zeitreise, UI-MCP-Spur, Blitzmomente, Rohwunschvergleich, Pakete und Ursprungssuche.'),
        ('Terminalwerkstrom', f"{counts['terminal_sessions']:,} Sitzungen", 'Nachrichten, Tools, Fehler, Entscheidungen und Impulse getrennt.'),
        ('Reaktiver Atlas', f"{counts['findings']:,} Befunde", 'Waisen, Lücken, Widersprüche und offene Prüfungen als Einladungen.'),
    ]
    card_html = ''.join(f'<article class="card"><h2>{html.escape(title)}</h2><p><strong>{html.escape(number)}</strong></p><p>{html.escape(description)}</p></article>' for title,number,description in cards)
    body = f'<section class="hero"><p class="muted">klein · schnell · explorativ</p><h1>Ein Koffer voller <span style="color:var(--accent)">Eingänge</span>, nicht voller Doppelkopien.</h1><p>Jede Facette ist auffindbar und erfragbar. Tiefe Originalkörper werden erst für eine konkrete Frage erzeugt.</p></section><section class="grid">{card_html}</section>'
    (offline / 'index.html').write_text(_page('Start', body), encoding='utf-8')
    facets = '<section class="hero"><h1>Facetten</h1><div class="grid">' + card_html + '</div><p>Für die vollständige maschinenlesbare Karte siehe <code>../MASCHINE/KAPSEL.sqlite</code>.</p></section>'
    (offline / 'facetten.html').write_text(_page('Facetten', facets), encoding='utf-8')
    questions = '<section class="hero"><h1>Fragen statt Lesepflicht</h1><div class="grid"><article class="card">Wo wurde etwas zuerst gesagt?</article><article class="card">Was ist gebaut, was nur gedacht?</article><article class="card">Welche AI setzte welchen Impuls?</article><article class="card">Welche Fehlentscheidung führte wohin?</article><article class="card">Welche Gegenquelle widerspricht?</article><article class="card">Welcher Detailkörper soll entstehen?</article></div></section>'
    (offline / 'fragen.html').write_text(_page('Fragen', questions), encoding='utf-8')


def build_capsule(staging: Path, core_db: Path, browser_dir: Path, terminal_dir: Path, reactive_dir: Path) -> dict[str, Any]:
    capsule = staging / 'capsule'
    capsule.mkdir(parents=True, exist_ok=True)
    machine = capsule / 'MASCHINE'
    machine.mkdir(parents=True, exist_ok=True)
    counts = _capsule_db(machine / 'KAPSEL.sqlite', core_db, browser_dir, terminal_dir, reactive_dir)
    anchors = _copy_anchor_sources(capsule)
    _write_query_script(capsule)
    _write_docs(capsule, counts, anchors)
    _write_offline(capsule, counts)
    manifest = {
        'schema_version': 'gesamtatlas-capsule-3.0',
        'generated_utc': utcnow(),
        'purpose': 'small_fast_explorative_handoff',
        'public_website': False,
        'facet_complete': True,
        'detail_complete': False,
        'details_available_on_demand': True,
        'counts': counts,
        'anchors': anchors,
        'size_limits': {'capsule_bytes': MAX_CAPSULE_BYTES, 'detail_package_bytes': MAX_DETAIL_BYTES},
        'truth_boundary': 'Every indexed facet is queryable, but the capsule intentionally does not duplicate every original.',
    }
    (capsule / 'MANIFEST.json').write_text(json_text(manifest), encoding='utf-8')
    temp_zip = staging / 'GESAMTATLAS_KAPSEL_AKTUELL.zip'
    with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=8, allowZip64=True) as archive:
        for path in sorted(capsule.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(capsule).as_posix())
    with zipfile.ZipFile(temp_zip) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'capsule ZIP damaged at {bad}')
        entries = len(archive.infolist())
    if temp_zip.stat().st_size > MAX_CAPSULE_BYTES:
        raise RuntimeError(f'capsule exceeds size budget: {temp_zip.stat().st_size} > {MAX_CAPSULE_BYTES}')
    manifest.update({'zip_integrity_ok': True, 'zip_entries': entries})
    (capsule / 'MANIFEST.json').write_text(json_text(manifest), encoding='utf-8')
    # Das finale ZIP enthält ein selbstkonsistentes Manifest ohne Selbsthash.
    temp_zip.unlink()
    with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=8, allowZip64=True) as archive:
        for path in sorted(capsule.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(capsule).as_posix())
    with zipfile.ZipFile(temp_zip) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'capsule ZIP damaged at {bad}')
        final_entries = len(archive.infolist())
    return {
        'ok': True,
        'capsule_dir': str(capsule),
        'zip_path': str(temp_zip),
        **manifest,
        'zip_bytes': temp_zip.stat().st_size,
        'zip_sha256': sha256_file(temp_zip),
        'zip_entries': final_entries,
    }


def install_capsule(built_capsule_dir: Path, built_zip: Path) -> None:
    if CAPSULE_DIR.exists():
        shutil.rmtree(CAPSULE_DIR)
    shutil.copytree(built_capsule_dir, CAPSULE_DIR)
    temp = CAPSULE_ZIP.with_suffix('.tmp')
    shutil.copy2(built_zip, temp)
    temp.replace(CAPSULE_ZIP)


def build_detail_package(query: str, current: Path, destination: Path | None = None, limit: int = 80) -> Path:
    query = query.strip()
    if not query:
        raise ValueError('query required')
    core_db = current / 'KERN' / 'ATLAS_SCHMAL.sqlite'
    browser_dir = current / 'BROWSER'
    terminal_dir = current / 'TERMINAL'
    results = {
        'core': search_core(core_db, query, limit),
        'browser': origin_search(browser_dir, query, limit),
        'terminal': search_terminal(terminal_dir, query, limit),
    }
    destination = destination or (DETAIL_ROOT / f'{stable_id("exploration", query).split(":",1)[1]}__EXPLORATION.zip')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix='.explore-', dir=DETAIL_ROOT))
    try:
        (temp_dir / '00_START_HIER.md').write_text(f'''# Explorationskörper: {query}\n\nDieser Körper wurde gezielt aus der schmalen Atlasstruktur erzeugt. Treffer sind Such- und Herkunftsbelege, keine automatische Gesamterzählung.\n''', encoding='utf-8')
        (temp_dir / 'SUCHERGEBNISSE.json').write_text(json_text({'query': query, 'generated_utc': utcnow(), 'results': results}), encoding='utf-8')
        sources = []
        total = 0
        candidate_paths = []
        for row in results['core']:
            path = row.get('path')
            if path:
                candidate_paths.append(Path(path))
        for row in results['browser']:
            conversation_id = row.get('conversation_id')
            if conversation_id:
                try:
                    package = package_conversation(browser_dir, conversation_id, temp_dir / f'GESPRÄCH_{stable_id("c",conversation_id).split(":",1)[1]}.zip')
                    total += package.stat().st_size
                    sources.append({'kind': 'conversation_package', 'conversation_id': conversation_id, 'path': package.name, 'bytes': package.stat().st_size})
                except Exception as exc:
                    sources.append({'kind': 'conversation_package_error', 'conversation_id': conversation_id, 'error': str(exc)})
                if total > MAX_DETAIL_BYTES // 2:
                    break
        original_root = temp_dir / 'ORIGINALAUSWAHL'
        original_root.mkdir(exist_ok=True)
        seen = set()
        for source in candidate_paths:
            try:
                resolved = source.resolve()
            except Exception:
                continue
            if resolved in seen or not resolved.exists() or not resolved.is_file() or resolved.suffix.lower() not in TEXT_SUFFIXES:
                continue
            seen.add(resolved)
            if resolved.stat().st_size > 8_000_000 or total + resolved.stat().st_size > MAX_DETAIL_BYTES * 0.8:
                sources.append({'kind': 'reference_only', 'source_path': str(resolved), 'bytes': resolved.stat().st_size, 'reason': 'size_budget'})
                continue
            text = resolved.read_text('utf-8', errors='replace')
            clean, redactions = redact(text)
            name = stable_id('source', str(resolved)).split(':',1)[1] + '__' + resolved.name
            target = original_root / name
            target.write_text(clean, encoding='utf-8')
            total += target.stat().st_size
            sources.append({'kind': 'selected_original_copy', 'source_path': str(resolved), 'source_sha256': sha256_file(resolved), 'path': str(target.relative_to(temp_dir)), 'bytes': target.stat().st_size, 'redactions': redactions})
        (temp_dir / 'QUELLENMANIFEST.json').write_text(json_text({'query': query, 'sources': sources, 'truth_boundary': 'Selected copies may contain marked privacy/secret removals. Source hashes remain visible.'}), encoding='utf-8')
        temp_zip = destination.with_suffix('.tmp')
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=7, allowZip64=True) as archive:
            for path in sorted(temp_dir.rglob('*')):
                if path.is_file():
                    archive.write(path, path.relative_to(temp_dir).as_posix())
        if temp_zip.stat().st_size > MAX_DETAIL_BYTES:
            temp_zip.unlink(missing_ok=True)
            raise RuntimeError('detail package exceeds configured budget')
        with zipfile.ZipFile(temp_zip) as archive:
            bad = archive.testzip()
            if bad:
                raise RuntimeError(f'detail package damaged at {bad}')
        temp_zip.replace(destination)
        return destination
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
