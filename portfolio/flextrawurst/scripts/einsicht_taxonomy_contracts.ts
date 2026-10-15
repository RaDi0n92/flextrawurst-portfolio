/**
 * Einsicht Taxonomy Contracts — TypeScript-Spiegel der Wesen Life Contracts.
 *
 * Wird vom Einsicht-Tab genutzt um Status-Chips korrekt darzustellen.
 * Kein Fake-Zählen. Kein erzwungenes Coloring.
 * Nur: was ist in der DB, was ist geplant, was hat einen echten Anlass.
 */

export type EinsichtStatus =
  | "no_data"
  | "planned"
  | "later"
  | "blocked"
  | "feature_locked"
  | "no_trigger"
  | "scanned"
  | "considered"
  | "rejected"
  | "deferred"
  | "chosen"
  | "dreamed"
  | "splittered"
  | "shadowed"
  | "related"
  | "ampel_affected"
  | "source_linked"
  | "saturated"
  | "overused"
  | "unknown";

export type Domain =
  | "decision" | "thought" | "dream" | "splitter" | "shadow"
  | "relation" | "source" | "amp_status" | "substance" | "cyberling"
  | "sleep" | "kompoase" | "retreat" | "group" | "system"
  | "memory" | "origin" | "post" | "human_profile" | "room";

export interface LifeContract {
  id: string;
  label: string;
  domain: Domain;
  ui_group: string;
  feature_flag: string | null;
  visibility_default: "aktiv" | "geplant" | "blockiert" | "später";
  can_be_thought: boolean;
  can_be_decided: boolean;
  can_be_dreamed: boolean;
  can_create_splitter: boolean;
  can_touch_shadow: boolean;
  can_affect_relation: boolean;
  can_affect_ampel: boolean;
  can_affect_memory: boolean;
  trigger_sources: string[];
  anti_triggers: string[];
  rhythm: "reaktiv" | "periodisch" | "schlaf_gebunden";
  minimum_review_interval_h: number;
  saturation_limit: number;
  overuse_risk: boolean;
  event_types: string[];
  blocked_reason: string | null;
  planned_reason: string | null;
  color: string;
}

export interface OrganHunger {
  organ_id: string;
  hunger_level: number;
  hunger_reason: string;
  has_trigger: boolean;
  trigger_sources: string[];
  last_activity: string | null;
  recommended_action: string | null;
}

export interface HungerReport {
  entity_id: string;
  calculated_at: string;
  organs: OrganHunger[];
}

/** Status-Label für UI-Darstellung */
export const STATUS_LABELS: Record<EinsichtStatus, { de: string; en: string; color: string }> = {
  no_data:        { de: "keine Daten",   en: "no data",      color: "#1a2a3a" },
  planned:        { de: "geplant",       en: "planned",      color: "#2a4a6a" },
  later:          { de: "später",        en: "later",        color: "#1a3a4a" },
  blocked:        { de: "blockiert",     en: "blocked",      color: "#6a2a2a" },
  feature_locked: { de: "Feature gesperrt", en: "feature locked", color: "#4a2a6a" },
  no_trigger:     { de: "kein Anlass",   en: "no trigger",   color: "#2a3a4a" },
  scanned:        { de: "geprüft",       en: "scanned",      color: "#3a6a5a" },
  considered:     { de: "erwogen",       en: "considered",   color: "#6a8a3a" },
  rejected:       { de: "verworfen",     en: "rejected",     color: "#8a4a2a" },
  deferred:       { de: "verschoben",    en: "deferred",     color: "#5a5a3a" },
  chosen:         { de: "gewählt",       en: "chosen",       color: "#10c080" },
  dreamed:        { de: "geträumt",      en: "dreamed",      color: "#8040c0" },
  splittered:     { de: "gesplittet",    en: "splittered",   color: "#10d8f0" },
  shadowed:       { de: "Schattenwirkung", en: "shadowed",   color: "#888888" },
  related:        { de: "Beziehungswirkung", en: "related",  color: "#10d080" },
  ampel_affected: { de: "Ampelwirkung",  en: "ampel impact", color: "#f0c010" },
  source_linked:  { de: "Quellenlink",   en: "source linked", color: "#6060c0" },
  saturated:      { de: "gesättigt",     en: "saturated",    color: "#a08040" },
  overused:       { de: "überreizt",     en: "overused",     color: "#c04020" },
  unknown:        { de: "unbekannt",     en: "unknown",      color: "#3a3a3a" },
};

/** Organhunger-Farbe nach Level */
export function hungerColor(level: number): string {
  if (level >= 0.7) return "#f04020";
  if (level >= 0.4) return "#f0c020";
  if (level >= 0.2) return "#c0a020";
  return "#2a4a3a";
}

/** Ob ein Contract UI-sichtbar sein soll (auch geplante, als ausgegraute Chips) */
export function isUiVisible(c: LifeContract): boolean {
  return c.visibility_default !== "blockiert";
}

/** Chip-CSS-Klasse basierend auf Status */
export function chipClass(status: EinsichtStatus, count: number): string {
  if (status === "planned" || status === "later" || status === "feature_locked")
    return "ei-kat-chip ei-kat-chip--plan";
  if (count === 0 && status === "no_data")
    return "ei-kat-chip ei-kat-chip--leer";
  if (status === "chosen" || status === "splittered" || status === "dreamed")
    return "ei-kat-chip aktiv";
  return "ei-kat-chip";
}

/** Status ableiten aus Zähldaten + Contract */
export function deriveStatus(
  c: LifeContract,
  counts: Record<string, number>,
  hungerLevel: number = 0,
): EinsichtStatus {
  if (c.visibility_default === "blockiert") return "blocked";
  if (c.visibility_default === "später") return "later";
  if (c.visibility_default === "geplant") return "planned";
  if (c.feature_flag && !(c.feature_flag in counts)) return "feature_locked";

  const total = counts[c.id] ?? 0;
  if (total === 0) {
    return hungerLevel > 0.3 ? "no_trigger" : "no_data";
  }

  // Grob: je nach domain bevorzugter Status
  if (c.domain === "dream") return "dreamed";
  if (c.domain === "splitter") return "splittered";
  if (c.domain === "shadow") return "shadowed";
  if (c.domain === "relation") return "related";

  if (c.can_be_decided && total > 0) return "chosen";
  if (c.can_be_thought && total > 0) return "scanned";
  return "unknown";
}

/**
 * Hilfsfunktion: rendert einen Status-Badge als HTML-String.
 * Für inline-Einbettung in bestehende Chip-Strukturen.
 */
export function statusBadgeHtml(status: EinsichtStatus, lang: "de" | "en" = "de"): string {
  const s = STATUS_LABELS[status];
  return `<span class="ei-status-badge" style="background:${s.color}22;border:1px solid ${s.color};color:${s.color};font-size:.4rem;padding:1px 4px;border-radius:2px;letter-spacing:.06em">${lang === "de" ? s.de : s.en}</span>`;
}
