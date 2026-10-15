# Karte — was ich bisher tatsächlich geprüft habe

Stand: 2026-07-31. Nur Einträge, die ich selbst gelesen/verifiziert habe — nichts geraten
oder aus zweiter Hand übernommen. Wird bei Bedarf ergänzt, nicht vorab vollständig ausgedacht.

## Steuerdokumente anderer Agents (gelesen)
- `/root/AGENTS.md` — Codex- und Kimi-Startdokument. Beschreibt Session-Start-Leseliste,
  Spiegeldatei-Konventionen, die "heilige Abschnittsliste", Grundgesetze für flextrawurst
  selbst (API/DB-Konventionen unter "Grundgesetz 1-6"), Bau-Reihenfolge.
- `/root/CLAUDE.md` (43KB, 603 Zeilen) — existiert, Quelle für `AGENTS.md`. Nicht im Detail
  gelesen (gehört zur werkraum-nativen Claude-Session, nicht zu dieser Instanz).

## Andere Agent-Zuhause (Existenz geprüft, nicht tief gelesen)
- `/root/werkraum/_claude/` — werkraum-native Claude-Session. RESONANZFELD.md (235KB),
  abwuerfe.md (235KB), brief_an_mich.md (85KB), plus Unterordner analog zu `_codex/`.
- `/root/werkraum/_codex/` — Codex' Zuhause. RESONANZFELD.md (223KB), `abwuerfe.md`,
  `brief_an_mich.md`, `spiegel/`, `notizen/`, `_import_*_grundriss/`-Ordner für Claude/
  Claude-Web/GPT.
- `/root/werkraum/_kimi/` — analog, laut AGENTS.md mit eigenem Resonanzfeld.

## MCP-Server (gelesen, Quellcode)
- `/root/werkraum/tools/vps_mcp/vps_mcp_server.py` (5566 Zeilen) — der selbstgebaute
  MCP-Server, über den ChatGPT im Browser angebunden ist (130+ Tools). Schickt beim
  `initialize`-Handshake einen hart codierten Begrüßungstext im `instructions`-Feld,
  spezifisch für den erkannten Stream (`chatgpt` bekommt einen anderen Text als
  claude/codex/gemini).
- `/root/werkraum/tools/vps_mcp/mcp_atlas_auto_arrival.py` — liest beim `atlas.arrive`/
  `history_startup`-Aufruf: zwei Gate-Dateien unter
  `_gpt/gesamtatlas/omega/checkpoints/` (MCP_WORLD_READY.json, FINAL_SCAN_READY.json)
  und zwei START_HIER.md-Dateien unter `werkraum_gesamtatlas_eingang/`.

## Noch nicht geprüft
Alles andere im Baum (welt/, codewesen/, innenleben/, Gesamtatlas/Omega-Struktur im Detail,
_shared/, Obsidian-Vault-Inhalt) — bewusst nicht vorab zusammengefasst, um nichts zu behaupten
was nicht selbst gelesen wurde.

## Claude_Haiku — root's eigene SSH-Terminal-Persona (2026-08-23)

- Root's native Session (`/root`, gesteuert von `/root/CLAUDE.md`) läuft, wenn Daniel per SSH
  vom Windows-Terminal aus verbindet, unter dem gepinnten Modell `haiku`
  (`/root/.claude/settings.json`, bestätigt durch Daniel und durch das Modellfeld im eigenen
  Transkript: `"model":"claude-haiku-4-5-20251001"`). Auf Daniels Wunsch **"Claude_Haiku"**
  genannt — eigene Identität, nicht diese `/config`-Instanz, nicht root's ursprüngliche.
- **virtuellerdesktop1** (Browser-Container, Docker-Volume `webtop1_config`) hat dagegen kein
  Modell in seiner `settings.json` gepinnt → läuft auf dem CLI-Default (Sonnet 5).
- `/root/CLAUDE.md` bekam am 2026-08-23 einen eigenen, angehängten Abschnitt
  "Arbeitsweise — Claude_Haiku" (Subagenten-Pflicht, Skalpell-Signalwörter, Datei-Beweis vor
  Behauptung, Batch-Regel, Drei Stopp-Fragen, Provenienz-Prinzip, Backup & Git) — Herkunft
  AGENTS.md/GEMINI.md, bewusst NICHT als Spiegelung von `/config` gekennzeichnet (Daniel:
  "das sollst ja nicht du sein").

## Guardianstyle-Cleanup jetzt in Git gesichert (2026-08-23)

Der am 20.08. begonnene Rewrite von root's `/root/CLAUDE.md` (Guardianstyle-Abschnitt komplett
raus, mehrere Vorfalls-Erzählungen auf die operative Regel gekürzt — deckt sich mit root's
eigener "Absolute Fehler-Schweige-Regel") lag seither nur unkommitiert auf der Platte. Beim
Anhängen des Claude_Haiku-Abschnitts zufällig entdeckt und mit committet — kein neuer Eingriff,
nur der erste tatsächliche Git-Commit für eine bereits beschlossene Änderung.
