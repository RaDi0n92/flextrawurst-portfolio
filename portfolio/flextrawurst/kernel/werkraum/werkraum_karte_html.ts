// Werkraum-Karte mit Sichtreichweite.
//
// Der bestehende Explorer (werkraum_explorer_html.ts) lädt den ganzen Graphen in
// den Browser und simuliert ihn vollständig. Bei 658.000 Knoten ist das nicht
// mehr tragbar — nicht wegen der Datei, sondern wegen der Kraftsimulation.
//
// Diese Karte lädt stattdessen nur, was in Reichweite liegt: zuerst die
// Übersicht aus graph/index.json (Ordnerebene, ~1.300 Regionen), und erst wenn
// man irgendwo stehenbleibt, die Kacheln der Umgebung aus graph/r/. Was
// außerhalb der Reichweite liegt, bleibt als einzelner Ballon sichtbar — man
// weiß also immer, dass dort noch etwas ist, ohne es zu laden.
export function buildWerkraumKarteHtml(): string {
  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Werkraum-Karte — Sichtreichweite</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; background:#050810; color:#8899aa;
         font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; }
  #bar { display:flex; align-items:center; gap:.9rem; flex-wrap:wrap;
         padding:.55rem .9rem; border-bottom:1px solid #16212e; background:#070c15; }
  #bar h1 { margin:0; font-size:.88rem; color:#4a7a9a; font-weight:600; letter-spacing:.04em; }
  #ort { color:#cfe3f2; font-size:.82rem; max-width:44ch; overflow:hidden;
         text-overflow:ellipsis; white-space:nowrap; }
  #ort.leer { color:#3a4a5a; font-style:italic; }
  label.feld { display:flex; align-items:center; gap:.35rem; color:#5a7a92; font-size:.76rem; }
  select, input[type=text] { background:#0b1420; color:#cfe3f2; border:1px solid #1d2c3c;
         border-radius:3px; padding:.24rem .45rem; font:inherit; font-size:.78rem; }
  input[type=text] { width:19ch; }
  button { background:#102030; color:#8fb4d0; border:1px solid #23394e; border-radius:3px;
         padding:.26rem .6rem; font:inherit; font-size:.76rem; cursor:pointer; }
  button:hover { background:#16304a; color:#d0e6f6; }
  button:disabled { opacity:.35; cursor:default; }
  #stats { margin-left:auto; color:#3d5468; font-size:.72rem; text-align:right; line-height:1.5; }
  #buehne { position:relative; width:100%; height:calc(100vh - 47px); overflow:hidden; }
  #hinweis { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
         color:#3a5064; font-size:.85rem; pointer-events:none; text-align:center; padding:2rem; }
  svg { display:block; }
  .kante { stroke:#1b2a3a; stroke-width:1; }
  .kante.fern { stroke:#233b52; stroke-dasharray:2,3; }
  .knoten { cursor:pointer; }
  .knoten:hover { stroke:#cfe3f2; stroke-width:1.5; }
  .beschriftung { fill:#54718a; font-size:9px; pointer-events:none; user-select:none; }
  .ballon { stroke-width:1.4; cursor:pointer; }
  .ballon:hover { stroke:#cfe3f2; stroke-width:2.2; }
  .ballontext { fill:#7fa8c8; font-size:9px; pointer-events:none; text-anchor:middle; user-select:none; }
  #tafel { position:absolute; top:0; right:0; width:min(430px,92vw); height:100%;
         background:#070d16; border-left:1px solid #16212e; padding:.9rem 1rem;
         overflow:auto; display:none; }
  #tafel.auf { display:block; }
  #tafel h2 { margin:0 0 .15rem; font-size:.84rem; color:#cfe3f2; word-break:break-all; }
  #tafel .pfad { color:#3d5468; font-size:.7rem; word-break:break-all; margin-bottom:.7rem; }
  #tafel dl { display:grid; grid-template-columns:auto 1fr; gap:.2rem .7rem; margin:0 0 .9rem;
         font-size:.74rem; }
  #tafel dt { color:#3d5468; } #tafel dd { margin:0; color:#8fb4d0; word-break:break-all; }
  #tafel pre { background:#040a12; border:1px solid #13202c; border-radius:3px; padding:.6rem;
         font-size:.71rem; line-height:1.55; color:#6d8fa8; white-space:pre-wrap;
         word-break:break-word; max-height:46vh; overflow:auto; margin:0; }
  #zu { position:absolute; top:.5rem; right:.7rem; cursor:pointer; color:#3d5468; font-size:1.1rem; }
  #zu:hover { color:#cfe3f2; }
  .warn { color:#b58a4a; }
</style>
</head>
<body>
<div id="bar">
  <h1>WERKRAUM-KARTE</h1>
  <span id="ort" class="leer">Übersicht — keine Region betreten</span>
  <label class="feld">Reichweite
    <select id="reichweite">
      <option value="0" selected>0 — nur hier</option>
      <option value="1">1 — Nachbarn</option>
      <option value="2">2 — zwei Schritte</option>
    </select>
  </label>
  <label class="feld">Kanten
    <select id="kantenart">
      <option value="stark" selected>nur tragende</option>
      <option value="alle">alle</option>
      <option value="keine">keine</option>
    </select>
  </label>
  <label class="feld">Suche <input id="suche" type="text" placeholder="Pfad oder Datei …"></label>
  <button id="zurueck" disabled>&#8598; Übersicht</button>
  <span id="stats"></span>
</div>
<div id="buehne">
  <div id="hinweis">Lade Übersicht …</div>
  <div id="tafel"><span id="zu">&#215;</span><div id="tafelinhalt"></div></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
'use strict';

// ---------------------------------------------------------------------------
// Zustand
// ---------------------------------------------------------------------------
var MAX_DETAIL = 4000;      // so viele Dateiknoten zeichnet die Karte höchstens
var index = null;           // graph/index.json
var regionNach = new Map(); // id -> Regionseintrag aus index.json
var nachbarn = new Map();   // id -> Set benachbarter Region-ids
var kachel = new Map();     // id -> geladene Kachel (graph/r/<id>.json)
var standort = null;        // id der Region, in der man steht (null = Übersicht)
var reichweite = 0;
var geladeneBytes = 0;
var simulation = null;
var uebersprungen = 0;      // Regionen, die wegen MAX_DETAIL Ballon geblieben sind
var kantenart = 'stark';    // stark | alle | keine
var MAX_NAMEN = 150;        // so viele Dateinamen werden höchstens geschrieben
var TRAGEND = { 'import':1, 'wikilink':1, 'owns':1, 'folder':1 };

var FARBEN = ['#4a7a9a','#7a9a4a','#9a7a4a','#8a4a7a','#4a9a8a','#9a4a4a',
              '#6a6aaa','#aa8a4a','#4a8a5a','#8a5a9a','#5a8aaa','#aa5a6a'];
function farbeVon(s) {
  var h = 0;
  for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return FARBEN[h % FARBEN.length];
}
function wurzelVon(pfad) {
  if (!pfad) return 'werkraum';
  var i = pfad.indexOf('/');
  return i === -1 ? pfad : pfad.slice(0, i);
}
function mengen(n) {
  if (n < 1000) return String(n);
  if (n < 1000000) return (n / 1000).toFixed(n < 10000 ? 1 : 0) + 'k';
  return (n / 1000000).toFixed(1) + 'M';
}
function bytesLesbar(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(0) + ' KB';
  if (b < 1073741824) return (b / 1048576).toFixed(1) + ' MB';
  return (b / 1073741824).toFixed(2) + ' GB';
}
function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
  });
}

// ---------------------------------------------------------------------------
// Laden
// ---------------------------------------------------------------------------
fetch('/graph/index.json')
  .then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  })
  .then(function (d) {
    index = d;
    d.regionen.forEach(function (r) { regionNach.set(r.id, r); });
    d.kanten.forEach(function (k) {
      if (!nachbarn.has(k.source)) nachbarn.set(k.source, new Set());
      if (!nachbarn.has(k.target)) nachbarn.set(k.target, new Set());
      nachbarn.get(k.source).add(k.target);
      nachbarn.get(k.target).add(k.source);
    });
    document.getElementById('hinweis').style.display = 'none';
    zeichne();
  })
  .catch(function (e) {
    document.getElementById('hinweis').innerHTML =
      'graph/index.json nicht erreichbar (' + escapeHtml(e.message) + ').<br>' +
      'Erst <code>export_werkraum_graph.ts</code> laufen lassen.';
  });

// Eine Kachel holen — höchstens einmal, danach aus dem Gedächtnis.
function holeKachel(id) {
  if (kachel.has(id)) return Promise.resolve(kachel.get(id));
  return fetch('/graph/r/' + encodeURIComponent(id) + '.json')
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    })
    .then(function (text) {
      geladeneBytes += text.length;
      var k = JSON.parse(text);
      kachel.set(id, k);
      return k;
    });
}

