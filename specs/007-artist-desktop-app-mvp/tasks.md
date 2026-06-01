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
