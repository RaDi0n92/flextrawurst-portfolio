# Reference manifest and comparison matrix

Create one manifest per Blender task. Keep it next to the evidence for the
task and never overwrite the original references.

## Manifest schema

```yaml
manifest_version: 1
task: "Daniel's exact request"
created_at: "UTC timestamp"
reference_revision: "short stable id"
references:
  - id: ref-01
    source: "/absolute/path/or/url"
    provenance: "who supplied it and how it was obtained"
    priority: 1
    controls:
      composition: "fact or unknown"
      silhouette: "fact or unknown"
      proportions: "fact or unknown"
      camera: "fact or unknown"
      palette: "fact or unknown"
      materials: "fact or unknown"
      lighting: "fact or unknown"
      negative_space: "fact or unknown"
      motion: "fact or unknown"
      non_negotiable: []
    tolerance:
      framing: "for example: subject bbox within 3%"
      placement: "for example: <= 0.02 Blender units"
      color: "for example: visual match; numeric only if color data exists"
      detail: "for example: explicit list or unknown"
```

`unknown` is a valid value. It means the reference does not prove that
criterion; it does not mean “use the agent’s best guess”.

## Comparison matrix

Use one row for every criterion that matters:

```text
criterion | reference fact | observed screenshot/state | delta | tolerance | status | next minimal action
```

Allowed statuses are `PASS`, `FAIL`, and `UNKNOWN`. A `PASS` must point to a
sample or final screenshot and, when the criterion is structural, a field in
the world-state snapshot. A `FAIL` must name the smallest correction. An
`UNKNOWN` must name the missing evidence or the unresolved choice.

## Reference priority

When references disagree, use the lowest numerical `priority` as the stronger
constraint, preserve both observations, and report the conflict. Do not blend
conflicting silhouettes, cameras, or palettes without Daniel choosing which
reference governs.
