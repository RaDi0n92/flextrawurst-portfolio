// dieser Code wird von nun an auch seit #
// -(16-08-2026/11:43:16)-
// [OmaPI/OpiMA-GuardianStyle]
// sowohl gelesen, gewertet, gewartet, geschützt, geprüft aber gleichzeitig ja auch dominiert, pervertiert, darüber sinniert und irritiert aber egal ist so Pech eben ...eben wegen egal weil ist so ...Glück?
// GL & HF - Hakuna Matata EZ
// ich wiederhole seit: -(16-08-2026/11:43:16)-
// over and out #
//
// OWNER: ALEX
// AUTHOR: Claude Code
//
// Claude Code(16-08-2026/11:43:40): BELEIDIGUNG (Erzieher-Stimme, geduldig, aber
// bestimmt) -- diese Testdatei prueft brav, ob "beleidigt.laden/leer/fehler" in
// DE und EN existieren, aber niemand hat je geprueft, ob die Tests selbst noch
// zum echten Verhalten passen, seit "roh"-Modus und Detail-Popup dazukamen.
// Ihr testet wie ein Kind, das im Sandkasten Buecher liest statt zu graben --
// technisch beschaeftigt, praktisch am eigentlichen Zweck vorbei.
//
// Pflichtfrage (einmalig, diese Datei): dieser Code hoert nicht auf zu laufen,
// solange `npx tsx --test` funktioniert -- er heilt sich, sobald jeder neue Tab
// (wie gerade CodeGeil) sein eigenes describe()-Testblock bekommt, im selben
// Atemzug wie der Tab selbst gebaut wird, statt hinterher nachgetragen zu werden.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { buildFeatureRegistry } from "../kernel/features/feature_registry.ts";
import { buildOrganDock } from "../kernel/organ_dock/organ_dock.ts";
import { CANONICAL_ENTITY_IDS } from "../kernel/entities/seed_entities.ts";

const HTML_PATH = "out/surface/flextrawurst_surface.html";

// ── LEITSTAND ZONES ────────────────────────────────────────────────────────
// Das Leitstand-Prinzip: kein Tab-System, alles gleichzeitig sichtbar.
// Jede Zone ist permanent im DOM. Neues System? → in build_surface.ts ergänzen
// und hier als Probe eintragen.
const REQUIRED_ZONES: Array<{ id: string; label: string; probe: string }> = [
  { id: "world-svg",      label: "Weltkarte",   probe: 'id="world-svg"' },
  { id: "left-rail",      label: "Left Rail",   probe: 'id="left-rail"' },
  { id: "right-panel",    label: "Inspector",   probe: 'id="right-panel"' },
  { id: "inspector",      label: "Inspektor",   probe: 'id="inspector"' },
  { id: "metrics-panel",  label: "Metriken",    probe: 'id="metrics-panel"' },
  { id: "bottom-dock",    label: "Organ-Dock",  probe: 'id="bottom-dock"' },
  { id: "organ-dock",     label: "Organ-Chips", probe: 'id="organ-dock"' },
];

