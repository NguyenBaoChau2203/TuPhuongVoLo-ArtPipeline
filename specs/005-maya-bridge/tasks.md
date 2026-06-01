# Tasks: Maya Bridge

**Input**: Design documents from `/specs/005-maya-bridge/`

**Correction applied**: Feature 005 treats Maya as the primary production DCC backend for the Illustrator + Maya artist workflow. Blender remains optional/fallback legacy MVP code and is not required for Feature 005 tests.

## Phase 1: Maya-First Build Wrapper

- [X] T001 Implement `scripts/python/build_maya_room.py` CLI wrapper
- [X] T002 Reuse existing Python SVG detection and room geometry logic
- [X] T003 Select room by normalized Vietnamese/ASCII room name
- [X] T004 Load style and room presets from config
- [X] T005 Create geometry JSON handoff for Maya
- [X] T006 Resolve Maya/mayapy executable from CLI, config, or PATH
- [X] T007 Support dry-run planning without Maya
- [X] T008 Name `.ma` outputs using `tu_phuong_vo_lo_{asset_name}_{variant}_maya_v{version}`
- [X] T009 Update manifest only after verified successful Maya `.ma` generation

## Phase 2: Maya Scene Script

- [X] T010 Implement `scripts/maya/build_maya_room_scene.py`
- [X] T011 Initialize Maya standalone safely when running under mayapy
- [X] T012 Read geometry JSON instead of parsing SVG directly in Maya
- [X] T013 Create floor mesh, wall blocks, simple placeholder props, materials, lights, and isometric camera
- [X] T014 Save editable Maya ASCII `.ma` scene
- [X] T015 Verify actual Maya execution on a machine with Autodesk Maya/mayapy installed

## Phase 3: Batch Maya Wrapper

- [X] T016 Implement `scripts/python/batch_maya_room.py`
- [X] T017 Support `--input-dir`, `--input-file`, and `--job-file`
- [X] T018 Support `--all-rooms`, `--room`, `--stop-on-error`, and dry-run mode
- [X] T019 Write JSON report to `outputs/reports/batch_maya_report.json`
- [X] T020 Continue past corrupt SVGs by default

## Phase 4: Artist Launchers and Docs

- [X] T021 Add `launchers/07_build_maya_room.bat`
- [X] T022 Add `launchers/08_batch_maya_room.bat`
- [X] T023 Update `docs/HOW_TO_USE_FOR_ARTIST_VI.md`
- [X] T024 Update `README.md` to document Maya as primary DCC backend
- [X] T025 Update `specs/005-maya-bridge/quickstart.md`

## Phase 5: Tests and Validation

- [X] T026 Add `tests/test_build_maya_room.py`
- [X] T027 Add `tests/test_batch_maya_room.py`
- [X] T028 Unit tests do not require Maya
- [X] T029 Dry-run does not update manifest
- [X] T030 Existing Feature 001/002/003/004 tests remain supported

## Phase 6: SVG Prop Marker Placement (005.3)

- [X] T031 Define `prop_`, `item_`, and `object_` marker naming convention
- [X] T032 Detect nested SVG prop marker geometry in the Python SVG layer
- [X] T033 Include `prop_markers` with SVG/local/Maya centers in geometry JSON
- [X] T034 Create deterministic Maya placeholder cubes from `prop_markers`
- [X] T035 Prefer explicit SVG markers over room-preset auto props
- [X] T036 Add `tests/in/illustrator_prop_markers.svg` fixture and non-Maya tests
- [X] T037 Update Vietnamese artist checklist with prop marker guidance

## Notes

Verified manually on artist/DCC machine with Autodesk Maya 2024 mayapy.exe. .ma output generated and opened successfully in Maya. Scene contained floor, walls, props, camera, and lights.
