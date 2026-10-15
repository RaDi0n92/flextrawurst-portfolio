#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'MOC/99_DATEIKATALOG.md'
REPORT_JSON=ROOT/'validation/VALIDATION_REPORT.json'
REPORT_MD=ROOT/'validation/VALIDATION_REPORT.md'
WIKI_RE=re.compile(r'!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]')
MD_RE=re.compile(r'(?<!!)\[[^\]]*\]\((?:<([^>]+)>|([^\)]+))\)')
GENERATED_MOC={f'MOC/{n}' for n in {'00_PROJEKTKARTE.md','01_HERKUNFT.md','02_WORTKOERPER.md','03_KONZEPTE.md','04_PROPAGANDA_UND_VERBREITUNG.md','05_GESPRAECHE.md','06_HISTORY_UND_ZEITSTROM.md','07_MUTATIONEN.md','08_QUELLEN.md','09_TECHNISCHE_ORGANE.md','98_ZULETZT_GEAENDERT.md','99_DATEIKATALOG.md'}}|{'HOME.md'}

def sha(p:Path)->str:
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()

def strip_code(text:str)->str:
 out=[];inside=False;char='';length=0
 for line in text.splitlines():
  m=re.match(r'\s*(`{3,}|~{3,})',line)
  if m:
   mark=m.group(1)
   if not inside:inside=True;char=mark[0];length=len(mark)
   elif mark[0]==char and len(mark)>=length:inside=False
   out.append('');continue
  if inside:out.append('');continue
  out.append(re.sub(r'`[^`\n]*`','',line))
 return '\n'.join(out)

def resolve_wiki(raw:str)->bool:
 raw=raw.strip()
 if not raw:return True
 for p in [ROOT/raw,ROOT/(raw+'.md')]:
  if p.exists():return True
 return False

def resolve_md(note:Path,raw:str)->bool:
 raw=raw.strip()
 if not raw or raw.startswith(('http://','https://','mailto:','obsidian://','file://','#')):return True
 raw=raw.split('#',1)[0]
 return (note.parent/raw).resolve().exists()

def catalog_expected()->list[Path]:
 out=[]
 for p in ROOT.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  r=p.relative_to(ROOT).as_posix()
  if r.startswith('.obsidian/') or r in GENERATED_MOC:continue
  if r in {'validation/VALIDATION_REPORT.json','validation/VALIDATION_REPORT.md'}:continue
  out.append(p)
 return sorted(out)

def validate()->dict[str,Any]:
 broken=[];count=0
 md_files=sorted(ROOT.rglob('*.md'))
 for note in md_files:
  text=strip_code(note.read_text(encoding='utf-8',errors='replace'))
  for m in WIKI_RE.finditer(text):
   count+=1;target=m.group(1)
   if not resolve_wiki(target):broken.append({'kind':'wikilink','note':note.relative_to(ROOT).as_posix(),'target':target})
  for m in MD_RE.finditer(text):
   target=m.group(1) or m.group(2) or ''
   if '{' in target or '}' in target:
    continue
   count+=1
   if not resolve_md(note,target):broken.append({'kind':'markdown_link','note':note.relative_to(ROOT).as_posix(),'target':target})
 catalog=CATALOG.read_text(encoding='utf-8') if CATALOG.exists() else ''
 missing=[]
 for p in catalog_expected():
  r=p.relative_to(ROOT).as_posix();tokens=[r,p.name]
  if p.suffix.lower()=='.md':tokens.append(r[:-3])
  if not any(t in catalog for t in tokens):missing.append(r)
 source_manifest_errors=[]
 sm=ROOT/'ANTIBIBEL_SOURCE_MANIFEST.json'
 try:
  data=json.loads(sm.read_text())
  for row in data.get('files',[]):
   p=Path(row.get('path',''))
   if not p.exists():source_manifest_errors.append({'path':str(p),'error':'missing'})
   elif sha(p)!=row.get('sha256'):source_manifest_errors.append({'path':str(p),'error':'sha256_mismatch','expected':row.get('sha256'),'actual':sha(p)})
 except Exception as e:source_manifest_errors.append({'path':str(sm),'error':repr(e)})
 required=['HOME.md','GESPRAECHSNETZ.md','ZEITSTROM.md','AKTUELLE_WAHRHEIT.md','MOC/99_DATEIKATALOG.md','Verweise/MANIFEST.json','Zeitstrom/MANIFEST.json']
 missing_required=[r for r in required if not (ROOT/r).exists()]
 return {'ok':not broken and not missing and not source_manifest_errors and not missing_required,'root':str(ROOT),'markdown_files_checked':len(md_files),'internal_links_checked':count,'broken_links':broken,'catalog_expected_files':len(catalog_expected()),'missing_from_catalog':missing,'source_manifest_errors':source_manifest_errors,'missing_required_organs':missing_required}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--write-report',action='store_true');a=ap.parse_args();r=validate()
 if a.write_report:
  REPORT_JSON.parent.mkdir(parents=True,exist_ok=True);REPORT_JSON.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  md='# Validierung der WorldWORDS ANTIBIBEL\n\n'+f'- **OK:** `{str(r["ok"]).lower()}`\n- **Markdown-Dateien:** `{r["markdown_files_checked"]}`\n- **Interne Links:** `{r["internal_links_checked"]}`\n- **Tote Links:** `{len(r["broken_links"])}`\n- **Fehlende Katalogeinträge:** `{len(r["missing_from_catalog"])}`\n- **Quellhash-Fehler:** `{len(r["source_manifest_errors"])}`\n- **Fehlende Pflichtorgane:** `{len(r["missing_required_organs"])}`\n\n## Details\n\n```json\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\n```\n\n- [[HOME|Vault Home]]\n'
  REPORT_MD.write_text(md,encoding='utf-8')
 print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
