# Quickstart: Floorplan to Isometric Room

## Prerequisites

- Python 3.11+ installed
- Dependencies installed with `pip install -r requirements.txt`
- A clean SVG from Feature 002
- Blender 4.x installed only for the actual render step

## 1. Create a simple clean SVG for verification

```powershell
@'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <g id="room_kho">
    <path d="M10 10 L100 10 L100 80 L10 80 Z" fill="none" stroke="#000"/>
  </g>
</svg>
'@ | Set-Content -Encoding UTF8 tests/in/feature001_kho.svg
```

## 2. Detect rooms

```powershell
python scripts/python/detect_rooms_from_svg.py --input tests/in/feature001_kho.svg --json-report outputs/reports/rooms.json
```

Expected:

- Room `kho` is listed.
- `closed_path_count` is at least `1`.
- `outputs/reports/rooms.json` contains the detected boundary.

## 3. Run dry-run without Blender

```powershell
python scripts/python/build_isometric_room.py --input tests/in/feature001_kho.svg --room kho --dry-run
```

Expected:

- Prints selected room `kho`.
- Prints planned outputs:
  - `outputs/blender/tu_phuong_vo_lo_kho_main_iso_v001.blend`
  - `outputs/preview/tu_phuong_vo_lo_kho_main_preview_v001.png`
- Prints a command containing `blender --background --python`.
- Does not update `outputs/manifest/asset_manifest.json`.

## 4. Run actual Blender build when Blender is installed

```powershell
python scripts/python/build_isometric_room.py --input tests/in/feature001_kho.svg --room kho --style line_art_green_floor
```

Expected:

- PNG preview appears in `outputs/preview/`.
- Editable Blender scene appears in `outputs/blender/`.
- Manifest receives one `iso` entry and one `preview` entry for the generated files.

If Blender is not found, the CLI exits with a Vietnamese error and does not create fake success outputs.

## 5. Artist launcher path

```powershell
launchers\03_build_isometric_room.bat
```

The launcher uses a dragged SVG if provided. Without a dragged file, it uses the newest `.svg` in `assets\2d\svg_clean`.

## 6. Required developer checks

```powershell
python -m pytest tests/test_svg_cleanup.py tests/test_manifest.py tests/test_naming_convention.py -v
python -m pytest tests/test_room_geometry.py tests/test_detect_rooms_from_svg.py tests/test_build_isometric_room.py -v
python scripts/python/detect_rooms_from_svg.py --help
python scripts/python/build_isometric_room.py --help
python scripts/python/build_isometric_room.py --input tests/in/feature001_kho.svg --room kho --dry-run
python -m compileall scripts/python
python -m ruff check scripts/python tests
```

If `ruff` is unavailable, report that and continue; it is not required for the artist workflow.
