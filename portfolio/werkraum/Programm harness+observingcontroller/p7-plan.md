Ja, genau. Dann ist die klare Trennung:

- Die Skills und Bauverträge dienen dem Entwickeln und Prüfen der Bridge.
- Das eigentliche operative Harnessprogramm der Bridge gehört auf `https://flextrawurst.de/os`.
- Die Windows-/KDE-Komponente läuft als lokaler Bridge-Körper auf den jeweiligen Desktops.
- `/os` ist die zentrale Regie-, Beobachtungs- und Kontrollschicht.

Beim Durchforsten des VPS habe ich außerdem einen wichtigen Punkt gefunden: Die laufende Hände‑Augen‑Bridge besitzt bereits bewusst eine eigene Datenbank und einen eigenen LangGraph-Unterbau.

In der aktuellen Laufzeit steht ausdrücklich:

> Eigene Bridge-Datenbank, nicht `flextrawurst`.

Das ist kein Problem, sondern sogar sinnvoll. Ich würde die Datenbanken nicht zwanghaft zusammenschieben:

```text
flextrawurst-Hauptsystem
├── Agenten-, Projekt- und Atlasdaten
├── ChatGPT-/Claude-/Codex-/Gemini-Ströme
├── Profile und globale Harness-Konfiguration
└── /os-Kontrolloberfläche

Augen-Hände-Bridge
├── eigene PostgreSQL-Datenbank
├── eigener LangGraph-Infragraph
├── eigene Ereignis- und Beweisspur
├── Fenster-/Desktop-Ziele
├── Terminalkanäle
├── Eingabe- und Overlay-Zustände
└── lokale Windows-/KDE-Körper
```

`/os` verbindet beide Welten über eindeutige Identitäten, Sitzungen, Ereignisse und Zustände. Die Bridge-Datenbank bleibt dabei die technische Wahrheit für das, was tatsächlich über Augen und Hände passiert ist.

Der vorhandene Bridge-LangGraph enthält bereits die richtige operative Reihenfolge:

```text
Ziel gebunden
→ frischer Wahrnehmungsstrom
→ gültige Lease
→ Handaktion
→ Beleg
→ Urteil
→ Ende
```

Wenn ein Schritt dreimal scheitert, geht der Lauf in einen sichtbaren Halt und anschließend in Diagnose. Das ist genau die Art von Kontrolllogik, die auf `/os` sichtbar und steuerbar werden sollte.

Wichtig ist außerdem: Das aktuelle Agentenregister unterscheidet bereits zwischen:

- einer von der Bridge selbst gestarteten Sitzung;
- einem Unteragenten;
- einem steuerbaren Agenten;
- einem nur gemeldeten Agenten;
- Gruppen;
- Eltern-/Kind-Beziehungen;
- verfügbaren Fähigkeiten wie Ansprechen, Beobachten, Pausieren und Beenden.

Das passt direkt zu deiner Flotte aus Claude, Codex, Gemini, Haiku, ChatGPT und Unteragenten.

Es gibt aber eine aktuelle Begrenzung, die für dein Ziel entscheidend ist: Der derzeitige Bridge-Code bindet absichtlich nur Sitzungen an, die er selbst gestartet hat. Bereits laufende fremde Sitzungen werden momentan nicht automatisch übernommen.

Für dein `/os` brauchen wir deshalb zwei unterschiedliche Betriebsarten:

| Betriebsart | Bedeutung |
|---|---|
| Bridge-owned | Die Bridge hat den Agenten gestartet und darf ihn über Terminal/Prozessgruppe steuern |
| Attached | Eine bestehende Sitzung wurde bewusst an die Bridge angebunden |
| Observed-only | Die Bridge kann sie lesen und beobachten, aber nicht steuern |
| Unknown | Eine Oberfläche oder Sitzung wurde entdeckt, aber noch nicht sicher identifiziert |

Damit können deine realen Situationen sauber abgebildet werden:

- Claude Code auf VD1: möglicherweise `attached` oder `observed-only`;
- Gemini „gemgem“: eigene externe Sitzung;
- Codex auf VD1: eigene Sitzung;
- Anthropic Claude auf VD2: eigene Web-/App-Sitzung;
- Gemini „gravityy“ auf VD2: weitere Sitzung;
- Claude Haiku über PuTTY: Terminal-Sitzung;
- ChatGPT über den Flextraxtreme-MCP: eigener AI-Strom;
- diese aktuelle ChatGPT-Session: eigene `/os`- beziehungsweise MCP-Kontrollsitzung.

Die Hände‑Augen‑Bridge wird dabei nicht einfach „noch ein Agent“. Sie ist der Körper und das Wahrnehmungs-/Aktionsorgan des gesamten Systems:

