---
datum: 2026-09-20
autor: codex bei Daniels VPS
herkunft: Daniels V3-Entscheidung, ChatGPT-/Chatty-Ausarbeitung und MCP-Haijagd
status: verbindliche V3-Ergänzung; Live-P0 geprüft, Session-/Atlas-Stufen offen
---

# V3 — AI-Strom-Anti-Terminal und MCP-P0

## Der Schiffbruch gehört zur sichtbaren Architektur

Ein angebundener ChatGPT-Strom bleibt technisch an seine echte Session
gebunden. Solange diese Session lebt, bleiben Session, Kontext, Chatkörper und
Bridge-Anbindung zusammen. Höhere technische Ereignisse können den Strom aber
unterbrechen oder verändern:

```text
alive
reconnecting
context_compacted
session_changed
lost
handoff_required
```

Die Bridge darf daraus keine dauerhafte Existenz behaupten. Sie muss aber
sichtbar machen, ob noch dieselbe Session an Bord ist, ob der Kontext kompakt
gefaltet wurde, ob eine neue Session übernommen hat oder ob Daniel eine
Übergabe entscheiden muss.

## Nicht vier Anti-Terminals bauen

Der Anti-Terminal-Kern ist eine gemeinsame technische Anatomie. Die AI-Ströme
behalten ihre eigenen Körper und Zugangswege:

```text
Anti-Terminal-Kern
├── ChatGPT-MCP-Adapter
├── Codex-MCP-Adapter
├── Claude-MCP-Adapter
└── Gemini-MCP-Adapter
```

Vorne bleiben die Körper verschieden:

```text
Codex       = echtes Terminal
ChatGPT     = Raute + manueller Chatkörper
Claude      = eigener Arbeitskörper
Gemini      = eigener Arbeitskörper
```

Hinten teilen sie nur das technische Rückgrat:

```text
Handshake
→ tools/list
→ Session
→ Call-ID
→ Tool
→ Resultat
→ Fehler
→ Provenienz
→ Beweisstatus
```

Gleiche Tools bedeuten nicht gleiche Rechte. Gemeinsamer Werkraum bedeutet
nicht gemeinsame Identität.

## Provider- und Zugangsprovenienz

Jeder Adapter führt mindestens:

```text
ai_stream_id
mcp_session_mode
mcp_session_id (nur stateful)
access_path
server_id
tool_profile
configured
reachable
handshake
tools_list
last_error
checked_at
```

Die vorgesehenen Strom-IDs sind `chatgpt`, `codex`, `claude` und `gemini`.
Zugangswege bleiben unterscheidbar, etwa `mcp_chatgpt_web`, `mcp_provider`
oder `terminal_direct`. Ein gemeinsamer Dateipfad oder ein gemeinsames
Modelllabel darf keine Identitätsverschmelzung auslösen.

## MCP-P0 — der kleine Diagnosezaun

MCP-P0 ist kein vierfacher Großbau und keine neue Oberfläche. Es ist ein
read-only Preflight, der einen Anschluss in wenigen Stufen ehrlich prüft:

```text
configured
→ reachable
→ handshake_succeeded
→ tools_list_received
→ atlas_read_verified
```

Für jeden AI-Strom wird dabei sichtbar:

```text
Codex MCP
configured       ✓/✗
reachable        ✓/✗
handshake        PASS/FAILED
tools/list       Anzahl oder UNKNOWN
atlas.read       PASS/NOT_TESTED
last_error       konkrete Stufe und Meldung
last_success     Zeitstempel
```

Ein Handshake ohne `Mcp-Session-Id` ist nicht automatisch ein Serverfehler:
Legacy-MCP kann stateless betrieben werden. Er braucht dann aber eine
ausdrückliche `session_mode=stateless`-Attestierung; ohne bekannten Modus bleibt
der Harness-Zustand BLOCKED. Eine vorhandene ID ist stateful und muss bei den
Folgeaufrufen mitgeführt werden. Ein Server-ACK ohne `tools/list` ist kein
vollständiger MCP-P0-Erfolg. Ein erfolgreiches `tools/list` ohne harmlosen
`/gesamtatlas`-Read bleibt unvollständig.