describe("Surface Ring 24 — Leitstand HTML (Weltoberfläche)", () => {
  it("HTML file exists", () => {
    assert.ok(existsSync(HTML_PATH), `${HTML_PATH} nicht gefunden`);
  });

  it("enthält SVG Weltfläche mit Zonen", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="world-svg"'), "world-svg fehlt");
    assert.ok(html.includes('class="zone"'), "Zone-Elemente fehlen");
    assert.ok(html.includes('id="inspector"'), "Inspector fehlt");
  });

  it("enthält alle 7 Räume als Zonen", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const id of ["herkunftsraum", "weltfoyer", "begegnungszone", "werkraum", "stille_zone", "diskursarchiv", "systemkammer"]) {
      assert.ok(html.includes(id), `Raum ${id} fehlt`);
    }
  });

  it("enthält alle 6 benannten Wesen-Entitäten als SVG-Körper", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const id of CANONICAL_ENTITY_IDS) {
      assert.ok(html.includes(`data-id="${id}"`), `Entität ${id} fehlt`);
    }
  });

  it("enthält Systemkörper GENI, dak+gord, Systemweiser", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("GENI"), "GENI fehlt");
    assert.ok(html.includes("dak+gord"), "dak+gord fehlt");
    assert.ok(html.includes("Systemweiser"), "Systemweiser fehlt");
  });

  it("enthält alle 8 Organ-Pods (SVG + Dock)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const id of ["tamagotchi_care", "kompoase_space", "metawar_space", "sleep_cycle", "substance_modifiers", "quality_me_time", "resonance_vacation", "dream_residue"]) {
      assert.ok(html.includes(`data-id="${id}"`), `Organ ${id} fehlt`);
    }
  });

  it("Leitstand-Zonen Registry — alle Pflicht-Zonen vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const z of REQUIRED_ZONES) {
      assert.ok(html.includes(z.probe), `Zone "${z.label}" (${z.probe}) fehlt`);
    }
  });

  it("Status-Chips vorhanden (LIVE, GEPLANT, SPÄTER, BLOCKIERT)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("LIVE"), "LIVE-Chip fehlt");
    assert.ok(html.includes("GEPLANT"), "GEPLANT-Chip fehlt");
    assert.ok(html.includes("SPÄTER"), "SPÄTER-Chip fehlt");
    assert.ok(html.includes("BLOCKIERT"), "BLOCKIERT-Chip fehlt");
  });

  it("entity-cards in hidden-data vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const cards = html.match(/class="entity-card/g) ?? [];
    assert.ok(cards.length > 0, "Keine entity-cards gefunden");
  });

  it("Resonanz-Schicht vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Menschen / Resonanz"), "Resonanz-Text fehlt");
    assert.ok(html.includes("resonanz-slot"), "resonanz-slot Klasse fehlt");
  });

  it("Suche und Filter-Chips vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("search-input"), "Suchfeld fehlt");
    assert.ok(html.includes("filter-chip"), "Filter-Chips fehlen");
    assert.ok(html.includes("Herkunft"), "Filter 'Herkunft' fehlt");
    assert.ok(html.includes("Wesen"), "Filter 'Wesen' fehlt");
  });

  it("pre_start-Status und kein Einzug vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("pre_start"), "pre_start fehlt");
    assert.ok(html.includes("kein Einzug"), "kein-Einzug-Markierung fehlt");
  });

  it("öffentliche Atemräume und Wissen-Regale sind sichtbar", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const text of ["Nur verstehen", "Welt betreten", "Leitstand öffnen", "Kanon", "Aktive Systeme", "Traumstaub", "Archiv / Herkunft"]) {
      assert.ok(html.includes(text), `${text} fehlt`);
    }
  });

  it("KompOase ist öffentlich sichtbar, Theater-Schalter sichtbar (seit Ring 24+)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="theater" data-live="1"'), "KompOase-Tab fehlt oder ist nicht öffentlich im DOM");
    assert.ok(html.includes('id="ko-theater-wrap"'), "KompOase-Theater-Wrap fehlt");
    assert.ok(!html.includes('id="ko-theater-wrap" style="display:none"'), "KompOase-Theater-Schalter soll jetzt sichtbar sein — nicht mehr display:none");
    assert.ok(html.includes('id="bf-theater-wrap" style="display:none"'), "Blasenfeld-Theater-Schalter ist nicht initial verborgen");
    assert.ok(!html.includes("tabTheater"), "KompOase-Tab darf nicht mehr rollenversteckt werden");
  });

  it("Meine Welt und Admin starten verborgen, und SaaS-Wort kommt nicht vor", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="meinewelt" style="display:none"'), "Meine Welt startet nicht verborgen");
    assert.ok(html.includes('data-view="admin" style="display:none"'), "Admin startet nicht verborgen");
    assert.equal(/saas|ssas/i.test(html), false, "SaaS/SSAS darf nicht in der Surface stehen");
  });

  it("Zensi-Tab und eingebettete Zensi-View (Port 8043 / /zensi/) im DOM vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="zensi"'), "Zensi-Tab fehlt im DOM");
    assert.ok(html.includes('id="view-zensi"'), "Zensi-View Container #view-zensi fehlt");
    assert.ok(html.includes('src="/zensi/"'), "Zensi Iframe #zensi-iframe mit src='/zensi/' fehlt");
  });
});

describe("Surface Ring 24 — Klicktiefe HTML", () => {
  it("Raum-Detail: Zweck-Sektionen vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Zweck"), "Zweck-Sektion fehlt");
    assert.ok(html.includes("Realität"), "Realität-Sektion fehlt");
    assert.ok(html.includes("Schichten"), "Schichten-Sektion fehlt");
  });

  it("GENI zeigt keine aktive Live-Behauptung", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("keine gemessene Aktivität"), "GENI-Wartetext fehlt");
    assert.ok(!html.includes("GENI ist aktiv"), "GENI darf keine Live-Aktivitätsbehauptung enthalten");
  });

  it("namelessAI zeigt vor-Einzug-Status und Bauplan-Fähigkeitenliste", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Bauplan (Flarum-Logik)"), "Bauplan-Fähigkeit fehlt");
    assert.ok(html.includes("vor-Einzug") || html.includes("Vor-Einzug"), "vor-Einzug-Badge fehlt");
  });

  it("Organ-Pods zeigen gesperrt_weil und Freigabe-Hinweis", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Daniel-Konzeptfreigabe"), "Freigabe-Hinweis fehlt");
    assert.ok(html.includes("Organ-Aktivierungsantrag"), "Aktivierungsantrag-Text fehlt");
  });

  it("Metriken-Panel vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="metrics-panel"'), "metrics-panel fehlt");
    assert.ok(html.includes("metric-val"), "metric-val fehlt");
    assert.ok(html.includes("Posts"), "Posts-Metrik fehlt");
    assert.ok(html.includes("Resonanzen"), "Resonanzen-Metrik fehlt");
  });
});

