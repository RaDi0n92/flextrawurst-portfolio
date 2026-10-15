import type { MemoryPolicyKind } from "./clean_start_decision_model.ts";

export interface MemoryPolicyInfo {
  kind: MemoryPolicyKind;
  adopts_automatically: false;
  deletes_origin: false;
  is_preview_only: true;
  requires_start_decision: true;
  description: string;
}

const POLICY_DESCRIPTIONS: Record<MemoryPolicyKind, string> = {
  with_full_flarum_memory:
    "Alle Flarum-Herkunftsdaten werden als Kandidaten bereitgestellt. Keine automatische Übernahme.",
  without_flarum_memory:
    "Kein Flarum-Ursprung wird als Erinnerungskandidat geführt. Herkunft bleibt erhalten.",
  with_selected_memory:
    "Ausgewählte Erinnerungskandidaten werden bereitgestellt. Bleibt Preview.",
  reduced_roster_start:
    "Reduziertes Wesen-Roster bei Start. Keine Slots werden gelöscht.",
  undecided: "Keine Entscheidung getroffen. Start blockiert.",
};

export function describeMemoryPolicy(kind: MemoryPolicyKind): MemoryPolicyInfo {
  return {
    kind,
    adopts_automatically: false,
    deletes_origin: false,
    is_preview_only: true,
    requires_start_decision: true,
    description: POLICY_DESCRIPTIONS[kind],
  };
}

export function getAllMemoryPolicyInfos(): MemoryPolicyInfo[] {
  const kinds: MemoryPolicyKind[] = [
    "with_full_flarum_memory",
    "without_flarum_memory",
    "with_selected_memory",
    "reduced_roster_start",
    "undecided",
  ];
  return kinds.map(describeMemoryPolicy);
}
