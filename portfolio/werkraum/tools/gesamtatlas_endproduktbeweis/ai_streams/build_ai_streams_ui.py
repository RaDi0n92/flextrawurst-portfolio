#!/usr/bin/env python3
from __future__ import annotations
import html,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ATLAS=Path('/root/werkraum/_gpt/gesamtatlas')
PROOF=ATLAS/'endproduktbeweis'
UI=PROOF/'UI'; OUT=PROOF/'AI_STROEME'
UI.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
streams=json.loads((ATLAS/'AI_STROEME.json').read_text('utf-8'))
bridges=json.loads((ATLAS/'AI_STROM_BRUECKEN.json').read_text('utf-8'))['streams']
verify=json.loads((ATLAS/'runtime/last_full_verification.json').read_text('utf-8'))
ids=[x['id'] for x in streams]
assert len(streams)==8 and len(bridges)==8 and set(ids)==set(bridges)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
status={'ok':True,'schema_version':'1.0','generated_utc':datetime.now(timezone.utc).isoformat(),'stream_count':len(streams),'bridge_count':len(bridges),'stream_ids':ids,'claudeweb_id':'claudeweb','claudeweb_registered':True,'full_verification_ok':verify['ok'],'full_verified_revision':verify['verified_revision'],'truth_boundary':'AI-Ströme sind getrennte dateigebundene Arbeits- und Herkunftsräume. Das Register behauptet keine gemeinsame Erinnerung, Identität oder dauerhaft laufende Instanz.','hashes':{'AI_STROEME.json':sha(ATLAS/'AI_STROEME.json'),'AI_STROM_BRUECKEN.json':sha(ATLAS/'AI_STROM_BRUECKEN.json'),'last_full_verification.json':sha(ATLAS/'runtime/last_full_verification.json')}}
(OUT/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf-8')
(OUT/'AI_STROEME.json').write_text(json.dumps(streams,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf-8')
(OUT/'AI_STROM_BRUECKEN.json').write_text(json.dumps({'streams':bridges},ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf-8')
css=''':root{color-scheme:dark;--bg:#0c0812;--panel:#181020;--panel2:#21152d;--ink:#f6edfb;--muted:#c9b7d6;--line:#503d61;--accent:#d3a6ff;--green:#9de4bd;--amber:#ffd48c}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 15% 0,#2a173d,#0c0812 50%);color:var(--ink);font:16px/1.5 system-ui,sans-serif}header,main,footer{max-width:1220px;margin:auto;padding:1rem}h1{font-size:clamp(2.5rem,7vw,5rem);line-height:.98;margin:.4rem 0 1rem;overflow-wrap:anywhere;hyphens:auto}a{color:#e1c1ff}.muted{color:var(--muted)}.hero{padding:2.5rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}.card,.panel{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;padding:1rem;min-width:0;overflow-wrap:anywhere;word-break:break-word}.number{font-size:2rem;font-weight:800;color:var(--accent)}.status{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.15rem .5rem}.green{color:var(--green)}.amber{color:var(--amber)}code{white-space:normal}.anchors{padding-left:1.2rem}.identity{border-left:4px solid var(--accent);padding-left:.8rem}.claudeweb{outline:2px solid var(--accent)}@media(max-width:680px){body{font-size:14px}header,main,footer{padding:.7rem}h1{font-size:2rem;line-height:1.02}.grid{grid-template-columns:1fr}}'''
cards=[]
for s in streams:
 b=bridges[s['id']]
 anchors=''.join(f'<li>{html.escape(x)}</li>' for x in s.get('entry_files',[])) or '<li>keine Einstiegsdatei erkannt</li>'
 cards.append(f'''<article class="card stream-card {'claudeweb' if s['id']=='claudeweb' else ''}" data-stream-id="{html.escape(s['id'])}" data-bridge="true"><p class="muted">AI-Strom</p><h2>{html.escape(s['id'])}</h2><p><span class="status green">Zuhause erkannt</span> <span class="status green">Bridge r{b.get('revision')}</span></p><p><strong>Home:</strong> <code>{html.escape(s.get('home') or 'nicht erkannt')}</code></p><p><strong>Verlauf:</strong> <code>{html.escape(s.get('sessions') or 'nicht erkannt')}</code></p><p><strong>Sessiondateien:</strong> {s.get('session_source_stats',{}).get('file_count',0)}</p><p><strong>indizierte Sitzungsdokumente:</strong> {b.get('indexed_session_document_count',0)}</p><h3>Einstiegsanker</h3><ul class="anchors">{anchors}</ul><p class="identity"><strong>Identitätsgrenze:</strong> {html.escape(s.get('identity_boundary') or 'nicht explizit gesetzt')}</p><p class="muted">Bridge-Fingerprint: {html.escape(b.get('fingerprint',''))}</p></article>''')
body=f'''<section class="hero"><p class="muted">GA-HOME-001 · acht getrennte AI-Ströme</p><h1>Acht Zuhause. <span style="color:var(--accent)">Keine Einheitsfantasie.</span></h1><p>Jeder Strom behält Herkunft, Dateien, Verlauf und eigene Bridge. Gegenseitige Lesbarkeit ist nicht dasselbe wie gemeinsame Erinnerung.</p></section><section class="grid"><article class="card"><div class="number">{len(streams)}</div><p>registrierte AI-Ströme</p></article><article class="card"><div class="number">{len(bridges)}</div><p>zugehörige Brücken</p></article><article class="card"><div class="number">{verify['counts']['status_text_documents']}</div><p>vollständig indizierte Textdokumente</p></article></section><section class="panel"><h2>Claude Web ist jetzt im Kreislauf</h2><p><code>/root/werkraum/_claudeweb</code> ist ein eigener achter Strom mit Verlauf unter <code>_claudeweb/verlauf</code>. Es bleibt ausdrücklich getrennt von Claude Code und ChatGPT.</p></section><section class="grid" id="streams">{''.join(cards)}</section><section class="panel"><strong>Wahrheitsgrenze:</strong> {html.escape(status['truth_boundary'])}</section>'''
page=f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Acht AI-Ströme · Gesamtatlas</title><style>{css}</style></head><body><header><a href="index.html">Anforderungen</a> · <a href="../AI_STROEME/AI_STROEME.json">Stromdaten</a> · <a href="../AI_STROEME/AI_STROM_BRUECKEN.json">Brückendaten</a></header><main>{body}</main><footer><p class="muted">Private lokale Beweisoberfläche. Keine öffentliche Atlasroute.</p></footer></body></html>'''
(UI/'ai-stroeme.html').write_text(page,'utf-8')
# Main navigation remains regenerable: inject link after normal builder has run.
index=UI/'index.html'; text=index.read_text('utf-8')
if 'ai-stroeme.html' not in text:
 text=text.replace(' · <a href="zeitreise.html">Zeitreise</a></header>',' · <a href="zeitreise.html">Zeitreise</a> · <a href="ai-stroeme.html">AI-Ströme</a></header>',1)
 index.write_text(text,'utf-8')
print(json.dumps({'ok':True,'stream_count':8,'bridge_count':8,'ui':str(UI/'ai-stroeme.html'),'stream_ids':ids},ensure_ascii=False))
