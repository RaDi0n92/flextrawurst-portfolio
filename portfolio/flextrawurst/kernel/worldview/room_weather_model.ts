import type { WorldOSSpine } from "../os_spine/world_os_spine.ts";
import type { WorldOSSpineImportExtension } from "../os_spine/world_os_spine_import_extension.ts";

export interface RoomWeather {
  room_id: string;
  density: number;
  activity: number;
  silence: number;
  tension: number;
  origin_pressure: number;
  import_presence: number;
  live_presence: number;
  explanation: string;
}

export function buildRoomWeather(
  roomId: string,
  spine: WorldOSSpine,
  importExtension: WorldOSSpineImportExtension
): RoomWeather {
  const slotCount = spine.slots.length;
  const importedCount = importExtension.dry_run.mapped_count;
  const tickCount = spine.runtime_readiness.tick_count;

  const density = slotCount > 0 ? Math.min(1.0, slotCount / 10.0) : 0;
  const activity = tickCount > 0 ? Math.min(1.0, tickCount / 10.0) : 0;
  const silence = Math.max(0, 1.0 - activity);
  const tension = importedCount > 0 ? 0.2 : 0.0;
  const origin_pressure =
    importedCount > 0 && slotCount > 0 ? importedCount / slotCount : 0;
  const import_presence = importedCount > 0 ? 1.0 : 0;
  const live_presence = 0.0;

  return {
    room_id: roomId,
    density,
    activity,
    silence,
    tension,
    origin_pressure,
    import_presence,
    live_presence,
    explanation:
      `Raum ${roomId}: ${slotCount} Slots, ${importedCount} Import-Kandidaten. ` +
      `Keine aktiven Bewohner. live_presence: 0. ` +
      `Flarum-Herkunft: ${importedCount > 0 ? "vorhanden" : "keine"}. ` +
      `Keine Aktivierung.`,
  };
}

export function buildDefaultRoomWeather(
  spine: WorldOSSpine,
  importExtension: WorldOSSpineImportExtension
): RoomWeather {
  return buildRoomWeather("room-world-main", spine, importExtension);
}
