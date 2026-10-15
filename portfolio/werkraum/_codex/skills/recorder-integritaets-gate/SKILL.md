---
name: recorder-integritaets-gate
description: Enforces the Recorder build contract. Use before and after every recorder, crawler, fetch, download, replica, UI, or live-browser change; missing contracts or evidence block the work.
---

# Recorder-Integritäts-Gate

Marker: `REC-GATE-001`

Use this skill for every task touching the Browser Recorder, crawler, collection workspace, artifact server, export, replica, or live acceptance.

## Hard stop

Run the contract gate before writing code:

```bash
python3 /root/werkraum/_codex/tools/check_recorder_skill_gates.py contracts
```

Select the stage from `registry.json`. After the stage, create the small Markdown evidence report and run:

```bash
python3 /root/werkraum/_codex/tools/check_recorder_skill_gates.py evidence \
  --stage <stage> --evidence <report.md>
```

Exit code 0 is the only release condition. A green unit test cannot replace this gate. `unknown`, `not checked`, missing screenshots, or missing persistence readback never count as `PASS`.

## Required behavior

- Load every skill listed for the selected stage; do not silently omit one.
- Map every implementation or live action to its marker.
- Stop on the first contradiction between screen, DOM, persisted state, file bytes, and hashes.
- Keep raw source, projection, export, and replica claims separate.
- Record open limits explicitly instead of upgrading them to success.

## Evidence format

The evidence file must contain `EVIDENCE_VERSION: 1`, one exact `PASS` line per required marker, and the concrete artifact or observation after the dash:

```md
EVIDENCE_VERSION: 1
- REC-EYE-001: PASS — /tmp/before.png, /tmp/after.png, URL and DOM reread attached
```

The checker rejects a marker without `PASS` and rejects an absent report.
