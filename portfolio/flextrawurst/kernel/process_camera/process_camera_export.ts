import type { ProcessCameraModel } from "./process_camera_model.ts";

export interface ProcessCameraExport {
  readonly export_kind: "process_camera_model";
  readonly is_static: true;
  readonly is_read_only: true;
  readonly no_runtime: true;
  readonly no_activation: true;
  readonly no_live_claims: true;
  readonly no_renderer: true;
  readonly model: ProcessCameraModel;
}

export function exportProcessCameraModelToJSON(
  model: ProcessCameraModel
): string {
  const exp: ProcessCameraExport = {
    export_kind: "process_camera_model",
    is_static: true,
    is_read_only: true,
    no_runtime: true,
    no_activation: true,
    no_live_claims: true,
    no_renderer: true,
    model,
  };
  return JSON.stringify(exp, null, 2);
}
