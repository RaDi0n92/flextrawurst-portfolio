# Werkraum-Karte

Navigationshilfe für Opencode. Stand: 2026-10-02.

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

## Opencode-spezifisch

| Pfad | Was ist da |
|------|-----------|
| `/root/werkraum/_opencode/` | Opencode' Zuhause im Obsidian-Vault |
| `/root/werkraum/_opencode/notizen/` | Session-Notizen |
| `/root/.opencode/config.toml` | Lokale Opencode-Konfiguration |
| `/root/.opencode/history.jsonl` | Lokale Opencode-Verlaufsspur |

## Importierte Grundrisse

| Pfad | Quelle | Zweck |
|------|--------|-------|
| `_opencode/_import_claude_grundriss/` | `_claude/` | Referenzmaterial Claude-Struktur |
| `_opencode/_import_codex_grundriss/` | `_codex/` | Referenzmaterial Codex-Struktur |
| `_opencode/_import_kimi_grundriss/` | `_kimi/` | Referenzmaterial Kimi-Struktur |