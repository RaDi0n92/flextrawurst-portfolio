#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3, subprocess, tempfile
from pathlib import Path

TOOL=Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis/terminal/terminal_effects.py')
REPORT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ/GA-TERMINAL-034-TECHNICAL.json')
checks=[]
def check(name,value,detail=''):
 checks.append({'name':name,'ok':bool(value),'detail':detail})
 if not value:raise AssertionError(f'{name}: {detail}')
def run(db,*args,ok=True):
 p=subprocess.run(['python3',str(TOOL),'--db',str(db),*args],text=True,capture_output=True)
 stream=p.stdout if p.returncode==0 else p.stderr
 try:value=json.loads(stream)
 except Exception:value={'raw':stream}
 if ok and p.returncode!=0:raise AssertionError(f'failed {args}: {stream}')
 if not ok and p.returncode==0:raise AssertionError(f'unexpected pass {args}: {stream}')
 return p,value

def write_spec(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

with tempfile.TemporaryDirectory(prefix='ga-terminal-effects-') as td:
 td=Path(td);db=td/'effects.sqlite';history=td/'history.jsonl';artifact=td/'artifact.txt';artifact.write_text('geprüftes Artefakt\n',encoding='utf-8')
 rows=[
  {'event_id':'E1','timestamp_utc':'2026-01-01T10:00:00+00:00','session_id':'S1','actor':'Daniel','action':'ui_visible.message_recorded','status':'success','completeness':'complete','target':'Impuls','parent_event_id':None,'event_hash':'h1','details':{'role':'user'}},
  {'event_id':'E2','timestamp_utc':'2026-01-01T10:00:01+00:00','session_id':'S1','actor':'Agent','action':'vps.shell','status':'failed','completeness':'complete','target':'python test.py --port 1234','parent_event_id':'E1','event_hash':'h2','details':{}},
  {'event_id':'E3','timestamp_utc':'2026-01-01T10:00:03+00:00','session_id':'S1','actor':'Agent','action':'vps.shell','status':'success','completeness':'complete','target':'python test.py --port 1234','parent_event_id':'E2','event_hash':'h3','details':{}},
  {'event_id':'E4','timestamp_utc':'2026-01-01T10:00:04+00:00','session_id':'S1','actor':'Agent','action':'write_file','status':'success','completeness':'complete','target':str(artifact),'parent_event_id':'E3','event_hash':'h4','details':{}},
  {'event_id':'E5','timestamp_utc':'2026-01-01T10:00:05+00:00','session_id':'S2','actor':'Agent','action':'vps.shell','status':'failed','completeness':'complete','target':'different','parent_event_id':None,'event_hash':'h5','details':{}},
 ]
 with history.open('w',encoding='utf-8') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 _,v=run(db,'import-history','--history',str(history))
 check('Fünf Ereignisse importiert',v['event_count']==5,str(v))
 check('Drei explizite Parent-Links gezählt',v['parent_event_count']==3,str(v['parent_event_count']))
 check('Ein Fehler-Erfolg-Kandidat',v['correction_candidates']==1,str(v['correction_candidates']))
 check('Kandidaten als nicht kausal markiert','keine Kausalbeweise' in v['truth_boundary'])
 _,v2=run(db,'import-history','--history',str(history))
 check('Import idempotent',v2['inserted']==0 and v2['updated']==5,str(v2))
 conn=sqlite3.connect(db);conn.row_factory=sqlite3.Row
 cand=dict(conn.execute('select * from correction_candidates').fetchone())
 check('Kandidat gleiche Zielsignatur',cand['failed_event_id']=='E2' and cand['successor_event_id']=='E3')
 check('Kandidat explizit nicht Beweis',cand['status']=='CANDIDATE_NOT_CAUSAL_PROOF')
 check('Fehlaktion klassifiziert',conn.execute("select event_class from imported_events where event_id='E2'").fetchone()[0]=='FAILED_ACTION')
 check('Dateimutation klassifiziert',conn.execute("select event_class from imported_events where event_id='E4'").fetchone()[0]=='FILE_MUTATION')
 conn.close()
 # Missing source must fail.
 bad=td/'bad.json';write_spec(bad,{'title':'bad','requirement_id':'R','nodes':[{'key':'x','node_type':'TOOL','label':'x','source_type':'history_event','source_ref':'MISSING'}],'links':[]})
 run(db,'create-chain','--spec',str(bad),ok=False);check('Fehlendes History-Ereignis blockiert',True)
 # Invalid line range must fail.
 badrange=td/'badrange.json';write_spec(badrange,{'title':'bad range','requirement_id':'R','nodes':[{'key':'x','node_type':'IMPULS','label':'x','source_type':'source_range','source_ref':str(artifact),'start_line':2,'end_line':9}],'links':[]})
 run(db,'create-chain','--spec',str(badrange),ok=False);check('Ungültiger Quellenbereich blockiert',True)
 # Strong link without evidence refs must fail.
 nostrong=td/'nostrong.json';write_spec(nostrong,{'title':'no evidence','requirement_id':'R','nodes':[{'key':'a','node_type':'TOOL','label':'a','source_type':'history_event','source_ref':'E2'},{'key':'b','node_type':'TEST','label':'b','source_type':'history_event','source_ref':'E3'}],'links':[{'from':'a','to':'b','relation':'test','relation_class':'COMMON_ARTIFACT_SUPPORTED'}]})
 run(db,'create-chain','--spec',str(nostrong),ok=False);check('Starker Link ohne Beleg blockiert',True)
 # Candidate may never make causal claim.
 fakecause=td/'fakecause.json';write_spec(fakecause,{'title':'fake cause','requirement_id':'R','nodes':[{'key':'a','node_type':'TOOL','label':'a','source_type':'history_event','source_ref':'E2'},{'key':'b','node_type':'KORREKTUR','label':'b','source_type':'history_event','source_ref':'E3'}],'links':[{'from':'a','to':'b','relation':'folgte','relation_class':'SAME_TARGET_SUCCESSOR','causal_claim':True}]})
 run(db,'create-chain','--spec',str(fakecause),ok=False);check('Kausalbehauptung aus Kandidat blockiert',True)
 # Partial honest chain with gap.
 partial=td/'partial.json';write_spec(partial,{
  'chain_id':'CHAIN-PARTIAL','title':'Teilweise belegte Kette','requirement_id':'GA-TERMINAL-034','source_session_id':'S1',
  'nodes':[
   {'key':'impulse','node_type':'IMPULS','label':'Nutzerimpuls','source_type':'history_event','source_ref':'E1'},
   {'key':'interpretation','node_type':'LUECKE','label':'Interpretation nicht protokolliert','source_type':'gap','gap_reason':'Kein sichtbarer Assistenztext'},
   {'key':'tool','node_type':'TOOL','label':'Fehlgeschlagener Test','source_type':'history_event','source_ref':'E2'},
   {'key':'correction','node_type':'KORREKTUR','label':'Späterer Erfolg','source_type':'history_event','source_ref':'E3'},
   {'key':'effect','node_type':'DATEI_ODER_DIENST','label':'Artefakt','source_type':'file','source_ref':str(artifact)},
  ],
  'links':[
   {'from':'impulse','to':'interpretation','relation':'Interpretation fehlt','relation_class':'UNLINKED_GAP','explanation':'Nicht aufgezeichnet'},
   {'from':'interpretation','to':'tool','relation':'zeitlich danach','relation_class':'SAME_SESSION_TEMPORAL_CANDIDATE','explanation':'Kein Ursachennachweis'},
   {'from':'tool','to':'correction','relation':'Fehler gefolgt von Erfolg','relation_class':'SAME_TARGET_SUCCESSOR','explanation':'Kandidat'},
   {'from':'correction','to':'effect','relation':'gemeinsames Artefakt','relation_class':'COMMON_ARTIFACT_SUPPORTED','evidence_refs':[str(artifact)],'explanation':'Artefakt bindet Ergebnis'},
  ]})
 _,v=run(db,'create-chain','--spec',str(partial))
 check('Teilkettenstatus sichtbar',v['assessment']['completeness_status']=='PARTIAL_WITH_VISIBLE_GAPS',str(v))
 check('Ein Gap gezählt',v['assessment']['gap_count']==1)
 check('Nur artefaktgestützte Teilbeweislage',v['assessment']['causal_proof_level']=='ARTIFACT_SUPPORTED_PARTIAL')
 _,inspect=run(db,'inspect','--chain-id','CHAIN-PARTIAL')
 check('Gapgrund erhalten',any(n['node_type']=='LUECKE' and n['gap_reason']=='Kein sichtbarer Assistenztext' for n in inspect['nodes']))
 check('Kein Link behauptet Kausalität',all(l['causal_claim']==0 for l in inspect['links']))
 check('Kandidaten bleiben Kandidaten',sum(l['relation_class'] in {'SAME_TARGET_SUCCESSOR','SAME_SESSION_TEMPORAL_CANDIDATE'} for l in inspect['links'])==2)
 check('Wahrheitsgrenze ausgeliefert','keine Kausalbeweise' in inspect['truth_boundary'])
 # Explicit parent allows causal claim.
 explicit=td/'explicit.json';write_spec(explicit,{
  'chain_id':'CHAIN-EXPLICIT','title':'Explizite Parent-Verbindung','requirement_id':'R','source_session_id':'S1',
  'nodes':[{'key':'a','node_type':'IMPULS','label':'a','source_type':'history_event','source_ref':'E1'},{'key':'b','node_type':'TOOL','label':'b','source_type':'history_event','source_ref':'E2'}],
  'links':[{'from':'a','to':'b','relation':'parent_event_id','relation_class':'EXPLICIT_PARENT_EVENT','evidence_refs':['E2.parent_event_id=E1'],'causal_claim':True,'explanation':'Expliziter technischer Elternzeiger'}]})
 _,v=run(db,'create-chain','--spec',str(explicit))
 _,iex=run(db,'inspect','--chain-id','CHAIN-EXPLICIT')
 check('Explizite Relation erlaubt Kausalmarke',iex['links'][0]['causal_claim']==1)
 check('Expliziter Link gezählt',iex['assessment']['explicit_link_count']==1)
 # Fully populated but candidate links are not proof.
 full=td/'full.json'
 roles=['IMPULS','INTERPRETATION','ENTSCHEIDUNG','TOOL','DATEI_ODER_DIENST','TEST','KORREKTUR','FOLGE']
 nodes=[]
 for i,role in enumerate(roles):nodes.append({'key':f'n{i}','node_type':role,'label':role,'source_type':'file','source_ref':str(artifact)})
 links=[{'from':f'n{i}','to':f'n{i+1}','relation':'gleiche Fundquelle','relation_class':'COMMON_ARTIFACT_SUPPORTED','evidence_refs':[str(artifact)],'explanation':'Gemeinsames Artefakt, keine automatische Ursache'} for i in range(7)]
 write_spec(full,{'chain_id':'CHAIN-FULL','title':'Voll besetzt','requirement_id':'R','nodes':nodes,'links':links})
 _,v=run(db,'create-chain','--spec',str(full))
 check('Voll besetzte Kette ohne Gap',v['assessment']['gap_count']==0)
 check('Artefaktgestützt vollständig, nicht kausal',v['assessment']['completeness_status']=='SUPPORTED_COMPLETE_NOT_NECESSARILY_CAUSAL')
 check('Kein expliziter Kausalbeweis',v['assessment']['causal_proof_level']=='ARTIFACT_SUPPORTED_PARTIAL')
 _,listed=run(db,'list')
 check('Drei gültige Ketten gelistet',listed['count']==3,str(listed['count']))
 conn=sqlite3.connect(db)
 check('SQLite-Integrität',conn.execute('pragma integrity_check').fetchone()[0]=='ok')
 check('Rohereignisse vollständig gespeichert',conn.execute('select count(*) from imported_events').fetchone()[0]==5)
 check('Keine stille Linkkausalität',conn.execute('select count(*) from chain_links where causal_claim=1').fetchone()[0]==1)
 conn.close()
report={'ok':all(c['ok'] for c in checks),'test_id':'GA-TERMINAL-034-TECH-001','check_count':len(checks),'checks':checks,'truth_boundary':'Beweist Import, Kandidaten-, Gap- und Linklogik. Beweist noch keine vollständige historische Kette des realen VPS.'}
REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
