#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
MOC = ROOT / 'MOC'
GENERATED_MOC_NAMES = {
    '00_PROJEKTKARTE.md','01_HERKUNFT.md','02_WORTKOERPER.md','03_KONZEPTE.md',
    '04_PROPAGANDA_UND_VERBREITUNG.md','05_GESPRAECHE.md','06_HISTORY_UND_ZEITSTROM.md',
    '07_MUTATIONEN.md','08_QUELLEN.md','09_TECHNISCHE_ORGANE.md',
    '98_ZULETZT_GEAENDERT.md','99_DATEIKATALOG.md'
}


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    data=(text.rstrip()+'\n').encode('utf-8')
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        try:os.unlink(tmp)
        except FileNotFoundError:pass
    if path.read_bytes()!=data: raise RuntimeError(f'Rücklesefehler: {path}')


def rel(path: Path) -> str: return path.relative_to(ROOT).as_posix()

def label(path: Path) -> str: return path.stem.replace('_',' ').replace('-',' ').strip()

def root_link(path: Path, text: str|None=None) -> str:
    r=rel(path)
    if path.suffix.lower()=='.md': return f'[[{r[:-3]}|{text or label(path)}]]'
    return f'[{text or path.name}](<{r}>)'

def moc_link(path: Path, text: str|None=None) -> str:
    r=rel(path)
    if path.suffix.lower()=='.md': return f'[[{r[:-3]}|{text or label(path)}]]'
    target=os.path.relpath(path,MOC).replace(os.sep,'/')
    return f'[{text or path.name}](<{target}>)'


def all_files() -> list[Path]:
    out=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts: continue
        r=rel(p)
        if r.startswith('.obsidian/'): continue
        if r=='HOME.md' or (r.startswith('MOC/') and p.name in GENERATED_MOC_NAMES): continue
        if r.startswith('validation/') and p.name in {'VALIDATION_REPORT.json','VALIDATION_REPORT.md'}: continue
        out.append(p)
    return sorted(out,key=lambda p:rel(p).casefold())


def header(title: str, kind: str, tags: list[str]) -> str:
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    return '---\n'+f'title: "{title}"\ntype: "{kind}"\ngenerated: true\nupdated_utc: "{now}"\ntags:\n'+'\n'.join(f'  - {t}' for t in tags)+'\n---\n\n'


def section(title: str, paths: Iterable[Path]) -> str:
    rows=list(paths)
    text=f'## {title}\n\n'
    if not rows: return text+'_Noch keine Dateien._\n\n'
    for p in rows:
        st=p.stat()
        text+=f'- {moc_link(p)}  `[{p.suffix.lstrip(".") or "datei"} · {st.st_size} B · {sha(p)[:12]}]`\n'
    return text+'\n'


def category(files:list[Path], prefix:str) -> list[Path]:
    return [p for p in files if rel(p).startswith(prefix)]


