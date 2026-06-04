# Feature Specification: Visual Fidelity MVP

**Feature Branch**: `workflow/maya-first-artist-pipeline`

**Created**: 2026-06-04

**Status**: Approved for implementation

**Input**: User request for Feature 014A: add a reusable, safe, post-build Maya visual fidelity pass for warehouse-style rooms.

## User Scenarios & Testing

### User Story 1 - Plan Visual Fidelity Without Maya (Priority: P1)

The artist/developer can run a dry-run report from existing geometry JSON and see exactly what visual additions would be created.

**Why this priority**: The pass must be safe and inspectable before any Maya scene is written.

**Independent Test**: Run the CLI with `--geometry-json`, `--preset warehouse_v0`, `--dry-run`, and `--report-json`; verify the report contains room name, prop counts, planned additions, warnings, and safety status.

**Acceptance Scenarios**:

1. **Given** valid blockout geometry JSON, **When** dry-run mode runs, **Then** no Maya executable is required and no `.ma` output is created.
2. **Given** known warehouse prop markers, **When** planning runs, **Then** wooden crates, barrels, shelves, floor grate, and electrical cabinet produce visual plans.

---

### User Story 2 - Apply Additive Maya Visual Fidelity (Priority: P1)

The operator can run a post-build pass after `build_maya_room.py` to produce a different `.ma` scene with visual detail helpers.

**Why this priority**: The current blockout is technically correct but visually too subtle for next-day artist review.

**Independent Test**: Run actual mode with `mayapy.exe`, a source `.ma`, geometry JSON, and a distinct output `.ma`; verify the source scene is not overwritten and all additions are under `GRP_visual_fidelity_v0`.

**Acceptance Scenarios**:

1. **Given** an input `.ma` and a different output `.ma`, **When** actual mode runs, **Then** the output scene contains a top-level visual fidelity group.
2. **Given** input and output scene paths are equal, **When** actual mode runs, **Then** the command fails before launching Maya.

---

### User Story 3 - Artist Operator Guidance (Priority: P2)

The artist/operator can read Vietnamese documentation for what the pass does, what it does not do, and how to roll back safely.

**Why this priority**: The pipeline is artist-first and Windows-first.

**Independent Test**: Open `docs/visual_fidelity_mvp_vi.md` and verify commands, safety rules, Maya open/toggle workflow, and rollback notes are present.

**Acceptance Scenarios**:

1. **Given** the operator has a generated blockout, **When** they follow the doc, **Then** they can dry-run first and then write an external visual fidelity scene.
2. **Given** the visual pass is not desired, **When** the operator hides/deletes `GRP_visual_fidelity_v0` or opens the source scene, **Then** rollback is clear.

## Edge Cases

- Unknown prop types must not crash; they are reported as warnings and skipped.
- Missing `center_maya` must not crash; the marker is skipped with a warning.
- Approximate path bounding boxes must use conservative default sizes.
- Dry-run with an output path must not create that output path.
- Actual mode must refuse to overwrite the input scene.

## Requirements

### Functional Requirements

- **FR-001**: The pass MUST be a standalone post-build workflow and not make `build_maya_room.py` visual fidelity mandatory.
- **FR-002**: Dry-run mode MUST work without Maya installed.
- **FR-003**: Actual mode MUST require `--output-scene` to differ from `--input-scene`.
- **FR-004**: All Maya additions MUST be under the top-level group `GRP_visual_fidelity_v0`.
- **FR-005**: The pass MUST plan or create recognizable templates for `wooden_crate`, `barrel`, `shelf_unit`, `floor_grate`, and `electrical_cabinet`.
- **FR-006**: The pass MUST add agent-owned review camera, review lighting, optional room presentation helper, and artist notes.
- **FR-007**: The pass MUST use geometry JSON prop markers and room data for placement where available.
- **FR-008**: Dry-run report MUST include room name, prop counts, planned additions, warnings, output path if provided, and safety status.
- **FR-009**: Unknown or incomplete marker data MUST produce warnings, not crashes.
- **FR-010**: The implementation MUST not use Illustrator MCP or Maya commandPort.

### Key Entities

- **VisualPlan**: Dry-run/apply report containing room name, preset, group name, prop counts, planned additions, warnings, paths, and safety status.
- **VisualAddition**: One planned prop template or presentation helper with template name, placement, size, source marker, and details.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Dry-run report works with no Maya runtime and exits 0 for valid geometry JSON.
- **SC-002**: Known 013B prop types all produce visual template plans.
- **SC-003**: Actual mode cannot overwrite its input scene.
- **SC-004**: Unit tests cover CLI help, dry-run, planning, path safety, group naming, known/unknown props, and tracked output safety.

## Assumptions

- Geometry JSON comes from the existing Maya-first pipeline and includes `prop_markers` with `center_maya`.
- The MVP may create simple proxy geometry, not final art assets.
- Actual apply validation that opens Maya is environment-dependent and uses `mayapy.exe`.
