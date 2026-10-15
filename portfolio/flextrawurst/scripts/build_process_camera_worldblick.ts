import { buildCanonicalProcessSnapshot } from "../kernel/process_model/process_snapshot.ts";
import { buildProcessCameraModel } from "../kernel/process_camera/process_camera_builder.ts";
import { exportProcessCameraModelToJSON } from "../kernel/process_camera/process_camera_export.ts";
import { buildProcessCameraInteractiveHtml } from "../kernel/process_camera/process_camera_interactive_html.ts";
import { PROCESS_CAMERA_LAYOUT } from "../kernel/process_camera/process_camera_layout.ts";
import { writeProcessCameraFiles } from "../kernel/process_camera/process_camera_writer.ts";

const JSON_PATH = "out/process_camera/process_camera_model.json";
const HTML_PATH = "out/process_camera/process_camera_worldblick.html";
const CREATED_AT = "2026-05-09T00:00:00.000Z";

const snapshot = buildCanonicalProcessSnapshot(CREATED_AT);
const model    = buildProcessCameraModel(snapshot, CREATED_AT);
const json     = exportProcessCameraModelToJSON(model);
const html     = buildProcessCameraInteractiveHtml(model, PROCESS_CAMERA_LAYOUT);

writeProcessCameraFiles(JSON_PATH, HTML_PATH, json, html);

console.log("Prozesskamera Weltblick erzeugt:");
console.log(`  JSON: ${JSON_PATH}`);
console.log(`  HTML: ${HTML_PATH}`);
console.log(`  Prozesskörper: ${model.status_summary.process_count}`);
console.log(`  measured_count: ${model.status_summary.measured_count}`);
console.log(`  active_claim_count: ${model.status_summary.active_claim_count}`);
console.log(`  occupied_count: ${model.status_summary.occupied_count}`);
console.log("  is_static: true | is_read_only: true | no_runtime: true");