def build_home(files:list[Path]) -> None:
    text=header('Daniel’s WorldWORDS ANTIBIBEL','vault-home',['worldwords','antibibel','obsidian','start'])
    text+='# Daniel’s WorldWORDS ANTIBIBEL\n\n'
    text+='> [!abstract] Wörter dürfen Welten bauen\n> Dieser Vault bewahrt Ursprung, Witz, Fehler, Korrekturen, Deutungen, reale Verkörperungen und spätere Mutationen. Primärquellen bleiben unverändert; MOCs, Verweise, Zeitstrom und aktuelle Wahrheit sind regenerierbare Ansichten.\n\n'
    text+='## Direkte Einstiege\n\n'
    for target,title in [
      ('00_START/00_START_HIER.md','Start hier'),('MOC/00_PROJEKTKARTE.md','Projektkarte'),
      ('MOC/01_HERKUNFT.md','Herkunft'),('MOC/02_WORTKOERPER.md','Wortkörper'),
      ('MOC/03_KONZEPTE.md','Konzepte'),('MOC/04_PROPAGANDA_UND_VERBREITUNG.md','Propaganda und Verbreitung'),
      ('MOC/05_GESPRAECHE.md','Gespräche'),('MOC/06_HISTORY_UND_ZEITSTROM.md','History und Zeitstrom'),
      ('MOC/07_MUTATIONEN.md','Mutationen'),('MOC/08_QUELLEN.md','Quellen'),
      ('MOC/09_TECHNISCHE_ORGANE.md','Technische Organe'),('MOC/98_ZULETZT_GEAENDERT.md','Zuletzt geändert'),
      ('MOC/99_DATEIKATALOG.md','Vollständiger Dateikatalog')]:
        p=ROOT/target
        text+=f'- {root_link(p,title)}\n'
    for target,title in [('GESPRAECHSNETZ.md','Gesprächs- und Bedeutungsnetz'),('ZEITSTROM.md','Zeitstrom'),('AKTUELLE_WAHRHEIT.md','Aktuelle Wahrheit'),('validation/VALIDATION_REPORT.md','Validierung')]:
        p=ROOT/target
        if p.exists(): text+=f'- {root_link(p,title)}\n'
    text+='\n## Erste Wortkörper\n\n'
    for p in category(files,'02_WORTKOERPER/'):
        if p.suffix.lower()=='.md' and p.name!='00_WORTREGISTER.md': text+=f'- {root_link(p)}\n'
    text+='\n## Harte Deutungsgrenze\n\n**„Verdeutschen“ bedeutet in diesem Projekt freiwillige Übernahme nach Verstehen der Tragweite eines Wortes. Wörter sind Einladungen, keine Uniformen.**\n\n'
    text+='## Maschinenstatus\n\n'
    wd=ROOT/'watchdog/STATUS.json'
    if wd.exists():
        try:
            s=json.loads(wd.read_text())
            text+=f'- Lokaler Watchdog: `{s.get("status")}` · installiert `{s.get("systemd_installed")}`\n'
        except Exception:text+='- Lokaler Watchdogstatus konnte nicht gelesen werden.\n'
    text+=f'- Dateien im katalogisierten Körper: `{len(files)}`\n'
    atomic(ROOT/'HOME.md',text)


def write_mocs(files:list[Path]) -> None:
    plans={
      '01_HERKUNFT.md':('Herkunft',[('Ursprung und Korrektur',category(files,'01_HERKUNFT/')),('Startverträge',category(files,'00_START/'))]),
      '02_WORTKOERPER.md':('Wortkörper',[('Verkörperte Wörter',category(files,'02_WORTKOERPER/')),('Sammelbecken',category(files,'05_SAMMELBECKEN/'))]),
      '03_KONZEPTE.md':('Konzepte',[('Denk- und Wachstumsmodelle',category(files,'03_KONZEPTE/'))]),
      '04_PROPAGANDA_UND_VERBREITUNG.md':('Propaganda und Verbreitung',[('Freiwillige Verbreitung',category(files,'04_PROPAGANDA/'))]),
      '05_GESPRAECHE.md':('Gespräche',[('Menschenlesbare Primärgespräche',category(files,'06_GESPRAECHE/')),('UI-Spiegel',category(files,'ui_exports/'))]),
      '06_HISTORY_UND_ZEITSTROM.md':('History und Zeitstrom',[('Lokale History',category(files,'07_HISTORY/')),('Generierter Zeitstrom',category(files,'Zeitstrom/'))]),
      '07_MUTATIONEN.md':('Mutationen',[('Mutationskörper',category(files,'08_MUTATIONEN/'))]),
      '08_QUELLEN.md':('Quellen',[('Quellenregister und Snapshots',category(files,'09_QUELLEN/'))]),
      '09_TECHNISCHE_ORGANE.md':('Technische Organe',[('Generatoren',category(files,'tools/')),('Gesprächsgraph',category(files,'conversation_graph/')),('Watchdog',category(files,'watchdog/')),('Wahrheitskörper',category(files,'truth_engine/')),('Validierung',category(files,'validation/')),('Koordination',category(files,'coordination/')),('Sessions',category(files,'sessions/'))]),
    }
    for name,(title,groups) in plans.items():
        text=header(title,'map-of-content',['worldwords','moc'])+f'# {title}\n\n'
        for group,paths in groups:text+=section(group,paths)
        text+='## Navigation\n\n- [[HOME|Vault Home]]\n- [[MOC/00_PROJEKTKARTE|Projektkarte]]\n'
        atomic(MOC/name,text)


