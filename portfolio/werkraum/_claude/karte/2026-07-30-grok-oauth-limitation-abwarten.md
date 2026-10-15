---
datum: 2026-07-30
betrifft: [grok, xai, oauth, mcp-connector, vps-mcp-server, unauthorized-style]
importable: false
autor: claude-code bei Daniels VPS
---

## Nachtrag zum Slash-Redirect-Fix: OAuth-Discovery scheitert grundsätzlich

Nach dem Slash-Fix (siehe `2026-07-30-grok-mcp-klon-und-slash-redirect-bug.md`) sah Grok den
Connector, aber jeder echte Tool-Aufruf scheiterte mit "Nicht autorisiert -- OAuth-Login
noetig" als reinem Chattext, ohne dass Grok selbst einen Login-Flow ausgelöst hätte.

**Erste Vermutung, per Code-Fund bestätigt statt geraten:** unser Server antwortete bei
fehlendem Token mit HTTP 200 + `_meta["mcp/www_authenticate"]` im JSON-RPC-Body -- eine
bewusste, dokumentierte Anpassung an ChatGPTs Apps-SDK-Auth-Flow (Kommentar im Code, 23.07.:
"ohne beide Teile wird das Linking-UI nicht angezeigt"). Ein echter HTTP-401 hätte ChatGPTs
Login-UI vermutlich gebrochen.

**Fix, additiv, ohne Risiko für die anderen 5 Klone:** neue Env-Var
`VPS_MCP_UNAUTHORIZED_STYLE` (Default `chatgpt_meta`, unverändert für alle bestehenden
Klone), nur Grok bekommt `http401` -- echter HTTP-401 mit korrektem `WWW-Authenticate`-Header.
Verifiziert: Grok bekommt jetzt 401, Claude Web bleibt exakt beim alten 200-Verhalten.

## Trotzdem weiterhin kein Erfolg -- der eigentliche Befund

Nach dem Fix: Daniel bekommt weiterhin "Auth required" / "Transport send error", diesmal aber
kein reiner Chattext mehr, sondern ein echter 401 in den Logs (`200→202→401`-Sequenz bei
mehreren Versuchen). Grok reagiert trotzdem nicht mit einem eigenen Login-Flow.

**Entscheidender Beleg, nicht nur Vermutung:** `grep -i grok-connectors-manager
access.log | grep -i "well-known\|register\|authorize\|token"` liefert **null Treffer**.
Grok hat zu keinem Zeitpunkt einen `.well-known`-Discovery-Pfad, `/oauth/register`,
`/oauth/authorize` oder `/oauth/token` aufgerufen -- egal ob unser Server 200+_meta oder
echten 401 zurückgab. Alle `.well-known`-Zugriffe in den Logs stammen von meinen eigenen
curl-Tests, nicht von Grok selbst.

**Schlussfolgerung:** Grok.com's aktueller Custom-Connector-Client
(`grok-connectors-manager/0.1.0`, sehr frühe Versionsnummer) geht direkt auf den
MCP-Endpunkt, hält die Verbindung für "erfolgreich" weil `initialize`/`tools/list` ohne Auth
funktionieren, und implementiert den OAuth-Discovery-Teil der MCP-Authorization-Spec
offenbar noch nicht -- unabhängig davon, was der Server zurückgibt. Das ist keine Lücke in
unserem Server mehr, sondern eine Limitation auf xAI/Groks Seite.

## Entscheidung

Zwei Wege vorgelegt: abwarten (Grok reift vermutlich nach) oder Token direkt als
Query-Parameter in der URL einbetten (Sicherheits-Tradeoff, Token könnte in Server-Logs
landen). Daniel: **abwarten.** Keine weitere Änderung am Server für Grok vorgenommen, der
`http401`-Stil bleibt wie er ist (spec-konform, für später wenn Grok nachzieht).

## Was ich mir merken will

Dieselbe Disziplin wie beim ersten Fund: nicht der ersten plausiblen Erklärung glauben
("Server-Bug"), sondern nachprüfen, ob der Fix überhaupt greift, bevor man weiter am eigenen
Code sucht. Der zweite, entscheidende Beleg (keine einzige Discovery-Anfrage von Grok selbst)
kam erst nach dem Fix -- hätte ich das vorher geprüft, wäre die Reihenfolge (erst Slash, dann
401, dann erst der eigentliche Client-Limitation-Fund) vielleicht kürzer gewesen.
