# Feature 008E: Door/Window SVG Marker Diagnostics

## User Story

As the artist, I need the pipeline to detect explicit `door_` and `window_`
markers when Illustrator preserves their names in common SVG metadata fields,
and I need clear Vietnamese diagnostics when the exported SVG does not preserve
those marker names.

## Requirements

- Detect door/window markers only from explicit exported labels or names:
  `id`, `data-name`, `aria-label`, `title`, namespaced label attributes,
  `label`, `name`, other `data-*` metadata, or a child `<title>`.
- Do not infer openings from unlabeled visual rectangles or other shapes.
- Keep room boundary detection strict; curved path fallback is marker-only.
- Preflight must list door/window marker names when found.
- Preflight and dry-run must clearly say when no `door_`/`window_` marker exists
  in the SVG export.
- Geometry JSON must include `opening_markers` when valid markers are present.
- Maya scene generation remains driven by the existing geometry JSON contract.

## Non-Goals

- No AI API, web UI, Feature 006 work, or new required dependencies.
- No mutation of `.ai`, source SVG, generated Maya scenes, or output artifacts.
- No automatic invention of `door_main` when the SVG export lacks an explicit marker.

## Success Criteria

- Inline SVG with `<g id="door_main">` reports one marker in preflight, detection,
  and Maya geometry JSON.
- Variant with `data-name="door_main"` and generic `id` is detected.
- Variants with `aria-label`, `title`, and child `<title>` are detected.
- `window_*` markers are emitted as `marker_type=window`.
- A door-like rectangle without explicit `door_`/`window_` naming is ignored.
