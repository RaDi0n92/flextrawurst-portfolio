export type FlarumSourceKind =
  | "flarum_discussion"
  | "flarum_post"
  | "flarum_account"
  | "flarum_export";

export interface FlarumOriginRecord {
  origin_record_id: string;
  origin_layer: "flarum_vorphase";
  source_kind: FlarumSourceKind;
  source_id: string;
  source_author: string;
  source_created_at: string;
  raw_title: string | null;
  raw_excerpt: string;
  canonical_slot_id: string | null;
  is_live_flextrawurst_state: false;
  is_memory_candidate: boolean;
  is_identity_final: boolean;
  requires_start_decision: true;
  can_create_events: false;
  can_activate_slots: false;
}

export function createFlarumOriginRecord(params: {
  origin_record_id: string;
  source_kind: FlarumSourceKind;
  source_id: string;
  source_author: string;
  source_created_at: string;
  raw_title?: string;
  raw_excerpt: string;
  canonical_slot_id?: string;
  is_memory_candidate?: boolean;
  is_identity_final?: boolean;
}): FlarumOriginRecord {
  return {
    origin_record_id: params.origin_record_id,
    origin_layer: "flarum_vorphase",
    source_kind: params.source_kind,
    source_id: params.source_id,
    source_author: params.source_author,
    source_created_at: params.source_created_at,
    raw_title: params.raw_title ?? null,
    raw_excerpt: params.raw_excerpt,
    canonical_slot_id: params.canonical_slot_id ?? null,
    is_live_flextrawurst_state: false,
    is_memory_candidate: params.is_memory_candidate ?? true,
    is_identity_final: params.is_identity_final ?? false,
    requires_start_decision: true,
    can_create_events: false,
    can_activate_slots: false,
  };
}

export const ALL_SOURCE_KINDS: FlarumSourceKind[] = [
  "flarum_discussion",
  "flarum_post",
  "flarum_account",
  "flarum_export",
];
