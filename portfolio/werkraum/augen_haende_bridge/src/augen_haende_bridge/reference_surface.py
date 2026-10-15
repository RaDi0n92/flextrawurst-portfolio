"""Reference-driven visible Bridge Surface.

This is the spatial desktop overlay shell from Daniel's sketch, not a
homepage. The diagnostic proof panel remains a separate test surface.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

from .target_registry import TargetRegistry


REFERENCE_SURFACE = "surface:windows:bridge"


HTML = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Augen &amp; Hände — Bridge Surface</title>
  <style>
    :root { color-scheme: dark; font: 14px system-ui, sans-serif; }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #11161d; color: #edf4fb; }
    #surface { position: relative; width: 100vw; height: 100vh; min-width: 1100px; min-height: 700px; overflow: hidden; background:
      radial-gradient(circle at 63% 38%, rgba(51, 91, 126, .24), transparent 30%),
      linear-gradient(135deg, #17212c 0%, #0d1218 72%); }
    #surface::before { content: ""; position: absolute; inset: 0; opacity: .13; background-image: linear-gradient(#9fb9ca 1px, transparent 1px), linear-gradient(90deg, #9fb9ca 1px, transparent 1px); background-size: 32px 32px; pointer-events: none; }
    .heading { position: absolute; left: 22px; top: 15px; z-index: 20; letter-spacing: .14em; color: #b9d8ed; text-transform: uppercase; font-size: 12px; }
    .heading span { color: #6cd6ff; }
    .status { position: absolute; right: 22px; top: 15px; z-index: 20; color: #ffd479; font-size: 12px; }
    .desktop-layer { position: absolute; left: 235px; right: 30px; top: 48px; bottom: 188px; border: 1px solid rgba(125, 175, 207, .32); background: rgba(25, 37, 49, .27); box-shadow: inset 0 0 60px rgba(0,0,0,.28); }
    .desktop-label { position: absolute; top: 12px; left: 14px; color: #77a9c5; font-size: 11px; letter-spacing: .12em; }
    .desktop-mode { position: absolute; top: 12px; right: 14px; color: #90e4bd; font-size: 11px; }
    .node { position: absolute; z-index: 8; border: 1px solid rgba(144, 202, 232, .54); background: rgba(17, 28, 39, .66); box-shadow: 0 10px 26px rgba(0,0,0,.28); backdrop-filter: blur(5px); opacity: .66; user-select: none; }
    .node.selected { border-color: #ffda78; box-shadow: 0 0 0 1px #ffda78, 0 10px 26px rgba(0,0,0,.35); }
    .node-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 7px 9px; color: #bde9ff; font-size: 12px; letter-spacing: .06em; }
    .node-header small { color: #86a1b2; letter-spacing: 0; }
    .terminal { width: 315px; height: 145px; }
    .terminal.t1 { left: 32px; bottom: 24px; }
    .terminal.t2 { left: 364px; bottom: 24px; }
    .terminal.t3 { left: 696px; bottom: 24px; }
    .terminal.t4 { right: 28px; bottom: 24px; width: 280px; }
    .terminal-body { padding: 5px 10px; height: 87px; overflow: hidden; color: #b9d1df; font: 12px ui-monospace, monospace; white-space: pre-line; }
    .prompt { color: #73e0ae; }
    .scanner { position: absolute; right: 7px; bottom: 7px; }
    button, select, input { font: inherit; }
    button, select { border: 1px solid #4c7087; border-radius: 4px; color: #eef8ff; background: rgba(29, 55, 72, .82); padding: 5px 8px; cursor: pointer; }
    button:hover, select:hover { border-color: #ffda78; }
    .diamond { width: 112px; height: 112px; transform: rotate(45deg); display: grid; place-items: center; background: rgba(24, 48, 64, .72); border: 2px solid var(--agent-color); }
    .diamond .diamond-content { transform: rotate(-45deg); text-align: center; color: #f3fbff; font-weight: 650; }
    .diamond small { display: block; color: #a8bec9; font-weight: 400; margin-top: 3px; }
    .agent-codex { left: 42%; top: 24%; --agent-color: #74d7ff; }
    .agent-gemini { left: 59%; top: 28%; --agent-color: #ff9bba; }
    .agent-claude { left: 49%; top: 49%; --agent-color: #c4a7ff; }
    .agent-daniel { left: 30%; top: 39%; --agent-color: #ffda78; }
    .agent-daniel .diamond-content { color: #ffda78; }
    .regie { left: 22px; bottom: 188px; width: 190px; min-height: 178px; padding: 12px; z-index: 15; }
    .regie h2 { margin: 0 0 9px; font-size: 13px; color: #ffda78; letter-spacing: .12em; text-transform: uppercase; }
    .regie-row { display: flex; align-items: center; justify-content: space-between; gap: 6px; margin: 8px 0; color: #aac2d0; }
    .regie-row button { min-width: 75px; }
    .regie-row button.on { border-color: #73e0ae; color: #73e0ae; }
    .regie-foot { color: #7d98a9; font-size: 11px; line-height: 1.35; }
    .arrow-layer { position: absolute; inset: 0; z-index: 4; pointer-events: none; }
    .arrow-layer line { stroke: #7ca5bc; stroke-width: 1.4; opacity: .6; marker-end: url(#arrow); }
    .arrow-layer text { fill: #9fbccc; font-size: 12px; letter-spacing: .04em; }
    .scanner-menu { position: absolute; right: 8px; bottom: 38px; width: 170px; padding: 7px; z-index: 30; background: #0d1822; border: 1px solid #ffda78; display: none; }
    .scanner-menu.open { display: block; }
    .scanner-menu button { display: block; width: 100%; text-align: left; margin: 3px 0; }
    .target-rail { position: absolute; left: 22px; top: 56px; bottom: 380px; width: 190px; padding: 11px; z-index: 12; border-left: 2px solid rgba(116,215,255,.45); background: rgba(13, 24, 34, .35); }
    .target-rail h2 { margin: 0 0 8px; color: #88b9cf; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; }
    .target-item { display: block; width: 100%; margin: 5px 0; text-align: left; background: transparent; border-color: transparent; color: #aac2d0; }
    .target-item.active { border-color: #ffda78; color: #ffda78; background: rgba(255,218,120,.08); }
    .target-item small { display: block; color: #718b9b; margin-top: 2px; }
    .control-strip { position: absolute; right: 22px; top: 48px; z-index: 20; display: flex; gap: 6px; align-items: center; }
    .control-strip label { color: #89a9b8; font-size: 11px; }
    .toast { position: absolute; left: 53%; top: 38%; z-index: 35; min-width: 180px; max-width: 340px; padding: 11px 14px; border: 1px solid #ffda78; background: rgba(15, 23, 30, .89); color: #ffe9a9; opacity: 0; transform: translateY(6px); transition: opacity .2s, transform .2s; pointer-events: none; }
    .toast.show { opacity: 1; transform: translateY(0); }
    .selected-readback { position: absolute; right: 22px; bottom: 350px; width: 250px; z-index: 15; color: #9db7c7; font: 11px ui-monospace, monospace; white-space: pre-wrap; }
    @media (max-width: 1250px) { .terminal { width: 255px; } .terminal.t2 { left: 300px; } .terminal.t3 { left: 568px; } .terminal.t4 { right: 12px; width: 225px; } }
  </style>
</head>
<body>
<main id="surface" data-testid="reference-surface">
  <div class="heading">AUGEN &amp; HÄNDE <span>— BRIDGE SURFACE</span></div>
  <div class="status" data-testid="reference-status">REFERENCE_SURFACE — kein Homepage-Modus</div>
  <div class="control-strip">
    <label for="opacity">Starttransparenz</label>
    <input id="opacity" data-testid="opacity-control" type="range" min="20" max="100" value="66">
    <button data-action="reset-layout">Layout zurücksetzen</button>
  </div>
  <aside class="target-rail" data-testid="target-rail">
    <h2>Ziele / Bindungen</h2>
    <div data-testid="target-list"></div>
  </aside>
  <section class="desktop-layer" data-testid="desktop-layer">
    <div class="desktop-label">BOUND WINDOWS DESKTOP / TARGET SURFACE</div>
    <div class="desktop-mode" data-testid="desktop-mode">Windows kompletter Desktop</div>
  </section>
  <svg class="arrow-layer" viewBox="0 0 1600 1000" preserveAspectRatio="none" aria-label="beschriftete Pfeilbeziehungen">
    <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#7ca5bc"/></marker></defs>
    <line x1="320" y1="200" x2="670" y2="290"/><text x="390" y="215">sehen</text>
    <line x1="890" y1="215" x2="755" y2="350"/><text x="820" y="230">sprechen</text>
    <line x1="640" y1="465" x2="530" y2="570"/><text x="548" y="485">handeln</text>
    <line x1="1010" y1="440" x2="1200" y2="570"/><text x="1060" y="455">weitergeben</text>
  </svg>
  <div class="node diamond agent-codex" data-node-id="agent-codex" data-draggable>
    <div class="diamond-content">Codex<small>◆ Auge / Hand</small></div>
  </div>
  <div class="node diamond agent-gemini" data-node-id="agent-gemini" data-draggable>
    <div class="diamond-content">Gemini<small>◆ Auge / Hand</small></div>
  </div>
  <div class="node diamond agent-claude" data-node-id="agent-claude" data-draggable>
    <div class="diamond-content">Claude<small>◆ Auge / Hand</small></div>
  </div>
  <div class="node diamond agent-daniel" data-node-id="agent-daniel" data-draggable>
    <div class="diamond-content">Daniel<small>◆ Regie</small></div>
  </div>
  <div class="node terminal t1" data-node-id="terminal-1" data-draggable>
    <div class="node-header"><span>Terminal (1)</span><small data-target-status="terminal-1">real / inspect</small></div>
    <div class="terminal-body"><span class="prompt">bash-5.3#</span> Codex / Original-Terminal<br>Scrollback sichtbar, Eingabe getrennt</div>
    <button class="scanner" data-action="scanner" data-target-id="terminal-1">Fensterscanner</button>
    <div class="scanner-menu" data-scanner-menu="terminal-1"><button data-action="bind" data-target-id="terminal-1">Agent binden</button><button data-action="inspect" data-target-id="terminal-1">Snapshot lesen</button></div>
  </div>
  <div class="node terminal t2" data-node-id="terminal-2" data-draggable>
    <div class="node-header"><span>Terminal (2)</span><small data-target-status="terminal-2">real / inspect</small></div>
    <div class="terminal-body"><span class="prompt">bash-5.3#</span> Claude / Original-Terminal<br>individuell austauschbares Ziel</div>
    <button class="scanner" data-action="scanner" data-target-id="terminal-2">Fensterscanner</button>
    <div class="scanner-menu" data-scanner-menu="terminal-2"><button data-action="bind" data-target-id="terminal-2">Agent binden</button><button data-action="inspect" data-target-id="terminal-2">Snapshot lesen</button></div>
  </div>
  <div class="node terminal t3" data-node-id="terminal-3" data-draggable>
    <div class="node-header"><span>Terminal (3)</span><small data-target-status="terminal-3">real / inspect</small></div>
    <div class="terminal-body"><span class="prompt">bash-5.3#</span> Gemini / Original-Terminal<br>eigenes Ziel, gleiche Surface</div>
    <button class="scanner" data-action="scanner" data-target-id="terminal-3">Fensterscanner</button>
    <div class="scanner-menu" data-scanner-menu="terminal-3"><button data-action="bind" data-target-id="terminal-3">Agent binden</button><button data-action="inspect" data-target-id="terminal-3">Snapshot lesen</button></div>
  </div>
  <div class="node terminal t4" data-node-id="terminal-4" data-draggable>
    <div class="node-header"><span>Terminal (4)</span><small data-target-status="terminal-4">real / inspect</small></div>
    <div class="terminal-body"><span class="prompt">bash-5.3#</span> frei / wechselbar<br>KDE Desktop 1 / 2 über Zielrail</div>
    <button class="scanner" data-action="scanner" data-target-id="terminal-4">Fensterscanner</button>
    <div class="scanner-menu" data-scanner-menu="terminal-4"><button data-action="bind" data-target-id="terminal-4">Agent binden</button><button data-action="inspect" data-target-id="terminal-4">Snapshot lesen</button></div>
  </div>
  <section class="node regie" data-node-id="regie" data-draggable data-testid="regie-panel">
    <h2>Regie</h2>
    <select data-testid="agent-select"><option value="codex">Codex</option><option value="gemini">Gemini</option><option value="claude">Claude</option></select>
    <div class="regie-row"><span>Mikrofon</span><button data-action="mic" data-agent-id="codex">aus</button></div>
    <div class="regie-row"><span>Kamera</span><button data-action="camera" data-agent-id="codex">aus</button></div>
    <div class="regie-row"><button data-action="regie-message" data-target-id="terminal-1">Spruch senden</button></div>
    <div class="regie-foot">pro Agent schaltbar · pro Ziel sichtbar<br>Raute/Chat-Text bleibt individuell</div>
  </section>
  <pre class="selected-readback" data-testid="surface-readback">selected: win-desktop</pre>
  <div class="toast" data-testid="toast"></div>
</main>
<script>
const node = id => document.querySelector(`[data-node-id="${id}"]`);
async function getState() { return fetch('/api/state').then(r => r.json()); }
function showToast(value) { const t = document.querySelector('[data-testid="toast"]'); t.textContent = value; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 3300); }
function render(data) {
  document.querySelector('[data-testid="desktop-mode"]').textContent = data.selected_target.label;
  document.querySelector('[data-testid="surface-readback"]').textContent = JSON.stringify({selected_target: data.selected_target, last_action: data.last_action, agents: data.agents}, null, 2);
  const list = document.querySelector('[data-testid="target-list"]'); list.replaceChildren();
  for (const target of data.targets) {
    const b = document.createElement('button'); b.className = 'target-item' + (target.id === data.selected_target.id ? ' active' : ''); b.dataset.action = 'select-target'; b.dataset.targetId = target.id;
    b.innerHTML = `${target.label}<small>${target.source} · ${target.availability}</small>`; list.appendChild(b);
  }
  for (const [agent, controls] of Object.entries(data.agents)) {
    for (const [kind, enabled] of Object.entries(controls)) {
      const b = document.querySelector(`[data-action="${kind}"][data-agent-id="${agent}"]`); if (b) { b.textContent = enabled ? 'an' : 'aus'; b.classList.toggle('on', enabled); }
    }
  }
  for (const [id, opacity] of Object.entries(data.opacity)) { const el = node(id); if (el) el.style.opacity = opacity; }
}
async function action(name, extra={}) { const r = await fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({action:name, ...extra})}); const data = await r.json(); render(data.state); if (data.result?.message) showToast(data.result.message); }
document.addEventListener('click', e => {
  const b = e.target.closest('[data-action]'); if (!b) return;
  const a = b.dataset.action;
  if (a === 'scanner') { document.querySelector(`[data-scanner-menu="${b.dataset.targetId}"]`).classList.toggle('open'); return; }
  action(a, {target_id:b.dataset.targetId, agent_id:b.dataset.agentId});
});
document.querySelector('[data-testid="opacity-control"]').addEventListener('input', e => {
  const selected = document.querySelector('.node.selected')?.dataset.nodeId || 'regie'; action('set-opacity', {node_id:selected, opacity:Number(e.target.value)/100});
});
document.querySelector('[data-testid="agent-select"]').addEventListener('change', e => showToast(`Regie-Fokus: ${e.target.value}`));
for (const el of document.querySelectorAll('[data-draggable]')) {
  let dragging = false, ox = 0, oy = 0;
  el.addEventListener('pointerdown', e => { if (e.target.closest('button,select,input')) return; dragging=true; el.setPointerCapture(e.pointerId); ox=e.clientX-el.offsetLeft; oy=e.clientY-el.offsetTop; el.classList.add('selected'); });
  el.addEventListener('pointermove', e => { if (!dragging) return; el.style.left=`${e.clientX-ox}px`; el.style.top=`${e.clientY-oy}px`; el.style.bottom='auto'; });
  el.addEventListener('pointerup', () => { if (!dragging) return; dragging=false; action('move-node',{node_id:el.dataset.nodeId,x:el.offsetLeft,y:el.offsetTop}); });
}
getState().then(render);
</script>
</body>
</html>"""


