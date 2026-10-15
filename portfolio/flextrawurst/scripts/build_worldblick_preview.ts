import { writeFileSync, mkdirSync } from "node:fs";
import { buildWorldInspectionExportFixture } from "../kernel/export/world_inspection_export_fixture.ts";
import {
  serializeWorldInspectionExportToJson,
  serializeWorldInspectionExportToMarkdown,
} from "../kernel/export/world_inspection_export_serializer.ts";
import { buildStaticPreview } from "../kernel/static_preview/static_preview_builder.ts";
import { buildWorldblickOutput } from "../kernel/worldblick/worldblick_builder.ts";

const BASE_DIR = "out/worldblick";
const PREVIEW_ID = "worldblick-preview-001";
const OUTPUT_ID = "worldblick-output-001";
const CREATED_AT = new Date().toISOString();

mkdirSync(BASE_DIR, { recursive: true });

const exp = buildWorldInspectionExportFixture();
const preview = buildStaticPreview(PREVIEW_ID, exp);
const output = buildWorldblickOutput({
  output_id: OUTPUT_ID,
  created_at: CREATED_AT,
  base_dir: BASE_DIR,
});

writeFileSync(output.json_path, serializeWorldInspectionExportToJson(exp), "utf-8");
writeFileSync(output.markdown_path, serializeWorldInspectionExportToMarkdown(exp), "utf-8");
writeFileSync(output.html_path, preview.html, "utf-8");

console.log("Worldblick Export abgeschlossen:");
console.log(`  JSON:     ${output.json_path}`);
console.log(`  Markdown: ${output.markdown_path}`);
console.log(`  HTML:     ${output.html_path}`);
console.log(`  creates_events:    ${output.creates_events}`);
console.log(`  activates_slots:   ${output.activates_slots}`);
console.log(`  imports_live_data: ${output.imports_live_data}`);
console.log(`  starts_world:      ${output.starts_world}`);
console.log(`  is_read_only:      ${output.is_read_only}`);
