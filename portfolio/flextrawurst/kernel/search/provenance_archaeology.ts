import type { SearchDocument } from "./search_document.ts";
import type { SearchCorpus } from "./search_corpus.ts";

export function findDocumentsByProvenanceType(
  corpus: SearchCorpus,
  provenance_type: string
): SearchDocument[] {
  return corpus.documents
    .filter((doc) => doc.provenance_type === provenance_type)
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}

export function findOriginTrail(
  corpus: SearchCorpus,
  subject_id: string
): SearchDocument[] {
  return corpus.documents
    .filter(
      (doc) =>
        doc.target_id === subject_id ||
        doc.slot_id === subject_id ||
        doc.source_ids.includes(subject_id)
    )
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}

export function findImportedCandidateDocuments(
  corpus: SearchCorpus
): SearchDocument[] {
  return corpus.documents
    .filter(
      (doc) =>
        doc.provenance_type === "flarum_import_candidate" ||
        doc.provenance_type === "chat_import_candidate" ||
        doc.provenance_type === "obsidian_import_candidate" ||
        doc.tags.includes("flarum_import_candidate") ||
        doc.tags.includes("import")
    )
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}
