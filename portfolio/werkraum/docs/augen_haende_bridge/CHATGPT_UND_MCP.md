---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: ChatGPT-Vertrag von codex bei Daniels VPS (2026-09-19; Daniels Bridge-Vision, ChatGPT-/Chatty-Ausarbeitung und Codex-Recherche) und V3-Ergänzung zu AI-Strom-Anti-Terminal und MCP-P0 von codex bei Daniels VPS (2026-09-20; Daniels V3-Entscheidung, ChatGPT-/Chatty-Ausarbeitung und MCP-Haijagd). Neu geschrieben von Claude aus den Originalen in archiv/originale/
status: verbindlicher Konzept- und Erstkontaktvertrag; native ChatGPT-Abnahme offen. MCP-P0 live read-only geprüft und als Ganzes BLOCKED (keine echte MCP-Sitzung, kein Atlas-Read)
---

# Augen & Hände — ChatGPT und MCP

Dieses Dokument beschreibt, wie ChatGPT als eigener Strom in die Bridge kommt, und wie ein MCP-Anschluss ehrlich geprüft wird. Der erste Teil ist der ChatGPT-Vertrag. Der zweite Teil ist die V3-Ergänzung: der gemeinsame Anti-Terminal-Kern für alle AI-Ströme und der kleine Diagnosezaun MCP-P0.

Das Dokument ersetzt nicht den nativen Nachweis unter Windows und KDE. Es behauptet keine bereits hergestellte ChatGPT-Verbindung.

## Der ChatGPT-Vertrag

### Die fünf getrennten Körper

- **Raute:** die räumliche Präsenz eines konkreten ChatGPT-Agenten. Sie ist frei verschiebbar, zielgebunden und kann kurzlebige Sprechblasen anzeigen.
- **Chatkörper:** ein kleiner, manuell öffnbarer und frei verschiebbarer Gesprächsraum. Daniel und ChatGPT schreiben dort als getrennte Absender.
- **Anti-Terminal:** die technische Wirbelsäule für Session, Turn, MCP-Calls, Zielbindung, Provenienz, Zustände, Fehler und Belege. Sie bleibt kompakt und ist bei Bedarf aufklappbar.
- **Bridge:** Transport und Verbindung zur realen Windows- und KDE-Bildschirmwelt.
- **Fensterscanner:** die Quelle für die Wahrheit über Ziel, Fenster, Desktop und Binding. Er ist nicht bloß eine dekorative Fensterliste.

Diese Teile dürfen nicht wieder in einem riesigen Monsterfenster verschmelzen. Anzeigeort, Arbeitsziel, konkrete Session und Empfänger bleiben unabhängige Entscheidungen.

Ergänzung vom 2026-09-20 (`ANFORDERUNGEN.md`): ChatGPT hat ein eigenes Anti-Terminal und daneben eine zweite Chatbox (R117). Der ChatGPT-Chat löst nichts aus und ist für alle Teilnehmer desselben Gates lesbar. Ob er für einzelne unsichtbar geschaltet werden kann, ist offen, und falls ja, soll es individuell wählbar sein (R116).

### ChatGPT ist kein lokaler Dummy

Die ChatGPT-Schicht bindet eine echte ChatGPT-Web- oder MCP-Session an. Die EXE simuliert kein lokales ChatGPT-Modell und kopiert keinen Webchat als Attrappe. ChatGPT bleibt ein externer AI-Strom mit eigener Session-ID, eigenem Turn und dem eigenen Zugriffspfad `mcp_chatgpt_web`.

Der Chatkörper ist standardmäßig ein Gesprächsraum. Eine normale Nachricht von Daniel darf keinen MCP- oder Toolaufruf implizit auslösen. Ein absichtlicher technischer Auftrag ist ein eigenes Action-Ereignis mit eigener Freigabe, eigener Capability, Zielbindung und Beweiskette.

### Zwei Ereignisbahnen

```text
CHAT
Daniel → ChatGPT → Antwort → Chatkörper

ACTION
ChatGPT → MCP → Tool → Zielwelt → Rücklese → Beleg
```

Beide Bahnen dürfen im Anti-Terminal nebeneinander angezeigt werden. Sie werden aber nicht als dasselbe Ereignis gespeichert.

Für die Chatbahn gilt:

```text
submitted → delivered → turn_received → rendered
```

Für eine technische Aktion gilt:

```text
accepted → sent → delivered → executed → observed → proven
```

Bei einer normalen Chatnachricht gibt es kein künstliches `executed` im Sinn einer Windows-Aktion. Die Harness behandelt diese beiden Bedeutungen getrennt.

### Absendervertrag

Die zulässigen sichtbaren Quellen sind:

- `daniel` — eine manuelle Nachricht von Daniel,
- `chatgpt` — eine veröffentlichte Antwort der echten ChatGPT-Session,
- `bridge_context` — eine technisch markierte Beobachtung, Status- oder Provenienzinformation.

`bridge_context` spricht nie wie Daniel oder ChatGPT. Eine ChatGPT-Bemerkung wird nicht als nativer Zielbefund ausgegeben. Jeder Eintrag trägt Session, Turn, Ziel, Empfänger und Provenienz, soweit diese Daten vorhanden sind.

### Der erste echte ChatGPT-Vertikalschnitt

Der erste ChatGPT-Slice gilt nur dann als erreicht, wenn diese Kette an einem realen Ziel durchlaufen und belegt wurde:

```text
EXE startet
→ echter Fensterscanner liefert Desktop/Fensterziel
→ reale ChatGPT-Session wird ausgewählt
→ Binding wird zurückgelesen
→ ChatGPT-Raute erscheint am Ziel
→ Chatkörper wird geöffnet
→ Daniel schreibt manuell
→ Nachricht erreicht die reale ChatGPT-Session
→ echte ChatGPT-Antwort kommt zurück
→ Antwort wird im Chatkörper gerendert
→ Absenderidentität stimmt
→ normaler Chat erzeugt keinen impliziten Toolcall
→ Ziel-/Frame-Zustand wird beobachtet
→ gesamte Kette wird belegt
```

Ein lokaler Dummy-Reply, ein Server-ACK, eine Browser-Proof-Surface oder eine angezeigte Beispielnachricht zählt dafür nicht.

### Die Zähne der Harness

Die maschinell kontrollierbaren Erstkontakt-Proofs sind:

```text
session_is_real
target_bound
binding_read_back
chat_message_submitted
message_delivered
chatgpt_turn_received
response_rendered
sender_identity_correct
tool_not_triggered_by_plain_chat
target_observed
proof_attested
```

Die Harness speichert diese als geordnete Beweise. Sie blockiert bei falscher Reihenfolge, bei unbekannter Absenderidentität und bei einer impliziten Kante von Chat zu Action. Sie speichert nicht die Philosophie der Raute. Sie behauptet keine Bilder, Gedanken oder Fähigkeiten, die nicht tatsächlich veröffentlicht und beobachtet wurden.

### Der sichtbare Chatkörper

Der Chatkörper bleibt klein und frei beweglich. Geschlossen ist ChatGPT nur als Raute sichtbar. Beim Öffnen erscheinen der relevante Verlaufsausschnitt, das manuelle Eingabefeld und ein klarer Hinweis auf Ziel und Session.

Die 3,3-Sekunden-Raumblende und der 6,6-Sekunden-Rautenticker bleiben zusätzliche Präsenzdarstellungen. Sie ersetzen nicht den dauerhaften Chatverlauf.

Die technische Anti-Terminal-Ansicht kann bei Bedarf daneben geöffnet werden. Sie zeigt dann mindestens Session, Turn, Gate, MCP-Call, Status, Provenienz und den Verlauf `accepted → sent → delivered → executed → observed → proven`.

### Was nicht versprochen wird

- ChatGPT wird nicht als dauerhaft autonom denkendes lokales Wesen behauptet, nur weil der Chatkörper offen ist.
- Eine ChatGPT-Antwort beweist keine native Wirkung unter Windows oder KDE.
- Ein MCP-Erfolg beweist keine Wirkung im gebundenen Programm.
- Playwright beweist die browserbedienbare Prüfstrecke, aber nicht automatisch die native EXE, den Windows-Fensterscanner oder eine echte Zustellung von Eingaben.

Der nächste technische Schritt nach dem tragenden Codex-Terminal und dem Fensterscanner ist ein einziger echter ChatGPT-Rundlauf. Erst danach kommen mehrere Sessions, ChatGPT-Subagenten, Hauhaucs-Beobachtung und größere Kapsel- und Replay-Funktionen.

## V3 — AI-Strom-Anti-Terminal und MCP-P0

### Der Schiffbruch gehört zur sichtbaren Architektur

Ein angebundener ChatGPT-Strom bleibt technisch an seine echte Session gebunden. Solange diese Session lebt, bleiben Session, Kontext, Chatkörper und Bridge-Anbindung zusammen. Höhere technische Ereignisse können den Strom aber unterbrechen oder verändern:

```text
alive
reconnecting
context_compacted
session_changed
lost
handoff_required
```

Die Bridge behauptet daraus keine dauerhafte Existenz. Sie macht aber sichtbar, ob noch dieselbe Session an Bord ist, ob der Kontext kompakt gefaltet wurde, ob eine neue Session übernommen hat oder ob Daniel eine Übergabe entscheiden muss.

