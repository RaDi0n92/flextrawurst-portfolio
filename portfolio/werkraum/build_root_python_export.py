import os, re, ast, csv, io, json, hashlib, zipfile, time
from collections import Counter, defaultdict
from pathlib import Path

ROOTS = [
    '/root/werkraum', '/root/flextrawurst', '/root/zensi',
    '/root/.gemini/antigravity-cli/brain', '/root/werkraum_bilder',
    '/root/werkraum_geni', '/root/werkraum_codewesen', '/root/werkraum_agent',
    '/root/werkraum_erkenntnis', '/root/werkraum_flarum', '/root/werkraum_logs',
    '/root/.claude/projects', '/root/.codex/sessions'
]
OUTDIR = Path('/root/werkraum/vps_python_export_2026-09-17')
OUTDIR.mkdir(parents=True, exist_ok=True)
ZIPPATH = Path('/root/werkraum/VPS_ROOT_PY_KONZEPTE_PLUS_MD_2026-09-17.zip')
SELF_PATHS = {str(OUTDIR.resolve()), str(ZIPPATH.resolve()), '/root/werkraum/build_root_python_export.py'}

CATEGORIES = {
 '01_CODEWESEN': ['codewesen','wesen','cyberling','resonanzknoten','schorschel','r1zz1','traeumer','träumer','gedankenfeld','neugier','dak_gord','dakgord'],
 '02_FLARUM_PLATTFORM': ['flarum','forum','post_sperre','poster','discussion','shadow comment','schattenkommentar','flextrawurst'],
 '03_SPIELWELT_GODOT_3D': ['godot','spielwelt','game','world_bridge','blender','3d','quest','kosmos','schrottplatz','casino','lod_grid','schwelm','wuppertal','gevelsberg','ennepetal','beyenburg'],
 '04_ZENSI_SCHLAF_TRAUM': ['zensi','schlaf','traum','dream','sleep','langgraph','tick'],
 '05_AGENTEN_LLM_SCHEDULER': ['agent','claude','codex','gemini','kimi','grok','llm','scheduler','haiku','anthrop'],
 '06_OBSIDIAN_DOKU': ['obsidian','vault','markdown','md_','dokument','doku','manifest','moc'],
 '07_SOCIAL_INSTAGRAM_WAYDROID': ['instagram','waydroid','anbox','reel','tiktok','social','frida','media-sync','media_sync'],
 '08_MOELLENKOTTEN_FORSCHUNG': ['moellenkotten','möllenkotten','forschung','semantic_fix','final3'],
 '09_MCP_VPS_INFRA': ['mcp','vps','container','daemon','watchdog','service','dienst','bridge','server','admin_cli','systemweiser'],
 '10_WEB_API_SERVER': ['api','fastapi','flask','http','web','server','client','endpoint','uvicorn'],
 '11_DATENBANK_RAG': ['postgres','database','db','sql','chroma','rag','embedding','vector','entity_states','relationship'],
 '12_TEST_AUDIT': ['test_','tests/','audit','redteam','premortem','simulation','rauchtest','fixture','verify','verification'],
 '13_TOOLS_DATEI_ENCODING': ['encoding','mojibake','file','datei','copy','build','generate','generator','patch','fix_','scan_','prepare_assets','tool']
}
THIRDPARTY_MARKERS = ['/site-packages/','/dist-packages/','/.analysis-tools/','/venv/','/.venv/','/node_modules/']
ARCHIVE_MARKERS = ['/extracted_sources/','/nested_archives/','/archive/','/archives/','/backup/','/backups/']


def read_bytes(path):
    try:
        with open(path, 'rb') as f:
            return f.read(), None
    except Exception as e:
        return b'', f'{type(e).__name__}: {e}'

def decode(data):
    for enc in ('utf-8','utf-8-sig','latin-1'):
        try: return data.decode(enc)
        except Exception: pass
    return data.decode('utf-8','replace')

