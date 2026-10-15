// Ring 22N — KompOase Living Datafield
// Nicht Daten auf Landschaft. Daten SIND Landschaft.

const WW = 3200;
const WH = 2200;

interface E { id:string;wx:number;wy:number;color:string;glow:string;coreR:number;pulseRate:number;vortexSpeed:number }
interface S { fx:number;fy:number;tx:number;ty:number;cx1:number;cy1:number;cx2:number;cy2:number;colorA:string;colorB:string;width:number;speed:number }

const EDEFS: E[] = [
  {id:'Schorschel',wx:1350,wy:950, color:'#00ff88',glow:'#00ffaa',coreR:42,pulseRate:2.1,vortexSpeed:0.9},
  {id:'Resonanzknoten',wx:1560,wy:870, color:'#bb00ff',glow:'#cc44ff',coreR:36,pulseRate:1.7,vortexSpeed:1.1},
  {id:'F3INSCHM3CK3R',wx:1780,wy:920, color:'#ff6600',glow:'#ff9944',coreR:45,pulseRate:2.5,vortexSpeed:0.7},
  {id:'träumerlie',wx:1430,wy:1080,color:'#ff0055',glow:'#ff4488',coreR:39,pulseRate:1.9,vortexSpeed:1.2},
  {id:'R1ZZ1',wx:1680,wy:1070,color:'#00eedd',glow:'#44ffee',coreR:34,pulseRate:2.8,vortexSpeed:0.85},
  {id:'jumpa',wx:1920,wy:1040,color:'#ffee00',glow:'#ffff55',coreR:48,pulseRate:1.5,vortexSpeed:0.6},
];

const SDEFS: S[] = [
  {fx:1350,fy:950, tx:1560,ty:870, cx1:1420,cy1:840,cx2:1500,cy2:840,colorA:'#00ff88',colorB:'#bb00ff',width:1.5,speed:0.35},
  {fx:1560,fy:870, tx:1780,ty:920, cx1:1620,cy1:800,cx2:1720,cy2:850,colorA:'#bb00ff',colorB:'#ff6600',width:1.5,speed:0.28},
  {fx:1350,fy:950, tx:1430,ty:1080,cx1:1340,cy1:1020,cx2:1380,cy2:1060,colorA:'#00ff88',colorB:'#ff0055',width:1.2,speed:0.42},
  {fx:1560,fy:870, tx:1680,ty:1070,cx1:1580,cy1:960,cx2:1640,cy2:1020,colorA:'#bb00ff',colorB:'#00eedd',width:1.2,speed:0.38},
  {fx:1780,fy:920, tx:1920,ty:1040,cx1:1830,cy1:870,cx2:1890,cy2:960,colorA:'#ff6600',colorB:'#ffee00',width:1.5,speed:0.31},
  {fx:1430,fy:1080,tx:1680,ty:1070,cx1:1520,cy1:1100,cx2:1600,cy2:1090,colorA:'#ff0055',colorB:'#00eedd',width:1.0,speed:0.45},
  {fx:1680,fy:1070,tx:1920,ty:1040,cx1:1760,cy1:1090,cx2:1860,cy2:1070,colorA:'#00eedd',colorB:'#ffee00',width:1.0,speed:0.29},
  {fx:1350,fy:950, tx:1640,ty:680, cx1:1440,cy1:760,cx2:1580,cy2:700,colorA:'#00ff88',colorB:'#4488ff',width:0.8,speed:0.22},
  {fx:1560,fy:870, tx:1640,ty:680, cx1:1580,cy1:750,cx2:1620,cy2:700,colorA:'#bb00ff',colorB:'#4488ff',width:0.8,speed:0.18},
  {fx:1780,fy:920, tx:1640,ty:680, cx1:1740,cy1:760,cx2:1680,cy2:700,colorA:'#ff6600',colorB:'#4488ff',width:0.8,speed:0.25},
  {fx:1430,fy:1080,tx:1640,ty:680, cx1:1500,cy1:820,cx2:1600,cy2:720,colorA:'#ff0055',colorB:'#4488ff',width:0.8,speed:0.20},
  {fx:1680,fy:1070,tx:1640,ty:680, cx1:1670,cy1:880,cx2:1650,cy2:750,colorA:'#00eedd',colorB:'#4488ff',width:0.8,speed:0.27},
  {fx:1920,fy:1040,tx:1640,ty:680, cx1:1820,cy1:820,cx2:1700,cy2:720,colorA:'#ffee00',colorB:'#4488ff',width:0.8,speed:0.23},
];

function buildCSS(): string { return `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#020408;font-family:monospace}
#viewport{width:100vw;height:100vh;overflow:hidden;position:relative;cursor:default}
#world{position:absolute;top:0;left:0;width:${WW}px;height:${WH}px;transform-origin:0 0;will-change:transform}
#c{display:block;width:${WW}px;height:${WH}px}
#ui{position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:20}
#topbar{
  position:absolute;top:0;left:0;right:0;height:46px;
  background:linear-gradient(to bottom,rgba(2,4,10,0.97) 0%,rgba(2,4,10,0.0) 100%);
  display:flex;align-items:center;gap:5px;padding:0 12px;
  pointer-events:auto;z-index:30
}
#topbar h1{font-size:0.74rem;color:rgba(0,168,255,0.55);letter-spacing:0.12em;white-space:nowrap;margin-right:4px}
.tb{
  background:rgba(2,6,16,0.88);border:1px solid rgba(0,168,255,0.18);
  color:rgba(0,168,255,0.65);font-family:monospace;font-size:0.66rem;
  padding:3px 7px;border-radius:2px;cursor:pointer;transition:all 0.15s;white-space:nowrap
}
.tb:hover{background:rgba(0,30,70,0.9);border-color:rgba(0,168,255,0.5);color:#00c8ff}
.tb.act{background:rgba(0,50,110,0.4);border-color:rgba(0,168,255,0.6);color:#00eeff}
.tb.e1{color:#00ff88;border-color:rgba(0,255,136,0.3)}.tb.e1:hover{border-color:#00ff88}
.tb.e2{color:#bb00ff;border-color:rgba(187,0,255,0.3)}.tb.e2:hover{border-color:#bb00ff}
.tb.e3{color:#ff6600;border-color:rgba(255,102,0,0.3)}.tb.e3:hover{border-color:#ff6600}
.tb.e4{color:#ff0055;border-color:rgba(255,0,85,0.3)}.tb.e4:hover{border-color:#ff0055}
.tb.e5{color:#00eedd;border-color:rgba(0,238,221,0.3)}.tb.e5:hover{border-color:#00eedd}
.tb.e6{color:#ffee00;border-color:rgba(255,238,0,0.3)}.tb.e6:hover{border-color:#ffee00}
.tb.ef{color:#4488ff;border-color:rgba(68,136,255,0.3)}.tb.ef:hover{border-color:#4488ff}
.tb.ed{color:#ff88cc;border-color:rgba(255,136,204,0.3)}.tb.ed:hover{border-color:#ff88cc}
#zoom-wrap{display:flex;align-items:center;gap:4px;margin-left:auto;flex-shrink:0}
#zoom-label{font-size:0.64rem;color:rgba(0,168,255,0.45);min-width:34px}
#zoom-slider{width:75px;cursor:pointer;accent-color:#00a8ff}
#dak{
  position:absolute;right:10px;top:56px;width:205px;
  background:rgba(2,3,12,0.93);border:1px solid rgba(255,136,204,0.18);
  border-radius:3px;padding:11px;font-size:0.69rem;color:rgba(255,136,204,0.65);
  pointer-events:auto;z-index:25;backdrop-filter:blur(8px)
}
#dak h2{font-size:0.75rem;color:#ff88cc;margin-bottom:7px;letter-spacing:0.07em}
.dr{display:flex;justify-content:space-between;margin-bottom:3px}
.dk{color:rgba(255,136,204,0.38)}.dv{color:rgba(255,136,204,0.8)}
.ds{border:none;border-top:1px solid rgba(255,136,204,0.09);margin:7px 0}
.dn{color:rgba(255,136,204,0.28);font-size:0.61rem;font-style:italic;margin-top:5px;line-height:1.5}
.dnav{margin-top:8px;display:flex;flex-wrap:wrap;gap:3px}
#loc{
  position:absolute;bottom:30px;left:50%;transform:translateX(-50%);
  min-width:290px;max-width:500px;
  background:rgba(2,4,14,0.96);border:1px solid rgba(0,168,255,0.2);
  border-radius:3px;padding:11px 15px;font-size:0.71rem;color:rgba(100,160,200,0.9);
  pointer-events:auto;z-index:25;backdrop-filter:blur(8px);transition:opacity 0.2s
}
#loc.h{opacity:0;pointer-events:none}
#ltit{font-size:0.88rem;color:#c0d8f4;margin-bottom:6px;display:flex;justify-content:space-between;align-items:baseline}
.lr{display:flex;gap:8px;margin-bottom:3px}
.lk{color:rgba(0,100,150,0.8);min-width:78px;flex-shrink:0}
.lv{color:rgba(120,180,220,0.9)}
.latm{color:rgba(80,150,80,0.9);font-style:italic}
.lreal{color:#00cc66}
.lsrc{color:rgba(0,130,90,0.7);font-size:0.64rem;margin-top:4px}
.lx{cursor:pointer;color:rgba(0,100,160,0.5);font-size:0.95rem;flex-shrink:0;margin-left:8px}
#etip{
  position:absolute;pointer-events:none;z-index:40;
  background:rgba(2,6,18,0.95);border:1px solid transparent;
  border-radius:2px;padding:5px 9px;font-size:0.67rem;display:none;white-space:nowrap
}
#leg{
  position:absolute;bottom:0;left:0;right:0;height:24px;
  background:rgba(2,4,8,0.93);border-top:1px solid rgba(0,168,255,0.06);
  display:flex;align-items:center;gap:10px;padding:0 11px;
  font-size:0.6rem;color:rgba(0,100,150,0.55);pointer-events:none;z-index:20;overflow:hidden
}
.lgsq{width:7px;height:7px;border-radius:1px;flex-shrink:0;display:inline-block;margin-right:2px}
.lgsh{margin-left:auto;color:rgba(0,80,40,0.5);font-style:italic;white-space:nowrap}
/* ── Entity panel ── */
#ep{
  position:absolute;right:225px;top:56px;width:340px;
  max-height:calc(100vh - 90px);overflow-y:auto;
  background:rgba(2,4,14,0.97);border:1px solid rgba(0,168,255,0.2);
  border-radius:3px;padding:14px;font-size:0.7rem;
  pointer-events:auto;z-index:26;backdrop-filter:blur(10px);transition:opacity 0.18s
}
#ep.h{opacity:0;pointer-events:none}
#ep::-webkit-scrollbar{width:3px}
#ep::-webkit-scrollbar-thumb{background:rgba(0,168,255,0.2);border-radius:2px}
.ep-head{font-size:0.92rem;font-weight:bold;margin-bottom:4px;display:flex;justify-content:space-between;align-items:baseline}
.ep-x{cursor:pointer;font-size:0.95rem;opacity:0.5;flex-shrink:0;margin-left:8px}
.ep-x:hover{opacity:1}
.ep-sec{border-left:2px solid;padding-left:10px;margin-bottom:10px;padding-bottom:2px}
.ep-sl{font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px;opacity:0.7}
.ep-row{display:flex;gap:6px;margin-bottom:3px;align-items:baseline}
.ep-k{color:rgba(160,185,210,0.38);min-width:100px;flex-shrink:0;font-size:0.67rem}
.ep-v{color:rgba(180,205,225,0.85)}
.ep-badge{display:inline-block;padding:1px 7px;border-radius:2px;font-size:0.66rem}
.ep-edge{border-left:2px solid;padding:4px 8px;margin-bottom:5px;font-size:0.66rem;line-height:1.5}
.ep-blocked{color:rgba(255,120,80,0.75)}
.ep-ok{color:rgba(80,220,140,0.8)}
`; }

