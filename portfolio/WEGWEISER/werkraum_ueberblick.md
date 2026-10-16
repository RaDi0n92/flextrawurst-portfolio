# Wegweiser: `werkraum/` — der Hauptordner

3382 Dateien. Quelle: Dateinamen, Docstrings, READMEs. Keine Deutung.

## A. Python-Skripte direkt in `werkraum/` (Wurzel)

| Gruppe | Dateien | Zweck laut Docstring |
|---|---|---|
| Codewesen-Daemons | `codewesen_*.py`, `starte_alle_codewesen.py`, `gedaechtnis.py`, `weltbild_builder.py` | → `codewesen.md` |
| Flarum-Anbindung | `flarum_api.py`, `flarum_poster.py`, `flarum_monitor.py`, `flarum_post_sperre.py`, `flarum_stopp_protokoll*.py`, `flarum_vokabel_filter.py` | REST-Client, Poster mit Mutex/Draft, Event-Monitor, Post-Sperre-Schalter und Protokoll |
| LLM-Zugriff | `hauhau_client.py`, `llm_scheduler.py`, `simulation_llm_scheduler.py` | lokaler llama-server-Client, Prioritäts-Warteschlange |
| Konfiguration der Dienste | `dienst_konfiguration.py`, `wesen_eigene_dienste.py`, `wesen_dienst_generator.py`, `kollisions_scheduler.py`, `container_admin_cli.py` | Takte/Verhalten in der DB; Wesen-eigene Dienste |
| dak+gord | `starte_dak_gord.py`, `starte_dak_gord_system.py`, `chatte_dak_gord.py` | → `agent_pro_dakgord.md` |
| Obsidian | `obsidian_api.py` (Port 8060), `obsidian_vault.py`, `obsidian_queue.py` | Brücke zwischen Obsidian-Vault und Wesen |
| Betriebswächter | `systemweiser_app.py`/`_web.py`/`_status.py` (Port 8080), `watchdog_daemon.py` | "Betriebswächter, kein Lenker. Liest, berichtet, warnt" |
| Einmal-Skripte | `erstpost.py`, `namensfindung.py`, `einmal_d17_antwort.py`, `trigger_*.py`, `profilbild_antworten.py`, `reaktion_auf_dakgord.py` | einmalige Orchestrierungen (Erstvorstellung, Namensfindung …) |
| Simulationen/Tests | `simulation_umgekehrte_neugier*.py`, `qualitaetstest_umgekehrte_neugier.py` | Szenario- und Qualitätstests |
| Export/Fix-Skripte | `build_*_export*.py`, `fix_*.py`, `scan_encoding_guard.py`, `patch_*.py`, `apply_moellenkotten_*` | Konzept-Exporte, Encoding-Reparaturen, Patches |

## B. Ordner

| Ordner | Inhalt |
|---|---|
| `welt/` | → `welt_api_und_datenbank.md` |
| `innenleben/` | LangGraph + Selbstmodell → `codewesen.md`, Schicht 4 |
| `codewesen/`, `codeweisen/` | `wesen.md` je Wesen, `_global/grundhaltung.md` |
| `docs/` (221 Dateien) | Berichte/Entscheidungen 2026-07 ff.; `docs/systemdoku/` = nummerierte Betreiber-Doku (00–46: Architektur, Ports/Services, Welt-API, Surface, Flarum, Codewesen, LangGraph, RAG, LLM-Scheduler, Browser-Agent, Vaults …); `code_archaeologie_*.md` = Datei-für-Datei-Lernprotokolle |
| `wissen/` (112) | Wissens-Markdown: `beziehung`, `entitaeten`, `entscheidungen`, `entwicklungszeit`, `genealogie`, `plattform`, `profile`; `WISSEN_INDEX.md` |
| `projekt/` | `gesamtprojekt.md` (lebendes Projektgedächtnis), `vision1–5.md`, `nebenprojekte.md`, `konzeptideen/` |
| `reports/` | `API_CATALOG`, `SURFACE_VIEWS`, `SECURITY_MANIFEST_2026`, `FLEXTRAWURST_PRO_*`, `FIX_GUIDE_*` u. a. |
| `plan/`, `mission/`, `state/`, `decisions/`, `policies/`, `die-lösung/`, `outputsystem/`, `watchdog/` | einzelne Plan-/Entscheidungs-/Policy-Dateien (`MASTER_PLAN.md`, `AGREEMENTS.md`, `autonomy.json`, `0002-agent-governance.md` …) |
| `scripts/`, `tools/`, `tests/`, `app/`, `uploads/` | → `werkzeuge_audit_inventur.md` |
| `_claude/`, `_codex/`, `_gemini/`, `_gpt/`, `_kimi/`, `_glm/`, `_grok/`, `_haiku/`, `_opencode/`, `_claudeweb/`, `_Anthropic-Claude/`, `_shared/`, `_ops/`, `_ordnung/` | → `ai_stroeme_und_atlas.md` |
| `Programm harness+observingcontroller/`, `augen_haende_bridge/`, `Mein-Gesamtkonstrukt-planer/`, `DREIERREGEN/`, `ai_strom_bruecke/` | → `harness_bridge_planer.md` |
| `WorldWORDS-*`, `MCP-VPS-…`, `DOM-FLEXTRAWUST/`, `CLAUDE-NEUGIRIGER-REPORT/`, `MDtalk/`, `Meine-Textsammlung…`, `Agentpapers/`, `claudeweb_bau-megavault/`, `claude-systembericht/`, `codex-systembericht/`, `dolphin_mischpult/`, `refferenzen/` | → `antibibel_visionen_konzepte.md` |
| `Musik/`, `gemgems-spielbeobachtung/` | → `musik_und_spiele.md` |
| `flextrawurst-audit/`, `datei_wandler/`, `inventur/` | → `werkzeuge_audit_inventur.md` |

## Reihenfolge für jemanden, der von außen kommt

1. `README` der Repo-Wurzel, dann `00_START_HIER.md` (dieser Wegweiser-Ordner)
2. `projekt/gesamtprojekt.md` und `projekt/vision1.md` … `vision5.md` (was das Ganze sein will, laut Projektgedächtnis)
3. `docs/systemdoku/00_was_ist_flextrawurst.md` und `01_architektur_uebersicht.md`
4. `docs/systemdoku/03_ports_und_services.md` (welcher Dienst auf welchem Port)
5. dann je nach Interesse die anderen Wegweiser
