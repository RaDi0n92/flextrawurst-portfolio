from __future__ import annotations

import html
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from common import json_text, load_json, utcnow

CSS = '''
:root{color-scheme:dark;--bg:#0e0915;--panel:#191122;--ink:#f5ecfa;--muted:#c9b4d7;--line:#4d3a5d;--accent:#d0a1ff;--ok:#9ee4be;--warn:#ffd186}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 12% 0,#2c1741,#0e0915 52%);color:var(--ink);font:17px/1.55 system-ui,sans-serif}header,main,footer{max-width:1180px;margin:auto;padding:1rem}nav{display:flex;gap:.55rem;flex-wrap:wrap;position:sticky;top:0;background:rgba(14,9,21,.94);padding:.7rem;z-index:3}nav a,.button{border:1px solid var(--line);border-radius:999px;padding:.5rem .75rem;text-decoration:none;color:#e4c5ff}a{color:#e4c5ff}.hero{padding:3rem 0 2rem}.hero h1{font-size:clamp(2.5rem,7vw,5.5rem);line-height:.96;margin:.2rem 0 1rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:1rem}.card{display:block;background:linear-gradient(145deg,#1d1427,#130d1b);border:1px solid var(--line);border-radius:18px;padding:1rem;color:inherit;text-decoration:none;overflow-wrap:anywhere}.number{font-size:2.2rem;font-weight:800;color:var(--accent)}.muted{color:var(--muted)}.status{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.15rem .5rem}.ok{color:var(--ok)}.warn{color:var(--warn)}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid var(--line);padding:.55rem;vertical-align:top}input{width:100%;padding:.8rem;border:1px solid var(--line);border-radius:12px;background:#0c0811;color:var(--ink)}code{overflow-wrap:anywhere}.notice{border-left:4px solid var(--warn);background:#22191b;border-radius:10px;padding:1rem}@media(max-width:500px){body{font-size:15px}header,main,footer{padding:.75rem}th:nth-child(3),td:nth-child(3){display:none}}
'''

NAV = [('index.html','Start'),('kern.html','Kern'),('haeuser.html','AI-Zuhause'),('browser.html','Browser A–F'),('terminal.html','Terminal'),('reaktion.html','Reaktion'),('kapsel.html','Kapsel'),('suche.html','Suche')]


def page(title: str, body: str) -> str:
    nav = ''.join(f'<a href="{href}">{html.escape(label)}</a>' for href,label in NAV)
    return f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · Gesamtatlas</title><style>{CSS}</style></head><body><header><nav>{nav}</nav></header><main>{body}</main><footer><p class="muted">Lokaler Gesamtatlas-Dateikörper. Die öffentliche Route bleibt abgeschaltet.</p></footer></body></html>'


def _status(path: Path) -> dict[str, Any]:
    return load_json(path, {}) or {}


def _card(title: str, number: Any, text: str, href: str = '#') -> str:
    return f'<a class="card" href="{href}"><h2>{html.escape(title)}</h2><div class="number">{html.escape(str(number))}</div><p>{html.escape(text)}</p></a>'


