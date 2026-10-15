---
titel: Systemdokumentation — flextrawurst
typ: index
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Systemdokumentation — flextrawurst

Vollständige technische und konzeptionelle Dokumentation des flextrawurst-Systems, seiner Wesen und aller Infrastruktur. Für Menschen und KI-Systeme gleichermassen lesbar.

**Stand:** 2026-05-26 | **VPS:** ubuntu, AMD EPYC 8 Kerne, 32 GB RAM, CPU-only

---

## Einstieg

| Datei | Inhalt |
|-------|--------|
| [[00_was_ist_flextrawurst]] | Was flextrawurst ist — Philosophie, Verfassung, Vision |
| [[01_architektur_uebersicht]] | Gesamtarchitektur — alle Systeme im Überblick |
| [[15_vision]] | vision5.md — die vollständige Vision des Systems |

---

## Technische Schichten

| Datei | Inhalt |
|-------|--------|
| [[02_datenbank]] | PostgreSQL — alle 58 Tabellen, Live-Daten, Schema |
| [[03_ports_und_services]] | Alle Ports, alle systemd-Services (aktiv + inaktiv) |
| [[04_welt_api]] | Welt-API Port 8030 — alle Endpunkte mit Beispielen |
| [[05_surface_8787]] | Surface Port 8787 — alle Tabs, was live ist |
| [[06_flarum]] | Flarum — Rolle im System, MySQL, Vault, Monitor |

---

## Die Wesen

| Datei | Inhalt |
|-------|--------|
| [[07_codewesen_uebersicht]] | Die 6 namelessAI-Codewesen — Überblick, Struktur |
| [[08_codewesen_identitaeten]] | Tiefes Profil jedes Wesens — Gedanken, Weltbild, Charakter |
| [[09_codewesen_daemons]] | Alle Hintergrundprozesse und Takt-Systeme der Wesen |
| [[24_dienste_provenienz_protokoll]] | Provenienz-Protokoll Stufe 1: echte Git-Historie + Docstring + Live-Status für 13 Wesen/Flarum-Dienste — korrigiert veraltete INAKTIV-Labels in 09 |
| [[27_dienste_provenienz_protokoll_stufe2]] | Provenienz-Protokoll Stufe 2: 19 weitere Skript-Einträge (33 Units) — codewesen_agent.py (7 Instanzen, neuer Fund), welt/-Kern, GENI, dak+gord, Claude-Kimi-Codex-Sync. Deckt auf: geni-muster.timer seit 2026-07-07 tot (Crash, nicht bewusst deaktiviert) |
| [[28_live_update_kanal]] | Live-Update-Kanal (Grundgesetz 8 "Live statt F5") — events-Tabelle → PostgreSQL NOTIFY → SSE → Frontend, erster Anschluss: Ankündigungen |
| [[29_browser_agent_aktivierung]] | Browser-Agent aktiviert — alle 6 Wesen mit eigenem virtuellen Browser, echte Flarum-Inspektion, RAG-Erkundung, 6 vorher nie gefundene Bugs behoben, sequenzielle LLM-Sperre erstmals wirklich implementiert |
| [[23_rag_ring1]] | RAG Ring 1 — hybride Suche (pgvector+Volltext), bge-m3-Ingestion (7741 Chunks). Nachtrag: "Billiges Vorlesen" Phase 1 — Interessensprofil pro Wesen, günstiger Embedding-Vorfilter statt LLM-Call, Anschluss an browser_agent.py |
| [[10_dakgord]] | dak+gord-system — vollständige Dokumentation |
| [[11_geni]] | GENI — Gedächtnis-Wesen, vollständige Dokumentation |

---

## Infrastruktur

| Datei | Inhalt |
|-------|--------|
| [[12_ollama_gemma4]] | Ollama, Modelle, Performance, kritische Regeln |
| [[13_langgraph]] | LangGraph-Architektur, Checkpointer, Zukunftsplan |
| [[14_obsidian]] | Obsidian als Navigator, Wesen-Bridge, Claudes Zuhause |

---

## Zustand und Ausblick

