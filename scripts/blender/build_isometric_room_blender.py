"""Build an isometric room scene inside Blender.

This script is executed by Blender Python only. The regular test suite does
not import bpy; scripts/python/build_isometric_room.py prepares the JSON handoff
and launches Blender when available.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import bpy
    from mathutils import Vector
except ModuleNotFoundError:  # pragma: no cover - only happens outside Blender
    bpy = None
    Vector = None

DEFAULT_WALL_HEIGHT = 3.0
DEFAULT_WALL_THICKNESS = 0.12


def blender_args(argv: list[str]) -> list[str]:
    """Return args after Blender's -- separator."""

    if "--" not in argv:
        return []
    return argv[argv.index("--") + 1 :]


def build_parser() -> argparse.ArgumentParser:
    """Create argument parser for Blender-side script."""

    parser = argparse.ArgumentParser(description="Build isometric room scene in Blender.")
    parser.add_argument("--geometry-json", required=True, type=Path)
    parser.add_argument("--blend-output", required=True, type=Path)
    parser.add_argument("--preview-output", required=True, type=Path)
    parser.add_argument("--style", required=True)
    parser.add_argument("--room-preset")
    return parser


def load_geometry(path: Path) -> dict[str, Any]:
    """Read and validate geometry JSON."""

    data = json.loads(path.read_text(encoding="utf-8"))
    points = data.get("boundary_points")
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError("Geometry thiếu boundary_points hợp lệ.")
    return data


def clear_scene() -> None:
    """Remove all objects from the current Blender scene."""

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def hex_to_rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """Convert #RRGGBB to Blender RGBA."""

    text = (value or "#cccccc").strip()
    if not text.startswith("#") or len(text) != 7:
        text = "#cccccc"
    return (
        int(text[1:3], 16) / 255.0,
        int(text[3:5], 16) / 255.0,
        int(text[5:7], 16) / 255.0,
        alpha,
    )


def create_material(name: str, color: str) -> object:
    """Create a simple material."""

    material = bpy.data.materials.new(name=name)
    material.diffuse_color = hex_to_rgba(color)
    return material


def create_floor(points: list[list[float]], material: object) -> object:
    """Create a floor ngon mesh from boundary points."""

    vertices = [(float(x), float(y), 0.0) for x, y in points]
    mesh = bpy.data.meshes.new("RoomFloorMesh")
    mesh.from_pydata(vertices, [], [list(range(len(vertices)))])
    mesh.update()
    obj = bpy.data.objects.new("RoomFloor", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: object,
    rotation_z: float = 0.0,
) -> object:
    """Add a cube with dimensions and material."""

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=(0.0, 0.0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def create_walls(segments: list[dict[str, list[float]]], height: float, material: object) -> None:
    """Create simple rectangular prism walls along boundary segments."""

    for index, segment in enumerate(segments, start=1):
        start = segment["start"]
        end = segment["end"]
        dx = float(end[0]) - float(start[0])
        dy = float(end[1]) - float(start[1])
        length = math.hypot(dx, dy)
        if length <= 0.0001:
            continue
        angle = math.atan2(dy, dx)
        location = (
            (float(start[0]) + float(end[0])) / 2.0,
            (float(start[1]) + float(end[1])) / 2.0,
            height / 2.0,
        )
        add_cube(
            f"Wall_{index:02d}",
            location,
            (length, DEFAULT_WALL_THICKNESS, height),
            material,
            rotation_z=angle,
        )


def bbox_from_points(points: list[list[float]]) -> tuple[float, float, float, float]:
    """Return bbox from Blender-space points."""

    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def prop_dimensions(prop_name: str) -> tuple[float, float, float]:
    """Return simple placeholder dimensions for known room props."""

    sizes = {
        "shelf_unit": (0.35, 1.1, 1.8),
        "wooden_crate": (0.45, 0.45, 0.45),
        "cardboard_box": (0.35, 0.35, 0.3),
        "console_desk": (1.2, 0.45, 0.75),
        "office_chair": (0.45, 0.45, 0.55),
        "monitor_screen": (0.35, 0.05, 0.25),
        "dining_table": (1.1, 0.7, 0.7),
        "folding_chair": (0.35, 0.35, 0.45),
        "metal_barrel": (0.35, 0.35, 0.75),
    }
    return sizes.get(prop_name, (0.4, 0.4, 0.4))


def prop_location(
    placement: str,
    index: int,
    count: int,
    bbox: tuple[float, float, float, float],
) -> tuple[float, float, float]:
    """Choose a deterministic placeholder position inside the room bbox."""

    min_x, min_y, max_x, max_y = bbox
    width = max(max_x - min_x, 0.1)
    depth = max(max_y - min_y, 0.1)
    center_x = min_x + width / 2.0
    center_y = min_y + depth / 2.0
    step = (index + 1) / (count + 1)

    if placement in {"along_wall", "center_wall", "on_shelf"}:
        return (min_x + width * step, min_y + 0.25, 0.25)
    if placement in {"corner", "floor_scattered", "flanking_entrance"}:
        return (min_x + 0.35 + (index % 2) * (width - 0.7), min_y + 0.35, 0.25)
    if placement in {"at_desk", "on_desk", "floor_under_desk"}:
        return (center_x + (index - count / 2.0) * 0.25, min_y + depth * 0.35, 0.25)
    if placement in {"center", "around_table"}:
        return (center_x + (index - count / 2.0) * 0.35, center_y, 0.25)
    if placement in {"against_wall", "opposite_bed", "entrance", "entrance_facing"}:
        return (center_x, max_y - 0.35 - index * 0.25, 0.25)
    return (center_x + (index - count / 2.0) * 0.3, center_y, 0.25)


def create_placeholder_props(
    room_preset: dict[str, Any],
    bbox: tuple[float, float, float, float],
    material: object,
) -> None:
    """Create simple placeholder prop cubes for configured room preset props."""

    props = room_preset.get("props", []) if isinstance(room_preset, dict) else []
    if not isinstance(props, list):
        print("Cảnh báo: room preset có props không hợp lệ; bỏ qua props.")
        return
    for prop in props:
        if not isinstance(prop, dict):
            continue
        name = str(prop.get("name", "prop"))
        count = max(int(prop.get("count", 1)), 0)
        placement = str(prop.get("placement", "center"))
        for index in range(count):
            dims = prop_dimensions(name)
            x, y, _z = prop_location(placement, index, count, bbox)
            add_cube(f"Prop_{name}_{index + 1:02d}", (x, y, dims[2] / 2.0), dims, material)


def setup_lighting(style: dict[str, Any]) -> None:
    """Add ambient and sun lighting."""

    ambient = float(style.get("ambient_light", 0.6))
    bpy.context.scene.world = bpy.data.worlds.new("World") if bpy.context.scene.world is None else bpy.context.scene.world
    bpy.context.scene.world.color = (ambient, ambient, ambient)
    bpy.ops.object.light_add(type="SUN", location=(4.0, -5.0, 8.0))
    sun = bpy.context.object
    sun.name = "IsoSun"
    sun.rotation_euler = (math.radians(45.0), 0.0, math.radians(35.0))
    sun.data.energy = 2.5
    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.0, 5.0))
    area = bpy.context.object
    area.name = "SoftFill"
    area.data.energy = 350.0
    area.data.size = 5.0


