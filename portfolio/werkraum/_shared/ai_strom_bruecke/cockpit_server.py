#!/usr/bin/env python3
"""Loopback cockpit for frames, claims, actions and the visible heartbeat."""

from __future__ import annotations

import argparse
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .anchors import AnchorStore
from .network_guard import runtime_status
from .object_store import TriViewObjectStore
from .inventory import build_inventory
from .requirements import summary as requirements_summary
from .world_flow import WorldFlow


HTML = r"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-Strom-Brücke · Realtime-Cockpit</title>
<style>
:root{color-scheme:dark;--bg:#101318;--panel:#191e27;--line:#303948;--ok:#55d98a;--warn:#f0c674;--bad:#f07178}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#e8edf5;font:14px system-ui,sans-serif}
header{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;gap:18px;align-items:center}
h1{font-size:18px;margin:0}.badge{padding:3px 8px;border-radius:12px;background:#293242}.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}
main{display:grid;grid-template-columns:minmax(480px,2fr) minmax(360px,1fr);gap:12px;padding:12px}
section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px;min-width:0}
section h2{font-size:14px;margin:0 0 8px;color:#aebbd0}.frame-wrap{position:relative;background:#050609;min-height:280px;display:grid;place-items:center;overflow:hidden}
#frame{max-width:100%;max-height:62vh;object-fit:contain}.crosshair{position:absolute;width:24px;height:24px;border:1px solid #ff6b6b;transform:translate(-50%,-50%);pointer-events:none;display:none}.crosshair:after,.crosshair:before{content:"";position:absolute;background:#ff6b6b}.crosshair:after{width:34px;height:1px;left:-6px;top:11px}.crosshair:before{height:34px;width:1px;left:11px;top:-6px}
dl{display:grid;grid-template-columns:145px 1fr;gap:4px;margin:0}dt{color:#8d9ab0}dd{margin:0;overflow-wrap:anywhere}.mono{font-family:ui-monospace,monospace;font-size:12px}
#timeline{max-height:210px;overflow:auto}.row{padding:5px 0;border-bottom:1px solid #252c37}.row:last-child{border:0}.small{font-size:12px;color:#9ba8ba}
pre{white-space:pre-wrap;margin:0;max-height:260px;overflow:auto}.grid{display:grid;gap:10px}.wide{grid-column:1/-1}
#humanStage{min-height:150px;position:relative;display:flex;gap:18px;align-items:center;justify-content:center;perspective:700px;background:radial-gradient(circle at 50% 45%,#263957,#0b0e14);overflow:hidden}
#humanCanvas{position:absolute;inset:0;width:100%;height:100%;opacity:.48;pointer-events:none}
#humanObjects{position:relative;z-index:1;display:flex;gap:18px;align-items:center;justify-content:center;width:100%;min-height:150px}
.surface-object{width:120px;height:90px;padding:12px;border:1px solid #75d7ff;border-radius:18px;background:linear-gradient(145deg,#384f79,#151c2b);box-shadow:0 0 22px #4ab6e966;text-align:center;cursor:pointer}
.surface-motion{height:100%;transform-style:preserve-3d;animation:surfacePulse 1.2s ease-in-out infinite alternate}
.surface-object[data-motion="lebt"]{border-color:#55d98a;box-shadow:0 0 30px #55d98a88}.surface-object small{display:block;color:#aebbd0;margin-top:8px}
@keyframes surfacePulse{from{transform:rotateX(8deg) rotateY(-8deg) translateZ(0) scale(.96)}to{transform:rotateX(-8deg) rotateY(8deg) translateZ(26px) scale(1.04)}}
@media(max-width:900px){main{grid-template-columns:1fr}}
</style></head>
<body>
<header><h1>AI-Strom-Brücke · Realtime-Cockpit</h1><span id="gate" class="badge">Gate unbekannt</span><span id="heartbeat" class="small">Heartbeat wartet</span></header>
<main>
<section><h2>aktueller Frame / Analyseoverlay</h2><div class="frame-wrap"><img id="frame" alt="aktueller Bridge-Frame"><div id="crosshair" class="crosshair"></div></div><div id="frameMeta" class="small">kein Frame</div></section>
<section class="grid"><div><h2>Kamera / Koordinaten</h2><dl id="camera"><dt>Status</dt><dd>warte</dd></dl></div><div><h2>Aktion</h2><pre id="action">keine Aktion</pre></div><div><h2>Provenienz / Gate</h2><pre id="provenance">warte</pre></div></section>
<section><h2>Frame-Zeitstrahl 30–60 s</h2><div id="timeline" class="mono">warte</div></section>
<section><h2>Dreileibige Objekte</h2><div id="objects" class="mono">warte</div></section>
<section><h2>Menschen-Leib / Organ-Leib</h2><div id="surface" class="mono" data-surface="human-organ">warte</div></section>
<section class="wide"><h2>Räumliche Menschenfläche aus derselben Objektwahrheit</h2><div id="humanStage" data-human-stage="3d-surface"><canvas id="humanCanvas" data-human-webgl="pending" aria-label="WebGL-Menschenfläche"></canvas><div id="humanObjects"></div></div><div id="renderReport" data-render-report="live" data-target-status="unmeasured" class="small">Rendermessung wartet</div></section>
<section><h2>Bestätigte Anker</h2><div id="anchors" class="mono">warte</div></section>
<section><h2>Kausaler Dreierregen</h2><div id="worldEvents" class="mono">warte</div></section>
<section><h2>Bauauftrag / Testfortschritt</h2><div id="requirements" class="mono" data-requirements="tracking">warte</div></section>
<section><h2>sichtbare kurze Entscheidungszusammenfassung</h2><pre id="decision">warte auf strukturierte Zustandszeile</pre></section>
<section class="wide"><h2>Ereignisstrom</h2><pre id="events" class="mono">warte</pre></section>
</main>
<script>
const $=id=>document.getElementById(id); let state={}; let surfaceTicks=0; let surfaceObjectKey=''; let webglState={available:false,mode:'pending',frames:0,first_frame_at:0,last_frame_at:0};
function text(v){return v===null||v===undefined?'—':String(v)}
function paintHumanSurface(objects){const nextKey=objects.map(x=>`${x.object_id}:${x.version}`).join('|'); if(nextKey===surfaceObjectKey)return; surfaceObjectKey=nextKey; $('humanObjects').innerHTML=objects.map(x=>{const h=x.menschen_leib||{}; return `<div class="surface-object" data-render-object="${text(x.object_id)}" data-motion="${text(h.motion)}"><div class="surface-motion"><b>${text(h.scene)}</b><small>${text(h.depth)} · ${text(h.motion)}</small></div></div>`}).join('')||'<span>keine kanonischen Objekte</span>'; objects.forEach(x=>{const node=document.querySelector(`[data-render-object="${x.object_id}"]`); if(node) node.onclick=()=>fetch('/api/reactions',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({object_id:x.object_id,human_effect:{scene:'Mensch reagiert',interaction:['gesehen']},organ_effect:{resonance_effect:{human_reaction:true}}})});});}
function setupHumanWebGL(){const canvas=$('humanCanvas'); if(!canvas)return; const gl=canvas.getContext('webgl',{antialias:true,alpha:true})||canvas.getContext('experimental-webgl'); if(!gl){webglState.mode='fallback-css-3d'; canvas.dataset.humanWebgl='unavailable'; return;} const vertex=gl.createShader(gl.VERTEX_SHADER); gl.shaderSource(vertex,'attribute vec2 p; uniform float t; void main(){float s=0.82+0.06*sin(t); gl_Position=vec4(p*s,0.0,1.0);}'); gl.compileShader(vertex); const fragment=gl.createShader(gl.FRAGMENT_SHADER); gl.shaderSource(fragment,'precision mediump float; uniform float t; void main(){gl_FragColor=vec4(0.16+0.04*sin(t),0.42+0.08*cos(t),0.72,0.34);}'); gl.compileShader(fragment); if(!gl.getShaderParameter(vertex,gl.COMPILE_STATUS)||!gl.getShaderParameter(fragment,gl.COMPILE_STATUS)){webglState.mode='fallback-css-3d'; canvas.dataset.humanWebgl='compile-fallback'; return;} const program=gl.createProgram(); gl.attachShader(program,vertex); gl.attachShader(program,fragment); gl.linkProgram(program); if(!gl.getProgramParameter(program,gl.LINK_STATUS)){webglState.mode='fallback-css-3d'; canvas.dataset.humanWebgl='link-fallback'; return;} const buffer=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW); const position=gl.getAttribLocation(program,'p'); const clock=gl.getUniformLocation(program,'t'); webglState={available:true,mode:'webgl',frames:0}; canvas.dataset.humanWebgl='available'; function loop(now){const dpr=Math.min(window.devicePixelRatio||1,2); const width=Math.max(1,Math.floor(canvas.clientWidth*dpr)); const height=Math.max(1,Math.floor(canvas.clientHeight*dpr)); if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;} gl.viewport(0,0,width,height); gl.clearColor(0.02,0.05,0.1,0); gl.clear(gl.COLOR_BUFFER_BIT); gl.useProgram(program); gl.bindBuffer(gl.ARRAY_BUFFER,buffer); gl.enableVertexAttribArray(position); gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0); gl.uniform1f(clock,now/1000); gl.drawArrays(gl.TRIANGLE_STRIP,0,4); webglState.frames++; requestAnimationFrame(loop);} requestAnimationFrame(loop);}
function repairHumanWebGL(){const canvas=$('humanCanvas'); const gl=canvas&&(canvas.getContext('webgl')||canvas.getContext('experimental-webgl')); if(!gl)return; const vertex=gl.createShader(gl.VERTEX_SHADER); gl.shaderSource(vertex,'precision highp float; attribute vec2 p; uniform float t; void main(){float s=0.82+0.06*sin(t); gl_Position=vec4(p*s,0.0,1.0);}'); gl.compileShader(vertex); const fragment=gl.createShader(gl.FRAGMENT_SHADER); gl.shaderSource(fragment,'precision highp float; uniform float t; void main(){gl_FragColor=vec4(0.16+0.04*sin(t),0.42+0.08*cos(t),0.72,0.34);}'); gl.compileShader(fragment); if(!gl.getShaderParameter(vertex,gl.COMPILE_STATUS)||!gl.getShaderParameter(fragment,gl.COMPILE_STATUS))return; const program=gl.createProgram(); gl.attachShader(program,vertex); gl.attachShader(program,fragment); gl.linkProgram(program); if(!gl.getProgramParameter(program,gl.LINK_STATUS))return; const buffer=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW); const position=gl.getAttribLocation(program,'p'); const clock=gl.getUniformLocation(program,'t'); webglState={available:true,mode:'webgl',frames:0}; canvas.dataset.humanWebgl='available'; function loop(now){const dpr=Math.min(window.devicePixelRatio||1,2); const width=Math.max(1,Math.floor(canvas.clientWidth*dpr)); const height=Math.max(1,Math.floor(canvas.clientHeight*dpr)); if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;} gl.viewport(0,0,width,height); gl.clearColor(0.02,0.05,0.1,0); gl.clear(gl.COLOR_BUFFER_BIT); gl.useProgram(program); gl.bindBuffer(gl.ARRAY_BUFFER,buffer); gl.enableVertexAttribArray(position); gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0); gl.uniform1f(clock,now/1000); gl.drawArrays(gl.TRIANGLE_STRIP,0,4); webglState.frames++; requestAnimationFrame(loop);} requestAnimationFrame(loop);}
let renderMeasurement={last_frames:0,last_at:performance.now(),fps:null}; setInterval(()=>{const now=performance.now(); const elapsed=now-renderMeasurement.last_at; if(elapsed>0){renderMeasurement.fps=(webglState.frames-renderMeasurement.last_frames)*1000/elapsed; renderMeasurement.last_frames=webglState.frames; renderMeasurement.last_at=now;}},250);
window.__humanSurfaceMetrics=()=>{const canvas=$('humanCanvas'); const width=canvas?.width||0; const height=canvas?.height||0; const fps=renderMeasurement.fps; const targetMet=width>=7680&&height>=4320&&fps!==null&&fps>=66; const targetStatus=fps===null?'unmeasured':(targetMet?'verified':'measured-below-target'); const report=$('renderReport'); if(report){report.dataset.targetStatus=targetStatus; report.textContent=`Canvas ${width}×${height} · RAF ${fps===null?'—':fps.toFixed(1)} FPS · Ziel 7680×4320 / 66 FPS · ${targetStatus}`;} return {ticks:surfaceTicks,target_fps:66,target_resolution:'8K',claim:'measured-render-loop-only',webgl:webglState.available,webgl_mode:webglState.mode,webgl_frames:webglState.frames,canvas_width:width,canvas_height:height,observed_fps:fps,target_met:targetMet,target_status:targetStatus};};
function surfaceLoop(){surfaceTicks++; requestAnimationFrame(surfaceLoop)} setupHumanWebGL(); if(webglState.mode==='fallback-css-3d') repairHumanWebGL(); surfaceLoop();
function setFrame(st){if(!st.frame_url)return; const url=(st.analysis_overlay_url||st.frame_url)+'?sequence='+(st.frame_sequence||Date.now()); $('frame').src=url; $('frameMeta').textContent=`seq ${text(st.frame_sequence)} · Alter ${text(st.frame_age_ms)} ms · ${text(st.frame_width)}×${text(st.frame_height)} · ${text(st.frame_digest)} · Overlay ${st.analysis_overlay_url?'aktiv':'—'}`;}
function render(st){state=st; const gate=st.gate||{}; $('gate').textContent=gate.allow_input?'GATE OFFEN':'GATE GESCHLOSSEN: '+text(gate.reason); $('gate').className='badge '+(gate.allow_input?'ok':'bad'); $('heartbeat').textContent='Heartbeat '+new Date().toLocaleTimeString()+' · '+text(st.phase||'observe'); setFrame(st);
 const c=st.camera||{}; $('camera').innerHTML=`<dt>Target</dt><dd>${text(st.target)}</dd><dt>Pointer</dt><dd>${text(JSON.stringify(c.pointer_xy||c.pointer_anchor||null))}</dd><dt>Koordinate</dt><dd>${text(c.coordinate||c.pointer_anchor?.normalized_text)}</dd><dt>Zoom/Sicht</dt><dd>${text(c.zoom)} / ${text(c.eye_altitude_m)}</dd><dt>Fokus</dt><dd>${c.focus?'ja':'nein'}</dd><dt>Popup</dt><dd>${text(c.popup)}</dd>`;
 $('action').textContent=JSON.stringify(st.action||{},null,2); $('provenance').textContent=JSON.stringify({gate,source:st.source,frame_id:st.frame_id,claims:st.claims||[]},null,2); $('decision').textContent=st.decision_summary||'keine neue Entscheidung';
 const rows=st.timeline||[]; $('timeline').innerHTML=rows.slice().reverse().map(x=>`<div class="row">${text(x.sequence)} · ${text(x.frame_id)} · ${text(x.freshness)} · ${text(x.width)}×${text(x.height)} · ${text(x.age_ms)} ms</div>`).join('')||'keine Frames';
 const objects=st.objects||[]; $('objects').innerHTML=objects.map(x=>`<div class="row" data-object-id="${text(x.object_id)}"><b>${text(x.object_id)}</b> · ${text(x.object_type)} · v${text(x.version)}<br>Leiber: ${x.codewesen_leib?'Code':'—'} / ${x.menschen_leib?'Mensch':'—'} / ${x.organ_leib?'Organ':'—'} · Rot ${text((x.rot_block||[]).length)}</div>`).join('')||'keine Objekte';
 paintHumanSurface(objects);
 $('surface').innerHTML=objects.map(x=>`<div class="row" data-human-surface="${text(x.object_id)}"><b>${text(x.menschen_leib?.scene)}</b> · Bewegung ${text(x.menschen_leib?.motion)} · Tiefe ${text(x.menschen_leib?.depth)}<br>Render ${text(JSON.stringify(x.menschen_leib?.render_metrics||{}))}<br>Organwirkung ${text(JSON.stringify(x.organ_leib||{}))}</div>`).join('')||'keine Menschen-/Organ-Leiber';
 $('anchors').innerHTML=(st.anchors||[]).map(x=>`<div class="row" data-anchor-id="${text(x.anchor_id)}"><b>${text(x.label)}</b> · ${text(x.claim?.normalized_text)} · Frame ${text(x.frame_id)}</div>`).join('')||'keine bestätigten Anker';
 $('worldEvents').innerHTML=(st.world_events||[]).slice().reverse().map(x=>`<div class="row" data-world-event-id="${text(x.event_id)}"><b>${text(x.source)}</b> · Objekt ${text(x.object_id)} · ${text(x.before_state?.version)} → ${text(x.after_state?.version)}<br>Code frisch ${text(x.codewesen_effect?.fresh_capsule)} · Mensch ${text(JSON.stringify(x.human_effect))} · Organ ${text(JSON.stringify(x.organ_effect))}</div>`).join('')||'keine kausalen Ereignisse';
 $('requirements').innerHTML=`<b>${text(st.requirements?.verified)} / ${text(st.requirements?.total)} verifiziert</b> · offen ${text(st.requirements?.open)} · Endabnahme ${text(st.requirements?.end_abnahme)}`; }