// ---------------------------------------------------------------------------
// Sichtreichweite: welche Regionen liegen wie weit vom Standort entfernt?
// ---------------------------------------------------------------------------
function umgebung(start, weite) {
  var abstand = new Map();
  abstand.set(start, 0);
  var rand = [start];
  for (var schritt = 1; schritt <= weite; schritt++) {
    var naechster = [];
    rand.forEach(function (id) {
      (nachbarn.get(id) || new Set()).forEach(function (n) {
        if (!abstand.has(n)) { abstand.set(n, schritt); naechster.push(n); }
      });
    });
    rand = naechster;
  }
  return abstand;
}

// ---------------------------------------------------------------------------
// Zeichnen
// ---------------------------------------------------------------------------
function zeichne() {
  if (standort === null) { zeichneUebersicht(); return; }
  var abstand = umgebung(standort, reichweite);
  // Nach Abstand sortiert laden, damit bei knappem Budget die Nähe gewinnt.
  var kandidaten = Array.from(abstand.keys()).sort(function (a, b) {
    return abstand.get(a) - abstand.get(b);
  });
  var nehmen = [];
  var summe = 0;
  uebersprungen = 0;
  kandidaten.forEach(function (id) {
    var r = regionNach.get(id);
    if (!r) return;
    if (summe + r.knoten <= MAX_DETAIL || nehmen.length === 0) {
      nehmen.push(id); summe += r.knoten;
    } else {
      uebersprungen++;
    }
  });
  Promise.all(nehmen.map(holeKachel))
    .then(function () { zeichneDetail(nehmen, abstand); })
    .catch(function (e) {
      document.getElementById('hinweis').style.display = 'flex';
      document.getElementById('hinweis').textContent = 'Kachel nicht ladbar: ' + e.message;
    });
}

