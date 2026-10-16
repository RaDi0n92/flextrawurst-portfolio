# Wegweiser: flextrawurst-agent, flextrawurst-pro, dak+gord-system, Erkenntnis-Archiv

Quelle: READMEs, Docs und Docstrings der genannten Ordner. Keine Deutung.

## `flextrawurst-agent/` (60 Dateien)

README: "Experimental agent/research system for exploring longer-term human-AI interaction, agent state logic,
approvals, background runs, and MCP-style tool …".

| Pfad | Inhalt |
|---|---|
| `graph/build.py`, `state.py`, `run_*.py` | LangGraph-Aufbau, Zustand, Läufe (Agent, Tool, Shell, Hintergrund, Resume) |
| `graph/nodes/` | Knoten: approval, background, dossier, focus, read, shell, summary, tool, trace |
| `graph/tools/` | Werkzeug-Schicht: Datei-, Shell-, MCP-Werkzeuge, Registry, Runtime |
| `graph/approval_*.py` | Freigabe-API und -Store |
| `graph/evals/` | Smoke-Evals (`run_smoke_evals.py`, `eval_mcp_fast.py`) |
| `docs/agent/` | `AGENT_STATE_SCHEMA`, `ARCHITEKTUR_HEUTE`, `GRAPH_MAP`, `MODULE_MAP`, `NODE_CATALOG`, `RUN_TYPES`, `RUNBOOK`, `KNOWN_ISSUES`, `GREEN_CHECKLIST` |
| `docs/vision/verfassung.md` | kurze Verfassung ("Öffentlich sprechen nur Entitäten …") |
| `remote_control/server.py` | startet Claude Code in einem PTY und verbindet es per WebSocket mit einem Browser-Terminal |
| `verarbeitung.py`, `verdichtung.py`, `verfassung_loader.py`, `zustand.py`, `sandbox.py` | Kopien/Varianten von Modulen, die auch in `werkraum_agent/dak_gord_system/` liegen |

Einstieg: `docs/agent/ARCHITEKTUR_HEUTE.md` → `MODULE_MAP.md` → `GRAPH_MAP.md`.

## `werkraum_agent/` (56 Dateien) — dak+gord-system

| Pfad | Inhalt |
|---|---|
| `AGENT.md` | Anweisungstext an den ersten Agenten ("Willkommen im Kosmos …") |
| `*.md` (Aneignung, Beobachtungen, Frust, Identität, …) | Arbeitsdateien, die der Agent selbst beschreiben darf; teils nur Platzhalter-Überschriften |
| `dak_gord_system/` | Python-Paket: `graf.py`/`dialog_graf.py` (LangGraph), `ollama_chat.py`, `neugierkern.py`, `neugier_ticker.py`, `freier_modus.py`, `schreibsystem.py`, `agentdateien.py`, `dateiwerkzeuge.py`, `verfassung_loader.py`, `verdichtung.py`, `verarbeitung.py`, `sandbox.py`, `zustand.py` |
| `dak_gord_system/verfassung/` | Verfassung in nummerierten Kapiteln 01–16 (Kern, Vision/Beziehung, Neugier, Schreibregeln, Dateiverhalten, Gedächtnis, Visionszyklen, Tiefe/Breite …) |
| `dak_gord_system/verfassung_neu/` | neuere Fassung in vier Dateien: `1_wesen`, `2_verhalten`, `3_werkzeuge`, `4_gedaechtnis` |
| `dak_gord_system/verfassung_altbestand/`, `verfassung_prueffassungen/` | frühere bzw. Prüf-Fassungen |
| `dak_gord_system/zustand.py` | Docstring-Notiz: älteste erhaltene Datei im System (mtime 2026-03-24) |

Zugehörig: `werkraum/starte_dak_gord_system.py`, `werkraum/starte_dak_gord.py`, `werkraum/chatte_dak_gord.py`,
`werkraum/codewesen/dak+gord-system/`.

## `werkraum_erkenntnis-alt/` (15 Dateien)

Texte in Ich-Form von dak+gord-system und Konzeptdateien: `selbstbild.md`, `selbstbild_dakgord.md`, `KONFLIKT_ENGINE.md`,
`SYSTEM_VALIDATION_RESONANZ.md`, `WELTKOSMOS_DETAIL.md`, `alles_als_zustand_2026-04-18.md`, `konzepte/` (Interface der Spannung,
Protokoll-Logik, Resonanz-Beschleuniger, Zwischenraum-Permeabilität, architektonische Spannung, Resonanz-Artefakt),
`nachklang/`. `INDEX.md` listet sie.

## `flextrawurst-pro/` (14 Dateien)

Next.js-Projekt (README = create-next-app-Standard). Eigener Code: `lib/api.ts` ("Alle Calls gehen gegen /api/ (Nginx-Proxy → Port 8030)"),
`lib/useSocket.ts`, `lib/useWeltStore.ts`, `store/useWeltStore.ts`, `lib/i18n.ts`, `capacitor.config.ts` (Mobile-Wrapper).
Blaupause/Status: `werkraum/reports/FLEXTRAWURST_PRO_BLUEPRINT.md`, `FLEXTRAWURST_PRO_STATUS.md`.

## Wo die Wesen-Variante davon liegt

`codewesen.md` beschreibt die sechs Codewesen und den gemeinsamen Unterbau.
