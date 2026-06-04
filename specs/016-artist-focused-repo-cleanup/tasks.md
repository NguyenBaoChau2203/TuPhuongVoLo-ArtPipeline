# Tasks: Artist-Focused Repo Cleanup

**Input**: Design documents from `specs/016-artist-focused-repo-cleanup/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Targeted pytest and smoke commands are required because this cleanup changes repo entry points and must preserve the core pipeline.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish SDD and branch context for cleanup.

- [x] T001 Create/switch to branch `codex/016-artist-focused-repo-cleanup`.
- [x] T002 [P] Create `specs/016-artist-focused-repo-cleanup/spec.md`.
- [x] T003 [P] Create `specs/016-artist-focused-repo-cleanup/plan.md`.
- [x] T004 [P] Create `specs/016-artist-focused-repo-cleanup/tasks.md`.
- [x] T005 [P] Create `specs/016-artist-focused-repo-cleanup/quickstart.md`, `research.md`, `data-model.md`, and `checklists/requirements.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Inventory existing daily, optional, and legacy surfaces before moving or rewriting.

- [x] T006 Inspect `README.md`, `docs/`, `launchers/`, `scripts/`, and `tests/` for daily versus optional surfaces.
- [x] T007 Update `AGENTS.md` Spec Kit marker to point at `specs/016-artist-focused-repo-cleanup/plan.md`.
- [x] T008 Create `archive/README.md` documenting what is archived/legacy versus retained fallback.

---

## Phase 3: User Story 1 - Daily Artist Workflow Is Obvious (Priority: P1)

**Goal**: Make the repo entry point clearly explain the one daily workflow.

**Independent Test**: Open README and the wife-facing workflow doc; verify the daily path, app entry point, CLI fallback, output folders, and next Maya review step are obvious.

- [x] T009 [US1] Rewrite `README.md` around the single daily workflow and core commands.
- [x] T010 [US1] Create `docs/WORKFLOW_FOR_WIFE_VI.md` as the Vietnamese daily guide.
- [x] T011 [US1] Update `docs/artist_daily_workflow_vi.md` to route to the new daily guide and remove hard-coded old sandbox paths.
- [x] T012 [US1] Update `docs/artist_handoff_desktop_app_vi.md` to reference `master` and the new daily workflow.
- [x] T013 [US1] Update `launchers/README_LAUNCHERS_VI.md` so the daily launcher list is only environment check, one-room Maya build, and artist desktop app.

---

## Phase 4: User Story 2 - Prompt Templates Reduce Blank-Page Work (Priority: P1)

**Goal**: Add copyable prompt docs and starter templates for Codex-generated Illustrator and Maya assistance.

**Independent Test**: Open the prompt doc and templates; verify placeholders, naming conventions, and sandbox/group safety are present.

- [x] T014 [US2] Create `docs/CODEX_PROMPTS_VI.md` with reference-image-to-JSX and Maya-polish prompt templates.
- [x] T015 [US2] Create `scripts/illustrator/templates/reference_to_layout_draft.jsx`.
- [x] T016 [US2] Create `scripts/maya/agent_polish_templates/agent_polish_additive_template.py`.

---

## Phase 5: User Story 3 - Legacy Work Is Preserved But Out Of The Way (Priority: P2)

**Goal**: Remove optional/legacy clutter from daily surfaces without breaking retained fallback code.

**Independent Test**: README no longer links old AI preview/research/Blender/batch paths as the main workflow; archive index records where to find them.

- [x] T017 [US3] Move safe optional docs such as AI preview docs, research docs, old verification docs, and roadmap docs under `archive/`.
- [x] T018 [US3] Move non-daily `.bat` launchers under `archive/launchers/` where they are not needed by the daily workflow.
- [x] T019 [US3] Keep tested legacy code in place but document it as retained fallback in `archive/README.md`.
- [x] T020 [US3] Search for and fix stale daily references to `workflow/maya-first-artist-pipeline`.

---

## Phase 6: User Story 4 - Verification Stays Trustworthy (Priority: P2)

**Goal**: Prove core workflow still works after cleanup.

**Independent Test**: Run quickstart smoke commands and targeted tests.

- [x] T021 [US4] Run SVG preflight smoke command from `quickstart.md`.
- [x] T022 [US4] Run Maya build dry-run smoke command from `quickstart.md`.
- [x] T023 [US4] Run targeted pytest command from `quickstart.md`.
- [x] T024 [US4] Run full pytest with `--ignore=tests/tmp` if time allows.
- [x] T025 [US4] Inspect `git status --short` for generated or unintended files.

---

## Phase 7: User Story 5 - Post-Build Maya Actions Are One Click (Priority: P1)

**Goal**: After a Maya `.ma` exists, the artist can run the next workflow actions from the desktop app or a launcher without terminal commands.

**Independent Test**: Open the desktop app helper tests; verify command builders and validation exist for Visual Fidelity and Maya sandbox. Inspect launchers; verify a sandbox launcher exists and docs list it.

- [x] T026 [US5] Add desktop app helpers for Visual Fidelity command construction, validation, and latest-output discovery.
- [x] T027 [US5] Add desktop app controls for `Tạo Visual Fidelity`, `Tạo Maya Sandbox`, and `Mở working/scene_agent_work.ma`.
- [x] T028 [US5] Add `launchers/08_create_maya_sandbox.bat` for artist-facing sandbox creation.
- [x] T029 [US5] Update Vietnamese HTML/launcher docs to mention the new buttons and launcher.
- [x] T030 [US5] Add or update targeted tests and run desktop app, Visual Fidelity, and Maya sandbox test slices.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: complete before implementation.
- **Foundational (Phase 2)**: complete before daily docs/archive edits.
- **US1 and US2**: can proceed after foundation and are both MVP-critical.
- **US3**: after README/prompt docs identify what is daily versus optional.
- **US4**: after all edits.

### User Story Dependencies

- **US1 (P1)**: no dependency after foundation.
- **US2 (P1)**: no dependency after foundation.
- **US3 (P2)**: depends on US1/US2 decisions so archive does not hide needed daily files.
- **US4 (P2)**: depends on all implemented changes.

## Parallel Opportunities

- T009/T010 can be drafted together but final wording should be consistent.
- T014/T015/T016 touch separate files and can be edited independently.
- T017/T018 are separate archive move operations.

## Implementation Strategy

### MVP First

1. Complete spec/plan/tasks.
2. Rewrite README and add `WORKFLOW_FOR_WIFE_VI.md`.
3. Add prompt doc and templates.
4. Verify smoke commands.

### Full Cleanup

1. Complete MVP.
2. Move safe optional docs/launchers into `archive/`.
3. Update references and run targeted/full tests.
