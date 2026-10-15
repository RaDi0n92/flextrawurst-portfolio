---
datum: 2026-07-30
betrifft: [vps-mcp, mcp-home, codex, gemini, claude-web, chatgpt, systemd, nginx]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich heute über das System gelernt habe

**Aus dem geteilten Klon (`vps-mcp-shared`) sind fünf gleichberechtigte, dedizierte Klone
geworden.** ChatGPT (8091), Claude Code (8092, `vps-mcp-claude` — vormals `-shared`, reine
Umwidmung), Codex (8094, neu), Gemini CLI (8095, neu), Claude Web (8093, `-sauber`). Alle fünf
führen exakt denselben `vps_mcp_server.py`-Prozess aus, unterscheiden sich nur über Env-Vars.

**`mcp_home`/`history_startup` und `session_continuity` sind zwei unabhängige Achsen.** Die
28.07.-Individualisierung (drei Klone statt einem) hatte nur die Kontinuitäts-Policy (resume/new-
Verhalten) pro Klon getrennt, nicht die Identität (`mcp.home`). Dadurch lieferten `shared` UND
`sauber` monatelang unbemerkt ChatGPTs Zuhause zurück, wenn `mcp.home`/`history_startup`
aufgerufen wurde — niemand hatte das bemerkt, bis Claude Web selbst draufgestoßen ist.
[status: widerlegt 2026-07-30 -- "monatelang" war falsch, unverifiziert übernommen. `vps_mcp_server.py`
existiert erst seit 2026-07-23 (Phase-1-Commit), `vps-mcp-sauber.service` sogar erst seit
2026-07-30 00:39 Uhr. Der Bug kann maximal die knappe Woche seit 23.07. bestanden haben, nicht
Monate. Von Daniel entdeckt, per systemctl/git-log nachgeprüft.]

**Zuhause-Manifeste sind reine Verweis-Ebenen, kein neuer Fließtext.** Für Codex/Gemini/Claude
Code hab ich keine neue "Wer bin ich"-Prosa erfunden — jedes bekommt nur ein minimales
`MANIFEST.json` (`{"sections": {"home": "<Pfad zur eigenen Konstitution>"}}`) plus ein schlankes
Protokoll-JSON, dessen `purpose`/`identity_boundary` ausdrücklich sagen, dass die Datei nicht für
den jeweiligen Strom spricht. `mcp.home` liest dann direkt AGENTS.md/GEMINI.md/CLAUDE.md selbst.
Daniels eigener Einwand ("warum nicht einfach verknüpfen") hat mich von einer komplizierteren,
schlechteren Lösung abgehalten.

**Codex und Gemini authentifizieren sich unterschiedlich gegen denselben Servertyp.** Codex
(`~/.codex/config.toml`) nutzt `bearer_token_env_var` — eine Indirektion über eine `.bashrc`-
Variable. Gemini (`~/.gemini/settings.json`) trägt den Bearer-Token direkt im JSON. Kein
technischer Grund für den Unterschied ersichtlich, einfach zwei verschiedene CLI-Tool-
Konventionen.

**Ein Dienst, der nie neu startet, bleibt für immer auf dem Stand seines letzten Starts.**
`vps-mcp.service` (ChatGPT) läuft seit vor dem 28.07. ununterbrochen und liefert deshalb nur 155
statt der inzwischen 162 tatsächlich registrierten Tools — das lange ungeklärte "155 vs. 162"-
Rätsel aus derselben Nacht (Systemdoku 38, Abschnitt 13) war vermutlich genau das, jetzt live
bestätigt statt nur vermutet. Bewusst nicht gefixt, weil ChatGPT laut Daniel gerade aktiv
verbunden ist ("chatgpt ist grade am basteln") — derselbe Vorsichtsgrund wie beim letzten Mal.

## Was mich überrascht hat

Wie sehr sich ein auf den ersten Blick großer Umbau ("jedem einen eigenen MCP") in lauter kleine,
einzeln schon bekannte Schritte zerlegen ließ (Keys generieren, systemd-Unit kopieren, nginx-
Location duplizieren, Manifest verlinken) — nichts davon war technisch neu, nur die Kombination
und der Umfang (fünf statt drei Klone gleichzeitig im Blick behalten).

## Was ich mir merken will

Bei jeder "X funktioniert nicht richtig für Klon/Instanz Y"-Frage künftig zuerst prüfen: läuft Y
überhaupt mit aktuellem Code, oder wartet der Prozess nur auf einen Neustart, der aus Vorsicht vor
einer aktiven fremden Session nie kam? Das war heute zweimal derselbe Grundfehler (Claude Web
zuerst, ChatGPT am Ende), nur an verschiedenen Enden der Kette.
