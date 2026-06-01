# Tasks: Artist Desktop App MVP

**Input**: Design documents from `/specs/007-artist-desktop-app-mvp/`

## Phase 1: Desktop App Wrapper

- [X] T001 Add `scripts/python/artist_desktop_app.py`
- [X] T002 Keep command-building in pure helper functions
- [X] T003 Run `build_maya_room.py` instead of duplicating SVG/Maya logic
- [X] T004 Support SVG picker, room name, output dir, dry-run, render preview,
  render size, and `mayapy.exe` path
- [X] T005 Capture stdout/stderr into the app log area
- [X] T006 Keep the UI responsive while the subprocess runs

## Phase 2: Artist Launcher And Docs

- [X] T007 Add `launchers/09_artist_desktop_app.bat`
- [X] T008 Add Vietnamese desktop app MVP documentation
- [X] T009 Update README, artist guide, and launcher guide

## Phase 3: Tests And Validation

- [X] T010 Add tests for command-building helpers
- [X] T011 Add tests for actual-run validation without `mayapy.exe`
- [X] T012 Add tests for output folder helper paths
- [X] T013 Run full test suite and CLI help validation

## Phase 4: 007B Packaging Workflow

- [X] T014 Add `scripts/python/package_artist_app.py` for PyInstaller dry-run/build
- [X] T015 Add `launchers/10_package_artist_app.bat`
- [X] T016 Ignore generated package artifacts: `build/`, `dist/`, `.spec`, `.exe`
- [X] T017 Document source run, launcher run, and package workflow
- [X] T018 Add packaging helper tests that do not require PyInstaller or Maya

## Phase 5: 007B-R Packaged .exe Verification Checkpoint

- [X] T019 Document artist/DCC machine verification for packaged `.exe`
- [X] T020 Confirm generated package artifacts and Maya outputs remain uncommitted
- [X] T021 Record recommended next step as 007C desktop app UX/reliability polish

## Phase 6: 007C Desktop App UX/Reliability Polish

- [X] T022 Add default mayapy detection, repo-root display, and repo-relative path helpers
- [X] T023 Add pre-run validation for SVG, room name, output folder, repo root, build script, mayapy, and frozen Python
- [X] T024 Add status label, run-button lock/unlock, command preview/copy, log clearing, and safer output folder buttons
- [X] T025 Update pure helper tests without Tkinter, Maya, PyInstaller, external APIs, or generated output artifacts
- [X] T026 Update Vietnamese artist docs and quickstart for 007C behavior
