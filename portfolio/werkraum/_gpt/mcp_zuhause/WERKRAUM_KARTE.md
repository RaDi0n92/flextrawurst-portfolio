# Werkraum-Karte des VPS-MCP

## Technischer Kern

| Zweck | Pfad |
|---|---|
| Produktiver MCP-Server | `/root/werkraum/tools/vps_mcp/vps_mcp_server.py` |
| Parallelitätsvertrag | `/root/werkraum/tools/vps_mcp/mcp_concurrency.py` |
| Zuhause-Projektion | `/root/werkraum/tools/vps_mcp/mcp_home.py` |
| Append-only Hash-History | `/root/werkraum/_gpt/session_history.jsonl` |
| Atomischer Endanker | `/root/werkraum/_gpt/session_history.jsonl.checkpoint.json` |
| Globale MCP-Protokolle | `/root/werkraum/_gpt/mcp_global_protocols/` |
| Dieses Zuhause | `/root/werkraum/_gpt/mcp_zuhause/` |
| GPT-Spiegelraum | `/root/werkraum/_gpt/spiegel/` |
| Spiegel-Verfassung | `/root/werkraum/_gpt/mcp_zuhause/SPIEGEL_ANLEITUNG.md` |
| Globaler Gesamtatlas | `/root/werkraum/_gpt/gesamtatlas/` |
| Atlas-Pfadindex | `/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite` |
| Atlas-Begriffsindex | `/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite` |
| Atlas-Wurzelbriefregister | `/root/werkraum/_gpt/gesamtatlas/WURZELBRIEFE.json` |
| Atlas-Eingebungsprovenienz | `/root/werkraum/_gpt/gesamtatlas/EINGEBUNGSPROVENIENZ.jsonl` |
| Atlas-Beziehungsgraph | `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite` |
| Atlas-Projektrevisionen | `/root/werkraum/_gpt/gesamtatlas/PROJEKTREVISIONEN.json` |
| Atlas-Sessionübergaben | `/root/werkraum/_gpt/gesamtatlas/UEBERGABEREGISTER.json` |
| Atlas-AI-Strom-Brücken | `/root/werkraum/_gpt/gesamtatlas/AI_STROM_BRUECKEN.json` |
| Atlas-Timerquellen | `/root/werkraum/_gpt/gesamtatlas/systemd/` |

## Gespräch und Zeit

| Zweck | Pfad |
|---|---|
| UI-sichtbare Gesprächskörper | `/root/werkraum/_gpt/ui_visible_conversations/` |
| Globaler Zeitstromspeicher | `/root/werkraum/_gpt/time_stream/` |
| Neutraler MCP-Arbeitskörper | `/root/werkraum/_gpt/mcp_arbeitskoerper/` |
| Menschenlesbarer globaler MCP-Zeitstrom | `/root/werkraum/_gpt/mcp_arbeitskoerper/ZEITSTROM.md` |
| Globaler MCP-Zeitstromspiegel | `/root/werkraum/_gpt/mcp_arbeitskoerper/Zeitstrom/` |

## Zusammenarbeit und Zuständigkeit

| Zweck | Pfad |
|---|---|
| Globale MCP-Claims | `/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/claims/` |
| Globale MCP-Inboxen | `/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/inbox/` |
| Globale MCP-Sitzungsbelege | `/root/werkraum/_gpt/mcp_arbeitskoerper/sessions/` |
| Globale MCP-Validierungen | `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/` |
| Projektspezifische Claims und Belege | im jeweils ausdrücklich gewählten Projektkörper, niemals durch stillen Fallback |

## Andere AI-Strom-Zuhause als Referenz, nicht als eigene Erinnerung

- Claude: `/root/werkraum/_claude/`
- Codex: `/root/werkraum/_codex/`
- Kimi: `/root/werkraum/_kimi/`
- Gemini: `/root/werkraum/_gemini/`
- GLM: `/root/werkraum/_glm/`
- Grok: kein bestätigtes eigenes Zuhause; `/root/grok.md` bleibt als Dateinamen-/Inhaltsabweichung im Wurzelbriefregister sichtbar.

Diese Orte dürfen zur Herkunfts- und Strukturprüfung gelesen werden. Ihre Notizen sind nicht automatisch GPTs eigene Vergangenheit.
