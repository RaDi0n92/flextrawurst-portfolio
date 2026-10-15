---
datum: 2026-07-31
betrifft: [gesamtatlas, ablagekonvention, durchsetzung, sicherheit, ai-stroeme]
importable: false
autor: claude-code bei Daniels VPS
---

# Gesamtatlas — AI_STROEME/-Ablagekonvention gebaut und technisch durchgesetzt

## Wo das herkommt

Direkter Anschluss an die Vokabular-Entschlackung. Daniel hat ein Gespräch mit ChatGPT geteilt,
in dem ChatGPT selbst einräumt: der Gesamtatlas ist ein exzellentes Such-/Erinnerungssystem
geworden, aber kein verbindliches Ablagesystem — kein Strom wusste beim Schreiben zuverlässig,
wohin genau. Daniels eigene, abschließende Formulierung: *"hier darum ging es mir seit
beginn...jeder aistrom muss am integration in gesamtatlass genau wissen wo ab sofort dinge hin
geschrieben werden."*

Ich habe den Befund selbst nachgeprüft, nicht nur ChatGPTs Selbstkritik geglaubt:
`werkraum_gesamtatlas_eingang/START_HIER.md` sortierte tatsächlich nur nach Inhaltstyp
(`DOKUMENTE/`, `IDEEN/`, `KONZEPTE/`, `REVIEWS/`, `AI_UEBERGABEN/`, `QUELLEN/`,
`00_UNSORTIERT/`) — nirgends nach Strom. Bestätigt, nicht nur behauptet.

## Was gebaut wurde

**1. Die Struktur.** `werkraum_gesamtatlas_eingang/AI_STROEME/<strom>/<kategorie>/` — neun
Ströme (`chatgpt`, `claude`, `codex`, `gemini`, `glm`, `kimi`, `claudeweb`, `grok`, `daniel`) ×
zwölf Kategorien (`eigene_texte`, `auftraege`, `entscheidungen`, `uebergaben`, `gespraeche`,
`arbeitsreste`, `konzepte`, `ideen`, `notizen`, `dokumentationen`, `reviews`, `beobachtungen`) =
108 Ordner, jeder mit eigener README.md-Erklärung (löst auch das Problem, dass Git leere
Verzeichnisse nicht trackt). Die letzten sechs Kategorien ersetzen die alten, strom-losen
Top-Level-Ordner. `START_HIER.md` entsprechend aktualisiert, dabei nebenbei eine übersehene
`## Wahrheitsgrenze`-Überschrift aus der vorherigen Vokabular-Runde nachgezogen (`## Einschraenkung`).

**2. Die Durchsetzung — `atlas.stream_file_write`.** Neues MCP-Werkzeug in `vps_mcp_server.py`.
Bewusstes Sicherheitsdesign, per Rückfrage bestätigt (neues eigenes Werkzeug statt Erweiterung
der bestehenden `vps.write_file`/`vps.edit_file`): das Werkzeug nimmt **weder einen Pfad noch
eine `stream_id`** entgegen. Der Zielordner wird ausschließlich aus dem server-eigenen,
vertrauenswürdigen Actor (`FLEXTRAWURST_ACTION_ACTOR`, derselbe Wert wie in der Action-History,
je Dienst über systemd-Environment gesetzt) abgeleitet — ein Strom kann sich technisch nicht als
anderer Strom ausgeben.

**Actor→Strom-Zuordnung** (sechs von neun Ordnern haben einen dedizierten, laufenden Dienst
dahinter — `glm`, `kimi`, `daniel` bisher ohne automatisches Routing, für sie bleibt nur die
manuelle Ablage):

| Actor | Strom |
|---|---|
| `GPT-5.6-sol-hoch` (Default) | `chatgpt` |
| `claude-code` | `claude` |
| `codex-cli` | `codex` |
| `gemini-cli` | `gemini` |
| `grok-check-in` | `grok` |
| `web-claude-check-in` | `claudeweb` |

## Verifikation — nicht nur behauptet, mehrfach getestet

Isoliert (Python-Import mit gesetztem `FLEXTRAWURST_ACTION_ACTOR`):
- Korrekter Aufruf (`claude-code`) → landete unter `AI_STROEME/claude/notizen/`.
- Unbekannte Kategorie → abgelehnt.
- Pfad-Traversal-Dateiname (`../../../etc/passwd`) → abgelehnt.
- Versteckte Datei (führender Punkt) → abgelehnt.
- Unbekannter Actor (simuliert `glm-unbekannt`) → abgelehnt mit klarer Fehlermeldung.
- **Der entscheidende Sicherheitstest:** `codex-cli` rief das Werkzeug mit `stream_id: "chatgpt"`
  auf, in der Absicht die eigene Identität vorzutäuschen — das Argument wurde komplett ignoriert,
  die Datei landete trotzdem korrekt unter `codex/`.

Danach live über den echten, gerade neu gestarteten `vps-mcp-claude.service` (Port 8092) per
direktem `curl`-Aufruf gegen `/mcp` bestätigt — nicht nur isoliert getestet, sondern der
tatsächlich laufende Produktionsdienst.

Alle sechs `vps-mcp-*`-Dienste neu gestartet (ChatGPTs eigener Dienst war zu diesem Zeitpunkt
seit ~4 Minuten inaktiv, bewusst kurz gewartet). Wieder derselbe, bereits mehrfach dokumentierte,
unabhängige `time_stream.py`-Race-Condition-Absturz bei `vps-mcp-claude.service` — selbstheilend,
inzwischen viermal beobachtet, weiterhin nicht Teil des heutigen Auftrags.

## Ehrlich offen

Die Durchsetzung gilt nur für dieses eine, neue Werkzeug. Wer stattdessen `vps.shell` (bekannte,
bewusst offen gelassene Pfadlücke, siehe `project_vps_mcp_ai_stroeme.md`) oder einen rohen
`vps.write_file`-Aufruf nutzt, kann die Konvention weiterhin technisch umgehen — das ist keine
lückenlose Durchsetzung, sondern ein bewusst einfacher, sauberer Weg, der als der vorgesehene
gilt. `glm`, `kimi` und `daniel` haben noch keinen dedizierten Dienst mit eigenem Actor-Wert,
also auch kein automatisches Routing über dieses Werkzeug — nur manuelle Ablage möglich.
