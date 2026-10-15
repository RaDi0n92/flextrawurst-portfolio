from pathlib import Path
import os, ast, csv, io, hashlib, json, zipfile, re
from collections import Counter

OUT=Path('/root/werkraum/VPS_ECHTE_KONZEPTE_PY_PLUS_DOKU_FINAL_2026-09-17.zip')
ROOTS=[Path('/root/werkraum'),Path('/root/werkraum_agent'),Path('/root/werkraum_geni'),Path('/root/zensi'),Path('/root/flextrawurst')]

EX_DIRS={'.git','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.analysis-tools','site-packages','dist-packages','node_modules','vendor','venv','.venv','.venv-whisper','env','.env','extracted_sources','nested_archives','archive','archives','backup','backups','history','evidence','releases','sessions','worktrees'}
EX_TOP={'_gemini','_claude','_codex','_kimi','_gpt','_shared','_Anthropic-Claude','wir-muessen-claude-code-retten','flextrawurst-audit','tests','uploads','kosmos_paket_chatgpt','arbeitskoerper-redteam-22','claude-systembericht','wesen_test','.claude'}
EX_PREFIX=('test_','debug_','fix_','patch_','apply_','simulation_','qualitaetstest_','_fix','_patch','_inspect','_splice','einmal_')
EX_CONTAINS=('before.','before-restore','before-framework','rauchtest','premortem','fixture')
EX_PATH_PARTS={'skripte_77','daniels_semantischer_bibliothekskoerper_20260801','bibliotheksatlas_20260801','piko-reference','waydroid-libndk-work'}
EX_FILE_NAMES={'build_root_python_export.py','build_real_python_concepts_export.py','build_final_real_concepts_export.py','inbox_leeren.py'}

