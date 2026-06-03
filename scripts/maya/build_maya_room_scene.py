"""Build an editable Maya ASCII room blockout from Feature 005 geometry JSON."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_WALL_HEIGHT = 3.0
DEFAULT_WALL_THICKNESS = 0.12
DEFAULT_PROP_COLOR = "#8A7F72"
PREVIEW_FLOOR_COLOR_FALLBACK = (0.64, 0.70, 0.58)
DEFAULT_PREVIEW_ASPECT_RATIO = 16.0 / 9.0
ISO_CAMERA_DISTANCE_FACTOR = 3.5
ORTHOGRAPHIC_PADDING_FACTOR = 2.8
MIN_ORTHOGRAPHIC_WIDTH = 6.0
GENERIC_PROP_SIZE = (0.5, 0.6, 0.5)
MARKER_BBOX_DEFAULT_SCALE = 0.01
PROP_MARKER_PREFIXES = ("prop_", "item_", "object_")
OPENING_MARKER_TYPES = {"door", "window"}
OPENING_MARKER_SIZES = {
    "door": (0.7, 2.0, 0.06),
    "window": (0.8, 1.0, 0.06),
}
OPENING_MARKER_CENTER_Y = {
    "door": 1.0,
    "window": 1.35,
}
OPENING_NUMBER_SUFFIX_RE = re.compile(r"_\d{2,}$")
PROP_DEFINITION_SIZES = {
    # Maya scene units. These are intentionally rough blockout proportions,
    # centralized so marker names map to deterministic editable placeholders.
    "bed": (0.9, 0.55, 1.6),
    "table": (1.0, 0.75, 0.65),
    "chair": (0.45, 0.85, 0.45),
    "cabinet": (0.8, 1.3, 0.45),
    "shelf_unit": (0.8, 1.8, 0.35),
    "wooden_crate": (0.45, 0.45, 0.45),
    "barrel": (0.45, 0.7, 0.45),
    "box": (0.35, 0.35, 0.35),
}
LEGACY_PROCEDURAL_PROP_SIZES = {
    "sofa": (1.25, 0.85, 0.65),
    "fridge": (0.55, 1.7, 0.55),
    "sink": (0.8, 0.9, 0.55),
    "kitchen_counter": (1.4, 0.9, 0.55),
    "locker": (0.55, 1.8, 0.5),
    "plant": (0.45, 0.9, 0.45),
}
PROCEDURAL_PROP_SIZES = {
    **PROP_DEFINITION_SIZES,
    **LEGACY_PROCEDURAL_PROP_SIZES,
}
PROP_TYPE_ALIASES = {
    "bed": "bed",
    "single_bed": "bed",
    "metal_bed_frame": "bed",
    "table": "table",
    "desk": "table",
    "console_desk": "table",
    "dining_table": "table",
    "folding_table": "table",
    "lab_table": "table",
    "reception_desk": "table",
    "small_desk": "table",
    "chair": "chair",
    "folding_chair": "chair",
    "office_chair": "chair",
    "sofa": "sofa",
    "couch": "sofa",
    "bench": "sofa",
    "fridge": "fridge",
    "refrigerator": "fridge",
    "sink": "sink",
    "kitchen_counter": "kitchen_counter",
    "counter": "kitchen_counter",
    "cabinet": "cabinet",
    "cupboard": "cabinet",
    "glass_cabinet": "cabinet",
    "sample_cabinet": "cabinet",
    "locker": "locker",
    "plant": "plant",
    "potted_plant": "plant",
    "potted_plant_large": "plant",
    "shelf_unit": "shelf_unit",
    "shelf": "shelf_unit",
    "shelving": "shelf_unit",
    "metal_shelf": "shelf_unit",
    "wooden_crate": "wooden_crate",
    "crate": "wooden_crate",
    "barrel": "barrel",
    "wooden_barrel": "barrel",
    "box": "box",
    "cardboard_box": "box",
}
PROP_PLACEHOLDER_SIZES = {
    **PROCEDURAL_PROP_SIZES,
    "console_desk": PROCEDURAL_PROP_SIZES["table"],
    "office_chair": PROCEDURAL_PROP_SIZES["chair"],
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args used by mayapy."""

    parser = argparse.ArgumentParser(description="Build Maya .ma room blockout from JSON.")
    parser.add_argument("--geometry-json", required=True, type=Path)
    parser.add_argument("--maya-output", required=True, type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def initialize_maya() -> Any:
    """Import Maya commands and initialize standalone when running via mayapy."""

    try:
        import maya.cmds as cmds  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Không tìm thấy module Maya Python. "
            "Hãy chạy script bằng mayapy hoặc trong Maya."
        ) from exc

    try:
        import maya.standalone  # type: ignore[import-not-found]

        try:
            maya.standalone.initialize(name="python")
        except Exception as exc:  # Maya raises if already initialized inside Maya.
            if "initialized" not in str(exc).lower():
                raise
    except ModuleNotFoundError:
        pass

    return cmds


