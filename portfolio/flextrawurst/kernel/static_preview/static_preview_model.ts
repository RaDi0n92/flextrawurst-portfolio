export interface StaticPreview {
  preview_id: string;
  source_export_id: string;
  html_title: string;
  is_static: true;
  is_read_only: true;
  has_external_dependencies: false;
  can_activate_slots: false;
  can_create_events: false;
  section_count: number;
  html: string;
}
