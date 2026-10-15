# Canonical Recorder Conversation Model

EVIDENCE_VERSION: 1
STAGE: live-click
BACKUP_COMMIT: 48962a332
IMPLEMENTATION_COMMIT: ed976b5d8

## Action

An isolated Chromium run opened `collection_workspace.html` with a two-message
ChatGPT fixture. The canonical model was read back in the page, then exactly
one visible `Questions` action was clicked. The before/after screenshots are
the visual evidence for that action.

## Visible result

- Before: `2/2 Quellen ausgewählt · ChatGPT · MARKDOWN`, two visible rows.
- After one visible `Questions` click: `1/2 Quellen ausgewählt · ChatGPT · MARKDOWN`.
- After-status: `Questions-Filter: 1 explizit belegte Nachrichten. Quellen ohne Provider-Rollen bleiben ausgeschlossen.`

## DOM and artifact readback

- Graph schema: `flextrawurst.conversation-1`.
- Read-back node roles: `user`, `assistant`.
- Projection read-back: JSON, CSV, TXT and MD each rendered with two rows and
  a concrete MIME type; the projection metadata carries provider, graph,
  selection and the explicit-role policy.
- Role provenance is explicit DOM evidence only. A snapshot without an
  explicit provider role remains a `snapshot` node and is not guessed into a
  user/assistant turn.

## Limits and next seam

PDF remains the existing Chromium projection path. Provider-specific rich
fields (attachments, links, media, branches and reasoning blocks) are the next
model extension; they must stay provenance-bearing instead of being inferred.

## Evidence files

- `2026-08-22-recorder-canonical-before.png`
- `2026-08-22-recorder-canonical-after-questions.png`

- REC-GATE-001: PASS — contracts gate was green before the canonical model build.
- REC-EYE-001: PASS — before/after screenshots show one visible action and the resulting state.
- REC-DOC-001: PASS — schema, role readback, formats and explicit limits are recorded.

OUTCOME: PASS