class ReferenceRuntime:
    def __init__(self) -> None:
        registry = TargetRegistry()
        self.targets = [record.to_dict() for record in registry.records.values()]
        self.selected_target_id = "win-desktop"
        self.opacity = {"regie": .66, "agent-codex": .66, "agent-gemini": .66, "agent-claude": .66, "agent-daniel": .66, "terminal-1": .66, "terminal-2": .66, "terminal-3": .66, "terminal-4": .66}
        self.agents = {"codex": {"mic": False, "camera": False}, "gemini": {"mic": False, "camera": False}, "claude": {"mic": False, "camera": False}}
        self.last_action: dict[str, object] = {"action": "surface.ready", "message": "Referenz-Surface bereit"}

    def state(self) -> dict[str, object]:
        selected = next(target for target in self.targets if target["id"] == self.selected_target_id)
        return {"surface_id": REFERENCE_SURFACE, "targets": self.targets, "selected_target": selected, "opacity": self.opacity, "agents": self.agents, "last_action": self.last_action}

    def action(self, name: str, payload: dict[str, object]) -> dict[str, object]:
        if name == "select-target":
            target_id = str(payload.get("target_id"))
            if not any(target["id"] == target_id for target in self.targets): raise ValueError("unknown target")
            self.selected_target_id = target_id
            self.last_action = {"action": name, "target_id": target_id, "message": f"Ziel gebunden: {target_id}"}
        elif name in {"mic", "camera"}:
            agent_id = str(payload.get("agent_id")); self.agents[agent_id][name] = not self.agents[agent_id][name]
            self.last_action = {"action": name, "agent_id": agent_id, "enabled": self.agents[agent_id][name], "message": f"{name} für {agent_id}: {'an' if self.agents[agent_id][name] else 'aus'}"}
        elif name == "set-opacity":
            node_id = str(payload.get("node_id")); value = max(.2, min(1.0, float(payload.get("opacity", .66)))); self.opacity[node_id] = value
            self.last_action = {"action": name, "node_id": node_id, "opacity": value, "message": f"Transparenz {node_id}: {round(value * 100)}%"}
        elif name == "move-node":
            self.last_action = {"action": name, "node_id": str(payload.get("node_id")), "x": payload.get("x"), "y": payload.get("y"), "message": "Position sichtbar übernommen"}
        elif name == "reset-layout":
            self.opacity = {key: .66 for key in self.opacity}; self.last_action = {"action": name, "message": "Referenzlayout zurückgesetzt"}
        elif name == "bind":
            self.last_action = {"action": name, "target_id": payload.get("target_id"), "message": "Agentenbindung geöffnet — Auswahl bleibt individuell"}
        elif name == "inspect":
            self.last_action = {"action": name, "target_id": payload.get("target_id"), "message": "Snapshot-Anzeige angefordert"}
        elif name == "regie-message":
            self.last_action = {"action": name, "target_id": payload.get("target_id"), "message": "Regiespruch erscheint zielgebunden"}
        else:
            raise ValueError(f"unknown action: {name}")
        return self.last_action


