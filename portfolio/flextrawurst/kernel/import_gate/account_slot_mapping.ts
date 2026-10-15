import type { ForumImportBundle } from "./forum_import_candidate.ts";
import type { EntitySlot } from "../slots/entity_slot.ts";

export type MappingStatus =
  | "matched_canonical_slot"
  | "unmatched_account"
  | "ambiguous";

export type MappingConfidence = "structural" | "weak" | "none";

export interface AccountSlotMapping {
  account_id: string;
  slot_id: string | null;
  mapping_status: MappingStatus;
  confidence: MappingConfidence;
  notes: string[];
}

export function mapForumAccountsToSlots(
  bundle: ForumImportBundle,
  slots: EntitySlot[]
): AccountSlotMapping[] {
  const slotIndex = new Map<string, EntitySlot>();
  for (const slot of slots) {
    slotIndex.set(slot.slot_id, slot);
  }

  return bundle.accounts.map((account) => {
    const matchedSlot = slotIndex.get(account.account_id);

    if (matchedSlot) {
      return {
        account_id: account.account_id,
        slot_id: matchedSlot.slot_id,
        mapping_status: "matched_canonical_slot",
        confidence: "structural",
        notes: [
          `Account ${account.account_id} stimmt mit kanonischem Slot überein.`,
          "Mapping erzeugt keinen occupied-Status.",
          "Mapping erzeugt kein occupant_id.",
          "Mapping erzeugt keine activation_ready-Freigabe.",
        ],
      };
    }

    return {
      account_id: account.account_id,
      slot_id: null,
      mapping_status: "unmatched_account",
      confidence: "none",
      notes: [
        `Account ${account.account_id} hat keinen passenden kanonischen Slot.`,
        "Unbekannter Account bleibt ohne Slot-Zuordnung.",
      ],
    };
  });
}
