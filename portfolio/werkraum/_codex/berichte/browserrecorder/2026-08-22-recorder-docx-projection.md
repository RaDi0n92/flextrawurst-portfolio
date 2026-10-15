# Canonical DOCX Projection

EVIDENCE_VERSION: 1
STAGE: download
BACKUP_COMMIT: 431129a7a
IMPLEMENTATION_COMMIT: d6fcb9873

## Aktion

The collection workspace was opened in Chromium with one saved snapshot
containing two explicitly role-labelled messages. The format selector was set
to DOCX and the visible `DOCX exportieren` action was clicked once.

## Sichtbar

- Before screenshot: `2026-08-22-recorder-docx-before.png`.
- After screenshot: `2026-08-22-recorder-docx-after.png`.
- URL: `file:///root/werkraum/refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/collection_workspace.html?collection_id=demo`.
- The after screen visibly reports: `DOCX-Projektion erzeugt · 2/2 Quellen · 3942 Bytes · SHA-256 e61c830c52a92a14926dacacb902c3b153c77530841a3a97abc4d4fb8e88bc75`.

## Rücklese

- Playwright observed a completed browser download with suggested filename
  `parity-demo.docx`.
- Read-back file: `2026-08-22-recorder-parity-demo.docx`, 3942 bytes.
- SHA-256: `e61c830c52a92a14926dacacb902c3b153c77530841a3a97abc4d4fb8e88bc75`.
- Python `zipfile.testzip()` passed. The package contains
  `[Content_Types].xml`, relationships, `word/document.xml` and styles; the
  document XML contains the role-bearing message content.
- The renderer consumes the canonical graph and XML-escapes message content;
  no live network fetch was used.

## Offen/Unbekannt

This is a projection of saved visible material, not a pixel-identical page
archive. DOCX rich formatting is intentionally small for this first renderer;
attachments, images, tables and provider-specific blocks remain future model
fields. PDF continues through the existing Chromium print path.

- REC-GATE-001: PASS — contracts gate returned `ok: true` before the build.
- REC-DOWNLOAD-001: PASS — completed download event, filename, bytes, SHA-256 and ZIP readback recorded.
- REC-FETCH-001: PASS — no network fetch occurred; the projection consumed only the saved snapshot/graph.
- REC-SEC-001: PASS — local fixture, XML escaping and no new broad permission or fetch path.
- REC-DOC-001: PASS — action, screenshots, URL, file readback and limits are documented.

OUTCOME: PASS