function buehneLeeren() {
  if (simulation) { simulation.stop(); simulation = null; }
  var alt = document.querySelector('#buehne svg');
  if (alt) alt.remove();
}

function neueBuehne() {
  var b = document.getElementById('buehne');
  var W = b.clientWidth, H = b.clientHeight;
  var svg = d3.select('#buehne').append('svg').attr('width', W).attr('height', H);
  var g = svg.append('g');
  svg.call(d3.zoom().scaleExtent([0.08, 9]).on('zoom', function (ev) {
    g.attr('transform', ev.transform);
  }));
  return { svg: svg, g: g, W: W, H: H };
}

// Übersicht: jede Region ein Ballon, Kanten verdichtet. Keine einzige Kachel
// wird dafür geladen — das sind nur die Zahlen aus index.json.
function zeichneUebersicht() {
  buehneLeeren();
  var sz = neueBuehne();
  var knoten = index.regionen.map(function (r) {
    return { id: r.id, art: 'ballon', pfad: r.pfad, anzahl: r.knoten,
             wurzel: wurzelVon(r.pfad),
             r: Math.max(4, Math.min(30, Math.sqrt(r.knoten) * 0.9)) };
  });
  var kanten = kantenart === 'keine' ? [] : index.kanten.map(function (k) {
    return { source: k.source, target: k.target, anzahl: k.anzahl, fern: true };
  });
  simuliere(sz, knoten, kanten);
  setzeStatus(index.regionen.length + ' Regionen · ' +
    mengen(index.regionen.reduce(function (a, r) { return a + r.knoten; }, 0)) + ' Dateien insgesamt',
    'Übersicht — keine Kachel geladen');
}