def build_project_map(files:list[Path]) -> None:
    text=header('WorldWORDS ANTIBIBEL · Projektkarte','map-of-content',['worldwords','projektkarte'])
    text+='# Projektkarte\n\n'
    text+='```text\nFreundeswitz / Fehler / Autokorrektur\n              ↓\n        Wort und Fundstelle\n              ↓\n  Deutungen + Korrekturen + Grenzen\n              ↓\n         reale Verkörperung\n              ↓\n Gesprächsnetz ↔ Zeitstrom ↔ Wahrheit\n              ↓\n        spätere Mutationen\n```\n\n'
    text+='## Kernkörper\n\n'
    for r in ['00_START/00_START_HIER.md','01_HERKUNFT/00_DER_FREUNDESWITZ.md','01_HERKUNFT/02_DIE_VERDEUTSCHEN_KORREKTUR.md','02_WORTKOERPER/00_WORTREGISTER.md','06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md','00_START/01_WACHSTUMSVERTRAG.md']:
        p=ROOT/r
        if p.exists():text+=f'- {moc_link(p)}\n'
    text+='\n## Navigation\n\n'
    for p in sorted(MOC.glob('*.md')):
        if p.name not in {'00_PROJEKTKARTE.md','98_ZULETZT_GEAENDERT.md','99_DATEIKATALOG.md'}:text+=f'- [[MOC/{p.stem}|{label(p)}]]\n'
    text+='- [[HOME|Vault Home]]\n'
    atomic(MOC/'00_PROJEKTKARTE.md',text)


def build_recent(files:list[Path]) -> None:
    rows=sorted(files,key=lambda p:p.stat().st_mtime,reverse=True)[:120]
    text=header('Zuletzt geändert','recent-files',['worldwords','recent'])+'# Zuletzt geändert\n\n'
    for p in rows:
        stamp=dt.datetime.fromtimestamp(p.stat().st_mtime,tz=dt.timezone.utc).isoformat()
        text+=f'- `{stamp}` · {moc_link(p)} · `{p.stat().st_size} B` · `{sha(p)[:12]}`\n'
    text+='\n- [[HOME|Vault Home]]\n'
    atomic(MOC/'98_ZULETZT_GEAENDERT.md',text)


def build_catalog(files:list[Path]) -> None:
    text=header('Vollständiger Dateikatalog','file-catalog',['worldwords','catalog'])+'# Vollständiger Dateikatalog\n\n'
    text+='> Dieser Katalog enthält Primärquellen und generierte Organe, ausgenommen seine eigenen MOC-Dateien und die Obsidian-Konfiguration.\n\n'
    groups={}
    for p in files:groups.setdefault(rel(p).split('/',1)[0],[]).append(p)
    for group in sorted(groups,key=str.casefold):
        text+=f'## {group}\n\n'
        for p in groups[group]:text+=f'- {moc_link(p)} · `{rel(p)}` · `{p.stat().st_size} B` · `{sha(p)[:12]}`\n'
        text+='\n'
    text+=f'## Summen\n\n- Dateien: `{len(files)}`\n- Markdown: `{sum(p.suffix.lower()==".md" for p in files)}`\n\n- [[HOME|Vault Home]]\n'
    atomic(MOC/'99_DATEIKATALOG.md',text)


def main() -> int:
    MOC.mkdir(parents=True,exist_ok=True)
    app={'alwaysUpdateLinks':True,'newLinkFormat':'relative','useMarkdownLinks':False,'showUnsupportedFiles':True,'attachmentFolderPath':'Anhaenge'}
    atomic(ROOT/'.obsidian/app.json',json.dumps(app,ensure_ascii=False,indent=2))
    files=all_files()
    write_mocs(files)
    build_project_map(files)
    build_recent(files)
    build_catalog(files)
    build_home(files)
    result={'ok':True,'root':str(ROOT),'catalogued_files':len(files),'generated_mocs':len(GENERATED_MOC_NAMES),'home':str(ROOT/'HOME.md')}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
