# Implementation Plan: Artist Desktop App MVP

**Branch**: `workflow/maya-first-artist-pipeline` | **Date**: 2026-06-01

## Summary

Add a small local Tkinter desktop app that wraps the verified Maya-first CLI
pipeline. The CLI remains the source of truth; the app only collects inputs,
builds the command, runs it, and displays logs.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Python standard library Tkinter, existing CLI scripts

**Target Platform**: Windows 10/11

**Testing Rule**: Unit tests must not create a Tkinter window, require a display,
require Maya, or require PyInstaller.

## Data Flow

```text
Tkinter app form
  -> pure command-building helper
  -> scripts/python/build_maya_room.py
  -> existing Python geometry JSON handoff
  -> existing mayapy Maya scene generation
  -> outputs/maya, outputs/preview, outputs/reports
```

## Project Structure

```text
scripts/python/
  artist_desktop_app.py

launchers/
  09_artist_desktop_app.bat

docs/
  desktop_app_mvp_vi.md
```

## Validation

- `python scripts/python/build_maya_room.py --help`
- `python scripts/python/batch_maya_room.py --help`
- `python scripts/python/artist_desktop_app.py --help`
- `pytest tests/ -v --ignore=tests/tmp`

