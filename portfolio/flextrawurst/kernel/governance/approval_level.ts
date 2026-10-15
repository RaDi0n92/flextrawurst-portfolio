import type { GovernanceActionDefinition } from "./governance_action.ts";

export type ApprovalLevel =
  | "none"
  | "operator_allowed"
  | "daniel_required"
  | "daniel_required_with_dry_run";

export interface ApprovalRequirement {
  approval_level: ApprovalLevel;
  required_role: "observer" | "operator" | "daniel_root" | "system_process";
  dry_run_required: boolean;
  explanation: string;
}

export function getApprovalRequirementForAction(
  action: GovernanceActionDefinition
): ApprovalRequirement {
  if (
    action.action_class === "search_inspection" ||
    action.action_class === "concept_guard_report" ||
    action.action_class === "readonly_export"
  ) {
    return {
      approval_level: "none",
      required_role: "observer",
      dry_run_required: false,
      explanation: "Read-only action. All roles permitted with required permission.",
    };
  }

  if (
    action.action_id === "future_organ.activate" ||
    action.action_id === "policy.set"
  ) {
    return {
      approval_level: "daniel_required_with_dry_run",
      required_role: "daniel_root",
      dry_run_required: true,
      explanation: "Requires daniel_root with a prior dry run.",
    };
  }

  if (action.requires_daniel_root) {
    return {
      approval_level: "daniel_required",
      required_role: "daniel_root",
      dry_run_required: false,
      explanation: "Requires daniel_root role.",
    };
  }

  return {
    approval_level: "operator_allowed",
    required_role: "operator",
    dry_run_required: false,
    explanation: "Operator-level action.",
  };
}
