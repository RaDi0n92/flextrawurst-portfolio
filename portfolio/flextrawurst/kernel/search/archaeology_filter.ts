import type { SearchDocument, SearchDocumentKind } from "./search_document.ts";
import type { SearchCorpus } from "./search_corpus.ts";

export interface ArchaeologyFilter {
  text?: string;
  kinds?: SearchDocumentKind[];
  tags?: string[];
  source_id?: string;
  event_type?: string;
  actor_type?: string;
  actor_id?: string;
  target_type?: string;
  target_id?: string;
  slot_id?: string;
  feature_id?: string;
  provenance_type?: string;
  command_id?: string;
  layer?: string;
  timeline_from?: number;
  timeline_to?: number;
  created_from?: string;
  created_to?: string;
  requires_source_ids?: boolean;
}

export function matchesArchaeologyFilter(
  doc: SearchDocument,
  filter: ArchaeologyFilter
): boolean {
  if (filter.kinds !== undefined && !filter.kinds.includes(doc.kind)) {
    return false;
  }
  if (filter.event_type !== undefined && doc.event_type !== filter.event_type) {
    return false;
  }
  if (filter.actor_type !== undefined && doc.actor_type !== filter.actor_type) {
    return false;
  }
  if (filter.actor_id !== undefined && doc.actor_id !== filter.actor_id) {
    return false;
  }
  if (filter.target_type !== undefined && doc.target_type !== filter.target_type) {
    return false;
  }
  if (filter.target_id !== undefined && doc.target_id !== filter.target_id) {
    return false;
  }
  if (filter.slot_id !== undefined && doc.slot_id !== filter.slot_id) {
    return false;
  }
  if (filter.feature_id !== undefined && doc.feature_id !== filter.feature_id) {
    return false;
  }
  if (
    filter.provenance_type !== undefined &&
    doc.provenance_type !== filter.provenance_type
  ) {
    return false;
  }
  if (filter.command_id !== undefined && doc.command_id !== filter.command_id) {
    return false;
  }
  if (filter.layer !== undefined && doc.layer !== filter.layer) {
    return false;
  }
  if (filter.source_id !== undefined && !doc.source_ids.includes(filter.source_id)) {
    return false;
  }
  if (filter.tags !== undefined) {
    const hasAll = filter.tags.every((t) => doc.tags.includes(t));
    if (!hasAll) return false;
  }
  if (
    filter.timeline_from !== undefined &&
    (doc.timeline_index === null || doc.timeline_index < filter.timeline_from)
  ) {
    return false;
  }
  if (
    filter.timeline_to !== undefined &&
    (doc.timeline_index === null || doc.timeline_index > filter.timeline_to)
  ) {
    return false;
  }
  if (filter.created_from !== undefined && doc.created_at !== null) {
    if (doc.created_at < filter.created_from) return false;
  }
  if (filter.created_to !== undefined && doc.created_at !== null) {
    if (doc.created_at > filter.created_to) return false;
  }
  if (filter.requires_source_ids === true && doc.source_ids.length === 0) {
    return false;
  }
  if (filter.text !== undefined) {
    const needle = filter.text.toLowerCase();
    const haystack =
      (doc.title + " " + doc.body + " " + doc.tags.join(" ")).toLowerCase();
    if (!haystack.includes(needle)) return false;
  }
  return true;
}

export function filterSearchCorpus(
  corpus: SearchCorpus,
  filter: ArchaeologyFilter
): SearchDocument[] {
  return corpus.documents
    .filter((doc) => matchesArchaeologyFilter(doc, filter))
    .sort((a, b) => a.document_id.localeCompare(b.document_id));
}
