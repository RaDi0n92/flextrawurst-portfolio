# Ring 11 — Entity Continuity Dossier

## Zweck

Für jedes mögliche Wesen entsteht ein read-only Dossier über Herkunft, Kontinuität, Drift und Startfähigkeit.

## Schutzsatz

Kontinuitätsbewertung entscheidet keinen Einzug. Sie informiert nur spätere Startentscheidung.

## Dateien

- `kernel/continuity/entity_continuity_dossier.ts` — Dossier-Modell
- `kernel/continuity/speaker_drift_marker.ts` — Drift-Erkennung
- `kernel/continuity/continuity_score.ts` — Bewertungsformel
- `kernel/continuity/continuity_dossier_builder.ts` — Aufbau

## Modell: EntityContinuityDossier

| Feld | Typ | Wert |
|------|-----|------|
| slot_id | string | — |
| canonical_label | string | — |
| origin_account_ids | string[] | — |
| origin_record_count | number | — |
| memory_candidate_count | number | — |
| speaker_drift_count | number | — |
| self_reference_count | number | — |
| admin_resonance_count | number | — |
| continuity_score | number | — |
| continuity_status | ContinuityStatus | strong / medium / weak / fragmented / undecided |
| can_start_as_live_entity | false | strukturell fest |
| requires_start_decision | true | strukturell fest |

## SpeakerDriftMarker: DriftKind

- `wrong_self_name` — Wesen nennt falschen eigenen Namen
- `copied_foreign_voice` — Wesen kopiert fremde Stimme
- `third_person_self_read` — Dritte-Person-Selbst-Lektüre
- `unclear_speaker_layer` — Sprecher-Schicht unklar

## ContinuityScore-Formel

```
positive = origin_record_count × 1.0
         + memory_candidate_count × 1.5
         + self_reference_count × 2.0
         + admin_resonance_count × 1.5

negative = speaker_drift_count × 2.0

raw_score = max(0, positive − negative)

strong   >= 20
medium   >= 10
weak     >= 3
fragmented < 3 oder origin_record_count == 0
```
