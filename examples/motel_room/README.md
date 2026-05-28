# Example: Motel Room

## Description

This example demonstrates the floorplan-to-isometric pipeline with a simple motel room layout.

## Files

- `placeholder_input.svg` — A minimal SVG floorplan with one room layer

## Usage (Future)

```powershell
python scripts/python/detect_rooms_from_svg.py --input examples/motel_room/placeholder_input.svg --list-rooms
blender --background --python scripts/blender/build_isometric_room.py -- --input examples/motel_room/placeholder_input.svg --room motel_room
```

## Expected Output

- PNG preview of an isometric motel room
- Blender scene with walls, floor, and basic furniture
