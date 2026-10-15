import type { SearchInspectionPack } from "./search_inspection_pack.ts";

export interface SearchExport {
  export_version: 1;
  pack_version: number;
  total_documents: number;
  counts: Record<string, number>;
  sample_query_ids: string[];
  sample_result_counts: Record<string, number>;
  notes: string[];
}

export function buildSearchExport(pack: SearchInspectionPack): SearchExport {
  const sample_result_counts: Record<string, number> = {};
  for (const result of pack.sample_results) {
    sample_result_counts[result.query_id] = result.result_count;
  }

  return {
    export_version: 1,
    pack_version: pack.pack_version,
    total_documents: pack.corpus.documents.length,
    counts: { ...pack.corpus.counts },
    sample_query_ids: pack.sample_queries.map((q) => q.query_id).sort(),
    sample_result_counts,
    notes: [...pack.notes],
  };
}

export function serializeSearchExport(pack: SearchInspectionPack): string {
  const exp = buildSearchExport(pack);
  return JSON.stringify(exp, Object.keys(exp).sort(), 2);
}
