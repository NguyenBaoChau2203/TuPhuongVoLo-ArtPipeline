# Quickstart: Batch Isometric Render

## Prerequisites

- Python 3.11+ with project dependencies installed.
- Feature 001, 002, and 003 are merged.
- Blender 4.x is optional for this MVP. Dry-run works without Blender.

## Step 1: Create Two Simple SVG Files

Use `tests/in/` or another temporary folder. Example:

```powershell
@'
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <g id="room_kho"><path d="M0 0 L40 0 L40 30 L0 30 Z"/></g>
</svg>
'@ | Set-Content -Encoding UTF8 tests/in/batch_kho.svg

@'
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <g id="room_sanh_chinh"><path d="M0 0 L60 0 L60 40 L0 40 Z"/></g>
</svg>
'@ | Set-Content -Encoding UTF8 tests/in/batch_sanh_chinh.svg
```

## Step 2: Run Folder Dry-Run

```powershell
python scripts/python/batch_isometric_render.py --input-dir tests/in --dry-run --json-report outputs/reports/batch_isometric_report.json
```

Expected:

- No source SVG is modified.
- Blender is not required.
- Manifest is not updated.
- A JSON report is written to `outputs/reports/batch_isometric_report.json`.

## Step 3: Run Dry-Run With All Rooms

```powershell
python scripts/python/batch_isometric_render.py --input-file tests/in/batch_kho.svg --all-rooms --dry-run
```

For an SVG with multiple usable room groups, `--all-rooms` creates one planned job per room.

## Step 4: Check the JSON Report

```powershell
Get-Content outputs/reports/batch_isometric_report.json | ConvertFrom-Json
```

The report should show:

- `scanned_files`
- `detected_rooms`
- `planned_jobs`
- `succeeded`
- `failed`
- `skipped`
- `jobs` with planned `.blend` and PNG preview paths

## Optional: Actual Blender Run

When Blender 4.x is installed and available on PATH or configured in `config/pipeline.yaml`:

```powershell
python scripts/python/batch_isometric_render.py --input-dir assets/2d/svg_clean --all-rooms
```

Expected outputs when Blender succeeds:

- Editable Blender scenes in `outputs/blender/`
- PNG previews in `outputs/preview/`
- Manifest updates in `outputs/manifest/asset_manifest.json`
- Batch report in `outputs/reports/batch_isometric_report.json`

If Blender is missing, actual render mode fails gracefully with a Vietnamese error message.
Dry-run remains the safe default for artist launcher verification.
