import type { RosterPolicyKind } from "./clean_start_decision_model.ts";

export interface RosterPolicyInfo {
  kind: RosterPolicyKind;
  deletes_slots: false;
  activates_slots: false;
  is_preview_only: true;
  requires_start_decision: true;
  description: string;
}

const ROSTER_DESCRIPTIONS: Record<RosterPolicyKind, string> = {
  all_six: "Alle sechs Wesen-Slots werden berücksichtigt.",
  selected_four: "Vier ausgewählte Slots werden berücksichtigt.",
  selected_three: "Drei ausgewählte Slots werden berücksichtigt.",
  manual_selection: "Manuelle Auswahl der Slots. Noch nicht vollzogen.",
  undecided: "Keine Roster-Entscheidung getroffen. Start blockiert.",
};

export function describeRosterPolicy(kind: RosterPolicyKind): RosterPolicyInfo {
  return {
    kind,
    deletes_slots: false,
    activates_slots: false,
    is_preview_only: true,
    requires_start_decision: true,
    description: ROSTER_DESCRIPTIONS[kind],
  };
}

export function getAllRosterPolicyInfos(): RosterPolicyInfo[] {
  const kinds: RosterPolicyKind[] = [
    "all_six",
    "selected_four",
    "selected_three",
    "manual_selection",
    "undecided",
  ];
  return kinds.map(describeRosterPolicy);
}
