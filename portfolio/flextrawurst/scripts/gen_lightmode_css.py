#!/usr/bin/env python3
"""
Generiert das Light-Mode CSS für alle flextrawurst-Tabs.
Ausgabe: /tmp/ftw_lightmode.css
Dann wird es in die Surface HTML injiziert.
"""

CSS = """
/* ══════════════════════════════════════════════════════════════════════════
   LIGHT MODE OVERRIDES — alle Tabs, individuelle Animationen
   ══════════════════════════════════════════════════════════════════════════ */

/* ── Cinema-Canvas im Lightmode deaktivieren ─────────────────────────────── */
html[data-theme="light"] #cin-a,
html[data-theme="light"] #cin-b,
html[data-theme="light"] #cin-flash { display:none!important }
html[data-theme="light"][data-surface-mode="cinema"] .v-view {
  background:var(--void)!important; backdrop-filter:none!important }
html[data-theme="light"] #cin-indicator { display:none!important }

/* ── Keyframes ───────────────────────────────────────────────────────────── */
@keyframes lm-float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
@keyframes lm-breathe { 0%,100%{opacity:.18;transform:scale(1)} 50%{opacity:.32;transform:scale(1.04)} }
@keyframes lm-shimmer { 0%{background-position:200% 50%} 100%{background-position:-200% 50%} }
@keyframes lm-pulse-warm { 0%,100%{box-shadow:0 0 0 0 rgba(180,120,40,.0)} 50%{box-shadow:0 0 28px 4px rgba(180,120,40,.12)} }
@keyframes lm-scan { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }
@keyframes lm-radar { 0%{transform:scale(0);opacity:.4} 100%{transform:scale(2.2);opacity:0} }
@keyframes lm-drift-r { 0%{transform:translateX(0) rotate(0deg)} 100%{transform:translateX(4px) rotate(2deg)} }
@keyframes lm-inkline { 0%{width:0;opacity:0} 100%{width:100%;opacity:1} }
@keyframes lm-hexglow { 0%,100%{border-color:rgba(140,100,60,.12)} 50%{border-color:rgba(140,100,60,.32)} }
@keyframes lm-nodepulse { 0%,100%{transform:scale(1);opacity:.6} 50%{transform:scale(1.18);opacity:1} }
@keyframes lm-strata { 0%{background-position:0 0} 100%{background-position:0 -40px} }
@keyframes lm-connbeam { 0%{stroke-dashoffset:200} 100%{stroke-dashoffset:0} }
@keyframes lm-layer-up { 0%{transform:translateY(0)} 100%{transform:translateY(-100vh)} }
@keyframes lm-worm { 0%,100%{transform:scaleX(1)} 50%{transform:scaleX(1.08) scaleY(.94)} }
@keyframes lm-ember { 0%{transform:translateY(0) scale(1);opacity:.7} 100%{transform:translateY(-40px) scale(.2);opacity:0} }

/* ── Allgemeine Light-Mode Basisstruktur ─────────────────────────────────── */
[data-theme="light"] #world-center { background:var(--surface)!important }
[data-theme="light"] #left-rail { background:var(--deep)!important }
[data-theme="light"] .rail-section-head { background:var(--surface)!important }
[data-theme="light"] .rail-item:hover { background:rgba(140,100,60,.06)!important }
[data-theme="light"] .rail-item.rl-active { background:rgba(8,144,168,.07)!important }

/* ── DISKURS ─────────────────────────────────────────────────────────────── */
[data-theme="light"] .dk-row { background:var(--void) }
[data-theme="light"] .dk-row:hover { background:rgba(140,100,60,.06)!important }
[data-theme="light"] .dk-row-titel { color:var(--t-bright)!important }
[data-theme="light"] .dk-row-intro { color:var(--t-mid)!important }
[data-theme="light"] .dk-row-autor { color:var(--world)!important }
[data-theme="light"] .dk-row-zeit { color:var(--t-sub)!important }
[data-theme="light"] .dk-row-lastakt { color:var(--t-dim)!important }
[data-theme="light"] .dk-row.ungelesen {
  background:linear-gradient(90deg,rgba(8,144,168,.09) 0%,var(--void) 100%)!important;
  border-left:3px solid var(--world)!important }
[data-theme="light"] .dk-row.ungelesen .dk-row-titel { color:var(--world)!important }
[data-theme="light"] .dk-row.ungelesen .dk-row-intro { color:var(--t-mid)!important }
[data-theme="light"] .dk-row.ungelesen .dk-row-accent { background:var(--world)!important }
[data-theme="light"] .dk-ungelesen-dot { background:var(--world)!important;box-shadow:0 0 6px var(--world)!important }
/* Diskurs — animierter Top-Separator */
[data-theme="light"] #view-diskurs::before {
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--world),var(--alive),transparent);
  background-size:200% auto;animation:lm-shimmer 5s linear infinite;z-index:2;pointer-events:none }
[data-theme="light"] #view-diskurs { position:relative }

/* ── THEATER (Wesen-Posts) ───────────────────────────────────────────────── */
[data-theme="light"] .th-post { background:var(--void);border-color:var(--rim) }
[data-theme="light"] .th-post:hover { border-color:var(--world)!important;background:rgba(8,144,168,.04)!important }
[data-theme="light"] .th-wesen { color:var(--world)!important }
[data-theme="light"] .th-title { color:var(--t-bright)!important }
[data-theme="light"] .th-excerpt { color:var(--t-mid)!important }
[data-theme="light"] .th-energie { color:var(--t-sub)!important }
[data-theme="light"] .th-time { color:var(--t-dim)!important }
[data-theme="light"] .th-empty { color:var(--t-mid)!important }
[data-theme="light"] .th-herkunft.entitaet { background:rgba(8,144,168,.08)!important;color:var(--world)!important;border:1px solid rgba(8,144,168,.2)!important }
[data-theme="light"] .th-herkunft.mensch { background:rgba(10,144,80,.07)!important;color:var(--alive)!important;border:1px solid rgba(10,144,80,.18)!important }
[data-theme="light"] .th-herkunft.resonanz { background:rgba(122,56,184,.07)!important;color:var(--wesen)!important;border:1px solid rgba(122,56,184,.18)!important }
/* Theater — Bühnen-Licht Animation */
[data-theme="light"] #view-theater::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 60% 40% at 50% 0%,rgba(192,90,24,.07) 0%,transparent 70%);
  animation:lm-breathe 6s ease-in-out infinite }
[data-theme="light"] #view-theater { position:relative }

/* ── MEINE WELT ──────────────────────────────────────────────────────────── */
[data-theme="light"] .mw-eintrag { border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .mw-eintrag-datum { color:var(--t-sub)!important }
[data-theme="light"] .mw-eintrag-text { color:var(--t-mid)!important }
[data-theme="light"] .mw-panel-titel { color:var(--world)!important }
[data-theme="light"] .mw-panel-x { color:var(--t-mid)!important }
[data-theme="light"] .mw-buch-tag { color:var(--world)!important }
[data-theme="light"] .mw-buch-vorschau { color:var(--t-mid)!important }
[data-theme="light"] .mw-buch-mark { color:var(--alive)!important }
[data-theme="light"] .mw-buch-seite-nr { color:var(--t-sub)!important }
[data-theme="light"] .mw-buch-seite-titel { color:var(--world)!important }
[data-theme="light"] .mw-buch-seite-datum { color:var(--t-sub)!important }
[data-theme="light"] .mw-buch-seite-text { color:var(--t-mid)!important }
[data-theme="light"] .mw-buch-neu { border-top:1px solid var(--rim)!important }
[data-theme="light"] .mw-kal-nav { border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .mw-kal-label { color:var(--t-sub)!important }
[data-theme="light"] .mw-kal-termin { background:rgba(10,144,80,.08)!important;color:var(--alive)!important }
[data-theme="light"] .mw-formular { border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .mw-leer { color:var(--t-sub)!important }
[data-theme="light"] .mw-notiz-ktext { color:var(--t-mid)!important }
[data-theme="light"] .mw-ico { color:var(--t-sub)!important }
[data-theme="light"] .mw-ico:hover { color:var(--world)!important }
[data-theme="light"] .mw-notiz-gruppe { color:var(--t-sub)!important;border-top:1px solid var(--rim)!important }
[data-theme="light"] .mw-kal-wt { color:var(--t-sub)!important }
[data-theme="light"] .mw-kal-d { color:var(--t-bright)!important }
[data-theme="light"] .mw-kal-neu { border-top:1px solid var(--rim)!important }
[data-theme="light"] .mw-btn:hover { background:var(--world)!important;color:#fff!important }
[data-theme="light"] .mw-ta,[data-theme="light"] .mw-inp {
  background:var(--surface)!important;border-color:var(--rim)!important;color:var(--t-mid)!important }
[data-theme="light"] .mw-ta:focus,[data-theme="light"] .mw-inp:focus { border-color:var(--world)!important }
/* MeineWelt — warmes Tagebuch-Glühen */
[data-theme="light"] #view-meinewelt::before {
  content:'';position:absolute;top:0;right:0;width:180px;height:100%;pointer-events:none;z-index:0;
  background:linear-gradient(270deg,rgba(192,90,24,.05) 0%,transparent 100%);
  animation:lm-breathe 8s ease-in-out infinite }
[data-theme="light"] #view-meinewelt { position:relative }

/* ── GEDANKENBLASEN (bf-*) ───────────────────────────────────────────────── */
[data-theme="light"] #bf-detail-panel { background:var(--deep)!important;border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .bf-dp-close { color:var(--t-sub)!important }
[data-theme="light"] #bf-dp-inhalt { color:var(--t-bright)!important }
[data-theme="light"] #bf-dp-meta { color:var(--t-mid)!important }
[data-theme="light"] #bf-dp-verwendungen { color:var(--world)!important }
[data-theme="light"] #bf-eingabe-panel h3 { color:var(--t-sub)!important }
[data-theme="light"] #bf-gedanke-text {
  background:var(--surface)!important;border:1px solid var(--rim)!important;color:var(--t-mid)!important }
[data-theme="light"] #bf-gedanke-text:focus { border-color:var(--world)!important }
[data-theme="light"] #bf-tags-input {
  background:var(--surface)!important;border:1px solid var(--rim)!important;color:var(--t-mid)!important }
[data-theme="light"] #bf-zeichenzahl { color:var(--t-sub)!important }
[data-theme="light"] #bf-btn-submit { border-color:var(--world)!important;color:var(--world)!important }
[data-theme="light"] #bf-btn-submit:hover { background:var(--world)!important;color:#fff!important }
[data-theme="light"] #bf-feedback { color:var(--world)!important }
[data-theme="light"] .bf-wesen-ind { border-color:var(--rim)!important;color:var(--t-sub)!important }
[data-theme="light"] .bf-wi-dot { background:var(--world)!important }
[data-theme="light"] .bf-wi-name { color:var(--t-mid)!important }
[data-theme="light"] .bf-wi-stufe { color:var(--t-sub)!important }
[data-theme="light"] .bf-drift-pos { color:var(--alive)!important }
[data-theme="light"] .bf-drift-neg { color:var(--sys)!important }
[data-theme="light"] .bf-drift-neu { color:var(--t-sub)!important }
/* Blasen — schwimmende Punkte */
[data-theme="light"] #view-blasen::before {
  content:'';position:absolute;bottom:10%;left:50%;transform:translateX(-50%);
  width:300px;height:300px;border-radius:50%;pointer-events:none;z-index:0;
  background:radial-gradient(circle,rgba(8,144,168,.08) 0%,transparent 70%);
  animation:lm-float 7s ease-in-out infinite }
[data-theme="light"] #view-blasen { position:relative }

/* ── WISSEN (Knowledge) ──────────────────────────────────────────────────── */
[data-theme="light"] .wk-h-section { border-top:1px solid var(--rim)!important }
[data-theme="light"] .wk-h-head { color:var(--world)!important;border-left-color:var(--world)!important }
[data-theme="light"] .wk-h-card:hover { border-color:var(--world)!important;background:rgba(8,144,168,.04)!important }
[data-theme="light"] .wk-h-slug { color:var(--world)!important }
[data-theme="light"] .wk-h-kurz { color:var(--t-mid)!important }
[data-theme="light"] .wk-title { color:var(--world)!important }
[data-theme="light"] .wk-sub { color:var(--t-sub)!important }
/* Wissen — Tintenbaum-Wachstum */
[data-theme="light"] #view-wissen::after {
  content:'';position:fixed;bottom:0;left:50%;transform:translateX(-50%);
  width:2px;height:60%;background:linear-gradient(to top,rgba(8,144,168,.2),transparent);
  pointer-events:none;z-index:0;animation:lm-breathe 6s ease-in-out infinite }

/* ── SPLITTER/KOMPOASE (mp-*) ────────────────────────────────────────────── */
[data-theme="light"] .mp-splitter-item {
  background:rgba(192,90,24,.06)!important;border:1px solid rgba(192,90,24,.15)!important }
[data-theme="light"] .mp-splitter-text { color:var(--splitter)!important }
[data-theme="light"] .mp-splitter-meta { color:var(--t-sub)!important }
[data-theme="light"] .mp-splitter-typ-n { color:var(--splitter)!important }
[data-theme="light"] .mp-splitter-typ-l { color:var(--t-sub)!important }
[data-theme="light"] .mp-edit-btn { border-color:var(--rim)!important;color:var(--t-mid)!important }

/* ── AV / SYSTEME ────────────────────────────────────────────────────────── */
[data-theme="light"] .av-sys-row { border-bottom:1px solid var(--rim)!important;color:var(--t-mid)!important }
/* Systeme — warmer Grid-Scan */
[data-theme="light"] #view-systeme::before {
  content:'';position:absolute;top:-2px;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--world),transparent);
  animation:lm-shimmer 4s linear infinite;pointer-events:none;z-index:1 }
[data-theme="light"] #view-systeme { position:relative }

/* ── NACHRICHTEN (nm-*, inline-injiziert) ────────────────────────────────── */
[data-theme="light"] .nm-gesprach { border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .nm-zeit { color:var(--t-sub)!important }
[data-theme="light"] .nm-vorschau { color:var(--t-mid)!important }
[data-theme="light"] .nm-ich-vor { color:var(--t-sub)!important }
[data-theme="light"] .nm-leer { color:var(--t-sub)!important }
[data-theme="light"] .nm-back { color:var(--world)!important }
[data-theme="light"] .nm-mz { color:var(--t-sub)!important }
[data-theme="light"] .nm-new-btn { border-color:var(--world)!important;color:var(--world)!important }

/* ── WESEN ───────────────────────────────────────────────────────────────── */
[data-theme="light"] .sc-card { background:var(--surface)!important;border-color:var(--rim)!important }
[data-theme="light"] .sc-card:hover { border-color:var(--wesen)!important;background:rgba(122,56,184,.04)!important }
/* Wesen — sanfte Aura */
[data-theme="light"] #view-wesen::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 50% 60% at 75% 50%,rgba(122,56,184,.06) 0%,transparent 65%);
  animation:lm-breathe 9s ease-in-out infinite }
[data-theme="light"] #view-wesen { position:relative }

/* ── DENKEN ──────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-denken::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 40% 40% at 30% 30%,rgba(10,144,80,.06) 0%,transparent 60%),
             radial-gradient(ellipse 30% 35% at 70% 65%,rgba(8,144,168,.05) 0%,transparent 55%);
  animation:lm-breathe 7s ease-in-out infinite }
[data-theme="light"] #view-denken { position:relative }

/* ── RÄUME ───────────────────────────────────────────────────────────────── */
[data-theme="light"] .rv-card { background:var(--surface)!important;border-color:var(--rim)!important }
[data-theme="light"] .rv-card:hover {
  border-color:var(--world)!important;background:rgba(8,144,168,.04)!important;
  box-shadow:0 2px 18px rgba(8,144,168,.1)!important }
[data-theme="light"] .rv-name { color:var(--t-bright)!important }
[data-theme="light"] .rv-desc { color:var(--t-mid)!important }
[data-theme="light"] .rv-sec { color:var(--t-sub)!important;border-top:1px solid var(--rim)!important }
[data-theme="light"] .rv-body { color:var(--t-mid)!important }
[data-theme="light"] .rv-expand-icon { color:var(--t-dim)!important }
[data-theme="light"] .rv-card[data-open="1"] { border-color:var(--world)!important }
[data-theme="light"] .rv-cta-btn { background:rgba(8,144,168,.06)!important;border-color:var(--t-dim)!important;color:var(--world)!important }
[data-theme="light"] .rv-cta-btn:hover { background:rgba(8,144,168,.12)!important }
/* Räume — Blueprint-Scan */
[data-theme="light"] #view-raume::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:repeating-linear-gradient(90deg,rgba(8,144,168,.025) 0px,rgba(8,144,168,.025) 1px,transparent 1px,transparent 60px),
             repeating-linear-gradient(0deg,rgba(8,144,168,.025) 0px,rgba(8,144,168,.025) 1px,transparent 1px,transparent 60px);
  animation:lm-strata 30s linear infinite }
[data-theme="light"] #view-raume { position:relative }

/* ── LEITSTAND ───────────────────────────────────────────────────────────── */
[data-theme="light"] #world-center { background:var(--surface)!important }
/* Weltkarte — warmer Amber-Puls auf SVG */
[data-theme="light"] #view-leitstand::before {
  content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:300px;height:300px;border-radius:50%;pointer-events:none;z-index:0;
  background:radial-gradient(circle,rgba(180,120,40,.07) 0%,transparent 70%);
  animation:lm-float 10s ease-in-out infinite }
[data-theme="light"] #view-leitstand { position:relative }

/* ── WAS IST DAS (uber) ──────────────────────────────────────────────────── */
[data-theme="light"] #view-uber { background:var(--void)!important }
[data-theme="light"] .ub2-hero-grid {
  background-image:linear-gradient(rgba(140,100,60,.12) 1px,transparent 1px),
    linear-gradient(90deg,rgba(140,100,60,.12) 1px,transparent 1px)!important;
  opacity:0.5!important }
[data-theme="light"] .ub2-hero::before {
  background:radial-gradient(ellipse 80% 60% at 50% 50%,rgba(8,144,168,.06) 0%,transparent 70%)!important }
[data-theme="light"] .ub2-eyebrow { color:var(--t-sub)!important }
[data-theme="light"] .ub2-claim { color:var(--t-mid)!important }
[data-theme="light"] .ub2-claim strong { color:var(--t-bright)!important }
/* Uber — floating warm motes */
[data-theme="light"] #view-uber::before {
  content:'';position:absolute;top:20%;left:10%;width:40px;height:40px;
  border-radius:50%;background:rgba(192,90,24,.12);pointer-events:none;z-index:0;
  animation:lm-float 6s ease-in-out infinite }
[data-theme="light"] #view-uber::after {
  content:'';position:absolute;top:40%;right:15%;width:24px;height:24px;
  border-radius:50%;background:rgba(8,144,168,.1);pointer-events:none;z-index:0;
  animation:lm-float 8s ease-in-out infinite 2s }
[data-theme="light"] #view-uber { position:relative }

/* ── ARCHÄOLOGIE ─────────────────────────────────────────────────────────── */
[data-theme="light"] #view-archaeologie::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:repeating-linear-gradient(0deg,
    rgba(140,100,60,.06) 0px,rgba(140,100,60,.06) 1px,
    transparent 1px,transparent 32px);
  animation:lm-strata 20s linear infinite }
[data-theme="light"] #view-archaeologie { position:relative }

/* ── SUCHE ───────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-suche::before,[data-theme="light"] #v-suche::before {
  content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:200px;height:200px;border-radius:50%;pointer-events:none;z-index:0;
  border:1px solid rgba(8,144,168,.15);
  animation:lm-radar 3s ease-out infinite }
[data-theme="light"] #view-suche,[data-theme="light"] #v-suche { position:relative }

/* ── GRUPPEN ─────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-gruppen::before {
  content:'';position:absolute;bottom:20%;right:10%;width:120px;height:120px;
  border-radius:50%;background:rgba(40,112,208,.06);pointer-events:none;z-index:0;
  animation:lm-float 9s ease-in-out infinite 1s }
[data-theme="light"] #view-gruppen::after {
  content:'';position:absolute;top:15%;left:5%;width:80px;height:80px;
  border-radius:50%;background:rgba(8,144,168,.05);pointer-events:none;z-index:0;
  animation:lm-float 11s ease-in-out infinite 3s }
[data-theme="light"] #view-gruppen { position:relative }

/* ── ZITATE ──────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-zitate::before {
  content:'"';position:absolute;top:5%;left:5%;font-size:8rem;line-height:1;
  color:rgba(8,144,168,.07);pointer-events:none;z-index:0;font-family:serif;
  animation:lm-float 12s ease-in-out infinite }
[data-theme="light"] #view-zitate::after {
  content:'"';position:absolute;bottom:5%;right:5%;font-size:8rem;line-height:1;
  color:rgba(8,144,168,.07);pointer-events:none;z-index:0;font-family:serif;
  animation:lm-float 10s ease-in-out infinite 4s }
[data-theme="light"] #view-zitate { position:relative }

/* ── GESETZE ─────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-gesetze::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:repeating-linear-gradient(90deg,rgba(24,104,200,.04) 0px,rgba(24,104,200,.04) 1px,transparent 1px,transparent 48px),
             repeating-linear-gradient(0deg,rgba(24,104,200,.04) 0px,rgba(24,104,200,.04) 1px,transparent 1px,transparent 48px) }
[data-theme="light"] #view-gesetze { position:relative }
[data-theme="light"] #view-gesetze .ub2-hero-grid {
  background-image:linear-gradient(rgba(24,104,200,.06) 1px,transparent 1px),
    linear-gradient(90deg,rgba(24,104,200,.06) 1px,transparent 1px)!important }

/* ── FORSCHUNG ───────────────────────────────────────────────────────────── */
[data-theme="light"] #view-forschung::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 50% 70% at 50% 50%,rgba(10,144,80,.05) 0%,transparent 65%);
  animation:lm-breathe 8s ease-in-out infinite }
[data-theme="light"] #view-forschung { position:relative }

/* ── PARTNER ─────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-partner::before {
  content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:60%;height:1px;background:linear-gradient(90deg,transparent,rgba(8,144,168,.2),transparent);
  pointer-events:none;z-index:0;animation:lm-shimmer 6s linear infinite }
[data-theme="light"] #view-partner::after {
  content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:1px;height:60%;background:linear-gradient(180deg,transparent,rgba(8,144,168,.15),transparent);
  pointer-events:none;z-index:0;animation:lm-shimmer 8s linear infinite 2s }
[data-theme="light"] #view-partner { position:relative }

/* ── ADMIN ───────────────────────────────────────────────────────────────── */
[data-theme="light"] .admin-bild-row { border-bottom:1px solid var(--rim)!important }
[data-theme="light"] .admin-bild-user { color:var(--world)!important }
[data-theme="light"] .admin-bild-zweck { color:var(--t-sub)!important }
[data-theme="light"] .admin-bild-pfad { color:var(--t-mid)!important }
[data-theme="light"] .admin-bild-no { border-color:var(--sys)!important;color:var(--sys)!important }
/* Admin — System-Monitor Shimmer */
[data-theme="light"] #view-admin::before {
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--sys),transparent);
  animation:lm-shimmer 3s linear infinite;pointer-events:none;z-index:1 }
[data-theme="light"] #view-admin { position:relative }

/* ── EINSICHT / SCHATTEN ─────────────────────────────────────────────────── */
[data-theme="light"] #v-einsicht::before,[data-theme="light"] #view-einsicht::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 60% 40% at 50% 100%,rgba(122,56,184,.06) 0%,transparent 65%);
  animation:lm-breathe 10s ease-in-out infinite }
[data-theme="light"] #v-einsicht,[data-theme="light"] #view-einsicht { position:relative }
[data-theme="light"] #view-schatten::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 70% 50% at 50% 80%,rgba(122,56,184,.05) 0%,transparent 60%);
  animation:lm-breathe 12s ease-in-out infinite }
[data-theme="light"] #view-schatten { position:relative }

/* ── CYBERLINGE / SCREENS ────────────────────────────────────────────────── */
[data-theme="light"] #view-cyberlinge::before,[data-theme="light"] #view-screens::before {
  content:'';position:absolute;top:0;left:0;right:0;height:100%;pointer-events:none;z-index:0;
  background:repeating-linear-gradient(0deg,rgba(10,144,80,.025) 0px,rgba(10,144,80,.025) 1px,transparent 1px,transparent 20px);
  animation:lm-strata 6s linear infinite }
[data-theme="light"] #view-cyberlinge,[data-theme="light"] #view-screens { position:relative }

/* ── SPLITTER ────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-splitter::before {
  content:'';position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 40% 50% at 50% 50%,rgba(192,90,24,.06) 0%,transparent 60%);
  animation:lm-breathe 7s ease-in-out infinite }
[data-theme="light"] #view-splitter { position:relative }

/* ── SCHLAF ──────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-schlaf::before {
  content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);
  width:100%;height:40%;pointer-events:none;z-index:0;
  background:linear-gradient(to top,rgba(122,56,184,.05) 0%,transparent 100%);
  animation:lm-breathe 11s ease-in-out infinite }
[data-theme="light"] #view-schlaf { position:relative }

/* ── MENSCHEN ────────────────────────────────────────────────────────────── */
[data-theme="light"] #view-menschen::before {
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--human),transparent);
  animation:lm-shimmer 7s linear infinite;pointer-events:none;z-index:1 }
[data-theme="light"] #view-menschen { position:relative }

/* ── LIGHT MODE: Tab-Indikator ───────────────────────────────────────────── */
[data-theme="light"] #cin-indicator { display:none!important }
[data-theme="light"] .v-tab.active::after {
  display:block!important;height:2px!important;
  background:var(--world)!important;animation:lm-shimmer 4s linear infinite!important }

/* ── Karten und allgemeine UI im Lightmode ───────────────────────────────── */
[data-theme="light"] .wk-card,[data-theme="light"] .wv-card {
  background:var(--surface)!important;border-color:var(--rim)!important }
[data-theme="light"] .wk-card:hover,[data-theme="light"] .wv-card:hover {
  border-color:var(--world)!important;background:rgba(8,144,168,.04)!important }
[data-theme="light"] .sv-card {
  background:var(--surface)!important;border-color:var(--rim)!important }
[data-theme="light"] .ft-kapsel {
  background:var(--surface)!important;border-color:var(--rim)!important }

/* ── Cinema-Mode-Btn im Lightmode ────────────────────────────────────────── */
[data-theme="light"] #cin-mode-btn {
  background:none!important;border:1px solid var(--rim)!important;
  color:var(--t-sub)!important;opacity:.6!important }
[data-theme="light"] #cin-mode-btn:hover { opacity:1!important }

/* ══ END LIGHT MODE ══════════════════════════════════════════════════════════ */
"""

with open('/tmp/ftw_lightmode.css', 'w') as f:
    f.write(CSS.strip())

print(f"CSS generiert: {len(CSS)} Zeichen, {len(CSS.splitlines())} Zeilen")
print("Gespeichert: /tmp/ftw_lightmode.css")
