import type { WorldInspectionExport } from "./world_inspection_export_model.ts";

export function serializeWorldInspectionExportToJson(
  exp: WorldInspectionExport
): string {
  return JSON.stringify(exp, null, 2);
}

export function serializeWorldInspectionExportToMarkdown(
  exp: WorldInspectionExport
): string {
  const lines: string[] = [
    `# World Inspection Export`,
    ``,
    `**Export ID:** ${exp.export_id}`,
    `**Version:** ${exp.export_version}`,
    `**Created:** ${exp.created_at}`,
    `**is_read_only:** ${exp.is_read_only}`,
    `**creates_events:** ${exp.creates_events}`,
    `**activates_slots:** ${exp.activates_slots}`,
    `**is_live_flextrawurst_state:** ${exp.is_live_flextrawurst_state}`,
    `**origin_layer:** ${exp.origin_layer}`,
    ``,
    `## Sections`,
    ``,
  ];

  for (const section of exp.sections) {
    lines.push(`### ${section.label}`);
    lines.push(`- **Section ID:** ${section.section_id}`);
    lines.push(`- **Items:** ${section.item_count}`);
    lines.push(`- **Summary:** ${section.summary}`);
    if (section.notes.length > 0) {
      lines.push(`- **Notes:**`);
      for (const note of section.notes) {
        lines.push(`  - ${note}`);
      }
    }
    lines.push(``);
  }

  if (exp.warnings.length > 0) {
    lines.push(`## Warnings`);
    lines.push(``);
    for (const w of exp.warnings) {
      lines.push(`- ${w}`);
    }
    lines.push(``);
  }

  if (exp.next_human_decisions.length > 0) {
    lines.push(`## Next Human Decisions`);
    lines.push(``);
    for (const d of exp.next_human_decisions) {
      lines.push(`- ${d}`);
    }
    lines.push(``);
  }

  return lines.join("\n");
}
