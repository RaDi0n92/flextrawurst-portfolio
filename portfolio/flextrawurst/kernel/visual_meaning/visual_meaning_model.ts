export type VisualKind =
  | "node_pulse"
  | "edge_pressure"
  | "silence_shell"
  | "memory_echo"
  | "dream_residue_hint"
  | "room_density"
  | "activation_block"
  | "origin_marker"
  | "replay_trace";

export type VisualConfidence = "structural" | "inferred" | "weak";

export interface VisualMeaning {
  visual_id: string;
  visual_kind: VisualKind;
  source_event_ids: string[];
  source_state_ids: string[];
  source_slot_ids: string[];
  source_room_ids: string[];
  meaning: string;
  intensity: number;
  confidence: VisualConfidence;
  visible_to: string[];
  created_from: string;
  created_at: string;
  is_decorative: false;
  origin_layer?: string;
  is_live_flextrawurst_state?: boolean;
  requires_start_decision?: boolean;
}

export interface CreateVisualMeaningParams {
  visual_id: string;
  visual_kind: VisualKind;
  source_event_ids?: string[];
  source_state_ids?: string[];
  source_slot_ids?: string[];
  source_room_ids?: string[];
  meaning: string;
  intensity: number;
  confidence: VisualConfidence;
  visible_to?: string[];
  created_from: string;
  created_at: string;
  origin_layer?: string;
  is_live_flextrawurst_state?: boolean;
  requires_start_decision?: boolean;
}

export function createVisualMeaning(
  params: CreateVisualMeaningParams
): VisualMeaning {
  const source_event_ids = params.source_event_ids ?? [];
  const source_state_ids = params.source_state_ids ?? [];
  const source_slot_ids = params.source_slot_ids ?? [];
  const source_room_ids = params.source_room_ids ?? [];

  const hasSource =
    source_event_ids.length > 0 ||
    source_state_ids.length > 0 ||
    source_slot_ids.length > 0 ||
    source_room_ids.length > 0;

  if (!hasSource) {
    throw new Error(
      `VisualMeaning '${params.visual_id}' ohne Herkunft. ` +
        `Mindestens eine source_* muss befüllt sein. ` +
        `VisualMeaning ohne Weltgrund ist verboten.`
    );
  }

  const vm: VisualMeaning = {
    visual_id: params.visual_id,
    visual_kind: params.visual_kind,
    source_event_ids,
    source_state_ids,
    source_slot_ids,
    source_room_ids,
    meaning: params.meaning,
    intensity: Math.max(0, Math.min(1, params.intensity)),
    confidence: params.confidence,
    visible_to: params.visible_to ?? ["system"],
    created_from: params.created_from,
    created_at: params.created_at,
    is_decorative: false,
  };

  if (params.origin_layer !== undefined) {
    vm.origin_layer = params.origin_layer;
  }
  if (params.is_live_flextrawurst_state !== undefined) {
    vm.is_live_flextrawurst_state = params.is_live_flextrawurst_state;
  }
  if (params.requires_start_decision !== undefined) {
    vm.requires_start_decision = params.requires_start_decision;
  }

  return vm;
}
