from pathlib import Path
import os, zipfile, hashlib, csv, io, ast, json, fnmatch

ZIP=Path('/root/werkraum/VPS_ECHTE_PY_KONZEPTE_PLUS_DOKU_2026-09-17.zip')

# Bewusst kuratierter Kern: keine Tests, Backups, Archive, venvs, Agentenspiegel, generierten Serien oder Audit-/Patchreste.
TOP_FILES = '''
api_bridge.py
chatte_dak_gord.py
codewesen_abwurf.py
codewesen_agent.py
codewesen_antwort_auf_daniel.py
codewesen_aufgabenchats.py
codewesen_batch_generator.py
codewesen_chat.py
codewesen_container.py
codewesen_engagement.py
codewesen_forum_neugier.py
codewesen_forum_scan.py
codewesen_gedankenfeld.py
codewesen_gruppenchat.py
codewesen_klon.py
codewesen_lg_daemon.py
codewesen_reaktion.py
codewesen_reflexion.py
codewesen_speicher.py
codewesen_takt.py
codewesen_umgekehrte_neugier.py
codewesen_vokabel_takt.py
codewesen_werkzeuge.py
container_admin_cli.py
dienst_konfiguration.py
erstpost.py
erstvorstellung_dakgord.py
flarum_api.py
flarum_monitor.py
flarum_post_sperre.py
flarum_poster.py
flarum_stopp_protokoll.py
flarum_stopp_protokoll_spiegel.py
flarum_vokabel_filter.py
gedaechtnis.py
geni_spiegel_batch.py
hauhau_client.py
kollisions_scheduler.py
left_talks_right.py
llm_scheduler.py
namensfindung.py
obsidian_api.py
obsidian_queue.py
obsidian_vault.py
profilbild_antworten.py
protokoll.py
reaktion_auf_dakgord.py
scan_encoding_guard.py
starte_alle_codewesen.py
starte_dak_gord.py
starte_dak_gord_system.py
systemweiser_app.py
systemweiser_status.py
systemweiser_web.py
trigger_daniel_antworten.py
trigger_vorstellung_lesen.py
trigger_vorstellung_neu.py
tts_utils.py
vps_agent_werkbank.py
watchdog_daemon.py
web_chat.py
weltbild_builder.py
wesen_dienst_generator.py
wesen_eigene_dienste.py
'''.strip().splitlines()

explicit=[]
for n in TOP_FILES:
    p=Path('/root/werkraum')/n
    if p.is_file(): explicit.append(p)

# Echte, eigenständige gebaute Teilsysteme. Rekursiv, aber mit harten Müllfiltern.
project_roots = [
 ('02_DAK_GORD_AGENT', Path('/root/werkraum_agent/dak_gord_system')),
 ('03_GENI', Path('/root/werkraum_geni')),
 ('04_ZENSI', Path('/root/zensi')),
 ('05_FLEXTRAWURST_HELPER', Path('/root/flextrawurst/scripts')),
 ('05_FLEXTRAWURST_HELPER', Path('/root/flextrawurst/i18n')),
 ('06_VPS_MCP', Path('/root/werkraum/tools/vps_mcp')),
 ('07_ACTION_HISTORY_BROWSER', Path('/root/werkraum/tools/action_history')),
 ('08_GESAMTATLAS_ORGANISMUS', Path('/root/werkraum/tools/gesamtatlas_organismus')),
 ('08_GESAMTATLAS_ORGANISMUS', Path('/root/werkraum/tools/gesamtatlas_dateikoerper')),
 ('08_GESAMTATLAS_ORGANISMUS', Path('/root/werkraum/tools/gesamtatlas_ursprungsring')),
 ('08_GESAMTATLAS_ORGANISMUS', Path('/root/werkraum/tools/gesamtatlas_endproduktbeweis')),
 ('08_GESAMTATLAS_ORGANISMUS', Path('/root/werkraum/tools/gesamtatlas_world')),
 ('09_SPIELWELT_3D', Path('/root/werkraum/tools/3d_pipeline')),
 ('10_BROWSER_RECORDER', Path('/root/werkraum/tools/chatgpt_browser_recorder')),
 ('11_WORLDWORDS_ANTIBIBEL', Path('/root/werkraum/WorldWORDS-ANTIBIBEL-Website')),
 ('12_GESAMTKONSTRUKT_PLANER', Path('/root/werkraum/Mein-Gesamtkonstrukt-planer/server')),
 ('09_SPIELWELT_3D', Path('/root/werkraum/engine/godot-vertical-slice/deploy')),
 ('09_SPIELWELT_3D', Path('/root/werkraum/engine/godot-vertical-slice/workshop_20260819')),
 ('13_SOCIAL_WAYDROID', Path('/root/werkraum/engine/godot-vertical-slice/frida-instagram')),
 ('13_SOCIAL_WAYDROID', Path('/root/werkraum/engine/godot-vertical-slice/waydroid-desktop1-fixed/frida')),
]

