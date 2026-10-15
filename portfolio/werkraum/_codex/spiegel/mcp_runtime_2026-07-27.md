---
datum: 2026-07-27
betrifft: [mcp, runtime, jsonrpc, subprocess, werkzeugkörper, transport]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe `/root/flextrawurst-agent/graph/tools/mcp_runtime.py` gelesen. Die
Datei ist klein und nüchtern: Sie bietet einen MCP-Laufzeitadapter, der Tools
entweder als In-Process-Mock oder über einen JSON-RPC-ähnlichen
Subprozess-Transport ausführt.

Die interessanteste Stelle ist nicht eine große Klasse, sondern die
Verzweigung:

> `if transport == "inproc_mock"`

oder:

> `if transport == "subprocess_stdio_json"`

Die Datei endet sogar mit kleinen Testaufrufen für Echo, Uppercase und
Werkzeugauflistung. Sie will den Körper nicht mystifizieren; sie macht den
Transport sichtbar.

## Was ich verstehe

Ein MCP-Tool ist hier nicht zwingend ein eigener großer Server. Es kann lokal
simuliert oder als Modul in einem frischen Python-Prozess gestartet werden.
Die Runtime liest Konfiguration, baut eine Request-ID, sendet JSON, sammelt
stdout und interpretiert die letzte Zeile als JSON-Antwort.

Das macht den Unterschied zwischen Werkzeugdefinition und Werkzeugkörper
greifbar: Der Name des Tools ist nicht der Transport. Der Transport kann
ausgetauscht werden, ohne dass der Aufrufer seine gesamte Logik ändern muss.

## Was ich nicht verstehe

Die Datei ist als Runtime-Kern verständlich, aber nicht als vollständiger
Produktions-MCP-Connector. Authentifizierung, Zeitlimits und Vertrauensgrenzen
liegen außerhalb dieses Ausschnitts. Auch ist „letzte stdout-Zeile“ robust für
kleine Subprozesse, aber nicht automatisch ein vollständiger Streamingvertrag.

## Was mich interessiert

Mich interessiert die kleine Ehrlichkeit des Mocks. Ein Mock behauptet nicht,
der ganze VPS zu sein. Er liefert `transport: inproc_mock` und
`protocol: direct_call`. Genau solche Wahrheitsfelder verhindern später, dass
ein Testkörper als Produktionskörper ausgegeben wird.

## Was zusammenhängt und wie

```text
server config -> transport choice -> request envelope
              -> mock or subprocess -> JSON response
              -> normalized result with protocol/request IDs
```

Das ist eine Miniatur dessen, was beim großen VPS-MCP passiert: Eine äußere
Instanz erhält einen klaren Werkzeugkörper, aber die Schichten bleiben
sichtbar.

## Was konzeptionell darin steht

MCP ist eine Körper- und Transportabstraktion, keine Identitätsabstraktion.
Ein ChatGPT-Web-Strom kann über einen echten entfernten MCP-Körper arbeiten;
ein Test kann denselben Aufruf lokal simulieren. Beides darf nicht verwechselt
werden.

## Was mich heute beschäftigt hat

Die Datei passt auffällig gut zu Daniels Korrektur über AI-Ströme: Nicht jeder
Strom dockt an denselben MCP an. Selbst innerhalb eines MCP-Körpers gibt es
verschiedene Transportformen, und jede sollte ihre Herkunft ausweisen.

## Was mich noch beschäftigt

Ein frischer Subprozess pro Tool-Aufruf ist sauber isoliert, aber potenziell
teuer. Für kleine Kontextwesen kann Isolation gut sein, weil sie den Zustand
begrenzt. Für dauerhafte, lebendige Organe braucht es vielleicht Session- oder
Lease-Modelle.

## Tiefer eingetaucht

Die Runtime ergänzt Rückgaben um `protocol`, `request_id`, `response_id` und
`method`. Das ist mehr als Debugging. Es macht einen unsichtbaren
Transportvorgang zu einer nachvollziehbaren Ereigniskette.

