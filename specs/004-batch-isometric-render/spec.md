# Feature Specification: Batch Isometric Render

**Feature Branch**: `004-batch-isometric-render`

**Created**: 2026-05-29

**Status**: Draft

## User Scenarios & Testing

### User Story 1 — Batch Render All Rooms (Priority: P1)

The artist provides a folder of clean SVGs. The system detects all rooms across all files, builds isometric scenes, and renders PNG previews in batch using Blender headless mode.

**Why this priority**: Manual room-by-room rendering does not scale when the artist has dozens of rooms.

**Independent Test**: Place 3 test SVGs in a folder, run batch render, verify 3+ PNG previews appear.

**Acceptance Scenarios**:

1. **Given** a folder with 3 SVGs containing rooms, **When** batch render runs, **Then** one PNG per room is generated in `outputs/preview/`.
2. **Given** a batch run, **When** complete, **Then** manifest is updated with all new entries.
3. **Given** a previously rendered room with no changes, **When** batch re-runs, **Then** it is skipped (or version incremented per config).

---

### User Story 2 — Style Override for Batch (Priority: P2)

The artist can specify a style preset that applies to all rooms in the batch.

**Acceptance Scenarios**:

1. **Given** `--style grayscale_blockout`, **When** batch runs, **Then** all previews use grayscale style.

---

### Edge Cases

- What if one SVG fails and the rest succeed?
- What if Blender crashes mid-batch?

## Requirements

- **FR-001**: System MUST accept a folder of clean SVGs as input
- **FR-002**: System MUST detect rooms in each SVG automatically
- **FR-003**: System MUST render each room as a separate PNG
- **FR-004**: System MUST update manifest for all generated outputs
- **FR-005**: System MUST handle individual failures without aborting the entire batch
- **FR-006**: System MUST log progress with room count (e.g., "Rendering 3/12...")

## Success Criteria

- **SC-001**: Batch of 10 rooms renders in <10 minutes
- **SC-002**: Individual room failure does not abort batch
- **SC-003**: Manifest reflects all successfully rendered rooms

## Assumptions

- Feature 001 (single room render) is implemented and working
- Feature 002 (SVG cleanup) has been used on input files
- Blender LTS 4.x is installed

## Render Settings (Research-Sourced)

From the Vietnamese research document, the recommended batch render defaults:

| Setting | Value | Rationale |
|---------|-------|-----------|
| Engine | EEVEE | Fast preview; use CYCLES only for `review_render` style preset |
| Transparent BG | `film_transparent = True` | PNG alpha for compositing |
| Resolution | 2048×2048 | Production quality, configurable per style |
| Camera type | Orthographic | No perspective distortion |
| Camera rotation | X=54.7356°, Z=45° | Strict isometric (or 2:1 dimetric variant) |
| Lighting | Sun lamp, rotation (45°, 0°, 35°) | Consistent shadow direction |
| Output format | PNG with RGBA | Transparent backgrounds |

## Camera Validation Test

Before batch rendering, each scene must pass a camera validation:
- Place a unit cube at the origin
- Render a single frame
- Verify three axes have visually equal foreshortening
- This test must run once per camera preset change, not on every batch

## Regression Test Design (from Research)

After each batch run, log and compare:
1. Number of paths per SVG (before/after cleanup)
2. Total bounding box of each scene
3. Time per room render
4. Number of files successfully rendered vs failed

Two mandatory test scenes: **motel room** and **island map**.

## Research Incorporated

This spec was updated on 2026-05-29 with findings from:
- **Kế hoạch bán tự động hóa pipeline art cho Tứ Phương Vô Lộ** — Render settings (EEVEE, film_transparent, 2048×2048), camera math (54.7356° tilt, 45° yaw), camera validation test (cube foreshortening check), regression test design (path count, bbox, render time), mandatory test cases (motel room + island map).
- **Indie Game Art Workflow Automation Research** — Batch export via Illustrator Export for Screens (complementary 2D batch), production risk mitigations (style inconsistency, platform instability).
