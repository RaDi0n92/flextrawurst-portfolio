#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import re

OUT=Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/entstehungsverlauf/aussenraum-scans')
CLAUDE=Path('/root/.claude/projects')
CODEX=Path('/root/.codex/sessions')
ZENSI=Path('/root/zensi')
TOKEN_RE=re.compile(r"[A-Za-zÄÖÜäöüßÀ-ÿ][A-Za-zÄÖÜäöüßÀ-ÿ0-9_+&'’.-]{2,109}")
CONTEXT_MARKERS=[re.compile(x,re.I) for x in [r'-{2,}\s*hier\s+kontext',r'\bhier\s+kontext\b',r'\bcontext\s*:',r'\bkontext\s*:',r'---\s*kontext',r'\n\s*✻\s*(?:Baked|Cooked)']]
DISTINCTIVE=('flextra','kompoase','resonanz','codewesen','cyberling','splitter','traum','stillgift','grellader','worldblick','spurenf','organhunger','klammerhonig','gesternöl','staubmilch','thronöl','blendhonig','rissmilch','biotop','warte','weltatom','zeitadresse','bauring','symbosit','metawar','gordslider','flextraburst','antibibel','worldwords','alleswisser','wesenspawn','resonanzknoten','dak+gord','namelessai','zensi','solarius','codexium','mischpult','eskalator','diskursarch','gedankenblase','schattenkommentar','weltkörper','druckkörper','wahrheitskörper','provenienz','spurmaschine','zwischenwesen','lebensvertrag','gedächtnis','wahrnehmung','formfaden','punktbühne','nullstund','bildhau','ideenmonstr','livesupport','stundenverlauf','robotermodus','forschungssnack','abrufbar','metamonster','wortlike','gärstoff','wesenstoff','questkeim','kontaktspur','emojiresonanz','frischer ai-strom','hakuna','halbtod','mause','wurst','weltorgan','innenquelle','einzugsritual','spielkörper','codekörper','arbeitskörper','materialkörper')
COMMON=set('''der die das und oder aber ein eine einer eines einem einen ist sind war waren wird werden wurde wurden mit ohne für fuer von zu im in am auf aus als bei nach vor über ueber unter zwischen durch nicht noch schon auch nur sehr mehr weniger diese dieser dieses diesem diesen ich du er sie es wir ihr man dass denn wenn dann hier dort was wie wer wo wann warum welche welcher welches jeden jede jedes kann können koennen soll sollen muss müssen muessen darf dürfen duerfen hat haben hatte hatten sein seine ihrer ihre mein meine dein deine text datei dateien ordner projekt system code test result output input status true false null none return class function def import from path root session chatgpt markdown json python service tool tools source target value name title type model user assistant message messages content data file files line lines generated current latest update updated created first last open closed active read write build builder report manifest index home start end error warning success failed unknown default config runtime server client local global public private new old original copy backup final live planned body world words word deutsch english german html css javascript typescript linux github obsidian flarum claude codex kimi gemini grok openai api mcp vps utc berlin okay ja nein bitte danke weiter nochmal jetzt dann schon auch einfach wirklich richtig eigentlich vielleicht irgendwie etwas jemand niemand immer manchmal heute gestern morgen hallo huhu'''.split())

def text_from_content(content):
 if isinstance(content,str):return content
 if isinstance(content,list):
  parts=[]
  for x in content:
   if isinstance(x,str):parts.append(x)
   elif isinstance(x,dict) and isinstance(x.get('text'),str):parts.append(x['text'])
  return '\n'.join(parts)
 if isinstance(content,dict) and isinstance(content.get('text'),str):return content['text']
 return ''
def direct_prefix(text):
 positions=[]
 for rx in CONTEXT_MARKERS:
  m=rx.search(text)
  if m:positions.append(m.start())
 if positions:
  cut=min(positions)
  prefix=text[:cut].strip()
  return prefix if prefix else text[:min(len(text),2000)].strip(), True
 return text.strip(), False

