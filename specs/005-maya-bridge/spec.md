# Feature Specification: Maya Bridge

**Feature Branch**: `005-maya-bridge`

**Created**: 2026-05-29

**Status**: Draft

## User Scenarios & Testing

### User Story 1 — Maya Isometric Camera Setup (Priority: P1)

A Maya Python script sets up a standard isometric camera matching the Blender pipeline's camera angle, enabling consistent previews across tools.

**Why this priority**: Camera consistency is the minimum viable bridge between Blender and Maya workflows.

**Independent Test**: Run `setup_iso_camera.py` in mayapy, verify camera parameters match Blender's isometric setup.

**Acceptance Scenarios**:

1. **Given** an empty Maya scene, **When** `setup_iso_camera.py` runs, **Then** an orthographic camera is created at the standard isometric angle.

---

### User Story 2 — SVG Wall Import via Bridge (Priority: P2)

Import SVG wall data into Maya via one of: (a) Blender → USD → Maya, (b) custom SVG parser → Maya curves, (c) direct SVG to Maya (limited support).

**Why this priority**: Getting geometry into Maya is the core purpose of the bridge.

**Independent Test**: Provide a clean SVG, run the import script, verify walls appear in Maya scene.

**Acceptance Scenarios**:

1. **Given** a clean SVG with room walls, **When** `import_svg_walls.py` runs, **Then** wall geometry appears in the Maya scene.

---

### User Story 3 — Maya Batch Render (Priority: P3)

Render isometric previews from Maya using mayapy in headless batch mode.

**Acceptance Scenarios**:

1. **Given** a Maya scene with room geometry, **When** `batch_render.py` runs via mayapy, **Then** PNG previews are generated.

---

### Edge Cases

- What if Maya is not installed? (Feature must fail gracefully)
- What if USD interchange loses geometry data?

## Requirements

- **FR-001**: System MUST provide Maya Python scripts for isometric camera setup
- **FR-002**: System MUST support at least one SVG → Maya import path
- **FR-003**: System MUST support batch rendering via mayapy
- **FR-004**: Maya features MUST NOT block the Blender pipeline
- **FR-005**: All Maya scripts MUST work with mayapy (headless)

## Success Criteria

- **SC-001**: Maya camera matches Blender isometric camera parameters
- **SC-002**: At least one SVG import path produces usable geometry
- **SC-003**: Maya scripts fail gracefully when Maya is not installed

## Assumptions

- Maya is optional — not all artists will have it
- Blender pipeline is the primary path; Maya is the advanced branch
- USD may be used as interchange format between Blender and Maya
