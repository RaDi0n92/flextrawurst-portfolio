import type { ForumImportBundle } from "./forum_import_candidate.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";
import type { AccountSlotMapping } from "./account_slot_mapping.ts";
import { mapForumAccountsToSlots } from "./account_slot_mapping.ts";

export interface ImportDryRunReport {
  bundle_id: string;
  source_type: string;
  account_count: number;
  discussion_count: number;
  post_count: number;
  mappings: AccountSlotMapping[];
  mapped_count: number;
  unmapped_count: number;
  would_create_events: boolean;
  would_activate_slots: boolean;
  warnings: string[];
  notes: string[];
}

export function runImportDryRun(
  bundle: ForumImportBundle,
  slots: EntitySlot[]
): ImportDryRunReport {
  const mappings = mapForumAccountsToSlots(bundle, slots);
  const mapped = mappings.filter(
    (m) => m.mapping_status === "matched_canonical_slot"
  );
  const unmapped = mappings.filter(
    (m) => m.mapping_status !== "matched_canonical_slot"
  );

  return {
    bundle_id: bundle.bundle_id,
    source_type: bundle.source_type,
    account_count: bundle.accounts.length,
    discussion_count: bundle.discussions.length,
    post_count: bundle.posts.length,
    mappings,
    mapped_count: mapped.length,
    unmapped_count: unmapped.length,
    would_create_events: false,
    would_activate_slots: false,
    warnings: [
      "Import-Kandidat ist kein Einzug.",
      "Forum-Account ist kein Bewohner.",
      "Dieser Dry Run schreibt keine Events.",
      "Dieser Dry Run aktiviert keine Slots.",
    ],
    notes: [
      "Dry Run für Ring 4. Nur Prüfung, kein Schreiben.",
      `${mapped.length} von ${bundle.accounts.length} Accounts auf kanonische Slots gemappt.`,
      `${unmapped.length} Accounts ohne Slot-Zuordnung.`,
      "would_create_events: false (strukturell erzwungen für Ring 4).",
      "would_activate_slots: false (strukturell erzwungen für Ring 4).",
    ],
  };
}
