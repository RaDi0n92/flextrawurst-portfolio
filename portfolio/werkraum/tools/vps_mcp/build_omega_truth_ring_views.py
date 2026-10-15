#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, hashlib, html, json, os, tempfile
from pathlib import Path
from typing import Any

OMEGA=Path('/root/werkraum/_gpt/gesamtatlas/omega')
POINTER=OMEGA/'VERIFIED_FULL_BASELINE.json'
DELTA=OMEGA/'LIVE_DELTA_STATE.json'
BINDING=OMEGA/'OMEGA_LEAN_BINDING.json'
WORLD_MODEL='VERIFIED_FULL_BASELINE_PLUS_VISIBLE_LIVE_DELTA'
GATES={'mcp_world_ready':OMEGA/'checkpoints/MCP_WORLD_READY.json','final_scan_ready':OMEGA/'checkpoints/FINAL_SCAN_READY.json'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p:Path,**extra:Any)->dict[str,Any]:return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),**extra}
def j(p:Path)->dict[str,Any]:
 v=json.loads(p.read_text());assert isinstance(v,dict),p;return v
def atomic(p:Path,raw:bytes)->None:
 p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def resolve_pointer()->tuple[dict[str,Any],Path,dict[str,Any]]:
 pointer=j(POINTER)
 assert pointer.get('pointer_class')=='CURRENT_VERIFIED_BASELINE_POINTER'
 assert pointer.get('status')=='CURRENT_VERIFIED_BASELINE_POINTER'
 assert pointer.get('world_model')==WORLD_MODEL
 target=pointer.get('target') or {};base=Path(str(target.get('path') or '')).resolve()
 expected=(OMEGA/'verified_full_baselines'/str(pointer['revision'])).resolve()
 base.relative_to(expected)
 assert base.is_file() and not base.is_symlink()
 assert base.stat().st_size==target.get('bytes') and sha(base)==target.get('sha256')
 b=j(base);assert b['baseline_id']==pointer['baseline_id']==target['baseline_id'];assert b['revision']==pointer['revision']==target['revision'];assert b['status']=='VERIFIED_FULL_BASELINE';assert b['world_model']==WORLD_MODEL
 checks=((b.get('verification') or {}).get('checks') or {});assert checks and all(checks.values())
 for key in ('full_refresh','full_verification'):
  r=b[key];p=Path(r['path']).resolve();p.relative_to(expected);assert p.is_file() and not p.is_symlink();assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
 assert '/runtime/last_full_' not in json.dumps(b,ensure_ascii=False)
 return b,base,pointer

