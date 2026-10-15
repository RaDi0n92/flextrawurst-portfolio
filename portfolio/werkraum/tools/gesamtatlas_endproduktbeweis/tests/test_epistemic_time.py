#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sqlite3,subprocess,tempfile
from pathlib import Path

TOOL=Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis/time/epistemic_time.py')
REPORT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ/GA-TIME-011-TECHNICAL.json')
checks=[]
def check(name,value,detail=''):
 checks.append({'name':name,'ok':bool(value),'detail':detail})
 if not value:raise AssertionError(f'{name}: {detail}')
def run(db,*args,ok=True):
 p=subprocess.run(['python3',str(TOOL),'--db',str(db),*args],text=True,capture_output=True)
 stream=p.stdout if p.returncode==0 else p.stdout+p.stderr
 try:value=json.loads(p.stdout or '{}')
 except Exception:value={'raw':stream}
 if ok and p.returncode!=0:raise AssertionError(f'failed {args}: {stream}')
 if not ok and p.returncode==0:raise AssertionError(f'unexpected pass {args}: {stream}')
 return p,value
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def item_states(item):return {x['state']:x['effective_status'] for x in item['states']}

with tempfile.TemporaryDirectory(prefix='ga-time-test-') as td:
 td=Path(td);db=td/'time.sqlite';history=td/'history.jsonl';source=td/'source.md';display=td/'display.json';read=td/'read.json';use=td/'use.md';later=td/'later.md'
 source.write_text('Information A existiert.\n',encoding='utf-8');display.write_text('{"visible":true}\n');read.write_text('{"read":true}\n');use.write_text('A wurde in Entscheidung D verwendet.\n');later.write_text('Spätere Bedeutung wurde erkannt.\n')
 events=[
  {'event_id':'E1','timestamp_utc':'2026-01-01T10:00:00+00:00','session_id':'S1','actor':'Agent','action':'session.begin','status':'success','target':None,'parent_event_id':None,'event_hash':'h1','details':{}},
  {'event_id':'E2','timestamp_utc':'2026-01-01T10:01:00+00:00','session_id':'S1','actor':'Agent','action':'vps.read_file','status':'success','target':str(source),'parent_event_id':None,'event_hash':'h2','details':{}},
  {'event_id':'E3','timestamp_utc':'2026-01-01T10:02:00+00:00','session_id':'S1','actor':'Agent','action':'write_file','status':'success','target':str(use),'parent_event_id':None,'event_hash':'h3','details':{}},
  {'event_id':'E4','timestamp_utc':'2026-01-01T10:03:00+00:00','session_id':'S1','actor':'Agent','action':'playwright.test','status':'success','target':'test moment','parent_event_id':None,'event_hash':'h4','details':{}},
  {'event_id':'E5','timestamp_utc':'2026-01-01T10:04:00+00:00','session_id':'S1','actor':'Agent','action':'write_file','status':'success','target':str(later),'parent_event_id':None,'event_hash':'h5','details':{}},
  {'event_id':'E6','timestamp_utc':'2026-01-01T09:59:00+00:00','session_id':'S2','actor':'Other','action':'vps.shell','status':'success','target':'foreign','parent_event_id':None,'event_hash':'h6','details':{}},
 ]
 with history.open('w',encoding='utf-8') as f:
  for e in events:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 _,v=run(db,'import-history','--history',str(history));check('Sechs Ereignisse importiert',v['event_count']==6,str(v));check('History-Hash gebunden',v['history_sha256']==hashlib.sha256(history.read_bytes()).hexdigest())
 _,v2=run(db,'import-history','--history',str(history));check('History-Import idempotent',v2['inserted']==0 and v2['updated']==6,str(v2))
 bad_anchor=td/'bad_anchor.json';write(bad_anchor,{'title':'bad','at_utc':'2026-01-01T10:02:59+00:00','source_session_id':'S1','anchor_event_id':'E4','items':[]})
 run(db,'create-moment','--spec',str(bad_anchor),ok=False);check('Falsche Anchor-Zeit blockiert',True)
 missing_anchor=td/'missing_anchor.json';write(missing_anchor,{'title':'bad','at_utc':'2026-01-01T10:03:00+00:00','source_session_id':'S1','anchor_event_id':'MISSING','items':[]})
 run(db,'create-moment','--spec',str(missing_anchor),ok=False);check('Fehlender Anchor blockiert',True)
 future_known=td/'future_known.json';write(future_known,{'title':'future','at_utc':'2026-01-01T10:03:00+00:00','source_session_id':'S1','anchor_event_id':'E4','items':[{'label':'Zukunft','object_ref':'F','object_type':'fact','first_known_utc':'2026-01-01T11:00:00+00:00','known_at_moment':True}]})
 run(db,'create-moment','--spec',str(future_known),ok=False);check('Spätere Information nicht als damaliges Wissen zulässig',True)
 post_att=td/'post_att.json';write(post_att,{'title':'post','at_utc':'2026-01-01T10:03:00+00:00','source_session_id':'S1','anchor_event_id':'E4','items':[{'label':'A','object_ref':'A','object_type':'fact','attestations':[{'state':'GELESEN','status':'BEWIESEN','evidence_class':'SYSTEM_OBSERVED','evidence_ref':str(read),'observed_utc':'2026-01-01T10:04:00+00:00','actor':'reader','statement':'später gelesen'}]}]})
 run(db,'create-moment','--spec',str(post_att),ok=False);check('Späterer Beleg nicht rückwirkend zugelassen',True)
 retro_early=td/'retro_early.json';write(retro_early,{'title':'retro','at_utc':'2026-01-01T10:03:00+00:00','source_session_id':'S1','anchor_event_id':'E4','items':[],'retrospective_meaning':[{'learned_utc':'2026-01-01T10:02:00+00:00','label':'falsch','source_ref':str(later),'statement':'zu früh'}]})
 run(db,'create-moment','--spec',str(retro_early),ok=False);check('Retrospektive vor Moment blockiert',True)
 spec=td/'moment.json';write(spec,{
  'moment_id':'MOMENT-001','title':'Epistemischer Testmoment','at_utc':'2026-01-01T10:03:00+00:00','source_session_id':'S1','anchor_event_id':'E4','include_session_history':True,
  'truth_boundary':'Nur explizit attestierte Zustände gelten. Späteres Wissen bleibt retrospektiv.',
  'items':[
   {'item_id':'ITEM-A','label':'Information A','object_ref':'A','object_type':'fact','first_known_utc':'2026-01-01T10:00:00+00:00','known_at_moment':True,'source_path':str(source),'attestations':[
    {'state':'EXISTIERTE','status':'BEWIESEN','evidence_class':'DIRECT_SOURCE','evidence_ref':str(source),'observed_utc':'2026-01-01T10:00:00+00:00','actor':'filesystem','statement':'Quelle existiert'},
    {'state':'ERREICHBAR','status':'BEWIESEN','evidence_class':'SYSTEM_OBSERVED','evidence_ref':'history:E2','observed_utc':'2026-01-01T10:01:00+00:00','actor':'resolver','statement':'Pfad erreichbar'},
    {'state':'ANGEZEIGT','status':'BEWIESEN','evidence_class':'SYSTEM_OBSERVED','evidence_ref':str(display),'observed_utc':'2026-01-01T10:01:30+00:00','actor':'ui','statement':'sichtbar'},
    {'state':'GELESEN','status':'BEWIESEN','evidence_class':'SYSTEM_OBSERVED','evidence_ref':str(read),'observed_utc':'2026-01-01T10:01:40+00:00','actor':'reader','statement':'explizit gelesen'},
    {'state':'VERWENDET','status':'BEWIESEN','evidence_class':'DIRECT_SOURCE','evidence_ref':str(use),'observed_utc':'2026-01-01T10:02:00+00:00','actor':'decision-log','statement':'in Entscheidung D verwendet'}]},
   {'item_id':'ITEM-B','label':'Information B','object_ref':'B','object_type':'fact','first_known_utc':'2026-01-01T10:00:00+00:00','known_at_moment':False,'source_path':str(source),'attestations':[
    {'state':'EXISTIERTE','status':'BEWIESEN','evidence_class':'DIRECT_SOURCE','evidence_ref':str(source),'observed_utc':'2026-01-01T10:00:00+00:00','actor':'filesystem','statement':'B lag in derselben Quelle'},
    {'state':'GELESEN','status':'BEWIESEN','evidence_class':'MODEL_DERIVED','evidence_ref':'model:guess','observed_utc':'2026-01-01T10:02:00+00:00','actor':'model','statement':'wahrscheinlich gelesen'}]}
  ],
  'retrospective_meaning':[{'learned_utc':'2026-01-01T10:04:00+00:00','label':'Spätere Bedeutung','source_ref':str(later),'statement':'Erst später wurde Bedeutung X erkannt','truth_class':'RETROSPECTIVE_SOURCE_BOUND'}]
 })
 _,created=run(db,'create-moment','--spec',str(spec));check('Moment erzeugt',created['moment_id']=='MOMENT-001');check('Moment bleibt wegen Unbekanntem teilweise',created['assessment']['completeness_status']=='PARTIAL_WITH_UNKNOWNS')
 _,v=run(db,'inspect','--moment-id','MOMENT-001');check('Zwei Informationsobjekte',len(v['items'])==2);a=next(x for x in v['items'] if x['item_id']=='ITEM-A');b=next(x for x in v['items'] if x['item_id']=='ITEM-B')
 check('A alle fünf Stufen bewiesen',all(x=='BEWIESEN' for x in item_states(a).values()),str(item_states(a)))
 check('B existiert, aber ist nicht automatisch gelesen',item_states(b)['EXISTIERTE']=='BEWIESEN' and item_states(b)['GELESEN']=='UNBEKANNT',str(item_states(b)))
 check('Modellableitung beweist Lesen nicht',next(x for x in b['states'] if x['state']=='GELESEN')['sufficient_count']==0)
 check('Technischer Kontext nur eigene Session',all(x['event_id'] in {'E1','E2','E3','E4'} for x in v['technical_context']),str([x['event_id'] for x in v['technical_context']]))
 check('Ereignis nach Moment ausgeschlossen',all(x['event_id']!='E5' for x in v['technical_context']))
 check('Fremdsession ausgeschlossen',all(x['event_id']!='E6' for x in v['technical_context']))
 check('Vier technische Ereignisse bis Moment',v['assessment']['technical_event_count']==4,str(v['assessment']))
 check('Werkzeugzählung korrekt',v['assessment']['tool_event_count']==1,str(v['assessment']))
 check('Mutationszählung korrekt',v['assessment']['mutation_event_count']==1,str(v['assessment']))
 check('Retrospektive getrennt vorhanden',len(v['retrospective_meaning'])==1 and v['retrospective_meaning'][0]['learned_utc']=='2026-01-01T10:04:00+00:00')
 check('Spätere Bedeutung nicht in Items eingeschmuggelt',all(x['object_ref']!='later' for x in v['items']))
 check('Wahrheitsgrenze ausgeliefert','nicht automatisch kognitives Wissen' in v['truth_boundary'])
 check('Momentgrenze ausgeliefert','Späteres Wissen bleibt retrospektiv' in v['moment']['truth_boundary'])
 _,listed=run(db,'list');check('Genau ein gültiger Moment',listed['count']==1,str(listed['count']))
 conn=sqlite3.connect(db);check('SQLite-Integrität',conn.execute('pragma integrity_check').fetchone()[0]=='ok');check('Retrospektive eigene Tabelle',conn.execute('select count(*) from retrospective_meaning').fetchone()[0]==1);check('Keine zukünftigen technischen Ereignisse',conn.execute("select count(*) from technical_context tc join history_events h using(event_id) where h.timestamp_utc>'2026-01-01T10:03:00+00:00'").fetchone()[0]==0);conn.close()
report={'ok':all(c['ok'] for c in checks),'test_id':'GA-TIME-011-TECH-001','check_count':len(checks),'checks':checks,'truth_boundary':'Beweist Momentmodell, Zeitgrenzen, Nicht-Vererbung und getrennte Retrospektive. Beweist noch keinen vollständigen historischen Browsermoment.'}
REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