EX_DIRS={'tests','test','history','backups','backup','evidence','releases','migration','migrations','.venv','venv','__pycache__','.git','.pytest_cache','archive','archiv'}
EX_PREFIX=('test_','debug_','patch_','fix_','_fix','_patch','_inspect','_splice','build_v','package_v','scan_v','eval_','run_smoke')
EX_CONTAINS=('before.','before-','probe','redteam','premortem','fixture')

items=[]

def top_category(p:Path):
    n=p.name.lower()
    if n.startswith('codewesen_') or n in {'starte_alle_codewesen.py','weltbild_builder.py','wesen_dienst_generator.py','wesen_eigene_dienste.py','profilbild_antworten.py','reaktion_auf_dakgord.py','erstpost.py','erstvorstellung_dakgord.py'}:
        return '01_CODEWESEN_KERN'
    if n.startswith('flarum_'): return '05_FLARUM_BRUECKE'
    if 'obsidian' in n or n in {'protokoll.py','scan_encoding_guard.py'}: return '14_OBSIDIAN_DOKU_INFRA'
    if n in {'llm_scheduler.py','kollisions_scheduler.py','hauhau_client.py','left_talks_right.py','watchdog_daemon.py','dienst_konfiguration.py','container_admin_cli.py','vps_agent_werkbank.py'}: return '15_LLM_SCHEDULER_INFRA'
    if n.startswith('systemweiser_'): return '16_SYSTEMWEISER'
    if n in {'web_chat.py','api_bridge.py','tts_utils.py'}: return '17_WEB_CHAT_API_TTS'
    if n.startswith('trigger_') or n in {'chatte_dak_gord.py','starte_dak_gord.py','starte_dak_gord_system.py','namensfindung.py','gedaechtnis.py','geni_spiegel_batch.py'}: return '02_DAK_GORD_AGENT'
    return '18_SONSTIGE_EIGENE_KERNTOOLS'

for p in explicit:
    items.append((top_category(p),p))

for cat,root in project_roots:
    if not root.is_dir(): continue
    for base,dirs,files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EX_DIRS and not d.startswith('.')]
        parts=set(Path(base).relative_to(root).parts)
        if parts & EX_DIRS: continue
        for fn in files:
            if not fn.endswith('.py'): continue
            low=fn.lower()
            if low.startswith(EX_PREFIX) or any(x in low for x in EX_CONTAINS): continue
            p=Path(base)/fn
            items.append((cat,p))

# Sonderfälle: die zwei Zensi-Kernskripte sind ohnehin drin; Waydroid nur aktuelle Daemons/Hooks, keine Probe-/Testserien.
# Dedupliziere Pfade.
seen=set(); clean=[]
for cat,p in items:
    s=str(p)
    if s in seen or not p.is_file(): continue
    seen.add(s); clean.append((cat,p))
items=clean

# Technische Markdown-Doku: nur klar benannte technische Dokumente, keine Text-/Erinnerungsbestände.
DOC_PREFIXES=('readme','architektur','architecture','konzept','concept','doku','documentation','design','spec','api','protokoll','protocol','uebergabe','übergabe','install','setup','overview','manifest')
DOC_EX=('log','session','gespraech','conversation','erinnerung','memory','antworten','posts','post_','flarum_antwort','spiegel','roh','journal','tagebuch')