def main()->int:
 b,base,pointer=resolve_pointer();d,m=j(DELTA),j(BINDING)
 bid=b['baseline_id'];lid=d['live_delta_id'];br=b['revision'];lr=d['live_revision'];checks=(b['verification']['checks'])
 bref=m['verified_full_baseline'];wref=m['world_model']['verified_full_baseline']
 assert bid==d['baseline_id']==bref['baseline_id']==wref['baseline_id']
 assert br==d['baseline_revision']==bref['revision']==wref['revision']
 assert bref['path']==wref['path']==str(base);assert bref['bytes']==base.stat().st_size;assert bref['sha256']==sha(base)
 assert d['baseline_manifest_path']==str(base) and d['baseline_manifest_sha256']==sha(base)
 assert lr==d['source_revision']==m['source_revision']
 fully_verified=bool(d['current_live_revision_fully_verified']);requires_full=bool(d['requires_new_full_verification']);dirty=bool(d['source_dirty']);mode=str(d['publication_mode'])
 if lr==br:
  assert mode=='full' and dirty is False and fully_verified is True and requires_full is False
 else:
  assert lr>br and mode=='light' and dirty is True and fully_verified is False and requires_full is True
 assert not any(path.exists() for path in GATES.values())
 generated=dt.datetime.now(dt.timezone.utc).isoformat();refresh=b['full_refresh'];verification=b['full_verification']
 if fully_verified:
  live_human=f'''Der aktuelle sichtbare Zustand heißt **`{lid}`** und steht ebenfalls bei Revision **{lr}**. Er entspricht damit exakt dem vollständig geprüften Grundstand. Veröffentlichung: **{mode}/clean**. Es besteht derzeit keine offene Neuverifikationsgrenze.'''
  live_child=f'''Der aktuelle Zettelstand trägt ebenfalls die Zahl **{lr}**. Er wurde zusammen mit dem ganzen Buch vollständig geprüft. Gerade liegt also kein ungeprüfter Zettelstapel daneben.'''
  live_html='<p class=ok>Der aktuelle Zustand entspricht dem vollständig geprüften Grundstand.</p>'
  child_html=f'Das geprüfte Buch und der aktuelle Zettelstand tragen beide die Zahl {lr}. Gerade ist alles gemeinsam vollständig kontrolliert.'
 else:
  live_human=f'''Der aktuelle sichtbare Nachlauf heißt **`{lid}`** und steht bei Revision **{lr}**. Er liegt **{lr-br} Revisionen** nach dem Vollgrundstand. Er ist **{mode}/dirty** und ausdrücklich **nicht erneut vollständig geprüft**.

Neue Spuren machen den geprüften Grundstand nicht rückwirkend falsch. Für den neuesten Gesamtstand ist später wieder ein Full-Refresh mit Vollprüfung nötig.'''
  live_child=f'''Danach kamen neue Zettel bis **{lr}** dazu. Der Zettelstapel heißt **`{lid}`**. Die Zettel sind sichtbar, aber das ganze Buch wurde mit ihnen noch nicht wieder vollständig kontrolliert.'''
  live_html='<p class=warn>Noch nicht vollständig neu geprüft.</p>'
  child_html=f'Das geprüfte Buch liegt fest im Schrank. Neue Zettel bis {lr} sind sichtbar, aber noch nicht gemeinsam neu geprüft.'
 historical=b.get('historical_binding_observation')
 if isinstance(historical,dict):
  historical_human='Vom damaligen Live-Binding wurde nur der beobachtete SHA-256 festgehalten. Die historischen Binding-Bytes wurden **nicht erhalten** und **nicht rekonstruiert**.'
  historical_html='Die historischen Binding-Bytes wurden nicht erhalten und nicht rekonstruiert.'
 else:
  historical_human='Für diesen neu verifizierten Grundstand ist kein separater historischer Live-Binding-Körper gebunden. Es werden keine fehlenden historischen Bytes erfunden oder rekonstruiert.'
  historical_html='Für diesen Grundstand wird kein fehlender historischer Binding-Körper erfunden.'
 human=f'''# Gesamtatlas · menschlicher Wahrheitsstand

## Was sicher geprüft ist

Der **Vollgrundstand `{bid}`** bei Revision **{br}** wurde vollständig geprüft. Alle **19 Vollprüfungen** sind grün. Er liegt dauerhaft unter:

`{base}`

Seine zwei revisionsgebundenen Beweise sind:

- Vollrefresh: `{refresh['path']}`
- Vollverifikation: `{verification['path']}`

Der kleine Zeiger `VERIFIED_FULL_BASELINE.json` enthält nicht noch einmal das ganze Buch. Er bindet Zielpfad, Bytezahl und SHA-256 des Grundstands.

## Aktueller sichtbarer Zustand

{live_human}

## Historische Bindungsgrenze

{historical_human}

## Wege

- Kleiner Zeiger: `VERIFIED_FULL_BASELINE.json`
- Maschinenmanifest: `TRUTH_RING_MANIFEST.json`
- Kindleichter Einstieg: `CHILD_EASY_STATUS.md`
- Aktueller Nachlauf: `LIVE_DELTA_STATE.json`
- Begehbare Welt: `/gesamtatlas/`

## Tore

`MCP_WORLD_READY` und `FINAL_SCAN_READY` sind noch nicht gesetzt. Dieser Ring ist noch keine Gesamtfreigabe.
'''
 child=f'''# Gesamtatlas für Kinder erklärt

Stell dir ein vollständig geprüftes Buch in einem festen Schrank vor.

Das Buch heißt **`{bid}`** und trägt die Zahl **{br}**. Im selben Fach liegen zwei Beweisblätter: der Vollrefresh und die Vollverifikation.

Vorne hängt nur ein kleines Schild. Das Schild heißt `VERIFIED_FULL_BASELINE.json` und sagt genau, in welchem Fach das Buch liegt und welchen Fingerabdruck es hat. Das Schild ist nicht heimlich ein zweites Buch.

{live_child}

{historical_human}

Zurück zum genauen Text: `HUMAN_READABLE_STATUS.md`
'''
 manifest={'schema_version':'2.0','generated_utc':generated,'kind':'OMEGA_TRUTH_RING','status':'RING_PASS_NOT_WORLD_READY','world_model':WORLD_MODEL,
  'pointer':ref(POINTER,pointer_class=pointer['pointer_class'],baseline_id=bid,revision=br,target=pointer['target']),
  'baseline':{'id':bid,'revision':br,'manifest':ref(base),'full_refresh':refresh,'full_verification':verification,'verification_check_count':len(checks),'all_verification_checks_pass':all(checks.values()),'mutable_latest_aliases':b.get('mutable_latest_aliases')},
  'live_delta':{'id':lid,'revision':lr,'baseline_id':d['baseline_id'],'baseline_revision':d['baseline_revision'],'revision_distance':d['revision_distance_from_baseline'],'publication_mode':d['publication_mode'],'dirty':d['source_dirty'],'current_live_revision_fully_verified':d['current_live_revision_fully_verified'],'requires_new_full_verification':d['requires_new_full_verification'],'manifest':ref(DELTA)},
  'binding':ref(BINDING),'historical_binding':historical,'human_views':{},'gates':{k:{'path':str(p),'present':p.exists()} for k,p in GATES.items()},
  'return_paths':['HUMAN_READABLE_STATUS.md','CHILD_EASY_STATUS.md','TRUTH_RING_MANIFEST.json','TRUTH_RING_VIEW.html','/gesamtatlas/'],
  'einschraenkung':'Pointer, revisionsgebundener Grundstand, immutable Evidence und Live-Nachlauf werden getrennt gebunden. Keine Ready-Freigabe.'}
 atomic(OMEGA/'HUMAN_READABLE_STATUS.md',human.encode());atomic(OMEGA/'CHILD_EASY_STATUS.md',child.encode())
 view=f'''<!doctype html><html lang=de><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Gesamtatlas Wahrheitsring</title><style>*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;font:18px/1.55 system-ui;background:#17131f;color:#f8efff}}main{{max-width:1060px;margin:auto;padding:clamp(14px,5vw,52px)}}section{{background:#241d30;border:1px solid #76658c;border-radius:22px;padding:clamp(18px,4vw,34px);margin:18px 0;overflow-wrap:anywhere}}h1{{font-size:clamp(2.4rem,8vw,5rem);line-height:1}}.ids,code{{font-family:ui-monospace,monospace;word-break:break-all}}.ok{{color:#aef4c4}}.warn{{color:#ffd58e}}a{{color:#dfc2ff}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px}}.big{{font-size:clamp(2rem,7vw,4rem);font-weight:800}}</style><main><section><p>Maschinell erzeugte menschliche Ansicht</p><h1 id=verdict class=ok>WAHRHEITSRING PASS</h1><p>Pointer, dauerhafter Grundstand, Beweisblätter und lebender Nachlauf bleiben getrennt.</p></section><div class=grid><section><h2>Geprüfter Grundstand</h2><div id=baseline-revision class=big>{br}</div><p id=baseline-id class=ids>{html.escape(bid)}</p><p class=ok>{len(checks)}/{len(checks)} Vollprüfungen bestanden.</p></section><section><h2>Lebender Nachlauf</h2><div id=live-revision class=big>{lr}</div><p id=live-id class=ids>{html.escape(lid)}</p>{live_html}</section></div><section id=pointer><h2>Das kleine Schild</h2><p>Der Pointer ist {POINTER.stat().st_size} Bytes groß und zeigt auf:</p><code>{html.escape(str(base))}</code><p>SHA-256: <code>{sha(base)}</code></p></section><section id=evidence><h2>Unveränderliche Beweisblätter</h2><p><code>{html.escape(refresh['path'])}</code></p><p><code>{html.escape(verification['path'])}</code></p></section><section id=child><h2>Wie für ein Kind</h2><p>{child_html}</p></section><section><h2>Was wir nicht vortäuschen</h2><p id=history-gap>{historical_html}</p></section><section><h2>Weiter und zurück</h2><p><a id=human-link href="HUMAN_READABLE_STATUS.md">Menschlicher Text</a> · <a id=child-link href="CHILD_EASY_STATUS.md">Kindereinstieg</a> · <a id=machine-link href="TRUTH_RING_MANIFEST.json">Maschinenmanifest</a> · <a id=world-link href="/gesamtatlas/">Begehbare Welt</a></p><p id=gates>Die Welt- und Finaltore bleiben geschlossen.</p></section></main></html>'''
 atomic(OMEGA/'TRUTH_RING_VIEW.html',view.encode());manifest['human_views']={k:ref(OMEGA/v) for k,v in {'human':'HUMAN_READABLE_STATUS.md','child':'CHILD_EASY_STATUS.md','visible':'TRUTH_RING_VIEW.html'}.items()};atomic(OMEGA/'TRUTH_RING_MANIFEST.json',(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode())
 print(json.dumps({'ok':True,'baseline_id':bid,'live_delta_id':lid,'pointer':ref(POINTER),'baseline':ref(base),'outputs':{x:ref(OMEGA/x) for x in ['HUMAN_READABLE_STATUS.md','CHILD_EASY_STATUS.md','TRUTH_RING_MANIFEST.json','TRUTH_RING_VIEW.html']}},ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
