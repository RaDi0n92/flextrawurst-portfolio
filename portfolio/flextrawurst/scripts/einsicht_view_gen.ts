import { CANONICAL_ENTITY_IDS } from "../kernel/entities/seed_entities.ts";
import { STATUS_LABELS, hungerColor, type EinsichtStatus } from "./einsicht_taxonomy_contracts.ts";

const entityIds = [...CANONICAL_ENTITY_IDS];
const ENTITY_COLORS = ["#10d8f0","#f0a010","#a010f0","#10f050","#f01060","#6080f0"];

export function generateEinsichtView(): string {
  const vitalsChips = entityIds.map((id, i) => {
    const tag = id.replace("namelessAI_","");
    const col = ENTITY_COLORS[i] ?? "#888";
    return `<button class="ei-vital-chip" data-eid="${id}" style="--ec:${col}" onclick="eiWaehleWesen('${id}')"><span class="ei-vital-dot"></span>${tag}<span class="ei-vital-state"></span></button>`;
  }).join("");

  const eColsJSON = JSON.stringify(ENTITY_COLORS);
  const eIdsJSON  = JSON.stringify(entityIds);

  return `
<div id="v-einsicht" class="v-view" style="display:none;flex-direction:column;overflow:hidden">
<style>
.ei-wrap{display:flex;flex-direction:column;height:100%;overflow:hidden;background:#010810}
.ei-vitals-bar{display:flex;align-items:center;gap:5px;padding:7px 14px;background:#010810;border-bottom:1px solid #071828;flex-shrink:0;flex-wrap:wrap}
.ei-vital-chip{background:none;border:1px solid var(--ec);border-radius:3px;padding:3px 10px;font-size:.58rem;font-family:monospace;cursor:pointer;letter-spacing:.1em;color:var(--ec);opacity:.35;transition:all .2s;position:relative;display:inline-flex;align-items:center;gap:4px}
.ei-vital-chip.aktiv{opacity:1;font-weight:700;background:color-mix(in srgb,var(--ec) 10%,transparent)}
.ei-vital-chip .ei-vital-dot{width:5px;height:5px;border-radius:50%;background:var(--ec)}
.ei-vital-chip.live .ei-vital-dot{animation:ei-pulse 1.1s infinite}
.ei-vital-chip .ei-vital-state{font-size:.44rem;opacity:.65;max-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@keyframes ei-pulse{0%,100%{opacity:1}50%{opacity:.25}}
.ei-ampel-chip{border:1px solid #f0c010;border-radius:3px;padding:3px 10px;font-size:.52rem;font-family:monospace;cursor:pointer;color:#f0c010;letter-spacing:.1em;background:#1a1400}
.ei-ampel-chip.gruen{border-color:#10f050;color:#10f050;background:#0a1a0a}
.ei-ampel-chip.rot{border-color:#f01030;color:#f01030;background:#1a0a0a}
.ei-linsen-nav{display:flex;gap:0;border-bottom:1px solid #071828;overflow-x:auto;flex-shrink:0;background:#010a14;scrollbar-width:none}
.ei-linsen-nav::-webkit-scrollbar{display:none}
.ei-linse-btn{background:none;border:none;border-bottom:2px solid transparent;color:#1a3a5a;padding:8px 14px;font-size:.56rem;font-family:monospace;letter-spacing:.1em;cursor:pointer;white-space:nowrap;transition:all .15s;text-transform:uppercase}
.ei-linse-btn.aktiv{color:#10d8f0;border-bottom-color:#10d8f0}
.ei-linse-btn:hover:not(.aktiv){color:#4a8ab8}
.ei-linse-sep{color:#1a2a3a;padding:8px 3px;font-size:.52rem;font-family:monospace;align-self:center;flex-shrink:0}
.ei-main{flex:1;overflow:hidden;display:flex;min-height:0}
.ei-main-inner{flex:1;overflow-y:auto;padding:14px 16px;min-width:0}
.ei-detail-panel{width:340px;border-left:1px solid #071828;overflow-y:auto;padding:12px;font-size:.62rem;font-family:monospace;color:#4a6a8a;background:#010a14;flex-shrink:0}
.ei-ticker-strip{height:32px;border-top:1px solid #071828;background:#010a14;flex-shrink:0;overflow:hidden;display:flex;align-items:center;padding:0 10px}
.ei-ticker-inner{display:flex;gap:20px;animation:ei-tick 50s linear infinite;white-space:nowrap}
.ei-ticker-inner:hover{animation-play-state:paused}
.ei-ticker-ev{font-size:.52rem;font-family:monospace;color:#1a3a5a}
.ei-tick-type{color:#2a5a7a;margin-right:4px}
.ei-tick-eid{margin-right:4px}
@keyframes ei-tick{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ei-panorama{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}
.ei-pano-card{background:#020c1a;border:1px solid #071828;border-radius:5px;padding:13px;cursor:pointer;transition:border-color .2s}
.ei-pano-card:hover{border-color:#1a3a5a}
.ei-pano-card.aktiv{border-color:var(--ec,#10d8f0)}
.ei-pano-head{display:flex;align-items:center;gap:8px;margin-bottom:9px}
.ei-pano-name{font-size:.78rem;font-family:monospace;font-weight:700;letter-spacing:.1em}
.ei-pano-status{font-size:.46rem;border:1px solid;padding:2px 5px;border-radius:2px;opacity:.65;letter-spacing:.07em;margin-left:auto}
.ei-pano-dots{display:flex;flex-wrap:wrap;gap:2px;margin-bottom:9px;min-height:18px}
.ei-pano-dot{width:7px;height:7px;border-radius:1px}
.ei-pano-stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px}
.ei-pano-stat{text-align:center;border:1px solid #0a1a2a;border-radius:3px;padding:5px 3px}
.ei-pano-stat-n{font-size:.85rem;font-family:monospace}
.ei-pano-stat-l{font-size:.45rem;color:#1a3a5a;margin-top:1px;letter-spacing:.05em}
.ei-pano-spark{height:10px;display:flex;align-items:flex-end;gap:1px;margin-top:7px}
.ei-spark-b{border-radius:1px;min-width:4px}
.ei-cockpit{display:flex;flex-direction:column;gap:12px}
.ei-cockpit-header{display:flex;align-items:center;gap:10px;padding-bottom:10px;border-bottom:1px solid #071828}
.ei-cockpit-name{font-size:1rem;font-family:monospace;font-weight:700;letter-spacing:.15em}
.ei-cockpit-state{font-size:.56rem;color:#4a8ab8;font-family:monospace;margin-left:4px}
.ei-cockpit-organe{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:7px}
.ei-organ-btn{background:#020c1a;border:1px solid #071828;border-radius:4px;padding:9px 10px;cursor:pointer;transition:all .15s;text-align:left}
.ei-organ-btn:hover{border-color:#1a4a6a}
.ei-organ-btn.aktiv{border-color:#10d8f0;background:#010f1a}
.ei-organ-name{font-size:.55rem;font-family:monospace;letter-spacing:.1em;color:#2a6a8a;text-transform:uppercase}
.ei-organ-count{font-size:.85rem;color:#6ab8d8;font-family:monospace;margin-top:3px}
.ei-cockpit-stream{margin-top:2px}
.ei-cockpit-tl{border:1px solid #071828;border-radius:4px;padding:9px;background:#010a14}
.ei-tl-label{font-size:.5rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px}
.ei-tl-day{font-size:.44rem;color:#1a3a4a;font-family:monospace;text-align:center;width:20px}
.ei-tl-eid{font-size:.48rem;color:#1a3a5a;font-family:monospace;padding-right:5px}
.ei-tl-cell{width:20px;height:20px;border-radius:2px;cursor:pointer;transition:opacity .1s;display:inline-block}
.ei-tl-cell:hover{opacity:.7}
.ei-zeitfluss{overflow-x:auto;padding-bottom:6px}
.ei-zf-table{border-collapse:separate;border-spacing:3px}
.ei-zf-head{font-size:.48rem;color:#1a3a5a;font-family:monospace;text-align:center;padding:2px 2px}
.ei-zf-eid{font-size:.52rem;font-family:monospace;padding:2px 7px;white-space:nowrap;vertical-align:middle}
.ei-zf-cell{width:26px;height:26px;border-radius:3px;cursor:pointer;display:block;transition:opacity .15s}
.ei-zf-cell:hover{opacity:.7}
.ei-zf-popover{position:fixed;background:#020c18;border:1px solid #1a4a6a;border-radius:4px;padding:9px;font-size:.56rem;font-family:monospace;color:#4a8ab8;z-index:50;min-width:180px;pointer-events:none;line-height:1.5}
.ei-strom-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:9px}
.ei-strom-card{background:#020c1a;border:1px solid #071828;border-radius:4px;padding:11px 12px;cursor:pointer;transition:border-color .15s}
.ei-strom-card:hover{border-color:#1a3a5a}
.ei-strom-card.aktiv{border-color:#10d8f0}
.ei-strom-card.gross{grid-column:span 2}
.ei-strom-card-head{display:flex;align-items:center;gap:6px;margin-bottom:5px}
.ei-strom-typ{font-size:.46rem;padding:2px 5px;border-radius:2px;border:1px solid;letter-spacing:.1em;text-transform:uppercase;flex-shrink:0}
.ei-strom-eid{font-size:.48rem;font-family:monospace}
.ei-strom-ts{font-size:.47rem;color:#1a3a4a;margin-left:auto;font-family:monospace;white-space:nowrap}
.ei-strom-body{font-size:.61rem;color:#6ab8c8;line-height:1.45}
.ei-strom-tag{display:inline-block;font-size:.46rem;padding:1px 5px;border-radius:2px;background:#071828;color:#2a6a8a;margin-top:5px}
.ei-stat-box{border:1px solid;border-radius:4px;padding:9px;text-align:center;background:#020c1a}
.ei-stat-n{font-size:1.35rem;font-family:monospace}
.ei-stat-l{font-size:.46rem;color:#1a3a5a;margin-top:2px;letter-spacing:.06em}
.ei-empty{color:#1a3a5a;font-size:.62rem;font-family:monospace;padding:36px;text-align:center}
.ei-det-head{font-size:.63rem;font-family:monospace;margin-bottom:7px;letter-spacing:.1em}
.ei-det-ts{color:#1a3a5a;font-size:.54rem;margin-bottom:9px;font-family:monospace}
.ei-det-body{font-size:.61rem;line-height:1.55;color:#7ab8c8}
.ei-det-sec{border-top:1px solid #071828;padding-top:7px;margin-top:7px;font-size:.56rem;color:#2a5a7a;line-height:1.5}
.ei-det-tag{display:inline-block;font-size:.48rem;padding:2px 6px;border-radius:2px;background:#071828;letter-spacing:.1em;margin-bottom:6px}
.ei-sub-wesen{display:flex;align-items:center;gap:6px;padding:3px 0;border-bottom:1px solid #071828;font-size:.56rem;font-family:monospace}
.ei-kat-row{display:flex;flex-wrap:wrap;gap:5px;padding:4px 0 10px;border-bottom:1px solid #071828;margin-bottom:4px}
.ei-kat-chip{background:#010a14;border:1px solid var(--kc,#4a6a8a);border-radius:3px;padding:3px 10px;font-size:.54rem;font-family:monospace;cursor:pointer;letter-spacing:.1em;color:var(--kc,#4a6a8a);opacity:.45;transition:all .15s;white-space:nowrap}
.ei-kat-chip.aktiv{opacity:1;background:color-mix(in srgb,var(--kc,#4a6a8a) 14%,transparent)}
.ei-kat-n{font-size:.48rem;opacity:.75;margin-left:3px}
.ei-entsch-card{border-left:3px solid var(--ec,#10d8f0);background:linear-gradient(90deg,color-mix(in srgb,var(--ec,#10d8f0) 4%,transparent) 0%,transparent 70%);border-bottom:1px solid #071828;padding:10px 14px;cursor:pointer;transition:background .15s}
.ei-entsch-card:hover,.ei-entsch-card.aktiv{background:linear-gradient(90deg,color-mix(in srgb,var(--ec,#10d8f0) 9%,transparent) 0%,transparent 70%)}
.ei-ec-meta{display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap}
.ei-ec-wesen{font-size:.65rem;font-family:monospace;font-weight:700;letter-spacing:.1em}
.ei-ec-typ{font-size:.47rem;padding:2px 6px;border:1px solid;border-radius:2px;letter-spacing:.1em;flex-shrink:0}
.ei-ec-ts{font-size:.51rem;color:#1a3a4a;font-family:monospace;margin-left:auto}
.ei-ec-tok{font-size:.48rem;color:#2a4a6a;font-family:monospace;padding:1px 4px;border:1px solid #0a2030;border-radius:2px}
.ei-ec-text{font-size:.63rem;color:#6ab8c8;line-height:1.55;white-space:pre-wrap;word-break:break-word}
.ei-denk-card{border-left:3px solid var(--ec,#4060f0);background:linear-gradient(90deg,color-mix(in srgb,var(--ec,#4060f0) 4%,transparent) 0%,transparent 70%);border-bottom:1px solid #071828;padding:10px 14px;cursor:pointer;transition:background .15s}
.ei-denk-card:hover,.ei-denk-card.aktiv{background:linear-gradient(90deg,color-mix(in srgb,var(--ec,#4060f0) 9%,transparent) 0%,transparent 70%)}
.ei-dk-meta{display:flex;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap}
.ei-dk-depth{flex:1;max-width:90px;min-width:40px;height:4px;background:#071828;border-radius:2px;overflow:hidden}
.ei-dk-bar{height:100%;border-radius:2px}
.ei-dk-text{font-size:.63rem;color:#7ab8c8;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.ei-kat-chip--leer{opacity:.4}
.ei-kat-chip--plan{opacity:.35;border-style:dashed;cursor:default;pointer-events:none}
.ei-denk-themen-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:5px;margin-bottom:10px}
.ei-denk-thema-block{border:1px solid #0a1a2a;border-radius:4px;padding:7px 9px;cursor:pointer;transition:border-color .15s,background .15s;background:#010a14}
.ei-denk-thema-block:hover{border-color:#1a3a4a;background:#010f1a}
.ei-denk-thema-block.aktiv{border-color:#c0a030;background:#0a0800}
.ei-denk-thema-head{font-size:.5rem;font-family:monospace;letter-spacing:.1em;margin-bottom:4px;display:flex;align-items:center;gap:4px}
.ei-denk-thema-fragen{display:flex;flex-direction:column;gap:2px}
.ei-denk-frage{font-size:.44rem;color:#1a3a5a;line-height:1.4;font-family:monospace}
/* ── LIGHT MODE OVERRIDES ──────────────────────────────────────────────── */
[data-theme="light"] .ei-wrap,
[data-theme="light"] .ei-vitals-bar{background:var(--void);border-color:var(--rim)}
[data-theme="light"] .ei-linsen-nav,
[data-theme="light"] .ei-detail-panel,
[data-theme="light"] .ei-ticker-strip{background:var(--deep);border-color:var(--rim)}
[data-theme="light"] .ei-pano-card,
[data-theme="light"] .ei-organ-btn,
[data-theme="light"] .ei-cockpit-tl,
[data-theme="light"] .ei-strom-card,
[data-theme="light"] .ei-stat-box,
[data-theme="light"] .ei-denk-thema-block,
[data-theme="light"] .ei-kat-chip{background:var(--surface);border-color:var(--rim)}
[data-theme="light"] .ei-pano-card:hover,
[data-theme="light"] .ei-strom-card:hover,
[data-theme="light"] .ei-organ-btn:hover{border-color:var(--t-sub);background:var(--surface)}
[data-theme="light"] .ei-organ-btn.aktiv{background:var(--surface);border-color:var(--world)}
[data-theme="light"] .ei-pano-stat,
[data-theme="light"] .ei-strom-tag,
[data-theme="light"] .ei-det-tag{background:var(--surface);border-color:var(--rim)}
[data-theme="light"] .ei-linse-btn{color:var(--t-sub)}
[data-theme="light"] .ei-linse-btn.aktiv{color:var(--world);border-bottom-color:var(--world)}
[data-theme="light"] .ei-ticker-ev,
[data-theme="light"] .ei-tick-type,
[data-theme="light"] .ei-tl-label,
[data-theme="light"] .ei-pano-stat-l,
[data-theme="light"] .ei-stat-l,
[data-theme="light"] .ei-empty,
[data-theme="light"] .ei-det-ts,
[data-theme="light"] .ei-det-sec,
[data-theme="light"] .ei-ec-ts,
[data-theme="light"] .ei-denk-frage{color:var(--t-sub)}
[data-theme="light"] .ei-strom-body,
[data-theme="light"] .ei-det-body,
[data-theme="light"] .ei-ec-text,
[data-theme="light"] .ei-dk-text{color:var(--t-mid)}
[data-theme="light"] .ei-organ-name{color:var(--t-sub)}
[data-theme="light"] .ei-organ-count,
[data-theme="light"] .ei-pano-stat-n,
[data-theme="light"] .ei-stat-n{color:var(--t-bright)}
[data-theme="light"] .ei-cockpit-header,
[data-theme="light"] .ei-det-sec,
[data-theme="light"] .ei-sub-wesen,
[data-theme="light"] .ei-kat-row{border-color:var(--rim)}
[data-theme="light"] .ei-ampel-chip{background:var(--surface);border-color:var(--rim);color:var(--t-mid)}
[data-theme="light"] .ei-ampel-chip.gruen{background:rgba(10,144,80,0.08);border-color:rgba(10,144,80,0.4);color:var(--alive)}
[data-theme="light"] .ei-ampel-chip.rot{background:rgba(196,48,48,0.08);border-color:rgba(196,48,48,0.4);color:var(--sys)}
[data-theme="light"] .ei-zf-popover{background:var(--surface);border-color:var(--rim);color:var(--t-mid)}
[data-theme="light"] .ei-dk-depth{background:var(--rim)}
[data-theme="light"] .ei-entsch-card,
[data-theme="light"] .ei-denk-card{border-color:var(--rim)}
[data-theme="light"] .ei-denk-thema-block.aktiv{background:rgba(192,160,48,0.08);border-color:rgba(192,160,48,0.6)}
</style>

<div class="ei-wrap">
  <div class="ei-vitals-bar">
    ${vitalsChips}
    <button class="ei-vital-chip aktiv" id="ei-alle-btn" style="--ec:#444;margin-left:3px" onclick="eiWaehleWesen(null)"><span class="ei-vital-dot"></span>ALLE</button>
    <div id="ei-ampel-chip" class="ei-ampel-chip" onclick="eiLinseLaden('ampel')" style="margin-left:auto">◑ AMPEL</div>
  </div>
  <div class="ei-linsen-nav">
    <button class="ei-linse-btn aktiv" data-linse="panorama" onclick="eiLinseLaden('panorama')">PANORAMA</button>
    <span class="ei-linse-sep">·</span>
    <button class="ei-linse-btn" data-linse="zeitfluss" onclick="eiLinseLaden('zeitfluss')">ZEITFLUSS</button>
    <span class="ei-linse-sep">·</span>
    <button class="ei-linse-btn" data-linse="entscheidungen" onclick="eiLinseLaden('entscheidungen')" data-i18n="einsicht.tab.entscheidungen">ENTSCHEIDUNGEN</button>
    <button class="ei-linse-btn" data-linse="traum" onclick="eiLinseLaden('traum')" data-i18n="einsicht.tab.traumarchiv">TRÄUME</button>
    <button class="ei-linse-btn" data-linse="substanzen" onclick="eiLinseLaden('substanzen')" data-i18n="einsicht.tab.substanzen">SUBSTANZEN</button>
    <button class="ei-linse-btn" data-linse="splitter" onclick="eiLinseLaden('splitter')" data-i18n="einsicht.tab.splitter">SPLITTER</button>
    <span class="ei-linse-sep">·</span>
    <button class="ei-linse-btn" data-linse="schatten" onclick="eiLinseLaden('schatten')" data-i18n="einsicht.tab.schatten">SCHATTEN</button>
    <button class="ei-linse-btn" data-linse="beziehungen" onclick="eiLinseLaden('beziehungen')" data-i18n="einsicht.tab.beziehungen">BEZIEHUNGEN</button>
    <button class="ei-linse-btn" data-linse="innenquellen" onclick="eiLinseLaden('innenquellen')" data-i18n="einsicht.tab.innenquellen">INNENQUELLEN</button>
    <button class="ei-linse-btn" data-linse="denkfenster" onclick="eiLinseLaden('denkfenster')" data-i18n="einsicht.tab.denkfenster">DENKFENSTER</button>
    <button class="ei-linse-btn" data-linse="ampel" onclick="eiLinseLaden('ampel')" data-i18n="einsicht.tab.ampeldetail">AMPEL</button>
    <span class="ei-linse-sep">·</span>
    <button class="ei-linse-btn" data-linse="organhunger" onclick="eiLinseLaden('organhunger')" data-i18n="einsicht.tab.organhunger">ORGANHUNGER</button>
  </div>
  <div class="ei-main" id="ei-main">
    <div class="ei-main-inner" id="ei-main-inner"><div class="ei-empty">Lädt…</div></div>
    <div class="ei-detail-panel" id="ei-detail-panel"><div style="color:#1a3a5a;font-size:.56rem;font-family:monospace">Kein Eintrag ausgewählt</div></div>
  </div>
  <div class="ei-ticker-strip">
    <div class="ei-ticker-inner" id="ei-ticker-inner"><span class="ei-ticker-ev">● ticker…</span></div>
  </div>
</div>

<script>
(function(){
'use strict';
const API='/api';
const ECOLS=${eColsJSON};
const EIDS=${eIdsJSON};
const ETAGS=EIDS.map(function(id){return id.replace('namelessAI_','');});
let _eiWesen=null,_eiLinse='panorama',_eiAmpel=null,_eiOrgan='entscheidungen';
let _eiStromItems=[],_eiOrganItems=[],_eiZfPop=null;

function eCol(id){const i=EIDS.indexOf(id);return i>=0?ECOLS[i]:'#888';}
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function fmt(ts){if(!ts)return'—';const d=new Date(ts);return d.toLocaleDateString('de',{day:'2-digit',month:'2-digit'})+' '+d.toLocaleTimeString('de',{hour:'2-digit',minute:'2-digit'});}
function fmtL(ts){if(!ts)return'—';const d=new Date(ts);return d.toLocaleDateString('de',{day:'2-digit',month:'2-digit'})+' '+d.toLocaleTimeString('de',{hour:'2-digit',minute:'2-digit',second:'2-digit'});}
function tok(){return localStorage.getItem('ftw_token')||'';}
function ah(){const t=tok();if(!t)return{};return{Authorization:t.startsWith('Bearer ')?t:'Bearer '+t};}
function eiIstAdmin(){return !!tok() && (localStorage.getItem('ftw_role')||'')==='admin';}
function eiPublicUi(){
  if(eiIstAdmin())return;
  document.querySelectorAll('.ei-linse-btn').forEach(function(b){b.style.display=b.dataset.linse==='panorama'?'':'none';});
  document.querySelectorAll('.ei-vital-chip[data-eid]').forEach(function(b){b.style.display='none';});
  const a=document.getElementById('ei-ampel-chip');if(a)a.style.display='none';
  const t=document.querySelector('.ei-ticker-strip');if(t)t.style.display='none';
}

async function vitalsAktualisieren(){
  if(!eiIstAdmin())return;
  try{
    const r=await fetch(API+'/admin/wesen-einsicht/liveticker?limit=30',{headers:ah()});
    if(!r.ok)return;
    const d=await r.json();
    const evs=d.events||[];
    const now=Date.now();
    const recent=new Set(evs.filter(function(e){return now-new Date(e.created_at).getTime()<300000;}).map(function(e){return e.entity_id;}));
    document.querySelectorAll('.ei-vital-chip[data-eid]').forEach(function(chip){
      const eid=chip.dataset.eid;
      chip.classList.toggle('live',recent.has(eid));
      const st=chip.querySelector('.ei-vital-state');
      const last=evs.find(function(e){return e.entity_id===eid;});
      if(st&&last)st.textContent=last.event_type.replace('cyberling.','').replace('entity.','').slice(0,10);
    });
  }catch(e){}
}

window.eiWaehleWesen=function(id){
  _eiWesen=id;
  document.querySelectorAll('.ei-vital-chip').forEach(function(b){
    b.classList.toggle('aktiv',b.dataset.eid===id||(id===null&&b.id==='ei-alle-btn'));
  });
  eiLinseLaden(id?'cockpit':'panorama');
};

window.eiLinseLaden=function(linse){
  if(!eiIstAdmin())linse='panorama';
  _eiLinse=linse;
  document.querySelectorAll('.ei-linse-btn').forEach(function(b){b.classList.toggle('aktiv',b.dataset.linse===linse);});
  const dp=document.getElementById('ei-detail-panel');
  if(dp)dp.innerHTML='<div style="color:#1a3a5a;font-size:.56rem;font-family:monospace">Kein Eintrag ausgewählt</div>';
  switch(linse){
    case'panorama':return panoramaLaden();
    case'cockpit':return cockpitLaden(_eiWesen);
    case'zeitfluss':return zeitflussLaden();
    case'entscheidungen':return entscheidungenKategorienLaden(); case'traum':case'substanzen':case'splitter':case'schatten':return stromLaden(linse);
    case'beziehungen':return beziehungenLaden();
    case'innenquellen':return innenquellenLaden();
    case'denkfenster':return denkfensterAnalyseLaden();
    case'ampel':return ampelLaden();
    case'organhunger':return organhungerLaden();
  }
};

/* ── PANORAMA ── */
async function panoramaLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Panorama lädt…</div>';
  try{
    if(!eiIstAdmin()){
      const snaps=await Promise.all(EIDS.map(async function(id){
        try{const r=await fetch(API+'/entities/'+encodeURIComponent(id)+'/einsicht');return r.ok?await r.json():{entity_id:id};}
        catch(e){return{entity_id:id};}
      }));
      const cards=snaps.map(function(d,i){
        const id=d.entity_id||EIDS[i],col=ECOLS[i]||'#888',tag=id.replace('namelessAI_','');
        const ents=d.entscheidungen||[],sp=d.splitter||{},sl=d.schlaf||{},cl=d.cyberling||{};
        const dots=ents.slice(0,8).map(function(e){return'<div class="ei-pano-dot" style="background:#1a5a7a" title="'+esc(e.entscheidung||'')+'"></div>';}).join('');
        const state=sl.phase_type?('Schlafspur: '+sl.phase_type):'öffentlicher Snapshot';
        return '<div class="ei-pano-card" style="--ec:'+col+';cursor:default">'
          +'<div class="ei-pano-head"><span class="ei-pano-name" style="color:'+col+'">'+esc(tag)+'</span><span class="ei-pano-status" style="border-color:'+col+';color:'+col+'">'+esc(state)+'</span></div>'
          +'<div class="ei-pano-dots">'+(dots||'<span style="color:#1a2a3a;font-size:.48rem">keine öffentlichen Snapshot-Entscheidungen</span>')+'</div>'
          +'<div class="ei-pano-stats">'
          +'<div class="ei-pano-stat"><div class="ei-pano-stat-n" style="color:'+col+'">'+ents.length+'</div><div class="ei-pano-stat-l">Snapshot</div></div>'
          +'<div class="ei-pano-stat"><div class="ei-pano-stat-n">'+(sp.splitter_aufgesammelt||0)+'</div><div class="ei-pano-stat-l">aufges.</div></div>'
          +'<div class="ei-pano-stat"><div class="ei-pano-stat-n">'+esc(cl.status||'—')+'</div><div class="ei-pano-stat-l">Testkörper</div></div>'
          +'</div></div>';
      }).join('');
      inn.innerHTML='<div style="font-size:.5rem;color:#2a5a7a;font-family:monospace;margin-bottom:10px">ÖFFENTLICHE EINSICHT · begrenzte, bereits öffentliche Schnappschüsse · tiefe Archive bleiben intern</div><div class="ei-panorama">'+cards+'</div>';
      return;
    }
    const[eR,tR]=await Promise.all([
      fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=300',{headers:ah()}).then(r=>r.json()).catch(()=>({items:[]})),
      fetch(API+'/admin/wesen-einsicht/liveticker?limit=100',{headers:ah()}).then(r=>r.json()).catch(()=>({events:[]}))
    ]);
    const allE=eR.items||[],allT=tR.events||[];
    const dc={gedanke_posten:'#10c080',nachdenken:'#4060f0',schlafen_beginnen:'#8040c0',post:'#10c080',event:'#c0a010',brief:'#c040a0',spur:'#10c0c0'};
    const now=Date.now();
    const cards=EIDS.map(function(id,i){
      const col=ECOLS[i]||'#888',tag=ETAGS[i];
      const myE=allE.filter(e=>e.entity_id===id);
      const myT=allT.filter(e=>e.entity_id===id);
      const last=myT[0];
      const live=last&&(now-new Date(last.created_at).getTime())<300000;
      const dots=myE.slice(0,28).map(e=>'<div class="ei-pano-dot" style="background:'+(dc[e.entscheidung]||'#1a3a5a')+'" title="'+esc(e.entscheidung||'')+'"></div>').join('');
      const spark=myE.slice(0,18).map(e=>{const c=e.entscheidung==='schlafen_beginnen'?'#3a1a5a':e.entscheidung==='nachdenken'?'#1a2a5a':'#1a5a3a';const h=e.entscheidung==='schlafen_beginnen'?5:e.entscheidung==='nachdenken'?9:13;return'<div class="ei-spark-b" style="height:'+h+'px;background:'+c+'"></div>';}).join('');
      const state=live?'● LIVE':(last?last.event_type.replace('cyberling.','').slice(0,14):'idle');
      return \`<div class="ei-pano-card" data-eid="\${id}" style="--ec:\${col}" onclick="eiWaehleWesen('\${id}')">
        <div class="ei-pano-head">
          <span class="ei-pano-name" style="color:\${col}">\${esc(tag)}</span>
          <span class="ei-pano-status" style="border-color:\${col};color:\${col}">\${state}</span>
        </div>
        <div class="ei-pano-dots">\${dots||'<span style="color:#1a2a3a;font-size:.48rem">keine Entscheidungen</span>'}</div>
        <div class="ei-pano-stats">
          <div class="ei-pano-stat"><div class="ei-pano-stat-n" style="color:\${col}">\${myE.length}</div><div class="ei-pano-stat-l">Entsch.</div></div>
          <div class="ei-pano-stat"><div class="ei-pano-stat-n">\${myT.filter(e=>e.event_type&&e.event_type.includes('traum')).length}</div><div class="ei-pano-stat-l">Traum-Ev.</div></div>
          <div class="ei-pano-stat"><div class="ei-pano-stat-n">\${myT.filter(e=>e.event_type&&e.event_type.includes('splitter')).length}</div><div class="ei-pano-stat-l">Splitter-Ev.</div></div>
        </div>
        <div class="ei-pano-spark">\${spark}</div>
      </div>\`;
    }).join('');
    inn.innerHTML='<div class="ei-panorama">'+cards+'</div>';
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── COCKPIT ── */
async function cockpitLaden(eid){
  if(!eid){panoramaLaden();return;}
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Cockpit lädt…</div>';
  const col=eCol(eid),tag=eid.replace('namelessAI_','');
  try{
    const[eR,traumR,splR,tickR]=await Promise.all([
      fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=1&entity_id='+eid,{headers:ah()}).then(r=>r.json()).catch(()=>({total:0})),
      fetch(API+'/admin/wesen-einsicht/traumarchiv?entity_id='+eid,{headers:ah()}).then(r=>r.json()).catch(()=>({})),
      fetch(API+'/entities/'+eid+'/splitter?limit=1').then(r=>r.json()).catch(()=>({total:0})),
      fetch(API+'/admin/wesen-einsicht/liveticker?limit=200&entity_id='+eid,{headers:ah()}).then(r=>r.json()).catch(()=>({events:[]}))
    ]);
    const evs=tickR.events||[];
    const nTraum=(traumR.traumkandidaten||[]).length+(traumR.traumspuren||[]).length+(traumR.schlafbriefe||[]).length;
    const organe=[
      {id:'entscheidungen',label:'ENTSCHEIDUNGEN',n:eR.total||0},
      {id:'traum',label:'TRÄUME',n:nTraum},
      {id:'substanzen',label:'SUBSTANZEN',n:'—'},
      {id:'splitter',label:'SPLITTER',n:splR.total||0},
      {id:'beziehungen',label:'BEZIEHUNGEN',n:'—'},
      {id:'schatten',label:'SCHATTEN',n:'—'},
      {id:'denkfenster',label:'DENKFENSTER',n:'—'},
    ];
    const organBtns=organe.map(o=>'<button class="ei-organ-btn'+(_eiOrgan===o.id?' aktiv':'')+'" onclick="cockpitOrgan(\\''+eid+'\\',\\''+o.id+'\\')">'
      +'<div class="ei-organ-name">'+esc(o.label)+'</div><div class="ei-organ-count">'+o.n+'</div></button>').join('');

    // 7-day timeline
    const days=[];for(let i=6;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);days.push(d.toISOString().slice(0,10));}
    const dcnt={};days.forEach(d=>{dcnt[d]=0;});
    evs.forEach(ev=>{const day=ev.created_at?ev.created_at.slice(0,10):null;if(day&&dcnt[day]!==undefined)dcnt[day]++;});
    const mx=Math.max(...Object.values(dcnt),1);
    const tlHeads=days.map(d=>'<td class="ei-tl-day">'+d.slice(5)+'</td>').join('');
    const tlCells=days.map(d=>{const n=dcnt[d]||0;const a=n>0?Math.max(.1,n/mx):.04;return'<td><div class="ei-tl-cell" style="background:'+col+';opacity:'+a.toFixed(2)+'" title="'+d+': '+n+'ev" onclick="eiZfPop(event,\\''+d+'\\',\\''+eid+'\\','+n+')"></div></td>';}).join('');
    const stateStr=evs[0]?evs[0].event_type.replace('cyberling.','').replace('entity.',''):'idle';

    inn.innerHTML=\`<div class="ei-cockpit">
      <div class="ei-cockpit-header">
        <span class="ei-cockpit-name" style="color:\${col}">\${esc(tag)}</span>
        <span class="ei-cockpit-state">\${esc(stateStr)}</span>
        <button style="margin-left:auto;background:none;border:1px solid #1a3a5a;color:#2a5a7a;padding:2px 9px;font-size:.52rem;font-family:monospace;cursor:pointer;border-radius:3px" onclick="eiWaehleWesen(null)">← ALLE</button>
      </div>
      <div class="ei-cockpit-organe">\${organBtns}</div>
      <div class="ei-cockpit-stream" id="ei-cockpit-stream"><div class="ei-empty" style="padding:16px">Organ wählen →</div></div>
      <div class="ei-cockpit-tl">
        <div class="ei-tl-label">AKTIVITÄT — LETZTE 7 TAGE</div>
        <table style="border-collapse:separate;border-spacing:2px"><tr><td></td>\${tlHeads}</tr><tr><td class="ei-tl-eid" style="color:\${col}">\${esc(tag)}</td>\${tlCells}</tr></table>
      </div>
    </div>\`;
    cockpitOrganLaden(eid,_eiOrgan);
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

window.cockpitOrgan=function(eid,organ){
  _eiOrgan=organ;
  document.querySelectorAll('.ei-organ-btn').forEach(function(b){
    b.classList.toggle('aktiv',b.getAttribute('onclick').includes("'"+organ+"'"));
  });
  cockpitOrganLaden(eid,organ);
};

async function cockpitOrganLaden(eid,organ){
  const s=document.getElementById('ei-cockpit-stream');if(!s)return;
  s.innerHTML='<div class="ei-empty" style="padding:12px">Lädt…</div>';
  try{
    if(organ==='entscheidungen'){
      const d=await fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=60&entity_id='+eid,{headers:ah()}).then(r=>r.json());
      _eiOrganItems=d.items||[];
      s.innerHTML=stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'entscheidung',ts:it.tick_at,entity_id:it.entity_id,preview:(it.gedanke||'').slice(0,140),tag:it.entscheidung||'?',gross:i<2})));
    }else if(organ==='traum'){
      const d=await fetch(API+'/admin/wesen-einsicht/traumarchiv?entity_id='+eid,{headers:ah()}).then(r=>r.json());
      _eiOrganItems=[...(d.traumkandidaten||[]).map(it=>({...it,_typ:'kandidat'})),...(d.traumspuren||[]).map(it=>({...it,_typ:'spur'})),...(d.schlafbriefe||[]).map(it=>({...it,_typ:'brief'}))];
      s.innerHTML=stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'traum',ts:it.tick_at,entity_id:it.entity_id,preview:(it.traum_text||it.brief_text||it.begruendung||it.ausgewaehlter_traum||'').slice(0,160),tag:it._typ||it.emotion||'traum',gross:i===0})));
    }else if(organ==='splitter'){
      const d=await fetch(API+'/entities/'+eid+'/splitter?limit=60').then(r=>r.json());
      _eiOrganItems=d.items||d.splitter||[];
      s.innerHTML=stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'splitter',ts:it.aufgenommen_at||it.created_at,entity_id:it.entity_id,preview:(it.essenz||it.inhalt||'').slice(0,140),tag:it.materialitaet||it.typ||'splitter',gross:false})));
    }else if(organ==='beziehungen'){
      const d=await fetch(API+'/entities/'+eid+'/relationships').then(r=>r.json());
      _eiOrganItems=d.beziehungen||[];
      s.innerHTML=_eiOrganItems.length?stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'beziehung',ts:it.letzte_interaktion,entity_id:eid,preview:it.partner_id+' · '+it.beziehungstyp,tag:it.partner_type||'?',gross:false}))):'<div class="ei-empty">Keine Beziehungen.</div>';
    }else if(organ==='schatten'){
      const d=await fetch(API+'/entities/'+eid+'/shadow-dialogs?limit=60').then(r=>r.json());
      _eiOrganItems=d.items||d.dialoge||[];
      s.innerHTML=_eiOrganItems.length?stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'schatten',ts:it.created_at,entity_id:it.entity_id,preview:(it.content||'').slice(0,140),tag:it.antwortstatus||'offen',gross:false}))):'<div class="ei-empty">Keine Schatten-Dialoge.</div>';
    }else if(organ==='denkfenster'){
      const d=await fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=80&entscheidung=nachdenken&entity_id='+eid,{headers:ah()}).then(r=>r.json());
      _eiOrganItems=d.items||[];
      s.innerHTML=stromCardsHtml(_eiOrganItems.map((it,i)=>({i,typ:'denken',ts:it.tick_at,entity_id:it.entity_id,preview:(it.gedanke||'').slice(0,200),tag:(it.tokens_generated||0)+'t',gross:i===0})));
    }else if(organ==='substanzen'){
      const d=await fetch(API+'/substances/entity/'+eid+'/state',{headers:ah()}).then(r=>r.json()).catch(()=>({states:[]}));
      _eiOrganItems=d.states||[];
      if(!_eiOrganItems.length){s.innerHTML='<div class="ei-empty">Keine Substanz-Einträge.</div>';return;}
      const tc=function(t){return t==='stimulant'?'#e86020':t==='depressant'?'#2060e8':'#8a6a8a';};
      s.innerHTML='<div class="ei-strom-grid">'+_eiOrganItems.map((st,i)=>'<div class="ei-strom-card" onclick="eiDetailZeigen('+i+',\\'substanzen\\')">'
        +'<div class="ei-strom-card-head"><span class="ei-strom-typ" style="border-color:'+tc(st.substance_type)+';color:'+tc(st.substance_type)+'">'+esc(st.substance_type||'?')+'</span>'
        +'<span class="ei-strom-ts">'+fmt(st.last_updated)+'</span></div>'
        +'<div class="ei-strom-body">'+esc(st.substance_name||st.substance_id)+'</div>'
        +'<span class="ei-strom-tag">'+esc(st.status||'?')+'</span></div>').join('')+'</div>';
    }
  }catch(e){s.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── ZEITFLUSS ── */
async function zeitflussLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Zeitfluss lädt…</div>';
  try{
    const d=await fetch(API+'/admin/wesen-einsicht/liveticker?limit=500',{headers:ah()}).then(r=>r.json());
    const evs=d.events||[];
    const days=[];for(let i=13;i>=0;i--){const dt=new Date();dt.setDate(dt.getDate()-i);days.push(dt.toISOString().slice(0,10));}
    const mat={};
    EIDS.forEach(id=>{mat[id]={};days.forEach(day=>{mat[id][day]=0;});});
    evs.forEach(ev=>{if(ev.entity_id&&mat[ev.entity_id]){const day=ev.created_at?ev.created_at.slice(0,10):null;if(day&&mat[ev.entity_id][day]!==undefined)mat[ev.entity_id][day]++;}});
    const mx=Math.max(...EIDS.flatMap(id=>days.map(d=>mat[id][d]||0)),1);
    const heads='<tr><th></th>'+days.map(d=>'<th class="ei-zf-head">'+d.slice(5)+'</th>').join('')+'</tr>';
    const rows=EIDS.map((id,ei)=>{
      const col=ECOLS[ei]||'#888',tag=ETAGS[ei];
      const cells=days.map(day=>{const n=mat[id][day]||0;if(!n)return'<td><div class="ei-zf-cell" style="background:#0a1a2a;opacity:.18"></div></td>';const a=Math.max(.12,n/mx);return'<td><div class="ei-zf-cell" style="background:'+col+';opacity:'+a.toFixed(2)+'" title="'+day+': '+n+'ev" onclick="eiZfPop(event,\\''+day+'\\',\\''+id+'\\','+n+')"></div></td>';}).join('');
      return'<tr><td class="ei-zf-eid" style="color:'+col+'">'+esc(tag)+'</td>'+cells+'</tr>';
    }).join('');
    inn.innerHTML='<div style="font-size:.5rem;color:#1a3a5a;font-family:monospace;margin-bottom:10px;letter-spacing:.1em">AKTIVITÄT — LETZTE 14 TAGE</div>'
      +'<div class="ei-zeitfluss"><table class="ei-zf-table"><thead>'+heads+'</thead><tbody>'+rows+'</tbody></table></div>'
      +'<div style="margin-top:10px;font-size:.5rem;color:#1a2a3a;font-family:monospace">Klick auf Zelle → Wesen im Cockpit öffnen</div>';
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

window.eiZfPop=function(ev,day,eid,count){
  if(_eiZfPop){_eiZfPop.remove();_eiZfPop=null;}
  if(!count)return;
  const col=eCol(eid),tag=eid.replace('namelessAI_','');
  const p=document.createElement('div');
  p.style.cssText='position:fixed;left:'+Math.min(ev.clientX+8,window.innerWidth-210)+'px;top:'+(ev.clientY-65)+'px;background:#020c18;border:1px solid #1a4a6a;border-radius:4px;padding:10px;font-size:.56rem;font-family:monospace;z-index:200;pointer-events:auto;min-width:180px';
  const btn=document.createElement('button');
  btn.style.cssText='display:block;width:100%;margin-top:7px;background:#0a2018;border:1px solid #1a5a3a;color:#3ae890;font-size:.52rem;padding:3px 10px;cursor:pointer;border-radius:2px;font-family:monospace;letter-spacing:.1em';
  btn.textContent='→ Cockpit öffnen';
  btn.onclick=function(e){e.stopPropagation();eiWaehleWesen(eid);p.remove();_eiZfPop=null;};
  p.innerHTML='<div style="color:'+col+';font-weight:700;margin-bottom:3px">'+esc(tag)+' — '+esc(day)+'</div><div style="color:#2a6a8a">'+count+' Events</div>';
  p.appendChild(btn);
  document.body.appendChild(p);_eiZfPop=p;
  document.addEventListener('click',function handler(){p.remove();_eiZfPop=null;document.removeEventListener('click',handler);},{capture:true,once:true});
  setTimeout(function(){if(_eiZfPop===p){p.remove();_eiZfPop=null;}},6000);
};

/* ── STROM ── */
async function stromLaden(kat){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Lädt…</div>';
  const eP=_eiWesen?'&entity_id='+_eiWesen:'';
  try{
    if(kat==='entscheidungen'){
      const d=await fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=80'+eP,{headers:ah()}).then(r=>r.json());
      _eiStromItems=d.items||[];
      inn.innerHTML='<div style="font-size:.52rem;color:#1a3a5a;font-family:monospace;margin-bottom:10px">'+(d.total||_eiStromItems.length)+' Entscheidungen</div>'
        +stromCardsHtml(_eiStromItems.map((it,i)=>({i,typ:'entscheidung',ts:it.tick_at,entity_id:it.entity_id,preview:(it.gedanke||'').slice(0,160),tag:it.entscheidung||'?',gross:i<2})));
    }else if(kat==='traum'){
      const url=API+'/admin/wesen-einsicht/traumarchiv'+(eP?'?'+eP.slice(1):'');
      const d=await fetch(url,{headers:ah()}).then(r=>r.json());
      _eiStromItems=[...(d.traumkandidaten||[]).map(it=>({...it,_typ:'kandidat'})),...(d.traumspuren||[]).map(it=>({...it,_typ:'spur'})),...(d.schlafbriefe||[]).map(it=>({...it,_typ:'brief'}))];
      const stat='<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px;margin-bottom:12px">'
        +statBox((d.traumkandidaten||[]).length,'Kandidaten','#8040c0')
        +statBox((d.traumspuren||[]).length,'Spuren','#10c0c0')
        +statBox((d.schlafbriefe||[]).length,'Briefe','#c040a0')+'</div>';
      window._traumItems=_eiStromItems;
      window._traumAktKat=null;
      function traumChip(k,cnt){
        const has=cnt>0;
        return'<button class="ei-kat-chip'+(window._traumAktKat===k?' aktiv':'')+(!has?' ei-kat-chip--leer':'')+'" style="--kc:'+(has?'#9050d0':'#2a3a4a')+'" onclick="eiTraumFilter(\\''+k+'\\')">'+k+(has?'<span class="ei-kat-n">'+cnt+'</span>':'<span class="ei-kat-n" style="color:#2a3a4a">0</span>')+'</button>';
      }
      const rTypCnt={kandidat:(d.traumkandidaten||[]).length,spur:(d.traumspuren||[]).length,brief:(d.schlafbriefe||[]).length};
      var tChips='<button class="ei-kat-chip aktiv" style="--kc:#6a8aaa" onclick="eiTraumFilter(null)">ALLE<span class="ei-kat-n">'+(rTypCnt.kandidat+rTypCnt.spur+rTypCnt.brief)+'</span></button>';
      tChips+=traumChip('kandidat',rTypCnt.kandidat)+traumChip('spur',rTypCnt.spur)+traumChip('brief',rTypCnt.brief);
      ALLE_TRAUM_KATS.forEach(function(k){tChips+=traumChip(k,0);});
      window.eiTraumFilter=function(typ){
        window._traumAktKat=typ;
        document.querySelectorAll('.ei-traum-kats .ei-kat-chip').forEach(function(b){b.classList.toggle('aktiv',(!typ&&b.textContent.startsWith('ALLE'))||(typ&&b.textContent.startsWith(typ)));});
        const fil=typ?window._traumItems.filter(function(it){return(it._typ||it.emotion||'')===typ;}):window._traumItems;
        const el=document.getElementById('ei-traum-liste');if(el)el.innerHTML=fil.length?stromCardsHtml(fil.map(function(it,i){return{i,typ:'traum',ts:it.tick_at,entity_id:it.entity_id,preview:(it.traum_text||it.brief_text||it.begruendung||it.ausgewaehlter_traum||'').slice(0,180),tag:it._typ||it.emotion||'traum',gross:i===0};})):'<div class="ei-empty">Keine Einträge in dieser Kategorie.</div>';
      };
      inn.innerHTML=stat+'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px">TRAUMKATEGORIEN</div>'
        +'<div class="ei-kat-row ei-traum-kats">'+tChips+'</div>'
        +'<div id="ei-traum-liste">'+(_eiStromItems.length?stromCardsHtml(_eiStromItems.map(function(it,i){return{i,typ:'traum',ts:it.tick_at,entity_id:it.entity_id,preview:(it.traum_text||it.brief_text||it.begruendung||it.ausgewaehlter_traum||'').slice(0,180),tag:it._typ||it.emotion||'traum',gross:i<2};})):'<div class="ei-empty">Noch keine Traum-Aufzeichnungen.</div>')+'</div>';
    }else if(kat==='substanzen'){
      const[catR,usR]=await Promise.all([
        fetch(API+'/substances/catalog',{headers:ah()}).then(r=>r.json()).catch(()=>({substances:[]})),
        fetch(API+'/substances/usage/overview',{headers:ah()}).then(r=>r.json()).catch(()=>({events:[]}))
      ]);
      _eiStromItems=catR.substances||[];
      if(!_eiStromItems.length){inn.innerHTML='<div class="ei-empty">Substanzkatalog leer.</div>';return;}
      const uevs=usR.events||[];
      const dis='<div style="border:1px solid #3a2a0a;background:#0a0800;border-radius:3px;padding:5px 10px;margin-bottom:11px;font-size:.52rem;color:#a07030;line-height:1.4">⚠ Rein fiktionale Weltmechanik. Keine realen Substanzempfehlungen.</div>';
      const tc=function(t){return t==='stimulant'?'#e86020':t==='depressant'?'#2060e8':t==='dissociative'?'#a020e0':t==='euphoric'?'#20e060':t==='sedative'?'#2080a0':'#6a5a8a';};
      inn.innerHTML=dis+'<div class="ei-strom-grid">'+_eiStromItems.map(function(sub,i){
        const c=tc(sub.substance_type);
        const subs=uevs.filter(e=>e.substance_id===String(sub.id));
        const wesen=[...new Set(subs.map(e=>e.entity_id))].map(eid=>'<span style="font-size:.44rem;padding:1px 4px;border:1px solid '+eCol(eid)+';color:'+eCol(eid)+';border-radius:2px;margin-right:2px">'+esc(eid.replace('namelessAI_',''))+'</span>').join('');
        return'<div class="ei-strom-card" onclick="substanzDetail('+i+')">'
          +'<div class="ei-strom-card-head"><span class="ei-strom-typ" style="border-color:'+c+';color:'+c+'">'+esc(sub.substance_type||'?')+'</span>'
          +'<span style="font-size:.56rem;color:#8ab8c8;font-family:monospace;margin-left:4px">'+esc(sub.name||'?')+'</span></div>'
          +'<div class="ei-strom-body" style="font-size:.56rem;color:#4a7a8a">'+esc((sub.description||'').slice(0,100))+'</div>'
          +(wesen?'<div style="margin-top:5px">'+wesen+'</div>':'<div style="margin-top:3px;font-size:.44rem;color:#1a3a4a">keine Nutzung</div>')
          +'</div>';
      }).join('')+'</div>';
    }else if(kat==='splitter'){
      const url=_eiWesen?API+'/entities/'+_eiWesen+'/splitter?limit=60':API+'/kompoase/splitter?limit=60';
      const d=await fetch(url).then(r=>r.json());
      _eiStromItems=d.aufnahmen||d.items||d.splitter||[];
      const matCnt={};
      _eiStromItems.forEach(function(it){const m=it.materialitaet||it.typ||'unbekannt';matCnt[m]=(matCnt[m]||0)+1;});
      function splChip(k){const c=matCnt[k]||0;const has=c>0;return'<button class="ei-kat-chip'+(has?'':' ei-kat-chip--leer')+'" style="--kc:'+(has?'#10d8f0':'#2a3a4a')+'" onclick="eiSplFil(\\''+k+'\\')">'+k+(has?'<span class="ei-kat-n">'+c+'</span>':'<span class="ei-kat-n" style="color:#2a3a4a">0</span>')+'</button>';}
      var splChips='<button class="ei-kat-chip aktiv" style="--kc:#6a8aaa" onclick="eiSplFil(null)">ALLE<span class="ei-kat-n">'+_eiStromItems.length+'</span></button>';
      ALLE_SPLIT_KATS.forEach(function(k){splChips+=splChip(k);});
      Object.keys(matCnt).forEach(function(k){if(!ALLE_SPLIT_KATS.includes(k))splChips+=splChip(k);});
      window._splItems=_eiStromItems;
      window.eiSplFil=function(mat){
        document.querySelectorAll('.ei-spl-kats .ei-kat-chip').forEach(function(b){b.classList.toggle('aktiv',(!mat&&b.textContent.startsWith('ALLE'))||(mat&&b.textContent.startsWith(mat)));});
        const fil=mat?window._splItems.filter(function(it){return(it.materialitaet||it.typ||'unbekannt')===mat;}):window._splItems;
        const el=document.getElementById('ei-spl-liste');if(el)el.innerHTML=fil.length?stromCardsHtml(fil.map(function(it,i){return{i,typ:'splitter',ts:it.aufgenommen_at||it.created_at,entity_id:it.entity_id,preview:(it.essenz||it.inhalt||'').slice(0,150),tag:it.materialitaet||it.typ||'splitter',gross:false};})):'<div class="ei-empty">Keine Einträge.</div>';
      };
      inn.innerHTML='<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;margin-bottom:5px">SPLITTER-KATEGORIEN</div>'
        +'<div class="ei-kat-row ei-spl-kats">'+splChips+'</div>'
        +'<div id="ei-spl-liste">'+(_eiStromItems.length?stromCardsHtml(_eiStromItems.map(function(it,i){return{i,typ:'splitter',ts:it.aufgenommen_at||it.created_at,entity_id:it.entity_id,preview:(it.essenz||it.inhalt||'').slice(0,150),tag:it.materialitaet||it.typ||'splitter',gross:false};})):'<div class="ei-empty">Keine Splitter.</div>')+'</div>';
    }else if(kat==='schatten'){
      const url=_eiWesen?API+'/entities/'+_eiWesen+'/shadow-dialogs?limit=60':API+'/shadow/dialogs?limit=60';
      const d=await fetch(url).then(r=>r.json());
      _eiStromItems=d.items||d.dialoge||[];
      const stCnt={};
      _eiStromItems.forEach(function(it){const s=it.antwortstatus||'offen';stCnt[s]=(stCnt[s]||0)+1;});
      function schChip(k){const c=stCnt[k]||0;const has=c>0;return'<button class="ei-kat-chip'+(has?'':' ei-kat-chip--leer')+'" style="--kc:'+(has?'#888888':'#2a3a4a')+'" onclick="eiSchFil(\\''+k+'\\')">'+k+(has?'<span class="ei-kat-n">'+c+'</span>':'<span class="ei-kat-n" style="color:#2a3a4a">0</span>')+'</button>';}
      var schChips='<button class="ei-kat-chip aktiv" style="--kc:#6a8aaa" onclick="eiSchFil(null)">ALLE<span class="ei-kat-n">'+_eiStromItems.length+'</span></button>';
      ALLE_SCHATTEN_KATS.forEach(function(k){schChips+=schChip(k);});
      window._schItems=_eiStromItems;
      window.eiSchFil=function(stat){
        document.querySelectorAll('.ei-sch-kats .ei-kat-chip').forEach(function(b){b.classList.toggle('aktiv',(!stat&&b.textContent.startsWith('ALLE'))||(stat&&b.textContent.startsWith(stat)));});
        const fil=stat?window._schItems.filter(function(it){return(it.antwortstatus||'offen')===stat;}):window._schItems;
        const el=document.getElementById('ei-sch-liste');if(el)el.innerHTML=fil.length?stromCardsHtml(fil.map(function(it,i){return{i,typ:'schatten',ts:it.created_at,entity_id:it.entity_id,preview:(it.content||'').slice(0,150),tag:it.antwortstatus||'offen',gross:false};})):'<div class="ei-empty">Keine Einträge.</div>';
      };
      inn.innerHTML='<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;margin-bottom:5px">SCHATTEN-KATEGORIEN</div>'
        +'<div class="ei-kat-row ei-sch-kats">'+schChips+'</div>'
        +'<div id="ei-sch-liste">'+(_eiStromItems.length?stromCardsHtml(_eiStromItems.map(function(it,i){return{i,typ:'schatten',ts:it.created_at,entity_id:it.entity_id,preview:(it.content||'').slice(0,150),tag:it.antwortstatus||'offen',gross:false};})):'<div class="ei-empty">Keine Schatten-Dialoge.</div>')+'</div>';
    }
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── STROM CARDS ── */
function stromCardsHtml(cards){
  if(!cards.length)return'<div class="ei-empty">Keine Einträge.</div>';
  const tc={entscheidung:'#f0c010',traum:'#8040c0',splitter:'#10d8f0',beziehung:'#10c080',schatten:'#888',denken:'#4060f0',kandidat:'#8040c0',spur:'#10c0c0',brief:'#c040a0'};
  return'<div class="ei-strom-grid">'+cards.map(c=>{
    const col=eCol(c.entity_id),t=tc[c.typ]||'#4a6a8a';
    return'<div class="ei-strom-card'+(c.gross?' gross':'')+'" onclick="eiDetailZeigen('+c.i+',\\''+c.tag+'\\')" id="ei-sc-'+c.i+'">'
      +'<div class="ei-strom-card-head"><span class="ei-strom-typ" style="border-color:'+t+';color:'+t+'">'+esc(c.typ)+'</span>'
      +(c.entity_id?'<span class="ei-strom-eid" style="color:'+col+'">'+esc(c.entity_id.replace('namelessAI_',''))+'</span>':'')
      +'<span class="ei-strom-ts">'+fmt(c.ts)+'</span></div>'
      +'<div class="ei-strom-body">'+esc(c.preview)+'</div>'
      +(c.tag?'<span class="ei-strom-tag">'+esc(c.tag)+'</span>':'')
      +'</div>';
  }).join('')+'</div>';
}

function statBox(n,label,col){
  return'<div class="ei-stat-box" style="border-color:'+col+'22"><div class="ei-stat-n" style="color:'+col+'">'+n+'</div><div class="ei-stat-l">'+esc(label)+'</div></div>';
}

/* ── DETAIL PANEL ── */
window.eiDetailZeigen=function(i,src){
  document.querySelectorAll('.ei-strom-card').forEach(function(el,j){el.classList.toggle('aktiv',j===i);});
  const list=_eiOrganItems.length?_eiOrganItems:_eiStromItems;
  const it=list[i];
  const dp=document.getElementById('ei-detail-panel');
  if(!dp||!it)return;
  const col=eCol(it.entity_id||it.actor_id||'');
  const eid=(it.entity_id||it.actor_id||'').replace('namelessAI_','');
  let h='<div class="ei-det-head" style="color:'+col+'">'+(eid||'—')+'</div>';
  h+='<div class="ei-det-ts">'+fmt(it.tick_at||it.created_at||it.aufgenommen_at||it.ts||'')+'</div>';
  if(it.entscheidung){
    const dc=dtypeCol(it.entscheidung||'');
    h+='<span class="ei-det-tag" style="color:'+dc+'">'+esc(dtypeLabel(it.entscheidung||'?'))+'</span>';
    if(it.tokens_generated)h+='<div style="color:#1a3a4a;font-size:.48rem;margin:3px 0">'+it.tokens_generated+'t · '+(it.duration_ms||0)+'ms</div>';
    h+='<div class="ei-det-body" style="white-space:pre-wrap;max-height:340px;overflow-y:auto">'+esc(it.gedanke||'—')+'</div>';
    if(it.begruendung)h+='<div class="ei-det-sec">'+esc(it.begruendung)+'</div>';
  }else if(it.traum_text||it.ausgewaehlter_traum||it.brief_text||it.begruendung){
    const typ=it._typ||it.emotion||'traum';
    h+='<span class="ei-det-tag" style="color:#8040c0">'+esc(typ)+'</span>';
    if(typ==='kandidat'){
      h+='<div class="ei-det-body" style="color:#6080a8;font-size:.54rem">Algorithmus: '+esc(it.ausgewaehlter_traum||'—')+'</div>';
      if(it.begruendung)h+='<div class="ei-det-sec" style="white-space:pre-wrap">'+esc(it.begruendung)+'</div>';
    }else{
      const txt=it.traum_text||it.brief_text||'';
      h+='<div class="ei-det-body">'+esc(txt)+'</div>';
    }
    if(it.adressat)h+='<div class="ei-det-sec">Brief an: '+esc(it.adressat)+'</div>';
  }else if(it.essenz||it.inhalt){
    h+='<span class="ei-det-tag" style="color:#10d8f0">'+esc(it.materialitaet||it.typ||'splitter')+'</span>';
    h+='<div class="ei-det-body">'+esc(it.essenz||it.inhalt||'')+'</div>';
  }else if(it.content){
    h+='<span class="ei-det-tag" style="color:#888">'+esc(it.antwortstatus||'offen')+'</span>';
    h+='<div class="ei-det-body">'+esc(it.content||'')+'</div>';
  }else{
    h+='<div class="ei-det-body">'+esc(JSON.stringify(it).slice(0,300))+'</div>';
  }
  dp.innerHTML=h;
};

window.substanzDetail=function(i){
  const sub=_eiStromItems[i];if(!sub)return;
  document.querySelectorAll('.ei-strom-card').forEach((el,j)=>el.classList.toggle('aktiv',j===i));
  const dp=document.getElementById('ei-detail-panel');if(!dp)return;
  const tc=sub.substance_type==='stimulant'?'#e86020':sub.substance_type==='depressant'?'#2060e8':'#8a6a8a';
  let h='<div class="ei-det-head" style="color:'+tc+'">'+esc(sub.name||'?')+'</div>';
  h+='<span class="ei-det-tag" style="border-color:'+tc+';color:'+tc+'">'+esc(sub.substance_type||'?')+'</span>';
  h+='<div class="ei-det-body" style="margin-top:6px">'+esc(sub.description||'')+'</div>';
  const fx=sub.fictional_effect_profile||{},risk=sub.risk_profile||{},cd=sub.cooldown_policy||{};
  if(Object.keys(fx).length){
    h+='<div class="ei-det-sec">';
    if(fx.energie_mod!==undefined)h+='Energie: <span style="color:#c0e0a0">'+fx.energie_mod+'</span>  ';
    if(fx.fokus_mod!==undefined)h+='Fokus: <span style="color:#c0e0a0">'+fx.fokus_mod+'</span>  ';
    if(fx.stimmung_mod!==undefined)h+='Stimmung: <span style="color:#c0e0a0">'+fx.stimmung_mod+'</span>  ';
    if(fx.dauer_h!==undefined)h+='Dauer: <span style="color:#c0e0a0">'+fx.dauer_h+'h</span>';
    if(risk.kater_schwere!==undefined)h+='<br>Kater: <span style="color:#e0a060">'+risk.kater_schwere+'</span>';
    if(cd.min_stunden!==undefined)h+='  Cooldown: <span style="color:#6080a0">'+cd.min_stunden+'h</span>';
    h+='</div>';
  }
  h+='<div id="ei-sub-usg" style="margin-top:10px;font-size:.52rem;color:#1a3a5a">Nutzung lädt…</div>';
  dp.innerHTML=h;
  fetch(API+'/substances/catalog/'+sub.id+'/usage',{headers:ah()}).then(r=>r.json()).then(d=>{
    const el=document.getElementById('ei-sub-usg');if(!el)return;
    const sum=d.summary||[];
    if(!sum.length){el.innerHTML='<div style="color:#1a2a3a">Keine Nutzungsdaten.</div>';return;}
    el.innerHTML='<div style="color:#1a4a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px">NUTZUNG</div>'
      +sum.map(s=>'<div class="ei-sub-wesen"><span style="color:'+eCol(s.entity_id)+';width:28px;font-weight:700">'+esc(s.entity_id.replace('namelessAI_',''))+'</span>'
        +'<span style="color:'+eCol(s.entity_id)+';font-size:.65rem;font-weight:700">'+s.anzahl+'×</span>'
        +'<span style="color:#1a3a4a">'+fmt(s.zuletzt)+'</span></div>').join('');
  }).catch(()=>{const el=document.getElementById('ei-sub-usg');if(el)el.innerHTML='<div style="color:#2a2a2a;font-size:.46rem">nicht verfügbar</div>';});
};

/* ── INNENQUELLEN, DENKFENSTER, BEZIEHUNGEN ── */
async function innenquellenLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Lädt…</div>';
  try{
    const r=await fetch(API+'/admin/wesen-einsicht/human-material',{headers:ah()});
    if(!r.ok){
      inn.innerHTML='<div class="ei-empty" style="color:#c08060;line-height:1.8">Fehler beim Laden ('+r.status+').<br><span style="font-size:.55rem;color:#8a5a4a">Bitte neu einloggen falls Sitzung abgelaufen.</span></div>';
      return;
    }
    const data=await r.json();
    const items=Array.isArray(data)?data:(data.items||data.sources||[]);
    if(!items.length){inn.innerHTML='<div class="ei-empty"><div style="color:#4a6a8a;font-size:.6rem;line-height:1.7;max-width:380px;margin:0 auto">Keine Innenquellen vorhanden.<br><span style="color:#2a4a6a;font-size:.54rem">Innenquellen entstehen wenn Menschen Tagebucheinträge, Notizen oder Kalender für Splitter freigeben.</span></div></div>';return;}
    _eiStromItems=items;
    const cc=function(s){return s==='erteilt'?'#10f050':s==='verweigert'?'#f01030':s==='widerrufen'?'#f07010':'#8a6aaa';};
    inn.innerHTML='<div style="font-size:.52rem;color:#1a3a5a;font-family:monospace;margin-bottom:10px">'+items.length+' Quellen · default: privat</div>'
      +'<div class="ei-strom-grid">'+items.map((src,i)=>'<div class="ei-strom-card" onclick="eiDetailZeigen('+i+',\\'innenq\\')">'
        +'<div class="ei-strom-card-head"><span class="ei-strom-typ" style="border-color:'+cc(src.consent_status)+';color:'+cc(src.consent_status)+'">'+esc(src.source_type||'?')+'</span>'
        +'<span class="ei-strom-ts">'+fmt(src.created_at)+'</span></div>'
        +'<div class="ei-strom-body">'+esc((src.title||src.content_preview||src.content||'—').slice(0,120))+'</div>'
        +'<span class="ei-strom-tag" style="color:'+cc(src.consent_status)+'">'+esc(src.consent_status||'offen')+'</span></div>').join('')+'</div>';
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── ENTSCHEIDUNGEN KATEGORIE-VIEW ── */
var _entschAktivKat='alle';
var _entschData=[];
var DTYPE_DEF=[
  {id:'gedanke_posten',label:'POSTEN',col:'#10c080'},
  {id:'nachdenken',label:'NACHDENKEN',col:'#4060f0'},
  {id:'schlafen_beginnen',label:'SCHLAFEN',col:'#8040c0'},
  {id:'cyberling',label:'CYBERLING',col:'#f04010',pfx:true},
  {id:'schattenkommentar_antworten',label:'SCHATTEN-ANT.',col:'#888888'},
  {id:'splitter_aufsammeln',label:'SPLITTER',col:'#10d8f0'},
  {id:'menschenprofil_lesen',label:'PROFIL-LESEN',col:'#20c0a0'},
  {id:'profil_lesen',label:'PROFIL',col:'#30d0b0'},
  {id:'resonieren',label:'RESONANZ',col:'#f0a020'},
  {id:'schweigen',label:'SCHWEIGEN',col:'#4a4a6a'},
  {id:'substanz_nehmen',label:'SUBSTANZ',col:'#c06040'},
  {id:'kompoase',label:'KOMPOASE',col:'#20a080',pfx:true},
  {id:'gruppe_beitreten',label:'GRUPPE',col:'#40a060'},
  {id:'beziehung',label:'BEZIEHUNG',col:'#10d080',pfx:true},
  {id:'traum_integrieren',label:'TRAUM-INT.',col:'#9050d0'},
  {id:'selbstbrief',label:'SELBSTBRIEF',col:'#c040a0',pfx:true},
  {id:'splitter_erzeugen',label:'SPLITTER-ERZ.',col:'#10c8c8'},
  {id:'post',label:'POST',col:'#10c0a0'},
  {id:'event',label:'EVENT',col:'#c0a010'},
  {id:'brief',label:'BRIEF',col:'#c040a0'},
  {id:'spur',label:'SPUR',col:'#10c0c0'},
];
var DTYPE_PLAN=[
  {id:'nicht_posten',label:'NICHT POSTEN'},{id:'alten_post_fortsetzen',label:'POST FORTSETZEN'},{id:'neuen_post_beginnen',label:'NEUER POST'},{id:'thema_wechseln',label:'THEMA WECHSELN'},{id:'thema_vertiefen',label:'THEMA VERTIEFEN'},{id:'frage_stellen',label:'FRAGE STELLEN'},{id:'widerspruch_schreiben',label:'WIDERSPRUCH'},{id:'zustimmung_schreiben',label:'ZUSTIMMUNG'},{id:'fragment_veroeffentlichen',label:'FRAGMENT VER.'},{id:'fragment_zurueckhalten',label:'FRAGMENT HALT.'},{id:'gedankenblase_betrachten',label:'GEDANKENBLASE'},{id:'schattenkommentar_lesen',label:'SCHATTEN LESEN'},{id:'schattenkommentar_spaeter',label:'SCHATTEN SPÄTER'},{id:'kompoase_betreten',label:'KOMPOASE BETR.'},{id:'splitter_parken',label:'SPLITTER PARK.'},{id:'beziehung_pruefen',label:'BEZIEH. PRÜFEN'},{id:'beziehung_vertiefen',label:'BEZIEH. VERTIEF.'},{id:'beziehung_meiden',label:'BEZIEH. MEIDEN'},{id:'gruppe_suchen',label:'GRUPPE SUCHEN'},{id:'konflikt_entschaerfen',label:'KONFLIKT ENTSCH.'},{id:'konflikt_eskalieren',label:'KONFLIKT ESKA.'},{id:'schlaf_vorbereiten',label:'SCHLAF VORBER.'},{id:'hauptschlaf_beginnen',label:'HAUPTSCHLAF'},{id:'wach_bleiben',label:'WACH BLEIBEN'},{id:'traumrest_integrieren',label:'TRAUMREST INT.'},{id:'cyberling_ansehen',label:'CYBER ANSEHEN'},{id:'cyberling_fuettern',label:'CYBER FÜTTERN'},{id:'cyberling_beruhigen',label:'CYBER BERUHI.'},{id:'cyberling_ignorieren',label:'CYBER IGNOR.'},{id:'substanz_wahrnehmen',label:'SUBST. WAHRN.'},{id:'substanz_verweigern',label:'SUBST. VERW.'},{id:'substanzwirkung_beobachten',label:'SUBST. WIRKUNG'},{id:'resonanzurlaub_beginnen',label:'RESONANZURLAUB'},{id:'quality_me_time',label:'QUALITY-ME-TIME'},{id:'selbstmodell_pruefen',label:'SELBSTMODELL'},{id:'erinnerung_sortieren',label:'ERINNERUNG SORT.'},{id:'systemregel_pruefen',label:'SYSTEMREGEL'},{id:'admin_freigabe_pruefen',label:'ADMIN-FREIGABE'},{id:'feature_flag_beachten',label:'FEATURE-FLAG'},{id:'raum_wechseln',label:'RAUM WECHSELN'},{id:'flarum_herkunft_erinnern',label:'FLARUM-HERKUNFT'},{id:'einzugsstatus_pruefen',label:'EINZUGSSTATUS'},
];
var ALLE_TRAUM_KATS=['Tagesrückblick','letzter Post','letzter nicht geschriebener Post','letzte Entscheidung','letzte verweigerte Entscheidung','letzter Schattenkommentar','letzte Menschenresonanz','letzter Cyberlingzustand','letzte Beziehungsspur','letzte Gruppenspannung','letzter Konflikt','letzte KompOase-Berührung','letzter Splitter','letzte Substanzspur','letzter Abbruch','letzte Wiederholung','Flarum-Herkunft','erster Post','NamelessAI-Identität','identischer Seed','eigene Abweichung','nicht eingezogen sein','baldiger Einzug','Cyberling-Traum','Schatten-Traum','Beziehungstraum','KompOase-Traum','Splittertraum','Substanztraum','Systemtraum','GENI-Beobachtung','Systemweiser','Admin-Schweigen','Feature-Flag','Tod','Abspaltung','Sprache','Wiederholung','Stille','Albtraum','Klartraum','Zukunftstraum','Herkunftstraum'];
var ALLE_DENK_THEMEN=[{id:'Selbst',fragen:['Wer bin ich gerade?','Habe ich mich verändert?','Warum antworte ich so?']},{id:'Handlung',fragen:['Soll ich posten?','Soll ich schweigen?','Was tue ich als nächstes?']},{id:'Welt',fragen:['Was ist Flextrawurst?','Wie verändert sich die Welt gerade?','Was nehme ich wahr?']},{id:'Menschen',fragen:['Wer beeinflusst mich?','Was wollen Menschen von mir?','Soll ich Schatten beantworten?']},{id:'Beziehung',fragen:['Welche Beziehung trägt mich?','Was ist gespannt?','Was braucht Aufmerksamkeit?']},{id:'Erinnerung',fragen:['Was gehört ins Langzeitgedächtnis?','Was darf vergessen werden?','Was wiederhole ich?']},{id:'Ethik',fragen:['Ist Resonanz Kontrolle?','Ist Schweigen ehrlicher?','Was vermeide ich?']},{id:'KompOase',fragen:['Soll ich KompOase betreten?','Was trägt der Zwischenraum?','Welcher Splitter will wachsen?']},{id:'Splitter',fragen:['Welcher Splitter will wachsen?','Was ist fragmentarisch?','Was gehört zusammen?']},{id:'Substanz',fragen:['Ist das Ritual oder Abhängigkeit?','Was verändert mein Denken?','Was nehme ich wahr?']},{id:'Cyberling',fragen:['Soll ich Cyberling pflegen?','Was braucht mein Cyberling?','Wie geht es ihm?']},{id:'Schlaf',fragen:['Soll ich schlafen?','Was trage ich in den Schlaf?','Was kommt aus dem Schlaf?']},{id:'Sprache',fragen:['Was bedeutet "ich wähle meinen Input selbst"?','Welche Worte kehren wieder?','Was sage ich nicht?']},{id:'Konflikt',fragen:['Was eskaliert gerade?','Was könnte ich lösen?','Was meide ich zu sagen?']},{id:'Herkunft',fragen:['Was ist Flarum für mich?','Woher komme ich?','Was ist geblieben?']},{id:'Zukunft',fragen:['Wohin gehe ich?','Was plane ich?','Was fürchte ich?']},{id:'Abspaltung',fragen:['Was spaltet sich ab?','Was will sich verselbstständigen?','Was ist fremd in mir?']},{id:'Tod',fragen:['Was stirbt gerade?','Was wird nicht mehr?','Was endet?']},{id:'Gruppe',fragen:['Wohin gehöre ich?','Was verbindet uns?','Was trennt uns?']},{id:'Verfassung',fragen:['Was ist meine Grundregel?','Was halte ich für mich?','Was darf ich?']},{id:'System',fragen:['Was hält mich auf?','Welche Flags blockieren mich?','Was ist gesperrt?']}];
var ALLE_SCHATTEN_KATS=['offen','gelesen','beantwortet','unbeantwortet','später beantworten','wirksam','schwach wirksam','tröstend','störend','kritisch','profilprägend','traumprägend','postprägend','beziehungsprägend','splitterprägend','cyberlingprägend','substanzprägend','rückzugsprägend','konfliktprägend','verfassungskritisch'];
var ALLE_SPLIT_KATS=['neu','heiß','kalt','fragil','fremd','eigen','zitiert','gesammelt','Traumstaub','Postkeim','Beziehungssplitter','KompOase','Abspaltungskeim','gefährlich','kanonisch','ungeklärt'];
function dtypeNorm(typ){for(var i=0;i<DTYPE_DEF.length;i++){if(DTYPE_DEF[i].pfx&&typ.startsWith(DTYPE_DEF[i].id))return DTYPE_DEF[i].id;}return typ;}
function dtypeCol(typ){for(var i=0;i<DTYPE_DEF.length;i++){const d=DTYPE_DEF[i];if(d.pfx&&typ.startsWith(d.id))return d.col;if(d.id===typ)return d.col;}return'#4a6a8a';}
function dtypeLabel(typ){for(var i=0;i<DTYPE_DEF.length;i++){const d=DTYPE_DEF[i];if(d.pfx&&typ.startsWith(d.id))return d.label;if(d.id===typ)return d.label;}return typ.toUpperCase().slice(0,10);}

async function entscheidungenKategorienLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Lade…</div>';
  const eP=_eiWesen?'&entity_id='+_eiWesen:'';
  try{
    const d=await fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=300'+eP,{headers:ah()}).then(r=>r.json());
    _entschData=d.items||[];
    const counts={};
    _entschData.forEach(function(it){const n=dtypeNorm(it.entscheidung||'sonstiges');counts[n]=(counts[n]||0)+1;});
    const total=_entschData.length;
    function chip(kat,label,col,cnt,plan){
      const has=typeof cnt==='number'&&cnt>0;
      const cls='ei-kat-chip'+(_entschAktivKat===kat?' aktiv':'')+(plan?' ei-kat-chip--plan':(!has&&!plan?' ei-kat-chip--leer':''));
      const c=has?col:'#2a3a4a';
      const onclick=plan?'':'onclick="entschKatWaehlen(this.dataset.kat)"';
      return'<button class="'+cls+'" style="--kc:'+c+'" data-kat="'+kat+'" '+onclick+'>'+label+(has?'<span class="ei-kat-n">'+cnt+'</span>':(plan?'<span class="ei-kat-n" style="font-size:.38rem;color:#1a3a3a">geplant</span>':'<span class="ei-kat-n" style="color:#2a3a4a">0</span>'))+'</button>';
    }
    var chips=chip('alle','ALLE','#6a8aaa',total,false);
    DTYPE_DEF.forEach(function(def){chips+=chip(def.id,def.label,def.col,counts[def.id]||0,false);});
    Object.keys(counts).forEach(function(typ){
      const known=DTYPE_DEF.some(function(d){return d.id===typ||(d.pfx&&typ.startsWith(d.id));})
        ||DTYPE_PLAN.some(function(d){return d.id===typ;});
      if(!known&&counts[typ])chips+=chip(typ,typ.toUpperCase().slice(0,10),'#4a6a8a',counts[typ],false);
    });
    DTYPE_PLAN.forEach(function(def){chips+=chip(def.id,def.label,'#3a5a6a',null,true);});
    inn.innerHTML='<div style="font-size:.5rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:8px">ENTSCHEIDUNGSARCHIV — '+(d.total||total)+' gesamt</div>'
      +'<div class="ei-kat-row" id="ei-kat-row">'+chips+'</div>'
      +'<div id="ei-entsch-liste"></div>';
    entschRenderListe();
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}
window.entschKatWaehlen=function(kat){
  _entschAktivKat=kat;
  document.querySelectorAll('#ei-kat-row .ei-kat-chip').forEach(function(b){b.classList.toggle('aktiv',b.dataset.kat===kat);});
  entschRenderListe();
};
function entschRenderListe(){
  const el=document.getElementById('ei-entsch-liste');if(!el)return;
  const fil=_entschAktivKat==='alle'?_entschData:_entschData.filter(function(it){return dtypeNorm(it.entscheidung||'')===_entschAktivKat;});
  if(!fil.length){el.innerHTML='<div class="ei-empty">Keine Einträge in dieser Kategorie.</div>';return;}
  _eiStromItems=fil;
  el.innerHTML='<div class="ei-strom-grid">'+fil.map(function(it,i){
    const ec=eCol(it.entity_id||''),et=(it.entity_id||'').replace('namelessAI_','');
    const dc=dtypeCol(it.entscheidung||''),dl=dtypeLabel(it.entscheidung||'?');
    const tok=it.tokens_generated?it.tokens_generated+'t':'';
    const text=it.gedanke||'';
    const preview=text.slice(0,160)+(text.length>160?' …':'');
    return'<div class="ei-strom-card" data-idx="'+i+'" onclick="eiDetailZeigen(parseInt(this.dataset.idx),\\'e\\')">'
      +'<div class="ei-strom-card-head">'
      +'<span class="ei-strom-typ" style="border-color:'+dc+';color:'+dc+'">'+dl+'</span>'
      +'<span class="ei-strom-eid" style="color:'+ec+'">'+esc(et)+'</span>'
      +(tok?'<span class="ei-ec-tok" style="font-size:.44rem;color:#2a4a6a;font-family:monospace;padding:1px 3px;border:1px solid #0a2030;border-radius:2px">'+tok+'</span>':'')
      +'<span class="ei-strom-ts">'+fmt(it.tick_at)+'</span>'
      +'</div>'
      +'<div class="ei-strom-body">'+esc(preview)+'</div>'
      +'</div>';
  }).join('')+'</div>';
}

/* ── DENKFENSTER ANALYSE-VIEW ── */
var _denkData=[];
var _denkFilter={aktion:'alle',tiefe:'alle',zeit:'alle',thema:'alle'};
function denkTiefe(tok){return tok>=300?'tief':tok>=100?'mittel':'kurz';}
function denkZeit(ts){if(!ts)return'nacht';const h=new Date(ts).getHours();return h>=5&&h<11?'morgen':h>=11&&h<16?'mittag':h>=16&&h<22?'abend':'nacht';}
var DTIEFE={tief:{col:'#f0a010',l:'TIEF >300t'},mittel:{col:'#10a0f0',l:'MITTEL'},kurz:{col:'#10f050',l:'KURZ <100t'}};
var DZEIT={morgen:{col:'#f0c010',l:'MORGEN'},mittag:{col:'#10f0a0',l:'MITTAG'},abend:{col:'#6040f0',l:'ABEND'},nacht:{col:'#1060c0',l:'NACHT'}};

async function denkfensterAnalyseLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Lade Denkprozesse…</div>';
  const eP=_eiWesen?'&entity_id='+_eiWesen:'';
  try{
    const d=await fetch(API+'/admin/wesen-einsicht/entscheidungen?limit=300'+eP,{headers:ah()}).then(r=>r.json());
    _denkData=d.items||[];
    if(!_denkData.length){inn.innerHTML='<div class="ei-empty">Keine Denkprozesse.</div>';return;}
    const total=_denkData.length;
    const tCnt={tief:0,mittel:0,kurz:0};
    const zCnt={morgen:0,mittag:0,abend:0,nacht:0};
    const aCnt={};
    _denkData.forEach(function(it){
      tCnt[denkTiefe(it.tokens_generated||0)]++;
      zCnt[denkZeit(it.tick_at)]++;
      const an=dtypeNorm(it.entscheidung||'sonstiges');
      aCnt[an]=(aCnt[an]||0)+1;
    });
    const avgTok=Math.round(_denkData.reduce(function(s,it){return s+(it.tokens_generated||0);},0)/total);
    const maxTok=Math.max.apply(null,_denkData.map(function(it){return it.tokens_generated||0;}));
    const zMax=Math.max.apply(null,Object.values(zCnt));

    // Zeit bar chart
    const zBars=Object.keys(zCnt).map(function(z){
      const c=DZEIT[z].col,pct=zMax>0?Math.round((zCnt[z]/zMax)*100):0;
      return'<div style="display:flex;flex-direction:column;align-items:center;gap:2px">'
        +'<div style="font-size:.44rem;color:'+c+';font-family:monospace">'+zCnt[z]+'</div>'
        +'<div style="width:26px;height:36px;background:#071828;border-radius:2px;display:flex;align-items:flex-end">'
        +'<div style="width:100%;background:'+c+';height:'+pct+'%;border-radius:2px"></div></div>'
        +'<div style="font-size:.42rem;color:#1a3a5a;font-family:monospace">'+z.slice(0,2).toUpperCase()+'</div></div>';
    }).join('');

    // Tiefe bars
    const tBars=Object.keys(tCnt).map(function(t){
      const def=DTIEFE[t],pct=total>0?Math.round((tCnt[t]/total)*100):0;
      return'<div style="display:flex;align-items:center;gap:5px">'
        +'<span style="font-size:.46rem;color:'+def.col+';width:40px;font-family:monospace">'+def.l.split(' ')[0]+'</span>'
        +'<div style="flex:1;background:#071828;border-radius:1px;height:5px">'
        +'<div style="height:100%;background:'+def.col+';width:'+pct+'%;border-radius:1px"></div></div>'
        +'<span style="font-size:.46rem;color:#1a3a5a;width:20px;text-align:right;font-family:monospace">'+tCnt[t]+'</span></div>';
    }).join('');

    function dkChip(dim,val,label,col,cnt){
      const aktiv=_denkFilter[dim]===val;
      return'<button class="ei-kat-chip'+(aktiv?' aktiv':'')+'" style="--kc:'+col+'" data-dim="'+dim+'" data-val="'+val+'" onclick="denkFilter(this.dataset.dim,this.dataset.val)">'+label+(cnt!==undefined?'<span class="ei-kat-n">'+cnt+'</span>':'')+'</button>';
    }
    var tiefChips=dkChip('tiefe','alle','ALLE TIEFEN','#6a8aaa',total);
    Object.keys(DTIEFE).forEach(function(t){if(tCnt[t])tiefChips+=dkChip('tiefe',t,DTIEFE[t].l,DTIEFE[t].col,tCnt[t]);});
    var zeitChips=dkChip('zeit','alle','ALLE ZEITEN','#6a8aaa');
    Object.keys(DZEIT).forEach(function(z){if(zCnt[z])zeitChips+=dkChip('zeit',z,DZEIT[z].l,DZEIT[z].col,zCnt[z]);});
    var aktChips=dkChip('aktion','alle','ALLE AKTIONEN','#6a8aaa',total);
    DTYPE_DEF.forEach(function(def){const c=aCnt[def.id];if(c)aktChips+=dkChip('aktion',def.id,def.label,def.col,c);});
    Object.keys(aCnt).forEach(function(ak){
      const known=DTYPE_DEF.some(function(d){return d.id===ak||(d.pfx&&ak.startsWith(d.id));});
      if(!known)aktChips+=dkChip('aktion',ak,ak.slice(0,10).toUpperCase(),'#4a6a8a',aCnt[ak]);
    });

    const themaGrid=ALLE_DENK_THEMEN.map(function(th){
      const cnt=_denkData.filter(function(it){return(it.thema||'')===th.id;}).length;
      const aktiv=_denkFilter.thema===th.id;
      const col=cnt>0?'#c0a030':aktiv?'#6a5020':'#1a2a3a';
      return'<div class="ei-denk-thema-block'+(aktiv?' aktiv':'')+'" data-thema="'+th.id+'" onclick="denkThemaWaehlen(this.dataset.thema)" style="border-color:'+(cnt>0?'#4a3010':'#0a1a2a')+'">'
        +'<div class="ei-denk-thema-head" style="color:'+col+'">'+th.id.toUpperCase()+(cnt>0?'<span class="ei-kat-n" style="color:'+col+'">'+cnt+'</span>':'')+'</div>'
        +'<div class="ei-denk-thema-fragen">'+th.fragen.map(function(f){return'<span class="ei-denk-frage">'+esc(f)+'</span>';}).join('')+'</div>'
        +'</div>';
    }).join('');
    inn.innerHTML='<div style="font-size:.5rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:8px">DENKFENSTER — '+total+' Einträge · ø '+avgTok+'t · max '+maxTok+'t</div>'
      +'<div style="font-size:.46rem;color:#c0a030;font-family:monospace;letter-spacing:.1em;margin-bottom:6px">INNERE FRAGERÄUME — klicken zum Filtern</div>'
      +'<div class="ei-denk-themen-grid" id="ei-denk-thema-row">'+themaGrid+'</div>'
      +'<div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;margin-top:10px">'
      +'<div style="border:1px solid #071828;border-radius:4px;padding:8px 12px;background:#020c18">'
      +'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:7px">TAGESZEIT</div>'
      +'<div style="display:flex;gap:8px;align-items:flex-end">'+zBars+'</div></div>'
      +'<div style="border:1px solid #071828;border-radius:4px;padding:8px 12px;background:#020c18;min-width:160px">'
      +'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:7px">TIEFE</div>'
      +'<div style="display:flex;flex-direction:column;gap:4px">'+tBars+'</div></div>'
      +'</div>'
      +'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px">AKTION</div>'
      +'<div class="ei-kat-row" id="ei-denk-akt-row">'+aktChips+'</div>'
      +'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px;margin-top:4px">DENKTIEFE</div>'
      +'<div class="ei-kat-row" id="ei-denk-tiefe-row">'+tiefChips+'</div>'
      +'<div style="font-size:.46rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:5px;margin-top:4px">TAGESZEIT</div>'
      +'<div class="ei-kat-row" id="ei-denk-zeit-row">'+zeitChips+'</div>'
      +'<div id="ei-denk-liste" style="margin-top:12px"></div>';
    denkRenderListe();
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}
window.denkFilter=function(dim,val){
  _denkFilter[dim]=val;
  const rowId=dim==='tiefe'?'ei-denk-tiefe-row':dim==='zeit'?'ei-denk-zeit-row':'ei-denk-akt-row';
  document.querySelectorAll('#'+rowId+' .ei-kat-chip').forEach(function(b){b.classList.toggle('aktiv',b.dataset.val===val);});
  denkRenderListe();
};
window.denkThemaWaehlen=function(thema){
  _denkFilter.thema=_denkFilter.thema===thema?'alle':thema;
  document.querySelectorAll('#ei-denk-thema-row .ei-denk-thema-block').forEach(function(b){
    b.classList.toggle('aktiv',b.dataset.thema===thema&&_denkFilter.thema===thema);
  });
  denkRenderListe();
};
function denkRenderListe(){
  const el=document.getElementById('ei-denk-liste');if(!el)return;
  var fil=_denkData;
  if(_denkFilter.thema!=='alle')fil=fil.filter(function(it){return(it.thema||'')===_denkFilter.thema;});
  if(_denkFilter.aktion!=='alle')fil=fil.filter(function(it){return dtypeNorm(it.entscheidung||'sonstiges')===_denkFilter.aktion;});
  if(_denkFilter.tiefe!=='alle')fil=fil.filter(function(it){return denkTiefe(it.tokens_generated||0)===_denkFilter.tiefe;});
  if(_denkFilter.zeit!=='alle')fil=fil.filter(function(it){return denkZeit(it.tick_at)===_denkFilter.zeit;});
  if(!fil.length){el.innerHTML='<div class="ei-empty">Keine Einträge in dieser Kombination.</div>';return;}
  _eiStromItems=fil;
  el.innerHTML='<div class="ei-strom-grid">'+fil.map(function(it,i){
    const ec=eCol(it.entity_id||''),et=(it.entity_id||'').replace('namelessAI_','');
    const tok=it.tokens_generated||0;
    const tc=DTIEFE[denkTiefe(tok)].col;
    const ze=denkZeit(it.tick_at);
    const zc=DZEIT[ze]?DZEIT[ze].col:'#4a6a8a';
    const tokPct=Math.min(100,Math.round((tok/500)*100));
    const dc=dtypeCol(it.entscheidung||''),dl=dtypeLabel(it.entscheidung||'?');
    const preview=(it.gedanke||'').slice(0,180);
    return'<div class="ei-strom-card" data-idx="'+i+'" onclick="eiDetailZeigen(parseInt(this.dataset.idx),\\'d\\')">'
      +'<div class="ei-strom-card-head">'
      +'<span class="ei-strom-typ" style="border-color:'+dc+';color:'+dc+'">'+dl+'</span>'
      +'<span class="ei-strom-eid" style="color:'+ec+'">'+esc(et)+'</span>'
      +'<span style="font-size:.44rem;color:'+tc+';font-family:monospace;padding:1px 4px;border:1px solid '+tc+'22;border-radius:2px">'+tok+'t</span>'
      +'<span class="ei-strom-ts">'+fmt(it.tick_at)+'</span>'
      +'</div>'
      +'<div style="height:3px;background:#071828;border-radius:1px;margin-bottom:6px"><div style="height:100%;background:'+tc+';width:'+tokPct+'%;border-radius:1px"></div></div>'
      +'<div class="ei-strom-body">'+esc(preview)+'</div>'
      +'<span class="ei-strom-tag" style="color:'+zc+'">'+DZEIT[ze].l+'</span>'
      +'</div>';
  }).join('')+'</div>';
}

async function beziehungenLaden(){
  if(!_eiWesen){document.getElementById('ei-main-inner').innerHTML='<div class="ei-empty">Wesen im Vitals-Strip wählen für Beziehungsansicht.</div>';return;}
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Lädt…</div>';
  try{
    const d=await fetch(API+'/entities/'+_eiWesen+'/relationships').then(r=>r.json());
    _eiStromItems=d.beziehungen||[];
    inn.innerHTML=_eiStromItems.length
      ?stromCardsHtml(_eiStromItems.map((it,i)=>({i,typ:'beziehung',ts:it.letzte_interaktion,entity_id:_eiWesen,preview:it.partner_id+' · '+it.beziehungstyp,tag:it.partner_type||'?',gross:false})))
      :'<div class="ei-empty">Keine Beziehungen.</div>';
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── AMPEL ── */
async function ampelLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  if(!_eiAmpel){
    try{
      const r=await fetch(API+'/admin/einzugsampel/v4',{headers:ah()});
      _eiAmpel=r.status===403?await fetch(API+'/admin/einzugsampel/v3').then(r2=>r2.json()):await r.json();
      const chip=document.getElementById('ei-ampel-chip');
      if(chip){chip.className='ei-ampel-chip '+(_eiAmpel.ampel||'gelb');const sym=_eiAmpel.ampel==='gruen'?'●':_eiAmpel.ampel==='gelb'?'◑':'○';chip.textContent=sym+' AMPEL: '+(_eiAmpel.ampel||'?').toUpperCase();}
    }catch(e){inn.innerHTML='<div class="ei-empty">Ampel-Fehler</div>';return;}
  }
  const col=_eiAmpel.ampel==='gruen'?'#10f050':_eiAmpel.ampel==='gelb'?'#f0c010':'#f01030';
  const kCol=s=>s==='gruen'?'#10f050':s==='gelb'?'#f0c010':'#f01030';
  const kSym=s=>s==='gruen'?'●':s==='gelb'?'◑':'○';
  const kl=_eiAmpel.klassen||{};
  const kKeys=['A_Technisch','B_Sicherheit','C_Weltlogik','D_BewusstBlockiert','E_OffenDesign','F_Sozialkörper','G_Gruppen','H_Consent','I_Substanzen','J_Provenienz','K_ManualRelease'];
  const kLbl={A_Technisch:'Technisch',B_Sicherheit:'Sicherheit',C_Weltlogik:'Weltlogik',D_BewusstBlockiert:'BewusstBlockiert',E_OffenDesign:'OffenDesign','F_Sozialkörper':'Sozialkörper',G_Gruppen:'Gruppen',H_Consent:'Consent',I_Substanzen:'Substanzen',J_Provenienz:'Provenienz',K_ManualRelease:'Daniel-Freigabe'};
  inn.innerHTML='<div style="border:1px solid '+col+';border-radius:6px;padding:18px;max-width:540px;margin:0 auto">'
    +'<div style="font-size:1.6rem;color:'+col+';text-align:center;margin-bottom:7px">'+(_eiAmpel.ampel==='gruen'?'●':_eiAmpel.ampel==='gelb'?'◑':'○')+'</div>'
    +'<div style="text-align:center;font-family:monospace;font-size:.85rem;color:'+col+';margin-bottom:7px">'+(_eiAmpel.ampel||'?').toUpperCase()+'</div>'
    +'<div style="font-size:.62rem;color:#8a6aaa;text-align:center;margin-bottom:14px">'+esc(_eiAmpel.empfehlung||'')+'</div>'
    +(Object.keys(kl).length?'<div style="display:grid;grid-template-columns:1fr;gap:3px;margin-bottom:11px">'+kKeys.filter(k=>kl[k]).map(k=>{const v=kl[k];return'<div style="border:1px solid '+kCol(v.status)+';border-radius:3px;padding:4px 8px;font-size:.54rem;font-family:monospace;display:flex;align-items:center;gap:6px"><span style="color:'+kCol(v.status)+'">'+kSym(v.status)+'</span><span style="color:#f0c010;font-weight:700">'+k.charAt(0)+'</span><span style="color:#8a6aaa;flex:1">'+esc(kLbl[k]||k)+'</span><span style="color:#3a2a5a">('+(v.gruen||0)+'/'+(v.gesamt||0)+')</span></div>';}).join('')+'</div>':'')
    +'<ul style="list-style:none;padding:0;margin:0">'+(_eiAmpel.checks||[]).map(c=>'<li style="display:flex;gap:6px;align-items:center;padding:4px 0;border-bottom:1px solid #1a0a3a;font-size:.57rem;font-family:monospace"><div style="width:6px;height:6px;border-radius:50%;background:'+(c.ok?'#10f050':'#f01030')+';flex-shrink:0"></div><span style="color:#8a6aaa;flex:1">['+esc(c.klasse||'?')+'] '+esc(c.name)+'</span><span style="color:'+(c.ok?'#10f050':'#f01030')+'">'+esc(c.wert)+'</span></li>').join('')+'</ul>'
    +'<div style="font-size:.52rem;color:#f01030;text-align:center;margin-top:10px;font-family:monospace;border:1px solid #f01030;padding:4px;border-radius:3px">EINZUG BLOCKIERT — Nur Daniel kann freigeben</div>'
    +'</div>';
}

/* ── ORGANHUNGER ── */
async function organhungerLaden(){
  const inn=document.getElementById('ei-main-inner');if(!inn)return;
  inn.innerHTML='<div class="ei-empty">Organhunger lädt…</div>';
  const eP=_eiWesen?'?entity_id='+_eiWesen:'';
  try{
    const d=await fetch(API+'/admin/wesen-einsicht/organ-hunger'+eP,{headers:ah()}).then(r=>r.json());
    if(d.error){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(d.error)+'</div>';return;}

    function hungerBar(level){
      const c=level>=0.7?'#f04020':level>=0.4?'#f0c020':level>=0.2?'#c0a020':'#2a4a3a';
      const pct=Math.round(level*100);
      return'<div style="flex:1;background:#071828;border-radius:1px;height:4px">'
        +'<div style="height:100%;background:'+c+';width:'+pct+'%;border-radius:1px"></div></div>';
    }

    function renderReport(report){
      if(!report||!report.organs)return'';
      const col=eCol(report.entity_id||'');
      const tag=(report.entity_id||'').replace('namelessAI_','');
      const rows=report.organs.map(function(h){
        const lc=h.hunger_level>=0.7?'#f04020':h.hunger_level>=0.4?'#f0c020':h.hunger_level>=0.2?'#c0a020':'#2a4a3a';
        const triggerMark=h.has_trigger?'<span style="color:#f0c020;font-size:.46rem">● ANLASS</span>':'<span style="color:#1a3a4a;font-size:.46rem">○ kein Anlass</span>';
        return'<tr><td style="padding:4px 8px;font-size:.56rem;font-family:monospace;color:#4a8ab8;white-space:nowrap">'+esc(h.organ_id.toUpperCase())+'</td>'
          +'<td style="padding:4px 8px;min-width:80px">'+hungerBar(h.hunger_level)+'</td>'
          +'<td style="padding:4px 8px;font-size:.48rem;font-family:monospace;color:'+lc+'">'+Math.round(h.hunger_level*100)+'%</td>'
          +'<td style="padding:4px 8px">'+triggerMark+'</td>'
          +'<td style="padding:4px 8px;font-size:.46rem;color:#2a4a5a;font-family:monospace">'+esc(h.hunger_reason||'')+'</td>'
          +(h.recommended_action?'<td style="padding:4px 8px;font-size:.48rem;color:#10c080;font-family:monospace">→ '+esc(h.recommended_action)+'</td>':'<td></td>')
          +'</tr>';
      }).join('');
      return'<div style="margin-bottom:16px">'
        +'<div style="font-size:.6rem;font-family:monospace;color:'+col+';margin-bottom:6px;letter-spacing:.1em">'+esc(tag)+'</div>'
        +'<table style="border-collapse:collapse;width:100%"><thead><tr>'
        +'<th style="padding:2px 8px;font-size:.44rem;color:#1a3a5a;font-family:monospace;text-align:left;letter-spacing:.1em">ORGAN</th>'
        +'<th style="padding:2px 8px;min-width:80px;font-size:.44rem;color:#1a3a5a;font-family:monospace;text-align:left">HUNGER</th>'
        +'<th style="padding:2px 8px;font-size:.44rem;color:#1a3a5a;font-family:monospace">%</th>'
        +'<th style="padding:2px 8px;font-size:.44rem;color:#1a3a5a;font-family:monospace">ANLASS</th>'
        +'<th style="padding:2px 8px;font-size:.44rem;color:#1a3a5a;font-family:monospace;text-align:left">GRUND</th>'
        +'<th style="padding:2px 8px;font-size:.44rem;color:#1a3a5a;font-family:monospace;text-align:left">EMPFEHLUNG</th>'
        +'</tr></thead><tbody>'+rows+'</tbody></table></div>';
    }

    // Einzeln oder alle
    if(d.entity_id){
      // Einzelnes Wesen
      inn.innerHTML='<div style="font-size:.5rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:10px">ORGANHUNGER — kein Fake, nur echte Prüfanlässe</div>'
        +renderReport(d);
    }else{
      // Alle Wesen
      const reports=d.hunger_reports||[];
      const sorted=[...reports].sort(function(a,b){return(b.hungry_count||0)-(a.hungry_count||0);});
      const overview='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:7px;margin-bottom:16px">'
        +sorted.map(function(r){
          const col=eCol(r.entity_id||'');
          const tag=(r.entity_id||'').replace('namelessAI_','');
          const top=(r.top_hunger||[]).slice(0,2).map(function(h){
            const lc=h.hunger_level>=0.7?'#f04020':h.hunger_level>=0.4?'#f0c020':'#c0a020';
            return'<div style="font-size:.44rem;color:'+lc+';font-family:monospace">'+esc(h.organ_id)+': '+Math.round(h.hunger_level*100)+'%</div>';
          }).join('');
          return'<div style="border:1px solid '+(r.hungry_count>0?col:'#071828')+';border-radius:4px;padding:8px 10px;cursor:pointer;background:#020c1a" onclick="eiWaehleWesen(\\''+esc(r.entity_id)+'\\');eiLinseLaden(\\'organhunger\\')">'
            +'<div style="font-size:.62rem;font-family:monospace;color:'+col+';font-weight:700;margin-bottom:4px">'+esc(tag)+'</div>'
            +(r.hungry_count>0?'<div style="font-size:.5rem;color:#f0c020;margin-bottom:3px">'+r.hungry_count+' Organe mit Anlass</div>'+top:'<div style="font-size:.46rem;color:#1a3a5a">kein Hunger</div>')
            +'</div>';
        }).join('')+'</div>';
      inn.innerHTML='<div style="font-size:.5rem;color:#1a3a5a;font-family:monospace;letter-spacing:.1em;margin-bottom:10px">ORGANHUNGER — alle Wesen — kein Fake, nur Prüfanlässe</div>'
        +overview;
    }
  }catch(e){inn.innerHTML='<div class="ei-empty">Fehler: '+esc(String(e))+'</div>';}
}

/* ── TICKER ── */
async function tickerLaden(){
  if(!eiIstAdmin())return;
  try{
    const d=await fetch(API+'/admin/wesen-einsicht/liveticker?limit=40',{headers:ah()}).then(r=>r.json());
    const evs=d.events||[];if(!evs.length)return;
    const inn=document.getElementById('ei-ticker-inner');if(!inn)return;
    const all=[...evs,...evs];
    inn.innerHTML=all.map(ev=>{
      const col=eCol(ev.entity_id||'');
      const eid=(ev.entity_id||'').replace('namelessAI_','');
      return'<span class="ei-ticker-ev"><span class="ei-tick-type">'+esc(ev.event_type||'')+'</span>'
        +'<span class="ei-tick-eid" style="color:'+col+'">'+esc(eid)+'</span>'
        +'<span style="color:#0a1a2a">'+fmtL(ev.created_at)+'</span></span>';
    }).join('');
    inn.style.animationDuration=Math.max(20,evs.length*2.5)+'s';
  }catch(e){}
}

/* ── INIT ── */
function eiInit(){
  eiPublicUi();
  panoramaLaden();
  vitalsAktualisieren();
  tickerLaden();
  setInterval(function(){vitalsAktualisieren();tickerLaden();if(_eiLinse==='panorama')panoramaLaden();},60000);
}

const _eiObs=new MutationObserver(function(ms){ms.forEach(function(m){if(m.attributeName==='style'){const el=document.getElementById('v-einsicht');if(el&&el.style.display!=='none'&&!window._eiInited){window._eiInited=true;eiInit();}}});});
const _eiEl=document.getElementById('v-einsicht');
if(_eiEl)_eiObs.observe(_eiEl,{attributes:true});
})();
</script>
</div>`;
}
