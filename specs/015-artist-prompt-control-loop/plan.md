# Implementation Plan: Artist Prompt Control Loop MVP

**Branch**: `workflow/maya-first-artist-pipeline` | **Date**: 2026-06-04 | **Spec**: `specs/015-artist-prompt-control-loop/spec.md`

**Input**: Feature specification from `specs/015-artist-prompt-control-loop/spec.md`

## Summary

Feature 015A is a documentation and SDD reset for the true product goal: a prompt-driven Illustrator + Maya art assistant for a Vietnamese-speaking artist. It does not implement a new app or run DCC edits. It creates the source-of-truth prompt-control spec, plan, tasks, quickstart, Vietnamese workflow docs, and prompt templates that future models should follow.

The stable path for tomorrow is manual SVG export, app/CLI preflight/dry-run/Maya build, optional Visual Fidelity pass, Maya sandbox creation, Codex prompt polish in the sandbox, artist review, and rollback. The Illustrator prompt loop is documented as beta/blocked until the Antigravity Illustrator MCP EOF issue is repaired and smoke-tested.

## Technical Context

**Language/Version**: Markdown documentation only; no runtime code changes planned.

**Primary Dependencies**: Existing repo docs and SDD structure.

**Storage**: New docs under `docs/`, prompt templates under `docs/templates/`, and SDD artifacts under `specs/015-artist-prompt-control-loop/`.

**Testing**: Existing pytest suite, with targeted documentation tests first.

**Target Platform**: Windows 10/11 artist/DCC machine; documentation uses Windows paths and PowerShell examples.

**Project Type**: Documentation and workflow architecture phase.

**Constraints**: No Illustrator MCP, no Maya commandPort, no Illustrator/Maya launch, no external sandbox mutation, no generated output commits, no push.

**Scale/Scope**: Prompt-loop MVP documentation for one current real scene (`phong_kho` Visual Fidelity sandbox) and future repeatable prompt sessions.

## Constitution Check

- Artist-first: all operator-facing docs are Vietnamese and prompt templates are copyable.
- Windows-first: paths and commands use Windows conventions.
- Script/API-first: the documented stable build path keeps using app/CLI scripts; no UI macro automation is introduced.
- Non-destructive: docs require sandbox working files, no overwrite, agent groups, hash checks where appropriate, and rollback.
- Manifest/versioning: Feature 015A does not generate pipeline outputs; existing build tools remain source of manifest updates.
- Maya primary backend: Maya prompt loop is the near-term MVP-ready loop after Visual Fidelity and sandbox creation.
- SDD workflow: `spec.md`, `plan.md`, `tasks.md`, and `quickstart.md` are created before future implementation.

## Project Structure

### Documentation

```text
specs/015-artist-prompt-control-loop/
├── spec.md
├── plan.md
├── tasks.md
└── quickstart.md

docs/
├── artist_prompt_control_loop_vi.md
├── artist_daily_workflow_vi.md
└── templates/
    ├── maya_artist_prompt_template_vi.md
    └── illustrator_artist_prompt_template_vi.md
```

### Existing References

```text
README.md
docs/artist_handoff_desktop_app_vi.md
docs/visual_fidelity_mvp_vi.md
docs/maya_mcp_sandbox_workflow_closeout_vi.md
docs/illustrator_mcp_edit_export_workflow_vi.md
docs/illustrator_agent_backup_workflow_vi.md
scripts/python/artist_desktop_app.py
scripts/python/build_maya_room.py
scripts/python/maya_visual_fidelity_pass.py
scripts/python/maya_agent_sandbox.py
scripts/python/illustrator_agent_sandbox.py
```

**Structure Decision**: Add a new 015A SDD folder and new docs rather than changing desktop app behavior or DCC automation. README and desktop handoff receive only link/status updates.

## Feature Status

### Stable for Tomorrow

```text
Illustrator manual SVG export
-> desktop app or CLI preflight
-> dry-run
-> actual Maya build
-> Visual Fidelity pass when desired
-> Maya agent sandbox
-> Codex prompt polish with scene path guard
-> artist review and rollback
```

### Beta After Illustrator MCP Repair

```text
Artist prompt
-> Antigravity controls Illustrator sandbox only
-> active document path guard
-> safe inspect/edit/export
-> SVG in sandbox export folder if explicitly allowed
-> same Maya pipeline
```

Blocked until the `illustrator-sandbox` MCP server no longer returns EOF on inspect/help/system-prompt smoke calls.

## Model Routing

- Codex GPT-5.5 medium: inspect, verification, documentation checks, path/hash review.
- Codex GPT-5.5 high: guarded Maya polish/write tasks after sandbox and scene path are verified.
- Codex GPT-5.5 xhigh: SDD, refactor planning, safety audits, cross-doc consistency reviews.
- Antigravity Claude Sonnet 4.6: Illustrator MCP write/export tasks only after MCP smoke test passes.
- Antigravity Claude Opus 4.6: Illustrator MCP architecture or safety audit.
- Gemini models: optional light inspect/report only.

## Implementation Notes

- Do not add code or app orchestration in 015A.
- Do not touch `D:\TuPhuongVoLo_AgentBackups` or `D:\TuPhuongVoLo_IllustratorAgentBackups`.
- Do not open Illustrator or Maya.
- Do not use MCP or commandPort.
- The next implementation phase should be 015B: Maya Prompt Polish Loop smoke test using the 014C Visual Fidelity sandbox.
