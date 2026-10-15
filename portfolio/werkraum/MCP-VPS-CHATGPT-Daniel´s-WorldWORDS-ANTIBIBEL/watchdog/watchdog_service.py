#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG_PATH=ROOT/'watchdog/config.json'
STATUS_PATH=ROOT/'watchdog/STATUS.json'
LOG=ROOT/'watchdog/logs/events.jsonl'

def load():return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
def ignored(rel:str,cfg:dict)->bool:return any(rel==p or rel.startswith(p.rstrip('/')+'/') for p in cfg['ignore_prefixes'])
def snapshot(cfg:dict)->dict[str,tuple[int,int]]:
 out={}
 for root_name in cfg['watch_roots']:
  base=ROOT/root_name
  if not base.exists():continue
  for p in base.rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts:continue
   r=p.relative_to(ROOT).as_posix()
   if ignored(r,cfg):continue
   st=p.stat();out[r]=(st.st_mtime_ns,st.st_size)
 return out
def log(kind:str,**details):
 LOG.parent.mkdir(parents=True,exist_ok=True)
 row={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'kind':kind,**details}
 with LOG.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
def status(value:str,**extra):
 data={'schema_version':'1.0','status':value,'updated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'observer':'polling','systemd_installed':False,'automatic_freshness_confirmed':value=='RUNNING_FOREGROUND',**extra}
 STATUS_PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pipeline()->dict:
 p=subprocess.run([sys.executable,str(ROOT/'tools/rebuild_all.py')],cwd=ROOT,text=True,capture_output=True,timeout=360)
 row={'returncode':p.returncode,'stdout':p.stdout[-20000:],'stderr':p.stderr[-20000:]}
 log('pipeline_finished',**row)
 if p.returncode!=0:raise RuntimeError(row)
 return row
def self_test()->dict:
 cfg=load();snap=snapshot(cfg)
 bad=[r for r in snap if ignored(r,cfg)]
 required=[ROOT/x for x in ['tools/rebuild_all.py','tools/build_obsidian_vault.py','tools/validate_obsidian_vault.py','tools/build_project_time_stream.py','tools/build_current_truth.py']]
 missing=[str(p) for p in required if not p.exists()]
 result={'ok':not bad and not missing,'observer':'polling','watched_file_count':len(snap),'ignored_leaks':bad,'missing_pipeline_organs':missing,'systemd_installed':False}
 status('AVAILABLE_NOT_INSTALLED',self_test=result);return result
def loop():
 cfg=load();interval=float(cfg.get('poll_interval_seconds',3));debounce=float(cfg.get('debounce_seconds',4));before=snapshot(cfg)
 status('RUNNING_FOREGROUND',pid=os.getpid(),watched_file_count=len(before));log('watchdog_started',pid=os.getpid(),watched_file_count=len(before))
 try:
  while True:
   time.sleep(interval);after=snapshot(cfg)
   if after!=before:
    changed=sorted(set(before)^set(after)|{p for p in set(before)&set(after) if before[p]!=after[p]})
    log('source_change_detected',changed=changed[:500],changed_count=len(changed));time.sleep(debounce);pipeline();before=snapshot(cfg)
 except KeyboardInterrupt:pass
 finally:status('AVAILABLE_NOT_INSTALLED',last_pid=os.getpid());log('watchdog_stopped',pid=os.getpid())
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--once',action='store_true');a=ap.parse_args()
 if a.self_test:print(json.dumps(self_test(),ensure_ascii=False,indent=2))
 elif a.once:print(json.dumps({'ok':True,'pipeline':pipeline()},ensure_ascii=False,indent=2))
 else:loop()
