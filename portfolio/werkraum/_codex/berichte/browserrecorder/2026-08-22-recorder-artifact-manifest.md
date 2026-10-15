# Persisted Projection Artifact Manifest

EVIDENCE_VERSION: 1
STAGE: replica
BACKUP_COMMIT: 62d47f5cc
IMPLEMENTATION_COMMIT: 5afec161e

## Aktion

In the visible collection workspace, DOCX was selected and exported once. The
workspace then exported its Replica-Bundle once. The replica manifest received
the canonical projection artifact entry instead of losing the export context.

## Sichtbar

- Before screenshot: `2026-08-22-recorder-manifest-before.png`.
- After screenshot: `2026-08-22-recorder-manifest-after.png`.
- URL: `file:///root/werkraum/refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/collection_workspace.html?collection_id=manifest-demo`.
- The after screen visibly shows `Letztes Artefaktmanifest · DOCX · 3923 Bytes`
  with its SHA-256 and `Replica zuletzt rückgelesen`.

## Rücklese

- DOCX download: `2026-08-22-recorder-manifest-docx.docx`, 3923 bytes,
  SHA-256 `79c79eb39931cc0b67a600f345c64e7fdc1fef79c9dd80dfae673dfab9767e6c`.
- Python `zipfile.testzip()` passed for the downloaded DOCX.
- Replica readback: `2026-08-22-replica-with-artifact-manifest.json`, 5786
  bytes, SHA-256 `39c5e3ac064ee93d55e55c3111bf01e74d1506e762c0660978596fe2aaff3`.
- `projections.canonical_projections.length === 1`; its format is `docx` and
  its SHA-256 equals the downloaded DOCX hash.
- The manifest records graph ID, projection job ID, selected IDs, MIME type,
  bytes, hash, role policy and projection limits. No live fetch occurred.

## Offen/Unbekannt

The artifact list is currently carried in the exported Replica-Bundle and in
the running workspace; durable server/IndexedDB history for arbitrary parity
exports is not yet implemented. Raw source bytes are intentionally not
embedded in this projection manifest.

- REC-GATE-001: PASS — contracts gate returned `ok: true` before the build.
- REC-REPLICA-001: PASS — replica JSON contains the canonical projection manifest and explicit limits.
- REC-DOWNLOAD-001: PASS — DOCX completion, filename, byte count, SHA-256 and ZIP readback recorded.
- REC-FETCH-001: PASS — no network fetch occurred; only persisted snapshot data was projected.
- REC-DOC-001: PASS — visible action, screenshots, URL, file hashes and readback are documented.

OUTCOME: PASS
