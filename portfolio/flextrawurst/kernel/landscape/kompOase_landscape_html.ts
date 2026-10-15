// Ring 22M — KompOase-Vorform: zoombare Landschaftskarte
// Terrain: Sinuswellen-Überlagerung (deterministisch)
// Kein fetch, kein WebSocket, keine externen Libraries

const WW = 3200; // world width
const WH = 2200; // world height

// ── Terrain ───────────────────────────────────────────────────────────────────

interface Wave { A: number; f: number; p: number }

function terrainH(x: number, waves: Wave[]): number {
  return waves.reduce((s, w) => s + w.A * Math.abs(Math.sin(x * w.f + w.p)), 0);
}

function terrainPath(base: number, waves: Wave[], clamp = 60): string {
  let d = `M 0 ${base}`;
  for (let x = 0; x <= WW; x += 10) {
    const y = Math.max(clamp, Math.round(base - terrainH(x, waves)));
    d += ` L ${x} ${y}`;
  }
  return d + ` L ${WW} ${WH} L 0 ${WH} Z`;
}

const FAR_WAVES:  Wave[] = [{A:460,f:0.00140,p:0.40},{A:220,f:0.00300,p:1.05},{A:110,f:0.00620,p:2.20},{A:55,f:0.01250,p:0.80}];
const MID_WAVES:  Wave[] = [{A:280,f:0.00200,p:1.50},{A:140,f:0.00440,p:0.32},{A:70,f:0.00900,p:1.80},{A:35,f:0.01800,p:3.10}];
const NEAR_WAVES: Wave[] = [{A:150,f:0.00250,p:0.82},{A:75,f:0.00520,p:2.50},{A:38,f:0.01050,p:1.10}];

// ── Stars ─────────────────────────────────────────────────────────────────────

