import type { SearchDocument } from "./search_document.ts";
import type { SearchCorpus } from "./search_corpus.ts";
import type { ArchaeologyFilter } from "./archaeology_filter.ts";
import { filterSearchCorpus } from "./archaeology_filter.ts";

export interface ArchaeologyQuery {
  query_id: string;
  label: string;
  filter: ArchaeologyFilter;
  explain: boolean;
}

export interface ArchaeologySearchResult {
  query_id: string;
  result_count: number;
  documents: SearchDocument[];
  explanations: string[];
}

export function runArchaeologyQuery(
  corpus: SearchCorpus,
  query: ArchaeologyQuery
): ArchaeologySearchResult {
  const documents = filterSearchCorpus(corpus, query.filter);
  const explanations = query.explain
    ? explainSearchResult(query, documents)
    : [];
  return {
    query_id: query.query_id,
    result_count: documents.length,
    documents,
    explanations,
  };
}

export function explainSearchResult(
  query: ArchaeologyQuery,
  documents: SearchDocument[]
): string[] {
  const lines: string[] = [];
  lines.push(`${documents.length} Treffer für Query "${query.label}".`);
  if (query.filter.event_type) {
    lines.push(
      `${documents.length} Treffer für event_type ${query.filter.event_type}.`
    );
  }
  if (query.filter.target_id) {
    lines.push(
      `${documents.length} Treffer mit target_id ${query.filter.target_id}.`
    );
  }
  if (query.filter.feature_id) {
    lines.push(
      `${documents.length} Treffer für feature_id ${query.filter.feature_id}.`
    );
  }
  if (query.filter.kinds) {
    lines.push(
      `Gefiltert nach ${query.filter.kinds.length} Dokumenttyp(en): ${query.filter.kinds.join(", ")}.`
    );
  }
  lines.push(
    "Alle Treffer sind read-only Suchdokumente; keine Weltmutation."
  );
  return lines;
}
