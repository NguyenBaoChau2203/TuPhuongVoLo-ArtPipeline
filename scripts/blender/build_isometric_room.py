"""
build_isometric_room.py — TuPhuongVoLo-ArtPipeline (Blender Script)

Purpose:
    Build an isometric room scene in Blender from a clean SVG floorplan.
    Imports SVG wall paths, extrudes to 3D walls, creates floor plane,
    sets up isometric camera, applies style preset, and renders PNG.

Usage (future):
    blender --background --python scripts/blender/build_isometric_room.py -- \\
        --input assets/2d/svg_clean/floorplan.svg \\
        --room kho \\
        --style line_art_green_floor

Status: PLACEHOLDER — TODO: Implement Blender scene builder

See: specs/001-floorplan-to-isometric-room/spec.md
"""

# NOTE: This script runs INSIDE Blender's Python environment.
# 'bpy' is only available when run via Blender.

import sys


def main():
    """Build isometric room scene from SVG input."""
    # TODO: Implement the following steps:
    #
    # 1. Parse command line arguments (after '--' separator)
    #    --input: path to clean SVG
    #    --room: room name to extract
    #    --style: style preset name
    #    --room-preset: room preset for props
    #    --output-dir: output directory
    #
    # 2. Import SVG into Blender
    #    bpy.ops.import_curve.svg(filepath=svg_path)
    #
    # 3. Convert curves to mesh
    #    Select imported curves → bpy.ops.object.convert(target='MESH')
    #
    # 4. Extrude walls
    #    Select wall faces → extrude by wall_height from room preset
    #
    # 5. Create floor plane
    #    Generate a plane matching room boundary polygon
    #
    # 6. Setup isometric camera
    #    Camera type: ORTHO
    #    Rotation: X=54.736°, Z=45° (standard isometric)
    #    Fit to room bounding box
    #
    # 7. Apply style preset
    #    Load colors from config/style_presets.yaml
    #    Create materials for walls, floor
    #    Set lighting and shadow parameters
    #
    # 8. Place props (if room preset provided)
    #    Load props from config/room_presets.yaml
    #    Generate basic geometry for each prop
    #    Place according to placement strategy
    #
    # 9. Render PNG
    #    Set resolution from config
    #    Set transparent background
    #    Render to outputs/preview/
    #
    # 10. Save .blend scene
    #     Save to outputs/blender/
    #
    # 11. Update manifest

    print("=" * 60)
    print("TuPhuongVoLo-ArtPipeline — Build Isometric Room (Blender)")
    print("=" * 60)
    print()
    print("⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)")
    print("TODO: Implement Blender isometric room builder")
    print("See: specs/001-floorplan-to-isometric-room/spec.md")
    print()
    print(f"Arguments received: {sys.argv}")


if __name__ == "__main__":
    main()
