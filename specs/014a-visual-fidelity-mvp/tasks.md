# Tasks: Visual Fidelity MVP

**Input**: Design documents from `specs/014a-visual-fidelity-mvp/`

**Prerequisites**: `spec.md`, `plan.md`

**Tests**: Required by Feature 014A.

## Phase 1: Setup and Audit

- [X] T001 Confirm initial git status, branch, and recent commits.
- [X] T002 Run pre-change test suite.
- [X] T003 Inspect Feature 005 Maya build wrapper, Maya scene builder, geometry JSON schema, tests, and handoff docs.

## Phase 2: Core Implementation

- [X] T004 Add `scripts/python/maya_visual_fidelity_pass.py` standalone CLI with dry-run planning and path safety.
- [X] T005 Add `scripts/maya/apply_visual_fidelity_pass.py` mayapy writer with additive `GRP_visual_fidelity_v0` output behavior.
- [X] T006 Implement visual templates for wooden crate, barrel, shelf unit, floor grate, and electrical cabinet.
- [X] T007 Implement review camera, review lights, room presentation helper, and artist note metadata.

## Phase 3: Tests

- [X] T008 Add tests for CLI help and dry-run report without Maya.
- [X] T009 Add tests for prop detection/planning, stable group name, known props, and unknown prop warnings.
- [X] T010 Add tests for input/output path safety and dry-run no-output behavior.
- [X] T011 Add tracked output safety test.

## Phase 4: Documentation

- [X] T012 Add Vietnamese operator documentation in `docs/visual_fidelity_mvp_vi.md`.
- [X] T013 Update README minimally with the new feature and command examples.
- [X] T014 Add `quickstart.md` validation notes.

## Phase 5: Validation and Commit

- [X] T015 Run targeted visual fidelity tests.
- [X] T016 Run full test suite.
- [X] T017 Verify external reference hashes are unchanged and generated outputs are not staged.
- [X] T018 Commit with message `feat: add Maya visual fidelity MVP pass`.

## Dependencies & Execution Order

- T001-T003 must complete before implementation.
- T004-T007 are core implementation tasks and may be validated by T008-T011.
- T012-T014 follow after the CLI/API shape is stable.
- T015-T018 complete final validation and commit.
