import type { EntitySlot } from "../slots/entity_slot.ts";
import type { ImportDryRunReport } from "../import_gate/import_dry_run.ts";
import type { ActivationReadinessReport } from "./activation_readiness.ts";

export interface ActivationFirewallCheck {
  check_id: string;
  passed: boolean;
  message: string;
}

export interface ActivationFirewallReport {
  ok: boolean;
  blocked: boolean;
  reason: string;
  blocked_slot_ids: string[];
  allowed_slot_ids: string[];
  checks: ActivationFirewallCheck[];
}

export function runActivationFirewall(
  slots: EntitySlot[],
  importDryRun: ImportDryRunReport,
  _activationReadinessReports: ActivationReadinessReport[]
): ActivationFirewallReport {
  const checks: ActivationFirewallCheck[] = [
    {
      check_id: "no_explicit_activation_event",
      passed: false,
      message:
        "Kein explizites Aktivierungsereignis vorhanden. Einzug blockiert.",
    },
    {
      check_id: "no_resident_profile",
      passed: false,
      message: "Kein Bewohnerprofil vorhanden. Einzug blockiert.",
    },
    {
      check_id: "no_memory_import",
      passed: false,
      message: "Kein Gedächtnis-Import vorhanden. Einzug blockiert.",
    },
    {
      check_id: "import_is_not_activation",
      passed: true,
      message:
        "Import-Kandidat ist kein Aktivierungsereignis. Schutzsatz eingehalten.",
    },
    {
      check_id: "presence_pulse_is_not_life",
      passed: true,
      message:
        "presence_pulse erzeugt kein Leben. Weltpuls ≠ Einzug. Schutzsatz eingehalten.",
    },
  ];

  const _ = importDryRun;

  return {
    ok: false,
    blocked: true,
    reason:
      "Kein Einzug ohne explizites Aktivierungsereignis. Alle Slots blockiert.",
    blocked_slot_ids: slots.map((s) => s.slot_id),
    allowed_slot_ids: [],
    checks,
  };
}
