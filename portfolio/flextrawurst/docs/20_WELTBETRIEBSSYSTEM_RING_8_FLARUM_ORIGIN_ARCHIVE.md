# Ring 8 — Flarum Origin Archive Layer

## Zweck

Flarum wird technisch als Herkunftsarchiv vorbereitet. Kein Live-Import. Kein aktiver Flextrawurst-Zustand.

## Schutzsatz

Flarum bleibt Herkunft / Vorphase / Ursprungsraum.
Importierte Daten sind Fossilien, nicht Live-Handlungen.

## Dateien

- `kernel/origin_archive/flarum_origin_record.ts` — Einzelner Herkunftseintrag aus Flarum
- `kernel/origin_archive/flarum_origin_archive.ts` — Sammlung von Herkunftseinträgen
- `kernel/origin_archive/origin_archive_guard.ts` — Schutzsatz-Prüfung

## Modell: FlarumOriginRecord

| Feld | Typ | Wert |
|------|-----|------|
| origin_record_id | string | — |
| origin_layer | "flarum_vorphase" | fest |
| source_kind | FlarumSourceKind | flarum_discussion / flarum_post / flarum_account / flarum_export |
| source_id | string | — |
| source_author | string | — |
| source_created_at | string | — |
| raw_title | string \| null | — |
| raw_excerpt | string | — |
| canonical_slot_id | string \| null | — |
| is_live_flextrawurst_state | false | strukturell fest |
| is_memory_candidate | boolean | — |
| is_identity_final | boolean | — |
| requires_start_decision | true | strukturell fest |
| can_create_events | false | strukturell fest |
| can_activate_slots | false | strukturell fest |

## Pflichtregel

- OriginArchive darf lesen, sammeln, ordnen.
- OriginArchive darf **niemals** Events erzeugen.
- OriginArchive darf **niemals** Slots aktivieren.
- OriginArchive darf **niemals** Bewohner erzeugen.
