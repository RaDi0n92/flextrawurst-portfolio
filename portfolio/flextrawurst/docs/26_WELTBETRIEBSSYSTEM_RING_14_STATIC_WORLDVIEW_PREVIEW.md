# Ring 14 — Static Worldview Preview HTML

## Status

read-only | kein Einzug | keine Aktivierung | kein Renderer | kein Server | kein Canvas

## Zweck

Ring 14 erzeugt eine **statische HTML-Datei**, die Daniel lokal im Browser öffnen kann. Sie zeigt den Weltkörper als lesbaren, nicht-interaktiven Weltblick. Keine App, kein React, kein Vite, kein Three.js.

## Schutzsatz

```
StaticPreview ist keine Live-Welt.
HTMLPreview aktiviert keine Wesen.
Preview ist kein Einzug.
Kein Renderer. Kein Canvas. Kein CDN. Kein extern JS. Kein Live-Fetch. Keine Mutation.
```

## Pflichtfelder

| Feld | Wert |
|---|---|
| is_static | true (strukturell) |
| is_read_only | true (strukturell) |
| has_external_dependencies | false (strukturell) |
| can_activate_slots | false (strukturell) |
| can_create_events | false (strukturell) |

## Sichtbare Sektionen

- Flextrawurst — Weltkamera Preview (Titel)
- Status: read-only / no activation / no live import
- Export-Metadaten
- OriginArchive
- MemoryCandidates
- ContinuityDossiers
- WorldviewGraph
- VisualMeanings
- ReplayExplanations
- ConceptGuardWarnings
- NextHumanDecisions

## HTML-Regeln

- Single file, keine externen Ressourcen
- Inline CSS, kein externes JS, kein CDN
- Kein `<canvas>`, kein WebSocket, kein `fetch()`
- Kein `script src`, kein `XMLHttpRequest`
- Deterministisch: gleicher Export → gleiche HTML

## Dateien

- `kernel/static_preview/static_preview_model.ts`
- `kernel/static_preview/static_preview_builder.ts`
- `kernel/static_preview/static_preview_html.ts`
- `kernel/static_preview/static_preview_writer.ts`
