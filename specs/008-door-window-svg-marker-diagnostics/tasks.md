# Tasks: Door/Window SVG Marker Diagnostics

**Input**: User request for Phase 008E marker preservation and diagnostics.

## Phase 1: Parser

- [X] T001 Extend explicit SVG label discovery for opening markers.
- [X] T002 Preserve deterministic behavior by ignoring unlabeled visual openings.
- [X] T003 Keep curved path bbox fallback limited to marker placement.

## Phase 2: Preflight

- [X] T004 Make preflight list actual door/window marker names from preserved metadata.
- [X] T005 Keep the zero-marker Vietnamese diagnostic when no marker is present.

## Phase 3: Maya Handoff

- [X] T006 Verify `build_maya_room.py` writes `opening_markers` to geometry JSON.
- [X] T007 Confirm existing Maya scene builder support remains compatible.

## Phase 4: Docs

- [X] T008 Update Vietnamese artist docs with the SVG export marker rule.
- [X] T009 Explain preflight is the source of truth for marker survival.

## Phase 5: Validation

- [X] T010 Add parser, preflight, and build-wrapper tests for 008E.
- [X] T011 Run required CLI help/version checks and pytest.
- [X] T012 Commit with message `fix: improve door window SVG marker detection`.
