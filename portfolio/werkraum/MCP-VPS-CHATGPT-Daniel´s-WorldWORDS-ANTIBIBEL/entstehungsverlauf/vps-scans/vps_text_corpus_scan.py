#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import os
import re
import sys

BASE = Path('/root/werkraum')
OUT = Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/entstehungsverlauf/vps-scans')
MAX_FILE = 12 * 1024 * 1024
EXTS = {'.md','.txt','.json','.jsonl','.html','.htm','.py','.js','.ts','.tsx','.jsx','.css','.yaml','.yml','.toml','.ini','.conf','.service','.sh','.gd','.tscn','.csv','.sql','.xml','.log','.modelfile'}
PRUNE = {'.git','node_modules','.venv','venv','__pycache__','.pytest_cache','.mypy_cache','.cache'}
SELF_SKIP_PREFIXES = (
    'MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/Verweise/',
    'MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/Zeitstrom/',
    'MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/MOC/',
    'MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/truth_engine/generations/',
)
TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüßÀ-ÿ][A-Za-zÄÖÜäöüßÀ-ÿ0-9_+&'’.-]{2,79}")
URL_RE = re.compile(r'(?:https?://|www\.|^[a-f0-9]{24,}$)', re.I)
DISTINCTIVE_ROOTS = (
 'flextra','kompoase','resonanz','codewesen','cyberling','splitter','traumrest','stillgift','grellader',
 'worldblick','spurenf','organhunger','klammerhonig','gesternöl','gesternoel','staubmilch','thronöl','thronoel',
 'blendhonig','rissmilch','biotop','wartekörper','wartekoerper','weltatom','zeitadresse','bauring','symbosit',
 'metawar','gordslider','flextraburst','antibibel','worldwords','alleswisser','wesenspawn','resonanzknoten',
 'dak+gord','namelessai','flarum','zensi','solarius','codexium','mischpult','eskalator','diskursarch',
 'gedankenblase','schattenkommentar','weltkörper','weltkoerper','druckkörper','druckkoerper','wahrheitskörper',
 'wahrheitskoerper','provenienzmaschine','spurmaschine','zwischenwesen','resonanzfrei','lebensraum','weltorgan',
 'wortkörper','wortkoerper','metamonster','wunschkörper','wunschkoerper','herkunftskörper','herkunftskoerper'
)
SEEDS = [
 'Flextrawurst','KompOase','Resonanzurlaub','Codewesen','AI-Ströme','AI-Stroeme','Schattenkommentar',
 'Gedankenblase','Cyberling','Cyberlinge','Splitterphysik','Traumrest-Diffusion','Stillgift','Grellader',
 'Worldblick','Spurenfähigkeit','Spurenfaehigkeit','Organhunger','Klammerhonig','Gesternöl','Gesternoel',
 'Staubmilch','Thronöl','Thronoel','Blendhonig','Rissmilch','Biotop-Protokoll','Flextraburst',
 'Wartekörper','Wartekoerper','Alleswisserbehaupterarschloch','Superdupermegaalleswisserbehaupterarschloch',
 'Symbositierung','Resonanzknoten','dak+gord','Gordslider','Zensi','GENI','MetaWar','Solarius','Codexium',
 'Dolphin Mischpult','Zwischenwesen','Resonanzfreiheit','resonanzfrei','Weltatom','Zeitadresse','Bauring',
 'WorldWORDS','ANTIBIBEL','Wesenspawner','Flüchtlinge','Fluechtlinge','KompOase','Diskursarchäologie',
 'Diskursarchaeologie','Wissenshüllen','Wissenshuellen','Lebensvertrag','Life Contracts','Systemweiser',
 'Neugierkern','Schattenaccount','Schatten-ai-stromaccount','Einzugsritual','Weltklima','Gedächtnismembran',
 'Gedaechtnismembran','Wahrnehmungsmembran','Gedankenwelt','Traumstaub','Weltapparat','Spurmaschine'
]
SEED_LOW = {s.casefold(): s for s in SEEDS}
COMMON = set('''der die das und oder aber ein eine einer eines einem einen ist sind war waren wird werden wurde wurden mit ohne für fuer von zu im in am auf aus als bei nach vor über ueber unter zwischen durch nicht noch schon auch nur sehr mehr weniger diese dieser dieses diesem diesen ich du er sie es wir ihr man dass denn wenn dann hier dort was wie wer wo wann warum welche welcher welches jeden jede jedes kann können koennen soll sollen muss müssen muessen darf dürfen duerfen hat haben hatte hatten sein seine ihrer ihre mein meine dein deine text datei dateien ordner projekt system code test result output input status true false null none return class function def import from path root werkraum session chatgpt flextrawurst markdown json python service tool tools source target value name title type model user assistant message messages content data file files line lines generated current latest update updated created first last open closed active read write build builder report manifest index home start end error warning success failed unknown default config runtime server client local global public private new old original copy backup final live planned spaeter später body world words word deutsch english german html css javascript typescript linux github obsidian flarum claude codex kimi gemini grok openai api mcp vps utc berlin'''.split())


def iter_files():
    for root, dirs, files in os.walk(BASE, followlinks=False):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        rroot = Path(root)
        for name in files:
            p = rroot / name
            try:
                rel = p.relative_to(BASE).as_posix()
                if any(rel.startswith(x) for x in SELF_SKIP_PREFIXES):
                    continue
                if p.is_symlink() or p.stat().st_size > MAX_FILE:
                    continue
                ext = p.suffix.lower()
                if ext not in EXTS and name not in {'GEMINI.md','CLAUDE.md','KIMI.md','AGENTS.md','grok.md'}:
                    continue
                yield p, rel
            except (OSError, ValueError):
                continue


def decode(raw: bytes):
    if b'\x00' in raw[:8192]:
        return None, 'binary-nul'
    for enc in ('utf-8','utf-8-sig','cp1252','latin-1'):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode('utf-8','replace'), 'utf-8-replace'


def score_token(tok: str, line: str) -> int:
    low = tok.casefold().strip(".'’-")
    if len(low) < 4 or low in COMMON or URL_RE.search(low):
        return -20
    score = 0
    if low in SEED_LOW: score += 20
    roots = sum(1 for r in DISTINCTIVE_ROOTS if r in low)
    score += min(roots * 6, 18)
    if re.search(r'[a-zäöüß][A-ZÄÖÜ]', tok): score += 5
    if re.search(r'[A-Za-zÄÖÜäöüß]\d|\d[A-Za-zÄÖÜäöüß]', tok): score += 4
    if any(ch in tok for ch in '+&'): score += 4
    if '-' in tok and len(tok) >= 9: score += 3
    if len(tok) >= 15: score += 3
    if len(tok) >= 22: score += 2
    if line.lstrip().startswith(('#','-','*','>')): score += 2
    if any(q in line for q in ('„','“','"',"'")): score += 1
    if '_' in tok: score -= 4
    if tok.isupper() and len(tok) < 18: score -= 2
    if re.fullmatch(r'[A-Za-z]+\.(?:md|json|py|js|html|css|txt)', tok, re.I): score -= 8
    return score

started = dt.datetime.now(dt.timezone.utc)
file_count = 0
bytes_read = 0
encoding_counts = Counter()
errors = []
token_counts = Counter()
file_sets = defaultdict(set)
contexts = defaultdict(list)
seed_occ = defaultdict(list)
file_manifest = []

for p, rel in iter_files():
    try:
        raw = p.read_bytes()
        text, enc = decode(raw)
        if text is None:
            continue
        file_count += 1
        bytes_read += len(raw)
        encoding_counts[enc] += 1
        file_manifest.append({'path':str(p),'relative_path':rel,'bytes':len(raw),'mtime_utc':dt.datetime.fromtimestamp(p.stat().st_mtime,tz=dt.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'encoding':enc})
        # Seed phrases, preserving line-level provenance.
        lowered = text.casefold()
        for low, canonical in SEED_LOW.items():
            if low in lowered and len(seed_occ[canonical]) < 40:
                for no, line in enumerate(text.splitlines(), 1):
                    if low in line.casefold():
                        seed_occ[canonical].append({'path':str(p),'relative_path':rel,'line':no,'context':line.strip()[:700]})
                        if len(seed_occ[canonical]) >= 40: break
        for no, line in enumerate(text.splitlines(), 1):
            if len(line) > 20000:
                line = line[:20000]
            for tok in TOKEN_RE.findall(line):
                tok = tok.strip(".'’-")
                s = score_token(tok, line)
                if s < 5:
                    continue
                key = tok.casefold()
                token_counts[key] += 1
                file_sets[key].add(rel)
                if len(contexts[key]) < 12:
                    contexts[key].append({'token':tok,'score':s,'path':str(p),'relative_path':rel,'line':no,'context':line.strip()[:700]})
    except Exception as exc:
        errors.append({'path':str(p),'error':type(exc).__name__+': '+str(exc)[:300]})

# Canonical token form from first occurrence; rank by quality, number of files and frequency.
rows=[]
for key,count in token_counts.items():
    ctx=contexts[key]
    best=max((x['score'] for x in ctx),default=0)
    canonical=ctx[0]['token'] if ctx else key
    rank=best*10 + min(len(file_sets[key]),50)*3 + min(count,100)
    rows.append({'token':canonical,'normalized':key,'occurrences':count,'file_count':len(file_sets[key]),'best_score':best,'rank':rank,'contexts':ctx})
rows.sort(key=lambda x:(-x['rank'],-x['file_count'],-x['occurrences'],x['normalized']))

OUT.mkdir(parents=True,exist_ok=True)
with (OUT/'VPS_DATEIMANIFEST.jsonl').open('w',encoding='utf-8') as f:
    for row in file_manifest: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
with (OUT/'VPS_ROHKANDIDATEN.jsonl').open('w',encoding='utf-8') as f:
    for row in rows: f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
with (OUT/'VPS_SEED_FUNDSTELLEN.json').open('w',encoding='utf-8') as f:
    json.dump(dict(sorted(seed_occ.items())),f,ensure_ascii=False,indent=2)
with (OUT/'VPS_SCAN_FEHLER.json').open('w',encoding='utf-8') as f:
    json.dump(errors,f,ensure_ascii=False,indent=2)

md=['# VPS-Textkorpus-Scan','',f'- Start UTC: `{started.isoformat()}`',f'- Ende UTC: `{dt.datetime.now(dt.timezone.utc).isoformat()}`',f'- Gelesene Text-/Codekörper: `{file_count}`',f'- Gelesene Bytes: `{bytes_read}`',f'- Rohkandidaten: `{len(rows)}`',f'- Seed-Begriffe mit Fundstellen: `{sum(bool(v) for v in seed_occ.values())}`',f'- Lesefehler: `{len(errors)}`','', '## Bewusste Ausschlüsse','', '- Versionskontrollobjekte und Abhängigkeitsbäume (`.git`, `node_modules`, virtuelle Python-Umgebungen).', '- Dateien über 12 MiB pro Einzelkörper.', '- Binärdateien mit NUL-Bytes.', '- Bereits generierte ANTIBIBEL-Verweis-, Zeitstrom-, MOC- und Wahrheitsgenerationen, damit der Scanner nicht seine eigenen Echos zählt.', '', '## Höchstrangige Rohkandidaten','']
for row in rows[:300]:
    c=row['contexts'][0] if row['contexts'] else {}
    md.append(f"- **{row['token']}** · Rang `{row['rank']}` · Vorkommen `{row['occurrences']}` · Dateien `{row['file_count']}` · `{c.get('relative_path','?')}:{c.get('line','?')}`")
(OUT/'VPS_SCAN_BERICHT.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
summary={'ok':True,'started_utc':started.isoformat(),'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'files_read':file_count,'bytes_read':bytes_read,'raw_candidate_count':len(rows),'seed_terms_found':sum(bool(v) for v in seed_occ.values()),'errors':len(errors),'encodings':dict(encoding_counts),'outputs':{x.name:{'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in OUT.iterdir() if x.is_file()}}
(OUT/'VPS_SCAN_MANIFEST.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