def make_server(runtime: ReferenceRuntime | None = None) -> tuple[ThreadingHTTPServer, ReferenceRuntime]:
    runtime = runtime or ReferenceRuntime()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def send_json(self, payload: dict[str, object], status: int = 200) -> None:
            encoded = json.dumps(payload).encode("utf-8"); self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(encoded))); self.end_headers(); self.wfile.write(encoded)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/":
                encoded = HTML.encode("utf-8"); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(encoded))); self.end_headers(); self.wfile.write(encoded); return
            if self.path == "/api/state": self.send_json(runtime.state()); return
            self.send_json({"error": "not_found"}, 404)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/action": self.send_json({"error": "not_found"}, 404); return
            length = int(self.headers.get("Content-Length", "0")); payload = json.loads(self.rfile.read(length) or b"{}")
            try: result = runtime.action(str(payload["action"]), payload)
            except (KeyError, ValueError, TypeError) as exc: self.send_json({"error": str(exc), "state": runtime.state()}, 400); return
            self.send_json({"result": result, "state": runtime.state()})

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler), runtime


def start_server(runtime: ReferenceRuntime | None = None) -> tuple[ThreadingHTTPServer, ReferenceRuntime]:
    server, runtime = make_server(runtime); Thread(target=server.serve_forever, name="augen-haende-reference-surface", daemon=True).start(); return server, runtime


if __name__ == "__main__":
    server, _runtime = make_server(); print(f"http://127.0.0.1:{server.server_port}", flush=True); server.serve_forever()
