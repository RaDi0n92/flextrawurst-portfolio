from pathlib import Path
import zipfile,re,json,csv,io,hashlib,os
from collections import Counter

SRC=Path('/root/werkraum/VPS_ECHTE_KONZEPTE_PY_PLUS_DOKU_FINAL_2026-09-17.zip')
BASE=Path('/root/werkraum')
OUTS={
 'all': BASE/'VPS_ECHTE_KONZEPTE_SANITIZED_ALLES_2026-09-17.zip',
 'no_md': BASE/'VPS_ECHTE_KONZEPTE_SANITIZED_OHNE_MD_2026-09-17.zip',
 'md_only': BASE/'VPS_ECHTE_KONZEPTE_SANITIZED_NUR_MD_2026-09-17.zip',
 'py_only': BASE/'VPS_ECHTE_KONZEPTE_SANITIZED_NUR_PY_2026-09-17.zip',
}

known_patterns=[
    re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),
    re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{20,}\b'),
    re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(r'\bAIza[0-9A-Za-z_-]{30,}\b'),
    re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'),
    re.compile(r'(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]{12,}'),
    re.compile(r'(?i)https?://[^\s/:]+:[^\s/@]{4,}@[^\s]+'),
]
assign=re.compile(r'(?i)^\s*(?:[-*]\s*)?(?:`)?([A-Za-z0-9_. -]*(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|secret|client[_ -]?secret|password|passwort|passwd|pwd|credential|crawl[_ -]?key|private[_ -]?key|auth[_ -]?token)[A-Za-z0-9_. -]*)(?:`)?\s*(?:=|:|=>|ist\s+)\s*(.+?)\s*$')
query_secret=re.compile(r'(?i)([?&](?:key|token|api_key|access_token|secret)=)([^&\s)\]}>]{8,})')
placeholder_re=re.compile(r'(?i)^(?:<[^>]+>|\$\{[^}]+\}|\$[A-Z_][A-Z0-9_]*|\*+|x+|redacted|removed|none|null|leer|nicht\s+gesetzt|nicht\s+gespeichert|env|umgebungsvariable|beispiel|example|your[_ -]|mein[_ -]?token)$')

def likely_real_value(v:str):
    vv=v.strip().strip('`"\'')
    if not vv or len(vv)<6: return False
    if placeholder_re.search(vv): return False
    low=vv.lower()
    if any(x in low for x in ['nirgends','nicht festgehalten','nicht gespeichert','kein passwort','keine zugangsdaten','separate variable','umgebungsvariable','chmod','datei liegt','rotiert','rotierbar','siehe ','steht in ','wird ']): return False
    if len(vv.split())>5 and not re.search(r'[A-Za-z0-9_-]{20,}',vv): return False
    if re.fullmatch(r'[0-9a-fA-F]{40,128}',vv): return False
    return True

def sanitize_md(text:str):
    out=[]; hits=[]; in_private=False
    for i,line in enumerate(text.splitlines(keepends=True),1):
        raw=line.rstrip('\r\n'); eol=line[len(raw):]
        if '-----BEGIN' in raw and 'PRIVATE KEY-----' in raw:
            in_private=True; hits.append((i,'private-key-block')); out.append('[REDACTED_CREDENTIAL_BLOCK]'+eol); continue
        if in_private:
            if '-----END' in raw and 'PRIVATE KEY-----' in raw: in_private=False
            continue
        replaced=raw; kinds=[]
        for pat in known_patterns:
            if pat.search(replaced):
                kinds.append('known-token-pattern'); replaced=pat.sub('[REDACTED_CREDENTIAL]',replaced)
        m=query_secret.search(replaced)
        if m and not placeholder_re.search(m.group(2)):
            kinds.append('secret-query-param'); replaced=query_secret.sub(r'\1[REDACTED_CREDENTIAL]',replaced)
        m=assign.match(replaced)
        if m and likely_real_value(m.group(2)):
            kinds.append('credential-assignment')
            prefix='- ' if raw.lstrip().startswith('- ') else ('* ' if raw.lstrip().startswith('* ') else '')
            replaced=f'{prefix}{m.group(1).strip(" `")}: [REDACTED_CREDENTIAL]'
        if kinds: hits.append((i,'+'.join(sorted(set(kinds)))))
        out.append(replaced+eol)
    return ''.join(out),hits

def is_stray_test_py(name:str):
    base=Path(name).name.lower()
    return base in {'tests.py','test.py'} or base.startswith('test_')