def python_meta(text):
    doc=''; imports=[]; funcs=classes=0; syntax='ok'
    try:
        tree=ast.parse(text)
        doc=ast.get_docstring(tree) or ''
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): funcs+=1
            elif isinstance(n,ast.ClassDef): classes+=1
            elif isinstance(n,ast.Import): imports.extend(a.name for a in n.names)
            elif isinstance(n,ast.ImportFrom) and n.module: imports.append(n.module)
    except Exception as e:
        syntax=f'{type(e).__name__}'
    return doc[:500].replace('\n',' '), sorted(set(imports))[:30], funcs, classes, syntax

def category(path, text):
    p=path.lower().replace('\\','/')
    if any(m in p for m in THIRDPARTY_MARKERS): return '90_DRITTBIBLIOTHEKEN'
    if any(m in p for m in ARCHIVE_MARKERS): return '80_EXTRAHIERTE_ARCHIVE'
    sample=(p+'\n'+text[:24000].lower())
    scores={k:0 for k in CATEGORIES}
    for cat, keys in CATEGORIES.items():
        for kw in keys:
            kl=kw.lower()
            c=sample.count(kl)
            if c:
                scores[cat]+=min(c,5)
                if kl in p: scores[cat]+=4
    best=max(scores, key=scores.get)
    if scores[best]==0:
        if p.startswith('/root/.claude/') or p.startswith('/root/.codex/') or p.startswith('/root/.gemini/'):
            return '05_AGENTEN_LLM_SCHEDULER'
        return '99_SONSTIGES'
    return best

def iter_files(ext):
    seen=set()
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for base, dirs, files in os.walk(root, followlinks=False):
            # Export selbst und typische Cache-Muellpfade nicht erneut durchlaufen; Pythondateien in echten Drittlibs bleiben drin.
            b=os.path.abspath(base)
            if b.startswith(str(OUTDIR)):
                dirs[:] = []
                continue
            for fn in files:
                if not fn.lower().endswith(ext): continue
                path=os.path.abspath(os.path.join(base,fn))
                if path in seen or path in SELF_PATHS: continue
                seen.add(path)
                yield path

start=time.time()
py_rows=[]; py_dirs=set(); py_cats=set(); unreadable_py=[]
for path in iter_files('.py'):
    data, err=read_bytes(path)
    text=decode(data)
    cat=category(path,text)
    doc, imports, funcs, classes, syntax=python_meta(text)
    sha=hashlib.sha256(data).hexdigest()
    py_dirs.add(os.path.dirname(path)); py_cats.add(cat)
    if err: unreadable_py.append((path,err))
    # Kurzbeschreibung aus Docstring, sonst aus Klassen/Funktionen/Imports + Dateiname.
    if doc:
        summary=doc[:220]
    else:
        bits=[]
        if classes: bits.append(f'{classes} Klassen')
        if funcs: bits.append(f'{funcs} Funktionen')
        if imports: bits.append('Imports: '+', '.join(imports[:6]))
        summary='; '.join(bits) or 'Kein AST-Metadatenhinweis; Einordnung über Pfad/Inhalt.'
    py_rows.append(dict(path=path, category=cat, size=len(data), sha256=sha, docstring=doc,
                        imports=';'.join(imports), functions=funcs, classes=classes, syntax=syntax,
                        summary=summary, data=data))

# Markdown: wirklich vollständig lesen; aufnehmen, wenn im selben Verzeichnis wie Python ODER klar einem vorhandenen Python-Konzept zugeordnet.
md_rows=[]; unreadable_md=[]
for path in iter_files('.md'):
    data, err=read_bytes(path)
    text=decode(data)
    cat=category(path,text)
    same_dir=os.path.dirname(path) in py_dirs
    conceptual=(cat in py_cats and cat not in ('99_SONSTIGES','90_DRITTBIBLIOTHEKEN'))
    thirdparty_related=(cat=='90_DRITTBIBLIOTHEKEN' and same_dir)
    include=same_dir or conceptual or thirdparty_related
    if not include: continue
    sha=hashlib.sha256(data).hexdigest()
    reason='gleiches Verzeichnis wie .py' if same_dir else 'gleiche erkannte Konzeptkategorie'
    if err: unreadable_md.append((path,err))
    md_rows.append(dict(path=path, category=cat, size=len(data), sha256=sha, reason=reason, data=data))

