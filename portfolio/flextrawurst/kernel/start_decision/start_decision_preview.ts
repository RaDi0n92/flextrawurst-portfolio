import type { CleanStartDecisionModel } from "./clean_start_decision_model.ts";

export interface StartDecisionPreview {
  preview_id: string;
  decision: CleanStartDecisionModel;
  is_execution: false;
  creates_live_state: false;
  activates_slots: false;
  requires_admin_confirmation: true;
  preview_note: string;
}

export function buildStartDecisionPreview(
  preview_id: string,
  decision: CleanStartDecisionModel
): StartDecisionPreview {
  return {
    preview_id,
    decision,
    is_execution: false,
    creates_live_state: false,
    activates_slots: false,
    requires_admin_confirmation: true,
    preview_note:
      "StartDecisionPreview ist keine Startausführung. Es ist nur eine Vorschau möglicher sauberer Startformen.",
  };
}