def load_geometry(path: Path) -> dict[str, Any]:
    """Load and validate geometry JSON."""

    if not path.exists():
        raise ValueError(f"Không tìm thấy geometry JSON: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Geometry JSON phải là object.")
    boundary_points = data.get("boundary_points")
    wall_segments = data.get("wall_segments")
    if not isinstance(boundary_points, list) or len(boundary_points) < 3:
        raise ValueError("Geometry JSON thiếu boundary_points hợp lệ.")
    if not isinstance(wall_segments, list) or len(wall_segments) < 3:
        raise ValueError("Geometry JSON thiếu wall_segments hợp lệ.")
    return data


def hex_to_rgb(value: str, fallback: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert #RRGGBB to Maya-friendly RGB floats."""

    text = str(value or "").strip().lstrip("#")
    if len(text) != 6:
        return fallback
    try:
        return tuple(
            int(text[index : index + 2], 16) / 255.0 for index in (0, 2, 4)
        )  # type: ignore[return-value]
    except ValueError:
        return fallback


def create_material(cmds: Any, name: str, color: tuple[float, float, float]) -> str:
    """Create a simple Lambert material and return its shading group."""

    material = cmds.shadingNode("lambert", asShader=True, name=name)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{name}SG")
    cmds.setAttr(f"{material}.color", color[0], color[1], color[2], type="double3")
    cmds.connectAttr(f"{material}.outColor", f"{shading_group}.surfaceShader", force=True)
    return shading_group


def preview_floor_color(value: Any) -> tuple[float, float, float]:
    """Return a visible floor color for white-background blockout previews."""

    color = hex_to_rgb(str(value or ""), PREVIEW_FLOOR_COLOR_FALLBACK)
    luminance = color[0] * 0.2126 + color[1] * 0.7152 + color[2] * 0.0722
    channel_range = max(color) - min(color)
    if luminance >= 0.86 and channel_range <= 0.14:
        return PREVIEW_FLOOR_COLOR_FALLBACK
    return color


def assign_material(cmds: Any, node: str, shading_group: str) -> None:
    """Assign material to a Maya node."""

    cmds.sets(node, edit=True, forceElement=shading_group)


def point2(value: Any) -> tuple[float, float]:
    """Validate and coerce a 2D point."""

    if not isinstance(value, list | tuple) or len(value) != 2:
        raise ValueError(f"Điểm không hợp lệ: {value}")
    return float(value[0]), float(value[1])


def room_bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Return min_x, min_z, max_x, max_z."""

    xs = [point[0] for point in points]
    zs = [point[1] for point in points]
    return min(xs), min(zs), max(xs), max(zs)


def camera_framing_from_bounds(
    bounds: tuple[float, float, float, float],
    wall_height: float,
    aspect_ratio: float = DEFAULT_PREVIEW_ASPECT_RATIO,
) -> dict[str, float]:
    """Return conservative isometric camera framing values for room bounds."""

    min_x, min_z, max_x, max_z = bounds
    room_width = max(max_x - min_x, 0.0)
    room_depth = max(max_z - min_z, 0.0)
    safe_wall_height = max(float(wall_height), 0.0)
    safe_aspect = max(float(aspect_ratio), 1.0)
    max_dimension = max(room_width, room_depth, 1.0)
    diagonal = max(math.hypot(room_width, room_depth), max_dimension)

    # OrthographicWidth is horizontal, but the real crop risk in a 16:9 preview
    # is often vertical: wall height projects upward and can touch the top edge.
    projected_vertical_extent = (room_width + room_depth) * 0.35 + safe_wall_height
    vertical_width_requirement = projected_vertical_extent * safe_aspect
    framing_base = max(
        max_dimension,
        diagonal * 0.85,
        safe_wall_height * 2.0,
        vertical_width_requirement,
    )

    return {
        "center_x": (min_x + max_x) / 2.0,
        "target_y": safe_wall_height / 2.0,
        "center_z": (min_z + max_z) / 2.0,
        "max_dimension": max_dimension,
        "camera_distance": max(max_dimension * ISO_CAMERA_DISTANCE_FACTOR, diagonal * 1.4),
        "orthographic_width": max(
            framing_base * ORTHOGRAPHIC_PADDING_FACTOR,
            MIN_ORTHOGRAPHIC_WIDTH,
        ),
    }


def scene_bounds_with_props(
    bounds: tuple[float, float, float, float],
    prop_markers: list[Any],
    units_scale: float = MARKER_BBOX_DEFAULT_SCALE,
) -> tuple[tuple[float, float, float, float], float]:
    """Expand room bounds with explicit prop marker centers and footprints."""

    min_x, min_z, max_x, max_z = bounds
    max_prop_height = 0.0
    for raw_marker in prop_markers:
        if not isinstance(raw_marker, dict):
            continue
        center = marker_center_maya(raw_marker)
        if center is None:
            continue
        raw_prop_type = marker_prop_type(raw_marker)
        width, height, depth = prop_blockout_size(
            normalize_prop_type(raw_prop_type),
            marker=raw_marker,
            units_scale=units_scale,
        )
        half_width = max(width / 2.0, 0.0)
        half_depth = max(depth / 2.0, 0.0)
        min_x = min(min_x, center[0] - half_width)
        max_x = max(max_x, center[0] + half_width)
        min_z = min(min_z, center[1] - half_depth)
        max_z = max(max_z, center[1] + half_depth)
        max_prop_height = max(max_prop_height, height)
    return (min_x, min_z, max_x, max_z), max_prop_height


def create_floor(
    cmds: Any,
    points: list[tuple[float, float]],
    material: str,
    parent: str,
) -> str:
    """Create a floor polygon from boundary points."""

    maya_points = [(x, 0.0, z) for x, z in points]
    floor = cmds.polyCreateFacet(point=maya_points, name="floor_blockout")[0]
    assign_material(cmds, floor, material)
    cmds.parent(floor, parent)
    return floor


def create_wall_block(
    cmds: Any,
    start: tuple[float, float],
    end: tuple[float, float],
    height: float,
    thickness: float,
    material: str,
    parent: str,
    index: int,
) -> str:
    """Create one wall segment as a transformed cube."""

    dx = end[0] - start[0]
    dz = end[1] - start[1]
    length = max(math.hypot(dx, dz), 0.001)
    mid_x = (start[0] + end[0]) / 2.0
    mid_z = (start[1] + end[1]) / 2.0
    angle_y = math.degrees(math.atan2(dz, dx))

    wall = cmds.polyCube(name=f"wall_{index:02d}", width=length, height=height, depth=thickness)[0]
    cmds.xform(wall, translation=(mid_x, height / 2.0, mid_z), rotation=(0.0, -angle_y, 0.0))
    assign_material(cmds, wall, material)
    cmds.parent(wall, parent)
    return wall


def create_prop_cube(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    parent: str,
    rotation_y_degrees: float = 0.0,
) -> str:
    """Create a simple placeholder prop cube."""

    width, height, depth = size
    node = cmds.polyCube(name=name, width=width, height=height, depth=depth)[0]
    cmds.xform(
        node,
        translation=(center[0], height / 2.0, center[1]),
        rotation=(0.0, rotation_y_degrees, 0.0),
    )
    assign_material(cmds, node, material)
    cmds.parent(node, parent)
    return node


def marker_rotation_y_degrees(marker: dict[str, Any]) -> float:
    """Return supported Y-axis prop marker rotation, defaulting to zero."""

    try:
        rotation = int(marker.get("rotation_y_degrees", 0))
    except (TypeError, ValueError):
        return 0.0
    if rotation in {0, 90, 180, 270}:
        return float(rotation)
    return 0.0


def safe_maya_name(value: Any, fallback: str = "prop") -> str:
    """Return a conservative Maya node-name token."""

    text = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "").strip().lower()).strip("_")
    if not text or not text[0].isalpha():
        return fallback
    return text


def opening_marker_type(value: Any) -> str:
    """Return a supported opening marker type."""

    token = safe_maya_name(value, fallback="opening")
    return token if token in OPENING_MARKER_TYPES else "opening"


def opening_marker_center_maya(marker: dict[str, Any]) -> tuple[float, float] | None:
    """Return an opening marker center from geometry JSON, or None if invalid."""

    try:
        return point2(marker.get("center_maya"))
    except (TypeError, ValueError):
        return None


def opening_marker_size(marker_type: Any) -> tuple[float, float, float]:
    """Return a simple thin placeholder size for door/window markers."""

    return OPENING_MARKER_SIZES.get(opening_marker_type(marker_type), (0.6, 1.0, 0.06))


def opening_marker_center_y(marker_type: Any) -> float:
    """Return a simple vertical center for the opening marker placeholder."""

    return OPENING_MARKER_CENTER_Y.get(opening_marker_type(marker_type), 0.5)


def opening_marker_node_name(marker: dict[str, Any], name_counts: dict[str, int]) -> str:
    """Return a deterministic Maya node name for one opening marker."""

    marker_type = opening_marker_type(marker.get("marker_type"))
    marker_name = safe_maya_name(marker.get("marker_name"), fallback="marker")
    base = safe_maya_name(f"{marker_type}_{marker_name}", fallback=f"{marker_type}_marker")
    count = name_counts.get(base, 0) + 1
    name_counts[base] = count
    if OPENING_NUMBER_SUFFIX_RE.search(base) and count == 1:
        return base
    return f"{base}_{count:02d}"


def create_opening_marker_cube(
    cmds: Any,
    name: str,
    marker_type: str,
    center: tuple[float, float],
    parent: str,
) -> str:
    """Create one simple door/window placeholder cube without cutting walls."""

    width, height, depth = opening_marker_size(marker_type)
    node = cmds.polyCube(name=name, width=width, height=height, depth=depth)[0]
    cmds.xform(
        node,
        translation=(center[0], opening_marker_center_y(marker_type), center[1]),
    )
    cmds.parent(node, parent)
    return node


def create_svg_opening_markers(
    cmds: Any,
    opening_markers: list[Any],
    parent: str,
) -> int:
    """Create placeholder door/window markers from explicit SVG markers."""

    created = 0
    name_counts: dict[str, int] = {}
    for raw_marker in opening_markers:
        if not isinstance(raw_marker, dict):
            continue
        center = opening_marker_center_maya(raw_marker)
        if center is None:
            continue
        marker_type = opening_marker_type(raw_marker.get("marker_type"))
        if marker_type not in OPENING_MARKER_TYPES:
            continue
        name = opening_marker_node_name(raw_marker, name_counts)
        create_opening_marker_cube(cmds, name, marker_type, center, parent)
        created += 1
    return created


def normalize_prop_type(value: Any) -> str:
    """Normalize prop aliases to the canonical procedural blockout type."""

    token = safe_maya_name(value, fallback="generic")
    for prefix in PROP_MARKER_PREFIXES:
        if token.startswith(prefix) and len(token) > len(prefix):
            token = token[len(prefix) :]
            break
    return PROP_TYPE_ALIASES.get(token, token)


def marker_prop_type(marker: dict[str, Any]) -> str:
    """Return the prop keyword from geometry JSON, accepting prop_type or name."""

    return safe_maya_name(marker.get("prop_type") or marker.get("name"), fallback="generic")


def has_prop_definition(prop_type: Any) -> bool:
    """Return whether a prop type has deterministic placeholder dimensions."""

    safe_type = safe_maya_name(prop_type, fallback="generic")
    return safe_type in PROP_PLACEHOLDER_SIZES or normalize_prop_type(safe_type) in PROP_PLACEHOLDER_SIZES


def has_procedural_prop(prop_type: Any) -> bool:
    """Return whether a prop type has a multi-piece procedural blockout builder."""

    return normalize_prop_type(prop_type) in PROP_BLOCKOUT_BUILDERS


def prop_placeholder_size(prop_type: str) -> tuple[float, float, float]:
    """Return the deterministic placeholder size for one prop type or alias."""

    safe_type = safe_maya_name(prop_type, fallback="generic")
    if safe_type in PROP_PLACEHOLDER_SIZES:
        return PROP_PLACEHOLDER_SIZES[safe_type]
    return PROP_PLACEHOLDER_SIZES.get(normalize_prop_type(safe_type), GENERIC_PROP_SIZE)


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bbox_dimensions(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, list | tuple) or len(value) != 4:
        return None
    min_x = _safe_float(value[0])
    min_y = _safe_float(value[1])
    max_x = _safe_float(value[2])
    max_y = _safe_float(value[3])
    if None in (min_x, min_y, max_x, max_y):
        return None
    width = abs(float(max_x) - float(min_x))
    depth = abs(float(max_y) - float(min_y))
    if width <= 0.0 or depth <= 0.0:
        return None
    return width, depth


def marker_footprint_maya(
    marker: dict[str, Any],
    units_scale: float = MARKER_BBOX_DEFAULT_SCALE,
) -> tuple[float, float] | None:
    """Return marker width/depth in Maya units if geometry JSON provides a safe bbox."""

    maya_bbox = _bbox_dimensions(marker.get("bbox_maya"))
    if maya_bbox is not None:
        return maya_bbox
    svg_bbox = _bbox_dimensions(marker.get("bbox_svg"))
    if svg_bbox is None:
        return None
    scale = abs(_safe_float(units_scale) or MARKER_BBOX_DEFAULT_SCALE)
    return svg_bbox[0] * scale, svg_bbox[1] * scale


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def prop_blockout_size(
    prop_type: str,
    marker: dict[str, Any] | None = None,
    units_scale: float = MARKER_BBOX_DEFAULT_SCALE,
) -> tuple[float, float, float]:
    """Return a conservative size for a procedural prop, optionally using marker bbox."""

    default_width, default_height, default_depth = prop_placeholder_size(prop_type)
    if marker is None:
        return default_width, default_height, default_depth

    footprint = marker_footprint_maya(marker, units_scale)
    if footprint is None:
        return default_width, default_height, default_depth

    marker_width, marker_depth = footprint
    width = _clamp(
        marker_width,
        max(0.25, default_width * 0.55),
        max(default_width * 1.8, default_width + 0.2),
    )
    depth = _clamp(
        marker_depth,
        max(0.25, default_depth * 0.55),
        max(default_depth * 1.8, default_depth + 0.2),
    )
    return width, default_height, depth


def marker_center_maya(marker: dict[str, Any]) -> tuple[float, float] | None:
    """Return a prop marker center from geometry JSON, or None if invalid."""

    try:
        return point2(marker.get("center_maya"))
    except (TypeError, ValueError):
        return None


def create_box(
    cmds: Any,
    name: str,
    center: tuple[float, float, float],
    size: tuple[float, float, float],
    material: str,
    parent: str,
) -> str:
    """Create one editable cube block with a world-space center."""

    width, height, depth = size
    node = cmds.polyCube(name=name, width=width, height=height, depth=depth)[0]
    cmds.xform(node, translation=center)
    assign_material(cmds, node, material)
    cmds.parent(node, parent)
    return node


def side_token(sign: int | float) -> str:
    """Return a Maya-safe left/right token for an x-axis sign."""

    return "left" if sign < 0 else "right"


def depth_token(sign: int | float) -> str:
    """Return a Maya-safe front/back token for a z-axis sign."""

    return "front" if sign < 0 else "back"


def corner_token(x_sign: int | float, z_sign: int | float) -> str:
    """Return a Maya-safe corner suffix from x/z signs."""

    return f"{side_token(x_sign)}_{depth_token(z_sign)}"


def build_bed_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a simple bed from base, mattress, and pillow blocks."""

    width, height, depth = size
    base_h = min(max(height * 0.38, 0.18), 0.28)
    mattress_h = min(max(height * 0.18, 0.08), 0.14)
    pillow_h = min(max(height * 0.16, 0.08), 0.14)
    create_box(
        cmds,
        f"{name}_base",
        (center[0], base_h / 2.0, center[1]),
        (width, base_h, depth),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_mattress",
        (center[0], base_h + mattress_h / 2.0, center[1]),
        (width * 0.92, mattress_h, depth * 0.92),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_pillow",
        (center[0], base_h + mattress_h + pillow_h / 2.0, center[1] - depth * 0.34),
        (width * 0.68, pillow_h, depth * 0.18),
        detail_material,
        parent,
    )


def build_table_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a table or desk from a tabletop and four legs."""

    width, height, depth = size
    top_h = min(max(height * 0.12, 0.06), 0.1)
    leg_h = max(height - top_h, 0.25)
    leg_w = min(max(width * 0.08, 0.045), 0.08)
    create_box(
        cmds,
        f"{name}_top",
        (center[0], leg_h + top_h / 2.0, center[1]),
        (width, top_h, depth),
        material,
        parent,
    )
    for x_sign, z_sign in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        create_box(
            cmds,
            f"{name}_leg_{corner_token(x_sign, z_sign)}",
            (
                center[0] + x_sign * (width / 2.0 - leg_w),
                leg_h / 2.0,
                center[1] + z_sign * (depth / 2.0 - leg_w),
            ),
            (leg_w, leg_h, leg_w),
            detail_material,
            parent,
        )


def build_chair_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a chair with seat, backrest, and simple legs."""

    width, height, depth = size
    seat_h = min(max(height * 0.12, 0.08), 0.12)
    seat_y = min(max(height * 0.45, 0.36), 0.48)
    back_h = max(height - seat_y, 0.28)
    leg_w = min(max(width * 0.1, 0.035), 0.06)
    create_box(
        cmds,
        f"{name}_seat",
        (center[0], seat_y, center[1]),
        (width, seat_h, depth),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_back",
        (center[0], seat_y + back_h / 2.0, center[1] + depth / 2.0 - leg_w),
        (width, back_h, leg_w),
        material,
        parent,
    )
    for x_sign, z_sign in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        create_box(
            cmds,
            f"{name}_leg_{corner_token(x_sign, z_sign)}",
            (
                center[0] + x_sign * (width / 2.0 - leg_w),
                (seat_y - seat_h / 2.0) / 2.0,
                center[1] + z_sign * (depth / 2.0 - leg_w),
            ),
            (leg_w, max(seat_y - seat_h / 2.0, 0.18), leg_w),
            detail_material,
            parent,
        )


def build_sofa_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a sofa from a seat, back, and two armrests."""

    width, height, depth = size
    seat_h = min(max(height * 0.35, 0.22), 0.32)
    back_h = max(height - seat_h * 0.5, 0.45)
    arm_w = min(max(width * 0.12, 0.09), 0.16)
    create_box(
        cmds,
        f"{name}_seat",
        (center[0], seat_h / 2.0, center[1]),
        (width, seat_h, depth),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_back",
        (center[0], seat_h + back_h / 2.0, center[1] + depth / 2.0 - arm_w / 2.0),
        (width, back_h, arm_w),
        material,
        parent,
    )
    for x_sign in (-1, 1):
        create_box(
            cmds,
            f"{name}_arm_{side_token(x_sign)}",
            (center[0] + x_sign * (width / 2.0 - arm_w / 2.0), seat_h, center[1]),
            (arm_w, seat_h * 2.0, depth),
            detail_material,
            parent,
        )


def build_tall_storage_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a tall cabinet/fridge/locker with a simple front seam."""

    width, height, depth = size
    seam_w = min(max(width * 0.035, 0.015), 0.035)
    seam_d = min(max(depth * 0.035, 0.012), 0.025)
    front_z = center[1] - depth / 2.0 - seam_d / 2.0
    create_box(cmds, f"{name}_body", (center[0], height / 2.0, center[1]), size, material, parent)
    create_box(
        cmds,
        f"{name}_door_seam",
        (center[0], height / 2.0, front_z),
        (seam_w, height * 0.82, seam_d),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_handle",
        (center[0] + width * 0.28, height * 0.55, front_z - seam_d),
        (seam_w, height * 0.18, seam_d),
        detail_material,
        parent,
    )


def build_sink_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a sink as a base cabinet, top slab, basin marker, and faucet."""

    width, height, depth = size
    top_h = min(max(height * 0.08, 0.05), 0.08)
    base_h = max(height - top_h, 0.4)
    create_box(
        cmds,
        f"{name}_base",
        (center[0], base_h / 2.0, center[1]),
        (width, base_h, depth),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_top",
        (center[0], base_h + top_h / 2.0, center[1]),
        (width * 1.04, top_h, depth * 1.04),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_basin_marker",
        (center[0], base_h + top_h + 0.006, center[1]),
        (width * 0.46, 0.012, depth * 0.45),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_faucet",
        (center[0], base_h + top_h + 0.08, center[1] - depth * 0.18),
        (0.04, 0.16, 0.04),
        detail_material,
        parent,
    )


def build_kitchen_counter_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a long counter block with a slightly wider top slab and panel seams."""

    width, height, depth = size
    top_h = min(max(height * 0.08, 0.05), 0.08)
    base_h = max(height - top_h, 0.45)
    create_box(
        cmds,
        f"{name}_base",
        (center[0], base_h / 2.0, center[1]),
        (width, base_h, depth),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_top",
        (center[0], base_h + top_h / 2.0, center[1]),
        (width * 1.04, top_h, depth * 1.04),
        material,
        parent,
    )
    for x_offset in (-width * 0.18, width * 0.18):
        create_box(
            cmds,
            f"{name}_panel_{x_offset:.2f}".replace("-", "m").replace(".", "_"),
            (center[0] + x_offset, base_h * 0.5, center[1] - depth / 2.0 - 0.01),
            (0.025, base_h * 0.72, 0.02),
            detail_material,
            parent,
        )


def build_plant_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a plant placeholder with pot, trunk, and simple crossed leaves."""

    width, height, depth = size
    pot_h = min(max(height * 0.28, 0.18), 0.28)
    trunk_h = max(height * 0.35, 0.25)
    leaf_h = max(height - pot_h - trunk_h * 0.45, 0.22)
    create_box(
        cmds,
        f"{name}_pot",
        (center[0], pot_h / 2.0, center[1]),
        (width * 0.62, pot_h, depth * 0.62),
        material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_stem",
        (center[0], pot_h + trunk_h / 2.0, center[1]),
        (width * 0.12, trunk_h, depth * 0.12),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_leaf_x",
        (center[0], pot_h + trunk_h + leaf_h * 0.25, center[1]),
        (width, leaf_h, depth * 0.16),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_leaf_z",
        (center[0], pot_h + trunk_h + leaf_h * 0.25, center[1]),
        (width * 0.16, leaf_h, depth),
        detail_material,
        parent,
    )


def build_crate_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a crate/box with subtle top and side seam blocks."""

    width, height, depth = size
    seam_h = min(max(height * 0.04, 0.015), 0.03)
    create_box(cmds, f"{name}_body", (center[0], height / 2.0, center[1]), size, material, parent)
    create_box(
        cmds,
        f"{name}_top_seam",
        (center[0], height + seam_h / 2.0, center[1]),
        (width * 0.85, seam_h, depth * 0.12),
        detail_material,
        parent,
    )
    create_box(
        cmds,
        f"{name}_side_seam",
        (center[0], height * 0.55, center[1] - depth / 2.0 - 0.01),
        (width * 0.12, height * 0.7, 0.02),
        detail_material,
        parent,
    )


def build_shelf_prop(
    cmds: Any,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a shelf unit from side posts and three shelf slabs."""

    width, height, depth = size
    post_w = min(max(width * 0.08, 0.04), 0.08)
    slab_h = min(max(height * 0.035, 0.035), 0.07)
    for x_sign in (-1, 1):
        create_box(
            cmds,
            f"{name}_side_{side_token(x_sign)}",
            (center[0] + x_sign * (width / 2.0 - post_w / 2.0), height / 2.0, center[1]),
            (post_w, height, depth),
            material,
            parent,
        )
    for shelf_index, y in enumerate((height * 0.18, height * 0.5, height * 0.82), start=1):
        create_box(
            cmds,
            f"{name}_shelf_{shelf_index}",
            (center[0], y, center[1]),
            (width, slab_h, depth),
            detail_material,
            parent,
        )


PROP_BLOCKOUT_BUILDERS = {
    "bed": build_bed_prop,
    "table": build_table_prop,
    "chair": build_chair_prop,
    "sofa": build_sofa_prop,
    "fridge": build_tall_storage_prop,
    "cabinet": build_tall_storage_prop,
    "locker": build_tall_storage_prop,
    "sink": build_sink_prop,
    "kitchen_counter": build_kitchen_counter_prop,
    "plant": build_plant_prop,
    "wooden_crate": build_crate_prop,
    "shelf_unit": build_shelf_prop,
}


def create_procedural_prop(
    cmds: Any,
    name: str,
    prop_type: str,
    center: tuple[float, float],
    marker: dict[str, Any] | None,
    material: str,
    detail_material: str,
    parent: str,
    units_scale: float = MARKER_BBOX_DEFAULT_SCALE,
    rotation_y_degrees: float = 0.0,
) -> str:
    """Create a procedural prop when known, or the generic cube fallback."""

    canonical_type = normalize_prop_type(prop_type)
    builder = PROP_BLOCKOUT_BUILDERS.get(canonical_type)
    if builder is None:
        size = (
            prop_blockout_size(canonical_type, marker=marker, units_scale=units_scale)
            if has_prop_definition(canonical_type)
            else GENERIC_PROP_SIZE
        )
        return create_prop_cube(
            cmds,
            name,
            center,
            size,
            material,
            parent,
            rotation_y_degrees=rotation_y_degrees,
        )

    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    size = prop_blockout_size(canonical_type, marker=marker, units_scale=units_scale)
    builder(cmds, name, center, size, material, detail_material, group)
    cmds.xform(
        group,
        pivots=(center[0], 0.0, center[1]),
        worldSpace=True,
        rotation=(0.0, rotation_y_degrees, 0.0),
    )
    return group


def create_svg_prop_markers(
    cmds: Any,
    prop_markers: list[Any],
    material: str,
    detail_material: str,
    parent: str,
    units_scale: float = MARKER_BBOX_DEFAULT_SCALE,
) -> int:
    """Create blockout props from explicit artist-authored SVG markers."""

    created = 0
    type_counts: dict[str, int] = {}
    for raw_marker in prop_markers:
        if not isinstance(raw_marker, dict):
            continue
        center = marker_center_maya(raw_marker)
        if center is None:
            continue
        raw_prop_type = marker_prop_type(raw_marker)
        canonical_type = normalize_prop_type(raw_prop_type)
        name_type = (
            canonical_type
            if has_procedural_prop(canonical_type) or has_prop_definition(canonical_type)
            else raw_prop_type
        )
        type_counts[name_type] = type_counts.get(name_type, 0) + 1
        create_procedural_prop(
            cmds,
            f"prop_{name_type}_{type_counts[name_type]:02d}",
            raw_prop_type,
            center,
            raw_marker,
            material,
            detail_material,
            parent,
            units_scale=units_scale,
            rotation_y_degrees=marker_rotation_y_degrees(raw_marker),
        )
        created += 1
    return created


def create_placeholder_props(
    cmds: Any,
    room_preset: dict[str, Any],
    bounds: tuple[float, float, float, float],
    material: str,
    detail_material: str,
    parent: str,
) -> None:
    """Create a few simple prop blockouts from room presets."""

    min_x, min_z, max_x, max_z = bounds
    width = max(max_x - min_x, 0.5)
    depth = max(max_z - min_z, 0.5)
    cursor_x = min_x + width * 0.25
    cursor_z = min_z + depth * 0.25
    props = room_preset.get("props", []) if isinstance(room_preset, dict) else []
    if not isinstance(props, list):
        return

    created = 0
    for raw_prop in props:
        if not isinstance(raw_prop, dict):
            continue
        prop_name = safe_maya_name(raw_prop.get("name", "prop"), fallback="prop")
        count = max(1, min(int(raw_prop.get("count", 1)), 3))
        for copy_index in range(count):
            created += 1
            offset_x = (copy_index % 3) * 0.65
            offset_z = (created // 3) * 0.65
            x = min(cursor_x + offset_x, max_x - 0.25)
            z = min(cursor_z + offset_z, max_z - 0.25)
            create_procedural_prop(
                cmds,
                f"{prop_name}_{copy_index + 1:02d}",
                prop_name,
                (x, z),
                None,
                material,
                detail_material,
                parent,
            )


def create_camera_and_lights(
    cmds: Any,
    room_name: str,
    bounds: tuple[float, float, float, float],
    framing_height: float,
    parent: str,
) -> None:
    """Create an orthographic isometric camera and simple lights."""

    framing = camera_framing_from_bounds(bounds, framing_height)
    camera_transform, camera_shape = cmds.camera(name=f"cam_{room_name}_iso")
    distance = framing["camera_distance"]
    target_locator = cmds.spaceLocator(name=f"LOC_{room_name}_camera_target")[0]
    cmds.xform(
        target_locator,
        translation=(framing["center_x"], framing["target_y"], framing["center_z"]),
    )
    cmds.xform(
        camera_transform,
        translation=(
            framing["center_x"] + distance,
            framing["target_y"] + distance,
            framing["center_z"] + distance,
        ),
    )
    aim = cmds.aimConstraint(
        target_locator,
        camera_transform,
        aimVector=(0.0, 0.0, -1.0),
        upVector=(0.0, 1.0, 0.0),
        worldUpType="vector",
        worldUpVector=(0.0, 1.0, 0.0),
    )[0]
    cmds.delete(aim, target_locator)
    cmds.setAttr(f"{camera_shape}.orthographic", True)
    cmds.setAttr(f"{camera_shape}.orthographicWidth", framing["orthographic_width"])
    # mayapy runs headless and has no active viewport; the camera is saved
    # into the scene without switching the current viewport.
    cmds.parent(camera_transform, parent)

    key_light = cmds.directionalLight(name="key_light")
    key_transform = cmds.listRelatives(key_light, parent=True)[0]
    cmds.xform(key_transform, rotation=(-45.0, 35.0, 0.0))
    cmds.parent(key_transform, parent)

    ambient = cmds.ambientLight(name="ambient_light", intensity=0.35)
    ambient_transform = cmds.listRelatives(ambient, parent=True)[0]
    cmds.parent(ambient_transform, parent)


def build_scene(cmds: Any, data: dict[str, Any], maya_output: Path) -> None:
    """Build and save the Maya scene."""

    room_name = str(data.get("room_name") or "room")
    style = data.get("style_preset", {}) if isinstance(data.get("style_preset"), dict) else {}
    room_preset = data.get("room_preset", {}) if isinstance(data.get("room_preset"), dict) else {}
    units = data.get("units", {}) if isinstance(data.get("units"), dict) else {}
    units_scale = _safe_float(units.get("scale")) or MARKER_BBOX_DEFAULT_SCALE
    prop_markers = data.get("prop_markers", [])
    if not isinstance(prop_markers, list):
        prop_markers = []
    opening_markers = data.get("opening_markers", [])
    if not isinstance(opening_markers, list):
        opening_markers = []
    points = [point2(point) for point in data["boundary_points"]]
    wall_segments = [
        (point2(segment["start"]), point2(segment["end"]))
        for segment in data["wall_segments"]
        if isinstance(segment, dict)
    ]
    if len(wall_segments) < 3:
        raise ValueError("wall_segments không hợp lệ.")

    cmds.file(new=True, force=True)
    cmds.currentUnit(linear="meter")
    root = cmds.group(empty=True, name=f"GRP_{room_name}_blockout")
    walls_group = cmds.group(empty=True, name="walls")
    props_group = cmds.group(empty=True, name="props")
    lights_group = cmds.group(empty=True, name="lights")
    cmds.parent(walls_group, root)
    cmds.parent(props_group, root)
    cmds.parent(lights_group, root)
    openings_group: str | None = None
    if opening_markers:
        openings_group = cmds.group(empty=True, name="openings")
        cmds.parent(openings_group, root)

    floor_mat = create_material(
        cmds,
        "MAT_floor",
        preview_floor_color(style.get("floor_color")),
    )
    wall_mat = create_material(
        cmds,
        "MAT_wall",
        hex_to_rgb(str(style.get("wall_color", "")), (0.95, 0.95, 0.9)),
    )
    prop_mat = create_material(cmds, "MAT_props", hex_to_rgb(DEFAULT_PROP_COLOR, (0.54, 0.5, 0.45)))
    prop_detail_mat = create_material(
        cmds,
        "MAT_prop_details",
        hex_to_rgb("#5D554D", (0.36, 0.33, 0.30)),
    )

    bounds = room_bounds(points)
    wall_height = float(room_preset.get("wall_height", DEFAULT_WALL_HEIGHT))
    camera_bounds, max_prop_height = scene_bounds_with_props(
        bounds,
        prop_markers,
        units_scale=units_scale,
    )
    framing_height = max(wall_height, max_prop_height)
    create_floor(cmds, points, floor_mat, root)
    for index, (start, end) in enumerate(wall_segments, start=1):
        create_wall_block(
            cmds,
            start,
            end,
            height=wall_height,
            thickness=DEFAULT_WALL_THICKNESS,
            material=wall_mat,
            parent=walls_group,
            index=index,
        )
    if prop_markers:
        # Explicit SVG markers are artist-authored placement, so they replace
        # room-preset auto props to avoid duplicate blockout placeholders.
        create_svg_prop_markers(
            cmds,
            prop_markers,
            prop_mat,
            prop_detail_mat,
            props_group,
            units_scale=units_scale,
        )
    else:
        create_placeholder_props(cmds, room_preset, bounds, prop_mat, prop_detail_mat, props_group)
    if openings_group is not None:
        create_svg_opening_markers(cmds, opening_markers, openings_group)
    create_camera_and_lights(cmds, room_name, camera_bounds, framing_height, lights_group)

    maya_output.parent.mkdir(parents=True, exist_ok=True)
    cmds.file(rename=str(maya_output))
    cmds.file(save=True, type="mayaAscii", force=True)


def main(argv: list[str] | None = None) -> int:
    """Run the Maya scene builder."""

    args = parse_args(argv)
    try:
        print("Feature 005 Maya: initializing Maya...")
        cmds = initialize_maya()
        data = load_geometry(args.geometry_json)
        print(f"Feature 005 Maya: building room {data.get('room_name')}")
        build_scene(cmds, data, args.maya_output.resolve())
        print(f"Feature 005 Maya: saved {args.maya_output}")
        return 0
    except Exception as exc:
        print(f"ERR_MAYA_SCENE_BUILD: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
