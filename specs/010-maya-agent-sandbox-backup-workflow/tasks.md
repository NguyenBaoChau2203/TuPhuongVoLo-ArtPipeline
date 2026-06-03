# Tasks: Maya Agent Sandbox Backup Workflow

**Input**: User request for Phase 010A Maya agent backup/sandbox preparation.

## Phase 1: Spec Traceability

- [X] T001 Create 010A spec, plan, tasks, and quickstart artifacts.

## Phase 2: CLI Utility

- [X] T002 Add `scripts/python/maya_agent_sandbox.py` parser and validation.
- [X] T003 Implement safe default backup root and timestamped session naming.
- [X] T004 Implement dry-run planning without filesystem mutation.
- [X] T005 Implement copy behavior for scene, optional geometry JSON, and optional SVG.
- [X] T006 Implement overwrite refusal and `--force` replacement behavior.
- [X] T007 Write `agent_session.json`, `agent_notes.md`, and `restore_agent_backup.ps1`.

## Phase 3: Tests

- [X] T008 Add focused pytest coverage for help, dry-run, copies, reports, force, missing inputs, and no-Maya behavior.

## Phase 4: Documentation

- [X] T009 Add Vietnamese Maya agent backup workflow documentation.

## Phase 5: Validation

- [X] T010 Run requested CLI help and pytest validation.
- [X] T011 Inspect git status and diff stat.
- [X] T012 Commit with message `chore: add Maya agent sandbox backup workflow`.
