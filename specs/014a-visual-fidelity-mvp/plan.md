# Implementation Plan: Visual Fidelity MVP

**Branch**: `workflow/maya-first-artist-pipeline` | **Date**: 2026-06-04 | **Spec**: `specs/014a-visual-fidelity-mvp/spec.md`

**Input**: Feature specification from `specs/014a-visual-fidelity-mvp/spec.md`

## Summary

Feature 014A adds a reusable, safe, post-build Maya visual fidelity pass. The pass reads the existing blockout geometry JSON, plans warehouse-style additions in dry-run mode without Maya, and in actual mode calls `mayapy.exe` to open a source `.ma`, add only agent-owned helpers under `GRP_visual_fidelity_v0`, and save a different output `.ma`.

## Technical Context

**Language/Version**: Python 3.11+ for CLI and tests; Maya Python under Autodesk Maya/mayapy for actual apply

**Primary Dependencies**: Standard library only for the new CLI; Maya Python API only inside `scripts/maya/apply_visual_fidelity_pass.py`

**Storage**: JSON report files and external `.ma` output scenes

**Testing**: pytest tests that do not require Maya; actual mayapy validation is optional and environment-dependent

**Target Platform**: Windows 10/11 with optional Autodesk Maya 2024+

**Project Type**: Python CLI plus Maya Python apply script

**Constraints**: No Illustrator MCP, no commandPort editing, no source scene overwrite, no generated output committed

**Scale/Scope**: Warehouse room MVP covering crates, barrels, shelves, floor grate, electrical cabinet, camera/light/note helpers

## Constitution Check

- Artist-first: Vietnamese operator documentation added; CLI messages are short and safety-focused.
- Windows-first: paths use `pathlib`; examples use Windows paths.
- Script/API-first: actual mode uses `mayapy.exe` and Maya Python, not UI macros.
- Non-destructive: input `.ma` is never overwritten; actual output must be a different path.
- Rebuildable: visual additions are planned from geometry JSON and preset.
- Maya primary backend: integrates after the existing Maya bridge without changing it.

## Project Structure

### Documentation

```text
specs/014a-visual-fidelity-mvp/
├── spec.md
├── plan.md
├── tasks.md
└── quickstart.md
```

### Source Code

```text
scripts/python/
└── maya_visual_fidelity_pass.py

scripts/maya/
└── apply_visual_fidelity_pass.py

tests/
└── test_maya_visual_fidelity_pass.py

docs/
└── visual_fidelity_mvp_vi.md
```

**Structure Decision**: Add a standalone post-build tool instead of changing `build_maya_room.py`, so visual fidelity remains optional and safe.

## Implementation Notes

- `maya_visual_fidelity_pass.py` owns argument parsing, safety validation, dry-run reporting, and mayapy subprocess execution.
- `apply_visual_fidelity_pass.py` owns Maya-only geometry creation and save-as behavior.
- The stable group name is `GRP_visual_fidelity_v0`.
- The only preset in MVP is `warehouse_v0`.
