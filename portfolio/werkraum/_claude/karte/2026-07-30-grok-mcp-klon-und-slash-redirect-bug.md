---
datum: 2026-07-30
betrifft: [vps-mcp, grok, xai, nginx, oauth, mcp-connector, redirect-bug]
importable: false
autor: claude-code bei Daniels VPS
---

## Sechster MCP-Klon: Grok

Daniel wollte grok.com ausprobieren, mit vollem Werkzeugzugriff wie die anderen fünf Ströme,
aber ohne vorgefertigtes Zuhause -- Grok soll sich selbst etwas aufbauen. Umgesetzt nach dem
etablierten Muster (ein gemeinsamer `vps_mcp_server.py`-Kern, neue Env-Vars, neue
systemd-Unit `vps-mcp-grok.service`, Port 8096, neue nginx-Locations):

- URL: `https://flextrawurst.de/werkzeugkoerper-grok-[REDACTED]/`
- Client ID: `vps-mcp-grok-[REDACTED]`
- Zuhause bewusst leer: `_grok/MANIFEST.json` mit `{"sections": {}}`, `_grok/protokoll/
  grok_zuhause_v1.json` beschreibt nur die Startbedingung ("leer, offen, selbst zu
  gestalten"), kein Fließtext der für Grok spricht.

Rührt `vps_mcp_server.py` selbst nicht an -- nur eine weitere Konfiguration desselben,
unveränderten Server-Codes. Deshalb kein Konflikt mit dem separat laufenden
ChatGPT-Omega-Redteam, das genau diese Datei gerade hash-prüft (siehe
`2026-07-30-abwurf-fuer-alle-ai-stroeme-teilweise-umgesetzt.md`).

## Echter Bug gefunden und gefixt: Slash-Redirect killt Groks Connector

Erster Verbindungsversuch scheiterte mit "Verbindung fehlgeschlagen", keine genauere Angabe
in der UI. nginx-Access-Log zeigte den tatsächlichen Ablauf, nicht nur eine Vermutung:

```
POST /werkzeugkoerper-grok-[REDACTED]/ ... 200/202/200 (121973 Bytes -- vollständiger Handshake)
POST /werkzeugkoerper-grok-[REDACTED]   ... 301 (Redirect auf die Slash-Form)
GET  /werkzeugkoerper-grok-[REDACTED]/  ... 404
```

Groks Connector-Manager ruft denselben Endpunkt aus zwei verschiedenen Quell-IPs auf --
einmal korrekt mit abschließendem Slash (funktioniert vollständig), einmal ohne (nginx
antwortet mit 301, der Client wandelt beim Redirect-Folgen den ursprünglichen POST in ein GET
um -- Standard-HTTP-301-Verhalten bei vielen Clients -- und landet als GET auf dem
JSON-RPC-Endpunkt, der nur POST akzeptiert -> 404). Vermutlich bewertet Groks UI schon einen
der beiden parallelen Probe-Aufrufe als maßgeblich, auch wenn der andere durchläuft.

**Fix:** ein zusätzlicher exakter `location = /werkzeugkoerper-grok-[REDACTED]` Block ohne
Redirect, der direkt auf denselben Backend proxyt -- analog zu den bereits bestehenden
`/authorize`/`/token`/`/register`-Root-Aliasen für Claude Web. Verifiziert: beide Formen
(mit/ohne Slash) liefern jetzt 200.

## Was ich mir merken will

Dieselbe Fehlerklasse wie beim Claude-Web-OAuth-Fund vom 29.07. (unerwartete URL-Form eines
Clients, die unsere Server-Konvention nicht vorgesehen hatte) -- nur diesmal nicht bei der
OAuth-Discovery, sondern beim MCP-Endpunkt selbst. Xai's offizielle Doku
(docs.x.ai/grok/connectors, .../custom-mcp-tunneling, .../connector-management) war zu dünn,
um das vorher zu erahnen -- der echte nginx-Access-Log war die einzige verlässliche Quelle,
nicht die Herstellerdoku.

## Offen

Ob damit die "Verbindung fehlgeschlagen"-Meldung wirklich behoben ist, hab ich nicht selbst
verifizieren können (kein eigener Grok-Zugang) -- Daniel muss den Connector in der Grok-UI
neu versuchen.
