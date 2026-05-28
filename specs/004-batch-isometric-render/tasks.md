# Tasks: Batch Isometric Render

**Input**: Design documents from `/specs/004-batch-isometric-render/`

**Prerequisites**: Feature 001 must be implemented first.

## Phase 1: Setup

- [ ] T001 Verify Feature 001 (build_isometric_room.py) is functional
- [ ] T002 Create batch orchestrator skeleton in `scripts/blender/batch_render_rooms.py`

---

## Phase 2: Batch Processing

- [ ] T003 [US1] Implement folder scanner for clean SVGs
- [ ] T004 [US1] Implement room detection across multiple SVGs
- [ ] T005 [US1] Implement batch loop calling build_isometric_room per room
- [ ] T006 [US1] Add progress logging ("Rendering 3/12...")
- [ ] T007 [US1] Add error resilience — continue on individual failure
- [ ] T008 [US1] Batch update manifest with all results

---

## Phase 3: Style Override

- [ ] T009 [US2] Add `--style` CLI argument for batch-wide style override
- [ ] T010 [US2] Pass style preset to each room render call

---

## Phase 4: Integration

- [ ] T011 Create `04_batch_render.bat` launcher
- [ ] T012 Write quickstart.md verification steps

---

## Dependencies

- Depends on Feature 001 being complete
- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2
