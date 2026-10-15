import type { ForumImportBundle } from "./forum_import_candidate.ts";
import type { AccountSlotMapping } from "./account_slot_mapping.ts";
import type { ProvenanceRecord } from "../provenance/provenance_record.ts";

export interface PostToSlotLink {
  post_id: string;
  account_id: string;
  slot_id: string | null;
  provenance_type: "flarum_import_candidate";
}

export interface ImportProvenancePreview {
  preview_id: string;
  bundle_id: string;
  provenance_records: ProvenanceRecord[];
  post_to_slot_links: PostToSlotLink[];
}

export function buildImportProvenancePreview(
  bundle: ForumImportBundle,
  mappings: AccountSlotMapping[]
): ImportProvenancePreview {
  const mappingIndex = new Map<string, AccountSlotMapping>();
  for (const m of mappings) {
    mappingIndex.set(m.account_id, m);
  }

  const provenance_records: ProvenanceRecord[] = bundle.accounts.map(
    (account) => ({
      record_id: `prov-import-account-${account.account_id}`,
      subject_type: "entity_slot" as const,
      subject_id: account.account_id,
      provenance_type: "flarum_import_candidate" as const,
      origin_label: bundle.source_label,
      source_event_ids: [],
      confidence: "imported" as const,
      notes: [
        "Flarum-Import-Kandidat. Kein Live-Wesen. Kein Einzug.",
        "Importierter Ursprung bleibt Ursprung.",
        "Er wird nicht rückwirkend zur aktuellen Live-Handlung.",
      ],
    })
  );

  const post_to_slot_links: PostToSlotLink[] = bundle.posts.map((post) => {
    const mapping = mappingIndex.get(post.author_account_id);
    return {
      post_id: post.post_id,
      account_id: post.author_account_id,
      slot_id: mapping?.slot_id ?? null,
      provenance_type: "flarum_import_candidate",
    };
  });

  return {
    preview_id: `preview-${bundle.bundle_id}`,
    bundle_id: bundle.bundle_id,
    provenance_records,
    post_to_slot_links,
  };
}