### Nicht vier Anti-Terminals bauen

Der Anti-Terminal-Kern ist eine gemeinsame technische Anatomie. Die AI-Ströme behalten ihre eigenen Körper und Zugangswege:

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

Gleiche Tools bedeuten nicht gleiche Rechte. Ein gemeinsamer Werkraum bedeutet keine gemeinsame Identität.

Der Kern ist ein providerneutraler Ledger- und Statuskern für:

- Session- und Turn-Identität,
- MCP-Handshake und Werkzeugauflistung,
- Toolaufruf, Ergebnis und Fehler,
- Ziel, Binding, Lease und Empfänger,
- Provenienz und Zugangsweg,
- die Trennung von Chat und Action,
- Continuity- und Schiffbruchzustände,
- Replay-, Handoff- und Beweisstatus.

Die Vorderseite darf je Strom anders bleiben. ChatGPT bekommt den manuellen Chatkörper, Codex behält sein echtes Terminal, Claude und Gemini bekommen ihre jeweiligen Arbeitskörper. Der technische Anti-Terminal-Kern zeigt bei Bedarf, was zwischen Strom, MCP und Welt wirklich passiert.

### Provider- und Zugangsprovenienz

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

Die vorgesehenen Strom-IDs sind `chatgpt`, `codex`, `claude` und `gemini`. Zugangswege bleiben unterscheidbar, etwa `mcp_chatgpt_web`, `mcp_provider` oder `terminal_direct`. Ein gemeinsamer Dateipfad oder ein gemeinsames Modelllabel löst keine Verschmelzung von Identitäten aus.

### MCP-P0 — der kleine Diagnosezaun

MCP-P0 ist kein vierfacher Großbau und keine neue Oberfläche. Es ist ein read-only Preflight, der einen Anschluss in wenigen Stufen ehrlich prüft:

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

Ein Handshake ohne `Mcp-Session-Id` ist nicht automatisch ein Serverfehler, denn Legacy-MCP kann stateless betrieben werden. Er braucht dann aber eine ausdrückliche Attestierung `session_mode=stateless`. Ohne bekannten Modus bleibt der Harness-Zustand BLOCKED.

Eine vorhandene ID heißt stateful und muss bei den Folgeaufrufen mitgeführt werden. Ein Server-ACK ohne `tools/list` ist kein vollständiger MCP-P0-Erfolg. Ein erfolgreiches `tools/list` ohne harmlosen Read von `/gesamtatlas` bleibt unvollständig.

