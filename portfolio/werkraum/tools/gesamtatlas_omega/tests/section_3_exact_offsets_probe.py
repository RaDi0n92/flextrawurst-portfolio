#!/usr/bin/env python3
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,'/root/werkraum/tools/vps_mcp')
import mcp_atlas_omega as omega
RUNTIME=Path('/root/werkraum/_gpt/gesamtatlas/omega/runtime')
def all_offsets(body:bytes,needle:bytes)->list[int]:
 out=[];start=0
 while True:
  i=body.find(needle,start)
  if i<0:return out
  out.append(i);start=i+1
def main()->dict:
 with tempfile.TemporaryDirectory(prefix='exact-offsets-',dir=RUNTIME) as td:
  root=Path(td);source=root/'exact-offsets.txt';db=root/'offsets.sqlite';marker='OMEGA_EXACT_OFFSET_MARKER_ß_Δ_12345';mb=marker.encode('utf-8')
  body=('A'*70011+'\n'+marker+'\n'+'B'*20000+'\n'+marker+'\n'+'C'*257).encode('utf-8');source.write_bytes(body)
  expected=all_offsets(body,mb)
  scan=omega.sync_roots([source],db_path=db,root_names=['section-3-offsets'],chunk_bytes=16384,force=True)
  search=omega.search_full(marker,db_path=db,limit=50)
  observed=sorted({int(off) for row in search.get('results',[]) for off in row.get('match_byte_offsets',[])})
  paths=sorted({row.get('path') for row in search.get('results',[]) if row.get('path')})
  boundary_bytes=[{'offset':off,'before':body[off-1],'after':body[off+len(mb)]} for off in expected]
  result={'schema_version':'1.0','ok':observed==expected and paths==[str(source)] and len(expected)==2,
          'marker':marker,'marker_utf8_hex':mb.hex(),'expected_byte_offsets':expected,'observed_byte_offsets':observed,
          'paths':paths,'source_path':str(source),'source_bytes':len(body),'boundary_bytes':boundary_bytes,'scan':scan,'search':search,
          'expected':'Every returned match_byte_offset equals the direct byte position in the UTF-8 source, for both occurrences.'}
  print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':main()
