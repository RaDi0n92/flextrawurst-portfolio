import { buildCanonicalProcessSnapshot } from "../kernel/process_model/process_snapshot.ts";
import { buildProcessCameraModel } from "../kernel/process_camera/process_camera_builder.ts";
import { exportProcessCameraModelToJSON } from "../kernel/process_camera/process_camera_export.ts";
import { buildProcessCameraHtml } from "../kernel/process_camera/process_camera_html.ts";
import { writeProcessCameraFiles } from "../kernel/process_camera/process_camera_writer.ts";
import { startServer } from "./serve_process_camera_preview.ts";

const JSON_PATH = "out/process_camera/process_camera_model.json";
const HTML_PATH = "out/process_camera/process_camera_worldblick.html";
const CREATED_AT = new Date().toISOString();

const snapshot = buildCanonicalProcessSnapshot(CREATED_AT);
const model = buildProcessCameraModel(snapshot, CREATED_AT);
const json = exportProcessCameraModelToJSON(model);
const html = buildProcessCameraHtml(model);

writeProcessCameraFiles(JSON_PATH, HTML_PATH, json, html);

console.log("Build fertig:");
console.log(`  JSON: ${JSON_PATH}`);
console.log(`  HTML: ${HTML_PATH}`);
console.log(`  Prozesskörper: ${model.status_summary.process_count}`);
console.log("");

startServer();
