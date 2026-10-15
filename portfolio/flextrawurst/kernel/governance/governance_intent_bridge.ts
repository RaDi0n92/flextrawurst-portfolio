import type { CommandIntent } from "../admin/command_intent.ts";

export interface GovernanceIntentBridgeResult {
  command_id: string;
  action_id: string;
  mapped: boolean;
  notes: string[];
}

const COMMAND_TO_ACTION: Record<string, string> = {
  request_feature_activation: "feature.activate",
  approve_feature_activation: "feature.activate",
  deactivate_feature: "feature.deactivate",
  pause_worldrun: "worldrun.pause",
  resume_worldrun: "worldrun.resume",
  freeze_worldrun: "worldrun.freeze",
  stop_worldrun: "worldrun.stop",
  approve_import: "import.approve",
  create_readonly_export: "export.create_readonly",
  set_policy: "policy.set",
};

export function mapCommandIntentToGovernanceAction(
  command: CommandIntent
): GovernanceIntentBridgeResult {
  const action_id = COMMAND_TO_ACTION[command.command_type];
  if (!action_id) {
    return {
      command_id: command.command_id,
      action_id: "",
      mapped: false,
      notes: [`unknown command_type: ${command.command_type}`],
    };
  }
  return {
    command_id: command.command_id,
    action_id,
    mapped: true,
    notes: [`mapped ${command.command_type} → ${action_id}`],
  };
}
