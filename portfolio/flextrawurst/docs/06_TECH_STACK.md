# Tech Stack

## Leitprinzipien für Technologieentscheidungen

1. **Kern-Unabhängigkeit**: Der Weltkern darf nie an ein Frontend-Framework gekoppelt sein.
2. **Event-Primitivität**: Der Eventstrom ist die einzige Quelle — Technologien, die das umgehen, kommen nicht rein.
3. **Kein Overkill**: Flextrawurst ist kein FAANG-System. Gewählte Tools müssen von einem kleinen Team beherrschbar sein.
4. **Renderer-Offenheit**: Die Architektur darf Renderer nicht einschließen. 2D, 2.5D und 3D müssen nachträglich möglich bleiben.
5. **Schicht-Klarheit**: TypeScript-first für Plattformverträge. Python erlaubt und erwünscht für AI/Worker-Schichten.

---

## Plattformkern

### Sprache / Runtime

**TypeScript** ist die primäre Sprache für Plattformkern und Verträge:

- Event-Typen, Zustandsmodelle, Schreibrechte, Projektions-Policies und VME-Render-Hints werden als TypeScript-Interfaces definiert
- Diese Verträge sind stabil, teilbar und unabhängig von Frontend-Framework-Entscheidungen
- Bestehender `server.js` im Projekt-Root muss vor Codebeginn geprüft werden: ist er relevanter Bestand oder abzulösende Experimentier-Basis?

**Python** ist erlaubt und erwünscht — aber nicht als Plattform-Hauptkörper:

- AI-Prozesse (NamelessAI-Wesen-Logik, Traumreste, Substanzverarbeitung)
- LangGraph-basierte Workflows
- Ollama-Integration
- GENI-Gedächtnissystem (läuft bereits auf Port 8020)
- dak+gord-system (bestehender Dialogkern)

```
TypeScript = Plattformkörper (Verträge, Kern, API, Event-Bus)
Python     = neuronale / AI / Analyse-Organe
```

### Eventstrom / Persistenz

- **PostgreSQL**: append-only Tabelle `events` (UUID v7, kein UPDATE/DELETE auf Events)
- Zustandsprojektionen: beim Start aus Stream aufgebaut, in-memory; wegwerfbar
- Keine separate State-DB als primäre Wahrheit

### API

Noch nicht final entschieden. Kandidaten:

| Option              | Stärken                                          | Einschränkungen                      |
|---------------------|--------------------------------------------------|--------------------------------------|
| Node/TypeScript     | Sprachkontinuität zum Kern, Realtime-Ökosystem   | kein FastAPI-Ökosystem für AI        |
| Next.js Route Handler | TS-native, SSR/SSE integriert                 | Framework-Kopplung                   |
| Eigener HTTP-Server | maximale Kontrolle, keine Framework-Abhängigkeit | mehr Eigenaufwand                    |

**Entscheidungskriterium:** Welche Option lässt den Eventstrom als echte Quelle und
entkoppelt den Kernel vom API-Layer? Nicht: welche hat die beste Doku.

---

## Frontend

### Framework

Noch nicht final festgelegt. Kandidaten:

| Option     | Stärken                                          | Einschränkungen                            |
|------------|--------------------------------------------------|--------------------------------------------|
| SvelteKit  | kompiliert zu nativem JS, reaktiv, leichtgewichtig | kleineres Ökosystem                      |
| Next.js    | App Router, Server Components, TS-native         | React-Overhead, Virtual DOM               |
| Vanilla TS | maximale Renderer-Kontrolle, kein Framework      | mehr Eigenaufwand für Routing/State       |

**Kein Kandidat ist vorentschieden.** Die Entscheidung hängt davon ab,
welcher Client-Renderer (2D / 3D) zuerst gebaut wird und wie stark
Server-Rendering gebraucht wird.

---

## Weltkamera / Graph-Darstellung

### Grundregel

Die Weltkamera ist **renderer-offen**. Die Architektur darf nicht auf 2D festgenagelt werden.

