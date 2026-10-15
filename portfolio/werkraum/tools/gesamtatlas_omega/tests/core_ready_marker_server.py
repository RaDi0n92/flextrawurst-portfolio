#!/usr/bin/env python3
from __future__ import annotations
import html,json,os,hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
MARKER=Path(os.environ['OMEGA_MARKER_PATH'])
PORT=int(os.environ.get('OMEGA_TEST_PORT','18770'))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load():return json.loads(MARKER.read_text('utf-8'))
def page()->bytes:
 d=load();a=d.get('monsterlabor_adapter') or {};core=d.get('core') or {};pre=d.get('prechecks') or {};n=d.get('next_gates') or {};cg=d.get('claim_gate') or {};claim=d.get('claim') or {}
 rows=[]
 for key,val in pre.items():rows.append(f"<tr data-evidence='{html.escape(key)}'><td>{html.escape(key)}</td><td>{html.escape(str(val.get('status')))}</td><td>{html.escape(str(val.get('checks','')))}</td><td><code>{html.escape(str(val.get('sha256')))}</code></td></tr>")
 adapter=''.join(f"<li data-adapter='{html.escape(k)}'><b>{html.escape(k)}</b>: <code>{html.escape(str(v))}</code></li>" for k,v in sorted(a.items()))
 gates=''.join(f"<li data-gate='{html.escape(k)}'><b>{html.escape(k)}</b>: {html.escape(str(v.get('allowed')))}</li>" for k,v in sorted(n.items()))
 body=f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Omega CORE_READY Marker-Abnahme</title><style>body{{font-family:system-ui;background:#11131a;color:#f1f2f6;margin:0;padding:30px}}main{{max-width:1320px;margin:auto}}section{{background:#1d202b;border:1px solid #4b5268;border-radius:14px;padding:20px;margin:18px 0}}code{{word-break:break-all;color:#ddd}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #555d72;padding:8px;text-align:left}}.pass{{background:#166534;padding:7px 12px;border-radius:9px;font-weight:800;display:inline-block}}pre{{white-space:pre-wrap;word-break:break-word;max-height:480px;overflow:auto;background:#090a0f;padding:15px;border-radius:10px}}</style></head><body><main><h1>Gesamtatlas Omega · CORE_READY</h1><p id="marker-path">{html.escape(str(MARKER))}</p><p id="marker-sha"><code>{sha(MARKER)}</code></p><section><h2>Checkpoint</h2><p id="checkpoint-id">{html.escape(str(d.get('checkpoint_id')))}</p><p id="checkpoint-status" class="pass">{html.escape(str(d.get('status')))}</p><p id="scope">{html.escape(str(d.get('scope')))}</p><p id="core-hash"><code>{html.escape(str(core.get('sha256')))}</code></p></section><section><h2>Playwright- und Prüfbelege</h2><table><thead><tr><th>Beleg</th><th>Status</th><th>Checks</th><th>SHA</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section><section><h2>Claim-Gate</h2><p id="claim-core-ready">{html.escape(str(cg.get('current_core_ready_allowed')))}</p><p id="claim-mcp-ready">{html.escape(str(cg.get('current_mcp_world_ready_allowed')))}</p><p id="claim-final-ready">{html.escape(str(cg.get('current_final_scan_ready_allowed')))}</p><p id="claim-sha"><code>{html.escape(str(claim.get('sha256')))}</code></p></section><section><h2>Monsterlabor-Adapter</h2><ul id="adapter">{adapter}</ul></section><section><h2>Weitere Tore bleiben zu</h2><ul id="next-gates">{gates}</ul></section><section><h2>Wahrheitsgrenze</h2><p id="truth-boundary">{html.escape(str(d.get('truth_boundary')))}</p></section><section><h2>Rohkörper</h2><pre id="raw-json">{html.escape(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True))}</pre></section></main></body></html>'''
 return body.encode('utf-8')
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/health':
   data=json.dumps({'ok':MARKER.is_file(),'marker_path':str(MARKER),'marker_sha256':sha(MARKER) if MARKER.is_file() else None}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  if self.path=='/':
   data=page();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  self.send_response(404);self.end_headers()
 def log_message(self,fmt,*args):print('[HTTP]',fmt%args,flush=True)
if __name__=='__main__':
 print(json.dumps({'ready':True,'port':PORT,'marker':str(MARKER),'sha256':sha(MARKER)}),flush=True)
 ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