- Augen: Fenster, Desktop, Terminal, Bilder, Kamera, sichtbare Zustände;
- Hände: Tastatur, Maus, Controller, Eingabegeräte, Aktionen;
- Körper: lokales Overlay, Raute, Terminal- und Nachrichtenfenster;
- Nervensystem: Relay, WebSocket, MCP und Sessionkanäle;
- Gedächtnis: eigene Bridge-PostgreSQL;
- Ablaufhirn: eigener LangGraph;
- Regie: `flextrawurst.de/os`;
- Zeuge: Ereignis-, Beleg- und Provenienzspur.

`/os` sollte dafür einen eigenen Bereich bekommen, etwa:

## Hände‑Augen‑Bridge

Dort sieht man live:

- ob der Bridge-Körper online ist;
- welcher Rechner und welcher virtuelle Desktop verbunden sind;
- welche Fenster erkannt wurden;
- welche Ziele aktuell gebunden sind;
- welche Fähigkeiten wirklich verfügbar sind;
- ob nur Beobachtung oder auch Eingabe erlaubt ist;
- welcher Agent welche Lease besitzt;
- welche Aktion gerade läuft;
- ob sie angenommen, übertragen, ausgeführt, beobachtet und protokolliert wurde;
- ob ein Not-Aus aktiv ist;
- ob der Wahrnehmungsstrom frisch oder veraltet ist;
- ob der lokale Körper und der VPS-Relay verbunden sind.

## Agentenregie

Hier sieht man:

- alle Agenten über VD1, VD2, PuTTY, ChatGPT und MCP;
- mehrere gleiche Claude- oder Gemini-Instanzen;
- Hauptagenten und Unteragenten;
- Eltern-/Kind-Beziehungen;
- externe und bridge-eigene Sitzungen;
- Profile und aktive Harnesses;
- gemeinsame Gruppen;
- laufende Aufträge;
- Übergaben;
- Pausen, Abbrüche und Fehler;
- Agenten, die nur beobachtbar, aber nicht steuerbar sind.

## Beweis- und Driftbereich

Hier wird nicht nur angezeigt, dass eine Aktion „erfolgreich gesendet“ wurde. Die Bridge unterscheidet bereits sinnvoll:

```text
angenommen
→ übertragen
→ vom Ziel empfangen
→ ausgeführt
→ Zielzustand beobachtet
→ protokolliert
→ bewiesen
```

Das ist für dein eigentliches Ziel extrem wichtig. Ein Klick- oder Tastaturpaket darf nicht automatisch als erfolgreiche Aktion gelten. `/os` muss zeigen, an welcher Stelle die Kette abgebrochen ist.

Und die ChatGPT-Anbindung gehört ebenfalls in diese Regie. Der vorhandene Bridge-Code unterscheidet schon zwischen Chat- und Aktionsspur. Eine normale Nachricht darf nicht heimlich einen Toolcall oder eine Desktopaktion auslösen. Wenn ChatGPT etwas über die Bridge tun soll, muss es als explizit ausgelöste Aktion mit eigenem Ziel, eigener Berechtigung und eigener Beweiskette erscheinen.

Die wichtigste Architekturformulierung lautet deshalb:

> Die Bau-Harness entwickelt die Hände‑Augen‑Bridge.  
> Die operative Bridge-Harness läuft auf `flextrawurst.de/os`.  
> Der lokale Bridge-Körper sieht und handelt auf Windows/KDE.  
> Die Agenten bleiben eigenständige Bewohner mit eigenen Sitzungen.  
> Der Flextraxtreme-/OS-Körper verbindet, beobachtet, regiert und beweist alles.

Der aktuelle Codebestand hat dafür schon viele passende Stücke: eigener Ereignisspeicher, eigener LangGraph, Agentenregister, Eltern-/Kind-Aufträge, Relay, Terminalkanal, Windows-Fensterscanner, Hände-Anbindung, Controller-Anbindung, MCP-P0 und ChatGPT-Protokollverträge.

Der nächste sinnvolle Architekturbaustein ist daher kein weiterer Build-Skill, sondern ein echter `/os`-Bridge-Control-Adapter, der beide Seiten verbindet:

```text
Bridge-Laufzeit
↕
Bridge-Control-Adapter
↕
flextrawurst.de/os
↕
Agentenregister, Atlas, Profile, Handoffs, Driftkontrolle
```

Dabei muss die Bridge-eigene Datenbank erhalten bleiben. `/os` bekommt zusätzlich eine kontrollierte Sicht darauf und verknüpft sie mit den globalen Agenten- und Session-IDs.
