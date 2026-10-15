---
name: recorder-ack-queue-integritaet
description: Protects Recorder event delivery from false acknowledgements, duplicate sends, unbounded retries, and ignored queue limits; use for queue, background transport, event, or retry changes.
---

# ACK- und Queue-Integrität

Marker: `REC-ACK-001`

## Contract

- Every event has a stable `event_id`; every batch has a stable `batch_id`.
- An event is delivered only after a validated server acknowledgement for that exact event.
- A missing, malformed, partial, or contradictory response is failure, never implicit success.
- Retry is bounded, age-limited, jittered, and ends in an inspectable dead-letter state.
- `maxQueueSize` is enforced in the write path, not merely present in config.
- Restart and duplicate delivery are idempotent and tested.

## Required test cases

Test success, HTTP 4xx/5xx, timeout/abort, malformed ACK, partial ACK, duplicate event, queue overflow, retry exhaustion, and restart recovery. Read the queue and server state after each case.

## Forbidden shortcuts

Never mark delivered because `fetch()` resolved, because `results[0]` exists optionally, or because a test returned green without inspecting the acknowledgement payload.
