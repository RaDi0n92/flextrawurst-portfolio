---
name: blender-live-reference-qa
description: "Control and review a live Blender session with 10 Hz visual evidence, structured scene readback, and reference-based comparison; use for Blender scene creation, editing, animation, rendering, or correction when visual fidelity matters."
---

# Blender Live Reference QA

Use this skill for live Blender work in which the result must be visibly checked while it is being made and aligned against supplied or selected references. It is not required for metadata-only inspection or a headless file conversion that has no live visual result.

## Operating contract

The goal is an auditable Blender change, not merely a successful Python call. Treat the live viewport, the structured Blender state, and the reference set as three independent witnesses. A claim of “done” requires them to agree.

Use the connected Blender MCP tools when they are available:

- `get_addon_info` and `ping` for the connection handshake.
- `get_scene_info` for a compact initial inventory.
- `get_viewport_screenshot` for visible evidence.
- `get_world_state_snapshot` for transforms, bounds, materials, camera, lights, animation, and frame state.
- `execute_code` for one deliberately scoped Blender mutation at a time.

If the MCP tool surface is not directly exposed but the local bridge is available, use the bundled `scripts/capture_trajectory.py` for observation and the existing serialized TCP bridge at `127.0.0.1:9876`. Do not start a second Blender, add-on server, or MCP bridge when one is already live. Never issue overlapping commands over one bridge connection.

## Reference-first gate

Before changing Blender, identify every reference that is actually in scope and preserve its provenance. Do not rewrite, resize, recolor, or silently replace a reference to make comparison easier.

Create a small reference manifest using the schema in [references/reference-manifest.md](references/reference-manifest.md). Record what each reference controls: composition, silhouette, proportions, camera, palette, materials, lighting, negative space, motion, and non-negotiable details. If references conflict, record their priority instead of averaging them invisibly.

Inspect references at the same meaningful scale and view as the Blender result. Use image inspection for local images and Blender screenshots for the live scene. Separate visual facts from interpretation and mark missing or ambiguous facts as `unknown`.

## Observation and action loop

For every meaningful live action:

1. Capture a baseline viewport screenshot and a structured world-state snapshot. Record the active scene, frame, selected objects, camera, and reference-manifest revision.
2. Perform exactly one mutation unit: one focused `execute_code` transaction, one import, one material adjustment, one camera adjustment, or one other named operation. Split large scripts into observable units.
3. During any operation or transition lasting longer than 100 ms, sample the viewport and world state at a 100 ms cadence (10 Hz). Use `scripts/capture_trajectory.py` when a repeatable capture window is needed. Record scheduled time, actual time, interval drift, screenshot path, screenshot hash, and readback result for every sample.
4. Capture the immediate after-state even when the operation was faster than one interval.
5. Compare the after-state and the 10-Hz samples to the expected action and the reference manifest. A screenshot is evidence of what was visible; a state snapshot is evidence of what Blender held. Neither substitutes for the other.

The 100 ms interval is an evidence cadence, not permission to hide a long unobservable script. If Blender blocks the main thread and samples arrive late, record the late interval and split the next attempt into smaller actions. Never label a missed interval as `PASS`.

## Reference comparison and correction

After each action, maintain an explicit comparison matrix:

`criterion | reference fact | observed screenshot/state | delta | tolerance | status | next minimal action`

Check in this order: framing and silhouette, relative proportions and placement, camera and perspective, materials and palette, lighting and shadows, animation/frame behavior, then fine detail. Use tolerances appropriate to the criterion; do not “improve” a result by optimizing unrelated details.

If a criterion fails, make the smallest corrective action that addresses that criterion, then repeat the baseline/action/10-Hz/after loop. Do not batch several speculative fixes. If the evidence is ambiguous or the reference does not determine the intended result, stop that branch as `UNKNOWN` and state what decision is needed.

## Evidence record

For each meaningful Blender stage, write evidence under `/root/werkraum/_codex/berichte/blender/` (or the active project’s declared evidence directory). Keep screenshots, `trajectory.jsonl`, the reference manifest, the comparison matrix, and the final structured readback together. The report must contain:

- `BLENDER-EYE-001: PASS` only when the required 10-Hz or immediate before/after visual evidence exists and cadence drift is recorded.
- `BLENDER-REF-001: PASS` only when all in-scope reference criteria have a manifest entry and a comparison status.
- `BLENDER-READ-001: PASS` only when the final Blender state was reread after the last mutation.
- `BLENDER-ACT-001: PASS` only when each mutation is named and bounded as one action unit.
- `BLENDER-QA-001: PASS` only when observed deltas are within tolerance or explicitly accepted by Daniel.

Keep test output separate from visible evidence. A successful `execute_code` response, a render file, or a green script exit code does not prove visual correctness. If any required witness is missing, use `UNKNOWN`, not an inferred success.

## Safety and provenance boundaries

- Preserve the existing scene, object names, reference files, materials, camera conventions, and user edits unless the request explicitly changes them.
- Do not delete or overwrite objects, references, `.blend` files, or renders without naming what would be lost and receiving explicit replacement intent.
- Do not quit Blender, restart its add-on, restart the virtual desktop, or start a competing bridge as part of ordinary QA.
- Treat `execute_code` as a powerful mutation surface. Keep code small, log the intended effect, and reread the result.
- Before any persistent file, add-on, configuration, or scene-file write, follow the project’s required backup checkpoint and write only the declared scope.

## Reusable helper

Run the observer for a short evidence window like this:

```bash
python3 scripts/capture_trajectory.py \
  --output /root/werkraum/_codex/berichte/blender/<stage> \
  --duration 2.0 \
  --interval 0.1 \
  --label <action-or-stage>
```

The helper is observational: it does not mutate Blender. Read [references/reference-manifest.md](references/reference-manifest.md) before building the comparison matrix, and keep the final report concise enough that another agent can audit it without opening every image.

The helper exits `0` only when the requested cadence is measured successfully, `1` when one or more captures fail, and `3` when captures exist but the 10-Hz cadence is not proven. A slow backend is therefore a visible QA failure, not a falsely successful run. The summary records `cadence_met`, `cadence_status`, expected versus successful samples, measured intervals, and the capture method.