with zipfile.ZipFile(SRC,'r') as zin:
    py=[]; md=[]; redactions=[]; dropped=[]
    for name in zin.namelist():
        if name.startswith('00_MANIFEST/'): continue
        data=zin.read(name)
        if name.lower().endswith('.py'):
            if is_stray_test_py(name):
                dropped.append({'file':name,'reason':'Testdatei, kein Konzept-/Produktivkörper'})
                continue
            py.append((name,data))
        elif name.lower().endswith('.md'):
            clean,hits=sanitize_md(data.decode('utf-8','replace'))
            md.append((name,clean.encode('utf-8')))
            if hits:
                redactions.append({'file':name,'count':len(hits),'lines':[i for i,_ in hits],'types':sorted(set(t for _,t in hits))})

# manifests from the actual sanitized payload, never copy stale manifests
pyrows=[]
for n,d in py:
    pyrows.append({'path':n,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})
mdrows=[]
for n,d in md:
    mdrows.append({'path':n,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()})

def csvb(rows,fields):
    s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=fields); w.writeheader(); w.writerows(rows); return s.getvalue().encode('utf-8-sig')

report={
 'source_zip':str(SRC),
 'python_files_retained':len(py),
 'markdown_files_retained':len(md),
 'markdown_files_redacted':len(redactions),
 'markdown_redaction_events':sum(x['count'] for x in redactions),
 'redactions':redactions,
 'dropped_python_files':dropped,
 'note':'Credential-Werte werden im Report bewusst nicht gespeichert.'
}
stats={'python_files':len(py),'markdown_files':len(md),'redacted_md_files':len(redactions),'redaction_events':sum(x['count'] for x in redactions),'dropped_test_python':len(dropped)}
readme=(
 'SANITIZED EXPORT 2026-09-17\n'
 'Credential-/Secret-artige Klartextwerte in Markdown wurden in den Exportkopien durch [REDACTED_CREDENTIAL] ersetzt.\n'
 'Originaldateien auf dem VPS wurden NICHT verändert.\n'
 'Eine versehentlich enthaltene Django-tests.py wurde als Testcode aus den neuen Paketen entfernt.\n'
 f'Python: {len(py)} | Markdown: {len(md)} | redigierte MD-Dateien: {len(redactions)} | Redaktionen: {sum(x["count"] for x in redactions)}\n'
).encode('utf-8')
manifest_files={
 '00_MANIFEST/README.txt':readme,
 '00_MANIFEST/PYTHON_MANIFEST.csv':csvb(pyrows,['path','bytes','sha256']),
 '00_MANIFEST/DOKU_MANIFEST.csv':csvb(mdrows,['path','bytes','sha256']),
 '00_MANIFEST/REDACTION_REPORT.json':json.dumps(report,ensure_ascii=False,indent=2).encode('utf-8'),
 '00_MANIFEST/STATISTIK.json':json.dumps(stats,ensure_ascii=False,indent=2).encode('utf-8'),
}

for p in OUTS.values():
    if p.exists(): p.unlink()

# ALL: everything + fresh non-MD manifests
with zipfile.ZipFile(OUTS['all'],'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
    for n,d in manifest_files.items(): z.writestr(n,d)
    for n,d in py+md: z.writestr(n,d)

# NO_MD: PY + non-MD manifests/report, literally zero .md entries
with zipfile.ZipFile(OUTS['no_md'],'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
    for n,d in manifest_files.items(): z.writestr(n,d)
    for n,d in py: z.writestr(n,d)

# Strict-only variants: no manifests, exactly requested file type
with zipfile.ZipFile(OUTS['md_only'],'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
    for n,d in md: z.writestr(n,d)
with zipfile.ZipFile(OUTS['py_only'],'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
    for n,d in py: z.writestr(n,d)

for key,p in OUTS.items():
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
        print(json.dumps({
          'variant':key,'path':str(p),'bytes':p.stat().st_size,'entries':len(names),
          'py':sum(n.endswith('.py') for n in names),'md':sum(n.endswith('.md') for n in names),
          'other':sum(not n.endswith(('.py','.md')) for n in names),'zip_test_bad':z.testzip()
        },ensure_ascii=False))
print('REDACTED_MD_FILES',len(redactions),'EVENTS',sum(x['count'] for x in redactions))
print('DROPPED_TEST_PY',len(dropped))
for x in redactions: print('REDACTED',x['file'],'LINES',','.join(map(str,x['lines'])))
for x in dropped: print('DROPPED',x['file'])
