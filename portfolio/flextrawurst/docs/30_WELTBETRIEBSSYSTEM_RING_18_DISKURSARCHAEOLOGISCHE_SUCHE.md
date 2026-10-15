# Ring 18 — Diskursarchäologische Deep Search + Filter Grammar + Provenance Query Layer

## Was Ring 18 baut

Ring 18 baut Deep Search als Diskursarchäologie.

Nicht UI.
Nicht API.
Nicht Datenbank.
Nicht Mutation.
Nicht AI.

Die Suche liest vorhandene Weltkörper und macht sie filterbar:
Events, Timeline, Provenienz, Slots, Features, Admin Commands, ConceptGuard,
Worldblick, Audit, CameraModel, Export und OS-Spine.

## Leitanker

```
Suche ist nicht „wo steht ein Wort?"
Suche ist: Woher kommt etwas, durch welche Schicht ging es, worauf verweist es,
welche Events, Slots, Policies, Provenienzen, ConceptGuards, Timelines,
Exports und Worldblick-Strukturen hängen daran?
```

## Schutzformeln

- SearchIndex ≠ Datenmutation
- SearchResult ≠ Wahrheit ohne Quelle
- Filter ≠ Policy-Änderung
- SearchQuery ≠ CommandIntent
- Diskursarchäologie ≠ Volltextsuche allein
- DeepSearchFoundation ≠ bereits fertige UI

## Neue Dateien (Ring 18)

```
kernel/search/search_document.ts
kernel/search/search_corpus.ts
kernel/search/archaeology_filter.ts
kernel/search/archaeology_query.ts
kernel/search/causal_archaeology.ts
kernel/search/provenance_archaeology.ts
kernel/search/search_inspection_pack.ts
kernel/search/search_export.ts
docs/30_WELTBETRIEBSSYSTEM_RING_18_DISKURSARCHAEOLOGISCHE_SUCHE.md
tests/world_os_ring_18_deep_search_archaeology.test.ts
```

## SearchDocument Kinds

| Kind | Quelle |
|---|---|
| event | FlextrawurstEvent |
| timeline_frame | WorldTimelineFrame |
| provenance_record | ProvenanceRecord |
| slot | EntitySlot |
| feature_flag | FeatureFlag |
| concept_guard_violation | ConceptGuardViolation |
| audit | WorldAudit |
| camera_node | WorldCameraNode |
| camera_edge | WorldCameraEdge |
| worldblick_output | WorldblickOutput |
| inspection_export_section | ExportSection |
| command_ledger_entry | CommandLedgerEntry |
| os_spine_summary | WorldOSSpine Summary |

## Was nie passieren darf (Ring 18)

- Keine Mutation durch Suche
- Keine Events durch Suche
- Keine Feature-Aktivierung durch Suche
- Keine Policy-Änderung durch Suche
- Keine UI
- Keine API
- Keine AI
- Kein Renderer
- Kein Postgres
- Kein Scheduler
- Keine Datei-I/O
