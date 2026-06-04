"""Apply Feature 014A visual fidelity additions to a Maya scene.

Run this with mayapy through scripts/python/maya_visual_fidelity_pass.py. It
opens a source .ma scene, adds only agent-owned visual helpers under
GRP_visual_fidelity_v0, then saves a different output .ma scene.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

VISUAL_GROUP_NAME = "GRP_visual_fidelity_v0"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse mayapy arguments."""

    parser = argparse.ArgumentParser(description="Apply additive Maya visual fidelity pass.")
    parser.add_argument("--input-scene", required=True, type=Path)
    parser.add_argument("--output-scene", required=True, type=Path)
    parser.add_argument("--plan-json", required=True, type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def initialize_maya() -> Any:
    """Import maya.cmds and initialize standalone mode."""

    try:
        import maya.cmds as cmds  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Khong tim thay Maya Python. Hay chay script bang mayapy.exe."
        ) from exc

    try:
        import maya.standalone  # type: ignore[import-not-found]

        try:
            maya.standalone.initialize(name="python")
        except Exception as exc:
            if "initialized" not in str(exc).lower():
                raise
    except ModuleNotFoundError:
        pass
    return cmds


def load_plan(path: Path) -> dict[str, Any]:
    """Load visual fidelity plan JSON."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Plan JSON phai la object.")
    return data


def create_material(
    cmds: Any,
    name: str,
    color: tuple[float, float, float],
    transparency: float = 0.0,
) -> str:
    """Create one agent-owned Lambert material and return its shading group."""

    material = cmds.shadingNode("lambert", asShader=True, name=name)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{name}SG")
    cmds.setAttr(f"{material}.color", color[0], color[1], color[2], type="double3")
    if transparency > 0.0:
        cmds.setAttr(
            f"{material}.transparency",
            transparency,
            transparency,
            transparency,
            type="double3",
        )
    cmds.connectAttr(f"{material}.outColor", f"{shading_group}.surfaceShader", force=True)
    return shading_group


def assign_material(cmds: Any, node: str, shading_group: str) -> None:
    """Assign a shading group to a node."""

    cmds.sets(node, edit=True, forceElement=shading_group)


def create_box(
    cmds: Any,
    name: str,
    center: tuple[float, float, float],
    size: tuple[float, float, float],
    material: str,
    parent: str,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> str:
    """Create one cube part."""

    width, height, depth = size
    node = cmds.polyCube(name=name, width=width, height=height, depth=depth)[0]
    cmds.xform(node, translation=center, rotation=rotation)
    assign_material(cmds, node, material)
    cmds.parent(node, parent)
    return node


def create_cylinder(
    cmds: Any,
    name: str,
    center: tuple[float, float, float],
    radius: float,
    height: float,
    material: str,
    parent: str,
) -> str:
    """Create a vertical cylinder part."""

    node = cmds.polyCylinder(name=name, radius=radius, height=height, subdivisionsX=18)[0]
    cmds.xform(node, translation=center)
    assign_material(cmds, node, material)
    cmds.parent(node, parent)
    return node


def _addition_center(addition: dict[str, Any]) -> tuple[float, float]:
    center = addition.get("center")
    if not isinstance(center, list | tuple) or len(center) != 2:
        return 0.0, 0.0
    return float(center[0]), float(center[1])


def _addition_size(
    addition: dict[str, Any],
    fallback: tuple[float, float, float],
) -> tuple[float, float, float]:
    size = addition.get("size")
    if not isinstance(size, list | tuple) or len(size) != 3:
        return fallback
    return float(size[0]), float(size[1]), float(size[2])


def _rotation_y(addition: dict[str, Any]) -> float:
    try:
        return float(addition.get("rotation_y_degrees", 0.0))
    except (TypeError, ValueError):
        return 0.0


def rotate_group_around_center(
    cmds: Any,
    group: str,
    center: tuple[float, float],
    rotation_y: float,
) -> None:
    """Rotate a template group around the prop floor center."""

    if rotation_y:
        cmds.xform(group, pivots=(center[0], 0.0, center[1]), worldSpace=True)
        cmds.xform(group, rotation=(0.0, rotation_y, 0.0), worldSpace=True)


def build_crate(
    cmds: Any,
    addition: dict[str, Any],
    materials: dict[str, str],
    parent: str,
) -> None:
    """Create a readable wooden crate proxy."""

    x, z = _addition_center(addition)
    width, height, depth = _addition_size(addition, (0.55, 0.45, 0.55))
    name = str(addition["name"])
    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    trim_h = max(min(height * 0.10, 0.06), 0.025)
    trim_w = max(min(width * 0.12, 0.07), 0.035)
    face_z = z - depth / 2.0 - 0.012
    create_box(
        cmds,
        f"{name}_body",
        (x, height / 2.0, z),
        (width, height, depth),
        materials["wood"],
        group,
    )
    create_box(
        cmds,
        f"{name}_top_trim",
        (x, height + trim_h / 2.0, z),
        (width, trim_h, depth),
        materials["dark_wood"],
        group,
    )
    create_box(
        cmds,
        f"{name}_front_band_h",
        (x, height * 0.52, face_z),
        (width * 0.92, trim_h, 0.025),
        materials["dark_wood"],
        group,
    )
    create_box(
        cmds,
        f"{name}_front_band_v",
        (x, height * 0.52, face_z),
        (trim_w, height * 0.78, 0.025),
        materials["dark_wood"],
        group,
    )
    create_box(
        cmds,
        f"{name}_left_trim",
        (x - width / 2.0 + trim_w / 2.0, height / 2.0, z),
        (trim_w, height, depth),
        materials["dark_wood"],
        group,
    )
    create_box(
        cmds,
        f"{name}_right_trim",
        (x + width / 2.0 - trim_w / 2.0, height / 2.0, z),
        (trim_w, height, depth),
        materials["dark_wood"],
        group,
    )
    rotate_group_around_center(cmds, group, (x, z), _rotation_y(addition))


def build_barrel(
    cmds: Any,
    addition: dict[str, Any],
    materials: dict[str, str],
    parent: str,
) -> None:
    """Create a cylinder barrel proxy with dark rings."""

    x, z = _addition_center(addition)
    width, height, depth = _addition_size(addition, (0.48, 0.72, 0.48))
    radius = max(min(width, depth) / 2.0, 0.12)
    name = str(addition["name"])
    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    create_cylinder(
        cmds,
        f"{name}_body",
        (x, height / 2.0, z),
        radius,
        height,
        materials["barrel"],
        group,
    )
    ring_h = max(min(height * 0.08, 0.055), 0.035)
    create_cylinder(
        cmds,
        f"{name}_top_ring",
        (x, height - ring_h / 2.0, z),
        radius * 1.04,
        ring_h,
        materials["dark_wood"],
        group,
    )
    create_cylinder(
        cmds,
        f"{name}_mid_band",
        (x, height * 0.52, z),
        radius * 1.05,
        ring_h,
        materials["dark_wood"],
        group,
    )
    create_cylinder(
        cmds,
        f"{name}_bottom_ring",
        (x, ring_h / 2.0, z),
        radius * 1.04,
        ring_h,
        materials["dark_wood"],
        group,
    )
    rotate_group_around_center(cmds, group, (x, z), _rotation_y(addition))


def build_shelf(
    cmds: Any,
    addition: dict[str, Any],
    materials: dict[str, str],
    parent: str,
) -> None:
    """Create a shelf unit from posts, shelves, and small fillers."""

    x, z = _addition_center(addition)
    width, height, depth = _addition_size(addition, (1.1, 1.55, 0.42))
    name = str(addition["name"])
    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    post_w = max(min(width * 0.07, 0.08), 0.04)
    shelf_h = max(min(height * 0.04, 0.07), 0.035)
    for side, sx in (("left", -1.0), ("right", 1.0)):
        create_box(
            cmds,
            f"{name}_{side}_post",
            (x + sx * (width / 2.0 - post_w / 2.0), height / 2.0, z),
            (post_w, height, depth),
            materials["shelf"],
            group,
        )
    for index, y in enumerate((height * 0.18, height * 0.48, height * 0.78), start=1):
        create_box(
            cmds,
            f"{name}_plank_{index}",
            (x, y, z),
            (width, shelf_h, depth),
            materials["dark_wood"],
            group,
        )
    filler_w = min(width * 0.24, 0.28)
    for index, sx in enumerate((-0.22, 0.22), start=1):
        create_box(
            cmds,
            f"{name}_filler_crate_{index}",
            (x + sx * width, height * 0.32, z),
            (filler_w, 0.22, max(depth * 0.70, 0.20)),
            materials["wood"],
            group,
        )
    rotate_group_around_center(cmds, group, (x, z), _rotation_y(addition))


def build_floor_grate(
    cmds: Any,
    addition: dict[str, Any],
    materials: dict[str, str],
    parent: str,
) -> None:
    """Create a low floor grate frame with dark slats."""

    x, z = _addition_center(addition)
    width, height, depth = _addition_size(addition, (1.0, 0.04, 0.4))
    name = str(addition["name"])
    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    y = max(height / 2.0, 0.025)
    frame_w = 0.045
    create_box(
        cmds,
        f"{name}_frame_front",
        (x, y, z - depth / 2.0),
        (width, height, frame_w),
        materials["metal"],
        group,
    )
    create_box(
        cmds,
        f"{name}_frame_back",
        (x, y, z + depth / 2.0),
        (width, height, frame_w),
        materials["metal"],
        group,
    )
    create_box(
        cmds,
        f"{name}_frame_left",
        (x - width / 2.0, y, z),
        (frame_w, height, depth),
        materials["metal"],
        group,
    )
    create_box(
        cmds,
        f"{name}_frame_right",
        (x + width / 2.0, y, z),
        (frame_w, height, depth),
        materials["metal"],
        group,
    )
    slat_count = 5
    for index in range(slat_count):
        offset = -width * 0.32 + index * (width * 0.16)
        create_box(
            cmds,
            f"{name}_slat_{index + 1}",
            (x + offset, y + 0.01, z),
            (0.035, height, depth * 0.82),
            materials["dark_metal"],
            group,
        )
    rotate_group_around_center(cmds, group, (x, z), _rotation_y(addition))


def build_electrical_cabinet(
    cmds: Any,
    addition: dict[str, Any],
    materials: dict[str, str],
    parent: str,
) -> None:
    """Create an electrical cabinet with handle and warning marker."""

    x, z = _addition_center(addition)
    width, height, depth = _addition_size(addition, (0.45, 1.20, 0.14))
    name = str(addition["name"])
    group = cmds.group(empty=True, name=name)
    cmds.parent(group, parent)
    face_z = z - depth / 2.0 - 0.012
    create_box(
        cmds,
        f"{name}_body",
        (x, height / 2.0, z),
        (width, height, depth),
        materials["cabinet"],
        group,
    )
    create_box(
        cmds,
        f"{name}_panel",
        (x, height * 0.55, face_z),
        (width * 0.82, height * 0.68, 0.025),
        materials["dark_metal"],
        group,
    )
    create_box(
        cmds,
        f"{name}_handle",
        (x + width * 0.28, height * 0.55, face_z - 0.02),
        (0.045, height * 0.22, 0.025),
        materials["warning"],
        group,
    )
    create_box(
        cmds,
        f"{name}_warning_mark",
        (x - width * 0.18, height * 0.68, face_z - 0.025),
        (width * 0.18, height * 0.09, 0.025),
        materials["warning"],
        group,
    )
    rotate_group_around_center(cmds, group, (x, z), _rotation_y(addition))


PROP_BUILDERS = {
    "wooden_crate": build_crate,
    "barrel": build_barrel,
    "shelf_unit": build_shelf,
    "floor_grate": build_floor_grate,
    "electrical_cabinet": build_electrical_cabinet,
}


def room_bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Return min_x, min_z, max_x, max_z for room boundary points."""

    xs = [point[0] for point in points]
    zs = [point[1] for point in points]
    return min(xs), min(zs), max(xs), max(zs)


