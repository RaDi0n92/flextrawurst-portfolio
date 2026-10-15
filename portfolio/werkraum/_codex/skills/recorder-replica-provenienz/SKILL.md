---
name: recorder-replica-provenienz
description: Defines honest raw-source, resource, projection, export, and replay bundles for Recorder replicas; use when building WARC/WACZ-like bundles, replicas, replays, or source/output comparisons.
---

# Replica-Provenienz

Marker: `REC-REPLICA-001`

## Contract

Every replica bundle has a manifest containing capture ID/time, active tab and source URL, mode, raw artifacts, resource registry, response metadata, hashes, limits, and known gaps. Each artifact is labeled `raw`, `projection`, `export`, or `replay`.

- Raw HTML/text/screenshot/PDF/Markdown are never silently substituted for one another.
- A generated projection retains a pointer and hash of its raw input.
- Resources record whether they were visible, fetched, blocked, missing, or synthetic.
- Replay is limited to what the bundle actually contains; it must not fetch the live site secretly.
- Compare source and produced/downloaded files with bytes, hashes, text, and structure before claiming fidelity.

## Hard stop

Do not call a shell with missing resources a replica, and do not call a generated PDF proof of original-page completeness.
