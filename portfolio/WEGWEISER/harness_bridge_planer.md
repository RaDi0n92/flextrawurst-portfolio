# Wegweiser: Harness, Observing Controller, Augen-&-Hände-Bridge, Dreierregen, Planer

Quelle: Dateinamen, READMEs, Kopfzeilen. Keine Deutung. Mehrere dieser Dokumente sind Gesprächsprotokolle mit ChatGPT.

## Programmharness + Observing Controller

| Pfad | Inhalt |
|---|---|
| `werkraum/Programm harness+observingcontroller/p1-plan.md` … `p8-plan.md` | acht Plan-Dokumente (Gesprächsauszüge). Überschriften u. a.: "Die wichtigste Trennung", "Die vier Ebenen deines Systems", "Die Zeitmaschine für Agenten", "Hände-Augen-Bridge", "Die Bridge bekommt drei Wahrheiten gleichzeitig" |
| `…/flextrawurst als betriebsystem p1-plan.md` u. a. | aus .odt extrahierte Fassungen |
| `…/Beobachtung-Abweichung-Agentenfeedback.md` | Beobachtung/Abweichung/Agentenfeedback |
| `…/README_desktopvisionGPT.md` | "Desktop-Sichtbarkeit für ChatGPT / VD1" (Stand 2026-09-19): bestätigter Weg, den virtuellen Desktop 1 über den Selkies-Livestream (Port 8882) zu sehen |
| `werkraum/_gpt/Programmharness+ObservingController/` | `DASHBOARD_SOLLBILD.md`, `DASHBOARD_CODECHECK.md`, `Agenten-im-Moment.md`, `Agenten-Scan-Analyse-2026-10-07.md`, `HARNESS_FIX_2026-10-06_CODEX_WEB.md`, `Programmharness-Observingcontroller-Zustand-Audit-2026-10-07.md` |
| `werkraum/Agentpapers/Agenten-Scan-Analyse-2026-10-07_vertieft.md` | vertiefte Analyse |
| `werkraum/_gpt/CHATGPT_HARNESS_ARBEITSCHRONIK.md`, `HARNESS_PFADINVENTUR_FIX_2026-10-04.md` | Arbeitschronik und Pfadinventur |
| `werkraum/tools/vps_mcp/` | MCP-Server mit Harness-Graphen (`mcp_action_graph.py`, `mcp_workflow_graph.py`, `mcp_delivery_graph.py`, `mcp_cognitive_graph.py`), `POSITIVE_HARNESSING_PRINCIPLE.md` |
| `flextrawurst-agent/` | LangGraph-Agent mit Freigaben/Hintergrundläufen → `agent_pro_dakgord.md` |

## Augen-&-Hände-Bridge (`werkraum/augen_haende_bridge/`, 442 Dateien)

`START_HIER.md`: "kanonischer gemeinsamer Arbeitsort für die Bridge", Quelle ist Daniels Wortlaut; maßgeblich
`bridge_docs/ANFORDERUNGEN.md` und `PLAN.md`. Im Paket liegen diese beiden unter `werkraum/docs/augen_haende_bridge/ANFORDERUNGEN.md` und `PLAN.md`.

| Pfad | Inhalt |
|---|---|
| `src/augen_haende_bridge/` | Haupt-Python-Paket |
| `client_vps/` | Dienste auf dem VPS (`bridge_server.py`, `bridge_agent.py`, `bridge_cli.py`, `terminal_launcher.py`, `ablauf_dienst.py`, `praxis_dienst.py` …) |
| `client_windows/` | Gegenstück für Windows |
| `skills/` | Skills `bridge-praxistest`, `skill-schreiben`, `web-seite-nachbauen` |
| `tests/`, `probes/`, `docs/`, `wiki/`, `BUILD_LOG.md`, `build_paket.sh` | Tests, Proben, Doku, Buildprotokoll |
| `_codex/augen-und-haende-bridge-2026-09-19/`, `_codex/CODEX_REVIEW_BRIDGE_SKILLS_PRAXIS_HARNESS_2026-10-02.md` | Codex-Dokumente dazu |
| `werkraum/ai_strom_bruecke/DOKUMENTATION.md` | frühere Brücke (Juli 2026) |

## Dreierregen (`werkraum/DREIERREGEN/`, 29 Dateien)

`00_START_HIER.md` (Frontmatter: typ startseite, erstellt 2026-07-26): `01_KERNVERTRAG.md`, `02_BEGRIFFE_UND_GRENZEN.md`,
`03_WELTKOERPER_MATRIX.md`, `04_ENTSCHEIDUNGSLOG.jsonl`, `05_OFFENE_ENTDECKUNGEN.md`, `06_BAUPROTOKOLL.md`,
`07_QUELLENKARTE.md`, `08_ZUSAMMENARBEIT_DER_AI_STROEME.md`, `09_ABNAHMEVERTRAG.md`, je Strom eine Datei (`CHATGPT.md`, `CLAUDE.md`,
`GEMINI.md`, `GROK.md`, `KIMI.md`), `AI_EINGAENGE/`, `BAUAUFTRAEGE/`, `BEWEISE/`.
Zugehörig: `werkraum/DOM-FLEXTRAWUST/` (Dreiergespann-Texte), `docs`-Verweis auf `dreiergespann_dom_theorie.md` in `_claude/ideen/`.

## Planer (`werkraum/Mein-Gesamtkonstrukt-planer/`, 164 Dateien)

README: "der reale, servergespeicherte Körper des Planers"; `data/current.json` = einziger autoritativer Arbeitsstand
(Browser-Speicher nur Cache; die Datei selbst ist nicht im Paket, `data/` enthält Advisory-Dokumente und `tree/`). `server/` mit `planner_api.py`, `goal_api.py`, `run_api.py`, `real_fs_api.py`, `world_state.py`,
`planner_events_stream.py` und Tests; `deploy/`; Verlauf in `GESAMTKONSTRUKTPLANER_VERLAUF_CHANGELOG.md`.
Hinweis: Ob die Planer-API Authentifizierung erzwingt, ist nicht geprüft.
