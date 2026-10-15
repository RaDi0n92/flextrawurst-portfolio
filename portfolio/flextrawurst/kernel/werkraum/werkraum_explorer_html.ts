export function buildWerkraumExplorerHtml(): string {
  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>dak+gord Werkraum</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;background:#050810;color:#8899aa;font-family:monospace;font-size:13px;overflow:hidden}
#bar{height:96px;display:grid;grid-template-columns:auto 220px auto 1fr;align-items:start;gap:8px 12px;padding:8px 16px;border-bottom:1px solid rgba(80,100,130,0.2);flex-shrink:0}
#bar h1{font-size:0.75rem;color:#ff88cc;font-weight:normal;letter-spacing:0.1em;white-space:nowrap}
#search{background:rgba(20,30,50,0.8);border:1px solid rgba(80,100,130,0.3);border-radius:2px;
  color:#8899aa;padding:3px 8px;font-family:monospace;font-size:0.72rem;width:220px;outline:none}
#search::placeholder{color:rgba(100,120,140,0.4)}
#search:focus{border-color:rgba(100,150,200,0.5)}
#stats{font-size:0.65rem;color:rgba(100,120,140,0.5);white-space:nowrap;padding-top:4px}
#layout{display:flex;height:calc(100vh - 96px)}
#graph{flex:1;position:relative;overflow:hidden}
#graph svg{width:100%;height:100%}
#panel{width:420px;flex-shrink:0;border-left:1px solid rgba(80,100,130,0.2);
  display:flex;flex-direction:column;overflow:hidden}
#panel.h{display:none}
#ph{padding:10px 14px;border-bottom:1px solid rgba(80,100,130,0.15);flex-shrink:0}
#ptitle{font-size:0.8rem;color:#88ddff;margin-bottom:3px;word-break:break-all}
#pmeta{font-size:0.62rem;color:rgba(100,120,140,0.5);line-height:1.7}
#pbody{flex:1;overflow-y:auto;padding:12px 14px}
#pbody::-webkit-scrollbar{width:3px}
#pbody::-webkit-scrollbar-thumb{background:rgba(80,100,130,0.3)}
#pcontent{font-size:0.74rem;line-height:1.75;color:#b0c0d0;word-break:break-word}
#pcontent h1{font-size:0.92rem;color:#88ddff;margin:10px 0 4px;font-weight:normal;border-bottom:1px solid rgba(100,180,240,0.15);padding-bottom:3px}
#pcontent h2{font-size:0.82rem;color:#66bbdd;margin:8px 0 3px;font-weight:normal}
#pcontent h3{font-size:0.76rem;color:#4499bb;margin:6px 0 2px;font-weight:normal}
#pcontent p{margin:2px 0 5px}
#pcontent ul,#pcontent ol{margin:3px 0 5px;padding-left:16px}
#pcontent li{margin:1px 0}
#pcontent strong{color:#ccdde0}
#pcontent em{color:#aaccbb;font-style:italic}
#pcontent code{background:rgba(100,150,200,0.1);color:#99ddcc;padding:0 3px;border-radius:2px;font-family:monospace;font-size:0.68rem}
#pcontent pre.cb{background:rgba(0,10,25,0.6);border:1px solid rgba(80,100,130,0.2);border-radius:3px;padding:8px 10px;margin:4px 0;overflow-x:auto;font-size:0.68rem;color:#99aabb;white-space:pre;font-family:monospace}
#pcontent blockquote{border-left:2px solid rgba(100,160,200,0.3);padding-left:8px;color:rgba(150,170,190,0.7);margin:3px 0}
#pcontent hr{border:none;border-top:1px solid rgba(80,100,130,0.2);margin:8px 0}
#pcontent .gap{height:5px}
#pclose{cursor:pointer;color:rgba(140,160,180,0.4);font-size:0.9rem;flex-shrink:0}
#pclose:hover{color:rgba(200,220,240,0.8)}
#link-bar{padding:8px 14px;border-top:1px solid rgba(80,100,130,0.15);flex-shrink:0;display:flex;gap:6px}
#link-input{flex:1;background:rgba(10,20,35,0.9);border:1px solid rgba(80,100,130,0.3);
  border-radius:2px;color:#88ddff;padding:4px 8px;font-family:monospace;font-size:0.7rem;outline:none}
#link-input:focus{border-color:rgba(80,160,220,0.6)}
#link-input::placeholder{color:rgba(80,100,130,0.5)}
#link-btn{background:rgba(40,80,130,0.4);border:1px solid rgba(80,130,200,0.3);border-radius:2px;
  color:#88ddff;padding:4px 10px;font-family:monospace;font-size:0.7rem;cursor:pointer;white-space:nowrap}