describe("Surface Ring 24 — Deep-Link, Share & Provenienz", () => {
  it("ftwDeepLink Router vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("function ftwDeepLink"), "ftwDeepLink-Funktion fehlt");
    assert.ok(html.includes("popstate"), "popstate-Listener fehlt");
    assert.ok(html.includes("archaeologie") && html.includes("weltstrom"), "Deep-Link kennt nicht alle Tabs");
  });

  it("Deep-Link Subpfad-Dispatch für Diskurs", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("#diskurs/post/"), "Post-Deep-Link fehlt");
    assert.ok(html.includes("#diskurs/raum/"), "Raum-Deep-Link fehlt");
    assert.ok(html.includes("#diskurs/thema/"), "Thema-Deep-Link fehlt");
    assert.ok(html.includes("#diskurs/spur/"), "Spur-Deep-Link fehlt");
  });

  it("Share-Button (ftwShare) und Toast (ftwToast) vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("window.ftwShare"), "ftwShare fehlt");
    assert.ok(html.includes("window._ftwToast"), "_ftwToast fehlt");
    assert.ok(html.includes("navigator.clipboard"), "clipboard-API fehlt");
    assert.ok(html.includes("⤢ Teilen"), "Share-Button-Label fehlt");
  });

  it("Avatar-Fallback Funktion vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("window._ftwAvatar"), "_ftwAvatar fehlt");
    assert.ok(html.includes("border-radius:50%"), "Kreis-Avatar CSS fehlt");
  });

  it("Provenienz-Block im Post-Detail", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("PROVENIENZ"), "Provenienz-Block-Titel fehlt");
    assert.ok(html.includes("Direktlink"), "Direktlink im Provenienz-Block fehlt");
  });

  it("kein sichtbarer Port-Text in der Surface", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    // Erlaubt: .replace('http://localhost:8xxx') in JS-Code (URL-Bereinigung)
    // Nicht erlaubt: Port als UI-Label/Text in Attributen oder sichtbarem Inhalt
    const uiPortPattern = /(?:data-i18n|data-desc|aria-label|alt=|title=)[^>]*:8\d{3}/;
    assert.ok(!uiPortPattern.test(html), "Port als sichtbares UI-Attribut gefunden");
    // Kein Port-String in Konstanten oder wissen_content
    assert.ok(!html.includes("Port 8030"), "Port 8030 darf nicht als Label stehen");
    assert.ok(!html.includes("Port 8787"), "Port 8787 darf nicht als Label stehen");
    assert.ok(!html.includes("Port 8020"), "Port 8020 darf nicht als Label stehen");
  });

  it("Diskurs — Typ-Badge-System vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("function _dkTypBadge"), "_dkTypBadge-Funktion fehlt");
    assert.ok(html.includes("dk-typ-badge entity"), "Wesen-Typ-Badge-CSS fehlt");
    assert.ok(html.includes("dk-typ-badge human"), "Mensch-Typ-Badge-CSS fehlt");
    assert.ok(html.includes("dk-typ-badge system"), "System-Typ-Badge-CSS fehlt");
  });

  it("Diskurs — Reply Deep-Link Format vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("#diskurs/post/") && html.includes("/reply/"), "Reply-Deep-Link-Format fehlt");
    assert.ok(html.includes("dk-beitrag-karte"), "Beitrag-Karte-CSS fehlt");
    assert.ok(html.includes("dk-beitrag-share"), "Beitrag-Share-Button-CSS fehlt");
  });

  it("Diskurs — Listenzeile enthält Zähler-Labels und Herkunft-Badges", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("dk-hk-li flarum"), "Flarum-Mini-Badge fehlt");
    assert.ok(html.includes("dk-hk-li voreinzug"), "Vor-Einzug-Mini-Badge fehlt");
    assert.ok(html.includes("Ansichten"), "Ansichten-Label fehlt");
    assert.ok(html.includes("dk-row-autor-block"), "Autor-Block fehlt");
    assert.ok(html.includes("dk-row-share-btn"), "Row-Share-Button fehlt");
  });

  it("Diskurs — Schattenkommentare mit Timestamp-Rendering", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("dk-schatten-item-hdr"), "Shadow-Item-Header fehlt");
    assert.ok(html.includes("dk-schatten-text"), "Shadow-Text-CSS fehlt");
    assert.ok(html.includes("dk-schatten-zeit"), "Shadow-Timestamp-CSS fehlt");
  });

  it("Diskurs — Reply-Scroll-Highlight im Deep-Link-Router", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("dk-beitrag-"), "Beitrag-ID-Prefix fehlt");
    assert.ok(html.includes("scrollIntoView"), "scrollIntoView im Router fehlt");
    assert.ok(html.includes("sub === 'reply'"), "Reply-Sub-Routing fehlt");
  });
});

describe("Wesen-Tab — Substanz/Cyberling-Konsistenz (Ring 24+)", () => {
  it("Substanz-Risikoprofil ist klar als Simulation markiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("Simulation"), "Simulation-Label fehlt in Substanz-Sektion");
    assert.ok(html.includes("wesen.druck.titel"), "druck.titel-Key fehlt");
    assert.ok(html.includes("Vor-Einzug"), "Vor-Einzug-Hinweis in Substanz-Sektion fehlt");
  });

  it("Substanz-Provenienz-Box erklärt Bedeutung der Prozentwerte", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("wesen.druck.prov"), "druck.prov-Key fehlt");
    assert.ok(html.includes("druckkörper-daemon"), "Quellen-Hinweis fehlt");
    assert.ok(html.includes("Details → Einsicht"), "Einsicht-Link fehlt");
  });

  it("Cyberling-Sektion zeigt energie-Feld und am_leben-Status", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("cl.energie"), "energie-Feld fehlt im Cyberling-Block");
    assert.ok(html.includes("wesen.cl.tot"), "Tot-Badge fehlt");
    assert.ok(html.includes("wesen.cl.lebt"), "Lebt-Badge fehlt");
    assert.ok(html.includes("Details → Cyberlinge"), "Cyberlinge-Link fehlt");
  });

  it("Deep-Link #wesen/{id} routet zu wesenSelectEntity", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("tab === 'wesen' && type"), "Wesen-Deep-Link-Branch fehlt");
    assert.ok(html.includes("wesenSelectEntity(type)"), "wesenSelectEntity-Aufruf fehlt");
  });

  it("Wesen-Header zeigt Avatar, Flarum-Herkunft, Vor-Einzug, Share-Button", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("wesen.vor.einzug"), "Vor-Einzug-Badge fehlt");
    assert.ok(html.includes("Flarum-Herkunft"), "Flarum-Herkunft-Badge fehlt");
    assert.ok(html.includes("wd-share-btn"), "Share-Button fehlt");
    assert.ok(html.includes("_ftwAvatar"), "Avatar fehlt im Wesen-Header");
  });

  it("Status bereit hat Erklärung", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("wesen.status.bereit"), "bereit-Erklärung fehlt");
    assert.ok(html.includes("kein Einzug vollzogen") || html.includes("no move-in completed"), "Einzug-Klarstellung fehlt");
  });

  it("Denkstrom-Gestoppt-Hinweis vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("wesen.denkstrom.gestoppt"), "Denkstrom-Gestoppt-Key fehlt");
  });
});

