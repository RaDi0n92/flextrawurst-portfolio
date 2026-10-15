#!/usr/bin/env python3
"""
Generiert Light-Mode Canvas-Szenen für flextrawurst.
Stil: Tinte auf Pergament — warm, sichtbar, individuell.
"""

JS = r"""
  // ── LIGHT MODE CANVAS SCENES (Tinte auf Pergament) ──────────────────────
  function lmVig(c){
    const vg=c.createRadialGradient(W*.5,H*.5,H*.28,W*.5,H*.5,Math.max(W,H)*.85);
    vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(140,100,60,.07)');
    c.fillStyle=vg;c.fillRect(0,0,W,H);
  }
  const LM={
    leitstand(c,t){
      c.fillStyle='#f3ede4';c.fillRect(0,0,W,H);
      const nd=[{x:.18,y:.3,r:3,cl:[160,100,40]},{x:.5,y:.2,r:2.5,cl:[140,80,40]},{x:.82,y:.3,r:3,cl:[160,100,40]},
        {x:.3,y:.55,r:2.5,cl:[80,120,80]},{x:.5,y:.65,r:3.5,cl:[180,120,40]},{x:.7,y:.5,r:2.5,cl:[120,80,160]},
        {x:.18,y:.7,r:2,cl:[160,100,40]},{x:.85,y:.6,r:2,cl:[80,120,80]},{x:.42,y:.82,r:2,cl:[140,80,40]},{x:.65,y:.78,r:2,cl:[160,100,40]}];
      const ed=[[0,4],[1,4],[2,5],[3,4],[4,5],[3,6],[5,7],[4,8],[8,9],[0,3],[1,2],[5,7]];
      ed.forEach(([a,b])=>{
        const p=Math.sin(t*.014+a*1.4+b*.8)*.5+.5,[r,g,bl]=nd[a].cl;
        c.beginPath();c.moveTo(nd[a].x*W,nd[a].y*H);c.lineTo(nd[b].x*W,nd[b].y*H);
        c.strokeStyle=`rgba(${r},${g},${bl},${p*.28+.08})`;c.lineWidth=p*1.8+.5;c.stroke();
        const tp=(t*.007+a*.4)%1,tx=nd[a].x*W+(nd[b].x-nd[a].x)*W*tp,ty=nd[a].y*H+(nd[b].y-nd[a].y)*H*tp;
        c.beginPath();c.arc(tx,ty,2.5,0,Math.PI*2);c.fillStyle=`rgba(${r},${g},${bl},${p*.7+.3})`;c.fill();
      });
      nd.forEach((n,i)=>{
        const p=Math.sin(t*.011+i*1.8)*.5+.5,[r,g,b]=n.cl;
        const ng=c.createRadialGradient(n.x*W,n.y*H,0,n.x*W,n.y*H,n.r*12+p*18);
        ng.addColorStop(0,`rgba(${r},${g},${b},${.35+p*.3})`);ng.addColorStop(1,'rgba(240,230,210,0)');
        c.fillStyle=ng;c.beginPath();c.arc(n.x*W,n.y*H,n.r*12+p*18,0,Math.PI*2);c.fill();
        c.beginPath();c.arc(n.x*W,n.y*H,n.r+p*2,0,Math.PI*2);c.fillStyle=`rgba(${r},${g},${b},1)`;c.fill();
      });
      lmVig(c);
    },
    uber(c,t){
      c.fillStyle='#f4eee6';c.fillRect(0,0,W,H);
      const r2=seededRand(77);
      for(let i=0;i<42;i++){
        const bx=r2()*W,spd=r2()*.0005+.0002,ph=r2()*Math.PI*2;
        const by=((r2()+t*spd+ph*.3)%1)*H,len=(r2()*.14+.04)*W,p=Math.sin(t*.01+i*1.7)*.5+.5;
        const al=(.1+p*.18)*(1-(by/H)*.35);
        c.strokeStyle=`rgba(100,70,40,${al})`;c.lineWidth=.8+r2()*.6;
        c.beginPath();c.moveTo(bx,by);c.lineTo(Math.min(bx+len,W),by);c.stroke();
        if(r2()>.78){c.fillStyle=`rgba(160,100,40,${al*2})`;c.font='bold '+(10+r2()*6)+'px serif';c.fillText('"',bx+len+3,by+4);}
      }
      for(let i=0;i<14;i++){
        const a=t*.003+i*(Math.PI*2/14),rx=.16+.12*Math.sin(t*.002+i*.5),ry=.09+.06*Math.cos(t*.0015+i*.4);
        const bx=(.5+Math.cos(a)*rx)*W,by=(.46+Math.sin(a)*ry)*H,p=Math.sin(t*.012+i*1.3)*.5+.5;
        c.beginPath();c.arc(bx,by,p*2.5+.5,0,Math.PI*2);c.fillStyle=`rgba(180,120,40,${.25+p*.35})`;c.fill();
      }
      lmVig(c);
    },
    raume(c,t){
      c.fillStyle='#f2ece3';c.fillRect(0,0,W,H);
      const gs=Math.min(W,H)/10;c.strokeStyle='rgba(80,100,140,.07)';c.lineWidth=.7;
      for(let x=0;x<W;x+=gs){c.beginPath();c.moveTo(x,0);c.lineTo(x,H);c.stroke();}
      for(let y=0;y<H;y+=gs){c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();}
      [[.13,.18,.28,.34,80,100,140],[.47,.14,.22,.22,120,80,40],[.47,.39,.24,.38,80,100,140],
       [.73,.18,.2,.47,120,80,40],[.14,.57,.3,.32,80,100,140]].forEach(([rx,ry,rw,rh,cr,cg,cb],i)=>{
        const p=Math.sin(t*.006+i*1.2)*.5+.5;
        c.strokeStyle=`rgba(${cr},${cg},${cb},${.28+p*.32})`;c.lineWidth=1.4;c.strokeRect(rx*W,ry*H,rw*W,rh*H);
        [[rx,ry],[rx+rw,ry],[rx,ry+rh],[rx+rw,ry+rh]].forEach(([nx,ny])=>{
          c.beginPath();c.arc(nx*W,ny*H,2+p*2.5,0,Math.PI*2);c.fillStyle=`rgba(${cr},${cg},${cb},${.6+p*.4})`;c.fill();
        });
        const sg=c.createRadialGradient((rx+rw*.5)*W,(ry+rh*.5)*H,0,(rx+rw*.5)*W,(ry+rh*.5)*H,Math.min(rw*W,rh*H)*.5);
        sg.addColorStop(0,`rgba(${cr},${cg},${cb},${.06+p*.06})`);sg.addColorStop(1,'rgba(242,236,227,0)');
        c.fillStyle=sg;c.fillRect(rx*W,ry*H,rw*W,rh*H);
      });
      const sl=(t*.0015)%1*H;c.fillStyle='rgba(80,100,140,.06)';c.fillRect(0,sl,W,2);
      lmVig(c);
    },
    diskurs(c,t){
      c.fillStyle='#f5f0e8';c.fillRect(0,0,W,H);
      for(let i=0;i<6;i++){
        const y=((i/6)+(t*.00018*(i%3?1:-1)))%1*H;
        c.fillStyle=`rgba(80,100,140,${.025+Math.sin(t*.003+i)*.012})`;c.fillRect(0,y,W,1.5);
      }
      const tg=c.createLinearGradient(0,0,0,H*.28);tg.addColorStop(0,'rgba(40,120,150,.04)');tg.addColorStop(1,'rgba(242,237,229,0)');
      c.fillStyle=tg;c.fillRect(0,0,W,H*.28);
      lmVig(c);
    },
    wesen(c,t){
      c.fillStyle='#f3ece3';c.fillRect(0,0,W,H);
      [{x:.5,y:.5,r:.12,cl:[150,80,180],s:1},{x:.24,y:.38,r:.09,cl:[40,120,150],s:1.3},
       {x:.76,y:.44,r:.09,cl:[60,140,80],s:.8},{x:.3,y:.72,r:.07,cl:[150,80,180],s:1.5},
       {x:.7,y:.66,r:.07,cl:[180,80,40],s:1.1},{x:.14,y:.58,r:.05,cl:[40,120,150],s:.9}]
      .forEach((o,i)=>{
        const br=Math.sin(t*.008*o.s+i*1.5)*.5+.5,[r,g,b]=o.cl;
        const bx=(o.x+Math.sin(t*.004*o.s+i)*.03)*W,by=(o.y+Math.cos(t*.003*o.s+i)*.022)*H;
        const rr=(o.r+br*.028)*Math.min(W,H);
        const og=c.createRadialGradient(bx,by,0,bx,by,rr);
        og.addColorStop(0,`rgba(${r},${g},${b},${.32+br*.25})`);og.addColorStop(.4,`rgba(${r},${g},${b},${.1+br*.08})`);og.addColorStop(1,'rgba(242,236,227,0)');
        c.fillStyle=og;c.beginPath();c.arc(bx,by,rr,0,Math.PI*2);c.fill();
        c.beginPath();c.arc(bx,by,4+br*3,0,Math.PI*2);c.fillStyle=`rgba(${r},${g},${b},${.75+br*.25})`;c.fill();
      });
      const r2=seededRand(11);
      for(let i=0;i<140;i++){
        const fl=Math.sin(t*.018+i*1.4)*.5+.5,col=r2()>.5?[60,140,80]:[150,80,180];
        c.beginPath();c.arc(r2()*W,r2()*H,r2()*.9+.2,0,Math.PI*2);
        c.fillStyle=`rgba(${col[0]},${col[1]},${col[2]},${fl*.35+.08})`;c.fill();
      }
      lmVig(c);
    },
    denken(c,t){
      c.fillStyle='#f2ede5';c.fillRect(0,0,W,H);
      const nn=[{x:.1,y:.3},{x:.2,y:.6},{x:.15,y:.8},{x:.3,y:.2},{x:.3,y:.5},{x:.3,y:.78},
        {x:.5,y:.35},{x:.5,y:.65},{x:.65,y:.25},{x:.65,y:.5},{x:.65,y:.75},{x:.8,y:.4},{x:.8,y:.65},{x:.9,y:.5},{x:.45,y:.15},{x:.55,y:.85}];
      const ne=[[0,4],[1,4],[2,5],[3,6],[4,6],[4,7],[5,7],[6,8],[6,9],[7,9],[7,10],[8,11],[9,11],[9,12],[10,12],[11,13],[12,13],[3,14],[14,6],[5,15],[15,10]];
      ne.forEach(([a,b])=>{
        const fire=Math.sin(t*.02+a*2.1+b*.9)>.55,p=Math.sin(t*.02+a*2.1+b*.9)*.5+.5;
        c.beginPath();c.moveTo(nn[a].x*W,nn[a].y*H);c.lineTo(nn[b].x*W,nn[b].y*H);
        c.strokeStyle=fire?`rgba(60,140,80,${p*.6+.15})`:'rgba(60,140,80,.06)';c.lineWidth=fire?2:.6;c.stroke();
        if(fire){const tp=(t*.025+a*.4)%1,tx=nn[a].x*W+(nn[b].x-nn[a].x)*W*tp,ty=nn[a].y*H+(nn[b].y-nn[a].y)*H*tp;
          c.beginPath();c.arc(tx,ty,3,0,Math.PI*2);c.fillStyle='rgba(60,140,80,.9)';c.fill();}
      });
      nn.forEach((n,i)=>{
        const fire=Math.sin(t*.015+i*1.8)>.45;
        const pg=c.createRadialGradient(n.x*W,n.y*H,0,n.x*W,n.y*H,fire?26:10);
        pg.addColorStop(0,fire?'rgba(60,140,80,.5)':'rgba(60,140,80,.14)');pg.addColorStop(1,'rgba(242,237,229,0)');
        c.fillStyle=pg;c.beginPath();c.arc(n.x*W,n.y*H,fire?26:10,0,Math.PI*2);c.fill();
        c.beginPath();c.arc(n.x*W,n.y*H,fire?5:2.5,0,Math.PI*2);c.fillStyle=fire?'rgba(60,140,80,1)':'rgba(60,140,80,.32)';c.fill();
      });
      lmVig(c);
    },
    schlaf(c,t){
      c.fillStyle='#f4edf5';c.fillRect(0,0,W,H);
      const cg=c.createRadialGradient(W*.5,H*.65,0,W*.5,H*.5,W*.6);
      cg.addColorStop(0,'rgba(140,80,170,.1)');cg.addColorStop(1,'rgba(244,237,245,0)');
      c.fillStyle=cg;c.fillRect(0,0,W,H);
      for(let i=0;i<7;i++){
        const y=.38+i*.09,amp=.032-i*.003,freq=.5+i*.1,spd=.003-i*.0002;
        const al=(.22-i*.022)*(Math.sin(t*.004+i)*.25+.75);
        c.beginPath();for(let x=0;x<=W;x+=4){const yw=y*H+Math.sin(x/W*Math.PI*2*freq+t*spd)*amp*H+Math.sin(x/W*Math.PI*3.5+t*spd*.7+i)*amp*.45*H;x===0?c.moveTo(x,yw):c.lineTo(x,yw);}
        c.strokeStyle=`rgba(140,80,170,${al})`;c.lineWidth=1.8;c.stroke();
      }
      const r2=seededRand(55);for(let i=0;i<28;i++){c.beginPath();c.arc(r2()*W,r2()*H*.5,r2()*.8+.2,0,Math.PI*2);c.fillStyle=`rgba(180,140,200,${r2()*.22+.08})`;c.fill();}
      lmVig(c);
    },
    splitter(c,t){
      c.fillStyle='#f4ede4';c.fillRect(0,0,W,H);
      const cg=c.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.45);
      cg.addColorStop(0,'rgba(180,80,40,.08)');cg.addColorStop(1,'rgba(244,237,228,0)');
      c.fillStyle=cg;c.fillRect(0,0,W,H);
      const r2=seededRand(99);
      for(let i=0;i<75;i++){
        const ang=r2()*Math.PI*2,dist=r2()*.44+.06,spd=r2()*.0006+.0002,ph=r2()*Math.PI*2;
        const cx=(.5+Math.cos(ang)*dist)*W,cy=(.5+Math.sin(ang)*dist)*H;
        const drift=Math.sin(t*spd+ph)*.016*W,px=cx+Math.cos(ang+Math.PI*.5)*drift,py=cy+Math.sin(ang+Math.PI*.5)*drift;
        const p=Math.sin(t*.01+ph)*.5+.5,sz=r2()*5+1.5,col=r2()>.5?[180,80,40]:[200,120,40];
        c.save();c.translate(px,py);c.rotate(t*spd*22+ph);
        c.fillStyle=`rgba(${col[0]},${col[1]},${col[2]},${.22+p*.38})`;c.fillRect(-sz/2,-sz/5,sz,sz/2.5);c.restore();
        const sg=c.createRadialGradient(px,py,0,px,py,sz*3.5);
        sg.addColorStop(0,`rgba(${col[0]},${col[1]},${col[2]},${p*.15})`);sg.addColorStop(1,'rgba(244,237,228,0)');
        c.fillStyle=sg;c.beginPath();c.arc(px,py,sz*3.5,0,Math.PI*2);c.fill();
      }
      lmVig(c);
    },
    cyberlinge(c,t){
      c.fillStyle='rgba(244,238,224,.15)';c.fillRect(0,0,W,H);
      const chars='01アイウエオ∆∑◈⬡≈';const cols=Math.floor(W/18);
      if(!c._lmdrops){c._lmdrops=[];for(let i=0;i<cols;i++)c._lmdrops[i]=Math.random()*(H/14);}
      c.font='12px JetBrains Mono,monospace';
      c._lmdrops.forEach((y,i)=>{
        const ch=chars[Math.floor(Math.random()*chars.length)];
        c.fillStyle=`rgba(120,80,20,${Math.random()*.6+.2})`;c.fillText(ch,i*18+2,y*14);
        if(y*14>H&&Math.random()>.97)c._lmdrops[i]=0;else c._lmdrops[i]+=.5;
      });
      lmVig(c);
    },
    theater(c,t){
      c.fillStyle='#f3ece3';c.fillRect(0,0,W,H);
      const cg=c.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.5);
      cg.addColorStop(0,'rgba(180,80,40,.07)');cg.addColorStop(1,'rgba(243,236,227,0)');
      c.fillStyle=cg;c.fillRect(0,0,W,H);
      const bars=64;
      for(let i=0;i<bars;i++){
        const f=i/bars,h=(Math.sin(t*.04+f*8)*Math.sin(t*.022+f*5.3)+1)*.5;
        const bh=h*H*.38+4,x=f*W,bw=W/bars-2,col=f<.33?[180,80,40]:f<.66?[160,100,40]:[120,80,160];
        const al=.35+h*.45;
        c.fillStyle=`rgba(${col[0]},${col[1]},${col[2]},${al})`;c.fillRect(x,H*.5-bh/2,bw,bh);
        const gg=c.createLinearGradient(0,H*.5-bh/2,0,H*.5+bh/2);
        gg.addColorStop(0,`rgba(${col[0]},${col[1]},${col[2]},0)`);gg.addColorStop(.5,`rgba(${col[0]},${col[1]},${col[2]},${al*.2})`);gg.addColorStop(1,`rgba(${col[0]},${col[1]},${col[2]},0)`);
        c.fillStyle=gg;c.fillRect(x-5,H*.5-bh/2-22,bw+10,bh+44);
      }
      lmVig(c);
    },
    schatten(c,t){
      c.fillStyle='#f3ecf4';c.fillRect(0,0,W,H);
      [{x:.5,y:.5,r:.22,cl:[140,80,170]},{x:.25,y:.4,r:.14,cl:[120,60,150]},
       {x:.75,y:.55,r:.14,cl:[160,80,180]},{x:.4,y:.75,r:.1,cl:[130,70,160]},{x:.65,y:.25,r:.1,cl:[150,80,170]}]
      .forEach((o,i)=>{
        const br=Math.sin(t*.006*(.8+i*.2)+i*1.3)*.5+.5,[r,g,b]=o.cl;
        const bx=(o.x+Math.sin(t*.003+i)*.04)*W,by=(o.y+Math.cos(t*.0025+i)*.03)*H,rr=(o.r+br*.04)*Math.min(W,H);
        const og=c.createRadialGradient(bx,by,0,bx,by,rr);
        og.addColorStop(0,`rgba(${r},${g},${b},${.28+br*.22})`);og.addColorStop(.5,`rgba(${r},${g},${b},.07)`);og.addColorStop(1,'rgba(243,236,244,0)');
        c.fillStyle=og;c.beginPath();c.arc(bx,by,rr,0,Math.PI*2);c.fill();
      });
      lmVig(c);
    },
    wissen(c,t){
      c.fillStyle='#f3ede5';c.fillRect(0,0,W,H);
      function lmBranch(x,y,ang,len,depth,ph){
        if(depth<1||len<5)return;const p=Math.sin(t*.008+ph)*.5+.5,nx=x+Math.cos(ang)*len,ny=y+Math.sin(ang)*len;
        c.strokeStyle=`rgba(100,70,40,${depth*.07+p*.07})`;c.lineWidth=depth*.55+.4;
        c.beginPath();c.moveTo(x,y);c.lineTo(nx,ny);c.stroke();
        c.beginPath();c.arc(nx,ny,2+p*depth*.3,0,Math.PI*2);c.fillStyle=`rgba(100,70,40,${.25+p*.4})`;c.fill();
        const sw=Math.sin(t*.004+ph)*.16;
        lmBranch(nx,ny,ang-.5+sw,len*.72,depth-1,ph+1.4);lmBranch(nx,ny,ang+.5-sw,len*.72,depth-1,ph+2.2);
        if(depth>2)lmBranch(nx,ny,ang+Math.sin(t*.003+depth)*.18,len*.58,depth-2,ph+3.1);
      }
      lmBranch(W*.5,H*.92,-Math.PI*.5,H*.17,5,0);lmBranch(W*.28,H*.94,-Math.PI*.5+.24,H*.12,4,2.2);lmBranch(W*.72,H*.94,-Math.PI*.5-.24,H*.12,4,4.1);
      lmVig(c);
    },
    gruppen(c,t){
      c.fillStyle='#f2eee5';c.fillRect(0,0,W,H);
      [[.26,.36,7,.1,80,100,160],[.73,.3,5,.08,40,120,150],[.5,.67,9,.12,150,80,180],[.18,.7,4,.07,80,100,160],[.8,.64,6,.09,60,140,80]].forEach(([cx,cy,n,r,cr,cg,cb],ci)=>{
        for(let i=0;i<n;i++){
          const a=t*.006*(.8+ci*.12)+i*(Math.PI*2/n)+ci,d=r*(Math.sin(t*.004+i+ci)*.15+.85);
          const bx=(cx+Math.cos(a)*d)*W,by=(cy+Math.sin(a)*d*.6)*H,p=Math.sin(t*.01+i*1.4+ci)*.5+.5;
          const rr=(5+p*5)*(Math.min(W,H)/800),og=c.createRadialGradient(bx,by,0,bx,by,rr*3);
          og.addColorStop(0,`rgba(${cr},${cg},${cb},${.28+p*.22})`);og.addColorStop(1,'rgba(242,238,229,0)');
          c.fillStyle=og;c.beginPath();c.arc(bx,by,rr*3,0,Math.PI*2);c.fill();
          c.beginPath();c.arc(bx,by,rr*.5,0,Math.PI*2);c.fillStyle=`rgba(${cr},${cg},${cb},${.75+p*.25})`;c.fill();
        }
        const gg=c.createRadialGradient(cx*W,cy*H,0,cx*W,cy*H,r*.75*Math.min(W,H));
        gg.addColorStop(0,`rgba(${cr},${cg},${cb},.07)`);gg.addColorStop(1,'rgba(242,238,229,0)');
        c.fillStyle=gg;c.beginPath();c.arc(cx*W,cy*H,r*.75*Math.min(W,H),0,Math.PI*2);c.fill();
      });
      lmVig(c);
    },
    zitate(c,t){
      c.fillStyle='#f3eee6';c.fillRect(0,0,W,H);
      const r2=seededRand(42);
      for(let col=0;col<10;col++){
        const bx=(col/10+.05)*W;
        for(let j=0;j<5;j++){
          const spd=r2()*.0004+.0002,ph=r2()*Math.PI*2;
          const by=((1-(t*spd+ph+col*.32+j*.72)%1))*H,len=(r2()*.1+.03)*W,p=Math.sin(t*.015+col*1.3+j)*.5+.5;
          const al=(.07+p*.12)*(by/H);
          c.strokeStyle=`rgba(100,70,40,${al})`;c.lineWidth=.8;c.beginPath();c.moveTo(bx,by);c.lineTo(bx+len,by);c.stroke();
          if(r2()>.72){c.fillStyle=`rgba(160,100,40,${al*2.5})`;c.font='bold '+(10+r2()*5)+'px serif';c.fillText(r2()>.5?'"':"'",bx+len+4,by+4);}
        }
      }
      const cg2=c.createRadialGradient(W*.5,H*.48,0,W*.5,H*.48,W*.32);
      cg2.addColorStop(0,'rgba(160,100,40,.05)');cg2.addColorStop(1,'rgba(243,238,230,0)');c.fillStyle=cg2;c.fillRect(0,0,W,H);
      lmVig(c);
    },
    archaeologie(c,t){
      c.fillStyle='#f0ebe0';c.fillRect(0,0,W,H);
      [[.12,.07,120,80,40,.22],[.22,.055,90,60,28,.18],[.31,.09,150,100,50,.2],[.43,.065,80,55,24,.16],
       [.53,.085,130,88,40,.18],[.64,.055,100,68,32,.16],[.72,.1,160,110,55,.22],[.85,.09,90,60,28,.16]].forEach(([y,h,r,g,b,a],i)=>{
        const w2=Math.sin(t*.002+i*1.1)*.007*H;
        c.fillStyle=`rgba(${r},${g},${b},${a})`;c.beginPath();c.moveTo(0,y*H+w2);
        for(let x=0;x<W;x+=10){c.lineTo(x,y*H+Math.sin(x/W*Math.PI*3+t*.003+i)*.005*H+w2);}
        c.lineTo(W,(y+h)*H+w2);c.lineTo(0,(y+h)*H+w2);c.closePath();c.fill();
        const r2=seededRand(i*13+7);
        for(let j=0;j<18;j++){const px=r2()*W,py=(y+r2()*h)*H+w2;c.beginPath();c.arc(px,py,r2()*1.8+.4,0,Math.PI*2);c.fillStyle=`rgba(${r+20},${g+15},${b+8},${.12+r2()*.16})`;c.fill();}
      });
      const ex=(.28+Math.sin(t*.002)*.08)*W;c.strokeStyle='rgba(140,100,60,.1)';c.lineWidth=1;c.beginPath();c.moveTo(ex,0);c.lineTo(ex,H);c.stroke();
      lmVig(c);
    },
    suche(c,t){
      c.fillStyle='#f2ede5';c.fillRect(0,0,W,H);
      const cx=W*.5,cy=H*.5;
      for(let i=0;i<5;i++){const ph=(t*.004+i*.2)%1,r=ph*Math.min(W,H)*.52,al=(1-ph)*.2;c.beginPath();c.arc(cx,cy,r,0,Math.PI*2);c.strokeStyle=`rgba(40,120,150,${al})`;c.lineWidth=1.8;c.stroke();}
      [.19,.34,.49].forEach(r=>{c.beginPath();c.arc(cx,cy,r*Math.min(W,H),0,Math.PI*2);c.strokeStyle='rgba(40,120,150,.07)';c.lineWidth=.6;c.stroke();});
      c.strokeStyle='rgba(40,120,150,.08)';c.lineWidth=.8;c.beginPath();c.moveTo(cx,0);c.lineTo(cx,H);c.stroke();c.beginPath();c.moveTo(0,cy);c.lineTo(W,cy);c.stroke();
      const sa=t*.025;c.save();c.translate(cx,cy);c.rotate(sa);
      const sg=c.createLinearGradient(0,0,Math.min(W,H)*.52,0);sg.addColorStop(0,'rgba(40,120,150,.25)');sg.addColorStop(1,'rgba(40,120,150,0)');
      c.beginPath();c.moveTo(0,0);c.arc(0,0,Math.min(W,H)*.52,-.4,0);c.closePath();c.fillStyle=sg;c.fill();c.restore();
      const cp=Math.sin(t*.015)*.5+.5;c.beginPath();c.arc(cx,cy,2.5+cp*3,0,Math.PI*2);c.fillStyle=`rgba(40,120,150,${.55+cp*.45})`;c.fill();
      lmVig(c);
    },
    gesetze(c,t){
      c.fillStyle='#f2eee6';c.fillRect(0,0,W,H);
      const step=Math.min(W,H)/16,ox=(t*.3)%step,oy=(t*.2)%step;
      c.strokeStyle='rgba(60,80,160,.07)';c.lineWidth=.6;
      for(let x=-step+ox;x<W+step;x+=step){c.beginPath();c.moveTo(x,0);c.lineTo(x,H);c.stroke();}
      for(let y=-step+oy;y<H+step;y+=step){c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();}
      [[.2,.25,.12],[.5,.2,.1],[.78,.28,.11],[.14,.6,.1],[.42,.55,.13],[.72,.58,.1],[.58,.76,.08]].forEach(([lx,ly,ls],i)=>{
        const p=Math.sin(t*.005+i*1.5)*.5+.5,s=ls*Math.min(W,H),px=lx*W-s*.5,py=ly*H-s*.5;
        c.strokeStyle=`rgba(60,80,160,${.18+p*.28})`;c.lineWidth=1.2;c.strokeRect(px,py,s,s);
        c.strokeStyle=`rgba(60,80,160,${.06+p*.07})`;c.lineWidth=.5;c.strokeRect(px+s*.2,py+s*.2,s*.6,s*.6);
        c.beginPath();c.arc(lx*W,ly*H,2+p*2.5,0,Math.PI*2);c.fillStyle=`rgba(60,80,160,${.5+p*.5})`;c.fill();
      });
      lmVig(c);
    },
    forschung(c,t){
      c.fillStyle='#f1ede5';c.fillRect(0,0,W,H);
      const hr=Math.min(W,H)/14,hh=Math.sqrt(3)*hr;let hi=0;
      for(let row=-1;row<H/hh+1;row++){
        for(let col=-1;col<W/(hr*3)+2;col++){
          const hx=col*hr*3+hr,hy=row*hh+(col%2?hh*.5:0);
          const p=Math.sin(t*.007+hi*.4)*.5+.5,dist=Math.sqrt(Math.pow(hx/W-.5,2)+Math.pow(hy/H-.5,2));hi++;
          const al=(.06+p*.12)*(1-dist*.75);if(al<.01)continue;
          c.beginPath();for(let k=0;k<6;k++){const a=Math.PI/3*k-Math.PI/6;c.lineTo(hx+hr*.86*Math.cos(a),hy+hr*.86*Math.sin(a));}
          c.closePath();c.strokeStyle=`rgba(60,140,80,${al})`;c.lineWidth=.9;c.stroke();
          if(p>.68){c.beginPath();for(let k=0;k<6;k++){const a=Math.PI/3*k-Math.PI/6;c.lineTo(hx+hr*.86*Math.cos(a),hy+hr*.86*Math.sin(a));}c.closePath();c.fillStyle=`rgba(60,140,80,${(p-.68)*.1})`;c.fill();}
        }
      }
      const fg=c.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.28);fg.addColorStop(0,'rgba(60,140,80,.06)');fg.addColorStop(1,'rgba(241,237,229,0)');c.fillStyle=fg;c.fillRect(0,0,W,H);lmVig(c);
    },
    partner(c,t){
      c.fillStyle='#f3ede5';c.fillRect(0,0,W,H);
      [[.22,.36,.78,.36,40,120,150],[.18,.62,.82,.62,150,80,180],[.3,.22,.7,.73,60,140,80]].forEach(([ax,ay,bx2,by2,cr,cg,cb],pi)=>{
        const p=Math.sin(t*.008+pi*2.1)*.5+.5,mx=(ax+bx2)*.5*W,my=((ay+by2)*.5-.06+Math.sin(t*.004+pi)*.04)*H;
        c.beginPath();c.moveTo(ax*W,ay*H);c.quadraticCurveTo(mx,my,bx2*W,by2*H);
        c.strokeStyle=`rgba(${cr},${cg},${cb},${.14+p*.18})`;c.lineWidth=1.8+p;c.stroke();
        const tp=(t*.008+pi*.4)%1,tx=(1-tp)*(1-tp)*ax*W+2*(1-tp)*tp*mx+tp*tp*bx2*W,ty=(1-tp)*(1-tp)*ay*H+2*(1-tp)*tp*my+tp*tp*by2*H;
        c.beginPath();c.arc(tx,ty,3+p*2.5,0,Math.PI*2);c.fillStyle=`rgba(${cr},${cg},${cb},${.7+p*.3})`;c.fill();
        [[ax,ay],[bx2,by2]].forEach(([nx,ny],ni)=>{
          const np=Math.sin(t*.01+pi*2.1+ni)*.5+.5,ng=c.createRadialGradient(nx*W,ny*H,0,nx*W,ny*H,20+np*18);
          ng.addColorStop(0,`rgba(${cr},${cg},${cb},${.32+np*.25})`);ng.addColorStop(1,'rgba(243,237,229,0)');
          c.fillStyle=ng;c.beginPath();c.arc(nx*W,ny*H,20+np*18,0,Math.PI*2);c.fill();
          c.beginPath();c.arc(nx*W,ny*H,4+np*3,0,Math.PI*2);c.fillStyle=`rgba(${cr},${cg},${cb},1)`;c.fill();
        });
      });
      lmVig(c);
    },
    meinewelt(c,t){
      c.fillStyle='#f4ede8';c.fillRect(0,0,W,H);
      const br=Math.sin(t*.005)*.5+.5;
      const wg=c.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.38+br*W*.08);
      wg.addColorStop(0,`rgba(180,60,100,${.12+br*.1})`);wg.addColorStop(.42,`rgba(160,80,60,${.06+br*.05})`);wg.addColorStop(1,'rgba(244,237,232,0)');
      c.fillStyle=wg;c.fillRect(0,0,W,H);
      const r2=seededRand(88);
      for(let i=0;i<55;i++){
        const ph=r2()*Math.PI*2,spd=r2()*.003+.001;
        const bx=(r2()+Math.sin(t*spd+ph)*.04)*W,by=(r2()+Math.cos(t*spd*.7+ph)*.03)*H,p=Math.sin(t*.009+i*1.6)*.5+.5;
        const col=r2()>.5?[180,60,100]:[200,100,40];
        c.beginPath();c.arc(bx,by,r2()*2.6+.5,0,Math.PI*2);c.fillStyle=`rgba(${col[0]},${col[1]},${col[2]},${.12+p*.22})`;c.fill();
      }
      c.beginPath();c.arc(W*.5,H*.5,W*.18+br*W*.025,0,Math.PI*2);c.strokeStyle=`rgba(180,60,100,${.07+br*.06})`;c.lineWidth=1;c.stroke();
      lmVig(c);
    },
    admin(c,t){
      c.fillStyle='#f2ede5';c.fillRect(0,0,W,H);
      const gs=Math.min(W,H)/20;c.strokeStyle='rgba(100,60,40,.03)';c.lineWidth=.5;
      for(let x=0;x<W;x+=gs){c.beginPath();c.moveTo(x,0);c.lineTo(x,H);c.stroke();}
      for(let y=0;y<H;y+=gs){c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();}
      const bl=.25*W,br2=.75*W,bw=br2-bl;
      [[.22,.72,180,80,40],[.32,.45,60,140,80],[.42,.88,200,120,40],[.52,.31,40,120,150],[.62,.56,150,80,180],[.72,.64,60,140,80]].forEach(([by,val,cr,cg,cb],i)=>{
        const p=Math.sin(t*.012+i*1.3)*.5+.5,v=Math.min(val+p*.04-.02,1);
        c.fillStyle='rgba(100,80,40,.06)';c.fillRect(bl,by*H-5,bw,10);
        const fg=c.createLinearGradient(bl,0,bl+bw*v,0);
        fg.addColorStop(0,`rgba(${cr},${cg},${cb},${.28+p*.15})`);fg.addColorStop(1,`rgba(${cr},${cg},${cb},${.4+p*.18})`);
        c.fillStyle=fg;c.fillRect(bl,by*H-5,bw*v,10);
        c.strokeStyle=`rgba(${cr},${cg},${cb},${.1+p*.08})`;c.lineWidth=1;
        c.beginPath();c.moveTo(bl+bw*v,by*H-7);c.lineTo(bl+bw*v,by*H+7);c.stroke();
      });
      lmVig(c);
    },
    default(c,t){
      c.fillStyle='#f3eee6';c.fillRect(0,0,W,H);
      // Warm nebula auf Pergament
      [{x:.18,y:.28,rx:.28,ry:.2,c:[160,100,40],a:.08},{x:.76,y:.18,rx:.24,ry:.18,c:[100,70,40],a:.07},
       {x:.5,y:.62,rx:.32,ry:.24,c:[140,80,40],a:.06},{x:.82,y:.58,rx:.2,ry:.15,c:[120,80,160],a:.06}].forEach((n,i)=>{
        const p=Math.sin(t*.006+i*1.4)*.5+.5,cx2=n.x*W,cy2=n.y*H;
        const g=c.createRadialGradient(cx2,cy2,0,cx2,cy2,n.rx*W);
        g.addColorStop(0,`rgba(${n.c[0]},${n.c[1]},${n.c[2]},${n.a+p*.06})`);g.addColorStop(1,'rgba(243,238,230,0)');
        c.fillStyle=g;c.save();c.scale(1,n.ry/n.rx);c.beginPath();c.arc(cx2,cy2*W/H*n.rx/n.ry,n.rx*W,0,Math.PI*2);c.fill();c.restore();
      });
      const r2=seededRand(800);for(let i=0;i<35;i++){const fl=Math.sin(t*.018+i*1.4)*.5+.5;c.beginPath();c.arc(r2()*W,r2()*H,r2()*1.2+.3,0,Math.PI*2);c.fillStyle=`rgba(140,100,60,${fl*.2+.06})`;c.fill();}
      lmVig(c);
    }
  };
"""

TICK_PATCH = r"""
  // ── Light mode tick patch ────────────────────────────────────────────────
  function tick(){
    if(document.documentElement.dataset.surfaceMode!=='cinema'){frame++;requestAnimationFrame(tick);return;}
    frame++;
    const lm=document.documentElement.dataset.theme==='light';
    const sceneSet=lm?LM:scenes;
    const key=sceneSet[currentScene]?currentScene:'default';
    (sceneSet[key]||sceneSet.default)(activeCtx,frame);
    requestAnimationFrame(tick);
  }
  tick();
"""

with open('/tmp/ftw_lm_scenes.js', 'w') as f:
    f.write(JS.strip())

with open('/tmp/ftw_lm_tick.js', 'w') as f:
    f.write(TICK_PATCH.strip())

print(f"LM Scenes JS: {len(JS)} Zeichen")
print(f"Tick Patch: {len(TICK_PATCH)} Zeichen")
print("Fertig: /tmp/ftw_lm_scenes.js + /tmp/ftw_lm_tick.js")