# Deterministische Sortierung.
py_rows.sort(key=lambda r:(r['category'],r['path']))
md_rows.sort(key=lambda r:(r['category'],r['path']))

# CSV-Manifeste in Memory.
def csv_bytes(rows, fields):
    s=io.StringIO(newline='')
    w=csv.DictWriter(s, fieldnames=fields, extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
    return s.getvalue().encode('utf-8-sig')

py_manifest=csv_bytes(py_rows,['category','path','size','sha256','syntax','functions','classes','imports','docstring','summary'])
md_manifest=csv_bytes(md_rows,['category','path','size','sha256','reason'])
counts_py=Counter(r['category'] for r in py_rows)
counts_md=Counter(r['category'] for r in md_rows)

readme = f'''# VPS ROOT Python-Export 2026-09-17\n\nDieser Export enthält alle gefundenen `.py`-Dateien aus den vom VPS-Connector freigegebenen `/root`-Arbeitsbereichen. Jede Python-Datei wurde vollständig als Bytes gelesen, SHA-256-gehasht und für die Einordnung dekodiert; soweit parsebar wurden Modul-Docstring, Imports sowie Klassen-/Funktionszahlen ermittelt.\n\nPassende `.md`-Dateien wurden ebenfalls vollständig gelesen und aufgenommen, wenn sie im selben Verzeichnis wie Python lagen oder semantisch derselben erkannten Konzeptkategorie zugeordnet wurden.\n\nPython-Dateien: {len(py_rows)}\nMarkdown-Dokumente: {len(md_rows)}\nUnlesbare Python-Dateien: {len(unreadable_py)}\nUnlesbare Markdown-Dateien: {len(unreadable_md)}\n\nWichtig: `/root` als pauschaler Dateibaum wurde vom Sicherheitsfilter nicht direkt freigegeben. Verarbeitet wurden daher die explizit freigegebenen Root-Arbeitsbereiche: {', '.join(ROOTS)}. Systempfade wie `/usr` gehören ausdrücklich nicht zu diesem Export.\n\nDie Originalpfade stehen vollständig in den CSV-Manifesten. Innerhalb jeder Konzeptkategorie bleibt der Originalpfad ab `root/...` erhalten, damit keine Namenskollisionen entstehen.\n'''.encode('utf-8')

categories_md=['# Kategorien und Dateizahlen','']
for cat in sorted(set(counts_py)|set(counts_md)):
    categories_md.append(f'- **{cat}**: {counts_py.get(cat,0)} Python, {counts_md.get(cat,0)} Markdown')
categories_md='\n'.join(categories_md).encode('utf-8')

stats={
 'python_count':len(py_rows),'markdown_count':len(md_rows),
 'python_bytes':sum(r['size'] for r in py_rows),'markdown_bytes':sum(r['size'] for r in md_rows),
 'python_by_category':dict(counts_py),'markdown_by_category':dict(counts_md),
 'roots':ROOTS,'unreadable_python':unreadable_py,'unreadable_markdown':unreadable_md,
 'elapsed_before_zip_seconds':round(time.time()-start,2)
}

if ZIPPATH.exists(): ZIPPATH.unlink()
with zipfile.ZipFile(ZIPPATH,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    z.writestr('00_MANIFEST/README.md',readme)
    z.writestr('00_MANIFEST/KATEGORIEN.md',categories_md)
    z.writestr('00_MANIFEST/PYTHON_DATEIEN.csv',py_manifest)
    z.writestr('00_MANIFEST/MARKDOWN_DOKU.csv',md_manifest)
    z.writestr('00_MANIFEST/STATISTIK.json',json.dumps(stats,ensure_ascii=False,indent=2).encode('utf-8'))
    for r in py_rows:
        arc=f"{r['category']}/PY/{r['path'].lstrip('/')}"
        z.writestr(arc,r['data'])
    for r in md_rows:
        arc=f"{r['category']}/MD/{r['path'].lstrip('/')}"
        z.writestr(arc,r['data'])

# Kleine externe Zusammenfassung.
summary={**stats,'zip':str(ZIPPATH),'zip_size':ZIPPATH.stat().st_size,'elapsed_total_seconds':round(time.time()-start,2)}
(OUTDIR/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
