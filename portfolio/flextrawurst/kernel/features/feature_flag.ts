export type FeatureKind =
  | "organ"
  | "import"
  | "runtime"
  | "export"
  | "policy"
  | "search"
  | "worldblick"
  | "admin";

export type FeatureStatus =
  | "registered"
  | "disabled"
  | "activation_requested"
  | "activation_blocked"
  | "enabled"
  | "deactivated";

export interface FeatureFlag {
  feature_id: string;
  label: string;
  kind: FeatureKind;
  status: FeatureStatus;
  default_enabled: boolean;
  enabled: boolean;
  requires_daniel_approval: boolean;
  requires_concept_readiness: boolean;
  can_enable_now: boolean;
  blockers: string[];
  source_blueprint_id: string | null;
}
