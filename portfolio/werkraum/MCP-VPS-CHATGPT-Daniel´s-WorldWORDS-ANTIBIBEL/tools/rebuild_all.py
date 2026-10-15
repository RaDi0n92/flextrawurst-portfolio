#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'truth_engine/runtime'

def sha(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def run(name:str,args:list[str])->dict:
 started=dt.datetime.now(dt.timezone.utc).isoformat()
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=300)
 row={'name':name,'command':args,'started_utc':started,'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'returncode':p.returncode,'stdout':p.stdout[-40000:],'stderr':p.stderr[-40000:]}
 if p.returncode!=0:raise RuntimeError(json.dumps(row,ensure_ascii=False))
 try:row['parsed']=json.loads(p.stdout)
 except Exception:pass
 return row

def build(dry_run=False)->dict:
 RUNTIME.mkdir(parents=True,exist_ok=True)
 if dry_run:return {'ok':True,'dry_run':True,'steps':['conversation_graph','time_stream','truth_pre','vault','validation','truth_final','vault_final','validation_final']}
 steps=[]
 steps.append(run('conversation_graph',[sys.executable,'conversation_graph/build_conversation_graph.py']))
 steps.append(run('time_stream',[sys.executable,'tools/build_project_time_stream.py']))
 steps.append(run('truth_pre',[sys.executable,'tools/build_current_truth.py','--phase','pre_validation']))
 steps.append(run('vault',[sys.executable,'tools/build_obsidian_vault.py']))
 try:steps.append(run('validation',[sys.executable,'tools/validate_obsidian_vault.py','--write-report']))
 except RuntimeError as e:
  # Truth gets to see the failed report; the final validation still decides success.
  steps.append({'name':'validation','returncode':2,'error':str(e)})
 steps.append(run('truth_final',[sys.executable,'tools/build_current_truth.py','--phase','final_validation']))
 steps.append(run('vault_final',[sys.executable,'tools/build_obsidian_vault.py']))
 steps.append(run('validation_final',[sys.executable,'tools/validate_obsidian_vault.py','--write-report']))
 result={'ok':True,'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'root':str(ROOT),'steps':steps}
 report=RUNTIME/'last_pipeline_run.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 result['report']=str(report);result['report_sha256']=sha(report)
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 try:r=build(a.dry_run);print(json.dumps(r,ensure_ascii=False,indent=2))
 except Exception as e:
  fail={'ok':False,'failed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'error':repr(e)}
  RUNTIME.mkdir(parents=True,exist_ok=True);(RUNTIME/'last_pipeline_failure.json').write_text(json.dumps(fail,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(fail,ensure_ascii=False,indent=2));raise SystemExit(2)
