# Feature Specification: Maya Bridge

**Feature Branch**: `005-maya-bridge`

**Created**: 2026-05-29

**Status**: MVP implemented; actual Maya execution pending local Maya verification

## Correction

The real production artist workflow for this project is Illustrator + Maya. Feature 005 treats Maya as the primary DCC backend. Blender remains available as the previous MVP/fallback backend and must not be removed or required.

## User Scenarios & Testing

### User Story 1 - Maya Room Blockout Dry-Run (Priority: P1)

An artist or developer can choose a clean Illustrator SVG and preview the Maya build plan without Maya installed.

**Why this priority**: Dry-run gives safe feedback on room detection, output naming, and the Maya command without modifying source files or manifest.

**Independent Test**: Run `build_maya_room.py --dry-run` against a clean SVG and verify the planned `.ma` path and Maya command.

### User Story 2 - Python Geometry JSON Handoff (Priority: P1)

Python reuses the existing SVG parsing and room geometry layer to write a geometry JSON handoff for Maya.

**Why this priority**: Maya should not parse SVG directly. The clean SVG and Python validation layer remain the source of truth.

**Independent Test**: Build a plan and write geometry JSON containing `boundary_points` and `wall_segments`.

### User Story 3 - Editable Maya Scene Generation (Priority: P2)

When Maya/mayapy is available, the Maya script reads geometry JSON and saves an editable `.ma` room blockout with floor, walls, placeholder props, lights, and camera.

**Independent Test**: Run `build_maya_room.py` with `--maya-path` on a machine with Maya installed and verify the `.ma` output opens in Maya.

### User Story 4 - Batch Maya Planning (Priority: P2)

A batch wrapper scans one SVG, a folder of SVGs, or a job file and writes a JSON report for planned Maya jobs.

**Independent Test**: Run `batch_maya_room.py --dry-run --json-report ...` and verify planned jobs, failures, and output paths.

### User Story 5 - SVG Prop Marker Placement (Priority: P2)

An artist can place simple named SVG groups/layers such as `prop_shelf_unit`, `item_cardboard_box`, or `object_console_desk` inside a room group. Python detects the marker geometry, writes it to the Maya geometry JSON handoff, and Maya creates deterministic placeholder cubes at those positions.

**Independent Test**: Run `build_maya_room.py --dry-run` against `tests/in/illustrator_prop_markers.svg`, write the geometry JSON, and verify the `prop_markers` payload contains SVG, local, and Maya-space centers.

## Requirements

- **FR-001**: System MUST provide `scripts/python/build_maya_room.py`.
- **FR-002**: System MUST provide `scripts/maya/build_maya_room_scene.py`.
- **FR-003**: System MUST provide `scripts/python/batch_maya_room.py`.
- **FR-004**: Maya scene generation MUST consume geometry JSON, not raw SVG.
- **FR-005**: Dry-run MUST NOT require Maya and MUST NOT update manifest.
- **FR-006**: Actual run MUST update manifest only after a successful verified `.ma` output.
- **FR-007**: Unit tests MUST NOT require Maya.
- **FR-008**: Source SVG files and `drops/` files MUST NOT be modified or deleted.
- **FR-009**: Blender code MUST remain available as optional/fallback legacy MVP backend.
- **FR-010**: Artist-facing launcher/docs MUST be Vietnamese-friendly.
- **FR-011**: SVG prop markers MUST use simple `prop_`, `item_`, or `object_` group/layer names and normalize to a prop type without the prefix.
- **FR-012**: Maya scene generation MUST prefer explicit SVG `prop_markers` over room-preset auto props to avoid duplicate placeholder placement.

## Success Criteria

- **SC-001**: Dry-run resolves room, geometry JSON path, `.ma` output path, and Maya command.
- **SC-002**: Batch dry-run writes `outputs/reports/batch_maya_report.json`.
- **SC-003**: Missing Maya executable fails gracefully in actual mode.
- **SC-004**: Existing Feature 001/002/003/004 tests still pass.
- **SC-005**: Actual Maya execution is documented as environment-dependent until verified locally.
- **SC-006**: Prop marker tests pass without Autodesk Maya installed.
