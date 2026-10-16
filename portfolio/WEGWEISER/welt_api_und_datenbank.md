# Wegweiser: `werkraum/welt/` — Welt-API, Datenbank, Daemons

Quelle aller Angaben: Docstrings und Dateinamen in `werkraum/welt/` (117 Dateien). Keine Deutung.

## Kern

| Datei | Laut Docstring |
|---|---|
| `api.py` | "Welt-API: FastAPI auf Port 8030." Sehr große Datei (~16.000 Zeilen); "Neue Endpunkte in Sub-Router auslagern" |
| `auth.py` | bcrypt + JWT für das Menschenprofil-System |
| `db_runtime.py` | fail-closed DB-Laufzeitkonfiguration |
| `bruecke.py` | liest Selbstmodell-JSONs und synchronisiert mit PostgreSQL |
| `schema*.sql`, `migration*.sql`, `migrate_*.sql` | Tabellenschemas (Welt, Menschen, Resonanz, Entitätenschichten, Gedankenwelt, Traum, RAG, Gruppen, LLM-Warteschlange, Dienst-Konfiguration, Substanzen …) und Migrationen |

## Sub-Router, die `api.py` einbindet (je eine Datei)

`denkstream_api` (SSE-Stream des Denkens je Wesen), `events_stream_api` (generischer Live-Kanal, "Live statt F5"),
`dom_events_api` (rrweb-Live-Spiegel), `fokus_events_api` (Röntgenblick-Overlay), `rag_api`, `groups_api`,
`reibungsgewebe_api`, `erlebnis_api`, `fragen_api`, `beobachtung_api`, `admin_einsicht_api`, `wesen_dateien_api`.

## Wesen-Denken und Schlaf

| Datei | Laut Docstring |
|---|---|
| `entity_kern.py` | LLM-Kern für alle Wesen; Entscheidung + Gedanke in `entity_thinking_log`; eigener Dienst seit mind. 2026-07-06 deaktiviert, Funktionen laufen als Bibliothek unter `werkraum/codewesen_lg_daemon.py` weiter |
| `entity_takt.py` | Entscheidungsloop; Schlaf ist eine der wählbaren Aktionen |
| `cyberling_daemon.py` | Bedürfnisse (Durst, Hunger, Energie, Stimmung), Tod und Wiedergeburt der Cyberlinge; `cyberling_balancing/` = reine Simulationen |
| `traum_skeleton.py`, `traum_llm.py`, `traum_generator.py`, `traum_luzid.py`, `traum_integrator*.py` | Traumprozess: regelbasierte Vorauswahl → Verdichtung → Traumtext → "luzider" Beobachter → Integration (Einzel-Freigabe, Dry-Run) |
| `wesen_life_contracts.py`, `wesen_organ_hunger.py` | Taxonomie der Erfahrungsräume ("Lebensverträge") und Organhunger (erzeugt Prüfanlässe, keine Fake-Events) |
| `projection_dry_run.py`, `projection_writer.py` | Selbstmodell-Projektion in `entity_profiles.meta` |
| `zweitgehirn.py` | "jede Facette der acht Wesen an einem Ort, live" |

## Zwischenraum / Splitter

`splitter_daemon.py` (3 Ticks alle 60 s), `tension_daemon.py` (alle 10 min, Tension + Sediment),
`similarity_daemon.py`, `themen_cluster.py`, `flarum_archiv_splitter.py`, `wesen_vault_splitter.py`,
`weltfutter.py` (echte Fremdkörper von außerhalb als Splitter), `reibung_bruecke.py` (Briefkasten → Reibungsgewebe).

## Beobachtung und Browser

`browser_agent.py` (ein Wesen navigiert; Docstring: später ersetzt durch "VOLLSTAENDIG_OHNE_BROWSER"),
`browser_agent_coordinator.py`, `on_demand_beobachtung.py`, `wesen_webbesucher.py`, `gen_*.py` (Generatoren für Denkstream-/Screens-HTML).

## Wesen-Vaults und Dienste

`obsidian_vault_agent.py`, `wesenvaultsystem_api.py` (Port 8097), `wesen_einzug_vault_*.py`, `wesen_lieder_agent.py`,
`wesen_dienst_*.py` (Brücken für den Node-Server), `vorlese_daemon.py`.

## Sicherheit / Betrieb

`service_*.py` (pro-Dienst Ed25519-Signierung, Tokens, Key-Verwaltung, "never imports the human JWT secret"),
`crawlkey_*.py` (Rotation von Crawl-Keys über Unix-Socket), `weltkern_watchdog.py` (prüft alle kritischen Services),
`tts_service.py` + `tts_*test*.py`, `llm_warteschlange_status.py`.

## Tests

`test_spurenfaehigkeit.py`, `test_wesen_spurenentscheidung.py` (laufen laut Docstring gegen die Live-DB).