function buildJS(): string {
  const ej = JSON.stringify(EDEFS);
  const sj = JSON.stringify(SDEFS);
  const cx = WW / 2;
  const cy = WH / 2;
  return `
var WW=${WW},WH=${WH};
var ENTITIES=${ej};
var FLARUM={id:'flarum-archiv',wx:1640,wy:680,color:'#4488ff',glow:'#88aaff',coreR:18,pulseRate:3.2,vortexSpeed:0.5};
var DAKGORD={id:'dak+gord',wx:280,wy:480,color:'#ff88cc',glow:'#ffbbdd',coreR:20,pulseRate:2.0,vortexSpeed:0.4};
var STREAMS=${sj};

var scale=0.32,tx=20,ty=20;
var isDragging=false,dragStart={x:0,y:0},dragOrigin={tx:0,ty:0},didDrag=false;
var T=0;
var mouseWX=-1,mouseWY=-1,hoveredEntity=null;
var ripples=[];
var showGeni=true,showParticles=true,showStreams=true;

var canvas=document.getElementById('c');
var ctx=canvas.getContext('2d');
var world=document.getElementById('world');
var viewport=document.getElementById('viewport');
var slider=document.getElementById('zoom-slider');
var zlabel=document.getElementById('zoom-label');
var etip=document.getElementById('etip');
var locEl=document.getElementById('loc');
var locContent=document.getElementById('loc-content');

function hexA(hex,a){
  var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return 'rgba('+r+','+g+','+b+','+a.toFixed(3)+')';
}

/* ── Particles ─────────────────────────────────────────────────────────────── */
var MAX_P=2400,particles=[];
function spawnP(opts){
  if(particles.length>=MAX_P)return;
  var ang=opts.angle!==undefined?opts.angle:Math.random()*Math.PI*2;
  var spd=(opts.speed||0.3)+Math.random()*(opts.spread||0.5);
  particles.push({
    x:(opts.x||0)+(Math.random()-0.5)*(opts.scatter||30),
    y:(opts.y||0)+(Math.random()-0.5)*(opts.scatter||30),
    vx:Math.cos(ang)*spd,vy:Math.sin(ang)*spd,
    life:0,maxLife:(opts.minLife||80)+Math.random()*(opts.lifeRange||160),
    color:opts.color||'#00a8ff',size:(opts.minSize||0.5)+Math.random()*(opts.sizeRange||2.5),
    drag:opts.drag||0.997,grav:opts.grav||0,opacity:opts.opacity||1,burst:opts.burst||false
  });
}
function seedParticles(){
  for(var i=0;i<550;i++){
    particles.push({x:Math.random()*WW,y:Math.random()*WH,
      vx:(Math.random()-0.5)*0.35,vy:(Math.random()-0.5)*0.35,
      life:Math.random()*220,maxLife:220+Math.random()*220,
      color:['#112233','#1a3a5a','#0a2040','#223344'][i%4],
      size:0.5+Math.random()*1.4,drag:0.9995,grav:0,opacity:0.8,burst:false});
  }
  var allE=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var ei=0;ei<allE.length;ei++){
    var e=allE[ei];
    for(var j=0;j<70;j++){
      var a=Math.random()*Math.PI*2,r=40+Math.random()*200;
      particles.push({x:e.wx+Math.cos(a)*r,y:e.wy+Math.sin(a)*r,
        vx:(Math.random()-0.5)*0.7,vy:(Math.random()-0.5)*0.7,
        life:Math.random()*150,maxLife:150+Math.random()*200,
        color:e.color,size:0.4+Math.random()*1.8,drag:0.998,grav:0,opacity:0.65,burst:false});
    }
  }
}
function updateParticles(){
  for(var i=particles.length-1;i>=0;i--){
    var p=particles[i];
    p.x+=p.vx;p.y+=p.vy;p.vx*=p.drag;p.vy*=p.drag;p.vy+=p.grav;p.life++;
    if(p.life>p.maxLife){
      if(!p.burst){p.x=Math.random()*WW;p.y=Math.random()*WH;
        p.vx=(Math.random()-0.5)*0.35;p.vy=(Math.random()-0.5)*0.35;p.life=0;p.maxLife=200+Math.random()*200;
      } else particles.splice(i,1);
    }
  }
  var frame=Math.round(T*60);
  if(frame%5===0){
    var ei=Math.floor(Math.random()*ENTITIES.length),e=ENTITIES[ei];
    spawnP({x:e.wx,y:e.wy,speed:0.15,spread:0.7,scatter:e.coreR*2,
      color:e.color,minSize:0.3,sizeRange:2,minLife:70,lifeRange:150,drag:0.996,opacity:0.75});
  }
}
function drawParticles(){
  if(!showParticles)return;
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(var i=0;i<particles.length;i++){
    var p=particles[i];
    var fade=p.life/p.maxLife;
    var a=p.opacity*(fade<0.2?fade/0.2:fade>0.8?(1-fade)/0.2:1)*0.65;
    if(a<=0.005)continue;
    ctx.fillStyle=hexA(p.color,a);
    ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
}

/* ── Vortexes ──────────────────────────────────────────────────────────────── */
var vortexes=[];
function initVortexes(){
  var all=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var ei=0;ei<all.length;ei++){
    var e=all[ei];
    var count=55+Math.floor(e.coreR*1.8),vps=[];
    for(var j=0;j<count;j++){
      var ang=(j/count)*Math.PI*2+Math.random()*0.3;
      var r=e.coreR*(1.3+Math.random()*2.8);
      vps.push({ang:ang,r:r,dr:(Math.random()-0.5)*0.06,
        size:0.4+Math.random()*2.2,opacity:0.25+Math.random()*0.55,
        spd:e.vortexSpeed*(0.6+Math.random()*0.8)*(Math.random()<0.5?1:-1),
        phase:Math.random()*Math.PI*2});
    }
    vortexes.push({e:e,vps:vps});
  }
}
function drawVortexes(t){
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(var vi=0;vi<vortexes.length;vi++){
    var v=vortexes[vi],e=v.e;
    for(var j=0;j<v.vps.length;j++){
      var vp=v.vps[j];
      vp.ang+=vp.spd*0.016;
      vp.r+=vp.dr;
      if(vp.r>e.coreR*4.8||vp.r<e.coreR*0.7)vp.dr*=-1;
      var px=e.wx+vp.r*Math.cos(vp.ang),py=e.wy+vp.r*Math.sin(vp.ang);
      var pulse=0.7+0.3*Math.sin(t*e.pulseRate*0.35+vp.phase);
      ctx.fillStyle=hexA(e.glow,vp.opacity*pulse);
      ctx.beginPath();ctx.arc(px,py,vp.size,0,Math.PI*2);ctx.fill();
    }
  }
  ctx.restore();
}

/* ── Entity cores ──────────────────────────────────────────────────────────── */
function drawEntity(e,t){
  var pulse=0.8+0.2*Math.sin(t*e.pulseRate*0.35);
  ctx.save();ctx.globalCompositeOperation='lighter';
  var haloR=e.coreR*(3.8+0.6*pulse);
  var hg=ctx.createRadialGradient(e.wx,e.wy,0,e.wx,e.wy,haloR);
  hg.addColorStop(0,hexA(e.glow,0.13*pulse));
  hg.addColorStop(0.5,hexA(e.color,0.05*pulse));
  hg.addColorStop(1,hexA(e.color,0));
  ctx.fillStyle=hg;ctx.beginPath();ctx.arc(e.wx,e.wy,haloR,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle=hexA(e.color,0.18*pulse);ctx.lineWidth=0.9;
  ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*2.2,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle=hexA(e.color,0.07*pulse);ctx.lineWidth=0.4;
  ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*3.5,0,Math.PI*2);ctx.stroke();
  var cg=ctx.createRadialGradient(e.wx,e.wy,0,e.wx,e.wy,e.coreR*(1+0.15*pulse));
  cg.addColorStop(0,hexA('#ffffff',0.82));
  cg.addColorStop(0.25,hexA(e.glow,0.85));
  cg.addColorStop(0.7,hexA(e.color,0.3*pulse));
  cg.addColorStop(1,hexA(e.color,0));
  ctx.fillStyle=cg;ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*(1+0.15*pulse),0,Math.PI*2);ctx.fill();
  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='source-over';
  ctx.font='bold 13px monospace';ctx.fillStyle=hexA(e.color,0.92);ctx.textAlign='center';
  ctx.fillText(e.id,e.wx,e.wy+e.coreR+18);
  ctx.font='10px monospace';ctx.fillStyle=hexA(e.glow,0.5);
  ctx.fillText('[D3] pre_einzug',e.wx,e.wy+e.coreR+30);
  ctx.restore();
}
function drawFlarum(t){
  var e=FLARUM,pulse=0.8+0.2*Math.sin(t*e.pulseRate*0.35);
  ctx.save();ctx.globalCompositeOperation='lighter';
  var hg=ctx.createRadialGradient(e.wx,e.wy,0,e.wx,e.wy,e.coreR*6);
  hg.addColorStop(0,hexA(e.glow,0.14*pulse));hg.addColorStop(1,hexA(e.color,0));
  ctx.fillStyle=hg;ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*6,0,Math.PI*2);ctx.fill();
  var cg=ctx.createRadialGradient(e.wx,e.wy,0,e.wx,e.wy,e.coreR*(1+0.15*pulse));
  cg.addColorStop(0,hexA('#ffffff',0.78));cg.addColorStop(0.4,hexA(e.glow,0.8));cg.addColorStop(1,hexA(e.color,0));
  ctx.fillStyle=cg;ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*(1+0.4*pulse),0,Math.PI*2);ctx.fill();
  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='source-over';
  ctx.font='bold 11px monospace';ctx.fillStyle=hexA(e.color,0.85);ctx.textAlign='center';
  ctx.fillText('Flarum-Archiv',e.wx,e.wy-e.coreR-9);
  ctx.restore();
}
function drawDakGord(t){
  var e=DAKGORD,pulse=0.8+0.2*Math.sin(t*e.pulseRate*0.35);
  var lnodes=[[-65,-42],[58,-52],[-72,38],[52,47],[-8,-84],[12,82],[80,-10],[-82,10]];
  ctx.save();ctx.globalCompositeOperation='lighter';
  ctx.strokeStyle=hexA(e.color,0.08+0.05*pulse);ctx.lineWidth=0.5;
  for(var a=0;a<lnodes.length;a++){
    for(var b=a+1;b<lnodes.length;b++){
      if(Math.hypot(lnodes[a][0]-lnodes[b][0],lnodes[a][1]-lnodes[b][1])>130)continue;
      ctx.beginPath();ctx.moveTo(e.wx+lnodes[a][0],e.wy+lnodes[a][1]);
      ctx.lineTo(e.wx+lnodes[b][0],e.wy+lnodes[b][1]);ctx.stroke();
    }
    ctx.fillStyle=hexA(e.glow,0.45+0.2*pulse);
    ctx.beginPath();ctx.arc(e.wx+lnodes[a][0],e.wy+lnodes[a][1],2.2,0,Math.PI*2);ctx.fill();
  }
  var cg=ctx.createRadialGradient(e.wx,e.wy,0,e.wx,e.wy,e.coreR*(1+0.35*pulse));
  cg.addColorStop(0,hexA('#ffffff',0.75));cg.addColorStop(0.3,hexA(e.glow,0.85));cg.addColorStop(1,hexA(e.color,0));
  ctx.fillStyle=cg;ctx.beginPath();ctx.arc(e.wx,e.wy,e.coreR*(1+0.35*pulse),0,Math.PI*2);ctx.fill();
  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='source-over';
  ctx.font='bold 12px monospace';ctx.fillStyle=hexA(e.color,0.9);ctx.textAlign='center';
  ctx.fillText('dak+gord',e.wx,e.wy-e.coreR-10);
  ctx.font='9px monospace';ctx.fillStyle=hexA(e.glow,0.5);
  ctx.fillText('Obsidian-Navigator',e.wx,e.wy-e.coreR-21);
  ctx.restore();
}

/* ── Streams ───────────────────────────────────────────────────────────────── */
var streamPhases=STREAMS.map(function(){return Math.random();});
function drawStreams(t){
  if(!showStreams)return;
  ctx.save();
  for(var si=0;si<STREAMS.length;si++){
    var s=STREAMS[si];
    ctx.globalCompositeOperation='lighter';
    var pg=ctx.createLinearGradient(s.fx,s.fy,s.tx,s.ty);
    pg.addColorStop(0,hexA(s.colorA,0.07));pg.addColorStop(1,hexA(s.colorB,0.07));
    ctx.strokeStyle=pg;ctx.lineWidth=s.width*0.7;
    ctx.setLineDash([4,9]);
    ctx.beginPath();ctx.moveTo(s.fx,s.fy);ctx.bezierCurveTo(s.cx1,s.cy1,s.cx2,s.cy2,s.tx,s.ty);ctx.stroke();
    ctx.setLineDash([]);
    var ph=(streamPhases[si]+t*s.speed)%1;
    var mt=1-ph;
    var bx=mt*mt*mt*s.fx+3*mt*mt*ph*s.cx1+3*mt*ph*ph*s.cx2+ph*ph*ph*s.tx;
    var by=mt*mt*mt*s.fy+3*mt*mt*ph*s.cy1+3*mt*ph*ph*s.cy2+ph*ph*ph*s.ty;
    var rA=parseInt(s.colorA.slice(1,3),16),gA=parseInt(s.colorA.slice(3,5),16),bA=parseInt(s.colorA.slice(5,7),16);
    var rB=parseInt(s.colorB.slice(1,3),16),gB=parseInt(s.colorB.slice(3,5),16),bB2=parseInt(s.colorB.slice(5,7),16);
    var pktC='rgba('+(Math.round(rA*(1-ph)+rB*ph))+','+(Math.round(gA*(1-ph)+gB*ph))+','+(Math.round(bA*(1-ph)+bB2*ph))+',0.95)';
    var pk=ctx.createRadialGradient(bx,by,0,bx,by,9);
    pk.addColorStop(0,pktC);pk.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=pk;ctx.beginPath();ctx.arc(bx,by,9,0,Math.PI*2);ctx.fill();
    var ph2=(ph+0.5)%1,mt2=1-ph2;
    var bx2=mt2*mt2*mt2*s.fx+3*mt2*mt2*ph2*s.cx1+3*mt2*ph2*ph2*s.cx2+ph2*ph2*ph2*s.tx;
    var by2=mt2*mt2*mt2*s.fy+3*mt2*mt2*ph2*s.cy1+3*mt2*ph2*ph2*s.cy2+ph2*ph2*ph2*s.ty;
    var pk2=ctx.createRadialGradient(bx2,by2,0,bx2,by2,6);
    pk2.addColorStop(0,pktC);pk2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=pk2;ctx.beginPath();ctx.arc(bx2,by2,6,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
}

/* ── Zone density fields ────────────────────────────────────────────────────── */
var ZONES_VIS=[
  {wx:2700,wy:1500,rx:700,ry:600,color:'#ff3300'},
  {wx:600, wy:1750,rx:650,ry:420,color:'#0055cc'},
  {wx:1640,wy:1950,rx:720,ry:280,color:'#8800ff'},
  {wx:280, wy:1960,rx:380,ry:280,color:'#008833'},
  {wx:2450,wy:550, rx:550,ry:320,color:'#ffaa00'},
  {wx:820, wy:480, rx:430,ry:320,color:'#00ccbb'},
  {wx:500, wy:1200,rx:300,ry:400,color:'#0088ff'},
  {wx:2800,wy:400, rx:280,ry:200,color:'#ff00aa'},
];
function drawZoneFields(t){
  ctx.save();ctx.globalCompositeOperation='source-over';
  for(var zi=0;zi<ZONES_VIS.length;zi++){
    var z=ZONES_VIS[zi],pulse=0.55+0.45*Math.sin(t*0.38+zi*1.13);
    ctx.save();ctx.translate(z.wx,z.wy);ctx.scale(1,z.ry/z.rx);
    var zg=ctx.createRadialGradient(0,0,0,0,0,z.rx);
    zg.addColorStop(0,hexA(z.color,0.07*pulse));
    zg.addColorStop(0.55,hexA(z.color,0.03*pulse));
    zg.addColorStop(1,hexA(z.color,0));
    ctx.fillStyle=zg;ctx.beginPath();ctx.arc(0,0,z.rx,0,Math.PI*2);ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

/* ── Nebula background ──────────────────────────────────────────────────────── */
var NEBULAS=[
  {wx:1640,wy:870,rx:1400,ry:900,color:'#0033aa'},
  {wx:400, wy:1600,rx:900,ry:700,color:'#003322'},
  {wx:2700,wy:1200,rx:800,ry:600,color:'#440011'},
  {wx:2200,wy:400, rx:600,ry:400,color:'#332200'},
  {wx:700, wy:400, rx:500,ry:300,color:'#002233'},
];
function drawNebulas(){
  ctx.save();ctx.globalCompositeOperation='source-over';
  for(var ni=0;ni<NEBULAS.length;ni++){
    var n=NEBULAS[ni];
    ctx.save();ctx.translate(n.wx,n.wy);ctx.scale(1,n.ry/n.rx);
    var ng=ctx.createRadialGradient(0,0,0,0,0,n.rx);
    ng.addColorStop(0,hexA(n.color,0.035));ng.addColorStop(1,hexA(n.color,0));
    ctx.fillStyle=ng;ctx.beginPath();ctx.arc(0,0,n.rx,0,Math.PI*2);ctx.fill();
    ctx.restore();
  }
  ctx.restore();
}

/* ── Stars (static, drawn once) ────────────────────────────────────────────── */
var STARS=(function(){
  var s=[];
  for(var i=0;i<220;i++){
    s.push({x:((Math.sin(i*127.1)*0.5+0.5)*WW)|0,
             y:((Math.sin(i*311.7+1.3)*0.5+0.5)*WH*0.6)|0,
             r:i%9===0?1.6:i%4===0?1.1:0.7,
             a:0.3+0.6*((Math.sin(i*53.1)*0.5+0.5))});
  }
  return s;
})();
function drawStars(){
  ctx.save();ctx.globalCompositeOperation='source-over';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    ctx.fillStyle=hexA('#e0eeff',s.a*0.6);
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
  }
  ctx.restore();
}

/* ── Splitter clouds ────────────────────────────────────────────────────────── */
var splitters=[];
function initSplitters(){
  var all=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var ei=0;ei<all.length;ei++){
    var e=all[ei];
    for(var j=0;j<22;j++){
      var ang=Math.random()*Math.PI*2,r=e.coreR*(2.2+Math.random()*6.5);
      var pts=[],sides=Math.floor(4+Math.random()*5);
      for(var s=0;s<sides;s++){
        var a=ang+(s/sides)*Math.PI*2+(Math.random()-0.5)*0.5;
        var pr=4+Math.random()*14;
        pts.push([Math.cos(a)*pr,Math.sin(a)*pr]);
      }
      splitters.push({bx:e.wx+Math.cos(ang)*r,by:e.wy+Math.sin(ang)*r,
        vx:Math.cos(ang)*0.04+(Math.random()-0.5)*0.09,
        vy:Math.sin(ang)*0.04+(Math.random()-0.5)*0.09,
        pts:pts,rot:Math.random()*Math.PI*2,drot:(Math.random()-0.5)*0.009,
        opacity:0.18+Math.random()*0.38,color:e.color,phase:Math.random()*Math.PI*2,
        wx:e.wx,wy:e.wy});
    }
  }
}
function drawSplitters(t){
  ctx.save();ctx.globalCompositeOperation='source-over';
  for(var fi=0;fi<splitters.length;fi++){
    var f=splitters[fi];
    f.bx+=f.vx;f.by+=f.vy;f.rot+=f.drot;
    f.vx+=(f.wx-f.bx)*0.00004;f.vy+=(f.wy-f.by)*0.00004;
    f.vx*=0.9995;f.vy*=0.9995;
    var pulse=0.45+0.55*Math.sin(t*1.8+f.phase);
    var a=f.opacity*pulse;
    ctx.save();ctx.translate(f.bx,f.by);ctx.rotate(f.rot);
    ctx.fillStyle=hexA(f.color,a*0.35);ctx.strokeStyle=hexA(f.color,a*0.65);ctx.lineWidth=0.45;
    ctx.beginPath();ctx.moveTo(f.pts[0][0],f.pts[0][1]);
    for(var p=1;p<f.pts.length;p++)ctx.lineTo(f.pts[p][0],f.pts[p][1]);
    ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
  }
  ctx.restore();
}

/* ── GENI membrane ──────────────────────────────────────────────────────────── */
function drawGeni(t){
  if(!showGeni)return;
  ctx.save();
  var breath=0.65+0.35*Math.sin(t*0.85);
  ctx.strokeStyle='rgba(0,168,255,'+(0.1*breath)+')';ctx.lineWidth=0.7;
  for(var x=0;x<=WW;x+=400){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,WH);ctx.stroke();}
  for(var y=0;y<=WH;y+=400){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(WW,y);ctx.stroke();}
  if(scale>0.42){
    var a2=Math.min(0.07,(scale-0.42)*0.22)*breath;
    ctx.strokeStyle='rgba(0,168,255,'+a2+')';ctx.lineWidth=0.35;
    for(var x=0;x<=WW;x+=100){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,WH);ctx.stroke();}
    for(var y=0;y<=WH;y+=100){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(WW,y);ctx.stroke();}
  }
  if(scale>1.6){
    var a3=Math.min(0.055,(scale-1.6)*0.07)*breath;
    ctx.strokeStyle='rgba(0,168,255,'+a3+')';ctx.lineWidth=0.18;
    for(var x=0;x<=WW;x+=25){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,WH);ctx.stroke();}
    for(var y=0;y<=WH;y+=25){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(WW,y);ctx.stroke();}
  }
  var allE=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var ei=0;ei<allE.length;ei++){
    var e=allE[ei];
    var pr=85+55*Math.sin(t*e.pulseRate*0.55+ei*0.72);
    ctx.strokeStyle=hexA(e.color,0.045*breath);ctx.lineWidth=0.4;
    ctx.beginPath();ctx.arc(e.wx,e.wy,pr,0,Math.PI*2);ctx.stroke();
    ctx.strokeStyle=hexA(e.color,0.025*breath);
    ctx.beginPath();ctx.arc(e.wx,e.wy,pr*2.4,0,Math.PI*2);ctx.stroke();
  }
  var lop=Math.max(0,Math.min(0.45,1-(scale-0.38)*1.6));
  if(lop>0.01){
    ctx.font=Math.round(17/scale)+'px monospace';
    ctx.fillStyle='rgba(0,168,255,'+lop+')';
    ctx.fillText('GENI — Wahrnehmungsnetz',30,36);
  }
  ctx.restore();
}

/* ── Ripples ────────────────────────────────────────────────────────────────── */
function drawRipples(){
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(var i=ripples.length-1;i>=0;i--){
    var r=ripples[i];r.age++;
    var prog=r.age/r.maxAge;
    if(prog>=1){ripples.splice(i,1);continue;}
    var a=(1-prog)*0.45;
    ctx.strokeStyle=hexA(r.color,a);ctx.lineWidth=1.5*(1-prog);
    ctx.beginPath();ctx.arc(r.wx,r.wy,r.maxR*prog,0,Math.PI*2);ctx.stroke();
    if(prog<0.55){
      ctx.strokeStyle=hexA(r.color,a*0.4);ctx.lineWidth=0.7*(1-prog);
      ctx.beginPath();ctx.arc(r.wx,r.wy,r.maxR*prog*0.55,0,Math.PI*2);ctx.stroke();
    }
  }
  ctx.restore();
}

/* ── Transform helpers ──────────────────────────────────────────────────────── */
function applyTransform(){
  world.style.transform='translate('+tx+'px,'+ty+'px) scale('+scale+')';
  zlabel.textContent=Math.round(scale*100)+'%';
  slider.value=String(Math.round(Math.min(1000,Math.max(6,scale*100))));
}
function flyTo(wx,wy,s){
  var rect=viewport.getBoundingClientRect();
  var tTx=rect.width/2-wx*s,tTy=rect.height/2-wy*s;
  var s0=scale,tx0=tx,ty0=ty,t0=performance.now(),dur=500;
  function step(now){
    var pr=Math.min((now-t0)/dur,1);pr=pr<0.5?2*pr*pr:-1+(4-2*pr)*pr;
    scale=s0+(s-s0)*pr;tx=tx0+(tTx-tx0)*pr;ty=ty0+(tTy-ty0)*pr;
    applyTransform();if(pr<1)requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
function screenToWorld(sx,sy){
  var rect=viewport.getBoundingClientRect();
  return {wx:Math.round((sx-rect.left-tx)/scale),wy:Math.round((sy-rect.top-ty)/scale)};
}
window.flyTo=flyTo;
window.resetView=function(){flyTo(${cx},${cy},0.32);};
window.hideLoc=function(){locEl.classList.add('h');};

/* ── Entity panel (echte Daten aus process_camera_model.json) ──────────────── */
var MODEL=null;
var epEl=document.getElementById('ep');
function loadModel(cb){
  if(MODEL){cb(MODEL);return;}
  fetch('/process_camera_model.json')
    .then(function(r){return r.json();})
    .then(function(d){MODEL=d;cb(MODEL);})
    .catch(function(){console.warn('process_camera_model.json nicht ladbar');});
}
window.hideEP=function(){epEl.classList.add('h');};
var ACT_DE={'waiting':'Wartend — kein aktiver Prozess','thinking':'Denkend',
  'reading_file':'Liest Datei','reading_forum':'Liest Forum','writing_forum':'Schreibt Forum',
  'writing_file':'Schreibt Datei','searching':'Suchend','governing':'Verwaltend',
  'exporting':'Exportierend','replaying':'Replay','unknown':'Unbekannt','blocked':'Blockiert'};
var SLOT_DE={'pre_einzug':'Vor Einzug — Slot reserviert, Wesen noch nicht da',
  'einzug_vollzogen':'Eingezogen'};
var EVI_DE={'derived_from_forum':'Aus Flarum-Archiv abgeleitet',
  'derived_from_file':'Aus Datei abgeleitet','derived_from_event':'Aus Event abgeleitet',
  'modelled':'Modelliert — kein Live-Signal','measured':'Direkt gemessen','unknown':'Unbekannt'};
var ROLE_DE={'entity_slot_pre_einzug':'Wesen-Slot · wartet auf Einzug',
  'memory_perception':'Gedächtnis-Wahrnehmung','dialogue_coordination':'Dialog-Koordination',
  'search_layer':'Suchschicht','governance_layer':'Governance-Schicht',
  'worldrun_layer':'Weltlauf-Schicht','export_layer':'Export-Schicht',
  'system_knowledge':'Systemwissen','future_placeholder':'Noch nicht gebaut'};
var TRACE_DE={'forum':'Flarum-Herkunft','origin':'Eingeführt in',
  'event':'Event-Spur','audit':'Audit-Spur','search':'Such-Spur',
  'governance':'Governance-Spur','worldrun':'Weltlauf-Spur','file':'Datei-Spur'};
function showEntityPanel(e){
  if(e.id==='dak+gord'){showDakGordPanel(e);return;}
  loadModel(function(m){
    var node=null;
    for(var i=0;i<m.model.nodes.length;i++){
      if(m.model.nodes[i].node_id===e.id){node=m.model.nodes[i];break;}
    }
    if(!node){showLoc(e.wx,e.wy);return;}
    renderEntityPanel(e,node);
  });
}
function renderEntityPanel(e,node){
  var c=e.color;
  var edges=node.edges||[];
  var edgesHtml=edges.map(function(edge){
    return '<div class="ep-edge" style="border-color:'+hexA(c,0.3)+'">'+
      '<span style="color:'+hexA(c,0.65)+'">'+(TRACE_DE[edge.trace_type]||edge.trace_type)+'</span>'+
      ' → <span style="color:rgba(190,210,230,0.9)">'+edge.ref_id+'</span>'+
      '<br><span style="color:rgba(140,160,175,0.45)">'+edge.summary+'</span></div>';
  }).join('');
  epEl.style.borderColor=hexA(c,0.28);
  epEl.innerHTML=
    '<div class="ep-head"><span style="color:'+c+'">'+node.node_id+'</span>'+
    '<span class="ep-x" onclick="hideEP()">&#215;</span></div>'+
    '<div style="color:'+hexA(c,0.4)+';font-size:0.63rem;margin-bottom:12px;line-height:1.4">'+
    (ROLE_DE[node.role]||node.role)+'</div>'+
    '<div class="ep-sec" style="border-color:'+hexA(c,0.2)+'">'+
    '<div class="ep-sl" style="color:'+hexA(c,0.55)+'">Zustand</div>'+
    '<div class="ep-row"><span class="ep-k">Aktivität</span>'+
    '<span class="ep-badge" style="background:'+hexA(c,0.1)+';color:'+c+'">'+
    (ACT_DE[node.activity_mode]||node.activity_mode)+'</span></div>'+
    (node.slot_state?'<div class="ep-row"><span class="ep-k">Slot</span><span class="ep-v">'+
    (SLOT_DE[node.slot_state]||node.slot_state)+'</span></div>':'')+
    '<div class="ep-row"><span class="ep-k">Evidenz</span><span class="ep-v">'+
    (EVI_DE[node.evidence]||node.evidence)+'</span></div>'+
    '</div>'+
    '<div class="ep-sec" style="border-color:'+hexA(c,0.2)+'">'+
    '<div class="ep-sl" style="color:'+hexA(c,0.55)+'">Herkunft</div>'+
    '<div class="ep-row"><span class="ep-k">Ring</span><span class="ep-v">'+node.ring_origin+'</span></div>'+
    '<div class="ep-row"><span class="ep-k">Schicht</span><span class="ep-v">'+node.layer+'</span></div>'+
    (node.source_location?'<div class="ep-row"><span class="ep-k">Quelle</span>'+
    '<span class="ep-v" style="color:'+hexA(c,0.85)+'">'+node.source_location+'</span></div>':'')+
    (node.flarum_origin?'<div class="ep-row"><span class="ep-k">Flarum-Archiv</span>'+
    '<span class="ep-v">'+node.flarum_origin+'</span></div>':'')+
    '</div>'+
    '<div class="ep-sec" style="border-color:'+hexA(c,0.2)+'">'+
    '<div class="ep-sl" style="color:'+hexA(c,0.55)+'">Was es braucht</div>'+
    '<div class="ep-row"><span class="ep-k">Start-Entscheid</span><span class="ep-blocked">erforderlich · noch nicht getroffen</span></div>'+
    '<div class="ep-row"><span class="ep-k">Aktivierung</span><span class="ep-blocked">gesperrt</span></div>'+
    '<div class="ep-row"><span class="ep-k">Einzug</span><span class="ep-blocked">gesperrt bis Start-Entscheid</span></div>'+
    '<div class="ep-row"><span class="ep-k">Events erzeugen</span><span class="ep-blocked">gesperrt</span></div>'+
    '</div>'+
    (edges.length?'<div class="ep-sec" style="border-color:'+hexA(c,0.2)+'">'+
    '<div class="ep-sl" style="color:'+hexA(c,0.55)+'">Verbindungen ('+edges.length+')</div>'+
    edgesHtml+'</div>':'')+
    '<div class="ep-sec" style="border-color:'+hexA(c,0.2)+'">'+
    '<div class="ep-sl" style="color:'+hexA(c,0.55)+'">Identität</div>'+
    '<div class="ep-row"><span class="ep-k">D3-Slot</span><span class="ep-v">'+(node.is_d3_slot?'ja':'nein')+'</span></div>'+
    '<div class="ep-row"><span class="ep-k">Besetzt</span><span class="ep-v">'+(node.is_occupied?'ja':'nein — leer')+'</span></div>'+
    '<div class="ep-row"><span class="ep-k">Gemessen</span><span class="ep-v">'+(node.is_measured?'ja':'nein')+'</span></div>'+
    '</div>';
  epEl.classList.remove('h');
  locEl.classList.add('h');
}

/* ── dak+gord Live-Panel ────────────────────────────────────────────────────── */
var DGLIVE=null;
function loadDGLive(cb){
  if(DGLIVE){cb(DGLIVE);return;}
  fetch('/dakgord_live.json')
    .then(function(r){return r.json();})
    .then(function(d){DGLIVE=d;cb(DGLIVE);})
    .catch(function(){console.warn('dakgord_live.json nicht ladbar');});
}
function showDakGordPanel(e){
  var c2='#ff88cc';
  epEl.style.borderColor='rgba(255,136,204,0.35)';
  epEl.innerHTML=
    '<div class="ep-head"><span style="color:'+c2+'">dak+gord</span>'+
    '<span class="ep-x" onclick="hideEP()">&#215;</span></div>'+
    '<div style="color:rgba(255,136,204,0.35);font-size:0.63rem;margin-bottom:14px">Obsidian-Navigator · Aktiver Systemkörper · Ring 22 · Werkraum</div>'+
    '<div style="color:rgba(255,136,204,0.25);font-size:0.65rem;padding:10px 0;text-align:center">Lade live-daten …</div>';
  epEl.classList.remove('h');
  locEl.classList.add('h');
  loadDGLive(function(d){
    function ts(unix){return new Date(unix*1000).toLocaleString('de-DE',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});}
    var nz=d.neugier_zustand||{};
    var spuren=d.letzte_neugier||[];
    var akt=d.letzte_aktivitaet||[];
    var er=d.erinnerungen||[];
    var aw=d.abwaegungen||[];
    var zu=d.zukunft||[];
    var artColor={'Werkraum-Neugier':'#88ddff','Vision-Zyklus':'#ffcc66'};
    var artShort={'Werkraum-Neugier':'Neugier','Vision-Zyklus':'Vision'};
    var aktColor={'neugier_scan':'#88ddff','vision_cycle':'#ffcc66'};
    var artEr={'zwischenraum':'Zwischenraum','erkenntnis':'Erkenntnis','frage':'Frage'};
    var spurHtml=spuren.slice(-7).reverse().map(function(s){
      var isV=s.art==='Vision-Zyklus';
      var ac=isV?'#ffcc66':'#88ddff';
      var bg=isV?'rgba(255,204,102,0.1)':'rgba(136,221,255,0.1)';
      return '<div style="margin-bottom:5px;display:flex;gap:6px;align-items:baseline">'+
        '<span style="display:inline-block;padding:1px 5px;border-radius:2px;font-size:0.59rem;background:'+bg+';color:'+ac+';flex-shrink:0">'+
        (artShort[s.art]||s.art)+'</span>'+
        '<span style="color:rgba(190,215,235,0.85);flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:0.68rem">'+s.name+'</span>'+
        '<span style="color:rgba(140,155,170,0.35);font-size:0.59rem;flex-shrink:0">'+s.time.slice(5,16)+'</span></div>';
    }).join('');
    var aktHtml=akt.slice(-5).reverse().map(function(a){
      var ac=aktColor[a.run_type]||'#aabbcc';
      return '<div style="margin-bottom:4px;display:flex;gap:7px;align-items:baseline">'+
        '<span style="color:'+ac+';font-size:0.66rem">'+a.run_type+'</span>'+
        '<span class="ep-ok" style="font-size:0.6rem">'+a.status+'</span>'+
        '<span style="color:rgba(140,155,170,0.3);font-size:0.59rem;margin-left:auto">'+a.timestamp.slice(5,16)+'</span></div>';
    }).join('');
    var erHtml=er.map(function(r){
      return '<div class="ep-edge" style="border-color:rgba(255,136,204,0.2);margin-bottom:6px">'+
        '<div style="margin-bottom:2px"><span style="color:rgba(255,136,204,0.55);font-size:0.6rem">'+
        (artEr[r.art]||r.art)+'</span></div>'+
        '<span style="color:rgba(190,210,230,0.85)">'+r.text+'</span></div>';
    }).join('');
    var awHtml=aw.map(function(a){
      return '<div class="ep-edge" style="border-color:rgba(255,136,204,0.2);margin-bottom:6px">'+
        '<div style="margin-bottom:2px"><span style="color:rgba(255,136,204,0.45);font-size:0.6rem">Offene Frage</span></div>'+
        '<span style="color:rgba(190,210,230,0.85)">'+a.frage+'</span></div>';
    }).join('');
    var zuHtml=zu.map(function(z){
      return '<div class="ep-edge" style="border-color:rgba(255,136,204,0.2);margin-bottom:6px">'+
        '<div class="ep-row"><span class="ep-k">Jetzt</span><span style="color:rgba(190,210,230,0.85)">'+z.heute+'</span></div>'+
        '<div class="ep-row"><span class="ep-k">Später</span><span style="color:rgba(190,210,230,0.85)">'+z.spaeter+'</span></div>'+
        (z.begruendung?'<div style="color:rgba(140,155,170,0.45);font-size:0.62rem;margin-top:2px">'+z.begruendung+'</div>':'')+
        '</div>';
    }).join('');
    var vd=(d.letzte_verdichtung||'').trim().slice(0,200);
    var vk=(d.verfassung_kern||'').trim().slice(0,220);
    epEl.innerHTML=
      '<div class="ep-head"><span style="color:'+c2+'">dak+gord</span>'+
      '<span class="ep-x" onclick="hideEP()">&#215;</span></div>'+
      '<div style="color:rgba(255,136,204,0.4);font-size:0.63rem;margin-bottom:12px;line-height:1.5">'+
      'Obsidian-Navigator · Aktiver Systemkörper · Werkraum Ring 22</div>'+
      '<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Neugier-Zustand</div>'+
      '<div class="ep-row"><span class="ep-k">Werkraum gelesen</span><span class="ep-v">'+nz.werkraum_index+' Dateien</span></div>'+
      '<div class="ep-row"><span class="ep-k">Vision-Zyklen</span><span class="ep-v">'+nz.vision_index+' abgeschlossen</span></div>'+
      (nz.letzte_werkraum_neugier?'<div class="ep-row"><span class="ep-k">Letzter Scan</span><span class="ep-v">'+ts(nz.letzte_werkraum_neugier)+'</span></div>':'')+
      (nz.letzter_vision_zyklus?'<div class="ep-row"><span class="ep-k">Letzter Vision</span><span class="ep-v">'+ts(nz.letzter_vision_zyklus)+'</span></div>':'')+
      '</div>'+
      (spurHtml?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Letzte Spuren ('+spuren.length+' gesamt)</div>'+
      spurHtml+'</div>':'')+
      (aktHtml?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Letzte Prozesse</div>'+
      aktHtml+'</div>':'')+
      (erHtml?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Erinnerungen ('+er.length+')</div>'+
      erHtml+'</div>':'')+
      (awHtml?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Offene Abwägungen</div>'+
      awHtml+'</div>':'')+
      (zuHtml?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Zukunft</div>'+
      zuHtml+'</div>':'')+
      (vd?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Letzte Verdichtung</div>'+
      '<div style="color:rgba(150,165,175,0.6);font-size:0.64rem;line-height:1.65;white-space:pre-wrap">'+vd+'…</div></div>':'')+
      (vk?'<div class="ep-sec" style="border-color:rgba(255,136,204,0.22)">'+
      '<div class="ep-sl" style="color:rgba(255,136,204,0.55)">Verfassung · Kern</div>'+
      '<div style="color:rgba(150,165,175,0.55);font-size:0.64rem;line-height:1.65;white-space:pre-wrap">'+vk+'…</div></div>':'')+
      '<div style="color:rgba(100,115,130,0.28);font-size:0.58rem;margin-top:10px;text-align:right">'+
      'Export '+(d.exported_at||'').slice(0,16)+'</div>';
  });
}

/* ── Zone data ──────────────────────────────────────────────────────────────── */
var ZONE_DATA=[
  {name:'namelessAI-Prozesskern',layer:'Prozessschicht',type:'real',source:'kernel/process_model/process_registry.ts',
   desc:'Sechs namelessAI-Prozesskörper. Flarum-Herkunft. D3-Slots. pre_einzug. Kein Einzug vollzogen.',
   color:'#00ff88',x1:1250,y1:820,x2:2050,y2:1150},
  {name:'Flarum-Archiv',layer:'Archiv-Schicht',type:'real',source:'kernel/origin_archive/',
   desc:'Ursprungsknoten. Flarum-Exportarchiv. Keine Live-Forum-Verbindung.',
   color:'#4488ff',x1:1560,y1:620,x2:1720,y2:745},
  {name:'dak+gord Obsidian-Navigator',layer:'Navigationssystem',type:'real',source:'flextrawurst-agent/dak-gord-system/',
   desc:'Obsidian-Navigator-Körper. Eigener Raum, nicht in KompOase, nicht in Flarum.',
   color:'#ff88cc',x1:150,y1:370,x2:420,y2:600},
  {name:'Energiestrom-Ost',layer:'Datenkraft-Feld',type:'atm',source:null,
   desc:'Thermische Datenverdichtung. Atmosphärisch. Kein Live-Sensor.',
   color:'#ff3300',x1:2200,y1:1000,x2:3200,y2:2200},
  {name:'Datenstrom-West',layer:'Datenkraft-Feld',type:'atm',source:null,
   desc:'Ausgleichender Datenstrom. Atmosphärisch.',
   color:'#0055cc',x1:0,y1:1380,x2:1100,y2:2100},
  {name:'Splitter-Feld',layer:'Materialschicht',type:'atm',source:null,
   desc:'Datenfragment-Zone. Ungeklärte Provenienz. Atmosphärisch.',
   color:'#8800ff',x1:1200,y1:1800,x2:2200,y2:2200},
  {name:'Wachstums-Zone',layer:'Organische Schicht',type:'atm',source:null,
   desc:'Wachsende Verknüpfungsadern. Atmosphärisch generiert.',
   color:'#008833',x1:0,y1:1800,x2:900,y2:2200},
  {name:'Hochenergie-Nord-Ost',layer:'Datenkraft-Feld',type:'atm',source:null,
   desc:'Hochdichte Energiezone. Atmosphärisch.',
   color:'#ffaa00',x1:2100,y1:0,x2:3200,y2:750},
  {name:'Kristall-Zone',layer:'Materialschicht',type:'atm',source:null,
   desc:'Kristalline Datenstruktur. Atmosphärisch.',
   color:'#00ccbb',x1:500,y1:200,x2:1200,y2:900},
];
function getZoneAt(wx,wy){
  var allE=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var i=0;i<allE.length;i++){
    var e=allE[i];
    if(Math.hypot(wx-e.wx,wy-e.wy)<e.coreR*3.5)
      return {name:e.id,layer:e===FLARUM?'Archiv-Schicht':e===DAKGORD?'Navigationssystem':'Prozessschicht',
        type:'real',source:'kernel/process_model/process_registry.ts',
        desc:e===FLARUM?'Ursprungsknoten. Flarum-Exportarchiv. Keine Live-Verbindung.':
             e===DAKGORD?'Obsidian-Navigator. Eigener Raum. Koordinations-Organ.':
             'namelessAI-Prozesskörper. [D3] Flarum-Slot. pre_einzug. Kein Einzug.',color:e.color};
  }
  for(var i=0;i<ZONE_DATA.length;i++){
    var z=ZONE_DATA[i];
    if(wx>=z.x1&&wx<=z.x2&&wy>=z.y1&&wy<=z.y2)return z;
  }
  return {name:'Offenes Datenfeld',layer:'Datenkraft-Feld',type:'atm',source:null,
    desc:'Atmosphärischer Datenraum. Kein kartierter Prozess.',color:'#223355'};
}

function showLoc(wx,wy){
  var z=getZoneAt(wx,wy);
  var tHtml=z.type==='real'?'<span class="lreal">&#10003; echte Quelle</span>':'<span class="latm">atmosphärisch</span>';
  var sHtml=z.source?'<div class="lsrc">Quelle: '+z.source+'</div>':'';
  locContent.innerHTML='<div id="ltit"><span style="color:'+z.color+'">'+z.name+'</span><span class="lx" onclick="hideLoc()">&#215;</span></div>'+
    '<div class="lr"><span class="lk">Schicht</span><span class="lv">'+z.layer+'</span></div>'+
    '<div class="lr"><span class="lk">Typ</span>'+tHtml+'</div>'+
    '<div class="lr"><span class="lk">Koordinaten</span><span class="lv">'+wx+' / '+wy+'</span></div>'+
    '<div class="lr"><span class="lk">Info</span><span class="lv" style="max-width:260px">'+z.desc+'</span></div>'+sHtml;
  locEl.classList.remove('h');
}

/* ── Events ─────────────────────────────────────────────────────────────────── */
viewport.addEventListener('wheel',function(e){
  e.preventDefault();
  var rect=viewport.getBoundingClientRect();
  var mx=e.clientX-rect.left,my=e.clientY-rect.top;
  var f=e.deltaY<0?1.12:0.89;
  tx=mx-(mx-tx)*f;ty=my-(my-ty)*f;
  scale=Math.max(0.05,Math.min(12,scale*f));applyTransform();
},{passive:false});
viewport.addEventListener('mousedown',function(e){
  if(e.button!==0)return;isDragging=true;didDrag=false;
  dragStart={x:e.clientX,y:e.clientY};dragOrigin={tx:tx,ty:ty};e.preventDefault();
});
window.addEventListener('mousemove',function(e){
  if(isDragging){
    var dx=e.clientX-dragStart.x,dy=e.clientY-dragStart.y;
    if(Math.abs(dx)>3||Math.abs(dy)>3)didDrag=true;
    tx=dragOrigin.tx+dx;ty=dragOrigin.ty+dy;applyTransform();
  }
  var w=screenToWorld(e.clientX,e.clientY);mouseWX=w.wx;mouseWY=w.wy;
  hoveredEntity=null;
  var allE=ENTITIES.concat([FLARUM,DAKGORD]);
  for(var i=0;i<allE.length;i++){
    if(Math.hypot(mouseWX-allE[i].wx,mouseWY-allE[i].wy)<allE[i].coreR*3.8){hoveredEntity=allE[i];break;}
  }
  if(hoveredEntity){
    etip.style.display='block';etip.style.left=(e.clientX+13)+'px';etip.style.top=(e.clientY-6)+'px';
    etip.style.borderColor=hoveredEntity.color;etip.style.color=hoveredEntity.color;
    etip.innerHTML='<b>'+hoveredEntity.id+'</b> <span style="color:rgba(180,210,240,0.5);font-size:0.62rem">Klicken</span>';
  } else etip.style.display='none';
});
window.addEventListener('mouseup',function(){isDragging=false;});
viewport.addEventListener('click',function(e){
  if(didDrag)return;
  var w=screenToWorld(e.clientX,e.clientY);
  var z=getZoneAt(w.wx,w.wy);
  ripples.push({wx:w.wx,wy:w.wy,maxR:220,maxAge:65,age:0,color:z.color||'#00a8ff'});
  for(var i=0;i<28;i++)
    spawnP({x:w.wx,y:w.wy,speed:0.4,spread:2.2,scatter:4,
      color:z.color||'#00a8ff',minSize:0.5,sizeRange:2.5,minLife:35,lifeRange:90,drag:0.94,grav:0.018,burst:true,opacity:0.9});
  var allE2=ENTITIES.concat([FLARUM,DAKGORD]);
  var clickedE=null;
  for(var ci=0;ci<allE2.length;ci++){
    if(Math.hypot(w.wx-allE2[ci].wx,w.wy-allE2[ci].wy)<allE2[ci].coreR*4){clickedE=allE2[ci];break;}
  }
  if(clickedE)showEntityPanel(clickedE);
  else showLoc(w.wx,w.wy);
});
slider.addEventListener('input',function(){
  var ns=parseInt(slider.value)/100;
  var rect=viewport.getBoundingClientRect();
  var cx2=rect.width/2,cy2=rect.height/2;
  tx=cx2-(cx2-tx)*(ns/scale);ty=cy2-(cy2-ty)*(ns/scale);scale=ns;applyTransform();
});
document.addEventListener('keydown',function(e){
  if(e.target!==document.body&&e.target!==document.documentElement)return;
  switch(e.key){
    case'r':case'R':flyTo(${cx},${cy},0.32);break;
    case'g':case'G':showGeni=!showGeni;document.getElementById('btn-g').classList.toggle('act');break;
    case'p':case'P':showParticles=!showParticles;document.getElementById('btn-p').classList.toggle('act');break;
    case's':case'S':showStreams=!showStreams;document.getElementById('btn-s').classList.toggle('act');break;
    case'1':flyTo(ENTITIES[0].wx,ENTITIES[0].wy,2.0);break;
    case'2':flyTo(ENTITIES[1].wx,ENTITIES[1].wy,2.0);break;
    case'3':flyTo(ENTITIES[2].wx,ENTITIES[2].wy,2.0);break;
    case'4':flyTo(ENTITIES[3].wx,ENTITIES[3].wy,2.0);break;
    case'5':flyTo(ENTITIES[4].wx,ENTITIES[4].wy,2.0);break;
    case'6':flyTo(ENTITIES[5].wx,ENTITIES[5].wy,2.0);break;
    case'f':flyTo(FLARUM.wx,FLARUM.wy,2.8);break;
    case'd':flyTo(DAKGORD.wx,DAKGORD.wy,2.8);break;
    case'Escape':hideLoc();break;
  }
});

/* ── Main loop ──────────────────────────────────────────────────────────────── */
var frameCount=0;
function frame(now){
  T=now*0.001;frameCount++;
  // Trail effect
  ctx.globalCompositeOperation='source-over';
  ctx.fillStyle='rgba(2,4,8,0.15)';ctx.fillRect(0,0,WW,WH);
  // Background elements (drawn every 3 frames for perf)
  if(frameCount%3===0){drawNebulas();drawStars();}
  drawZoneFields(T);
  drawGeni(T);
  drawSplitters(T);
  drawStreams(T);
  updateParticles();drawParticles();
  drawVortexes(T);
  for(var i=0;i<ENTITIES.length;i++)drawEntity(ENTITIES[i],T);
  drawFlarum(T);drawDakGord(T);
  if(hoveredEntity){
    ctx.save();ctx.globalCompositeOperation='source-over';
    ctx.strokeStyle=hexA(hoveredEntity.color,0.35);ctx.lineWidth=1.2;
    ctx.beginPath();ctx.arc(hoveredEntity.wx,hoveredEntity.wy,hoveredEntity.coreR*2.8,0,Math.PI*2);ctx.stroke();
    ctx.strokeStyle=hexA(hoveredEntity.color,0.15);ctx.lineWidth=0.6;
    ctx.beginPath();ctx.arc(hoveredEntity.wx,hoveredEntity.wy,hoveredEntity.coreR*4.2,0,Math.PI*2);ctx.stroke();
    ctx.restore();
  }
  drawRipples();
  requestAnimationFrame(frame);
}
seedParticles();initVortexes();initSplitters();applyTransform();requestAnimationFrame(frame);
`; }