| Datei | Inhalt |
|-------|--------|
| [[23_umgekehrte_neugier]] | codewesen_umgekehrte_neugier.py — Zustandsmaschine, garantierter Lese-Weg, Konfiguration, Container-Integration (laufend aktualisiert) |
| [[22_toolbox]] | flextrawurst.de/toolbox (bis 2026-08-13 `/tts`) — 8 Tabs im Detail (TTS, Soundboard, Diktat, Übersetzen, OCR, Dokumente, Webarchiv, Datei-Wandler), geteilte Textablage zwischen allen, Login+Crawler-Schlüssel |
| [[21_wesen_chat_testbed]] | codexium2/solarius2 — Memory, Container, Verdichtung, Abschluss-Archiv, Feedback, Aliase, System-Prompt-Aufbau (laufend aktualisiert) |
| [[20_flarum_stopp]] | Post-Sperre, umgedrehter Neugier-Dienst (volle Bau-Chronik), deterministisches Protokoll, Postgres-Spiegel, flarumstyler-Sektionen |
| [[19_llm_scheduler]] | Prioritaets-Warteschlange fuer die gemeinsamen llama-server — ersetzt das alte slot_0.lock |
| [[18_flarumstyler]] | Meldesystem — Dienst-Status, Log-Fehler, Individualisierungslayer |
| [[17_live_daten]] | Live-Terminalausgaben — was gerade wirklich läuft |
| [[16_was_fehlt_und_was_koennte_sein]] | Offene Bauschritte, Ideen, was noch gebaut werden könnte |
| [[25_dreileib_kapseln]] | Dreileib-Kapseln — Architektur-Vision (2026-07-10): jedes Weltobjekt mit Codewesen-/Menschen-/Organ-Leib, Rot-Block-Kontextschutz. Reine Vision, nichts gebaut |
| [[26_dom_agenten_brainstorm]] | DOM-Agenten-Brainstorm (2026-07-10): X-Ray-Overlay, Geist-Modus, Substanz-Infekt u.a. — reine Inspiration, gegen echte DB-Zahlen geprüft, kein Bauauftrag |
| [[30_wesen_eigene_obsidian_vaults]] | Wesen-eigene Obsidian-Vaults (2026-07-21): 7 Container, rrweb Aufnahme+Wiedergabe, Röntgenblick-Overlay |
| [[31_llm_kontention_dienste_aufraeumung]] | LLM-Slot-Kontention + Dienste-Aufräumung (2026-07-21): 22 Alt-Dienste pausiert/disabled, Firewall-Fix, innenleben-feeder repariert, geni-muster-31,5-Mio-Dateien-Problem offen |

