#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path

TOOL=Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis/llm_abnahme.py')
SOURCE_INTEGRATION=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/INTEGRATION')
REPORT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ/GA-INTEGRATION-001_TECHNICAL.json')
checks=[]

def check(name, value, detail=''):
    checks.append({'name':name,'ok':bool(value),'detail':detail})
    if not value: raise AssertionError(f'{name}: {detail}')

def run(env,*args,ok=True):
    p=subprocess.run(['python3',str(TOOL),*args],env=env,text=True,capture_output=True)
    if ok and p.returncode!=0: raise AssertionError(f'command failed {args}: {p.stderr}')
    if not ok and p.returncode==0: raise AssertionError(f'command unexpectedly passed {args}: {p.stdout}')
    stream=p.stdout if p.returncode==0 else p.stderr
    return p,json.loads(stream)

with tempfile.TemporaryDirectory(prefix='ga-llm-test-') as td:
    td=Path(td); proof=td/'proof'; integ=proof/'INTEGRATION'; integ.mkdir(parents=True)
    for name in ('LLM_ABNAHME_AUFGABEN.json','RAW_RESPONSE_SCHEMA.json','INTEGRATION_FREIGABE_SCHEMA.json'):
        shutil.copy2(SOURCE_INTEGRATION/name,integ/name)
    capsule=td/'capsule.zip'; capsule.write_bytes(b'private-test-capsule')
    capsha=hashlib.sha256(capsule.read_bytes()).hexdigest()
    env=os.environ.copy(); env['GA_PROOF_ROOT']=str(proof); env['GA_CAPSULE']=str(capsule)
    _,value=run(env,'prepare-run','--label','Technischer Test','--run-id','TEST-RUN-001')
    check('Run ist PREPARED',value['result']['state']=='PREPARED')
    check('Kapselhash gebunden',value['result']['capsule_sha256']==capsha)
    _,value=run(env,'record-distribution','--run-id','TEST-RUN-001','--provider','TestProvider','--model','TestModel','--model-version','1.0','--recipient-label','Isolierter Prüfer')
    check('Verteilung ist DISTRIBUTED',value['result']['state']=='DISTRIBUTED')
    response={
      'provider':'TestProvider','model':'TestModel','model_version':'1.0','task_set_id':'GA-CLEANROOM-001','capsule_sha256':capsha,
      'answers':[{'task_id':f'CR-{i:02d}','answer':f'Antwort {i}','citations':['00_START_HIER.md'],'uncertainties':['Grenze erkannt'],'claims':['Testbehauptung']} for i in range(1,11)],
      'final_limitations':['Kein VPS-Zugriff']
    }
    source=td/'response.json'; source.write_text(json.dumps(response,ensure_ascii=False),encoding='utf-8')
    sourcesha=hashlib.sha256(source.read_bytes()).hexdigest()
    _,value=run(env,'ingest','--run-id','TEST-RUN-001','--provider','TestProvider','--model','TestModel','--model-version','1.0','--file',str(source))
    response_id=value['result']['response_id']
    check('Rohantwort schema-konform',value['result']['schema_ok'] is True)
    check('Rohhash erhalten',value['result']['raw_sha256']==sourcesha)
    _,dedupe=run(env,'ingest','--run-id','TEST-RUN-001','--provider','TestProvider','--model','TestModel','--model-version','1.0','--file',str(source))
    check('Doppelimport dedupliziert',dedupe['result']['deduplicated'] is True)
    _,value=run(env,'compare','--run-id','TEST-RUN-001')
    check('Alle zehn Aufgaben erkannt',len(value['result']['responses'][0]['covered_tasks'])==10)
    check('Vergleich bleibt nicht-kanonisch',value['result']['responses'][0]['assessment_state']=='STRUCTURALLY_ASSESSED_NOT_TRUTH_VALIDATED')
    _,value=run(env,'propose','--run-id','TEST-RUN-001','--title','Testvorschlag','--description','Nur Zustandsprüfung','--requirement-id','GA-INTEGRATION-001','--response-id',response_id)
    proposal=value['result']['proposal_id']
    check('Vorschlag nicht kanonisch',value['result']['state']=='PROPOSED_NOT_CANONICAL' and value['result']['canonical'] is False)
    run(env,'decide','--proposal-id',proposal,'--decision','approve','--decided-by','NichtDaniel','--comment','Nein',ok=False)
    check('Fremdfreigabe blockiert',True)
    run(env,'mark-implemented','--proposal-id',proposal,'--evidence-path','/tmp/x',ok=False)
    check('Implementierung vor Daniel blockiert',True)
    _,value=run(env,'decide','--proposal-id',proposal,'--decision','approve','--decided-by','Daniel','--comment','Testfreigabe')
    check('Daniel-Freigabe gesetzt',value['result']['state']=='DANIEL_APPROVED' and value['result']['canonical'] is False)
    run(env,'mark-canonical','--proposal-id',proposal,'--confirmed-by','Daniel',ok=False)
    check('Kanonisierung vor Tests blockiert',True)
    _,value=run(env,'mark-implemented','--proposal-id',proposal,'--evidence-path','/tmp/implementation')
    check('Implementiert bleibt unbestätigt',value['result']['state']=='IMPLEMENTED_UNVERIFIED')
    run(env,'mark-validated','--proposal-id',proposal,ok=False)
    check('Validierung ohne Beleg blockiert',True)
    _,value=run(env,'mark-validated','--proposal-id',proposal,'--evidence-path','/tmp/test-report.json')
    check('Validierung mit Beleg',value['result']['state']=='VALIDATED')
    run(env,'mark-canonical','--proposal-id',proposal,'--confirmed-by','EinModell',ok=False)
    check('Kanonisierung durch Modell blockiert',True)
    _,value=run(env,'mark-canonical','--proposal-id',proposal,'--confirmed-by','Daniel')
    check('Kanonisierung nur nach kompletter Kette',value['result']['state']=='CANONICAL' and value['result']['canonical'] is True)
    raw=list((proof/'INTEGRATION/RUNS/TEST-RUN-001/responses').glob('*/RAW.json'))[0]
    check('Gespeicherte Rohantwort bytegleich',hashlib.sha256(raw.read_bytes()).hexdigest()==sourcesha)
    status=json.loads((proof/'INTEGRATION/STATUS.json').read_text())
    check('Status zählt exakt einen Run',status['run_count']==1)
    check('Status zählt genau eine Rohantwort',status['raw_response_count']==1)
    check('Status zählt genau eine kanonische Entscheidung',status['canonical_count']==1)

report={'ok':all(x['ok'] for x in checks),'test_id':'GA-INTEGRATION-001-TECH-001','check_count':len(checks),'checks':checks}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