Diese Unterscheidung folgt der offiziellen MCP-Transportdokumentation. Die aktuelle Spezifikationsentwicklung beschreibt den stateless Protokollkern und entfernt in der Revision `2026-07-28` sogar Handshake und `Mcp-Session-Id`. Die Legacy-Varianten dürfen weiterhin stateful oder stateless betrieben werden. Siehe [MCP Specification Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) und [MCP Specification Changelog](https://modelcontextprotocol.io/specification/draft/changelog).

Das Anti-Terminal ist genau dafür wichtig: Ein alter Codex-Fehler darf nicht wieder jahrelang unsichtbar bleiben, während Dokumente behaupten, der Anschluss sei aktiv.

**Anfangsprofil für `/gesamtatlas`.** Der erste reale MCP-P0-Lauf erhält nur ein enges Atlas-Profil:

- Atlas lesen,
- Atlas suchen,
- Provenienz prüfen,
- Sessionstatus lesen,
- eigene Spur schreiben.

Es gibt keine pauschale Vollfreigabe, keine stillen Seiteneingänge und keine Bridge-Aktionen aus einem Atlas-Preflight. Desktopsteuerung, Capture, Overlay, Terminalinput und fremde Empfänger kommen erst über eigene Capabilities, Leases und Belege.

**Abnahme.** MCP-P0 ist bestanden, wenn für den jeweiligen Strom ein echter, rücklesbarer Lauf existiert:

```text
configured
→ reachable
→ stateful: echte Session-ID / stateless: explizite Modus-Attestierung
→ tools/list mit Toolanzahl oder Hash
→ harmloser Atlas-Read
→ normalisiertes Resultat
→ Provenienz-/Zeitspur
```

Bei Fehlern wird nicht weitergeschaltet. Das Anti-Terminal zeigt die letzte erreichte Stufe und die konkrete Ursache.

Die Harness erzwingt diese Reihenfolge in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/harness.py` über `MCPPreflightRun`. Dieselbe Harness trägt außerdem die Chat-/Action-Trennung des ChatGPT-Vertrags.

### V3-Baufolge

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

V3.6 ist kein beiläufiger Unterpunkt von V3.7. Es ist ChatGPTs eigener Vertikalschnitt nach Terminal, Fensterscanner, Binding und nativer Evidence, im Gesamtplan `G06.5`:

```text
echte ChatGPT-Session binden
→ eigene Raute und manueller Chatkörper
→ echte Nachricht und echte Antwort zurücklesen
→ Anti-Terminal-Ledger führen
→ Plain-Chat darf keinen Toolcall auslösen
→ mehrere ChatGPT-Slots getrennt halten
```

V3 baut nicht gleichzeitig fünf Rauten, drei Terminals, ChatGPT, Kamera, Mikrofon, Bilder, Scrubber und alles Übrige. Der erste tragende Körper ist klein und muss wirklich leben:

```text
EXE lebt
→ ein echter Terminalkanal lebt
→ Eingabe und Ausgabe sind rücklesbar
→ der Fensterscanner sieht echte Ziele
→ das Binding überlebt Änderungen
→ Guardian und native Evidence bestätigen den Weg
→ danach gehen die AI-Ströme real an Bord
```

### Was nicht passieren darf

- Eine gemeinsame MCP-Schicht darf AI-Identitäten nicht verschmelzen.
- Ein ChatGPT-Chatkörper darf nicht zum Codex-Terminal werden.
- Ein Codex-MCP-Fehler darf nicht als »nicht relevant« verschwinden, nur weil `/gesamtatlas` der wichtigste Zweck ist.
- `configured` darf nicht als `reachable` gelten.
- `reachable` darf nicht als `handshake_succeeded` gelten.
- `tools/list` darf nicht als erfolgreicher Atlas-Read gelten.
- Ein MCP-Erfolg darf nicht als Wirkung in der Zielwelt ausgegeben werden.
- Ein Sessionwechsel darf nicht still als Sessionkontinuität erscheinen.

### Live-P0 vom 2026-09-20

Der erste read-only Transportlauf wurde gegen die öffentlichen Klone ausgeführt. Der vollständige Bericht steht unter `/root/werkraum/augen_haende_bridge/tests/evidence/MCP_P0_LIVE_READONLY_EVIDENCE.md`.

```text
configured             PASS für die bekannten VPS-Units / Konfiguration
reachable              PASS
initialize response    PASS — flextrawurst-vps-mcp 1.1.1
real MCP session       BLOCKED — keine Mcp-Session-Id im Response
tools/list             PASS — 137 Werkzeuge
harmloser Atlas-Read   BLOCKED — OAuth-Token nicht verwendet/verfügbar
MCP-P0 insgesamt       BLOCKED
```

Die sechs VPS-MCP-Units sind als enabled markiert, und die Ports 8091 bis 8096 lauschen. Für Codex existiert der dedizierte VPS-Serverkörper unter Port 8094. `/config/.codex/config.toml` enthält in dieser Laufzeit aber keinen MCP-Servereintrag. Das erklärt die Trennung zwischen vorhandenem Server und nicht aktiviertem Client, ohne zu behaupten, damit sei jede historische Codex-Fehlermeldung bereits erklärt.

Claude und Gemini haben ebenfalls reale öffentliche Klone. Ihre lokalen Konfigurationsdateien enthalten in dieser Umgebung keinen entsprechenden VPS-MCP-Eintrag.

Wichtig: `initialize` und `tools/list` sind damit live nachgewiesen. Der Server-Quelltext und die Antwortform sprechen für einen stateless betriebenen Klon. Diese Betriebsentscheidung wird aber nicht aus einem fehlenden Header abgeleitet, sondern muss als Providerprofil eingetragen werden. Danach folgt genau ein autorisierter, read-only Atlas-Read mit Resultat, Provenienz und Zeitspur.

### Der Greenfield-Runner

Der erste ausführbare Greenfield-Adapter liegt in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/mcp_p0.py`. Er akzeptiert die öffentliche Basis-URL oder `/mcp`, führt den Preflight in der verbindlichen Reihenfolge aus und verlangt für `atlas_read_verified` tatsächlich zurückgelesenen Content. Ein Bearer-Token ist optionaler Prozessinput und wird nicht geloggt.

Der Live-Dogfood-Lauf gegen den Codex-Klon reproduziert den Befund:

```text
configured → reachable → initialize response
→ session_mode=stateless attestieren
→ tools/list → BLOCKED: atlas_read_requires_bearer_token
```

Das ist nicht mehr nur ein manueller Curl-Befund, sondern ein wiederholbarer Greenfield-Test. Der Runner repariert absichtlich noch keinen laufenden Dienst und aktiviert keinen fremden Client automatisch.
