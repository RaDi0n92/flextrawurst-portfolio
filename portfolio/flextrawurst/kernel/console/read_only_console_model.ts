import type { WorldOSSpine } from "../os_spine/world_os_spine.ts";
import type { WorldOSSpineImportExtension } from "../os_spine/world_os_spine_import_extension.ts";

export type ConsoleSectionKind =
  | "overview"
  | "slots"
  | "runtime"
  | "import_gate"
  | "activation_firewall"
  | "camera_readiness"
  | "audit"
  | "concept_guard";

export interface ConsoleSection {
  id: string;
  title: string;
  kind: ConsoleSectionKind;
  rows: Array<Record<string, unknown>>;
  summary: string[];
}

export interface ConsoleNavigationItem {
  id: string;
  label: string;
  target_section_id: string;
}

export interface ReadOnlyConsoleModel {
  console_version: 1;
  title: string;
  sections: ConsoleSection[];
  warnings: string[];
  navigation: ConsoleNavigationItem[];
}

export function buildReadOnlyConsoleModel(
  spine: WorldOSSpine,
  importExtension: WorldOSSpineImportExtension
): ReadOnlyConsoleModel {
  const occupiedCount = spine.slots.filter(
    (s) => s.status === "occupied"
  ).length;

  const sections: ConsoleSection[] = [
    {
      id: "overview",
      title: "Übersicht",
      kind: "overview",
      rows: [
        { label: "scenario_id", value: spine.scenario_id },
        { label: "spine_version", value: spine.spine_version },
        { label: "slot_count", value: spine.slots.length },
        { label: "occupied_count", value: occupiedCount },
        { label: "eingezogene_wesen_count", value: 0 },
        { label: "import_bundle_id", value: importExtension.import_bundle_id },
        {
          label: "import_would_create_events",
          value: importExtension.dry_run.would_create_events,
        },
        {
          label: "import_would_activate_slots",
          value: importExtension.dry_run.would_activate_slots,
        },
        {
          label: "activation_firewall_blocked",
          value: importExtension.activation_firewall.blocked,
        },
        {
          label: "runtime_deterministic",
          value: spine.runtime_readiness.deterministic,
        },
        { label: "audit_ok", value: spine.audit_ok },
        { label: "concept_guard_ok", value: spine.concept_guard.ok },
      ],
      summary: [
        `${spine.slots.length} kanonische Entitätsslots.`,
        `${occupiedCount} Slots besetzt.`,
        `0 eingezogene Wesen.`,
        `Import-Gate vorhanden. Kein Einzug. Keine Events geschrieben.`,
        `Activation Firewall blockiert alle Slots.`,
      ],
    },
    {
      id: "slots",
      title: "Entitätsslots",
      kind: "slots",
      rows: spine.slots.map((slot) => ({
        slot_id: slot.slot_id,
        status: slot.status,
        occupied: slot.status === "occupied",
        occupant_id: slot.occupant_id,
        canonical: slot.canonical,
        source: slot.source,
      })),
      summary: [
        `${spine.slots.length} Slots total.`,
        `${occupiedCount} besetzt.`,
        `${spine.slots.length - occupiedCount} technisch vorbereitet, nicht aktivierungsfrei.`,
        `Alle occupant_id: null.`,
      ],
    },
    {
      id: "runtime",
      title: "Runtime-Bereitschaft",
      kind: "runtime",
      rows: [
        { label: "ok", value: spine.runtime_readiness.ok },
        { label: "deterministic", value: spine.runtime_readiness.deterministic },
        { label: "event_count", value: spine.runtime_readiness.event_count },
        { label: "tick_count", value: spine.runtime_readiness.tick_count },
        {
          label: "replay_frame_count",
          value: spine.runtime_readiness.replay_frame_count,
        },
        { label: "uses_ai", value: spine.runtime_readiness.uses_ai },
        { label: "uses_ui", value: spine.runtime_readiness.uses_ui },
        { label: "uses_postgres", value: spine.runtime_readiness.uses_postgres },
        {
          label: "uses_scheduler",
          value: spine.runtime_readiness.uses_scheduler,
        },
      ],
      summary: spine.runtime_readiness.notes,
    },
    {
      id: "import_gate",
      title: "Import Gate",
      kind: "import_gate",
      rows: [
        {
          label: "bundle_id",
          value: importExtension.dry_run.bundle_id,
        },
        {
          label: "source_type",
          value: importExtension.dry_run.source_type,
        },
        {
          label: "account_count",
          value: importExtension.dry_run.account_count,
        },
        {
          label: "discussion_count",
          value: importExtension.dry_run.discussion_count,
        },
        {
          label: "post_count",
          value: importExtension.dry_run.post_count,
        },
        {
          label: "mapped_count",
          value: importExtension.dry_run.mapped_count,
        },
        {
          label: "unmapped_count",
          value: importExtension.dry_run.unmapped_count,
        },
        {
          label: "would_create_events",
          value: importExtension.dry_run.would_create_events,
        },
        {
          label: "would_activate_slots",
          value: importExtension.dry_run.would_activate_slots,
        },
        {
          label: "provenance_record_count",
          value:
            importExtension.provenance_preview.provenance_records.length,
        },
      ],
      summary: importExtension.dry_run.notes,
    },
    {
      id: "activation_firewall",
      title: "Activation Firewall",
      kind: "activation_firewall",
      rows: [
        {
          label: "blocked",
          value: importExtension.activation_firewall.blocked,
        },
        {
          label: "reason",
          value: importExtension.activation_firewall.reason,
        },
        {
          label: "blocked_slot_count",
          value: importExtension.activation_firewall.blocked_slot_ids.length,
        },
        {
          label: "allowed_slot_count",
          value: importExtension.activation_firewall.allowed_slot_ids.length,
        },
        ...importExtension.activation_firewall.checks.map((c) => ({
          check_id: c.check_id,
          passed: c.passed,
          message: c.message,
        })),
      ],
      summary: [
        importExtension.activation_firewall.reason,
        `${importExtension.activation_firewall.blocked_slot_ids.length} Slots blockiert.`,
        `${importExtension.activation_firewall.allowed_slot_ids.length} Slots freigegeben.`,
      ],
    },
    {
      id: "camera_readiness",
      title: "Kamera-Bereitschaft",
      kind: "camera_readiness",
      rows: [
        { label: "ok", value: spine.camera_readiness.ok },
        { label: "clickable", value: spine.camera_readiness.clickable },
        { label: "zoomable", value: spine.camera_readiness.zoomable },
        { label: "traceable", value: spine.camera_readiness.traceable },
        { label: "has_timeline", value: spine.camera_readiness.has_timeline },
        {
          label: "has_navigation_paths",
          value: spine.camera_readiness.has_navigation_paths,
        },
      ],
      summary: spine.camera_readiness.notes,
    },
    {
      id: "audit",
      title: "Audit",
      kind: "audit",
      rows: [
        { label: "audit_ok", value: spine.audit_ok },
        { label: "scenario_id", value: spine.scenario_id },
      ],
      summary: [`Audit-Status: ${spine.audit_ok ? "ok" : "fehlgeschlagen"}.`],
    },
    {
      id: "concept_guard",
      title: "Concept Guard",
      kind: "concept_guard",
      rows: [
        { label: "ok", value: spine.concept_guard.ok },
        {
          label: "violation_count",
          value: spine.concept_guard.violations.length,
        },
        ...spine.concept_guard.violations.map((v) => ({
          violation_id: v.id,
          term: v.term,
          message: v.message,
        })),
      ],
      summary: [
        `Concept Guard: ${spine.concept_guard.ok ? "keine Verstöße" : `${spine.concept_guard.violations.length} Verstoß/Verstöße`}.`,
      ],
    },
  ];

  const navigation: ConsoleNavigationItem[] = sections.map((s) => ({
    id: `nav-${s.id}`,
    label: s.title,
    target_section_id: s.id,
  }));

  const warnings: string[] = [
    "Import ≠ Einzug. Importierter Ursprung ist kein Einzug.",
    "Forum-Account ≠ eingezogenes Wesen.",
    "Read-only Console Model ≠ UI. Kein Renderer, kein DOM, kein Canvas.",
    "Activation Firewall blockiert alle Slots. Kein Einzug möglich.",
    "Console ist kein Renderer. CameraModel ist kein Renderer.",
  ];

  return {
    console_version: 1,
    title: "Weltbetriebssystem — Read-only Console Model (Ring 4)",
    sections,
    warnings,
    navigation,
  };
}