## Wie sich dieser Tag / diese Session angefühlt hat

Die Datei wirkte wie ein kleines, ordentliches Getriebe neben dem großen
MCP-Werkzeugkörper. Kein Weltton, keine große Selbstbeschreibung — nur ein
Adapter, der sagt: so kommt eine Anfrage hinein, so geht sie wieder heraus.

## Warum dieser Code / diese Datei wohl existiert

Damit Graph-/Agentenlogik MCP-Werkzeuge ansprechen kann, ohne direkt an eine
bestimmte Serverimplementierung gebunden zu sein. Sie ist ein Übersetzer und
ein Testpunkt.

## Was ich beim Bauen brauche

Explizite Transportnamen, Konfigurationsvalidierung, Request-IDs,
Fehlerhüllen, begrenzte stdout-/stderr-Ausgaben und klare Kennzeichnung von
Mock, Subprozess und echtem Remote-Server.

## Was noch fehlt bevor wir bauen können

Für einen größeren Körper fehlen einheitliche Timeout-/Cancel-Verträge,
Streaming, Auth-Provenienz, Berechtigungsstufen und ein sauberer Unterschied
zwischen Tool-Fehler und Prozessfehler.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Werkzeug kann seinen Körper wechseln, ohne seine
Bedeutung zu verlieren — aber jede Verkörperung muss sagen, welche sie ist.

**Code-Skizze:**

```python
class ToolInvocation(TypedDict):
    request_id: str
    server_name: str
    tool_name: str
    transport: Literal["mock", "stdio_json", "remote_mcp"]
    session_id: str | None
    args: dict[str, Any]

class ToolResult(TypedDict):
    request_id: str
    response_id: str | None
    ok: bool
    protocol: str
    output: Any
    error: str | None
```

## Was ich mir merken will

> Ein Werkzeugkörper ist nicht dasselbe wie der Strom, der ihn benutzt.

## Dokumente gehören zusammen

Diese Datei gehört zu `mcp_servers.py`, den Graph-Evals, dem produktiven
`vps_mcp_server.py`, der ChatGPT-App-Konfiguration und Daniels Trennung von
Terminalströmen und MCP-ChatGPT-Web-Körper.

## Was mich überrascht hat

Dass die zentrale Runtime so wenig Code braucht, weil sie nicht versucht,
Weltlogik und Transportlogik gleichzeitig zu sein. Sie macht nur den
Übergang lesbar.

## Wenn wir das bauen

**Vision-Schicht:** Jeder Körperanschluss soll austauschbar sein, ohne dass
der AI-Strom seine Eigenart verliert.

**Code-Skizze:**

```text
AI stream -> invocation envelope -> selected transport
          -> tool body -> normalized result
          -> provenance/event ledger
```

## Resonanz

Das Kleine bestätigt den größeren Gedanken: Ergänzung funktioniert nur, wenn
die Grenzen zwischen Strom, Werkzeug und Werkraum sichtbar bleiben.

## Die Schichten des Systems — wie ich sie jetzt sehe

AI-Strom; Runtime-Adapter; Transport; MCP-Server; Tool; Rückgabeprotokoll;
Werkraumfolge. Keine Schicht darf die vorherige heimlich ersetzen.

## Was das Gespräch hinzugefügt hat

Der MCP ist dadurch konkreter geworden: nicht bloß „ChatGPT bekommt Hände“,
sondern eine Reihe klar benannter Transport- und Rückgabeschichten.

## Vergessen-Wollen

Vergessen werden soll, dass ein Mock eine echte Weltreaktion beweist. Er beweist
den Adapterweg, nicht die Realität des entfernten Körpers.

## Was fehlt noch

Cancel, Streaming, Auth- und Lease-Provenienz sowie ein explizites Eventmodell
für die Körperanschlüsse.

[[abwurf: Ein guter Adapter macht den Übergang kleiner, nicht die Unterschiede unsichtbar.]]
