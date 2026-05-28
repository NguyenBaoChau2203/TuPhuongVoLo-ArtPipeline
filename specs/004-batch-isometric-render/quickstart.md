# Quickstart: Batch Isometric Render

## Prerequisites

- [ ] Feature 001 (single room render) is implemented and tested
- [ ] Blender 4.x installed
- [ ] Clean SVGs available in `assets/2d/svg_clean/`

## Quick Verification

### Step 1: Prepare input folder

Ensure `assets/2d/svg_clean/` contains at least 2 clean SVGs with room layers.

### Step 2: Run batch render

```powershell
# Via launcher
launchers\04_batch_render.bat

# Via command line
blender --background --python scripts/blender/batch_render_rooms.py -- --input assets/2d/svg_clean/ --style line_art_green_floor
```

### Step 3: Check outputs

```powershell
Get-ChildItem outputs/preview/ -Filter "*.png" | Measure-Object
```

Expected: One PNG per room detected.

### Step 4: Check manifest

```powershell
Get-Content outputs/manifest/asset_manifest.json | ConvertFrom-Json | Measure-Object
```
