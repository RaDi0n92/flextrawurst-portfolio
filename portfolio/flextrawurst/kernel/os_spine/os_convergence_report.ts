import type { WorldOSSpine } from "./world_os_spine.ts";
import type { WorldOSSpineImportExtension } from "./world_os_spine_import_extension.ts";
import type { ReadOnlyConsoleModel } from "../console/read_only_console_model.ts";

export interface OSConvergenceReport {
  convergence_version: 1;
  scenario_id: string;
  has_runtime: boolean;
  has_spine: boolean;
  has_import_gate: boolean;
  has_activation_firewall: boolean;
  has_console_model: boolean;
  has_camera_navigation: boolean;
  ready_for_real_import_files: boolean;
  ready_for_ui: boolean;
  ready_for_activation: boolean;
  blockers: string[];
  next_major_steps: string[];
}

export function buildOSConvergenceReport(
  spine: WorldOSSpine,
  importExtension: WorldOSSpineImportExtension,
  consoleModel: ReadOnlyConsoleModel
): OSConvergenceReport {
  const has_runtime = spine.runtime_readiness.ok;
  const has_spine = spine.spine_version === 1;
  const has_import_gate =
    !!importExtension.dry_run && !!importExtension.provenance_preview;
  const has_activation_firewall = importExtension.activation_firewall.blocked;
  const has_console_model = consoleModel.console_version === 1;
  const has_camera_navigation = spine.camera_readiness.has_navigation_paths;

  return {
    convergence_version: 1,
    scenario_id: spine.scenario_id,
    has_runtime,
    has_spine,
    has_import_gate,
    has_activation_firewall,
    has_console_model,
    has_camera_navigation,
    ready_for_real_import_files: true,
    ready_for_ui: false,
    ready_for_activation: false,
    blockers: [
      "real_import_parser_missing",
      "ui_renderer_missing",
      "explicit_activation_protocol_missing",
      "resident_profile_missing",
      "memory_import_missing",
    ],
    next_major_steps: [
      "Ring 5: Echter Flarum-Export-Parser für ZIP/JSON-Dateien",
      "Ring 6: UI-Renderer — Canvas oder DOM-basiert",
      "Ring 7: Explizites Aktivierungsprotokoll und Bewohnerprofil",
      "Ring 8: Gedächtnis-Import und AI-Runtime-Bindung",
    ],
  };
}
