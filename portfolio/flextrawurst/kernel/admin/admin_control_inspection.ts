import type { AdminActor } from "./admin_permissions.ts";
import type { FeatureFlag } from "../features/feature_flag.ts";
import type { FeatureActivationGateReport } from "../features/feature_activation_gate.ts";
import type { AdminControlSnapshot } from "./admin_control_snapshot.ts";
import type { CommandLedger } from "./command_ledger.ts";
import { buildFeatureRegistry } from "../features/feature_registry.ts";
import { evaluateFeatureActivationGate } from "../features/feature_activation_gate.ts";
import { buildAdminControlSnapshot } from "./admin_control_snapshot.ts";
import { createEmptyCommandLedger } from "./command_ledger.ts";

export interface AdminControlInspection {
  inspection_version: 1;
  actor: AdminActor;
  features: FeatureFlag[];
  activation_gates: FeatureActivationGateReport[];
  snapshot: AdminControlSnapshot;
  ledger: CommandLedger;
  summary: string[];
}

export function buildAdminControlInspection(
  actor: AdminActor
): AdminControlInspection {
  const features = buildFeatureRegistry();
  const activation_gates = features.map((f) =>
    evaluateFeatureActivationGate(f, actor)
  );
  const snapshot = buildAdminControlSnapshot(actor, features);
  const ledger = createEmptyCommandLedger();

  return {
    inspection_version: 1,
    actor,
    features,
    activation_gates,
    snapshot,
    ledger,
    summary: [
      "Verwaltungs-Steuerungsebene aktiv.",
      "Alle Organ-Features deaktiviert.",
      "Aktivierung blockiert bis Daniel-Planung und Freigabe.",
      "Weltblick nur-lesen erlaubt.",
      "Tiefensuche-Grundlage registriert, aber noch nicht implementiert.",
    ],
  };
}
