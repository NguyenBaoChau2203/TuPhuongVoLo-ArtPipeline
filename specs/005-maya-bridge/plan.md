# Implementation Plan: Maya Bridge

**Branch**: `005-maya-bridge` | **Date**: 2026-05-29

## Summary

Maya is the primary production DCC backend for Feature 005. The bridge reuses the existing Python SVG detection and room geometry layer, writes a JSON handoff, then runs a Maya Python script via `mayapy` to produce an editable `.ma` blockout scene.

Blender remains in the repository as the previous MVP/fallback backend and is not required for this feature.

## Technical Context

**Language/Version**: Python 3.11+ external tooling, Maya Python inside Autodesk Maya/mayapy

**Primary Dependencies**: Standard library, PyYAML, existing SVG/manifest modules, Maya Python API when available

**Target Platform**: Windows 10/11 + optional Autodesk Maya 2024+

**Testing Rule**: Unit tests must not require Maya. Actual Maya execution is optional and environment-dependent.

## Data Flow

```text
Illustrator clean SVG
  -> detect_rooms_from_svg.py
  -> room_geometry.py
  -> outputs/tmp/*.json
  -> scripts/maya/build_maya_room_scene.py
  -> outputs/maya/*.ma
  -> manifest append after verified success
```

## Project Structure

```text
scripts/python/
├── build_maya_room.py
└── batch_maya_room.py

scripts/maya/
└── build_maya_room_scene.py

launchers/
├── 07_build_maya_room.bat
└── 08_batch_maya_room.bat
```

## Validation

- Existing Feature 001/002/003/004 tests must continue to pass.
- New Maya dry-run and batch tests run with normal `pytest`.
- CLI help and dry-run commands must work without Maya installed.
