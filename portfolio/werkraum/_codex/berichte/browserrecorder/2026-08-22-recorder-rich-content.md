# Canonical Rich Content and Reasoning

EVIDENCE_VERSION: 1
STAGE: download
BACKUP_COMMIT: 8225aa580
IMPLEMENTATION_COMMIT: 06527b47c

## Aktion

A visible Chromium workspace run opened a saved fixture with one user message
and one assistant message. The assistant DOM contained a heading, paragraph,
strong text, link, list, explicit reasoning marker and image. The JSON format
was selected and exported once.

## Sichtbar

- Before screenshot: `2026-08-22-recorder-rich-before.png`.
- After screenshot: `2026-08-22-recorder-rich-after.png`.
- URL: `file:///root/werkraum/refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/collection_workspace.html?collection_id=rich-demo`.
- The visible message row showed `4 Rich-Blöcke · 1 Links · 1 Medien · Reasoning`.

## Rücklese

- Downloaded file: `2026-08-22-recorder-rich.json`.
- SHA-256: `30aa9e7b16d754402e3ad7afe1c25988d0744de0ee79453e25dd7688fb808927`.
- JSON readback for the assistant node: 4 rich-content blocks, one explicit
  reasoning string, one link and one media entry.
- The graph preserves `rich_content`, `reasoning`, `links` and `media` with
  explicit DOM provenance. CSV/TXT/Markdown/DOCX renderers now carry counts or
  fields instead of dropping them silently.

## Offen/Unbekannt

Rich block extraction is conservative and only covers structures present in
the captured DOM. It does not fetch linked media, infer hidden reasoning, or
claim that a flattened export is pixel-identical to the provider page.

- REC-GATE-001: PASS — contracts gate returned `ok: true` before the build.
- REC-DOWNLOAD-001: PASS — JSON download completion and file SHA-256 were read back.
- REC-FETCH-001: PASS — no network fetch occurred; links/media are metadata from saved DOM only.
- REC-SEC-001: PASS — captured values are XML/JSON escaped and no new permission or fetch path was added.
- REC-DOC-001: PASS — visible row, URL, screenshots, JSON hash, fields and limits are documented.

OUTCOME: PASS