# Kategorieerkennung für Code und Doku.
def category(path:Path, text=''):
    s=str(path).lower().replace('\\','/')
    n=path.name.lower()
    blob=(s+' '+text[:12000].lower())

    # Erst eindeutige Dateinamen/Pfade, erst danach Inhaltsbegriffe.
    if n in {'tts_service.py','windows_diktat.py','windows_diktat_knopf.py'} or '/datei_wandler/' in s or any(k in n for k in ('toolbox','tts_werkzeugsammlung','diktat_stimme')):
        return '07_SURFACE_TOOLBOX'
    if 'surface_8787' in n:
        return '08_SURFACE_8787_UI'
    if any(k in n for k in ('obsidian','vault','megavault')) or '/obsidian_vault/' in s:
        return '03_OBSIDIAN_UND_WESEN_VAULTS'
    if n.startswith('codewesen_') or any(k in n for k in ('cyberling','wesen_dienst','wesen_einzug','traum_','schlaf','weltfutter')):
        return '01_CODEWESEN_WELT_SCHLAF_TRAUM'
    if n in {'erstpost.py','erstvorstellung_dakgord.py','profilbild_antworten.py','reaktion_auf_dakgord.py','starte_alle_codewesen.py','weltbild_builder.py'}:
        return '01_CODEWESEN_WELT_SCHLAF_TRAUM'
    if n.startswith('flarum_') or '/flarum/' in s:
        return '02_FLARUM_PLATTFORM'
    if '/tools/vps_mcp/' in s or 'vps_mcp' in n:
        return '09_VPS_MCP_WERKZEUGKOERPER'
    if '/tools/action_history/' in s:
        return '10_ACTION_HISTORY_BROWSER'
    if '/gesamtatlas' in s:
        return '13_GESAMTATLAS'
    if '/tools/3d_pipeline/' in s or '/engine/' in s or 'godot' in n:
        return '14_SPIELWELT_3D_GODOT'
    if 'worldwords' in s or 'antibibel' in s:
        return '15_WORLDWORDS_ANTIBIBEL'
    if '/mein-gesamtkonstrukt-planer/' in s or n.startswith('planner_'):
        return '16_GESAMTKONSTRUKT_PLANER'
    if '/kosmos/' in s:
        return '17_KOSMOS_WELTBAU'
    if '/werkraum_agent/' in s or 'dak_gord' in n or 'dakgord' in n:
        return '04_DAK_GORD_AGENT'
    if '/werkraum_geni/' in s:
        return '05_GENI'
    if '/zensi/' in s:
        return '06_ZENSI_SCHLAF_SPIEGELWESEN'
    if '/welt/' in s:
        if any(k in n for k in ('rag_','splitter','similarity','themen_cluster','zweitgehirn')):
            return '12_RAG_DATEN_GEDAECHTNIS'
        return '11_WELT_API_BEOBACHTUNG'
    if 'systemweiser' in n:
        return '18_SYSTEMWEISER'
    if any(k in n for k in ('llm_scheduler','kollisions_scheduler','watchdog','dienst_konfiguration','container_admin')):
        return '19_SCHEDULER_DAEMONS_INFRA'
    if any(k in n for k in ('web_chat','api_bridge','tts_utils')):
        return '20_WEB_CHAT_API_TTS'
    if '/tools/chatgpt_browser_recorder/' in s:
        return '21_BROWSER_RECORDER'
    if '/innenleben/' in s:
        return '22_INNENLEBEN'

    # Technische Dokus anhand ihres Namens einordnen.
    if any(k in n for k in ('codewesen','wesen_chat','wesen_dienst','langgraph','umgekehrte_neugier','wesenkern','gruppenchat')):
        return '01_CODEWESEN_WELT_SCHLAF_TRAUM'
    if 'flarum' in n:
        return '02_FLARUM_PLATTFORM'
    if any(k in n for k in ('obsidian','vault','megavault')):
        return '03_OBSIDIAN_UND_WESEN_VAULTS'
    if any(k in n for k in ('dakgord','dak_gord')):
        return '04_DAK_GORD_AGENT'
    if 'geni' in n:
        return '05_GENI'
    if 'zensi' in n:
        return '06_ZENSI_SCHLAF_SPIEGELWESEN'
    if 'mcp' in n and '3d' not in n:
        return '09_VPS_MCP_WERKZEUGKOERPER'
    if any(k in n for k in ('3d','godot','spielwelt')):
        return '14_SPIELWELT_3D_GODOT'
    if any(k in n for k in ('rag','gedaechtnis','gedächtnis')):
        return '12_RAG_DATEN_GEDAECHTNIS'
    if any(k in n for k in ('scheduler','daemon','dienste_provenienz','ports_und_services')):
        return '19_SCHEDULER_DAEMONS_INFRA'
    if any(k in n for k in ('welt_api','kompoase','live_daten','weltfutter','reibungsgewebe','fragen_api')):
        return '11_WELT_API_BEOBACHTUNG'
    if any(k in n for k in ('browser','live_update')):
        return '10_ACTION_HISTORY_BROWSER'

    # Nur als letzter Ausweg semantischer Inhalt.
    if 'obsidian' in blob or 'wesen-vault' in blob or 'wesenvault' in blob:
        return '03_OBSIDIAN_UND_WESEN_VAULTS'
    if 'codewesen' in blob or 'cyberling' in blob:
        return '01_CODEWESEN_WELT_SCHLAF_TRAUM'
    if 'flarum' in blob:
        return '02_FLARUM_PLATTFORM'
    return '90_SONSTIGE_EIGENE_TOOLS'

# 1) PYTHON: alle eigenen Kandidaten, harte technische Müllfilter.
py_items=[]
for root in ROOTS:
    if not root.is_dir(): continue
    for base,dirs,files in os.walk(root,followlinks=False):
        b=Path(base)
        try: rel=b.relative_to(root)
        except: rel=Path('.')
        parts=list(rel.parts)
        top=parts[0] if parts else ''
        if root==Path('/root/werkraum') and top in EX_TOP:
            dirs[:]=[]; continue
        if any(p in EX_PATH_PARTS for p in parts):
            dirs[:]=[]; continue
        dirs[:]=[d for d in dirs if d not in EX_DIRS and d not in EX_PATH_PARTS]
        for fn in files:
            if not fn.endswith('.py') or fn in EX_FILE_NAMES: continue
            low=fn.lower()
            if low.startswith(EX_PREFIX) or any(x in low for x in EX_CONTAINS): continue
            p=b/fn
            if '/migrations/' in str(p): continue
            # aktive Tests/Probes sind Beweis-/QA-Code, nicht das gebaute Konzept selbst
            if '/tests/' in str(p) or '/test/' in str(p) or 'probe' in low: continue
            try: data=p.read_bytes()
            except: continue
            text=data.decode('utf-8','replace')
            py_items.append((category(p,text),p,data,text))

