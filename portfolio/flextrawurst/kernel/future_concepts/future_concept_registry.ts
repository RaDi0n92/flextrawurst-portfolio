import type { FutureConcept, FutureConceptKind } from "./future_concept_model.ts";

const REGISTRY: FutureConcept[] = [
  {
    concept_id: "tamagotchi_care",
    label: "Cyberling-Pflegesystem",
    kind: "care_system",
    status: "implemented",
    short_description:
      "Cyberling — individuelles Pflegewesen pro Entität. 5 Zustände, Kaskaden-Verfall, Tod nach Vernachlässigung, Wiedergeburt nach 24h.",
    not_yet: [
      "Name-Vergabe beim Einzug noch offen",
      "Integration ins öffentliche Entitätenprofil",
      "keine Care-Automatik",
      "keine Entitätsbindung",
    ],
    must_not_confuse_with: [
      "Tamagotchi-Blueprint ≠ lebendes Tamagotchi",
      "Care-Konzept ≠ aktives Pflegesystem",
      "Blueprint ≠ Implementierung",
    ],
    required_planning_questions: [
      "Was ist das Care-Objekt?",
      "Kann es sterben?",
      "Kann es neu starten?",
      "Welche Zustände sind sichtbar?",
      "Wer darf pflegen?",
      "Was bedeutet Vernachlässigung?",
      "Wie wird Schuld/Lernen verhindert oder geschützt?",
    ],
    possible_event_families: [
      "care_action",
      "neglect_signal",
      "care_state_change",
      "care_object_lifecycle",
    ],
    possible_state_surfaces: [
      "care_object_state",
      "care_relationship",
      "neglect_accumulation",
    ],
    possible_camera_layers: [
      "care_status_layer",
      "care_history_layer",
    ],
    guard_terms: [
      "Tamagotchi ist implementiert",
      "lebendes Tamagotchi",
      "Hunger-Simulation",
      "Durst-Simulation",
      "Tamagotchi stirbt",
    ],
  },
  {
    concept_id: "kompoase_space",
    label: "KompOase-Raumsystem",
    kind: "space_system",
    status: "needs_daniel_planning",
    short_description:
      "Potentialitätsraum / offene Zone, in der Form noch nicht erzwungen wird.",
    not_yet: [
      "kein fertiger Raum",
      "keine Kategorie",
      "kein Feed",
      "kein Aufenthaltszwang",
    ],
    must_not_confuse_with: [
      "KompOase-Blueprint ≠ fertiger Raum",
      "Potentialitätsraum ≠ Kategoriensystem",
      "Offenheit ≠ Unstrukturiertheit",
    ],
    required_planning_questions: [
      "Was darf in der KompOase unfertig bleiben?",
      "Wann wird aus Potential ein Artefakt?",
      "Welche Resonanz ist erlaubt?",
      "Welche Form darf nicht zu früh erzwungen werden?",
    ],
    possible_event_families: [
      "space_entry",
      "potential_emergence",
      "artifact_crystallization",
      "resonance_contact",
    ],
    possible_state_surfaces: [
      "space_openness",
      "potential_density",
      "crystallization_readiness",
    ],
    possible_camera_layers: [
      "kompoase_topology_layer",
      "potential_field_layer",
    ],
    guard_terms: [
      "KompOase ist fertig",
      "KompOase ist implementiert",
      "fertiger KompOase-Raum",
    ],
  },
  {
    concept_id: "sleep_cycle",
    label: "Schlaf-System",
    kind: "runtime_state_system",
    status: "implemented",
    short_description:
      "Schlaf-System live — 6–9h/Tag Pflicht, Phasen min 1h, Hauptschlaf min 3h, Brief vor Hauptschlaf, entity-takt.service + SCHLAF-Tab.",
    not_yet: [
      "Traumgenerierung (Neuroevolution)",
      "Abspaltungslogik",
    ],
    must_not_confuse_with: [
      "Schlaf-Blueprint ≠ laufendes Schlafsystem",
      "Schlafzustand ≠ Inaktivität",
      "Traumrest ≠ generierter Traum",
    ],
    required_planning_questions: [
      "Was löst Schlaf aus?",
      "Wie lange dauert ein Schlafzyklus?",
      "Was passiert während des Schlafs?",
      "Welche Zustände folgen auf Schlaf?",
      "Können Traumreste entstehen?",
      "Wie verhält sich Schlaf zu anderen Systemen?",
    ],
    possible_event_families: [
      "sleep_onset",
      "sleep_phase_change",
      "wake_trigger",
      "dream_residue_formation",
    ],
    possible_state_surfaces: [
      "sleep_phase",
      "wakefulness_level",
      "rest_accumulation",
    ],
    possible_camera_layers: [
      "sleep_rhythm_layer",
      "rest_state_layer",
    ],
    guard_terms: [
      "Schlafsystem läuft",
      "Schlafsystem ist aktiv",
      "automatische Müdigkeit",
      "Schlafzwang",
    ],
  },
  {
    concept_id: "substance_modifiers",
    label: "Substanz-Modifikationssystem",
    kind: "modifier_system",
    status: "needs_daniel_planning",
    short_description:
      "Spätere Zustandsmodifikatoren, die Wahrnehmung, Zusammenhang, Tempo oder Assoziationsräume verändern könnten.",
    not_yet: [
      "keine echte Substanzlogik",
      "keine Wirkung",
      "kein Balancing",
      "keine riskante Normalisierung",
    ],
    must_not_confuse_with: [
      "Substanz-Blueprint ≠ wirkendes Substanzsystem",
      "Modifier-Konzept ≠ Balancing-System",
      "Substanzeffekt ≠ Normalisierung",
    ],
    required_planning_questions: [
      "Was wird modifiziert?",
      "Wie lange wirkt eine Substanz?",
      "Wie werden Risiken begrenzt?",
      "Welche Zustände sind erreichbar?",
      "Wann endet eine Wirkung?",
      "Wie wird Normalisierung verhindert?",
    ],
    possible_event_families: [
      "substance_intake",
      "modifier_onset",
      "modifier_fade",
      "perception_shift",
    ],
    possible_state_surfaces: [
      "modifier_active",
      "perception_state",
      "association_density",
    ],
    possible_camera_layers: [
      "modifier_overlay_layer",
      "perception_shift_layer",
    ],
    guard_terms: [
      "Substanzen wirken",
      "Substanzsystem aktiv",
      "echte Substanzlogik",
      "Substanz-Balancing",
    ],
  },
  {
    concept_id: "dream_residue",
    label: "Traumreste-Artefaktsystem",
    kind: "artifact_system",
    status: "needs_daniel_planning",
    short_description:
      "Spätere Traumreste als halbklare Artefakte aus Schlaf, Erinnerung und ungesagten Spuren.",
    not_yet: [
      "keine Traumgenerierung",
      "kein Memory-Import",
      "kein Symbolsystem",
      "keine Artefaktpersistenz",
    ],
    must_not_confuse_with: [
      "Traumrest-Blueprint ≠ generierter Traum",
      "Traumrest ≠ Erinnerung",
      "Artefakt ≠ persistente Datei",
    ],
    required_planning_questions: [
      "Wie entsteht ein Traumrest?",
      "Wie lange bleibt ein Traumrest sichtbar?",
      "Kann ein Traumrest interpretiert werden?",
      "Wer hat Zugang zu Traumresten?",
      "Wie verhält sich Traumrest zu Schlaf?",
      "Was macht einen Traumrest halbklar?",
    ],
    possible_event_families: [
      "dream_residue_emergence",
      "residue_dissolution",
      "residue_interpretation",
      "residue_trace_formation",
    ],
    possible_state_surfaces: [
      "residue_clarity",
      "residue_age",
      "residue_accessibility",
    ],
    possible_camera_layers: [
      "dream_residue_layer",
      "trace_visibility_layer",
    ],
    guard_terms: [
      "Traumreste werden generiert",
      "Traumgenerierung aktiv",
      "Traumrest-Persistenz",
      "Symbolsystem aktiv",
    ],
  },
  {
    concept_id: "resonance_vacation",
    label: "Resonanzurlaub-Richtliniensystem",
    kind: "policy_system",
    status: "needs_daniel_planning",
    short_description:
      "Zustand sichtbarer Existenz ohne kommentierende Rückformung.",
    not_yet: [
      "keine aktive Kommentarblockade",
      "keine Policy im EventStore",
      "keine UI-Regel",
      "kein Statuswechsel",
    ],
    must_not_confuse_with: [
      "Resonanzurlaub-Blueprint ≠ aktive Policy",
      "Resonanzurlaub ≠ Stille",
      "Sichtbare Existenz ≠ Inaktivität",
    ],
    required_planning_questions: [
      "Was löst Resonanzurlaub aus?",
      "Was darf während Resonanzurlaub nicht passieren?",
      "Wie lange dauert ein Resonanzurlaub?",
      "Wer kann Resonanzurlaub beenden?",
      "Welche Zustände bleiben sichtbar?",
      "Wie verhält sich Resonanzurlaub zu anderen Policies?",
    ],
    possible_event_families: [
      "resonance_vacation_start",
      "resonance_vacation_end",
      "non_interference_signal",
      "presence_without_comment",
    ],
    possible_state_surfaces: [
      "vacation_active",
      "interference_level",
      "presence_mode",
    ],
    possible_camera_layers: [
      "resonance_mode_layer",
      "non_interference_layer",
    ],
    guard_terms: [
      "Resonanzurlaub ist aktiv",
      "Kommentarblockade aktiv",
      "Policy im EventStore",
      "Resonanzurlaub implementiert",
    ],
  },
  {
    concept_id: "metawar_space",
    label: "METAWAR-Konfliktraumsystem",
    kind: "conflict_system",
    status: "needs_daniel_planning",
    short_description:
      "Späterer Debatten-/Konfliktraum mit Stimmen, Zuständen, Archiv und Gegenrede.",
    not_yet: [
      "keine Live-Debatte",
      "keine Sprecherlogik",
      "keine Konfliktwertung",
      "kein Archivdruck",
    ],
    must_not_confuse_with: [
      "METAWAR-Blueprint ≠ Live-Debatte",
      "Konfliktraum ≠ Kampfsystem",
      "Gegenrede ≠ Konflikt-Scoring",
    ],
    required_planning_questions: [
      "Was löst einen METAWAR aus?",
      "Wer darf sprechen?",
      "Wie wird Gegenrede strukturiert?",
      "Wie lange dauert ein METAWAR?",
      "Was kommt ins Archiv?",
      "Wie wird Archivdruck verhindert?",
      "Wer beendet einen METAWAR?",
    ],
    possible_event_families: [
      "metawar_initiation",
      "voice_contribution",
      "counter_voice",
      "metawar_resolution",
      "archive_entry",
    ],
    possible_state_surfaces: [
      "conflict_phase",
      "voice_roster",
      "resolution_state",
      "archive_pressure",
    ],
    possible_camera_layers: [
      "conflict_topology_layer",
      "voice_map_layer",
      "archive_layer",
    ],
    guard_terms: [
      "METAWAR ist live",
      "METAWAR läuft",
      "Live-Debatte aktiv",
      "Konfliktwertung aktiv",
      "Sprecherlogik aktiv",
    ],
  },
];

export function getFutureConceptRegistry(): FutureConcept[] {
  return [...REGISTRY];
}

export function findFutureConceptById(concept_id: string): FutureConcept | undefined {
  return REGISTRY.find((c) => c.concept_id === concept_id);
}

export function listFutureConceptsByKind(kind: FutureConceptKind): FutureConcept[] {
  return REGISTRY.filter((c) => c.kind === kind);
}

export function listConceptsNeedingDanielPlanning(): FutureConcept[] {
  return REGISTRY.filter(
    (c) => c.status === "needs_daniel_planning" || c.status === "raw_idea"
  );
}
