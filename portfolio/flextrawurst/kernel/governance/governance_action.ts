export type GovernanceActionClass =
  | "feature_activation"
  | "feature_deactivation"
  | "import_approval"
  | "slot_activation"
  | "worldrun_control"
  | "readonly_export"
  | "concept_guard_report"
  | "policy_setting"
  | "future_organ_activation"
  | "search_inspection"
  | "emergency_stop"
  | "global_lock";

export type GovernanceRiskLevel =
  | "low"
  | "medium"
  | "high"
  | "critical";

export interface GovernanceActionDefinition {
  action_id: string;
  action_class: GovernanceActionClass;
  label: string;
  risk_level: GovernanceRiskLevel;
  required_permission: string;
  requires_daniel_root: boolean;
  requires_dry_run_first: boolean;
  requires_command_intent: boolean;
  requires_ledger_entry: boolean;
  requires_audit_entry: boolean;
  requires_search_document: boolean;
  blocked_by_global_lock: boolean;
  notes: string[];
}

export function buildGovernanceActionDefinitions(): GovernanceActionDefinition[] {
  return [
    {
      action_id: "feature.activate",
      action_class: "feature_activation",
      label: "Feature aktivieren",
      risk_level: "high",
      required_permission: "feature.approve_activation",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: ["Nur daniel_root. Approval Level 3."],
    },
    {
      action_id: "feature.deactivate",
      action_class: "feature_deactivation",
      label: "Feature deaktivieren",
      risk_level: "high",
      required_permission: "feature.deactivate",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Deaktivierung ist keine Löschung."],
    },
    {
      action_id: "import.approve",
      action_class: "import_approval",
      label: "Import freigeben",
      risk_level: "high",
      required_permission: "import.approve",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: ["Operator darf freigeben, aber kein Organ aktivieren."],
    },
    {
      action_id: "slot.approve_activation",
      action_class: "slot_activation",
      label: "Slot-Aktivierung freigeben",
      risk_level: "high",
      required_permission: "slot.approve_activation",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: [],
    },
    {
      action_id: "worldrun.pause",
      action_class: "worldrun_control",
      label: "WorldRun pausieren",
      risk_level: "medium",
      required_permission: "worldrun.pause",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Operator erlaubt. Approval Level 1."],
    },
    {
      action_id: "worldrun.resume",
      action_class: "worldrun_control",
      label: "WorldRun fortsetzen",
      risk_level: "medium",
      required_permission: "worldrun.resume",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: ["Bei GlobalLock blockiert. Approval Level 1."],
    },
    {
      action_id: "worldrun.freeze",
      action_class: "worldrun_control",
      label: "WorldRun einfrieren",
      risk_level: "high",
      required_permission: "worldrun.freeze",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Emergency-Variante möglich. Approval Level 3."],
    },
    {
      action_id: "worldrun.stop",
      action_class: "worldrun_control",
      label: "WorldRun stoppen",
      risk_level: "critical",
      required_permission: "worldrun.stop",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Terminaler Zustand. Kein Rollback ohne expliziten Start."],
    },
    {
      action_id: "worldrun.lock",
      action_class: "worldrun_control",
      label: "WorldRun sperren",
      risk_level: "critical",
      required_permission: "worldrun.freeze",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Relation zu Global Lock. Approval Level 3."],
    },
    {
      action_id: "export.create_readonly",
      action_class: "readonly_export",
      label: "Read-only Export erstellen",
      risk_level: "low",
      required_permission: "export.create_readonly",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: false,
      requires_ledger_entry: false,
      requires_audit_entry: false,
      requires_search_document: false,
      blocked_by_global_lock: false,
      notes: ["Read-only. Keine Audit-Pflicht."],
    },
    {
      action_id: "concept_guard.report",
      action_class: "concept_guard_report",
      label: "ConceptGuard Report",
      risk_level: "low",
      required_permission: "concept_guard.view",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: false,
      requires_ledger_entry: false,
      requires_audit_entry: false,
      requires_search_document: false,
      blocked_by_global_lock: false,
      notes: ["Nur Report. Kein Override."],
    },
    {
      action_id: "policy.set",
      action_class: "policy_setting",
      label: "Policy setzen",
      risk_level: "high",
      required_permission: "policy.set",
      requires_daniel_root: true,
      requires_dry_run_first: true,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: ["Nie still. Dry-Run empfohlen. Approval Level 3."],
    },
    {
      action_id: "future_organ.activate",
      action_class: "future_organ_activation",
      label: "Future-Organ aktivieren",
      risk_level: "critical",
      required_permission: "governance.future_organ_activate",
      requires_daniel_root: true,
      requires_dry_run_first: true,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: true,
      notes: ["Immer critical. Nur daniel_root. Dry-Run zuerst."],
    },
    {
      action_id: "search.inspect",
      action_class: "search_inspection",
      label: "Search Inspection",
      risk_level: "low",
      required_permission: "export.view",
      requires_daniel_root: false,
      requires_dry_run_first: false,
      requires_command_intent: false,
      requires_ledger_entry: false,
      requires_audit_entry: false,
      requires_search_document: false,
      blocked_by_global_lock: false,
      notes: ["Read-only. Alle Rollen mit Permission erlaubt."],
    },
    {
      action_id: "emergency.stop",
      action_class: "emergency_stop",
      label: "Emergency Stop",
      risk_level: "critical",
      required_permission: "worldrun.stop",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Darf immer ausgeführt werden, auch bei GlobalLock."],
    },
    {
      action_id: "global.lock",
      action_class: "global_lock",
      label: "Global Lock aktivieren",
      risk_level: "critical",
      required_permission: "governance.global_lock",
      requires_daniel_root: true,
      requires_dry_run_first: false,
      requires_command_intent: true,
      requires_ledger_entry: true,
      requires_audit_entry: true,
      requires_search_document: true,
      blocked_by_global_lock: false,
      notes: ["Kann nicht doppelt aktiviert werden. Nur daniel_root."],
    },
  ];
}