def score(tok,line):
 low=tok.casefold().strip(".'’-")
 if len(low)<4 or low in COMMON or re.fullmatch(r'[a-f0-9]{18,}',low):return -50
 s=min(sum(1 for x in DISTINCTIVE if x in low)*8,24)
 if len(low)>=13:s+=3
 if len(low)>=21:s+=3
 if re.search(r'[a-zäöüß][A-ZÄÖÜ]',tok):s+=5
 if any(c in tok for c in '+&'):s+=4
 if '-' in tok and len(tok)>=9:s+=3
 if re.search(r'\d',tok):s+=1
 if '_' in tok:s-=5
 if tok.isupper() and len(tok)<14:s-=2
 return s

messages=[];source_files=[];seen_message=set();parse_errors=[]
def add(provider,path,timestamp,text,source_class,session_id=None,meta=None):
 if not text or not text.strip():return
 direct,embedded=direct_prefix(text)
 if not direct:return
 digest=hashlib.sha256((provider+'\0'+(timestamp or '')+'\0'+direct).encode('utf-8','replace')).hexdigest()
 # mirrors in Zensi and duplicated event forms collapse here
 if digest in seen_message:return
 seen_message.add(digest)
 messages.append({'provider':provider,'source_class':source_class,'path':str(path),'session_id':session_id,'timestamp':timestamp,'direct_text':direct,'full_input_sha256':hashlib.sha256(text.encode('utf-8','replace')).hexdigest(),'direct_text_sha256':hashlib.sha256(direct.encode('utf-8','replace')).hexdigest(),'embedded_context_detected':embedded,'full_input_length':len(text),'direct_text_length':len(direct),'metadata':meta or {}})

# Claude direct type=user records
if CLAUDE.exists():
 for p in CLAUDE.rglob('*.jsonl'):
  count=0
  try:
   with p.open(encoding='utf-8',errors='replace') as f:
    for no,line in enumerate(f,1):
     try:o=json.loads(line)
     except Exception:continue
     if o.get('type')!='user':continue
     msg=o.get('message') or {}
     if isinstance(msg,dict) and msg.get('role')=='user':
      text=text_from_content(msg.get('content'))
      add('claude',p,o.get('timestamp'),text,'CLAUDE_DIRECT_USER_INPUT_POSSIBLE_PASTED_CONTEXT',o.get('sessionId'),{'line':no,'uuid':o.get('uuid'),'promptId':o.get('promptId')});count+=1
   source_files.append({'provider':'claude','path':str(p),'bytes':p.stat().st_size,'user_records_seen':count,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.stat().st_size<32*1024*1024 else None})
  except Exception as e:parse_errors.append({'path':str(p),'error':repr(e)})
# Codex only event_msg user_message, not injected response_item role=user
if CODEX.exists():
 for p in CODEX.rglob('*.jsonl'):
  count=0
  try:
   with p.open(encoding='utf-8',errors='replace') as f:
    for no,line in enumerate(f,1):
     try:o=json.loads(line)
     except Exception:continue
     if o.get('type')!='event_msg':continue
     payload=o.get('payload') or {}
     if payload.get('type')=='user_message' and isinstance(payload.get('message'),str):
      add('codex',p,o.get('timestamp'),payload['message'],'CODEX_DIRECT_USER_MESSAGE',None,{'line':no});count+=1
   source_files.append({'provider':'codex','path':str(p),'bytes':p.stat().st_size,'user_records_seen':count,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.stat().st_size<32*1024*1024 else None})
  except Exception as e:parse_errors.append({'path':str(p),'error':repr(e)})
# Zensi is deliberately NOT treated as a direct Daniel conversation source.
# Daniel clarified on 2026-07-26 that Zensi has never been in direct use.
# Any Zensi chat-like records are therefore excluded from the direct-speaker corpus
# and must remain a separate imported/mirrored/generated/unknown-provenance layer.