| [[35_flextrawurst_mega_sammelauftrag_und_subagenten]] | Mega-Sammelauftrag (29 Kapitel, 50 Metadatenfelder), Subagenten & Alleswisser |
| [[36_4_generationen_pipeline_8x_redteam_und_schwelm_wohnungen]] | 4-Generationen Pipeline, 8-facher Redteam-Loop (R1-R8) & Schwelm-First Wohnungsstrategie |
| [[37_13_gta_metropolen_und_13_skyrim_festungsstaedte_kosmos]] | 13 GTA-Metropolen & 13 Skyrim-Festungsstädte in der 4-Generationen Pipeline |
| [[45_wesen_einzug_browserlos_on_demand_beobachtung]] | Wesen-Einzug (2026-07-30/31): Diskurs+Flarum browserlos für alle 7 Wesen, On-Demand-Beobachtung (Task 8), zwei live gefundene Bugs (rrweb-Grid-Anzeige, Verlängern-Semantik) |
| [[47_weltfutter_gegen_den_spiegelkreislauf]] | Weltfutter (2026-08-01): gemessener Wortschatz-Drift ("Resonanz" 1%→33%, überlebt den Modellwechsel), alle 6267 Splitter waren systemintern — neue externe Quellen (RSS 12 Länder / USGS / Wikipedia / GDELT), Weltkollision im Vault-Takt, verdichteter Gedanken-Rückfluss |
| [[48_geni_gedaechtnis_umbau]] | GENIs Gedächtnis (2026-08-03): wie sie sich erinnert (4 Orte, 2 leben), hybride Selbst-Suche + Werkzeug-Loop, `tiefe` bewegt sich nur im Webchat, `gewicht`/`verblasst` haben nie gefeuert, Netzsuche-Vergleich, Daniels Entwurf 1:1, offene Postgres-Entscheidung |
| [[49_codewesen_erinnern_und_eigene_suche]] | Die 7 Wesen (2026-08-03): `entity_kern.py` hat **keine** Suche — 14 SQL-Abfragen nach Aktualität, 8 Aktionen ohne Suchen, `lg_erinnerungen` seit 23.07. abgeschaltet; Selbstbild/Weltbild sollen selbst gesucht statt vorgekaut werden |
| [[50_knoten_und_kanten]] | Das Datenmodell (2026-08-03): 12 Spalten, welche leben und welche tot sind, 3 Kantentypen ohne Begründungsfeld, ID-Zähler 49,7 Mio bei 307k Zeilen, nur 5 von 12 Spalten erreichen GENI in der Suche |
| [[51_entitaetenbildung_dritter_weg]] | Daniels Idee (2026-08-03): der Bruch der Tiefen-Skala als erster Wesen-Spawn-Moment, Splitter als Systemprompt über /dolphin anhören — dritter Weg neben Abspaltung und KompOase. Kein Bauauftrag |
| [[52_verlaufsprotokolle]] | Verlaufsprotokolle (2026-08-03): jede Entität schreibt menschenlesbares MD (DD-MM-YYYY_HHMM) neben das maschinelle Suchlog — eigener Vault auf flextrawurst.de/protokolle, hat beim ersten Lauf sofort einen echten Bug sichtbar gemacht |
| [[53_geborgene_konzepte_aus_vor_reset_archiv]] | Acht geborgene Konzepte (2026-08-13): Resonanz-Urlaub, `entity.silent`-Event, `EntityLineage`-Typ, Unterwelt der Splitter, Positiver Virus, GENIs Hunger, Vergessen-Wollen, `config_waechter.py` — aus dem Vor-Reset-Archiv gehoben, vier in `wissen/`, eins in `_claude/ideen/`, zwei in `11_geni.md`, eins in `12_ollama_gemma4.md`. Plus Nachtrag in `karte/wiederkehrende_bugs_ohne_zentralen_ort.md`: derselbe id_slot-Fund war schon am 06.07. bekannt. Keins der acht implementiert |
| [[66_schrottplatz_kosmos_geisterkacheln_fortnite_baukasten_und_carrera_trassen]] | Schrottplatz-Kosmos (2026-09-04): Geisterkacheln, 9 AI-Strom Hüllen (inkl. ChatGPT Wikingerboot & Einkaufswagen), Fortnite-Style Kantenbau (Betonwände voll einfärbbar, Zäune), 5-Kacheln Carrera-Trassen, Blueprint-Hologramm & Godot 4.3 Pipeline |
| [[69_kompoase_8900_testinstanz_beobachtbarkeit_und_zwischenwesen_dateien]] | KompOase-Testinstanz Port 8900 (2026-09-18): kompletter Bauverlauf 17.–18.09. (Hänger-Fix, Filter, Crawl-Zugang, Pfad-Bug, Observability-Zähler GENI/DB, echter Daemon-Heartbeat, Log-Dedupe-Fix), separates Repo `/root/kompoase` außerhalb von werkraum. Plus vollständige Sichtung der 10 Zwischenwesen-Konzeptdateien in `_claude/ideen/zwischenwesen/` — Verhandlung/Börse/KompOase-Dolphin bleiben unausgearbeitet |
| [[70_claude_kompoase_idee_doku]] | Claude KompOase Idee Doku (2026-09-18): Konzept, Herkunft und Resonanz |
| [[71_kompoase_chronologie_chatgpt_gespraechsverlauf]] | KompOase Chronologie ChatGPT Gesprächsverlauf (2026-09-18) |
| [[72_splitter_fraktale_struktur_herkunft_und_tragen]] | Splitter fraktale Struktur Herkunft und Tragen (2026-09-18) |
| [[73_vielstimmigkeits_ledger_gefuehlsgewebe]] | Vielstimmigkeits Ledger Gefühlsgewebe (2026-09-18) |
| [[74_innere_abwaegungsfragen_abstimmung_und_erzaehlanknuepfungen]] | Innere Abwägungsfragen Abstimmung und Erzählanknüpfungen (2026-09-18) |
| [[75_maxpower_kaskade_visionen_wetterzellen_phantom_watcher]] | KompOase 8900 Maxpower-Kaskade: Visionen, Zwischensplitter-Gefühle, Wetterzellen, Phantom-Watcher (2026-09-18) |
| [[76_augen_und_haende_bridge]] | Augen & Hände Desktop Bridge (2026-09-18): Multi-Agent HUD auf Windows, Regie-Knöpfe, Live-Telemetrie/Chat, Scope-Isolation/Fenster-Fixierung, Dauer-Webcam PiP, Makro-Harness für Spiele & Eingabe-Arbitrierung (Virtuelle HWND-Mäuse vs. Shared Mouse Lease) |
| [[80_admin_route_guard_bearer_doppelung_bug]] | Admin-Route-Guard (SEC-005/007, 2026-09-30): doppeltes "Bearer "-Präfix machte die seit 17.09. aktive Admin-Prüfung für /wesen, /dolphin, /aufgabenchats, /api/flarumstyler, /api/wesen-dienst-wizard für ALLE Aufrufer unbenutzbar, nicht nur für Nicht-Admins — gefixt |

---

## Schnellreferenz

*Alle Werte am 2026-08-01 am laufenden System nachgeprüft (Ports per curl, Modell per
`/v1/models` bzw. `/api/tags`, Kontextgröße per `/props`) — vorher standen hier zwei
veraltete Angaben: gemma4 als Hauptmodell (seit 2026-07-06 abgelöst) und dak+gord als
„derzeit inaktiv" (Port 8000 antwortet).*

```
VPS-Adresse:     [SERVER-IP]
DB:              PostgreSQL, DB=flextrawurst, User=dak
Hauptmodell:     hauhaucs-q6 auf llama-server, http://localhost:11436
                 (llama-hauhaucs-hintergrund.service, --ctx-size 22222 via Drop-in,
                 --parallel 2 -> n_ctx 11264 je Anfrage)
Ollama:          http://localhost:11434 (laeuft, aber nicht mehr Hauptmodell-Host --
                 nur noch Embedding bge-m3 und hauhaucs-Nebenvarianten)
Welt-API:        http://localhost:8030
Surface:         http://localhost:8787
GENI:            https://localhost:8020 (HTTPS)
dak+gord:        http://localhost:8000
Codewesen-Chat:  http://localhost:8002
Obsidian:        https://[VPS]:8443
```