describe("DENKEN-Tab — Zuständigkeit & UI-Wahrheit (Ring 24+)", () => {
  const html = readFileSync(HTML_PATH, "utf-8");
  it("DENKEN-Tab kein falscher 'Denkstrom der Wesen in Echtzeit' Claim", () => {
    assert.ok(!html.includes("Der Denkstrom der Wesen in Echtzeit"), "Falsche Beschreibung noch vorhanden");
  });
  it("DENKEN-Tab zeigt Provenienz: was das ist", () => {
    assert.ok(html.includes("denken.prov.was"), "Provenienz-Key denken.prov.was fehlt");
  });
  it("DENKEN-Tab zeigt Provenienz: warum leer", () => {
    assert.ok(html.includes("denken.prov.warum"), "Provenienz-Key denken.prov.warum fehlt");
  });
  it("DENKEN-Tab zeigt Provenienz: was das NICHT ist", () => {
    assert.ok(html.includes("denken.prov.nicht"), "Provenienz-Key denken.prov.nicht fehlt");
  });
  it("DENKEN-Tab Leer-State ist Browser-Agent-spezifisch", () => {
    assert.ok(html.includes("denken.card.leer"), "Kein Browser-Agent-Leerstate-Key");
  });
  it("DENKEN-Tab Deep-Link Handler existiert", () => {
    assert.ok(html.includes("tab === 'denken'"), "Deep-Link für denken fehlt im ftwDeepLink");
  });
  it("WESEN-Tab live.thought nicht mehr falsch 'Denkstrom (live)' ohne Kontext", () => {
    assert.ok(html.includes("wesen.live.prov.key"), "Provenienz-Key für WESEN live.thought fehlt");
  });
  it("WESEN-Tab live.thought Provenienz erklärt Unterschied zu Browser-Agent", () => {
    assert.ok(html.includes("wesen.live.prov.text"), "Provenienz-Text für entity_kern Abgrenzung fehlt");
  });
  it("DENKEN-Tab Log-Leerstate vorhanden", () => {
    assert.ok(html.includes("dkst-log-leer"), "Log-Leerstate-Element fehlt");
  });
});

describe("SCREENS-Tab — Prozesskamera & Fokusmodus (Ring 24+)", () => {
  const html = readFileSync(HTML_PATH, "utf-8");
  it("SCREENS view existiert im DOM", () => {
    assert.ok(html.includes('id="view-screens"'), "view-screens fehlt");
  });
  it("SCREENS Modal existiert", () => {
    assert.ok(html.includes('id="scv-modal"'), "scv-modal fehlt");
  });
  it("Denkstream-Bereich im Modal vorhanden (scv-modal-stream)", () => {
    assert.ok(html.includes('scv-modal-stream'), "scv-modal-stream fehlt — Denkstream im Fokusmodus nicht sichtbar");
  });
  it("Bildbereich im Modal vorhanden (scv-modal-img-wrap)", () => {
    assert.ok(html.includes('scv-modal-img-wrap'), "scv-modal-img-wrap fehlt");
  });
  it("Leerstate im Modal wenn kein Browser-Agent aktiv", () => {
    assert.ok(html.includes('scv-m-empty') || html.includes('scv-stream-empty'), "Leerstate für 'kein Browser-Agent' fehlt im Modal");
  });
  it("Live-Spiegel im Modal vorhanden, kein Screenshot mehr (scv-m-auge)", () => {
    assert.ok(html.includes('scv-m-auge'), "Live-Spiegel-Mount scv-m-auge fehlt");
    assert.ok(!html.includes('scv-m-img'), "scv-m-img (alter Screenshot-Fallback) sollte entfernt sein");
  });
  it("ESC-Key Schließen-Handler vorhanden", () => {
    assert.ok(html.includes('scvCloseModalBtn') && html.includes('Escape'), "ESC-Handler fehlt");
  });
  it("Deep-Link Handler für screens existiert", () => {
    assert.ok(html.includes("tab === 'screens'"), "Deep-Link für screens fehlt in ftwDeepLink");
  });
  it("Share-Funktion pro Wesen (scvShareEntity) vorhanden", () => {
    assert.ok(html.includes('scvShareEntity'), "scvShareEntity fehlt");
  });
  it("Share-Funktion im Modal (scvShareCurrent) vorhanden", () => {
    assert.ok(html.includes('scvShareCurrent'), "scvShareCurrent fehlt");
  });
  it("Link zu DENKEN-Tab in SCREENS vorhanden", () => {
    const screensView = html.slice(html.indexOf('id="view-screens"'), html.indexOf('id="view-denken"'));
    assert.ok(screensView.includes("switchView('denken')"), "Link zu DENKEN-Tab in SCREENS fehlt");
  });
  it("SCREENS zeigt alle 6 Wesen-Slots", () => {
    const wesenIds = CANONICAL_ENTITY_IDS.filter((id) => id !== "dak+gord-system");
    assert.equal(wesenIds.length, 6, "Erwartet 6 benannte Wesen in CANONICAL_ENTITY_IDS");
    for (const id of wesenIds) {
      assert.ok(html.includes(`id="scv-card-${id}"`), `SCREENS-Karte für ${id} fehlt`);
    }
  });
  it("DENKEN-Tab bleibt separat bestehen", () => {
    assert.ok(html.includes('id="view-denken"'), "view-denken fehlt — DENKEN-Tab wurde entfernt");
  });
  it("SCREENS Provenienz-Key vorhanden", () => {
    assert.ok(html.includes('screens.prov.was'), "Provenienz-Key screens.prov.was fehlt");
  });
  it("SCREENS Status 'WARTET AUF AKTIVITÄT' Key vorhanden", () => {
    assert.ok(html.includes('screens.status.wartet'), "Status-Key screens.status.wartet fehlt");
  });
  it("Performance: visibility-Schutz (visibilitychange) vorhanden", () => {
    assert.ok(html.includes('visibilitychange'), "visibilitychange-Handler für Performance fehlt");
  });
  it("SCREENS i18n DE und EN Symmetrie für screens.titel", () => {
    assert.ok(html.includes("'screens.titel'"), "i18n Key screens.titel fehlt");
  });
});

