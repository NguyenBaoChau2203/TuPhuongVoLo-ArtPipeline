# Feature Specification: Maya Agent Sandbox Backup Workflow

**Branch**: `workflow/maya-first-artist-pipeline`  
**Date**: 2026-06-03  
**Phase**: 010A

## Summary

Prepare a safe local backup/sandbox workflow before experimenting with
Antigravity or MCP full-control over Maya. The workflow copies a generated Maya
scene and optional handoff/source snapshots into a timestamped sandbox session.
Agents may work only on the sandbox working copy.

## User Need

The artist-developer wants to experiment with full-control AI agents in Maya
without risking original Illustrator files, source SVGs, geometry JSON handoff
files, or generated production scenes.

## Requirements

- Provide `scripts/python/maya_agent_sandbox.py`.
- Accept generated `.ma`, optional geometry JSON, optional source SVG, backup
  root, room, session label, dry-run, and force flags.
- Default backup root must be outside generated output folders.
- Create `original/`, `working/`, and `reports/` folders in a timestamped
  session directory.
- Copy the Maya scene to both `original/scene_before_agent.ma` and
  `working/scene_agent_work.ma`.
- Copy optional geometry JSON and source SVG snapshots into `original/`.
- Write JSON and Markdown reports for the session.
- Write a PowerShell restore script that restores the original scene to a
  user-specified target path.
- Refuse to overwrite an existing session folder unless `--force` is passed.
- Support `--dry-run` without creating folders or copying files.
- Require no Maya installation, no MCP server, no AI API, and no web UI.

## Non-Goals

- Do not implement Feature 006 natural-language agent control.
- Do not install, vendor, or configure MayaMCP.
- Do not connect to Antigravity.
- Do not mutate artist source files or generated source outputs.

## Success Criteria

- `python scripts/python/maya_agent_sandbox.py --help` works.
- `pytest tests/test_maya_agent_sandbox.py -v` passes.
- `pytest tests/ -v --ignore=tests/tmp` passes without Maya installed.
- Vietnamese documentation explains the backup rule and safe workflow.
