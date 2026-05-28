# Implementation Plan: Floorplan to Isometric Room

**Branch**: `001-floorplan-to-isometric-room` | **Date**: 2026-05-29 | **Spec**: `specs/001-floorplan-to-isometric-room/spec.md`

**Input**: Feature specification from `/specs/001-floorplan-to-isometric-room/spec.md`

## Summary

Convert a clean SVG floorplan into an isometric 3D room draft using Blender Python. The system parses SVG room boundaries, creates extruded walls on a floor plane, places preset props, configures an orthographic isometric camera, and renders a PNG preview. The artist controls the process via `.bat` launchers.

## Technical Context

**Language/Version**: Python 3.10+ (CLI glue), Blender Python (bpy) for 3D

**Primary Dependencies**: svgpathtools (SVG parsing), bpy (Blender Python API), PyYAML (config), click (CLI)

**Storage**: File-based — SVG input, .blend + PNG output, JSON manifest

**Testing**: pytest for Python CLI, manual Blender scene verification

**Target Platform**: Windows 10/11

**Project Type**: CLI tool + Blender script

**Performance Goals**: Single room render in <60 seconds

**Constraints**: Must work with Blender 4.x headless mode, Windows paths

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Artist-First | ✅ Pass | .bat launcher, Vietnamese error messages |
| Non-Destructive | ✅ Pass | Outputs to outputs/ only |
| Rebuildable | ✅ Pass | Same SVG + config = same output |
| SVG Source of Truth | ✅ Pass | Consumes clean SVG |
| Windows-First | ✅ Pass | pathlib, .bat launchers |
| Script/API-First | ✅ Pass | Blender Python, Python CLI |
| Naming Convention | ✅ Pass | Uses config/naming_convention.yaml |
| Manifest | ✅ Pass | Updates manifest on every run |

## Project Structure

### Documentation (this feature)

```text
specs/001-floorplan-to-isometric-room/
├── spec.md              # Feature specification
├── plan.md              # This file
├── tasks.md             # Task checklist
├── research.md          # SVG-to-3D research notes
├── data-model.md        # Data model for rooms, presets
├── contracts.md         # Input/output contracts
└── quickstart.md        # Verification guide
```

### Source Code (repository root)

```text
scripts/
├── python/
│   ├── detect_rooms_from_svg.py     # SVG → room boundary extraction
│   └── validate_svg_contract.py     # SVG validation
│
├── blender/
│   ├── build_isometric_room.py      # Main Blender scene builder
│   ├── batch_render_rooms.py        # Batch variant (Feature 004)
│   └── props_library.py             # Prop placement utilities
│
config/
├── room_presets.yaml                # Room type → prop definitions
├── style_presets.yaml               # Visual style definitions
├── naming_convention.yaml           # Output naming rules
└── pipeline.yaml                    # Global config

launchers/
├── 03_build_isometric_room.bat      # Artist launcher
```

**Structure Decision**: Single-project structure with scripts organized by tool (python/blender/maya). No monorepo or web app patterns needed.

## Complexity Tracking

No constitution violations — this is a straightforward SVG-to-3D pipeline step.