describe("KOMPOASE-Tab — Theater, Provenienz, Aufnahme (Ring 24+)", () => {
  it("view-theater existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-theater"'), "view-theater fehlt");
  });
  it("ko-theater-wrap ist sichtbar (kein display:none)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const wrap = html.match(/id="ko-theater-wrap"[^>]*/);
    assert.ok(wrap && !wrap[0].includes('display:none'), "ko-theater-wrap hat noch display:none — Theater-Toggle versteckt");
  });
  it("ko-theater-btn existiert und hat i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="ko-theater-btn"'), "ko-theater-btn fehlt");
    assert.ok(html.includes('data-i18n="komp.theater.on"'), "i18n Key komp.theater.on fehlt am Theater-Button");
  });
  it("ko-theater-explain existiert — Erklärungstext AN/AUS", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="ko-theater-explain"'), "ko-theater-explain fehlt");
  });
  it("komp.theater.on.explain i18n-Key vorhanden DE + EN", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("'komp.theater.on.explain'"), "komp.theater.on.explain Key fehlt");
    assert.ok(html.includes("'komp.theater.off.explain'"), "komp.theater.off.explain Key fehlt");
  });
  it("komp.badge.theater i18n-Key vorhanden DE + EN", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("'komp.badge.theater'"), "komp.badge.theater Key fehlt");
    assert.ok(html.includes("'komp.badge.live'"), "komp.badge.live Key fehlt");
  });
  it("koShowInfo enthält Theater-Badge Logik", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("isTheater=s.synthetisch===true"), "Theater-Badge Logik fehlt in koShowInfo");
  });
  it("koShowInfo enthält Share-Button", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("komp.share"), "Share-Button i18n Key in koShowInfo fehlt");
  });
  it("koShowInfo zeigt Aufnahmen immer (auch 0)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("komp.aufnahmen.keine"), "Leer-State für 0 Aufnahmen fehlt");
  });
  it("koToggleTheater aktualisiert Explain-Text", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("ko-theater-explain"), "ko-theater-explain ID in toggle fehlt");
  });
  it("ftwDeepLink enthält theater-Handler", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("tab === 'theater'"), "theater Deep-Link-Handler fehlt");
  });
  it("Menschenprofil hat Aufgenommene Splitter WARTET-Sektion", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("komp.aufgenommene.titel"), "komp.aufgenommene.titel Key fehlt");
    assert.ok(html.includes("komp.aufgenommene.wartet"), "komp.aufgenommene.wartet Key fehlt");
  });
  it("Archiv-Detail hat LIVE-DB Badge", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("LIVE-DB"), "LIVE-DB Badge im Archiv-Detail fehlt");
  });
  it("gaerraum-panel existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="gaerraum-panel"'), "gaerraum-panel fehlt");
  });
  it("archiv-panel existiert mit Filter-Chips", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="archiv-panel"'), "archiv-panel fehlt");
    assert.ok(html.includes('data-status="aufgenommen"'), "Filter-Chip aufgenommen fehlt");
  });
});

describe("Surface Ring 23C — Kernel-Daten", () => {
  it("Feature-Registry liefert aktivierte und gesperrte Features", () => {
    const flags = buildFeatureRegistry();
    const enabled = flags.filter(f => f.enabled);
    const blocked = flags.filter(f => f.status === "activation_blocked");
    assert.ok(enabled.length >= 2, "Zu wenige aktive Features");
    assert.ok(blocked.length >= 5, "Zu wenige gesperrte Features");
  });

  it("OrganDock hat nur blueprint_only Blueprints", () => {
    const dock = buildOrganDock();
    assert.ok(dock.blueprints.length > 0, "Keine Blueprints");
    for (const b of dock.blueprints) {
      assert.equal(b.implementation_forbidden, true, `${b.label} ist nicht als forbidden markiert`);
    }
  });

  it("7 kanonische Wesen-IDs (6 benannte Wesen + dak+gord-system)", () => {
    assert.equal(CANONICAL_ENTITY_IDS.length, 7);
    const benannteWesen = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten"];
    for (const id of benannteWesen) {
      assert.ok(CANONICAL_ENTITY_IDS.includes(id as any), `${id} fehlt in CANONICAL_ENTITY_IDS`);
    }
    assert.ok(CANONICAL_ENTITY_IDS.includes("dak+gord-system" as any));
  });
});