def create_floor_tint(
    cmds: Any,
    points: list[tuple[float, float]],
    material: str,
    parent: str,
) -> None:
    """Create a subtle agent-owned floor tint slightly above the blockout floor."""

    maya_points = [(x, 0.012, z) for x, z in points]
    floor = cmds.polyCreateFacet(point=maya_points, name="vf_room_floor_tint")[0]
    assign_material(cmds, floor, material)
    cmds.parent(floor, parent)


def create_review_camera_and_lights(
    cmds: Any,
    room_name: str,
    points: list[tuple[float, float]],
    parent: str,
) -> None:
    """Create agent-owned review camera and lights."""

    if points:
        min_x, min_z, max_x, max_z = room_bounds(points)
    else:
        min_x, min_z, max_x, max_z = 0.0, -2.0, 4.0, 0.0
    center_x = (min_x + max_x) / 2.0
    center_z = (min_z + max_z) / 2.0
    width = max(max_x - min_x, 1.0)
    depth = max(max_z - min_z, 1.0)
    distance = max(math.hypot(width, depth) * 1.6, 6.0)
    camera_transform, camera_shape = cmds.camera(name=f"cam_{room_name}_visual_review")
    target = cmds.spaceLocator(name=f"LOC_{room_name}_visual_review_target")[0]
    cmds.xform(target, translation=(center_x, 0.9, center_z))
    cmds.xform(camera_transform, translation=(center_x + distance, 4.2, center_z + distance))
    aim = cmds.aimConstraint(
        target,
        camera_transform,
        aimVector=(0.0, 0.0, -1.0),
        upVector=(0.0, 1.0, 0.0),
        worldUpType="vector",
        worldUpVector=(0.0, 1.0, 0.0),
    )[0]
    cmds.delete(aim, target)
    cmds.setAttr(f"{camera_shape}.orthographic", True)
    cmds.setAttr(f"{camera_shape}.orthographicWidth", max(width, depth) * 1.65)
    cmds.parent(camera_transform, parent)

    key_shape = cmds.directionalLight(name="key_agent_visual_review")
    key_transform = cmds.listRelatives(key_shape, parent=True)[0]
    cmds.xform(key_transform, rotation=(-50.0, 35.0, 0.0))
    cmds.parent(key_transform, parent)

    ambient_shape = cmds.ambientLight(name="ambient_agent_visual_review", intensity=0.28)
    ambient_transform = cmds.listRelatives(ambient_shape, parent=True)[0]
    cmds.parent(ambient_transform, parent)


