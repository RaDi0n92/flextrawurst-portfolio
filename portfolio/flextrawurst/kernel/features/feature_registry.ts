import type { FeatureFlag } from "./feature_flag.ts";

const ORGAN_FEATURES: FeatureFlag[] = [
  {
    feature_id: "tamagotchi_care_feature",
    label: "Cyberling-Pflegesystem",
    kind: "organ",
    status: "enabled",
    default_enabled: true,
    enabled: true,
    requires_daniel_approval: false,
    requires_concept_readiness: false,
    can_enable_now: true,
    blockers: [],
    source_blueprint_id: "blueprint_tamagotchi_care",
  },
  {
    feature_id: "kompoase_space_feature",
    label: "KompOase-Raumsystem",
    kind: "organ",
    status: "activation_blocked",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["concept_not_planned_by_daniel", "organ_blueprint_only"],
    source_blueprint_id: "blueprint_kompoase_space",
  },
  {
    feature_id: "sleep_cycle_feature",
    label: "Schlafzyklus-System",
    kind: "organ",
    status: "enabled",
    default_enabled: true,
    enabled: true,
    requires_daniel_approval: false,
    requires_concept_readiness: false,
    can_enable_now: true,
    blockers: [],
    source_blueprint_id: "blueprint_sleep_cycle",
  },
  {
    feature_id: "substance_modifiers_feature",
    label: "Substanz-Modifikationssystem",
    kind: "organ",
    status: "activation_blocked",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["concept_not_planned_by_daniel", "organ_blueprint_only"],
    source_blueprint_id: "blueprint_substance_modifiers",
  },
  {
    feature_id: "dream_residue_feature",
    label: "Traumreste-Artefaktsystem",
    kind: "organ",
    status: "activation_blocked",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["concept_not_planned_by_daniel", "organ_blueprint_only"],
    source_blueprint_id: "blueprint_dream_residue",
  },
  {
    feature_id: "resonance_vacation_feature",
    label: "Resonanzurlaub-Richtliniensystem",
    kind: "organ",
    status: "activation_blocked",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["concept_not_planned_by_daniel", "organ_blueprint_only"],
    source_blueprint_id: "blueprint_resonance_vacation",
  },
  {
    feature_id: "metawar_space_feature",
    label: "METAWAR-Konfliktraumsystem",
    kind: "organ",
    status: "activation_blocked",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["concept_not_planned_by_daniel", "organ_blueprint_only"],
    source_blueprint_id: "blueprint_metawar_space",
  },
];

const SYSTEM_FEATURES: FeatureFlag[] = [
  {
    feature_id: "worldblick_readonly_export",
    label: "Weltblick Nur-Lesen-Export",
    kind: "worldblick",
    status: "enabled",
    default_enabled: true,
    enabled: true,
    requires_daniel_approval: false,
    requires_concept_readiness: false,
    can_enable_now: true,
    blockers: [],
    source_blueprint_id: null,
  },
  {
    feature_id: "admin_control_plane",
    label: "Verwaltungs-Steuerungsebene",
    kind: "admin",
    status: "enabled",
    default_enabled: true,
    enabled: true,
    requires_daniel_approval: false,
    requires_concept_readiness: false,
    can_enable_now: true,
    blockers: [],
    source_blueprint_id: null,
  },
  {
    feature_id: "deep_search_foundation",
    label: "Diskursarchäologische Tiefensuche-Grundlage",
    kind: "search",
    status: "registered",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["ring_18_not_yet_built", "concept_not_planned_by_daniel"],
    source_blueprint_id: null,
  },
  {
    feature_id: "import_gate",
    label: "Live-Importschleuse",
    kind: "import",
    status: "disabled",
    default_enabled: false,
    enabled: false,
    requires_daniel_approval: true,
    requires_concept_readiness: true,
    can_enable_now: false,
    blockers: ["live_import_not_active", "concept_not_planned_by_daniel"],
    source_blueprint_id: null,
  },
];

const FULL_REGISTRY: FeatureFlag[] = [...ORGAN_FEATURES, ...SYSTEM_FEATURES];

export function buildFeatureRegistry(): FeatureFlag[] {
  return FULL_REGISTRY.map((f) => ({ ...f, blockers: [...f.blockers] }));
}

export function findFeatureFlag(feature_id: string): FeatureFlag | undefined {
  return FULL_REGISTRY.find((f) => f.feature_id === feature_id);
}

export function listDisabledFeatures(): FeatureFlag[] {
  return FULL_REGISTRY.filter(
    (f) =>
      f.status === "disabled" ||
      f.status === "activation_blocked" ||
      f.status === "deactivated"
  );
}

export function listBlockedFeatures(): FeatureFlag[] {
  return FULL_REGISTRY.filter(
    (f) => f.status === "activation_blocked" || f.blockers.length > 0
  );
}

export function listEnabledFeatures(): FeatureFlag[] {
  return FULL_REGISTRY.filter((f) => f.enabled === true);
}
