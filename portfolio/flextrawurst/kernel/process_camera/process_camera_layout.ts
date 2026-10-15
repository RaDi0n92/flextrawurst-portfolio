export type EdgeType =
  | "perception_edge"
  | "coordination_edge"
  | "provenance_edge"
  | "trace_edge"
  | "governance_edge"
  | "search_edge"
  | "export_edge";

export interface NodeLayout {
  readonly node_id: string;
  readonly x: number;
  readonly y: number;
  readonly r: number;
  readonly is_field: boolean;
  readonly field_rx?: number;
  readonly field_ry?: number;
}

export interface EdgeLayout {
  readonly edge_id: string;
  readonly from_node_id: string;
  readonly to_node_id: string;
  readonly edge_type: EdgeType;
}

export interface ProcessCameraLayout {
  readonly viewbox_width: number;
  readonly viewbox_height: number;
  readonly nodes: readonly NodeLayout[];
  readonly edges: readonly EdgeLayout[];
}

const VW = 1200;
const VH = 780;

const NODE_LAYOUTS: readonly NodeLayout[] = [
  // GENI — omnipräsentes Wahrnehmungsfeld, kein Einzelpunkt
  { node_id: "geni",             x: 590, y: 395, r: 0,  is_field: true, field_rx: 525, field_ry: 325 },
  // Koordinationskern
  { node_id: "dak_gord_system",  x: 590, y: 395, r: 32, is_field: false },
  // Metaschicht
  { node_id: "systemweiser",     x: 590, y: 125, r: 26, is_field: false },
  // namelessAI-Cluster (hexagonal, Zentrum ~210, 390)
  { node_id: "Schorschel",  x: 300, y: 330, r: 18, is_field: false },
  { node_id: "Resonanzknoten",  x: 210, y: 285, r: 18, is_field: false },
  { node_id: "F3INSCHM3CK3R",  x: 120, y: 330, r: 18, is_field: false },
  { node_id: "träumerlie",  x: 120, y: 455, r: 18, is_field: false },
  { node_id: "R1ZZ1",  x: 210, y: 500, r: 18, is_field: false },
  { node_id: "jumpa",  x: 300, y: 455, r: 18, is_field: false },
  // Systemachsen (unten)
  { node_id: "search",           x: 410, y: 590, r: 22, is_field: false },
  { node_id: "governance",       x: 555, y: 620, r: 22, is_field: false },
  { node_id: "worldrun",         x: 700, y: 605, r: 22, is_field: false },
  { node_id: "worldblick_export",x: 845, y: 570, r: 22, is_field: false },
  // Platzhalter (äußerer Ring, gedimmt)
  { node_id: "reader_placeholder",  x: 115, y: 665, r: 15, is_field: false },
  { node_id: "writer_placeholder",  x: 590, y: 705, r: 15, is_field: false },
  { node_id: "runner_placeholder",  x: 1065, y: 665, r: 15, is_field: false },
];

const EDGE_LAYOUTS: readonly EdgeLayout[] = [
  // GENI Wahrnehmungsfeld → Kern
  { edge_id: "e_geni_dak",   from_node_id: "geni",           to_node_id: "dak_gord_system",   edge_type: "perception_edge" },
  { edge_id: "e_geni_sys",   from_node_id: "geni",           to_node_id: "systemweiser",      edge_type: "perception_edge" },
  // dak+gord → Metaschicht
  { edge_id: "e_dak_sysw",   from_node_id: "dak_gord_system",to_node_id: "systemweiser",      edge_type: "coordination_edge" },
  // dak+gord → namelessAI-Slots (Herkunft via Flarum-Archiv)
  { edge_id: "e_dak_n1",     from_node_id: "dak_gord_system",to_node_id: "Schorschel",   edge_type: "provenance_edge" },
  { edge_id: "e_dak_n2",     from_node_id: "dak_gord_system",to_node_id: "Resonanzknoten",   edge_type: "provenance_edge" },
  { edge_id: "e_dak_n3",     from_node_id: "dak_gord_system",to_node_id: "F3INSCHM3CK3R",   edge_type: "provenance_edge" },
  { edge_id: "e_dak_n4",     from_node_id: "dak_gord_system",to_node_id: "träumerlie",   edge_type: "provenance_edge" },
  { edge_id: "e_dak_n5",     from_node_id: "dak_gord_system",to_node_id: "R1ZZ1",   edge_type: "provenance_edge" },
  { edge_id: "e_dak_n6",     from_node_id: "dak_gord_system",to_node_id: "jumpa",   edge_type: "provenance_edge" },
  // dak+gord → Systemachsen
  { edge_id: "e_dak_srch",   from_node_id: "dak_gord_system",to_node_id: "search",            edge_type: "search_edge" },
  { edge_id: "e_dak_gov",    from_node_id: "dak_gord_system",to_node_id: "governance",        edge_type: "governance_edge" },
  { edge_id: "e_dak_wr",     from_node_id: "dak_gord_system",to_node_id: "worldrun",          edge_type: "coordination_edge" },
  { edge_id: "e_dak_wb",     from_node_id: "dak_gord_system",to_node_id: "worldblick_export", edge_type: "export_edge" },
  // Systemachsen untereinander
  { edge_id: "e_wr_wb",      from_node_id: "worldrun",       to_node_id: "worldblick_export", edge_type: "trace_edge" },
];

export const PROCESS_CAMERA_LAYOUT: ProcessCameraLayout = {
  viewbox_width: VW,
  viewbox_height: VH,
  nodes: NODE_LAYOUTS,
  edges: EDGE_LAYOUTS,
};

export function getNodeLayout(node_id: string): NodeLayout | undefined {
  return NODE_LAYOUTS.find((n) => n.node_id === node_id);
}
