# Implementation Plan: Maya Agent Sandbox Backup Workflow

**Branch**: `workflow/maya-first-artist-pipeline` | **Date**: 2026-06-03

## Summary

Add a local-only Python CLI that prepares timestamped Maya agent sandbox
sessions. The utility copies generated scene inputs into immutable snapshots and
a separate editable working copy, then writes reports and a PowerShell restore
helper.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Python standard library only

**Target Platform**: Windows 10/11, with platform-safe fallback paths

## Data Flow

```text
generated .ma scene
  + optional geometry JSON
  + optional source SVG snapshot
  -> maya_agent_sandbox.py
  -> timestamped backup session
  -> Antigravity/MCP opens only working/scene_agent_work.ma
```

## Safety Design

- The backup root defaults outside `outputs/`.
- The source `.ma`, optional `.json`, and optional `.svg` are read only.
- Existing session folders are protected unless `--force` is explicit.
- `--dry-run` reports planned paths without writing anything.
- The restore script copies the snapshot to a user-specified target only.

## Validation

- `python scripts/python/maya_agent_sandbox.py --help`
- `pytest tests/test_maya_agent_sandbox.py -v`
- `pytest tests/ -v --ignore=tests/tmp`
- `git status`
- `git diff --stat`
