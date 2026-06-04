# Tasks: Artist Prompt Control Loop MVP

**Input**: Design documents from `specs/015-artist-prompt-control-loop/`

**Prerequisites**: `spec.md`, `plan.md`

**Tests**: Documentation validation required; full pytest if feasible.

## Phase 1: Repo Audit

- [X] T001 Confirm initial git status, branch, and recent commits from `D:\TuPhuongVoLo_DCC_Test\TuPhuongVoLo-ArtPipeline`.
- [X] T002 Verify branch is `workflow/maya-first-artist-pipeline`, worktree is clean, and commit `4e7079c` is visible.
- [X] T003 Inspect current SDD structure and Feature 014A plan/spec/tasks/quickstart.

## Phase 2: Context Review

- [X] T004 Inspect `README.md` for current feature status and artist quickstart links.
- [X] T005 Inspect `docs/artist_handoff_desktop_app_vi.md`, `docs/visual_fidelity_mvp_vi.md`, `docs/maya_mcp_sandbox_workflow_closeout_vi.md`, `docs/illustrator_mcp_edit_export_workflow_vi.md`, and `docs/illustrator_agent_backup_workflow_vi.md`.
- [X] T006 Inspect relevant script boundaries in `scripts/python/artist_desktop_app.py`, `scripts/python/build_maya_room.py`, `scripts/python/maya_visual_fidelity_pass.py`, `scripts/python/maya_agent_sandbox.py`, and `scripts/python/illustrator_agent_sandbox.py`.

## Phase 3: SDD Artifacts

- [X] T007 [P] Create `specs/015-artist-prompt-control-loop/spec.md` with prompt-control product reset, two prompt loops, requirements, and success criteria.
- [X] T008 [P] Create `specs/015-artist-prompt-control-loop/plan.md` with docs-only implementation plan, stable/beta workflow status, safety constraints, and model routing.
- [X] T009 [P] Create `specs/015-artist-prompt-control-loop/tasks.md` with dependency-ordered 015A tasks.
- [X] T010 [P] Create `specs/015-artist-prompt-control-loop/quickstart.md` with validation and next-phase handoff.

## Phase 4: Artist Docs and Prompt Templates

- [X] T011 [P] Create `docs/artist_prompt_control_loop_vi.md` documenting the product goal, Illustrator loop, Maya loop, model routing, and safety checklist.
- [X] T012 [P] Create `docs/templates/maya_artist_prompt_template_vi.md` with required copyable placeholders and scene path guard.
- [X] T013 [P] Create `docs/templates/illustrator_artist_prompt_template_vi.md` with required copyable placeholders and active document guard.
- [X] T014 [P] Create `docs/artist_daily_workflow_vi.md` answering tomorrow's operator handoff questions.

## Phase 5: Minimal References

- [X] T015 Update `README.md` minimally with Feature 015A status and artist doc links.
- [X] T016 Update `docs/artist_handoff_desktop_app_vi.md` minimally with links to Visual Fidelity, Daily Workflow, and Artist Prompt Control Loop.

## Phase 6: Validation and Commit

- [X] T017 Run targeted documentation tests, including `tests/test_antigravity_maya_mcp_docs.py`.
- [X] T018 Record that full `python -m pytest tests/ -v` is not feasible on this machine because `python` is missing, `.venv` points to a removed Python 3.11 install, and the bundled Python 3.12 lacks pytest.
- [X] T019 Inspect `git status`, changed files, and staged content to ensure no generated outputs or external files are included.
- [X] T020 Commit with message `docs: add artist prompt control loop SDD`.

## Dependencies & Execution Order

- T001-T003 must complete before documentation edits.
- T004-T006 inform all new docs and templates.
- T007-T010 can be written in parallel once context is known.
- T011-T014 can be written in parallel after the SDD direction is clear.
- T015-T016 follow after new doc paths exist.
- T017-T020 complete validation and commit.

## MVP Scope

The MVP for 015A is documentation-only: future models and the artist/operator can understand the prompt-control product direction and safely run the existing manual-export-to-Maya-sandbox workflow. New orchestration code, Illustrator MCP repair, and Maya prompt-edit smoke execution are explicitly deferred.
