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

## Phase 7: 007C-R Desktop App UX/Reliability Verification Checkpoint

- [X] T027 Document 007C packaged `.exe` rebuild on artist/DCC machine
- [X] T028 Record dry-run exit code 0 verification
- [X] T029 Record actual Maya run exit code 0 verification
- [X] T030 Record verified Maya Outliner structure
- [X] T031 Confirm generated package and output artifacts remain uncommitted

## Phase 8: 007D Artist Handoff / Release Packaging Notes

- [X] T032 Add Vietnamese artist/developer handoff checklist document
- [X] T033 Document DCC repo update, retest, packaging, and safety checklist
- [X] T034 Link the handoff checklist from existing desktop app documentation

## Phase 9: 007E Small Packaging Polish

- [X] T035 Add desktop app version metadata and display it in title/UI
- [X] T036 Add `--version` support for the desktop app CLI
- [X] T037 Print app version metadata from packaging dry-run/version output
- [X] T038 Add Vietnamese release packaging checklist
- [X] T039 Update focused desktop app docs, launcher docs, quickstart, and tests

## Phase 10: 007E-R Packaging Metadata Verification Checkpoint

- [X] T040 Verify `63c59bb` is present with a clean worktree before checkpoint work
- [X] T041 Record app version, dry-run packaging output, and full pytest result
- [X] T042 Confirm packaging remains local/dev-only and generated artifacts stay uncommitted
- [X] T043 Confirm Feature 006 remains deferred after 007E-R

## Phase 11: 007G Desktop App AI Polish Preview Integration

- [X] T044 Bump desktop app metadata to `v0.7.6 (007G)`
- [X] T045 Add pure AI preview options, validation, output-folder, and command-building helpers
- [X] T046 Add desktop AI preview controls for PNG input, provider, model, prompt preset, optional prompt, skip-on-missing-config, and AI dry-run
- [X] T047 Run `scripts/python/ai_polish_preview.py` through subprocess without importing `fal-client` in the desktop app
- [X] T048 Keep Maya pipeline controls independent from AI preview controls
- [X] T049 Add tests for AI command building, prompt handling, PNG validation, output folder helpers, and version metadata
- [X] T050 Update Vietnamese docs, quickstart, launcher guide, README, and safety notes for optional AI preview
- [X] T051 Confirm Feature 006, source SVG, Maya generation, render logic, manifest, dependencies, secrets, and generated outputs remain unchanged by 007G

## Phase 12: 007G-R AI Preview Verification Checkpoint

- [X] T052 Re-run desktop app, AI CLI, compileall, and full pytest validation from commit `fc036c0`
- [X] T053 Add Vietnamese verification checkpoint document for 007G-R
- [X] T054 Link checkpoint from relevant desktop app and AI preview docs
- [X] T055 Confirm fal-client remains optional, no external API calls were made, and generated `outputs/ai_preview/` artifacts remain uncommitted

## Phase 13: 007H Artist Workflow Cat Guide

- [X] T056 Create `docs/artist_workflow_cat_guide_vi.html` — single self-contained static HTML, inline CSS, no CDN or external deps
- [X] T057 Link cat guide from README.md Artist Quickstart section and Feature Status table
- [X] T058 Link cat guide from `docs/desktop_app_mvp_vi.md` Phase 007G update section
- [X] T059 Link cat guide from `docs/artist_handoff_desktop_app_vi.md` section 12 related docs
- [X] T060 Link cat guide from `launchers/README_LAUNCHERS_VI.md`
- [X] T061 Confirm no Python logic, SVG/Maya/render/AI provider logic, Feature 006, secrets, external assets, CDN, or generated outputs added

