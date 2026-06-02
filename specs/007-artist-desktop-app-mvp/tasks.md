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

## Phase 007I: Artist App Guide and Template UX Polish

- [X] T062 Add app buttons to open guide/template/template folder
- [X] T063 Improve grouping/layout clarity
- [X] T064 Keep AI preview optional
- [X] T065 Add/update tests
- [X] T066 Confirm no pipeline logic or AI provider behavior changes

## Phase 007J: Cat-themed Artist App Visual Polish

- [X] Add cat-themed header and pastel UI styling (`configure_artist_theme`, `ttk.Style` only)
- [X] Improve section titles and helper text (🐾/🏠/📖/✨/📋 emoji labels, `Hint.TLabel` hints)
- [X] Keep guide/template shortcut buttons visible with accent styling
- [X] Keep AI preview optional/reference-only (hint label added)
- [X] Update tests and docs (version `0.7.8 (007J)`, theme/style constant tests)
- [X] Confirm no pipeline logic, AI provider behavior, local web UI, Feature 006, external APIs,
      secrets, new dependencies, binary assets, or generated outputs were added

## Phase 007J-F1: Cat UI Contrast Fix and Detailed App Guide

- [X] Improve button contrast for primary/accent/secondary/utility buttons
  - Added `STYLE_UTILITY_BUTTON` (Utility.TButton) and `STYLE_GUIDE_BUTTON` (Guide.TButton) style constants
  - Primary (terracotta/orange, raised, bold): "Chạy pipeline", "Tạo AI polish preview"
  - Guide (dusty rose, raised, bold): "Mở hướng dẫn", "Mở SVG mẫu marker"
  - Utility (warm peach, raised): all file-picker and folder-open buttons
  - All style names include `style.map(...)` for active/pressed/disabled states
- [X] Add detailed HTML guide section in `docs/artist_workflow_cat_guide_vi.html`
  explaining each app step, field, button, checkbox, and output folder
- [X] New HTML section covers: Step 1–4, Log/status panel, recommended workflow checklist,
  and common mistakes — all in Vietnamese, inline CSS, no CDN
- [X] Keep AI preview optional/reference-only across UI and HTML guide
- [X] Update `tests/test_artist_desktop_app.py`: version 0.7.9 (007J-F1),
  STYLE_UTILITY_BUTTON and STYLE_GUIDE_BUTTON constant tests
- [X] Bump version to `APP_VERSION = "0.7.9"`, `APP_PHASE = "007J-F1"`
- [X] Update `specs/007-artist-desktop-app-mvp/tasks.md` with new phase
- [X] Confirm no Maya generation logic, SVG parser logic, AI provider behavior,
  local web UI, Feature 006, external APIs, secrets, new dependencies,
  binary assets, or generated outputs were added

## Phase 007J-F2: De-emphasize Paid AI Preview in Artist Docs

- [X] T067 Clarify AI preview is optional/reference-only in docs and HTML guide
- [X] T068 Clarify paid AI APIs are deferred due to cost
- [X] T069 Clarify normal workflow does not require API keys or fal-client
- [X] T070 Align current app version references to v0.7.9 (007J-F1) in docs
- [X] T071 Keep local web UI out of near-term roadmap (confirm it's dropped)
- [X] T072 Confirm docs-only scope (no Python code changes)

## Phase 007L: One-click Guided Artist Workflow

- [X] T073 Integrate `scripts/python/svg_preflight_check.py` into the desktop app as a subprocess step
- [X] T074 Add `Kiểm tra SVG`, `Chạy dry-run`, and `Chạy Maya thật` guided buttons
- [X] T075 Track dry-run success for the current SVG, room, output, and render settings
- [X] T076 Block actual Maya run when the current settings do not have a matching successful dry-run
- [X] T077 Keep manual/advanced controls and existing CLI behavior intact
- [X] T078 Bump desktop app metadata to `v0.7.10 (007L)`
- [X] T079 Update focused tests and Vietnamese workflow docs
- [X] T080 Confirm no Maya scene generation logic, SVG parser logic, local web UI, Feature 006, external APIs, secrets, or new dependencies were added
