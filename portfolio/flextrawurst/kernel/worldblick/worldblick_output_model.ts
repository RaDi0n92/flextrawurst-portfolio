export interface WorldblickOutput {
  output_id: string;
  created_at: string;
  json_path: string;
  markdown_path: string;
  html_path: string;
  creates_events: false;
  activates_slots: false;
  imports_live_data: false;
  starts_world: false;
  is_read_only: true;
}