async function refresh(){try{const r=await fetch('/state',{cache:'no-store'}); if(r.ok)render(await r.json())}catch(e){$('heartbeat').textContent='Cockpit-Fehler: '+e}}
let heartbeatCount=0; window.__bridgeHeartbeatCount=()=>heartbeatCount;
const es=new EventSource('/state-stream'); es.onmessage=e=>{try{heartbeatCount++; render(JSON.parse(e.data))}catch{}}; es.onerror=()=>{ $('heartbeat').textContent='State-Stream unterbrochen; reconnect läuft'};
const ev=new EventSource('/events'); ev.onmessage=e=>{const line=e.data; $('events').textContent=(line+'\n'+$('events').textContent).slice(0,12000)};
refresh(); setInterval(refresh,1000);
</script></body></html>"""


class CockpitHandler(BaseHTTPRequestHandler):
    server_version = "AI-Strom-Bruecke-Cockpit/1.0"

    def log_message(self, *_args):
        return

    @property
    def config(self):
        return self.server.cockpit_config

    def _json(self, value: object, status: int = 200) -> None:
        data = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _state(self) -> dict:
        path: Path = self.config["state"]
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            value = {"schema": "ai-strom-bruecke.cockpit-state.v1", "phase": "starting"}
        self.server.heartbeat_sequence = getattr(self.server, "heartbeat_sequence", 0) + 1
        value["heartbeat_sequence"] = self.server.heartbeat_sequence
        value["heartbeat_at"] = time.time()
        frame: Path = self.config["frame"]
        if frame.exists():
            stat = frame.stat()
            value.update({
                "frame_url": "/latest.png",
                "frame_sequence": value.get("frame_sequence", value.get("last_frame_sequence")),
                "frame_age_ms": round(max(0, time.time() - stat.st_mtime) * 1000, 1),
                "frame_width": value.get("frame_width"),
                "frame_height": value.get("frame_height"),
            })
        timeline_path: Path = self.config["timeline"]
        if timeline_path.exists():
            try:
                value["timeline"] = json.loads(timeline_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                value["timeline"] = []
        objects_path: Path = self.config["objects"]
        value["objects"] = []
        if objects_path.exists():
            try:
                objects = {}
                for line in objects_path.read_text(encoding="utf-8").splitlines():
                    event = json.loads(line)
                    obj = event.get("object")
                    if isinstance(obj, dict) and obj.get("object_id"):
                        objects[obj["object_id"]] = obj
                value["objects"] = list(objects.values())
            except (OSError, json.JSONDecodeError):
                value["objects"] = []
        value["anchors"] = self._read_jsonl_objects(self.config["anchors"], "anchor")
        value["world_events"] = self._read_jsonl_objects(self.config["world_events"], "event")
        try:
            gate = json.loads(self.config["gate"].read_text(encoding="utf-8"))
            if isinstance(gate, dict):
                value["gate"] = gate
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        try:
            vision = json.loads(self.config["vision_state"].read_text(encoding="utf-8"))
            if isinstance(vision, dict):
                value["vision"] = vision
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        value["requirements"] = requirements_summary()
        value["inventory"] = build_inventory(Path(__file__).resolve().parent)
        value["runtime"] = runtime_status()
        value.setdefault("render_metrics", {"mode": "dom-derived", "fps": None, "resolution": None, "target_fps": 66, "target_resolution": "8K", "target_status": "planned"})
        return value

    @staticmethod
    def _read_jsonl_objects(path: Path, key: str) -> list[dict]:
        result = []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return result
        for line in lines:
            try:
                value = json.loads(line).get(key)
            except (json.JSONDecodeError, AttributeError):
                continue
            if isinstance(value, dict):
                result.append(value)
        return result

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("request body too large")
        raw = self.rfile.read(length) if length else b"{}"
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def _created_json(self, value: object, status: int = 201) -> None:
        self._json(value, status=status)

    def do_POST(self):  # noqa: N802
        route = urlparse(self.path).path
        try:
            body = self._body()
            objects = TriViewObjectStore(self.config["objects"])
            flow = WorldFlow(objects, self.config["world_events"])
            if route == "/api/objects":
                obj, event = flow.create(body)
                self._created_json({"object": obj, "event": event})
                return
            if route.startswith("/api/objects/") and route.endswith("/apply"):
                object_id = route[len("/api/objects/"):-len("/apply")]
                obj, event = flow.apply(object_id, source=str(body.get("source", "world.apply")), action_id=body.get("action_id"), human_effect=body.get("human_effect"), organ_effect=body.get("organ_effect"))
                self._created_json({"object": obj, "event": event})
                return
            if route == "/api/reactions":
                obj, event = flow.apply(str(body["object_id"]), source="human.reaction", human_effect=body.get("human_effect", {"interaction": ["human-reaction"]}), organ_effect=body.get("organ_effect", {"resonance_effect": {"new_reaction": True}}))
                self._created_json({"object": obj, "event": event})
                return
            if route == "/api/anchors":
                anchor = AnchorStore(self.config["anchors"]).create(label=str(body["label"]), claim=body["claim"], camera=body["camera"], frame_id=str(body["frame_id"]), frame_digest=str(body["frame_digest"]), frame_path=body.get("frame_path"), provenance=body.get("provenance", []))
                self._created_json({"anchor": anchor})
                return
            self._json({"error": "unknown POST route"}, status=404)
        except (KeyError, ValueError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, status=400)

    def do_GET(self):  # noqa: N802
        route = urlparse(self.path).path
        if route == "/":
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif route in {"/health", "/state"}:
            state = self._state()
            if route == "/health":
                self._json({"ok": True, "schema": "ai-strom-bruecke.cockpit-health.v1", "state": state})
            else:
                self._json(state)
        elif route == "/latest.png":
            self._file(self.config["frame"], "image/png")
        elif route == "/analysis-overlay.png":
            self._file(self.config["overlay"], "image/png")
        elif route == "/state-stream":
            self._stream_state()
        elif route == "/events":
            self._stream_events()
        elif route == "/timeline":
            self._json(self._state().get("timeline", []))
        elif route == "/objects":
            self._json(self._state().get("objects", []))
        elif route == "/anchors":
            self._json(self._state().get("anchors", []))
        elif route == "/world-events":
            self._json(self._state().get("world_events", []))
        elif route == "/metrics":
            self._json(self._state().get("render_metrics", {}))
        elif route == "/requirements":
            self._json(self._state().get("requirements", {}))
        elif route == "/inventory":
            self._json(self._state().get("inventory", {}))
        else:
            self.send_error(404, "Use /, /health, /state, /state-stream, /events, /timeline, /objects, /anchors, /world-events, /analysis-overlay.png or /latest.png")

    def _file(self, path: Path, content_type: str) -> None:
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            self.send_error(503, "Ressource noch nicht vorhanden")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _stream_state(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last = None
        try:
            while True:
                state = self._state()
                serialized = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
                marker = (
                    state.get("heartbeat_sequence"), state.get("frame_sequence"),
                    state.get("last_event"), state.get("phase"), state.get("gate"),
                )
                if marker != last:
                    self.wfile.write(b"data: " + serialized.encode() + b"\n\n")
                    self.wfile.flush()
                    last = marker
                time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return

    def _stream_events(self) -> None:
        ledger: Path = self.config["ledger"]
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        position = 0
        try:
            while True:
                if ledger.exists():
                    with ledger.open(encoding="utf-8") as stream:
                        stream.seek(position)
                        for line in stream:
                            self.wfile.write(b"data: " + line.rstrip().encode() + b"\n\n")
                            self.wfile.flush()
                        position = stream.tell()
                time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-Strom-Brücke loopback cockpit")
    root = Path(__file__).resolve().parent
    parser.add_argument("--bind", default=os.environ.get("AI_STROM_BRUECKE_COCKPIT_BIND", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("AI_STROM_BRUECKE_COCKPIT_PORT", "8100")))
    parser.add_argument("--state", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_STATE", root / "state.json")))
    parser.add_argument("--frame", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_FRAME", root / "latest.png")))
    parser.add_argument("--overlay", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_OVERLAY", root / "analysis-overlay.png")))
    parser.add_argument("--ledger", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_LEDGER", root / "events.jsonl")))
    parser.add_argument("--timeline", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_TIMELINE", root / "timeline.json")))
    parser.add_argument("--objects", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_OBJECTS", root / "objects.jsonl")))
    parser.add_argument("--anchors", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_ANCHORS", root / "anchors.jsonl")))
    parser.add_argument("--world-events", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_WORLD_EVENTS", root / "world_events.jsonl")))
    parser.add_argument("--gate", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_GATE", "/tmp/ai-strom-bruecke-input-gate.json")))
    parser.add_argument("--vision-state", type=Path, default=Path(os.environ.get("AI_STROM_BRUECKE_COCKPIT_VISION_STATE", root / "vision_state.json")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.bind, args.port), CockpitHandler)
    server.daemon_threads = True
    server.cockpit_config = vars(args)
    print(f"AI-Strom-Brücke Cockpit auf http://{args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
