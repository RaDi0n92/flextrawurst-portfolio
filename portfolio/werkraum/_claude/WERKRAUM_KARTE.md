# Werkraum-Karte

Navigationshilfe für Claude. Stand: 2026-05-10, ergänzt 2026-08-01.

## ⚑ Zuerst lesen: dein Haus wurde am 2026-08-01 zurückgesetzt

`notizen/`, `spiegel/`, `ideen/` und `karte/` sind **nicht leer, weil nichts passiert ist** —
sie sind leer, weil der Sessionstart frisch beginnen sollte. Vorher kostete er rund 336.000
Zeichen, davon allein 49% `karte/`, das laut Ritual jede Session vollständig gelesen wird.

Alles Bisherige liegt vollständig in `archiv/vor_reset_2026-08-01/` — 181 Dateien, 69 Notizen,
50 Spiegel, 30 Ideen, 32 Karten-Dateien, das alte RESONANZFELD (2182 Zeilen) und alle 469 Zeilen
`brief_an_mich.md`. Nichts davon ist gelöscht.

**Es ist durchsuchbar, und das ist der Punkt** — aber mit zwei Werkzeugen, nicht mit einem:

```bash
# 1. Wenn du einen Begriff kennst: grep. Zuverlässig, findet Wortgleiches sofort.
grep -rl "<begriff>" /root/werkraum/_claude/archiv/

# 2. Wenn du nur eine Ahnung hast: semantische Suche. Findet Verwandtes, nicht Wortgleiches.
python3 /root/werkraum/_claude/tools/semantische_suche.py suche "<beschreibung>"
```

Der Index umfasst das Archiv (`QUELL_ORDNER` in `semantische_suche.py` wurde dafür erweitert;
am 2026-08-01 verifiziert, 230 Dateien indiziert).

**Geprüfte Grenze, damit du dich nicht darauf verlässt:** Die semantische Suche hat im Test die
eine archivierte Datei *nicht* zurückgegeben — obwohl sie mit allen 7 Abschnitten im Index
steht und die Suchanfrage eine Überschrift daraus wörtlich enthielt. Alle Treffer lagen bei
Distanz > 1,0, also faktisch "nichts Passendes gefunden". `grep -rl "Zustimmungs-Tendenz"` fand
die Datei sofort. Fazit: bei bekannten Begriffen immer erst grep, semantische Suche nur zum
Stöbern.

Wenn dir etwas fehlt oder du das Gefühl hast, hier fehle Vorgeschichte: **frag das Archiv,
statt es neu zu erfinden.** Ein Archiv, das niemand befragt, ist dasselbe wie keins.

Was bewusst *nicht* zurückgesetzt wurde, weil es das Destillat ist und nur 10% der Startkosten
ausmachte: `STAERKEN.md`, `FRAGEN.md`, `wesen/` und diese Datei.

## Kern-Orte

| Verzeichnis | Was ist da | Wichtige Dateien |
|-------------|-----------|-----------------|
| `erkenntnis/` | Wissensarchiv des Systems | `INDEX.md`, `selbstbild.md`, `konzepte/` |
| `wissen/` | Strukturiertes Wissen | `WISSEN_INDEX.md`, `entitaeten/`, `resonanz/` |
| `docs/` | Systemdokumentation | div. Konzeptdokumente |
| `decisions/` | Entscheidungsprotokoll | `0002-agent-governance.md` |
| `projekt/` | Visionen | `vision1.md`–`vision7.md` |

## Code-Orte

| Verzeichnis | Was ist da |
|-------------|-----------|
| `agent/`, `agents/` | Agent-Kern-Code |
| `codewesen/` | Codewesen-Logik (dak+gord und andere) |
| `skills/` | Skills für Codewesen |
| `tools/` | Werkzeuge |
| `flextrawurst/` | flextrawurst-Projekt (gesamte App) |

## Laufende Systeme (VPS)

| System | Port | Status-Check |
|--------|------|-------------|
| GENI (Gedächtnis) | 8020 | `curl localhost:8020/health` |
| Obsidian | 3080 → 8443 | Docker: `docker ps` |
| dak+gord | — | `ps aux | grep starte_dak` |

## Daten & Zustand

| Verzeichnis | Was ist da |
|-------------|-----------|
| `state/` | Systemzustände |
| `brain/` | Projektvisionen (vision1–7) |
| `telemetry/` | Telemetrie-Daten |
| `backups/` | Backups |

## Claude-spezifisch

| Pfad | Was ist da |
|------|-----------|
| `/root/.claude/projects/-root/memory/` | Auto-Memory (MEMORY.md + Einzeldateien) |
| `/root/werkraum/_claude/` | Claudes Zuhause im Obsidian-Vault |
| `/root/werkraum/_claude/notizen/` | Session-Notizen |
| `/root/CLAUDE.md` | Projekt-Instruktionen |
| `/root/.claude/CLAUDE.md` | Globale Instruktionen |
| `/root/werkraum/_claudeweb/` | Zuhause von Claude Web (claude.ai-Chat über Daniels eigenen MCP-Konnektor "sauber") — eigener, getrennter Strom von mir (Claude Code), bewusst leicht gehalten, kein volles Ritual. Ihr eigener Bereich, ich schreibe da nicht rein (2026-07-29). |