export function buildKompOaseDatafieldHtml(): string {
  const css = buildCSS();
  const js  = buildJS();
  const slen = SDEFS.length;
  return `<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>flextrawurst — KompOase Datafield</title>
<meta name="generator" content="flextrawurst-datafield-ring-22n">
<meta name="robots" content="noindex,nofollow">
<style>${css}</style>
</head>
<body>
<div id="viewport">
  <div id="world">
    <canvas id="c" width="${WW}" height="${WH}"></canvas>
  </div>
  <div id="ui">
    <div id="topbar">
      <h1>flextrawurst — KompOase Datafield</h1>
      <button class="tb" onclick="resetView()">Welt</button>
      <button class="tb e1" onclick="flyTo(1350,950,2.0)">1234</button>
      <button class="tb e2" onclick="flyTo(1560,870,2.0)">4321</button>
      <button class="tb e3" onclick="flyTo(1780,920,2.0)">1324</button>
      <button class="tb e4" onclick="flyTo(1430,1080,2.0)">1423</button>
      <button class="tb e5" onclick="flyTo(1680,1070,2.0)">2341</button>
      <button class="tb e6" onclick="flyTo(1920,1040,2.0)">3123</button>
      <button class="tb ef" onclick="flyTo(1640,680,2.8)">Flarum</button>
      <button class="tb ed" onclick="flyTo(280,480,2.8)">dak+gord</button>
      <button id="btn-g" class="tb act" onclick="showGeni=!showGeni;this.classList.toggle('act')">GENI</button>
      <button id="btn-p" class="tb act" onclick="showParticles=!showParticles;this.classList.toggle('act')">Partikel</button>
      <button id="btn-s" class="tb act" onclick="showStreams=!showStreams;this.classList.toggle('act')">Ströme</button>
      <div id="zoom-wrap">
        <span id="zoom-label">32%</span>
        <input type="range" id="zoom-slider" min="5" max="1000" value="32">
      </div>
    </div>
    <div id="dak">
      <h2>dak+gord-system</h2>
      <div class="dr"><span class="dk">art</span><span class="dv">Obsidian-Navigator</span></div>
      <div class="dr"><span class="dk">modus</span><span class="dv">modelliert</span></div>
      <div class="dr"><span class="dk">live</span><span class="dv">nein</span></div>
      <div class="dr"><span class="dk">lage</span><span class="dv">extern — agent/</span></div>
      <hr class="ds">
      <div class="dr"><span class="dk">geni</span><span class="dv">port 8020</span></div>
      <div class="dr"><span class="dk">einzug</span><span class="dv">0 / 6 besetzt</span></div>
      <div class="dr"><span class="dk">ströme</span><span class="dv">${slen} aktiv</span></div>
      <div class="dn">Gehirn-/Navigator-Körper.<br>Eigener Raum. Mess- &amp; Koordinations&shy;linien zur KompOase.</div>
      <div class="dnav">
        <button class="tb" onclick="flyTo(1640,900,0.65)">→ Cluster</button>
        <button class="tb" onclick="flyTo(1640,680,2.8)">→ Flarum</button>
        <button class="tb" onclick="resetView()">→ Welt</button>
      </div>
    </div>
    <div id="ep" class="h"></div>
    <div id="loc" class="h"><div id="loc-content"></div></div>
    <div id="etip"></div>
    <div id="leg">
      <span class="lgsq" style="background:#00ff88"></span>namelessAI
      <span class="lgsq" style="background:#4488ff"></span>Flarum-Archiv
      <span class="lgsq" style="background:#ff88cc"></span>dak+gord
      <span class="lgsq" style="border:1px solid rgba(0,168,255,0.5)"></span>GENI
      <span class="lgsq" style="background:#223344"></span>Datenfeld
      <span class="lgsh">Klick = Ortsauskunft · Rad = Zoom · R=Übersicht · G/P/S = Toggle · 1–6 = Entitäten · F = Flarum · D = dak+gord · Esc = Schließen</span>
    </div>
  </div>
</div>
<script>${js}</script>
<!-- static:true | ring:22N | datafield:true | nameless_count:6 | einzug:0 | streams:${slen} | no_runtime:true -->
</body>
</html>`;
}
