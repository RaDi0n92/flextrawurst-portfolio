# Ring 17 — Admin Control Plane + Feature Flag Registry + Activation Gates

## Was Ring 17 baut

Ring 17 baut keine Features.
Ring 17 baut Admin-/Operator-Kontrolle und Feature-/Organ-Flags.

Alle späteren Organe bleiben deaktiviert.
Jede Aktivierung braucht explizite Freigabe.
Jede kritische Handlung wird als CommandIntent/Audit-Spur behandelbar.

KompOase, Tamagotchi, Resonanzurlaub, Schlaf, Substanzen, Traumreste und METAWAR
bleiben registrierbare, aber deaktivierte FeatureSlots.

## Leitanker

```
Admin zuerst.
Feature-Kontrolle zuerst.
Aktivierungsgates zuerst.

Kein Schritt ohne Freigabe.
Kein Feature ohne Flag.
Keine Aktivierung ohne Daniel.
Keine Weltbewegung ohne Kontrolle.
```

## Schutzformeln

- Registriert ≠ gebaut
- Gebaut ≠ aktiv
- Aktiv ≠ unkontrolliert
- Blueprint ≠ Feature
- FeatureSlot ≠ laufendes Organ
- Import ≠ Einzug
- presence_pulse ≠ Leben
- ConsoleModel ≠ UI
- SearchIndex ≠ Datenmutation
- AdminControl ≠ heimliche Manipulation

## Neue Dateien (Ring 17)

```
kernel/admin/admin_permissions.ts
kernel/admin/command_intent.ts
kernel/admin/command_ledger.ts
kernel/admin/admin_control_snapshot.ts
kernel/admin/admin_control_inspection.ts
kernel/admin/admin_control_export.ts
kernel/features/feature_flag.ts
kernel/features/feature_registry.ts
kernel/features/feature_activation_gate.ts
kernel/features/feature_deactivation_gate.ts
tests/world_os_ring_17_admin_feature_control.test.ts
```

## Feature Registry (Ring 17)

| feature_id | Kind | Status | Enabled |
|---|---|---|---|
| tamagotchi_care_feature | organ | activation_blocked | false |
| kompoase_space_feature | organ | activation_blocked | false |
| sleep_cycle_feature | organ | activation_blocked | false |
| substance_modifiers_feature | organ | activation_blocked | false |
| dream_residue_feature | organ | activation_blocked | false |
| resonance_vacation_feature | organ | activation_blocked | false |
| metawar_space_feature | organ | activation_blocked | false |
| worldblick_readonly_export | worldblick | enabled | true |
| admin_control_plane | admin | enabled | true |
| deep_search_foundation | search | registered | false |
| import_gate | import | disabled | false |

## Admin Roles

| Role | Permissions |
|---|---|
| daniel_root | alle |
| operator | alle außer approve_activation, approve_import, slot.approve_activation |
| observer | nur view-Permissions |
| system_process | view + export.create_readonly |

## Erweiterter ConceptGuard (Ring 17)

Neue verbotene Muster:
- "Feature registriert heißt aktiv"
- "Blueprint ist aktivierbar"
- "AdminControl aktiviert Organe automatisch"
- "Worldblick darf Welt verändern"
- "ImportGate darf live importieren"
- "DeepSearch ist schon implementiert"
- "Operator darf ohne Daniel aktivieren"

## Was nie passieren darf (Ring 17)

- Keine echte Feature-Aktivierung
- Kein Organ aktivieren
- Keine UI
- Keine AI
- Kein Renderer
- Kein Postgres
- Kein Scheduler
- Kein Daemon
- Keine API
- Keine Datei-I/O
- Kein occupied-Status
