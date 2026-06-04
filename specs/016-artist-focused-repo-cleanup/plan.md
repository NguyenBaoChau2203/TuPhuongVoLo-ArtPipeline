# Implementation Plan: Artist-Focused Repo Cleanup

**Branch**: `codex/016-artist-focused-repo-cleanup` | **Date**: 2026-06-05 | **Spec**: `specs/016-artist-focused-repo-cleanup/spec.md`

**Input**: Feature specification from `specs/016-artist-focused-repo-cleanup/spec.md`

## Summary

Refocus the repository around one daily artist workflow: reference image and Vietnamese description -> Codex-generated Illustrator JSX draft -> artist edit/export SVG -> desktop app or CLI creates editable Maya `.ma` -> optional Visual Fidelity -> Maya sandbox -> Codex-generated Maya Python polish script -> artist review/rollback. Keep core production tools intact, move or hide optional/legacy surfaces from the daily path, and add practical Vietnamese docs plus reusable JSX/Maya templates.

## Technical Context

**Language/Version**: Markdown documentation, Illustrator JSX/ExtendScript templates, Python 3.11+ for existing CLI/Maya scripts

**Primary Dependencies**: Existing standard-library Python tools, Tkinter desktop app, Autodesk Maya `mayapy.exe` for actual scene generation, Illustrator for running JSX

**Storage**: Repository docs/templates plus existing `outputs/` for generated artifacts

**Testing**: `pytest` targeted suites; smoke CLI commands for SVG preflight and Maya dry-run

**Target Platform**: Windows 10/11 artist/DCC workstation

**Project Type**: Documentation and repository-structure cleanup for a Python/JSX/Maya toolkit

**Performance Goals**: Artist/operator can identify daily workflow and launcher in under two minutes; dry-run commands remain fast and do not require Maya

**Constraints**: No generated output commits, no source artwork edits, no direct Illustrator/Maya automation in this feature, no breaking existing core pipeline tests, no deletion of legacy code required by constitution

**Scale/Scope**: One repository cleanup pass, one daily workflow doc, one prompt doc, one JSX starter template, one Maya polish template, README and launcher docs updates, archive reference for optional/legacy surfaces

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Artist-First Automation**: Pass. Adds Vietnamese daily workflow and prompt docs for a non-programmer artist.
- **Non-Destructive Generation**: Pass. Cleanup touches repo docs/templates only and forbids source/output mutations.
- **Rebuildable Outputs**: Pass. Existing SVG -> Maya build remains source of truth.
- **SVG as Clean Source of Truth**: Pass. README preserves SVG preflight and dry-run gates.
- **Windows-First Setup**: Pass. Commands and docs use Windows paths and `.bat` launchers.
- **Script/API-First Automation**: Pass. JSX and Maya Python templates are script/API based.
- **Illustrator as 2D Authoring Tool**: Pass. JSX assists drafts; artist remains in Illustrator.
- **Maya as Primary Production DCC Backend**: Pass. Daily workflow centers on Maya `.ma`, Visual Fidelity, and sandbox polish.
- **Blender as Legacy/Fallback Draft Bridge**: Pass with constraint. Blender code remains available as legacy/fallback but is hidden from daily README flow.
- **Natural-Language Control is Future Layer**: Pass. Prompt assistance uses Codex-generated scripts, not direct MCP production automation.
- **Spec-Driven Development**: Pass. This plan follows Feature 016 spec/tasks.
- **Naming Convention & Manifest**: Pass. Existing build tools continue to handle versioned outputs and manifests.
- **Vietnamese Artist Documentation**: Pass. New artist-facing docs are Vietnamese.

## Project Structure

### Documentation (this feature)

```text
specs/016-artist-focused-repo-cleanup/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md
AGENTS.md
archive/
└── README.md
docs/
├── WORKFLOW_FOR_WIFE_VI.md
├── CODEX_PROMPTS_VI.md
├── artist_daily_workflow_vi.md
├── artist_handoff_desktop_app_vi.md
└── ...
launchers/
├── 00_maya_env_check.bat
├── 07_build_maya_room.bat
├── 09_artist_desktop_app.bat
└── README_LAUNCHERS_VI.md
scripts/
├── illustrator/
│   └── templates/
│       └── reference_to_layout_draft.jsx
└── maya/
    └── agent_polish_templates/
        └── agent_polish_additive_template.py
```

**Structure Decision**: Keep core code in place to avoid breaking tested behavior. Archive or de-emphasize optional/legacy documentation and launchers while adding new first-class workflow/prompt/template artifacts.

## Phase 0 Research Decisions

See `research.md`.

## Phase 1 Design

See `data-model.md` and `quickstart.md`. No external API contracts are required because this cleanup exposes no service API.

## Complexity Tracking

No constitution violations.
