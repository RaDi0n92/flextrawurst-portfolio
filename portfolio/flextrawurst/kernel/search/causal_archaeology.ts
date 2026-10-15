import type { SearchDocument } from "./search_document.ts";
import type { SearchCorpus } from "./search_corpus.ts";

export function findCausalChainDocuments(
  corpus: SearchCorpus,
  event_id: string
): SearchDocument[] {
  return corpus.documents
    .filter((doc) => doc.source_ids.includes(event_id))
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}

export function findCausalChildrenDocuments(
  corpus: SearchCorpus,
  event_id: string
): SearchDocument[] {
  return corpus.documents
    .filter(
      (doc) =>
        doc.source_ids.length > 1 &&
        doc.source_ids.slice(1).includes(event_id)
    )
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}

export function findDocumentsBySource(
  corpus: SearchCorpus,
  source_id: string
): SearchDocument[] {
  return corpus.documents
    .filter((doc) => doc.source_ids.includes(source_id))
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}
