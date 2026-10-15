import type { FlarumOriginRecord } from "./flarum_origin_record.ts";
import type { FlarumSourceKind } from "./flarum_origin_record.ts";

export interface FlarumOriginArchive {
  archive_id: string;
  records: FlarumOriginRecord[];
  can_create_events: false;
  can_activate_slots: false;
  can_create_residents: false;
}

export function createFlarumOriginArchive(
  archive_id: string,
  records: FlarumOriginRecord[]
): FlarumOriginArchive {
  return {
    archive_id,
    records,
    can_create_events: false,
    can_activate_slots: false,
    can_create_residents: false,
  };
}

export function queryArchiveBySlot(
  archive: FlarumOriginArchive,
  slot_id: string
): FlarumOriginRecord[] {
  return archive.records.filter((r) => r.canonical_slot_id === slot_id);
}

export function queryArchiveBySourceKind(
  archive: FlarumOriginArchive,
  source_kind: FlarumSourceKind
): FlarumOriginRecord[] {
  return archive.records.filter((r) => r.source_kind === source_kind);
}

export function queryMemoryCandidates(
  archive: FlarumOriginArchive
): FlarumOriginRecord[] {
  return archive.records.filter((r) => r.is_memory_candidate);
}
