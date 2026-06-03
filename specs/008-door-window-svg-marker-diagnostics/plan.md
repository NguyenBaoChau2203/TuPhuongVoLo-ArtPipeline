# Implementation Plan: Door/Window SVG Marker Diagnostics

**Branch**: `workflow/maya-first-artist-pipeline` | **Date**: 2026-06-03

## Summary

Improve explicit SVG label discovery for door/window marker groups while keeping
opening generation deterministic and artist-friendly. The parser remains the
source of truth for geometry; preflight mirrors the same naming sources for
diagnostics.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing Python standard library and project modules

**Target Platform**: Windows 10/11

## Data Flow

```text
Illustrator SVG export
  -> svg_preflight_check.py marker-name diagnostics
  -> detect_rooms_from_svg.py explicit marker extraction
  -> build_maya_room.py geometry JSON opening_markers
  -> existing Maya scene builder openings group
```

## Validation

- `python scripts/python/svg_preflight_check.py --help`
- `python scripts/python/build_maya_room.py --help`
- `python scripts/python/artist_desktop_app.py --version`
- `pytest tests/ -v --ignore=tests/tmp`