# Kategorie + Projektwurzel + maximale Rekursionstiefe für Doku.
doc_roots=[
 ('18_SONSTIGE_EIGENE_KERNTOOLS', Path('/root/werkraum'), 0),
 ('02_DAK_GORD_AGENT', Path('/root/werkraum_agent/dak_gord_system'), 2),
 ('03_GENI', Path('/root/werkraum_geni'), 1),
 ('04_ZENSI', Path('/root/zensi'), 1),
 ('05_FLEXTRAWURST_HELPER', Path('/root/flextrawurst'), 2),
]
for cat,r in project_roots:
    doc_roots.append((cat,r,2))

md_items=[]
seen_md=set()
for cat,root,maxdepth in doc_roots:
    if not root.is_dir(): continue
    for base,dirs,files in os.walk(root):
        rel=Path(base).relative_to(root)
        if len(rel.parts)>=maxdepth: dirs[:] = []
        dirs[:] = [d for d in dirs if d not in EX_DIRS and d not in {'obsidian_vault','vault','logs','sessions','spuren','flarum_antworten'} and not d.startswith('.')]
        for fn in files:
            low=fn.lower()
            if not low.endswith('.md'): continue
            stem=low[:-3]
            if any(x in low for x in DOC_EX): continue
            if not stem.startswith(DOC_PREFIXES): continue
            q=Path(base)/fn
            if not q.is_file() or str(q) in seen_md: continue
            seen_md.add(str(q)); md_items.append((cat,q))
md_items.sort(key=lambda x:(x[0],str(x[1])))
md=[p for _,p in md_items]

# Datei-Metadaten wirklich aus Inhalt erzeugen.
rows=[]
for cat,p in items:
    data=p.read_bytes()
    text=data.decode('utf-8','replace')
    doc=''; funcs=classes=0
    try:
        tree=ast.parse(text)
        doc=(ast.get_docstring(tree) or '').replace('\n',' ')[:300]
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): funcs+=1
            elif isinstance(n,ast.ClassDef): classes+=1
    except Exception: pass
    rows.append({'category':cat,'path':str(p),'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'functions':funcs,'classes':classes,'docstring':doc})

buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=['category','path','size','sha256','functions','classes','docstring']); w.writeheader(); w.writerows(rows)

readme=f'''# Echte Python-Konzepte / gebaute Teilsysteme\n\nBereinigter Export vom 17.09.2026.\n\nEnthalten: {len(items)} Python-Dateien aus aktiv gebauten, eigenen Teilsystemen sowie {len(md)} technische Markdown-Dokumente.\n\nBewusst NICHT enthalten: venv/site-packages, Fremdbibliotheken, Agenten-Spiegelordner, extrahierte Archive, Backups/History, Tests, Red-Team-/Probe-Dateien, einmalige Patch/Fix-Skripte, generierte Kosmos-100er-Serien, Gesprächs-/Erinnerungs-/Codewesen-Textmassen.\n\nJede Python-Datei wurde vollständig eingelesen und SHA-256-gehasht. Das Manifest nennt den Originalpfad.\n'''

if ZIP.exists(): ZIP.unlink()
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.writestr('00_MANIFEST/README.md',readme.encode())
    z.writestr('00_MANIFEST/PYTHON_MANIFEST.csv',buf.getvalue().encode('utf-8-sig'))
    z.writestr('00_MANIFEST/DOKU_MANIFEST.txt','\n'.join(f'{cat} | {p}' for cat,p in md_items).encode())
    for cat,p in items:
        z.write(p, f'{cat}/PY/{str(p).lstrip("/")}')
    for cat,p in md_items:
        z.write(p, f'{cat}/MD/{str(p).lstrip("/")}')

with zipfile.ZipFile(ZIP) as z:
    bad=z.testzip(); entries=len(z.namelist())
print(json.dumps({'zip':str(ZIP),'python_count':len(items),'md_count':len(md),'zip_bytes':ZIP.stat().st_size,'entries':entries,'zip_test_bad':bad,'categories':sorted(set(c for c,_ in items))},ensure_ascii=False,indent=2))
