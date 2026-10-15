---
name: recorder-echtaugen-belegkette
description: Requires a visible before/one-action/after proof chain for browser clicks and live recorder work, with DOM and persisted-state rereads; use for every live UI action or acceptance.
---

# Echtaugen-Belegkette

Marker: `REC-EYE-001`

## Hard stop

For each meaningful live action, in this order:

1. Capture the visible screen, active URL, title, tab list, and expected state.
2. Perform exactly one visible action.
3. Capture the resulting screen.
4. Reread DOM, IndexedDB/server state, and artifact metadata.
5. Compare all observations. If they disagree, stop and report `UNKNOWN`.

No success claim without both screenshots and a persistence reread. A test runner assertion is not an eye witness.

## Boundaries

- Do not call hidden click, scroll, follow, focus, or route helpers as proof of a human-visible action.
- A tab change alone creates no snapshot; a visible capture action creates exactly one snapshot.
- Report what was visible, not what the code was supposed to show.
- A PDF or Markdown export proves an export only; it does not prove a human read the source page.