terms=defaultdict(lambda:{'occurrences':0,'messages':set(),'providers':Counter(),'source_classes':Counter(),'evidence':[],'best_score':0})
for idx,m in enumerate(messages):
 for line_no,line in enumerate(m['direct_text'].splitlines(),1):
  for tok in TOKEN_RE.findall(line):
   tok=tok.strip(".'’-");s=score(tok,line)
   if s<5:continue
   low=tok.casefold();r=terms[low];r['occurrences']+=1;r['messages'].add(idx);r['providers'][m['provider']]+=1;r['source_classes'][m['source_class']]+=1;r['best_score']=max(r['best_score'],s)
   if len(r['evidence'])<30:r['evidence'].append({'term':tok,'provider':m['provider'],'source_class':m['source_class'],'path':m['path'],'timestamp':m['timestamp'],'message_index':idx,'line_in_message':line_no,'context':line.strip()[:1200]})
rows=[]
for low,r in terms.items():
 rank=r['best_score']*10+min(len(r['messages']),40)*4+min(r['occurrences'],100)+len(r['providers'])*8
 rows.append({'term':r['evidence'][0]['term'],'normalized':low,'rank':rank,'best_score':r['best_score'],'occurrences':r['occurrences'],'message_count':len(r['messages']),'providers':dict(r['providers']),'source_classes':dict(r['source_classes']),'evidence':r['evidence']})
rows.sort(key=lambda x:(-x['rank'],-x['message_count'],-x['occurrences'],x['normalized']))
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'AGENT_DANIEL_MESSAGES.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in messages),encoding='utf-8')
(OUT/'AGENT_DANIEL_WORDCANDIDATES.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in rows),encoding='utf-8')
(OUT/'AGENT_DANIEL_SOURCE_MANIFEST.json').write_text(json.dumps(source_files,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'AGENT_DANIEL_PARSE_ERRORS.json').write_text(json.dumps(parse_errors,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'ok':True,'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_files':len(source_files),'deduplicated_direct_messages':len(messages),'providers':dict(Counter(x['provider'] for x in messages)),'messages_with_embedded_context':sum(x['embedded_context_detected'] for x in messages),'candidate_terms':len(rows),'parse_errors':len(parse_errors)}
(OUT/'AGENT_DANIEL_SCAN_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# Agenten-Sprecher-Scan: Daniels direkte Eingaben','',f'- Quellen: `{manifest["source_files"]}`',f'- Deduplizierte direkte Nachrichten: `{manifest["deduplicated_direct_messages"]}`',f'- Provider: `{json.dumps(manifest["providers"],ensure_ascii=False)}`',f'- Eingaben mit erkanntem eingebettetem Kontext: `{manifest["messages_with_embedded_context"]}`',f'- Kandidatenterme: `{manifest["candidate_terms"]}`',f'- Parsefehler: `{manifest["parse_errors"]}`','','## Herkunftsschutz','', '- Claude-Nachrichten können von Daniel eingefügten Alttext enthalten. Bei erkannten Kontextmarkern wird nur der Präfix als direkte aktuelle Eingabe gewertet.', '- Codex zählt ausschließlich `event_msg/user_message`, nicht künstlich als Userrolle eingespeiste Startverträge.', '- Zensi ist vollständig aus dem direkten Daniel-Sprecherkorpus ausgeschlossen. Daniel stellte klar, dass Zensi nie direkt eingesetzt wurde.', '', '## Höchstrangige Kandidaten','']
for r in rows[:500]:
 e=r['evidence'][0];md.append(f"- **{r['term']}** · Rang `{r['rank']}` · Nachrichten `{r['message_count']}` · Provider `{','.join(r['providers'])}` · `{e['path']}` · `{e['timestamp']}`")
(OUT/'AGENT_DANIEL_SCAN_BERICHT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
