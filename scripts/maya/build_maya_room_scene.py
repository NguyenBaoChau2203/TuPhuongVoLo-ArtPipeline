"""Build an editable Maya ASCII room blockout from Feature 005 geometry JSON."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

DEFAULT_WALL_HEIGHT = 3.0
DEFAULT_WALL_THICKNESS = 0.12
DEFAULT_PROP_COLOR = "#8A7F72"


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
) -> str:
    """Create a simple placeholder prop cube."""

    width, height, depth = size
    node = cmds.polyCube(name=name, width=width, height=height, depth=depth)[0]
    cmds.xform(node, translation=(center[0], height / 2.0, center[1]))
    assign_material(cmds, node, material)
    cmds.parent(node, parent)
    return node


def create_placeholder_props(
    cmds: Any,
    room_preset: dict[str, Any],
    bounds: tuple[float, float, float, float],
    material: str,
    parent: str,
) -> None:
    """Create a few simple prop placeholders from room presets."""

    min_x, min_z, max_x, max_z = bounds
    width = max(max_x - min_x, 0.5)
    depth = max(max_z - min_z, 0.5)
    cursor_x = min_x + width * 0.25
    cursor_z = min_z + depth * 0.25
    props = room_preset.get("props", []) if isinstance(room_preset, dict) else []
    if not isinstance(props, list):
        return

    known_sizes = {
        "shelf_unit": (0.8, 1.8, 0.35),
        "wooden_crate": (0.45, 0.45, 0.45),
        "cardboard_box": (0.35, 0.35, 0.35),
        "console_desk": (1.2, 0.75, 0.55),
        "office_chair": (0.45, 0.8, 0.45),
    }
    created = 0
    for raw_prop in props:
        if not isinstance(raw_prop, dict):
            continue
        prop_name = str(raw_prop.get("name", "prop"))
        count = max(1, min(int(raw_prop.get("count", 1)), 3))
        size = known_sizes.get(prop_name, (0.5, 0.6, 0.5))
        for copy_index in range(count):
            created += 1
            offset_x = (copy_index % 3) * 0.65
            offset_z = (created // 3) * 0.65
            x = min(cursor_x + offset_x, max_x - 0.25)
            z = min(cursor_z + offset_z, max_z - 0.25)
            create_prop_cube(
                cmds,
                f"{prop_name}_{copy_index + 1:02d}",
                (x, z),
                size,
                material,
                parent,
            )


def create_camera_and_lights(
    cmds: Any,
    room_name: str,
    bounds: tuple[float, float, float, float],
    parent: str,
) -> None:
    """Create an orthographic isometric camera and simple lights."""

    min_x, min_z, max_x, max_z = bounds
    center_x = (min_x + max_x) / 2.0
    center_z = (min_z + max_z) / 2.0
    span = max(max_x - min_x, max_z - min_z, 1.0)
    camera_transform, camera_shape = cmds.camera(name=f"cam_{room_name}_iso")
    distance = span * 1.8
    cmds.xform(
        camera_transform,
        translation=(center_x + distance, distance * 0.8, center_z + distance),
        rotation=(-35.264, 45.0, 0.0),
    )
    cmds.setAttr(f"{camera_shape}.orthographic", True)
    cmds.setAttr(f"{camera_shape}.orthographicWidth", span * 1.4)
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

    floor_mat = create_material(
        cmds,
        "MAT_floor",
        hex_to_rgb(str(style.get("floor_color", "")), (0.29, 0.49, 0.35)),
    )
    wall_mat = create_material(
        cmds,
        "MAT_wall",
        hex_to_rgb(str(style.get("wall_color", "")), (0.95, 0.95, 0.9)),
    )
    prop_mat = create_material(cmds, "MAT_props", hex_to_rgb(DEFAULT_PROP_COLOR, (0.54, 0.5, 0.45)))

    bounds = room_bounds(points)
    create_floor(cmds, points, floor_mat, root)
    wall_height = float(room_preset.get("wall_height", DEFAULT_WALL_HEIGHT))
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
    create_placeholder_props(cmds, room_preset, bounds, prop_mat, props_group)
    create_camera_and_lights(cmds, room_name, bounds, lights_group)

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