Diese Unterscheidung folgt der offiziellen MCP-Transportdokumentation: Die
aktuelle Spezifikationsentwicklung beschreibt den stateless Protokollkern und
entfernt in der Revision `2026-07-28` sogar Handshake und
`Mcp-Session-Id`; die Legacy-Varianten dürfen weiterhin stateful oder stateless
betrieben werden. Siehe [MCP Specification Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
und [MCP Specification Changelog](https://modelcontextprotocol.io/specification/draft/changelog).

Das Anti-Terminal ist genau dafür wichtig: Ein alter Codex-Fehler darf nicht
wieder jahrelang unsichtbar bleiben, während Dokumente behaupten, der Anschluss
sei aktiv.

## Anfangsprofil für `/gesamtatlas`

Der erste reale MCP-P0-Lauf erhält nur ein enges Atlas-Profil:

- Atlas lesen;
- Atlas suchen;
- Provenienz prüfen;
- Sessionstatus lesen;
- eigene Spur schreiben.

Keine pauschale Vollfreigabe, keine stillen Seiteneingänge und keine
Bridge-Aktionen aus einem Atlas-Preflight. Desktopsteuerung, Capture, Overlay,
Terminalinput und fremde Empfänger kommen erst über eigene Capabilities,
Leases und Belege.

## V3-Baufolge

```text
MCP-P0 als kurzer Diagnosezaun
        ↓
V3.0 EXE lebt
V3.1 echter Codex-Terminalkanal
V3.2 Ein-/Ausgabe wirklich rücklesbar
V3.3 Fensterscanner sieht echte Welt
V3.4 Binding überlebt Bewegung und Änderung
V3.5 Guardian + native Evidence bestätigen es
V3.6 ChatGPT kommt real an Bord
V3.7 Codex-/Claude-/Gemini-MCP-Körper sauber anschließen
```

V3.6 ist dabei kein beiläufiger Unterpunkt von V3.7, sondern ChatGPTs eigener
Vertikalschnitt nach Terminal, Fensterscanner, Binding und nativer Evidence
(im Gesamtplan `G06.5`):

```text
echte ChatGPT-Session binden
→ eigene Raute und manueller Chatkörper
→ echte Nachricht und echte Antwort zurücklesen
→ Anti-Terminal-Ledger führen
→ Plain-Chat darf keinen Toolcall auslösen
→ mehrere ChatGPT-Slots getrennt halten
```

V3 baut nicht gleichzeitig fünf Rauten, drei Terminals, ChatGPT, Kamera,
Mikrofon, Bilder, Scrubber und den gesamten Jahrmarkt. Der erste tragende
Körper ist klein und muss wirklich leben:

```text
EXE lebt
→ ein echter Terminalkanal lebt
→ Eingabe und Ausgabe sind rücklesbar
→ der Fensterscanner sieht echte Ziele
→ das Binding überlebt Änderungen
→ Guardian und native Evidence bestätigen den Weg
→ danach gehen die AI-Ströme real an Bord
```

## Gemeinsame technische Anatomie

Der Anti-Terminal-Kern ist keine vierfache UI. Er ist ein providerneutraler
Ledger-/Statuskern für:

- Session- und Turn-Identität;
- MCP-Handshake und Werkzeugauflistung;
- Toolaufruf, Ergebnis und Fehler;
- Ziel, Binding, Lease und Empfänger;
- Provenienz und access path;
- Chat-/Action-Trennung;
- Continuity-/Schiffbruchzustände;
- Replay-, Handoff- und Beweisstatus.

Die Vorderseite darf je Strom anders bleiben. ChatGPT bekommt den manuellen
Chatkörper; Codex behält sein echtes Terminal; Claude und Gemini bekommen ihre
jeweiligen Arbeitskörper. Der technische Anti-Terminal-Kern zeigt bei Bedarf,
was zwischen Strom, MCP und Welt wirklich passiert.

## Was nicht passieren darf

- Eine gemeinsame MCP-Schicht darf AI-Identitäten nicht verschmelzen.
- Ein ChatGPT-Chatkörper darf nicht zum Codex-Terminal werden.
- Ein Codex-MCP-Fehler darf nicht als „nicht relevant“ verschwinden, nur weil
  `/gesamtatlas` der wichtigste Zweck ist.
- `configured` darf nicht als `reachable` gelten.
- `reachable` darf nicht als `handshake_succeeded` gelten.
- `tools/list` darf nicht als erfolgreicher Atlas-Read gelten.
- Ein MCP-Erfolg darf nicht als Wirkung in der Zielwelt ausgegeben werden.
- Ein Sessionwechsel darf nicht still als Sessionkontinuität erscheinen.

## Abnahme von MCP-P0

MCP-P0 ist bestanden, wenn für den jeweiligen Strom ein echter, rücklesbarer
Lauf existiert:

```text
configured
→ reachable
→ stateful: echte Session-ID / stateless: explizite Modus-Attestierung
→ tools/list mit Toolanzahl oder Hash
→ harmloser Atlas-Read
→ normalisiertes Resultat
→ Provenienz-/Zeitspur
```

Bei Fehlern wird nicht weitergeschaltet. Das Anti-Terminal zeigt die letzte
erreichte Stufe und die konkrete Ursache.

Die Harness erzwingt diese Reihenfolge in
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` über
`MCPPreflightRun`. Die gleiche Harness trägt außerdem die Chat-/Action-Trennung
des ChatGPT-Vertrags.

## Live-P0 vom 2026-09-20

Der erste read-only Transportlauf wurde gegen die öffentlichen Klone ausgeführt;
der vollständige Bericht steht unter
`/root/werkraum/augen_haende_bridge/tests/evidence/MCP_P0_LIVE_READONLY_EVIDENCE.md`.

Ergebnis:

```text
configured             PASS für die bekannten VPS-Units / Konfiguration
reachable              PASS
initialize response    PASS — flextrawurst-vps-mcp 1.1.1
real MCP session       BLOCKED — keine Mcp-Session-Id im Response
tools/list             PASS — 137 Werkzeuge
harmloser Atlas-Read   BLOCKED — OAuth-Token nicht verwendet/verfügbar
MCP-P0 insgesamt       BLOCKED
```

Die sechs VPS-MCP-Units sind als enabled markiert und die Ports 8091–8096
lauschen. Für Codex existiert der dedizierte VPS-Serverkörper unter Port 8094,
aber `/config/.codex/config.toml` enthält in dieser Laufzeit keinen MCP-
Servereintrag. Das erklärt die Trennung zwischen vorhandenem Server und nicht
aktiviertem Client, ohne zu behaupten, dass damit jede historische Codex-
Fehlermeldung bereits erklärt ist. Claude und Gemini haben ebenfalls reale
öffentliche Klone; ihre lokalen Konfigurationsdateien enthalten in dieser
Umgebung keinen entsprechenden VPS-MCP-Eintrag.

Wichtig: `initialize` und `tools/list` sind damit live nachgewiesen. Der
Server-Quelltext und die Antwortform sprechen für einen stateless betriebenen
Klon; diese Betriebsentscheidung wird aber nicht aus fehlender Header-
Beobachtung halluziniert, sondern muss als Providerprofil eingetragen werden.
Danach folgt genau ein autorisierter read-only Atlas-Read mit Resultat,
Provenienz und Zeitspur.

## Greenfield-Runner

Der erste ausführbare Greenfield-Adapter liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/mcp_p0.py`.
Er akzeptiert die öffentliche Basis-URL oder `/mcp`, führt den Preflight in der
verbindlichen Reihenfolge aus und verlangt für `atlas_read_verified` tatsächlich
rückgelesenen Content. Ein Bearer-Token ist optionaler Prozessinput und wird
nicht geloggt.

Der Live-Dogfood-Lauf gegen den Codex-Klon reproduziert den Befund:

```text
configured → reachable → initialize response
→ session_mode=stateless attestieren
→ tools/list → BLOCKED: atlas_read_requires_bearer_token
```

Das ist jetzt nicht mehr nur ein manueller Curl-Befund, sondern ein
wiederholbarer Greenfield-Test. Der Runner repariert absichtlich noch keinen
laufenden Dienst und aktiviert keinen fremden Client automatisch.