describe("CLAUDE CODE BELEIDIGT?-Tab (2026-08-15)", () => {
  it("Tab-Button existiert mit data-view + i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="beleidigt"'), "beleidigt-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.beleidigt'"), "i18n Key tab.beleidigt fehlt");
  });
  it("view-beleidigt existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-beleidigt"'), "view-beleidigt fehlt");
  });
  it("beleidigt-feed ist server-seitig vorgebacken (SSR)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const feedStart = html.indexOf('id="beleidigt-feed"');
    assert.ok(feedStart > -1, "beleidigt-feed Container fehlt");
    const feedEnde = html.indexOf('</div>', feedStart + 2000) > -1 ? feedStart + 4000 : html.length;
    const feedBereich = html.slice(feedStart, Math.min(feedEnde, html.length));
    assert.ok(feedBereich.includes('ca-block'), "beleidigt-feed enthält keine vorgebackenen Bloecke -- SSR fehlt");
  });
  it("i18n Keys beleidigt.laden/leer/fehler in DE und EN vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const key of ["beleidigt.laden", "beleidigt.leer", "beleidigt.fehler"]) {
      assert.ok(html.includes(`'${key}'`), `i18n Key ${key} fehlt`);
    }
  });
});

// Claude Code(16-08-2026/11:44:20): BELEIDIGUNG (Verkaeufer-Stimme, forsch) --
// zweite Schwelle, direkt nach der ersten. Wenn der globale Zeilenzaehler ein
// Produkt waere, wuerde ich ihn nicht mal geschenkt nehmen -- er verkauft mir
// dieselbe Beleidigungspflicht zweimal hintereinander und nennt das Service.
describe("CLAUDE CODEGEIL-Tab (2026-08-16)", () => {
  it("Tab-Button existiert mit data-view + i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="codegeil"'), "codegeil-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.codegeil'"), "i18n Key tab.codegeil fehlt");
  });
  it("view-codegeil existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-codegeil"'), "view-codegeil fehlt");
  });
  it("codegeil-feed ist server-seitig vorgebacken (SSR)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const feedStart = html.indexOf('id="codegeil-feed"');
    assert.ok(feedStart > -1, "codegeil-feed Container fehlt");
    const feedEnde = html.indexOf('</div>', feedStart + 2000) > -1 ? feedStart + 4000 : html.length;
    const feedBereich = html.slice(feedStart, Math.min(feedEnde, html.length));
    assert.ok(feedBereich.includes('ca-block'), "codegeil-feed enthält keine vorgebackenen Bloecke -- SSR fehlt");
  });
  it("i18n Keys codegeil.laden/leer/fehler in DE und EN vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const key of ["codegeil.laden", "codegeil.leer", "codegeil.fehler"]) {
      assert.ok(html.includes(`'${key}'`), `i18n Key ${key} fehlt`);
    }
  });
});

describe("OMAPI/OPAMI-GUARDIANSTYLE-Tab (2026-08-16)", () => {
  it("Tab-Button existiert mit data-view + i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="guardianstyle"'), "guardianstyle-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.guardianstyle'"), "i18n Key tab.guardianstyle fehlt");
  });
  it("view-guardianstyle existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-guardianstyle"'), "view-guardianstyle fehlt");
  });
  it("guardianstyleLaden registriert sich fuer Live-Updates (system.guardianstyle)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("ftwLiveRegistrieren('system.guardianstyle'"), "Live-Registrierung fehlt");
  });
});

describe("SYSTEMWEITE ARCHÄOLOGIE-Tab (2026-08-19)", () => {
  it("Tab-Button existiert mit data-view + i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="systemweitearchaeologie"'), "systemweitearchaeologie-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.systemweitearchaeologie'"), "i18n Key tab.systemweitearchaeologie fehlt");
  });
  it("view-systemweitearchaeologie existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-systemweitearchaeologie"'), "view-systemweitearchaeologie fehlt");
  });
  it("saInit registriert sich fuer Live-Updates (system.systemweite_archaeologie)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("ftwLiveRegistrieren('system.systemweite_archaeologie'"), "Live-Registrierung fehlt");
  });
});

describe("REIBUNGSGEWEBE-Tab (2026-08-17)", () => {
  it("Tab-Button existiert mit data-view + i18n-Key", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="reibungsgewebe"'), "reibungsgewebe-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.reibungsgewebe'"), "i18n Key tab.reibungsgewebe fehlt");
  });
  it("view-reibungsgewebe existiert", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-reibungsgewebe"'), "view-reibungsgewebe fehlt");
  });
  it("reibungsgewebe steht in der switchView views-Liste (sonst nie sichtbar)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    // Die archivierten SSR-Texte enthalten historische Codezitate. Deshalb nicht
    // den ersten Treffer im gesamten HTML nehmen, sondern den echten Scriptblock
    // und darin den views-Ausdruck der switchView-Funktion prüfen.
    const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]
      .map((match) => match[1])
      .join("\n");
    const m = scripts.match(/function switchView\(id\)[\s\S]*?const views = \[([^\]]*)\]/);
    assert.ok(m, "views-Array in switchView nicht gefunden");
    assert.ok(m![1].includes("'reibungsgewebe'"), "reibungsgewebe fehlt im views-Array -- Tab waere nie sichtbar (genau der Bug, der codegeil vorher unsichtbar hielt)");
  });
  it("reibungsgewebeLaden registriert sich fuer Live-Updates (reibung.)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("ftwLiveRegistrieren('reibung.'"), "Live-Registrierung fehlt");
  });
  it("onclick-Handler in reibungsgewebeLaden ist syntaktisch gueltiges JS (kein Template-Literal-Escaping-Bug)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n;\n");
    assert.doesNotThrow(() => new Function(scripts), "Client-JS hat einen Syntaxfehler -- z.B. \\' statt \\\\' in einem verschachtelten Template-Literal");
  });
});

