#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile, zipfile
from pathlib import Path

TOOL=Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/install_proof_capsule.py')
SOURCE_BASE=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/BASE_AKTUELL.zip')
REPORT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ/GA-CAPSULE-INSTALL-TECHNICAL.json')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value,detail=''):
 checks.append({'name':name,'ok':bool(value),'detail':detail})
 if not value:raise AssertionError(f'{name}: {detail}')
def run(env,*args,ok=True):
 p=subprocess.run(['python3',str(TOOL),*args],env=env,text=True,capture_output=True,timeout=900)
 stream=p.stdout if p.returncode==0 else p.stderr
 try:v=json.loads(stream)
 except Exception:v={'raw':stream}
 if ok and p.returncode!=0:raise AssertionError(f'failed {args}: {stream[-5000:]}')
 if not ok and p.returncode==0:raise AssertionError(f'unexpected pass {args}: {stream}')
 return p,v
def manifest(p):
 with zipfile.ZipFile(p) as z:
  return json.loads(z.read('ENDPRODUKTBEWEIS/MANIFEST.json')) if 'ENDPRODUKTBEWEIS/MANIFEST.json' in z.namelist() else None

check('Ausgangskapsel existiert',SOURCE_BASE.exists())
check('Ausgangskapsel ist noch reine Basis',manifest(SOURCE_BASE) is None)
source_hash=sha(SOURCE_BASE)
with tempfile.TemporaryDirectory(prefix='ga-install-test-') as td:
 td=Path(td);canonical=td/'canonical.zip';base=td/'base.zip';status=td/'status.json';failure=td/'INSTALL_FAILURE.json';backups=td/'backups';lock=td/'lock'
 shutil.copy2(SOURCE_BASE,canonical)
 env=os.environ.copy();env.update({'GA_CANONICAL_CAPSULE':str(canonical),'GA_BASE_STORE':str(base),'GA_INSTALL_STATUS':str(status),'GA_INSTALL_BACKUP_ROOT':str(backups),'GA_INSTALL_LOCK':str(lock)})
 _,v=run(env)
 result=v['result']
 check('Erster Lauf installiert',result['state']=='PROOF_CAPSULE_INSTALLED' and result['changed'] is True,str(result))
 check('Basis separat gespeichert',base.exists() and sha(base)==source_hash)
 check('Kanonischer Testpfad jetzt überlagert',manifest(canonical) is not None)
 check('Installierter Hash entspricht Kandidat',result['canonical_sha256']==sha(canonical)==result['candidate']['sha256'])
 check('Quellenfingerabdruck gesetzt',len(result['proof_source_fingerprint'])==64)
 check('Manifest trägt gleichen Fingerabdruck',manifest(canonical)['proof_source_fingerprint']==result['proof_source_fingerprint'])
 check('Manifest trägt Basishash',manifest(canonical)['base_capsule']['sha256']==source_hash)
 check('Backup des alten Kanons existiert',Path(result['backup_path']).exists())
 check('Backup ist ursprüngliche Basis',sha(Path(result['backup_path']))==source_hash)
 check('Installstatus geschrieben',status.exists())
 first_hash=sha(canonical)
 first_manifest=manifest(canonical)
 _,v=run(env)
 check('Zweiter Lauf idempotent',v['result']['state']=='CURRENT_PROOF_CAPSULE_ALREADY_INSTALLED' and v['result']['changed'] is False,str(v))
 check('Idempotenter Lauf verändert Hash nicht',sha(canonical)==first_hash)
 # Simulate organism replacing proof capsule with a fresh base.
 shutil.copy2(SOURCE_BASE,canonical)
 check('Simulierter Organismus-Rückfall ist Basis',manifest(canonical) is None)
 _,v=run(env)
 check('Basis-Rückfall automatisch überlagert',v['result']['state']=='PROOF_CAPSULE_INSTALLED' and manifest(canonical) is not None)
 check('Basis nach Rückfall weiterhin korrekt',sha(base)==source_hash)
 rebuilt_manifest=manifest(canonical)
 check('Überlagerung nach Rückfall semantisch gleich',
       rebuilt_manifest['proof_source_fingerprint']==first_manifest['proof_source_fingerprint']
       and rebuilt_manifest['base_capsule']['sha256']==first_manifest['base_capsule']['sha256']
       and rebuilt_manifest['public_delivery'] is False
       and rebuilt_manifest['browser_real_acceptance']=='OPEN_BLOCKED_EXTERNAL'
       and rebuilt_manifest['external_response_count']==0,
       json.dumps({'first':first_manifest,'rebuilt':rebuilt_manifest},ensure_ascii=False)[:2000])
 check('Neubau darf wegen Zeitmanifest neuen ZIP-Hash tragen',len(sha(canonical))==64)
 # Force rebuild must stay valid and private.
 _,v=run(env,'--force')
 check('Force-Rebuild erfolgreich',v['result']['state']=='PROOF_CAPSULE_INSTALLED')
 check('Force-Rebuild bleibt valide',manifest(canonical)['public_delivery'] is False)
 # Missing base while canonical already overlaid must fail safely and not mutate canonical.
 protected_hash=sha(canonical);base.unlink()
 _,fail=run(env,ok=False)
 check('Fehlende Basis bei Overlay blockiert','BASE_AKTUELL.zip fehlt' in fail['error'],str(fail))
 check('Fehler lässt Kanon unverändert',sha(canonical)==protected_hash)
 check('Fehlerbericht geschrieben',failure.exists())
 # Corrupt base input must be rejected before replacement.
 shutil.copy2(SOURCE_BASE,base);canonical.write_bytes(b'not-a-zip');corrupt_hash=sha(canonical)
 _,fail=run(env,ok=False)
 check('Beschädigter Kanon blockiert',('BadZipFile' in fail['error'] or 'ZIP' in fail['error']),str(fail))
 check('Beschädigter Kanon nicht weiter verändert',sha(canonical)==corrupt_hash)
 # Backup pruning never grows without bound.
 check('Backupanzahl begrenzt',len(list(backups.glob('*.zip')))<=3,str(list(backups.glob('*.zip'))))
report={'ok':all(c['ok'] for c in checks),'test_id':'GA-CAPSULE-INSTALL-TECH-001','check_count':len(checks),'checks':checks,'source_base_sha256':source_hash,'truth_boundary':'Beweist atomare Installation, Idempotenz und Wiederherstellung an isolierten Pfaden. Der reale WinSCP-Pfad wurde in diesem Test nicht verändert.'}
REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
