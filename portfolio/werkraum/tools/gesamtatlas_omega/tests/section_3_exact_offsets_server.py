#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
PROBE=Path('/root/werkraum/tools/gesamtatlas_omega/tests/section_3_exact_offsets_probe.py')
def load_probe():
 spec=importlib.util.spec_from_file_location('omega_section3_probe',PROBE)
 if not spec or not spec.loader:raise RuntimeError(f'cannot load {PROBE}')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
PAGE='''<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Omega Exact Byte Offsets</title><style>body{font:16px/1.45 system-ui;background:#111;color:#eee;max-width:1050px;margin:40px auto;padding:0 24px}button{font-size:18px;padding:12px 18px}pre{white-space:pre-wrap;background:#1d1d1d;padding:18px;border-radius:10px;max-height:650px;overflow:auto}#status[data-state="PASS"]{color:#8f8}#status[data-state="FAIL"]{color:#f88}</style></head><body><h1>Omega Bauabschnitt 3: Exakte UTF-8-Bytepositionen</h1><p>Chromium indexiert zwei Unicode-Treffer und vergleicht direkte Quellbytes mit den Suchpositionen.</p><button id="run">Bytepositionen prüfen</button><h2 id="status" data-state="IDLE">IDLE</h2><pre id="result"></pre><script>const b=document.getElementById('run'),s=document.getElementById('status'),o=document.getElementById('result');b.addEventListener('click',async()=>{b.disabled=true;s.textContent='RUNNING';s.dataset.state='RUNNING';try{const r=await fetch('/run',{method:'POST'}),d=await r.json();o.textContent=JSON.stringify(d,null,2);s.textContent=d.ok?'PASS':'FAIL';s.dataset.state=d.ok?'PASS':'FAIL';}catch(e){o.textContent=String(e);s.textContent='FAIL';s.dataset.state='FAIL';}finally{b.disabled=false;}});</script></body></html>'''
class H(BaseHTTPRequestHandler):
 def send(self,body:bytes,ctype:str,code:int=200):
  self.send_response(code);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  if self.path=='/':self.send(PAGE.encode(),'text/html; charset=utf-8')
  else:self.send(b'not found','text/plain',404)
 def do_POST(self):
  if self.path!='/run':self.send(b'not found','text/plain',404);return
  try:self.send(json.dumps(load_probe().main(),ensure_ascii=False).encode(),'application/json; charset=utf-8')
  except Exception as e:self.send(json.dumps({'ok':False,'error':repr(e)}).encode(),'application/json; charset=utf-8',500)
 def log_message(self,fmt,*args):print('[HTTP]',fmt%args,flush=True)
if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',0),H);print(json.dumps({'ready':True,'host':'127.0.0.1','port':server.server_address[1]}),flush=True);server.serve_forever()
