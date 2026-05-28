# Tasks: Maya Bridge

**Input**: Design documents from `/specs/005-maya-bridge/`

**Prerequisites**: Feature 001 (Blender pipeline) should be implemented first for reference.

## Phase 1: Camera Setup

- [ ] T001 [US1] Implement `setup_iso_camera.py` — create orthographic isometric camera in Maya
- [ ] T002 [US1] Match camera parameters to Blender isometric setup
- [ ] T003 [US1] Test with mayapy in headless mode

---

## Phase 2: SVG Import

- [ ] T004 [US2] Research SVG → Maya import options (USD bridge, custom parser, direct)
- [ ] T005 [US2] Implement `import_svg_walls.py` — chosen import method
- [ ] T006 [US2] Handle wall extrusion in Maya
- [ ] T007 [US2] Apply materials from style presets

---

## Phase 3: Batch Render

- [ ] T008 [US3] Implement `batch_render.py` — headless render via mayapy
- [ ] T009 [US3] Output to `outputs/maya/` with naming convention
- [ ] T010 [US3] Update manifest

---

## Phase 4: Integration

- [ ] T011 Graceful failure when Maya is not installed
- [ ] T012 Write quickstart.md verification steps

---

## Dependencies

- Reference Feature 001 Blender pipeline for camera parameters
- Independent of Blender pipeline execution