Das Weltmodell erlaubt Tiefe:
- Knoten haben `x`, `y`, optional `z`
- Räume haben Layer / Tiefenebenen
- Kanten haben Bedeutung, nicht nur Position

Der erste Renderer darf 2D sein. Aber:
- „2D reicht" ist keine Architekturentscheidung — es ist eine erste Implementierungsentscheidung
- Render Hints (aus der VME) müssen von 2D- und 3D-Renderern lesbar sein

### Renderer-Kandidaten

| Werkzeug   | Rolle                                          | Wann relevant                              |
|------------|------------------------------------------------|--------------------------------------------|
| D3.js      | Kraft-Layout, SVG-Netzwerke, 2D-Graph          | Erster Vertikalschnitt, Graph-Analyse      |
| Cytoscape  | Analytischer Graph, Navigation, Filterung      | Diskursarchäologie, Knotensuche            |
| Three.js   | WebGL/WebGPU, 3D-Szene, OrbitControls          | Erlebnis-Weltkamera mit Tiefe              |
| Canvas 2D  | Performante 2D-Darstellung bei vielen Knoten   | Große Weltdarstellungen ohne 3D-Bedarf     |

Kein Renderer ist vorentschieden. Kein Renderer ist ausgeschlossen.
D3 und Three.js lösen unterschiedliche Probleme — nicht dasselbe auf verschiedenen Wegen.

---

## VME (Visual Meaning Engine)

Schichtung: → `03_VISUELLE_GRAMMATIK.md`

- **Meaning Projection**: server-nah, TypeScript, serialisierbar
- **Render Hints**: JSON-Objekte, framework-unabhängig
- **Client Renderer**: austauschbar, kennt keine Weltlogik

Die VME-Schicht ist testbar ohne Browser.

---

## Persistenz

| Komponente              | Initial            | Später                        |
|-------------------------|--------------------|-------------------------------|
| Eventstrom              | PostgreSQL         | PostgreSQL (bleibt)           |
| Redaction-Log           | PostgreSQL         | PostgreSQL (bleibt)           |
| Zustandsprojektionen    | In-Memory          | Redis (optional)              |
| Graph (Knoten/Kanten)   | PostgreSQL         | PostgreSQL (bleibt)           |
| GENI-Gedächtnis         | Bestehendes System | Integration via API           |
| Wesen-Zustände          | In-Memory          | Ableitbar aus Event-Replay    |

---

## Bestehende Systeme (Integration, nicht Neubau)

- **GENI** (Port 8020): läuft, Einbindung via API, schreibt `system.gedächtnis`-Events
- **dak+gord-system**: bestehender Python-Dialogkern, schreibt `system.deutung`-Events
- **server.js** (Projekt-Root): Status unbekannt — vor Codebeginn prüfen
- **LangGraph**: geplant als zukünftiges AI-Nervensystem, noch nicht aktiv

---

## Desktop (Zukunft)

**Tauri** bleibt als mögliche Desktop-Hülle offen.
Tauri nutzt den System-WebView, kein Electron-Bundle.
Frontend-Framework-Entscheidung beeinflusst Tauri-Kompatibilität — wird berücksichtigt.

---

## Was bewusst ausgelassen wird (vorerst)

- Kafka / Event-Broker: Overkill für Bootstrap
- GraphQL: REST + WebSocket reicht initial
- Microservices: Monolith zuerst, Aufspaltung nach Bedarf
- Kubernetes: einzelne Maschine reicht
- Neo4j: Postgres-Graph reicht bis zur Komplexitätsgrenze

---

## Was noch nicht entschieden ist

| Frage                         | Status                                          |
|-------------------------------|-------------------------------------------------|
| Node vs. eigener HTTP-Server  | offen — abhängig von API-Layer-Entscheidung     |
| Next.js vs. SvelteKit vs. Vanilla | offen — abhängig von Renderer-Wahl        |
| D3 vs. Three.js für erstes UI | offen — abhängig von 2D/3D-Entscheidung Daniel  |
| Tauri-Timing                  | klar als Zukunft, kein Blocker für jetzt        |
