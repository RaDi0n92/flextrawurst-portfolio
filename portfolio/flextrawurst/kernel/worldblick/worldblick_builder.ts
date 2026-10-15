import type { WorldblickOutput } from "./worldblick_output_model.ts";

export function buildWorldblickOutput(params: {
  output_id: string;
  created_at: string;
  base_dir: string;
}): WorldblickOutput {
  return {
    output_id: params.output_id,
    created_at: params.created_at,
    json_path: `${params.base_dir}/world_inspection_export.json`,
    markdown_path: `${params.base_dir}/world_inspection_export.md`,
    html_path: `${params.base_dir}/worldview_static_preview.html`,
    creates_events: false,
    activates_slots: false,
    imports_live_data: false,
    starts_world: false,
    is_read_only: true,
  };
}
