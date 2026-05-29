# Tasks: Batch Isometric Render

**Input**: Design documents from `/specs/004-batch-isometric-render/`

**Prerequisites**: Feature 001 single-room build, Feature 002 clean SVG validation,
and Feature 003 naming/manifest are already merged.

## Phase 1: Setup

- [X] T001 Verify Feature 001 Python build wrapper is importable and reusable.
- [X] T002 Create batch orchestrator in `scripts/python/batch_isometric_render.py`.

## Phase 2: Batch Planning MVP

- [X] T003 [US1] Implement deterministic non-recursive folder scanner for `.svg` files.
- [X] T004 [US1] Implement room detection across multiple SVG files via `detect_rooms`.
- [X] T005 [US1] Implement batch job creation for one room, `--all-rooms`, and `--room`.
- [X] T006 [US1] Add dry-run planning that does not run Blender or update manifest.
- [X] T007 [US1] Add error resilience so corrupt/failed SVGs are reported and later files continue.
- [X] T008 [US1] Add `--stop-on-error` to stop after the first file/job failure.
- [X] T009 [US1] Write UTF-8 pretty JSON report under `outputs/reports/` by default.

## Phase 3: Style Override

- [X] T010 [US2] Add `--style` CLI argument for batch-wide style override.
- [X] T011 [US2] Pass style and optional room preset through Feature 001 planning/build logic.

## Phase 4: Actual Render Delegation

- [X] T012 Implement actual render mode by delegating each job to Feature 001 build logic.
- [ ] T013 Validate actual Blender batch render on a machine with Blender 4.x installed.

> Note: T012 is implemented, but actual Blender rendering remains pending environment
> verification. Unit tests intentionally do not require Blender.

## Phase 5: Artist Integration and Tests

- [X] T014 Create `launchers/04_batch_isometric_render.bat` with safe dry-run default.
- [X] T015 Keep legacy `launchers/04_batch_render.bat` as a compatibility wrapper.
- [X] T016 Add unit tests in `tests/test_batch_isometric_render.py`.
- [X] T017 Add Vietnamese-facing CLI/launcher error and summary messages.
- [X] T018 Update quickstart verification steps for dry-run and optional actual Blender run.
- [X] T019 Update Vietnamese artist usage documentation.
- [X] T020 Update README feature status.
