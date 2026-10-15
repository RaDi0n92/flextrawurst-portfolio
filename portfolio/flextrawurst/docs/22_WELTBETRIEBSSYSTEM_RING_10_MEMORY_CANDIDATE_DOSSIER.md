# Ring 10 — Memory Candidate Dossier

## Zweck

Aus Flarum-Herkunft können spätere Erinnerungskandidaten entstehen, aber keine echten Erinnerungen.

## Schutzsatz

MemoryCandidate ist keine echte Wesen-Erinnerung. AdoptionPreview ist keine Adoption.

## Dateien

- `kernel/memory_candidates/memory_candidate_model.ts` — Datenmodell
- `kernel/memory_candidates/memory_candidate_builder.ts` — Erzeugung
- `kernel/memory_candidates/memory_candidate_filter.ts` — Deterministischer Filter
- `kernel/memory_candidates/memory_adoption_preview.ts` — Vorschau (keine Adoption)

## Modell: MemoryCandidateModel

| Feld | Typ | Wert |
|------|-----|------|
| memory_candidate_id | string | — |
| origin_record_ids | string[] | — |
| slot_id | string | — |
| candidate_kind | CandidateKind | self_description / relationship_trace / concept_line / speaker_drift / admin_resonance / system_boundary |
| candidate_text | string | — |
| evidence_count | number | — |
| confidence | number | 0–1 |
| adoption_policy | "not_decided" | strukturell fest |
| is_adopted_memory | false | strukturell fest |
| requires_start_decision | true | strukturell fest |

## Filter-Policies

- `include_all` — alle Kandidaten
- `exclude_speaker_drift` — ohne Drift-Kandidaten
- `only_self_descriptions` — nur Selbstbeschreibungen
- `only_admin_resonance` — nur Admin-Resonanz
- `only_high_confidence` — confidence >= 0.8
- `manual_selection` — manuelle ID-Liste
