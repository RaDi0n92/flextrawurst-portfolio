# Ring 22D–H — Static Process Camera Worldblick

## Was dieser Ring baut

Einen statischen, read-only, atmosphärischen Weltblick der Prozesskamera: das erste wirklich sichtbare Artefakt, das alle 16 Prozesskörper der Welt als zusammenhängende Karte zeigt.

Konkret entsteht:
- `ProcessCameraModel` — read-only Kameramodell aus `ProcessSnapshot`
- `process_camera_model.json` — deterministischer JSON-Export
- `process_camera_worldblick.html` — lokal öffnbare, statische HTML-Weltkarte
- Such-Integration für `process_camera_node`, `process_camera_layer`, `process_camera_model`
- ConceptGuard-Erweiterung für fünf neue Driftmuster

## Was dieser Ring nicht baut

- Keine App, kein React, kein Vite, kein Canvas, kein Three.js
- Kein externer Fetch, kein WebSocket, kein Renderer
- Kein Live-Dashboard, keine erfundenen Zustände
- Keine AI-Subsysteme, kein Postgres, kein Scheduler, kein Daemon
- Kein Einzug, keine Aktivierung von Slots

## Warum das der erste sichtbare Prozesskamera-Erlebnisring ist

Alle früheren Ringe haben das Prozessmodell aufgebaut (Registry, Traces, Snapshot, Search, Export). Ring 22D–H macht es zum ersten Mal sichtbar: als atmosphärische HTML-Weltkarte, lokal öffnbar, ohne externe Abhängigkeiten. GENI erscheint nicht als normaler Knoten, sondern als Wahrnehmungsschicht. Die sechs namelessAI-Flarum-Wesen erscheinen als D3-Slots mit Herkunftsmarkierung, ohne Einzug. Jeder Prozesskörper zeigt Rolle, Evidenz, Aktivitätsmodus, Spuren und Schutzstatus ehrlich.

## Layer-Struktur

| Layer | Inhalt |
|---|---|
| `perception_layer` | GENI — als Wahrnehmungshintergrundfeld |
| `dialogue_core` | dak+gord-system — Koordinationskern |
| `system_layers` | Systemweiser — Metaschicht |
| `flarum_origin_slots` | 6× namelessAI — D3-Slots, Flarum-Herkunft |
| `infrastructure_processes` | Search, Governance, WorldRun, Worldblick/Export |
| `placeholders` | Reader, Writer, Runner — künftig |
| `guardrails` | Konzeptuelle Schutzschicht (keine Knoten, nur Markierung) |

## Testbudget

40–60 gezielte Tests. Keine künstliche Testmasse.

## Erzeugte Ausgabedateien

```
out/process_camera/process_camera_model.json
out/process_camera/process_camera_worldblick.html
```

## Schutzsatz

Atmosphäre ja. Falsche Innenwelt nein.  
measured_count = 0. active_claim_count = 0.  
Kein Prozesskörper ist besetzt. Kein Zustand ist live gemessen.
