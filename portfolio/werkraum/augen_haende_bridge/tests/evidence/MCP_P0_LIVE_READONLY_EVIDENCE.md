EVIDENCE_VERSION: 1
DATE: 2026-09-20
SCOPE: live read-only MCP-P0 transport probe
OUTCOME: BLOCKED — atlas read and real MCP session identity are not proven

# MCP-P0 — live read-only evidence

## Gegenstand

Geprüft wurden die öffentlich konfigurierten VPS-MCP-Klone, ohne Dienstneustart,
ohne Token auszulesen und ohne mutierende Toolaufrufe. Die Probe verwendete
`GET /mcp`, JSON-RPC `initialize`, JSON-RPC `tools/list` und einen absichtlich
unauthorisierten, harmlosen Atlas-Suchaufruf.

## Quelle und Infrastruktur

- `/root/werkraum/tools/vps_mcp/mcp_app_config.json` weist den ChatGPT-Klon auf
  `https://flextrawurst.de/werkzeugkoerper-[PFAD-GESCHWAERZT]/mcp` mit OAuth hin.
- Die Offline-Units unter `/vps_system/etc/systemd/system/` enthalten dedizierte
  Klone für ChatGPT (8091), Claude (8092), Claude Web (8093), Codex (8094),
  Gemini (8095) und Grok (8096). Alle sechs Units sind offline als `enabled`
  markiert; alle sechs lokalen Ports lauschen.
- `/config/.codex/config.toml` enthält keinen MCP-Servereintrag.
- `/config/.mcp.json` enthält nur den lokalen `blender`-Server.
- `/config/.gemini/config/mcp_config.json` ist leer.

## Live-Befund pro öffentlichem Klon

Für ChatGPT, Codex, Claude und Gemini sowie den zusätzlich vorhandenen Grok-Klon
war der Befund gleich:

- `GET /mcp`: HTTP 401 mit OAuth-Discovery-Hinweis — `reachable: PASS`.
- JSON-RPC `initialize`: HTTP 200, Server `flextrawurst-vps-mcp` Version `1.1.1`,
  Protokoll `2025-06-18` — `handshake response: PASS`.
- Die Antwort enthielt keine `Mcp-Session-Id`. Das ist bei einem stateless
  betriebenen Legacy-MCP nicht automatisch ein Fehler; ohne explizite
  `session_mode=stateless`-Attestierung bleibt der Harness aber bewusst
  `BLOCKED`, weil der Modus sonst unbekannt wäre.
- JSON-RPC `tools/list`: HTTP 200, 137 Werkzeuge, darunter
  `atlas_hybrid_search` — `tools_list_received: PASS`.
- JSON-RPC `tools/call` ohne Token: strukturierte MCP-Fehlerantwort mit
  `mcp/www_authenticate` und „OAuth-Login nötig“ — Auth-Gate arbeitet; dies ist
  kein Atlas-Read und daher `atlas_read_verified: NOT_TESTED`.

## Status nach dem V3-Vertrag

```text
configured             PASS für die bekannten VPS-Units / öffentliche Konfiguration
reachable              PASS
session mode           UNKNOWN — stateless nicht automatisch aus Header-Abwesenheit ableiten
handshake_succeeded    PASS nach expliziter `session_mode=stateless`-Attestierung
tools_list_received    PASS — 137
atlas_read_verified    BLOCKED — vorhandenes OAuth-Token nicht verwendet/verfügbar
```

## Konsequenz

Der alte Codex-Befund ist präzisiert: Der serverseitige Codex-Körper existiert,
ist aktiviert, lauscht und liefert den Werkzeugkatalog. Der lokale Codex-Client
hat in dieser Umgebung aber keinen MCP-Eintrag. Der aktuelle Server-Handshake
ist mit einem stateless Providerprofil vereinbar; eine fehlende
`Mcp-Session-Id` wird nicht mehr als automatischer Serverfehler ausgegeben.
Providerprofil und autorisierter Atlas-Read bleiben trotzdem offen.

## Nächster kleinster Schritt

1. Das Providerprofil ausdrücklich als `stateful` oder `stateless` markieren;
   Header-Abwesenheit allein genügt nicht.
2. Den tatsächlichen Codex-/Provider-Clienteintrag gezielt aktivieren oder seine
   fehlende Konfiguration herstellen — ohne bestehende Sessions zu stören.
3. Einen vorhandenen autorisierten Read-only-Testweg verwenden und genau einen
   Atlas-Read mit Resultat, Provenienz und Zeitspur zurücklesen.

Kein Windows-/EXE-, Fensterscanner- oder Playwright-PASS ist aus diesem Bericht
abgeleitet. Diese Datei belegt nur den MCP-Transport-Preflight.

## Greenfield-Runner

Der reproduzierbare Runner liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/mcp_p0.py` und wird
durch `/root/werkraum/augen_haende_bridge/tests/test_mcp_p0.py` geprüft. Er
akzeptiert sowohl die öffentliche Basis-URL als auch eine explizite `/mcp`-URL,
trägt eine vorhandene Session-ID nur als MCP-Header weiter und verlangt für den
Atlas-Schritt nicht nur `isError=false`, sondern auch tatsächlich rückgelesenen
Textinhalt. Ein OAuth-Token wird ausschließlich vom aufrufenden Prozess übergeben
und nie in Resultaten oder Logs ausgegeben.

Die vier nichtgeheimen Providerprofile sind im selben Modul hinterlegt. Der
reproduzierbare Aufruf für Codex lautet:

```text
PYTHONPATH=src python3 -m augen_haende_bridge --provider codex
```

Der Live-Lauf gegen den Codex-Klon wurde mit dem Runner wiederholt. Ergebnis:

```text
configured             PASS
reachable              PASS — HTTP 401 auf GET /mcp ist die erwartete OAuth-Schranke
initialize response    PASS — flextrawurst-vps-mcp 1.1.1
session_mode            UNKNOWN → mit `session_mode=stateless` attestierbar
handshake_succeeded    PASS nach expliziter Stateless-Attestierung
tools_list_received    PASS — 137
atlas_read_verified    nicht erreicht
```
