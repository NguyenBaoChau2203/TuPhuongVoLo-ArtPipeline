# Implementation Plan: Batch Isometric Render

**Branch**: `004-batch-isometric-render` | **Date**: 2026-05-29

## Summary

Extend the single-room Blender render (Feature 001) to process clean SVGs in batch mode. The MVP focuses on safe dry-run planning, JSON reporting, and error resilience without requiring Blender for unit tests.

## Technical Context

**Language/Version**: Python 3.11+ (orchestrator), Blender Python via Feature 001 (renderer)
**Primary Dependencies**: Feature 001 (build_isometric_room.py), PyYAML
**Target Platform**: Windows 10/11

## Project Structure

```text
scripts/
├── python/
│   └── batch_isometric_render.py   # Batch orchestrator and dry-run report
│
launchers/
├── 04_batch_isometric_render.bat   # Artist launcher, dry-run by default
├── 04_batch_render.bat             # Compatibility wrapper
```