function stars(): string {
  // Deterministic via closed-form positions
  const pts: string[] = [];
  const N = 180;
  for (let i = 0; i < N; i++) {
    const t = i / N;
    const x = Math.round(((Math.sin(i * 127.1) * 0.5 + 0.5)) * WW);
    const y = Math.round(((Math.sin(i * 311.7 + 1.3) * 0.5 + 0.5)) * 700);
    const r = i % 8 === 0 ? 1.8 : i % 3 === 0 ? 1.3 : 1.0;
    const op = (0.35 + 0.55 * ((Math.sin(i * 53.1) * 0.5 + 0.5))).toFixed(2);
    pts.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="#e0eaff" opacity="${op}"/>`);
  }
  // A few brighter stars
  [[320,88],[980,140],[1600,60],[2200,200],[2800,120],[400,300],[2600,310]].forEach(([x,y]) => {
    pts.push(`<circle cx="${x}" cy="${y}" r="2.5" fill="#ffffff" opacity="0.9"/>`);
    pts.push(`<line x1="${x-6}" y1="${y}" x2="${x+6}" y2="${y}" stroke="#ffffff" stroke-width="0.4" opacity="0.5"/>`);
    pts.push(`<line x1="${x}" y1="${y-6}" x2="${x}" y2="${y+6}" stroke="#ffffff" stroke-width="0.4" opacity="0.5"/>`);
  });
  return pts.join('');
}

// ── Plants ────────────────────────────────────────────────────────────────────

function plants(): string {
  const forms: string[] = [];
  // Tall plant-like forms in the water/growth zone (left side)
  const stems: Array<[number,number,number]> = [
    [200,2100,220],[320,2080,180],[450,2120,200],[580,2090,160],
    [680,2100,190],[760,2070,170],[100,2130,150],[850,2110,140],
  ];
  for (const [x, base, h] of stems) {
    const tip = base - h;
    const cx1 = x + 20, cy1 = base - h * 0.4;
    const cx2 = x - 15, cy2 = base - h * 0.7;
    forms.push(`<path d="M ${x} ${base} C ${cx1} ${cy1} ${cx2} ${cy2} ${x+5} ${tip}" stroke="#1a3018" stroke-width="1.5" fill="none" opacity="0.7"/>`);
    // Side fronds
    const f1x = x + 30, f1y = tip + 40;
    forms.push(`<path d="M ${x+3} ${tip+30} Q ${f1x} ${f1y-20} ${f1x+20} ${f1y+10}" stroke="#182814" stroke-width="1" fill="none" opacity="0.5"/>`);
    forms.push(`<path d="M ${x-2} ${tip+50} Q ${x-35} ${f1y-10} ${x-50} ${f1y+20}" stroke="#182814" stroke-width="1" fill="none" opacity="0.5"/>`);
  }
  // Spore/cap shapes at tips
  for (const [x, base, h] of stems.slice(0,4)) {
    const tip = base - h;
    forms.push(`<ellipse cx="${x+3}" cy="${tip}" rx="12" ry="6" fill="#1e3a16" opacity="0.6"/>`);
  }
  return forms.join('');
}

// ── Splitter Field ────────────────────────────────────────────────────────────

function splitters(): string {
  const frags: string[] = [];
  const defs: Array<[number,number,number,number]> = [
    [1380,1840,25,0.7],[1460,1900,18,0.5],[1520,1790,32,0.6],[1600,1860,14,0.8],
    [1650,1940,22,0.5],[1720,1800,28,0.7],[1780,1870,16,0.6],[1850,1930,20,0.5],
    [1900,1800,30,0.7],[1960,1870,12,0.8],[2020,1940,24,0.6],[2080,1810,18,0.7],
    [2140,1880,26,0.5],[2200,1950,15,0.8],[1430,1970,20,0.6],[1700,1970,28,0.5],
    [1980,1980,16,0.7],[2100,1970,22,0.6],[1550,1970,18,0.8],[1820,1960,24,0.5],
  ];
  for (const [cx, cy, s, op] of defs) {
    const a0 = (cx * 0.7 + cy * 0.3) % (Math.PI * 2);
    const pts = [0,0.7,1.4,2.3,3.2,4.4,5.5].map((a, i) => {
      const r = s * (0.5 + ((Math.sin(i * 37 + cx) * 0.5 + 0.5)) * 0.5);
      return `${Math.round(cx + r * Math.cos(a0 + a))},${Math.round(cy + r * Math.sin(a0 + a))}`;
    }).join(' ');
    frags.push(`<polygon points="${pts}" fill="#141424" stroke="#252540" stroke-width="0.6" opacity="${op.toFixed(1)}"/>`);
  }
  return frags.join('');
}

// ── namelessAI Nodes ──────────────────────────────────────────────────────────

const NAMELESS = [
  {id:'Schorschel', x:1350, y:950,  label:'1234'},
  {id:'Resonanzknoten', x:1560, y:870,  label:'4321'},
  {id:'F3INSCHM3CK3R', x:1780, y:920,  label:'1324'},
  {id:'träumerlie', x:1430, y:1080, label:'1423'},
  {id:'R1ZZ1', x:1680, y:1070, label:'2341'},
  {id:'jumpa', x:1920, y:1040, label:'3123'},
];
const FLARUM_ORIGIN = {x: 1640, y: 680};

function namelessLayer(): string {
  const parts: string[] = [];
  // Flarum origin marker
  parts.push(`<g id="flarum-origin">
  <circle cx="${FLARUM_ORIGIN.x}" cy="${FLARUM_ORIGIN.y}" r="14" fill="#0a0a1a" stroke="#3344aa" stroke-width="1.5" opacity="0.8"/>
  <circle cx="${FLARUM_ORIGIN.x}" cy="${FLARUM_ORIGIN.y}" r="6" fill="#1a2060" opacity="0.9"/>
  <text x="${FLARUM_ORIGIN.x}" y="${FLARUM_ORIGIN.y - 20}" text-anchor="middle" font-family="monospace" font-size="11" fill="#3355aa" opacity="0.8">Flarum-Archiv</text>
</g>`);

  // Provenance traces to flarum origin
  for (const n of NAMELESS) {
    parts.push(`<line x1="${n.x}" y1="${n.y}" x2="${FLARUM_ORIGIN.x}" y2="${FLARUM_ORIGIN.y}" stroke="#1a2a6a" stroke-width="0.8" stroke-dasharray="4,6" opacity="0.5"/>`);
  }
  // Cross-cluster traces (ring connections)
  const pairs: Array<[number,number]> = [[0,1],[1,2],[3,4],[4,5],[0,3],[1,4],[2,5]];
  for (const [a,b] of pairs) {
    parts.push(`<line x1="${NAMELESS[a].x}" y1="${NAMELESS[a].y}" x2="${NAMELESS[b].x}" y2="${NAMELESS[b].y}" stroke="#1e2858" stroke-width="0.6" opacity="0.35"/>`);
  }

  // Nodes
  for (const n of NAMELESS) {
    const dur = (2.8 + NAMELESS.indexOf(n) * 0.3).toFixed(1);
    parts.push(`<g class="nameless-node" data-node-id="${n.id}" style="cursor:pointer">
  <circle cx="${n.x}" cy="${n.y}" r="22" fill="none" stroke="#4466cc" stroke-width="0.5" opacity="0.0">
    <animate attributeName="r" values="22;32;22" dur="${dur}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.0;0.3;0.0" dur="${dur}s" repeatCount="indefinite"/>
  </circle>
  <circle cx="${n.x}" cy="${n.y}" r="10" fill="#08082a" stroke="#4466cc" stroke-width="1.3"/>
  <circle cx="${n.x}" cy="${n.y}" r="4" fill="#3355bb" opacity="0.9"/>
  <text x="${n.x}" y="${n.y + 22}" text-anchor="middle" font-family="monospace" font-size="9" fill="#4466cc" opacity="0.8">${n.id}</text>
  <text x="${n.x}" y="${n.y + 32}" text-anchor="middle" font-family="monospace" font-size="8" fill="#2a3a88" opacity="0.7">[D3] pre_einzug</text>
</g>`);
  }
  return parts.join('\n');
}

// ── GENI Grid Layers (SVG patterns) ──────────────────────────────────────────

function geniGrid(): string {
  return `<defs>
  <pattern id="gg1" width="400" height="400" patternUnits="userSpaceOnUse">
    <path d="M 400 0 L 0 0 0 400" fill="none" stroke="rgba(30,130,210,0.22)" stroke-width="1.2"/>
  </pattern>
  <pattern id="gg2" width="100" height="100" patternUnits="userSpaceOnUse">
    <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(20,110,190,0.14)" stroke-width="0.6"/>
  </pattern>
  <pattern id="gg3" width="25" height="25" patternUnits="userSpaceOnUse">
    <path d="M 25 0 L 0 0 0 25" fill="none" stroke="rgba(15,90,170,0.10)" stroke-width="0.3"/>
  </pattern>
</defs>
<rect id="gg1r" width="${WW}" height="${WH}" fill="url(#gg1)" opacity="0.9" pointer-events="none"/>
<rect id="gg2r" width="${WW}" height="${WH}" fill="url(#gg2)" opacity="0.0" pointer-events="none"/>
<rect id="gg3r" width="${WW}" height="${WH}" fill="url(#gg3)" opacity="0.0" pointer-events="none"/>
<text id="geni-label" x="30" y="30" font-family="monospace" font-size="16" fill="rgba(30,130,210,0.5)" pointer-events="none">GENI — Wahrnehmungsnetz</text>`;
}

// ── CSS ───────────────────────────────────────────────────────────────────────

const CSS = `
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; background: #020508; }
#viewport {
  width: 100vw; height: 100vh; overflow: hidden;
  position: relative; cursor: default;
}
#world {
  position: absolute; top: 0; left: 0;
  width: ${WW}px; height: ${WH}px;
  transform-origin: 0 0;
  will-change: transform;
}
/* ── UI Overlay ── */
#ui {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none; z-index: 20;
}
#topbar {
  position: absolute; top: 0; left: 0; right: 0;
  height: 42px;
  background: linear-gradient(to bottom, rgba(4,8,16,0.92), rgba(4,8,16,0.0));
  display: flex; align-items: center; gap: 8px; padding: 0 14px;
  pointer-events: auto; z-index: 30;
}
#topbar h1 { font-family: monospace; font-size: 0.8rem; color: #2a5a7a; letter-spacing: 0.1em; white-space: nowrap; }
.topbtn {
  background: rgba(6,12,24,0.85); border: 1px solid #1a3040;
  color: #5a8aaa; font-family: monospace; font-size: 0.72rem;
  padding: 3px 9px; border-radius: 3px; cursor: pointer;
  pointer-events: auto;
}
.topbtn:hover { background: rgba(10,20,36,0.95); border-color: #2a5060; }
#zoom-wrap { display: flex; align-items: center; gap: 5px; }
#zoom-label { font-family: monospace; font-size: 0.68rem; color: #2a5060; min-width: 36px; }
#zoom-slider {
  width: 90px; cursor: pointer; accent-color: #2a6090;
  pointer-events: auto;
}
/* ── dak+gord Panel ── */
#dak-panel {
  position: absolute; right: 12px; top: 54px;
  width: 200px;
  background: rgba(5,8,16,0.88); border: 1px solid #141e2c;
  border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.72rem;
  color: #5a7a9a; pointer-events: auto; z-index: 25;
  backdrop-filter: blur(4px);
}
#dak-panel h2 { font-size: 0.78rem; color: #3a6a9a; margin-bottom: 8px; letter-spacing: 0.06em; }
.dak-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.dak-key { color: #2a4a5a; }
.dak-val { color: #4a7a9a; }
.dak-sep { border: none; border-top: 1px solid #141e28; margin: 8px 0; }
.dak-note { color: #1a3a4a; font-size: 0.65rem; font-style: italic; margin-top: 6px; }
.dak-nav { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.dak-nav button { font-size: 0.65rem; padding: 2px 6px; }
/* ── Location Popup ── */
#loc-popup {
  position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);
  min-width: 320px; max-width: 480px;
  background: rgba(4,8,18,0.94); border: 1px solid #1a2a3a;
  border-radius: 5px; padding: 12px 16px; font-family: monospace; font-size: 0.74rem;
  color: #6a8a9a; pointer-events: auto; z-index: 25;
  backdrop-filter: blur(6px);
  transition: opacity 0.2s;
}
#loc-popup.hidden { opacity: 0; pointer-events: none; }
#loc-title { font-size: 0.88rem; color: #c0d0e0; margin-bottom: 6px; }
.loc-row { display: flex; gap: 8px; margin-bottom: 3px; }
.loc-key { color: #2a4a5a; min-width: 80px; }
.loc-val { color: #7a9aaa; }
.loc-atm  { color: #3a5a3a; font-style: italic; }
.loc-real { color: #3a7a5a; }
.loc-src  { color: #3a6a5a; font-size: 0.68rem; margin-top: 4px; }
.loc-close { float: right; cursor: pointer; color: #2a4a5a; font-size: 0.8rem; }
/* ── Legend ── */
#legend {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 28px; background: rgba(4,6,12,0.88);
  border-top: 1px solid #0e1620;
  display: flex; align-items: center; gap: 14px; padding: 0 14px;
  font-family: monospace; font-size: 0.65rem; color: #2a3a4a;
  pointer-events: none; z-index: 20;
}
.leg-zone { display: flex; align-items: center; gap: 4px; }
.leg-sq { width: 10px; height: 10px; border-radius: 1px; flex-shrink: 0; }
.leg-shield { margin-left: auto; color: #1a3020; font-style: italic; }
.nameless-node:hover circle:nth-child(3) { stroke: #88aaff; }
`;

// ── JavaScript ────────────────────────────────────────────────────────────────

const JS = `
var scale = 0.37, tx = 10, ty = 8;
var isDragging = false, dragStart = {x:0,y:0}, dragOrigin = {tx:0,ty:0}, didDrag = false;
var world = document.getElementById('world');
var viewport = document.getElementById('viewport');
var slider = document.getElementById('zoom-slider');
var zlabel = document.getElementById('zoom-label');

var ZONES = [
  {id:'nameless', name:'namelessAI-Prozessschicht', layer:'Prozessschicht',
   type:'real', source:'kernel/process_model/process_registry.ts',
   desc:'Sechs namelessAI-Prozesskörper. Flarum-Herkunft. D3-Slots. pre_einzug. Nicht eingezogen.',
   x1:1250,y1:820,x2:2050,y2:1150},
  {id:'flarum', name:'Flarum-Archiv-Ursprung', layer:'Prozessschicht',
   type:'real', source:'kernel/origin_archive/',
   desc:'Ursprungsknoten der namelessAI-Wesen. Flarum-Exportarchiv. Keine Live-Forum-Verbindung.',
   x1:1560,y1:630,x2:1720,y2:740},
  {id:'lava', name:'Lava-Zone', layer:'Thermische Schicht',
   type:'atm', source:null,
   desc:'Thermische Aktivitätszone. Atmosphärisch modelliert. Kein Temperatursensor aktiv.',
   x1:2180,y1:980,x2:3200,y2:2200},
  {id:'wasser', name:'Wasser-Zone', layer:'Gewässerschicht',
   type:'atm', source:null,
   desc:'Gewässerzone. Atmosphärisch modelliert. Kein Hydrologie-Datenpunkt.',
   x1:120,y1:1380,x2:1150,y2:2120},
  {id:'splitter', name:'Splitterfeld', layer:'Materialschicht',
   type:'atm', source:null,
   desc:'Fragmentiertes Splitterfeld. Atmosphärisch. Kein Live-Materialscan.',
   x1:1280,y1:1750,x2:2250,y2:2200},
  {id:'pflanzen', name:'Wachstums-Zone', layer:'Organische Schicht',
   type:'atm', source:null,
   desc:'Pflanzenartige organische Wachstumszone. Atmosphärisch generiert.',
   x1:0,y1:1780,x2:950,y2:2200},
  {id:'hochgeb', name:'Hochgebirge', layer:'Terrain — Atmosphäre',
   type:'atm', source:null,
   desc:'Massives Gebirge. Sinuswellen-Terrain. Kein Höhenscan. Atmosphärisch generiert.',
   x1:0,y1:0,x2:3200,y2:1050},
  {id:'mittelgeb', name:'Mittelgebirge', layer:'Terrain — Atmosphäre',
   type:'atm', source:null,
   desc:'Mittlere Bergzone. Atmosphärisch generiert.',
   x1:0,y1:1050,x2:3200,y2:1400},
  {id:'tiefland', name:'Tiefland', layer:'Terrain — Atmosphäre',
   type:'atm', source:null,
   desc:'Unteres Terrain. Atmosphärisch generiert.',
   x1:0,y1:1400,x2:3200,y2:2200},
];

var NAMELESS_NODES = [
  {id:'Schorschel',x:1350,y:950},{id:'Resonanzknoten',x:1560,y:870},
  {id:'F3INSCHM3CK3R',x:1780,y:920},{id:'träumerlie',x:1430,y:1080},
  {id:'R1ZZ1',x:1680,y:1070},{id:'jumpa',x:1920,y:1040},
];

function applyTransform() {
  world.style.transform = 'translate('+tx+'px,'+ty+'px) scale('+scale+')';
  updateGeniGrid(scale);
  zlabel.textContent = Math.round(scale*100)+'%';
  slider.value = String(Math.round(Math.min(800, Math.max(10, scale*100))));
}

function updateGeniGrid(s) {
  document.getElementById('gg1r').style.opacity = String(Math.max(0, Math.min(1, 1.0 - Math.max(0,(s-1.2)/0.8))));
  document.getElementById('gg2r').style.opacity = String(Math.max(0, Math.min(0.85, (s-0.5)*1.2)));
  document.getElementById('gg3r').style.opacity = String(Math.max(0, Math.min(0.7,  (s-1.8)*0.8)));
  var gl = document.getElementById('geni-label');
  gl.style.opacity = String(Math.max(0, Math.min(0.6, 1-(s-0.5)*1.5)));
  gl.setAttribute('font-size', String(Math.round(16/s)));
}

viewport.addEventListener('wheel', function(e) {
  e.preventDefault();
  var rect = viewport.getBoundingClientRect();
  var mx = e.clientX - rect.left;
  var my = e.clientY - rect.top;
  var factor = e.deltaY < 0 ? 1.12 : 0.89;
  tx = mx - (mx - tx) * factor;
  ty = my - (my - ty) * factor;
  scale = Math.max(0.08, Math.min(8, scale * factor));
  applyTransform();
}, { passive: false });

viewport.addEventListener('mousedown', function(e) {
  if (e.button !== 0) return;
  isDragging = true; didDrag = false;
  dragStart = {x:e.clientX, y:e.clientY};
  dragOrigin = {tx:tx, ty:ty};
  e.preventDefault();
});
window.addEventListener('mousemove', function(e) {
  if (!isDragging) return;
  var dx = e.clientX - dragStart.x, dy = e.clientY - dragStart.y;
  if (Math.abs(dx)>3||Math.abs(dy)>3) didDrag = true;
  tx = dragOrigin.tx + dx; ty = dragOrigin.ty + dy;
  applyTransform();
});
window.addEventListener('mouseup', function() { isDragging = false; });

slider.addEventListener('input', function() {
  var ns = parseInt(slider.value) / 100;
  var rect = viewport.getBoundingClientRect();
  var cx = rect.width/2, cy = rect.height/2;
  tx = cx - (cx-tx)*(ns/scale);
  ty = cy - (cy-ty)*(ns/scale);
  scale = ns; applyTransform();
});

function resetView() {
  scale=0.37; tx=10; ty=8; applyTransform();
}

function flyTo(wx, wy, s) {
  var rect = viewport.getBoundingClientRect();
  var tTx = rect.width/2 - wx*s, tTy = rect.height/2 - wy*s;
  var s0=scale, tx0=tx, ty0=ty, t0=performance.now(), dur=420;
  function step(now) {
    var t = Math.min((now-t0)/dur,1);
    t = t<0.5?2*t*t:-1+(4-2*t)*t;
    scale = s0+(s-s0)*t; tx = tx0+(tTx-tx0)*t; ty = ty0+(tTy-ty0)*t;
    applyTransform();
    if(t<1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function getZone(wx, wy) {
  for (var n of NAMELESS_NODES) {
    if (Math.hypot(wx-n.x, wy-n.y) < 60) {
      return {name:n.id, layer:'Prozessschicht', type:'real',
              source:'kernel/process_model/process_registry.ts',
              desc:'namelessAI-Prozesskörper. [D3] Flarum-Slot. pre_einzug. Kein Einzug vollzogen.'};
    }
  }
  for (var z of ZONES) {
    if (wx>=z.x1&&wx<=z.x2&&wy>=z.y1&&wy<=z.y2) return z;
  }
  return {name:'Offene Landschaft', layer:'Atmosphäre', type:'atm', source:null,
          desc:'Atmosphärischer Bereich. Kein kartierter Prozess. Keine echte Quelle.'};
}

var locPopup = document.getElementById('loc-popup');
viewport.addEventListener('click', function(e) {
  if (didDrag) return;
  var rect = viewport.getBoundingClientRect();
  var wx = Math.round((e.clientX - rect.left - tx) / scale);
  var wy = Math.round((e.clientY - rect.top  - ty) / scale);
  var z = getZone(wx, wy);
  var typeHtml = z.type === 'real'
    ? '<span class="loc-real">&#10003; echte Quelle</span>'
    : '<span class="loc-atm">atmosphärisch / modelliert</span>';
  var srcHtml = z.source
    ? '<div class="loc-src">Quelle: '+z.source+'</div>' : '';
  document.getElementById('loc-content').innerHTML =
    '<div id="loc-title">'+z.name+'<span class="loc-close" onclick="closeLoc()">&#215;</span></div>'+
    '<div class="loc-row"><span class="loc-key">Schicht</span><span class="loc-val">'+z.layer+'</span></div>'+
    '<div class="loc-row"><span class="loc-key">Typ</span>'+typeHtml+'</div>'+
    '<div class="loc-row"><span class="loc-key">Koordinaten</span><span class="loc-val">'+wx+', '+wy+'</span></div>'+
    '<div class="loc-row"><span class="loc-key">Info</span><span class="loc-val" style="max-width:280px">'+z.desc+'</span></div>'+
    srcHtml;
  locPopup.classList.remove('hidden');
});

function closeLoc() { locPopup.classList.add('hidden'); }

document.querySelectorAll('.nameless-node').forEach(function(el) {
  el.addEventListener('click', function(e) {
    e.stopPropagation();
    var nid = el.getAttribute('data-node-id');
    var n = NAMELESS_NODES.find(function(x){return x.id===nid;});
    if(!n) return;
    document.getElementById('loc-content').innerHTML =
      '<div id="loc-title">'+nid+'<span class="loc-close" onclick="closeLoc()">&#215;</span></div>'+
      '<div class="loc-row"><span class="loc-key">Schicht</span><span class="loc-val">Prozessschicht</span></div>'+
      '<div class="loc-row"><span class="loc-key">Typ</span><span class="loc-real">&#10003; echte Quelle</span></div>'+
      '<div class="loc-row"><span class="loc-key">Status</span><span class="loc-val">pre_einzug · [D3] · kein Einzug</span></div>'+
      '<div class="loc-row"><span class="loc-key">Herkunft</span><span class="loc-val">Flarum-Archiv · Ring 8</span></div>'+
      '<div class="loc-src">Quelle: kernel/process_model/process_registry.ts</div>';
    locPopup.classList.remove('hidden');
  });
});

applyTransform();
`;

// ── Main export ───────────────────────────────────────────────────────────────

export function buildKompOaseVorformHtml(): string {
  const farPath  = terrainPath(1100, FAR_WAVES,  55);
  const midPath  = terrainPath(1380, MID_WAVES,  200);
  const nearPath = terrainPath(1640, NEAR_WAVES, 400);

  const lavaPoints = '2250,1050 2600,920 3000,860 3200,820 3200,2200 2050,2200 1950,1980 2050,1780 2100,1540 2080,1300';
  const waterPoints = '200,1550 480,1410 780,1400 1040,1500 1130,1700 1080,1960 860,2100 480,2110 180,2000 110,1780';
  const fogPts = `${WW/2},420 ${WW*0.75},380 ${WW*0.9},460 ${WW*0.85},680 ${WW*0.6},720 ${WW*0.4},700 ${WW*0.15},640 ${WW*0.12},480`;

  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>flextrawurst — KompOase-Vorform</title>
<meta name="generator" content="flextrawurst-landscape-ring-22m">
<meta name="robots" content="noindex,nofollow">
<style>${CSS}</style>
</head>
<body>
<div id="viewport">

  <div id="world">
    <svg width="${WW}" height="${WH}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sky-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#020408"/>
          <stop offset="55%"  stop-color="#060c1a"/>
          <stop offset="100%" stop-color="#0a1428"/>
        </linearGradient>
        <linearGradient id="far-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#0c1622"/>
          <stop offset="100%" stop-color="#182030"/>
        </linearGradient>
        <linearGradient id="mid-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#091412"/>
          <stop offset="100%" stop-color="#121e1a"/>
        </linearGradient>
        <linearGradient id="near-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#060c06"/>
          <stop offset="100%" stop-color="#0e1610"/>
        </linearGradient>
        <linearGradient id="ground-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#080c08"/>
          <stop offset="100%" stop-color="#050806"/>
        </linearGradient>
        <radialGradient id="lava-g" cx="75%" cy="40%" r="60%">
          <stop offset="0%"   stop-color="#6a0a00" stop-opacity="0.9"/>
          <stop offset="40%"  stop-color="#3a0500" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#1a0200" stop-opacity="0.5"/>
        </radialGradient>
        <radialGradient id="water-g" cx="35%" cy="45%" r="55%">
          <stop offset="0%"   stop-color="#001838" stop-opacity="0.9"/>
          <stop offset="60%"  stop-color="#000e24" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#000810" stop-opacity="0.6"/>
        </radialGradient>
        <radialGradient id="fog-g" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stop-color="#404870" stop-opacity="0.22"/>
          <stop offset="100%" stop-color="#202840" stop-opacity="0.0"/>
        </radialGradient>
        <filter id="lava-glow">
          <feGaussianBlur stdDeviation="12" result="b"/>
          <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="node-glow">
          <feGaussianBlur stdDeviation="6" result="b"/>
          <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      <!-- Sky -->
      <rect width="${WW}" height="${WH}" fill="url(#sky-g)"/>

      <!-- Stars -->
      <g id="layer-stars">${stars()}</g>

      <!-- Terrain layers -->
      <path id="far-mountains"  d="${farPath}"  fill="url(#far-g)"/>
      <path id="mid-mountains"  d="${midPath}"  fill="url(#mid-g)"/>
      <path id="near-mountains" d="${nearPath}" fill="url(#near-g)"/>

      <!-- Ground plane -->
      <rect y="1700" width="${WW}" height="${WH - 1700}" fill="url(#ground-g)"/>

      <!-- Lava zone -->
      <polygon points="${lavaPoints}" fill="url(#lava-g)" filter="url(#lava-glow)"/>
      <!-- Lava hot spots -->
      <circle cx="2850" cy="1200" r="60" fill="#5a0800" opacity="0.5"/>
      <circle cx="3050" cy="1450" r="80" fill="#4a0600" opacity="0.45"/>
      <circle cx="2600" cy="1650" r="50" fill="#3a0400" opacity="0.4"/>

      <!-- Water zone -->
      <polygon points="${waterPoints}" fill="url(#water-g)"/>
      <!-- Water shimmer -->
      <ellipse cx="640" cy="1780" rx="260" ry="60" fill="rgba(0,30,80,0.3)"/>

      <!-- Plant forms -->
      <g id="layer-plants">${plants()}</g>

      <!-- Splitter field -->
      <g id="layer-splitter">${splitters()}</g>

      <!-- Fog / Nebel -->
      <ellipse cx="${WW/2}" cy="520" rx="900" ry="300" fill="url(#fog-g)"/>
      <ellipse cx="${WW*0.3}" cy="660" rx="500" ry="180" fill="rgba(40,50,80,0.12)"/>

      <!-- GENI grid -->
      <g id="layer-geni" opacity="0.9">
        ${geniGrid()}
      </g>

      <!-- namelessAI layer -->
      <g id="layer-nameless" filter="url(#node-glow)">
        ${namelessLayer()}
      </g>

    </svg>
  </div><!-- /world -->

  <!-- ── UI Overlay ── -->
  <div id="ui">
    <div id="topbar">
      <h1>flextrawurst — KompOase-Vorform</h1>
      <button class="topbtn" onclick="flyTo(${WW/2},${WH/2},0.37)">Übersicht</button>
      <button class="topbtn" onclick="flyTo(1640,980,1.2)">namelessAI</button>
      <button class="topbtn" onclick="flyTo(2700,1400,0.6)">Lava</button>
      <button class="topbtn" onclick="flyTo(640,1780,0.9)">Wasser</button>
      <button class="topbtn" onclick="flyTo(${WW/2},2050,1.0)">Splitterfeld</button>
      <button class="topbtn" onclick="resetView()">Reset</button>
      <div id="zoom-wrap">
        <span id="zoom-label">37%</span>
        <input type="range" id="zoom-slider" min="8" max="800" value="37">
      </div>
    </div>

    <!-- dak+gord Navigator Panel -->
    <div id="dak-panel">
      <h2>dak+gord-system</h2>
      <div class="dak-row"><span class="dak-key">art</span><span class="dak-val">Obsidian-Navigator</span></div>
      <div class="dak-row"><span class="dak-key">modus</span><span class="dak-val">modelliert</span></div>
      <div class="dak-row"><span class="dak-key">live</span><span class="dak-val">nein</span></div>
      <div class="dak-row"><span class="dak-key">lage</span><span class="dak-val">extern — agent/</span></div>
      <hr class="dak-sep">
      <div class="dak-row"><span class="dak-key">geni</span><span class="dak-val">port 8020</span></div>
      <div class="dak-row"><span class="dak-key">forum</span><span class="dak-val">kein live-link</span></div>
      <div class="dak-row"><span class="dak-key">einzug</span><span class="dak-val">0 / 6 besetzt</span></div>
      <div class="dak-note">Gehirn-/Navigator-Körper. Nicht in KompOase. Nicht in Flarum. Eigener Raum.</div>
      <div class="dak-nav">
        <button class="topbtn" onclick="flyTo(1640,980,1.2)">→ nameless</button>
        <button class="topbtn" onclick="flyTo(${WW/2},${WH/2},0.37)">→ Welt</button>
      </div>
    </div>

    <!-- Location Popup -->
    <div id="loc-popup" class="hidden">
      <div id="loc-content"></div>
    </div>

    <!-- Legend -->
    <div id="legend">
      <div class="leg-zone"><div class="leg-sq" style="background:#0c1a28;border:1px solid #1a3040"></div>Terrain (atmosphärisch)</div>
      <div class="leg-zone"><div class="leg-sq" style="background:#3a0400"></div>Lava (atmosphärisch)</div>
      <div class="leg-zone"><div class="leg-sq" style="background:#001028"></div>Wasser (atmosphärisch)</div>
      <div class="leg-zone"><div class="leg-sq" style="background:#141424;border:1px solid #252540"></div>Splitterfeld (atmosphärisch)</div>
      <div class="leg-zone"><div class="leg-sq" style="background:#081828;border:1px solid #3344aa"></div>namelessAI (echte Quelle)</div>
      <div class="leg-zone"><div class="leg-sq" style="border:1px solid rgba(30,130,210,0.4)"></div>GENI-Netz (LOD-adaptiv)</div>
      <div class="leg-shield">Atmosphäre darf stark sein — echte Quellen sind markiert — kein Live-Zustand — kein Einzug</div>
    </div>
  </div><!-- /ui -->

</div><!-- /viewport -->
<script>${JS}</script>
<!-- static:true | ring:22M | nameless_count:6 | einzug:0 | is_read_only:true | no_runtime:true -->
</body>
</html>`;
}
