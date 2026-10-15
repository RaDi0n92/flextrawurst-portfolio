#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import re

ROOT = Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL')
OUT = ROOT / 'entstehungsverlauf/vps-scans'
SOURCES = [
    Path('/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai'),
    Path('/root/werkraum/_gpt/ui_visible_conversations'),
    Path('/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/sessions'),
    ROOT / '06_GESPRAECHE',
]
EXTS={'.md','.txt','.json','.jsonl'}
USER_MARKERS={
    'user','nutzer','daniel','### daniel','## daniel','# daniel','you said:','you said','### user','## user','# user'
}
ASSIST_MARKERS={
    'chatgpt','assistant','### assistant','## assistant','# assistant','gpt-5','gpt5','kimi','claude','gemini','grok','codex',
    '### chatgpt','## chatgpt','# chatgpt','### gpt-5','## gpt-5','# gpt-5'
}
TOKEN_RE=re.compile(r"[A-Za-zÄÖÜäöüßÀ-ÿ][A-Za-zÄÖÜäöüßÀ-ÿ0-9_+&'’.-]{2,89}")
COMMON=set('''aber alle allein also als am an auch auf aus bei bin bis bist da dann das dass dein deine dem den denn der des die dies diese dir doch du ein eine einer einem einen er es etwas für fuer ganz gar gegen gehabt haben hat hatte hier ich im in ist ja jede jeder jedes kann kein keine kommt könnte koennte machen mal man mehr mein meine mit muss nach nicht noch nun nur ob oder ohne schon sehr sein seine sich sie sind so soll sonst über ueber um und uns unser unsere von vor war waren was weil weiter welche wenn wer wie wieder will wir wird wo wohl zu zum zur zwei jetzt heute gestern morgen bitte danke okay hey hallo wirklich richtig einfach genau eigentlich vielleicht irgendwie etwas jemand niemand immer manchmal bisher bisherige text chat session modell antwort frage punkt thema projekt system idee ideen website ai ki gpt chatgpt kimi claude code bild bilder menschen mensch leben welt software kontakt direkt grob nennen erste ersten etwas noch schon mehr weniger'''.split())
DISTINCTIVE_PARTS=('flextra','kompoase','resonanz','wesen','cyber','splitter','traum','still','grell','world','organ','klammer','gestern','staub','thron','blend','riss','biotop','warte','atom','zeit','bauring','symb','meta','gord','zensi','geni','solarius','codexium','faden','punktbühne','punktbuehne','nullstund','bildhau','ideenmonstr','livesupport','spiralflow','systemwohl','stundenverlauf','robotermodus','forschungssnack','fehlercode','zwischenraum','abrufbar','kontext','schwebezustand','eigenleben','antiperfekt','metamonster','antibibel','worldwords','verdeutsch','müllfresko','muellfresko','wortlike')


def decode(p:Path):
    raw=p.read_bytes()
    for enc in ('utf-8-sig','utf-8','cp1252','latin-1'):
        try:return raw.decode(enc),enc,hashlib.sha256(raw).hexdigest()
        except UnicodeDecodeError:pass
    return raw.decode('utf-8','replace'),'replace',hashlib.sha256(raw).hexdigest()

def norm_marker(line:str)->str:
    return re.sub(r'\s+',' ',line.strip().casefold()).rstrip(':')

def iter_files():
    for base in SOURCES:
        if not base.exists():continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in EXTS and '__pycache__' not in p.parts and p.stat().st_size<8*1024*1024:
                yield p

def explicit_blocks(lines:list[str], path:str):
    blocks=[];mode=None;start=None;buf=[]
    for i,line in enumerate(lines,1):
        marker=norm_marker(line)
        next_mode=None
        if marker in USER_MARKERS or re.fullmatch(r'#+\s*(daniel|user|nutzer)',marker):next_mode='user'
        elif marker in ASSIST_MARKERS or re.fullmatch(r'#+\s*(assistant|chatgpt|gpt-?5|kimi|claude|gemini|grok|codex)',marker):next_mode='assistant'
        if next_mode:
            if mode=='user' and buf:
                text='\n'.join(buf).strip()
                if text:blocks.append({'speaker_status':'EXPLIZIT_DANIEL','path':path,'start_line':start,'end_line':i-1,'text':text})
            mode=next_mode;start=i+1;buf=[]
        elif mode is not None:
            buf.append(line)
    if mode=='user' and buf:
        text='\n'.join(buf).strip()
        if text:blocks.append({'speaker_status':'EXPLIZIT_DANIEL','path':path,'start_line':start,'end_line':len(lines),'text':text})
    return blocks

def kimi_heuristic(lines:list[str], path:str):
    blocks=[]
    for i in range(len(lines)-2):
        if lines[i].strip().casefold()=='edit' and lines[i+1].strip().casefold()=='copy' and lines[i+2].strip().casefold()=='share':
            j=i-1;tail=[]
            while j>=0 and len(tail)<14:
                s=lines[j].rstrip()
                if not s.strip() and tail:break
                if s.strip():tail.append(s)
                j-=1
            tail.reverse();text='\n'.join(tail).strip()
            if text and len(text)<4000:
                blocks.append({'speaker_status':'WAHRSCHEINLICH_DANIEL_KIMI_UI_HEURISTIK','path':path,'start_line':j+2,'end_line':i,'text':text})
    return blocks

