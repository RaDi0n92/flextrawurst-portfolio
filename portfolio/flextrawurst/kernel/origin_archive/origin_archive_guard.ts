import type { FlarumOriginArchive } from "./flarum_origin_archive.ts";

export interface OriginArchiveGuardResult {
  ok: boolean;
  can_create_events: false;
  can_activate_slots: false;
  can_create_residents: false;
  message: string;
}

export function checkOriginArchiveGuard(
  _archive: FlarumOriginArchive
): OriginArchiveGuardResult {
  return {
    ok: true,
    can_create_events: false,
    can_activate_slots: false,
    can_create_residents: false,
    message:
      "OriginArchive ist read-only. Keine Events, keine Slot-Aktivierung, keine Bewohner-Erzeugung.",
  };
}
