---
name: recorder-download-abnahme
description: Verifies that Recorder downloads and exports really completed and match their source bytes, type, size, and hash; use for Chrome downloads, PDF, Markdown, office, and artifact exports.
---

# Download-Abnahme

Marker: `REC-DOWNLOAD-001`

## Contract

“Download started” is not “download complete”. For every export:

1. Record the source artifact hash, byte count, media type, and intended filename.
2. Start the download or attachment once.
3. Observe completion or interruption (`chrome.downloads.onChanged` where applicable).
4. Read the produced file back when the environment permits.
5. Recompute byte count, media type, and SHA-256; compare with the source and persist the result.

For Markdown/PDF, compare the original source file and generated/downloaded file separately, including text/page structure. A projection is not a byte-identical source.

## Hard stop

No completion claim from a returned download ID, a visible link, a base64 string, or a green test alone. Size limits must be consistent across UI, extension, proxy, and server.
