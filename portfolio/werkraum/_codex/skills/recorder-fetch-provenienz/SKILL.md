---
name: recorder-fetch-provenienz
description: Enforces explicit, bounded, provenance-preserving fetch behavior for crawler and recorder assets; use for every network request, manifest probe, resource fetch, or server-side retrieval.
---

# Fetch-Provenienz

Marker: `REC-FETCH-001`

## Contract

- Every request has an owner, purpose, source URL, credentials mode, timeout, abort path, size limit, response-type check, and result status.
- A hidden manifest probe or automatic follow is a real fetch and must be declared, visible in provenance, and explicitly allowed by the mode.
- Same-origin, cross-origin, redirect, and server-side URL policy are checked separately; no SSRF-shaped server fetch is accepted by accident.
- Store request/response metadata and content hashes without pretending fetched assets were human-visible.
- Preserve raw bytes before creating HTML, Markdown, PDF, screenshot, or text projections.

## Hard stop

No unbounded `fetch()`, no `0 => Infinity` limit, no implicit credentials, and no success claim from HTTP resolution alone. Abort and size-limit tests are mandatory.