def create_artist_note(cmds: Any, plan: dict[str, Any], parent: str) -> None:
    """Create locator/annotation metadata for the artist."""

    room_name = str(plan.get("room_name") or "room")
    prop_counts = plan.get("prop_counts", {})
    count_text = ", ".join(f"{key}={value}" for key, value in sorted(prop_counts.items()))
    text = (
        "Visual Fidelity MVP 014A\\n"
        f"Room: {room_name}\\n"
        f"Group: {VISUAL_GROUP_NAME}\\n"
        f"Props: {count_text or '0'}\\n"
        "Safe rollback: open the source .ma or hide/delete this group."
    )
    locator = cmds.spaceLocator(name=f"NOTE_{room_name}_visual_fidelity")[0]
    cmds.xform(locator, translation=(0.2, 1.4, 0.2))
    cmds.parent(locator, parent)
    annotation = cmds.annotate(locator, text=text)
    annotation_transform = cmds.listRelatives(annotation, parent=True)[0]
    annotation_transform = cmds.rename(
        annotation_transform,
        f"annotation_{room_name}_visual_fidelity",
    )
    cmds.xform(annotation_transform, translation=(0.55, 1.65, 0.2))
    cmds.parent(annotation_transform, parent)
    try:
        cmds.addAttr(parent, longName="agentVisualFidelityNote", dataType="string")
        cmds.setAttr(f"{parent}.agentVisualFidelityNote", text, type="string")
    except Exception:
        pass


