# Contracts: Floorplan to Isometric Room

## Input Contract: Clean SVG

The input SVG must satisfy these constraints:

```
SVG Clean Contract:
  - Valid XML / SVG 1.1
  - Rooms are in named <g> elements (id attribute = room name)
  - Wall paths are closed <path> elements with 'd' attribute
  - No embedded raster images
  - No JavaScript or animation elements
  - Transforms flattened (no nested transform matrices)
  - Coordinates in absolute units (not relative)
  - File extension: .svg
  - Encoding: UTF-8
```

### Example Valid Input

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <g id="room_kho">
    <path d="M100,100 L300,100 L300,250 L100,250 Z"
          fill="none" stroke="#000" stroke-width="2"/>
  </g>
  <g id="room_sanh_chinh">
    <path d="M350,100 L600,100 L600,400 L350,400 Z"
          fill="none" stroke="#000" stroke-width="2"/>
  </g>
</svg>
```

## Output Contract: Generated Files

### PNG Preview

```
Output: outputs/preview/{naming_convention}.png
- Format: PNG with transparent background
- Resolution: from config/pipeline.yaml (default 1920x1080)
- Color profile: sRGB
```

### Blender Scene

```
Output: outputs/blender/{naming_convention}.blend
- Format: Blender native (.blend)
- Compatible with: Blender 4.x
- Contains: walls mesh, floor plane, camera, lights, props (if preset used)
- Scene named: room name from SVG
```

### SVG Output (where possible)

```
Output: outputs/svg/{naming_convention}.svg
- Format: SVG 1.1
- Contains: 2D isometric projection of the room (optional, advanced)
```

### Manifest Entry

```json
{
  "asset_name": "kho",
  "variant": "main",
  "stage": "iso",
  "version": "001",
  "source_file": "assets/2d/svg_clean/floorplan.svg",
  "output_path": "outputs/blender/tu_phuong_vo_lo_kho_main_iso_v001.blend",
  "timestamp": "2026-05-29T12:00:00+07:00",
  "checksum": "sha256:abc123...",
  "pipeline_step": "001-floorplan-to-isometric-room"
}
```

## CLI Contract

```
python scripts/python/detect_rooms_from_svg.py
  --input <path-to-clean-svg>
  [--room <room-name>]              # Optional, default: all rooms
  [--list-rooms]                     # List available rooms and exit

blender --background --python scripts/blender/build_isometric_room.py --
  --input <path-to-clean-svg>
  --room <room-name>
  [--style <style-preset-name>]      # Default: line_art_green_floor
  [--room-preset <room-preset-name>] # Default: auto-detect from room name
  [--output-dir <path>]             # Default: outputs/
  [--version <NNN>]                  # Default: auto-increment
```

## Error Contract

All errors must include:
- Error code (e.g., `ERR_SVG_INVALID`, `ERR_ROOM_NOT_FOUND`)
- Vietnamese message for artist-facing errors
- English message for developer logs
- Exit code ≠ 0 for CLI failures