def token_score(tok:str, text:str):
    low=tok.casefold().strip(".'’-")
    if len(low)<4 or low in COMMON or re.fullmatch(r'[a-f0-9]{18,}',low):return -50
    s=0
    if any(part in low for part in DISTINCTIVE_PARTS):s+=9
    if len(low)>=13:s+=3
    if len(low)>=20:s+=3
    if re.search(r'[a-zäöüß][A-ZÄÖÜ]',tok):s+=4
    if any(c in tok for c in '+&'):s+=3
    if '-' in tok and len(tok)>=9:s+=2
    if re.search(r'\d',tok):s+=1
    if tok.isupper() and len(tok)<12:s-=2
    if '_' in tok:s-=5
    if re.search(r'\b(?:nen|ne|son|sowas|nurnoch|irgendwas)\b',text.casefold()):s+=1
    return s

blocks=[];files=[]
for p in iter_files():
    try:
        text,enc,sha=decode(p);lines=text.replace('\r\n','\n').replace('\r','\n').splitlines();path=str(p)
        eb=explicit_blocks(lines,path);kb=[]
        if '250seiter der ersten chatverläufe mit kimi' in path or ('Edit\nCopy\nShare' in text):kb=kimi_heuristic(lines,path)
        if eb or kb:
            files.append({'path':path,'sha256':sha,'bytes':p.stat().st_size,'encoding':enc,'explicit_blocks':len(eb),'kimi_heuristic_blocks':len(kb)})
            blocks.extend(eb);blocks.extend(kb)
    except Exception:pass

# de-duplicate same path/range/text
seen=set();dedup=[]
for b in blocks:
    k=(b['path'],b['start_line'],b['end_line'],hashlib.sha256(b['text'].encode()).hexdigest())
    if k not in seen:seen.add(k);dedup.append(b)
blocks=dedup

terms=defaultdict(lambda:{'occurrences':0,'blocks':set(),'speaker_statuses':Counter(),'evidence':[],'best_score':0})
for idx,b in enumerate(blocks):
    for tok in TOKEN_RE.findall(b['text']):
        tok=tok.strip(".'’-");score=token_score(tok,b['text'])
        if score<5:continue
        low=tok.casefold();r=terms[low];r['occurrences']+=1;r['blocks'].add(idx);r['speaker_statuses'][b['speaker_status']]+=1;r['best_score']=max(r['best_score'],score)
        if len(r['evidence'])<20:
            # exact local line
            line_offset=0
            for off,line in enumerate(b['text'].splitlines()):
                if low in line.casefold():line_offset=off;ctx=line.strip()[:900];break
            else:ctx=b['text'][:900].replace('\n',' ')
            r['evidence'].append({'token':tok,'speaker_status':b['speaker_status'],'path':b['path'],'line':b['start_line']+line_offset,'context':ctx})
rows=[]
for low,r in terms.items():
    canonical=r['evidence'][0]['token'];explicit=r['speaker_statuses'].get('EXPLIZIT_DANIEL',0);heur=r['speaker_statuses'].get('WAHRSCHEINLICH_DANIEL_KIMI_UI_HEURISTIK',0)
    rank=r['best_score']*10+min(explicit,20)*5+min(len(r['blocks']),30)*2+min(r['occurrences'],50)
    rows.append({'term':canonical,'normalized':low,'rank':rank,'best_score':r['best_score'],'occurrences':r['occurrences'],'block_count':len(r['blocks']),'explicit_daniel_blocks':explicit,'heuristic_daniel_blocks':heur,'speaker_statuses':dict(r['speaker_statuses']),'evidence':r['evidence']})
rows.sort(key=lambda x:(-x['rank'],-x['explicit_daniel_blocks'],-x['block_count'],x['normalized']))

(OUT/'DANIEL_SPRECHERBLOECKE.jsonl').write_text(''.join(json.dumps(b,ensure_ascii=False,sort_keys=True)+'\n' for b in blocks),encoding='utf-8')
(OUT/'DANIEL_SPRACHSPUR_KANDIDATEN.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
(OUT/'DANIEL_SPRACHSPUR_QUELLMANIFEST.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# Daniel-Sprachspur-Scan','',f'- Erstellt UTC: `{dt.datetime.now(dt.timezone.utc).isoformat()}`',f'- Quellen mit erkannten Daniel-Blöcken: `{len(files)}`',f'- Daniel-Sprecherblöcke: `{len(blocks)}`',f'- Kandidatenterme: `{len(rows)}`','','## Herkunftsklassen','','- `EXPLIZIT_DANIEL`: durch Sprecherlabel abgegrenzt.','- `WAHRSCHEINLICH_DANIEL_KIMI_UI_HEURISTIK`: aus dem UI-Muster unmittelbar vor `Edit / Copy / Share`; muss vor Kanonisierung geprüft werden.','','## Höchstrangige Kandidaten','']
for r in rows[:500]:
    ev=r['evidence'][0]
    md.append(f"- **{r['term']}** · Rang `{r['rank']}` · explizite Daniel-Blöcke `{r['explicit_daniel_blocks']}` · heuristisch `{r['heuristic_daniel_blocks']}` · `{ev['path']}:{ev['line']}`")
(OUT/'DANIEL_SPRACHSPUR_BERICHT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
manifest={'ok':True,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_files':len(files),'speaker_blocks':len(blocks),'candidate_terms':len(rows),'outputs':{n:{'bytes':(OUT/n).stat().st_size,'sha256':hashlib.sha256((OUT/n).read_bytes()).hexdigest()} for n in ['DANIEL_SPRECHERBLOECKE.jsonl','DANIEL_SPRACHSPUR_KANDIDATEN.jsonl','DANIEL_SPRACHSPUR_QUELLMANIFEST.json','DANIEL_SPRACHSPUR_BERICHT.md']}}
(OUT/'DANIEL_SPRACHSPUR_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