#link-btn:hover{background:rgba(60,100,160,0.5)}
#link-msg{font-size:0.62rem;color:rgba(100,200,120,0.7);padding:0 14px 6px;flex-shrink:0;display:none}
.wl{color:#88ddff;cursor:pointer;text-decoration:none;border-bottom:1px solid rgba(100,200,255,0.3);padding-bottom:1px}
.wl:hover{color:#aaeeff;border-bottom-color:rgba(150,230,255,0.7);text-shadow:0 0 7px rgba(100,200,255,0.35)}
.wl-dead{color:rgba(200,150,100,0.45)}
#editor{display:none;flex:1;overflow:hidden;flex-direction:column}
#etextarea{flex:1;background:rgba(5,10,20,0.98);border:none;border-top:1px solid rgba(80,100,130,0.15);
  color:#ccdde0;font-family:monospace;font-size:0.72rem;line-height:1.6;padding:12px 14px;
  resize:none;outline:none;width:100%;tab-size:4}
#etextarea::-webkit-scrollbar{width:3px}
#etextarea::-webkit-scrollbar-thumb{background:rgba(80,100,130,0.3)}
#ebar{display:flex;gap:6px;padding:8px 14px;border-top:1px solid rgba(80,100,130,0.15);flex-shrink:0}
#esave{background:rgba(30,80,50,0.6);border:1px solid rgba(60,160,100,0.4);border-radius:2px;
  color:#66dd88;padding:4px 12px;font-family:monospace;font-size:0.7rem;cursor:pointer}
#esave:hover{background:rgba(40,100,60,0.7)}
#ecancel{background:rgba(40,30,20,0.5);border:1px solid rgba(130,80,60,0.3);border-radius:2px;
  color:rgba(180,130,100,0.7);padding:4px 10px;font-family:monospace;font-size:0.7rem;cursor:pointer}
#emsg{font-size:0.62rem;padding:0 14px 6px;flex-shrink:0;display:none}
#pedit{cursor:pointer;font-size:0.72rem;color:rgba(100,160,200,0.5);margin-left:8px;user-select:none}
#pedit:hover{color:rgba(140,200,240,0.9)}
#legend{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:6px 8px;align-items:flex-start;overflow:auto;
  max-height:54px;padding:1px 2px 3px 0}
#legend::-webkit-scrollbar{height:3px;width:3px}
#legend::-webkit-scrollbar-thumb{background:rgba(90,120,160,0.35)}
#detail-legend{position:absolute;left:12px;bottom:12px;z-index:4;width:520px;max-height:36vh;overflow:auto;
  background:rgba(3,7,15,0.82);border:1px solid rgba(80,110,150,0.22);border-radius:6px;
  padding:10px 11px;box-shadow:0 10px 28px rgba(0,0,0,0.35)}
