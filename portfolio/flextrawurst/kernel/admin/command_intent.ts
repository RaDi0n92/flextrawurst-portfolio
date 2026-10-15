export type CommandIntentType =
  | "request_feature_activation"
  | "approve_feature_activation"
  | "deactivate_feature"
  | "pause_worldrun"
  | "resume_worldrun"
  | "freeze_worldrun"
  | "stop_worldrun"
  | "approve_import"
  | "create_readonly_export"
  | "set_policy";

export interface CommandIntent {
  command_id: string;
  command_type: CommandIntentType;
  requested_by: string;
  target_type:
    | "feature"
    | "organ"
    | "import_bundle"
    | "slot"
    | "worldrun"
    | "export"
    | "policy";
  target_id: string;
  reason: string;
  created_at: string;
  dry_run: boolean;
}

export interface CreateCommandIntentParams {
  command_id: string;
  command_type: CommandIntentType;
  requested_by: string;
  target_type: CommandIntent["target_type"];
  target_id: string;
  reason: string;
  created_at: string;
}

export function createCommandIntent(
  params: CreateCommandIntentParams
): CommandIntent {
  return {
    command_id: params.command_id,
    command_type: params.command_type,
    requested_by: params.requested_by,
    target_type: params.target_type,
    target_id: params.target_id,
    reason: params.reason,
    created_at: params.created_at,
    dry_run: true,
  };
}
