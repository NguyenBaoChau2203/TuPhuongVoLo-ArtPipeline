"""
import_svg_walls.py — TuPhuongVoLo-ArtPipeline (Maya Script)

Purpose:
    Import SVG wall geometry into Maya via one of:
    - Blender → USD → Maya interchange
    - Custom SVG parser → Maya curves
    - Direct SVG (limited support)

Usage (future):
    mayapy scripts/maya/import_svg_walls.py --input file.svg --room kho

Status: PLACEHOLDER — TODO: Implement SVG-to-Maya import

See: specs/005-maya-bridge/spec.md
"""

import sys


def main():
    """Import SVG walls into Maya."""
    # TODO: Implement SVG import strategy:
    # Option A: Parse SVG with svgpathtools → create Maya NURBS curves
    # Option B: Load USD file exported from Blender
    # Option C: Use Maya's limited SVG support (if available)

    print("=" * 60)
    print("TuPhuongVoLo-ArtPipeline — Maya SVG Wall Import")
    print("=" * 60)
    print()
    print("⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)")
    print("TODO: Implement SVG wall import to Maya")
    print("See: specs/005-maya-bridge/spec.md")


if __name__ == "__main__":
    main()
