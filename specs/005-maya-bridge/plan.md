# Implementation Plan: Maya Bridge

**Branch**: `005-maya-bridge` | **Date**: 2026-05-29

## Summary

Optional advanced branch providing Maya-based isometric rendering as an alternative to the Blender pipeline. Uses mayapy for headless execution and supports SVG import via Blender/USD bridge or custom parser.

## Technical Context

**Language/Version**: Python 3.10+ (glue), Maya Python / MEL (Maya scripting)
**Primary Dependencies**: mayapy, Maya Python API, optionally USD/Alembic
**Target Platform**: Windows 10/11 + Autodesk Maya 2024+
**Project Type**: Optional branch scripts

## Project Structure

```text
scripts/maya/
├── setup_iso_camera.py      # Isometric camera setup
├── import_svg_walls.py      # SVG → Maya geometry import
└── batch_render.py          # Headless batch render
```
