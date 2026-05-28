# Feature Specification: Illustrator Export & Clean SVG

**Feature Branch**: `002-illustrator-export-clean-svg`

**Created**: 2026-05-29

**Status**: Draft

**Input**: Artist's Illustrator workflow → organized layers → clean SVG export

## User Scenarios & Testing

### User Story 1 — One-Click SVG Export (Priority: P1)

The artist finishes work in Illustrator, runs a JSX script (or Action), and gets a clean SVG exported to `assets/2d/svg_raw/` with proper layer names preserved.

**Why this priority**: This is the entry point for the entire pipeline — without clean SVG, nothing downstream works.

**Independent Test**: Open a test `.ai` file in Illustrator, run the export script, verify SVG appears in `assets/2d/svg_raw/` with correct layer names.

**Acceptance Scenarios**:

1. **Given** an Illustrator file with named layers, **When** the artist runs `export_clean_svg.jsx`, **Then** an SVG file is created in `assets/2d/svg_raw/` preserving layer names as `<g>` groups.
2. **Given** multiple artboards, **When** the script runs, **Then** each artboard exports as a separate SVG.

---

### User Story 2 — Layer Organization Helper (Priority: P2)

A JSX script helps the artist organize layers with consistent naming conventions before export.

**Why this priority**: Consistent layer names enable reliable room detection downstream.

**Independent Test**: Run `organize_layers.jsx` and verify layers are renamed to convention.

**Acceptance Scenarios**:

1. **Given** an Illustrator file with ad-hoc layer names, **When** `organize_layers.jsx` runs, **Then** layers are renamed with prefix convention (e.g., `room_kho`, `room_sanh_chinh`).

---

### User Story 3 — SVG Cleanup Pipeline (Priority: P1)

After raw SVG export, a Python cleanup pipeline (vpype + svgpathtools) simplifies paths, flattens transforms, removes hidden elements, and validates the SVG.

**Why this priority**: Clean SVG is the source of truth for all downstream tools.

**Independent Test**: Run cleanup on a raw SVG, verify output passes validation.

**Acceptance Scenarios**:

1. **Given** a raw SVG with nested transforms, **When** cleanup runs, **Then** output SVG has flattened transforms.
2. **Given** a raw SVG with hidden layers, **When** cleanup runs, **Then** hidden elements are removed.
3. **Given** a valid clean SVG, **When** validation runs, **Then** it passes with no errors.

---

### Edge Cases

- What if the Illustrator file has locked/hidden layers?
- What if SVG paths use relative coordinates?
- What if the file contains embedded raster images?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide Illustrator JSX scripts for export
- **FR-002**: System MUST preserve layer names as SVG group IDs
- **FR-003**: System MUST export SVG 1.1 compatible files
- **FR-004**: System MUST provide Python cleanup pipeline (vpype + svgpathtools)
- **FR-005**: System MUST flatten all transforms in SVG
- **FR-006**: System MUST remove hidden/invisible elements
- **FR-007**: System MUST validate clean SVG against contract
- **FR-008**: Output filenames MUST follow naming convention

## Success Criteria

- **SC-001**: Illustrator export script produces valid SVG with correct layer names
- **SC-002**: Cleanup pipeline reduces SVG complexity by removing unnecessary elements
- **SC-003**: Validation script catches common SVG issues before downstream consumption
- **SC-004**: Full export-to-clean pipeline completes in <30 seconds for typical files

## Assumptions

- Artist has Adobe Illustrator CC installed on Windows (recommend **29.8.7 LTS** for production stability, **30.4** for R&D)
- Artist organizes layers with meaningful names
- Files are vector-only (no embedded rasters in floorplan layers)
- Illustrator scripting is enabled (*Preferences > General > Enable Scripting*)

## Vectorization Paths (Research-Sourced)

Not all SVGs come from Illustrator direct export. Research identifies two vectorization branches:

| Input Type | Recommended Tool | Output |
|------------|-----------------|--------|
| B&W line art, ink masks, wall contours | `mkbitmap + Potrace 1.16` → `vpype 1.15.0` | Clean SVG paths |
| Color art, logo with transparency, noisy scans | `Vectorizer.AI` (web/API) or `Illustrator Image Trace` | SVG requiring further cleanup |
| SVG from artist with messy nodes | Skip tracing, go directly to `vpype + svgpathtools + Auto-Simplify` | Clean SVG paths |

### vpype Pipeline (research-confirmed commands)

```bash
vpype read input.svg linemerge --tolerance 0.2mm linesort reloop linesimplify write output.svg
```

### svgpathtools Rule-Based Cleanup

Filter out tracing artifacts by path length and bounding box:
- `MIN_LENGTH = 8.0` px — discard paths shorter than this
- `MIN_BBOX_SIDE = 2.0` px — discard paths with both width and height below this

## Clean SVG Gate Criteria

A clean SVG must pass all of these checks before downstream consumption:

- [x] Valid XML / SVG 1.1
- [x] Walls/room boundaries are **closed paths** (no open endpoints)
- [x] No self-intersecting paths on wall geometry
- [x] No zero-length or sub-pixel runt paths
- [x] All transforms flattened (no nested `transform` attributes)
- [x] Layer/group names describe elements (`room_kho`, not `Layer 1`)
- [x] No embedded raster images in geometry layers
- [x] No live Illustrator effects — appearances expanded before export
- [x] UTF-8 encoding

## Illustrator Automation Reference (from Research)

| Script/Tool | Source | Purpose |
|-------------|--------|---------|
| `ExportSequence.jsx` | `creold/illustrator-scripts` (MIT) | Export layers to PNG/SVG sequence |
| `SortLayerItems.jsx` | `creold/illustrator-scripts` (MIT) | Sort/organize layers |
| `TrimMasks.jsx` / `SplitPath.jsx` | `creold/illustrator-scripts` (MIT) | Clean redundant points, split overlapping |
| `alignInCenterOfSpace.js` | `sky-chaser-high/adobe-illustrator-scripts` (MIT) | Grid alignment |
| `stepAndRepeat.js` | `sky-chaser-high/adobe-illustrator-scripts` (MIT) | Asset scattering along paths |
| Illustrator Actions | Built-in | Batch operations (can run on folder, data sets) |
| Export for Screens | Built-in | Multi-artboard/multi-format export (PNG, SVG, PDF, WebP, TIFF) |

## Research Incorporated

This spec was updated on 2026-05-29 with findings from:
- **Indie Game Art Workflow Automation Research** — Osokin/sky-chaser-high script libraries, Illustrator Action/Export for Screens capabilities, Vectorizer.AI and Image Trace comparison.
- **Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ** — Dual vectorization branches (Potrace vs Vectorizer.AI), vpype 1.15.0 CLI pipeline, svgpathtools 1.7.2 rule-based cleanup, clean SVG gate criteria, Illustrator version recommendations (29.8.7 LTS).
