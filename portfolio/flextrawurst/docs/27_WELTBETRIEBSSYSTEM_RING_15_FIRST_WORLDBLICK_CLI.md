# Ring 15 — CLI / Script: Erster Weltblick

## Status

read-only | kein Einzug | keine Aktivierung | kein Live-Import | kein Server | kein Daemon

## Zweck

Ring 15 ist der erste sichtbare Weltabdruck. Daniel kann einen Befehl ausführen und bekommt Export + HTML Preview lokal auf der Festplatte.

```bash
npm run worldblick
```

## Schutzsatz

```
Worldblick startet kein Flextrawurst.
Worldblick liest nur deterministische Fixture-/Kernel-Daten.
Worldblick erzeugt keine Events.
Worldblick aktiviert keine Slots.
Worldblick importiert nichts live.
Worldblick startet keine Wesen.
```

## Erzeugte Output-Dateien

```
out/worldblick/world_inspection_export.json
out/worldblick/world_inspection_export.md
out/worldblick/worldview_static_preview.html
```

## WorldblickOutput Pflichtfelder

| Feld | Wert |
|---|---|
| creates_events | false |
| activates_slots | false |
| imports_live_data | false |
| starts_world | false |
| is_read_only | true |

## Dateien

- `kernel/worldblick/worldblick_output_model.ts`
- `kernel/worldblick/worldblick_builder.ts`
- `scripts/build_worldblick_preview.ts`

## Package Script

```json
"worldblick": "node --experimental-strip-types scripts/build_worldblick_preview.ts"
```

## Ziel

Daniel kann zum ersten Mal eine lokale Datei öffnen und den Weltkörper als statischen, read-only Weltblick sehen. Nicht lebendig. Nicht aktiviert. Aber sichtbar.