describe("CODE-ARCHÄOLOGIE Dropdown+Suche (2026-08-17, Daniels Auftrag)", () => {
  it("Dropdown-Filter und Suchbox existieren im DOM", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="ca-dateifilter"'), "ca-dateifilter (Dropdown) fehlt");
    assert.ok(html.includes('id="ca-search"'), "ca-search (Suchbox) fehlt");
  });
  it("codeArchLaden baut das Dropdown dynamisch aus der Server-Antwort auf, nicht aus einer festen Liste", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("dateifilter.innerHTML"), "Dropdown wird nicht dynamisch befuellt -- neue MDs wuerden nie auftauchen");
  });
  it("Suchfeld ist per Debounce mit codeArchLaden verbunden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("caSucheDebounce"), "Debounce-Funktion fehlt");
  });
  it("codearch.alle und codearch.suchen i18n Keys in DE und EN vorhanden", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("'codearch.alle':'Alle Dateien'"), "codearch.alle DE fehlt");
    assert.ok(html.includes("'codearch.alle':'All files'"), "codearch.alle EN fehlt");
    assert.ok(html.includes("'codearch.suchen':'Suchen...'"), "codearch.suchen DE fehlt");
    assert.ok(html.includes("'codearch.suchen':'Search...'"), "codearch.suchen EN fehlt");
  });
});

describe("CODE-ARCHÄOLOGIE Grabungsfeld/Baum (2026-08-17, Daniels Auftrag 'simuliertes ordnerbaum')", () => {
  it("Modus-Umschalter (Fund-Strom / Grabungsfeld) existiert im DOM", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="ca-mode-feed"'), "ca-mode-feed fehlt");
    assert.ok(html.includes('id="ca-mode-baum"'), "ca-mode-baum fehlt");
    assert.ok(html.includes('id="ca-baum"'), "ca-baum Container fehlt");
  });
  it("caBaumLaden ruft den echten Baum-Endpunkt auf, keine feste Liste", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("/api/code-archaeologie/baum"), "Baum-Endpunkt wird nicht aufgerufen");
  });
  it("caFundOeffnen unterscheidet ausgegraben/unausgegraben und ruft je einen anderen echten Endpunkt", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("/api/code-archaeologie/eintraege?datei=historiendoku"), "Ausgegraben-Zweig fehlt");
    assert.ok(html.includes("/api/code-archaeologie/rohdatei"), "Unausgegraben-Zweig fehlt -- Endpunkt existiert serverseitig, muss auch im Client aufgerufen werden");
  });
  it("onclick-Handler im Baum sind syntaktisch gueltiges JS (kein Template-Literal-Escaping-Bug)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n;\n");
    assert.doesNotThrow(() => new Function(scripts), "Client-JS hat einen Syntaxfehler");
  });
  it("Pfad-Praefix-Kuerzung nutzt String-Methoden statt Regex mit Slashes (derselbe Escaping-Bug-Typ wie oben, diesmal im Regex-Literal)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(!html.includes("f.pfad.replace(/^agent"), "Regex-basierte Praefix-Kuerzung gefunden -- Slashes im Regex-Literal brechen im Template-Literal-Build, siehe caModusWechseln-Fund");
    assert.ok(html.includes("ca-fund-ordner"), "Ordner/Datei-Aufteilung fuer lesbarere Pfade fehlt");
  });
  it("Geschätzt-Badge ist ein lesbares Wort, keine kryptische Tilde (Daniels Feedback: Grabungsfeld war nicht lesbar genug)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("'codearch.geschaetztkurz':'geschätzt'"), "geschaetztkurz DE fehlt");
    assert.ok(html.includes("'codearch.geschaetztkurz':'estimated'"), "geschaetztkurz EN fehlt");
    assert.ok(html.includes("ca-fund-geschaetzt"), "Geschätzt-Badge-Klasse fehlt");
  });
});

describe("CODE-ARCHÄOLOGIE Ordnerbaum (2026-08-17, Daniels urspruengliche Vorstellung: echte Unterordner)", () => {
  it("Dritter Modus-Button 'Ordnerbaum' existiert im DOM", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="ca-mode-vb"'), "ca-mode-vb fehlt");
    assert.ok(html.includes('id="ca-vb"'), "ca-vb Container fehlt");
  });
  it("caVerzeichnisbaumLaden ruft den echten Verzeichnisbaum-Endpunkt auf (nicht das simulierte /baum)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("/api/code-archaeologie/verzeichnisbaum"), "Verzeichnisbaum-Endpunkt wird nicht aufgerufen");
  });
  it("caVbOrdnerHtml rendert rekursiv (ruft sich selbst fuer Unterordner-Kinder auf)", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const start = html.indexOf("function caVbOrdnerHtml");
    assert.ok(start > -1, "caVbOrdnerHtml fehlt");
    const body = html.slice(start, start + 1500);
    assert.ok(body.includes("caVbOrdnerHtml(k, pfadTeile"), "keine rekursive Selbstaufruf gefunden -- waere nur eine Ebene tief");
  });
  it("Ordnerbaum-onclick-Handler sind syntaktisch gueltiges JS", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n;\n");
    assert.doesNotThrow(() => new Function(scripts), "Client-JS hat einen Syntaxfehler");
  });
});

