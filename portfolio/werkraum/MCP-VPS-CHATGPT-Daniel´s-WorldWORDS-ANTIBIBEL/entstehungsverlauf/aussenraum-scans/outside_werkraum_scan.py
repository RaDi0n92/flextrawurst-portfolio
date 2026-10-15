#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import os
import re
import tarfile
import zipfile

OUT=Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/entstehungsverlauf/aussenraum-scans')
ROOTS=[
 Path('/root/flextrawurst'),Path('/root/zensi'),Path('/root/.gemini/antigravity-cli/brain'),
 Path('/root/werkraum_bilder'),Path('/root/werkraum_geni'),Path('/root/werkraum_codewesen'),
 Path('/root/werkraum_agent'),Path('/root/werkraum_erkenntnis'),Path('/root/werkraum_flarum'),
 Path('/root/werkraum_logs'),Path('/root/.claude/projects'),Path('/root/.codex/sessions'),
 Path('/opt'),Path('/srv'),Path('/etc'),Path('/var/log')
]
ROOT_SINGLE_FILES=[Path('/root/GEMINI.md'),Path('/root/CLAUDE.md'),Path('/root/KIMI.md'),Path('/root/grok.md'),Path('/root/AGENTS.md'),Path('/input.txt')]
MAX_TEXT=16*1024*1024
MAX_ARCHIVE_ENTRIES=20000
EXTS={'.md','.txt','.json','.jsonl','.html','.htm','.py','.js','.ts','.tsx','.jsx','.css','.yaml','.yml','.toml','.ini','.conf','.service','.sh','.gd','.tscn','.csv','.sql','.xml','.log','.rtf'}
ARCHIVES={'.zip','.7z','.tar','.tgz','.gz','.bz2','.xz'}
PRUNE={'.git','node_modules','.venv','venv','__pycache__','.pytest_cache','.mypy_cache','.cache','models','model','blobs','snap','lost+found'}
TOKEN_RE=re.compile(r"[A-Za-zÄÖÜäöüßÀ-ÿ][A-Za-zÄÖÜäöüßÀ-ÿ0-9_+&'’.-]{2,99}")
SEEDS=[
 'Flextrawurst','KompOase','Resonanzurlaub','Codewesen','Schattenkommentar','Gedankenblase','Cyberling','Cyberlinge',
 'Splitterphysik','Traumrest-Diffusion','Stillgift','Grellader','Worldblick','Spurenfähigkeit','Organhunger','Klammerhonig',
 'Gesternöl','Staubmilch','Thronöl','Blendhonig','Rissmilch','Biotop-Protokoll','Flextraburst','Wartekörper',
 'Superdupermegaalleswisserbehaupterarschloch','Alleswisserbehaupterarschloch','Symbositierung','Resonanzknoten',
 'dak+gord','Gordslider','Zensi','GENI','MetaWar','Solarius','Codexium','Dolphin Mischpult','Zwischenwesen',
 'Resonanzfreiheit','resonanzfrei','Weltatom','Zeitadresse','Bauring','WorldWORDS','ANTIBIBEL','Wesenspawner',
 'Flüchtlinge','Diskursarchäologie','Wissenshüllen','Lebensvertrag','Systemweiser','Neugierkern','Schattenaccount',
 'Einzugsritual','Weltklima','Gedächtnismembran','Wahrnehmungsmembran','Traumstaub','Weltapparat','Spurmaschine',
 'Formfadenprompt','Stundenverlaufsystemwesen','Stundenversaufssystemwesen','Punktbühne','Robotermodus','Forschungssnack',
 'NULLSTUNDEN','Ideenmonstrum','Bildhauen','KI-Livesupport','Spiralflowspace','abrufbarmodus','Metamonster','Wortlike',
 'positive Viruszustände','KompOase-Gärstoffe','digitale Stoffkörper','Wesenstoff','Questkeime','Kontaktspur','Emojiresonanz',
 'Wochenstimme','Wunschkalender','Provenienzmaschine','Weltzugriff','Cheatkörper','Spawnmaschine','Weltkörper','Druckkörper'
]
SEED_LOW={x.casefold():x for x in SEEDS}
DISTINCTIVE=('flextra','kompoase','resonanz','codewesen','cyberling','splitter','traumrest','stillgift','grellader','worldblick',
 'spurenf','organhunger','klammerhonig','gesternöl','gesternoel','staubmilch','thronöl','thronoel','blendhonig','rissmilch',
 'biotop','wartekörper','wartekoerper','weltatom','zeitadresse','bauring','symbosit','metawar','gordslider','flextraburst',
 'antibibel','worldwords','alleswisser','wesenspawn','resonanzknoten','dak+gord','namelessai','zensi','solarius','codexium',
 'mischpult','eskalator','diskursarch','gedankenblase','schattenkommentar','weltkörper','weltkoerper','druckkörper',
 'wahrheitskörper','provenienzmaschine','spurmaschine','zwischenwesen','lebensvertrag','gedächtnismembran','wahrnehmungsmembran',
 'formfaden','punktbühne','nullstund','bildhau','ideenmonstr','livesupport','stundenverlauf','robotermodus','forschungssnack',
 'abrufbarmodus','metamonster','wortlike','gärstoff','gaerstoff','wesenstoff','questkeim','kontaktspur','emojiresonanz')
