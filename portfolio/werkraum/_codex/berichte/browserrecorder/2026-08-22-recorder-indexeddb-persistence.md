# IndexedDB Artifact Manifest Persistence

EVIDENCE_VERSION: 1
STAGE: replica
BACKUP_COMMIT: a33596459
IMPLEMENTATION_COMMIT: e5d85bd46

## Aktion

The visible collection workspace exported one DOCX projection. The artifact
manifest was written through the existing `DakCrawlDB` collection store. The
workspace was then reloaded and the Replica-Bundle was exported afterwards.

## Sichtbar

- Before screenshot: `2026-08-22-recorder-persist-before.png`.
- After-reload screenshot: `2026-08-22-recorder-persist-after-reload.png`.
- URL: `file:///root/werkraum/refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/collection_workspace.html?collection_id=persist-demo`.
- After reload, the visible parity layer again showed `Letztes Artefaktmanifest · DOCX · 3926 Bytes` with the same SHA-256.

## Rücklese

- `DakCrawlDB.appendCollectionArtifact()` stores up to 100 manifests in the
  existing IndexedDB `collections` record as `artifact_manifests`.
- The reload status returned one stored manifest; the UI hydrated its list from
  `collection.artifact_manifests` rather than the previous page memory.
- Downloaded DOCX: `2026-08-22-recorder-persist.docx`, 3926 bytes,
  SHA-256 `2ee877c89f38bfc2835ab07d0e6a90aaeb7a70e0d55c91fd4b187833ca793bc6`;
  `zipfile.testzip()` passed.
- Replica readback: `2026-08-22-recorder-persist-replica.json`, SHA-256
  `725b406a1a31ff5e21bdb61b39b2942358e7e44bf270f9463593115a8fa01481`;
  `projections.canonical_projections.length === 1` after reload.
- Persisted manifest status is explicitly `persisted` with store
  `dak_web_crawl_recorder.collections.artifact_manifests`.

## Offen/Unbekannt

This proves extension IndexedDB persistence across a workspace reload, not
cross-profile sync or server replication. Raw page bytes remain separate from
the projection manifest; no live fetch or navigation was introduced.

- REC-GATE-001: PASS — contracts gate returned `ok: true` before the build.
- REC-REPLICA-001: PASS — the post-reload replica contains the persisted canonical projection entry.
- REC-DOWNLOAD-001: PASS — completed DOCX download, bytes, SHA-256 and ZIP readback recorded.
- REC-FETCH-001: PASS — only the saved snapshot was used; no network fetch occurred.
- REC-DOC-001: PASS — screenshots, URL, reload observation, hashes and limits are documented.

OUTCOME: PASS
