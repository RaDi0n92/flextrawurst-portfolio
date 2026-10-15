export interface ExportSection {
  section_id: string;
  label: string;
  summary: string;
  item_count: number;
  notes: string[];
}

export interface WorldInspectionExport {
  export_id: string;
  export_version: string;
  created_at: string;
  is_read_only: true;
  creates_events: false;
  activates_slots: false;
  is_live_flextrawurst_state: false;
  origin_layer: "inspection_export";
  sections: ExportSection[];
  warnings: string[];
  next_human_decisions: string[];
}