# Dedup Pfad.
seen=set(); tmp=[]
for x in py_items:
    if str(x[1]) in seen: continue
    seen.add(str(x[1])); tmp.append(x)
py_items=tmp

# 2) DOKU: kanonische Systemdoku komplett.
md_items=[]
def add_md(p,cat=None):
    p=Path(p)
    if not p.is_file() or p.suffix.lower()!='.md': return
    try: data=p.read_bytes()
    except: return
    text=data.decode('utf-8','replace')
    md_items.append((cat or category(p,text),p,data,text))

sysd=Path('/root/werkraum/docs/systemdoku')
if sysd.is_dir():
    for p in sorted(sysd.glob('*.md')): add_md(p)

# Technische Berichte direkt unter docs. Bewusst alle: nur ~50 kuratierte Dateien, kein Vault-/Chat-Massenbestand.
docs=Path('/root/werkraum/docs')
if docs.is_dir():
    for p in sorted(docs.glob('*.md')): add_md(p)

# Technische Vault-Kerndateien: keine Gespräche, Antworten, Weltbilder oder Erinnerungsmasse.
vault=Path('/root/werkraum/obsidian_vault')
VAULT_KEYS=('index','konzept','architektur','system','engine','protokoll','status','struktur','technik','service','dienst','pipeline','scheduler','graph','langgraph','vault','api','modell','workflow','zustand','validierung','validation','feedbacksystem')
VAULT_EX=('antwort','gespraech','post','erinner','tagebuch','journal','spiegel','weltbild','ideen','abwaurf')
if vault.is_dir():
    for p in vault.rglob('*.md'):
        low=p.name.lower()
        if any(x in low for x in VAULT_EX): continue
        if any(x in low for x in VAULT_KEYS): add_md(p,'03_OBSIDIAN_UND_WESEN_VAULTS')

