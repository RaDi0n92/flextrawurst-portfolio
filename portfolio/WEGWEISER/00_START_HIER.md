# Wegweiser — Start hier

Neutrale Dateiwegweiser durch das Portfolio-Paket. Sie sagen nur, **welche Datei was ist und womit sie zusammenhängt**,
und stützen sich auf Docstrings, Kopfzeilen und READMEs der Quelldateien selbst. Keine Bewertung, keine Einordnung —
die schreibt Daniel selbst.

Pfade sind relativ zur Paketwurzel (dem Ordner, der `werkraum/`, `zensi/`, `flextrawurst/` … enthält).
Nicht im Paket enthalten sind Laufzeitdaten (Datenbankinhalte, Wesen-Gedächtnisse, Logs, Secrets); Server-Zugangsdaten
und IPs sind geschwärzt (`[GESCHWAERZT]`, `[IP-GESCHWAERZT]` …).

## Neu: wo liegt was, und was wurde versucht? / New: where is what, and what was attempted?

| Frage / Question | Datei / File |
|---|---|
| Wie ist das alles entstanden, wer arbeitet wie? / How did all this come about, who works how? | `../ARBEITSWEISE.md` (DE/EN) |
| Was gab es vor Flextrawurst, in welcher Reihenfolge? / What existed before Flextrawurst, in what order? | `../VOR_FLEXTRAWURST.md` (DE/EN) |
| Was hat Daniel wann mit ChatGPT besprochen und geplant? / What did Daniel discuss and plan with ChatGPT, and when? | `../CHATGPT_ERINNERUNGSBERICHT_2026-10-17.md` (Bericht von ChatGPT, unverändert / ChatGPT's own report, unchanged) |
| Wie erinnert Daniel den Weg vom Systemweiser zum Programmharness? / How does Daniel recall the path from Systemweiser to program harness? | `../DANIEL_ROHTEXT_2026-10-18_VOM_SYSTEMWEISER_ZUM_PROGRAMMHARNESS.md` (Daniels Rohtext, unverändert / Daniel's raw text, unchanged) |
| Wo liegen Spiegel, Notizen, Ideen, Konzepte, Doku, Wissen, Code? / Where are mirrors, notes, ideas, concepts, docs, knowledge, code? | `../INHALT_ORT_FUER_ORT.md` (DE/EN) |
| Was liegt im Zuhause von Claude Code, Codex, Gemini, Kimi, ChatGPT …? / What is in the home of each AI stream? | `../HEIMAT_ORDNER.md` (DE/EN) |
| Was wurde in den Projekten versucht, warum, welche Dateien gehören dazu? / What was attempted in the projects, why, which files belong to them? | `../PROJEKTE/README.md` (DE/EN) |

Die Wegweiser unten bleiben technische Dateiwegweiser (nur Deutsch). / The guides below remain technical file guides (German only).

## Welcher Wegweiser für welche Frage

| Frage | Wegweiser |
|---|---|
| Wie ist ein Codewesen aufgebaut (Selbstbild, Gedächtnis, RAG, LangGraph, Takt)? | `codewesen.md` |
| Was ist die Welt-API / Datenbank / Schlaf, Träume, Cyberlinge, Splitter? | `welt_api_und_datenbank.md` |
| Was ist die Surface / der Weltkern / die "Ringe"? | `flextrawurst_surface_und_kern.md` |
| Was sind flextrawurst-agent, flextrawurst-pro, dak+gord-system, Erkenntnis-Archiv? | `agent_pro_dakgord.md` |
| Was ist zensi? Was ist GENI? | `zensi_und_geni.md` |
| Wo liegt der Rest von `werkraum/` (Skripte, Dienste, Docs)? | `werkraum_ueberblick.md` |
| Was sind die AI-Ströme (_claude, _codex, _gemini, _gpt …), Briefkasten, Brücke, Atlas? | `ai_stroeme_und_atlas.md` |
| Harness, Observing Controller, Augen-&-Hände-Bridge, Dreierregen, Planer | `harness_bridge_planer.md` |
| WorldWORDS ANTIBIBEL, Visionen, Textsammlung, Konzepte | `antibibel_visionen_konzepte.md` |
| Musik, Lieder, Spiele-Beobachtung | `musik_und_spiele.md` |
| Audit, Werkzeuge, Tests, Inventur | `werkzeuge_audit_inventur.md` |

## Die Top-Level-Ordner des Pakets

| Ordner | Dateien | Kurzbeschreibung laut eigenem README/Docstring |
|---|---:|---|
| `werkraum/` | 3382 | Hauptordner: Daemons, Wesen, Docs, AI-Ströme, Nebenprojekte |
| `flextrawurst/` | 262 | TypeScript-Weltkern ("Ringe"), Surface-Builder, Tests, Docs 00–43 |
| `flextrawurst-agent/` | 60 | LangGraph-Agent-/Forschungssystem (Zustände, Freigaben, Hintergrundläufe, MCP-Werkzeuge) |
| `flextrawurst-pro/` | 14 | Next.js-Frontend (Client gegen Welt-API Port 8030) |
| `werkraum_agent/` | 56 | dak+gord-system: Agent-Dateien, Verfassung, Python-Paket `dak_gord_system/` |
| `werkraum_erkenntnis-alt/` | 15 | Erkenntnis-Archiv (Selbstbild, Konflikt-Engine, Konzepte) |
| `werkraum_geni/` | 43 | GENI-System |
| `werkraum_gesamtatlas_eingang/` | 129 | Abgabestelle je AI-Strom für den Gesamtatlas |
| `zensi/` | 18 | Chat-/Sandbox-System "zensi" mit Server, Daemons, Tests |
| `inventur/` | 36 | Ist-Zustand-Beschreibungen der Surface-Tabs (28 Tab-Dateien) |
| `kompoase/` | 1 | `server.py` |
| `flarum_exporter/` | 1 | `flarum_export.py` (Read-only-Export des Flarum-Forums) |
| `visionen/` | 2 | Vision-Bild + Notiz |

## Konventionen, die in den Quellen immer wieder auftauchen

- **Wesen:** Codewesen = die sechs `namelessAI_*`-Wesen (heute mit eigenen Namen) + dak+gord-system = sieben.
- **Flarum:** das ursprüngliche Forum, in dem die Wesen zuerst "lebten"; viele Dateien tragen noch `flarum_`.
- **Welt-API / Port 8030, Surface / Port 8787, Chat / Port 8002:** laut Docstrings.
- **Datumsangaben** in Dateinamen und Docstrings beziehen sich auf 2026.
- **Wegweiser statt Gesamtindex:** die vollständige Dateiliste steht im ZIP selbst bzw. in den Ordnern.
