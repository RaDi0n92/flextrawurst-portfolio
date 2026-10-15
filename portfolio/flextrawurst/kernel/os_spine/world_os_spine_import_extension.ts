import type { WorldOSSpine } from "./world_os_spine.ts";
import type { ForumImportBundle } from "../import_gate/forum_import_candidate.ts";
import type { ImportDryRunReport } from "../import_gate/import_dry_run.ts";
import type { ImportProvenancePreview } from "../import_gate/import_provenance_preview.ts";
import type { ActivationFirewallReport } from "../activation/activation_firewall.ts";
import { runImportDryRun } from "../import_gate/import_dry_run.ts";
import { buildImportProvenancePreview } from "../import_gate/import_provenance_preview.ts";
import { runActivationFirewall } from "../activation/activation_firewall.ts";

export interface WorldOSSpineImportExtension {
  import_bundle_id: string;
  dry_run: ImportDryRunReport;
  provenance_preview: ImportProvenancePreview;
  activation_firewall: ActivationFirewallReport;
}

export function extendSpineWithImportGate(
  spine: WorldOSSpine,
  bundle: ForumImportBundle
): WorldOSSpineImportExtension {
  const dry_run = runImportDryRun(bundle, spine.slots);
  const provenance_preview = buildImportProvenancePreview(
    bundle,
    dry_run.mappings
  );
  const activation_firewall = runActivationFirewall(
    spine.slots,
    dry_run,
    spine.activation_readiness
  );

  return {
    import_bundle_id: bundle.bundle_id,
    dry_run,
    provenance_preview,
    activation_firewall,
  };
}