COMMON=set('''der die das und oder aber ein eine einer eines einem einen ist sind war waren wird werden wurde wurden mit ohne für fuer von zu im in am auf aus als bei nach vor über ueber unter zwischen durch nicht noch schon auch nur sehr mehr weniger diese dieser dieses diesem diesen ich du er sie es wir ihr man dass denn wenn dann hier dort was wie wer wo wann warum welche welcher welches jeden jede jedes kann können koennen soll sollen muss müssen muessen darf dürfen duerfen hat haben hatte hatten sein seine ihrer ihre mein meine dein deine text datei dateien ordner projekt system code test result output input status true false null none return class function def import from path root session chatgpt markdown json python service tool tools source target value name title type model user assistant message messages content data file files line lines generated current latest update updated created first last open closed active read write build builder report manifest index home start end error warning success failed unknown default config runtime server client local global public private new old original copy backup final live planned body world words word deutsch english german html css javascript typescript linux github obsidian flarum claude codex kimi gemini grok openai api mcp vps utc berlin flextrawurst zensi geni'''.split())

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
def decode(raw:bytes):
 if b'\0' in raw[:8192]:return None,'binary-nul'
 for enc in ('utf-8','utf-8-sig','cp1252','latin-1'):
  try:return raw.decode(enc),enc
  except UnicodeDecodeError:pass
 return raw.decode('utf-8','replace'),'replace'
def score(tok:str,line:str)->int:
 low=tok.casefold().strip(".'’-")
 if len(low)<4 or low in COMMON or re.fullmatch(r'[a-f0-9]{20,}',low):return -50
 s=0
 if low in SEED_LOW:s+=22
 s+=min(sum(1 for x in DISTINCTIVE if x in low)*7,21)
 if len(low)>=14:s+=3
 if len(low)>=22:s+=3
 if re.search(r'[a-zäöüß][A-ZÄÖÜ]',tok):s+=5
 if any(c in tok for c in '+&'):s+=4
 if '-' in tok and len(tok)>=9:s+=3
 if line.lstrip().startswith(('#','-','*','>')):s+=2
 if '_' in tok:s-=5
 if tok.isupper() and len(tok)<14:s-=2
 return s

def iter_files():
 seen=set()
 for base in ROOTS:
  if not base.exists():continue
  for d,dirs,files in os.walk(base,followlinks=False):
   dirs[:]=[x for x in dirs if x not in PRUNE]
   for name in files:
    p=Path(d)/name
    try:
     if p.is_symlink():continue
     key=str(p.resolve())
     if key in seen:continue
     seen.add(key)
     yield base,p
    except OSError:continue
 for p in ROOT_SINGLE_FILES:
  if p.exists() and p.is_file():yield p.parent,p

started=dt.datetime.now(dt.timezone.utc)
root_stats=defaultdict(lambda:{'all_files_seen':0,'text_files_read':0,'text_bytes_read':0,'archives_seen':0,'archive_entries_read':0,'skipped_large':0,'binary_skipped':0,'errors':0})
file_manifest=[];archive_manifest=[];errors=[]
tokens=Counter();filesets=defaultdict(set);contexts=defaultdict(list);seed_hits=defaultdict(list);filename_hits=[]
for base,p in iter_files():
 r=root_stats[str(base)];r['all_files_seen']+=1
 try:
  st=p.stat();lowname=p.name.casefold();suffix=p.suffix.lower()
  # filename and path seed hits
  pathlow=str(p).casefold()
  for low,canon in SEED_LOW.items():
   if low in pathlow and len(seed_hits[canon])<60:
    seed_hits[canon].append({'kind':'path','path':str(p),'line':None,'context':str(p)})
  if suffix in ARCHIVES or p.name.lower().endswith(('.tar.gz','.tar.bz2','.tar.xz')):
   r['archives_seen']+=1
   members=[];err=None
   try:
    if zipfile.is_zipfile(p):
     with zipfile.ZipFile(p) as z:
      for info in z.infolist()[:MAX_ARCHIVE_ENTRIES]:members.append({'name':info.filename,'size':info.file_size,'compressed':info.compress_size})
    elif tarfile.is_tarfile(p):
     with tarfile.open(p,'r:*') as t:
      for i,m in enumerate(t):
       if i>=MAX_ARCHIVE_ENTRIES:break
       members.append({'name':m.name,'size':m.size,'type':m.type.decode('latin-1','replace') if isinstance(m.type,bytes) else str(m.type)})
   except Exception as e:err=type(e).__name__+': '+str(e)[:300]
   r['archive_entries_read']+=len(members)
   archive_manifest.append({'path':str(p),'bytes':st.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if st.st_size<64*1024*1024 else None,'members_captured':len(members),'error':err,'members':members[:2000]})
   for m in members:
    ml=m['name'].casefold()
    for low,canon in SEED_LOW.items():
     if low in ml and len(seed_hits[canon])<60:seed_hits[canon].append({'kind':'archive_member','path':str(p),'line':None,'context':m['name']})
   continue
  if suffix not in EXTS:continue
  if st.st_size>MAX_TEXT:r['skipped_large']+=1;continue
  raw=p.read_bytes();text,enc=decode(raw)
  if text is None:r['binary_skipped']+=1;continue
  r['text_files_read']+=1;r['text_bytes_read']+=len(raw)
  file_manifest.append({'root':str(base),'path':str(p),'bytes':len(raw),'mtime_utc':dt.datetime.fromtimestamp(st.st_mtime,tz=dt.timezone.utc).isoformat(),'sha256':sha(raw),'encoding':enc})
  lines=text.splitlines()
  for low,canon in SEED_LOW.items():
   if low not in text.casefold():continue
   for no,line in enumerate(lines,1):
    if low in line.casefold() and len(seed_hits[canon])<60:seed_hits[canon].append({'kind':'text','path':str(p),'line':no,'context':line.strip()[:900]})
  for no,line in enumerate(lines,1):
   if len(line)>24000:line=line[:24000]
   for tok in TOKEN_RE.findall(line):
    tok=tok.strip(".'’-");s=score(tok,line)
    if s<6:continue
    key=tok.casefold();tokens[key]+=1;filesets[key].add(str(p))
    if len(contexts[key])<15:contexts[key].append({'token':tok,'score':s,'path':str(p),'line':no,'context':line.strip()[:900]})
 except Exception as e:
  r['errors']+=1;errors.append({'path':str(p),'error':type(e).__name__+': '+str(e)[:400]})