def build_visual_fidelity_group(cmds: Any, plan: dict[str, Any]) -> None:
    """Create all visual fidelity additions in a top-level group."""

    if cmds.objExists(VISUAL_GROUP_NAME):
        raise ValueError(f"Scene da co {VISUAL_GROUP_NAME}; khong stack pass trung lap.")

    root = cmds.group(empty=True, name=VISUAL_GROUP_NAME)
    props_group = cmds.group(empty=True, name="vf_props")
    presentation_group = cmds.group(empty=True, name="vf_presentation")
    notes_group = cmds.group(empty=True, name="vf_artist_notes")
    cmds.parent(props_group, root)
    cmds.parent(presentation_group, root)
    cmds.parent(notes_group, root)

    materials = {
        "wood": create_material(cmds, "MAT_agent_vf_wood", (0.50, 0.31, 0.16)),
        "dark_wood": create_material(cmds, "MAT_agent_vf_dark_wood", (0.20, 0.12, 0.06)),
        "barrel": create_material(cmds, "MAT_agent_vf_barrel", (0.42, 0.24, 0.10)),
        "shelf": create_material(cmds, "MAT_agent_vf_shelf", (0.42, 0.29, 0.14)),
        "metal": create_material(cmds, "MAT_agent_vf_metal", (0.42, 0.44, 0.45)),
        "dark_metal": create_material(cmds, "MAT_agent_vf_dark_metal", (0.08, 0.09, 0.10)),
        "cabinet": create_material(cmds, "MAT_agent_vf_cabinet", (0.52, 0.56, 0.57)),
        "warning": create_material(cmds, "MAT_agent_vf_warning_yellow", (0.95, 0.75, 0.12)),
        "floor_tint": create_material(
            cmds,
            "MAT_agent_vf_floor_tint",
            (0.36, 0.45, 0.37),
            transparency=0.35,
        ),
    }

    for addition in plan.get("planned_additions", []):
        if not isinstance(addition, dict) or addition.get("kind") != "prop_template":
            continue
        template = str(addition.get("template") or "")
        builder = PROP_BUILDERS.get(template)
        if builder:
            builder(cmds, addition, materials, props_group)

    boundary_points = []
    for raw_point in plan.get("boundary_points", []):
        if isinstance(raw_point, list | tuple) and len(raw_point) == 2:
            boundary_points.append((float(raw_point[0]), float(raw_point[1])))
    if len(boundary_points) >= 3:
        create_floor_tint(cmds, boundary_points, materials["floor_tint"], presentation_group)
    create_review_camera_and_lights(
        cmds,
        str(plan.get("room_name") or "room"),
        boundary_points,
        presentation_group,
    )
    create_artist_note(cmds, plan, notes_group)


def apply_pass(cmds: Any, input_scene: Path, output_scene: Path, plan: dict[str, Any]) -> None:
    """Open input scene, apply additive group, and save as output scene."""

    if input_scene.resolve() == output_scene.resolve():
        raise ValueError("output_scene phai khac input_scene.")
    if output_scene.exists():
        raise ValueError(f"Output scene da ton tai: {output_scene}")
    cmds.file(str(input_scene), open=True, force=True, ignoreVersion=True)
    build_visual_fidelity_group(cmds, plan)
    output_scene.parent.mkdir(parents=True, exist_ok=True)
    cmds.file(rename=str(output_scene))
    cmds.file(save=True, type="mayaAscii", force=True)


def main(argv: list[str] | None = None) -> int:
    """Run the Maya visual fidelity pass."""

    args = parse_args(argv)
    try:
        cmds = initialize_maya()
        plan = load_plan(args.plan_json.resolve())
        apply_pass(cmds, args.input_scene.resolve(), args.output_scene.resolve(), plan)
        if args.verbose:
            print(f"Feature 014A visual fidelity saved: {args.output_scene.resolve()}")
        return 0
    except Exception as exc:
        print(f"ERR_VISUAL_FIDELITY_APPLY: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
