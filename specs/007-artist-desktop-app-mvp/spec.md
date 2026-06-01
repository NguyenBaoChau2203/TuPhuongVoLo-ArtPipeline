# Feature Specification: Artist Desktop App MVP

**Feature Branch**: `workflow/maya-first-artist-pipeline`

**Created**: 2026-06-01

**Status**: MVP

## User Scenarios & Testing

### User Story 1 - Run Maya Room Pipeline From A Local App (Priority: P1)

The artist selects a clean SVG file, enters a room name, chooses dry-run or actual
run, optionally enables PNG preview rendering, and starts the verified Maya-first
pipeline without typing PowerShell commands.

**Why this priority**: The Maya-first CLI is verified, but the artist workflow
needs a friendlier local entry point than manual commands.

**Independent Test**: Build the app command from pure helper functions and verify
it calls `scripts/python/build_maya_room.py` with the expected arguments.

**Acceptance Scenarios**:

1. **Given** a selected SVG and room name, **When** dry-run is enabled, **Then**
   the app runs `build_maya_room.py` with `--dry-run` and does not require Maya.
2. **Given** preview rendering is enabled, **When** the command is built, **Then**
   it includes `--render-preview`, `--render-width`, and `--render-height`.
3. **Given** actual run is selected, **When** no `mayapy.exe` path is provided,
   **Then** the app refuses to run and shows a clear Vietnamese validation
   message.

### User Story 2 - Inspect Outputs Quickly (Priority: P2)

The artist opens `outputs/maya/`, `outputs/preview/`, `outputs/reports/`, or the
repository folder from buttons in the app.

**Acceptance Scenarios**:

1. **Given** an output root, **When** the app builds output folder paths, **Then**
   it resolves the intended subfolders without deleting or modifying source
   files.

## Requirements

- **FR-001**: The app MUST wrap the existing Maya-first CLI pipeline.
- **FR-002**: The app MUST NOT duplicate SVG parsing or Maya scene generation.
- **FR-003**: The app MUST show the exact command being run.
- **FR-004**: The app MUST capture stdout/stderr and display them in a log area.
- **FR-005**: Dry-run mode MUST NOT require Maya.
- **FR-006**: Actual run MUST require a `mayapy.exe` path.
- **FR-007**: Artist-facing UI messages MUST be Vietnamese.
- **FR-008**: Tests MUST avoid GUI display and Autodesk Maya requirements.

## Out Of Scope

- Feature 006 natural-language control.
- Phase 005.5 AI polish or external AI APIs.
- Rewriting SVG parser, geometry handoff, or Maya scene generation logic.
- Committing generated `.ma`, `.png`, report, build, dist, `.exe`, or temporary
  files.

## Success Criteria

- **SC-001**: Artist can run a single-room dry-run from the app.
- **SC-002**: Artist can run actual Maya execution when `mayapy.exe` is provided.
- **SC-003**: Artist can enable PNG preview rendering from the app.
- **SC-004**: Pure command-building and validation helpers are covered by tests.