# Projektdoku direkt an echten Codekörpern: README/ARCHITEKTUR/KONZEPT/SPEC/MANIFEST/SETUP.
DOC_NAMES=('readme','architecture','architektur','konzept','concept','design','spec','manifest','setup','install','documentation','doku')
project_roots=[
Path('/root/werkraum_agent/dak_gord_system'),Path('/root/werkraum_geni'),Path('/root/zensi'),
Path('/root/werkraum/WorldWORDS-ANTIBIBEL-Website'),Path('/root/werkraum/WorldWORDS-ANTIBIBEL-Open-Source'),
Path('/root/werkraum/Mein-Gesamtkonstrukt-planer'),Path('/root/werkraum/tools/vps_mcp'),Path('/root/werkraum/tools/action_history'),
Path('/root/werkraum/tools/gesamtatlas_organismus'),Path('/root/werkraum/tools/gesamtatlas_world'),Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis'),
Path('/root/werkraum/tools/3d_pipeline'),Path('/root/werkraum/tools/chatgpt_browser_recorder'),
Path('/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum'),Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL')]
for root in project_roots:
    if not root.is_dir(): continue
    for base,dirs,files in os.walk(root):
        b=Path(base)
        try: rel=b.relative_to(root)
        except: rel=Path('.')
        if len(rel.parts)>=3: dirs[:]=[]
        dirs[:]=[d for d in dirs if d not in EX_DIRS and d not in EX_PATH_PARTS and not d.startswith('.')]
        for fn in files:
            low=fn.lower()
            if not low.endswith('.md'): continue
            if any(low.startswith(x) for x in DOC_NAMES): add_md(b/fn)

# Dedupliziere Doku nach Pfad.
seen=set(); tmp=[]
for x in md_items:
    if str(x[1]) in seen: continue
    seen.add(str(x[1])); tmp.append(x)
md_items=tmp

# Metadaten/Analyse: jede PY vollständig gelesen; AST soweit möglich.
rows=[]
for cat,p,data,text in py_items:
    funcs=classes=0; doc=''; syntax='ok'; imports=[]
    try:
        tree=ast.parse(text)
        doc=(ast.get_docstring(tree) or '').replace('\n',' ')[:350]
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): funcs+=1
            elif isinstance(n,ast.ClassDef): classes+=1
            elif isinstance(n,ast.Import): imports += [a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom) and n.module: imports.append(n.module)
    except Exception as e: syntax=type(e).__name__
    rows.append({'category':cat,'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'syntax':syntax,'functions':funcs,'classes':classes,'imports':';'.join(sorted(set(imports))[:30]),'docstring':doc})

mdrows=[{'category':cat,'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for cat,p,data,text in md_items]

def csv_bytes(rows,fields):
    s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=fields); w.writeheader(); w.writerows(rows); return s.getvalue().encode('utf-8-sig')

py_counts=Counter(x[0] for x in py_items); md_counts=Counter(x[0] for x in md_items)
readme='''# Finaler bereinigter Export echter Python-Konzepte\n\nZiel: echte selbst gebaute Python-Teilsysteme und ihre technische Dokumentation.\n\nEnthalten werden aktive Eigenbauten aus Werkraum, Welt, Tools, Agent, GENI, Zensi und Flextrawurst-Helfern. Die kanonische `docs/systemdoku` ist vollständig enthalten. Dazu kommen technische Berichte unter `docs/`, technische Kern-Dokumente aus dem Obsidian-Vault sowie projektnahe README/KONZEPT/ARCHITEKTUR/SPEC-Dokumente.\n\nBewusst ausgeschlossen: virtuelle Umgebungen, site-packages/dist-packages, Fremdcode, Agenten-Spiegel/Kopien, extrahierte Archive, Backups/History, Tests/Fixtures/Probes, generierte `kosmos/skripte_77`, Bibliotheksatlas-Massenkörper und einmalige Fix/Patch/Red-Team-Skripte.\n\nSurface Toolbox ist explizit enthalten (`welt/tts_service.py`, Datei-Wandler, Diktat-Helfer und Toolbox-Doku). Obsidian/Wesen-Vaults und Codewesen/Welt/Schlaf/Traum sind explizite eigene Kategorien.\n'''

if OUT.exists(): OUT.unlink()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
    z.writestr('00_MANIFEST/README.md',readme.encode('utf-8'))
    z.writestr('00_MANIFEST/PYTHON_MANIFEST.csv',csv_bytes(rows,['category','path','bytes','sha256','syntax','functions','classes','imports','docstring']))
    z.writestr('00_MANIFEST/DOKU_MANIFEST.csv',csv_bytes(mdrows,['category','path','bytes','sha256']))
    stats={'python_count':len(py_items),'markdown_count':len(md_items),'python_by_category':dict(sorted(py_counts.items())),'markdown_by_category':dict(sorted(md_counts.items()))}
    z.writestr('00_MANIFEST/STATISTIK.json',json.dumps(stats,ensure_ascii=False,indent=2).encode('utf-8'))
    for cat,p,data,text in sorted(py_items,key=lambda x:(x[0],str(x[1]))):
        z.writestr(f'{cat}/PY/{str(p).lstrip("/")}',data)
    for cat,p,data,text in sorted(md_items,key=lambda x:(x[0],str(x[1]))):
        z.writestr(f'{cat}/MD/{str(p).lstrip("/")}',data)

with zipfile.ZipFile(OUT) as z:
    bad=z.testzip(); entries=len(z.namelist())
print(json.dumps({'zip':str(OUT),'python_count':len(py_items),'markdown_count':len(md_items),'zip_bytes':OUT.stat().st_size,'entries':entries,'zip_test_bad':bad,'python_by_category':dict(sorted(py_counts.items())),'markdown_by_category':dict(sorted(md_counts.items()))},ensure_ascii=False,indent=2))
