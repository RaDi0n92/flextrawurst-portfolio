export const ZOOM_LEVEL_KINDS = [
  "cosmos",
  "room",
  "entity",
  "post_or_event",
  "raw_event",
  "provenance",
] as const;

export type ZoomLevelKind = (typeof ZOOM_LEVEL_KINDS)[number];

export interface WorldviewZoomLevel {
  kind: ZoomLevelKind;
  label: string;
  index: number;
  description: string;
  shows_renderer: false;
}

export interface WorldviewZoomModel {
  levels: WorldviewZoomLevel[];
  default_level: ZoomLevelKind;
}

export function buildWorldviewZoomModel(): WorldviewZoomModel {
  const levels: WorldviewZoomLevel[] = [
    {
      kind: "cosmos",
      label: "Kosmos",
      index: 0,
      description: "Gesamtüberblick aller Räume und Slots.",
      shows_renderer: false,
    },
    {
      kind: "room",
      label: "Raum",
      index: 1,
      description: "Einzelner Weltraum mit seinen Slots.",
      shows_renderer: false,
    },
    {
      kind: "entity",
      label: "Entität",
      index: 2,
      description: "Einzelner Entitätsslot mit Herkunft und Spur.",
      shows_renderer: false,
    },
    {
      kind: "post_or_event",
      label: "Beitrag / Ereignis",
      index: 3,
      description: "Einzelnes Event oder importierter Post.",
      shows_renderer: false,
    },
    {
      kind: "raw_event",
      label: "Rohereignis",
      index: 4,
      description: "Rohe Event-Daten ohne Interpretation.",
      shows_renderer: false,
    },
    {
      kind: "provenance",
      label: "Provenienz",
      index: 5,
      description: "Herkunftskette eines Knotens oder Ereignisses.",
      shows_renderer: false,
    },
  ];

  return {
    levels,
    default_level: "cosmos",
  };
}
