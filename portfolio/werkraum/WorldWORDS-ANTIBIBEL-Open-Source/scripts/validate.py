#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'{p}: invalid JSON: {e}');return None

contributors={p.stem for p in (ROOT/'data/contributors').glob('*.json')}
approvals={p.stem:load(p) for p in (ROOT/'data/approvals').glob('*.json')}
ids=set()
for p in sorted((ROOT/'data/terms').glob('*.json')):
    d=load(p)
    if not d:continue
    for key in ['id','canonical_form','status','origin','definitions','approval']:
        if key not in d:errors.append(f'{p}: missing {key}')
    if d.get('id') in ids:errors.append(f'{p}: duplicate id {d.get("id")}')
    ids.add(d.get('id'))
    if d.get('raw_form_policy')!='preserve-exactly':errors.append(f'{p}: raw form policy changed')
    if d.get('status')=='accepted':
        aid=d.get('approval',{}).get('approval_id')
        if aid not in approvals:errors.append(f'{p}: missing approval {aid}')
        elif approvals[aid].get('decided_by')!='daniel':errors.append(f'{p}: approval not decided by Daniel')
    for lang in ['de','en','es']:
        if lang not in d.get('definitions',{}):errors.append(f'{p}: missing {lang} definition')
    for c in d.get('origin',{}).get('contributors',[]):
        if c not in contributors:errors.append(f'{p}: unknown contributor {c}')
for p in sorted((ROOT/'data/proposals').glob('*.json')):
    d=load(p)
    if not d:continue
    for key in ['id','raw_form','status','submitted_by','authorship_status','first_seen','exact_input','source_ref','definitions']:
        if key not in d:errors.append(f'{p}: missing {key}')
    if d.get('official_registry',{}).get('accepted_by_daniel') is True:
        errors.append(f'{p}: proposal falsely marked Daniel-accepted')
    for lang in ['de','en','es']:
        if lang not in d.get('definitions',{}):errors.append(f'{p}: missing {lang} definition')
reg=load(ROOT/'data/registry.json') or {}
for item in reg.get('accepted_terms',[]):
    p=ROOT/item['record']
    if not p.exists():errors.append(f'registry missing {p}')
raw=load(ROOT/'raw/MANIFEST.json') or {}
for item in raw.get('files',[]):
    p=ROOT/item['public_path']
    if not p.exists():errors.append(f'raw file missing {p}');continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=item['sha256']:errors.append(f'raw hash mismatch {p}')
secret_rx=re.compile(r'(?i)(client_secret|api[_-]?key|authorization|bearer|password)\s*[=:]\s*(?!\[REDACTED\])\S+')
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts or p.suffix.lower() not in {'.md','.json','.jsonl','.yml','.yaml','.txt','.py','.html'}:continue
    txt=p.read_text(encoding='utf-8',errors='replace')
    if secret_rx.search(txt):errors.append(f'possible secret assignment in {p}')
if errors:
    print('\n'.join('ERROR '+e for e in errors));sys.exit(1)
print(f'OK accepted_terms={len(list((ROOT/"data/terms").glob("*.json")))} proposals={len(list((ROOT/"data/proposals").glob("*.json")))} raw_files={len(raw.get("files",[]))}')