// Detailansicht: die Dateien der Regionen in Reichweite, alles dahinter als Ballon.
function zeichneDetail(geladen, abstand) {
  buehneLeeren();
  var sz = neueBuehne();
  var geladenSet = new Set(geladen);
  var knoten = [];
  var knotenNach = new Map();

  geladen.forEach(function (id) {
    var k = kachel.get(id);
    if (!k) return;
    var dist = abstand.get(id) || 0;
    k.nodes.forEach(function (n) {
      var e = { id: n.id, art: 'datei', region: id, abstand: dist,
                label: n.label, typ: n.type, groesse: n.size, zeilen: n.lines,
                mtime: n.mtime, auszug: n.excerpt, gross: n.large,
                wurzel: wurzelVon(n.id),
                r: Math.max(2.5, Math.min(11, 2.5 + Math.log((n.lines || 0) + 1) * 1.15)) };
      knoten.push(e); knotenNach.set(n.id, e);
    });
  });

  // Alles, was an die geladene Umgebung grenzt, aber nicht geladen ist: ein Ballon.
  var ballons = new Map();
  function ballonFuer(id) {
    if (ballons.has(id)) return ballons.get(id);
    var r = regionNach.get(id);
    if (!r) return null;
    var e = { id: 'ballon:' + id, art: 'ballon', region: id, pfad: r.pfad,
              anzahl: r.knoten, wurzel: wurzelVon(r.pfad),
              r: Math.max(6, Math.min(26, Math.sqrt(r.knoten) * 0.8)) };
    ballons.set(id, e); knoten.push(e); knotenNach.set(e.id, e);
    return e;
  }

  var kanten = [];
  var gesehen = new Set();
  function kante(a, b, fern, art) {
    if (kantenart === 'keine') return;
    if (kantenart === 'stark' && art && !TRAGEND[art]) return;
    if (!a || !b || a === b) return;
    var s = a < b ? a + '|' + b : b + '|' + a;
    if (gesehen.has(s)) return;
    gesehen.add(s);
    kanten.push({ source: a, target: b, fern: !!fern });
  }

  geladen.forEach(function (id) {
    var k = kachel.get(id);
    if (!k) return;
    k.links.forEach(function (l) { kante(l.source, l.target, false, l.kind); });
    k.randkanten.forEach(function (l) {
      var innenQuelle = knotenNach.has(l.source);
      var innenZiel = knotenNach.has(l.target);
      if (innenQuelle && innenZiel) { kante(l.source, l.target, false, l.kind); return; }
      // Eine Kante ins Ungeladene: sie endet am Ballon der fremden Region.
      var fremd = innenQuelle ? l.zielRegion : l.quellRegion;
      var eigen = innenQuelle ? l.source : l.target;
      if (!fremd || geladenSet.has(fremd)) return;
      var b = ballonFuer(fremd);
      if (b) kante(eigen, b.id, true, l.kind);
    });
  });

  simuliere(sz, knoten, kanten);

  var r = regionNach.get(standort);
  var dateien = knoten.filter(function (n) { return n.art === 'datei'; }).length;
  var warn = uebersprungen > 0
    ? ' · <span class="warn">' + uebersprungen + ' Regionen außer Budget</span>' : '';
  setzeStatus(
    dateien + ' Dateien · ' + geladen.length + ' Kacheln · ' + ballons.size + ' Ballons' + warn +
    '<br>' + bytesLesbar(geladeneBytes) + ' geladen · ' + kanten.length + ' Kanten',
    r ? (r.pfad || 'werkraum') : standort);
}

