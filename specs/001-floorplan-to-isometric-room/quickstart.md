# Quickstart: Floorplan to Isometric Room

## Prerequisites

- [ ] Python 3.10+ installed
- [ ] Blender 4.x installed and in PATH (or path configured in `config/pipeline.yaml`)
- [ ] Virtual environment activated: `.\.venv\Scripts\Activate.ps1`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Feature 002 (SVG export/cleanup) completed — you need a clean SVG

## Quick Verification

### Step 1: Check example input exists

```powershell
Test-Path examples/motel_room/placeholder_input.svg
```

### Step 2: List rooms in SVG

```powershell
python scripts/python/detect_rooms_from_svg.py --input examples/motel_room/placeholder_input.svg --list-rooms
```

Expected: List of room names found in the SVG.

### Step 3: Build one room

```powershell
# Via launcher (artist way)
launchers\03_build_isometric_room.bat

# Via command line (developer way)
blender --background --python scripts/blender/build_isometric_room.py -- --input examples/motel_room/placeholder_input.svg --room kho --style line_art_green_floor
```

### Step 4: Check outputs

```powershell
Get-ChildItem outputs/preview/ -Filter "*.png"
Get-ChildItem outputs/blender/ -Filter "*.blend"
```

### Step 5: Check manifest

```powershell
Get-Content outputs/manifest/asset_manifest.json | ConvertFrom-Json
```

### Step 6: Open Blender scene

```powershell
# Open the generated .blend file in Blender for manual review
blender outputs/blender/tu_phuong_vo_lo_kho_main_iso_v001.blend
```

## Expected Results

| Output | Location | Format |
|--------|----------|--------|
| PNG preview | `outputs/preview/` | Transparent PNG |
| Blender scene | `outputs/blender/` | .blend |
| Manifest entry | `outputs/manifest/asset_manifest.json` | JSON |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Blender not found" | Set `tool_paths.blender` in `config/pipeline.yaml` |
| "No rooms found in SVG" | Ensure SVG has named `<g>` groups for rooms |
| "SVG validation failed" | Run Feature 002 cleanup first |
| PNG is blank | Check camera position and room boundaries |