def render_ui(root: Path, stage: int) -> dict[str, Any]:
    ui = root / 'UI'
    if ui.exists():
        shutil.rmtree(ui)
    ui.mkdir(parents=True)
    core = _status(root / 'KERN/STATUS.json')
    homes = _status(root / 'HÄUSER/STATUS.json')
    browser = _status(root / 'BROWSER/STATUS.json')
    terminal = _status(root / 'TERMINAL/STATUS.json')
    reactive = _status(root / 'REAKTION/STATUS.json')
    capsule = _status(root / 'KAPSEL_STATUS.json')
    cards = [
        _card('Schmaler Kern', core.get('counts', {}).get('paths', '–'), 'Pfade als Verweise statt Doppelkopien.', 'kern.html'),
        _card('AI-Zuhause', homes.get('homes_present', '–'), 'Getrennte Häuser, gemeinsam erforschbar.', 'haeuser.html'),
        _card('Browser A–F', browser.get('totals', {}).get('conversations', '–'), 'Zeitreise bis Ursprungssuche.', 'browser.html'),
        _card('Terminalwerkstrom', terminal.get('totals', {}).get('sessions', '–'), 'Gespräche, Tools, Fehler und Impulse.', 'terminal.html'),
        _card('Reaktiver Atlas', reactive.get('finding_count', '–'), 'Lücken und Widersprüche als Arbeitsimpulse.', 'reaktion.html'),
        _card('Kleine Kapsel', capsule.get('zip_bytes', '–'), 'Facettenvollständig, nicht detailvollständig.', 'kapsel.html'),
    ]
    body = f'''<section class="hero"><p class="muted">Bauabschnitt {stage} von 7 · Playwright-Abnahme vor jedem Weiterbau</p><h1>Ein schmaler Atlas, der <span style="color:var(--accent)">überallhin führt.</span></h1><p>Originale bleiben an ihren Orten. Der Atlas verbindet Herkunft, Gespräche, AI-Häuser, Terminalarbeit, Fehler, Beziehungen und gezielte Explorationskörper.</p></section><section class="grid">{''.join(cards)}</section><section class="notice"><strong>Keine öffentliche Website:</strong> <code>https://flextrawurst.de/gesamtatlas/</code> bleibt absichtlich nicht ausgeliefert.</section>'''
    (ui / 'index.html').write_text(page('Start', body), encoding='utf-8')

    core_body = '<section class="hero"><h1>Schmaler Kern</h1><p>Vollständige Erreichbarkeit ohne vollständige Vervielfältigung.</p></section>'
    if core:
        core_body += '<section class="grid">' + ''.join([
            _card('Pfade', core.get('counts', {}).get('paths', 0), 'Schlanke Herkunftsreferenzen.'),
            _card('Projekte', core.get('counts', {}).get('projects', 0), 'Kanonische und technische Projektkörper.'),
            _card('AI-Ströme', core.get('counts', {}).get('streams', 0), 'Getrennte Herkunft und Häuser.'),
            _card('Vorschauen', core.get('counts', {}).get('previews', 0), 'Kurze redigierte Suchausschnitte.'),
        ]) + '</section><p><a href="../KERN/STATUS.json">Maschinenstatus</a> · <a href="../KERN/ATLAS_SCHMAL.sqlite">SQLite-Kern</a></p>'
    else:
        core_body += '<p class="notice">Dieser Körper entsteht in Bauabschnitt 2.</p>'
    (ui / 'kern.html').write_text(page('Kern', core_body), encoding='utf-8')

    home_cards = []
    for stream, status in (homes.get('streams') or {}).items():
        home_cards.append(_card(stream, status.get('file_count', 0), f"{status.get('source_bytes',0):,} Quellbytes nur referenziert."))
    homes_body = '<section class="hero"><h1>Getrennte Zuhause</h1><p>Jeder AI-Strom behält seine Herkunft. Importierte Grundrisse werden nicht zu eigener Erinnerung umetikettiert.</p></section>'
    homes_body += '<section class="grid">' + ''.join(home_cards) + '</section>' if home_cards else '<p class="notice">Dieser Körper entsteht in Bauabschnitt 3.</p>'
    (ui / 'haeuser.html').write_text(page('AI-Zuhause', homes_body), encoding='utf-8')

    browser_body = '<section class="hero"><h1>Browserarchäologie A–F</h1><p>Gespräche bleiben Originalkörper. Zusätzliche Ansichten liegen reproduzierbar daneben.</p></section>'
    if browser:
        labels = browser.get('a_to_f', {})
        browser_body += '<section class="grid">' + ''.join(_card(key, '✓', value.replace('_',' ')) for key,value in labels.items()) + '</section>'
        browser_body += f'<p>{browser.get("totals",{}).get("messages",0):,} Nachrichten · {browser.get("totals",{}).get("gaps",0):,} protokollierte Lücken</p><p><a href="../BROWSER/STATUS.json">Maschinenstatus</a></p>'
    else:
        browser_body += '<p class="notice">Dieser Körper entsteht in Bauabschnitt 4.</p>'
    (ui / 'browser.html').write_text(page('Browser A–F', browser_body), encoding='utf-8')

    terminal_body = '<section class="hero"><h1>Terminalwerkstrom</h1><p>Daniel, Agent, Werkzeug und Ergebnis bleiben chronologisch getrennt sichtbar.</p></section>'
    provider_cards = []
    for provider, status in (terminal.get('providers') or {}).items():
        provider_cards.append(_card(provider, status.get('sessions',0), status.get('status','unbekannt')))
    terminal_body += '<section class="grid">' + ''.join(provider_cards) + '</section>' if provider_cards else '<p class="notice">Dieser Körper entsteht in Bauabschnitt 5.</p>'
    if terminal:
        terminal_body += f'<p>{terminal.get("totals",{}).get("events",0):,} Ereignisse · {terminal.get("totals",{}).get("tool_calls",0):,} Toolaufrufe</p><p><a href="../TERMINAL/STATUS.json">Maschinenstatus</a></p>'
    (ui / 'terminal.html').write_text(page('Terminal', terminal_body), encoding='utf-8')

    reactive_body = '<section class="hero"><h1>Reaktiver Atlas</h1><p>Er darf finden, fragen und vorschlagen. Er darf keine Originale automatisch verschieben oder seine Ableitungen zur Wahrheit ernennen.</p></section>'
    if reactive:
        reactive_body += '<section class="grid">' + ''.join(_card(kind, count, 'Offene, markierte Befundklasse.') for kind,count in (reactive.get('finding_kinds') or {}).items()) + '</section>'
        reactive_body += f'<p>{reactive.get("impulse_count",0):,} verfügbare Arbeitsimpulse · <a href="../REAKTION/STATUS.json">Maschinenstatus</a></p>'
    else:
        reactive_body += '<p class="notice">Dieser Körper entsteht in Bauabschnitt 6.</p>'
    (ui / 'reaktion.html').write_text(page('Reaktion', reactive_body), encoding='utf-8')

    capsule_body = '<section class="hero"><h1>Kleine übertragbare Kapsel</h1><p>Sie enthält jede Facette als Eingang, aber nicht jedes Detail als Kopie.</p></section>'
    if capsule:
        capsule_body += '<section class="grid">' + ''.join([
            _card('ZIP-Größe', capsule.get('zip_bytes', 0), 'Hartes Größenbudget: 25 MB.'),
            _card('Pfade erfragbar', capsule.get('counts',{}).get('paths',0), 'Schlanker Pfadindex in SQLite.'),
            _card('Originalanker', len(capsule.get('anchors') or []), 'Ausgewählte Ursprungskörper mit Hash.'),
        ]) + '</section><p><a href="../GESAMTATLAS_KAPSEL_AKTUELL.zip">Lokale ZIP-Datei</a> · <a href="../capsule/OFFLINE/index.html">Kapsel erkunden</a></p>'
    else:
        capsule_body += '<p class="notice">Dieser Körper entsteht in Bauabschnitt 7.</p>'
    (ui / 'kapsel.html').write_text(page('Kapsel', capsule_body), encoding='utf-8')

    search_rows = []
    core_db = root / 'KERN/ATLAS_SCHMAL.sqlite'
    if core_db.exists():
        connection = sqlite3.connect(f'file:{core_db}?mode=ro', uri=True)
        connection.row_factory = sqlite3.Row
        for row in connection.execute('select path,root_name,kind,size,basename from paths where is_dir=0 order by mtime_ns desc limit 2500'):
            search_rows.append(dict(row))
        connection.close()
    payload = json.dumps(search_rows, ensure_ascii=False).replace('</', '<\\/')
    search_body = f'''<section class="hero"><h1>Lokale Schnellsuche</h1><p>Die vollständige Suche läuft über <code>gesamtatlas search</code>. Hier liegt ein kleiner UI-Ausschnitt.</p><input id="q" placeholder="Pfad oder Begriff"><p id="count" class="muted"></p><div id="results" class="grid"></div></section><script>const D={payload};const q=document.getElementById('q'),o=document.getElementById('results'),c=document.getElementById('count');function e(s){{return String(s).replace(/[&<>"']/g,x=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[x]))}}function run(){{const n=q.value.trim().toLowerCase();const r=n?D.filter(x=>(x.path+' '+x.basename+' '+x.root_name).toLowerCase().includes(n)).slice(0,100):[];c.textContent=r.length+' Treffer';o.innerHTML=r.map(x=>'<article class="card"><h2>'+e(x.basename)+'</h2><p>'+e(x.path)+'</p></article>').join('')}}q.addEventListener('input',run);</script>'''
    (ui / 'suche.html').write_text(page('Suche', search_body), encoding='utf-8')
    ui_status = {'ok': True, 'generated_utc': utcnow(), 'stage': stage, 'pages': [path.name for path in sorted(ui.glob('*.html'))], 'search_sample_rows': len(search_rows)}
    (ui / 'STATUS.json').write_text(json_text(ui_status), encoding='utf-8')
    return ui_status
