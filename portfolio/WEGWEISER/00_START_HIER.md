# Wegweiser — Start hier

Neutrale Dateiwegweiser durch das Portfolio-Paket. Sie sagen nur, **welche Datei was ist und womit sie zusammenhängt**,
und stützen sich auf Docstrings, Kopfzeilen und READMEs der Quelldateien selbst. Keine Bewertung, keine Einordnung —
die schreibt Daniel selbst.

Pfade sind relativ zur Paketwurzel (dem Ordner, der `werkraum/`, `zensi/`, `flextrawurst/` … enthält).
Nicht im Paket enthalten sind Laufzeitdaten (Datenbankinhalte, Wesen-Gedächtnisse, Logs, Secrets); Server-Zugangsdaten
und IPs sind geschwärzt (`[GESCHWAERZT]`, `[IP-GESCHWAERZT]` …).

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
