---
name: recorder-security-inputs
description: Prevents XSS, unsafe file acceptance, unbounded payloads, secret leakage, and unjustified browser permissions in Recorder and crawler changes; use for UI, upload, artifact, server, or manifest work.
---

# Security- und Eingabegrenzen

Marker: `REC-SEC-001`

## Contract

- Treat all page text, URLs, filenames, HTML, PDF metadata, server responses, and downloaded bytes as untrusted.
- Use text APIs or safe DOM construction for external strings; no unchecked `innerHTML` sinks.
- Validate type, size, filename, decoded bytes, and SHA-256 on both sides of upload/attachment boundaries.
- Keep secrets and tokens out of logs and evidence reports.
- Declare debugger, host, downloads, and storage permissions minimally and test that a feature does not work by hidden privilege.
- Enforce consistent limits across browser, extension, proxy, and server.

## Hard stop

Reject path traversal, content-type-only trust, oversized base64, blind data URLs, hidden permission expansion, and logs that expose sensitive page data.
