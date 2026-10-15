#!/usr/bin/env python3
from __future__ import annotations
import html,json,os,hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
MARKER=Path(os.environ['OMEGA_MARKER_PATH']);PORT=int(os.environ.get('OMEGA_TEST_PORT','18772'))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load():return json.loads(MARKER.read_text('utf-8'))
def page()->bytes:
 d=load();ev=d['evidence'];dbs=d['databases'];g=d['claim_gate'];n=d['next_gates']
 rows=''.join(f"<tr data-evidence='{html.escape(k)}'><td>{html.escape(k)}</td><td>{html.escape(v['status'])}</td><td>{html.escape(str(v.get('checks','')))}</td><td><code>{html.escape(v['sha256'])}</code></td></tr>" for k,v in ev.items())
 dbrows=''.join(f"<tr data-db='ready'><td>{html.escape(Path(x['path']).name)}</td><td>{html.escape(x['integrity'])}</td><td>{html.escape(str(x['wal_present']))}</td><td><code>{html.escape(x['sha256'])}</code></td></tr>" for x in dbs)
 red=''.join(f"<li data-red='preserved'>{html.escape(x)}</li>" for x in d['red_evidence_preserved'])
 gates=''.join(f"<li data-gate='{html.escape(k)}'>{html.escape(k)}: {html.escape(str(v['allowed']))}</li>" for k,v in n.items())
 body=f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Omega Monsterlabor Dynamic Ready</title><style>body{{font-family:system-ui;background:#11131a;color:#eee;margin:0;padding:30px}}main{{max-width:1450px;margin:auto}}section{{background:#1d202b;border:1px solid #4c5369;border-radius:14px;padding:20px;margin:18px 0}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #596176;padding:8px;text-align:left}}code{{word-break:break-all}}.pass{{display:inline-block;background:#166534;padding:8px 13px;border-radius:9px;font-weight:900}}</style></head><body><main><h1>Gesamtatlas Omega · Monsterlabor Dynamic Ready</h1><p id="marker-path">{html.escape(str(MARKER))}</p><p id="marker-sha"><code>{sha(MARKER)}</code></p><section><p id="checkpoint-id">{html.escape(d['checkpoint_id'])}</p><p id="checkpoint-status" class="pass">{html.escape(d['status'])}</p><p id="scope">{html.escape(d['scope'])}</p><p id="core-hash"><code>{html.escape(d['core']['sha256'])}</code></p><p id="core-ready-hash"><code>{html.escape(d['core_ready']['sha256'])}</code></p></section><section><h2>Claim-Gate</h2><p id="dynamic-ready">{html.escape(str(g['monsterlabor_dynamic_ready_allowed']))}</p><p id="mcp-ready">{html.escape(str(g['mcp_world_ready_allowed']))}</p><p id="final-ready">{html.escape(str(g['final_scan_ready_allowed']))}</p></section><section><h2>Browserbelege</h2><table><tbody>{rows}</tbody></table></section><section><h2>Ergebnisbindungen</h2><p id="result-hash"><code>{html.escape(d['result']['sha256'])}</code></p><p id="evaluation-hash"><code>{html.escape(d['evaluation']['sha256'])}</code></p><p id="result-counts">{html.escape(d['result']['cases'])} · {html.escape(d['result']['searches'])}</p><p id="evaluation-counts">{html.escape(d['evaluation']['checks'])}</p></section><section><h2>SQLite</h2><table><tbody>{dbrows}</tbody></table></section><section><h2>Rote Belege</h2><ul>{red}</ul></section><section><h2>Weitere Tore geschlossen</h2><ul>{gates}</ul></section><section><p id="truth-boundary">{html.escape(d['truth_boundary'])}</p></section></main></body></html>'''
 return body.encode('utf-8')
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/health':
   data=json.dumps({'ok':MARKER.is_file(),'sha256':sha(MARKER),'path':str(MARKER)}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  if self.path=='/':
   data=page();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  self.send_response(404);self.end_headers()
 def log_message(self,fmt,*args):print('[HTTP]',fmt%args,flush=True)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
