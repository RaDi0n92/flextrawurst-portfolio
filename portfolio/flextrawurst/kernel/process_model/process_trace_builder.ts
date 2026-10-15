import type { ProcessBody, ProcessTrace } from "./process_types.ts";

export function buildTracesForBody(body: ProcessBody): ProcessTrace[] {
  const traces: ProcessTrace[] = [];

  if (body.file_ref) {
    traces.push({
      trace_type: "file",
      body_id: body.id,
      ref_id: body.file_ref,
      source_type: "derived_from_file",
      summary: `Kernel-Modul: ${body.file_ref}`,
    });
  }

  if (body.forum_ref) {
    traces.push({
      trace_type: "forum",
      body_id: body.id,
      ref_id: body.forum_ref,
      source_type: "derived_from_forum",
      summary: `Flarum-Herkunft: ${body.forum_ref}`,
    });
  }

  if (body.governance_state) {
    traces.push({
      trace_type: "governance",
      body_id: body.id,
      ref_id: body.governance_state,
      source_type: "derived_from_file",
      summary: `Governance: ${body.governance_state}`,
    });
  }

  if (body.ring_origin !== undefined) {
    traces.push({
      trace_type: "origin",
      body_id: body.id,
      ref_id: `ring_${body.ring_origin}`,
      source_type: "modelled",
      summary: `Eingeführt in Ring ${body.ring_origin}`,
    });
  }

  return traces;
}

export function buildTracesForSnapshot(
  bodies: readonly ProcessBody[]
): ProcessBody[] {
  return bodies.map((b) => ({ ...b, traces: buildTracesForBody(b) }));
}
