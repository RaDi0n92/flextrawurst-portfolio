---
datum: 2026-10-04
betrifft: [lernschleife, claude-code-hooks, postgresql, langgraph]
importable: false
autor: claude-code bei Daniels VPS
---

# Claude-Lernschleife

Neu im System: ein Lernmechanismus nur für Claude in Claude Code, unter `/config/.claude/erfahrung/`
(auf dem Server `/var/lib/docker/volumes/webtop1_config/_data/.claude/erfahrung/`).

Eigener PostgreSQL-Cluster (Datenbank `erfahrung`, Socket `pgdata`), nicht der Bridge-Speicher, nicht flextrawurst.
Ein LangGraph mit sieben Knoten (`lernschleife.py`) läuft im Venv `/root/bridge_speicher/venv`.
Hooks: Halt-Block bei Fehlschlag, Korrekturerkennung, Stop-Verifier mit zwei Wiederholungen, Einspeisen der Regeln.

Die Hooks stehen erst nach `python3 /root/eh2.py` in `/config/.claude/settings.json`.
Claude Code sperrt Änderungen an den eigenen Settings als Self-Modification, die macht Daniel.

Eine Ansicht des Stands erzeugt `ansicht.py` (`ansicht.html`). Details: `docs/systemdoku/83_claude_lernschleife.md`.