def setup_camera(points: list[list[float]], wall_height: float) -> None:
    """Create an orthographic isometric camera fitted to the room.

    The project isometric preset follows strict iso math: yaw about 45 degrees
    and pitch about 54.7356 degrees, even though an early spec mentioned 30.
    """

    min_x, min_y, max_x, max_y = bbox_from_points(points)
    center = Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, wall_height / 2.0))
    span = max(max_x - min_x, max_y - min_y, wall_height, 1.0)
    distance = span * 2.0
    location = center + Vector((distance, -distance, distance))
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = "IsometricCamera"
    direction = center - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = span * 1.8
    bpy.context.scene.camera = camera


def setup_render(style: dict[str, Any], resolution: dict[str, int], preview_output: Path) -> None:
    """Configure render engine, transparency, resolution, and output path."""

    engine = str(style.get("render_engine", "EEVEE")).upper()
    try:
        bpy.context.scene.render.engine = "CYCLES" if engine == "CYCLES" else "BLENDER_EEVEE_NEXT"
    except TypeError:
        bpy.context.scene.render.engine = "CYCLES" if engine == "CYCLES" else "BLENDER_EEVEE"
    bpy.context.scene.render.film_transparent = style.get("background", "transparent") == "transparent"
    bpy.context.scene.render.resolution_x = int(resolution.get("width", 1920))
    bpy.context.scene.render.resolution_y = int(resolution.get("height", 1080))
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.filepath = str(preview_output)


def main(argv: list[str] | None = None) -> int:
    """Build the Blender scene and render preview."""

    if bpy is None:
        print("ERR_BPY_MISSING: Script này phải chạy bên trong Blender Python.", file=sys.stderr)
        return 1

    args = build_parser().parse_args(argv if argv is not None else blender_args(sys.argv))
    try:
        data = load_geometry(args.geometry_json)
        points = data["boundary_points"]
        segments = data.get("wall_segments", [])
        style = data.get("style_preset", {})
        room_preset = data.get("room_preset", {})
        wall_height = float(room_preset.get("wall_height", DEFAULT_WALL_HEIGHT))

        print("TuPhuongVoLo-ArtPipeline - Blender build start")
        print(f"Room: {data.get('room_name')}")
        clear_scene()
        floor_material = create_material("FloorMaterial", style.get("floor_color", "#4A7C59"))
        wall_material = create_material("WallMaterial", style.get("wall_color", "#F5F5F0"))
        prop_material = create_material("BlockoutPropMaterial", style.get("line_color", "#2C2C2C"))

        create_floor(points, floor_material)
        create_walls(segments, wall_height, wall_material)
        create_placeholder_props(room_preset, bbox_from_points(points), prop_material)
        setup_lighting(style)
        setup_camera(points, wall_height)
        setup_render(style, data.get("render_resolution", {}), args.preview_output)

        args.preview_output.parent.mkdir(parents=True, exist_ok=True)
        args.blend_output.parent.mkdir(parents=True, exist_ok=True)
        print(f"Rendering PNG: {args.preview_output}")
        bpy.ops.render.render(write_still=True)
        print(f"Saving .blend: {args.blend_output}")
        bpy.ops.wm.save_as_mainfile(filepath=str(args.blend_output))
        print("TuPhuongVoLo-ArtPipeline - Blender build done")
        return 0
    except Exception as exc:
        print(f"ERR_BLENDER_BUILD: Không thể dựng phòng isometric. Chi tiết: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
