"""
detect_rooms_from_svg.py — TuPhuongVoLo-ArtPipeline

Purpose:
    Parse a clean SVG file and detect rooms by identifying
    named groups (<g> elements with room-related IDs).

Usage (future):
    python scripts/python/detect_rooms_from_svg.py --input file.svg --list-rooms
    python scripts/python/detect_rooms_from_svg.py --input file.svg --room kho

Status: PLACEHOLDER — TODO: Implement room detection

See: specs/001-floorplan-to-isometric-room/spec.md
"""

from pathlib import Path


def detect_rooms(svg_path: Path) -> list[dict]:
    """Detect rooms in an SVG file by parsing named groups.

    Returns:
        List of room dicts with keys: name, layer_id, path_count, bounding_box
    """
    # TODO: Implement room detection:
    # 1. Parse SVG with lxml or svgpathtools
    # 2. Find <g> elements with id matching "room_*"
    # 3. Extract paths within each group
    # 4. Calculate bounding box for each room
    # 5. Return list of room metadata
    print(f"TODO: Detect rooms from {svg_path}")
    return []


def main() -> None:
    """CLI entry point for room detection."""
    print("=" * 60)
    print("TuPhuongVoLo-ArtPipeline — Room Detection")
    print("=" * 60)
    print()
    print("⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)")
    print("TODO: Implement room detection from SVG")
    print("See: specs/001-floorplan-to-isometric-room/spec.md")


if __name__ == "__main__":
    main()