#detail-legend::-webkit-scrollbar{width:3px}
#detail-legend::-webkit-scrollbar-thumb{background:rgba(90,120,160,0.35)}
.lg-section{margin-bottom:12px}
.lg-title{font-size:0.6rem;color:rgba(210,225,245,0.68);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:7px}
.lg-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 12px}
.lg{display:flex;align-items:center;gap:6px;font-size:0.64rem;color:rgba(165,185,205,0.8);min-width:0}
.lg span:last-child{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lg input{width:10px;height:10px;accent-color:#72ddff;flex-shrink:0}
.lgd{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.group-chip{border:1px solid rgba(80,110,150,0.22);background:rgba(8,14,26,0.68);border-radius:4px;
  padding:4px 7px;cursor:pointer;min-width:130px;max-width:190px;align-items:flex-start}
.group-chip:hover{border-color:rgba(140,190,230,0.4);background:rgba(16,25,42,0.86)}
.group-chip.active{border-color:rgba(140,220,255,0.75);background:rgba(28,50,72,0.9)}
.group-chip .lgd{margin-top:2px}
.lg-text{display:flex;flex-direction:column;gap:1px;min-width:0}
.lg-main{color:rgba(210,225,238,0.88);font-size:0.64rem;line-height:1.15;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lg-sub{color:rgba(120,145,170,0.72);font-size:0.55rem;line-height:1.1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lg-shape{width:14px;height:14px;flex-shrink:0}
.lg-line{width:24px;height:0;border-top:2px solid rgba(120,150,190,0.55);flex-shrink:0}
.lg-line.dashed{border-top-style:dashed}
.lg-line.dotted{border-top-style:dotted}
.node{cursor:pointer}
.node path{stroke-opacity:0.62}
.node text{pointer-events:none;user-select:none}
.link{stroke:rgba(80,110,140,0.35);stroke-width:1;fill:none}
.link.import{stroke:rgba(100,140,200,0.4)}
.link.hidden{display:none}
.node.hidden{display:none}
.node.dimmed path{opacity:0.14}
.node.dimmed text{opacity:0.1}
.node.highlighted path{stroke-width:2.9}
#loading{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  color:rgba(100,120,140,0.5);font-size:0.75rem}
</style>
</head>
<body>
<div id="bar">
  <h1>dak+gord — Werkraum</h1>
  <input id="search" type="text" placeholder="Datei suchen …">
  <span id="stats"></span>
  <div id="legend"></div>
</div>
<div id="layout">
  <div id="graph"><div id="detail-legend"></div><div id="loading">Lade Graph …</div></div>
  <div id="panel" class="h">
    <div id="ph">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div style="display:flex;align-items:center;gap:6px">
          <div id="ptitle"></div>
          <span id="pedit" onclick="editFile()">&#9998;</span>
        </div>
        <span id="pclose" onclick="closePanel()">&#215;</span>
      </div>
      <div id="pmeta"></div>
    </div>
    <div id="pbody"><div id="pcontent"></div></div>
    <div id="editor">
      <textarea id="etextarea" spellcheck="false"></textarea>
      <div id="emsg"></div>
      <div id="ebar">
        <button id="esave" onclick="saveFile()">Speichern</button>
        <button id="ecancel" onclick="cancelEdit()">Abbrechen</button>
      </div>
    </div>
    <div id="link-msg"></div>
    <div id="link-bar">
      <input id="link-input" list="node-list" placeholder="[[Link einfügen …]]" autocomplete="off">
      <datalist id="node-list"></datalist>
      <button id="link-btn" onclick="insertLink()">&#8617; Link</button>
    </div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
var COLORS = {
  // dak+gord intern
  'dak_gord_system':   '#ff5fb7',
  'kerne':             '#ff9f3f',
  'graph':             '#3f7cff',
  'graph/nodes':       '#34b7ff',
  'graph/tools':       '#7f6dff',
  'graph/evals':       '#b06dff',
  'verfassung':        '#ffd23f',
  'verfassung_neu':    '#c8f14b',
  'verfassung_altbestand':'#ad8b36',
  'verfassung_prueffassungen':'#7f6b2a',
  'aufforderungen':    '#ff5f3f',
  'spuren':            '#37f0a2',
  'gedaechtnis_daten': '#d66dff',
  'graphen':           '#3fdcff',
  'herz':              '#ff335f',
  // Werkraum-weit
  'projekt':           '#f7f06a',
  'erkenntnis':        '#58f2c2',
  'flarum':            '#376dff',
  'geni':              '#ff4f91',
  'innenleben':        '#9a62ff',
  'codewesen':         '#21d68f',
  'agent-meta':        '#b9c7d8',
  'struktur':          '#f3aa39',
  'state':             '#78a9d8',
  'wissen':            '#6bd4ff',
  'scripts':           '#9bd083',
  'logs':              '#627186',
  'memory':            '#b78cff',
  'app':               '#4da3ff',
  'tests':             '#7be38b',
  'skills':            '#ff8d48',
  'werkraum-root':     '#8a9bab',
  'docs':              '#b8dfc9',
  // 6 Codewesen-Beings — eigene Farben
  'Schorschel':   '#ff6688',
  'F3INSCHM3CK3R':   '#ff9944',
  'träumerlie':   '#ffdd22',
  'R1ZZ1':   '#44ff88',
  'jumpa':   '#44ddff',
  'Resonanzknoten':   '#cc88ff',
};
function colorFromString(s){
  var h=0;
  for(var i=0;i<s.length;i++) h=(h*31+s.charCodeAt(i))%360;
  return 'hsl('+h+' 72% 62%)';
}
function nodeColor(g){ return COLORS[g] || colorFromString(g || 'unknown'); }

var GROUPS_LABEL = {
  'dak_gord_system':'dak+gord Kern','kerne':'Organe','graph':'LangGraph',
  'graph/nodes':'Graph-Nodes','graph/tools':'Graph-Tools','graph/evals':'Evals',
  'verfassung':'Verfassung','verfassung_neu':'Verfassung (neu)',
  'verfassung_altbestand':'Verfassung (alt)','aufforderungen':'Aufforderungen',
  'spuren':'Spuren','gedaechtnis_daten':'Gedächtnis','graphen':'Graphen','herz':'Herz',
  'projekt':'Vision/Projekt','erkenntnis':'Erkenntnis','flarum':'Flarum',
  'geni':'GENI','innenleben':'Innenleben','codewesen':'Codewesen',
  'agent-meta':'Agent-Doku','struktur':'Struktur','state':'State',
  'wissen':'Wissen','scripts':'Scripts','logs':'Logs','memory':'Memory',
  'app':'App','tests':'Tests','skills':'Skills','werkraum-root':'Werkraum-Root',
  'docs':'Docs',
  'Schorschel':'Wesen 1234','F3INSCHM3CK3R':'Wesen 1324',
  'träumerlie':'Wesen 1423','R1ZZ1':'Wesen 2341',
  'jumpa':'Wesen 3123','Resonanzknoten':'Wesen 4321',
};

var TYPE_SHAPES = {
  'md':   {label:'Markdown', shape:'circle'},
  'py':   {label:'Python', shape:'diamond'},
  'json': {label:'JSON', shape:'square'},
  'jsonl':{label:'JSONL', shape:'star'},
  'ts':   {label:'TypeScript', shape:'triangle'},
  'js':   {label:'JavaScript', shape:'wye'},
  'html': {label:'HTML', shape:'hex'},
  'css':  {label:'CSS', shape:'cross'},
  'txt':  {label:'Text/Log', shape:'crescent'},
  'log':  {label:'Log', shape:'crescent'},
  'yml':  {label:'YAML', shape:'triangleDown'},
  'yaml': {label:'YAML', shape:'triangleDown'},
  'sh':   {label:'Shell', shape:'pentagon'},
  'sql':  {label:'SQL', shape:'square'},
  'bin':  {label:'Binärdaten', shape:'cross'},
  'pickle':{label:'Pickle', shape:'pentagon'},
  'canvas':{label:'Canvas', shape:'hex'},
  'sqlite3':{label:'SQLite', shape:'square'},
  'example':{label:'Example', shape:'triangle'}
};

var LINK_STYLE = {
  'import':    {label:'Python Import', color:'rgba(76,144,255,0.62)', width:1.5, dash:null, distance:82, strength:0.42},
  'ref':       {label:'Pfad-/Namensreferenz', color:'rgba(255,185,75,0.28)', width:0.75, dash:null, distance:115, strength:0.045},
  'wikilink':  {label:'Wikilink [[...]]', color:'rgba(95,235,210,0.68)', width:1.7, dash:'2,2', distance:70, strength:0.5},
  'folder':    {label:'Ordner-Nachbarschaft', color:'rgba(115,135,160,0.25)', width:0.8, dash:'3,5', distance:28, strength:0.06},
  'uses-json': {label:'nutzt JSON-Datei', color:'rgba(198,126,255,0.58)', width:1.25, dash:'7,3', distance:80, strength:0.36},
  'owns':      {label:'JSON besitzt/Geschwister', color:'rgba(116,235,132,0.54)', width:1.15, dash:'1,4', distance:55, strength:0.4}
};

function fmt(bytes){
  if(bytes<1024) return bytes+'B';
  if(bytes<1024*1024) return (bytes/1024).toFixed(1)+'KB';
  return (bytes/1024/1024).toFixed(1)+'MB';
}

var graph = null;
var simulation = null;
var selectedId = null;
var activeGroupFilter = null;
var activeLinkKinds = {'import':true,'wikilink':true,'ref':false,'folder':true,'uses-json':true,'owns':true};
var renderedLinkKinds = {'import':true,'wikilink':true,'folder':true,'uses-json':true,'owns':true};

function shapeKey(d){
  var t = (d.type || '').toLowerCase();
  return (TYPE_SHAPES[t] && TYPE_SHAPES[t].shape) || 'circle';
}

function symbolPath(shape, r){
  var area = Math.max(36, r*r*3.15);
  if(shape==='circle') return d3.symbol().type(d3.symbolCircle).size(area)();
  if(shape==='diamond') return d3.symbol().type(d3.symbolDiamond).size(area*1.15)();
  if(shape==='square') return d3.symbol().type(d3.symbolSquare).size(area)();
  if(shape==='star') return d3.symbol().type(d3.symbolStar).size(area*1.25)();
  if(shape==='triangle') return d3.symbol().type(d3.symbolTriangle).size(area*1.1)();
  if(shape==='triangleDown') return 'M 0 '+r+' L '+(-r*0.95)+' '+(-r*0.72)+' L '+(r*0.95)+' '+(-r*0.72)+' Z';
  if(shape==='cross') return d3.symbol().type(d3.symbolCross).size(area*1.2)();
  if(shape==='wye') return d3.symbol().type(d3.symbolWye).size(area*1.35)();
  if(shape==='hex') {
    var pts=[];
    for(var i=0;i<6;i++){
      var a=Math.PI/6+i*Math.PI/3;
      pts.push((Math.cos(a)*r).toFixed(2)+','+(Math.sin(a)*r).toFixed(2));
    }
    return 'M'+pts.join('L')+'Z';
  }
  if(shape==='pentagon') {
    var p=[];
    for(var j=0;j<5;j++){
      var a2=-Math.PI/2+j*2*Math.PI/5;
      p.push((Math.cos(a2)*r).toFixed(2)+','+(Math.sin(a2)*r).toFixed(2));
    }
    return 'M'+p.join('L')+'Z';
  }
  if(shape==='crescent') {
    return 'M '+(-r*0.35)+' '+(-r)+' A '+r+' '+r+' 0 1 0 '+(-r*0.35)+' '+r+' A '+(r*0.66)+' '+(r*0.66)+' 0 1 1 '+(-r*0.35)+' '+(-r)+' Z';
  }
  return d3.symbol().type(d3.symbolCircle).size(area)();
}

function legendShapeSvg(shape, color){
  var path = symbolPath(shape, 5.5);
  return '<svg class="lg-shape" viewBox="-9 -9 18 18" aria-hidden="true"><path d="'+path+'" fill="'+color+'" stroke="'+color+'" stroke-width="1.1" fill-opacity="0.78"></path></svg>';
}

var _graphTimestamp = null;

fetch('/werkraum_graph.json')
  .then(function(r){ return r.json(); })
  .then(function(data){ graph=data; _graphTimestamp=data.exported_at||null; init(data); })
  .catch(function(){ document.getElementById('loading').textContent='werkraum_graph.json nicht gefunden — erst bauen.'; });

setInterval(function(){
  fetch('/werkraum_graph.json?_='+Date.now())
    .then(function(r){ return r.json(); })
    .then(function(data){
      if(_graphTimestamp && data.exported_at && data.exported_at !== _graphTimestamp){
        location.reload();
      }
    })
    .catch(function(){});
}, 60000);

function init(data){
  document.getElementById('loading').remove();

  var nodes = data.nodes;
  var links = data.links;

  buildWikilinkIndex(nodes);

  // Datalist für Link-Autocomplete befüllen
  var dl = document.getElementById('node-list');
  nodes.forEach(function(n){
    var opt = document.createElement('option');
    opt.value = n.label;
    dl.appendChild(opt);
  });

  var kinds={};
  links.forEach(function(l){ kinds[l.kind]=(kinds[l.kind]||0)+1; });
  var kindOrder=['import','wikilink','ref','folder','uses-json','owns'];
  var kstr=kindOrder.filter(function(k){ return kinds[k]; }).map(function(k){ return kinds[k]+' '+k; }).join(' · ');
  document.getElementById('stats').textContent = nodes.length+' Dateien · '+kstr;
  var visibleLinks = links.filter(function(l){ return renderedLinkKinds[l.kind]; });
  var nodeById = new Map(nodes.map(function(n){ return [n.id, n]; }));

  // Legend: Gruppen, Dateiformen, Kantenarten
  var groups = [...new Set(nodes.map(function(n){ return n.group; }))].sort();
  var types = [...new Set(nodes.map(function(n){ return (n.type||'txt').toLowerCase(); }))].sort();
  var groupCounts={}; nodes.forEach(function(n){ groupCounts[n.group]=(groupCounts[n.group]||0)+1; });
  var typeCounts={}; nodes.forEach(function(n){ var t=(n.type||'txt').toLowerCase(); typeCounts[t]=(typeCounts[t]||0)+1; });
  var legEl = document.getElementById('legend');
  var detailLegEl = document.getElementById('detail-legend');
  var linkHtml = kindOrder.filter(function(k){ return kinds[k]; }).map(function(k){
    var st = LINK_STYLE[k] || {};
    var dash = st.dash ? (st.dash === '1,4' ? 'dotted' : 'dashed') : '';
    var disabled = renderedLinkKinds[k] ? '' : ' disabled';
    var checked = activeLinkKinds[k] && renderedLinkKinds[k] ? ' checked' : '';
    var note = renderedLinkKinds[k] ? '' : ' · aus Performance-Gründen nicht gezeichnet';
    return '<label class="lg"><input type="checkbox" data-link-kind="'+escapeHtml(k)+'"'+checked+disabled+'><span class="lg-line '+dash+'" style="border-top-color:'+st.color+'"></span><span>'+escapeHtml(st.label || k)+' · '+kinds[k]+escapeHtml(note)+'</span></label>';
  }).join('');
  var typeHtml = types.sort(function(a,b){ return (typeCounts[b]||0)-(typeCounts[a]||0); }).map(function(t){
    var spec = TYPE_SHAPES[t] || {label:t.toUpperCase(), shape:'circle'};
    return '<div class="lg">'+legendShapeSvg(spec.shape, '#d7e5ef')+'<span>'+escapeHtml(spec.label)+' · .'+escapeHtml(t)+' · '+typeCounts[t]+'</span></div>';
  }).join('');
  var groupHtml = groups.sort(function(a,b){ return (groupCounts[b]||0)-(groupCounts[a]||0); }).map(function(g){
    var lbl = GROUPS_LABEL[g] || g;
    return '<div class="lg group-chip" data-group-filter="'+escapeHtml(g)+'" title="Nur '+escapeHtml(lbl)+' anzeigen"><div class="lgd" style="background:'+nodeColor(g)+'"></div><span class="lg-text"><span class="lg-main">'+escapeHtml(lbl)+'</span><span class="lg-sub">'+escapeHtml(g)+' · '+groupCounts[g]+' Dateien</span></span></div>';
  }).join('');
  legEl.innerHTML = '<div class="lg group-chip active" data-group-filter="" title="Alle Farbräume anzeigen"><div class="lgd" style="background:#8899aa"></div><span class="lg-text"><span class="lg-main">Alle Farben</span><span class="lg-sub">'+nodes.length+' Dateien sichtbar</span></span></div>'+groupHtml;
  detailLegEl.innerHTML =
    '<div class="lg-section"><div class="lg-title">Kanten</div><div class="lg-grid">'+linkHtml+'</div></div>'+
    '<div class="lg-section"><div class="lg-title">Dateiformen</div><div class="lg-grid">'+typeHtml+'</div></div>';

  var W = document.getElementById('graph').clientWidth;
  var H = document.getElementById('graph').clientHeight;

  var svg = d3.select('#graph').append('svg')
    .attr('width', W).attr('height', H);

  var g = svg.append('g');

  svg.call(d3.zoom()
    .scaleExtent([0.1, 8])
    .on('zoom', function(event){ g.attr('transform', event.transform); }));

  // Node radius
  nodes.forEach(function(n){
    n.r = Math.max(5, Math.min(18, 4 + Math.log(n.lines+1)*2));
  });

  var groupIndex = new Map(groups.map(function(g,i){ return [g,i]; }));
  var clusterRadius = Math.min(W,H) * 0.34;
  function clusterPoint(d){
    var idx = groupIndex.get(d.group) || 0;
    var a = (idx / Math.max(1, groups.length)) * Math.PI * 2 - Math.PI/2;
    return {x: W/2 + Math.cos(a)*clusterRadius, y: H/2 + Math.sin(a)*clusterRadius};
  }

  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(visibleLinks).id(function(d){ return d.id; })
      .distance(function(l){ return (LINK_STYLE[l.kind] && LINK_STYLE[l.kind].distance) || 90; })
      .strength(function(l){ return (LINK_STYLE[l.kind] && LINK_STYLE[l.kind].strength) || 0.25; }))
    .force('charge', d3.forceManyBody().strength(-120).distanceMax(260))
    .force('center', d3.forceCenter(W/2, H/2).strength(0.035))
    .force('x', d3.forceX(function(d){ return clusterPoint(d).x; }).strength(0.025))
    .force('y', d3.forceY(function(d){ return clusterPoint(d).y; }).strength(0.025))
    .force('collide', d3.forceCollide().radius(function(d){ return d.r+5; }).strength(0.55))
    .alphaDecay(0.08)
    .velocityDecay(0.55);

  var link = g.append('g').selectAll('line')
    .data(visibleLinks).join('line')
    .attr('class', function(d){ return 'link '+d.kind; })
    .attr('stroke', function(d){ return (LINK_STYLE[d.kind] && LINK_STYLE[d.kind].color) || 'rgba(80,110,140,0.3)'; })
    .attr('stroke-width', function(d){ return (LINK_STYLE[d.kind] && LINK_STYLE[d.kind].width) || 1; })
    .attr('stroke-dasharray', function(d){ return (LINK_STYLE[d.kind] && LINK_STYLE[d.kind].dash) || null; });

  document.querySelectorAll('input[data-link-kind]').forEach(function(cb){
    cb.addEventListener('change', function(){
      activeLinkKinds[this.getAttribute('data-link-kind')] = this.checked;
      updateVisibility();
    });
  });

  var node = g.append('g').selectAll('g.node')
    .data(nodes).join('g')
    .attr('class','node')
    .call(d3.drag()
      .on('start', function(event, d){
        if(!event.active) simulation.alphaTarget(0.3).restart();
        d.fx=d.x; d.fy=d.y;
      })
      .on('drag', function(event, d){ d.fx=event.x; d.fy=event.y; })
      .on('end', function(event, d){
        if(!event.active) simulation.alphaTarget(0);
        d.fx=null; d.fy=null;
      }))
    .on('click', function(event, d){ event.stopPropagation(); openNode(d); });

  document.querySelectorAll('[data-group-filter]').forEach(function(chip){
    chip.addEventListener('click', function(event){
      event.stopPropagation();
      var gname = this.getAttribute('data-group-filter') || null;
      activeGroupFilter = activeGroupFilter === gname ? null : gname;
      updateVisibility();
    });
  });

  node.append('path')
    .attr('d', function(d){ return symbolPath(shapeKey(d), d.r); })
    .attr('fill', function(d){ return nodeColor(d.group); })
    .attr('fill-opacity', 0.75)
    .attr('stroke', function(d){ return nodeColor(d.group); })
    .attr('stroke-opacity', 0.5)
    .attr('stroke-width', 1.5);

  var LABEL_GROUPS = new Set(['kerne','verfassung','projekt','erkenntnis','geni',
    'aufforderungen','gedaechtnis_daten','dak_gord_system','struktur',
    'Schorschel','F3INSCHM3CK3R','träumerlie',
    'R1ZZ1','jumpa','Resonanzknoten']);
  // Labels für wichtige Gruppen und große Dateien
  node.filter(function(d){ return d.lines > 60 || LABEL_GROUPS.has(d.group); })
    .append('text')
    .text(function(d){ return d.label; })
    .attr('dy', function(d){ return -d.r-3; })
    .attr('text-anchor','middle')
    .attr('fill','rgba(180,200,220,0.7)')
    .attr('font-size','9px');

  simulation.on('tick', function(){
    link
      .attr('x1', function(d){ return d.source.x; })
      .attr('y1', function(d){ return d.source.y; })
      .attr('x2', function(d){ return d.target.x; })
      .attr('y2', function(d){ return d.target.y; });
    node.attr('transform', function(d){ return 'translate('+d.x+','+d.y+')'; });
  });

  function linkEndpointId(endpoint){
    return typeof endpoint === 'object' ? endpoint.id : endpoint;
  }

  function updateGroupLegend(){
    document.querySelectorAll('[data-group-filter]').forEach(function(chip){
      var gname = chip.getAttribute('data-group-filter') || null;
      chip.classList.toggle('active', activeGroupFilter === gname || (!activeGroupFilter && !gname));
    });
  }

  function updateVisibility(){
    updateGroupLegend();
    node.classed('hidden', function(d){
      return !!activeGroupFilter && d.group !== activeGroupFilter;
    });
    link.classed('hidden', function(d){
      if(!activeLinkKinds[d.kind]) return true;
      if(!activeGroupFilter) return false;
      var s = nodeById.get(linkEndpointId(d.source));
      var t = nodeById.get(linkEndpointId(d.target));
      return !s || !t || s.group !== activeGroupFilter || t.group !== activeGroupFilter;
    });
  }

  // Click on background → deselect
  svg.on('click', function(){ deselect(); });

  // Search
  document.getElementById('search').addEventListener('input', function(){
    var q = this.value.toLowerCase().trim();
    if(!q){ node.classed('dimmed',false).classed('highlighted',false); return; }
    node.classed('dimmed', function(d){ return !d.id.toLowerCase().includes(q); });
    node.classed('highlighted', function(d){ return d.id.toLowerCase().includes(q); });
  });
}

// Wikilink-Index: label/basename/id → node
var wikilinkIndex = {};
function buildWikilinkIndex(nodes){
  nodes.forEach(function(n){
    var base = n.id.split('/').pop();
    var noext = base.replace(/\.[^.]+$/, '');
    wikilinkIndex[base.toLowerCase()] = n;
    wikilinkIndex[noext.toLowerCase()] = n;
    wikilinkIndex[n.id.toLowerCase()] = n;
    wikilinkIndex[n.label.toLowerCase()] = n;
  });
}

function escapeHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderInline(s){
  var out = ''; var i = 0;
  while(i < s.length){
    var c = s[i];
    if(c==='[' && s[i+1]==='['){
      var e=s.indexOf(']]',i+2);
      if(e!==-1){
        var tgt=s.slice(i+2,e).trim();
        var nd=wikilinkIndex[tgt.toLowerCase()];
        if(nd) out+='<span class="wl" data-nid="'+escapeHtml(nd.id)+'">[['+escapeHtml(tgt)+']]</span>';
        else out+='<span class="wl-dead">[['+escapeHtml(tgt)+']]</span>';
        i=e+2; continue;
      }
    }
    if(c==='*' && s[i+1]==='*'){
      var e2=s.indexOf('**',i+2);
      if(e2!==-1){ out+='<strong>'+escapeHtml(s.slice(i+2,e2))+'</strong>'; i=e2+2; continue; }
    }
    if(c==='*' && s[i+1]!=='*' && s[i+1]!==' '){
      var e3=s.indexOf('*',i+1);
      if(e3!==-1 && e3>i+1){ out+='<em>'+escapeHtml(s.slice(i+1,e3))+'</em>'; i=e3+1; continue; }
    }
    if(c==='\`'){
      var e4=s.indexOf('\`',i+1);
      if(e4!==-1){ out+='<code>'+escapeHtml(s.slice(i+1,e4))+'</code>'; i=e4+1; continue; }
    }
    out+=escapeHtml(c); i++;
  }
  return out;
}

function renderContent(text){
  var lines=text.split('\\n'); var html='';
  var inList=false; var inCode=false; var codeBuf='';
  for(var i=0;i<lines.length;i++){
    var ln=lines[i];
    if(ln.startsWith('\`\`\`')){
      if(!inCode){ if(inList){html+='</ul>';inList=false;} inCode=true; codeBuf=''; continue; }
      else { html+='<pre class="cb">'+escapeHtml(codeBuf)+'</pre>'; inCode=false; continue; }
    }
    if(inCode){ codeBuf+=(codeBuf?'\\n':'')+ln; continue; }
    if(ln.startsWith('### ')){ if(inList){html+='</ul>';inList=false;} html+='<h3>'+renderInline(ln.slice(4))+'</h3>'; continue; }
    if(ln.startsWith('## ')){ if(inList){html+='</ul>';inList=false;} html+='<h2>'+renderInline(ln.slice(3))+'</h2>'; continue; }
    if(ln.startsWith('# ')){ if(inList){html+='</ul>';inList=false;} html+='<h1>'+renderInline(ln.slice(2))+'</h1>'; continue; }
    var tr=ln.trim();
    if(tr==='---'||tr==='***'||tr==='==='){ if(inList){html+='</ul>';inList=false;} html+='<hr>'; continue; }
    if(ln.startsWith('> ')){ if(inList){html+='</ul>';inList=false;} html+='<blockquote>'+renderInline(ln.slice(2))+'</blockquote>'; continue; }
    if(ln.startsWith('- ')||ln.startsWith('* ')){ if(!inList){html+='<ul>';inList=true;} html+='<li>'+renderInline(ln.slice(2))+'</li>'; continue; }
    if(tr===''){ if(inList){html+='</ul>';inList=false;} html+='<div class="gap"></div>'; continue; }
    if(inList){html+='</ul>';inList=false;}
    html+='<p>'+renderInline(ln)+'</p>';
  }
  if(inList) html+='</ul>';
  return html;
}

// Delegierter Click-Handler für Wikilinks (kein inline-onclick nötig)
document.addEventListener('click', function(e){
  var el = e.target;
  if(el && el.classList && el.classList.contains('wl')){
    var nid = el.getAttribute('data-nid');
    if(nid && graph){
      var n = graph.nodes.find(function(x){ return x.id===nid; });
      if(n) openNode(n);
    }
  }
});

function openNode(d){
  if(!d) return;
  selectedId = d.id;
  document.getElementById('ptitle').textContent = d.id;
  document.getElementById('panel').classList.remove('h');
  document.getElementById('link-input').value = '';
  document.getElementById('link-msg').style.display = 'none';
  var mt = new Date(d.mtime).toLocaleString('de-DE');
  document.getElementById('pmeta').innerHTML =
    '<span style="color:'+nodeColor(d.group)+'">'+d.group+'</span>' +
    ' &nbsp;·&nbsp; '+d.type+
    ' &nbsp;·&nbsp; '+fmt(d.size)+
    ' &nbsp;·&nbsp; '+d.lines+' Zeilen' +
    ' &nbsp;·&nbsp; '+mt;
  var pre = document.getElementById('pcontent');
  pre.innerHTML = d.large ? escapeHtml('(Große Datei · ' + fmt(d.size) + ' · Lade …)') : renderContent(d.excerpt || '');
  showView();
  var encodedPath = d.id.split('/').map(encodeURIComponent).join('/');
  fetch('/werkraum/'+encodedPath)
    .then(function(r){ return r.text(); })
    .then(function(text){
      pre.innerHTML = renderContent(text || '(leer)');
      pre._rawText = text || '';
    })
    .catch(function(){ pre.innerHTML = '(Konnte Datei nicht laden)'; });
  // Graph-Highlight: verbundene Knoten aufleuchten lassen
  highlightConnected(d.id);
}

function highlightConnected(id){
  if(!graph) return;
  var connected = new Set([id]);
  graph.links.forEach(function(l){
    var s = typeof l.source === 'object' ? l.source.id : l.source;
    var t = typeof l.target === 'object' ? l.target.id : l.target;
    if(s===id) connected.add(t);
    if(t===id) connected.add(s);
  });
  d3.selectAll('.node').classed('dimmed', function(d){ return !connected.has(d.id); });
  d3.selectAll('.node').classed('highlighted', function(d){ return d.id===id; });
}

function insertLink(){
  if(!selectedId) return;
  var input = document.getElementById('link-input');
  var val = input.value.trim().replace(new RegExp('^\\\\[\\\\[|\\\\]\\\\]$', 'g'),'');
  if(!val) return;
  var msg = document.getElementById('link-msg');
  fetch('/werkraum-link', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({file: selectedId, link: val})
  }).then(function(r){ return r.json(); })
    .then(function(j){
      if(j.ok){
        msg.textContent = '[['+val+']] eingefügt in '+selectedId;
        msg.style.display='block';
        input.value='';
        // Datei neu laden
        var ep2 = selectedId.split('/').map(encodeURIComponent).join('/');
        fetch('/werkraum/'+ep2)
          .then(function(r){return r.text();})
          .then(function(t){
            var pre2 = document.getElementById('pcontent');
            pre2.innerHTML=renderContent(t);
            pre2._rawText=t;
          });
      }
    })
    .catch(function(){ msg.textContent='Fehler beim Schreiben'; msg.style.display='block'; });
}

function showView(){
  document.getElementById('pbody').style.display='';
  document.getElementById('editor').style.display='none';
  document.getElementById('link-bar').style.display='';
  document.getElementById('emsg').style.display='none';
}

function editFile(){
  if(!selectedId) return;
  var raw = document.getElementById('pcontent')._rawText || '';
  document.getElementById('etextarea').value = raw;
  document.getElementById('pbody').style.display='none';
  document.getElementById('link-bar').style.display='none';
  document.getElementById('editor').style.display='flex';
  document.getElementById('emsg').style.display='none';
  document.getElementById('etextarea').focus();
}

function cancelEdit(){
  showView();
}

function saveFile(){
  if(!selectedId) return;
  var content = document.getElementById('etextarea').value;
  var msg = document.getElementById('emsg');
  msg.textContent = 'Speichere …';
  msg.style.display = 'block';
  msg.style.color = 'rgba(100,160,200,0.7)';
  fetch('/werkraum-write', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({file: selectedId, content: content})
  }).then(function(r){ return r.json(); })
    .then(function(j){
      if(j.ok){
        msg.textContent = 'Gespeichert.';
        msg.style.color = 'rgba(80,200,120,0.8)';
        document.getElementById('pcontent').innerHTML = renderContent(content);
        document.getElementById('pcontent')._rawText = content;
        setTimeout(function(){ showView(); }, 800);
      } else {
        msg.textContent = 'Fehler: '+(j.error||'unbekannt');
        msg.style.color = 'rgba(220,80,80,0.8)';
      }
    })
    .catch(function(e){
      msg.textContent = 'Netzwerkfehler: '+String(e);
      msg.style.color = 'rgba(220,80,80,0.8)';
    });
}

function closePanel(){
  document.getElementById('panel').classList.add('h');
  selectedId = null;
  deselect();
}

function deselect(){
  document.getElementById('search').value='';
  d3.selectAll('.node').classed('dimmed',false).classed('highlighted',false);
}

document.addEventListener('keydown', function(e){
  if(e.key==='Escape'){ closePanel(); deselect(); }
});
</script>
</body>
</html>`;
}
