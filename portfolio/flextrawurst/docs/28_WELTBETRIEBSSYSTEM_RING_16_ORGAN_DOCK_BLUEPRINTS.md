# Ring 16 — Organ-Dock + Future Concept Registry + Expansion Blueprint System

## Was Ring 16 baut

Ring 16 baut keine Features.
Ring 16 baut Andockstellen für spätere Weltorgane.

Tamagotchi, KompOase, Schlaf, Substanzen, Traumreste, Resonanzurlaub und METAWAR bleiben Blueprint-Kandidaten.

Jeder spätere Organ-Bau braucht zuerst:
- Begriffsklärung
- Grenzen
- Nicht-Verwechslungen
- Eventtypen
- Zustandsflächen
- Projektionen
- Kamera-Anschluss
- Audit-Anschluss
- ConceptGuard-Regeln
- Tests

## Leitanker

Große Ideen werden nicht vorzeitig implementiert.
Sie bekommen zuerst einen eigenen Organ-Plan:
Begriff → Grenzen → Eventtypen → Zustände → Projektionen → Kamera → Audit → Guard → Tests.

## Schutzformeln

- Blueprint ≠ Implementierung
- Organ-Dock ≠ aktives Organ
- Tamagotchi-Blueprint ≠ lebendes Tamagotchi
- KompOase-Blueprint ≠ fertiger Raum
- Substanz-Blueprint ≠ Substanzsystem
- Sleep-Blueprint ≠ Schlafsimulation
- METAWAR-Blueprint ≠ Live-Debatte
- Resonanzurlaub-Blueprint ≠ aktive Policy

## Registrierte Blueprint-Konzepte

| concept_id | Label | Kind | Status |
|---|---|---|---|
| tamagotchi_care | Tamagotchi Care System | care_system | needs_daniel_planning |
| kompoase_space | KompOase Space System | space_system | needs_daniel_planning |
| sleep_cycle | Sleep Cycle System | runtime_state_system | needs_daniel_planning |
| substance_modifiers | Substance Modifier System | modifier_system | needs_daniel_planning |
| dream_residue | Dream Residue Artifact System | artifact_system | needs_daniel_planning |
| resonance_vacation | Resonance Vacation Policy System | policy_system | needs_daniel_planning |
| metawar_space | METAWAR Conflict Space System | conflict_system | needs_daniel_planning |

## Was nie passieren darf (Ring 16)

- Kein Tamagotchi implementieren
- Keine KompOase implementieren
- Kein Schlafsystem implementieren
- Keine Substanzlogik implementieren
- Keine Traumgenerierung implementieren
- Keinen Resonanzurlaub aktivieren
- Kein METAWAR starten
- Keine UI
- Keine AI
- Kein Renderer
- Kein Postgres
- Kein Scheduler
- Kein Daemon
- Keine Datei-I/O
- Kein occupied-Status

## Neue Dateien (Ring 16)

```
kernel/future_concepts/future_concept_model.ts
kernel/future_concepts/future_concept_registry.ts
kernel/organ_dock/organ_blueprint.ts
kernel/organ_dock/organ_dock.ts
kernel/organ_dock/organ_readiness.ts
kernel/organ_dock/organ_dock_inspection.ts
kernel/organ_dock/organ_dock_export.ts
tests/world_os_ring_16_organ_dock_blueprints.test.ts
```

## Erweiterter ConceptGuard

Neu erkannte verbotene Muster:
- "Tamagotchi ist implementiert"
- "KompOase ist fertig"
- "Schlafsystem läuft"
- "Substanzen wirken"
- "Traumreste werden generiert"
- "Resonanzurlaub ist aktiv"
- "METAWAR ist live"
- "Blueprint ist Feature"
- "OrganDock implementiert Organe"

Erlaubte Sprache:
- Tamagotchi-Blueprint
- KompOase-Blueprint
- Schlaf-Blueprint
- Substanz-Blueprint
- Traumrest-Blueprint
- Resonanzurlaub-Blueprint
- METAWAR-Blueprint
- Organ-Dock
- Anschlussstruktur
