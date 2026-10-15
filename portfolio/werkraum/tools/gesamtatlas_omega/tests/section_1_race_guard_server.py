#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROBE = Path('/root/werkraum/tools/gesamtatlas_omega/tests/section_1_race_guard_probe.py')


def load_probe():
    spec = importlib.util.spec_from_file_location('omega_section1_probe', PROBE)
    if not spec or not spec.loader:
        raise RuntimeError(f'cannot load {PROBE}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PAGE = '''<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Omega Race Guard</title>
<style>body{font:16px/1.45 system-ui;background:#111;color:#eee;max-width:1000px;margin:40px auto;padding:0 24px}button{font-size:18px;padding:12px 18px}pre{white-space:pre-wrap;background:#1d1d1d;padding:18px;border-radius:10px;max-height:620px;overflow:auto}#status[data-state="PASS"]{color:#8f8}#status[data-state="FAIL"]{color:#f88}</style></head><body>
<h1>Omega Bauabschnitt 1: Race Guard</h1><p>Chromium löst den echten Scan aus und verändert die Quelle nach dem ersten Chunk.</p>
<button id="run">Race-Scan ausführen</button><h2 id="status" data-state="IDLE">IDLE</h2><pre id="result"></pre>
<script>const runButton=document.getElementById('run');const statusElement=document.getElementById('status');const resultElement=document.getElementById('result');runButton.addEventListener('click',async()=>{runButton.disabled=true;statusElement.textContent='RUNNING';statusElement.dataset.state='RUNNING';try{const response=await fetch('/run',{method:'POST'});const data=await response.json();resultElement.textContent=JSON.stringify(data,null,2);statusElement.textContent=data.ok?'PASS':'FAIL';statusElement.dataset.state=data.ok?'PASS':'FAIL';}catch(error){resultElement.textContent=String(error);statusElement.textContent='FAIL';statusElement.dataset.state='FAIL';}finally{runButton.disabled=false;}});</script>
</body></html>'''


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, content_type: str, code: int = 200) -> None:
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            self.send_bytes(PAGE.encode('utf-8'), 'text/html; charset=utf-8')
            return
        if self.path == '/health':
            body = json.dumps({'ok': True, 'probe': str(PROBE)}).encode('utf-8')
            self.send_bytes(body, 'application/json; charset=utf-8')
            return
        self.send_bytes(b'not found', 'text/plain; charset=utf-8', 404)

    def do_POST(self):
        if self.path != '/run':
            self.send_bytes(b'not found', 'text/plain; charset=utf-8', 404)
            return
        try:
            result = load_probe().main()
            body = json.dumps(result, ensure_ascii=False).encode('utf-8')
            self.send_bytes(body, 'application/json; charset=utf-8')
        except Exception as exc:
            body = json.dumps({'ok': False, 'error': repr(exc)}, ensure_ascii=False).encode('utf-8')
            self.send_bytes(body, 'application/json; charset=utf-8', 500)

    def log_message(self, fmt, *args):
        print('[HTTP]', fmt % args, flush=True)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    print(json.dumps({'ready': True, 'host': '127.0.0.1', 'port': server.server_address[1]}), flush=True)
    server.serve_forever()
