# Tasks: Illustrator Export & Clean SVG

**Input**: Design documents from `/specs/002-illustrator-export-clean-svg/`

## Phase 1: Setup

- [x] T001 Create Illustrator JSX script skeleton with header/docstring
- [x] T002 [P] Set up Python cleanup module structure

---

## Phase 2: Illustrator JSX Scripts

- [x] T003 [US1] Implement `export_clean_svg.jsx` — export active document as SVG preserving layer names
- [x] T004 [US1] Add artboard iteration for multi-artboard export
- [x] T005 [US1] Add output path configuration (default: `assets/2d/svg_raw/`)
- [x] T006 [US2] Implement `organize_layers.jsx` — rename layers to convention
- [ ] T007 [P] Implement `batch_export_assets.jsx` — batch export selected artboards
- [ ] T008 [P] Create `isometric_transform_helper.jsx` — isometric skew/rotate utilities

**Checkpoint**: JSX scripts export clean SVG from Illustrator

---

## Phase 3: Python SVG Cleanup

- [x] T009 [US3] Implement `clean_svg_paths.py` — vpype simplification pipeline
- [x] T010 [US3] Add transform flattening logic
- [x] T011 [US3] Add hidden element removal
- [x] T012 [US3] Implement `validate_svg_contract.py` — check SVG meets clean contract
- [x] T013 [US3] Add unit tests in `tests/test_svg_cleanup.py`

**Checkpoint**: SVG cleanup pipeline produces validated clean SVG

---

## Phase 4: Integration & Launchers

- [x] T014 Create `02_clean_svg.bat` launcher
- [x] T015 Add Vietnamese error messages
- [ ] T016 Write quickstart.md verification steps

---

## Dependencies

- Phase 1: No dependencies
- Phase 2: Depends on Phase 1 (JSX skeleton)
- Phase 3: Depends on Phase 1 (Python setup)
- Phase 4: Depends on Phase 2 + 3
- Phases 2 and 3 can run in parallel