function simuliere(sz, knoten, kanten) {
  var g = sz.g, W = sz.W, H = sz.H;
  var linie = g.append('g').selectAll('line').data(kanten).enter().append('line')
    .attr('class', function (d) { return d.fern ? 'kante fern' : 'kante'; });

  var form = g.append('g').selectAll('g').data(knoten).enter().append('g')
    .attr('class', 'knoten')
    .on('click', function (ev, d) { angeklickt(d); });

  form.append('circle')
    .attr('r', function (d) { return d.r; })
    .attr('class', function (d) { return d.art === 'ballon' ? 'ballon' : ''; })
    .attr('fill', function (d) { return farbeVon(d.wurzel); })
    .attr('stroke', function (d) { return d.art === 'ballon' ? farbeVon(d.wurzel) : null; })
    .attr('opacity', function (d) {
      if (d.art === 'ballon') return 0.4;
      return d.abstand ? Math.max(0.3, 1 - d.abstand * 0.32) : 1;
    });

  // Beschriftet wird nur, was groß genug ist — sonst erschlägt der Text die Karte.
  // Ballons immer (sie sind die Wegweiser), Dateien nur die größten MAX_NAMEN.
  var beschriftet = new Set();
  var dateiKnoten = [];
  knoten.forEach(function (d) {
    if (d.art === 'ballon') beschriftet.add(d.id); else dateiKnoten.push(d);
  });
  dateiKnoten.sort(function (x, y) { return y.r - x.r; });
  dateiKnoten.slice(0, MAX_NAMEN).forEach(function (d) { beschriftet.add(d.id); });

  form.filter(function (d) { return beschriftet.has(d.id); })
    .append('text')
    .attr('class', function (d) { return d.art === 'ballon' ? 'ballontext' : 'beschriftung'; })
    .attr('dy', function (d) { return d.art === 'ballon' ? 3 : -d.r - 3; })
    .attr('x', function (d) { return d.art === 'ballon' ? 0 : d.r + 3; })
    .text(function (d) {
      if (d.art === 'ballon') return mengen(d.anzahl);
      return d.label.length > 26 ? d.label.slice(0, 25) + '…' : d.label;
    });

  form.append('title').text(function (d) {
    return d.art === 'ballon'
      ? (d.pfad || 'werkraum') + '\\n' + d.anzahl + ' Dateien — klicken zum Betreten'
      : d.id + '\\n' + bytesLesbar(d.groesse) + ' · ' + (d.zeilen || 0) + ' Zeilen';
  });

  simulation = d3.forceSimulation(knoten)
    .force('link', d3.forceLink(kanten).id(function (d) { return d.id; }).distance(34).strength(0.16))
    .force('charge', d3.forceManyBody().strength(-95).distanceMax(320))
    .force('center', d3.forceCenter(W / 2, H / 2).strength(0.04))
    .force('collide', d3.forceCollide().radius(function (d) { return d.r + 3; }).strength(0.6))
    .alphaDecay(0.035)
    .on('tick', function () {
      linie.attr('x1', function (d) { return d.source.x; })
           .attr('y1', function (d) { return d.source.y; })
           .attr('x2', function (d) { return d.target.x; })
           .attr('y2', function (d) { return d.target.y; });
      form.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    });

  form.call(d3.drag()
    .on('start', function (ev, d) {
      if (!ev.active) simulation.alphaTarget(0.25).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on('drag', function (ev, d) { d.fx = ev.x; d.fy = ev.y; })
    .on('end', function (ev, d) {
      if (!ev.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }));
}

// ---------------------------------------------------------------------------
// Bedienung
// ---------------------------------------------------------------------------
function angeklickt(d) {
  if (d.art === 'ballon') { betrete(d.region || d.id); return; }
  zeigeTafel(d);
}

function betrete(id) {
  if (!regionNach.has(id)) return;
  standort = id;
  document.getElementById('zurueck').disabled = false;
  schliesseTafel();
  zeichne();
}

function setzeStatus(html, ort) {
  document.getElementById('stats').innerHTML = html;
  var o = document.getElementById('ort');
  o.textContent = ort;
  o.className = standort === null ? 'leer' : '';
}

function zeigeTafel(d) {
  document.getElementById('tafelinhalt').innerHTML =
    '<h2>' + escapeHtml(d.label) + '</h2>' +
    '<div class="pfad">' + escapeHtml(d.id) + '</div>' +
    '<dl>' +
      '<dt>Typ</dt><dd>.' + escapeHtml(d.typ || 'txt') + '</dd>' +
      '<dt>Größe</dt><dd>' + bytesLesbar(d.groesse) + (d.gross ? ' <span class="warn">(nur Kopf gelesen)</span>' : '') + '</dd>' +
      '<dt>Zeilen</dt><dd>' + (d.zeilen || (d.gross ? '—' : 0)) + '</dd>' +
      '<dt>Geändert</dt><dd>' + escapeHtml((d.mtime || '').replace('T', ' ').slice(0, 19)) + '</dd>' +
      '<dt>Region</dt><dd>' + escapeHtml(d.region) + '</dd>' +
    '</dl>' +
    (d.auszug ? '<pre>' + escapeHtml(d.auszug) + '</pre>'
              : '<pre style="color:#3a4a5a">kein Auszug</pre>');
  document.getElementById('tafel').classList.add('auf');
}
function schliesseTafel() { document.getElementById('tafel').classList.remove('auf'); }
document.getElementById('zu').addEventListener('click', schliesseTafel);

document.getElementById('zurueck').addEventListener('click', function () {
  standort = null;
  this.disabled = true;
  schliesseTafel();
  zeichne();
});

document.getElementById('reichweite').addEventListener('change', function () {
  reichweite = parseInt(this.value, 10);
  if (standort !== null) zeichne();
});

document.getElementById('kantenart').addEventListener('change', function () {
  kantenart = this.value;
  zeichne();
});

// Die Suche geht immer über alle Regionspfade — auch über die, die nie geladen
// wurden. Wer etwas findet, landet mit einem Klick als Standort dort.
var sucheEl = document.getElementById('suche');
sucheEl.addEventListener('keydown', function (ev) {
  if (ev.key !== 'Enter' || !index) return;
  var q = this.value.trim().toLowerCase();
  if (!q) return;
  var treffer = index.regionen.filter(function (r) {
    return (r.pfad || 'werkraum').toLowerCase().indexOf(q) !== -1;
  });
  if (!treffer.length) {
    setzeStatus('<span class="warn">kein Regionspfad enthält &bdquo;' + escapeHtml(q) + '&ldquo;</span>',
      document.getElementById('ort').textContent);
    return;
  }
  treffer.sort(function (a, b) { return (a.pfad || '').length - (b.pfad || '').length; });
  betrete(treffer[0].id);
});

window.addEventListener('resize', function () { if (index) zeichne(); });
</script>
</body>
</html>`;
}
