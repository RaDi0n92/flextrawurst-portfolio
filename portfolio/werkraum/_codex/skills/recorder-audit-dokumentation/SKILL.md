---
name: recorder-audit-dokumentation
description: Produces the small mandatory Markdown evidence record for each meaningful Recorder build or live stage; use after every scoped action and at session handoff.
---

# Audit-Dokumentation

Marker: `REC-DOC-001`

## Required four-part record

For each meaningful stage, write a short Markdown report containing:

1. `Aktion` — exactly what was done.
2. `Sichtbar` — what the real screen showed, with screenshot path, URL, title, and tab context where relevant.
3. `Rücklese` — DOM, IndexedDB/server state, file bytes, hashes, page count, or other persisted reread.
4. `Offen/Unbekannt` — what was not proven.

Add the marker lines required by the gate and keep “green test” separate from human-visible evidence. Never fill an unknown field with an inference.

## Location

Persistent live/build acceptance reports belong under `/root/werkraum/_codex/berichte/browserrecorder/`. Session handoff belongs under `_codex/notizen/YYYY-MM-DD.md` and follows the project’s holy section list.