rows=[]
for key,count in tokens.items():
 ctx=contexts[key];best=max((x['score'] for x in ctx),default=0);rank=best*10+min(len(filesets[key]),50)*3+min(count,100)
 rows.append({'token':ctx[0]['token'] if ctx else key,'normalized':key,'rank':rank,'best_score':best,'occurrences':count,'file_count':len(filesets[key]),'contexts':ctx})
rows.sort(key=lambda x:(-x['rank'],-x['file_count'],-x['occurrences'],x['normalized']))
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'AUSSENRAUM_DATEIMANIFEST.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in file_manifest),encoding='utf-8')
(OUT/'AUSSENRAUM_ARCHIVMANIFEST.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in archive_manifest),encoding='utf-8')
(OUT/'AUSSENRAUM_ROHKANDIDATEN.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in rows),encoding='utf-8')
(OUT/'AUSSENRAUM_SEED_FUNDSTELLEN.json').write_text(json.dumps(dict(sorted(seed_hits.items())),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'AUSSENRAUM_FEHLER.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'ok':True,'started_utc':started.isoformat(),'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'outside /root/werkraum, selected personal and technical roots','root_stats':dict(root_stats),'text_files_read':len(file_manifest),'text_bytes_read':sum(x['bytes'] for x in file_manifest),'archives_seen':len(archive_manifest),'archive_members_captured':sum(x['members_captured'] for x in archive_manifest),'raw_candidates':len(rows),'seed_terms_found':sum(bool(v) for v in seed_hits.values()),'errors':len(errors)}
(OUT/'AUSSENRAUM_SCAN_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# Außenraum-Scan außerhalb von `/root/werkraum`','',f'- Start UTC: `{started.isoformat()}`',f'- Ende UTC: `{manifest["finished_utc"]}`',f'- Gelesene Textkörper: `{manifest["text_files_read"]}`',f'- Gelesene Textbytes: `{manifest["text_bytes_read"]}`',f'- Archive inventarisiert: `{manifest["archives_seen"]}`',f'- Archivmitglieder erfasst: `{manifest["archive_members_captured"]}`',f'- Rohkandidaten: `{manifest["raw_candidates"]}`',f'- Seed-Begriffe gefunden: `{manifest["seed_terms_found"]}`',f'- Lesefehler: `{manifest["errors"]}`','','## Wurzelstatistik','']
for r,s in sorted(root_stats.items()):md.append(f"- `{r}` · Dateien gesehen `{s['all_files_seen']}` · Texte gelesen `{s['text_files_read']}` · Bytes `{s['text_bytes_read']}` · Archive `{s['archives_seen']}` · Archivmitglieder `{s['archive_entries_read']}` · Fehler `{s['errors']}`")
md+=['','## Höchstrangige Rohkandidaten','']
for row in rows[:400]:
 c=row['contexts'][0] if row['contexts'] else {};md.append(f"- **{row['token']}** · Rang `{row['rank']}` · Vorkommen `{row['occurrences']}` · Dateien `{row['file_count']}` · `{c.get('path','?')}:{c.get('line','?')}`")
(OUT/'AUSSENRAUM_SCAN_BERICHT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
