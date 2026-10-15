import type { SearchCorpus } from "./search_corpus.ts";
import type { ArchaeologyQuery, ArchaeologySearchResult } from "./archaeology_query.ts";
import { runArchaeologyQuery } from "./archaeology_query.ts";

export interface SearchInspectionPack {
  pack_version: 1;
  corpus: SearchCorpus;
  sample_queries: ArchaeologyQuery[];
  sample_results: ArchaeologySearchResult[];
  notes: string[];
}

const SAMPLE_QUERIES: ArchaeologyQuery[] = [
  {
    query_id: "all_ticks",
    label: "Alle system.tick Events",
    filter: { event_type: "system.tick" },
    explain: true,
  },
  {
    query_id: "all_presence_traces",
    label: "Alle presence_pulse Traces",
    filter: { kinds: ["event", "timeline_frame"], tags: ["entity.state_changed"] },
    explain: true,
  },
  {
    query_id: "slot_Schorschel",
    label: "Alle Dokumente für Slot Schorschel",
    filter: { slot_id: "Schorschel" },
    explain: true,
  },
  {
    query_id: "disabled_features",
    label: "Alle deaktivierten Features",
    filter: { kinds: ["feature_flag"], tags: ["disabled"] },
    explain: true,
  },
  {
    query_id: "concept_guard_violations",
    label: "Alle ConceptGuard-Verletzungen",
    filter: { kinds: ["concept_guard_violation"] },
    explain: true,
  },
  {
    query_id: "worldblick_readonly",
    label: "Worldblick read-only Feature",
    filter: { feature_id: "worldblick_readonly_export" },
    explain: true,
  },
];

export function buildSearchInspectionPack(
  corpus: SearchCorpus
): SearchInspectionPack {
  const sample_results = SAMPLE_QUERIES.map((q) =>
    runArchaeologyQuery(corpus, q)
  );

  return {
    pack_version: 1,
    corpus,
    sample_queries: SAMPLE_QUERIES,
    sample_results,
    notes: [
      "SearchInspectionPack ist read-only.",
      "Keine Mutation durch Suche.",
      "Alle Dokumente haben Herkunft, Schicht und Typ.",
      "Suche ist Diskursarchäologie: Provenienz, Kausalität, Timeline, Slots, Features.",
    ],
  };
}