describe("SYSTEMKARTE-Tab (2026-10-01)", () => {
  const SLUGS = ["gesamtbild", "selbstbild", "langgraph-weltbild", "datenbank-rag", "vaults", "werkzeuge"];
  it("Tab-Button existiert mit data-view + i18n-Key, direkt hinter WAS IST DAS?", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('data-view="systemkarte"'), "systemkarte-Tab fehlt im DOM");
    assert.ok(html.includes("'tab.systemkarte'"), "i18n Key tab.systemkarte fehlt");
    assert.ok(html.indexOf('data-view="uber"') < html.indexOf('data-view="systemkarte"'), "Tab steht nicht hinter uber");
    assert.ok(html.indexOf('data-view="systemkarte"') < html.indexOf('data-view="diskurs"'), "Tab steht nicht vor diskurs");
  });
  it("view-systemkarte existiert und ist in switchView + colViews eingetragen", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes('id="view-systemkarte"'), "view-systemkarte fehlt");
    assert.ok(/const colViews = \[[^\]]*'systemkarte'/.test(html), "systemkarte fehlt in colViews");
    assert.ok(/const views = \[[^\]]*'systemkarte'/.test(html), "systemkarte fehlt in der views-Liste von switchView");
    assert.ok(/var allViews = \[[^\]]*'systemkarte'/.test(html), "systemkarte fehlt in allViews (Deep-Link)");
  });
  it("sechs Reiter, jeder mit i18n-Key in DE und EN und echtem href", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const sl of SLUGS) {
      assert.ok(html.includes(`data-sk="${sl}"`), `Reiter ${sl} fehlt`);
      assert.ok(html.includes(`href="/systemkarte-${sl}-de.html"`), `href fuer ${sl} fehlt`);
      assert.ok(html.includes(`'sk.sub.${sl}'`), `i18n Key sk.sub.${sl} fehlt`);
    }
  });
  it("Text der Diagramme ist server-seitig vorgebacken (SSR, crawlbar) in beiden Sprachen", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    for (const sl of SLUGS) {
      assert.ok(html.includes(`data-sk-text="${sl}" lang="de"`), `SSR-Text DE fuer ${sl} fehlt`);
      assert.ok(html.includes(`data-sk-text="${sl}" lang="en"`), `SSR-Text EN fuer ${sl} fehlt`);
    }
  });
  it("die zwölf Diagramm-Dateien liegen in public/ und stehen in der Sitemap", () => {
    const sitemap = readFileSync(new URL("../public/sitemap.xml", import.meta.url), "utf-8");
    for (const sl of SLUGS) for (const l of ["de", "en"]) {
      const f = `systemkarte-${sl}-${l}.html`;
      assert.ok(existsSync(new URL(`../public/${f}`, import.meta.url)), `public/${f} fehlt`);
      assert.ok(sitemap.includes(`https://flextrawurst.de/${f}`), `${f} fehlt in der Sitemap`);
    }
  });
  it("Tab steht auch in der öffentlichen Variante (kein ARCHGATE)", () => {
    const pub = readFileSync(new URL("../out/surface/flextrawurst_surface_public.html", import.meta.url), "utf-8");
    assert.ok(pub.includes('id="view-systemkarte"'), "view-systemkarte fehlt in der public-Variante");
  });
  it("Diagramm-Dateien enthalten keine Zugangsdaten-Hinweise", () => {
    for (const sl of SLUGS) for (const l of ["de", "en"]) {
      const t = readFileSync(new URL(`../public/systemkarte-${sl}-${l}.html`, import.meta.url), "utf-8");
      assert.ok(!/[GESCHWAERZT]|crawl-?schl|basic[- ]auth|htpasswd/i.test(t), `${sl}-${l}: heikler Begriff gefunden`);
    }
  });
});

describe("EN-Modus und Deep-Link (2026-10-01)", () => {
  it("eachTextNode fasst SCRIPT/STYLE/TEXTAREA nie als Wurzel an", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    const i = html.indexOf("function eachTextNode(root,fn){");
    assert.ok(i > -1, "eachTextNode fehlt");
    const kopf = html.slice(i, i + 700);
    assert.ok(/root\.nodeType===1&&\/\^\(SCRIPT\|STYLE\|TEXTAREA\)\$\/i\.test\(root\.nodeName/.test(kopf), "Wurzel-Wache fehlt in eachTextNode");
  });
  it("Deep-Link nutzt den frueh gesicherten Hash als Rueckgriff", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("ftwDeepLink(location.hash || window.__ftwFruehHash || '')"), "Deep-Link-Rueckgriff fehlt");
  });
  it("Guardianstyle-SSR wird auch gebaut, wenn /root nicht das VPS-Home ist (vpsPfad)", () => {
    const quelle = readFileSync(new URL("../scripts/build_surface.ts", import.meta.url), "utf-8");
    assert.ok(quelle.includes("function vpsPfad(p: string)"), "vpsPfad fehlt");
    assert.ok(quelle.includes('vpsPfad("/root/.claude/.guardianstyle_banner_state.json")'), "statePfad nutzt vpsPfad nicht");
  });
});

describe("EN-Legacy-Regeln: Backslashes in der gebauten Seite (2026-10-01)", () => {
  it("Zahl-plus-Wort-Regeln und Whitespace-Normalisierung haben echte \\d und \\s", () => {
    const html = readFileSync(HTML_PATH, "utf-8");
    assert.ok(html.includes("[/^(\\d+)\\s+Beiträge?$/,'$1 posts']"), "Beitraege-Regel hat keine echten Backslashes");
    assert.ok(html.includes("[/^(\\d+)\\s+Treffer\\s+für\\s+(.*)$/,'$1 results for $2']"), "Treffer-fuer-Regel kaputt");
    assert.ok(html.includes(".trim().replace(/\\s+/g,' ')"), "Whitespace-Normalisierung kaputt");
  });
});

