import type { StaticPreview } from "./static_preview_model.ts";
import type { WorldInspectionExport } from "../export/world_inspection_export_model.ts";
import { buildStaticPreviewHtml } from "./static_preview_html.ts";

export function buildStaticPreview(
  preview_id: string,
  exp: WorldInspectionExport
): StaticPreview {
  const html = buildStaticPreviewHtml(exp);
  return {
    preview_id,
    source_export_id: exp.export_id,
    html_title: "Flextrawurst — Weltkamera Preview",
    is_static: true,
    is_read_only: true,
    has_external_dependencies: false,
    can_activate_slots: false,
    can_create_events: false,
    section_count: exp.sections.length,
    html,
  };
}
