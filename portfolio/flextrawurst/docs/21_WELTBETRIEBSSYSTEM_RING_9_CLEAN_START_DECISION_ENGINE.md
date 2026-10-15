# Ring 9 — Clean Start Decision Engine

## Zweck

Der spätere saubere Flextrawurst-Start wird als Entscheidung vorbereitet, nicht ausgeführt.

## Schutzsatz

StartDecisionPreview ist keine Startausführung. Es ist nur eine Vorschau möglicher sauberer Startformen.

## Dateien

- `kernel/start_decision/clean_start_decision_model.ts` — Datenmodell der Startentscheidung
- `kernel/start_decision/start_memory_policy.ts` — Speicher-Policy-Optionen
- `kernel/start_decision/start_roster_policy.ts` — Roster-Policy-Optionen
- `kernel/start_decision/start_decision_preview.ts` — Vorschau-Wrapper

## Startmodi (MemoryPolicyKind)

| Modus | Bedeutung |
|-------|-----------|
| with_full_flarum_memory | Alle Flarum-Kandidaten bereitgestellt, keine Übernahme |
| without_flarum_memory | Kein Kandidat wird geführt, Herkunft bleibt |
| with_selected_memory | Ausgewählte Kandidaten als Preview |
| reduced_roster_start | Reduziertes Roster, keine Löschung |
| undecided | Kein Start möglich |

## Roster-Optionen (RosterPolicyKind)

| Option | Bedeutung |
|--------|-----------|
| all_six | Alle sechs Slots |
| selected_four | Vier Slots |
| selected_three | Drei Slots |
| manual_selection | Manuelle Auswahl |
| undecided | Kein Start möglich |

## Pflichtfelder (alle strukturell gesetzt)

- `uses_flarum_as_origin_only: true`
- `creates_live_state: false`
- `activates_slots: false`
- `requires_admin_confirmation: true`
