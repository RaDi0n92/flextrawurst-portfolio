# Ring 22A-C — Process Camera Foundation

**Status:** Umsetzungsdokument  
**Stand:** 2026-05-09  
**Vorgänger:** Ring 22 (Planung) + Ring 22a (Modellplan)

---

## Was dieser Ring baut

| Artefakt | Zweck |
|---|---|
| `kernel/process_model/process_types.ts` | Typen, Enums, Interfaces |
| `kernel/process_model/process_registry.ts` | 14 kanonische Prozesskörper |
| `kernel/process_model/process_snapshot.ts` | Read-only Snapshot mit Invariante active_claim_count = 0 |
| `kernel/process_model/process_trace_builder.ts` | Statische Spurenerzeugung aus Metadaten |
| `kernel/process_model/process_export.ts` | Deterministischer JSON-Export |
| `kernel/search/search_document.ts` | +3 neue SearchDocumentKind |
| `kernel/search/search_corpus.ts` | `buildSearchCorpusFromProcessSnapshot` |
| `kernel/concept_guard/concept_guard.ts` | +4 neue Guard-Muster |
| `tests/world_os_ring_22abc_process_camera_foundation.test.ts` | ~35 gezielte Tests |

---

## Was dieser Ring ausdrücklich nicht baut

- Keine UI, kein Renderer, kein DOM
- Kein Live-Daemon, kein Scheduler, kein setInterval
- Keine Postgres-Persistenz
- Kein Forum-Import
- Keine AI-Ausführung
- Kein Einzugsritual für Wesen
- Keine echte Live-Messung (measured_count = 0 für alle Körper)
- Kein HTML-Export (folgt in Ring 22e)
- Keine Spur außer statischer Ableitung aus Metadaten und Ring-Entscheidungen

---

## Testbudget

| Bereich | Tests |
|---|---|
| Registry | 10 |
| Snapshot | 8 |
| Export | 5 |
| Trace Builder | 4 |
| Search | 4 |
| ConceptGuard | 4 |
| **Gesamt** | **35** |
