"""
setup_iso_camera.py — TuPhuongVoLo-ArtPipeline (Maya Script)

Purpose:
    Set up an orthographic isometric camera in Maya matching
    the Blender pipeline's camera parameters.

Usage (future):
    mayapy scripts/maya/setup_iso_camera.py

Status: PLACEHOLDER — TODO: Implement Maya isometric camera setup

See: specs/005-maya-bridge/spec.md
"""

import sys


def main():
    """Setup isometric camera in Maya."""
    # TODO: Implement Maya camera setup:
    # 1. Import maya.cmds (only available in mayapy)
    # 2. Create camera: cmds.camera(orthographic=True)
    # 3. Set rotation: X=54.736°, Z=45° (match Blender)
    # 4. Set orthographic width based on scene
    # 5. Name camera: "IsometricCamera"

    print("=" * 60)
    print("TuPhuongVoLo-ArtPipeline — Maya Isometric Camera Setup")
    print("=" * 60)
    print()
    print("⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)")
    print("TODO: Implement Maya isometric camera")
    print("See: specs/005-maya-bridge/spec.md")


if __name__ == "__main__":
    main()
