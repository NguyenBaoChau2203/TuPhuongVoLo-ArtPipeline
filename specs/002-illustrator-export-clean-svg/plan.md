# Implementation Plan: Illustrator Export & Clean SVG

**Branch**: `002-illustrator-export-clean-svg` | **Date**: 2026-05-29 | **Spec**: `specs/002-illustrator-export-clean-svg/spec.md`

## Summary

Create Illustrator JSX scripts for organized layer export and a Python pipeline for SVG cleanup and validation. This is the entry point for all downstream pipeline features.

## Technical Context

**Language/Version**: ExtendScript/JSX (Illustrator), Python 3.10+ (cleanup/validation)

**Primary Dependencies**: vpype (SVG simplification), svgpathtools (path parsing), lxml (XML manipulation)

**Target Platform**: Windows 10/11 + Adobe Illustrator CC

## Constitution Check

All principles satisfied — JSX is script-first, outputs to designated folders, non-destructive.

## Project Structure

```text
scripts/
├── illustrator/
│   ├── export_clean_svg.jsx         # Main export script
│   ├── organize_layers.jsx          # Layer naming helper
│   ├── batch_export_assets.jsx      # Batch export for multiple artboards
│   └── isometric_transform_helper.jsx  # Isometric transform utilities
│
├── python/
│   ├── clean_svg_paths.py           # vpype + svgpathtools cleanup
│   └── validate_svg_contract.py     # SVG contract validation
│
launchers/
├── 02_clean_svg.bat                 # Artist launcher for cleanup
```
