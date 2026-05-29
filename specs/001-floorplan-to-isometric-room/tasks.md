# Tasks: Floorplan to Isometric Room

**Input**: Design documents from `/specs/001-floorplan-to-isometric-room/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts.md

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

**Purpose**: Project dependencies and configuration validation

- [ ] T001 Verify Python 3.10+ is available and create venv
- [ ] T002 [P] Install svgpathtools, PyYAML, click dependencies
- [ ] T003 [P] Verify Blender is installed and accessible from PATH or config
- [x] T004 Validate config/room_presets.yaml and config/style_presets.yaml parse correctly

---

## Phase 2: Foundational — SVG Parsing

**Purpose**: Core SVG-to-room extraction that all user stories depend on

- [x] T005 Implement `detect_rooms_from_svg.py` — parse SVG, identify named layers/groups as rooms
- [x] T006 [P] Implement room boundary extraction — convert SVG paths to wall segments
- [ ] T007 [P] Implement `validate_svg_contract.py` — check SVG meets clean SVG requirements
- [ ] T008 Add unit tests for SVG room detection in `tests/test_svg_cleanup.py`

**Checkpoint**: SVG parsing works — can extract room names and wall paths from clean SVG

---

## Phase 3: User Story 1 — Single Room Isometric Draft (P1) 🎯 MVP

**Goal**: Generate a PNG preview + Blender scene from a single room in a clean SVG

### Implementation

- [x] T009 [US1] Create `build_isometric_room.py` Blender script skeleton
- [ ] T010 [US1] Implement SVG path → Blender curve import
- [x] T011 [US1] Implement curve → mesh → extrude walls workflow
- [x] T012 [US1] Implement floor plane generation from room boundary
- [x] T013 [US1] Implement orthographic isometric camera setup (30° angle, ORTHO)
- [x] T014 [US1] Implement basic lighting setup
- [x] T015 [US1] Implement PNG render with transparent background
- [x] T016 [US1] Implement .blend scene save
- [x] T017 [US1] Implement output filename generation per naming convention
- [x] T018 [US1] Create `03_build_isometric_room.bat` launcher
- [x] T019 [US1] Add Vietnamese error messages for common failures

**Checkpoint**: Artist can run .bat → get PNG preview + .blend file for one room

---

## Phase 4: User Story 2 — Style Presets (P2)

**Goal**: Apply different visual styles to the room render

- [x] T020 [US2] Implement style preset loader from `config/style_presets.yaml`
- [x] T021 [US2] Apply floor/wall colors from preset to Blender materials
- [x] T022 [US2] Apply lighting settings from preset
- [ ] T023 [US2] Apply shadow settings from preset
- [x] T024 [US2] Add `--style` CLI argument to build_isometric_room.py

**Checkpoint**: Same room renders differently with different presets

---

## Phase 5: User Story 3 — Room Preset Props (P2)

**Goal**: Place placeholder props based on room type

- [ ] T025 [US3] Implement `props_library.py` — basic prop geometry generators
- [x] T026 [US3] Implement room preset loader from `config/room_presets.yaml`
- [x] T027 [US3] Implement prop placement logic (along_wall, center, corner, etc.)
- [x] T028 [US3] Add `--room-preset` CLI argument
- [x] T029 [US3] Handle unknown room preset gracefully (empty room + warning)

**Checkpoint**: Rooms have appropriate placeholder furniture based on type

---

## Phase 6: User Story 4 — Manifest (P3)

**Goal**: Track all generated outputs in manifest

- [ ] T030 [US4] Implement manifest writer in `scripts/python/manifest.py`
- [x] T031 [US4] Integrate manifest update into build_isometric_room.py
- [x] T032 [US4] Add checksum calculation for generated files
- [ ] T033 [US4] Add unit tests for manifest in `tests/test_manifest.py`

**Checkpoint**: Every build run creates/updates manifest entry

---

## Phase 7: Polish

- [ ] T034 [P] End-to-end test with example motel_room SVG
- [x] T035 [P] Write quickstart.md verification steps
- [ ] T036 [P] Update README with feature 001 status
- [ ] T037 Code cleanup and docstring review

---

## Dependencies & Execution Order

- Phase 1 (Setup): No dependencies
- Phase 2 (SVG Parsing): Depends on Phase 1
- Phase 3 (US1 - MVP): Depends on Phase 2
- Phase 4 (US2 - Styles): Depends on Phase 3
- Phase 5 (US3 - Props): Depends on Phase 3
- Phase 6 (US4 - Manifest): Can start after Phase 3
- Phase 7 (Polish): Depends on all prior phases

### Parallel Opportunities

- T002 and T003 can run in parallel (setup)
- T006 and T007 can run in parallel (SVG parsing)
- Phase 4 and Phase 5 can run in parallel (both depend on Phase 3)
- Phase 6 can overlap with Phase 4/5
